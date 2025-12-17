---
name: artifacts-creating-and-managing
description: |
  Creates and manages project artifacts (research, spikes, analysis, plans) using templated scripts.
  Use when asked to "create an ADR", "research topic", "spike investigation", "implementation plan", or "create analysis".
  Provides standardized structure, naming conventions, and helper scripts for artifact organization.
allowed-tools: Read, Write, Bash, Glob, Edit
---

# Artifacts: Creating and Managing

## Quick Start

**Create an ADR:**
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_adr.py \
  --title "Use Event Sourcing" \
  --status proposed \
  --context "Need audit trail for compliance"
```

**Create a Research Topic:**
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_research_topic.py \
  --topic "GraphQL vs REST" \
  --objective "Choose API architecture" \
  --questions "Performance?" "Tooling?"
```

**Create an Implementation Plan:**
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_implementation_plan.py \
  --feature "User Auth" \
  --overview "Add OAuth2 support" \
  --steps "Configure provider" "Implement tokens" "Add tests"
```

**Customize templates:** Edit files in `templates/` folder.

---

## Table of Contents

1. [Purpose](#purpose)
2. [Directory Structure](#directory-structure)
3. [File Naming Conventions](#file-naming-conventions)
4. [Core Rules](#core-rules)
5. [Category Definitions](#category-definitions)
6. [When to Use Artifacts](#when-to-use-artifacts)
7. [Integration Pattern](#integration-pattern)
8. [Examples](#examples)
9. [Helper Scripts](#helper-scripts)
10. [Reference](#reference)

## Purpose

This skill standardizes how artifacts are created and organized within the `.claude/artifacts/` directory. Artifacts are temporary work products that support the development process but don't belong in version control or permanent documentation.

By following these conventions, all skills and agents create consistent, discoverable, and maintainable work products.

## Directory Structure

```
.claude/artifacts/
└── YYYY-MM-DD/                          # Date-based root (today's date)
    ├── analysis/                        # Research, spikes, investigations
    │   ├── SINGLE_TOPIC_RESEARCH.md     # For single-file topics
    │   └── multi-topic/                 # Subfolder when multiple files needed
    │       ├── PART_ONE.md
    │       └── PART_TWO.md
    │
    ├── reports/                         # Generated reports, health checks
    │   ├── SINGLE_REPORT.md             # For single-file reports
    │   └── multi-file-report/           # Subfolder when multiple files needed
    │       ├── SUMMARY.md
    │       └── DETAILS.md
    │
    ├── sessions/                        # Session logs, transcripts
    │   ├── SESSION_TRANSCRIPT.md        # Raw session output
    │   └── analysis/
    │       └── SESSION_ANALYSIS.md      # Analysis of session
    │
    └── todos/                           # Temporary session-specific tasks
        ├── CURRENT_WORK.md              # Single task list
        └── complex-project/             # Subfolder for related work
            ├── SPRINT_TASKS.md
            └── BACKLOG.md
```

### Key Structural Rules

1. **Date folders are mandatory**: All artifacts live under date-based folders (`YYYY-MM-DD`)
2. **Use today's date**: The date folder should be the current date when the artifact is created
3. **Single file** for a topic: Place directly in category folder (e.g., `analysis/RESEARCH_SUMMARY.md`)
4. **Multiple files** for same topic: Create a subfolder and place files inside
5. **Subfolder naming**: Use lowercase kebab-case (e.g., `langgraph-research/`, `auth-investigation/`)

## File Naming Conventions

### Markdown Files

Use **SCREAMING_SNAKE_CASE** for all markdown files:

```
RESEARCH_SUMMARY.md          ✅ Correct
Research_Summary.md          ❌ Wrong (mixed case)
research-summary.md          ❌ Wrong (kebab-case)
research_summary.md          ❌ Wrong (snake_case)
RESEARCH SUMMARY.md          ❌ Wrong (spaces)
```

### Subfolder Names

Use **lowercase kebab-case** for topic subfolders:

```
langgraph-research/          ✅ Correct
LanggraphResearch/           ❌ Wrong (PascalCase)
langgraph_research/          ❌ Wrong (snake_case)
LANGGRAPH_RESEARCH/          ❌ Wrong (SCREAMING_SNAKE_CASE)
langgraph research/          ❌ Wrong (spaces)
```

### Date Format

Use **ISO 8601 format** for date folders:

```
2025-11-26/                  ✅ Correct (YYYY-MM-DD)
25-11-26/                    ❌ Wrong (YY-MM-DD)
2025/11/26/                  ❌ Wrong (nested folders)
11-26-2025/                  ❌ Wrong (MM-DD-YYYY)
```

### File Organization Within Subfolders

When using a topic subfolder, organize related files clearly:

```
analysis/langgraph-research/
├── RESEARCH_SUMMARY.md       # Overview of findings
├── IMPLEMENTATION_NOTES.md   # Technical details
└── COMPARISON_WITH_LLAMA.md  # Alternative analysis
```

## Artifact Minimalism Summary

This is the core principle: **If it fits in one file, use one file. Humans cannot read 10 documents about the same thing.**

| Category | Default Files | Max Files | Consolidate Into |
|----------|---|---|---|
| `analysis/` | 1 (RESEARCH_SUMMARY.md) | 3 | Single primary file; only split if >60 lines AND distinct parts |
| `reports/` | 1 (HEALTH_CHECK_REPORT.md) | 2 | SUMMARY + DETAILS only; consolidate analysis into single file |
| `sessions/` | 1 (SESSION_TRANSCRIPT.md) | 2 | Transcript + 1 analysis file; put learning/outcomes in analysis |
| `todos/` | 1 (CURRENT_WORK.md) | 3 | Single file for single task; 2-3 phases only for multi-month |

**Anti-Pattern (Document Sprawl):**
```
❌ 5+ separate files for one topic
❌ RESEARCH.md + ANALYSIS.md + FINDINGS.md + RECOMMENDATIONS.md + NEXT_STEPS.md
❌ PART_ONE.md + PART_TWO.md + PART_THREE.md + PART_FOUR.md (in analysis/)
❌ Separate files for each metric/result
```

**Pattern (Consolidated):**
```
✅ 1-2 files per topic
✅ RESEARCH_SUMMARY.md contains: research + analysis + findings + recommendations
✅ Single SESSION_ANALYSIS.md contains: summary + outcomes + learning + next steps
✅ Single HEALTH_CHECK_REPORT.md contains: all metrics + analysis + recommendations
```

---

## Core Rules

### Rule 1: Date Folders Are Mandatory

Every artifact must live under a date folder matching the creation date:

```
✅ CORRECT
.claude/artifacts/2025-11-26/analysis/RESEARCH.md

❌ WRONG
.claude/artifacts/analysis/RESEARCH.md
.claude/artifacts/RESEARCH.md
```

### Rule 2: Single vs. Multiple Files

**Single file for a topic?** Place directly in the category:

```
.claude/artifacts/2025-11-26/
├── analysis/
│   └── LANGFUSE_SPIKE.md          # Only file on this topic
```

**Multiple files for same topic?** Create a subfolder:

```
.claude/artifacts/2025-11-26/
├── analysis/
│   └── langfuse-spike/            # Multiple files on this topic
│       ├── RESEARCH_SUMMARY.md
│       ├── COST_ANALYSIS.md
│       └── IMPLEMENTATION_PLAN.md
```

### Rule 3: Naming Consistency

All files in an artifact set should use consistent naming:

```
✅ CORRECT - Consistent naming
langgraph-spike/
├── RESEARCH_SUMMARY.md
├── PROOF_OF_CONCEPT.md
├── TRADEOFFS_ANALYSIS.md

❌ WRONG - Inconsistent naming
langgraph-spike/
├── research-summary.md           # kebab-case
├── POC_Implementation.md         # Mixed case
├── tradeoffs_analysis.md         # snake_case
```

### Rule 4: Avoid Nested Subfolders

Keep directory structure flat - no more than one subfolder level deep:

```
✅ CORRECT
.claude/artifacts/2025-11-26/
├── analysis/
│   └── langgraph-research/
│       └── RESEARCH_SUMMARY.md

❌ WRONG - Too deeply nested
.claude/artifacts/2025-11-26/
├── analysis/
│   └── langgraph/
│       └── research/
│           └── RESEARCH_SUMMARY.md
```

### Rule 5: Prevent Document Sprawl (CRITICAL)

**The Core Anti-Pattern: One topic with 5+ separate files**

DO NOT create multiple files as a substitute for good document organization:

```
❌ WRONG - Document sprawl for single topic
analysis/langfuse-evaluation/
├── RESEARCH.md                    # Research findings
├── ANALYSIS.md                    # Analysis of research
├── FINDINGS.md                    # Summary of findings
├── RECOMMENDATIONS.md             # What we should do
├── IMPLEMENTATION_PLAN.md         # How to implement
├── COST_ANALYSIS.md               # Cost breakdown
├── TIMELINE.md                    # Timeline estimate
└── RISKS.md                       # Risk analysis

✅ CORRECT - Consolidated single file
analysis/
└── LANGFUSE_EVALUATION.md         # Contains: research + analysis + findings + recommendations + implementation + costs + timeline + risks
```

**The Rule:** A topic gets ONE or TWO files maximum. Use sections within the file for organization.

**When to split (the ONLY justification for 2-3 files):**
1. Document exceeds 100+ lines AND
2. Different audience contexts (e.g., technical deep-dive vs executive summary) AND
3. Clear, distinct sections that don't belong together

**When NOT to split (most cases - consolidate into one):**
- Different types of content for same topic → Use sections in one file
- Sequential analysis steps → All in one file with headers
- Related findings and recommendations → All in one file
- Any topic <60 lines → Definitely one file

## Category Definitions

### `analysis/` - Research and Investigation

Use for research documents, spikes, investigations, and ADR research output.

**File Count Rule:**
- **Single-topic research**: 1 file (e.g., `LANGFUSE_SPIKE.md`)
- **Multi-topic research**: 2-3 files maximum (create subfolder)
- **Consolidation required**: Never create RESEARCH.md, ANALYSIS.md, RESEARCH_SUMMARY.md, and IMPLEMENTATION_PLAN.md for same topic

**Typical Files (pick 1-2 per topic):**
- `RESEARCH_SUMMARY.md` - Overview of findings (primary, contains research + analysis)
- `SPIKE_REPORT.md` - Spike investigation results (alternative to above)
- `PROOF_OF_CONCEPT.md` - POC implementation notes (only if significant findings warrant separate file)
- **DO NOT** create separate: TRADEOFFS_ANALYSIS.md, IMPLEMENTATION_NOTES.md (put in RESEARCH_SUMMARY.md)

**Example Structure (CORRECT):**
```
.claude/artifacts/2025-11-26/analysis/
├── LANGFUSE_SPIKE.md              # Single-file: research + findings + recommendation
└── cqrs-architecture/              # Multi-file ONLY if >60 lines + multiple distinct parts
    ├── RESEARCH_SUMMARY.md         # Contains: research + analysis + tradeoffs
    └── PROOF_OF_CONCEPT.md         # Only if separate POC has significant findings
```

**Example Structure (WRONG - TOO MANY FILES):**
```
❌ cqrs-architecture/
   ├── RESEARCH_SUMMARY.md
   ├── PATTERN_COMPARISON.md        # Consolidate into RESEARCH_SUMMARY.md
   ├── TRADEOFFS_ANALYSIS.md        # Put in RESEARCH_SUMMARY.md
   ├── IMPLEMENTATION_PLAN.md       # Put in RESEARCH_SUMMARY.md
   └── IMPLEMENTATION_NOTES.md      # Put in RESEARCH_SUMMARY.md
```

### `reports/` - Generated Reports

Use for health reports, analysis outputs, quality gate results, and status reports.

**File Count Rule:**
- **Single-topic report**: 1 file (e.g., `WEEKLY_HEALTH_CHECK.md`)
- **Multi-part report**: 2 files maximum (SUMMARY + DETAILS only)
- **Consolidation required**: Never create 5+ separate files for one topic

**Typical Files (pick 1-2 per topic):**
- `QUALITY_GATE_REPORT.md` - Complete report (coverage + linting + types)
- `HEALTH_CHECK_REPORT.md` - Complete report (status + metrics + recommendations)
- `ANALYSIS_REPORT.md` - Investigation output (findings + conclusions)
- **Multi-file only when**: SUMMARY.md + DETAILS.md (justified by >100 lines and distinct audiences)
- **DO NOT** create: COVERAGE_ANALYSIS.md, LINTING_RESULTS.md, METRICS_SUMMARY.md, RECOMMENDATIONS.md (all go in main report)

**Example Structure (CORRECT):**
```
.claude/artifacts/2025-11-26/reports/
├── WEEKLY_HEALTH_CHECK.md         # Single-file: status + metrics + recommendations
└── project-quality/                # Multi-file ONLY if >100 lines + different reader contexts
    ├── SUMMARY.md                  # Executive summary
    └── DETAILS.md                  # Technical deep-dive (or use appendix in SUMMARY.md)
```

**Example Structure (WRONG - TOO MANY FILES):**
```
❌ project-quality/
   ├── SUMMARY.md
   ├── COVERAGE_ANALYSIS.md         # Consolidate into SUMMARY.md
   ├── LINTING_RESULTS.md           # Consolidate into SUMMARY.md
   ├── TYPE_CHECK_RESULTS.md        # Consolidate into SUMMARY.md
   └── RECOMMENDATIONS.md           # Consolidate into SUMMARY.md
```

### `sessions/` - Session Logs and Transcripts

Use for session logs, transcripts, and session-specific analysis.

**File Count Rule:**
- **Transcript only**: 1 file (`SESSION_TRANSCRIPT.md`)
- **With analysis**: 2 files (TRANSCRIPT + analysis/SESSION_ANALYSIS.md)
- **Maximum**: 2 files per session (transcript + ONE analysis file)

**Typical Files (pick appropriate subset):**
- `SESSION_TRANSCRIPT.md` - Raw session output (single file, required)
- `analysis/SESSION_ANALYSIS.md` - Summary of work completed (optional, only 1)
- **DO NOT** create: LEARNING_CONSOLIDATION.md, OUTCOMES.md, NEXT_STEPS.md (all go in SESSION_ANALYSIS.md)
- **DO NOT** create: analysis/PART_ONE.md, analysis/PART_TWO.md (one analysis file per session)

**Example Structure (CORRECT):**
```
.claude/artifacts/2025-11-26/sessions/
├── SESSION_TRANSCRIPT.md           # Raw output from session
└── analysis/
    └── SESSION_ANALYSIS.md         # Summary + outcomes + learning (1 file only)
```

**Example Structure (WRONG - TOO MANY FILES):**
```
❌ analysis/
   ├── SESSION_ANALYSIS.md
   ├── LEARNING_CONSOLIDATION.md    # Consolidate into SESSION_ANALYSIS.md
   ├── OUTCOMES_SUMMARY.md          # Consolidate into SESSION_ANALYSIS.md
   └── NEXT_STEPS.md                # Consolidate into SESSION_ANALYSIS.md
```

### `todos/` - Temporary Task Lists

Use for temporary, session-specific task lists and work tracking. Unlike permanent todos (./todo.md), these are part of artifacts and can be archived.

**File Count Rule:**
- **Single task list**: 1 file (e.g., `CURRENT_WORK.md`)
- **Multi-phase project**: 2-3 files maximum (phases only, no sub-phases)
- **Consolidation required**: Never create PHASE_ONE.md, PHASE_TWO.md, PHASE_THREE.md, BACKLOG.md (2-3 files max)

**Typical Files (pick appropriate subset):**
- `CURRENT_WORK.md` - Session work plan (primary, all-in-one)
- `SPRINT_TASKS.md` - Sprint planning (alternative, if dedicated)
- **Multi-file only for**: Major multi-phase projects, e.g., `PHASE_ONE.md` + `PHASE_TWO.md` (keep backlog in one of them or CURRENT_WORK.md)
- **DO NOT** create: BACKLOG.md separately (append to PHASE_TWO.md or CURRENT_WORK.md)

**Example Structure (CORRECT):**
```
.claude/artifacts/2025-11-26/todos/
├── CURRENT_WORK.md                # Single task list (phases + backlog)
└── feature-development/            # Multi-file ONLY for multi-month effort
    ├── PHASE_ONE.md               # Phase 1 tasks + notes
    └── PHASE_TWO.md               # Phase 2 tasks + notes + backlog
```

**Example Structure (WRONG - TOO MANY FILES):**
```
❌ feature-development/
   ├── PHASE_ONE.md
   ├── PHASE_TWO.md
   ├── PHASE_THREE.md              # Consolidate into PHASE_TWO.md
   └── BACKLOG.md                  # Consolidate into PHASE_TWO.md or CURRENT_WORK.md
```

## When to Use Artifacts

### Use Artifacts For

✅ **Research output** that doesn't belong in version control:
```
.claude/artifacts/2025-11-26/analysis/
└── FRAMEWORK_EVALUATION.md  # Spike comparing React, Vue, Svelte
```

✅ **Temporary analysis documents** for a specific task:
```
.claude/artifacts/2025-11-26/reports/
└── DEBUGGING_SESSION.md     # Notes from debugging investigation
```

✅ **Session-specific work products**:
```
.claude/artifacts/2025-11-26/sessions/
├── SESSION_TRANSCRIPT.md
└── analysis/
    └── LEARNING_CONSOLIDATION.md
```

✅ **Investigation notes** that are ephemeral:
```
.claude/artifacts/2025-11-26/analysis/
└── bug-investigation/
    ├── ISSUE_SUMMARY.md
    ├── ROOT_CAUSE_ANALYSIS.md
    └── PROPOSED_FIX.md
```

### Do NOT Use Artifacts For

❌ **Permanent documentation**:
- Use `docs/` instead
- Example: Framework setup guides, user manuals

❌ **Architecture Decision Records (ADRs)**:
- Use `docs/adr/` instead with CONSOLIDATED structure
- For `not_started/`: Only ADR.md (contains research + analysis + decision)
- For `in_progress/`: ADR.md + IMPLEMENTATION_PLAN.md only
- **NEVER** create separate RESEARCH.md, ANALYSIS.md, EXECUTIVE_SUMMARY.md, or IMPLEMENTATION_NOTES.md
- Put ALL research directly in ADR.md sections, not in `.claude/artifacts/`

❌ **Configuration files**:
- Use project root or `.claude/` directory
- Example: `pyproject.toml`, `.env`, `.claude/settings.json`

❌ **Persistent task lists**:
- Use `.claude/todos/` or `.claude/artifacts/YYYY-MM-DD/todos/` for ongoing work
- Never check in permanent task tracking to `docs/`

❌ **Code or test files**:
- Keep in `src/` and `tests/` directories
- Artifacts are for documentation only

## Integration Pattern

### Skills That Create Artifacts

Several skills create artifacts as part of their workflow:

#### 1. **create-adr-spike** - Architecture Decision Records

Creates consolidated ADR documents in `docs/adr/`:
```
docs/adr/not_started/028-microservices-architecture/
└── ADR.md          # Contains: Research + Analysis + Decision + Alternatives

docs/adr/in_progress/028-microservices-architecture/
├── ADR.md          # Decision (research + analysis + recommendation)
└── IMPLEMENTATION_PLAN.md  # How to build it (phases, tasks, notes)
```

**Integration:**
- Creates properly numbered ADRs in correct status directory
- Consolidates research, analysis, and decision into **single ADR.md file**
- Does NOT create separate RESEARCH.md, ANALYSIS.md, EXECUTIVE_SUMMARY.md, or IMPLEMENTATION_NOTES.md
- All research goes directly into ADR.md "Research" and "Analysis" sections
- Does NOT put research in `.claude/artifacts/` (artifacts are only for non-ADR research)

#### 2. **observability-analyze-logs** - Log Analysis

Creates analysis output in `analysis/` or `reports/`:
```
.claude/artifacts/2025-11-26/reports/
└── error-trace-analysis/
    ├── TRACE_SUMMARY.md           # Overview of errors found
    ├── ROOT_CAUSE_ANALYSIS.md     # Detailed analysis
    └── RECOMMENDED_FIXES.md       # Action items
```

**Integration:**
- Processes logs and creates findings
- Saves analysis to `reports/` category
- Links back to source logs in findings

#### 3. **editing-claude** - Session Analysis

Creates session output in `sessions/`:
```
.claude/artifacts/2025-11-26/sessions/
├── SESSION_TRANSCRIPT.md
└── analysis/
    └── SESSION_ANALYSIS.md        # Summary of session work
```

**Integration:**
- Captures session transcript
- Creates structured analysis
- Stores in sessions category with analysis subfolder

#### 4. **check-progress-status** - Health Reports

Creates reports in `reports/`:
```
.claude/artifacts/2025-11-26/reports/
└── WEEKLY_HEALTH_CHECK.md
```

**Integration:**
- Generates quality metrics
- Creates date-stamped report
- Stored in reports category

### How to Reference Artifacts in Skills

When creating a skill that generates artifacts, document the artifact pattern:

```markdown
### Artifact Output

This skill creates artifacts in the following structure:

Location: `.claude/artifacts/YYYY-MM-DD/analysis/{topic}/`

Example output:
```
.claude/artifacts/2025-11-26/analysis/langgraph-spike/
├── RESEARCH_SUMMARY.md
├── PROOF_OF_CONCEPT.md
└── DECISION_RECOMMENDATION.md
```

Files are automatically created with:
- Date folder (today's date in YYYY-MM-DD format)
- Category folder (`analysis/`, `reports/`, etc.)
- Topic subfolder (lowercase kebab-case)
- File names (SCREAMING_SNAKE_CASE)
```

## Examples

### Example 1: Single Research Document

Task: Document spike investigation for database migration

```
.claude/artifacts/2025-11-26/analysis/
└── DATABASE_MIGRATION_SPIKE.md

File: DATABASE_MIGRATION_SPIKE.md
---
# Database Migration Spike: PostgreSQL to Cassandra

## Overview
Investigating migration options for high-scale data storage...

## Options Evaluated
1. PostgreSQL with sharding
2. Cassandra
3. DynamoDB

## Recommendation
Cassandra - Superior for time-series data...
```

### Example 2: Multi-File Research Topic

Task: Compare multiple reactive programming frameworks

```
.claude/artifacts/2025-11-26/analysis/
└── reactive-framework-comparison/
    ├── RESEARCH_SUMMARY.md
    ├── REACT_ANALYSIS.md
    ├── VUE_ANALYSIS.md
    ├── SVELTE_ANALYSIS.md
    └── RECOMMENDATION.md

File: RESEARCH_SUMMARY.md
---
# Reactive Framework Comparison

This directory contains analysis of three reactive frameworks...
- React: Most mature ecosystem
- Vue: Best developer experience
- Svelte: Most performant

See individual files for detailed analysis.

File: REACT_ANALYSIS.md
---
# React Analysis

## Ecosystem
- NPM package ecosystem: 2M+ packages
- Learning curve: Moderate
- Community: Very large
...
```

### Example 3: Session-Specific Work

Task: Capture session analysis and learning consolidation

```
.claude/artifacts/2025-11-26/sessions/
├── SESSION_TRANSCRIPT.md
└── analysis/
    ├── SESSION_ANALYSIS.md
    └── LEARNING_CONSOLIDATION.md

File: SESSION_TRANSCRIPT.md
---
# Session Transcript - 2025-11-26

## Initial Request
Implement authentication module with...

## Work Completed
1. Created auth service module
2. Implemented JWT token validation
3. Added unit tests (95% coverage)
...

File: analysis/SESSION_ANALYSIS.md
---
# Session Analysis

## Goals Achieved
- ✓ Authentication module implemented
- ✓ 95% test coverage
- ✓ Type safety verified

## Time Allocation
- Implementation: 60%
- Testing: 30%
- Documentation: 10%
```

### Example 4: Health Report

Task: Generate weekly quality metrics report

```
.claude/artifacts/2025-11-26/reports/
├── WEEKLY_HEALTH_CHECK.md

File: WEEKLY_HEALTH_CHECK.md
---
# Weekly Health Check Report - 2025-11-26

## Summary
Quality metrics for week ending 2025-11-26

## Metrics
- Test Coverage: 94% (↑ 2% from last week)
- Type Checking: 0 errors (maintained)
- Linting: 0 warnings (↓ 3 from last week)

## Trend Analysis
...

## Recommendations
1. Focus on integration test coverage
2. Review error handling patterns
...
```

## Helper Scripts

Three Python scripts are provided to automate artifact creation. All scripts follow functional programming principles, include full type annotations, and pass strict linting and type checking.

### create_adr.py - Create Architecture Decision Records

Creates new ADR files in `docs/adr/` with auto-incremented numbering and standard template structure.

**Location**: `.claude/skills/artifacts-creating-and-managing/scripts/create_adr.py`

**Minimal Usage**:
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_adr.py \
  --title "Use Langchain for Multi-Agent Coordination"
```

**Full Usage**:
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_adr.py \
  --title "Use Langchain for Multi-Agent Coordination" \
  --status proposed \
  --context "Need efficient coordination between multiple Claude agents"
```

**Arguments**:
- `--title` (required): ADR title, max 100 characters
- `--status` (optional): proposed, accepted, deprecated, or superseded (default: proposed)
- `--context` (optional): Context summary explaining the decision background
- `--adr-dir` (optional): Directory containing ADRs (default: docs/adr)

**Output**:
- Creates directory: `docs/adr/{number:03d}-{slug}/`
- Creates file: `README.md` with ADR template
- Template includes: Status, Date, Context, Decision, Consequences, Alternatives, References

**Example Output**:
```
✓ ADR created successfully
  Location: /absolute/path/docs/adr/001-use-langchain-for-multi-agent-coordination/README.md
  Parent: 001-use-langchain-for-multi-agent-coordination
```

### create_research_topic.py - Create Research/Spike Documents

Creates new research topic files in `.claude/artifacts/YYYY-MM-DD/analysis/` with standard template structure.

**Location**: `.claude/skills/artifacts-creating-and-managing/scripts/create_research_topic.py`

**Minimal Usage**:
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_research_topic.py \
  --topic "Langfuse Integration" \
  --objective "Evaluate Langfuse for LLM observability and tracing"
```

**With Questions**:
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_research_topic.py \
  --topic "Async Context Manager Patterns" \
  --objective "Research best practices for async context managers" \
  --questions "How do we handle async cleanup?" \
  --questions "What are common pitfalls?" \
  --questions "How does pytest handle async fixtures?"
```

**Arguments**:
- `--topic` (required): Research topic name, max 80 characters
- `--objective` (required): Research objective or goal
- `--questions` (optional): Key questions to answer (can be specified multiple times)
- `--artifacts-dir` (optional): Artifacts directory (default: .claude/artifacts)

**Output**:
- Creates directory: `.claude/artifacts/YYYY-MM-DD/analysis/{topic-slug}/`
- Creates file: `RESEARCH_SUMMARY.md` with research template
- Template includes: Objective, Key Questions, Research Summary, Key Findings, Conclusions, Next Steps, References

**Example Output**:
```
✓ Research topic created successfully
  Location: /absolute/path/.claude/artifacts/2025-11-26/analysis/langfuse-integration/RESEARCH_SUMMARY.md
  Date: 2025-11-26
  Topic: langfuse-integration
```

### create_implementation_plan.py - Create Implementation Plans

Creates new implementation plan files in `.claude/artifacts/YYYY-MM-DD/plans/` with standard template structure.

**Location**: `.claude/skills/artifacts-creating-and-managing/scripts/create_implementation_plan.py`

**Minimal Usage**:
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_implementation_plan.py \
  --feature "TUI Agent Dashboard" \
  --overview "Build interactive terminal dashboard for agent monitoring"
```

**With Implementation Steps**:
```bash
python .claude/skills/artifacts-creating-and-managing/scripts/create_implementation_plan.py \
  --feature "TUI Agent Dashboard" \
  --overview "Build interactive terminal dashboard for real-time agent monitoring" \
  --steps "Design widget architecture" \
  --steps "Implement real-time log viewer" \
  --steps "Add status indicators" \
  --steps "Integrate with daemon IPC"
```

**Arguments**:
- `--feature` (required): Feature name, max 80 characters
- `--overview` (required): Feature overview/description
- `--steps` (optional): Implementation steps (can be specified multiple times)
- `--artifacts-dir` (optional): Artifacts directory (default: .claude/artifacts)

**Output**:
- Creates directory: `.claude/artifacts/YYYY-MM-DD/plans/{feature-slug}/`
- Creates file: `IMPLEMENTATION_PLAN.md` with implementation template
- Template includes: Overview, Prerequisites, Implementation Steps, Technical Considerations, Testing Strategy, Rollout Plan, Success Metrics, Timeline

**Example Output**:
```
✓ Implementation plan created successfully
  Location: /absolute/path/.claude/artifacts/2025-11-26/plans/tui-agent-dashboard/IMPLEMENTATION_PLAN.md
  Date: 2025-11-26
  Feature: tui-agent-dashboard
```

### Script Quality Standards

All scripts follow strict quality standards:

- **Type Safety**: 100% type annotations, passes `mypy --strict`
- **Linting**: Zero warnings, passes `ruff check`
- **Input Validation**: Fail-fast on invalid inputs with clear error messages
- **Error Handling**: Explicit error handling with descriptive exceptions
- **Documentation**: Google-style docstrings for all functions
- **Portability**: Use `pathlib` for cross-platform file operations

### Integration with Artifacts System

These scripts automatically:

1. **Generate today's date** in YYYY-MM-DD format
2. **Create required directories** (mkdir -p behavior)
3. **Use proper slug formatting** for directory names (lowercase kebab-case)
4. **Format file names** with SCREAMING_SNAKE_CASE
5. **Provide templates** with placeholders for customization
6. **Report results** with absolute file paths and parent directory names

## Reference

### Directory Tree of Artifact Structure

Complete reference structure:

```
.claude/artifacts/
├── 2025-11-24/
│   ├── analysis/
│   │   ├── ASYNC_PATTERNS_SPIKE.md
│   │   └── validation-framework/
│   │       ├── RESEARCH_SUMMARY.md
│   │       ├── POC_VALIDATION.md
│   │       └── IMPLEMENTATION_PLAN.md
│   ├── reports/
│   │   └── DAILY_HEALTH_CHECK.md
│   ├── sessions/
│   │   └── analysis/
│   │       └── SESSION_ANALYSIS.md
│   └── todos/
│       └── SPRINT_WORK.md
│
├── 2025-11-25/
│   ├── analysis/
│   │   └── memory-optimization/
│   │       ├── RESEARCH_SUMMARY.md
│   │       ├── PROFILING_RESULTS.md
│   │       └── OPTIMIZATION_ROADMAP.md
│   ├── reports/
│   │   └── PERFORMANCE_ANALYSIS.md
│   ├── sessions/
│   │   ├── SESSION_TRANSCRIPT.md
│   │   └── analysis/
│   │       ├── SESSION_ANALYSIS.md
│   │       └── LEARNING_CONSOLIDATION.md
│   └── todos/
│       └── feature-development/
│           ├── PHASE_ONE_TASKS.md
│           └── BACKLOG.md
│
└── 2025-11-26/
    ├── analysis/
    │   ├── LANGFUSE_SPIKE.md
    │   └── tui-framework-selection/
    │       ├── RESEARCH_SUMMARY.md
    │       ├── TEXTUAL_ANALYSIS.md
    │       ├── RICH_COMPARISON.md
    │       └── RECOMMENDATION.md
    ├── reports/
    │   └── WEEKLY_HEALTH_CHECK.md
    ├── sessions/
    │   └── analysis/
    │       └── SESSION_ANALYSIS.md
    └── todos/
        └── CURRENT_WORK.md
```

### Verification Checklist

Before finalizing artifacts, verify:

- [ ] Date folder uses YYYY-MM-DD format and matches creation date
- [ ] Files placed in appropriate category (analysis, reports, sessions, todos)
- [ ] Single-file topics are at category root
- [ ] Multi-file topics use kebab-case subfolder
- [ ] All markdown files use SCREAMING_SNAKE_CASE names
- [ ] No nested subfolders beyond one level
- [ ] File content is well-structured with clear headings
- [ ] Links between files use relative paths
- [ ] No version control artifacts (.git, __pycache__, .pyc)

### Integration Tips

When a skill creates artifacts:

1. **Document the pattern** in skill's SKILL.md
2. **Use date folder** automatically (read current date)
3. **Choose category** based on artifact type
4. **Create subfolder** only if multiple files needed
5. **Follow naming** consistently throughout artifact set
6. **Link back** to artifact location in main documentation

For questions about artifact structure, reference this skill and consult the Directory Structure and Category Definitions sections.
