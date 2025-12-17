# Todo Templates

Complete templates for different use cases.

---

## Template 1: Simple Feature Implementation

**Use when:** Single feature with 3-7 straightforward tasks

```markdown
# Todo: [Feature Name]
Date: YYYY-MM-DD
Project: [Project Name]

## Objective
Implement [feature] to enable [user goal].

## Context
- Current state: [What exists now]
- Desired outcome: [What success looks like]

## Tasks

### Task 1: [Implementation]
**Status:** 🔴 Not Started
**Priority:** High
**Assigned:** [agent/person]

**Description:**
Core implementation in [file path].

**Acceptance Criteria:**
- [ ] Functionality works as specified
- [ ] Unit tests pass
- [ ] Code follows project conventions

---

### Task 2: [Testing]
**Status:** 🔴 Not Started
**Priority:** High
**Dependencies:** Task 1

**Description:**
Write comprehensive tests.

**Acceptance Criteria:**
- [ ] Unit tests with 90%+ coverage
- [ ] Integration tests for key paths
- [ ] All tests pass

---

### Task 3: [Documentation]
**Status:** 🔴 Not Started
**Priority:** Medium
**Dependencies:** Tasks 1, 2

**Description:**
Update documentation.

**Acceptance Criteria:**
- [ ] API docs updated
- [ ] User guide updated
- [ ] Examples added

## Progress Summary
- Total Tasks: 3
- Completed: 0 (0%)
- In Progress: 0
- Blocked: 0

## Session Notes
[Add notes as work progresses]
```

---

## Template 2: Complex Multi-Phase Project

**Use when:** Large project requiring multiple phases and dependencies

```markdown
# Todo: [Project Name]
Date: YYYY-MM-DD
Project: [Project Name]
Memory: [project_identifier]

## Objective
[Comprehensive project goal - 2-3 sentences]

## Context
- Current state: [Detailed description]
- Desired outcome: [Specific success criteria]
- Constraints: [Technical/time/resource limitations]
- Stakeholders: [Who cares about this]

## Phase 1: Foundation (Days 1-3)

### Task 1.1: [Setup/Infrastructure]
**Status:** 🔴 Not Started
**Priority:** Critical
**Assigned:** [agent/person]
**Estimated Time:** 4-6 hours

**Description:**
[What to build and why]

**Implementation Checklist:**
- [ ] Subtask 1
  - Status: Not Started
  - File: path/to/file.ext
  - Notes: [specifics]
- [ ] Subtask 2
  - Status: Not Started
  - File: path/to/file.ext
  - Notes: [specifics]

**Dependencies:**
- Depends on: None (phase start)
- Blocks: Tasks 1.2, 1.3

**Acceptance Criteria:**
- [ ] Specific criterion 1
- [ ] Specific criterion 2
- [ ] Quality gates pass

**Notes:**
[Any special considerations]

---

### Task 1.2: [Core Logic]
**Status:** 🔴 Not Started
**Priority:** Critical
**Dependencies:** Task 1.1

[Same structure as Task 1.1]

---

## Phase 2: Enhancement (Days 4-6)

### Task 2.1: [Feature Addition]
[Same structure]

---

## Phase 3: Polish (Days 7-8)

### Task 3.1: [Refinement]
[Same structure]

---

## Progress Summary by Phase

### Phase 1: Foundation
- Total: 3 tasks
- Complete: 0 (0%)
- Status: Not Started

### Phase 2: Enhancement
- Total: 4 tasks
- Complete: 0 (0%)
- Status: Not Started

### Phase 3: Polish
- Total: 2 tasks
- Complete: 0 (0%)
- Status: Not Started

### Overall Progress
- Total Tasks: 9
- Completed: 0 (0%)
- In Progress: 0
- Blocked: 0
- Estimated Completion: [Date]

## Session Notes
[Add detailed notes as work progresses]

## Decisions Log
- [Date]: Decision to [X] because [Y]
- [Date]: Changed approach from [A] to [B] due to [reason]

## Blockers & Resolutions
- [Date]: Blocked on [X] → Resolved by [Y]
```

---

## Template 3: Refactor/Migration Project

**Use when:** Large-scale refactor or migration requiring ADR and marker tracking

```markdown
# Refactor: [Pattern/Technology] Migration (ADR-XXX)
Date: YYYY-MM-DD
Project: [Project Name]
Memory: adr_XXX_[refactor_name]
ADR: docs/adr/in_progress/XXX-[title].md

## Refactor Context
- **ADR Reference:** ADR-XXX
- **Scope:** [X files across Y modules]
- **Pattern:** [Old Pattern] → [New Pattern]
- **Markers Required:** Yes (see CLAUDE.md)
- **Breaking Changes:** [Yes/No - details]
- **Estimated Timeline:** [X days/weeks]

## Why This Refactor?
[Brief explanation of motivation and benefits]

## Affected Components
- Component 1: [X files]
- Component 2: [Y files]
- Component 3: [Z files]

## Migration Strategy
1. Phase 1: Add markers and baseline tests
2. Phase 2: Migrate component-by-component
3. Phase 3: Remove old pattern and markers
4. Phase 4: Validate and document

## Tasks

### Task 1: Add REFACTOR markers to all affected files
**Status:** 🔴 Not Started
**Priority:** Critical
**Assigned:** @implementer
**Estimated Time:** 2-3 hours

**Description:**
Add file-level REFACTOR markers to all files in scope.

**Implementation Checklist:**
- [ ] Add markers to Component 1 (X files)
- [ ] Add markers to Component 2 (Y files)
- [ ] Add markers to Component 3 (Z files)

**Marker Format:**
```python
# REFACTOR: ADR-XXX [Pattern] Migration
# STATUS: IN_PROGRESS
# STARTED: YYYY-MM-DD
# PERMANENT_RECORD: docs/adr/in_progress/XXX-title.md
# Active Tracking: todo.md "Refactor: [Title]"
```

**Acceptance Criteria:**
- [ ] All affected files have markers
- [ ] Markers reference ADR-XXX correctly
- [ ] Markers are in standard format
- [ ] Can be detected via: `grep -rn "^# REFACTOR:" src/`

**Dependencies:**
- Depends on: None (must be first)
- Blocks: All refactor tasks

**Notes:**
Markers must be in place BEFORE any refactoring work begins.

---

### Task 2: Create baseline test suite
**Status:** 🔴 Not Started
**Priority:** Critical
**Dependencies:** Task 1

**Description:**
Ensure comprehensive test coverage before refactoring.

**Acceptance Criteria:**
- [ ] Unit test coverage > 90% for affected code
- [ ] Integration tests for key workflows
- [ ] All tests pass (baseline)
- [ ] Tests documented for reference

---

### Task 3: Migrate Component 1
**Status:** 🔴 Not Started
**Priority:** High
**Dependencies:** Tasks 1, 2

**Description:**
Migrate [Component 1] from [Old Pattern] to [New Pattern].

**Implementation Checklist:**
- [ ] File 1: [path/to/file1.ext]
  - Status: Not Started
  - Method/Class affected: [names]
- [ ] File 2: [path/to/file2.ext]
  - Status: Not Started
  - Method/Class affected: [names]

**Migration Pattern:**
```python
# OLD PATTERN
[example of old code]

# NEW PATTERN
[example of new code]
```

**Acceptance Criteria:**
- [ ] All files in Component 1 migrated
- [ ] Tests updated and passing
- [ ] No regressions in functionality
- [ ] Code review approved

---

### Task 4: Migrate Component 2
[Same structure as Task 3]

---

### Task 5: Migrate Component 3
[Same structure as Task 3]

---

### Task 6: Remove old pattern code
**Status:** 🔴 Not Started
**Priority:** High
**Dependencies:** Tasks 3, 4, 5

**Description:**
Remove old pattern code and dependencies (if any).

**Acceptance Criteria:**
- [ ] Old pattern no longer present
- [ ] Unused imports removed
- [ ] Dead code eliminated (vulture check)
- [ ] Tests still pass

---

### Task 7: Remove REFACTOR markers
**Status:** 🔴 Not Started
**Priority:** High
**Dependencies:** Task 6

**Description:**
Remove all REFACTOR markers from files.

**Acceptance Criteria:**
- [ ] All markers removed from source files
- [ ] Verify: `grep -rn "^# REFACTOR:" src/` returns 0 results
- [ ] ADR status updated to COMPLETE
- [ ] Quality gates pass

---

### Task 8: Update documentation
**Status:** 🔴 Not Started
**Priority:** Medium
**Dependencies:** Task 7

**Description:**
Update ARCHITECTURE.md and relevant docs.

**Acceptance Criteria:**
- [ ] ARCHITECTURE.md reflects new pattern
- [ ] Code examples updated
- [ ] Migration guide added (if reusable pattern)
- [ ] ADR moved to docs/adr/implemented/

---

## Progress Summary
- Total Tasks: 8
- Completed: 0 (0%)
- In Progress: 0
- Blocked: 0

## Migration Tracking

### Files Migrated by Component
- Component 1: 0/X files (0%)
- Component 2: 0/Y files (0%)
- Component 3: 0/Z files (0%)

### Overall Migration Progress
- Total files: [X+Y+Z]
- Migrated: 0 (0%)
- Remaining: [X+Y+Z]

## Refactor Health Checks

### Active Markers
```bash
# Check current marker count
grep -rn "^# REFACTOR:" src/ | wc -l
# Expected: [X+Y+Z] at start, 0 at completion
```

### ADR Status
- Location: docs/adr/in_progress/XXX-title.md
- Status: IN_PROGRESS
- Started: YYYY-MM-DD
- Target Completion: YYYY-MM-DD

### Stale Check
- Age: [X] days (alert if >30)
- Blocker: [None/Description]

## Session Notes
[Track key decisions and challenges]

## Lessons Learned
[Document insights for future refactors]
```

---

## Template 4: Bug Fix with Investigation

**Use when:** Bug requires investigation before fixing

```markdown
# Bug Fix: [Bug Description]
Date: YYYY-MM-DD
Project: [Project Name]
Bug ID: [#123 or reference]

## Objective
Fix [bug description] causing [user impact].

## Bug Details
- **Reported By:** [User/Team]
- **Severity:** Critical | High | Medium | Low
- **Impact:** [Number of users/systems affected]
- **Reproduction:** [Steps to reproduce]
- **Expected Behavior:** [What should happen]
- **Actual Behavior:** [What actually happens]
- **Environment:** [Where bug occurs]

## Tasks

### Task 1: Reproduce bug locally
**Status:** 🔴 Not Started
**Priority:** Critical

**Description:**
Consistently reproduce the bug in dev environment.

**Acceptance Criteria:**
- [ ] Bug reproduced reliably
- [ ] Reproduction steps documented
- [ ] Test case written to catch bug

---

### Task 2: Root cause analysis
**Status:** 🔴 Not Started
**Priority:** Critical
**Dependencies:** Task 1

**Description:**
Identify exact cause of bug.

**Investigation Checklist:**
- [ ] Review logs for error patterns
- [ ] Check recent code changes
- [ ] Analyze stack traces
- [ ] Test edge cases
- [ ] Document findings

**Acceptance Criteria:**
- [ ] Root cause identified
- [ ] Impact scope determined
- [ ] Fix approach documented

---

### Task 3: Implement fix
**Status:** 🔴 Not Started
**Priority:** Critical
**Dependencies:** Task 2

**Description:**
Implement minimal fix for root cause.

**Implementation Checklist:**
- [ ] Fix implemented in [file]
- [ ] Regression test added
- [ ] Edge cases handled

**Acceptance Criteria:**
- [ ] Bug no longer reproducible
- [ ] Tests pass (including new regression test)
- [ ] No side effects introduced
- [ ] Code review approved

---

### Task 4: Verify fix across environments
**Status:** 🔴 Not Started
**Priority:** High
**Dependencies:** Task 3

**Acceptance Criteria:**
- [ ] Verified in dev
- [ ] Verified in staging
- [ ] Verified in production (post-deploy)

---

### Task 5: Post-mortem documentation
**Status:** 🔴 Not Started
**Priority:** Medium
**Dependencies:** Task 4

**Description:**
Document lessons learned.

**Acceptance Criteria:**
- [ ] Post-mortem doc created
- [ ] Root cause documented
- [ ] Prevention steps identified
- [ ] Team notified

## Progress Summary
- Total Tasks: 5
- Completed: 0 (0%)
- In Progress: 0
- Blocked: 0

## Investigation Notes
[Track findings during investigation]

## Fix Validation
- [ ] Original reproduction case fixed
- [ ] Edge cases tested
- [ ] Performance impact checked
- [ ] No regressions introduced
```

---

## Template 5: Spike/Research Task

**Use when:** Need to research/prototype before committing to implementation

```markdown
# Spike: [Research Topic]
Date: YYYY-MM-DD
Project: [Project Name]
Time Box: [X days/hours]

## Objective
Research [topic] to determine [decision/approach].

## Research Questions
1. [Question 1]?
2. [Question 2]?
3. [Question 3]?

## Success Criteria
At end of spike, we should know:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

## Tasks

### Task 1: Literature review
**Status:** 🔴 Not Started
**Time Box:** 2-3 hours

**Description:**
Review existing documentation, papers, implementations.

**Checklist:**
- [ ] Official documentation reviewed
- [ ] Community best practices researched
- [ ] Similar implementations analyzed
- [ ] Alternatives compared

---

### Task 2: Prototype implementation
**Status:** 🔴 Not Started
**Time Box:** 4-6 hours
**Dependencies:** Task 1

**Description:**
Build minimal prototype to test approach.

**Acceptance Criteria:**
- [ ] Prototype demonstrates key concepts
- [ ] Performance measured
- [ ] Complexity assessed
- [ ] Trade-offs identified

---

### Task 3: Document findings
**Status:** 🔴 Not Started
**Time Box:** 1-2 hours
**Dependencies:** Tasks 1, 2

**Description:**
Summarize research and make recommendation.

**Deliverables:**
- [ ] Findings document created
- [ ] Recommendation provided (Go/No-Go/Alternative)
- [ ] If Go: Implementation plan drafted
- [ ] If No-Go: Alternatives documented

## Progress Summary
- Total Tasks: 3
- Completed: 0 (0%)
- Time Remaining: [X hours]

## Findings
[Document discoveries here]

## Recommendation
[Final recommendation: Implement/Don't Implement/Alternative Approach]

## Next Steps
[If Go: Link to implementation todo]
[If No-Go: Document why and alternatives]
```

---

## Template Selection Guide

| Use Case | Template | Complexity | Timeline |
|----------|----------|------------|----------|
| Simple feature (3-7 tasks) | Template 1 | Low | Days |
| Complex project (phases) | Template 2 | High | Weeks |
| Refactor/migration | Template 3 | High | Weeks |
| Bug fix requiring investigation | Template 4 | Medium | Days |
| Research/spike | Template 5 | Low-Medium | Hours-Days |

## Customization Tips

1. **Add/remove sections** based on project needs
2. **Adjust task granularity** to match team velocity
3. **Include project-specific fields** (e.g., JIRA ID, Epic link)
4. **Adapt progress tracking** to team's reporting needs
5. **Extend with custom states** if needed (e.g., "In Review")

## Common Modifications

### Add Estimation Fields
```markdown
**Estimated Time:** [X hours]
**Actual Time:** [Y hours]
**Variance:** [+/- Z hours]
```

### Add Risk Assessment
```markdown
**Risk Level:** High | Medium | Low
**Risk Factors:**
- [Factor 1]
- [Factor 2]
**Mitigation:** [Strategy]
```

### Add Stakeholder Section
```markdown
## Stakeholders
- **Owner:** [Name]
- **Reviewers:** [Names]
- **Informed:** [Names]
```

### Add Testing Strategy
```markdown
## Testing Strategy
- Unit Tests: [Approach]
- Integration Tests: [Approach]
- E2E Tests: [Approach]
- Performance Tests: [If needed]
```

---

**Template Version:** 1.0.0
**Last Updated:** 2025-10-16
**Maintenance:** Add new templates as patterns emerge
