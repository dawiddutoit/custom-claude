# Group 5 Action Items - Quick Reference

**Date:** 2026-01-22

## 🚨 Critical (Fix First)

### 1. validating-clickhouse-kafka-pipelines (4.0/10)
```bash
cd skills/validating-clickhouse-kafka-pipelines
```

**Actions:**
- [ ] Fix name in frontmatter: `clickhouse-kafka-validation` → `validating-clickhouse-kafka-pipelines`
- [ ] Add "When to Use This Skill" section
- [ ] Create missing files in references/:
  - clickhouse-schema.sql
  - producer-patterns.py
  - consumer-patterns.py
  - monitoring-queries.sql
- [ ] Create examples/examples.md
- [ ] Fix broken artifact links or move to references/

**Estimated Time:** 2-3 hours

### 2. util-resolve-serviceresult-errors (4.0/10)
```bash
cd skills/util-resolve-serviceresult-errors
```

**Actions:**
- [ ] Move 100 lines to references/ (currently 600 lines)
- [ ] Create missing scripts/:
  - find_serviceresult_chains.py
  - fix_serviceresult_mocks.py
  - validate_serviceresult_usage.py
  - README.md
  - EXAMPLES.md
  - SCRIPT_SUMMARY.md
  - examples.md
- [ ] Create missing templates/serviceresult-patterns.md
- [ ] Create missing references/monad-pattern.md
- [ ] Add "Utility Scripts" section in SKILL.md

**Estimated Time:** 3-4 hours

## ⚠️ High Priority (Fix Second)

### 3. test-setup-async (5.0/10)
**Actions:**
- [ ] Move 36 lines to references/
- [ ] Create missing scripts/: convert_to_async.py, generate_async_fixture.py, validate_async_tests.py
- [ ] Create templates/async-test-template.py
- [ ] Create references/: SCRIPTS-REFERENCE.md, QUICK-REFERENCE.md, IMPLEMENTATION-SUMMARY.md

**Estimated Time:** 2 hours

### 4. uv-ci-cd-integration (5.0/10)
**Actions:**
- [ ] Add "When to Use" section
- [ ] Create examples/: github-actions-complete.yml, dockerfile-development, gitlab-ci-complete.yml, pypi-publishing-workflow.yml
- [ ] Create references/: cache-optimization.md, docker-patterns.md, troubleshooting.md

**Estimated Time:** 2 hours

### 5. test-implement-constructor-validation (5.5/10)
**Actions:**
- [ ] Create scripts/: find_missing_validation.py, generate_constructor_tests.py, validate_constructor_tests.py
- [ ] Create templates/test-template.py
- [ ] Create references/reference.md

**Estimated Time:** 1.5 hours

### 6. test-organize-layers (5.5/10)
**Actions:**
- [ ] Create scripts/: analyze_test_pyramid.py, move_test.py, validate_test_placement.py, organize_tests.py
- [ ] Create references/reference.md

**Estimated Time:** 1.5 hours

### 7. test-implement-factory-fixtures (6.5/10)
**Actions:**
- [ ] Add "When to Use" section
- [ ] Move 58 lines to references/
- [ ] Create scripts/: convert_fixture_to_factory.py, generate_factory_fixture.py, validate_fixtures.py

**Estimated Time:** 1.5 hours

### 8. uv-project-migration (6.5/10)
**Actions:**
- [ ] Add "When to Use" section
- [ ] Update description to include CONTEXT (file types/technologies)
- [ ] Fix cross-references to other UV skills (add /SKILL.md suffix)

**Estimated Time:** 30 minutes

### 9. uv-troubleshooting (6.5/10)
**Actions:**
- [ ] Add "When to Use" section
- [ ] Update description to include CONTEXT
- [ ] Fix cross-references to other UV skills

**Estimated Time:** 30 minutes

## 📋 Bulk Fixes (Apply to Multiple Skills)

### Fix A: Add "When to Use" Sections (20 skills)
Skills missing usage guidance:
- All 7 Textual skills
- All 5 UV skills (except uv-tool-management)
- test-implement-factory-fixtures
- test-organize-layers
- textual-layout-styling
- textual-test-patterns
- util-research-library
- uv-ci-cd-integration
- web-artifacts-builder
- webapp-testing
- xlsx

**Template:**
```markdown
## When to Use This Skill

Use this skill when you need to:

- **[Primary use case]** - [Description]
- **[Secondary use case]** - [Description]
- **[Tertiary use case]** - [Description]

**Trigger Phrases:**
- "[Exact phrase user would say]"
- "[Another trigger phrase]"
- "[Third trigger phrase]"

**When NOT to use:**
- [Anti-pattern or exclusion]
```

**Estimated Time:** 10 min per skill = 3.5 hours total

### Fix B: Add Missing CONTEXT to Descriptions (10 skills)
Skills needing "Works with..." context:
- theme-factory
- util-multi-file-refactor
- util-research-library
- uv-dependency-management
- uv-project-migration
- uv-python-version-management
- uv-troubleshooting
- web-artifacts-builder
- work-with-adf
- xlsx

**Template:**
```yaml
description: |
  [Existing description]

  Works with [file types], [technologies], [frameworks].
```

**Estimated Time:** 5 min per skill = 50 minutes total

### Fix C: Add Trigger Phrases to Descriptions (5 skills)
Skills missing WHEN component:
- test-debug-failures (has section, but not in description)
- theme-factory
- util-tool-management
- web-artifacts-builder
- webapp-testing
- xlsx

**Template:**
```yaml
description: |
  [Existing content]

  Use when asked to "[trigger phrase]", "[another phrase]", or "[third phrase]".
```

**Estimated Time:** 5 min per skill = 25 minutes total

### Fix D: Fix Terraform Cross-References (5 skills)
Skills referencing non-existent `terraform` skill:
- terraform-gcp-integration
- terraform-module-design
- terraform-secrets-management
- terraform-state-management
- terraform-troubleshooting

**Find & Replace:**
```bash
# In each SKILL.md:
# Find:    [terraform skill](../terraform/SKILL.md)
# Replace: [terraform-basics](../terraform-basics/SKILL.md)
```

**Estimated Time:** 2 min per skill = 10 minutes total

### Fix E: Fix Textual Cross-References (10 skills)
All Textual skills reference other skills incorrectly:

**Find & Replace:**
```bash
# Find:    [textual-XXX](../textual-XXX)
# Replace: [textual-XXX](../textual-XXX/SKILL.md)
```

**Estimated Time:** 2 min per skill = 20 minutes total

### Fix F: Move Content to references/ (6 skills)
Skills exceeding 500 lines:

| Skill | Current | Target | To Move |
|-------|---------|--------|---------|
| test-property-based | 651 | 500 | 151 lines |
| util-resolve-serviceresult-errors | 600 | 500 | 100 lines |
| util-research-library | 589 | 500 | 89 lines |
| textual-layout-styling | 582 | 500 | 82 lines |
| test-implement-factory-fixtures | 558 | 500 | 58 lines |
| test-debug-failures | 556 | 500 | 56 lines |

**Strategy:**
1. Identify advanced/deep-dive sections
2. Move to references/advanced-topics.md or references/detailed-examples.md
3. Replace with cross-reference: "For detailed information, see [references/advanced-topics.md](./references/advanced-topics.md)"

**Estimated Time:** 20 min per skill = 2 hours total

### Fix G: Add Version Fields (All 41 skills)
**Find:**
```yaml
---
name: skill-name
description: |
  ...
---
```

**Replace:**
```yaml
---
name: skill-name
version: 1.0.0
description: |
  ...
---
```

**Estimated Time:** 1 min per skill = 40 minutes total

## 🎯 Priority Workflow

### Week 1: Critical Fixes (12 hours)
1. validating-clickhouse-kafka-pipelines (3h)
2. util-resolve-serviceresult-errors (4h)
3. test-setup-async (2h)
4. uv-ci-cd-integration (2h)
5. Fix A: Add "When to Use" sections to 10 highest priority skills (1h)

### Week 2: High Priority (8 hours)
6. test-implement-constructor-validation (1.5h)
7. test-organize-layers (1.5h)
8. test-implement-factory-fixtures (1.5h)
9. uv-project-migration (0.5h)
10. uv-troubleshooting (0.5h)
11. Fix A: Complete remaining "When to Use" sections (2.5h)

### Week 3: Polish (6 hours)
12. Fix B: Add CONTEXT to descriptions (1h)
13. Fix C: Add trigger phrases (0.5h)
14. Fix D: Terraform cross-references (0.2h)
15. Fix E: Textual cross-references (0.3h)
16. Fix F: Move excessive content (2h)
17. Fix G: Add version fields (0.7h)
18. Final validation run (1h)
19. Spot-check top 10 skills (0.3h)

## 📊 Success Metrics

**Target by End of Phase 3:**
- ✅ All skills scoring 8.5+/10
- ✅ Zero broken cross-references
- ✅ All skills have "When to Use" sections
- ✅ All descriptions have 4 components (WHAT, WHEN, TERMS, CONTEXT)
- ✅ All skills under 500 lines (progressive disclosure)
- ✅ All version fields added

**Current vs Target:**

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Average Score | 7.6/10 | 8.5/10 | +0.9 |
| Perfect Scores | 4 | 15+ | +11 |
| Needs Improvement | 9 | 0 | -9 |
| Broken References | 23 skills | 0 | -23 |
| Missing Usage | 20 skills | 0 | -20 |

## 🔧 Tools & Scripts

**Validation Script:**
```bash
python3 .claude/artifacts/2026-01-22/validation/validate_group5.py
```

**Quick Check Single Skill:**
```bash
# Check line count
wc -l skills/SKILL-NAME/SKILL.md

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('skills/SKILL-NAME/SKILL.md').read().split('---')[1])"

# Find broken links
grep -oP '\[([^\]]+)\]\(([^\)]+)\)' skills/SKILL-NAME/SKILL.md
```

**Bulk Operations:**
```bash
# Add version to all skills
for skill in skills/*/SKILL.md; do
  # Add version: 1.0.0 after name field
  sed -i '' '/^name:/a\
version: 1.0.0' "$skill"
done

# Fix terraform cross-references
for skill in skills/terraform-*/SKILL.md; do
  sed -i '' 's|\[terraform skill\](../terraform/SKILL.md)|[terraform-basics](../terraform-basics/SKILL.md)|g' "$skill"
done
```

## 📝 Notes

- Focus on critical fixes first (scores < 5)
- Bulk fixes provide maximum efficiency
- Version fields are optional but recommended
- All broken cross-references must be resolved
- "When to Use" sections critical for discoverability

**Total Estimated Effort:** 26 hours across 3 weeks
