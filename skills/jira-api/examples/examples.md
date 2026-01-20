# Jira API v3 Extended Examples

## Real-World Scenarios

### Scenario 1: Bulk Create Issues Under Epic

Create multiple issues as part of an epic with rich descriptions:

```python
from jira_tool.client import JiraClient
from jira_tool.formatter import JiraDocumentBuilder

client = JiraClient()

# Data for multiple issues
issues_data = [
    {
        "summary": "Backend API endpoint for user creation",
        "tasks": ["Design schema", "Implement endpoint", "Write tests"]
    },
    {
        "summary": "Frontend form for user registration",
        "tasks": ["Design UI mockup", "Implement form", "Add validation"]
    },
    {
        "summary": "Database migration for new fields",
        "tasks": ["Design migration", "Test rollback", "Document changes"]
    }
]

epic_key = "PROJ-1"  # The epic to add issues to

for issue_data in issues_data:
    # Build rich description with task list
    doc = JiraDocumentBuilder()
    doc.add_heading(issue_data["summary"], level=2)
    doc.add_paragraph(doc.add_text("Tasks to complete:"))
    doc.add_bullet_list(issue_data["tasks"])
    adf_description = doc.build()

    # Create issue
    response = client.create_issue({
        "fields": {
            "project": {"key": "PROJ"},
            "summary": issue_data["summary"],
            "description": adf_description,
            "issuetype": {"name": "Task"},
            "priority": {"name": "High"},
            "customfield_10014": epic_key,  # Epic Link
            "labels": ["epic-subtask", "high-priority"]
        }
    })

    print(f"Created {response['key']}")
```

### Scenario 2: Track Issue Progress Through Workflow

Monitor how long issues spend in each state:

```python
from jira_tool.client import JiraClient
from jira_tool.analysis.state_analyzer import StateDurationAnalyzer
from datetime import datetime

client = JiraClient()

# Get issues from last sprint
issues = client.search_issues(
    jql="project = PROJ AND sprint = 'Sprint 10' AND type != Epic",
    expand=["changelog"]
)

# Analyze state transitions
analyzer = StateDurationAnalyzer()
for issue in issues:
    transitions = analyzer.extract_state_transitions(issue)

    print(f"\n{issue['key']}: {issue['fields']['summary']}")
    print("-" * 60)

    for transition in transitions:
        print(f"  {transition.from_state} -> {transition.to_state}")
        print(f"    {transition.timestamp}")

# Calculate average time in each state
durations = analyzer.analyze_issues(issues)
csv_output = analyzer.format_as_csv(durations)
print("\n" + csv_output)
```

### Scenario 3: Find and Update Issues Matching Criteria

Find all high-priority bugs from last week and assign them:

```python
from jira_tool.client import JiraClient

client = JiraClient()

# Find high-priority bugs
issues = client.search_issues(
    jql=(
        "project = PROJ AND "
        "type = Bug AND "
        "priority >= High AND "
        "created >= -7d AND "
        "assignee IS EMPTY"
    ),
    maxResults=100
)

print(f"Found {len(issues)} unassigned bugs")

# Get available team members
team_members = client.search_users(query="team=backend")

# Assign issues round-robin
for i, issue in enumerate(issues):
    assignee = team_members[i % len(team_members)]

    client.update_issue(
        issue["key"],
        {
            "fields": {
                "assignee": {"accountId": assignee["accountId"]}
            }
        }
    )

    print(f"Assigned {issue['key']} to {assignee['displayName']}")
```

### Scenario 4: Export Issues to CSV with Custom Fields

Export specific issues with selected fields to CSV:

```python
from jira_tool.client import JiraClient
from jira_tool.analysis.formatters import format_as_csv
import csv

client = JiraClient()

# Search for issues
issues = client.search_issues(
    jql="project = PROJ AND status IN (Open, 'In Progress')",
    fields=["key", "summary", "assignee", "status", "priority", "created"],
    maxResults=200
)

# Extract data
rows = []
for issue in issues:
    fields = issue["fields"]
    rows.append({
        "Key": issue["key"],
        "Summary": fields["summary"],
        "Assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
        "Status": fields["status"]["name"],
        "Priority": fields["priority"]["name"],
        "Created": fields["created"][:10],  # Date only
    })

# Write to CSV
with open("issues_export.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Key", "Summary", "Assignee", "Status", "Priority", "Created"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Exported {len(rows)} issues to issues_export.csv")
```

### Scenario 5: Create Issue with Detailed Error Handling

Robust issue creation with comprehensive error handling:

```python
from jira_tool.client import JiraClient
from jira_tool.formatter import JiraDocumentBuilder
import requests
import time

client = JiraClient()

def create_issue_with_retry(issue_data, max_retries=3):
    """Create issue with retry logic and detailed error handling."""

    for attempt in range(max_retries):
        try:
            print(f"Creating issue (attempt {attempt + 1}/{max_retries})...")
            response = client.create_issue(issue_data)
            print(f"Successfully created {response['key']}")
            return response["key"]

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code == 429:
                # Rate limited - wait and retry
                reset_time = int(e.response.headers.get('X-RateLimit-Reset', 0))
                wait_seconds = reset_time - time.time()
                print(f"Rate limited. Waiting {wait_seconds:.0f} seconds...")
                time.sleep(wait_seconds + 1)
                continue

            elif status_code == 400:
                # Bad request - extract error details
                try:
                    error_data = e.response.json()
                    print("Validation errors:")
                    if "errorMessages" in error_data:
                        for msg in error_data["errorMessages"]:
                            print(f"  - {msg}")
                    if "errors" in error_data:
                        for field, msg in error_data["errors"].items():
                            print(f"  - {field}: {msg}")
                except:
                    print(f"Bad request: {e.response.text}")
                return None

            elif status_code == 401:
                print("Authentication failed. Check credentials.")
                return None

            elif status_code == 403:
                print("Permission denied. Check project/issue permissions.")
                return None

            elif status_code in [500, 502, 503, 504]:
                # Server error - retry with backoff
                wait_seconds = 2 ** attempt
                print(f"Server error. Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
                continue

            else:
                print(f"Unexpected error: {status_code} {e}")
                return None

        except Exception as e:
            print(f"Error: {e}")
            return None

    print(f"Failed to create issue after {max_retries} attempts")
    return None

# Example usage
doc = JiraDocumentBuilder()
doc.add_heading("Bug Report", level=1)
doc.add_paragraph(doc.add_text("Error details"))

issue_data = {
    "fields": {
        "project": {"key": "PROJ"},
        "summary": "Test Issue",
        "description": doc.build(),
        "issuetype": {"name": "Bug"},
        "priority": {"name": "High"}
    }
}

issue_key = create_issue_with_retry(issue_data)
if issue_key:
    print(f"Issue ready: https://company.atlassian.net/browse/{issue_key}")
```

### Scenario 6: Generate Status Report

Create a comprehensive status report from Jira data:

```python
from jira_tool.client import JiraClient
from datetime import datetime

client = JiraClient()

# Fetch data for report
statuses = ["Open", "In Progress", "In Review", "Done"]
report_data = {}

for status in statuses:
    issues = client.search_issues(
        jql=f"project = PROJ AND status = '{status}'",
        fields=["key", "summary", "assignee", "priority"],
        maxResults=100
    )
    report_data[status] = issues

# Generate report
print("=" * 80)
print(f"PROJECT STATUS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 80)

total_issues = sum(len(issues) for issues in report_data.values())
print(f"\nTotal Issues: {total_issues}\n")

for status, issues in report_data.items():
    print(f"{status}: {len(issues)} issues")
    for issue in issues[:5]:  # Show first 5
        assignee_name = issue["fields"].get("assignee", {}).get("displayName", "Unassigned")
        priority = issue["fields"]["priority"]["name"]
        print(f"  - {issue['key']}: {issue['fields']['summary']}")
        print(f"    Priority: {priority}, Assigned: {assignee_name}")

    if len(issues) > 5:
        print(f"  ... and {len(issues) - 5} more")
    print()
```

### Scenario 7: Webhook Integration Example

Handle Jira webhook events:

```python
from flask import Flask, request
import json
from jira_tool.client import JiraClient

app = Flask(__name__)
client = JiraClient()

@app.route('/webhook/jira', methods=['POST'])
def handle_jira_webhook():
    """Handle Jira webhook events."""

    payload = request.json
    event_type = payload.get('webhookEvent')
    issue_key = payload['issue']['key']
    issue = payload['issue']['fields']

    print(f"Webhook event: {event_type} for {issue_key}")

    if event_type == 'jira:issue_created':
        print(f"New issue created: {issue['summary']}")
        # Handle new issue

    elif event_type == 'jira:issue_updated':
        # Check what changed
        changelog = payload.get('changelog', {})
        for history in changelog.get('histories', []):
            for item in history.get('items', []):
                field = item.get('field')
                from_value = item.get('from')
                to_value = item.get('to')
                print(f"  {field}: {from_value} -> {to_value}")

        # Example: Auto-transition issue if specific field changes
        if field == 'assignee' and to_value:
            print(f"Issue assigned to {to_value}")

    elif event_type == 'jira:issue_deleted':
        print(f"Issue deleted: {issue_key}")

    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(port=5000)
```

### Scenario 8: Complex JQL Queries

Examples of advanced JQL patterns:

```python
from jira_tool.client import JiraClient

client = JiraClient()

# Example 1: Find issues stuck in review
stuck_issues = client.search_issues(
    jql=(
        "project = PROJ AND "
        "status = 'In Review' AND "
        "updated < -3d"  # Not updated in 3 days
    )
)
print(f"Found {len(stuck_issues)} issues stuck in review")

# Example 2: Find issues assigned to teams
team_issues = client.search_issues(
    jql=(
        "project IN (BACKEND, FRONTEND) AND "
        "(assignee IN (user1, user2) OR "
        "assignee IS EMPTY)"
    )
)
print(f"Found {len(team_issues)} team issues")

# Example 3: Find issues with specific epic and not done
epic_work = client.search_issues(
    jql=(
        "project = PROJ AND "
        "text ~ 'epic' AND "
        "status != Done AND "
        "priority >= High AND "
        "assignee IS NOT EMPTY"
    ),
    expand=["changelog"],
    orderBy="priority DESC,created ASC"
)
print(f"Found {len(epic_work)} high-priority epic issues")

# Example 4: Find recent high-activity issues
active_issues = client.search_issues(
    jql=(
        "project = PROJ AND "
        "updated >= -1d AND "
        "created >= -30d"
    ),
    maxResults=100
)
print(f"Found {len(active_issues)} recently active issues")
```

### Scenario 9: Monitor Issue Metrics

Calculate metrics from issue data:

```python
from jira_tool.client import JiraClient
from collections import defaultdict
from datetime import datetime

client = JiraClient()

# Fetch recent issues
issues = client.search_issues(
    jql="project = PROJ AND created >= -30d",
    fields=["key", "summary", "priority", "assignee", "status", "created"],
    maxResults=100
)

# Calculate metrics
metrics = {
    "total": len(issues),
    "by_priority": defaultdict(int),
    "by_status": defaultdict(int),
    "by_assignee": defaultdict(int),
    "unassigned": 0
}

for issue in issues:
    fields = issue["fields"]

    # By priority
    priority = fields["priority"]["name"]
    metrics["by_priority"][priority] += 1

    # By status
    status = fields["status"]["name"]
    metrics["by_status"][status] += 1

    # By assignee
    assignee = fields.get("assignee")
    if assignee:
        name = assignee.get("displayName", "Unknown")
        metrics["by_assignee"][name] += 1
    else:
        metrics["unassigned"] += 1

# Print metrics
print("ISSUE METRICS (Last 30 days)")
print("=" * 40)
print(f"Total Issues: {metrics['total']}")
print(f"Unassigned: {metrics['unassigned']}")
print("\nBy Priority:")
for priority, count in sorted(metrics["by_priority"].items()):
    print(f"  {priority}: {count}")
print("\nBy Status:")
for status, count in sorted(metrics["by_status"].items()):
    print(f"  {status}: {count}")
print("\nBy Assignee:")
for assignee, count in sorted(metrics["by_assignee"].items(), key=lambda x: -x[1])[:5]:
    print(f"  {assignee}: {count}")
```

### Scenario 10: Rich Description with Code Example

Create issue with embedded code and panels:

```python
from jira_tool.client import JiraClient
from jira_tool.formatter import JiraDocumentBuilder

client = JiraClient()

# Build detailed bug report
doc = JiraDocumentBuilder()

doc.add_heading("API Response Parsing Bug", level=1)

doc.add_heading("Description", level=2)
doc.add_paragraph(
    doc.add_text("The API returns malformed JSON in error responses, causing our parser to crash.")
)

doc.add_heading("Steps to Reproduce", level=2)
doc.add_bullet_list([
    "Make request to /api/users with invalid filter",
    "Observe 400 response",
    "Parser throws JSON decode error"
])

doc.add_heading("Error Response", level=2)
doc.add_code_block(
    '{\n  "error": "Invalid filter syntax"\n  "status": 400  <- Missing comma!\n}',
    language="json"
)

doc.add_heading("Expected Behavior", level=2)
doc.add_paragraph(
    doc.add_text("API should return valid JSON even for error responses")
)

doc.add_heading("Impact", level=2)
impact_doc = JiraDocumentBuilder()
impact_doc.add_paragraph(
    doc.add_text("Client application crashes when handling API errors")
)
doc.add_panel("error", doc.add_paragraph(
    doc.add_text("Severity: High - affects production error handling")
))

# Create issue
response = client.create_issue({
    "fields": {
        "project": {"key": "PROJ"},
        "summary": "API returns malformed JSON in error responses",
        "description": doc.build(),
        "issuetype": {"name": "Bug"},
        "priority": {"name": "Highest"},
        "labels": ["api", "critical", "json-parsing"],
        "components": [{"name": "API"}]
    }
})

print(f"Created issue: {response['key']}")
```

## Common Patterns

### Pattern 1: Pagination with Generator

```python
def search_all_issues(jql, batch_size=100):
    """Yield all issues matching JQL, handling pagination."""
    client = JiraClient()
    start_at = 0

    while True:
        issues = client.search_issues(
            jql=jql,
            startAt=start_at,
            maxResults=batch_size
        )

        if not issues:
            break

        for issue in issues:
            yield issue

        if len(issues) < batch_size:
            break

        start_at += batch_size

# Usage
for issue in search_all_issues("project = PROJ"):
    print(f"{issue['key']}: {issue['fields']['summary']}")
```

### Pattern 2: Cached Field Discovery

```python
from functools import lru_cache

class JiraFieldCache:
    def __init__(self):
        self.client = JiraClient()
        self._fields = None

    def get_field_id(self, field_name):
        """Get field ID by name, cached."""
        if self._fields is None:
            self._fields = self.client.list_fields()

        for field in self._fields:
            if field['name'].lower() == field_name.lower():
                return field['id']
        return None

    def get_custom_field_ids(self):
        """Get all custom field IDs."""
        if self._fields is None:
            self._fields = self.client.list_fields()
        return {f['name']: f['id'] for f in self._fields if f['custom']}

# Usage
cache = JiraFieldCache()
epic_field = cache.get_field_id("Epic Link")
custom_fields = cache.get_custom_field_ids()
```

### Pattern 3: Batch Updates

```python
def batch_update_issues(jql, update_func, batch_size=50):
    """Update multiple issues based on criteria."""
    client = JiraClient()
    updated_count = 0

    for issue in search_all_issues(jql, batch_size):
        update_data = update_func(issue)
        if update_data:
            client.update_issue(issue['key'], update_data)
            updated_count += 1

    return updated_count

# Usage
def mark_stale_as_inactive(issue):
    """Mark old issues as inactive."""
    fields = issue['fields']
    if fields['created'] < "2023-01-01":
        return {"fields": {"labels": ["inactive"]}}
    return None

updated = batch_update_issues(
    "project = PROJ AND status = Open",
    mark_stale_as_inactive
)
print(f"Updated {updated} issues")
```

## Error Handling Patterns

### Pattern: Retry with Exponential Backoff

```python
import time
import requests

def api_call_with_backoff(method, url, max_retries=5, initial_delay=1):
    """Make API call with exponential backoff on failure."""
    client = JiraClient()

    for attempt in range(max_retries):
        try:
            response = client.session.request(method, url)
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                delay = int(e.response.headers.get('X-RateLimit-Reset', 0)) - time.time()
                delay = max(delay, initial_delay * (2 ** attempt))
            elif e.response.status_code >= 500:
                # Server error - use exponential backoff
                delay = initial_delay * (2 ** attempt)
            else:
                # Client error - don't retry
                raise

            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise

    return None
```

