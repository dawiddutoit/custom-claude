# jira-tool CLI - Quick Reference

## Most Common Operations

### Search & Discovery

```bash
# Get total ticket count
jira-tool search 'project=WPCW' --stats

# Find export-related tickets
jira-tool search 'project=WPCW AND (summary~"export" OR summary~"oracle")'

# List all epics
jira-tool epics --project WPCW

# Get epic with children
jira-tool epic-details WPCW-370

# Search by status
jira-tool search 'project=WPCW AND status="In Progress"'

# Search by assignee
jira-tool search 'project=WPCW AND assignee=currentUser()'

# Complex JQL
jira-tool search 'project=WPCW AND (status="To Do" OR status="In Progress") AND assignee=currentUser() ORDER BY priority DESC'
```

### Export Data for Analysis

```bash
# Export all tickets to JSON Lines (best for processing)
jira-tool export --project WPCW --all --format jsonl -o tickets.jsonl

# Then process with jq:
jq -r 'select(.fields.status.name == "To Do") | .key' tickets.jsonl

# Export to CSV for spreadsheets
jira-tool export --project WPCW --all --format csv -o tickets.csv

# Export with changelog (for state analysis)
jira-tool export --project WPCW --expand changelog --format json -o issues.json

# Count tickets by status
jq -r '.fields.status.name' tickets.jsonl | sort | uniq -c
```

### Create Tickets

```bash
# Create epic with formatted description
jira-tool create --project WPCW --type Epic \
  --summary "Daily CSV Export" \
  --description "$(cat <<'EOF'
Epic for CSV export functionality with automated scheduling.

**Goal:** Export supplier charge data to CSV daily

**Components:**
- Cloud Scheduler configuration
- Export service implementation
- CSV formatting logic
EOF
)"

# Create story under epic
jira-tool create --project WPCW --type Story \
  --summary "Configure Cloud Scheduler" \
  --parent WPCW-370 \
  --description "Set up Cloud Scheduler to trigger daily at 2 AM UTC"

# Create sub-task
jira-tool create --project WPCW --type Sub-task \
  --summary "Add timezone handling" \
  --parent WPCW-371

# Create with assignee
jira-tool create --project WPCW --type Story \
  --summary "Implement retry logic" \
  --assignee "email@example.com"
```

### Get Ticket Details

```bash
# Rich formatted output (default)
jira-tool get WPCW-370

# JSON output for processing
jira-tool search 'key=WPCW-370' --format json

# Get with specific fields
jira-tool get WPCW-370 --fields summary,status,assignee
```

### Update Tickets

```bash
# Update status
jira-tool update WPCW-370 --status "In Progress"

# Add comment
jira-tool comment WPCW-370 "Started implementation"

# View available transitions
jira-tool transitions WPCW-370
```

## Output Formats

The `--format` flag controls output style:

```bash
# Table (default, for console viewing)
jira-tool search 'project=WPCW' --format table

# JSON (pretty-printed, small datasets)
jira-tool search 'project=WPCW' --format json

# JSONL (one per line, large datasets)
jira-tool export --project WPCW --all --format jsonl -o file.jsonl

# CSV (spreadsheet-compatible)
jira-tool export --project WPCW --all --format csv -o file.csv
```

**Format Selection Guide:**
- **Table**: Console viewing only (not saveable)
- **JSON**: Readability, small-to-medium datasets
- **JSONL**: Large datasets, streaming, line-by-line processing (RECOMMENDED for >100 tickets)
- **CSV**: Spreadsheet analysis, non-technical users

## Common JQL Patterns

```bash
# My open tickets
jira-tool search 'assignee=currentUser() AND status!="Done"'

# Recently updated
jira-tool search 'project=WPCW AND updated >= -7d'

# High priority blockers
jira-tool search 'priority in (Highest, High) AND status="Blocked"'

# Tickets without assignee
jira-tool search 'project=WPCW AND assignee is EMPTY'

# Epics with children
jira-tool search 'project=WPCW AND type=Epic' --expand subtasks

# Text search across summary and description
jira-tool search 'project=WPCW AND text~"authentication"'
```

## Workflow Analysis

State duration analysis requires changelog:

```bash
# Step 1: Export with changelog
jira-tool export WPCW --expand changelog --format json -o issues.json

# Step 2: Analyze durations
jira-tool analyze state-durations issues.json -o durations.csv

# Open in spreadsheet
open durations.csv  # macOS
```

The CSV contains:
- Issue key
- State name
- Start date/time
- End date/time
- Duration (calendar days)
- Business hours (9 AM - 5 PM, weekdays)

## Batch Operations

Create multiple related tickets:

```bash
#!/bin/bash

# Create epic and capture key
EPIC=$(jira-tool create --project WPCW --type Epic \
  --summary "Q1 2026 Features" --format json | jq -r '.key')

# Create stories under epic
for feature in "User Auth" "API Gateway" "Dashboard"; do
  STORY=$(jira-tool create --project WPCW --type Story \
    --summary "$feature" --parent "$EPIC" --format json | jq -r '.key')

  # Create sub-tasks for each story
  for task in "Design" "Implementation" "Testing"; do
    jira-tool create --project WPCW --type Sub-task \
      --summary "$feature - $task" --parent "$STORY"
  done
done

echo "Created epic $EPIC with stories and sub-tasks"
```

## Error Troubleshooting

### "ModuleNotFoundError: No module named 'jira_tool'"

**Cause:** You tried `from jira_tool import ...`

**Solution:** The jira_tool Python module is private/internal. Use `jira-tool` CLI instead.

```bash
# WRONG
python3 -c "from jira_tool import JiraClient"

# RIGHT
jira-tool search 'project=WPCW'
```

### "0 results found" (when tickets exist)

**Debug Steps:**
1. Verify project exists: `jira-tool search 'project=WPCW' --stats`
2. Check JQL syntax with simpler query: `jira-tool search 'key=WPCW-370'`
3. Try without filters: `jira-tool epics --project WPCW`
4. Verify credentials: `echo $JIRA_BASE_URL`

### "jira-tool: command not found"

**Cause:** Tool not installed or not in PATH

**Solution:**
```bash
# Check if installed
which jira-tool

# If not found, install from project directory
cd /path/to/jira-tool
uv sync
uv run jira-tool --version
```

### "Authentication failed" / "401 Unauthorized"

**Debug Steps:**
1. Check environment variables:
   ```bash
   echo $JIRA_BASE_URL
   echo $JIRA_USERNAME
   echo $JIRA_API_TOKEN  # Should show token (careful in shared terminals)
   ```

2. Verify API token is valid:
   - Go to https://id.atlassian.com/manage/api-tokens
   - Check token is active
   - Regenerate if needed

3. Test authentication:
   ```bash
   jira-tool search 'project=WPCW' --stats
   ```

### "curl: option : blank argument"

**Cause:** You tried to use curl with environment variables instead of jira-tool

**Solution:** Use `jira-tool` CLI - it handles authentication automatically

```bash
# WRONG
curl -u "$JIRA_USERNAME:$JIRA_API_TOKEN" "$JIRA_BASE_URL/rest/api/3/search"

# RIGHT
jira-tool search 'project=WPCW'
```

## Environment Setup

Required environment variables:

```bash
# Add to ~/.bashrc or ~/.zshrc
export JIRA_BASE_URL="https://company.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token-here"

# Optional: Set defaults
export JIRA_DEFAULT_PROJECT="WPCW"
export JIRA_DEFAULT_COMPONENT="Supplier Charges"
```

Generate API token:
1. Go to https://id.atlassian.com/manage/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "jira-tool CLI")
4. Copy token and add to environment

## Advanced Tips

### Piping and Filtering

```bash
# Get issue keys only
jira-tool search 'project=WPCW' --format json | jq -r '.issues[].key'

# Count by status
jira-tool export --project WPCW --all --format jsonl -o tickets.jsonl
jq -r '.fields.status.name' tickets.jsonl | sort | uniq -c | sort -rn

# Extract custom fields
jq -r '.fields.customfield_10014' tickets.jsonl  # Epic Link
```

### Watch for Changes

```bash
# Monitor ticket status every 30 seconds
watch -n 30 'jira-tool get WPCW-370 --fields status,assignee'
```

### Bulk Export

```bash
# Export multiple projects
for project in WPCW PROJ AUTH; do
  jira-tool export --project $project --all --format jsonl \
    -o "${project}_tickets.jsonl"
done
```

### JSON vs JSONL Performance

For large datasets (>100 tickets), ALWAYS use JSONL:

```bash
# JSON: Loads entire array in memory (slow for 1000+ tickets)
jira-tool export --project WPCW --all --format json -o tickets.json

# JSONL: Streams one ticket per line (fast for any size)
jira-tool export --project WPCW --all --format jsonl -o tickets.jsonl

# Process JSONL line-by-line
while IFS= read -r line; do
  echo "$line" | jq -r '.key'
done < tickets.jsonl
```

## When to Use jira-ticket-manager Agent

Use the agent for complex operations that jira-tool CLI doesn't support:

```bash
# Agent invocation (via Claude Code)
Task: "Analyze WPCW project and create summary report with dependencies"
Subagent: jira-ticket-manager
```

**Agent capabilities:**
- Multi-ticket analysis and reporting
- Dependency graph creation
- Batch enrichment of epic descriptions
- Complex state transition analysis
- Custom data transformations

**CLI capabilities (use first):**
- Single ticket operations
- Standard searches
- Basic exports
- Epic listing
- Comment management

## See Also

- Main skill documentation: `~/.claude/skills/jira-builders/SKILL.md`
- Project CLAUDE.md: `/path/to/jira-tool/CLAUDE.md`
- Tool selection guide: `~/.claude/skills/jira-builders/references/TOOL_SELECTION.md`
