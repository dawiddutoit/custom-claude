# Todo Management Examples

## Example 1: Creating Feature Todo

```bash
# User says: "Break down the authentication feature into tasks"
# Skill actions:
# 1. Read project context
# 2. Create ./todo.md with 5-7 structured tasks
# 3. Assign states (🔴 pending)
# 4. Add acceptance criteria
# 5. Initialize TodoWrite

# Result: ./todo.md created with tasks ready for implementation
```

## Example 2: Updating Task State

```bash
# User says: "Mark task 1 as in progress"
# Skill actions:
# 1. Read ./todo.md
# 2. Update task state: 🔴 → 🟡
# 3. Update TodoWrite to match
# 4. Update progress summary (0% → 20%)

# Result: Task state synchronized, progress visible
```

## Example 3: Refactor Todo with ADR

```bash
# User says: "Create refactor todo for pattern migration (ADR-027)"
# Skill actions:
# 1. Detect refactor keywords ("refactor", "migration")
# 2. Invoke validate-refactor-adr skill
# 3. If ADR validated: Use enhanced template (refactor-todo-template.md)
# 4. Create 13-task refactor todo with skill integration
# 5. Initialize TodoWrite

# Result: Comprehensive refactor todo with ADR governance
```

## Workflow 1: Feature Development

```
User: "Create a todo for authentication"
  ↓
Skill: Creates todo.md with 5-7 tasks
  ↓
User: "Start task 1"
  ↓
Skill: Updates state to 🟡 In Progress
  ↓
User completes Task 1
  ↓
Skill: Updates to 🟢 Complete, progress 20%
  ↓
Repeat for remaining tasks
```

## Workflow 2: Refactor Project (Enhanced)

```
User: "Create refactor todo for pattern migration (ADR-XXX)"
  ↓
Skill: Detects refactor, searches for ADR-XXX
  ↓
If no ADR: STOP, instruct user to create ADR
  ↓
If ADR exists: Use enhanced template (refactor-todo-template.md)
  ↓
Skill: Creates 13-task refactor todo with:
  - Phase 1: ADR validation, marker placement, baseline
  - Phase 2: Component migrations with skill integration
  - Phase 3: Cleanup and health validation
  - Phase 4: Documentation updates
  ↓
User/Agent executes tasks:
  - Task 1.1: validate-refactor-adr skill validates ADR
  - Task 1.3: manage-refactor-markers adds markers
  - Tasks 2.x: multi-file-refactor executes code changes
  - Task 3.2: manage-refactor-markers removes markers
  - Task 3.3: detect-refactor-markers validates completion
  ↓
All tasks complete: Refactor done, ADR moved to implemented/
```

## Workflow 3: Cross-Session Work

```
Session 1: Create todo, complete Tasks 1-3 (30%)
  ↓
Between sessions: State persisted in todo.md
  ↓
Session 2: Resume work, complete Tasks 4-6 (60%)
  ↓
Skill: Reports progress, suggests next tasks
```

## Example Integration Todo (LangGraph Node)

```markdown
## Feature: Add ArchitectureReview Node

### Phase 1: CREATION (Artifacts)
- [ ] Create `coordination/graph/architecture_nodes.py`
- [ ] Implement `create_architecture_review_node()` factory
- [ ] Implement `should_review_architecture()` routing function
- [ ] Unit tests pass (24 tests with mocks)

### Phase 2: CONNECTION (Integration)
- [ ] Import `architecture_nodes` in `builder.py`
- [ ] Call `create_architecture_review_node(agent)` in builder
- [ ] Add node to graph with `graph.add_node("architecture_review", node)`
- [ ] Add conditional edge from `query_claude` using routing function
- [ ] Verify import: `grep "architecture_nodes" src/temet_run/coordination/graph/builder.py`

### Phase 3: VERIFICATION (Runtime)
- [ ] **INTEGRATION TEST**: `"architecture_review" in graph.nodes` passes
- [ ] **EXECUTION PROOF**: Run coordinator, attach logs showing node triggered
- [ ] **OUTCOME PROOF**: `state.architecture_review` is populated (not None)
- [ ] **FOUR QUESTIONS**: All answered with evidence
```

## Expected Outcomes

### Successful Todo Creation

```
✓ Todo created: ./todo.md

Tasks: 7 total
  - 🔴 Not Started: 7
  - 🟡 In Progress: 0
  - 🟢 Complete: 0

Acceptance criteria defined for all tasks
TodoWrite synchronized
Ready for implementation
```

### Successful State Update

```
✓ Task 1 updated: 🔴 → 🟡

Progress: 20% (1/5 tasks in progress)
TodoWrite synchronized
No blockers detected

Next: Continue implementing Task 1
```
