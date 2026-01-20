---
name: build-jira-document-format
description: |
  Build complex ADF (Atlassian Document Format) documents with advanced patterns, templates,
  and specialized builders. Use when creating sophisticated Jira descriptions, epics with
  structure, or rich content documents. Extends basic ADF knowledge with builder patterns,
  method chaining, and pre-built templates for common layouts.
  Trigger keywords: "ADF template", "document builder", "complex description", "fluent API",
  "epic structure", "formatted issue", "rich content", "builder pattern", "EpicBuilder",
  "IssueBuilder", "document template", "nested content", "advanced formatting".
---

# Build Jira Document Format (Advanced)

## Purpose

Master advanced Atlassian Document Format patterns for creating sophisticated, reusable Jira documents. Learn the builder pattern for fluent APIs, create specialized templates (EpicBuilder, IssueBuilder), design complex nested structures, and build document templates that scale from individual issues to epic planning. Transform raw content into professionally formatted Jira documents.

## Quick Start

Create a formatted epic with problem statement, technical details, and acceptance criteria:

```python
from jira_tool.formatter import EpicBuilder

# Create epic with builder
epic = EpicBuilder("Authentication Overhaul", "P0")
epic.add_problem_statement("Current auth is vulnerable to timing attacks")
epic.add_description("Implement OAuth2 with PKCE and secure session management")
epic.add_technical_details(
    requirements=[
        "PKCE flow support",
        "Session token encryption",
        "Rate limiting"
    ],
    code_example="""
    # OAuth2 flow
    token = oauth_client.get_token(code, pkce_verifier)
    session.set_secure_cookie(token)
    """
)
epic.add_acceptance_criteria([
    "All authentication tests pass",
    "Security audit complete",
    "Rate limiting works per RFC 6749"
])

# Get ADF for Jira API
adf = epic.build()
```

Or build step-by-step with the general-purpose builder:

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()
doc.add_heading("Epic: Authentication System", 1)
doc.add_heading("Problem", 2)
doc.add_panel("warning",
    {"type": "paragraph", "content": [
        doc.add_text("Current authentication has security vulnerabilities")
    ]}
)
doc.add_heading("Approach", 2)
doc.add_bullet_list([
    "Implement OAuth2 with PKCE",
    "Use session token encryption",
    "Add rate limiting"
])
doc.add_heading("Acceptance Criteria", 2)
doc.add_ordered_list([
    "All tests pass",
    "Security audit complete",
    "Rate limiting implemented"
])

adf = doc.build()
```

## Instructions

### Step 1: Understand the Builder Pattern

The builder pattern solves the problem of constructing complex objects through method chaining.

**Why Builders?**

Without builder (verbose):
```python
# Manual ADF construction is error-prone and hard to read
doc = {
    "version": 1,
    "type": "doc",
    "content": [
        {
            "type": "heading",
            "attrs": {"level": 1},
            "content": [{"type": "text", "text": "Title"}]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Start: "},
                {"type": "text", "text": "Bold", "marks": [{"type": "bold"}]}
            ]
        }
    ]
}
```

With builder (readable):
```python
doc = JiraDocumentBuilder()
doc.add_heading("Title", 1)
doc.add_paragraph(
    doc.add_text("Start: "),
    doc.bold("Bold")
)
adf = doc.build()
```

**Builder Benefits**:
1. **Fluent API**: Chain methods for readability
2. **Safety**: Builders handle nesting automatically
3. **Reusability**: Extend builders for custom layouts
4. **Validation**: Catch errors early

### Step 2: Master the JiraDocumentBuilder

The general-purpose builder is your foundation:

**Method Chaining** (call methods in sequence):
```python
doc = JiraDocumentBuilder()
doc.add_heading("Title", 1) \
    .add_paragraph(doc.add_text("Introduction")) \
    .add_rule() \
    .add_heading("Section", 2) \
    .add_bullet_list(["Point 1", "Point 2"])

adf = doc.build()
```

**Key Methods**:

1. **Structural Elements**:
   ```python
   doc.add_heading("Text", level=1)      # Level 1-6
   doc.add_paragraph(content_nodes)       # Mixed content
   doc.add_rule()                         # Horizontal line
   ```

2. **Lists**:
   ```python
   doc.add_bullet_list(["Item 1", "Item 2"])
   doc.add_ordered_list(["First", "Second"], start=1)
   ```

3. **Code Blocks**:
   ```python
   doc.add_code_block("def hello(): pass", language="python")
   ```

4. **Panels** (colored boxes):
   ```python
   doc.add_panel("info",
       {"type": "paragraph", "content": [doc.add_text("Info panel")]}
   )
   # Types: info, note, warning, success, error
   ```

5. **Visual Elements**:
   ```python
   doc.add_rule()                         # Separator
   emoji = doc.add_emoji(":rocket:", "🚀")  # Emoji
   ```

**Text Content Helpers**:

```python
# Create formatted text nodes
doc.bold("Bold text")              # Returns text node with bold mark
doc.italic("Italic text")           # Returns text node with italic mark
doc.code("inline_code")             # Returns text node with code mark
doc.strikethrough("Deleted")        # Returns text node with strikethrough
doc.link("Click here", "https://...") # Returns text node with link
doc.add_text("Plain text")          # Plain text node
```

**Combining Formatting**:
```python
doc.add_paragraph(
    doc.bold("Important: "),
    doc.add_text("This is a ")
    doc.italic("complex"),
    doc.add_text(" message")
)
```

### Step 3: Create Specialized Builders for Common Patterns

For repeated structures, build specialized builders (subclass or composition):

**Pattern 1: Titled Panels** (common pattern):
```python
def add_titled_panel(builder, title, panel_type, content):
    """Add a heading followed by a panel."""
    builder.add_heading(title, 2)
    builder.add_panel(panel_type, {
        "type": "paragraph",
        "content": [builder.add_text(content)]
    })

# Usage
doc = JiraDocumentBuilder()
add_titled_panel(doc, "⚠️ Risks", "warning", "Performance impact on v1 API")
add_titled_panel(doc, "✅ Benefits", "success", "Eliminates 50% of CPU usage")
```

**Pattern 2: Key-Value Pairs** (common in specifications):
```python
def add_kv_section(builder, title, pairs):
    """Add a section with key-value pairs."""
    builder.add_heading(title, 2)
    items = []
    for key, value in pairs.items():
        items.append(f"{key}: {value}")
    builder.add_bullet_list(items)

# Usage
doc = JiraDocumentBuilder()
add_kv_section(doc, "Specifications", {
    "Language": "Python 3.10+",
    "Framework": "FastAPI",
    "Database": "PostgreSQL 13"
})
```

**Pattern 3: Feature Lists** (for requirements):
```python
def add_feature_list(builder, title, features):
    """Add a section with feature checklist."""
    builder.add_heading(title, 2)
    items = [f"☐ {f}" for f in features]
    builder.add_bullet_list(items)

# Usage
doc = JiraDocumentBuilder()
add_feature_list(doc, "Must-Have Features", [
    "User authentication",
    "Database persistence",
    "API rate limiting"
])
```

### Step 4: Extend with Specialized Builders

Create purpose-built builders for complex documents:

**Example: EpicBuilder** (from codebase)
```python
from jira_tool.formatter import EpicBuilder

class EpicBuilder:
    """Pre-formatted epic template."""

    def __init__(self, title: str, priority: str = "P1"):
        self.title = title
        self.priority = priority
        self.builder = JiraDocumentBuilder()
        self._add_header()

    def _add_header(self):
        """Add standardized header."""
        self.builder.add_heading(f"🎯 {self.title}", 1)
        self.builder.add_paragraph(
            self.builder.bold("Priority: "),
            self.builder.add_text(self.priority)
        )

    def add_problem_statement(self, statement: str):
        """Add problem section."""
        self.builder.add_heading("Problem Statement", 2)
        self.builder.add_panel("warning", {
            "type": "paragraph",
            "content": [self.builder.add_text(statement)]
        })
        return self

    def add_acceptance_criteria(self, criteria: list[str]):
        """Add acceptance criteria."""
        self.builder.add_heading("Acceptance Criteria", 2)
        self.builder.add_ordered_list(criteria)
        return self

    def build(self):
        """Return ADF."""
        return self.builder.build()
```

**Usage**:
```python
epic = EpicBuilder("New Auth System", "P0")
epic.add_problem_statement("Current auth is insecure")
epic.add_acceptance_criteria([
    "OAuth2 implemented",
    "Tests pass",
    "Security audit complete"
])

adf = epic.build()
```

**Template Benefits**:
- Consistent structure across epics
- Enforces best practices
- Reduces boilerplate
- Easy to extend with custom methods

### Step 5: Design Complex Nested Structures

ADF supports hierarchical nesting for sophisticated layouts:

**Complex Example: Multi-Level Epic with Risk Assessment**

```python
doc = JiraDocumentBuilder()

# Header
doc.add_heading("🚀 Payment System Redesign", 1)
doc.add_paragraph(
    doc.bold("Priority: "), doc.add_text("P0"),
    doc.add_text(" | "),
    doc.bold("Timeline: "), doc.add_text("Q2 2024")
)

# Problem section
doc.add_heading("Problem", 2)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("Current system handles only credit cards; enterprise needs ACH/wire")]
})

# Solution approach
doc.add_heading("Solution Approach", 2)
doc.add_bullet_list([
    "Abstract payment gateway interface",
    "Implement ACH driver with bank reconciliation",
    "Add webhook for transaction status"
])

# Technical requirements
doc.add_heading("Technical Requirements", 2)
doc.add_ordered_list([
    "Design payment abstraction",
    "Implement ACH provider integration",
    "Add transaction state machine",
    "Create reconciliation batch process"
])

# Code example
doc.add_heading("Reference Implementation", 2)
doc.add_code_block("""
class PaymentGateway:
    def process(self, amount, method):
        driver = self._get_driver(method)
        return driver.charge(amount)

    def _get_driver(self, method):
        if method == 'ach':
            return ACHDriver()
        elif method == 'credit':
            return CreditCardDriver()
""", language="python")

# Risk assessment
doc.add_heading("Risk Assessment", 2)
doc.add_heading("Financial Risk", 3)
doc.add_panel("error", {
    "type": "paragraph",
    "content": [doc.add_text("ACH payments are slow and reversible; implement hold period")]
})
doc.add_heading("Integration Risk", 3)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("Requires new bank partnership; 2-week setup time")]
})

# Acceptance criteria
doc.add_heading("Acceptance Criteria", 2)
doc.add_ordered_list([
    "ACH charges succeed with test account",
    "Reconciliation matches bank records",
    "All error cases handled",
    "Documentation complete",
    "Load test passes (100+ TPS)"
])

# Dependencies
doc.add_heading("Dependencies", 2)
doc.add_bullet_list([
    "Bank partnership agreement",
    "Infrastructure team support",
    "Security review approval"
])

adf = doc.build()
```

### Step 6: Implement Builder Best Practices

**Best Practice 1: Return self for Chaining**
```python
class CustomBuilder:
    def add_something(self) -> "CustomBuilder":
        # ... implementation
        return self  # Allow chaining

# Usage
builder.add_a().add_b().add_c().add_d()
```

**Best Practice 2: Lazy Content**
```python
# ❌ Don't require all content upfront
def __init__(self, title, items, criteria):
    pass

# ✅ Build step-by-step
def __init__(self, title):
    self.title = title

def add_items(self, items):
    # ...
    return self

def add_criteria(self, criteria):
    # ...
    return self
```

**Best Practice 3: Validate Before Building**
```python
def build(self) -> dict:
    """Build and validate before returning."""
    if not self.title:
        raise ValueError("Title is required")
    if not self.builder.content:
        raise ValueError("Content is empty")

    return self.builder.build()
```

**Best Practice 4: Document Structure**
```python
class DocumentTemplate:
    """
    Template for standard epic documentation.

    Structure:
    - Header (title, priority, timeline)
    - Problem statement (warning panel)
    - Solution approach (bullet list)
    - Technical requirements (ordered list)
    - Code examples (code blocks)
    - Risk assessment (info/warning panels)
    - Acceptance criteria (ordered list)
    - Dependencies (bullet list)
    """

    def __init__(self, title: str):
        pass
```

### Step 7: Reuse and Extend Builders

**Pattern: Builder Inheritance**
```python
class BaseIssueBuilder(JiraDocumentBuilder):
    """Base for all issue templates."""

    def add_standard_header(self, title: str, issue_type: str):
        self.add_heading(title, 1)
        self.add_paragraph(
            self.bold(f"Type: "),
            self.add_text(issue_type)
        )
        return self

class BugBuilder(BaseIssueBuilder):
    """Specialized builder for bug reports."""

    def add_reproduction_steps(self, steps: list[str]):
        self.add_heading("Steps to Reproduce", 2)
        self.add_ordered_list(steps)
        return self

    def add_expected_vs_actual(self, expected: str, actual: str):
        self.add_heading("Expected vs Actual", 2)
        self.add_paragraph(
            self.bold("Expected: "),
            self.add_text(expected)
        )
        self.add_paragraph(
            self.bold("Actual: "),
            self.add_text(actual)
        )
        return self

# Usage
bug = BugBuilder()
bug.add_standard_header("Login fails on Safari", "Bug")
bug.add_reproduction_steps([
    "Open Safari 17",
    "Visit login.example.com",
    "Click 'Sign In with Google'",
    "Approve permissions"
])
bug.add_expected_vs_actual(
    "Redirect to dashboard",
    "Blank page with JS console error"
)

adf = bug.build()
```

## Examples

### Example 1: Create Structured Epic

```python
from jira_tool.formatter import EpicBuilder

epic = EpicBuilder("Migrate to PostgreSQL 15", "P1", dependencies="Database migration tool")
epic.add_problem_statement(
    "Current MySQL 5.7 is EOL. Must upgrade for security patches and performance."
)
epic.add_description(
    "Migrate data, update connection pools, test thoroughly, then cutover to PostgreSQL 15."
)
epic.add_technical_details(
    requirements=[
        "Schema migration preserves all data",
        "Zero downtime migration",
        "Rollback plan ready",
        "Performance benchmarking complete"
    ],
    code_example="""
    -- Migration strategy
    1. Create PostgreSQL schema
    2. Use logical replication for sync
    3. Test with production data copy
    4. Cutover during maintenance window
    5. Verify integrity
    """,
    code_language="sql"
)
epic.add_acceptance_criteria([
    "Data migrated with zero loss",
    "Query performance >= MySQL baseline",
    "All tests pass",
    "Rollback tested and documented",
    "Production data verified"
])

adf = epic.build()
```

### Example 2: Complex Feature Request

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()

# Overview
doc.add_heading("Add Two-Factor Authentication", 1)
doc.add_paragraph(
    doc.bold("User Impact: "),
    doc.add_text("Users can secure accounts with TOTP/SMS")
)

# Use cases
doc.add_heading("Use Cases", 2)
doc.add_ordered_list([
    "User enables 2FA with TOTP app (Authy/Google Authenticator)",
    "User enables 2FA with SMS verification code",
    "User signs in with password + 2FA code",
    "User recovers account with backup codes"
])

# Design
doc.add_heading("Technical Design", 2)

doc.add_heading("Components", 3)
doc.add_bullet_list([
    "TOTP generator (time-based one-time password)",
    "SMS gateway integration (Twilio)",
    "Recovery code generation",
    "Session validation with 2FA"
])

doc.add_heading("Database Changes", 3)
doc.add_code_block("""
ALTER TABLE users ADD COLUMN totp_secret VARCHAR(32);
ALTER TABLE users ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN sms_number VARCHAR(20);

CREATE TABLE recovery_codes (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users,
    code VARCHAR(12) UNIQUE,
    used_at TIMESTAMP
);
""", language="sql")

# Acceptance criteria
doc.add_heading("Acceptance Criteria", 2)
doc.add_ordered_list([
    "User can enable TOTP via settings",
    "QR code generated for authenticator apps",
    "Recovery codes downloaded or emailed",
    "Login validates TOTP token",
    "SMS 2FA available as alternative",
    "Backup codes work for account recovery",
    "All tests pass (unit + integration)"
])

# Risks
doc.add_heading("Risks & Mitigation", 2)

doc.add_heading("Risk: Lost 2FA Device", 3)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("User can't access account. Mitigation: Backup codes + email recovery")]
})

doc.add_heading("Risk: SMS Spoofing", 3)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("SMS codes intercepted. Mitigation: Prefer TOTP, SMS as fallback only")]
})

adf = doc.build()
```

### Example 3: Custom Builder for Bug Reports

```python
from jira_tool.formatter import JiraDocumentBuilder

class BugReportBuilder(JiraDocumentBuilder):
    """Specialized builder for structured bug reports."""

    def __init__(self, title: str, severity: str = "Medium"):
        super().__init__()
        self.title = title
        self.severity = severity
        self.add_header()

    def add_header(self):
        self.add_heading(f"🐛 {self.title}", 1)
        self.add_paragraph(
            self.bold("Severity: "),
            self.add_text(self.severity)
        )
        return self

    def add_environment(self, browser: str, os: str):
        self.add_heading("Environment", 2)
        self.add_bullet_list([
            f"Browser: {browser}",
            f"OS: {os}"
        ])
        return self

    def add_reproduction_steps(self, steps: list[str]):
        self.add_heading("Steps to Reproduce", 2)
        self.add_ordered_list(steps)
        return self

    def add_expected_result(self, result: str):
        self.add_heading("Expected Result", 2)
        self.add_panel("success", {
            "type": "paragraph",
            "content": [self.add_text(result)]
        })
        return self

    def add_actual_result(self, result: str):
        self.add_heading("Actual Result", 2)
        self.add_panel("error", {
            "type": "paragraph",
            "content": [self.add_text(result)]
        })
        return self

    def add_error_log(self, error: str):
        self.add_heading("Error Log", 2)
        self.add_code_block(error, language="text")
        return self

# Usage
bug = BugReportBuilder("Login button unresponsive on mobile", "Critical")
bug.add_environment("Safari 17", "iOS 17.1")
bug.add_reproduction_steps([
    "Open app on iPhone 14",
    "Tap login button",
    "Wait 3 seconds"
])
bug.add_expected_result("Login form appears immediately")
bug.add_actual_result("Button freezes, requires page refresh")
bug.add_error_log("""
TypeError: Cannot read property 'click' of null
    at Object.<anonymous> (app.js:234:15)
    at Module._load (internal/modules/loader.js:580:5)
""")

adf = bug.build()
```

## Requirements

### Core Requirements
- **Python 3.10+** (for type hints and dataclass improvements)
- **jira_tool.formatter module** from this project containing:
  - `JiraDocumentBuilder` - General-purpose builder
  - `EpicBuilder` - Epic-specific template
  - `IssueBuilder` - Issue-specific template

### For Testing Builders
- **Jira REST API v3 access** (to submit built documents)
- **Environment variables**: `JIRA_BASE_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
- **Test project** where you can create issues

### Recommended Tools
- **jira_adf_validator** (https://github.com/atlassian-community/jira-adf-validator):
  ```bash
  npm install -g jira-adf-validator
  echo '{"version":1,"type":"doc","content":[]}' | jira-adf-validator
  ```
- **Python json**: Built-in (for validating ADF structure)
- **curl**: For testing API submissions

## See Also

- [Work with ADF](/skills/work-with-adf) - Basic ADF concepts and structure
- [Jira REST API](/skills/jira-api) - API endpoints for creating/updating documents
- [Export and Analyze Jira Data](/skills/export-and-analyze-jira-data) - Generating report documents
- CLAUDE.md - Project configuration and patterns
- src/jira_tool/formatter.py - Full builder implementation reference
