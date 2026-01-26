# Action Checklist - Skill Validation Fixes

**Generated:** 2026-01-22
**Skills:** Group 1 (41 skills)
**Priority Order:** Critical → High → Medium → Low

---

## CRITICAL PRIORITY (Must Fix Immediately)

### 1. Fix YAML Syntax Error

- [ ] **agent-sdk-python** - YAML parsing error on line 8
  - **Issue:** Commas in description causing parse failure
  - **Fix:** Use pipe `|` for multi-line description, escape quotes
  - **Time:** 5 minutes

### 2. Fix Content Length Violations (>700 lines)

- [ ] **clickhouse-operations** (1,051 lines → 500 lines)
  - **Action:** Move 551 lines to references/
  - **Sections to move:** Detailed examples, troubleshooting, configuration
  - **Time:** 2 hours

- [ ] **data-migration-versioning** (887 lines → 500 lines)
  - **Action:** Move 387 lines to references/
  - **Sections to move:** Version strategies, migration examples
  - **Time:** 1.5 hours

- [ ] **build-jira-document-format** (746 lines → 500 lines)
  - **Action:** Move 246 lines to references/
  - **Sections to move:** ADF format details, complex examples
  - **Time:** 1 hour

- [ ] **export-and-analyze-jira-data** (681 lines → 500 lines)
  - **Action:** Move 181 lines to references/
  - **Sections to move:** Analysis patterns, complex queries
  - **Time:** 1 hour

### 3. Fix Major Broken Cross-References

- [ ] **create-adr-spike** (10 broken links)
  - Create missing: references/examples.md
  - Fix or remove: ../../../docs/ links (outside skill directory)
  - **Time:** 30 minutes

- [ ] **editing-claude** (6 broken links)
  - Create missing: scripts/examples.md
  - Fix: ~/.claude/CLAUDE.md reference (external)
  - **Time:** 20 minutes

- [ ] **data-migration-versioning** (4 broken links)
  - Create missing: references/version-strategies.md, examples/yaml-migration.md, templates/load-save-template.py
  - **Time:** 30 minutes

---

## HIGH PRIORITY (Fix This Week)

### 4. Add Missing Usage Sections (18 skills)

Template to use:
```markdown
## When to Use This Skill

**Explicit Triggers:**
- "trigger phrase 1"
- "trigger phrase 2"
- "trigger phrase 3"

**Implicit Triggers:**
- Scenario 1
- Scenario 2

**Debugging Scenarios:**
- Error condition 1
- Problem state 2
```

Skills needing usage sections:
- [ ] **build-jira-document-format** (3.0/10)
- [ ] **create-adr-spike** (3.5/10)
- [ ] **design-jira-state-analyzer** (3.5/10)
- [ ] **export-and-analyze-jira-data** (3.5/10)
- [ ] **clickhouse-operations** (4.0/10)
- [ ] **clickhouse-materialized-views** (5.0/10)
- [ ] **brand-guidelines** (5.0/10)
- [ ] **canvas-design** (5.0/10)
- [ ] **doc-coauthoring** (5.0/10)
- [ ] **docx** (5.0/10)
- [ ] **frontend-design** (5.0/10)
- [ ] **clickhouse-query-optimization** (5.5/10)
- [ ] **algorithmic-art** (6.0/10)
- [ ] **browser-layout-editor** (6.0/10)
- [ ] **chrome-gif-recorder** (6.0/10)

**Time per skill:** 15 minutes
**Total time:** ~4 hours

### 5. Enhance Descriptions - Add CONTEXT Component (28 skills)

Template addition:
```yaml
description: |
  [Existing text...]

  Works with [file types: .py, .js, .ts] / [technologies: Python, React, etc.]
```

Skills needing CONTEXT:
- [ ] build-jira-document-format (3.0/10)
- [ ] create-adr-spike (3.5/10)
- [ ] design-jira-state-analyzer (3.5/10)
- [ ] export-and-analyze-jira-data (3.5/10)
- [ ] clickhouse-operations (4.0/10)
- [ ] gcp-gke-cluster-setup (4.5/10)
- [ ] clickhouse-materialized-views (5.0/10)
- [ ] cloudflare-dns-operations (5.0/10)
- [ ] doc-coauthoring (5.0/10)
- [ ] gcp-gke-cost-optimization (5.5/10)
- [ ] gcp-gke-deployment-strategies (5.5/10)
- [ ] gcp-gke-monitoring-observability (5.5/10)
- [ ] gcp-gke-troubleshooting (5.5/10)
- [ ] architecture-single-responsibility-principle (6.0/10)
- [ ] architecture-validate-architecture (6.0/10)
- [ ] architecture-validate-layer-boundaries (6.0/10)
- [ ] And 12 more...

**Time per skill:** 10 minutes
**Total time:** ~5 hours

### 6. Fix Remaining Broken Cross-References (6 skills)

- [ ] **build-jira-document-format** (3 broken links)
  - Fix: /skills/ absolute paths to relative ../
  - **Time:** 10 minutes

- [ ] **design-jira-state-analyzer** (3 broken links)
  - Fix: /skills/ absolute paths to relative ../
  - **Time:** 10 minutes

- [ ] **export-and-analyze-jira-data** (3 broken links)
  - Fix: /skills/ absolute paths to relative ../
  - **Time:** 10 minutes

- [ ] **gcp-gke-cluster-setup** (3 broken links)
  - Fix: ../gke-* paths to ../gcp-gke-*
  - **Time:** 10 minutes

---

## MEDIUM PRIORITY (Fix Next Week)

### 7. Document allowed-tools Justification (12 skills)

Add justification to description or body:
```markdown
## Tool Access Restrictions

This skill uses `allowed-tools` to restrict access to read-only operations because:
- [Reason 1: e.g., validation skill should not modify code]
- [Reason 2: e.g., security/safety considerations]
```

Skills needing justification:
- [ ] gcp-gke-cluster-setup (4.5/10)
- [ ] cloudflare-dns-operations (5.0/10)
- [ ] clickhouse-query-optimization (5.5/10)
- [ ] gcp-gke-cost-optimization (5.5/10)
- [ ] gcp-gke-deployment-strategies (5.5/10)
- [ ] gcp-gke-monitoring-observability (5.5/10)
- [ ] gcp-gke-troubleshooting (5.5/10)
- [ ] artifacts-creating-and-managing (6.5/10)
- [ ] caddy-certificate-maintenance (6.5/10)
- [ ] caddy-https-troubleshoot (6.5/10)
- [ ] cloudflare-access-setup (6.5/10)
- [ ] cloudflare-access-troubleshoot (6.5/10)

**Alternative:** If tools aren't actually restricted in practice, remove allowed-tools.

**Time per skill:** 15 minutes
**Total time:** ~3 hours

### 8. Reduce Moderate Content Length (5 skills)

- [ ] **architecture-validate-srp** (676 lines → 500 lines)
  - Move 176 lines to references/
  - **Time:** 1 hour

- [ ] **chrome-browser-automation** (584 lines → 500 lines)
  - Move 84 lines to references/
  - **Time:** 30 minutes

- [ ] **cloudflare-dns-operations** (529 lines → 500 lines)
  - Move 29 lines to references/
  - **Time:** 20 minutes

- [ ] **design-jira-state-analyzer** (524 lines → 500 lines)
  - Move 24 lines to references/
  - **Time:** 20 minutes

- [ ] **create-adr-spike** (520 lines → 500 lines)
  - Move 20 lines to references/
  - **Time:** 15 minutes

---

## LOW PRIORITY (Optimization)

### 9. Add Missing WHEN Component (9 skills)

These skills have CONTEXT but missing trigger phrases:

- [ ] brand-guidelines (5.0/10)
- [ ] canvas-design (5.0/10)
- [ ] docx (5.0/10)
- [ ] frontend-design (5.0/10)

**Time per skill:** 10 minutes
**Total time:** ~1.5 hours

### 10. Standardize Section Ordering

Create consistent structure across all skills:
1. YAML frontmatter
2. Title
3. Purpose/Overview
4. Quick Start
5. When to Use This Skill
6. Instructions
7. Examples
8. Supporting Files
9. Integration Points
10. Requirements
11. Troubleshooting
12. Red Flags

**Time:** Ongoing, apply to new/updated skills

---

## Time Estimates Summary

| Priority | Tasks | Total Time |
|----------|-------|------------|
| Critical | 3 areas, 16 items | ~8 hours |
| High | 3 areas, 52 items | ~9 hours |
| Medium | 2 areas, 17 items | ~6 hours |
| Low | 2 areas | ~2 hours |
| **Total** | | **~25 hours** |

## Weekly Sprint Plan

### Week 1: Critical Issues
**Goal:** Fix all broken functionality

- Day 1: Fix YAML syntax (1 skill)
- Day 2-3: Reduce content length (4 skills)
- Day 4: Fix major broken cross-references (3 skills)
- Day 5: Validation and testing

### Week 2: High Priority - Usage Sections
**Goal:** Improve discoverability

- Day 1-3: Add usage sections (18 skills, 6 per day)
- Day 4: Enhance descriptions with CONTEXT (start batch)
- Day 5: Continue descriptions, fix remaining broken links

### Week 3: High Priority - Descriptions
**Goal:** Complete descriptions

- Day 1-4: Complete CONTEXT additions (28 skills, 7 per day)
- Day 5: Validation and testing

### Week 4: Medium Priority
**Goal:** Polish and optimize

- Day 1-2: Document allowed-tools justification (12 skills)
- Day 3-4: Reduce moderate content length (5 skills)
- Day 5: Final validation

## Validation After Fixes

Run validation script to verify improvements:

```bash
python3 .claude/artifacts/2026-01-22/validation/validate_skills.py
```

**Target Metrics:**
- Average score: 5.6 → 8.0 (43% improvement)
- Perfect scores: 0% → 25%
- Needs work: 90% → 25%

## Quick Wins (Do First for Immediate Impact)

These 5 actions will have the biggest impact:

1. ✅ **Fix YAML syntax in agent-sdk-python** (5 min)
   - Unblocks skill functionality

2. ✅ **Add usage sections to critical skills** (1 hour)
   - build-jira-document-format, create-adr-spike, design-jira-state-analyzer, export-and-analyze-jira-data
   - Immediate discoverability improvement

3. ✅ **Fix create-adr-spike broken links** (30 min)
   - 10 broken links → 0
   - Highest link-break density

4. ✅ **Reduce clickhouse-operations content** (2 hours)
   - 1,051 lines → 500 lines
   - Largest progressive disclosure violation

5. ✅ **Add CONTEXT to top 10 incomplete descriptions** (2 hours)
   - Most impactful for autonomous invocation

**Total Quick Wins Time:** ~6 hours
**Impact:** Average score 5.6 → 6.5 (16% improvement)

---

## Notes

- **Automation:** After manual fixes, create pre-commit hook using validation script
- **Templates:** Document patterns from top performers (caddy-subdomain-add, chrome-form-filler)
- **Prevention:** Update skill creation documentation with validation criteria
- **Continuous:** Run validation on all PRs touching skills/

---

**Generated by:** validate_skills.py
**Detailed Report:** group-1-report.md
**Summary:** group-1-summary.md
