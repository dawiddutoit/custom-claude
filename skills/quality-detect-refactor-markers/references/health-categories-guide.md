# Health Categories Guide

**Detailed classification logic for refactor marker health assessment.**

---

## Overview

The detect-refactor-markers skill categorizes markers into four health states:

1. **✅ Healthy** - All good, continue monitoring
2. **⚠️ Stale** - Attention needed, review progress
3. **❌ Orphaned** - Critical issue, immediate action required
4. **🔴 Should Be Removed** - Cleanup needed, work complete

This guide defines the criteria, detection logic, and recommended actions for each category.

---

## 1. Healthy Markers ✅

### Definition

A healthy marker indicates an active, well-tracked refactor with no issues.

### Criteria

**All of the following must be true:**

- ✅ ADR file exists and is accessible
- ✅ ADR status matches marker status (both IN_PROGRESS)
- ✅ Age < 30 days (if STARTED date present)
- ✅ ADR located in `docs/adr/in_progress/`
- ✅ PERMANENT_RECORD path is correct
- ✅ No blocking issues documented

### Detection Logic

```bash
# Step 1: Validate ADR existence
find docs/adr/in_progress -name "*027-*.md" -type f
# Output: docs/adr/in_progress/027-service-result-migration.md
# Result: ✅ ADR exists

# Step 2: Check ADR location
dirname docs/adr/in_progress/027-service-result-migration.md
# Output: docs/adr/in_progress
# Result: ✅ In progress directory (correct)

# Step 3: Calculate age
STARTED="2025-10-10"
CURRENT=$(date +%Y-%m-%d)  # 2025-10-16
AGE_DAYS=6
# 6 < 30 = ✅ Fresh

# Step 4: Check status consistency
grep "STATUS:" src/service.py
# Output: # STATUS: IN_PROGRESS

grep "Status:" docs/adr/in_progress/027-service-result-migration.md
# Output: Status: IN_PROGRESS
# Result: ✅ Consistent

# Conclusion: HEALTHY ✅
```

### Example

```python
# src/service.py
# REFACTOR: ADR-027 - ServiceResult Migration
# STATUS: IN_PROGRESS
# STARTED: 2025-10-10
# PERMANENT_RECORD: docs/adr/in_progress/027-service-result-migration.md
```

**ADR:** `docs/adr/in_progress/027-service-result-migration.md` (exists)
**Age:** 6 days
**Status:** IN_PROGRESS (both marker and ADR)

### Health Report

```yaml
health: GOOD
marker:
  adr: ADR-027
  age_days: 6
  status: IN_PROGRESS
  adr_valid: true
  adr_location: in_progress
  issues: []
recommendation: Continue monitoring, no action needed
```

### Actions

**Monitor:**
- Track progress weekly
- Update ADR with milestones
- Remove markers when complete

**No immediate action required.**

---

## 2. Stale Markers ⚠️

### Definition

A stale marker indicates a refactor taking longer than expected, potentially blocked or abandoned.

### Criteria

**Any of the following triggers stale classification:**

- ⚠️ Age > 30 days since STARTED date
- ⚠️ ADR shows IN_PROGRESS but last modified >14 days ago
- ⚠️ No recent commits touching marked files
- ⚠️ ADR documents blockers without resolution plan

### Detection Logic

```bash
# Step 1: Calculate age
STARTED="2025-09-01"
CURRENT="2025-10-16"
AGE_DAYS=45
# 45 > 30 = ⚠️ STALE

# Step 2: Check ADR last modified date
stat -f "%Sm" -t "%Y-%m-%d" docs/adr/in_progress/015-database-migration.md
# Output: 2025-09-05
DAYS_SINCE_MODIFIED=41
# 41 > 14 = ⚠️ No recent updates

# Step 3: Check recent commits
git log --since="30 days ago" --oneline -- src/infrastructure/database.py
# Output: (empty or very few)
# Result: ⚠️ No recent activity

# Conclusion: STALE ⚠️
```

### Staleness Thresholds

| Threshold | Severity | Action Required |
|-----------|----------|-----------------|
| 30-45 days | Low | Review progress |
| 45-60 days | Medium | Update ADR or re-scope |
| 60-90 days | High | Decide: complete, pause, or abandon |
| >90 days | Critical | Immediate review, likely abandon |

### Example

```python
# src/infrastructure/database.py
# REFACTOR: ADR-015 - Database Migration
# STATUS: IN_PROGRESS
# STARTED: 2025-09-01  # 45 days ago
# PERMANENT_RECORD: docs/adr/in_progress/015-database-migration.md
```

**ADR:** Exists but last modified 41 days ago
**Age:** 45 days
**Recent commits:** None in last 30 days

### Health Report

```yaml
health: ATTENTION_NEEDED
marker:
  adr: ADR-015
  age_days: 45
  started: 2025-09-01
  adr_last_modified: 2025-09-05
  days_since_adr_update: 41
  recent_commits: 0
  status: IN_PROGRESS
severity: MEDIUM
issues:
  - Refactor taking longer than typical 30-day window
  - No recent ADR updates (>14 days)
  - No code activity in last 30 days
possible_causes:
  - Work blocked by external dependency
  - Developer unavailable (vacation, other priorities)
  - Refactor more complex than estimated
  - Work abandoned without cleanup
recommendation: |
  Review within 7 days:
  1. Assess if work should continue
  2. Update ADR with current status
  3. Document blockers if any
  4. Set new completion date or abandon
```

### Actions

**Immediate (within 7 days):**
1. **Review ADR** - Read current state and blockers
2. **Check git log** - When was last activity?
3. **Contact developer** - Is work continuing?

**Decision Required:**

**Option A: Continue Work**
- Update ADR with new timeline
- Document current progress
- Set milestone checkpoints
- Update STARTED date to current (reset clock)

**Option B: Re-scope**
- Split into smaller phases
- Complete current phase, defer rest
- Update ADR with new scope
- Remove markers for deferred work

**Option C: Abandon**
- Document decision in ADR
- Move ADR to `deprecated/`
- Remove all markers
- Add lessons learned

### Automation

```bash
# Weekly cron job to detect stale markers
# .github/workflows/stale-markers.yml

name: Detect Stale Markers
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday 9am

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check for stale markers
        run: |
          # Invoke detect-refactor-markers skill
          # If stale markers found, create GitHub issue
```

---

## 3. Orphaned Markers ❌

### Definition

An orphaned marker references a non-existent ADR, indicating missing or deleted documentation.

### Criteria

**Any of the following:**

- ❌ ADR file not found in any `docs/adr/` directory
- ❌ PERMANENT_RECORD path incorrect (404)
- ❌ ADR number doesn't match any existing ADR
- ❌ ADR deleted without removing markers

### Detection Logic

```bash
# Step 1: Extract ADR number from marker
ADR_NUM=$(grep "REFACTOR:" src/service.py | sed -n 's/.*ADR-\([0-9]\+\).*/\1/p')
# Output: 042

# Step 2: Search for ADR in all directories
find docs/adr -name "*042-*.md" -type f
# Output: (empty)
# Result: ❌ ADR NOT FOUND

# Step 3: Search git history (was it deleted?)
git log --all --full-history -- "docs/adr/*042*"
# Output: commit abc123 "Remove ADR-042" (example)
# Result: ❌ ADR was deleted

# Step 4: Search for related ADRs (wrong number?)
find docs/adr -name "*payment*" -type f
# Output: docs/adr/in_progress/043-payment-refactor.md
# Result: Possible typo (042 vs 043)

# Conclusion: ORPHANED ❌
```

### Severity Levels

| Scenario | Severity | Impact |
|----------|----------|--------|
| ADR deleted recently | High | Can be recovered from git |
| ADR never existed | Critical | No documentation, unclear intent |
| Wrong ADR number (typo) | Medium | Fixable, correct ADR may exist |
| ADR moved, not updated | Low | Update PERMANENT_RECORD path |

### Example

```python
# src/services/payment_service.py
# REFACTOR: ADR-042 - Payment Processing Refactor
# STATUS: IN_PROGRESS
# STARTED: 2025-10-01
# PERMANENT_RECORD: docs/adr/in_progress/042-payment-refactor.md

# But ADR-042 doesn't exist anywhere
```

**Search results:** No files found
**Git history:** ADR was deleted in commit abc123
**Related ADRs:** ADR-043 found with similar title

### Health Report

```yaml
health: CRITICAL
marker:
  adr: ADR-042
  file: src/services/payment_service.py
  markers: 4
  status: IN_PROGRESS
  adr_valid: false
severity: HIGH
issues:
  - ADR file not found in any docs/adr directory
  - PERMANENT_RECORD path returns 404
investigation:
  git_history:
    found: true
    deleted_in: commit abc123
    deleted_date: 2025-09-15
    deleted_by: user@example.com
  possible_related_adrs:
    - adr: ADR-043
      title: Payment Processing Refactor (similar)
      path: docs/adr/in_progress/043-payment-refactor.md
possible_causes:
  - ADR deleted without removing markers (most likely)
  - Typo in marker (042 vs 043)
  - ADR moved to different directory
recommendation: |
  CRITICAL: Resolve immediately

  Investigation steps:
  1. Check if ADR-043 is the correct ADR (title matches)
  2. If yes: Update markers 042 → 043
  3. If no: Check why ADR-042 was deleted
  4. Review commit abc123 for context

  Resolution (choose one):
  A. Correct ADR exists (typo in marker):
     - Update markers: manage-refactor-markers update --old=042 --new=043

  B. ADR deleted intentionally (work abandoned):
     - Remove markers: manage-refactor-markers remove --adr=042

  C. ADR deleted accidentally:
     - Restore ADR: git checkout abc123^ -- docs/adr/in_progress/042-payment-refactor.md
```

### Actions

**Immediate (within 24 hours):**

1. **Investigate:**
   ```bash
   # Search all directories
   find docs/adr -name "*042*"

   # Check git history
   git log --all --full-history -- "docs/adr/*042*"

   # Search for similar ADRs
   find docs/adr -name "*payment*"
   ```

2. **Determine cause:**
   - Deleted? Check commit message for reason
   - Typo? Compare with existing ADRs
   - Moved? Search entire project

3. **Choose resolution:**

**Resolution A: Correct ADR Found (Typo)**
```bash
# Update marker ADR numbers
manage-refactor-markers update --file=src/services/payment_service.py --old-adr=042 --new-adr=043

# Verify
grep "ADR-042" src/services/payment_service.py
# (should be empty)
```

**Resolution B: ADR Deleted Intentionally**
```bash
# Remove all markers
manage-refactor-markers remove --adr=042

# Verify
grep -r "ADR-042" src/
# (should be empty)

# Commit
git add -A
git commit -m "chore: remove orphaned ADR-042 markers (ADR deleted)"
```

**Resolution C: ADR Deleted Accidentally**
```bash
# Restore ADR from git history
git log --all --full-history -- "docs/adr/*042*"
# Find commit before deletion: abc123^

git checkout abc123^ -- docs/adr/in_progress/042-payment-refactor.md

# Verify restoration
ls docs/adr/in_progress/042-payment-refactor.md

# Re-validate markers
detect-refactor-markers
# Should now show healthy
```

### Prevention

**Best practices to prevent orphaned markers:**

1. **Never delete ADRs without checking markers:**
   ```bash
   # Before deleting ADR-042
   grep -r "ADR-042" src/
   # If output: Remove markers first
   ```

2. **Use manage-refactor-markers remove before ADR deletion:**
   ```bash
   # Correct workflow
   manage-refactor-markers remove --adr=042
   rm docs/adr/in_progress/042-payment-refactor.md
   git add -A
   git commit -m "chore: remove ADR-042 and markers"
   ```

3. **Move ADRs instead of deleting:**
   ```bash
   # If work abandoned
   mv docs/adr/in_progress/042-payment.md docs/adr/deprecated/042-payment.md
   # Markers remain valid, ADR shows deprecated status
   ```

4. **Add pre-commit hook:**
   ```bash
   # .git/hooks/pre-commit
   # Check for orphaned markers before allowing commit
   if detect-refactor-markers | grep -q "ORPHANED"; then
     echo "Error: Orphaned markers detected"
     exit 1
   fi
   ```

---

## 4. Should Be Removed 🔴

### Definition

Markers that reference completed ADRs but haven't been cleaned up.

### Criteria

**Any of the following:**

- 🔴 ADR moved to `docs/adr/implemented/`
- 🔴 ADR status changed to COMPLETE or IMPLEMENTED
- 🔴 ADR marked as done but markers remain in code
- 🔴 Refactor work finished but cleanup forgotten

### Detection Logic

```bash
# Step 1: Find ADR location
find docs/adr -name "*028-*.md"
# Output: docs/adr/implemented/028-cache-layer.md
# Result: 🔴 ADR in implemented/ directory

# Step 2: Check ADR status
grep "Status:" docs/adr/implemented/028-cache-layer.md
# Output: Status: COMPLETE
# Result: 🔴 Work complete

# Step 3: Check for remaining markers
grep -r "ADR-028" src/
# Output:
# src/service.py:1:# REFACTOR: ADR-028
# src/service.py:5:# REFACTOR(ADR-028)
# Result: 🔴 Markers still present

# Conclusion: SHOULD BE REMOVED 🔴
```

### Completion Indicators

| Indicator | Meaning | Action |
|-----------|---------|--------|
| ADR in `implemented/` | Work complete | Remove markers |
| ADR status: COMPLETE | Work finished | Remove markers |
| ADR status: IMPLEMENTED | Merged and deployed | Remove markers |
| All acceptance criteria met | Ready for cleanup | Remove markers |

### Example

```python
# src/application/cache_service.py
# REFACTOR: ADR-028 - Cache Layer Implementation
# STATUS: IN_PROGRESS  # <-- Outdated, should be removed
# STARTED: 2025-10-01
# PERMANENT_RECORD: docs/adr/implemented/028-cache-layer.md  # <-- Note: implemented/
```

**ADR location:** `docs/adr/implemented/` (completed)
**ADR status:** COMPLETE
**Markers:** Still present (outdated)

### Health Report

```yaml
health: CLEANUP_REQUIRED
marker:
  adr: ADR-028
  title: Cache Layer Implementation
  files: 2
  markers: 4
  adr_valid: true
  adr_location: implemented
  adr_status: COMPLETE
severity: HIGH
issues:
  - ADR marked COMPLETE and moved to implemented/
  - Refactor work finished but markers not removed
  - Code shows IN_PROGRESS but work actually done
impact:
  - Confuses developers (looks like work in progress)
  - Pollutes codebase with outdated markers
  - Prevents accurate refactor health reporting
  - Blocks feature completion gates
  - False positive for "active refactors"
completion_date: 2025-10-15  # From ADR metadata
days_since_completion: 1
recommendation: |
  Remove markers immediately

  1. Verify ADR completion:
     cat docs/adr/implemented/028-cache-layer.md

  2. Review acceptance criteria:
     # Ensure all criteria met

  3. Remove markers (dry-run first):
     manage-refactor-markers remove --adr=028 --dry-run

  4. Review changes:
     # Tool shows what will be removed

  5. Execute removal:
     manage-refactor-markers remove --adr=028

  6. Verify cleanup:
     grep -r "ADR-028" src/
     # Should return no results

  7. Commit:
     git add -A
     git commit -m "chore: remove ADR-028 markers (refactor complete)"
```

### Actions

**Immediate (within 24 hours):**

1. **Verify completion:**
   ```bash
   # Check ADR status
   cat docs/adr/implemented/028-cache-layer.md | grep "Status:"
   # Output: Status: COMPLETE

   # Check acceptance criteria
   cat docs/adr/implemented/028-cache-layer.md | grep -A 10 "Acceptance Criteria"
   # All criteria met? Yes → Safe to remove markers
   ```

2. **Remove markers (dry-run first):**
   ```bash
   # Dry-run: Show what will be removed
   manage-refactor-markers remove --adr=028 --dry-run

   # Output:
   # Would remove from src/application/cache_service.py:
   #   Line 1-4: File-level marker
   #   Line 6: Method marker
   # Would remove from src/queries/cache_query.py:
   #   Line 1-4: File-level marker
   #   Line 8: Method marker

   # Review changes (ensure correct)
   ```

3. **Execute removal:**
   ```bash
   # Remove markers
   manage-refactor-markers remove --adr=028

   # Output:
   # Removed 4 markers from 2 files
   # - src/application/cache_service.py: 2 markers removed
   # - src/queries/cache_query.py: 2 markers removed
   ```

4. **Verify cleanup:**
   ```bash
   # Ensure no markers remain
   grep -r "ADR-028" src/
   # (should be empty)

   # Run health check
   detect-refactor-markers
   # Should no longer report ADR-028
   ```

5. **Commit removal:**
   ```bash
   git add -A
   git commit -m "chore: remove ADR-028 markers (refactor complete)"
   git push
   ```

### Why This Matters

**Impact of not removing markers:**

1. **Developer confusion:**
   - New developers see markers, assume work in progress
   - Waste time investigating "incomplete" refactor
   - Unclear if they should continue work

2. **False metrics:**
   - Status reports show "active refactors" that are done
   - Feature completion blocked by phantom markers
   - Architecture health reports show false concerns

3. **Technical debt:**
   - Outdated comments pollute codebase
   - Harder to find real in-progress work
   - Reduces trust in marker system

4. **Blocking workflows:**
   - @feature-completer blocks completion (thinks work active)
   - @statuser reports incomplete refactor (false negative)
   - Quality gates may fail (markers present = work incomplete)

### Prevention

**Best practices:**

1. **Remove markers as last step of refactor:**
   ```bash
   # Refactor completion checklist:
   # [ ] All code changes complete
   # [ ] Tests passing
   # [ ] ADR updated to COMPLETE
   # [ ] ADR moved to implemented/
   # [ ] Markers removed ← Don't forget!
   # [ ] Changes committed
   ```

2. **Add to Definition of Done:**
   ```markdown
   # Feature Definition of Done
   - [ ] Code complete
   - [ ] Tests passing
   - [ ] Documentation updated
   - [ ] Refactor markers removed  ← Add this
   ```

3. **Automate detection:**
   ```bash
   # CI/CD pipeline check
   # .github/workflows/check-markers.yml

   - name: Check for completed refactors
     run: |
       if detect-refactor-markers | grep -q "should_be_removed"; then
         echo "Error: Completed refactors have markers remaining"
         echo "Run: manage-refactor-markers remove --adr=XXX"
         exit 1
       fi
   ```

4. **Feature completion gate:**
   ```bash
   # @feature-completer automatic check
   # Before allowing feature completion:
   1. Check detect-refactor-markers
   2. If should_be_removed found: Block completion
   3. Provide removal command
   4. Re-check after user runs command
   ```

---

## Health Summary Matrix

| Category | Criteria | Severity | Action Timeline | Automation |
|----------|----------|----------|-----------------|------------|
| ✅ Healthy | Age < 30d, ADR valid, status consistent | None | Monitor weekly | Status checks |
| ⚠️ Stale | Age > 30d OR no updates >14d | Medium | Review within 7 days | Weekly alerts |
| ❌ Orphaned | ADR not found | Critical | Fix within 24 hours | Block commits |
| 🔴 Should Remove | ADR complete, markers remain | High | Remove within 24 hours | Block completion |

---

## Decision Tree

```
Start: Marker detected
│
├─ Does ADR file exist?
│  ├─ No → ❌ ORPHANED (critical)
│  └─ Yes → Continue
│
├─ Where is ADR located?
│  ├─ implemented/ → 🔴 SHOULD BE REMOVED (high)
│  ├─ deprecated/ → 🔴 SHOULD BE REMOVED (high)
│  └─ in_progress/ → Continue
│
├─ What is marker age?
│  ├─ > 90 days → ⚠️ STALE (critical)
│  ├─ 60-90 days → ⚠️ STALE (high)
│  ├─ 30-60 days → ⚠️ STALE (medium)
│  └─ < 30 days → Continue
│
├─ When was ADR last updated?
│  ├─ > 30 days → ⚠️ STALE (medium)
│  ├─ 14-30 days → ⚠️ STALE (low)
│  └─ < 14 days → Continue
│
└─ All checks passed → ✅ HEALTHY
```

---

## Reporting Format

**Health report structure:**

```yaml
overall_health: GOOD | ATTENTION_NEEDED | CRITICAL | CLEANUP_REQUIRED

markers_by_health:
  healthy: 5
  stale: 1
  orphaned: 0
  should_be_removed: 1

priority_actions:
  - priority: HIGH
    category: should_be_removed
    adr: ADR-028
    action: Remove markers
    timeline: Within 24 hours

  - priority: MEDIUM
    category: stale
    adr: ADR-015
    action: Review progress
    timeline: Within 7 days

summary: |
  7 total markers detected
  - 5 healthy (monitor)
  - 1 stale (review)
  - 1 should remove (cleanup)

  2 actions required (see priority_actions above)
```

---

## Integration with Agents

### @statuser
- Invokes skill during every status check
- Includes refactor health in status report
- Highlights stale markers as potential blockers

### @feature-completer
- Invokes skill before allowing feature completion
- Blocks if any markers present (active, stale, or should-remove)
- Provides remediation commands

### @architecture-guardian
- Invokes skill during architecture health audits
- Flags long-running refactors as architectural concerns
- Recommends re-assessment for stale refactors

---

**See also:**
- [remediation-guide.md](./remediation-guide.md) - Step-by-step fix instructions
- [examples.md](./examples.md) - Real-world scenarios
- [SKILL.md](./SKILL.md) - Main skill documentation
