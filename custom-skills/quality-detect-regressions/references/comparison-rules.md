# Comparison Rules - detect-quality-regressions

This document details the metric comparison logic, tolerance rules, and rationale for regression detection.

---

## Overview

The skill compares **5 core quality metrics** against baseline values to detect regressions:

1. **Tests passed** (strict: no tolerance)
2. **Code coverage %** (tolerant: 1% drop allowed)
3. **Type errors count** (strict: no tolerance)
4. **Linting errors count** (strict: no tolerance)
5. **Dead code %** (tolerant: 2% increase allowed)

---

## Metric 1: Tests Passed

### Comparison Rule

```
PASS if: current >= baseline
FAIL if: current < baseline
```

### Tolerance

**None** - Tests must not decrease

### Rationale

- Tests should only increase or stay the same
- Removing tests is a regression (less validation)
- Failing tests should be fixed, not removed
- Test count is a direct measure of validation coverage

### Examples

| Baseline | Current | Change | Result | Reason |
|----------|---------|--------|--------|--------|
| 145 | 150 | +5 | ✅ PASS | More tests (improvement) |
| 145 | 145 | 0 | ✅ PASS | Same tests (stable) |
| 145 | 143 | -2 | ❌ FAIL | Fewer tests (regression) |

### Edge Cases

**Case 1: Tests removed because code removed**
- If code AND tests removed together (intentional)
- Still counts as regression (less validation)
- Document reason in commit message
- Consider updating baseline if intentional cleanup

**Case 2: Tests skipped**
- Skipped tests don't count toward "passed"
- Moving from passed → skipped is regression
- Skipped tests must be fixed or removed

**Case 3: Test count same but different tests**
- Baseline: 145 passed (test_a.py, test_b.py)
- Current: 145 passed (test_a.py, test_c.py)
- Skill sees: 145 == 145 → PASS
- ⚠️ Limitation: Doesn't detect test replacement
- Solution: Review git diff to see test changes

---

## Metric 2: Code Coverage %

### Comparison Rule

```
PASS if: current >= baseline - 1%
FAIL if: current < baseline - 1%
```

### Tolerance

**1%** - Small drops allowed to prevent false positives

### Rationale

- Coverage can fluctuate slightly due to:
  - Rounding differences in coverage.py
  - Minor code additions without immediate tests
  - Refactoring that temporarily affects coverage
- 1% tolerance prevents false alarms
- Larger drops (>1%) indicate insufficient testing

### Examples

| Baseline | Current | Change | Threshold | Result | Reason |
|----------|---------|--------|-----------|--------|--------|
| 88% | 90% | +2% | 87% | ✅ PASS | Coverage improved |
| 88% | 88% | 0% | 87% | ✅ PASS | Coverage stable |
| 88% | 87.5% | -0.5% | 87% | ✅ PASS | Within tolerance |
| 88% | 87% | -1% | 87% | ✅ PASS | Exactly at threshold |
| 88% | 86.5% | -1.5% | 87% | ❌ FAIL | Below threshold |
| 88% | 85% | -3% | 87% | ❌ FAIL | Significant drop |

### Edge Cases

**Case 1: Coverage drops due to new code**
- Add new feature without tests
- Coverage drops from 88% → 85%
- Result: ❌ FAIL (write tests for new code)

**Case 2: Coverage drops due to removed tests**
- Remove tests that covered code
- Coverage drops from 88% → 84%
- Result: ❌ FAIL (restore tests or remove code)

**Case 3: Coverage improves then stabilizes**
- Baseline: 88%, Current: 92% → PASS
- Update baseline to 92%
- Next change: 92% → 91.5% → PASS (within 1%)

**Case 4: Rounding edge case**
- Baseline: 87.49% (rounds to 87%)
- Current: 86.51% (rounds to 87%)
- Display shows: 87% → 87%
- Actual: 87.49% → 86.51% = -0.98% → PASS

### Calculation

```python
baseline_coverage = 88.0  # percent
tolerance = 1.0  # percent
threshold = baseline_coverage - tolerance  # 87.0%

current_coverage = 87.5  # percent
if current_coverage >= threshold:
    result = "PASS"
else:
    result = "FAIL"
```

---

## Metric 3: Type Errors Count

### Comparison Rule

```
PASS if: current <= baseline
FAIL if: current > baseline
```

### Tolerance

**None** - Type errors must not increase

### Rationale

- Type errors indicate type safety violations
- New type errors are regressions (broke type contracts)
- Type errors should only decrease or stay same
- Zero tolerance for new type errors

### Examples

| Baseline | Current | Change | Result | Reason |
|----------|---------|--------|--------|--------|
| 0 | 0 | 0 | ✅ PASS | No errors (ideal) |
| 3 | 3 | 0 | ✅ PASS | Same errors (stable) |
| 3 | 1 | -2 | ✅ PASS | Fewer errors (improvement) |
| 0 | 2 | +2 | ❌ FAIL | New errors (regression) |
| 3 | 5 | +2 | ❌ FAIL | More errors (regression) |

### Edge Cases

**Case 1: Pre-existing type errors**
- Baseline: 3 errors (documented legacy issues)
- Current: 3 errors (same issues)
- Result: ✅ PASS (no NEW errors)
- Note: Skill doesn't require fixing pre-existing issues

**Case 2: Different type errors**
- Baseline: 3 errors (file_a.py:10, file_b.py:20, file_c.py:30)
- Current: 3 errors (file_a.py:10, file_d.py:40, file_e.py:50)
- Skill sees: 3 == 3 → PASS
- ⚠️ Limitation: Doesn't detect error replacement
- Solution: Review pyright output for specific errors

**Case 3: Type errors fixed during work**
- Baseline: 3 errors
- Current: 0 errors
- Result: ✅ PASS (improvement!)
- Consider updating baseline to reflect 0 errors

**Case 4: Pyright version upgrade**
- Upgrade pyright: v1.1.0 → v1.2.0
- New version detects more errors
- Baseline: 0 (old pyright), Current: 5 (new pyright)
- Result: ❌ FAIL
- Solution: Fix new errors OR update baseline (document pyright upgrade)

### Severity

**Critical** - Type errors are highest severity regression

- Breaks type safety guarantees
- Can cause runtime errors
- Must be fixed before merging

### Parsing

Extract from pyright output:

```bash
$ uv run pyright

src/service.py:45 - error: Type "None" cannot be assigned to type "str"
src/helper.py:12 - error: Argument of type "int" cannot be assigned

Found 2 errors
```

**Count:** 2 errors (from "Found X errors" line or count "error:" occurrences)

---

## Metric 4: Linting Errors Count

### Comparison Rule

```
PASS if: current <= baseline
FAIL if: current > baseline
```

### Tolerance

**None** - Linting errors must not increase

### Rationale

- Linting errors indicate code quality issues
- New linting errors are regressions (degraded code quality)
- Linting errors should only decrease or stay same
- Zero tolerance for new linting violations

### Examples

| Baseline | Current | Change | Result | Reason |
|----------|---------|--------|--------|--------|
| 0 | 0 | 0 | ✅ PASS | No errors (ideal) |
| 5 | 5 | 0 | ✅ PASS | Same errors (stable) |
| 5 | 2 | -3 | ✅ PASS | Fewer errors (improvement) |
| 0 | 3 | +3 | ❌ FAIL | New errors (regression) |
| 5 | 8 | +3 | ❌ FAIL | More errors (regression) |

### Edge Cases

**Case 1: Auto-fixable linting errors**
- Current: 3 errors (all auto-fixable)
- Run: `uv run ruff check --fix`
- Re-run: 0 errors
- Result: ✅ PASS (easy fix)

**Case 2: Pre-existing linting errors**
- Baseline: 10 errors (legacy code)
- Current: 10 errors (same issues)
- Result: ✅ PASS (no NEW errors)

**Case 3: Linting rule changes**
- Update ruff config: Add new rule
- New rule detects 5 violations
- Baseline: 0 (old rules), Current: 5 (new rules)
- Result: ❌ FAIL
- Solution: Fix violations OR update baseline (document rule change)

**Case 4: False positive linting errors**
- Linter reports error but code is correct
- Add `# noqa` comment or configure linter
- Re-run: Error suppressed
- Result: ✅ PASS

### Severity

**Medium** - Linting errors are medium severity

- Affects code quality and maintainability
- Usually easy to fix (auto-fixable)
- Should be fixed before merging

### Parsing

Extract from ruff output:

```bash
$ uv run ruff check src/

src/service.py:23 - F401 [*] `logging` imported but unused
src/helper.py:45 - E501 Line too long (92 > 88 characters)

Found 2 errors
```

**Count:** 2 errors (count violation lines or "Found X errors")

---

## Metric 5: Dead Code %

### Comparison Rule

```
PASS if: current <= baseline + 2%
FAIL if: current > baseline + 2%
```

### Tolerance

**2%** - Small increases allowed due to refactoring

### Rationale

- Dead code can fluctuate during refactoring
- Temporary dead code acceptable during multi-step refactors
- 2% tolerance prevents false alarms
- Large increases (>2%) indicate unused code accumulation

### Examples

| Baseline | Current | Change | Threshold | Result | Reason |
|----------|---------|--------|-----------|--------|--------|
| 1.0% | 0.5% | -0.5% | 3.0% | ✅ PASS | Dead code reduced |
| 1.0% | 1.0% | 0% | 3.0% | ✅ PASS | Dead code stable |
| 1.0% | 2.5% | +1.5% | 3.0% | ✅ PASS | Within tolerance |
| 1.0% | 3.0% | +2.0% | 3.0% | ✅ PASS | Exactly at threshold |
| 1.0% | 3.5% | +2.5% | 3.0% | ❌ FAIL | Above threshold |
| 1.0% | 5.0% | +4.0% | 3.0% | ❌ FAIL | Significant increase |

### Edge Cases

**Case 1: Refactoring in progress**
- Refactor phase 1: Extract new methods (not yet used)
- Dead code increases temporarily
- Result: ✅ PASS (within 2% tolerance)
- Refactor phase 2: Use new methods
- Dead code returns to baseline
- Result: ✅ PASS

**Case 2: Dead code cleanup**
- Run: `uv run vulture src/ --min-confidence 80`
- Identify dead code
- Remove unused functions/imports
- Dead code: 2.5% → 0.8%
- Result: ✅ PASS (improvement)

**Case 3: False positive dead code**
- Vulture reports code as unused but it's dynamic
- Add `# type: ignore[vulture]` comment
- Or lower confidence threshold
- Re-run: Dead code reduced
- Result: ✅ PASS

**Case 4: Legacy dead code**
- Baseline: 5% dead code (legacy project)
- Current: 5% dead code (maintained)
- Result: ✅ PASS (no increase)
- Note: Baseline includes legacy dead code

### Severity

**Low** - Dead code is lowest severity (but should be cleaned up)

- Affects code maintainability
- Increases codebase size
- Should be cleaned up eventually

### Parsing

Extract from vulture output:

```bash
$ uv run vulture src/ --min-confidence 80

src/service.py:45: unused function 'helper' (60% confidence)
src/utils.py:12: unused import 'logging' (100% confidence)

Dead code: 1.2% (5 occurrences in 420 lines)
```

**Extract:** 1.2% (from "Dead code: X%" line)

---

## Tolerance Rationale

### Why Tolerance for Coverage and Dead Code?

**Coverage (1% tolerance):**
- Prevents false alarms from rounding differences
- Allows minor code additions during refactoring
- Still catches significant coverage drops (>1%)

**Dead code (2% tolerance):**
- Allows temporary dead code during multi-step refactors
- Prevents blocking on minor unused imports
- Still catches dead code accumulation (>2%)

### Why NO Tolerance for Tests, Type Errors, Linting?

**Tests (no tolerance):**
- Test removal is always intentional (should be documented)
- No false positives (test count is exact)
- Should never decrease accidentally

**Type errors (no tolerance):**
- Type errors are critical (break type safety)
- New type errors are always regressions
- Zero tolerance enforces type safety

**Linting errors (no tolerance):**
- Linting errors indicate code quality issues
- Often auto-fixable (ruff check --fix)
- Zero tolerance encourages clean code

---

## Comparison Algorithm

### Pseudocode

```python
def compare_metrics(baseline, current):
    results = {}

    # 1. Tests passed (strict)
    if current.tests >= baseline.tests:
        results['tests'] = 'PASS'
    else:
        results['tests'] = 'FAIL'

    # 2. Coverage (tolerant: 1%)
    threshold = baseline.coverage - 1.0
    if current.coverage >= threshold:
        results['coverage'] = 'PASS'
    else:
        results['coverage'] = 'FAIL'

    # 3. Type errors (strict)
    if current.type_errors <= baseline.type_errors:
        results['type_errors'] = 'PASS'
    else:
        results['type_errors'] = 'FAIL'

    # 4. Linting errors (strict)
    if current.linting <= baseline.linting:
        results['linting'] = 'PASS'
    else:
        results['linting'] = 'FAIL'

    # 5. Dead code (tolerant: 2%)
    threshold = baseline.dead_code + 2.0
    if current.dead_code <= threshold:
        results['dead_code'] = 'PASS'
    else:
        results['dead_code'] = 'FAIL'

    # Determine overall result
    if all(result == 'PASS' for result in results.values()):
        return 'PASS', results
    else:
        regressions = [k for k, v in results.items() if v == 'FAIL']
        return 'FAIL', results, regressions
```

### Example Execution

**Baseline:**
```python
baseline = {
    'tests': 145,
    'coverage': 88.0,
    'type_errors': 0,
    'linting': 0,
    'dead_code': 1.2
}
```

**Current:**
```python
current = {
    'tests': 148,
    'coverage': 87.5,
    'type_errors': 0,
    'linting': 0,
    'dead_code': 1.1
}
```

**Comparison:**
```python
# Tests: 148 >= 145 → PASS
# Coverage: 87.5 >= 87.0 (88.0 - 1.0) → PASS
# Type errors: 0 <= 0 → PASS
# Linting: 0 <= 0 → PASS
# Dead code: 1.1 <= 3.2 (1.2 + 2.0) → PASS

overall_result = 'PASS'
```

---

## Severity Levels

When regressions detected, assign severity for prioritization:

| Severity | Metrics | Priority | Fix Urgency |
|----------|---------|----------|-------------|
| **Critical** | Type errors | 1 | Fix immediately |
| **High** | Tests, Coverage (>2% drop) | 2 | Fix before merge |
| **Medium** | Linting, Coverage (1-2% drop) | 3 | Fix soon |
| **Low** | Dead code | 4 | Fix eventually |

**Fix order:**
1. Critical (type errors)
2. High (tests, significant coverage drops)
3. Medium (linting, minor coverage drops)
4. Low (dead code)

---

## Customizing Comparison Rules

### Option 1: Adjust Tolerances

**In baseline entity observations, add:**
```yaml
- Tolerance_coverage: 2%  # Increase from 1% to 2%
- Tolerance_dead_code: 5%  # Increase from 2% to 5%
```

**Skill reads tolerances from baseline (if specified) or uses defaults.**

### Option 2: Strict Mode

**Zero tolerance for ALL metrics:**
```yaml
- Strict_mode: true
```

**All metrics must match exactly (no tolerance).**

### Option 3: Custom Thresholds

**Specify absolute thresholds instead of relative:**
```yaml
- Threshold_coverage_min: 85%  # Absolute minimum (not relative to baseline)
- Threshold_type_errors_max: 5  # Allow up to 5 type errors
```

---

## Summary

| Metric | Rule | Tolerance | Rationale |
|--------|------|-----------|-----------|
| Tests passed | >= baseline | None | Test removal is regression |
| Coverage | >= baseline - 1% | 1% | Prevent false alarms |
| Type errors | <= baseline | None | Type safety critical |
| Linting | <= baseline | None | Code quality standard |
| Dead code | <= baseline + 2% | 2% | Allow refactoring |

**Overall philosophy:**
- Strict on critical metrics (type errors, tests)
- Tolerant on fluctuating metrics (coverage, dead code)
- Zero tolerance for quality degradation
- Block merges if regressions detected
