# Quality Gates - Shared Reference

**Purpose:** Validation requirements that MUST pass before any work is considered "done".

**Principle:** Quality gates are non-negotiable. Fix issues or explain why guidance is needed.

---

## Mandatory Check (Before "Done")

**Run before saying work is complete:**

```bash
./scripts/check_all.sh  # Runs pyright, vulture, pytest, ruff in parallel (8s vs 31s)
```

**Why this matters:**
- Runs all checks in parallel (efficient)
- Catches type errors, dead code, test failures, and linting issues
- Must pass with ABSOLUTELY NO FAILURES

---

## Individual Checks (If Needed)

### Type Checking
```bash
uv run pyright
```

**What it validates:**
- Type annotations correctness
- Type consistency across calls
- Return type accuracy
- Parameter type matching

**When to run:**
- After adding new functions/classes
- After changing type signatures
- Before committing type-heavy code

---

### Dead Code Detection
```bash
uv run vulture src/your_project/
```

**What it validates:**
- Unused functions/classes/variables
- Unreachable code
- Dead imports

**When to run:**
- After refactoring
- Before cleaning up old code
- When removing features

**Note:** Vulture may report false positives for:
- MCP tool functions (called by framework)
- Test fixtures (used by pytest)
- Configuration dataclasses (instantiated via injection)

---

### Test Suite
```bash
uv run pytest tests/unit
```

**What it validates:**
- Unit tests pass
- Integration tests pass (if applicable)
- E2E tests pass (if applicable)
- No regressions introduced

**When to run:**
- After implementing new features
- After fixing bugs
- After refactoring
- Before committing any code

---

### Linting
```bash
uv run ruff check src/
```

**What it validates:**
- Code style compliance
- Import ordering
- Line length
- Unused imports
- Code complexity

**When to run:**
- After writing new code
- Before committing
- When code review flags style issues

---

## When to Run Quality Gates

### During Development
- Run individual checks as you work
- Focus on relevant check (e.g., pytest after writing tests)
- Use for rapid feedback

### Before Commit
- **ALWAYS** run `./scripts/check_all.sh`
- Fix ALL failures (no exceptions)
- Do not commit failing code

### After Refactoring
- Run full suite after major changes
- Verify no regressions introduced
- Confirm all layers still comply

### Before Pull Request
- Run `./scripts/check_all.sh` one final time
- Ensure CI will pass
- Document any expected warnings (with justification)

---

## Red Flags - STOP

1. **Quality gates fail but "it works"** → Tests are more reliable than manual verification
2. **"Tests are unrelated to my change"** → All failures must be investigated
3. **Skip quality checks** → Never skip, fix or explain
4. **Quality gates pass but code feels wrong** → Trust your instincts, review architecture

---

## Definition of Done

Work is NOT done until:
- [ ] `./scripts/check_all.sh` passes and ABSOLUTELY NO FAILURES
- [ ] Tests added for new code
- [ ] ServiceResult used everywhere
- [ ] No optional dependencies
- [ ] Clean Architecture respected

**Principle:** Task is NOT done if quality gates fail. Fix or explain why guidance needed.

---

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Core rules and definition of done
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Testing strategy
- [Agent Dispatch](./dispatch.md) - When to use test agents

---

**Last Updated:** 2025-10-16
**Principle:** Quality gates are the final arbiter of "done". No exceptions.
