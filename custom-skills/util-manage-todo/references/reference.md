# Manage Todo - Technical Reference

Complete technical documentation for the manage-todo skill consolidating state management, synchronization protocol, and refactor tracking.

## Python Example Modules

The following utility modules provide the core functionality for todo management:

- [todo_types.py](../examples/todo_types.py) - Dataclass definitions for Task and Todo objects with state enums
- [todo_manager.py](../examples/todo_manager.py) - Core CRUD operations for todo lists and tasks with markdown parsing
- [state_manager.py](../examples/state_manager.py) - Task state management, validation, and state transition logic
- [todowrite_sync.py](../examples/todowrite_sync.py) - Synchronization between todo.md and TodoWrite tool with state mapping
- [refactor_validator.py](../examples/refactor_validator.py) - ADR validation for refactor/migration work with keyword detection
- [template_loader.py](../examples/template_loader.py) - Template loading and selection utilities for different task types

---

## Table of Contents

- [Part 1: Task State Management](#part-1-task-state-management)
  - [Task States](#task-states)
  - [State Transition Rules](#state-transition-rules)
  - [State Management Workflows](#state-management-workflows)
  - [Progress Tracking](#progress-tracking)
  - [Anti-Patterns & Best Practices](#anti-patterns--best-practices)
- [Part 2: TodoWrite Synchronization](#part-2-todowrite-synchronization)
  - [Core Principles](#core-principles)
  - [Synchronization Workflows](#synchronization-workflows)
  - [State Mapping](#state-mapping)
  - [Validation & Error Handling](#validation--error-handling)
  - [Sync Best Practices](#sync-best-practices)
- [Part 3: Refactor & Migration Tracking](#part-3-refactor--migration-tracking)
  - [ADR Requirements](#adr-requirements)
  - [Refactor Markers](#refactor-markers)
  - [Refactor Todo Structure](#refactor-todo-structure)
  - [Health Checks](#health-checks)
  - [Rollback Plans](#rollback-plans)

---

# Part 1: Task State Management

Comprehensive guide to task state transitions, rules, and workflows.

## Task States

### 🔴 Not Started (Pending)

**Definition:** Task has been identified but work has not begun.

**When to use:**
- Task is in the backlog
- Dependencies not yet met
- Waiting to be assigned
- Planning is complete, ready for execution

**Allowed transitions:**
- 🔴 → 🟡 (Start work)
- 🔴 → ⚫ (Discovered blocker before starting)
- 🔴 → 🗑️ (Remove if no longer needed)

**Characteristics:**
- No code changes
- No time invested
- May have assigned owner
- May have priority set

**Example:**
```markdown
### Task 3: Implement caching layer
**Status:** 🔴 Not Started
**Priority:** Medium
**Assigned:** @backend-developer

**Description:**
Add Redis caching to reduce database load.

**Notes:**
Waiting for Tasks 1-2 to complete before starting.
```

---

### 🟡 In Progress

**Definition:** Task is actively being worked on.

**When to use:**
- Developer has started implementation
- Code changes are being made
- Tests are being written
- Currently in an active session

**Allowed transitions:**
- 🟡 → 🟢 (Complete)
- 🟡 → ⚫ (Blocked)
- 🟡 → 🔴 (Pause work, return to backlog)

**Characteristics:**
- Partial code changes exist
- Time is being invested
- May have work-in-progress notes
- Should have clear owner

**Best practices:**
- ✅ Update progress notes regularly
- ✅ Track blockers immediately
- ✅ Keep subtask checklist current
- ✅ Sync with TodoWrite frequently
- ❌ Don't leave in this state >7 days without update

**Example:**
```markdown
### Task 2: Build authentication service
**Status:** 🟡 In Progress
**Priority:** High
**Assigned:** @backend-developer
**Started:** 2025-10-15

**Implementation Checklist:**
- [x] User model created
- [x] JWT service implemented
- [ ] Login endpoint (60% done)
- [ ] Unit tests
```

---

### 🟢 Complete

**Definition:** All acceptance criteria met, task is done.

**When to use:**
- Implementation complete
- Tests passing
- Code reviewed (if required)
- Acceptance criteria validated
- No known issues

**Allowed transitions:**
- 🟢 → 🟡 (Reopen if issues found)
- 🟢 → 🗑️ (Archive after project complete)

**Completion checklist:**
- [ ] Functionality works as specified
- [ ] Tests pass with adequate coverage
- [ ] Code follows project conventions
- [ ] Documentation updated
- [ ] Code reviewed (if required)
- [ ] Quality gates pass

**Example:**
```markdown
### Task 1: Setup database schema
**Status:** 🟢 Complete
**Completed:** 2025-10-15

**Notes:**
- Migration: 001_create_users_table.sql
- Tests: test_user_schema.py (100% coverage)
- Reviewed by: @tech-lead
```

---

### ⚫ Blocked

**Definition:** Work is paused due to external dependency or unresolved issue.

**When to use:**
- Waiting on another task
- Waiting on external team/service
- Technical blocker (e.g., bug in dependency)
- Decision needed from stakeholder
- Resource unavailable

**Allowed transitions:**
- ⚫ → 🟡 (Resume when blocker resolved)
- ⚫ → 🔴 (Return to backlog if blocker long-term)

**Blocker documentation requirements:**
- **What:** Clear description of blocker
- **Why:** Root cause of blocker
- **Impact:** What's blocked (just this task or others?)
- **Owner:** Who can unblock
- **ETA:** When expected to be resolved
- **Workaround:** Alternative approach if available

**Example:**
```markdown
### Task 5: Deploy to production
**Status:** ⚫ Blocked

**Blocker:**
- **What:** Production Kubernetes cluster needs security approval
- **Why:** New service requires elevated permissions
- **Impact:** Blocks deployment (Tasks 5-7)
- **Owner:** Security team (ticket #SEC-456)
- **ETA:** 2025-10-20 (3 days)
- **Workaround:** Can deploy to staging
```

---

## State Transition Rules

### Valid Transitions

```
🔴 Not Started
  ├─→ 🟡 In Progress (start work)
  ├─→ ⚫ Blocked (discovered blocker)
  └─→ 🗑️ Remove (no longer needed)

🟡 In Progress
  ├─→ 🟢 Complete (finish work)
  ├─→ ⚫ Blocked (hit blocker)
  └─→ 🔴 Not Started (pause/reset)

🟢 Complete
  ├─→ 🟡 In Progress (reopen)
  └─→ 🗑️ Archive (cleanup)

⚫ Blocked
  ├─→ 🟡 In Progress (resume)
  └─→ 🔴 Not Started (reset)
```

### Transition Actions

#### 🔴 → 🟡 (Starting Work)

**Actions:**
1. Update status to 🟡
2. Add "Started: [date]" field
3. Ensure assigned owner is set
4. Initialize subtask checklist
5. Sync with TodoWrite

#### 🟡 → 🟢 (Completing Work)

**Actions:**
1. Verify completion checklist
2. Update status to 🟢
3. Add "Completed: [date]" field
4. Update progress summary
5. Move to Completed section (if exists)
6. Sync with TodoWrite

#### 🟡 → ⚫ (Hitting Blocker)

**Actions:**
1. Update status to ⚫
2. Document blocker (what, why, impact, owner, ETA)
3. Assess impact on other tasks
4. Escalate if critical path blocked
5. Identify alternative work
6. Sync with TodoWrite

#### ⚫ → 🟡 (Unblocking)

**Actions:**
1. Update status to 🟡
2. Document resolution
3. Resume from where left off
4. Update ETA if changed
5. Sync with TodoWrite

---

## State Management Workflows

### Workflow 1: Linear Task Progression

```
🔴 Not Started
  ↓ (Start work)
🟡 In Progress
  - Implement feature
  - Write tests
  ↓ (Complete)
🟢 Complete
```

### Workflow 2: Task with Blocker

```
🔴 Not Started
  ↓ (Start work)
🟡 In Progress (50%)
  ↓ (Hit blocker)
⚫ Blocked
  ↓ (Blocker resolved after 2 days)
🟡 In Progress (50% → 100%)
  ↓ (Complete)
🟢 Complete
```

### Workflow 3: Task with Reopen

```
🔴 → 🟡 → 🟢 Complete
  ↓ (Bug found in QA)
🟡 In Progress (Reopened)
  - Fix bug
  - Add regression test
  ↓ (Fix complete)
🟢 Complete
```

---

## Progress Tracking

### Calculating Progress Percentage

```python
def calculate_progress(tasks: List[Task]) -> float:
    """Calculate completion percentage"""
    if not tasks:
        return 0.0

    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == "🟢")

    return (completed / total) * 100

# Example: 2 complete out of 5 tasks = 40%
```

### Velocity Tracking

```python
def calculate_velocity(completed_tasks: List[Task], time_period_days: int) -> float:
    """Calculate tasks completed per day"""
    return len(completed_tasks) / time_period_days

# Example: 10 tasks in 5 days = 2 tasks/day
# Remaining: 15 tasks → ETA: 15/2 = 7.5 days
```

### Progress Reporting Format

```markdown
## Progress Summary
- Total Tasks: 10
- Completed: 4 (40%)
- In Progress: 2 (Tasks 5, 6)
- Blocked: 1 (Task 8)
- Pending: 3 (Tasks 9-11)

**Velocity:** 2 tasks/day (last 5 days)
**ETA:** 3 more days to completion

**Next Up:**
1. Complete Task 5 (80% done)
2. Complete Task 6 (30% done)
3. Unblock Task 8 or start Task 9
```

---

## Anti-Patterns & Best Practices

### ❌ Anti-Pattern 1: Stale "In Progress"

**Problem:** Task left as 🟡 In Progress for weeks without updates

**Why it's bad:**
- No visibility into actual progress
- Can't calculate accurate completion ETA

**Solution:**
- Update progress notes weekly at minimum
- If paused >7 days, move to 🔴 or ⚫
- Use subtask checklist to show progress

---

### ❌ Anti-Pattern 2: Unmarked Blockers

**Problem:** Task is 🟡 In Progress but actually blocked, not marked ⚫

**Why it's bad:**
- Progress metrics inaccurate
- Blockers not visible to team
- Can't escalate or find workarounds

**Solution:**
- Mark ⚫ Blocked immediately when blocked
- Document blocker clearly
- Escalate if on critical path

---

### ❌ Anti-Pattern 3: Premature Completion

**Problem:** Marking task 🟢 Complete before all acceptance criteria met

**Why it's bad:**
- Incomplete work looks done
- Progress metrics misleading
- Work may need reopening

**Solution:**
- Use completion checklist
- Verify all acceptance criteria
- If partially done, keep as 🟡 with progress notes

---

### ✅ Best Practice 1: Frequent Updates

**Update task state immediately when:**
- Starting work (🔴 → 🟡)
- Hitting blocker (🟡 → ⚫)
- Unblocking (⚫ → 🟡)
- Completing (🟡 → 🟢)

**Update progress notes at least:**
- Daily for active tasks
- Weekly for blocked tasks
- End of each session

---

### ✅ Best Practice 2: Granular Subtasks

```markdown
**Implementation Checklist:**
- [x] Subtask 1 (complete)
- [x] Subtask 2 (complete)
- [ ] Subtask 3 (in progress - 60% done)
- [ ] Subtask 4 (not started)

**Current Focus:** Subtask 3, working on validation logic
```

---

# Part 2: TodoWrite Synchronization

Detailed guide for keeping TodoWrite tool and todo.md files in perfect sync.

## Core Principles

### Principle 1: todo.md is Source of Truth

**Always:**
- Update todo.md first
- Then sync TodoWrite to match
- Never update only TodoWrite

**Why:**
- todo.md persists across sessions
- todo.md is version controlled (git)
- todo.md is human-readable
- todo.md works without tools

### Principle 2: Immediate Synchronization

**When to sync:**
- After creating todo.md → Initialize TodoWrite
- After updating task state → Update TodoWrite immediately
- After adding/removing tasks → Update TodoWrite immediately
- Before progress reports → Validate sync first

**Never:**
- Update todo.md and "sync later"
- Update TodoWrite without updating todo.md
- Assume sync is automatic

### Principle 3: Fail-Safe Validation

**Always validate:**
- After every state change
- Before progress reports
- When resuming work after breaks
- When switching between agents

**If mismatch found:**
- Log the discrepancy
- Update TodoWrite to match todo.md
- Report sync issue to user

---

## Synchronization Workflows

### Workflow 1: Create New Todo List

**Step 1: Create todo.md**
```markdown
# Todo: Authentication Feature
Date: 2025-10-17

## Tasks

### Task 1: Implement user model
**Status:** 🔴 Not Started
**Priority:** High
```

**Step 2: Initialize TodoWrite**
```python
TodoWrite({
    "todos": [
        {
            "content": "Task 1: Implement user model",
            "status": "pending",
            "activeForm": "Implementing user model"
        }
    ]
})
```

**Step 3: Verify Sync**
- Check both show same task count
- Check all show matching states
- Confirm to user

---

### Workflow 2: Update Task State

**Step 1: Update todo.md (Source of Truth)**
```markdown
### Task 1: Implement user model
**Status:** 🟡 In Progress  ← Changed from 🔴
**Started:** 2025-10-17
```

**Step 2: Update TodoWrite to Match**
```python
TodoWrite({
    "todos": [
        {
            "content": "Task 1: Implement user model",
            "status": "in_progress",  ← Changed
            "activeForm": "Implementing user model"
        }
    ]
})
```

**Step 3: Validate and Confirm**
```
✅ Task 1 status updated to In Progress
✅ TodoWrite synced
✅ Progress: 0/3 tasks in progress
```

---

## State Mapping

### todo.md States → TodoWrite States

| todo.md | Emoji | TodoWrite | Description |
|---------|-------|-----------|-------------|
| Not Started | 🔴 | `pending` | Task not begun |
| In Progress | 🟡 | `in_progress` | Actively working |
| Complete | 🟢 | `completed` | All done |
| Blocked | ⚫ | `pending` + note | Waiting on dependency |

### Special Cases

**Blocked Tasks:**
- todo.md: Use ⚫ Blocked with blocker documentation
- TodoWrite: Use `pending` status + add blocker note in content
- Reason: TodoWrite doesn't have native "blocked" state

**Example:**
```python
# todo.md shows ⚫ Blocked
TodoWrite({
    "todos": [
        {
            "content": "Task 5: Deploy (BLOCKED: waiting on security)",
            "status": "pending",
            "activeForm": "Deploying to production"
        }
    ]
})
```

---

## Validation & Error Handling

### Sync Validation Algorithm

```python
def validate_full_sync(todo_file: str) -> SyncReport:
    """Comprehensive sync validation"""
    todo_tasks = parse_todo_file(todo_file)
    write_tasks = get_todowrite_tasks()

    report = SyncReport()

    # Check task counts
    if len(todo_tasks) != len(write_tasks):
        report.add_mismatch("count")
        sync_todowrite_from_file(todo_file)

    # Check each task state
    for i, (todo_task, write_task) in enumerate(zip(todo_tasks, write_tasks)):
        if not states_match(todo_task.status, write_task.status):
            report.add_mismatch("state", task_id=i+1)
            update_todowrite_task(i, map_state(todo_task.status))

    return report
```

### Common Sync Errors

#### Error 1: Task Count Mismatch

**Symptoms:** todo.md has 5 tasks, TodoWrite shows 4 tasks

**Causes:**
- Task added to todo.md but not TodoWrite
- Task removed from todo.md but not TodoWrite

**Fix:**
```python
# Re-sync entire task list from todo.md
tasks = parse_todo_file("todo.md")
todowrite_tasks = [map_task(t) for t in tasks]
TodoWrite({"todos": todowrite_tasks})
```

#### Error 2: State Mismatch

**Symptoms:** todo.md shows 🟢 Complete, TodoWrite shows `in_progress`

**Causes:**
- todo.md updated but TodoWrite not synced
- Manual edit to todo.md

**Fix:**
```python
# Update specific task in TodoWrite
todo_state = get_task_state_from_file(task_id=2)
update_todowrite_task(task_id=2, new_status=map_state(todo_state))
```

---

## Sync Best Practices

### ✅ DO: Update Both Simultaneously

```python
def update_task_state(task_id: int, new_state: str):
    """Update task state in both systems atomically"""
    # 1. Update todo.md (source of truth)
    update_todo_file(task_id, new_state)

    # 2. Update TodoWrite to match
    update_todowrite(task_id, map_state(new_state))

    # 3. Validate sync
    validate_sync(task_id)

    return {"synced": True}
```

### ✅ DO: Validate Before Reporting

```python
def get_progress_report(todo_file: str):
    """Get progress report with sync validation"""
    # 1. Validate sync first
    sync_report = validate_full_sync(todo_file)

    # 2. If mismatches, fix them
    if sync_report.has_mismatches():
        log_warning(f"Sync issues fixed")

    # 3. Generate accurate report
    return generate_progress_report(todo_file)
```

### ❌ DON'T: Update Only TodoWrite

**Why bad:** Single source of truth violated

**Fix:** Always update todo.md first, then sync TodoWrite

### ❌ DON'T: Assume Sync is Automatic

**Why bad:** No automatic sync, states can diverge

**Fix:** Explicitly sync after any manual edit

---

# Part 3: Refactor & Migration Tracking

Comprehensive guide for tracking refactors and migrations with ADR integration.

## ADR Requirements

### Core Requirement

**All refactor/migration work REQUIRES an ADR document.**

No exceptions.

### ADR Directory Structure

```
docs/adr/
├── not_started/      # Proposed ADRs, work not begun
├── in_progress/      # Active refactor work
└── implemented/      # Completed refactors
```

**ADR Lifecycle:**
1. Created in `not_started/`
2. Moved to `in_progress/` when work begins
3. Moved to `implemented/` when work complete

---

## Pre-Refactor Validation

### Refactor Keywords

Words that trigger refactor validation:
- refactor, migrate, migration
- convert, conversion
- adopt pattern
- breaking change
- multi-file change
- across, system-wide
- deprecate and replace

### Validation Process

**Step 1: Detect refactor work**
```bash
if [[ $description =~ (refactor|migrate|convert|breaking) ]]; then
    refactor_detected=true
fi
```

**Step 2: Search for ADR**
```bash
find docs/adr -name "*<topic>*"
```

**Step 3: Validate**
```bash
if [[ $refactor_detected == true && -z $adr_files ]]; then
    echo "❌ STOP: Refactor work requires an ADR document"
    exit 1
fi
```

### ADR Creation Workflow

**If refactor detected but no ADR:**

1. **Stop immediately** - Do not create todo.md
2. **Inform user:**
   ```
   ❌ Refactor/migration work requires an ADR document.

   Create ADR using template:
   cp docs/adr/TEMPLATE-refactor-migration.md \
      docs/adr/not_started/027-title.md

   After ADR created, run this command again.
   ```

3. **Wait for ADR creation**

4. **Validate ADR exists, then proceed**

---

## Refactor Markers

### What are Refactor Markers?

**Purpose:** Visual indicators in source files showing active refactor work

**Benefits:**
- Quickly identify files under refactor
- Track refactor progress
- Link code to ADR documentation

### Marker Types

#### File-Level Marker

```python
# REFACTOR: ADR-027 ServiceResult Pattern Migration
# STATUS: IN_PROGRESS
# STARTED: 2025-10-17
# PERMANENT_RECORD: docs/adr/in_progress/027-title.md
# Active Tracking: todo.md "Refactor: Title"
# SCOPE: Convert Optional[T] returns to ServiceResult[T]
# OWNER: @backend-team
```

#### Method-Level Marker

```python
class UserService:
    # REFACTOR(ADR-027): Convert to ServiceResult pattern
    # Current: Returns None on error
    # Target: Returns ServiceResult[User]
    # Status: IN_PROGRESS
    def get_user(self, user_id: int) -> Optional[User]:
        pass
```

### Marker Lifecycle

**Phase 1: Add Markers (Before Refactoring)**
```python
# REFACTOR: ADR-027 Title
# STATUS: IN_PROGRESS
# ... OLD CODE (not refactored yet)
```

**Phase 2: During Refactoring**
```python
# REFACTOR: ADR-027 Title
# NOTES: 2/5 methods converted
# ... MIXED OLD/NEW CODE
```

**Phase 3: Remove Markers (After Completion)**
```python
# Markers removed - refactor complete
# ... NEW CODE (refactored)
```

### Marker Detection

```bash
# Find file-level markers
grep -rn "^# REFACTOR:" src/ --include="*.py"

# Find method-level markers
grep -rn "# REFACTOR(" src/ --include="*.py"

# Count markers by ADR
grep -rn "REFACTOR.*ADR-027" src/ | wc -l
```

---

## Refactor Todo Structure

### Key Elements

A refactor todo must include:

1. **ADR Reference** - Link to ADR document
2. **Refactor Context** - Scope, pattern, markers required
3. **Marker Tasks** - Task 1 adds markers, Task N+1 removes
4. **Phase Structure** - Break work into logical phases
5. **Health Checks** - Monitor stale markers and progress

### Minimal Template

```markdown
# Refactor: [Title] (ADR-XXX)
Date: 2025-10-17
Memory: adr_XXX_refactor_name
ADR: docs/adr/in_progress/XXX-title.md

## Refactor Context
- **ADR Reference:** ADR-XXX
- **Scope:** N files affected
- **Pattern:** Old → New
- **Markers Required:** Yes

## Tasks

### Task 1: Add REFACTOR markers
**Status:** 🔴 Not Started
**Priority:** Critical
- Must be done BEFORE refactoring

### Task 2-N: Implementation tasks
**Status:** 🔴 Not Started
**Dependencies:** Task 1

### Task N+1: Remove REFACTOR markers
**Status:** 🔴 Not Started
**Dependencies:** All refactor tasks
**Completion Criteria:**
- All markers removed
- ADR moved to implemented/
```

---

## Health Checks

### Daily Health Check

```bash
#!/bin/bash
echo "=== Refactor Health Check ==="

# Count active markers
marker_count=$(grep -rn "^# REFACTOR: ADR-027" src/ | wc -l)
echo "Active markers: $marker_count"

# Check ADR location
if [ -f "docs/adr/in_progress/027-title.md" ]; then
    echo "ADR status: IN_PROGRESS"
fi

# Check for stale markers (>30 days)
started_date=$(grep "STARTED:" src/*.py | head -1 | awk '{print $3}')
days_old=$(( ($(date +%s) - $(date -d $started_date +%s)) / 86400 ))
if [ $days_old -gt 30 ]; then
    echo "⚠️  Refactor is $days_old days old (stale)"
fi
```

### Stale Refactor Detection

**Definition:** Refactor markers present for >30 days without completion

**Response:**
1. Review ADR for blocker information
2. Identify why work stalled
3. Either: Complete refactor or Roll back
4. Never leave markers indefinitely

---

## Rollback Plans

**If refactor needs to be rolled back:**

1. **Revert commits:**
   ```bash
   git log --grep="ADR-027" --oneline
   git revert <commit-range>
   ```

2. **Remove markers:**
   ```bash
   find src/ -name "*.py" -exec sed -i '/# REFACTOR: ADR-027/,/^$/d' {} \;
   ```

3. **Update ADR:**
   - Move to docs/adr/not_started/ or rejected/
   - Document why rollback occurred

4. **Notify stakeholders**

---

## Supporting Scripts

The manage-todo skill includes several Python modules in the `scripts/` directory:

### state_manager.py

**Purpose:** Task state management, validation, and markdown parsing utilities.

**Key Functions:**
- `validate_state_transition(current_state, new_state)` - Validates if a state transition is allowed
- `format_state_emoji(state)` - Maps task state to emoji (e.g., "in_progress" → "🟡")
- `parse_state_from_emoji(emoji)` - Reverse mapping from emoji to state
- `parse_task_from_markdown(markdown_text)` - Extracts task details from markdown section

**Usage Example:**
```python
from scripts.state_manager import validate_state_transition, format_state_emoji

# Validate transition
is_valid = validate_state_transition("not_started", "in_progress")  # True

# Get emoji
emoji = format_state_emoji("in_progress")  # Returns "🟡"
```

### todo_manager.py

**Purpose:** Core CRUD operations for todo lists and tasks.

**Key Functions:**
- `create_todo(title, date_str, ...)` - Creates new Todo object
- `add_task(todo, title, status, ...)` - Adds task to todo list
- `update_task_state(todo, task_index, new_state)` - Updates task state
- `calculate_progress(todo)` - Calculates completion percentage
- `render_todo_to_markdown(todo)` - Renders todo to markdown format
- `parse_todo_file(content)` - Parses markdown file to Todo object

### todo_types.py

**Purpose:** Dataclass definitions for Todo and Task objects.

**Key Types:**
- `TaskState` - Enum: PENDING, IN_PROGRESS, COMPLETED, BLOCKED
- `Task` - Dataclass for individual tasks
- `Todo` - Dataclass for todo lists
- `ProgressSummary` - Dataclass for progress tracking

### template_loader.py

**Purpose:** Template loading and selection utilities.

**Key Functions:**
- Template selection based on project type
- ADR template integration
- Template variable substitution

### todowrite_sync.py

**Purpose:** Synchronization between todo.md and TodoWrite tool.

**Key Functions:**
- State mapping between todo.md and TodoWrite
- Sync validation and repair
- Bidirectional state updates

### refactor_validator.py

**Purpose:** ADR validation for refactor/migration work.

**Key Functions:**
- Detects refactor keywords
- Validates ADR existence
- Enforces ADR-first workflow

---

## Related Documentation

- [SKILL.md](../SKILL.md) - Main skill documentation
- [examples.md](../examples/examples.md) - Real-world examples
- [templates/task-template.md](../templates/task-template.md) - Task template
- [templates/refactor-todo-template.md](../templates/refactor-todo-template.md) - Refactor template

---

**Document Version:** 1.1.0
**Last Updated:** 2025-10-17
**Maintenance:** Review quarterly for pattern updates
**Recent Changes:** Added scripts/ documentation (state_manager.py, todo_manager.py, etc.)
