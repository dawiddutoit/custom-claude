# Regression Fixes - detect-quality-regressions

This document provides fix strategies for each type of quality regression detected by the skill.

---

## Overview

When regressions are detected, this guide helps you:

1. **Understand the root cause** of the regression
2. **Apply the appropriate fix** for each metric type
3. **Verify the fix** worked (re-run regression detection)
4. **Prevent future regressions** of the same type

---

## Regression Type 1: Tests Passed Decreased

### Symptoms

```
❌ Tests: -2 passed (150 vs 152)
   → 2 tests removed or now failing
```

### Root Causes

**Cause 1: Tests removed**
- Deleted test files
- Commented out tests
- Removed test functions

**Cause 2: Tests now failing**
- Tests exist but fail
- Failures counted as "not passed"

**Cause 3: Tests now skipped**
- Tests marked with @skip decorator
- Tests conditionally skipped
- Tests disabled in config

### Investigation Steps

**Step 1: Check git diff**
```bash
git diff baseline_commit..HEAD -- tests/
```

**Look for:**
- Deleted test files
- Removed test functions
- Added @skip decorators

**Step 2: Run tests to see failures**
```bash
uv run pytest tests/ -v
```

**Look for:**
- FAILED tests
- SKIPPED tests
- ERROR collecting tests

**Step 3: Compare test counts**
```bash
# Baseline
git checkout baseline_commit
uv run pytest tests/ --collect-only | grep "test_"

# Current
git checkout current_branch
uv run pytest tests/ --collect-only | grep "test_"
```

### Fixes

**Fix 1: Restore removed tests**

If tests were accidentally removed:

```bash
# Restore from git
git checkout baseline_commit -- tests/unit/test_user_service.py

# Verify tests pass
uv run pytest tests/unit/test_user_service.py -v

# Re-run regression detection
detect-quality-regressions
```

**Fix 2: Fix failing tests**

If tests are failing:

```bash
# Run failing tests
uv run pytest tests/unit/test_user_service.py -v

# Read error messages
# Fix code or test as appropriate

# Verify fix
uv run pytest tests/unit/test_user_service.py -v

# Re-run regression detection
detect-quality-regressions
```

**Fix 3: Remove skip decorators**

If tests are skipped:

```python
# Before
@pytest.mark.skip(reason="Temporarily disabled")
def test_user_search():
    ...

# After (remove skip)
def test_user_search():
    ...
```

**Fix 4: Intentional test removal**

If test removal was intentional (e.g., removed feature):

1. Document reason in commit message
2. Update baseline to reflect new test count
3. Capture new baseline:
   ```
   capture-quality-baseline --name baseline_feature_removed_2025-10-16
   ```

### Verification

```bash
# 1. Run tests
uv run pytest tests/ -v

# Expected: Same or more tests passed vs baseline

# 2. Re-run regression detection
detect-quality-regressions

# Expected: ✅ PASS for tests metric
```

### Prevention

- **Never remove tests** without documenting reason
- **Fix failing tests** instead of deleting them
- **Update baseline** when intentionally removing tests
- **Review test changes** in code review

---

## Regression Type 2: Coverage Decreased

### Symptoms

```
❌ Coverage: -4% (85% vs 89%)
   → Coverage dropped below tolerance (88%)
   → Action: Add tests for uncovered code
```

### Root Causes

**Cause 1: New code without tests**
- Added new functions/classes
- No tests for new code
- Coverage denominator increased (total lines up)

**Cause 2: Tests removed**
- Deleted tests that covered code
- Coverage numerator decreased (covered lines down)

**Cause 3: Code refactored**
- Moved code to untested areas
- Refactored in ways that reduce coverage

### Investigation Steps

**Step 1: Generate coverage report**
```bash
uv run pytest --cov --cov-report=html
open htmlcov/index.html
```

**Look for:**
- Red/yellow lines (uncovered code)
- Newly added files with low coverage
- Files with coverage drop

**Step 2: Compare to baseline**
```bash
# Baseline coverage
git checkout baseline_commit
uv run pytest --cov --cov-report=term | grep TOTAL

# Current coverage
git checkout current_branch
uv run pytest --cov --cov-report=term | grep TOTAL
```

**Step 3: Identify uncovered changes**
```bash
# See what code changed
git diff baseline_commit..HEAD -- src/

# Check coverage for changed files
uv run pytest --cov=src/services/user_service.py --cov-report=term-missing
```

### Fixes

**Fix 1: Add tests for new code**

If new code lacks tests:

```python
# New code (uncovered)
def search_users(query: str) -> List[User]:
    """Search users by query."""
    return [u for u in users if query in u.name]

# Add tests
def test_search_users_with_match():
    result = search_users("alice")
    assert len(result) == 1

def test_search_users_no_match():
    result = search_users("nonexistent")
    assert len(result) == 0

def test_search_users_empty_query():
    result = search_users("")
    assert len(result) == len(users)
```

**Fix 2: Restore removed tests**

If tests were removed:

```bash
git checkout baseline_commit -- tests/unit/test_user_service.py
uv run pytest tests/unit/test_user_service.py -v
```

**Fix 3: Add missing test scenarios**

If existing tests don't cover all branches:

```python
# Code with branches
def process_user(user: User | None) -> str:
    if user is None:
        return "No user"
    if user.is_admin:
        return f"Admin: {user.name}"
    return f"User: {user.name}"

# Tests for all branches
def test_process_user_none():
    assert process_user(None) == "No user"

def test_process_user_admin():
    admin = User(name="Alice", is_admin=True)
    assert process_user(admin) == "Admin: Alice"

def test_process_user_regular():
    user = User(name="Bob", is_admin=False)
    assert process_user(user) == "User: Bob"
```

**Fix 4: Coverage is acceptable (update baseline)**

If coverage drop is intentional and acceptable:

1. Justify in commit message
2. Update baseline:
   ```
   capture-quality-baseline --name baseline_coverage_adjusted_2025-10-16
   ```

### Verification

```bash
# 1. Run coverage
uv run pytest --cov --cov-report=term

# Expected: Coverage >= baseline - 1%

# 2. Re-run regression detection
detect-quality-regressions

# Expected: ✅ PASS for coverage metric
```

### Prevention

- **Write tests before code** (TDD)
- **Check coverage** before committing: `uv run pytest --cov`
- **Aim for >90% coverage** on new code
- **Review coverage reports** in CI/CD

---

## Regression Type 3: Type Errors Increased

### Symptoms

```
❌ Type errors: +2 new errors (5 vs 3)
   → New type errors introduced:
     • src/services/user_service.py:67 - Type "None" cannot be assigned to type "str"
     • src/services/user_service.py:89 - Argument of type "int" cannot be assigned
```

### Root Causes

**Cause 1: Changed type signatures**
- Made parameter non-optional
- Changed return type
- Modified type annotations

**Cause 2: Missing type annotations**
- Added functions without types
- Removed type annotations
- Used untyped libraries

**Cause 3: Type contract violations**
- Passed wrong type to function
- Returned wrong type from function
- Type mismatches in assignments

### Investigation Steps

**Step 1: Run pyright with verbose**
```bash
uv run pyright --verbose
```

**Look for:**
- Specific error messages
- File:line locations
- Type mismatches

**Step 2: Compare to baseline errors**
```bash
# Baseline errors
git checkout baseline_commit
uv run pyright > /tmp/baseline_errors.txt

# Current errors
git checkout current_branch
uv run pyright > /tmp/current_errors.txt

# Compare
diff /tmp/baseline_errors.txt /tmp/current_errors.txt
```

**Step 3: Identify NEW errors**
- Errors in current but NOT in baseline = new regressions
- Errors in both = pre-existing (not regressions)

### Fixes

**Fix 1: Add type annotations**

If function lacks types:

```python
# Before (untyped)
def search_users(query):
    return [u for u in users if query in u.name]

# After (typed)
def search_users(query: str) -> List[User]:
    return [u for u in users if query in u.name]
```

**Fix 2: Fix type mismatches**

If passing wrong type:

```python
# Error: Type "None" cannot be assigned to type "str"

# Before
def get_username(user: User) -> str:
    return user.name  # name could be None

# After (Option 1: Handle None)
def get_username(user: User) -> str:
    return user.name or "Unknown"

# After (Option 2: Change return type)
def get_username(user: User) -> str | None:
    return user.name
```

**Fix 3: Use Optional types**

If parameter can be None:

```python
# Error: Argument of type "None" cannot be assigned to parameter

# Before
def create_user(name: str) -> User:
    return User(name=name)

create_user(None)  # Type error

# After
def create_user(name: str | None) -> User:
    if name is None:
        name = "Anonymous"
    return User(name=name)
```

**Fix 4: Type ignore (last resort)**

If type checker is wrong (rare):

```python
# Pyright reports error but code is correct
result = some_function()  # type: ignore[pyright]
```

**⚠️ Use sparingly - usually indicates real type issue**

### Verification

```bash
# 1. Run pyright
uv run pyright

# Expected: Same or fewer errors vs baseline

# 2. Re-run regression detection
detect-quality-regressions

# Expected: ✅ PASS for type_errors metric
```

### Prevention

- **Type all functions** from the start
- **Run pyright** before committing
- **Use strict mode** in pyproject.toml
- **Review type errors** in code review

---

## Regression Type 4: Linting Errors Increased

### Symptoms

```
❌ Linting: +2 new errors (2 vs 0)
   → Unused imports detected:
     • src/services/user_service.py:1 - 'logging' imported but unused
     • src/services/auth_service.py:3 - 'Optional' imported but unused
```

### Root Causes

**Cause 1: Unused imports**
- Imported but never used
- Removed code that used import
- Duplicate imports

**Cause 2: Code style violations**
- Line too long
- Missing whitespace
- Incorrect formatting

**Cause 3: Code complexity**
- Function too complex
- Too many arguments
- Cyclomatic complexity

### Investigation Steps

**Step 1: Run ruff check**
```bash
uv run ruff check src/
```

**Look for:**
- Error codes (F401, E501, etc.)
- File:line locations
- Auto-fixable markers [*]

**Step 2: Compare to baseline**
```bash
# Baseline errors
git checkout baseline_commit
uv run ruff check src/ > /tmp/baseline_lint.txt

# Current errors
git checkout current_branch
uv run ruff check src/ > /tmp/current_lint.txt

# Compare
diff /tmp/baseline_lint.txt /tmp/current_lint.txt
```

### Fixes

**Fix 1: Auto-fix (preferred)**

Most linting errors are auto-fixable:

```bash
# Fix all auto-fixable errors
uv run ruff check --fix src/

# Verify
uv run ruff check src/
```

**Auto-fixes:**
- Remove unused imports (F401)
- Fix import order (I001)
- Remove unused variables (F841)
- Fix whitespace (W293)

**Fix 2: Manual fixes**

For non-auto-fixable errors:

```python
# Error: E501 Line too long (92 > 88 characters)

# Before
user = User(name="Alice", email="alice@example.com", role="admin", department="Engineering")

# After (split line)
user = User(
    name="Alice",
    email="alice@example.com",
    role="admin",
    department="Engineering"
)
```

**Fix 3: Simplify code**

For complexity errors:

```python
# Error: C901 Function too complex (complexity 12 > 10)

# Before (complex)
def process_user(user):
    if user.is_admin:
        if user.is_active:
            if user.has_permission("write"):
                # 10 more nested ifs...
                return result

# After (simplified)
def process_user(user):
    if not user.is_admin or not user.is_active:
        return None

    if not user.has_permission("write"):
        return None

    return _do_complex_processing(user)

def _do_complex_processing(user):
    # Extract complex logic
    ...
```

**Fix 4: Suppress specific error (rare)**

If linting rule is incorrect:

```python
# Suppress specific error on line
result = complex_expression()  # noqa: E501

# Suppress for entire file
# ruff: noqa: E501
```

### Verification

```bash
# 1. Run linting
uv run ruff check src/

# Expected: Same or fewer errors vs baseline

# 2. Re-run regression detection
detect-quality-regressions

# Expected: ✅ PASS for linting metric
```

### Prevention

- **Run ruff check --fix** before committing
- **Use pre-commit hooks** to auto-fix
- **Enable ruff in IDE** for real-time feedback
- **Review linting** in code review

---

## Regression Type 5: Dead Code Increased

### Symptoms

```
❌ Dead code: +2.5% (3.5% vs 1.0%)
   → Above threshold (3.0%)
   → Action: Remove unused code or document false positives
```

### Root Causes

**Cause 1: Unused functions/classes**
- Added code not yet used
- Removed code that used functions
- Legacy code no longer called

**Cause 2: Unused imports**
- Imported but never used
- Duplicate imports

**Cause 3: Unreachable code**
- Code after return statements
- Code in always-false branches

### Investigation Steps

**Step 1: Run vulture**
```bash
uv run vulture src/ --min-confidence 80
```

**Look for:**
- Unused functions
- Unused imports
- Unused variables
- Confidence level (higher = more likely dead)

**Step 2: Verify dead code**

For each item vulture reports:

```bash
# Search for usage
grep -r "function_name" src/
```

**If found:** Not dead (false positive)
**If not found:** Likely dead (true positive)

### Fixes

**Fix 1: Remove dead code**

If code is truly unused:

```python
# Before
def unused_helper():  # Reported by vulture
    return "This is never called"

# After (remove)
# (deleted)
```

**Fix 2: Remove unused imports**

```python
# Before
import logging  # Reported by vulture
from typing import Optional  # Used
```

```bash
# Auto-fix
uv run ruff check --fix src/
```

**Fix 3: Document false positives**

If code appears dead but is used dynamically:

```python
# Dynamic usage (vulture can't detect)
def dynamic_handler():
    """Called dynamically via getattr."""
    return "result"

# Mark as used
dynamic_handler.__used__ = True  # type: ignore[vulture]
```

**Fix 4: Lower confidence threshold**

If too many false positives:

```bash
# Higher threshold = fewer false positives
uv run vulture src/ --min-confidence 90
```

**Fix 5: Temporarily allow dead code**

If refactoring in progress:

1. Document in commit message
2. Update baseline temporarily
3. Clean up dead code in next commit

### Verification

```bash
# 1. Run vulture
uv run vulture src/ --min-confidence 80

# Expected: Dead code <= baseline + 2%

# 2. Re-run regression detection
detect-quality-regressions

# Expected: ✅ PASS for dead_code metric
```

### Prevention

- **Remove unused code** immediately
- **Use ruff** to remove unused imports
- **Run vulture** regularly
- **Review dead code reports** in code review

---

## Systematic Fix Process

When multiple regressions detected, fix in this order:

### Priority Order

1. **Linting** (easiest, often auto-fixable)
   ```bash
   uv run ruff check --fix src/
   ```

2. **Type errors** (critical, must fix)
   ```bash
   uv run pyright
   # Fix each error manually
   ```

3. **Tests** (restore or fix failing tests)
   ```bash
   uv run pytest tests/ -v
   # Fix failures
   ```

4. **Coverage** (add tests for uncovered code)
   ```bash
   uv run pytest --cov --cov-report=html
   # Add tests for red/yellow lines
   ```

5. **Dead code** (lowest priority, can defer)
   ```bash
   uv run vulture src/
   # Remove unused code
   ```

### Iterative Process

```bash
# Round 1: Fix linting
uv run ruff check --fix src/
detect-quality-regressions
# Result: 3 regressions remaining

# Round 2: Fix type errors
# (manual fixes)
detect-quality-regressions
# Result: 2 regressions remaining

# Round 3: Restore tests
git checkout baseline_commit -- tests/unit/test_user.py
detect-quality-regressions
# Result: 1 regression remaining

# Round 4: Add coverage
# (write new tests)
detect-quality-regressions
# Result: ✅ PASS
```

---

## Common Patterns

### Pattern 1: Refactoring Regressions

**Symptoms:** All metrics regressed during refactoring

**Cause:** Refactoring broke tests, removed coverage, introduced type errors

**Fix:**
1. Revert refactoring
2. Refactor incrementally (one file at a time)
3. Run regression detection after each file
4. Fix regressions before continuing

### Pattern 2: Test Removal Cascade

**Symptoms:** Tests decreased, coverage decreased

**Cause:** Removed tests → uncovered code

**Fix:**
1. Restore tests
2. Or add new tests for coverage
3. Don't remove tests without replacement

### Pattern 3: Import Cleanup Gone Wrong

**Symptoms:** Type errors increased, linting increased

**Cause:** Removed imports that were actually used

**Fix:**
1. Restore removed imports
2. Use ruff --fix (smarter than manual removal)
3. Verify code still works

---

## Quick Reference

| Regression | First Fix To Try | Time to Fix |
|------------|-----------------|-------------|
| Linting +2 | `ruff check --fix` | <1 min |
| Dead code +1% | `ruff check --fix` (imports) | <5 min |
| Type errors +1 | Check error message, fix type | 5-15 min |
| Tests -2 | Restore from git or fix failures | 10-30 min |
| Coverage -3% | Add tests for uncovered code | 20-60 min |

---

## Summary

**Key Principles:**

1. **Understand root cause** before fixing
2. **Fix in priority order** (linting → type → tests → coverage → dead code)
3. **Verify fix** by re-running regression detection
4. **Prevent future regressions** with pre-commit hooks and CI/CD
5. **Document intentional changes** when updating baseline

**Most regressions are easy to fix:**
- 80% of linting errors auto-fixable
- 60% of type errors fixable in <5 min
- 90% of dead code removable safely

**The skill makes fixing easy by:**
- Identifying exact file:line locations
- Categorizing by severity
- Suggesting specific fix actions
- Verifying fixes with re-run
