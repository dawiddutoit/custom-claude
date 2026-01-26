# Skill Validation Parallel Execution Plan

**Date:** 2026-01-22
**Status:** 190 skills validated - 48 perfect (25.3%), 142 need fixes
**Average Score:** 8.5/10

## Validation Results Summary

```
Total Skills:        190
Perfect (10/10):     48 (25.3%)
Average Score:       8.5/10
Skills needing work: 142
```

## Issue Categories & Batch Groups

### Batch 1: Critical Issues (Score 6-7/10) - 25 skills
**Priority:** HIGH - Multiple violations, needs refactoring

Skills with 3+ issues requiring significant work:
- `create-adr-spike` (6/10) - Missing example, 521 lines, missing usage section
- `data-migration-versioning` (6/10) - Missing WHAT/CONTEXT, 889 lines
- `quality-detect-orphaned-code` (6/10) - Missing example, 761 lines
- `quality-reflective-questions` (6/10) - Disallowed XML, missing example
- `validating-clickhouse-kafka-pipelines` (6/10) - Name mismatch, missing WHAT/CONTEXT
- `build-jira-document-format` (7/10) - Disallowed XML, missing example
- `chrome-browser-automation` (7/10) - Disallowed XML, missing WHAT/CONTEXT
- `clickhouse-operations` (7/10) - Missing example, 1,052 lines (LONGEST)
- `design-jira-state-analyzer` (7/10) - Disallowed XML, missing example
- `editing-claude` (7/10) - Reserved word "claude", missing example
- `export-and-analyze-jira-data` (7/10) - Disallowed XML, missing example
- `java-best-practices-security-audit` (7/10) - Missing WHAT/CONTEXT, 1,015 lines
- `java-spring-service` (7/10) - Missing WHAT/CONTEXT, 916 lines
- `java-test-generator` (7/10) - Missing example, 776 lines
- `lotus-convert-rich-text-fields` (7/10) - Missing WHAT, 608 lines
- `openscad-collision-detection` (7/10) - Disallowed XML, missing example
- `openscad-cutlist-woodworkers` (7/10) - Disallowed XML, missing example
- `pytest-adapter-integration-testing` (7/10) - Missing WHAT/CONTEXT, 550 lines
- `pytest-domain-model-testing` (7/10) - Missing WHAT/CONTEXT, 586 lines
- `pytest-test-data-factories` (7/10) - Missing WHAT/CONTEXT, 564 lines
- `pytest-type-safety` (7/10) - Missing WHAT/CONTEXT, 561 lines
- `python-micrometer-business-metrics` (7/10) - Missing WHAT/CONTEXT

### Batch 2: Progressive Disclosure (Too Long) - 35 skills
**Priority:** MEDIUM - Need content moved to references/

Skills exceeding 500 lines (some already in Batch 1):
```
1,052 lines: clickhouse-operations
1,015 lines: java-best-practices-security-audit
  916 lines: java-spring-service
  889 lines: data-migration-versioning
  836 lines: observability-analyze-logs
  776 lines: java-test-generator
  761 lines: quality-detect-orphaned-code
  683 lines: otel-logging-patterns
  608 lines: lotus-convert-rich-text-fields
  586 lines: pytest-domain-model-testing
  564 lines: pytest-test-data-factories
  561 lines: pytest-type-safety
  550 lines: pytest-adapter-integration-testing
  521 lines: create-adr-spike
```

### Batch 3: Missing Example Blocks - 80+ skills
**Priority:** MEDIUM - Quick fix, high impact

Most common issue. Skills need `<example>` blocks added to descriptions.

### Batch 4: Missing WHAT Statements - 40+ skills
**Priority:** MEDIUM - Description needs action verbs

Add capability statements with action verbs (creates, manages, validates, etc.)

### Batch 5: XML Tag Issues - 15 skills
**Priority:** LOW - Usually just formatting

Skills with disallowed XML tags (not `<example>`):
- `quality-reflective-questions`
- `build-jira-document-format`
- `chrome-browser-automation`
- `design-jira-state-analyzer`
- `export-and-analyze-jira-data`
- `openscad-collision-detection`
- `openscad-cutlist-woodworkers`
- `playwright-responsive-screenshots`
- `scad-load`
- `terraform-basics`

### Batch 6: Special Cases - 2 skills
**Priority:** HIGH - Structural issues

- `validating-clickhouse-kafka-pipelines` - Directory name doesn't match YAML name
- `editing-claude` - Contains reserved word "claude"

## Parallel Execution Strategy

### Phase 1: Critical Issues (Use 5 agents in parallel)
```bash
# Agent 1: Fix score 6/10 skills (5 skills)
@skill-creator Fix validation issues for: create-adr-spike, data-migration-versioning, quality-detect-orphaned-code, quality-reflective-questions, validating-clickhouse-kafka-pipelines

# Agent 2: Fix large Java/Spring skills (4 skills)
@skill-creator Fix validation issues for: java-best-practices-security-audit, java-spring-service, java-test-generator

# Agent 3: Fix large pytest skills (4 skills)
@skill-creator Fix validation issues for: pytest-adapter-integration-testing, pytest-domain-model-testing, pytest-test-data-factories, pytest-type-safety

# Agent 4: Fix JIRA/browser automation skills (4 skills)
@skill-creator Fix validation issues for: build-jira-document-format, design-jira-state-analyzer, export-and-analyze-jira-data, chrome-browser-automation

# Agent 5: Fix OpenSCAD/misc skills (5 skills)
@skill-creator Fix validation issues for: openscad-collision-detection, openscad-cutlist-woodworkers, editing-claude, lotus-convert-rich-text-fields, clickhouse-operations
```

### Phase 2: Progressive Disclosure (Use 3 agents in parallel)
```bash
# Agent 6: Move content to references/ for largest files (5 skills)
@skill-creator Refactor skills for progressive disclosure: clickhouse-operations, java-best-practices-security-audit, java-spring-service, data-migration-versioning, observability-analyze-logs

# Agent 7: Move content to references/ for medium files (5 skills)
@skill-creator Refactor skills for progressive disclosure: java-test-generator, quality-detect-orphaned-code, otel-logging-patterns, lotus-convert-rich-text-fields, pytest-domain-model-testing

# Agent 8: Move content to references/ for 500-600 line files (5 skills)
@skill-creator Refactor skills for progressive disclosure: pytest-test-data-factories, pytest-type-safety, pytest-adapter-integration-testing, create-adr-spike
```

### Phase 3: Missing Examples (Use 4 agents in parallel)
```bash
# Divide 80+ skills into 4 groups of ~20 skills each
# Agent 9-12: Add example blocks to descriptions
```

### Phase 4: Polish & Validation
```bash
# Run validation again
python scripts/validate-skills-anthropic.py --all --skills-dir skills

# Fix any remaining issues
# Target: 90%+ skills at 10/10
```

## Task Instructions for Each Agent

### For Critical Issues (Agents 1-5):
```
Context: You are fixing skills that scored 6-7/10 on Anthropic best practices validation.

For each skill assigned to you:

1. **Read current state:**
   - Read skills/{skill-name}/SKILL.md
   - Note validation issues from the summary above

2. **Fix YAML frontmatter:**
   - Add/improve description with WHAT, WHEN, TERMS, CONTEXT
   - Ensure <example> blocks are present
   - Fix any XML tag issues (only <example> allowed)
   - Fix name mismatches or reserved words

3. **Fix progressive disclosure:**
   - If SKILL.md > 500 lines, move content to references/
   - Keep core content ~350-450 lines
   - Add "See references/{file}.md for details" links

4. **Add Usage section:**
   - If missing, add ## Usage or ## Instructions section
   - Include clear step-by-step guidance

5. **Validate:**
   - Run: python scripts/validate-skills-anthropic.py skills/{skill-name} -v
   - Ensure score is 9/10 or 10/10

Work on all assigned skills, then report completion summary.
```

### For Progressive Disclosure (Agents 6-8):
```
Context: You are refactoring skills that exceed 500 lines to follow progressive disclosure.

For each skill assigned to you:

1. **Read and analyze:**
   - Read skills/{skill-name}/SKILL.md
   - Identify sections that can move to references/

2. **Create references structure:**
   - Create skills/{skill-name}/references/ if needed
   - Move detailed content to appropriately named .md files:
     - detailed-guide.md (comprehensive how-to)
     - api-reference.md (API details)
     - patterns.md (design patterns)
     - troubleshooting.md (common issues)

3. **Update SKILL.md:**
   - Keep only essential content (~350-450 lines)
   - Add clear links: "See references/{file}.md for {topic}"
   - Ensure flow is logical even without references

4. **Validate:**
   - Run: python scripts/validate-skills-anthropic.py skills/{skill-name} -v
   - Line count should be <500 (ideally <450)
   - Score should be 9/10 or 10/10

Work on all assigned skills, then report completion summary.
```

### For Missing Examples (Agents 9-12):
```
Context: You are adding <example> blocks to skill descriptions.

For each skill assigned to you:

1. **Read skill:**
   - Read skills/{skill-name}/SKILL.md
   - Understand what the skill does

2. **Add example block:**
   - In YAML description, add realistic <example> block:
     ```
     <example>
     User: "trigger phrase that would invoke this skill"
     Assistant: [Invokes this skill to accomplish the task]
     </example>
     ```

3. **Ensure completeness:**
   - Verify description has WHAT (action verbs)
   - Verify description has WHEN (trigger phrases)
   - Example should show clear trigger phrase

4. **Validate:**
   - Run: python scripts/validate-skills-anthropic.py skills/{skill-name} -v
   - Score should improve to 9/10 or 10/10

Work on all assigned skills in batch, then report completion summary.
```

## Execution Template

Copy and paste this to spawn parallel agents:

```
I need to fix 142 skills that failed Anthropic validation. I'm going to spawn 5 skill-creator agents in parallel to work on the critical issues first.

**Context for all agents:**
- Validation tool: scripts/validate-skills-anthropic.py
- Target score: 9-10/10 (currently 8.5/10 average)
- Total skills: 190 (48 perfect, 142 need work)

**Agent 1:** Fix these 5 critical skills (score 6/10):
- create-adr-spike (missing example, 521 lines, missing usage)
- data-migration-versioning (missing WHAT/CONTEXT, 889 lines)
- quality-detect-orphaned-code (missing example, 761 lines)
- quality-reflective-questions (disallowed XML, missing example)
- validating-clickhouse-kafka-pipelines (name mismatch, missing WHAT/CONTEXT)

For each skill:
1. Read skills/{skill-name}/SKILL.md
2. Fix YAML frontmatter (add WHAT, WHEN, CONTEXT with <example>)
3. Move content >500 lines to references/
4. Add Usage section if missing
5. Fix any name mismatches or XML issues
6. Validate with: python scripts/validate-skills-anthropic.py skills/{skill-name} -v
7. Target: 9-10/10 score

**Agent 2:** Fix these 4 Java/Spring skills (score 7/10, very long):
- java-best-practices-security-audit (missing WHAT/CONTEXT, 1,015 lines)
- java-spring-service (missing WHAT/CONTEXT, 916 lines)
- java-test-generator (missing example, 776 lines)
- lotus-convert-rich-text-fields (missing WHAT, 608 lines)

Same instructions as Agent 1.

**Agent 3:** Fix these 4 pytest skills (score 7/10, 550-586 lines):
- pytest-adapter-integration-testing
- pytest-domain-model-testing
- pytest-test-data-factories
- pytest-type-safety

All missing WHAT/CONTEXT and exceed 500 lines. Same instructions as Agent 1.

**Agent 4:** Fix these 4 JIRA/automation skills (score 7/10, XML issues):
- build-jira-document-format (disallowed XML, missing example)
- design-jira-state-analyzer (disallowed XML, missing example)
- export-and-analyze-jira-data (disallowed XML, missing example)
- chrome-browser-automation (disallowed XML, missing WHAT/CONTEXT)

Same instructions as Agent 1.

**Agent 5:** Fix these 5 misc skills (score 7/10):
- openscad-collision-detection (disallowed XML, missing example)
- openscad-cutlist-woodworkers (disallowed XML, missing example)
- editing-claude (reserved word "claude", missing example)
- clickhouse-operations (missing example, 1,052 lines - LONGEST FILE)
- python-micrometer-business-metrics (missing WHAT/CONTEXT)

Same instructions as Agent 1. For editing-claude, rename to "editing-claude-config" or similar to avoid reserved word.

**Report back when complete with:**
- Skills fixed
- Before/after scores
- Any issues encountered
```

## Success Criteria

- **Phase 1 Complete:** All critical (6-7/10) skills at 9-10/10
- **Phase 2 Complete:** All skills <500 lines (target <450)
- **Phase 3 Complete:** All skills have example blocks
- **Final Target:** 90%+ skills at 10/10 (current: 25.3%)

## Notes

- Auto-fix script available: `scripts/auto-fix-skills.py` (fixes numbered headings, empty dirs)
- Run full validation between phases: `python scripts/validate-skills-anthropic.py --all --skills-dir skills`
- Estimated time: 2-3 hours with 5 parallel agents per phase
- Most issues are quick fixes - average score is already 8.5/10

## Validation Command Reference

```bash
# Validate single skill (verbose)
python scripts/validate-skills-anthropic.py skills/skill-name -v

# Validate all skills
python scripts/validate-skills-anthropic.py --all --skills-dir skills

# Auto-fix common issues (dry run)
python scripts/auto-fix-skills.py --dry-run skills/skill-name

# Auto-fix all skills (with backup)
python scripts/auto-fix-skills.py --all --skills-dir skills --backup
```
