# Refactor/Migration Marker Guide

**Purpose:** Track multi-file refactoring and pattern migrations with clear accountability.

**Principle:** MANDATORY for multi-file refactoring and pattern migrations. All markers MUST reference an ADR.

---

## Table of Contents

1. [When to Use Markers](#when-to-use-markers)
2. [ADR Requirement (CRITICAL)](#adr-requirement-critical)
3. [Marker Formats](#marker-formats)
4. [Lifecycle Rules](#lifecycle-rules)
5. [Permanent Record (ADR) Requirements](#permanent-record-adr-requirements)
6. [Active Tracking (todo.md) Rules](#active-tracking-todomd-rules)
7. [Validation & Enforcement](#validation-and-enforcement)
8. [Common Patterns](#common-patterns)
9. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
10. [Benefits](#benefits)
11. [Red Flags - STOP](#red-flags---stop)

---

## When to Use Markers

You MUST use refactor markers when:

1. **Multi-file refactoring** (3+ files affected)
2. **Breaking API contracts** or changing public interfaces
3. **Migrating patterns** across the codebase (e.g., adopting ServiceResult)
4. **Work spanning multiple sessions** (likely to be interrupted)
5. **Complex architectural changes** requiring coordination

**Key Decision:** If the change affects multiple files OR changes behavior across boundaries, use markers.

---

## ADR Requirement (CRITICAL)

**CRITICAL:** Refactors/migrations can ONLY be done if there is an associated ADR document.

### Before starting ANY refactor work:

#### 1. Check if ADR exists:

```bash
# Search all status directories
find docs/adr -name "*<topic>*"

# Or search by number
find docs/adr -name "*015*"
```

#### 2. If NO ADR exists:

- **STOP immediately**
- Create ADR using `docs/adr/TEMPLATE-refactor-migration.md`
- Place in `docs/adr/not_started/` initially
- Get approval before proceeding

#### 3. If ADR exists:

- Reference it in all markers (including full path with status directory)
- Update ADR "Implementation Tracking" section
- Move ADR to `in_progress/` when work begins
- Move to `implemented/` when complete

---

## Marker Formats

### File-Level Marker

Use at the top of files undergoing refactoring:

```python
# =============================================================================
# TODO: "Section Name"
# REFACTOR: [ADR-XXX] [Brief description]
# WHY: [One-line reason]
# STARTED: YYYY-MM-DD
# COMPLETED:
# STATUS: IN_PROGRESS | BLOCKED | REVIEW
# PERMANENT_RECORD: docs/adr/in_progress/XXX-title.md
# ACTIVE_TRACKING: todo.md "Section Name"
# =============================================================================
```

#### Field Descriptions:

- **TODO**: Links to specific section in todo.md for tracking
- **REFACTOR**: ADR reference and brief description
- **WHY**: One-line reason for this refactor
- **STARTED**: Date refactoring began (YYYY-MM-DD)
- **COMPLETED**: Date completed (leave blank until done)
- **STATUS**: Current state (IN_PROGRESS, BLOCKED, REVIEW)
- **PERMANENT_RECORD**: Path to ADR document (includes status subdirectory!)
- **ACTIVE_TRACKING**: Reference to todo.md section name

#### Example:

```python
# =============================================================================
# TODO: "ServiceResult Migration Phase 2"
# REFACTOR: [ADR-015] Migration to ServiceResult pattern
# WHY: Standardizing error handling across infrastructure layer
# STARTED: 2025-10-10
# COMPLETED:
# STATUS: IN_PROGRESS
# PERMANENT_RECORD: docs/adr/in_progress/015-serviceresult-pattern-migration.md
# ACTIVE_TRACKING: todo.md "ServiceResult Migration Phase 2"
# =============================================================================

class CodeRepository:
    """Repository for code entities."""
    # Class implementation...
```

---

### Method/Class Level Marker

Use for specific methods or classes being refactored:

```python
# REFACTOR(ADR-XXX): [Specific change being made]
def method_name():
    ...
```

#### Example:

```python
class UserService:
    # REFACTOR(ADR-015): Return ServiceResult instead of raising exceptions
    async def save(self, entity: UserEntity) -> ServiceResult[None]:
        ...

    # REFACTOR(ADR-015): Add proper error handling with ServiceResult
    async def find_by_id(self, id: str) -> ServiceResult[UserEntity | None]:
        ...
```

---

## Lifecycle Rules

### 1. ADD markers when:

- Starting multi-file refactor (3+ files)
- Breaking API contracts
- Migrating patterns (e.g., ServiceResult adoption)
- Work spans multiple sessions
- **ONLY after ADR is created and approved**

### 2. UPDATE status:

- After each significant milestone
- When blocked (change STATUS to BLOCKED, add reason)
- When entering review (change STATUS to REVIEW)
- Update ADR "Implementation Tracking" section in parallel
- **Move ADR file** to appropriate status directory as work progresses

### 3. REMOVE markers when:

- All files complete
- All tests pass
- Quality gates pass (`./scripts/check_all.sh`)
- Code review approved
- ADR status updated to COMPLETE
- **Move ADR** to `implemented/` directory

---

## Permanent Record (ADR) Requirements

**Every refactor marker MUST reference an ADR that:**

1. **EXISTS** before markers are added (in `not_started/` or `in_progress/`)
2. **TRACKS** affected files and completion criteria
3. **DOCUMENTS** the "why" and migration strategy
4. **REMAINS** after refactor is complete (moves to `implemented/`)

### ADR must include:

- Status (Proposed → Accepted → In Progress → Completed)
- Files Under Refactor table with status
- Completion Criteria checklist
- Active Tracking (todo.md reference)
- Progress Log (updated as work proceeds)

---

## Active Tracking (todo.md) Rules

**Refactor work MUST have corresponding todo.md section:**

- Reference ADR in todo header: `Memory: adr_015_serviceresult_migration`
- List specific file-level tasks with agents assigned
- Update task status as work progresses
- Can be cleared after completion (ADR preserves context)

### Example todo.md section:

```markdown
## ServiceResult Migration (ADR-015)
Memory: adr_015_serviceresult_migration
Status: In Progress (3/8 files complete)
ADR: docs/adr/in_progress/015-serviceresult-migration.md

### Task 1: Migrate CodeRepository methods
Status: 🟡 In Progress
Assigned: @implementer
Files: src/infrastructure/repository/code_repository.py
- [ ] save() method
- [ ] find_by_name() method
- [ ] delete() method

### Task 2: Update unit tests for CodeRepository
Status: ⭕ Not Started
Assigned: @unit-tester
Files: tests/unit/infrastructure/test_code_repository.py
```

---

## Validation and Enforcement

### Pre-commit Hook (automatic):

- Validates all `REFACTOR:` markers reference existing ADRs
- Fails commit if ADR file not found in any status directory
- Located at: `scripts/hooks/check_refactor_markers.sh`

### Slash Command (manual):

- Use `/refactors` to list all active refactors
- Shows status, ADR links, and orphaned markers
- Identifies markers older than 30 days

### Agent Enforcement:

Specialized agents enforce ADR requirement:

- `@planner` - Checks ADR exists before creating refactor plan
- `@implementer` - Validates ADR before starting refactor tasks
- `@project-todo-orchestrator` - Requires ADR for refactor todos
- `@architecture-guardian` - Validates ADR references in reviews
- `@reviewer` - Checks markers match ADR status

---

## Common Patterns

### Pattern 1: Starting New Refactor

```bash
# 1. Create ADR from template
cp docs/adr/TEMPLATE-refactor-migration.md docs/adr/not_started/015-serviceresult-migration.md

# 2. Fill out ADR with scope and criteria
vim docs/adr/not_started/015-serviceresult-migration.md

# 3. Create todo.md section
# Reference ADR number in memory field

# 4. Move ADR to in_progress when beginning work
mv docs/adr/not_started/015-serviceresult-migration.md docs/adr/in_progress/

# 5. Add file-level markers to affected files
# Reference ADR-015 in all markers with path docs/adr/in_progress/015-...

# 6. Begin implementation
```

---

### Pattern 2: Resuming Interrupted Refactor

```bash
# 1. Find active refactors
/refactors

# 2. Read ADR for context (check in_progress directory)
cat docs/adr/in_progress/015-serviceresult-migration.md

# 3. Check todo.md for current task
cat todo.md

# 4. Continue implementation
```

---

### Pattern 3: Completing Refactor

```bash
# 1. Verify all completion criteria met
# Check ADR "Completion Criteria" section

# 2. Run quality gates
./scripts/check_all.sh

# 3. Remove all refactor markers
# Find: grep -r "REFACTOR(ADR-015)" src/

# 4. Update ADR status to COMPLETE
# Add final entry to Progress Log

# 5. Move ADR to implemented directory
mv docs/adr/in_progress/015-serviceresult-migration.md docs/adr/implemented/

# 6. Update todo.md or archive it
# ADR preserves permanent record
```

---

## Anti-Patterns to Avoid

### ❌ Starting refactor without ADR

```python
# REFACTOR: Migrating to new pattern  # WRONG - No ADR reference!
```

**Fix:** Create ADR first, then add markers.

---

### ❌ Vague marker references

```python
# REFACTOR(ADR-???): Fixing stuff  # WRONG - No ADR number!
```

**Fix:** Include exact ADR number (e.g., ADR-015).

---

### ❌ Missing permanent record link

```python
# REFACTOR: [ADR-015] ServiceResult migration
# WHY: Better error handling
# STARTED: 2025-10-10
# STATUS: IN_PROGRESS
# PERMANENT_RECORD: ???  # WRONG - Must specify ADR path with status directory!
```

**Fix:** Add full path: `docs/adr/in_progress/015-serviceresult-pattern-migration.md`

---

### ❌ Wrong status directory in path

```python
# PERMANENT_RECORD: docs/adr/015-serviceresult-pattern-migration.md  # WRONG - No status directory!
# CORRECT: docs/adr/in_progress/015-serviceresult-pattern-migration.md
```

**Fix:** Always include status directory (`implemented/`, `in_progress/`, `not_started/`).

---

### ❌ Orphaned markers (ADR doesn't exist)

```python
# REFACTOR: [ADR-999] NonExistent refactor  # WRONG - ADR not found!
```

**Fix:** Create ADR or remove invalid marker.

---

### ❌ Stale markers (never removed)

```python
# REFACTOR(ADR-015): Completed 3 months ago  # WRONG - Should be removed!
```

**Fix:** Remove markers when work complete and ADR moved to `implemented/`.

---

## Benefits

1. **Visibility**: All refactors tracked in one place (`/refactors`)
2. **Context Preservation**: ADR documents "why" permanently
3. **Session Continuity**: Resume work after interruptions
4. **Coordination**: Multiple developers understand scope
5. **Quality**: Completion criteria prevent premature closure
6. **Accountability**: Markers indicate work in progress
7. **Status Tracking**: Directory structure shows implementation progress

---

## Red Flags - STOP

1. Refactor marker without ADR → Create ADR first in `not_started/`
2. ADR reference doesn't exist → Fix path or create ADR
3. Marker older than 30 days → Review and complete or document blocker
4. Inconsistent status (marker says COMPLETE, ADR says IN_PROGRESS) → Sync them
5. todo.md missing for active refactor → Create tracking section
6. ADR in wrong status directory → Move to correct directory

---

## Related Documentation

- [CLAUDE.md](../../../../CLAUDE.md) - Core rules and project overview
- [ADR Directory Guide](../../../../docs/ADR-DIRECTORY-GUIDE.md) - ADR organization
- [Agent Dispatch](.claude/agents/dispatch.md) - When to use which agent
- [ARCHITECTURE.md](../../../../ARCHITECTURE.md) - Architecture decision records index

---

**Last Updated:** 2025-10-16
**Principle:** Track all multi-file refactoring with markers and ADRs. No refactor without an ADR.
