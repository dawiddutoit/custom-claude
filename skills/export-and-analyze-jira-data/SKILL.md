---
name: export-and-analyze-jira-data
description: |
  Export Jira issues with flexible filtering and analyze data using multiple formats (JSON, CSV, JSONL).
  Use when extracting bulk data from Jira, filtering issues, exporting for external analysis, or analyzing
  Jira metrics and trends. Covers export patterns, format selection, pagination, filtering strategies,
  and analysis workflows for large datasets.
  Trigger keywords: "export", "bulk data", "extract data", "filter issues", "analyze", "metrics",
  "CSV export", "JSON format", "large dataset", "streaming", "pagination", "data pipeline",
  "prepare data", "analysis workflow", "save to file", "filter by status".
---

# Export and Analyze Jira Data

## Purpose

Master the art of extracting and analyzing Jira data at scale. Learn how to export issues with complex filters, choose the right data format for your use case (JSON for readability, JSONL for streaming, CSV for spreadsheets), analyze trends and metrics, and integrate data into external tools. This skill covers the complete data pipeline: query → export → transform → analyze → report.

## Quick Start

Export all active issues to CSV:

```bash
uv run jira-tool export --format csv -o tickets.csv
```

Export high-priority issues in JSON for analysis:

```bash
uv run jira-tool export --priority High --status "In Progress" \
  --format json -o important_tickets.json
```

Analyze state durations for a project:

```bash
# Step 1: Export with changelog
uv run jira-tool search "project = PROJ" \
  --expand changelog \
  --format json \
  -o issues_with_history.json

# Step 2: Analyze
uv run jira-tool analyze state-durations issues_with_history.json \
  -o durations.csv --business-hours
```

## Instructions

### Step 1: Understand Export Filters and Query Strategy

Before exporting, define what data you need. Think about:

**1. Scope Dimension**:
- **Project**: Which project? (e.g., `PROJ`, `WPCW`)
- **Date Range**: Created/updated when? (e.g., last 30 days, specific quarter)
- **Status**: What states? (open only, all states, specific workflow stages)
- **Type**: What issue types? (bugs, stories, tasks, all)

**2. Quality Dimension**:
- **Assignee**: Who? (you, unassigned, specific team, all)
- **Priority**: Importance level? (high/medium/low, P0-P3)
- **Labels**: How categorized? (urgent, backend, frontend, etc.)
- **Components**: Which parts of system? (API, UI, Database, etc.)

**3. Complexity Dimension**:
- **Expansion**: Include changelog? (needed for state analysis)
- **Fields**: All fields or specific ones? (optimize for export size)
- **Pagination**: Results within limits? (avoid timeouts on large exports)

**Query Building**:

Simple query (project only):
```bash
uv run jira-tool export --project PROJ --format csv -o all_tickets.csv
```

Complex query with multiple filters:
```bash
uv run jira-tool export \
  --project WPCW \
  --status "In Progress" \
  --priority High \
  --assignee "team-member@company.com" \
  --type Bug \
  --created "2024-01-01" \
  --format json \
  -o filtered_issues.json
```

**Using Custom JQL** (most flexible):
```bash
uv run jira-tool search "project = PROJ AND created >= -30d AND labels = urgent" \
  --format csv \
  -o recent_urgent.csv
```

### Step 2: Choose the Right Export Format

Each format has trade-offs. Choose based on your use case:

**Format 1: CSV (Spreadsheet-Friendly)**
```bash
uv run jira-tool export --format csv -o issues.csv
```

**Best for**:
- Excel/spreadsheet analysis
- Non-technical stakeholders
- Simple tabular data
- Importing to other tools

**Characteristics**:
- Flat structure (one row per issue)
- Limited to top-level fields only
- Easy to sort/filter in Excel
- Lossy (complex data simplified)

**Example output**:
```csv
key,summary,status,assignee,priority,created
PROJ-1,Fix login bug,In Progress,alice@co.com,High,2024-01-15
PROJ-2,Add profile page,To Do,bob@co.com,Medium,2024-01-16
```

---

**Format 2: JSON (Readable, Processable)**
```bash
uv run jira-tool export --format json -o issues.json
```

**Best for**:
- Human-readable processing
- Small-to-medium datasets (< 100MB)
- Pretty-printed output
- Version control/review

**Characteristics**:
- Full nested structure preserved
- All fields included
- Pretty-printed for readability
- Entire file in memory

**Example output**:
```json
{
  "issues": [
    {
      "key": "PROJ-1",
      "fields": {
        "summary": "Fix login bug",
        "status": { "name": "In Progress" },
        "changelog": {
          "histories": [
            {
              "created": "2024-01-15T10:00:00Z",
              "items": [...]
            }
          ]
        }
      }
    }
  ]
}
```

---

**Format 3: JSONL (Streaming-Friendly)**
```bash
uv run jira-tool export --format jsonl -o issues.jsonl
```

**Best for**:
- Large datasets (100MB - GB scale)
- Streaming/processing pipeline
- Line-by-line consumption
- Minimal memory usage

**Characteristics**:
- One JSON object per line
- Perfect for `jq`, `grep`, Python streaming
- Full structure per line
- Process without loading entire file

**Example output**:
```
{"key":"PROJ-1","fields":{"summary":"Fix login bug","status":{"name":"In Progress"}}}
{"key":"PROJ-2","fields":{"summary":"Add profile page","status":{"name":"To Do"}}}
```

**Processing JSONL efficiently**:
```bash
# Count issues
wc -l issues.jsonl

# Filter with jq
jq 'select(.fields.status.name == "In Progress")' issues.jsonl > in_progress.jsonl

# Extract specific field
jq '.key' issues.jsonl | wc -l

# Python streaming
python3 << 'EOF'
import json

total = 0
for line in open('issues.jsonl'):
    issue = json.loads(line)
    if issue['fields']['status']['name'] == 'In Progress':
        total += 1

print(f"In Progress: {total}")
EOF
```

---

**Format 4: Table (Console-Only)**
```bash
uv run jira-tool export --format table
```

**Best for**:
- Quick viewing
- Console output
- Not saving to file

**Characteristics**:
- Rich formatting (colors, alignment)
- Limited fields shown
- Cannot be saved
- Interactive review

---

**Format Comparison**:

| Format | Size | Speed | Readability | Scalability | Use Case |
|--------|------|-------|-------------|-------------|----------|
| CSV | Small | Fast | High | Medium | Excel, simple tools |
| JSON | Large | Medium | High | Small | Processing, review |
| JSONL | Large | Fast | Medium | Very High | Streaming, big data |
| Table | N/A | Fast | Highest | N/A | Quick viewing |

**Decision Tree**:
- Want to open in Excel? → CSV
- Want human-readable? → JSON
- Have 10,000+ issues? → JSONL
- Just checking results? → Table

### Step 3: Handle Pagination and Large Datasets

The Jira API limits results. You need to handle pagination for large exports.

**Problem**: Default limit is 100 issues per request

```bash
# Gets ONLY first 100
uv run jira-tool export --format json -o issues.json

# Gets 100 (limit applies!)
uv run jira-tool export --limit 50 --format json -o issues.json
```

**Solution 1: Use --all flag** (recommended)
```bash
# Gets all, handles pagination automatically
uv run jira-tool export --all --format json -o all_issues.json
```

**Solution 2: Use --limit strategically**
```bash
# Get only top 1000 (faster than --all)
uv run jira-tool export --limit 1000 --format json -o top_issues.json
```

**Solution 3: Filter to reduce results**
```bash
# Get only recent, unfinished issues (smaller subset)
uv run jira-tool search "project = PROJ AND created >= -30d AND status NOT IN (Done, Closed)" \
  --format json \
  -o recent_active.json
```

**Rule of Thumb**:
- < 1000 issues: Use `--limit` or default
- 1000-10000 issues: Use `--all` with JSONL
- > 10000 issues: Filter first, then use `--all` with JSONL

### Step 4: Export with Expanded Fields for Analysis

Some analysis requires expanded data (changelog, transitions, etc.).

**Export for State Analysis** (must have changelog):
```bash
uv run jira-tool search "project = PROJ" \
  --expand changelog \
  --format json \
  -o issues_with_history.json
```

The `--expand changelog` adds complete state transition history to each issue.

**Export for Workflow Analysis** (transitions):
```bash
uv run jira-tool search "project = PROJ" \
  --expand transitions \
  --format json \
  -o issues_with_transitions.json
```

The `--expand transitions` shows what states are available next.

**Export Multiple Expansions**:
```bash
uv run jira-tool search "project = PROJ" \
  --expand "changelog,transitions" \
  --format json \
  -o enriched.json
```

**Important**: Expanded data significantly increases file size:
- Without expand: ~5KB per issue
- With changelog: ~20-50KB per issue (can be 10x larger!)

Use filters to reduce before expanding:
```bash
# Export LAST 30 DAYS with changelog (smaller set)
uv run jira-tool search "project = PROJ AND created >= -30d" \
  --expand changelog \
  --format jsonl \
  -o recent_with_history.jsonl
```

### Step 5: Filter and Prepare Data

Export is just the first step. Prepare data for analysis:

**Filter After Export** (with jq):
```bash
# Extract only open issues
jq '.issues[] | select(.fields.status.name == "Open")' issues.json > open_issues.json

# Get issue keys and summaries
jq '.issues[] | {key: .key, summary: .fields.summary}' issues.json > keys_summaries.jsonl

# Count by status
jq '.issues | group_by(.fields.status.name) | map({status: .[0].fields.status.name, count: length})' issues.json
```

**Filter After Export** (with Python):
```python
import json
import csv

# Convert JSON to CSV (with selected fields)
with open('issues.json') as f:
    data = json.load(f)

with open('issues_simple.csv', 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=['key', 'summary', 'status', 'priority'])
    writer.writeheader()

    for issue in data['issues']:
        writer.writerow({
            'key': issue['key'],
            'summary': issue['fields']['summary'],
            'status': issue['fields']['status']['name'],
            'priority': issue['fields']['priority']['name'] if issue['fields'].get('priority') else 'N/A'
        })
```

**Aggregation After Export**:
```python
import json
from collections import defaultdict

with open('issues.json') as f:
    data = json.load(f)

# Count by status
by_status = defaultdict(int)
for issue in data['issues']:
    status = issue['fields']['status']['name']
    by_status[status] += 1

print("Issues by Status:")
for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
    print(f"  {status}: {count}")
```

### Step 6: Analyze and Generate Insights

Transform exported data into actionable insights:

**Analysis 1: Status Distribution**
```python
import json
from collections import Counter

with open('issues.json') as f:
    data = json.load(f)

statuses = Counter(
    issue['fields']['status']['name']
    for issue in data['issues']
)

print("Status Distribution:")
for status, count in statuses.most_common():
    pct = (count / len(data['issues'])) * 100
    print(f"  {status}: {count} ({pct:.1f}%)")
```

**Analysis 2: Workload by Assignee**
```python
import json
from collections import Counter

with open('issues.json') as f:
    data = json.load(f)

assignees = Counter()
for issue in data['issues']:
    assignee = issue['fields']['assignee']
    if assignee:
        assignees[assignee['displayName']] += 1

print("Workload Distribution:")
for name, count in assignees.most_common(10):
    print(f"  {name}: {count}")
```

**Analysis 3: Age of Open Issues**
```python
import json
from datetime import datetime, UTC

with open('issues.json') as f:
    data = json.load(f)

now = datetime.now(UTC)
open_issues = [
    issue for issue in data['issues']
    if issue['fields']['status']['name'] != 'Done'
]

# Calculate age
for issue in open_issues[:5]:  # Top 5
    created = datetime.fromisoformat(
        issue['fields']['created'].replace('Z', '+00:00')
    )
    age = (now - created).days
    print(f"{issue['key']}: {age} days old")
```

**Analysis 4: Priority vs Status** (correlation analysis)
```python
import json

with open('issues.json') as f:
    data = json.load(f)

matrix = {}
for issue in data['issues']:
    priority = issue['fields']['priority']['name'] if issue['fields'].get('priority') else 'None'
    status = issue['fields']['status']['name']

    key = (priority, status)
    matrix[key] = matrix.get(key, 0) + 1

print("Priority vs Status Matrix:")
print("Priority\tTo Do\tIn Progress\tDone")
for priority in ['Highest', 'High', 'Medium', 'Low']:
    row = f"{priority}"
    for status in ['To Do', 'In Progress', 'Done']:
        count = matrix.get((priority, status), 0)
        row += f"\t{count}"
    print(row)
```

### Step 7: Export for External Tools

Jira data can fuel other systems:

**Export for BI Tools** (Tableau, Power BI):
```bash
# CSV format for most BI tools
uv run jira-tool export --all --format csv -o issues_for_bi.csv

# Or combine with advanced tools
# Power BI: CSV import with automatic refresh
# Tableau: Direct CSV or API connection
```

**Export for Analytics** (spreadsheet):
```bash
# Export to CSV, then open in Excel/Google Sheets
uv run jira-tool export --format csv -o team_metrics.csv

# In spreadsheet: Add formulas, pivot tables, charts
```

**Export for Reporting** (Markdown/HTML):
```python
import json
import csv

# Read JSON, write Markdown report
with open('issues.json') as f:
    data = json.load(f)

with open('report.md', 'w') as out:
    out.write("# Jira Export Report\n\n")
    out.write(f"Total Issues: {len(data['issues'])}\n\n")
    out.write("## Issues\n\n")
    out.write("| Key | Summary | Status |\n")
    out.write("|-----|---------|--------|\n")

    for issue in data['issues'][:20]:  # First 20
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        out.write(f"| {key} | {summary} | {status} |\n")
```

**Export for Archive** (JSON backup):
```bash
# Keep full JSON backup with all data
uv run jira-tool export --all \
  --expand "changelog,transitions" \
  --format json \
  -o archive_$(date +%Y%m%d).json
```

## Examples

### Example 1: Weekly Metrics Report

```bash
#!/bin/bash
# Export this week's activity
uv run jira-tool export \
  --project PROJ \
  --created "-7d" \
  --format json \
  -o weekly_issues.json

# Analyze
python3 << 'EOF'
import json
from datetime import datetime, UTC, timedelta

with open('weekly_issues.json') as f:
    data = json.load(f)

issues = data['issues']
now = datetime.now(UTC)
week_ago = now - timedelta(days=7)

print(f"Weekly Metrics ({week_ago.date()} to {now.date()})")
print(f"====================================")
print(f"Total Issues Created: {len(issues)}")

by_status = {}
for issue in issues:
    status = issue['fields']['status']['name']
    by_status[status] = by_status.get(status, 0) + 1

print("\nBy Status:")
for status, count in sorted(by_status.items()):
    print(f"  {status}: {count}")
EOF
```

### Example 2: Archive Old Issues with History

```bash
# Export all closed issues with full changelog (for archive)
uv run jira-tool search "status = Done AND updated <= -30d" \
  --expand changelog \
  --format jsonl \
  -o archived_issues.jsonl

# Verify integrity
wc -l archived_issues.jsonl
```

### Example 3: Prepare Data for Analysis Tool

```bash
# Export with all expansions for external analysis
uv run jira-tool search "sprint in openSprints()" \
  --expand "changelog,transitions,operations" \
  --format json \
  -o sprint_full.json

# Convert to simplified CSV for Excel analysis
python3 << 'EOF'
import json
import csv

with open('sprint_full.json') as f:
    data = json.load(f)

with open('sprint_analysis.csv', 'w', newline='') as out:
    fields = ['key', 'summary', 'status', 'assignee', 'created', 'updated']
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()

    for issue in data['issues']:
        assignee = issue['fields']['assignee']
        writer.writerow({
            'key': issue['key'],
            'summary': issue['fields']['summary'],
            'status': issue['fields']['status']['name'],
            'assignee': assignee['displayName'] if assignee else 'Unassigned',
            'created': issue['fields']['created'],
            'updated': issue['fields']['updated']
        })

print(f"Converted {len(data['issues'])} issues to CSV")
EOF
```

### Example 4: Compare Two Projects

```bash
# Export both projects
uv run jira-tool export --project PROJ1 --format jsonl -o proj1.jsonl
uv run jira-tool export --project PROJ2 --format jsonl -o proj2.jsonl

# Analyze differences
python3 << 'EOF'
import json
from collections import Counter

def analyze_file(filename):
    statuses = Counter()
    types = Counter()
    count = 0
    for line in open(filename):
        issue = json.loads(line)
        statuses[issue['fields']['status']['name']] += 1
        types[issue['fields']['issuetype']['name']] += 1
        count += 1
    return count, statuses, types

proj1_count, proj1_status, proj1_types = analyze_file('proj1.jsonl')
proj2_count, proj2_status, proj2_types = analyze_file('proj2.jsonl')

print(f"PROJ1: {proj1_count} issues")
print(f"  Status: {dict(proj1_status)}")
print(f"PROJ2: {proj2_count} issues")
print(f"  Status: {dict(proj2_status)}")
EOF
```

## Requirements

### Core Requirements
- **Jira Cloud instance** with REST API v3 access
- **Python 3.10+** (for jira-tool CLI)
- **Environment variables**:
  - `JIRA_BASE_URL` - Your Jira instance (e.g., `https://company.atlassian.net`)
  - `JIRA_USERNAME` - Email for authentication
  - `JIRA_API_TOKEN` - API token from Jira user settings

### Recommended Tools
- **jq** (command-line JSON processor): `brew install jq`
- **Python pandas**: `pip install pandas` (optional, for advanced analysis)
- **Python json**: Built-in (for JSON processing)
- **csv module**: Built-in (for CSV operations)

### Data Requirements
- **For state analysis**: Issues must be exported with `--expand changelog`
- **For trend analysis**: Export with `--created` or `--updated` date filters
- **For large datasets**: Use JSONL format and streaming tools

## See Also

- [Design Jira State Analyzer](/skills/design-jira-state-analyzer) - Analyze state transitions and cycle time
- [Jira REST API](/skills/jira-api) - API reference for filter and expand options
- [Build Jira Document Format](/skills/build-jira-document-format) - Create formatted reports
- CLAUDE.md - Project configuration and patterns
