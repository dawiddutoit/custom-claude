# Skills Created 2025-12-07: Preventing "Done But Not Integrated" Failures

**Date:** 2025-12-07
**Context:** Response to ADR-013 failure analysis
**Purpose:** Prevent incomplete work from being marked as "done"

---

## What Was Created

Three new skills were created in `~/.claude/skills/` to prevent the ADR-013 failure pattern:

1. **quality-verify-implementation-complete** - Technical verification of integration
2. **quality-reflective-questions** - Mental framework for challenging assumptions
3. **quality-detect-orphaned-code** - Automated detection of unused code

---

## Skill 1: quality-verify-implementation-complete

**Location:** `~/.claude/skills/quality-verify-implementation-complete/`

**Purpose:** Enforce the Creation-Connection-Verification (CCV) principle by verifying code is actually integrated and executes at runtime.

**Key Features:**
- Three-phase verification (Creation → Connection → Verification)
- Four Questions Test framework
- Step-by-step verification process for different artifact types
- Detection methods for common failure patterns
- Integration with quality gates

**Trigger Phrases:**
- "Verify this implementation is complete"
- "Is this code integrated?"
- "Check if my code is wired into the system"
- "Prove this feature runs"

**When to Use:**
- Before marking any task as "done"
- Before moving ADRs to completed
- After creating new modules/nodes/services
- Before claiming "feature works"

**What It Prevents:**
- ADR-013 failure mode (code exists but never integrated)
- Orphaned modules (files created but never imported)
- Orphaned functions (defined but never called)
- Dead code paths (wired but never triggered)

**Supporting Files:**
- `references/adr-013-case-study.md` - Real-world failure analysis
- `examples/` - Verification examples for different artifact types
- `scripts/` - Verification automation scripts
- `templates/` - Copy-paste checklists

---

## Skill 2: quality-reflective-questions

**Location:** `~/.claude/skills/quality-reflective-questions/`

**Purpose:** Provide reflective questioning framework to challenge assumptions about work completeness, catching gaps through critical thinking.

**Key Features:**
- The Four Mandatory Questions (deep dive)
- Category-specific questions (LangGraph, CLI, Services, API)
- Red Flag Questions (15 warning signs)
- Honesty Checklist (evidence requirements)
- Common Self-Deception Patterns

**Trigger Phrases:**
- "Challenge my assumptions about completeness"
- "Ask me reflective questions about my work"
- "Is this really done?"
- "Self-review my implementation"

**When to Use (PROACTIVE):**
- Before marking any task complete (every time)
- Before moving ADR to completed
- Before claiming "feature works"
- During self-review
- When feeling uncertain

**What It Prevents:**
- Self-deception about completeness
- Vague claims without evidence ("it should work")
- Premature completion (rushing to "done")
- Assumption-based verification (vs evidence-based)

**Supporting Files:**
- `templates/four-questions-template.md` - Self-review template
- `references/` - Deep dives on self-deception patterns
- `examples/` - Good vs bad answer comparisons

**The Four Questions:**
1. **How do I trigger this?** (entry point)
2. **What connects it to the system?** (wiring)
3. **What evidence proves it runs?** (execution)
4. **What shows it works correctly?** (outcome)

---

## Skill 3: quality-detect-orphaned-code

**Location:** `~/.claude/skills/quality-detect-orphaned-code/`

**Purpose:** Detect code that exists but is never imported or called in production, providing automated verification of integration.

**Key Features:**
- Five types of orphaned code detection
- Manual grep methods (quick checks)
- Automated script (`verify_integration.sh`)
- Integration test patterns (LangGraph-specific)
- CI/CD integration

**Trigger Phrases:**
- "Detect orphaned code"
- "Find dead code in the project"
- "Check for unused modules"
- "Verify no orphaned files exist"

**When to Use:**
- Before marking features complete
- Before moving ADRs to completed
- After creating new modules
- As part of quality gates
- During code review

**What It Detects:**
1. Orphaned modules (files never imported)
2. Orphaned functions (defined but never called)
3. Orphaned classes (defined but never instantiated)
4. Orphaned LangGraph nodes (not in graph)
5. Dead code paths (wired but conditional never triggers)

**Supporting Files:**
- `scripts/verify_integration.sh` - Comprehensive orphan detection
- `scripts/check_imports.sh` - Module-specific import check
- `scripts/check_callsites.sh` - Function-specific call check
- `examples/` - Detection walkthroughs

**Tools:** Read-only (Read, Grep, Bash, Glob)

---

## How These Skills Work Together

### The Workflow

```
1. Implement feature (code + tests)
   ↓
2. Run quality-reflective-questions
   - Answer Four Questions
   - Challenge assumptions
   - Check for vague language
   ↓
3. Run quality-detect-orphaned-code
   - Check for orphaned modules
   - Verify imports exist
   - Verify call-sites exist
   ↓
4. Run quality-verify-implementation-complete
   - Verify Phase 1: CREATION (artifacts exist)
   - Verify Phase 2: CONNECTION (wiring exists)
   - Verify Phase 3: VERIFICATION (execution proven)
   ↓
5. All pass? → Mark complete ✅
   Any fail? → Fix gaps, repeat ❌
```

### Complementary Strengths

| Skill | Focus | Type | Output |
|-------|-------|------|--------|
| quality-reflective-questions | Mental framework | Questioning | Self-assessment |
| quality-detect-orphaned-code | Automated detection | Technical | Code analysis |
| quality-verify-implementation-complete | Comprehensive verification | Structured process | Evidence report |

**Together:** Cover mental, automated, and structured verification of completeness.

---

## Integration with Existing Skills

These skills should be integrated with:

### util-manage-todo
- Add three-phase pattern (Create → Connect → Verify)
- Require Phase 3 evidence before marking complete
- Reference quality-verify-implementation-complete

### create-adr-spike
- Add Phase 6: Integration Verification
- Require quality-verify-implementation-complete before completion
- Check for orphaned code before moving to completed

### quality-run-quality-gates
- Add Gate 6: Integration Verification
- Run quality-detect-orphaned-code script
- Require verification for new modules

---

## The Core Principle: CCV

All three skills enforce the **Creation-Connection-Verification** principle:

**COMPLETE = CREATION + CONNECTION + VERIFICATION**

| Phase | Proves | Evidence |
|-------|--------|----------|
| **CREATION** | Artifact exists | File, tests, types, linting |
| **CONNECTION** | Artifact is wired in | Import, registration, config |
| **VERIFICATION** | Artifact executes | Logs, output, state changes |

**Missing any phase = Feature is INCOMPLETE**

---

## The Four Questions Test

All three skills reference the **Four Questions** that must be answered:

1. **How do I trigger this?** → Entry point
2. **What connects it to the system?** → Wiring
3. **What evidence proves it runs?** → Execution
4. **What shows it works correctly?** → Outcome

**Cannot answer all four = NOT COMPLETE**

---

## What This Prevents

### The ADR-013 Failure Pattern

**What happened:**
- 313 lines of code written (architecture_nodes.py, task_provider_nodes.py)
- 46 unit tests passing
- All quality gates passing (mypy, ruff, pytest)
- ADR moved to completed
- **But code was NEVER imported into builder.py**
- **Feature never executed at runtime**

**What these skills prevent:**

| Without Skills | With Skills |
|----------------|-------------|
| ❌ "Tests pass" → Complete | ✅ "Tests pass AND integrated AND executed" → Complete |
| ❌ Vague claims ("it should work") | ✅ Specific evidence required |
| ❌ Self-approval without verification | ✅ Structured verification required |
| ❌ Orphaned code passes quality gates | ✅ Orphan detection catches it |
| ❌ Assumptions about integration | ✅ Proof of integration required |

---

## Quick Reference: When to Use Each Skill

### Before Marking Task Complete
1. **quality-reflective-questions** - Self-assessment (5 min)
2. **quality-detect-orphaned-code** - Quick check (30 sec)
3. **quality-verify-implementation-complete** - Full verification (5-10 min)

### Before Moving ADR to Completed
1. **quality-verify-implementation-complete** - Comprehensive check
2. **quality-detect-orphaned-code** - Run verification script
3. **quality-reflective-questions** - Final honesty check

### During Code Review
1. **quality-reflective-questions** - Ask the Four Questions
2. **quality-detect-orphaned-code** - Verify integration
3. **quality-verify-implementation-complete** - Demand evidence

### As Part of Quality Gates
1. **quality-detect-orphaned-code** - Automated check (CI/CD)
2. **quality-verify-implementation-complete** - Pre-commit hook

---

## Example Usage

### Scenario: Implementing a New LangGraph Node

**Step 1: Create the node file**
```bash
# Create architecture_nodes.py
# Write unit tests
# All tests pass
```

**Step 2: Run quality-reflective-questions**
```
Q1: How do I trigger this?
A: "Run the coordinator" ❌ Too vague

Re-answer: "uv run temet-run -a talky -p 'Write code'"
          "When should_review_architecture() returns True" ✅

Q2: What connects it to the system?
A: "It's in builder.py" ❌ Vague

Check: grep "architecture_nodes" builder.py
Result: (empty) ❌

FOUND GAP: Node not imported!
```

**Step 3: Fix the gap**
```python
# In builder.py
from .architecture_nodes import create_architecture_review_node
graph.add_node("architecture_review", review_node)
```

**Step 4: Run quality-detect-orphaned-code**
```bash
./scripts/verify_integration.sh
# Output: ✅ All modules integrated
```

**Step 5: Run quality-verify-implementation-complete**
```
Phase 1: CREATION ✅
  - File exists
  - Tests pass

Phase 2: CONNECTION ✅
  - Imported in builder.py line 12
  - Added to graph line 146

Phase 3: VERIFICATION ✅
  - Logs show execution
  - State populated correctly

Four Questions: All answered ✅

DECISION: ✅ Implementation is COMPLETE
```

**Result:** Feature is verified complete with evidence, preventing ADR-013 pattern.

---

## Files Created

### Skill 1: quality-verify-implementation-complete
```
~/.claude/skills/quality-verify-implementation-complete/
├── SKILL.md (355 lines)
├── references/
│   └── adr-013-case-study.md
├── examples/
├── scripts/
└── templates/
```

### Skill 2: quality-reflective-questions
```
~/.claude/skills/quality-reflective-questions/
├── SKILL.md (347 lines)
├── references/
├── examples/
└── templates/
    └── four-questions-template.md
```

### Skill 3: quality-detect-orphaned-code
```
~/.claude/skills/quality-detect-orphaned-code/
├── SKILL.md (368 lines)
├── references/
├── examples/
├── scripts/
│   └── verify_integration.sh (executable)
└── templates/
```

**Total:** 3 skills, 1070+ lines of documentation, 1 executable script

---

## Next Steps

### Immediate (This Session)
- [x] Create quality-verify-implementation-complete skill
- [x] Create quality-reflective-questions skill
- [x] Create quality-detect-orphaned-code skill
- [ ] Test skills on a real feature implementation
- [ ] Update project CLAUDE.md with CCV principle reference

### Short-term (Next Session)
- [ ] Integrate with util-manage-todo skill
- [ ] Integrate with create-adr-spike skill
- [ ] Integrate with quality-run-quality-gates skill
- [ ] Add verify_integration.sh to project scripts/
- [ ] Create test_graph_completeness.py integration test

### Medium-term (Future)
- [ ] Add to project quality gates
- [ ] Train team on the Four Questions
- [ ] Audit existing completed ADRs
- [ ] Add to CI/CD pipeline

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Integration Failures** | 0% | No ADRs moved to completed with orphaned code |
| **Evidence Required** | 100% | All completions have Four Questions answered |
| **Orphan Detection** | Weekly | Run verify_integration.sh in CI/CD |
| **Self-Review Adoption** | 100% | All developers use reflective questions |

---

## Key Takeaway

**Code is not "done" when it compiles and tests pass.**

**Code is "done" when:**
1. It is **CREATED** (file exists, tests pass)
2. It is **CONNECTED** (imported, registered, wired)
3. It is **VERIFIED** (executed at runtime, produces correct outcome)

**These skills enforce all three phases.**

---

## References

- ADR-013 failure analysis: `/Users/dawiddutoit/projects/play/temet-run/.claude/artifacts/2025-12-07/analysis/adr-not-done/`
- Prevention framework: `05-PREVENTION-FRAMEWORK.md`
- CCV principle: `03-UNIVERSAL-PRINCIPLE.md`
- Root cause analysis: `02-ROOT-CAUSE-ANALYSIS.md`

---

**Skills are now ACTIVE and ready to use.**

Invoke with trigger phrases or reference directly in prompts.
