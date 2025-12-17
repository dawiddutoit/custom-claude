# Log Analysis Response Template

Use this template when reporting log analysis findings to users.

## Template 1: Summary Response (Quick Health Check)

```
Analyzed logs from {TIME_RANGE}

**Status:** {HEALTHY | ISSUES_FOUND}

**Summary:**
- Total log entries: {COUNT}
- Total traces: {COUNT}
- Errors found: {COUNT}
- Files affected: {COUNT}

{IF ERRORS:}
**Critical Issues:**
1. {ERROR_TYPE} in {FILE}:{LINE}
   - {BRIEF_DESCRIPTION}
   - Trace: {TRACE_ID_SHORT}
   - Occurrences: {COUNT}

2. {ERROR_TYPE} in {FILE}:{LINE}
   - {BRIEF_DESCRIPTION}
   - Trace: {TRACE_ID_SHORT}
   - Occurrences: {COUNT}

**Recommended Actions:**
1. {ACTION_1}
2. {ACTION_2}

**To investigate further:**
- View error details: `python3 .claude/tools/utils/log_analyzer.py --error-id {N} --format markdown`
- See full trace: `python3 .claude/tools/utils/log_analyzer.py --trace {TRACE_ID} --format markdown`
```

**Example:**
```
Analyzed logs from 2025-10-16 14:30:00 to 2025-10-16 14:35:00

**Status:** ISSUES_FOUND

**Summary:**
- Total log entries: 1,523
- Total traces: 12
- Errors found: 7
- Files affected: 4

**Critical Issues:**
1. Neo4j Connection Failure in neo4j_client.py:123
   - Database server not running or unreachable
   - Trace: a1b2c3d4
   - Occurrences: 3 (initial + 2 retries)

2. Missing Configuration in settings.py:45
   - Required parameter 'api_key' not found
   - Trace: d4e5f6g7
   - Occurrences: 1

**Recommended Actions:**
1. Start Neo4j: `neo4j start`
2. Add API_KEY to .env file

**To investigate further:**
- View error details: `python3 .claude/tools/utils/log_analyzer.py --error-id 1 --format markdown`
- See full trace: `python3 .claude/tools/utils/log_analyzer.py --trace a1b2c3d4e5f6g7h8 --format markdown`
```

---

## Template 2: Detailed Error Response

```
**Error Analysis:** {ERROR_TYPE}

**Location:** {FILE}:{LINE} in {FUNCTION}()
**Trace ID:** {TRACE_ID}
**Timestamp:** {TIMESTAMP}

**What happened:**
{DESCRIPTION_FROM_CALL_CHAIN}

**Full error message:**
```
{FULL_ERROR_MESSAGE}
```

**Call chain:**
1. {ENTRY_POINT} - {DESCRIPTION}
2. {STEP_2} - {DESCRIPTION}
...
N. {ERROR_LOCATION} - ERROR

**Root cause:**
{ROOT_CAUSE_FROM_CONTEXT}

**Fix:**
{STEP_BY_STEP_FIX}

{IF STACK_TRACE:}
**Stack trace:**
```
{STACK_TRACE}
```

{IF RELATED_ERRORS:}
**Related errors in same trace:**
- {ERROR_2}
- {ERROR_3}
```

**Example:**
```
**Error Analysis:** Neo4j Connection Failure

**Location:** neo4j_client.py:123 in connect()
**Trace ID:** a1b2c3d4e5f6g7h8
**Timestamp:** 2025-10-16 14:32:15

**What happened:**
1. automatic_indexing() [deprecated] was called
2. System loaded configuration (bolt://localhost:7687)
3. Attempted to connect to Neo4j
4. Connection timed out after 5 seconds
5. Retry logic triggered twice (both failed)

**Full error message:**
```
Failed to connect to Neo4j at bolt://localhost:7687: Connection timeout after 5s. Ensure Neo4j is running and accessible.
```

**Call chain:**
1. initialize.py:23 - automatic_indexing() [deprecated] - Starting initialization
2. config.py:45 - load_config() - Loading configuration
3. database.py:12 - initialize_database() - Setting up database
4. neo4j_client.py:101 - connect() - Attempting connection
5. neo4j_client.py:123 - ERROR: Connection timeout

**Root cause:**
Neo4j database server is not running on the expected port (7687).

**Fix:**
1. Check Neo4j status:
   ```bash
   neo4j status
   ```

2. If not running, start it:
   ```bash
   neo4j start
   # OR use Neo4j Desktop
   ```

3. Verify connection:
   ```bash
   cypher-shell -a bolt://localhost:7687 -u neo4j -p password
   ```

4. Re-run initialization:
   ```bash
   # Your operation here
   ```

**Related errors in same trace:**
- neo4j_client.py:145 - Retry attempt 1 failed
- neo4j_client.py:145 - Retry attempt 2 failed
```

---

## Template 3: Trace Analysis Response

```
**Trace Analysis:** {TRACE_ID}

**Duration:** {DURATION_SECONDS}s
**Entry Point:** {ENTRY_POINT_FUNCTION}
**Errors:** {ERROR_COUNT}

**Timeline:**
{TIMESTAMP_1} - {EVENT_1}
{TIMESTAMP_2} - {EVENT_2}
{TIMESTAMP_3} - ERROR: {ERROR_1}
{TIMESTAMP_4} - Recovery: {RECOVERY_ATTEMPT_1}
{TIMESTAMP_5} - ERROR: {ERROR_2}

**What this trace shows:**
{INTERPRETATION_OF_EXECUTION_FLOW}

**All errors in this trace:**
1. {ERROR_1} - {FILE}:{LINE}
   - {MESSAGE}

2. {ERROR_2} - {FILE}:{LINE}
   - {MESSAGE}

**Root cause:**
{UNIFIED_ROOT_CAUSE_FOR_TRACE}

**Fix:**
{CONSOLIDATED_FIX_FOR_ALL_ERRORS_IN_TRACE}
```

**Example:**
```
**Trace Analysis:** a1b2c3d4e5f6g7h8

**Duration:** 5.23s
**Entry Point:** automatic_indexing() [deprecated]
**Errors:** 3

**Timeline:**
14:32:15 - Repository initialization started
14:32:15 - Configuration loaded successfully
14:32:15 - Attempting Neo4j connection
14:32:20 - ERROR: Connection timeout (5s)
14:32:20 - Retry attempt 1 triggered
14:32:22 - ERROR: Retry 1 failed
14:32:22 - Retry attempt 2 triggered
14:32:25 - ERROR: Retry 2 failed
14:32:25 - Initialization aborted

**What this trace shows:**
The system correctly attempted to initialize the repository, loaded configuration successfully, but failed at the database connection step. The retry logic worked as designed (2 automatic retries), but all attempts failed due to the same underlying issue.

**All errors in this trace:**
1. neo4j_client.py:123 - connect()
   - Failed to connect to Neo4j: Connection timeout after 5s

2. neo4j_client.py:145 - retry_connection()
   - Retry attempt 1 failed: Connection still unavailable

3. neo4j_client.py:145 - retry_connection()
   - Retry attempt 2 failed: Connection still unavailable

**Root cause:**
Neo4j database is not running. All three errors are symptoms of this single issue.

**Fix:**
Start Neo4j and retry initialization:
```bash
# Start Neo4j
neo4j start

# Wait for startup
sleep 5

# Verify it's running
neo4j status

# Retry your operation
```
```

---

## Template 4: File-Specific Analysis Response

```
**File Analysis:** {FILE_NAME}

**Errors found:** {ERROR_COUNT}
**Time range:** {TIME_RANGE}
**Affected traces:** {TRACE_COUNT}

**Error breakdown:**
1. Line {LINE_1} - {FUNCTION_1}() - {COUNT_1} occurrences
   - {MESSAGE_1}
   - First seen: {TIMESTAMP_1}
   - Last seen: {TIMESTAMP_2}

2. Line {LINE_2} - {FUNCTION_2}() - {COUNT_2} occurrences
   - {MESSAGE_2}
   - First seen: {TIMESTAMP_3}

**Patterns identified:**
{PATTERNS_IN_THIS_FILE}

**Recommended fixes for {FILE_NAME}:**
{FILE_SPECIFIC_FIXES}
```

**Example:**
```
**File Analysis:** neo4j_client.py

**Errors found:** 5
**Time range:** 2025-10-16 14:30:00 to 14:35:00
**Affected traces:** 2

**Error breakdown:**
1. Line 123 - connect() - 2 occurrences
   - Failed to connect to Neo4j: Connection timeout
   - First seen: 14:32:15
   - Last seen: 14:34:20

2. Line 145 - retry_connection() - 3 occurrences
   - Retry attempts failed: Connection still unavailable
   - First seen: 14:32:17

**Patterns identified:**
- All errors are connection-related
- Retry logic is triggering correctly
- Same timeout value (5s) across all attempts
- Errors occur in 2 different traces (2 separate executions both failed)

**Recommended fixes for neo4j_client.py:**
1. Add health check before connection attempts:
   ```python
   def connect(self):
       if not self._is_neo4j_available():
           raise ServiceUnavailable("Neo4j not running")
       # ... existing connection logic
   ```

2. Implement exponential backoff for retries:
   ```python
   # Current: Fixed 2 retries
   # Suggested: Exponential backoff (1s, 2s, 4s)
   ```

3. Add more descriptive error messages:
   ```python
   # Include port, host, and troubleshooting steps
   ```
```

---

## Template 5: Pattern Recognition Response (AI Analysis)

```
**AI-Powered Pattern Analysis**

**Root Causes Identified:**
1. {ROOT_CAUSE_1}
   - Affects: {AFFECTED_COMPONENTS}
   - Evidence: {SUPPORTING_EVIDENCE}
   - Impact: {IMPACT_DESCRIPTION}

2. {ROOT_CAUSE_2}
   - Affects: {AFFECTED_COMPONENTS}
   - Evidence: {SUPPORTING_EVIDENCE}
   - Impact: {IMPACT_DESCRIPTION}

**Cross-Trace Patterns:**
{PATTERNS_ACROSS_MULTIPLE_TRACES}

**Priority Ranking:**
1. **CRITICAL:** {ISSUE_1} - {WHY_CRITICAL}
2. **HIGH:** {ISSUE_2} - {WHY_HIGH}
3. **MEDIUM:** {ISSUE_3} - {WHY_MEDIUM}

**Recommended Fixes (in priority order):**
1. {FIX_1_WITH_FILE_LINE_REFERENCES}
2. {FIX_2_WITH_FILE_LINE_REFERENCES}
3. {FIX_3_WITH_FILE_LINE_REFERENCES}

**Systemic Issues:**
{ARCHITECTURAL_OR_DESIGN_ISSUES_IDENTIFIED}

**Prevention Recommendations:**
{HOW_TO_PREVENT_THESE_ERRORS_GOING_FORWARD}
```

**Example:**
```
**AI-Powered Pattern Analysis**

**Root Causes Identified:**
1. Missing External Dependencies
   - Affects: neo4j_client.py, database initialization
   - Evidence: 5 connection timeout errors across 2 traces
   - Impact: Complete system failure - no database operations possible

2. Configuration Validation Gap
   - Affects: settings.py, initialization flow
   - Evidence: Missing required parameters not caught until runtime
   - Impact: Delayed error discovery, poor user experience

**Cross-Trace Patterns:**
- Multiple traces failing at same initialization step (database connection)
- Retry logic working correctly but can't overcome root cause
- Configuration loads successfully but missing required external dependencies

**Priority Ranking:**
1. **CRITICAL:** Neo4j dependency check - System cannot function without database
2. **HIGH:** Configuration validation - Should fail fast at startup, not mid-execution
3. **MEDIUM:** Error messaging - Current errors could be more actionable

**Recommended Fixes (in priority order):**
1. Add dependency health checks (neo4j_client.py:90):
   ```python
   @classmethod
   def check_neo4j_available(cls, uri: str) -> bool:
       """Check if Neo4j is running before attempting connection."""
       # Implementation here
   ```

2. Enhance config validation (settings.py:30):
   ```python
   def validate_external_dependencies(self):
       """Validate all external services are available."""
       # Check Neo4j, API endpoints, etc.
   ```

3. Improve error messages (neo4j_client.py:123):
   ```python
   # Current: "Connection timeout after 5s"
   # Better: "Connection timeout after 5s. Is Neo4j running? Check with: neo4j status"
   ```

**Systemic Issues:**
- **No Pre-Flight Checks:** System doesn't verify external dependencies before starting
- **Delayed Validation:** Configuration validated but external services not checked
- **Retry Without Context:** Retry logic doesn't check if retrying will help

**Prevention Recommendations:**
1. Add startup health check suite that validates:
   - Neo4j connectivity
   - Required configuration parameters
   - External API availability

2. Implement fail-fast principle:
   - Check all dependencies at startup
   - Fail immediately with actionable errors
   - Don't retry operations that can't succeed

3. Enhance observability:
   - Add metrics for connection failures
   - Alert on repeated retry patterns
   - Track time-to-failure for dependency issues
```

---

## Template 6: Real-Time Monitoring Response

```
**Real-Time Log Monitoring**

Currently watching: {LOG_FILE}
Started at: {START_TIME}

**Recent Activity (last {N} entries):**
{RECENT_LOG_ENTRIES}

**Errors detected (last {N} minutes):**
{RECENT_ERRORS}

**To stop monitoring:** Press Ctrl+C

**Commands:**
# View summary:        python3 .claude/tools/utils/log_analyzer.py {{LOG_DIR}}/{{LOG_FILE}}.log
# Filter errors only:  tail -f {{LOG_DIR}}/{{LOG_FILE}}.log | grep ERROR
# Filter specific:     tail -f {{LOG_DIR}}/{{LOG_FILE}}.log | grep "{PATTERN}"
```

---

## Template 7: No Errors Found Response

```
**Log Analysis Complete**

**Status:** ✓ HEALTHY

**Summary:**
- Analyzed {ENTRY_COUNT} log entries
- Time range: {TIME_RANGE}
- Total traces: {TRACE_COUNT}
- **No errors found**

**Recent activity:**
{SUMMARY_OF_INFO_LEVEL_LOGS}

The system appears to be functioning normally. All operations completed successfully.
```

**Example:**
```
**Log Analysis Complete**

**Status:** ✓ HEALTHY

**Summary:**
- Analyzed 1,234 log entries
- Time range: 2025-10-16 14:00:00 to 14:30:00
- Total traces: 8
- **No errors found**

**Recent activity:**
- 3 repository initialization operations (all successful)
- 42 file indexing operations (all successful)
- 12 code search queries (all successful)
- Average operation time: 1.2s

The system appears to be functioning normally. All operations completed successfully.
```

---

## Template 8: Comparison Response (Before/After Fix)

```
**Log Comparison: Before vs After Fix**

**Before fix:**
- Errors: {ERROR_COUNT_BEFORE}
- Failed traces: {FAILED_TRACE_COUNT_BEFORE}
- Most common error: {MOST_COMMON_ERROR_BEFORE}

**After fix:**
- Errors: {ERROR_COUNT_AFTER}
- Failed traces: {FAILED_TRACE_COUNT_AFTER}
- Most common error: {MOST_COMMON_ERROR_AFTER}

**Improvement:**
- Error reduction: {PERCENTAGE_REDUCTION}%
- Success rate: {SUCCESS_RATE_BEFORE}% → {SUCCESS_RATE_AFTER}%

{IF ERRORS_AFTER > 0:}
**Remaining issues:**
{REMAINING_ERRORS_SUMMARY}
```

**Example:**
```
**Log Comparison: Before vs After Neo4j Fix**

**Before fix (14:00-14:30):**
- Errors: 15
- Failed traces: 5 out of 5 (0% success)
- Most common error: Neo4j connection timeout

**After fix (14:30-15:00):**
- Errors: 0
- Failed traces: 0 out of 8 (100% success)
- Most common error: None

**Improvement:**
- Error reduction: 100%
- Success rate: 0% → 100%

All initialization operations now completing successfully. Fix confirmed working.
```

---

## Usage Guidelines

**Choose template based on context:**

1. **Template 1 (Summary):** User asks "check the logs" or "any errors?"
2. **Template 2 (Detailed Error):** User asks about specific error or needs deep dive
3. **Template 3 (Trace Analysis):** Multiple related errors in same trace
4. **Template 4 (File-Specific):** User asks about specific file or component
5. **Template 5 (AI Analysis):** Complex issues requiring pattern recognition
6. **Template 6 (Real-Time):** User is actively testing/debugging
7. **Template 7 (No Errors):** Clean logs, everything working
8. **Template 8 (Comparison):** Validating a fix worked

**Customization:**
- Replace {PLACEHOLDERS} with actual values
- Adjust detail level based on user needs
- Include code snippets for fixes
- Add relevant file:line references
- Link to related documentation

**Tone:**
- Clear and actionable
- Focus on "what" and "how to fix"
- Provide specific commands
- Explain root causes, not just symptoms
