# Response Templates: Session Log Analysis

## Template Selection Guide

Choose template based on analysis type:

| User Request | Template |
|--------------|----------|
| "What happened in the session?" | [List Mode Summary](#template-1-list-mode-summary) |
| "Why did Claude do X?" | [Decision Investigation](#template-2-decision-investigation) |
| "Why so many tokens?" | [Token Usage Analysis](#template-3-token-usage-analysis) |
| "Why did agent Y fail?" | [Agent Delegation Analysis](#template-4-agent-delegation-analysis) |
| "Claude stopped responding normally" | [Context Exhaustion](#template-5-context-exhaustion) |
| "Why so slow?" | [Performance Investigation](#template-6-performance-investigation) |

---

## Template 1: List Mode Summary

**Use when:** User asks for session overview or "what happened?"

```markdown
Analyzed session {filename} ({message_count} messages):

**Summary:**
- Duration: {duration} minutes
- Main thread: {main_count} messages
- Agent delegations: {sidechain_count} messages ({agent_names})
- Total tokens: {total_tokens:,}
- Estimated cost: ${cost:.2f}

**Token breakdown:**
- Cache creation: {cache_create:,} tokens (${cache_create_cost:.2f})
- Cache read: {cache_read:,} tokens (${cache_read_cost:.2f})
- Output: {output:,} tokens (${output_cost:.2f})
- Cache efficiency: {cache_efficiency}%

**Key observations:**
1. {observation_1}
2. {observation_2}
3. {observation_3}

{optional_concerns}

To investigate further:
- View message {interesting_index}: `python3 .claude/tools/utils/view_session_context.py {filename} --message-index {interesting_index}`
- {additional_commands}
```

**Example:**

```markdown
Analyzed session abc123.jsonl (35 messages):

**Summary:**
- Duration: 18 minutes
- Main thread: 30 messages
- Agent delegations: 5 messages (@unit-tester)
- Total tokens: 287,456
- Estimated cost: $0.78

**Token breakdown:**
- Cache creation: 95,234 tokens ($0.36)
- Cache read: 178,456 tokens ($0.05)
- Output: 13,766 tokens ($0.21)
- Cache efficiency: 65%

**Key observations:**
1. Good cache utilization after initial setup (messages 1-3)
2. Agent delegation at message 15 for unit test creation
3. Context remained manageable (<30k tokens per message)

To investigate further:
- View agent delegation: `python3 .claude/tools/utils/view_session_context.py abc123.jsonl --message-index 15`
```

---

## Template 2: Decision Investigation

**Use when:** User asks "Why did Claude do X?" or needs to understand specific behavior

```markdown
Analyzed Claude's decision at message {message_index}:

**Decision:** {decision_summary}

**Context available at that point:**
- {context_item_1}
- {context_item_2}
- {context_item_3}

**Claude's reasoning (from thinking block):**
> {thinking_excerpt}

**Key factors:**
1. **{factor_1_name}:** {factor_1_explanation}
2. **{factor_2_name}:** {factor_2_explanation}
3. **{factor_3_name}:** {factor_3_explanation}

**Why this decision makes sense:**
{justification}

**Alternative approaches considered:**
{alternatives_if_mentioned}

**Relevant messages in chain:**
- Message {msg1}: {msg1_summary}
- Message {msg2}: {msg2_summary}

To view full context:
`python3 .claude/tools/utils/view_session_context.py {filename} --message-index {message_index}`
```

**Example:**

```markdown
Analyzed Claude's decision at message 12:

**Decision:** Delegated to @unit-tester instead of fixing bug directly

**Context available at that point:**
- Bug report mentioning "intermittent failures"
- Existing test file test_auth.py with limited coverage
- Error logs showing test failures in multiple scenarios
- No clear root cause identified

**Claude's reasoning (from thinking block):**
> "User reported bug in authentication service. Looking at error logs, I see test failures
> in test_auth_handler.py. The bug report mentions 'intermittent failures' which suggests test
> coverage gaps rather than a simple logic error. Without comprehensive test coverage, I can't
> confidently identify root cause. I should delegate to @unit-tester to create systematic test
> coverage first."

**Key factors:**
1. **Intermittent nature:** Suggests environmental or edge case issue, not simple logic bug
2. **Limited test coverage:** Existing tests don't cover all scenarios
3. **Systematic approach:** Need comprehensive testing before fixing

**Why this decision makes sense:**
For intermittent bugs, systematic test coverage is more effective than guessing at fixes.
By creating comprehensive tests first, we can reproduce the issue reliably and identify
the actual root cause. This aligns with debugging best practices.

**Alternative approaches considered:**
Claude could have attempted direct fix, but thinking block shows explicit reasoning against
this: "can't confidently identify root cause" without better tests.

**Relevant messages in chain:**
- Message 10: User reported bug with error logs
- Message 11: Claude analyzed logs, found test gaps
- Message 12: Decided to delegate for systematic testing

To view full context:
`python3 .claude/tools/utils/view_session_context.py session.jsonl --message-index 12`
```

---

## Template 3: Token Usage Analysis

**Use when:** User asks about costs, efficiency, or "why so many tokens?"

```markdown
Token usage analysis for session {filename}:

**Total cost:** ${total_cost:.2f}

**Breakdown:**
- Cache write: {cache_create:,} tokens @ $3.75/MTok = ${cache_create_cost:.2f} ({cache_create_pct}%)
- Cache read: {cache_read:,} tokens @ $0.30/MTok = ${cache_read_cost:.2f} ({cache_read_pct}%)
- Output: {output:,} tokens @ $15.00/MTok = ${output_cost:.2f} ({output_pct}%)

**Cache efficiency:** {cache_efficiency}% ({efficiency_assessment})

{problem_section_if_applicable}

**Optimization opportunities:**
1. {optimization_1}
2. {optimization_2}
3. {optimization_3}

**Estimated savings:** ${estimated_savings:.2f} ({savings_pct}%)

**Commands to investigate:**
- View high-cost messages: `jq 'select(.message.usage.{metric} > {threshold})' {filename}`
- {additional_commands}
```

**Example:**

```markdown
Token usage analysis for session expensive.jsonl:

**Total cost:** $1.23

**Breakdown:**
- Cache write: 185,000 tokens @ $3.75/MTok = $0.69 (56%)
- Cache read: 95,000 tokens @ $0.30/MTok = $0.03 (2%)
- Output: 35,000 tokens @ $15.00/MTok = $0.52 (42%)

**Cache efficiency:** 34% (POOR - target is >80%)

**Problems identified:**

1. **Cache thrashing at messages 15-20**
   - Pattern: Read file → Edit → Read again (6 times)
   - Each cycle: 18k tokens re-cached
   - Wasted: 6 × 18k = 108k tokens ($0.41)

2. **Repeated file reads**
   - src/auth.py read 8 times
   - Each read: 8k tokens
   - Could cache: 7 × 8k = 56k tokens ($0.21)

**Optimization opportunities:**
1. **Use MultiEdit for batch changes** - Combine edits to reduce cache invalidation
2. **Read files once upfront** - Cache large files before editing
3. **Use Grep instead of Read** - For finding specific code, Grep is more efficient

**Estimated savings:** $0.62 (50%)

**Commands to investigate:**
- View thrashing: `python3 .claude/tools/utils/view_session_context.py expensive.jsonl --message-index 16`
- Find repeated reads: `jq -r '.message.content[]? | select(.type == "tool_use" and .name == "Read")' expensive.jsonl`
```

---

## Template 4: Agent Delegation Analysis

**Use when:** User asks about agent usage or "why did agent Y fail/succeed?"

```markdown
Agent delegation analysis for session {filename}:

**Agent: {agent_name}**
- Spawned at: Message {spawn_index} (main thread)
- Sidechain: Messages {sidechain_start}-{sidechain_end}
- Duration: {sidechain_count} messages
- Result: {result_summary}

**Parent context (what main thread had):**
- {parent_context_1}
- {parent_context_2}
- {parent_context_3}

**Agent context (what agent received):**
- {agent_context_1}
- {agent_context_2}
- {agent_context_3}

**Context delta (what agent DIDN'T have):**
- {missing_context_1}
- {missing_context_2}

**Agent's approach:**
{agent_thinking_summary}

**Outcome:**
{outcome_description}

{problem_explanation_if_failed}

**Recommendations:**
1. {recommendation_1}
2. {recommendation_2}

**Commands:**
- View parent delegation: `python3 .claude/tools/utils/view_session_context.py {filename} --message-index {spawn_index}`
- View agent start: `python3 .claude/tools/utils/view_session_context.py {filename} --message-index {sidechain_start}`
```

**Example:**

```markdown
Agent delegation analysis for session multi-agent.jsonl:

**Agent: @unit-tester**
- Spawned at: Message 15 (main thread)
- Sidechain: Messages 16-19
- Duration: 4 messages
- Result: Created comprehensive unit tests (SUCCESS)

**Parent context (what main thread had):**
- Full architecture documentation (ARCHITECTURE.md)
- Service implementation (src/services/auth.py)
- Domain entities and value objects
- Requirements document with edge cases

**Agent context (what agent received):**
- Service implementation (src/services/auth.py)
- Test patterns from cache
- Delegation prompt: "Create unit tests for AuthService"

**Context delta (what agent DIDN'T have):**
- Architecture documentation (layer boundaries)
- Requirements document (edge cases)
- Design rationale from earlier discussion

**Agent's approach:**
Agent focused on code-level testing without architectural context. Created tests for:
- Constructor validation
- Happy path scenarios
- Basic error handling

**Outcome:**
Tests created but missing edge cases mentioned in requirements. Tests passed but
didn't catch integration issues discovered later.

**Why this happened:**
Agent was spawned with minimal context (just the code). The requirements document
and edge case discussion from messages 5-8 weren't included in agent's context window.

**Recommendations:**
1. Include requirements in agent delegation prompt
2. Reference specific edge cases in delegation task
3. Consider using longer-running main thread for complex testing

**Commands:**
- View parent delegation: `python3 .claude/tools/utils/view_session_context.py multi-agent.jsonl --message-index 15`
- View agent start: `python3 .claude/tools/utils/view_session_context.py multi-agent.jsonl --message-index 16`
```

---

## Template 5: Context Exhaustion

**Use when:** User reports "Claude changed behavior" or "stopped providing details"

```markdown
Context window analysis for session {filename}:

**Context exhaustion detected at message {exhaustion_index}**

**Metrics:**
- Total context: {total_context:,} tokens ({pct_of_limit}% of 200k limit)
- Messages in context: {message_count}
- Average per message: {avg_tokens:,} tokens

**Growth pattern:**
- Message {early_index}: {early_context:,} tokens
- Message {mid_index}: {mid_context:,} tokens
- Message {late_index}: {late_context:,} tokens

**What's consuming space:**
1. {consumer_1}: {tokens_1:,} tokens ({pct_1}%)
2. {consumer_2}: {tokens_2:,} tokens ({pct_2}%)
3. {consumer_3}: {tokens_3:,} tokens ({pct_3}%)

**Behavioral changes observed:**
- Message {change_index}: {change_description}
- {claude_adaptation}

**Claude's explicit acknowledgment:**
> {thinking_quote_if_available}

**Solutions:**
1. **Start new session** - Fresh context window
2. **Reduce file reads** - Use targeted Grep instead of full Read
3. **Prune context** - Focus on recent messages
4. {additional_solution}

**Estimated continuation:**
- Remaining capacity: {remaining_tokens:,} tokens
- Can fit approximately: {estimated_messages} more messages

**Commands:**
- View exhaustion point: `python3 .claude/tools/utils/view_session_context.py {filename} --message-index {exhaustion_index}`
```

**Example:**

```markdown
Context window analysis for session long-session.jsonl:

**Context exhaustion detected at message 48**

**Metrics:**
- Total context: 189,450 tokens (95% of 200k limit)
- Messages in context: 48
- Average per message: 3,947 tokens

**Growth pattern:**
- Message 10: 45,230 tokens
- Message 25: 98,670 tokens
- Message 40: 165,340 tokens
- Message 48: 189,450 tokens

**What's consuming space:**
1. Tool results (file reads): 125,000 tokens (66%)
2. User prompts: 35,000 tokens (18%)
3. Assistant responses: 29,450 tokens (16%)

**Behavioral changes observed:**
- Message 42: Started summarizing instead of quoting full code
- Message 45: Switched to file:line references instead of code blocks
- Message 48: Very brief responses (98 tokens vs earlier 400-500)

**Claude's explicit acknowledgment:**
> "Context window is approaching 200k limit (currently at 189k). I need to be more concise.
> Instead of quoting full code blocks, I'll summarize changes and provide file:line references."

**Solutions:**
1. **Start new session** - Fresh context window (recommended)
2. **Use Grep for targeted searches** - Instead of reading full files
3. **Reference previous work** - "As implemented in message 25..." instead of repeating
4. **Check with @statuser** - Assess if new session appropriate

**Estimated continuation:**
- Remaining capacity: 10,550 tokens
- Can fit approximately: 2-3 more messages with current pattern

**Commands:**
- View exhaustion point: `python3 .claude/tools/utils/view_session_context.py long-session.jsonl --message-index 48`
- View earlier context: `python3 .claude/tools/utils/view_session_context.py long-session.jsonl --message-index 25`
```

---

## Template 6: Performance Investigation

**Use when:** User reports slow responses or asks "why did message X take so long?"

```markdown
Performance analysis for message {slow_index}:

**Response time:** ~{estimated_time} seconds

**Breakdown:**
1. **File I/O:** {io_time}s
   {io_details}

2. **Token processing:** {token_time}s
   - Cache creation: {cache_create:,} tokens
   - Cache read: {cache_read:,} tokens
   - Processing overhead: ~{processing_overhead}s

3. **LLM generation:** {generation_time}s
   - Output tokens: {output_tokens:,}

**Session context:**
{session_context_details}

**Execution logs correlation:**
{otel_log_correlation}

**Performance bottlenecks:**
1. {bottleneck_1}
2. {bottleneck_2}

**Optimization opportunities:**
1. {optimization_1}
2. {optimization_2}

**Commands:**
- View slow message: `python3 .claude/tools/utils/view_session_context.py {filename} --message-index {slow_index}`
- Check execution logs: `python3 .claude/tools/utils/log_analyzer.py logs/project-watch-mcp.log`
```

**Example:**

```markdown
Performance analysis for message 25:

**Response time:** ~14 seconds

**Breakdown:**
1. **File I/O:** 9.2s
   - Read large-file-1.py: 2.3s (15,234 tokens)
   - Read large-file-2.py: 2.8s (18,456 tokens)
   - Read large-file-3.py: 2.1s (12,789 tokens)
   - Grep operation: 2.0s (5,521 tokens)

2. **Token processing:** 3.5s
   - Cache creation: 52,000 tokens
   - Cache read: 0 tokens (no cache reuse!)
   - Processing overhead: ~3.5s for 52k new tokens

3. **LLM generation:** 1.3s
   - Output tokens: 456

**Session context:**
- Message 25 had no cached context from previous messages
- All file reads were new (not previously cached)
- This was first time these files were accessed

**Execution logs correlation:**
```
2025-10-19 14:35:12 - Read file: large-file-1.py (2.3s)
2025-10-19 14:35:15 - Read file: large-file-2.py (2.8s)
2025-10-19 14:35:18 - Read file: large-file-3.py (2.1s)
2025-10-19 14:35:21 - Grep pattern in src/ (1.9s)
```

**Performance bottlenecks:**
1. **Cold cache** - 52k tokens processed without cache reuse
2. **Large file reads** - 3 files totaling 46k tokens
3. **Sequential I/O** - Files read one-by-one (9.2s total)

**Optimization opportunities:**
1. **Pre-cache files** - Read commonly-used files earlier in session
   - Example: Read all service files upfront in message 1-2
   - Subsequent messages use cache (90% cost reduction)

2. **Use MCP search** - Instead of reading full files:
   ```python
   # Instead of:
   Read('large-file-1.py')  # 15k tokens
   Read('large-file-2.py')  # 18k tokens

   # Use:
   mcp__project-watch-mcp__search_code({
     'query': 'Service implementations',
     'search_type': 'semantic'
   })
   # Returns relevant excerpts only
   ```

3. **Parallel I/O** - If using custom script, read files concurrently

**Expected improvement:** ~8-10s (60-70% faster)

**Commands:**
- View slow message: `python3 .claude/tools/utils/view_session_context.py session.jsonl --message-index 25`
- Check execution logs: `python3 .claude/tools/utils/log_analyzer.py logs/project-watch-mcp.log --file-specific`
```

---

## Template 7: No Issues Found

**Use when:** Analysis shows healthy session

```markdown
Analyzed session {filename} - No issues detected

**Health metrics:**
✓ Cache efficiency: {cache_efficiency}% (excellent)
✓ Context size: {max_context:,} tokens ({pct_of_limit}% of limit)
✓ Message count: {message_count} (reasonable)
✓ Agent delegations: {delegation_count} (appropriate)

**Token usage:**
- Total cost: ${total_cost:.2f}
- Breakdown: {cache_create_pct}% cache write, {cache_read_pct}% cache read, {output_pct}% output

**Notable patterns:**
- {positive_pattern_1}
- {positive_pattern_2}

This session demonstrates best practices:
1. {best_practice_1}
2. {best_practice_2}
3. {best_practice_3}

{optional_minor_suggestions}
```

**Example:**

```markdown
Analyzed session efficient.jsonl - No issues detected

**Health metrics:**
✓ Cache efficiency: 87% (excellent)
✓ Context size: 42,345 tokens (21% of limit)
✓ Message count: 22 (reasonable)
✓ Agent delegations: 1 (appropriate)

**Token usage:**
- Total cost: $0.52
- Breakdown: 18% cache write, 62% cache read, 20% output

**Notable patterns:**
- MultiEdit used consistently (8 operations vs 1 Write)
- Files pre-cached in messages 1-3, reused throughout
- Single focused agent delegation (@unit-tester)
- Minimal context growth (24k → 42k over 22 messages)

This session demonstrates best practices:
1. **Efficient tool usage** - MultiEdit for batch operations
2. **Smart caching** - Pre-read commonly-used files
3. **Focused delegation** - Single agent for clear subtask
4. **Context management** - Stayed well under limit

Minor suggestions:
- Could use MCP search_code() for file discovery (currently using Grep)
- Agent delegation could include more architectural context
```

---

## Quick Selection Matrix

| Symptom | Likely Issue | Template |
|---------|--------------|----------|
| "Session cost $2+" | Cache thrashing or large output | #3 Token Usage |
| "Claude did unexpected X" | Decision needs investigation | #2 Decision Investigation |
| "Agent failed task" | Context mismatch | #4 Agent Delegation |
| "Responses got shorter" | Context exhaustion | #5 Context Exhaustion |
| "Message took >30s" | I/O or cache issues | #6 Performance |
| "General overview" | - | #1 List Mode Summary |
| All metrics healthy | - | #7 No Issues Found |

---

**Usage notes:**
- Replace `{placeholders}` with actual values
- Include specific file paths and commands
- Provide concrete examples and evidence
- Always give actionable next steps
