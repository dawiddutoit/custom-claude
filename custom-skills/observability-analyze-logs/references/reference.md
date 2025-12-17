# Log Analyzer Reference

> **Note:** This reference is generic and applies to any project using OpenTelemetry-formatted logs. Replace `your_project` with your actual project package name where referenced.

## Technical Architecture

### Components

The log analyzer consists of four main components:

1. **OTelLogParser** - Parses OpenTelemetry-formatted logs
2. **TraceReconstructor** - Rebuilds execution traces from log entries
3. **ErrorExtractor** - Extracts errors with full context
4. **LogAnalyzer** - Coordinates analysis and LLM integration

### Data Flow

```
Log File
  ↓
OTelLogParser (regex parsing)
  ↓
List[LogEntry] (structured entries)
  ↓
TraceReconstructor (group by trace_id)
  ↓
Dict[TraceID, TraceExecution] (organized traces)
  ↓
ErrorExtractor (find errors, build context)
  ↓
List[ErrorContext] (errors with call chains)
  ↓
LogAnalyzer (format + optional AI analysis)
  ↓
AnalysisReport (JSON/Markdown/Summary)
```

## OpenTelemetry Log Format

### Log Pattern

```
YYYY-MM-DD HH:MM:SS - [trace:TRACE_ID | span:SPAN_ID] - module.path - LEVEL - [file.py:line] - function() - message
```

### Example

```
2025-10-16 14:32:15 - [trace:abc123def456 | span:789ghi] - your_project.database - ERROR - [neo4j_client.py:123] - connect() - Failed to connect to Neo4j: Connection timeout after 5s
```

### Fields

| Field | Description | Example |
|-------|-------------|---------|
| timestamp | ISO format datetime | `2025-10-16 14:32:15` |
| trace_id | Unique execution ID | `abc123def456` |
| span_id | Unique operation ID | `789ghi` |
| module | Python module path | `your_project.database` |
| level | Log level | `ERROR`, `WARNING`, `INFO`, `DEBUG` |
| file | Source filename | `neo4j_client.py` |
| line | Line number | `123` |
| function | Function name | `connect` |
| message | Log message | `Failed to connect...` |

### Trace and Span IDs

**Trace ID:**
- Represents one complete execution flow
- All operations in single MCP tool call share same trace ID
- Used to group related logs across multiple files/functions

**Span ID:**
- Represents one operation within a trace
- Each function call gets unique span ID
- Child operations inherit parent's trace but have own span

**Example trace:**
```
trace:abc123 | span:001 - automatic_indexing() [deprecated] called
trace:abc123 | span:002 - connect_to_neo4j() called
trace:abc123 | span:003 - ERROR: Connection failed
trace:abc123 | span:004 - retry_connection() called
trace:abc123 | span:005 - ERROR: Retry failed
```

All logs share `trace:abc123` (same execution), but each has unique span ID.

## Data Models

### LogEntry

```python
@dataclass
class LogEntry:
    timestamp: str          # "2025-10-16 14:32:15"
    level: str             # "ERROR"
    module: str            # "your_project.database"
    file: str              # "neo4j_client.py"
    line: int              # 123
    function: str          # "connect"
    message: str           # "Failed to connect..."
    trace_id: str | None   # "abc123def456"
    span_id: str | None    # "789ghi"
    raw_line: str          # Original log line

    @property
    def datetime(self) -> datetime:
        """Parse timestamp to datetime object."""
```

### TraceExecution

```python
@dataclass
class TraceExecution:
    trace_id: str                                  # "abc123def456"
    entries: list[LogEntry]                        # All logs in this trace
    spans: dict[str, list[LogEntry]]              # span_id -> logs in that span
    errors: list[LogEntry]                         # ERROR/CRITICAL logs only
    start_time: str                                # First log timestamp
    end_time: str                                  # Last log timestamp
    duration_seconds: float                        # Time from start to end

    @property
    def entry_point(self) -> LogEntry | None:
        """First log entry (entry point of execution)."""

    @property
    def has_errors(self) -> bool:
        """True if trace contains any errors."""

    def get_call_chain_to_error(self, error: LogEntry) -> list[LogEntry]:
        """All logs from trace start up to and including error."""

    def get_entries_after_error(self, error: LogEntry, count: int = 5) -> list[LogEntry]:
        """Logs after error (to see recovery attempts)."""
```

### ErrorContext

```python
@dataclass
class ErrorContext:
    error: LogEntry                    # The error log
    trace: TraceExecution             # Full trace containing error
    call_chain: list[LogEntry]        # All logs leading to error
    recovery_attempts: list[LogEntry] # Logs after error
    related_errors: list[LogEntry]    # Other errors in same trace
    stack_trace: list[str]            # Stack trace lines (if present)
```

### AnalysisReport

```python
@dataclass
class AnalysisReport:
    summary: dict[str, Any]                        # Summary statistics
    traces: dict[str, TraceExecution]             # All traces (trace_id -> TraceExecution)
    error_contexts: list[ErrorContext]            # All errors with context
    grouped_by_file: dict[str, list[ErrorContext]] # Errors grouped by file
    llm_analysis: str                             # AI analysis (if not skipped)
```

## Parsing Logic

### Log Pattern Regex

```python
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - "
    r"(?:\[trace:(?P<trace_id>\w+) \| span:(?P<span_id>\w+)\] - )?"
    r"(?P<module>[\w\.]+) - "
    r"(?P<level>\w+) - "
    r"\[(?P<file>[\w\._]+):(?P<line>\d+)\] - "
    r"(?P<function>[\w_]+)\(\) - "
    r"(?P<message>.*)"
)
```

**What it matches:**
- Required: timestamp, module, level, file, line, function, message
- Optional: trace_id, span_id (logs without tracing still parse)

**Why optional trace/span:**
- Some logs may not have tracing enabled
- Early logs before tracing initialized
- Standalone utility scripts

### Trace Reconstruction

**Algorithm:**
1. Parse all log lines into LogEntry objects
2. Group entries by trace_id (or "no_trace" if missing)
3. For each trace:
   - Add entries to trace.entries list
   - Organize by span_id into trace.spans dict
   - Collect errors into trace.errors list
   - Sort entries by timestamp
   - Calculate start_time, end_time, duration

**Result:** Complete execution traces with chronological ordering

### Error Extraction

**For each error in each trace:**
1. Get call chain: All logs from trace start up to error
2. Get recovery attempts: Next 5 logs after error
3. Get related errors: Other errors in same trace
4. Extract stack trace: Lines after error that look like stack traces

**Call chain example:**
```
Call chain to error (15 steps):
  1. automatic_indexing() [deprecated] - Starting initialization
  2. validate_config() - Checking configuration
  3. connect_to_neo4j() - Attempting connection
  ...
  15. ERROR: Connection timeout after 5s
```

## AI Analysis

### LLM Prompt Strategy

**System prompt:**
- Expert at analyzing logs and debugging with distributed tracing
- Focus on root causes from full call chains
- Identify patterns across multiple traces
- Provide specific file:line fixes

**User prompt:**
- Summary stats (total entries, traces, errors)
- Top 5 errors with full context:
  - Error message and location
  - Trace ID and duration
  - Entry point (where execution started)
  - Call chain (last 10 steps leading to error)
  - Related errors in same trace
  - Recovery attempts (logs after error)
  - Stack trace (if available)

**Response format:**
1. Root Causes (analyze call chains)
2. Patterns (common issues across traces)
3. Priority (what to fix first)
4. Fixes (specific file:line changes)
5. Systemic Issues (architectural problems)

### Configuration

```python
config = CallConfig(
    timeout=45.0,           # 45 second timeout
    max_tokens=3000,        # Up to 3000 tokens response
    temperature=0.2,        # Low temp for focused analysis
    extended_thinking=True, # Enable deep reasoning
    thinking_budget=8000,   # 8000 tokens for thinking
)
```

**Why these settings:**
- Extended thinking: Enables reasoning about complex traces
- Low temperature: Focused, deterministic analysis
- High thinking budget: Needed for trace reasoning
- 3000 token output: Enough for detailed analysis

### Budget Tracking

The analyzer uses LangChainClient with built-in budget tracking:

```python
llm_client = LangChainClient(
    model="claude-sonnet-4-5-20250929",
    monthly_budget=50.0,  # $50/month
    daily_budget=5.0,     # $5/day
)

# After analysis
budget = llm_client.get_budget_status()
print(f"Cost: ${budget['daily_usage']:.4f}")
```

**Cost per analysis:** Typically $0.01-0.05 depending on error count

## Output Formats

### Summary Format

**Purpose:** Quick overview, error ID lookup

**Structure:**
```
=============================================================================
Log Analysis Summary
=============================================================================

Log file: logs/your_project.log
Total entries: 1523
Total traces: 12
Traces with errors: 3
Total errors: 7
Time range: 2025-10-16 14:30:00 to 2025-10-16 14:35:00

=============================================================================
Errors Summary (use --error-id N to see details)
=============================================================================

ID   | Trace      | File:Line              | Function    | Message
-----|------------|------------------------|-------------|------------------
1    | abc123     | database.py:45         | connect     | Connection failed...
2    | abc123     | database.py:67         | query       | No active connection
3    | def456     | settings.py:23         | load        | Missing required key...
...
```

**Features:**
- Compact table format
- Error IDs for drill-down
- Truncated messages (40 chars)
- Quick commands for next steps

### Markdown Format

**Purpose:** Detailed investigation, documentation

**Structure:**
```markdown
# Log Analysis Report

## Summary
- Log file: ...
- Total entries: ...
- Total traces: ...

## AI Analysis (Trace-Based)
[LLM-generated analysis with root causes, patterns, priority, fixes]

## Errors with Execution Traces

### Error 1: database.py:45
**Trace ID:** abc123
**Time:** 2025-10-16 14:32:15
**Trace Duration:** 5.23s
**Function:** connect()
**Level:** ERROR

**Full Message:**
```
Failed to connect to Neo4j: Connection timeout after 5s
```

**Trace started at:**
- `initialize.py:23` - automatic_indexing() [deprecated]
- Starting repository initialization

**Call chain leading to error (15 total steps):**
```
  1.     initialize.py:23 - automatic_indexing() [deprecated]
         Starting repository initialization
  2.     config.py:45 - load_config()
         Loading configuration from settings
  ...
  15. ERROR-> database.py:45 - connect()
         Failed to connect to Neo4j: Connection timeout after 5s
```

**Related errors in same trace:** 2
- `database.py:67` - No active connection available
- `database.py:89` - Query failed due to connection error

---

## Errors Grouped by File

### database.py (3 errors)
- Line 45 [abc123] - Connection timeout...
- Line 67 [abc123] - No active connection...
- Line 89 [def456] - Query failed...
```

**Features:**
- Full messages (no truncation)
- Complete call chains
- Stack traces (if available)
- Related errors
- AI analysis
- Grouped by file summary

### JSON Format

**Purpose:** Programmatic access, automation

**Structure:**
```json
{
  "summary": {
    "total_entries": 1523,
    "total_traces": 12,
    "traces_with_errors": 3,
    "total_errors": 7,
    "unique_files": 4,
    "time_range": "...",
    "log_file": "..."
  },
  "llm_analysis": "...",
  "errors": [
    {
      "timestamp": "2025-10-16 14:32:15",
      "level": "ERROR",
      "file": "database.py",
      "line": 45,
      "function": "connect",
      "message": "Failed to connect...",
      "trace_id": "abc123",
      "trace_duration": 5.23,
      "call_chain_length": 15,
      "related_errors": 2,
      "stack_trace": [...]
    }
  ],
  "traces": {
    "abc123": {
      "trace_id": "abc123",
      "start": "2025-10-16 14:32:10",
      "end": "2025-10-16 14:32:15",
      "duration_seconds": 5.23,
      "total_entries": 42,
      "error_count": 3,
      "span_count": 8
    }
  }
}
```

**Use cases:**
- Automated monitoring scripts
- CI/CD pipelines
- Custom analysis tools
- Data aggregation

## CLI Arguments

### Positional Arguments

```bash
log_file        Path to log file (default: logs/your_project.log)
```

### Output Format

```bash
--format {json|markdown|summary}
    Output format (default: summary)
```

### Filtering

```bash
--error-id N
    Show detailed view of specific error by ID (from summary)

--trace TRACE_ID
    Show all errors in specific trace ID

--file FILENAME
    Filter errors by file name (e.g., 'database.py')
```

**Examples:**
```bash
# Error ID 1
--error-id 1

# Specific trace
--trace abc123def456

# All errors in database.py
--file database.py

# Combine filters (file + trace)
--file database.py --trace abc123
```

### Performance

```bash
--no-ai
    Skip AI analysis (faster, no cost)
    Still parses logs and builds traces

--output PATH, -o PATH
    Write output to file instead of stdout
```

**Examples:**
```bash
# Fast parsing without AI
--no-ai

# Save to file
--output report.md
-o errors.json
```

## Call Chain Summarization

For long call chains (>15 steps), the analyzer uses intelligent summarization:

### Strategy

1. **Always show first 3 steps** (execution context)
2. **Always show last 8 steps** (immediate error context)
3. **Summarize middle** (collapse repetitive operations)

### Repetition Detection

Groups consecutive operations by `file:function`:

```python
# Before summarization (25 steps):
1.  process.py:10 - process_item()
2.  process.py:10 - process_item()
3.  process.py:10 - process_item()
4.  process.py:10 - process_item()
5.  process.py:10 - process_item()
...
25. ERROR: Processing failed

# After summarization (12 steps):
1.  initialize.py:5 - start()
2.  loader.py:20 - load_items()
3.  loader.py:30 - validate_items()
  ... [21x repeated] process.py:process_item()
18. validator.py:15 - validate_final()
19. validator.py:20 - check_constraints()
20. validator.py:25 - verify_state()
ERROR-> process.py:45 - finalize()
```

### Configuration

```python
MAX_SUMMARY_MESSAGE_LEN = 40      # Summary table message length
MAX_DETAIL_MESSAGE_LEN = 80       # Markdown detail message length
MAX_FILE_GROUP_MESSAGE_LEN = 100  # File grouping message length
MIN_COLLAPSE_GROUP_SIZE = 3       # Minimum repetitions to collapse
MAX_LLM_CALL_CHAIN_STEPS = 10     # Steps to show LLM for analysis
```

## Performance Characteristics

### Parsing Speed

- **~10,000 lines/second** (pure parsing)
- 1MB log file (~20,000 lines) parses in ~2 seconds

### AI Analysis Cost

- **~$0.01-0.05 per analysis** (depends on error count)
- Uses extended thinking for deep reasoning
- Budget tracking prevents overruns

### Memory Usage

- **~1MB per 10,000 log entries** (in-memory parsed entries)
- Traces organized in dict (O(1) lookup)
- No streaming (all entries loaded at once)

**Scaling limits:**
- Files up to 100MB: No issues
- Files >100MB: Consider splitting or filtering

## Integration Points

### LangChain Client

```python
from langchain_client import LangChainClient, CallConfig

client = LangChainClient(
    model="claude-sonnet-4-5-20250929",
    monthly_budget=50.0,
    daily_budget=5.0,
)

config = CallConfig(
    timeout=45.0,
    max_tokens=3000,
    temperature=0.2,
    extended_thinking=True,
    thinking_budget=8000,
)

response = await client.generate(prompt, system_prompt, config)
```

### OpenTelemetry Logger

Project uses OTEL-formatted logging:

```python
# In project code
logger.error(
    "Failed to connect",
    extra={
        "trace_id": get_current_trace_id(),
        "span_id": get_current_span_id(),
    }
)
```

**Formatter** (in logging config):
```python
{
    "format": "%(asctime)s - [trace:%(trace_id)s | span:%(span_id)s] - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"
}
```

## Error Scenarios

### Parsing Failures

**Invalid log format:**
```python
# Unmatched line (not OTEL format)
entry = parser.parse_line(line)  # Returns None

# Analyzer skips invalid lines
# Total entries count will be < file line count
```

**Partial traces:**
```python
# Logs rotated mid-trace
# Some logs have trace ID, others don't

# Result: Incomplete trace, missing context
# Solution: Check log rotation settings
```

### LLM Failures

**AI analysis timeout:**
```python
# 45 second timeout reached
# Returns: "LLM analysis failed"

# Fallback: Use --no-ai for quick parsing
```

**Budget exceeded:**
```python
# Daily or monthly budget hit
# Client returns error

# Solution: Increase budget or use --no-ai
```

### File Access

**Log file not found:**
```bash
Error: Log file not found: logs/your_project.log

# Check file exists
ls logs/your_project.log
```

**Permission denied:**
```bash
# Make script executable
chmod +x .claude/tools/utils/log_analyzer.py
```

## Extension Points

### Custom Parsers

```python
class CustomLogParser(OTelLogParser):
    """Custom parser for different log format."""

    LOG_PATTERN = re.compile(r"your_custom_pattern")

    def parse_line(self, line: str) -> LogEntry | None:
        # Custom parsing logic
        pass
```

### Custom Extractors

```python
class CustomErrorExtractor(ErrorExtractor):
    """Extract specific error types."""

    def extract_error_contexts(self, traces):
        # Custom extraction logic
        # E.g., only Neo4j errors
        pass
```

### Custom Formatters

```python
class LogAnalyzer:
    def _format_custom(self, report: AnalysisReport) -> str:
        """Custom output format."""
        # E.g., HTML report, CSV, etc.
        pass
```

## Related Files

- **Main implementation:** `.claude/tools/utils/log_analyzer.py`
- **Usage examples:** `.claude/tools/utils/example_usage.py`
- **LangChain client:** `.claude/tools/langchain_client.py`
- **Log file:** `logs/your_project.log`
- **SKILL.md:** This skill's main documentation

## Version History

**Current version:** 1.0.0 (2025-10-16)

**Features:**
- OpenTelemetry log parsing
- Trace reconstruction
- Error context extraction
- AI-powered analysis
- Multiple output formats
- Filtering (error ID, trace ID, file)
- Budget tracking
- Call chain summarization
