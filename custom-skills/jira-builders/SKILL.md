---
name: jira-builders
description: |
  Creates well-formatted Jira issue descriptions using ADF document builders (EpicBuilder, IssueBuilder, SubtaskBuilder).
  Use when creating tickets, epics, or subtasks that need structured descriptions with acceptance criteria,
  implementation details, and rich formatting. Triggers on "create jira ticket", "create epic", "create subtask",
  "jira description", "adf format", "format issue". Works with jira_tool Python package and Atlassian Document Format.
---

# Jira Document Builders Skill

Use the specialized document builders to create well-formatted Jira issue descriptions using Atlassian Document Format (ADF).

## Quick Start

```python
from jira_tool import create_issue, JiraClient

# Create a well-structured ticket in one call
issue = create_issue(
    client=JiraClient(),
    project_key="PROJ",
    title="Implement user login",
    component="Backend",
    description="Add OAuth2 login endpoint",
    implementation_details=["Create /auth/login endpoint", "Validate JWT tokens"],
    acceptance_criteria=["Returns valid JWT", "Handles invalid credentials"],
    epic_key="PROJ-100",
)
print(f"Created: {issue['key']}")
```

## When to Use This Skill

**Explicit triggers:**
- "Create a Jira ticket for..."
- "Create an epic for..."
- "Add a subtask under..."
- "Format this as a Jira description"

**Implicit triggers:**
- When creating any Jira issue that needs structured content
- When batch-creating tickets from requirements
- When enriching existing epics with proper formatting

## Available Builders

### EpicBuilder
For large bodies of work that contain multiple child issues.

```python
from jira_tool.document.builders import EpicBuilder

epic = (
    EpicBuilder(
        title="User Authentication System",
        priority="P1",
        dependencies="Auth0 SDK",
        services="API, Frontend"
    )
    .add_problem_statement("Users cannot securely log in to the application")
    .add_description("Implement OAuth2 authentication flow with session management")
    .add_technical_details([
        "Integrate Auth0 SDK for identity management",
        "Implement JWT token validation",
        "Add session persistence with Redis",
    ])
    .add_acceptance_criteria([
        "User can log in with email/password",
        "User can log in with Google SSO",
        "Session persists across browser refresh",
        "Logout invalidates all active sessions",
    ])
    .add_edge_cases([
        "Handle expired tokens gracefully",
        "Manage concurrent session limits",
    ])
    .add_testing_considerations([
        "Unit tests for token validation",
        "Integration tests for OAuth flow",
        "E2E tests for login/logout journey",
    ])
    .add_out_of_scope([
        "Password-less authentication (future epic)",
        "Two-factor authentication (separate epic)",
    ])
    .add_success_metrics([
        "Login success rate > 99%",
        "Average login time < 2 seconds",
    ])
    .build()
)
```

### IssueBuilder
For standard issues (Tasks, Stories) that represent concrete work items.

```python
from jira_tool.document.builders import IssueBuilder

issue = (
    IssueBuilder(
        title="Implement Login Form Component",
        component="Frontend",
        story_points=5,
        epic_key="PROJ-100"
    )
    .add_description("Create a responsive login form with email and password fields")
    .add_implementation_details([
        "Use React Hook Form for validation",
        "Apply existing design system components",
        "Connect to Auth0 via React SDK",
    ])
    .add_acceptance_criteria([
        "Form validates email format",
        "Password shows/hides toggle works",
        "Error messages display correctly",
        "Loading state shown during submission",
    ])
    .add_technical_notes([
        "Use existing Button and Input components",
        "Follow accessibility guidelines (WCAG 2.1)",
    ])
    .add_dependencies([
        "Blocked by: Auth0 SDK integration (PROJ-101)",
    ])
    .add_testing_notes([
        "Test with screen reader",
        "Test keyboard navigation",
    ])
    .build()
)
```

### SubtaskBuilder
For small, focused pieces of work under a parent issue.

```python
from jira_tool.document.builders import SubtaskBuilder

subtask = (
    SubtaskBuilder(
        title="Add email validation",
        parent_key="PROJ-102",
        estimated_hours=2.0
    )
    .add_description("Implement email format validation using regex")
    .add_steps([
        "Create validation utility function",
        "Add real-time validation feedback",
        "Write unit tests for edge cases",
    ])
    .add_done_criteria([
        "Validation catches invalid formats",
        "Error message is user-friendly",
        "All unit tests pass",
    ])
    .add_notes([
        "Use RFC 5322 compliant regex",
        "Consider allowing + in local part",
    ])
    .build()
)
```

## Integration Functions

Use these for full issue creation with all fields handled:

```python
from jira_tool import JiraClient, create_epic, create_issue, create_subtask

client = JiraClient()

# Create epic
epic = create_epic(
    client=client,
    project_key="PROJ",
    title="Authentication System",
    priority="P1",
    problem_statement="Users cannot log in",
    description="Implement secure authentication",
    technical_requirements=["OAuth2", "JWT"],
    acceptance_criteria=["User can log in", "Sessions persist"],
)

# Create issue under epic
issue = create_issue(
    client=client,
    project_key="PROJ",
    title="Login Form",
    component="Frontend",
    description="Create login form component",
    implementation_details=["React Hook Form", "Auth0 SDK"],
    acceptance_criteria=["Form validates", "Errors shown"],
    epic_key=epic["key"],
)

# Create subtask under issue
subtask = create_subtask(
    client=client,
    project_key="PROJ",
    parent_key=issue["key"],
    title="Email validation",
    description="Add email format validation",
    steps=["Create validator", "Add tests"],
    done_criteria=["Tests pass"],
)
```

## Builder Method Reference

### EpicBuilder Methods
| Method | Purpose |
|--------|---------|
| `add_problem_statement(str)` | Why this epic is needed |
| `add_description(str)` | What the epic delivers |
| `add_technical_details(list, code?, lang?)` | Implementation requirements |
| `add_acceptance_criteria(list)` | How we know it's done |
| `add_edge_cases(list)` | Special cases to handle |
| `add_testing_considerations(list)` | Testing requirements |
| `add_out_of_scope(list)` | What's NOT included |
| `add_success_metrics(list)` | How we measure success |

### IssueBuilder Methods
| Method | Purpose |
|--------|---------|
| `add_description(str)` | What needs to be done |
| `add_implementation_details(list)` | How to implement |
| `add_acceptance_criteria(list)` | Definition of done |
| `add_technical_notes(list)` | Technical considerations |
| `add_code_example(code, lang?, title?)` | Code reference |
| `add_dependencies(list)` | Blockers and dependencies |
| `add_testing_notes(list)` | Testing guidance |

### SubtaskBuilder Methods
| Method | Purpose |
|--------|---------|
| `add_description(str)` | Brief description |
| `add_steps(list)` | Ordered implementation steps |
| `add_done_criteria(list)` | Definition of done |
| `add_notes(list)` | Additional notes |
| `add_code_snippet(code, lang)` | Code reference |
| `add_blockers(list)` | Blocking issues |

## Choosing the Right Builder

| Creating... | Use | When |
|------------|-----|------|
| **Epic** | `EpicBuilder` | Large feature spanning multiple sprints |
| **Story** | `IssueBuilder` | User-facing feature, 1-2 sprints |
| **Task** | `IssueBuilder` | Technical work item, days to 1 sprint |
| **Bug** | `IssueBuilder` | Defect fix with known scope |
| **Sub-task** | `SubtaskBuilder` | Small task under parent, hours to 1 day |

## Best Practices

1. **Always include acceptance criteria** - Every issue should have clear "done" definition
2. **Use appropriate builder** - Epics need scope/metrics, subtasks need steps
3. **Link properly** - Set `epic_key` for issues, `parent_key` for subtasks
4. **Be concise** - ADF renders well, but keep content focused
5. **Test build()** - Always call `.build()` to verify ADF structure before API call

## Red Flags to Avoid

1. **Missing acceptance criteria** - Every ticket needs a definition of done
2. **Wrong builder type** - Don't use EpicBuilder for simple tasks
3. **Forgetting `.build()`** - Builder returns dict only after build() is called
4. **No epic link** - Issues should link to parent epics when applicable
5. **Overly verbose descriptions** - Keep content focused and actionable

## Requirements

- `jira_tool` Python package installed
- Environment variables set: `JIRA_BASE_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
