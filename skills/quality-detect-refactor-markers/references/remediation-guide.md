# Remediation Guide

**Step-by-step instructions to fix each type of refactor marker health issue.**

---

## Overview

This guide provides detailed remediation workflows for each marker health category detected by the detect-refactor-markers skill:

1. **⚠️ Stale Markers** - Review and update or complete
2. **❌ Orphaned Markers** - Investigate and resolve missing ADRs
3. **🔴 Should Be Removed** - Clean up completed refactor markers
4. **✅ Healthy Markers** - Maintenance and monitoring

---

## 1. Remediating Stale Markers ⚠️

**Issue:** Marker age > 30 days or no recent ADR updates

**Severity:** Medium to High (depending on age)

**Timeline:** Review within 7 days

### Step-by-Step Workflow

#### Step 1: Gather Information

```bash
# Navigate to project root
cd ${PROJECT_ROOT}

# Find the stale marker
grep -rn "ADR-015" src/ --include="*.py"
# Output:
# src/infrastructure/database.py:1:# REFACTOR: ADR-015 - Database Migration
# src/infrastructure/database.py:5:# REFACTOR(ADR-015): Migrate connection pool

# Check marker age
grep "STARTED:" src/infrastructure/database.py
# Output: # STARTED: 2025-09-01
# Age: 45 days (current: 2025-10-16)

# Read the ADR
cat docs/adr/in_progress/015-database-migration.md
# Review: Scope, status, blockers, acceptance criteria
```

#### Step 2: Check Recent Activity

```bash
# When was ADR last modified?
stat -f "%Sm" -t "%Y-%m-%d" docs/adr/in_progress/015-database-migration.md
# Output: 2025-09-05 (41 days ago)

# When was marked file last modified?
git log -1 --format="%ai" -- src/infrastructure/database.py
# Output: 2025-09-10 (36 days ago)

# Recent commits to marked file?
git log --since="30 days ago" --oneline -- src/infrastructure/database.py
# Output: (empty or minimal)

# Who owns this refactor?
git log -1 --format="%an <%ae>" -- docs/adr/in_progress/015-database-migration.md
# Output: John Doe <john@example.com>
```

#### Step 3: Assess Situation

**Answer these questions:**

1. **Is work actually in progress?**
   - Check with developer (John Doe)
   - Review git activity
   - Check related PRs

2. **What's blocking completion?**
   - Technical blocker (dependency, complexity)
   - Resource blocker (developer time, prioritization)
   - Scope blocker (requirements changed)

3. **Should work continue?**
   - Yes → Update timeline and continue
   - No → Abandon and clean up
   - Partial → Complete current phase, defer rest

#### Step 4: Choose Resolution Path

**Path A: Continue Work (Active)**

```bash
# 1. Update ADR with current status
cat >> docs/adr/in_progress/015-database-migration.md <<EOF

## Status Update - $(date +%Y-%m-%d)

**Current Progress:** 60% complete
- ✅ Connection pool configured
- ✅ Basic tests written
- ⚠️ Performance testing blocked by staging environment
- ⏳ Migration scripts pending review

**Blockers:**
- Staging environment downtime (resolved expected: 2025-10-20)
- Waiting on DBA review of migration scripts

**Next Steps:**
1. Complete performance testing (2025-10-21)
2. Finalize migration scripts (2025-10-25)
3. Run full test suite (2025-10-28)
4. Deploy to staging (2025-10-30)

**Revised Completion Date:** 2025-10-31

**Assigned:** John Doe
EOF

# 2. Optionally reset STARTED date (if major delay)
# This resets the staleness clock
sed -i '' 's/STARTED: 2025-09-01/STARTED: 2025-10-16/' src/infrastructure/database.py

# 3. Commit updates
git add docs/adr/in_progress/015-database-migration.md src/infrastructure/database.py
git commit -m "docs: update ADR-015 status (unblocked, revised timeline)"

# 4. Re-run health check
detect-refactor-markers
# Should now show updated timeline
```

**Path B: Re-scope Work (Split)**

```bash
# 1. Assess what's complete vs incomplete
# Complete: Connection pool configuration
# Incomplete: Performance testing, migration scripts

# 2. Complete current phase
# Remove markers from completed work
manage-refactor-markers remove --file=src/infrastructure/database.py --line=5
# (Only remove method marker for completed work)

# 3. Update ADR to reflect partial completion
cat >> docs/adr/in_progress/015-database-migration.md <<EOF

## Re-Scope Decision - $(date +%Y-%m-%d)

**Phase 1 Complete:**
- ✅ Connection pool configuration (done)
- ✅ Basic functionality working

**Phase 2 Deferred:**
- ⏸️ Performance optimization (new ADR: ADR-050)
- ⏸️ Advanced migration scripts (new ADR: ADR-050)

**Rationale:**
Core functionality is complete and stable. Advanced features deferred to ADR-050 to unblock current feature development.

**Status:** PARTIALLY COMPLETE
EOF

# 4. Move ADR to implemented/ (if core work done)
mv docs/adr/in_progress/015-database-migration.md docs/adr/implemented/015-database-migration.md

# 5. Update remaining marker to point to new ADR
# (If deferring work to new ADR-050)
sed -i '' 's/ADR-015/ADR-050/g' src/infrastructure/database.py

# 6. Create new ADR for deferred work
cat > docs/adr/in_progress/050-database-performance.md <<EOF
# ADR-050: Database Performance Optimization

Status: IN_PROGRESS
Supersedes: ADR-015 (partial)

## Context
Phase 2 of database migration (ADR-015). Core functionality complete, now optimizing performance.

## Decision
[...]
EOF

# 7. Commit changes
git add -A
git commit -m "feat: complete ADR-015 phase 1, defer phase 2 to ADR-050"
```

**Path C: Abandon Work**

```bash
# 1. Document abandonment reason in ADR
cat >> docs/adr/in_progress/015-database-migration.md <<EOF

## Abandonment Decision - $(date +%Y-%m-%d)

**Status:** ABANDONED

**Reason:**
Requirements changed. Database migration no longer needed due to switch to managed database service.

**Completed Work:**
- Connection pool POC (functional but not deployed)

**Lessons Learned:**
- Requirements should be validated before starting refactor
- Consider cloud-managed solutions earlier in planning

**Disposition:**
- Code reverted to pre-refactor state
- ADR moved to deprecated for historical reference
EOF

# 2. Move ADR to deprecated/
mv docs/adr/in_progress/015-database-migration.md docs/adr/deprecated/015-database-migration.md

# 3. Revert code changes (if needed)
git log --oneline -- src/infrastructure/database.py
# Find commit before refactor started
git revert <commit-hash>

# 4. Remove all markers
manage-refactor-markers remove --adr=015

# 5. Verify cleanup
grep -r "ADR-015" src/
# (should be empty)

# 6. Commit
git add -A
git commit -m "revert: abandon ADR-015 database migration (requirements changed)"
```

#### Step 5: Verify Resolution

```bash
# Run health check again
detect-refactor-markers

# Expected outcomes:
# Path A: Marker now shows updated STARTED date (fresh)
# Path B: Marker updated to new ADR or partially removed
# Path C: All ADR-015 markers removed (healthy)
```

### Prevention

**Best practices to avoid stale markers:**

1. **Set realistic timelines** (most refactors: 1-2 weeks)
2. **Update ADR weekly** (even if just progress notes)
3. **Split large refactors** into smaller phases
4. **Set checkpoint milestones** (review at 2 weeks, 4 weeks)
5. **Communicate blockers** early (don't wait 30 days)

---

## 2. Remediating Orphaned Markers ❌

**Issue:** Marker references non-existent ADR

**Severity:** Critical

**Timeline:** Fix within 24 hours

### Step-by-Step Workflow

#### Step 1: Investigate Missing ADR

```bash
# Navigate to project root
cd ${PROJECT_ROOT}

# Find the orphaned marker
grep -rn "ADR-042" src/ --include="*.py"
# Output:
# src/services/payment_service.py:1:# REFACTOR: ADR-042 - Payment Processing Refactor
# src/services/payment_service.py:6:# REFACTOR(ADR-042): [...]

# Search for ADR in all directories
find docs/adr -name "*042-*.md" -type f
# Output: (empty - not found)

# Search git history (was it deleted?)
git log --all --full-history -- "docs/adr/*042*"
# Output:
# commit abc123 2025-09-15 "feat: consolidate payment ADRs"
# (ADR was deleted or never existed)
```

#### Step 2: Check for Related ADRs

```bash
# Search by topic (payment)
find docs/adr -name "*payment*" -type f
# Output:
# docs/adr/in_progress/043-payment-refactor.md
# docs/adr/implemented/041-payment-integration.md

# Check if similar title
cat docs/adr/in_progress/043-payment-refactor.md | head -n 10
# Title: Payment Processing Refactor
# (Matches marker title!)

# Was 042 renamed to 043?
git log --all --follow -- "docs/adr/*payment*"
# (Check rename history)
```

#### Step 3: Determine Root Cause

**Scenario A: Typo in Marker (ADR exists as different number)**

**Evidence:**
- ADR-043 exists with matching title
- No git history of ADR-042 deletion
- Similar marker elsewhere references ADR-043

**Resolution:** Update marker ADR number

---

**Scenario B: ADR Deleted Intentionally (Work abandoned)**

**Evidence:**
- Git log shows ADR-042 deletion
- Commit message: "Remove abandoned refactor"
- No replacement ADR created

**Resolution:** Remove markers

---

**Scenario C: ADR Deleted Accidentally (Merge conflict)**

**Evidence:**
- Git log shows ADR-042 deleted
- Commit message: "Merge branch X" (no mention of ADR)
- ADR existed before merge

**Resolution:** Restore ADR from git

---

**Scenario D: ADR Never Created (Premature markers)**

**Evidence:**
- No git history of ADR-042 ever existing
- Markers added but ADR never written
- Developer forgot to create ADR

**Resolution:** Create ADR or remove markers

---

#### Step 4: Execute Resolution

**Resolution A: Correct Typo (Update Marker)**

```bash
# Verify correct ADR number
cat docs/adr/in_progress/043-payment-refactor.md | head -n 5
# Title matches, ADR-043 is correct

# Update markers: 042 → 043
manage-refactor-markers update \
  --file=src/services/payment_service.py \
  --old-adr=042 \
  --new-adr=043

# Verify update
grep "ADR-043" src/services/payment_service.py
# Should show updated markers

# No markers with old number
grep "ADR-042" src/services/payment_service.py
# (should be empty)

# Commit
git add src/services/payment_service.py
git commit -m "fix: correct ADR number in markers (042 → 043)"
```

**Resolution B: Remove Markers (Work Abandoned)**

```bash
# Verify ADR was intentionally deleted
git show abc123
# Commit message: "Remove abandoned payment refactor ADR-042"
# Confirmed: Work was abandoned

# Remove all ADR-042 markers
manage-refactor-markers remove --adr=042

# Verify removal
grep -r "ADR-042" src/
# (should be empty)

# Commit
git add -A
git commit -m "chore: remove orphaned ADR-042 markers (refactor abandoned)"
```

**Resolution C: Restore ADR (Accidental Deletion)**

```bash
# Find commit before deletion
git log --all --full-history -- "docs/adr/*042*"
# Output: commit abc123 deleted ADR (find parent: abc123^)

# Restore ADR
git checkout abc123^ -- docs/adr/in_progress/042-payment-refactor.md

# Verify restoration
ls docs/adr/in_progress/042-payment-refactor.md
# File restored

# Re-run health check
detect-refactor-markers
# Should now show healthy (ADR found)

# Commit restoration
git add docs/adr/in_progress/042-payment-refactor.md
git commit -m "restore: recover accidentally deleted ADR-042"
```

**Resolution D: Create Missing ADR**

```bash
# Check marker for context
cat src/services/payment_service.py | grep -A 5 "REFACTOR: ADR-042"
# Title: Payment Processing Refactor
# Context from code: Refactoring payment validation logic

# Create ADR from marker information
cat > docs/adr/in_progress/042-payment-refactor.md <<'EOF'
# ADR-042: Payment Processing Refactor

**Status:** IN_PROGRESS
**Started:** 2025-10-01
**Owner:** [Determine from git blame]

## Context

Payment processing code has grown complex and requires refactoring for:
- Improved validation logic
- Better error handling
- Simplified payment flow

## Decision

Refactor payment service to:
1. Extract validation into separate module
2. Implement ServiceResult pattern for error handling
3. Simplify payment processing flow

## Acceptance Criteria

- [ ] Validation logic extracted
- [ ] ServiceResult pattern implemented
- [ ] Tests updated
- [ ] Performance maintained

## Status

In progress. Markers added but ADR was not created initially (oversight).

## Notes

Created retroactively based on markers and code context.
EOF

# Commit new ADR
git add docs/adr/in_progress/042-payment-refactor.md
git commit -m "docs: create missing ADR-042 (retroactive from markers)"

# Verify health check
detect-refactor-markers
# Should now show healthy
```

#### Step 5: Verify Resolution

```bash
# Run health check
detect-refactor-markers

# Should no longer report ADR-042 as orphaned

# Verify specific ADR
grep -r "ADR-042" src/
# Resolution A: Should now show ADR-043
# Resolution B: Should be empty
# Resolution C: Should be present and healthy
# Resolution D: Should be present and healthy
```

### Prevention

**Best practices to avoid orphaned markers:**

1. **Create ADR before adding markers:**
   ```bash
   # Correct workflow:
   # 1. Write ADR
   # 2. Get ADR approved
   # 3. Add markers to code
   # 4. Start refactor work
   ```

2. **Check markers before deleting ADR:**
   ```bash
   # Before deleting ADR:
   grep -r "ADR-042" src/
   # If found: Remove markers first
   ```

3. **Use atomic operations:**
   ```bash
   # Remove markers AND ADR together:
   manage-refactor-markers remove --adr=042
   rm docs/adr/in_progress/042-payment.md
   git add -A
   git commit -m "chore: remove ADR-042 and all markers"
   ```

4. **Add pre-commit hook:**
   ```bash
   # .git/hooks/pre-commit
   # Check for orphaned markers before commit

   if detect-refactor-markers | grep -q "orphaned_markers"; then
     echo "Error: Orphaned markers detected"
     echo "Run: detect-refactor-markers"
     exit 1
   fi
   ```

---

## 3. Remediating Should-Be-Removed Markers 🔴

**Issue:** ADR complete but markers not removed

**Severity:** High

**Timeline:** Remove within 24 hours

### Step-by-Step Workflow

#### Step 1: Verify Completion

```bash
# Navigate to project root
cd ${PROJECT_ROOT}

# Check ADR location and status
find docs/adr -name "*028-*.md"
# Output: docs/adr/implemented/028-cache-layer.md
# Result: ADR in implemented/ (completed)

# Read ADR completion status
cat docs/adr/implemented/028-cache-layer.md | grep -A 10 "Status:"
# Output:
# Status: COMPLETE
# Completed: 2025-10-15
# Deployed: Production

# Verify acceptance criteria met
cat docs/adr/implemented/028-cache-layer.md | grep -A 20 "Acceptance Criteria"
# All criteria should be marked complete: [x]
```

#### Step 2: Find All Markers

```bash
# Find all ADR-028 markers
grep -rn "ADR-028" src/ --include="*.py"
# Output:
# src/application/cache_service.py:1:# REFACTOR: ADR-028 - Cache Layer
# src/application/cache_service.py:6:# REFACTOR(ADR-028): Add caching
# src/queries/cache_query.py:1:# REFACTOR: ADR-028 - Cache Layer
# src/queries/cache_query.py:8:# REFACTOR(ADR-028): Cache lookup

# Count markers
grep -r "ADR-028" src/ | wc -l
# Output: 4 markers across 2 files
```

#### Step 3: Dry-Run Removal

```bash
# Preview what will be removed (dry-run)
manage-refactor-markers remove --adr=028 --dry-run

# Output:
# DRY RUN - No changes will be made
#
# Would remove from src/application/cache_service.py:
#   Lines 1-4 (file-level marker):
#     1: # REFACTOR: ADR-028 - Cache Layer Implementation
#     2: # STATUS: IN_PROGRESS
#     3: # STARTED: 2025-10-01
#     4: # PERMANENT_RECORD: docs/adr/implemented/028-cache-layer.md
#   Line 6 (method marker):
#     6: # REFACTOR(ADR-028): Add caching
#
# Would remove from src/queries/cache_query.py:
#   Lines 1-4 (file-level marker)
#   Line 8 (method marker)
#
# Summary:
# - 2 files affected
# - 4 marker blocks removed (2 file-level, 2 method-level)
# - 8 total lines removed
#
# To execute, run without --dry-run flag

# Review output carefully
# Ensure only marker lines are removed (not actual code)
```

#### Step 4: Execute Removal

```bash
# Remove markers (no dry-run)
manage-refactor-markers remove --adr=028

# Output:
# Removing markers for ADR-028...
#
# ✅ src/application/cache_service.py: 2 markers removed
# ✅ src/queries/cache_query.py: 2 markers removed
#
# Summary:
# - Files modified: 2
# - Markers removed: 4
# - Lines removed: 8
#
# Success: All ADR-028 markers removed
```

#### Step 5: Verify Cleanup

```bash
# Ensure no markers remain
grep -r "ADR-028" src/
# Output: (should be empty)

# Check specific files
cat src/application/cache_service.py | head -n 10
# Should no longer have REFACTOR marker at top

# Run health check
detect-refactor-markers
# Should no longer report ADR-028

# Verify code still works (run tests)
uv run pytest tests/ -k cache
# All tests should pass
```

#### Step 6: Commit Removal

```bash
# Stage changes
git add src/application/cache_service.py src/queries/cache_query.py

# Review diff
git diff --staged
# Verify only marker lines removed

# Commit
git commit -m "chore: remove ADR-028 markers (refactor complete and deployed)"

# Push
git push origin main
```

### Alternative: Manual Removal

If `manage-refactor-markers` tool not available:

```bash
# Manually edit files to remove markers

# File 1: src/application/cache_service.py
# Remove lines 1-4 (file marker)
# Remove line 6 (method marker)

# File 2: src/queries/cache_query.py
# Remove lines 1-4 (file marker)
# Remove line 8 (method marker)

# Or use sed (careful!)
# Remove file-level markers (lines 1-4)
sed -i '' '1,4d' src/application/cache_service.py
sed -i '' '1,4d' src/queries/cache_query.py

# Remove method markers (manually find line numbers)
sed -i '' '/# REFACTOR(ADR-028)/d' src/application/cache_service.py
sed -i '' '/# REFACTOR(ADR-028)/d' src/queries/cache_query.py

# Verify
grep "ADR-028" src/
# (should be empty)
```

### Prevention

**Best practices:**

1. **Add marker removal to Definition of Done:**
   ```markdown
   # Feature/Refactor Definition of Done
   - [ ] Code complete
   - [ ] Tests passing
   - [ ] Documentation updated
   - [ ] ADR marked COMPLETE
   - [ ] ADR moved to implemented/
   - [ ] Refactor markers removed ← Critical!
   - [ ] Changes committed
   ```

2. **Feature completion checklist:**
   ```bash
   # Before marking feature complete:
   detect-refactor-markers
   # If should_be_removed found: Block completion
   ```

3. **Automate with CI/CD:**
   ```yaml
   # .github/workflows/check-markers.yml
   - name: Check for completed refactors
     run: |
       if detect-refactor-markers | grep -q "should_be_removed"; then
         echo "Error: Completed refactors have markers"
         exit 1
       fi
   ```

4. **@feature-completer integration:**
   - Auto-invokes detect-refactor-markers
   - Blocks completion if markers found
   - Provides removal command

---

## 4. Maintaining Healthy Markers ✅

**Issue:** None (markers are healthy)

**Action:** Monitor and maintain

### Ongoing Maintenance

#### Weekly Health Check

```bash
# Run health check every Monday
detect-refactor-markers

# Review output:
# - How many active refactors?
# - Any approaching staleness (20-25 days)?
# - All ADRs up to date?

# If healthy: No action needed
# If concerns: Proactively address
```

#### Monthly Review

```bash
# Review all in-progress ADRs
ls docs/adr/in_progress/*.md

# For each ADR:
# - Is progress on track?
# - Should timeline be updated?
# - Any blockers?

# Update ADRs with current status
```

#### Update ADR Progress

```bash
# Add status update to ADR
cat >> docs/adr/in_progress/027-service-result-migration.md <<EOF

## Progress Update - $(date +%Y-%m-%d)

**Completed This Week:**
- Migrated 5 more services to ServiceResult
- Added unit tests for new pattern
- Updated documentation

**Next Week:**
- Migrate remaining 3 services
- Run integration tests
- Code review

**On Track:** Yes
**Blockers:** None
**Expected Completion:** 2025-10-25
EOF

# Commit
git add docs/adr/in_progress/027-service-result-migration.md
git commit -m "docs: update ADR-027 progress (on track)"
```

### Best Practices

1. **Keep refactors small** (1-2 weeks)
2. **Update ADR weekly** (even if just "no change")
3. **Remove markers promptly** when complete
4. **Use health checks** proactively
5. **Integrate with workflows** (@statuser, @feature-completer)

---

## Summary: Quick Reference

| Issue | Severity | Timeline | Command |
|-------|----------|----------|---------|
| ⚠️ Stale | Medium-High | 7 days | Update ADR or complete/abandon |
| ❌ Orphaned | Critical | 24 hours | `manage-refactor-markers remove/update --adr=XXX` |
| 🔴 Should Remove | High | 24 hours | `manage-refactor-markers remove --adr=XXX` |
| ✅ Healthy | None | Ongoing | Monitor weekly |

---

## Troubleshooting

### Issue: manage-refactor-markers command not found

**Solution:**
```bash
# Check if skill exists
ls .claude/skills/manage-refactor-markers/

# If not: Create skill or use manual removal
sed -i '' '/# REFACTOR(ADR-XXX)/d' src/file.py
```

### Issue: Dry-run shows unexpected removals

**Solution:**
```bash
# Review dry-run output carefully
# If wrong lines targeted:
#   1. Don't execute
#   2. Check marker format
#   3. Remove manually with precision
```

### Issue: Tests fail after marker removal

**Solution:**
```bash
# Likely removed actual code, not just markers

# Restore from git
git checkout src/file.py

# Remove markers manually (carefully)
vim src/file.py  # Delete only marker comment lines

# Re-run tests
uv run pytest
```

### Issue: Can't decide if should continue or abandon

**Solution:**
```bash
# Consult with:
# 1. Developer assigned to refactor
# 2. Team lead (prioritization decision)
# 3. Product owner (if affects features)

# Consider:
# - Is blocker temporary or permanent?
# - Is refactor still valuable?
# - What's cost to complete vs abandon?

# Document decision in ADR regardless of outcome
```

---

**See also:**
- [health-categories-guide.md](./health-categories-guide.md) - Health classification details
- [examples.md](./examples.md) - Real-world scenarios
- [SKILL.md](./SKILL.md) - Main skill documentation
