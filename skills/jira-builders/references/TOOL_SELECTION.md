# When to Use Which Jira Tool

## Decision Tree

```
Need to interact with Jira?
│
├─ Single operation (get/search/create/update)?
│  └─→ Use jira-tool CLI (FASTEST, PREFERRED)
│
├─ Batch operations (multiple tickets)?
│  ├─ Simple loop (create 5 related stories)?
│  │  └─→ Shell script with jira-tool CLI
│  │
│  └─ Complex analysis (dependency graphs, reports)?
│     └─→ jira-ticket-manager agent
│
└─ Low-level API operation not in jira-tool?
   └─→ curl + Jira REST API (LAST RESORT)
```

## Available Jira Tools (in priority order)

### 1. jira-tool CLI ⭐ PREFERRED

**When to use:**
- Getting ticket details
- Searching for tickets
- Creating tickets with formatted descriptions
- Exporting ticket data
- Listing epics and their children
- Adding comments
- Updating ticket fields
- Viewing transitions

**Examples:**
```bash
jira-tool get PROJ-123
jira-tool search 'project=WPCW AND text~"export"'
jira-tool epics --project WPCW
jira-tool export --project WPCW --all --format jsonl -o tickets.jsonl
jira-tool create --project WPCW --type Story --summary "Title"
jira-tool comment PROJ-123 "Update message"
jira-tool update PROJ-123 --status "In Progress"
```

**Advantages:**
- Already installed and configured
- Rich formatting (tables, colored output)
- Handles authentication automatically
- Professional description formatting (ADF)
- Supports JSON/JSONL/CSV export
- Fast and reliable
- Stable interface

**Limitations:**
- Single operation at a time
- No complex analysis features
- Limited to supported commands

**How to check if available:**
```bash
jira-tool --version
```

---

### 2. Shell Scripts with jira-tool CLI

**When to use:**
- Creating multiple related tickets
- Batch operations (10-50 tickets)
- Conditional logic based on ticket data
- Data transformation pipelines

**Example:**
```bash
#!/bin/bash
# Create epic with stories

EPIC=$(jira-tool create --project WPCW --type Epic \
  --summary "Q1 Features" --format json | jq -r '.key')

for feature in "Auth" "API" "Dashboard"; do
  jira-tool create --project WPCW --type Story \
    --summary "$feature" --parent "$EPIC"
done
```

**Advantages:**
- Uses familiar shell scripting
- Combines jira-tool with other CLI tools (jq, awk, grep)
- Scriptable and repeatable
- Version controllable

**Limitations:**
- No built-in error handling for Jira-specific issues
- Manual retry logic needed
- Limited analysis capabilities

---

### 3. jira-ticket-manager Agent

**When to use:**
- Complex multi-ticket operations (batch create, enrich epics)
- Ticket analysis and reporting
- State duration analysis
- Dependency management
- When you need autonomous ticket management
- Operations requiring decision-making

**How to invoke:**
Via Claude Code Task tool:
```
User: "Analyze WPCW project and create summary report"
Assistant: [Invokes jira-ticket-manager agent]
```

**Agent capabilities:**
- Multi-step ticket workflows
- Intelligent error handling
- Complex state transition analysis
- Dependency graph creation
- Batch enrichment of descriptions
- Custom data transformations
- Analysis and reporting

**Advantages:**
- Specialized for complex Jira workflows
- Can perform multi-step operations
- Built-in error handling and retry logic
- Decision-making capabilities
- Can use jira-tool CLI internally

**Limitations:**
- Requires Claude Code environment
- More overhead than direct CLI
- Agent invocation adds latency

**When NOT to use:**
- Simple get/search operations (use jira-tool CLI)
- Single ticket creation (use jira-tool CLI)
- Standard exports (use jira-tool CLI)

---

### 4. curl + Jira REST API ⚠️ LAST RESORT

**When to use:**
- jira-tool doesn't support the operation
- Need low-level API access for debugging
- Testing authentication issues
- Accessing undocumented Jira features

**Example:**
```bash
curl -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123"
```

**Issues:**
- Environment variable handling is fragile
- No automatic formatting
- More error-prone
- Requires manual JSON parsing
- No ADF formatting helpers
- Authentication errors harder to debug

**Before using curl, ask yourself:**
1. Does jira-tool support this operation? (Check: `jira-tool --help`)
2. Can jira-ticket-manager agent handle this?
3. Is this truly a low-level API need?

**Common mistakes:**
```bash
# ❌ BAD: Using curl when jira-tool works
curl "$JIRA_BASE_URL/rest/api/3/search?jql=project=WPCW"

# ✅ GOOD: Use jira-tool instead
jira-tool search 'project=WPCW'
```

---

## Decision Matrix

| Operation | Use This | Not This |
|-----------|----------|----------|
| Get single ticket | `jira-tool get` | curl, agent |
| Search tickets | `jira-tool search` | curl, agent |
| Create 1 ticket | `jira-tool create` | agent, curl |
| Create 5 related tickets | Shell script + jira-tool | agent, curl |
| Create 100+ tickets with logic | jira-ticket-manager agent | shell script, curl |
| Export for analysis | `jira-tool export --format jsonl` | curl, manual queries |
| State duration analysis | `jira-tool analyze state-durations` | agent, manual |
| Dependency graph | jira-ticket-manager agent | jira-tool, curl |
| List epics | `jira-tool epics` | search, curl |
| Add comment | `jira-tool comment` | curl, agent |
| Update status | `jira-tool update --status` | curl, transitions + curl |
| Undocumented API feature | curl | jira-tool, agent |

## Common Scenarios

### Scenario 1: "Get details of WPCW-370"
**Use:** `jira-tool get WPCW-370`

**Why:** Single operation, direct CLI is fastest and most reliable.

**Don't use:** curl (fragile), agent (overkill)

---

### Scenario 2: "Search for tickets about export"
**Use:** `jira-tool search 'project=WPCW AND text~"export"'`

**Why:** Built-in JQL support, formatted output.

**Don't use:** curl + manual JQL (error-prone), agent (unnecessary)

---

### Scenario 3: "Create epic with 10 stories"
**Use:** Shell script with jira-tool CLI in loop

```bash
EPIC=$(jira-tool create --type Epic --summary "Title" --format json | jq -r '.key')
for i in {1..10}; do
  jira-tool create --type Story --summary "Story $i" --parent "$EPIC"
done
```

**Why:** Straightforward batch operation, no complex logic needed.

**Don't use:** agent (overkill), curl (too much code)

---

### Scenario 4: "Analyze project and create dependency report"
**Use:** jira-ticket-manager agent

**Why:** Complex analysis, multi-step workflow, decision-making required.

**Don't use:** jira-tool alone (no analysis features), curl (too manual)

---

### Scenario 5: "Export all tickets to CSV for spreadsheet"
**Use:** `jira-tool export --project WPCW --all --format csv -o tickets.csv`

**Why:** Built-in CSV formatting, handles pagination.

**Don't use:** curl + manual pagination, agent (unnecessary)

---

### Scenario 6: "Create tickets from CSV file"
**Use:** Shell script reading CSV with jira-tool CLI

```bash
while IFS=, read -r summary description; do
  jira-tool create --project WPCW --type Story \
    --summary "$summary" --description "$description"
done < tickets.csv
```

**Why:** Simple data transformation, CLI handles Jira formatting.

**Don't use:** Pure curl (complex ADF formatting), agent (not needed)

---

### Scenario 7: "Test new Jira beta API endpoint"
**Use:** curl + Jira REST API

**Why:** Endpoint not in jira-tool yet, need low-level access.

**Don't use:** jira-tool (doesn't support it), agent (may not support it)

---

## Red Flags: You're Using the Wrong Tool

### Red Flag 1: "ModuleNotFoundError: No module named 'jira_tool'"
**Problem:** Trying to import jira_tool Python module

**Solution:** Use `jira-tool` CLI instead

```python
# ❌ WRONG
from jira_tool import JiraClient
client = JiraClient()

# ✅ RIGHT
import subprocess
subprocess.run(['jira-tool', 'get', 'PROJ-123'])
```

---

### Red Flag 2: "curl: option : blank argument"
**Problem:** Using curl with environment variables (fragile)

**Solution:** Use `jira-tool` CLI which handles auth automatically

```bash
# ❌ WRONG
curl -u "$JIRA_USERNAME:$JIRA_API_TOKEN" "$JIRA_BASE_URL/rest/api/3/search"

# ✅ RIGHT
jira-tool search 'project=WPCW'
```

---

### Red Flag 3: Writing manual ADF formatting in shell script
**Problem:** Manually building Atlassian Document Format JSON

**Solution:** Use `jira-tool create` which handles ADF automatically

```bash
# ❌ WRONG (complex ADF JSON)
curl -X POST ... -d '{
  "fields": {
    "description": {
      "type": "doc",
      "version": 1,
      "content": [...]
    }
  }
}'

# ✅ RIGHT (automatic ADF conversion)
jira-tool create --project WPCW --type Story \
  --summary "Title" --description "Simple text converts to ADF"
```

---

### Red Flag 4: Invoking agent for simple get/search
**Problem:** Using jira-ticket-manager agent for single-ticket operations

**Solution:** Use `jira-tool` CLI directly (faster, simpler)

```bash
# ❌ WRONG (overkill)
Task: "Get details of WPCW-370"
Subagent: jira-ticket-manager

# ✅ RIGHT
jira-tool get WPCW-370
```

---

### Red Flag 5: Manual pagination in curl
**Problem:** Writing loop to handle Jira pagination with curl

**Solution:** Use `jira-tool export --all` (handles pagination)

```bash
# ❌ WRONG (manual pagination)
for ((i=0; i<10; i++)); do
  curl "$JIRA_BASE_URL/rest/api/3/search?startAt=$((i*100))&maxResults=100"
done

# ✅ RIGHT (automatic pagination)
jira-tool export --project WPCW --all --format jsonl -o tickets.jsonl
```

---

## Quick Reference

**Default choice for 90% of operations:**
```bash
jira-tool [command] [options]
```

**Check what's available:**
```bash
jira-tool --help
jira-tool search --help
jira-tool create --help
```

**If jira-tool doesn't support it:**
1. Check if agent can help (complex workflow)
2. Last resort: Use curl (low-level API)

**Never do this:**
```python
from jira_tool import ...  # ❌ Module is private/internal
```

**See Also:**
- Quick reference: `~/.claude/skills/jira-builders/references/QUICK_REFERENCE.md`
- Main skill: `~/.claude/skills/jira-builders/SKILL.md`
- Project docs: `/path/to/jira-tool/CLAUDE.md`
