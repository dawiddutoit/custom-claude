# Baseline Lifecycle Guide

Best practices for managing quality baselines throughout their lifecycle.

---

## Overview

**A baseline's lifecycle consists of:**
1. **Creation** - Capture initial metrics
2. **Active Use** - Reference during development
3. **Updates** - Add observations, document issues
4. **Re-baseline** - Replace after major changes
5. **Archival** - Preserve historical baselines

**This guide covers:**
- When to create baselines
- How to maintain baselines
- When to re-baseline
- Archival strategies
- Multi-feature baseline management

---

## 1. Baseline Creation

### When to Create

**ALWAYS create a baseline:**

✅ **New feature start**
- Timing: BEFORE writing any code
- Reason: Establish regression detection reference
- Who: @planner (at plan creation)

✅ **Refactor work start**
- Timing: AFTER validating ADR, BEFORE refactoring
- Reason: Document pre-refactor state
- Who: @implementer (task 0)

✅ **Major dependency upgrade**
- Timing: AFTER upgrade, BEFORE new work
- Reason: Establish new reference point
- Who: @statuser (on request)

✅ **Architecture change**
- Timing: AFTER architecture shift, BEFORE feature work
- Reason: Reset expectations for new architecture
- Who: @planner or @implementer

❌ **DON'T create a baseline:**
- In the middle of feature work (too late)
- After every commit (too noisy)
- For trivial changes (typos, comments)

### Naming Convention

**Format:** `baseline_{feature}_{date}`

**Components:**
- `baseline_` - Prefix for discoverability
- `{feature}` - Feature name or refactor identifier (lowercase, underscores)
- `{date}` - YYYY-MM-DD format

**Examples:**
```
✅ GOOD:
- baseline_auth_2025-10-16
- baseline_service_result_migration_2025-10-16
- baseline_post_py312_upgrade_2025-10-16
- baseline_graphql_api_2025-10-17

❌ BAD:
- baseline_1 (no feature, no date)
- baseline_feature (no date, not unique)
- baseline_2025-10-16 (no feature)
- auth_baseline (non-standard prefix)
- baseline-auth-20251016 (hyphens in date)
```

### Creation Checklist

**Before creating a baseline:**
- [ ] Feature name identified (clear, descriptive)
- [ ] Quality checks available (check_all.sh or individual tools)
- [ ] Git repository accessible (for commit hash)
- [ ] Memory MCP server running (or fallback file ready)

**During creation:**
- [ ] Run quality checks (document failures if any)
- [ ] Parse all 5 metrics (tests, coverage, type errors, linting, dead code)
- [ ] Capture git commit hash
- [ ] Record timestamp
- [ ] Document pre-existing issues (if any)

**After creation:**
- [ ] Memory entity created
- [ ] Baseline name returned
- [ ] Reference stored in todo.md
- [ ] Baseline metrics communicated to user

---

## 2. Active Use

### Referencing Baselines

**In todo.md:**
```markdown
# Todo: Authentication Feature
Baseline: baseline_auth_2025-10-16
Created: 2025-10-16 10:30:00

## Quality Metrics (Baseline)
- Tests: 145 passed (87% coverage)
- Type safety: Clean
- Code quality: Clean
```

**In memory (feature entity):**
```yaml
name: feature_auth
type: feature
observations:
  - "Baseline: baseline_auth_2025-10-16"
  - "Started: 2025-10-16"
  - "Status: in_progress"
```

**In quality gate runs:**
```bash
# Compare current metrics to baseline
BASELINE_NAME="baseline_auth_2025-10-16"

# Retrieve baseline from memory
BASELINE=$(mcp__memory__find_memories_by_name(names=["$BASELINE_NAME"]))

# Parse baseline metrics
BASELINE_TESTS=$(echo "$BASELINE" | jq '.observations[] | select(. | contains("Tests:"))' | grep -oE "[0-9]+ passed")

# Compare to current
CURRENT_TESTS=148  # From current run
if [ $CURRENT_TESTS -lt $BASELINE_TESTS ]; then
    echo "❌ Regression: Test count dropped"
fi
```

### Updating Baselines

**Add observations (don't replace):**
```python
# Document issue found during development
mcp__memory__add_observations({
    "observations": [{
        "entityName": "baseline_auth_2025-10-16",
        "observations": [
            "Issue found: Flaky test test_login (documented in issue #123)",
            "Workaround: Skip test until fixed"
        ]
    }]
})
```

**Example scenarios for updates:**

**1. Flaky test discovered:**
```yaml
observations:
  - "Tests: 145 passed, 2 skipped"
  - "Note: test_login is flaky (skipped), documented in issue #123"
```

**2. Pre-existing issue documented later:**
```yaml
observations:
  - "Type errors: 3"
  - "Update: 2 of 3 errors are in legacy code (will not fix)"
```

**3. Baseline used by multiple agents:**
```yaml
observations:
  - "Used by: @planner, @implementer, @unit-tester"
  - "Referenced in: todo.md, quality gate runs (10 times)"
```

### Retrieving Baselines

**By name (exact match):**
```python
baseline = mcp__memory__find_memories_by_name(names=["baseline_auth_2025-10-16"])
```

**By search (fuzzy match):**
```python
baselines = mcp__memory__search_memories(query="baseline auth")
```

**By feature (via relations):**
```python
# If baseline linked to feature entity
feature = mcp__memory__find_memories_by_name(names=["feature_auth"])
# Find related baseline
```

---

## 3. Re-baseline (When to Replace)

### Triggers for Re-baseline

**ALWAYS re-baseline after:**

✅ **Major dependency upgrade**
- Example: Python 3.11 → 3.12
- Reason: Metrics may change (tests removed, errors fixed)
- Action: Create new baseline, archive old

✅ **Architecture change**
- Example: Monolith → microservices
- Reason: Fundamentally different codebase structure
- Action: Create new baseline, archive old

✅ **Large refactor completion**
- Example: ServiceResult migration complete
- Reason: Baseline reflects pre-refactor state, no longer relevant
- Action: Create new baseline, archive old

✅ **Test suite overhaul**
- Example: Migrated from unittest to pytest
- Reason: Test count, execution time changed significantly
- Action: Create new baseline, archive old

❌ **DON'T re-baseline after:**
- Single bug fix (maintain continuity)
- Minor dependency patch (no significant changes)
- Small feature addition (use delta instead)

### Re-baseline Process

**Step 1: Capture new baseline**
```bash
# Run quality checks (new environment)
./scripts/check_all.sh > /tmp/new-baseline-output.txt 2>&1

# Parse metrics
# (use metrics-parsing-guide.md)
```

**Step 2: Calculate delta from previous baseline**
```python
# Retrieve previous baseline
old_baseline = mcp__memory__find_memories_by_name(names=["baseline_auth_2025-10-15"])

# Extract old metrics
old_tests = 152  # From old_baseline observations

# Compare to new
new_tests = 150
delta = new_tests - old_tests  # -2
```

**Step 3: Create new baseline with delta documentation**
```python
mcp__memory__create_entities({
    "entities": [{
        "name": "baseline_post_py312_upgrade_2025-10-16",
        "type": "quality_baseline",
        "observations": [
            "Tests: 150 passed, 0 failed, 2 skipped",
            "Coverage: 88%",
            # ... other metrics
            "Re-baseline reason: Python 3.11 → 3.12 upgrade",
            "Delta from baseline_auth_2025-10-15:",
            "  - Tests: 152 → 150 (-2, deprecated APIs removed)",
            "  - Type errors: 3 → 0 (-3, fixed by Python 3.12)",
            "Previous baseline archived: baseline_auth_2025-10-15"
        ]
    }]
})
```

**Step 4: Archive previous baseline**
```python
# Add archival observation to old baseline
mcp__memory__add_observations({
    "observations": [{
        "entityName": "baseline_auth_2025-10-15",
        "observations": [
            "Archived: Replaced by baseline_post_py312_upgrade_2025-10-16",
            "Reason: Python 3.12 upgrade",
            "Archived date: 2025-10-16"
        ]
    }]
})
```

**Step 5: Update references**
```markdown
# Update todo.md
# Old:
Baseline: baseline_auth_2025-10-15

# New:
Baseline: baseline_post_py312_upgrade_2025-10-16
Previous baseline: baseline_auth_2025-10-15 (archived, Python 3.11)
```

### Re-baseline Checklist

- [ ] Trigger identified (upgrade, architecture change, etc.)
- [ ] New baseline captured
- [ ] Delta calculated and documented
- [ ] Previous baseline archived (not deleted)
- [ ] References updated (todo.md, memory)
- [ ] User notified of re-baseline
- [ ] Reason documented in new baseline

---

## 4. Archival

### Why Archive (Not Delete)

**Reasons to preserve old baselines:**
- Historical context (understand project evolution)
- Debugging (compare to earlier states)
- Audit trail (when did metrics change?)
- Regression analysis (was this issue present before?)

**Archival vs Deletion:**
- ✅ **Archive:** Keep in memory, mark as archived
- ❌ **Delete:** Lose historical context, can't reference

### Archival Process

**Mark as archived:**
```python
mcp__memory__add_observations({
    "observations": [{
        "entityName": "baseline_auth_2025-10-15",
        "observations": [
            "Status: ARCHIVED",
            "Archived date: 2025-10-16",
            "Replaced by: baseline_post_py312_upgrade_2025-10-16",
            "Reason: Python 3.12 upgrade",
            "Do not use for regression detection (use new baseline)"
        ]
    }]
})
```

**Link archived baseline to successor:**
```python
# Create relation: old → new
mcp__memory__create_relations({
    "relations": [{
        "source": "baseline_auth_2025-10-15",
        "target": "baseline_post_py312_upgrade_2025-10-16",
        "relationType": "succeeded_by"
    }]
})
```

**Export to file (optional):**
```bash
# Export archived baseline to JSON
mcp__memory__find_memories_by_name(names=["baseline_auth_2025-10-15"]) > .archived-baselines/baseline_auth_2025-10-15.json
```

### Archival Checklist

- [ ] Baseline marked as "ARCHIVED"
- [ ] Archived date recorded
- [ ] Successor baseline linked
- [ ] Reason documented
- [ ] Warning added ("do not use for regression detection")
- [ ] Optional: Exported to file for backup

---

## 5. Multi-Feature Baseline Management

### Scenario: Multiple Features in Parallel

**Context:**
- Feature A: Authentication (in progress)
- Feature B: Profile (starting)
- Feature C: Settings (planned)

**Baseline strategy:**
```
baseline_auth_2025-10-15        (Feature A, active)
baseline_profile_2025-10-16     (Feature B, active)
baseline_settings_2025-10-17    (Feature C, planned)
```

**Key principles:**
- ✅ Each feature has its own baseline
- ✅ Baselines created at feature start (not shared)
- ✅ Baselines may have different metrics (different starting points)

**Why separate baselines?**
- Feature A may introduce changes affecting Feature B's baseline
- Each feature should detect regressions independently
- Baselines capture project state at different times

### Scenario: Shared Baseline After Integration

**Context:**
- Feature A complete (auth merged to main)
- Feature B starting (uses Feature A code)

**Baseline strategy:**
```
baseline_auth_2025-10-15        (Feature A baseline, archived)
baseline_post_auth_merge_2025-10-16  (New baseline after Feature A merge)
baseline_profile_2025-10-16     (Feature B baseline, uses post-merge state)
```

**Process:**
1. Feature A completes, merges to main
2. Re-baseline main branch: `baseline_post_auth_merge_2025-10-16`
3. Feature B starts, uses new baseline
4. Feature A baseline archived

**Benefits:**
- Feature B baseline includes Feature A changes
- No false regressions (Feature B sees clean post-merge state)
- Clear lineage (Feature A → merge → Feature B)

### Scenario: Long-Running Feature

**Context:**
- Feature A started 2 weeks ago (baseline_auth_2025-10-01)
- Main branch has evolved (new features merged)
- Feature A nearing completion

**Question:** Should Feature A re-baseline?

**Decision matrix:**

| Condition | Re-baseline? | Reason |
|-----------|--------------|--------|
| Main evolved but Feature A isolated | ❌ No | Keep original baseline, detect regressions in Feature A only |
| Main evolved AND Feature A merged main | ✅ Yes | Re-baseline to reflect merged changes |
| Feature A complete, ready to merge | ❌ No | Use original baseline for final quality check |
| Post-merge to main | ✅ Yes | Re-baseline main for next feature |

**Best practice:**
- Maintain original baseline throughout feature development
- Re-baseline main after merge (for next feature)

### Scenario: Hotfix Baseline

**Context:**
- Production bug found
- Hotfix needed (bypass normal feature workflow)

**Baseline strategy:**
```
baseline_main_2025-10-16        (Current main baseline)
baseline_hotfix_bug123_2025-10-16  (Hotfix baseline)
```

**Process:**
1. Create hotfix baseline from main
2. Fix bug
3. Compare to hotfix baseline (ensure no regressions)
4. Merge hotfix
5. Re-baseline main (include hotfix)

**Why separate hotfix baseline?**
- Hotfix may have different quality thresholds (speed over perfection)
- Document hotfix state separately
- Compare hotfix to main baseline (understand impact)

---

## 6. Baseline Comparison Strategies

### Strict Comparison (No Regressions Allowed)

**Use for:**
- Production code
- Critical features (auth, payments)
- Refactor work (must not break existing)

**Comparison logic:**
```python
def strict_compare(baseline, current):
    return (
        current.tests_passed >= baseline.tests_passed and
        current.coverage >= baseline.coverage and
        current.type_errors <= baseline.type_errors and
        current.linting_errors <= baseline.linting_errors and
        current.dead_code <= baseline.dead_code
    )
```

**Result:**
- ✅ Pass: All metrics maintained or improved
- ❌ Fail: Any metric regressed

### Flexible Comparison (Allow Minor Regressions)

**Use for:**
- Experimental features
- Prototypes
- Early development

**Comparison logic:**
```python
def flexible_compare(baseline, current):
    # Allow 5% regression in coverage
    coverage_ok = current.coverage >= (baseline.coverage - 5)

    # Allow 2 fewer tests (if deprecated)
    tests_ok = current.tests_passed >= (baseline.tests_passed - 2)

    # Type errors: no new errors
    type_errors_ok = current.type_errors <= baseline.type_errors

    return coverage_ok and tests_ok and type_errors_ok
```

**Result:**
- ✅ Pass: Metrics within acceptable range
- ⚠️  Warning: Minor regression (document reason)
- ❌ Fail: Significant regression

### Delta-Only Comparison (Report Changes)

**Use for:**
- Reporting (not blocking)
- Major changes (re-baseline expected)
- Historical analysis

**Comparison logic:**
```python
def delta_compare(baseline, current):
    return {
        "tests": current.tests_passed - baseline.tests_passed,
        "coverage": current.coverage - baseline.coverage,
        "type_errors": current.type_errors - baseline.type_errors,
        # ... report all deltas, no pass/fail
    }
```

**Result:**
- Report deltas (positive, negative, neutral)
- No blocking (informational only)

---

## 7. Troubleshooting

### Issue: Baseline Not Found

**Symptoms:**
- Search returns no results
- Quality gate can't compare to baseline

**Diagnosis:**
```python
# Search by name
mcp__memory__find_memories_by_name(names=["baseline_auth_2025-10-16"])

# Search by query
mcp__memory__search_memories(query="baseline auth")

# Check fallback file
ls .quality-baseline-*.json
```

**Solutions:**
1. **If in memory but search fails:** Try different query
2. **If in fallback file:** Import to memory
3. **If completely lost:** Recapture baseline (last resort)

### Issue: Baseline Has Wrong Metrics

**Symptoms:**
- Baseline says "0 tests" but codebase has tests
- Coverage is "N/A"

**Diagnosis:**
```python
# Retrieve baseline
baseline = mcp__memory__find_memories_by_name(names=["baseline_auth_2025-10-16"])

# Inspect observations
print(baseline.observations)
# Look for parsing warnings
```

**Solutions:**
1. **If parsing failed:** Recapture baseline with updated parsing
2. **If metrics changed:** Re-baseline (document reason)
3. **If observation incorrect:** Update observation (don't replace baseline)

### Issue: Too Many Baselines

**Symptoms:**
- Search returns 20+ baselines
- Hard to find current baseline

**Diagnosis:**
```python
# Search for baselines
baselines = mcp__memory__search_memories(query="baseline")

# Count active vs archived
active = [b for b in baselines if "ARCHIVED" not in b.observations]
archived = [b for b in baselines if "ARCHIVED" in b.observations]
```

**Solutions:**
1. **Archive old baselines:** Mark inactive baselines as archived
2. **Export to files:** Move old baselines to `.archived-baselines/`
3. **Link baselines:** Create relations (succeeded_by) for clarity

### Issue: Baseline Outdated

**Symptoms:**
- Baseline from 2 months ago
- Many changes since baseline created

**Diagnosis:**
```python
# Check baseline date
baseline = mcp__memory__find_memories_by_name(names=["baseline_auth_2025-08-16"])

# Compare to current date
# 2 months old = likely outdated
```

**Solutions:**
1. **Re-baseline:** Capture new baseline, archive old
2. **Document staleness:** Add observation "Baseline outdated (2 months old)"
3. **Use delta comparison:** Report changes, don't block

---

## 8. Best Practices Summary

### Do's ✅

- ✅ Create baseline BEFORE any code changes
- ✅ Use consistent naming convention
- ✅ Document pre-existing issues in baseline
- ✅ Reference baseline in todo.md
- ✅ Update baseline observations (add, don't replace)
- ✅ Re-baseline after major changes
- ✅ Archive old baselines (don't delete)
- ✅ Link baselines (succeeded_by relations)
- ✅ Export baselines to files (backup)

### Don'ts ❌

- ❌ Skip baseline creation (no regression detection)
- ❌ Reuse baselines across features (stale reference)
- ❌ Capture baseline after starting work (too late)
- ❌ Ignore failures in baseline (document them)
- ❌ Delete old baselines (lose history)
- ❌ Forget to update references (todo.md, memory)
- ❌ Re-baseline too frequently (noise)
- ❌ Use strict comparison for experimental work (too rigid)

### When in Doubt

**Question:** Should I create a new baseline?
**Answer:** If starting new work (feature, refactor) → YES

**Question:** Should I re-baseline?
**Answer:** If major change (upgrade, architecture) → YES

**Question:** Should I archive a baseline?
**Answer:** If replaced by new baseline → YES

**Question:** Should I delete a baseline?
**Answer:** NO (archive instead)

---

## 9. Baseline Lifecycle Flowchart

```
┌─────────────────────┐
│  Feature Start      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Create Baseline     │ ◄─── Baseline Creation
│ (capture-quality-   │
│  baseline skill)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Reference in        │ ◄─── Active Use
│ todo.md, memory     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Development         │
│ (compare to         │
│  baseline)          │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌──────┐     ┌──────────┐
│ Done │     │ Major    │
│      │     │ Change   │
└──┬───┘     └────┬─────┘
   │              │
   │              ▼
   │         ┌─────────────────┐
   │         │ Re-baseline     │ ◄─── Re-baseline
   │         │ (new baseline)  │
   │         └────┬────────────┘
   │              │
   │              ▼
   │         ┌─────────────────┐
   │         │ Archive Old     │ ◄─── Archival
   │         │ Baseline        │
   │         └────┬────────────┘
   │              │
   └──────────────┘
                  │
                  ▼
           ┌─────────────────┐
           │ Feature         │
           │ Complete        │
           └─────────────────┘
```

---

## 10. Templates

### Baseline Creation Template

```python
# Template for creating a baseline
def create_baseline(feature_name: str):
    # 1. Prepare context
    git_commit = get_git_commit()  # git rev-parse HEAD
    timestamp = get_timestamp()    # date +"%Y-%m-%d %H:%M:%S"
    date = get_date()              # date +"%Y-%m-%d"

    # 2. Run quality checks
    output = run_quality_checks()  # ./scripts/check_all.sh

    # 3. Parse metrics
    metrics = parse_metrics(output)  # See metrics-parsing-guide.md

    # 4. Create memory entity
    baseline_name = f"baseline_{feature_name}_{date}"
    mcp__memory__create_entities({
        "entities": [{
            "name": baseline_name,
            "type": "quality_baseline",
            "observations": [
                f"Tests: {metrics['tests_passed']} passed, {metrics['tests_failed']} failed, {metrics['tests_skipped']} skipped",
                f"Coverage: {metrics['coverage']}%",
                f"Type errors: {metrics['type_errors']}",
                f"Linting errors: {metrics['linting_errors']}",
                f"Dead code: {metrics['dead_code']} items",
                f"Execution time: {metrics['exec_time']}s",
                f"Git commit: {git_commit}",
                f"Timestamp: {timestamp}",
                f"Feature: {feature_name}"
            ]
        }]
    })

    # 5. Return baseline reference
    return baseline_name
```

### Re-baseline Template

```python
# Template for re-baseline with delta documentation
def rebaseline(old_baseline_name: str, new_feature_name: str, reason: str):
    # 1. Retrieve old baseline
    old_baseline = mcp__memory__find_memories_by_name(names=[old_baseline_name])
    old_metrics = parse_baseline_observations(old_baseline)

    # 2. Capture new baseline
    new_baseline_name = create_baseline(new_feature_name)

    # 3. Calculate delta
    new_baseline = mcp__memory__find_memories_by_name(names=[new_baseline_name])
    new_metrics = parse_baseline_observations(new_baseline)
    delta = calculate_delta(old_metrics, new_metrics)

    # 4. Add delta documentation to new baseline
    mcp__memory__add_observations({
        "observations": [{
            "entityName": new_baseline_name,
            "observations": [
                f"Re-baseline reason: {reason}",
                f"Delta from {old_baseline_name}:",
                f"  - Tests: {old_metrics['tests']} → {new_metrics['tests']} ({delta['tests']:+d})",
                f"  - Coverage: {old_metrics['coverage']}% → {new_metrics['coverage']}% ({delta['coverage']:+.1f}%)",
                f"  - Type errors: {old_metrics['type_errors']} → {new_metrics['type_errors']} ({delta['type_errors']:+d})",
                f"Previous baseline archived: {old_baseline_name}"
            ]
        }]
    })

    # 5. Archive old baseline
    mcp__memory__add_observations({
        "observations": [{
            "entityName": old_baseline_name,
            "observations": [
                "Status: ARCHIVED",
                f"Archived date: {get_date()}",
                f"Replaced by: {new_baseline_name}",
                f"Reason: {reason}"
            ]
        }]
    })

    # 6. Create relation
    mcp__memory__create_relations({
        "relations": [{
            "source": old_baseline_name,
            "target": new_baseline_name,
            "relationType": "succeeded_by"
        }]
    })

    return new_baseline_name
```

---

**Last Updated:** 2025-10-16
**Version:** 1.0.0
