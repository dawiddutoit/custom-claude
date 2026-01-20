# Jira API v3 Comprehensive Reference

## Complete Endpoint Reference

### Issue Endpoints

#### Get Issue
```
GET /rest/api/3/issue/{issueIdOrKey}

Parameters:
- issueIdOrKey (required): Issue ID or key (e.g., "PROJ-123")
- expand: Additional data to include (changelog, transitions, editmeta, names)
- fields: Comma-separated field names to return
- updateHistory: Include update history (true/false)

Response:
{
  "expand": "names,schema",
  "id": "10000",
  "key": "PROJ-123",
  "self": "https://company.atlassian.net/rest/api/3/issue/10000",
  "fields": {
    "summary": "Issue summary",
    "description": {...},
    "created": "2024-01-01T10:00:00.000+0000",
    "updated": "2024-01-02T15:30:00.000+0000",
    "assignee": {"accountId": "...", "emailAddress": "..."},
    "status": {"name": "In Progress", "id": "3"},
    "priority": {"name": "High", "id": "2"},
    ...
  },
  "changelog": {...}  // If expand=changelog
}

Status Codes:
- 200: Success
- 401: Unauthorized
- 404: Issue not found
```

#### Create Issue
```
POST /rest/api/3/issues

Body:
{
  "fields": {
    "project": {"key": "PROJ"},           // Required
    "summary": "Issue summary",            // Required
    "issuetype": {"name": "Task"},         // Required
    "description": {"type": "doc", ...},   // Optional, ADF format
    "assignee": {"accountId": "..."},
    "priority": {"name": "High"},
    "labels": ["label1", "label2"],
    "components": [{"name": "Component"}],
    "customfield_10014": "Custom value"
  }
}

Response: 201 Created
{
  "id": "10000",
  "key": "PROJ-124",
  "self": "https://company.atlassian.net/rest/api/3/issue/10000"
}

Status Codes:
- 201: Issue created
- 400: Invalid request
- 401: Unauthorized
- 403: Forbidden
```

#### Update Issue
```
PUT /rest/api/3/issue/{issueIdOrKey}

Body:
{
  "fields": {
    "summary": "Updated summary",
    "description": {"type": "doc", ...},
    "assignee": {"accountId": "..."},
    "priority": {"name": "Medium"},
    "labels": ["label1", "label2"]
  }
}

Response: 204 No Content

Status Codes:
- 204: Success
- 400: Invalid request
- 401: Unauthorized
- 404: Issue not found
```

#### Delete Issue
```
DELETE /rest/api/3/issue/{issueIdOrKey}

Parameters:
- deleteSubtasks (optional): Delete subtasks (true/false)

Response: 204 No Content

Status Codes:
- 204: Success
- 400: Issue not found
- 401: Unauthorized
- 403: Forbidden
```

#### Add Comment to Issue
```
POST /rest/api/3/issue/{issueIdOrKey}/comments

Body:
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Comment text"}]
      }
    ]
  }
}

Response: 201 Created
{
  "self": "...",
  "id": "10001",
  "author": {...},
  "body": {...},
  "created": "2024-01-02T16:00:00.000+0000",
  "updated": "2024-01-02T16:00:00.000+0000"
}

Status Codes:
- 201: Comment created
- 400: Invalid request
- 401: Unauthorized
- 404: Issue not found
```

#### Get Transitions
```
GET /rest/api/3/issue/{issueIdOrKey}/transitions

Response:
{
  "expand": "transitions",
  "transitions": [
    {
      "id": "11",
      "name": "In Progress",
      "to": {
        "self": "...",
        "description": "Work is in progress",
        "iconUrl": "...",
        "name": "In Progress",
        "id": "3"
      },
      "hasScreen": false,
      "isGlobal": true,
      "isInitial": false,
      "isConditional": false,
      "fields": {
        "assignee": {...},
        "resolution": {...}
      }
    }
  ]
}

Status Codes:
- 200: Success
- 404: Issue not found
```

#### Transition Issue
```
POST /rest/api/3/issue/{issueIdOrKey}/transitions

Body:
{
  "transition": {
    "id": "11"  // From GET transitions
  },
  "fields": {
    "resolution": {"name": "Done"},
    "assignee": {"accountId": "..."}
  }
}

Response: 204 No Content

Status Codes:
- 204: Success
- 400: Invalid transition
- 404: Issue not found
```

### Search Endpoints

#### Search Issues
```
GET /rest/api/3/search

Parameters:
- jql (required): JQL query string
- startAt: Pagination start (default 0)
- maxResults: Results per page (default 50, max 100)
- fields: Comma-separated fields to return
- expand: Additional data (changelog, transitions)
- orderBy: Sort order

Response:
{
  "expand": "names,schema",
  "startAt": 0,
  "maxResults": 50,
  "total": 523,
  "isLast": false,
  "values": [
    {
      "expand": "...",
      "id": "10000",
      "key": "PROJ-123",
      "fields": {...}
    }
  ]
}

Status Codes:
- 200: Success
- 400: Invalid JQL
- 401: Unauthorized
```

#### Search Issues (POST)
```
POST /rest/api/3/issues/search

Body:
{
  "jql": "project = PROJ AND status = Open",
  "startAt": 0,
  "maxResults": 100,
  "fields": ["key", "summary", "status"],
  "expand": ["changelog"]
}

Response: Same as GET search
```

### User Endpoints

#### Search Users
```
GET /rest/api/3/users/search

Parameters:
- query (required): Username or email to search
- startAt: Pagination start (default 0)
- maxResults: Results per page (default 50)

Response:
[
  {
    "self": "...",
    "accountId": "5d6c6c8d8c0e",
    "accountType": "atlassian",
    "emailAddress": "user@example.com",
    "avatarUrls": {...},
    "displayName": "User Name",
    "active": true,
    "timeZone": "America/New_York"
  }
]

Status Codes:
- 200: Success
- 401: Unauthorized
```

#### Get User
```
GET /rest/api/3/user

Parameters:
- accountId (required): User account ID

Response:
{
  "self": "...",
  "accountId": "5d6c6c8d8c0e",
  "accountType": "atlassian",
  "emailAddress": "user@example.com",
  "avatarUrls": {...},
  "displayName": "User Name",
  "active": true,
  "timeZone": "America/New_York"
}

Status Codes:
- 200: Success
- 401: Unauthorized
- 404: User not found
```

#### Get Current User
```
GET /rest/api/3/myself

Response: Same as GET /user

Status Codes:
- 200: Success
- 401: Unauthorized
```

### Project Endpoints

#### List Projects
```
GET /rest/api/3/project

Parameters:
- startAt: Pagination start
- maxResults: Results per page
- orderBy: Sort order
- expand: Additional data

Response:
[
  {
    "self": "...",
    "id": "10000",
    "key": "PROJ",
    "name": "Project Name",
    "projectTypeKey": "software",
    "simplified": false,
    "avatarUrls": {...}
  }
]

Status Codes:
- 200: Success
- 401: Unauthorized
```

#### Get Project
```
GET /rest/api/3/project/{projectIdOrKey}

Parameters:
- projectIdOrKey (required): Project ID or key
- expand: Additional data (issueTypes, description)

Response:
{
  "self": "...",
  "id": "10000",
  "key": "PROJ",
  "name": "Project Name",
  "projectTypeKey": "software",
  "description": "Project description",
  "lead": {...},
  "components": [...],
  "issueTypes": [
    {
      "self": "...",
      "id": "10001",
      "description": "A task",
      "iconUrl": "...",
      "name": "Task"
    }
  ]
}

Status Codes:
- 200: Success
- 401: Unauthorized
- 404: Project not found
```

### Field Endpoints

#### List Fields
```
GET /rest/api/3/field

Response:
[
  {
    "id": "summary",
    "key": "summary",
    "name": "Summary",
    "untranslatedName": "Summary",
    "custom": false,
    "orderable": true,
    "searchable": true,
    "clauseNames": ["summary", "text"]
  },
  {
    "id": "customfield_10014",
    "key": "customfield_10014",
    "name": "Epic Link",
    "untranslatedName": "Epic Link",
    "custom": true,
    "orderable": true,
    "searchable": true,
    "clauseNames": ["customfield_10014"]
  }
]

Status Codes:
- 200: Success
- 401: Unauthorized
```

#### Search Fields
```
GET /rest/api/3/field/search

Parameters:
- type: Field type (custom, standard, etc.)
- query: Search term

Response: Same as List Fields
```

### Webhook Endpoints

#### List Webhooks
```
GET /rest/api/3/webhook

Parameters:
- startAt: Pagination start
- maxResults: Results per page

Response:
{
  "pageSize": 10,
  "startAt": 0,
  "total": 2,
  "isLast": true,
  "values": [
    {
      "id": 1,
      "name": "My Webhook",
      "url": "https://example.com/webhook",
      "self": "...",
      "jqlFilter": "project = PROJ",
      "events": ["jira:issue_created", "jira:issue_updated"],
      "expirationDate": null,
      "created": "2024-01-01T10:00:00.000+0000",
      "updated": "2024-01-01T10:00:00.000+0000"
    }
  ]
}

Status Codes:
- 200: Success
- 401: Unauthorized
```

#### Create Webhook
```
POST /rest/api/3/webhook

Body:
{
  "name": "My Webhook",
  "url": "https://example.com/webhook",
  "jqlFilter": "project = PROJ",
  "events": [
    "jira:issue_created",
    "jira:issue_updated",
    "jira:issue_deleted"
  ],
  "expirationDate": "2025-01-01T00:00:00.000+0000"
}

Response: 201 Created
{
  "id": 1,
  "self": "...",
  "name": "My Webhook",
  ...
}

Status Codes:
- 201: Webhook created
- 400: Invalid request
- 401: Unauthorized
```

#### Delete Webhook
```
DELETE /rest/api/3/webhook/{id}

Response: 204 No Content

Status Codes:
- 204: Success
- 401: Unauthorized
- 404: Webhook not found
```

## Webhook Event Payloads

### Issue Created Event

```json
{
  "timestamp": 1234567890,
  "webhookEvent": "jira:issue_created",
  "issue": {
    "id": "10000",
    "self": "https://company.atlassian.net/rest/api/3/issue/10000",
    "key": "PROJ-123",
    "fields": {
      "created": "2024-01-01T10:00:00.000+0000",
      "updated": "2024-01-01T10:00:00.000+0000",
      "summary": "Issue summary",
      "description": {...},
      "project": {"id": "10000", "key": "PROJ"},
      "status": {"id": "1", "name": "Open"},
      "assignee": {...},
      "creator": {...},
      "reporter": {...}
    }
  },
  "changelog": {
    "id": "10001",
    "histories": [
      {
        "created": "2024-01-01T10:00:00.000+0000",
        "author": {...},
        "items": [
          {
            "field": "summary",
            "fieldtype": "jira",
            "fieldId": "summary",
            "from": null,
            "fromString": null,
            "to": "Issue summary",
            "toString": "Issue summary"
          }
        ]
      }
    ]
  }
}
```

### Issue Updated Event

```json
{
  "timestamp": 1234567890,
  "webhookEvent": "jira:issue_updated",
  "issue": {...},
  "changelog": {
    "id": "10002",
    "histories": [
      {
        "created": "2024-01-02T15:30:00.000+0000",
        "author": {...},
        "items": [
          {
            "field": "status",
            "fieldtype": "jira",
            "fieldId": "status",
            "from": "1",
            "fromString": "Open",
            "to": "3",
            "toString": "In Progress"
          }
        ]
      }
    ]
  }
}
```

### Issue Deleted Event

```json
{
  "timestamp": 1234567890,
  "webhookEvent": "jira:issue_deleted",
  "issue": {...}
}
```

## JQL (Jira Query Language) Reference

### Basic Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| = | status = Open | Exact match |
| != | status != Done | Not equal |
| > | created > -7d | Greater than |
| >= | created >= 2024-01-01 | Greater or equal |
| < | updated < -1d | Less than |
| <= | created <= 2024-12-31 | Less or equal |
| ~ | summary ~ "bug fix" | Text contains |
| !~ | description !~ "urgent" | Text doesn't contain |
| IN | status IN (Open, "In Progress") | In list |
| NOT IN | priority NOT IN (Low) | Not in list |
| IS | assignee IS EMPTY | Is value |
| IS NOT | assignee IS NOT EMPTY | Is not value |

### Field Types and Examples

**Standard Fields**:
```
project = PROJ                          # Project key
status = Open                           # Status name
type = Task                             # Issue type
priority = High                         # Priority name
assignee = currentUser()                # Current user
reporter = "user@example.com"           # Reporter email
created >= -7d                          # Creation date
updated < -1d                           # Update date
summary ~ "keyword"                     # Summary text search
description ~ "critical"                # Description search
labels IN (bug, urgent)                 # Labels
component = "Component Name"            # Component
```

**Custom Fields**:
```
customfield_10014 = "Epic Name"         # Epic Link field
customfield_10015 = "Custom Value"      # Other custom field
```

### Date Functions

| Function | Example | Result |
|----------|---------|--------|
| -Xd | created >= -7d | Last X days |
| -Xw | created >= -2w | Last X weeks |
| -Xm | created >= -1m | Last X months |
| -Xy | created >= -1y | Last X years |
| startOfDay() | updated >= startOfDay() | Today |
| endOfDay() | created <= endOfDay() | Today |
| now() | updated >= now() - 1h | Last hour |

### Function Examples

```
assignee = currentUser()                # Current user
assignee = EMPTY                        # Unassigned
reporter = currentUser()                # Reported by me
project IN (getProjectsFromIssueFilter("filter-123"))
status IN (Open, "In Progress")
priority >= Medium
created >= -7d AND updated <= -1d
(project = PROJ1 OR project = PROJ2)
  AND status IN (Open, "In Progress")
  AND assignee = currentUser()
```

## ADF (Atlassian Document Format) Reference

### Document Structure

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    // Document nodes here
  ]
}
```

### Node Types

#### Heading
```json
{
  "type": "heading",
  "attrs": {"level": 1},
  "content": [
    {"type": "text", "text": "Heading Text"}
  ]
}
```

#### Paragraph
```json
{
  "type": "paragraph",
  "content": [
    {"type": "text", "text": "Paragraph text"}
  ]
}
```

#### Text Node with Marks (Formatting)

```json
{
  "type": "text",
  "text": "Formatted text",
  "marks": [
    {"type": "strong"},     // Bold
    {"type": "em"},         // Italic
    {"type": "underline"},  // Underline
    {"type": "code"},       // Inline code
    {"type": "strike"},     // Strikethrough
    {
      "type": "link",
      "attrs": {
        "href": "https://example.com"
      }
    }
  ]
}
```

#### Bullet List
```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "Item 1"}]
        }
      ]
    },
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "Item 2"}]
        }
      ]
    }
  ]
}
```

#### Ordered List
```json
{
  "type": "orderedList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "Step 1"}]
        }
      ]
    }
  ]
}
```

#### Code Block
```json
{
  "type": "codeBlock",
  "attrs": {
    "language": "python"  // Optional: javascript, java, etc.
  },
  "content": [
    {
      "type": "text",
      "text": "code content here"
    }
  ]
}
```

#### Panel
```json
{
  "type": "panel",
  "attrs": {
    "panelType": "info"  // info, note, warning, success, error
  },
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Panel content"}]
    }
  ]
}
```

#### Block Quote
```json
{
  "type": "blockquote",
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Quote text"}]
    }
  ]
}
```

#### Table
```json
{
  "type": "table",
  "content": [
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableHeader",
          "content": [
            {
              "type": "paragraph",
              "content": [{"type": "text", "text": "Header 1"}]
            }
          ]
        },
        {
          "type": "tableHeader",
          "content": [
            {
              "type": "paragraph",
              "content": [{"type": "text", "text": "Header 2"}]
            }
          ]
        }
      ]
    },
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableCell",
          "content": [
            {
              "type": "paragraph",
              "content": [{"type": "text", "text": "Cell 1"}]
            }
          ]
        },
        {
          "type": "tableCell",
          "content": [
            {
              "type": "paragraph",
              "content": [{"type": "text", "text": "Cell 2"}]
            }
          ]
        }
      ]
    }
  ]
}
```

#### Horizontal Rule
```json
{
  "type": "rule"
}
```

### Text Marks (Formatting) Quick Reference

```python
# Using JiraDocumentBuilder
doc = JiraDocumentBuilder()

# Bold text
node = doc.add_text("Bold", marks=[{"type": "strong"}])

# Italic text
node = doc.add_text("Italic", marks=[{"type": "em"}])

# Code inline
node = doc.add_text("code", marks=[{"type": "code"}])

# Link
node = doc.add_text("Link", marks=[{"type": "link", "attrs": {"href": "https://..."}}])
```

## Field Types and Examples

### Standard Fields

| Field | Type | Searchable | Example |
|-------|------|-----------|---------|
| key | string | Yes | PROJ-123 |
| summary | string | Yes | Issue title |
| description | ADF | Yes | Rich text document |
| created | date | Yes | 2024-01-01 |
| updated | date | Yes | 2024-01-02 |
| assignee | user | Yes | {"accountId": "..."} |
| reporter | user | Yes | {"accountId": "..."} |
| status | selection | Yes | {"name": "Open", "id": "1"} |
| priority | selection | Yes | {"name": "High", "id": "2"} |
| issuetype | selection | Yes | {"name": "Task", "id": "3"} |
| project | string | Yes | {"key": "PROJ"} |
| labels | string[] | Yes | ["bug", "urgent"] |
| components | selection[] | Yes | [{"name": "Backend"}] |
| fixVersions | version[] | Yes | [{"name": "1.0"}] |
| environment | string | Yes | "Production" |

### Common Custom Fields

| Field Name | ID Pattern | Type | Example |
|------------|-----------|------|---------|
| Epic Link | customfield_10014 or 11923 | issue | "PROJ-1" |
| Story Points | customfield_10012 | number | 5 |
| Sprint | customfield_10020 | sprint | 123 |
| Due Date | duedate | date | "2024-12-31" |
| Team | customfield_10011 | selection | {"value": "Team A"} |

## Error Responses

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 Bad Request | Invalid request format | Malformed JSON, invalid JQL |
| 401 Unauthorized | Authentication failed | Wrong credentials, expired token |
| 403 Forbidden | Permission denied | Insufficient project/issue permissions |
| 404 Not Found | Resource not found | Invalid issue key, user not found |
| 429 Too Many Requests | Rate limited | Too many API calls (implement backoff) |
| 500 Internal Server Error | Server error | Temporary issue (retry with backoff) |
| 502 Bad Gateway | Gateway error | Temporary infrastructure issue |
| 503 Service Unavailable | Service down | Maintenance or overload (retry) |

### Error Response Format

```json
{
  "errorMessages": [
    "Error message describing what went wrong"
  ],
  "errors": {
    "fieldName": "Field-specific error message"
  }
}
```

### Example Error: Invalid JQL

```json
{
  "errorMessages": [
    "Error in the JQL Query: the field 'status' is not recognized"
  ],
  "errors": {}
}
```

### Example Error: Invalid Transition

```json
{
  "errorMessages": [
    "Workflow operation error"
  ],
  "errors": {
    "status": "You do not have permission to transition this issue"
  }
}
```

## Rate Limiting

Jira Cloud API rate limits:
- **Authenticated requests**: ~10 requests/second (600/minute)
- **Anonymous requests**: ~5 requests/second (300/minute)
- **Backoff**: Use `X-RateLimit-Reset` header for retry timing

### Response Headers

```
X-RateLimit-Limit: 600
X-RateLimit-Interval-Seconds: 60
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1234567890
```

### Handling Rate Limits

```python
import time
import requests

response = requests.get(url)

if response.status_code == 429:
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
    wait_seconds = reset_time - time.time()
    if wait_seconds > 0:
        print(f"Rate limited. Waiting {wait_seconds} seconds...")
        time.sleep(wait_seconds + 1)
        # Retry the request
        response = requests.get(url)
```

The project's `JiraClient` handles this automatically with exponential backoff.

## Custom Field Discovery

Custom fields vary per Jira instance. Always discover them programmatically:

```python
from jira_tool.client import JiraClient

client = JiraClient()

# Get all fields
fields = client.list_fields()

# Find custom fields
for field in fields:
    if field['custom']:
        print(f"{field['name']}: {field['id']}")

# Find Epic Link field (common patterns)
epic_field_id = client.get_epic_link_field()
```

Common Epic Link field IDs:
- `customfield_11923` (many instances)
- `customfield_10014` (some instances)
- `customfield_10001` (some instances)

Check your instance's fields endpoint to be sure.

## Best Practices Summary

1. **Authentication**: Use API tokens, not passwords. Rotate regularly.
2. **Error Handling**: Always catch exceptions and implement exponential backoff.
3. **Rate Limiting**: Use `maxResults=100` to minimize requests. Cache when possible.
4. **Field Expansion**: Use `expand` and `fields` parameters to optimize payload.
5. **Pagination**: Always implement pagination for large result sets.
6. **JQL Queries**: Keep them simple and use indexes. Avoid complex OR conditions.
7. **Bulk Operations**: Use batch operations where available.
8. **Logging**: Log API responses and errors for debugging.
9. **Timeouts**: Set reasonable timeouts (30s default).
10. **Testing**: Test with sandbox/development Jira instance first.
