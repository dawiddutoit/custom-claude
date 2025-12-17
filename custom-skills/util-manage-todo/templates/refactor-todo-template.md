# Refactor Todo Template

**Enhanced template with skill integration for ADR-governed refactoring workflows.**

---

## Template: ADR-Governed Refactor Project

**Use when:** Large-scale refactor, migration, or pattern adoption requiring ADR documentation and marker tracking.

**Key Features:**
- Enforces ADR validation before work starts
- Automates marker placement and removal
- Integrates with specialized refactor skills
- Tracks health metrics (stale/orphaned markers)
- Ensures quality gates at each phase

```markdown
# Refactor: [Pattern/Technology] Migration (ADR-XXX)

**Date:** YYYY-MM-DD
**Project:** [Project Name]
**ADR:** docs/adr/in_progress/XXX-[title].md
**Memory:** adr_XXX_[refactor_name]
**Started:** YYYY-MM-DD
**Target Completion:** YYYY-MM-DD

---

## Refactor Context

**ADR Reference:** ADR-XXX
**Scope:** [X files across Y modules/packages]
**Pattern Change:** [Old Pattern] → [New Pattern]
**Markers Required:** Yes (enforced by CLAUDE.md)
**Breaking Changes:** [Yes/No - describe if yes]
**Estimated Effort:** [X days/weeks]

**Why This Refactor?**
[Brief explanation of motivation, benefits, and alignment with architecture goals]

**Affected Components:**
- Component 1: [X files] - [Description]
- Component 2: [Y files] - [Description]
- Component 3: [Z files] - [Description]

---

## Migration Strategy

**Approach:** [Bottom-up | Top-down | Component-by-component]

**Phases:**
1. **Pre-Work:** Validate ADR, add markers, baseline tests
2. **Implementation:** Migrate components in dependency order
3. **Cleanup:** Remove old pattern, verify completeness
4. **Documentation:** Update ADR, architecture docs

**Rollback Plan:**
[How to safely revert if critical issues discovered]

---

## Phase 1: Pre-Work (ADR Validation & Marker Placement)

### Task 1.1: Validate ADR Document

**Status:** 🔴 Not Started
**Priority:** Critical
**Skill:** `validate-refactor-adr`
**Estimated Time:** 15-30 minutes

**Description:**
Validate that ADR-XXX exists, is complete, and follows required structure before allowing any refactor work to begin.

**Skill Invocation:**
```python
# Claude will automatically invoke when refactor keywords detected
# Or manually: Skill(command: "validate-refactor-adr")
```

**Acceptance Criteria:**
- [ ] ADR found at `docs/adr/in_progress/XXX-*.md`
- [ ] ADR has all required sections:
  - [ ] Status (IN_PROGRESS or PROPOSED)
  - [ ] Context (problem description)
  - [ ] Decision (chosen approach)
  - [ ] Consequences (trade-offs)
- [ ] ADR has file tracking table (for marker updates)
- [ ] ADR reviewed and approved by relevant stakeholders

**Validation Commands:**
```bash
# Check ADR exists
ls docs/adr/in_progress/XXX-*.md

# Verify structure (manual review or use validate-refactor-adr skill)
```

**Dependencies:**
- Depends on: None (MUST be first task)
- Blocks: All subsequent refactor tasks

**Notes:**
This is a BLOCKING gate - no refactor work can proceed until ADR is validated.

---

### Task 1.2: Identify and Map Affected Files

**Status:** 🔴 Not Started
**Priority:** Critical
**Dependencies:** Task 1.1
**Estimated Time:** 1-2 hours

**Description:**
Comprehensively identify all files requiring changes and map their dependencies to determine migration order.

**Discovery Commands:**
```bash
# Search for old pattern usage
grep -rn "old_pattern_signature" src/ --include="*.py"

# Find imports of old modules
grep -rn "from old_module import" src/ --include="*.py"

# Check test coverage
grep -rn "test.*old_pattern" tests/ --include="*.py"
```

**Implementation Checklist:**
- [ ] List all source files with old pattern
  ```
  File count: [X]
  Files: [List paths]
  ```
- [ ] List all test files requiring updates
  ```
  Test files: [Y]
  Files: [List paths]
  ```
- [ ] Map dependencies to determine migration order
  ```
  Layer 1 (Core): [files with no deps on old pattern]
  Layer 2 (Services): [files depending on Layer 1]
  Layer 3 (Infrastructure): [files depending on Layer 2]
  ```
- [ ] Document complexity hotspots
  ```
  High complexity: [files with >10 occurrences]
  Medium complexity: [files with 5-10 occurrences]
  Low complexity: [files with <5 occurrences]
  ```

**Acceptance Criteria:**
- [ ] Complete file list documented above
- [ ] Dependency order determined (migration sequence)
- [ ] Complexity assessment complete
- [ ] File list added to ADR tracking table

**Notes:**
Use `multi-file-refactor` skill for pattern discovery and analysis.

---

### Task 1.3: Add REFACTOR Markers to All Files

**Status:** 🔴 Not Started
**Priority:** Critical
**Skill:** `manage-refactor-markers` (ADD mode)
**Dependencies:** Tasks 1.1, 1.2
**Estimated Time:** 30-60 minutes

**Description:**
Add file-level and method-level REFACTOR markers to all affected files BEFORE making any code changes. This ensures refactor work is tracked and can be monitored for completion.

**Skill Invocation:**
```python
# Invoke manage-refactor-markers skill with ADD mode
# Skill will:
# 1. Add file-level markers to each file
# 2. Add method-level markers to specific functions/classes
# 3. Update ADR tracking table
# 4. Verify markers are detectable
```

**Marker Format (Auto-generated by skill):**
```python
# REFACTOR: ADR-XXX [Pattern] Migration
# STATUS: IN_PROGRESS
# STARTED: YYYY-MM-DD
# PERMANENT_RECORD: docs/adr/in_progress/XXX-title.md
# Active Tracking: todo.md "Refactor: [Title]"
```

**Implementation Checklist:**
- [ ] Markers added to Component 1 files ([X] files)
- [ ] Markers added to Component 2 files ([Y] files)
- [ ] Markers added to Component 3 files ([Z] files)
- [ ] Method-level markers added to specific functions:
  ```
  File: [path]
    - Function: [name] (line [N])
  ```
- [ ] ADR tracking table updated with marker status

**Acceptance Criteria:**
- [ ] All identified files have markers
- [ ] Markers reference ADR-XXX correctly
- [ ] Markers follow standard format (validated by skill)
- [ ] Verification passes:
  ```bash
  # Should return [X+Y+Z] results
  grep -rn "^# REFACTOR: ADR-XXX" src/ | wc -l
  ```
- [ ] ADR tracking table updated

**Dependencies:**
- Depends on: Tasks 1.1 (ADR validated), 1.2 (files identified)
- Blocks: All implementation tasks (2.x)

**Notes:**
CRITICAL: Markers MUST be in place before ANY code changes. This is non-negotiable per CLAUDE.md refactor policy.

---

### Task 1.4: Establish Test Baseline

**Status:** 🔴 Not Started
**Priority:** Critical
**Dependencies:** Task 1.3
**Estimated Time:** 1-2 hours

**Description:**
Ensure comprehensive test coverage exists BEFORE refactoring. This baseline confirms we can detect regressions during migration.

**Implementation Checklist:**
- [ ] Run full test suite and capture baseline:
  ```bash
  uv run pytest tests/ -v --cov=src --cov-report=term-missing
  # Expected: All tests PASS (if tests fail, fix before proceeding)
  # Coverage target: >90% for affected modules
  ```
- [ ] Document baseline metrics:
  ```
  Total tests: [N]
  Passing: [N]
  Coverage: [X]%
  Test execution time: [X]s
  ```
- [ ] Add missing tests for uncovered critical paths:
  ```
  File: [path] - Coverage: [X]% (target: 90%+)
  Missing coverage: [describe gaps]
  ```
- [ ] Run quality gates baseline:
  ```bash
  ./scripts/check_all.sh
  # Capture output for comparison
  ```

**Acceptance Criteria:**
- [ ] All existing tests pass (100%)
- [ ] Coverage ≥90% for files in migration scope
- [ ] Quality gates pass (pyright, ruff, vulture)
- [ ] Baseline metrics documented for regression detection

**Notes:**
If tests fail or coverage is insufficient, stop and fix before proceeding. Use `debug-test-failures` skill if needed.

---

## Phase 2: Implementation (Component-by-Component Migration)

### Task 2.1: Migrate Component 1 [Component Name]

**Status:** 🔴 Not Started
**Priority:** High
**Skill:** `multi-file-refactor` (for 2+ files)
**Dependencies:** Phase 1 complete (Tasks 1.1-1.4)
**Estimated Time:** [X] hours

**Description:**
Migrate [Component 1 name/description] from [Old Pattern] to [New Pattern]. This is the foundation layer - migrate first due to [reason: no deps / core functionality / etc.].

**Files in Scope:**
```
1. src/[path]/file1.py
   - Classes/Functions: [list]
   - Occurrences: [N]

2. src/[path]/file2.py
   - Classes/Functions: [list]
   - Occurrences: [N]

[Continue for all files in component]
```

**Migration Pattern:**
```python
# OLD PATTERN (before)
def fetch_user(user_id: int) -> User | None:
    try:
        user = db.get(user_id)
        return user
    except Exception:
        return None

# NEW PATTERN (after)
def fetch_user(user_id: int) -> ServiceResult[User]:
    try:
        user = db.get(user_id)
        return ServiceResult.success(user)
    except Exception as e:
        return ServiceResult.failure(f"Failed to fetch user: {e}")
```

**Implementation Checklist:**
- [ ] File 1: `[path/to/file1.py]`
  - Status: 🔴 Not Started
  - Method: `[method_name]` (line [N])
  - Tests updated: [ ]
  - Tests passing: [ ]

- [ ] File 2: `[path/to/file2.py]`
  - Status: 🔴 Not Started
  - Method: `[method_name]` (line [N])
  - Tests updated: [ ]
  - Tests passing: [ ]

**Use MultiEdit for Token Efficiency:**
```python
# If editing 2+ files, use MultiEdit (30-50% token savings)
# The multi-file-refactor skill enforces this automatically
```

**Acceptance Criteria:**
- [ ] All files in Component 1 migrated to new pattern
- [ ] All affected tests updated and passing
- [ ] No regressions in functionality (tests confirm)
- [ ] Quality gates pass for migrated files:
  ```bash
  uv run pyright src/[component_path]/
  uv run ruff check src/[component_path]/
  uv run pytest tests/[component_path]/ -v
  ```
- [ ] Code review approved (if team workflow requires)

**Validation Commands:**
```bash
# Verify old pattern removed from this component
grep -rn "old_pattern" src/[component_path]/ --include="*.py"
# Should return 0 results for this component

# Verify tests pass
uv run pytest tests/[component_path]/ -v
```

**Dependencies:**
- Depends on: Phase 1 complete (baseline established)
- Blocks: Component 2 migration (if Component 2 depends on Component 1)

**Notes:**
- Use `multi-file-refactor` skill for coordinated changes across multiple files
- Run tests after EACH file to catch issues early (fail-fast principle)
- Document any unexpected issues or edge cases discovered

---

### Task 2.2: Migrate Component 2 [Component Name]

**Status:** 🔴 Not Started
**Priority:** High
**Skill:** `multi-file-refactor`
**Dependencies:** Task 2.1 (Component 1 complete)
**Estimated Time:** [X] hours

**Description:**
[Same structure as Task 2.1, customized for Component 2]

**Files in Scope:**
[List Component 2 files]

**Implementation Checklist:**
[Same structure as Task 2.1]

**Acceptance Criteria:**
[Same structure as Task 2.1]

---

### Task 2.3: Migrate Component 3 [Component Name]

**Status:** 🔴 Not Started
**Priority:** High
**Skill:** `multi-file-refactor`
**Dependencies:** Task 2.2 (Component 2 complete)
**Estimated Time:** [X] hours

**Description:**
[Same structure as Task 2.1, customized for Component 3]

**Files in Scope:**
[List Component 3 files]

**Implementation Checklist:**
[Same structure as Task 2.1]

**Acceptance Criteria:**
[Same structure as Task 2.1]

---

## Phase 3: Cleanup & Validation

### Task 3.1: Remove Old Pattern Code

**Status:** 🔴 Not Started
**Priority:** High
**Dependencies:** All Component migrations (Tasks 2.1-2.3)
**Estimated Time:** 1-2 hours

**Description:**
Completely remove old pattern code, unused imports, and dependencies. Verify no old pattern references remain in codebase.

**Implementation Checklist:**
- [ ] Verify old pattern completely replaced:
  ```bash
  # Should return 0 results
  grep -rn "old_pattern_signature" src/ --include="*.py"
  ```
- [ ] Remove unused imports related to old pattern:
  ```bash
  # Use optimize-imports skill or manual cleanup
  Skill(command: "optimize-imports")
  ```
- [ ] Remove dead code (old pattern helper functions/classes):
  ```bash
  uv run vulture src/ --min-confidence 80
  # Review and remove identified dead code
  ```
- [ ] Update type hints if pattern changed types:
  ```bash
  uv run pyright src/
  # Fix any type errors from pattern migration
  ```

**Acceptance Criteria:**
- [ ] No old pattern references remain (grep returns 0 results)
- [ ] Unused imports removed (pyright/ruff confirms)
- [ ] Dead code eliminated (vulture check passes)
- [ ] All quality gates pass:
  ```bash
  ./scripts/check_all.sh
  # Must pass: pyright, ruff, vulture, pytest
  ```
- [ ] No performance regressions (if applicable):
  ```bash
  # Run performance tests if refactor impacts hot paths
  uv run pytest tests/performance/ -v
  ```

**Notes:**
Be thorough - leftover old pattern code can confuse developers and create maintenance debt.

---

### Task 3.2: Remove REFACTOR Markers

**Status:** 🔴 Not Started
**Priority:** High
**Skill:** `manage-refactor-markers` (REMOVE mode)
**Dependencies:** Task 3.1 (cleanup complete)
**Estimated Time:** 15-30 minutes

**Description:**
Remove all REFACTOR markers from files after migration is complete and validated.

**Skill Invocation:**
```python
# Invoke manage-refactor-markers skill with REMOVE mode
# Skill will:
# 1. Remove all file-level markers
# 2. Remove all method-level markers
# 3. Update ADR tracking table to COMPLETE
# 4. Verify no markers remain (grep check)
```

**Implementation Checklist:**
- [ ] Invoke `manage-refactor-markers` skill (REMOVE mode)
- [ ] Verify all markers removed from Component 1 files
- [ ] Verify all markers removed from Component 2 files
- [ ] Verify all markers removed from Component 3 files
- [ ] Verify ADR tracking table updated to COMPLETE

**Acceptance Criteria:**
- [ ] All markers removed (verified by skill):
  ```bash
  # Should return 0 results
  grep -rn "^# REFACTOR: ADR-XXX" src/
  ```
- [ ] ADR tracking table shows all files COMPLETE
- [ ] No orphaned markers (detect-refactor-markers skill confirms)
- [ ] Commit marker removal separately:
  ```bash
  git add .
  git commit -m "refactor(ADR-XXX): remove markers after migration complete"
  ```

**Notes:**
Only remove markers AFTER all quality gates pass and migration is fully validated.

---

### Task 3.3: Run Health Check & Validation

**Status:** 🔴 Not Started
**Priority:** High
**Skill:** `detect-refactor-markers` (health check)
**Dependencies:** Task 3.2 (markers removed)
**Estimated Time:** 15 minutes

**Description:**
Final health check to ensure refactor is fully complete with no lingering markers or issues.

**Skill Invocation:**
```python
# Use detect-refactor-markers for final health audit
Skill(command: "detect-refactor-markers")
```

**Validation Checklist:**
- [ ] No active markers in codebase:
  ```bash
  grep -rn "^# REFACTOR:" src/
  # Expected: 0 results
  ```
- [ ] No stale markers (>30 days old):
  ```
  detect-refactor-markers output: "No markers found" (healthy)
  ```
- [ ] No orphaned markers (markers without ADR):
  ```
  detect-refactor-markers output: "No orphaned markers" (healthy)
  ```
- [ ] Full quality gate pass:
  ```bash
  ./scripts/check_all.sh
  # All checks PASS
  ```
- [ ] Integration tests pass:
  ```bash
  uv run pytest tests/integration/ -v
  ```

**Acceptance Criteria:**
- [ ] Health check: GOOD (no markers, no issues)
- [ ] Quality gates: 100% pass
- [ ] Test coverage maintained or improved from baseline
- [ ] No regressions detected

**Notes:**
This is the final validation before moving ADR to implemented/ and declaring refactor complete.

---

## Phase 4: Documentation & Completion

### Task 4.1: Update ADR Status to COMPLETE

**Status:** 🔴 Not Started
**Priority:** High
**Dependencies:** Task 3.3 (validation complete)
**Estimated Time:** 15 minutes

**Description:**
Move ADR from in_progress/ to implemented/ and update status to IMPLEMENTED.

**Implementation Checklist:**
- [ ] Update ADR metadata:
  ```markdown
  Status: IMPLEMENTED
  Implemented Date: YYYY-MM-DD
  Implementation Duration: [X days/weeks]
  ```
- [ ] Add "Implementation Notes" section to ADR:
  ```markdown
  ## Implementation Notes
  - Files migrated: [X] files across [Y] components
  - Test coverage: [X]% (maintained/improved)
  - Challenges encountered: [list key challenges]
  - Lessons learned: [insights for future refactors]
  ```
- [ ] Move ADR to implemented directory:
  ```bash
  git mv docs/adr/in_progress/XXX-[title].md docs/adr/implemented/
  ```
- [ ] Update ADR index (if exists):
  ```
  Add entry to docs/adr/README.md or index
  ```

**Acceptance Criteria:**
- [ ] ADR status updated to IMPLEMENTED
- [ ] Implementation date recorded
- [ ] ADR moved to implemented/ directory
- [ ] ADR index updated
- [ ] Commit:
  ```bash
  git add docs/adr/
  git commit -m "docs(ADR-XXX): mark as implemented, move to implemented/"
  ```

---

### Task 4.2: Update Architecture Documentation

**Status:** 🔴 Not Started
**Priority:** Medium
**Dependencies:** Task 4.1 (ADR updated)
**Estimated Time:** 1-2 hours

**Description:**
Update ARCHITECTURE.md and related documentation to reflect new pattern as standard.

**Implementation Checklist:**
- [ ] Update ARCHITECTURE.md:
  - [ ] Replace old pattern examples with new pattern
  - [ ] Update pattern documentation section
  - [ ] Add migration notes (if helpful for context)
- [ ] Update code examples in docs:
  ```
  Files to update:
  - docs/patterns/[pattern-name].md
  - docs/examples/[example].md
  - README.md (if contains examples)
  ```
- [ ] Update CLAUDE.md if pattern is core rule:
  ```
  Example: If ServiceResult is now required, ensure CLAUDE.md
  "Core Rules" section reflects this
  ```
- [ ] Create migration guide (if pattern is reusable):
  ```
  docs/guides/migration-[old-to-new-pattern].md
  - When to use new pattern
  - Migration steps
  - Common pitfalls
  - Examples
  ```

**Acceptance Criteria:**
- [ ] ARCHITECTURE.md reflects new pattern as standard
- [ ] All code examples updated
- [ ] Migration guide created (if reusable pattern)
- [ ] Documentation review complete
- [ ] Commit:
  ```bash
  git add docs/
  git commit -m "docs(ADR-XXX): update architecture and examples for new pattern"
  ```

---

### Task 4.3: Create Completion Summary

**Status:** 🔴 Not Started
**Priority:** Low
**Dependencies:** All previous tasks
**Estimated Time:** 30 minutes

**Description:**
Document refactor completion summary with metrics, learnings, and outcomes.

**Summary Template:**
```markdown
# Refactor Completion: [Pattern] Migration (ADR-XXX)

## Overview
- **ADR:** ADR-XXX
- **Started:** YYYY-MM-DD
- **Completed:** YYYY-MM-DD
- **Duration:** [X days/weeks]
- **Effort:** [Y hours]

## Scope
- **Files Modified:** [X] files
- **Components:** [Y] components
- **Lines Changed:** [Z] lines (estimate from git diff --stat)

## Outcomes
- **Pattern Adoption:** [Old Pattern] → [New Pattern]
- **Test Coverage:** [Before: X%] → [After: Y%]
- **Quality Gates:** All passing
- **Regressions:** None detected

## Challenges & Solutions
1. **Challenge:** [Description]
   - **Solution:** [How resolved]
   - **Time Impact:** [+X hours]

2. **Challenge:** [Description]
   - **Solution:** [How resolved]

## Lessons Learned
- [Lesson 1 - what worked well]
- [Lesson 2 - what to improve next time]
- [Lesson 3 - unexpected discovery]

## Next Steps
- [ ] Monitor production for [X days] post-deployment
- [ ] Share learnings with team in [meeting/document]
- [ ] Apply pattern to [other areas if applicable]

## References
- ADR: docs/adr/implemented/XXX-[title].md
- PR: [Link if using PRs]
- Commits: [Range or links]
```

**Acceptance Criteria:**
- [ ] Completion summary created
- [ ] Metrics captured (files, time, coverage)
- [ ] Lessons learned documented
- [ ] Summary added to ADR or separate doc
- [ ] Team notified (if applicable)

---

## Progress Tracking

### Overall Progress
- **Total Tasks:** 13
- **Completed:** 0 (0%)
- **In Progress:** 0
- **Blocked:** 0
- **Estimated Completion:** YYYY-MM-DD

### Progress by Phase

#### Phase 1: Pre-Work
- Total: 4 tasks
- Complete: 0 (0%)
- Status: 🔴 Not Started

#### Phase 2: Implementation
- Total: 3 tasks (adjust based on components)
- Complete: 0 (0%)
- Status: 🔴 Not Started

#### Phase 3: Cleanup & Validation
- Total: 3 tasks
- Complete: 0 (0%)
- Status: 🔴 Not Started

#### Phase 4: Documentation
- Total: 3 tasks
- Complete: 0 (0%)
- Status: 🔴 Not Started

### Migration Tracking

**Files Migrated by Component:**
- Component 1: 0/[X] files (0%)
- Component 2: 0/[Y] files (0%)
- Component 3: 0/[Z] files (0%)

**Overall File Progress:**
- Total files in scope: [X+Y+Z]
- Migrated: 0 (0%)
- Remaining: [X+Y+Z]

---

## Refactor Health Monitoring

Use `detect-refactor-markers` skill regularly to monitor health.

**Skill Invocation:**
```python
Skill(command: "detect-refactor-markers")
```

**Health Metrics:**

### Active Markers Count
```bash
# Check current marker count
grep -rn "^# REFACTOR: ADR-XXX" src/ | wc -l
# Expected: [X+Y+Z] at start → 0 at completion
# Current: [update as progress]
```

### ADR Status
- **Location:** docs/adr/in_progress/XXX-title.md
- **Status:** IN_PROGRESS
- **Started:** YYYY-MM-DD
- **Age:** [X] days
- **Alert Threshold:** >30 days (stale)
- **Current Status:** [HEALTHY | ATTENTION_NEEDED | STALE]

### Marker Health Categories
- **🟢 GOOD:** All markers have ADRs, <30 days old
- **🟡 ATTENTION_NEEDED:** Markers 20-30 days old, needs progress check
- **🔴 CRITICAL:** Markers >30 days (stale) or orphaned (no ADR)

**Current Health:** [Update during refactor]

---

## Session Notes

**[YYYY-MM-DD]:**
- [Track key decisions, challenges, discoveries]
- [Example: "Discovered Component 2 has hidden dependency on Component 1, adjusted migration order"]

**[YYYY-MM-DD]:**
- [Continue logging important events]

---

## Quality Gate Results

### Baseline (Before Refactor)
```bash
# Captured in Task 1.4
Tests: [N] passing
Coverage: [X]%
Pyright: [Y] errors
Ruff: [Z] warnings
Vulture: [W] dead code items
```

### Current (During Refactor)
```bash
# Update as progress
Tests: [N] passing / [M] total
Coverage: [X]%
Pyright: [Y] errors
Ruff: [Z] warnings
Vulture: [W] dead code items
```

### Final (After Refactor)
```bash
# Captured in Task 3.3
Tests: [N] passing (100%)
Coverage: [X]% (maintained/improved)
Pyright: 0 errors ✅
Ruff: 0 warnings ✅
Vulture: 0 dead code ✅
```

---

## Skill Integration Reference

**Skills Used in This Refactor:**

1. **validate-refactor-adr** (Task 1.1)
   - Validates ADR exists and is complete
   - Blocks work if ADR incomplete
   - Enforces refactor governance

2. **manage-refactor-markers** (Tasks 1.3, 3.2)
   - ADD mode: Places markers before work starts
   - REMOVE mode: Removes markers after completion
   - Updates ADR tracking table

3. **detect-refactor-markers** (Task 3.3)
   - Health monitoring and compliance
   - Detects stale markers (>30 days)
   - Finds orphaned markers (no ADR)

4. **multi-file-refactor** (Tasks 2.1-2.3)
   - Token-efficient MultiEdit enforcement
   - Coordinates changes across files
   - Validates imports and references
   - Runs quality gates

5. **optimize-imports** (Task 3.1, optional)
   - Removes unused imports
   - Fixes circular dependencies
   - Organizes import statements

6. **debug-test-failures** (Task 1.4, as needed)
   - Evidence-based test debugging
   - Root cause analysis
   - Prevents assumption-based fixes

7. **run-quality-gates** (Tasks 1.4, 3.1, 3.3)
   - Runs all quality checks (pyright, ruff, vulture, pytest)
   - Enforces Definition of Done
   - Baseline and regression detection

**Skill Invocation Pattern:**
```python
# Auto-invoked by agent when appropriate, or manual:
Skill(command: "skill-name")
```

---

## Blockers & Resolutions

**[Date]:** Blocked on [Issue]
- **Blocker:** [Description]
- **Impact:** [High/Medium/Low]
- **Resolution:** [How resolved or still investigating]
- **Time Lost:** [X hours/days]

---

## Lessons Learned (Ongoing)

- [Lesson 1: What worked well in this refactor]
- [Lesson 2: What to improve next time]
- [Lesson 3: Unexpected discovery or insight]
- [Add more as refactor progresses]

---

**Template Version:** 2.0.0
**Last Updated:** 2025-10-17
**Changelog:**
- v2.0.0: Enhanced with skill integration, health monitoring, workflow automation
- v1.0.0: Initial refactor template
```

---

## Template Usage Guide

### When to Use This Template

Use this enhanced refactor template when:

1. **ADR is required** - Large architectural changes, migrations, pattern adoptions
2. **Multiple files affected** - Refactor spans >3 files or multiple components
3. **Marker tracking needed** - Long-running refactor requiring progress monitoring
4. **Quality gates critical** - Changes must maintain/improve quality metrics
5. **Team coordination** - Multiple developers or sessions working on refactor

### When NOT to Use This Template

Don't use for:

1. **Simple bug fixes** - Single file, <30 lines changed
2. **Refactoring without ADR** - Quick refactors that don't need formal documentation
3. **Exploratory work** - Use spike template instead
4. **Non-code changes** - Documentation-only updates

### Template Customization

**Required customizations when using:**
- Replace `[Placeholders]` with actual values
- Adjust component count (may be more/less than 3)
- Modify phases based on ADR strategy
- Add project-specific sections (e.g., deployment steps, rollback procedures)

**Optional customizations:**
- Add risk assessment section
- Include performance testing tasks
- Add security review steps
- Expand documentation tasks

### Integration with Skills

**Automatic skill invocation:**
Claude will automatically invoke refactor skills when:
- Refactor keywords detected (migrate, refactor, pattern adoption)
- ADR referenced in task
- Markers mentioned in context

**Manual skill invocation:**
Use `Skill(command: "skill-name")` for explicit control:
```python
Skill(command: "validate-refactor-adr")  # Pre-work validation
Skill(command: "manage-refactor-markers")  # Marker management
Skill(command: "detect-refactor-markers")  # Health checks
Skill(command: "multi-file-refactor")  # Code execution
```

### Best Practices

1. **Start with Phase 1** - Never skip ADR validation or marker placement
2. **One component at a time** - Don't parallelize component migrations (too risky)
3. **Test after each file** - Fail fast, catch issues early
4. **Monitor health regularly** - Use detect-refactor-markers weekly
5. **Update tracking immediately** - Don't batch status updates
6. **Document surprises** - Log unexpected issues in Session Notes
7. **Quality gates every phase** - Not just at the end

### Common Pitfalls to Avoid

❌ **Don't:**
- Skip ADR validation (Task 1.1) - causes governance issues
- Remove markers before refactor complete - loses tracking
- Batch all changes into one commit - hard to debug/revert
- Ignore stale markers (>30 days) - indicates blocked work
- Skip baseline testing (Task 1.4) - can't detect regressions

✅ **Do:**
- Follow task sequence (phases are ordered for safety)
- Run quality gates frequently (not just end)
- Document blockers immediately (don't lose context)
- Use skills for automation (don't manual everything)
- Celebrate completion properly (update ADR, remove markers, document)

---

**Questions or Issues?**
- Review CLAUDE.md refactor policy
- Check .claude/refactor-marker-guide.md for marker standards
- Consult docs/ADR-DIRECTORY-GUIDE.md for ADR workflow
- Ask for help in project chat/issues
