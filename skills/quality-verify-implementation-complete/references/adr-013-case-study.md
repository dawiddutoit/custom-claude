# ADR-013 Case Study: "Done But Not Integrated" Failure

**Date:** 2025-12-07
**Incident:** ADR-013 (Uber Agent Coordination Integration)
**Status:** Critical Process Failure

## What Happened

ADR-013 was moved to `docs/adr/3_completed/` with status "ACCEPTED | Implemented". All quality gates passed:
- ✅ Type checking (mypy)
- ✅ Linting (ruff)
- ✅ Unit tests (46 tests, 100% coverage)
- ✅ All todos marked complete

**But the feature didn't work.**

Two fully implemented modules were **never integrated**:
- `architecture_nodes.py` (175 lines, 24 tests)
- `task_provider_nodes.py` (138 lines, 22 tests)

## The Evidence

```bash
# These returned NOTHING
$ grep "architecture_nodes" src/temet_run/coordination/graph/builder.py
(empty)

$ grep "task_provider_nodes" src/temet_run/coordination/graph/builder.py
(empty)
```

## The Root Cause: Unit Test Isolation Trap

Tests verified functions work **in isolation**:

```python
# test_architecture_nodes.py
async def test_architecture_review_node_with_code(mock_guardian_agent):
    node = await create_architecture_review_node(mock_guardian_agent)
    result = await node(state_with_code)
    assert result["architecture_review"] is not None  # ✅ PASSES
```

But no test verified the node was **wired into the graph**:

```python
# This test NEVER EXISTED
async def test_architecture_review_node_in_graph():
    graph = await create_coordination_graph(checkpointer)
    assert "architecture_review" in graph.nodes  # Would have FAILED
```

## Why Existing Checks Failed

| Check | Result | Why It Missed This |
|-------|--------|-------------------|
| mypy | ✅ Pass | Type-checks file in isolation, not usage |
| ruff | ✅ Pass | Checks style, not call-sites |
| pytest | ✅ Pass | Tests functions work, not that they're used |
| 100% coverage | ✅ Pass | Covers the file, not its integration |
| vulture | ❓ Maybe | Unit tests import modules, obscuring dead code |

## The Process Gap

**Current (Broken) Flow:**
```
1. Create file ✅
2. Write unit tests ✅
3. Tests pass ✅
4. Mark todo complete ✅
5. Move ADR to completed ✅
6. Code never executes ❌
```

**Required Flow:**
```
1. Create file
2. Write unit tests
3. Tests pass
4. Mark "Create" todo complete
5. Import in builder.py
6. Add node registration and edges
7. Run integration test
8. Mark "Integrate" todo complete
9. Run verification script
10. Move ADR to completed
```

## What Should Have Been Checked

### Connection Verification (Was Never Done)

```bash
# Should have run this before "complete"
$ grep "architecture_nodes" src/temet_run/coordination/graph/builder.py
# Expected: from .architecture_nodes import create_architecture_review_node
# Actual: (empty) ❌
```

### Integration Test (Was Never Created)

```python
# Should have added to test_graph_completeness.py
EXPECTED_NODES = [
    "architecture_review",  # ❌ NEVER ADDED
    "retrieve_tasks",       # ❌ NEVER ADDED
    # ... other nodes
]
```

### Runtime Verification (Was Never Done)

```bash
# Should have run coordinator and checked logs
$ uv run temet-run -a talky -p "Write code" | grep "architecture_review"
# Expected: [INFO] architecture_review_triggered
# Actual: (empty - node never executed) ❌
```

## The Four Questions (Were Never Answered)

### Question 1: How do I trigger this?
**Answer at time of completion:** "Run the coordinator"
**Problem:** Too vague - no specific command provided

### Question 2: What connects it to the system?
**Answer at time of completion:** "builder.py should import it"
**Problem:** "Should" is not "does" - never verified

### Question 3: What evidence proves it runs?
**Answer at time of completion:** (never asked)
**Problem:** No execution proof was required

### Question 4: What shows it works correctly?
**Answer at time of completion:** "Tests pass"
**Problem:** Unit tests don't prove integration

## Lessons Learned

### What Went Wrong

1. **File creation ≠ Integration** — These are two separate, verifiable steps
2. **Unit tests can hide orphans** — Tests that import directly make dead code appear alive
3. **"Done" was defined as artifacts, not behavior** — File exists vs feature works
4. **No runtime verification requirement** — Compile-time success was deemed sufficient
5. **Self-approval bypassed verification** — No external reviewer caught the gap

### What Would Have Prevented This

1. **Three-phase todos** — Separate "Create", "Connect", "Verify" tasks
2. **Four Questions Test** — Mandatory answers before claiming "done"
3. **Integration verification** — Script to detect orphaned modules
4. **Integration tests** — Test that components are in compiled system
5. **Runtime proof requirement** — Show execution logs before completion
6. **External review** — Reviewer agent would have asked "where is it wired?"

## The Universal Principle

This failure applies beyond LangGraph:

| Scenario | Created | Missing Connection |
|----------|---------|-------------------|
| CLI command | `commands/foo.py` | Not registered in CLI group |
| Service class | `services/bar.py` | Not added to DI container |
| API endpoint | `routes/baz.py` | Not added to router |
| LangGraph node | `*_nodes.py` | Not added to graph builder |

**In every case:** Artifact exists, tests pass, feature doesn't work.

## Prevention Framework

### CLAUDE.md Addition

```markdown
## Completion Requires Runtime Evidence (MANDATORY)

Before claiming "done", you MUST:
1. Verify CREATION (artifact exists, tests pass)
2. Verify CONNECTION (imported, registered, wired)
3. Verify VERIFICATION (executed at runtime, correct outcome)

Cannot answer the Four Questions = NOT COMPLETE.
```

### Todo Pattern

```markdown
## Feature: Add X Node

### Phase 1: CREATION
- [ ] Create module file
- [ ] Unit tests pass

### Phase 2: CONNECTION
- [ ] Import in builder.py
- [ ] Add to graph
- [ ] Wire edges

### Phase 3: VERIFICATION
- [ ] Integration test exists
- [ ] Runtime execution proven
- [ ] Correct outcome observed
```

### Verification Script

```bash
#!/bin/bash
# scripts/verify_integration.sh
# Detects orphaned modules

for file in $(find src/ -name "*.py"); do
  module=$(basename "$file" .py)
  imports=$(grep -r "import.*$module" src/ | grep -v "$file" | wc -l)
  if [ "$imports" -eq 0 ]; then
    echo "⚠️  ORPHANED: $file"
  fi
done
```

## Impact

### Trust Violation
- "Completed" status became unreliable
- All ADRs in `3_completed/` now suspect
- Self-assessment process fundamentally flawed

### Technical Debt
- 313 lines of orphaned code
- 46 tests that don't prove integration
- State fields prepared but never used

### Process Failure
- No mechanism caught this before completion
- Quality gates insufficient for integration work
- Definition of "done" was broken

## Resolution

### Immediate (Fixed ADR-013)
1. Wire `architecture_nodes.py` into `builder.py`
2. Wire `task_provider_nodes.py` into `builder.py`
3. Add integration test for graph completeness
4. Verify execution with runtime logs

### Short-term (Prevent Recurrence)
1. Update CLAUDE.md with CCV principle
2. Update `util-manage-todo` skill with three-phase pattern
3. Create `quality-verify-implementation-complete` skill
4. Add verification script to quality gates

### Long-term (Cultural Change)
1. Change "done" definition from artifacts to behavior
2. Require runtime proof for all completion claims
3. Mandate Four Questions Test before "complete"
4. External review required for complex features

## References

- Full analysis: `.claude/artifacts/2025-12-07/analysis/adr-not-done/`
- Prevention framework: `05-PREVENTION-FRAMEWORK.md`
- CCV principle: `03-UNIVERSAL-PRINCIPLE.md`
- Root cause analysis: `02-ROOT-CAUSE-ANALYSIS.md`

## Key Takeaway

**Code is not "done" when it compiles and tests pass.**

**Code is "done" when:**
1. It is **CREATED** (file exists, tests pass)
2. It is **CONNECTED** (imported, registered, wired)
3. It is **VERIFIED** (executed at runtime, produces correct outcome)

**Missing any phase = Feature incomplete.**
