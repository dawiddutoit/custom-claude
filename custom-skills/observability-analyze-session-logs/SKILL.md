---
name: observability-analyze-session-logs
description: |
  Analyze Claude Code session transcripts (JSONL files) for context window content, token usage, and decision analysis.
  NOT for application logs (use analyze-logs instead). Use when debugging Claude behavior, investigating token patterns,
  tracking agent delegation, or analyzing context exhaustion. Works with ~/.claude/projects/ session files.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

# Analyze Session Logs

> **IMPORTANT DISTINCTION**: This skill analyzes **Claude Code session transcripts** (what Claude saw and thought), NOT application/production logs (what code executed). For application logs, use the **analyze-logs** skill instead.

## Table of Contents

### Core Sections
- [What This Skill Does](#what-this-skill-does) - Core capabilities and visibility features
- [When to Use This Skill](#when-to-use-this-skill) - Trigger conditions and use cases
- [Quick Start](#quick-start) - Most common commands for immediate use
- [Session File Locations](#session-file-locations) - Where to find Claude transcript files
- [Analysis Workflow](#analysis-workflow) - Complete step-by-step process
  - [Step 1: Locate Session File](#step-1-locate-session-file) - Finding the right session file
  - [Step 2: Choose Analysis Mode](#step-2-choose-analysis-mode) - List, context window, UUID, or raw modes
  - [Step 3: Execute Analysis](#step-3-execute-analysis) - Running the commands
  - [Step 4: Interpret Results](#step-4-interpret-results) - Understanding output for list, context, sidechain, token usage
  - [Step 5: Report Findings](#step-5-report-findings) - Summarizing insights
- [Command Reference](#command-reference) - Basic commands, finding files, advanced analysis
- [Understanding the Output](#understanding-the-output) - Session file structure, content blocks, token breakdown, message chains
- [Best Practices](#best-practices) - 8 recommended practices for effective analysis
- [Common Scenarios](#common-scenarios) - 5 real-world debugging workflows
  - Why did Claude do X?
  - Token usage investigation
  - Agent delegation analysis
  - Context window exhaustion
  - Performance debugging

### Advanced Topics
- [Integration with Other Skills](#integration-with-other-skills) - How this skill complements analyze-logs, debug-test-failures, orchestrate-agents, check-progress-status
- [Troubleshooting](#troubleshooting) - Common errors and solutions
- [Advanced Usage](#advanced-usage) - Session comparison, pattern detection, agent metrics, context optimization
- [Expected Outcomes](#expected-outcomes) - Success examples for list mode, context window mode, common scenarios
- [Supporting Files](#supporting-files) - References, examples, templates
- [Requirements](#requirements) - Tools, session files, dependencies, verification
- [Related Documentation](#related-documentation) - Tool implementation and complementary skills
- [Quick Reference Card](#quick-reference-card) - Command cheat sheet

---

## Purpose

Analyzes Claude Code session transcripts (NOT application logs) to provide forensic visibility into Claude's internal state, decision-making process, context window content, and token usage patterns.

## What This Skill Does

**Analyzes Claude Code session transcripts** (NOT application logs) to provide visibility into Claude's internal state. This is your forensic tool for understanding "why Claude did X" by showing what information Claude had access to at decision points.

**What it reveals:**
- **Context window content** at any point in conversation
- **Token usage breakdown** (input, cache creation, cache read, output)
- **Message chains** (parent-child relationships)
- **Agent delegation patterns** (sidechain vs main thread)
- **Context window growth** over time
- **Thinking blocks** (Claude's internal reasoning)
- **Tool calls** with parameters and results

**Core capabilities:**
- Parse Claude session JSONL transcripts from `~/.claude/projects/`
- Reconstruct conversation flow with parent-child relationships
- Show actual content in context window at specific points
- Track token usage patterns (cache hits, cache creation)
- Distinguish main conversation from agent sidechains
- Debug unexpected Claude behavior by seeing what context was available

**Key Distinction:**
- **This skill (analyze-session-logs)**: Analyzes Claude's session transcripts → Shows "what Claude saw and thought"
- **Different skill (analyze-logs)**: Analyzes OpenTelemetry application logs → Shows "what code executed"
- **Use both together** for complete debugging: Session logs explain Claude's decisions, application logs show execution results

## When to Use This Skill

Invoke this skill when users mention:
- "why did Claude do X?"
- "what was in the context window?"
- "analyze session" / "check session logs"
- "debug Claude behavior"
- "understand what Claude saw"
- "session forensics"
- "token usage investigation"
- "context window exhaustion"
- "track agent delegation"
- "why did agent Y get called?"
- Any mention of `.jsonl` session files

**Use cases:**
1. **Debugging decisions** - "Why did Claude choose approach X?" → View context at decision point
2. **Token analysis** - "Where are tokens being used?" → Track cache creation vs cache read
3. **Agent tracking** - "How are agents being delegated?" → Follow sidechain messages
4. **Context exhaustion** - "Why did Claude lose context?" → See context window growth
5. **Performance issues** - "Why is Claude slow?" → Identify cache thrashing

## Quick Start

**Most common usage (list all messages):**
```bash
python3 .claude/tools/utils/view_session_context.py <session-file.jsonl> --list
```

**View context at specific point (by message index):**
```bash
python3 .claude/tools/utils/view_session_context.py <session-file.jsonl> --message-index 10
```

**View context at specific message (by UUID from logs/errors):**
```bash
python3 .claude/tools/utils/view_session_context.py <session-file.jsonl> --uuid "3c8467d6-..."
```

## Session File Locations

**User-level session files (Claude Code transcripts):**
```
~/.claude/projects/-Users-{username}-{project-path}/{session-uuid}.jsonl
```

**Project session artifacts (event logs - different format):**
```
.claude/artifacts/YYYY-MM-DD/sessions/session-{name}-{uuid}.jsonl
```

**Important:** This skill analyzes **user-level Claude Code transcripts** (contain full message content, token usage). Project session artifacts use a different event-based format.

## Analysis Workflow

### Step 1: Locate Session File

**For recent sessions:**
```bash
# Find most recent user-level session file
ls -lt ~/.claude/projects/-Users-$(whoami)-*/.jsonl | head -5

# Find session files for this project
ls -lt ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/*.jsonl
```

**From error messages or logs:**
- Error logs often include message UUIDs
- Use those UUIDs to search: `grep -r "uuid" ~/.claude/projects/*/`

**From user description:**
- "The session from this morning" → Sort by timestamp
- "The session where we debugged X" → Search session content

### Step 2: Choose Analysis Mode

**Mode 1: List All Messages (Overview)**
```bash
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --list
```

**Output:**
```
Found 42 messages:

  1. [MAIN] 3c8467d6... | user       | Input: 0 | Cache Create: 24,059 | Cache Read: 0 | Output: 0 | Total Context: 24,059
  2. [MAIN] 4f1ba8c3... | assistant  | Input: 156 | Cache Create: 0 | Cache Read: 15,047 | Output: 182 | Total Context: 15,203
  3. [SIDE] bb64a278... | user       | Input: 0 | Cache Create: 18,234 | Cache Read: 0 | Output: 0 | Total Context: 18,234
  4. [SIDE] c9f2d145... | assistant  | Input: 89 | Cache Create: 0 | Cache Read: 12,456 | Output: 234 | Total Context: 12,545
```

**Use when:**
- Initial investigation ("what happened in this session?")
- Finding specific messages (to get message index for deeper analysis)
- Tracking token usage across entire session
- Identifying sidechain (agent) conversations

**Mode 2: Context Window at Specific Point**
```bash
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 10
```

**Output:**
- Complete message chain leading to that point
- Full content of each message (thinking blocks, tool calls, text)
- Token usage for each message
- Total context size
- Parent-child relationships

**Use when:**
- Debugging specific decision ("why did Claude do X at message 10?")
- Understanding what context was available
- Investigating unexpected behavior
- Seeing full thinking blocks

**Mode 3: View Specific Message by UUID**
```bash
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --uuid "3c8467d6-..."
```

**Use when:**
- Error logs reference specific message UUID
- Jumping to exact point from external reference
- Following up on specific message from list mode

**Mode 4: View Raw JSON**
```bash
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 10 --raw
```

**Output:** Raw JSON content array and usage object

**Use when:**
- Need exact JSON structure
- Programmatic analysis
- Debugging the tool itself
- Precise content inspection

### Step 3: Execute Analysis

**Execute the appropriate command using the Bash tool:**

```bash
# Example: List messages to find interesting points
python3 .claude/tools/utils/view_session_context.py ~/.claude/projects/-Users-dawiddutoit-projects-play-project-watch-mcp--claude-logs/abc123.jsonl --list
```

### Step 4: Interpret Results

**For List Output:**
1. **Check message count** - How long was the session?
2. **Identify MAIN vs SIDE** - SIDE indicates agent delegation
3. **Spot token patterns**:
   - High `Cache Create` = New context being cached
   - High `Cache Read` = Good cache utilization
   - High `Cache Create` repeatedly = Cache thrashing (context keeps changing)
4. **Find interesting points** - Large output tokens, sudden cache creation, sidechains
5. **Note message indices** for deeper investigation

**For Context Window Output:**
1. **Review message chain** - Understand conversation flow
2. **Read THINKING blocks** - See Claude's internal reasoning
3. **Check TOOL calls** - What tools were invoked and why
4. **Examine token breakdown**:
   - `Input tokens` = New tokens not in cache
   - `Cache creation` = Tokens being added to ephemeral cache
   - `Cache read` = Tokens retrieved from cache (cost savings)
   - `Output tokens` = Claude's response
5. **Total context size** - Is context window approaching limit?
6. **Parent-child flow** - Follow the conversation thread

**For Sidechain Analysis:**
- **[SIDE]** messages are agent executions
- Find parent in main thread that spawned agent
- Follow agent's execution in sidechain
- See what context agent had access to
- Understand agent's decision-making

**For Token Usage Analysis:**
- **Cache creation spike** = Context changed significantly
- **High cache read** = Good cache utilization (cost effective)
- **Low cache read** = Cache misses (investigate why)
- **Growing total context** = Approaching 200k limit

### Step 5: Report Findings

**Always provide:**
1. **Summary** - Session length, main vs sidechain messages, total tokens
2. **Key insights** - What explains the behavior?
3. **Specific examples** - Quote relevant thinking blocks, tool calls
4. **Context evidence** - Show what Claude had access to
5. **Suggested next steps** - Additional investigation or fixes

**Example response format:**
```
Analyzed session abc123.jsonl (42 messages):

Key Findings:
1. Agent delegation at message 15 (→ unit-tester)
   - Context window at that point: 24,059 tokens
   - Thinking: "Need comprehensive test coverage for new service"
   - Agent had access to service implementation but not architectural context

2. Cache thrashing at messages 28-35
   - Cache creation spiked to 18k tokens each message
   - Context kept changing due to repeated file edits
   - Suggestion: Batch edits to reduce cache invalidation

3. Context exhaustion at message 40
   - Total context: 189,234 tokens (approaching 200k limit)
   - Claude started summarizing instead of quoting full code
   - Explains truncated responses

To investigate further:
- View agent delegation context: python3 ... --message-index 15
- Examine cache thrashing: python3 ... --message-index 30
```

## Command Reference

### Basic Commands

```bash
# List all messages in session
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --list

# View context at specific message index (1-based)
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 10

# View context at specific message UUID
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --uuid "3c8467d6-..."

# View raw JSON content
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 10 --raw

# View latest message (default)
python3 .claude/tools/utils/view_session_context.py <session.jsonl>
```

### Finding Session Files

```bash
# Find most recent session for this project
ls -lt ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/*.jsonl | head -1

# List all sessions
ls -lt ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/

# Find sessions containing specific text
for f in ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/*.jsonl; do
  echo "=== $f ==="
  grep -o "\"content\":\"[^\"]*agent[^\"]*\"" "$f" | head -3
done

# Search by date
find ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/ -name "*.jsonl" -newermt "2025-10-19"
```

### Advanced Analysis

```bash
# Count messages by role
jq -r '.message.role' <session.jsonl> | sort | uniq -c

# Extract all thinking blocks
jq -r '.message.content[] | select(.type == "thinking") | .thinking' <session.jsonl>

# Find all tool calls
jq -r '.message.content[] | select(.type == "tool_use") | "\(.name): \(.input | keys)"' <session.jsonl>

# Calculate total tokens
jq -s 'map(.message.usage | .input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens + .output_tokens) | add' <session.jsonl>

# Find high cache creation points
jq -r 'select(.message.usage.cache_creation_input_tokens > 10000) | "Line \(.message.usage.cache_creation_input_tokens): \(.uuid)"' <session.jsonl>
```

## Understanding the Output

### Session File Structure

Each line in the JSONL file represents a message:

```json
{
  "uuid": "3c8467d6-170e-4cb6-9a6c-6e3f27da5588",
  "parentUuid": "bb64a278-170e-4cb6-9a6c-6e3f27da5588",
  "isSidechain": false,
  "sessionId": "abc123-def456-...",
  "message": {
    "role": "user" | "assistant",
    "content": [...] | "string",
    "usage": {
      "input_tokens": 156,
      "cache_creation_input_tokens": 24059,
      "cache_read_input_tokens": 15047,
      "output_tokens": 182
    }
  },
  "timestamp": "2025-10-19T17:49:25.466Z"
}
```

**Key fields:**
- **uuid**: Unique identifier for this message
- **parentUuid**: UUID of parent message (builds conversation chain)
- **isSidechain**: `true` for agent executions, `false` for main conversation
- **message.role**: "user" or "assistant"
- **message.content**: Array of content blocks (text, thinking, tool_use, tool_result) or string
- **message.usage**: Token usage breakdown
- **timestamp**: When message was created

### Content Block Types

**Text Block:**
```json
{
  "type": "text",
  "text": "Here's the implementation..."
}
```

**Thinking Block (Claude's internal reasoning):**
```json
{
  "type": "thinking",
  "thinking": "I need to consider the edge cases..."
}
```

**Tool Use Block:**
```json
{
  "type": "tool_use",
  "id": "tool_call_id",
  "name": "Read",
  "input": {
    "file_path": "/path/to/file.py"
  }
}
```

**Tool Result Block:**
```json
{
  "type": "tool_result",
  "tool_use_id": "tool_call_id",
  "content": "file contents..."
}
```

### Token Usage Breakdown

**Input Tokens:**
- New tokens not in cache
- User prompts, new tool results
- Cost: Standard input rate

**Cache Creation Input Tokens:**
- Tokens being added to ephemeral cache
- System prompts, context documents, large code files
- Cost: Cache write rate (higher than input)
- Cache TTL: 5 minutes (ephemeral_5m) or 1 hour (ephemeral_1h)

**Cache Read Input Tokens:**
- Tokens retrieved from cache
- Cost: Reduced rate (90% discount)
- Indicates good cache utilization

**Output Tokens:**
- Claude's generated response
- Cost: Output rate (most expensive)

**Total Context:**
- `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`
- Max: 200,000 tokens for Claude Sonnet/Opus

### Message Chain Structure

**Main Thread:**
```
User message 1 (uuid: A, parent: null)
  ↓
Assistant message 1 (uuid: B, parent: A)
  ↓
User message 2 (uuid: C, parent: B)
  ↓
Assistant message 2 (uuid: D, parent: C)
```

**Sidechain (Agent Execution):**
```
Main: Assistant message (uuid: D, parent: C)
  ↓ [spawns agent]
Sidechain: Agent user message (uuid: E, parent: D, isSidechain: true)
  ↓
Sidechain: Agent assistant message (uuid: F, parent: E, isSidechain: true)
```

The tool reconstructs the full chain by following `parentUuid` references.

## Best Practices

### 1. Start with List Mode

Always get the overview first:
```bash
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --list
```

This shows:
- How many messages
- Main vs sidechain distribution
- Token usage patterns
- Where to focus deeper investigation

### 2. Identify Interesting Points

Look for:
- **High cache creation** (>10k tokens) = Context changed significantly
- **[SIDE] messages** = Agent delegations
- **Large output tokens** (>1k) = Comprehensive responses
- **Low cache read** = Cache not being utilized
- **Message clusters** = Rapid back-and-forth

### 3. Use Message Index for Deep Dives

From list output, identify message index, then:
```bash
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 15
```

This shows full context window at that exact point.

### 4. Follow Agent Delegation Chains

When you see `[SIDE]` in list:
1. Find the SIDE message index
2. View that message to see agent context
3. Trace back to parent in main thread
4. Understand what information agent had vs main thread

### 5. Track Token Usage Patterns

**Good patterns:**
- High cache read (>80% of context)
- Stable cache creation (context not changing)
- Low input tokens (efficient prompts)

**Bad patterns:**
- Repeated cache creation (thrashing)
- Low cache read (<50% of context)
- Growing total context (approaching limit)

### 6. Compare Before/After

When debugging changes:
1. Analyze session before fix: `--list`
2. Note token patterns
3. Analyze session after fix: `--list`
4. Compare: Did cache utilization improve? Context size decrease?

### 7. Correlate with Code Execution Logs

**Session logs show "what Claude thought"**
**OpenTelemetry logs show "what code executed"**

Cross-reference:
```bash
# Session: What Claude decided
python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 10

# Execution: What actually ran
python3 .claude/tools/utils/log_analyzer.py logs/project-watch-mcp.log
```

### 8. Save Important Sessions

Archive critical sessions for future reference:
```bash
# Copy to project artifacts
cp ~/.claude/projects/-Users-*/abc123.jsonl \
   .claude/artifacts/$(date +%Y-%m-%d)/sessions/analysis/critical-session.jsonl
```

## Common Scenarios

### Scenario 1: "Why did Claude do X?"

**Workflow:**
1. Find session file (recent or by description)
2. List messages: `--list`
3. Identify message where decision was made
4. View context at that point: `--message-index N`
5. Read THINKING blocks to see reasoning
6. Check what information was in context
7. Explain: "Claude did X because context included Y but not Z"

**Example:**
```bash
# User: "Why did Claude call @unit-tester instead of fixing the bug directly?"

# Step 1: Find session
ls -lt ~/.claude/projects/-Users-$(whoami)-*/abc123.jsonl

# Step 2: List messages
python3 .claude/tools/utils/view_session_context.py abc123.jsonl --list
# Output shows message 12 has text about "delegating to tester"

# Step 3: View context
python3 .claude/tools/utils/view_session_context.py abc123.jsonl --message-index 12

# Analysis shows:
# - Thinking: "Bug is complex, need systematic test coverage"
# - Context includes: Bug report, existing tests
# - Context missing: Root cause analysis
# - Decision: Delegate to @unit-tester for comprehensive testing

# Response: "Claude delegated because the bug report suggested missing test coverage,
# and the context included existing tests showing gaps. Claude's thinking block shows
# it prioritized systematic testing over immediate fix."
```

### Scenario 2: Token Usage Investigation

**Workflow:**
1. List messages to see token breakdown
2. Identify spikes in cache_creation_input_tokens
3. View context at spike points
4. Determine what caused cache invalidation
5. Suggest optimizations

**Example:**
```bash
# User: "Why is this session using so many tokens?"

# Step 1: List with token analysis
python3 .claude/tools/utils/view_session_context.py session.jsonl --list
# Shows: Messages 15-20 each have 18k cache_creation tokens

# Step 2: View one of the spike points
python3 .claude/tools/utils/view_session_context.py session.jsonl --message-index 16

# Analysis shows:
# - Each message includes full file reads (15k tokens each)
# - Files are being edited, invalidating cache
# - Cache recreated every message

# Response: "Token spike caused by repeated file edits (messages 15-20).
# Each edit invalidated the cache, causing 18k tokens to be re-cached.
# Optimization: Batch edits using MultiEdit to reduce cache invalidation."
```

### Scenario 3: Agent Delegation Analysis

**Workflow:**
1. List messages to find sidechains
2. Identify SIDE messages
3. View sidechain context
4. Trace back to parent in main thread
5. Compare context available in main vs sidechain

**Example:**
```bash
# User: "Why did the agent fail to implement the fix correctly?"

# Step 1: List messages
python3 .claude/tools/utils/view_session_context.py session.jsonl --list
# Shows: Messages 8-12 are [SIDE]

# Step 2: View sidechain message
python3 .claude/tools/utils/view_session_context.py session.jsonl --message-index 8

# Analysis shows:
# - Parent message (7) had full architecture context
# - Sidechain message (8) started fresh, missing architecture
# - Agent only had file contents, not design rationale

# Response: "Agent failed because it was spawned at message 8 with only
# immediate file context. The architecture rationale from message 3-5
# wasn't in the agent's context window. Agent couldn't see the 'why'
# behind the design."
```

### Scenario 4: Context Window Exhaustion

**Workflow:**
1. List messages to track context growth
2. Identify where total context approaches 200k
3. View context at exhaustion point
4. Analyze what's consuming space
5. Suggest context optimization

**Example:**
```bash
# User: "Claude stopped quoting full code and started summarizing. Why?"

# Step 1: List messages
python3 .claude/tools/utils/view_session_context.py session.jsonl --list
# Shows: Total context grows from 50k (msg 1) to 189k (msg 40)

# Step 2: View context near limit
python3 .claude/tools/utils/view_session_context.py session.jsonl --message-index 40

# Analysis shows:
# - Context contains 25 previous messages
# - Each includes full tool results (8k tokens each)
# - Total: 189k tokens (95% of 200k limit)

# Response: "Context exhaustion at message 40 (189k/200k tokens).
# Context contains 25 messages with full tool results. Claude adapted
# by summarizing instead of quoting to stay within limit. Consider
# starting new session or pruning old messages."
```

### Scenario 5: Performance Debugging

**Workflow:**
1. List messages to find slow points
2. Identify large cache creation spikes
3. Analyze what caused them
4. Correlate with OpenTelemetry logs

**Example:**
```bash
# User: "Why did message 15 take so long to respond?"

# Step 1: View context at slow message
python3 .claude/tools/utils/view_session_context.py session.jsonl --message-index 15

# Analysis shows:
# - Cache creation: 45k tokens
# - Cache read: 0 tokens
# - Input: 2k tokens
# - Content: Large file reads (5 files, 9k tokens each)

# Step 2: Check execution logs
python3 .claude/tools/utils/log_analyzer.py logs/project-watch-mcp.log --file-specific

# Correlation:
# - Session: 45k cache creation = processing new files
# - Logs: File indexing took 8s
# - Combined: Slow response = large cache creation + file indexing

# Response: "Message 15 slow because: (1) 45k token cache creation
# (5 large files), and (2) file indexing took 8s. Total: ~12s response.
# Optimization: Cache files earlier or reduce file reads."
```

## Integration with Other Skills

### Complements analyze-logs

**analyze-logs** → What code executed (OpenTelemetry traces)
**analyze-session-logs** → What Claude thought (context window)

**Combined workflow:**
1. User reports: "Tests failed unexpectedly"
2. Check execution: `Skill(command: "analyze-logs")` → See test errors
3. Check decision: `Skill(command: "analyze-session-logs")` → See why Claude ran those tests
4. Cross-reference: Test errors + Claude's reasoning = full picture

### Complements debug-test-failures

**debug-test-failures** → Systematic test debugging
**analyze-session-logs** → Why tests were written that way

**Combined workflow:**
1. Tests fail: Use debug-test-failures to fix
2. Tests keep failing: Use analyze-session-logs to see what context was available when tests were written
3. Discovery: Tests were written without seeing full requirements
4. Fix: Provide missing context and regenerate tests

### Complements orchestrate-agents

**orchestrate-agents** → Intelligent agent delegation
**analyze-session-logs** → Track actual delegation patterns

**Combined workflow:**
1. Agent produces unexpected results
2. Use analyze-session-logs to see what context agent received
3. Compare: Expected context vs actual context
4. Fix: Improve agent prompting or context passing

### Complements check-progress-status

**check-progress-status** → What tasks are complete
**analyze-session-logs** → How tasks were completed

**Combined workflow:**
1. User: "How did we get here?"
2. check-progress-status: Shows completed tasks
3. analyze-session-logs: Shows decision points, delegations, context
4. Narrative: Full story of implementation journey

## Troubleshooting

### Error: Session file not found

```bash
# Verify file exists
ls -l ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/

# Check if path is correct (project name encoding)
ls -l ~/.claude/projects/

# Try absolute path
python3 .claude/tools/utils/view_session_context.py $(realpath ~/.claude/projects/-Users-*/abc123.jsonl) --list
```

### Error: No messages found

**Cause:** File is project session artifact (event-based format), not Claude transcript

**Solution:** Use user-level session files instead:
```bash
# Wrong: Project artifact
.claude/artifacts/2025-10-19/sessions/session-name-uuid.jsonl

# Correct: User-level transcript
~/.claude/projects/-Users-*/uuid.jsonl
```

### Error: UUID not found

```bash
# List all UUIDs to find correct one
jq -r '.uuid' session.jsonl | head -20

# Search by timestamp instead
jq -r 'select(.timestamp > "2025-10-19T10:00") | .uuid' session.jsonl
```

### Output shows unknown role and 0 tokens

**Cause:** File format is project event log, not Claude transcript

**Solution:** Find corresponding user-level session file:
```bash
# Get session ID from project artifact
jq -r '.session_id' .claude/artifacts/*/sessions/session-name-uuid.jsonl | head -1

# Find user-level file (UUIDs don't match, search by timestamp)
ls -lt ~/.claude/projects/-Users-*/
```

### Empty thinking blocks

**Cause:** Some messages don't have thinking (user messages, tool results)

**Solution:** Normal behavior. Thinking blocks only in assistant messages with extended thinking enabled.

### Tool crashes on large files

**Cause:** Very long sessions (1000+ messages) can be slow

**Solution:**
```bash
# Use jq to filter first
jq 'select(.message.role == "assistant")' session.jsonl > assistant-only.jsonl
python3 .claude/tools/utils/view_session_context.py assistant-only.jsonl --list

# Or use --message-index directly if you know the target
python3 .claude/tools/utils/view_session_context.py session.jsonl --message-index 500
```

## Advanced Usage

### Session Comparison

Compare token usage between sessions:
```bash
# Session 1 analysis
python3 .claude/tools/utils/view_session_context.py session1.jsonl --list > session1-analysis.txt

# Session 2 analysis
python3 .claude/tools/utils/view_session_context.py session2.jsonl --list > session2-analysis.txt

# Compare
diff session1-analysis.txt session2-analysis.txt

# Or use jq for programmatic comparison
jq -s '{"session1": .[0] | [.message.usage.cache_read_input_tokens] | add,
        "session2": .[1] | [.message.usage.cache_read_input_tokens] | add}' \
   <(jq -s '.' session1.jsonl) <(jq -s '.' session2.jsonl)
```

### Pattern Detection

Find repeated tool calls:
```bash
# Extract all tool calls
jq -r '.message.content[]? | select(.type == "tool_use") | "\(.name)"' session.jsonl | sort | uniq -c | sort -rn

# Find repeated Read operations on same file
jq -r '.message.content[]? | select(.type == "tool_use" and .name == "Read") | .input.file_path' session.jsonl | sort | uniq -c | sort -rn
```

### Agent Performance Metrics

Measure sidechain vs main thread token usage:
```bash
# Main thread tokens
jq -s '[.[] | select(.isSidechain == false) | .message.usage | .input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens + .output_tokens] | add' session.jsonl

# Sidechain tokens
jq -s '[.[] | select(.isSidechain == true) | .message.usage | .input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens + .output_tokens] | add' session.jsonl
```

### Context Optimization Analysis

Find opportunities to reduce context:
```bash
# Find large cache creation events
jq -r 'select(.message.usage.cache_creation_input_tokens > 10000) |
       "[\(.message.usage.cache_creation_input_tokens) tokens] Message \(.uuid[:8]): \(.message.content[0].text[:100])"' \
       session.jsonl

# Identify cache thrashing (repeated creation of similar content)
jq -r '.message.usage.cache_creation_input_tokens' session.jsonl | \
  awk '{sum+=$1; if(NR>1 && $1>10000) thrash++} END {print "Total cache creation:", sum, "| Thrashing events:", thrash}'
```

### Export to Analysis-Friendly Format

Convert to CSV for spreadsheet analysis:
```bash
jq -r '["Index", "Role", "Sidechain", "Input", "CacheCreate", "CacheRead", "Output", "Total"],
       (to_entries | .[] |
        [.key + 1,
         .value.message.role,
         .value.isSidechain,
         .value.message.usage.input_tokens,
         .value.message.usage.cache_creation_input_tokens,
         .value.message.usage.cache_read_input_tokens,
         .value.message.usage.output_tokens,
         (.value.message.usage.input_tokens +
          .value.message.usage.cache_creation_input_tokens +
          .value.message.usage.cache_read_input_tokens)
        ]) |
       @csv' session.jsonl > session-analysis.csv
```

## Expected Outcomes

### Successful Analysis - List Mode

```
Found 42 messages:

  1. [MAIN] 3c8467d6... | user       | Input: 0 | Cache Create: 24,059 | Cache Read: 0 | Output: 0 | Total Context: 24,059
  2. [MAIN] 4f1ba8c3... | assistant  | Input: 156 | Cache Create: 0 | Cache Read: 15,047 | Output: 182 | Total Context: 15,203
  3. [MAIN] 58afc378... | user       | Input: 0 | Cache Create: 1,234 | Cache Read: 14,500 | Output: 0 | Total Context: 15,734
  ...
 15. [SIDE] bb64a278... | user       | Input: 0 | Cache Create: 18,234 | Cache Read: 0 | Output: 0 | Total Context: 18,234
 16. [SIDE] c9f2d145... | assistant  | Input: 89 | Cache Create: 0 | Cache Read: 12,456 | Output: 234 | Total Context: 12,545
```

**Insights:**
- Message 1: Large cache creation (system prompt, context)
- Message 2: Good cache read (15k tokens from cache)
- Message 15-16: Agent delegation (sidechain)

### Successful Analysis - Context Window Mode

```
====================================================================================================
CONTEXT WINDOW AT MESSAGE: 4f1ba8c3-2a8e-4d3f-9c5b-1e7f3a9d6c2b
Line: 2 | Timestamp: 2025-10-19T17:49:25.466Z
Sidechain: False
====================================================================================================

TOTAL MESSAGES IN CONTEXT: 2

────────────────────────────────────────────────────────────────────────────────────────────────────
MESSAGE 1/2
UUID: 3c8467d6-170e-4cb6-9a6c-6e3f27da5588
Parent: (root)
Role: user | Line: 1 | Sidechain: False
Timestamp: 2025-10-19T17:49:15.123Z

TOKEN USAGE: Input: 0 | Cache Create: 24,059 | Cache Read: 0 | Output: 0 | Total Context: 24,059

CONTENT:
TEXT: Implement the new authentication service following Clean Architecture...

────────────────────────────────────────────────────────────────────────────────────────────────────
MESSAGE 2/2 >>> CURRENT MESSAGE <<<
UUID: 4f1ba8c3-2a8e-4d3f-9c5b-1e7f3a9d6c2b
Parent: 3c8467d6-170e-4cb6-9a6c-6e3f27da5588
Role: assistant | Line: 2 | Sidechain: False
Timestamp: 2025-10-19T17:49:25.466Z

TOKEN USAGE: Input: 156 | Cache Create: 0 | Cache Read: 15,047 | Output: 182 | Total Context: 15,203

CONTENT:
THINKING: I need to implement authentication following Clean Architecture. First, I'll create the
domain entities, then application layer handlers, infrastructure implementation, and finally the
interface layer. Let me start by reading the existing code structure...

TOOL: Read(['file_path'])
TOOL_RESULT: (content)

TEXT: I'll implement the authentication service in phases. First, let's create the domain layer...

════════════════════════════════════════════════════════════════════════════════════════════════════
TOTAL CONTEXT SIZE: 39,262 tokens
════════════════════════════════════════════════════════════════════════════════════════════════════
```

**Insights:**
- Context contains 2 messages (user request + assistant response)
- Good cache utilization (15k cache read vs 0 cache create in message 2)
- Thinking block reveals decision process
- Tool calls show Read operation for context
- Total context well under 200k limit

### Common Outcomes

**Scenario: Debugging unexpected delegation**
- Discovery: Agent spawned with minimal context
- Evidence: Sidechain message shows only file contents, missing architecture
- Resolution: Improve delegation prompts to include architectural context

**Scenario: Token usage spike**
- Discovery: Cache thrashing at messages 15-20
- Evidence: Repeated 18k cache_creation due to file edits
- Resolution: Batch edits using MultiEdit to reduce cache invalidation

**Scenario: Context exhaustion**
- Discovery: Context at 189k tokens at message 40
- Evidence: 25 messages with full tool results
- Resolution: Start new session or prune old messages

**Scenario: Performance investigation**
- Discovery: Message 15 has 45k cache creation
- Evidence: 5 large files read simultaneously
- Resolution: Stagger file reads or cache files earlier

## Supporting Files

### Skill Comparison Reference

| Aspect | analyze-session-logs (THIS SKILL) | analyze-logs (DIFFERENT SKILL) |
|--------|-----------------------------------|-------------------------------|
| **Analyzes** | Claude Code session transcripts | OpenTelemetry application logs |
| **File Format** | JSONL (message-by-message) | Structured text (trace spans) |
| **File Location** | `~/.claude/projects/-Users-*/` | `logs/project-watch-mcp.log` |
| **Shows** | What Claude saw and thought | What code executed |
| **Use When** | Debug Claude behavior, token usage | Debug application errors, trace execution |
| **Key Content** | Context window, thinking blocks, tool calls | Trace spans, error details, execution flow |
| **Tool** | `view_session_context.py` | `log_analyzer.py` |
| **Trigger Terms** | "session logs", "what Claude saw", "agent delegation" | "application logs", "trace", "execution flow" |

**Combined Usage**: Use both skills together for complete debugging - session logs explain *why* Claude made decisions, application logs show *what* happened when code executed.

---

This skill follows progressive disclosure with supporting files for depth:

- **[references/reference.md](references/reference.md)** - Technical documentation:
  - Session file format specification (JSONL structure)
  - Data models (Message, ContentBlock types)
  - Parent-child chain reconstruction algorithm
  - Cache token types and pricing
  - Performance characteristics and limits
  - Tool implementation details

- **[templates/response-template.md](templates/response-template.md)** - Response formatting:
  - 6 response templates for different contexts
  - List mode summary template
  - Context window analysis template
  - Agent delegation investigation template
  - Token usage spike template
  - Context exhaustion template
  - No issues found template

## Requirements

**Tools needed:**
- Python 3.12+ (already in project)
- Session viewer tool: `.claude/tools/utils/view_session_context.py` (bundled)
- jq (optional, for advanced analysis): `brew install jq`

**Session files:**
- User-level: `~/.claude/projects/-Users-{username}-{project-path}/{session-uuid}.jsonl`
- Generated automatically by Claude Code during sessions

**Dependencies:**
- Standard library modules (no additional installation needed)
- dataclasses, json, pathlib, typing

**Verification:**
```bash
# Verify tool exists
ls .claude/tools/utils/view_session_context.py

# Verify session files exist
ls -l ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/

# Test the tool
python3 .claude/tools/utils/view_session_context.py \
  $(ls -t ~/.claude/projects/-Users-$(whoami)-projects-play-project-watch-mcp--claude-logs/*.jsonl | head -1) \
  --list
```

## Related Documentation

- **Tool implementation:** `.claude/tools/utils/view_session_context.py`
- **Session workspace guidelines:** `../manage-session-workspace/references/session-workspace-guidelines.md`
- **Complementary skill (OpenTelemetry logs):** `.claude/skills/analyze-logs/SKILL.md`
- **Agent orchestration:** `.claude/skills/orchestrate-agents/SKILL.md`
- **Debugging workflows:** `.claude/skills/debug-test-failures/SKILL.md`

## Quick Reference Card

| Goal | Command |
|------|---------|
| List all messages | `python3 .claude/tools/utils/view_session_context.py <session.jsonl> --list` |
| View context at point | `python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 10` |
| View by UUID | `python3 .claude/tools/utils/view_session_context.py <session.jsonl> --uuid "abc123..."` |
| View raw JSON | `python3 .claude/tools/utils/view_session_context.py <session.jsonl> --message-index 10 --raw` |
| Find recent sessions | `ls -lt ~/.claude/projects/-Users-$(whoami)-*/*.jsonl \| head -5` |
| Count messages | `wc -l <session.jsonl>` |
| Extract thinking | `jq -r '.message.content[]? \| select(.type == "thinking") \| .thinking' <session.jsonl>` |
| Calculate tokens | `jq -s 'map(.message.usage \| add) \| add' <session.jsonl>` |

---

**Key Messages:**
- This skill provides **X-ray vision into Claude's decision-making**
- Use when behavior is unexpected or token usage is unclear
- Complements OpenTelemetry logs (code execution) with context window visibility (what Claude thought)
- Essential for debugging complex agent orchestration
- Start with `--list`, then drill down with `--message-index`

**Remember:** Session logs show what Claude had access to and how it reasoned. This is your forensic tool for understanding "why Claude did X."
