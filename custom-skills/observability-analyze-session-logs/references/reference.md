# Technical Reference: Session Log Analysis

## Session File Format Specification

### JSONL Structure

Session files use **JSON Lines** format (`.jsonl`):
- Each line is a complete, valid JSON object
- Lines represent individual messages in chronological order
- No comma between lines (not a JSON array)
- Streamed format (can be parsed incrementally)

**Example:**
```jsonl
{"uuid":"abc","parentUuid":null,"message":{"role":"user","content":"Hello"}}
{"uuid":"def","parentUuid":"abc","message":{"role":"assistant","content":[{"type":"text","text":"Hi"}]}}
```

### Message Object Schema

```typescript
interface SessionMessage {
  uuid: string;                    // Unique message identifier
  parentUuid: string | null;       // Parent message UUID (null for root)
  isSidechain: boolean;            // true for agent executions
  sessionId: string;               // Session identifier
  message: {
    role: "user" | "assistant";
    content: ContentBlock[] | string;
    usage?: TokenUsage;
  };
  timestamp: string;               // ISO 8601 format
}
```

### Content Block Types

#### Text Block
```typescript
interface TextBlock {
  type: "text";
  text: string;
}
```

User messages may have `content` as plain string instead of array.

#### Thinking Block
```typescript
interface ThinkingBlock {
  type: "thinking";
  thinking: string;
}
```

Only present when extended thinking is enabled. Contains Claude's internal reasoning.

#### Tool Use Block
```typescript
interface ToolUseBlock {
  type: "tool_use";
  id: string;
  name: string;              // Tool name (Read, Write, Bash, etc.)
  input: Record<string, any>; // Tool parameters
}
```

#### Tool Result Block
```typescript
interface ToolResultBlock {
  type: "tool_result";
  tool_use_id: string;       // References ToolUseBlock.id
  content: string | ContentBlock[];
  is_error?: boolean;
}
```

### Token Usage Object

```typescript
interface TokenUsage {
  input_tokens: number;                    // New tokens not in cache
  cache_creation_input_tokens: number;     // Tokens added to cache
  cache_read_input_tokens: number;         // Tokens read from cache
  output_tokens: number;                   // Generated response tokens
}
```

**Pricing (as of 2025-10):**
- Input tokens: $3.00 / MTok (Sonnet 4.5)
- Cache write: $3.75 / MTok (25% premium)
- Cache read: $0.30 / MTok (90% discount)
- Output tokens: $15.00 / MTok

**Cache TTL:**
- `ephemeral_5m`: 5 minutes
- `ephemeral_1h`: 1 hour (not visible in session files, inferred from Claude Code behavior)

### Parent-Child Chain Reconstruction

**Algorithm:**
```python
def build_context_chain(messages: list[Message], target_uuid: str) -> list[Message]:
    """Build conversation chain leading to target message."""
    msg_map = {msg.uuid: msg for msg in messages}
    target = msg_map[target_uuid]

    chain = [target]
    current = target

    while current.parent_uuid:
        parent = msg_map.get(current.parent_uuid)
        if not parent:
            break
        chain.insert(0, parent)  # Prepend (oldest first)
        current = parent

    return chain
```

**Example chain:**
```
Root (uuid: A, parent: null)
  ↓
Message B (uuid: B, parent: A)
  ↓
Message C (uuid: C, parent: B)
  ↓
Message D (uuid: D, parent: C)

build_context_chain(messages, "D") → [A, B, C, D]
```

### Sidechain vs Main Thread

**Main thread:**
- `isSidechain: false`
- Direct user ↔ Claude conversation
- Sequential parent-child chain

**Sidechain:**
- `isSidechain: true`
- Agent executions
- Spawned from main thread message
- Separate conversation context

**Example structure:**
```
Main thread:
  User message (uuid: 1, parent: null)
  ↓
  Assistant message (uuid: 2, parent: 1)  [spawns agent]
  ↓
  User message (uuid: 5, parent: 2)

Sidechain (agent):
  User message (uuid: 3, parent: 2, sidechain: true)  [agent prompt]
  ↓
  Assistant message (uuid: 4, parent: 3, sidechain: true)  [agent response]
```

Parent of sidechain message (3) is main thread message (2).

## Data Models

### Message Class

```python
@dataclass
class Message:
    uuid: str
    parent_uuid: str | None
    role: str                    # "user" | "assistant"
    content: list[dict[str, Any]]
    usage: dict[str, Any]
    timestamp: str
    is_sidechain: bool
    line_number: int             # Line in JSONL file (1-based)
```

### Content Formatting

**format_content(max_length: int) -> str:**
- Handles string content (user messages)
- Parses content blocks (assistant messages)
- Truncates long content
- Formats as human-readable text

**Output example:**
```
TEXT: Implement the authentication service...
THINKING: I need to consider the layering...
TOOL: Read(['file_path'])
TOOL_RESULT: (content)
```

### Token Usage Formatting

**format_usage() -> str:**
```python
def format_usage(self) -> str:
    input_tokens = self.usage.get("input_tokens", 0)
    cache_creation = self.usage.get("cache_creation_input_tokens", 0)
    cache_read = self.usage.get("cache_read_input_tokens", 0)
    output_tokens = self.usage.get("output_tokens", 0)

    total_input = input_tokens + cache_creation + cache_read

    return (
        f"Input: {input_tokens:,} | "
        f"Cache Create: {cache_creation:,} | "
        f"Cache Read: {cache_read:,} | "
        f"Output: {output_tokens:,} | "
        f"Total Context: {total_input:,}"
    )
```

**Output example:**
```
Input: 156 | Cache Create: 0 | Cache Read: 15,047 | Output: 182 | Total Context: 15,203
```

## Tool Implementation Details

### view_session_context.py Structure

**Components:**
1. **Message dataclass** - Structured representation of session message
2. **parse_session_file()** - JSONL parsing with error handling
3. **build_context_chain()** - Parent chain reconstruction
4. **display_context_window()** - Full context visualization
5. **display_raw_message_content()** - JSON output for debugging

**Entry point:**
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session_file", type=Path)
    parser.add_argument("--message-index", type=int)
    parser.add_argument("--uuid", type=str)
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--list", action="store_true")

    args = parser.parse_args()
    messages = parse_session_file(args.session_file)

    # ... dispatch to appropriate display function
```

### Parsing Logic

**Error handling:**
```python
try:
    data = json.loads(line)
    messages.append(Message(...))
except json.JSONDecodeError as e:
    print(f"Warning: Failed to parse line {line_num}: {e}", file=sys.stderr)
    continue  # Skip malformed lines
```

**Robustness:**
- Handles empty lines
- Skips malformed JSON
- Provides default values for missing fields
- Continues parsing on errors

### Display Modes

**List mode (`--list`):**
- Compact table format
- Shows all messages with index, role, sidechain status, token usage
- Good for overview and finding message indices

**Context window mode (`--message-index N` or `--uuid`):**
- Reconstructs full conversation chain
- Shows each message with complete content
- Displays token usage and cumulative context size
- Highlights current message

**Raw mode (`--raw`):**
- JSON output of content array
- Exact structure from file
- For programmatic analysis or debugging

**Default (no flags):**
- Context window mode for last message
- Quick way to see final state

## Performance Characteristics

### File Size Limits

**Tested ranges:**
- Small sessions: 10-50 messages (< 100 KB)
- Medium sessions: 100-500 messages (100 KB - 1 MB)
- Large sessions: 500-2000 messages (1-5 MB)

**Performance:**
- Parsing: O(n) where n = number of messages
- Chain reconstruction: O(m) where m = chain length (typically < 50)
- Memory: O(n) - all messages loaded into memory

**Practical limits:**
- Files up to 10 MB parse in < 1 second
- Files > 50 MB may be slow (consider filtering with jq first)

### Optimization Strategies

**For large files:**
```bash
# Filter before parsing (only assistant messages)
jq 'select(.message.role == "assistant")' large-session.jsonl > filtered.jsonl
python3 view_session_context.py filtered.jsonl --list

# Or use message index directly if known
python3 view_session_context.py large-session.jsonl --message-index 1500
```

**For repeated analysis:**
```bash
# Convert to more efficient format
jq -c '{uuid, parent: .parentUuid, role: .message.role, tokens: .message.usage}' \
  session.jsonl > session-summary.jsonl
```

## Token Usage Patterns

### Healthy Patterns

**Good cache utilization:**
```
Message 1: Input: 500   | Cache Create: 25,000 | Cache Read: 0      | Output: 200
Message 2: Input: 100   | Cache Create: 0      | Cache Read: 24,500 | Output: 150
Message 3: Input: 150   | Cache Create: 500    | Cache Read: 24,000 | Output: 180
```

- Message 1: Initial cache population
- Messages 2-3: High cache read (>95% of context)
- Small cache creation (incremental updates)

**Efficient prompting:**
```
Message N: Input: 50 | Cache Create: 0 | Cache Read: 30,000 | Output: 500
```

- Low input tokens (concise prompt)
- High cache read (leveraging context)
- Moderate output (focused response)

### Problematic Patterns

**Cache thrashing:**
```
Message 10: Input: 100 | Cache Create: 18,000 | Cache Read: 5,000  | Output: 200
Message 11: Input: 120 | Cache Create: 17,500 | Cache Read: 6,000  | Output: 180
Message 12: Input: 110 | Cache Create: 18,200 | Cache Read: 4,800  | Output: 210
```

- Repeated high cache creation
- Low cache read
- Indicates context keeps changing (edits, new files)

**Context exhaustion:**
```
Message 40: Input: 1,000 | Cache Create: 5,000 | Cache Read: 180,000 | Output: 500
Total context: 186,000 tokens (approaching 200k limit)
```

- Very high cache read (accumulated context)
- Approaching Claude's 200k token limit
- May cause context pruning or summarization

**Inefficient prompting:**
```
Message N: Input: 5,000 | Cache Create: 0 | Cache Read: 20,000 | Output: 100
```

- Very high input tokens (verbose prompt)
- Low output (didn't utilize the context)
- Wasting tokens on input

### Cost Analysis

**Example session (50 messages):**
```
Total input: 10,000 tokens × $3.00/MTok = $0.03
Total cache write: 100,000 tokens × $3.75/MTok = $0.375
Total cache read: 500,000 tokens × $0.30/MTok = $0.15
Total output: 20,000 tokens × $15.00/MTok = $0.30

Session total: $0.855
```

**Cost optimization:**
- Maximize cache read (90% discount)
- Minimize cache creation (25% premium)
- Reduce output tokens (most expensive)

## Session File Locations

### User-Level Sessions

**Path pattern:**
```
~/.claude/projects/-Users-{username}-{project-path}--claude-logs/{session-uuid}.jsonl
```

**Example:**
```
~/.claude/projects/-Users-dawiddutoit-projects-play-your_project--claude-logs/dab64f62-0256-497e-a23a-224573f349c9.jsonl
```

**Encoding rules:**
- Path separators (`/`) → hyphens (`-`)
- Dots (`.`) → hyphens (`-`)
- Underscores preserved
- Result: `-Users-dawiddutoit-projects-play-your_project--claude-logs`

**How to find:**
```bash
# List all projects
ls ~/.claude/projects/

# Find sessions for specific project
ls -lt ~/.claude/projects/-Users-$(whoami)-*your_project*/*.jsonl

# Find recent sessions across all projects
find ~/.claude/projects -name "*.jsonl" -newermt "2025-10-19" -type f
```

### Project Session Artifacts (Different Format)

**Path pattern:**
```
.claude/artifacts/YYYY-MM-DD/sessions/session-{name}-{uuid}.jsonl
```

**Important:** These use **event-based format**, not Claude transcript format:
```jsonl
{"event": "session_start", "session_id": "...", "prompt": "...", "timestamp": "..."}
{"event": "user_prompt", "session_id": "...", "prompt": "...", "timestamp": "..."}
```

**Not compatible** with `view_session_context.py`. Use for event tracking, not context analysis.

## Advanced Analysis Techniques

### Extracting Specific Content Types

**All thinking blocks:**
```bash
jq -r '.message.content[]? | select(.type == "thinking") | .thinking' session.jsonl
```

**All tool calls:**
```bash
jq -r '.message.content[]? | select(.type == "tool_use") | "\(.name)(\(.input | keys | join(", ")))"' session.jsonl
```

**All user prompts:**
```bash
jq -r 'select(.message.role == "user") | .message.content' session.jsonl
```

### Statistical Analysis

**Token distribution:**
```bash
jq -r '[.message.usage | .input_tokens, .cache_creation_input_tokens, .cache_read_input_tokens, .output_tokens] | @csv' session.jsonl > token-analysis.csv
```

**Message timing:**
```bash
jq -r '[.timestamp, .message.role] | @csv' session.jsonl
```

**Cache efficiency:**
```bash
jq -s '
  map(.message.usage) |
  {
    total_cache_create: map(.cache_creation_input_tokens) | add,
    total_cache_read: map(.cache_read_input_tokens) | add
  } |
  .cache_efficiency = (.total_cache_read / (.total_cache_create + .total_cache_read) * 100)
' session.jsonl
```

### Pattern Detection

**Find expensive messages:**
```bash
jq -r 'select(.message.usage.output_tokens > 1000) |
       "[\(.message.usage.output_tokens) tokens] \(.uuid[:8]): \(.message.content[0].text[:100])"' \
       session.jsonl
```

**Identify delegation points:**
```bash
jq -r 'select(.isSidechain == true) |
       "[\(.message.role)] Parent: \(.parentUuid[:8]) | UUID: \(.uuid[:8])"' \
       session.jsonl
```

**Track context growth:**
```bash
jq -r '.message.usage |
       (.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens) as $total |
       "Context: \($total)"' session.jsonl
```

## Comparison with Other Log Formats

### vs OpenTelemetry Logs

**OpenTelemetry logs** (`logs/your_project.log`):
- Code execution traces
- Function calls, errors, performance
- Shows "what code ran"

**Session logs** (`.jsonl`):
- Claude's context and reasoning
- Thinking blocks, tool calls, token usage
- Shows "what Claude thought"

**Use together:**
- Session: Why Claude made decision X
- OTel: How decision X executed and what happened

### vs Project Session Artifacts

**Project artifacts** (`.claude/artifacts/.../sessions/session-*.jsonl`):
- Event-based format
- Session lifecycle events
- Created/updated by hooks

**User sessions** (`~/.claude/projects/.../*.jsonl`):
- Full Claude transcripts
- Complete message content
- Token usage data

**Use cases:**
- Artifacts: Session tracking, event logging
- User sessions: Context analysis, debugging decisions

## Limitations and Caveats

### File Format Assumptions

**Assumes:**
- Valid JSONL (one JSON object per line)
- Standard message schema (uuid, parentUuid, message, etc.)
- Token usage present in assistant messages

**May fail if:**
- File is corrupted or truncated
- Schema changes in future Claude Code versions
- Very old session files (pre-2025) may have different structure

### Content Truncation

**Tool truncates content in list mode:**
- Text preview: First 500 characters
- Thinking preview: First 500 characters
- Full content available in context window mode

**Reason:** List mode optimized for overview, not detailed reading.

### Memory Requirements

**All messages loaded into memory:**
- 1000 messages ≈ 5-10 MB RAM
- 10000 messages ≈ 50-100 MB RAM

**For very large files:** Consider filtering with jq before loading.

### Cache Token Interpretation

**Cannot determine:**
- Exact cache TTL (5m vs 1h)
- What specific content was cached
- Cache invalidation reasons

**Can only observe:**
- Cache creation amount
- Cache read amount
- Patterns suggesting thrashing

## Future Enhancements

**Potential improvements:**
1. **Incremental parsing** - Stream large files instead of loading all
2. **Cache analysis** - Identify what content is being cached
3. **Diff mode** - Compare two sessions side-by-side
4. **Graph visualization** - Show message chain as tree
5. **Cost calculator** - Estimate session cost from token usage
6. **Export formats** - CSV, HTML report generation
7. **Filter by date range** - Time-based message filtering
8. **Search content** - Full-text search across messages

## References

- **Tool source:** `.claude/tools/utils/view_session_context.py`
- **Claude Code documentation:** (internal to Anthropic)
- **Token pricing:** https://anthropic.com/pricing
- **JSONL format:** https://jsonlines.org/
