# Metrics Parsing Guide

Detailed guide for extracting quality metrics from tool outputs.

---

## Overview

**Quality checks produce different output formats. This guide provides:**
- Regex patterns for each metric
- Example outputs and expected parsing results
- Fallback strategies when parsing fails
- Common parsing issues and solutions

**Tools covered:**
1. **pytest** - Test execution and coverage
2. **pyright** - Type checking
3. **ruff** - Linting
4. **vulture** - Dead code detection
5. **check_all.sh** - Combined output

---

## 1. Test Metrics (pytest)

### Expected Output Format

**Successful run:**
```
===== test session starts =====
platform darwin -- Python 3.11.5, pytest-7.4.2, pluggy-1.3.0
collected 147 items

tests/test_auth.py ........                                   [ 10%]
tests/test_profile.py ............                            [ 25%]
tests/test_settings.py .................                      [ 50%]
...

===== 145 passed, 2 skipped in 8.34s =====
```

**With failures:**
```
===== FAILURES =====
_____ test_login _____
...
===== 140 passed, 5 failed, 2 skipped in 9.12s =====
```

### Parsing Patterns

**Test count (passed):**
```bash
# Pattern: "X passed"
PASSED=$(echo "$OUTPUT" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" | head -1)

# Example input: "145 passed, 2 skipped in 8.34s"
# Extracted: 145
```

**Test count (failed):**
```bash
# Pattern: "X failed"
FAILED=$(echo "$OUTPUT" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" | head -1)

# Example input: "140 passed, 5 failed, 2 skipped"
# Extracted: 5

# Default if not found: 0
FAILED=${FAILED:-0}
```

**Test count (skipped):**
```bash
# Pattern: "X skipped"
SKIPPED=$(echo "$OUTPUT" | grep -oE "[0-9]+ skipped" | grep -oE "[0-9]+" | head -1)

# Example input: "145 passed, 2 skipped in 8.34s"
# Extracted: 2

# Default if not found: 0
SKIPPED=${SKIPPED:-0}
```

**Execution time:**
```bash
# Pattern: "in X.XXs"
EXEC_TIME=$(echo "$OUTPUT" | grep -oE "in [0-9]+\.[0-9]+s" | grep -oE "[0-9]+\.[0-9]+" | head -1)

# Example input: "145 passed, 2 skipped in 8.34s"
# Extracted: 8.34

# Round to integer for simplicity
EXEC_TIME=$(printf "%.0f" "$EXEC_TIME")
# Result: 8
```

### Fallback Strategy

**If parsing fails (empty result):**
```bash
# Check if pytest ran successfully
if [ -z "$PASSED" ]; then
    # Try alternative pattern (older pytest versions)
    PASSED=$(echo "$OUTPUT" | grep -oE "passed=[0-9]+" | grep -oE "[0-9]+")
fi

# If still empty, check exit code
if [ -z "$PASSED" ] && [ $EXIT_CODE -eq 0 ]; then
    # Pytest succeeded but parsing failed
    # Store raw output and report parsing issue
    echo "⚠️ Test count parsing failed. Raw output:"
    echo "$OUTPUT"
fi
```

### Example Parsing Function

```bash
parse_pytest_output() {
    local output="$1"

    # Extract metrics
    local passed=$(echo "$output" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" | head -1)
    local failed=$(echo "$output" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" | head -1)
    local skipped=$(echo "$output" | grep -oE "[0-9]+ skipped" | grep -oE "[0-9]+" | head -1)
    local exec_time=$(echo "$output" | grep -oE "in [0-9]+\.[0-9]+s" | grep -oE "[0-9]+\.[0-9]+" | head -1)

    # Defaults
    passed=${passed:-0}
    failed=${failed:-0}
    skipped=${skipped:-0}
    exec_time=${exec_time:-0}

    # Round execution time
    exec_time=$(printf "%.0f" "$exec_time" 2>/dev/null || echo "0")

    # Output JSON
    cat <<EOF
{
  "passed": $passed,
  "failed": $failed,
  "skipped": $skipped,
  "execution_time": $exec_time
}
EOF
}
```

---

## 2. Coverage Metrics (pytest-cov)

### Expected Output Format

**With --cov-report=term:**
```
---------- coverage: platform darwin, python 3.11.5 -----------
Name                                Stmts   Miss  Cover
-------------------------------------------------------
src/your_project/__init__.py      12      2    83%
src/your_project/config.py        45      5    89%
src/your_project/main.py         123     15    88%
-------------------------------------------------------
TOTAL                                1234    156    87%
```

### Parsing Patterns

**Coverage percentage:**
```bash
# Pattern: "TOTAL ... X%"
COVERAGE=$(echo "$OUTPUT" | grep "^TOTAL" | grep -oE "[0-9]+%" | head -1 | grep -oE "[0-9]+")

# Example input: "TOTAL                                1234    156    87%"
# Extracted: 87
```

**Alternative pattern (if TOTAL line differs):**
```bash
# Pattern: Last percentage in TOTAL line
COVERAGE=$(echo "$OUTPUT" | grep "^TOTAL" | awk '{print $NF}' | grep -oE "[0-9]+")

# Example input: "TOTAL   1234   156   87%"
# Extracted: 87
```

### Fallback Strategy

**If parsing fails:**
```bash
if [ -z "$COVERAGE" ]; then
    # Try to find any percentage in coverage output
    COVERAGE=$(echo "$OUTPUT" | grep -E "coverage|TOTAL" | grep -oE "[0-9]+%" | tail -1 | grep -oE "[0-9]+")
fi

# If still empty, report issue
if [ -z "$COVERAGE" ]; then
    echo "⚠️ Coverage parsing failed. Raw output:"
    echo "$OUTPUT" | grep -A5 "coverage:"
    COVERAGE="N/A"
fi
```

### Example Parsing Function

```bash
parse_coverage_output() {
    local output="$1"

    # Extract coverage percentage
    local coverage=$(echo "$output" | grep "^TOTAL" | grep -oE "[0-9]+%" | head -1 | grep -oE "[0-9]+")

    # Fallback: Try alternative patterns
    if [ -z "$coverage" ]; then
        coverage=$(echo "$output" | grep "TOTAL" | awk '{print $NF}' | grep -oE "[0-9]+")
    fi

    # Default
    coverage=${coverage:-0}

    # Output
    echo "$coverage"
}
```

---

## 3. Type Errors (pyright)

### Expected Output Format

**No errors:**
```
0 errors, 0 warnings, 0 informations
```

**With errors:**
```
src/your_project/auth.py
  /path/to/auth.py:45:12 - error: Type "None" is not assignable to type "str" (reportGeneralTypeIssues)
  /path/to/auth.py:67:8 - error: Argument missing for parameter "user_id" (reportCallIssue)

src/your_project/config.py
  /path/to/config.py:23:5 - error: "dict" object is not subscriptable (reportGeneralTypeIssues)

3 errors, 0 warnings, 0 informations
```

### Parsing Patterns

**Error count:**
```bash
# Pattern: "X errors"
TYPE_ERRORS=$(echo "$OUTPUT" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" | head -1)

# Example input: "3 errors, 0 warnings, 0 informations"
# Extracted: 3

# Default: 0
TYPE_ERRORS=${TYPE_ERRORS:-0}
```

**Error details (for documentation):**
```bash
# Extract error lines
ERROR_LINES=$(echo "$OUTPUT" | grep " - error:" | sed 's/^[[:space:]]*//')

# Example output:
# /path/to/auth.py:45:12 - error: Type "None" is not assignable to type "str"
# /path/to/auth.py:67:8 - error: Argument missing for parameter "user_id"
# /path/to/config.py:23:5 - error: "dict" object is not subscriptable
```

**Simplified error locations:**
```bash
# Extract file:line only
ERROR_LOCATIONS=$(echo "$OUTPUT" | grep " - error:" | grep -oE "[^/]+\.py:[0-9]+")

# Example output:
# auth.py:45
# auth.py:67
# config.py:23
```

### Fallback Strategy

**If parsing fails:**
```bash
# Check exit code
if [ $EXIT_CODE -ne 0 ] && [ -z "$TYPE_ERRORS" ]; then
    # Pyright failed but error count not found
    # Count "error:" occurrences manually
    TYPE_ERRORS=$(echo "$OUTPUT" | grep -c " - error:")
fi

# If still zero but exit code indicates failure
if [ $TYPE_ERRORS -eq 0 ] && [ $EXIT_CODE -ne 0 ]; then
    TYPE_ERRORS="N/A (parsing failed, check raw output)"
fi
```

### Example Parsing Function

```bash
parse_pyright_output() {
    local output="$1"
    local exit_code="$2"

    # Extract error count
    local error_count=$(echo "$output" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" | head -1)
    error_count=${error_count:-0}

    # Extract error details
    local error_details=$(echo "$output" | grep " - error:" | sed 's/^[[:space:]]*//')

    # Simplified locations
    local error_locations=$(echo "$output" | grep " - error:" | grep -oE "[^/]+\.py:[0-9]+" | tr '\n' ', ' | sed 's/,$//')

    # Output JSON
    cat <<EOF
{
  "error_count": $error_count,
  "error_locations": "$error_locations",
  "error_details": $(echo "$error_details" | jq -Rs .)
}
EOF
}
```

---

## 4. Linting Errors (ruff)

### Expected Output Format

**No errors:**
```
All checks passed!
```

**With errors:**
```
src/your_project/auth.py:45:12: E501 Line too long (92 > 88 characters)
src/your_project/config.py:23:5: F401 'typing.Dict' imported but unused
src/your_project/main.py:67:8: E302 Expected 2 blank lines, found 1

Found 3 errors.
```

### Parsing Patterns

**Error count:**
```bash
# Pattern: "Found X errors"
LINTING_ERRORS=$(echo "$OUTPUT" | grep -oE "Found [0-9]+ error" | grep -oE "[0-9]+" | head -1)

# Example input: "Found 3 errors."
# Extracted: 3

# Alternative: Count error lines
if [ -z "$LINTING_ERRORS" ]; then
    LINTING_ERRORS=$(echo "$OUTPUT" | grep -cE ":[0-9]+:[0-9]+: [A-Z][0-9]+ ")
fi

# Default: 0
LINTING_ERRORS=${LINTING_ERRORS:-0}
```

**Error details:**
```bash
# Extract error lines
ERROR_LINES=$(echo "$OUTPUT" | grep -E ":[0-9]+:[0-9]+: [A-Z][0-9]+ ")

# Example output:
# src/your_project/auth.py:45:12: E501 Line too long (92 > 88 characters)
# src/your_project/config.py:23:5: F401 'typing.Dict' imported but unused
```

### Fallback Strategy

**If parsing fails:**
```bash
# Check exit code and output
if [ $EXIT_CODE -ne 0 ] && [ -z "$LINTING_ERRORS" ]; then
    # Ruff failed, count lines with error codes
    LINTING_ERRORS=$(echo "$OUTPUT" | grep -cE ":[0-9]+:[0-9]+: [A-Z][0-9]+ ")
fi

# Check for "All checks passed"
if echo "$OUTPUT" | grep -q "All checks passed"; then
    LINTING_ERRORS=0
fi
```

### Example Parsing Function

```bash
parse_ruff_output() {
    local output="$1"
    local exit_code="$2"

    # Check for success message
    if echo "$output" | grep -q "All checks passed"; then
        echo '{"error_count": 0, "status": "clean"}'
        return
    fi

    # Extract error count
    local error_count=$(echo "$output" | grep -oE "Found [0-9]+ error" | grep -oE "[0-9]+" | head -1)

    # Fallback: Count error lines
    if [ -z "$error_count" ]; then
        error_count=$(echo "$output" | grep -cE ":[0-9]+:[0-9]+: [A-Z][0-9]+ ")
    fi

    error_count=${error_count:-0}

    # Extract error details
    local error_details=$(echo "$output" | grep -E ":[0-9]+:[0-9]+: [A-Z][0-9]+ ")

    # Output JSON
    cat <<EOF
{
  "error_count": $error_count,
  "status": "$([ $error_count -eq 0 ] && echo "clean" || echo "errors")",
  "error_details": $(echo "$error_details" | jq -Rs .)
}
EOF
}
```

---

## 5. Dead Code (vulture)

### Expected Output Format

**No unused code:**
```
# (empty output or no findings)
```

**With unused code:**
```
src/your_project/auth.py:45: unused function 'validate_token' (60% confidence)
src/your_project/config.py:23: unused variable 'DEBUG_MODE' (60% confidence)
src/your_project/main.py:67: unused import 'typing' (90% confidence)
```

### Parsing Patterns

**Dead code count:**
```bash
# Count lines with "unused"
DEAD_CODE=$(echo "$OUTPUT" | grep -c "unused")

# Example input: 3 lines with "unused"
# Extracted: 3

# Default: 0
DEAD_CODE=${DEAD_CODE:-0}
```

**Alternative: Filter by confidence**
```bash
# Only count high-confidence (>= 80%)
DEAD_CODE=$(echo "$OUTPUT" | grep "unused" | grep -E "\([8-9][0-9]% confidence\)" | wc -l | xargs)

# Example: Only lines with 80%+ confidence
```

**Dead code details:**
```bash
# Extract unused items
UNUSED_ITEMS=$(echo "$OUTPUT" | grep "unused" | sed 's/^[[:space:]]*//')

# Example output:
# src/your_project/auth.py:45: unused function 'validate_token' (60% confidence)
# src/your_project/config.py:23: unused variable 'DEBUG_MODE' (60% confidence)
```

### Fallback Strategy

**If vulture not installed:**
```bash
if ! command -v vulture &> /dev/null; then
    echo "⚠️ Vulture not installed. Dead code detection skipped."
    DEAD_CODE="N/A"
fi
```

**If output is empty:**
```bash
if [ -z "$OUTPUT" ]; then
    # Empty output = no dead code found
    DEAD_CODE=0
fi
```

### Example Parsing Function

```bash
parse_vulture_output() {
    local output="$1"

    # Count unused items
    local dead_code_count=$(echo "$output" | grep -c "unused")
    dead_code_count=${dead_code_count:-0}

    # High-confidence items (80%+)
    local high_confidence=$(echo "$output" | grep "unused" | grep -cE "\([8-9][0-9]% confidence\)")
    high_confidence=${high_confidence:-0}

    # Extract details
    local unused_items=$(echo "$output" | grep "unused" | sed 's/^[[:space:]]*//')

    # Output JSON
    cat <<EOF
{
  "dead_code_count": $dead_code_count,
  "high_confidence_count": $high_confidence,
  "unused_items": $(echo "$unused_items" | jq -Rs .)
}
EOF
}
```

---

## 6. Combined Output (check_all.sh)

### Expected Output Format

**check_all.sh runs all checks in parallel and aggregates results.**

**Sample output:**
```
Running quality checks...

[1/5] Running tests...
===== 145 passed, 2 skipped in 8.34s =====
TOTAL                                1234    156    87%

[2/5] Running type checking...
0 errors, 0 warnings, 0 informations

[3/5] Running linting...
All checks passed!

[4/5] Running dead code detection...
src/your_project/auth.py:45: unused function 'validate_token'
Found 3 unused items.

[5/5] All checks complete.

Summary:
- Tests: 145 passed, 2 skipped
- Coverage: 87%
- Type errors: 0
- Linting: Clean
- Dead code: 3 items
- Total time: 9s
```

### Parsing Patterns

**Extract individual sections:**
```bash
# Split output by section headers
TESTS_OUTPUT=$(echo "$OUTPUT" | sed -n '/\[1\/5\] Running tests/,/\[2\/5\]/p')
PYRIGHT_OUTPUT=$(echo "$OUTPUT" | sed -n '/\[2\/5\] Running type checking/,/\[3\/5\]/p')
RUFF_OUTPUT=$(echo "$OUTPUT" | sed -n '/\[3\/5\] Running linting/,/\[4\/5\]/p')
VULTURE_OUTPUT=$(echo "$OUTPUT" | sed -n '/\[4\/5\] Running dead code/,/\[5\/5\]/p')
```

**Parse each section using individual functions:**
```bash
# Parse tests
TESTS_JSON=$(parse_pytest_output "$TESTS_OUTPUT")

# Parse coverage
COVERAGE=$(parse_coverage_output "$TESTS_OUTPUT")

# Parse type errors
PYRIGHT_JSON=$(parse_pyright_output "$PYRIGHT_OUTPUT" $PYRIGHT_EXIT_CODE)

# Parse linting
RUFF_JSON=$(parse_ruff_output "$RUFF_OUTPUT" $RUFF_EXIT_CODE)

# Parse dead code
VULTURE_JSON=$(parse_vulture_output "$VULTURE_OUTPUT")
```

**Extract summary (if available):**
```bash
# Extract summary section
SUMMARY=$(echo "$OUTPUT" | sed -n '/^Summary:/,$p')

# Parse summary lines
TESTS_SUMMARY=$(echo "$SUMMARY" | grep "Tests:" | sed 's/^- Tests: //')
COVERAGE_SUMMARY=$(echo "$SUMMARY" | grep "Coverage:" | grep -oE "[0-9]+")
TYPE_ERRORS_SUMMARY=$(echo "$SUMMARY" | grep "Type errors:" | grep -oE "[0-9]+")
```

### Fallback Strategy

**If check_all.sh doesn't exist:**
```bash
if [ ! -f "./scripts/check_all.sh" ]; then
    # Run individual checks
    uv run pytest tests/ -v --cov=src > /tmp/pytest-output.txt 2>&1
    uv run pyright src/ > /tmp/pyright-output.txt 2>&1
    uv run ruff check src/ > /tmp/ruff-output.txt 2>&1
    uv run vulture src/ > /tmp/vulture-output.txt 2>&1

    # Parse individual outputs
fi
```

---

## Common Parsing Issues

### Issue 1: Output Format Changed

**Problem:** Tool updated, output format differs from expected.

**Example:**
```bash
# Old format: "145 passed, 2 skipped in 8.34s"
# New format: "passed=145 skipped=2 time=8.34s"
```

**Solution:**
```bash
# Try multiple patterns
PASSED=$(echo "$OUTPUT" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" | head -1)
if [ -z "$PASSED" ]; then
    PASSED=$(echo "$OUTPUT" | grep -oE "passed=[0-9]+" | grep -oE "[0-9]+")
fi
```

### Issue 2: Empty Output

**Problem:** Command ran but produced no output.

**Example:**
```bash
# vulture src/ produces no output (no dead code found)
OUTPUT=""
```

**Solution:**
```bash
# Empty output != failure for some tools
if [ -z "$OUTPUT" ]; then
    case "$TOOL" in
        vulture)
            # Empty = no dead code
            DEAD_CODE=0
            ;;
        ruff)
            # Empty = all checks passed
            LINTING_ERRORS=0
            ;;
        *)
            # Empty = parsing failed, investigate
            echo "⚠️ Empty output from $TOOL"
            ;;
    esac
fi
```

### Issue 3: Multi-line Matches

**Problem:** Metric spans multiple lines.

**Example:**
```bash
# Coverage output:
# TOTAL                                1234
#                                            156    87%
```

**Solution:**
```bash
# Use multi-line grep or awk
COVERAGE=$(echo "$OUTPUT" | awk '/^TOTAL/{getline; print $NF}' | grep -oE "[0-9]+")
```

### Issue 4: Locale Issues

**Problem:** Numbers formatted differently (1,234 vs 1234).

**Example:**
```bash
# Some locales use comma separators
# "TOTAL 1,234 156 87%"
```

**Solution:**
```bash
# Remove commas before parsing
CLEAN_OUTPUT=$(echo "$OUTPUT" | tr -d ',')
COVERAGE=$(echo "$CLEAN_OUTPUT" | grep "^TOTAL" | grep -oE "[0-9]+%" | grep -oE "[0-9]+")
```

---

## Complete Parsing Script

**Comprehensive script combining all patterns:**

```bash
#!/bin/bash
# parse-quality-metrics.sh
# Extracts all quality metrics from check_all.sh output

set -euo pipefail

OUTPUT_FILE="$1"
OUTPUT=$(cat "$OUTPUT_FILE")

# Parse tests
PASSED=$(echo "$OUTPUT" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" | head -1 || echo "0")
FAILED=$(echo "$OUTPUT" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" | head -1 || echo "0")
SKIPPED=$(echo "$OUTPUT" | grep -oE "[0-9]+ skipped" | grep -oE "[0-9]+" | head -1 || echo "0")

# Parse coverage
COVERAGE=$(echo "$OUTPUT" | grep "^TOTAL" | grep -oE "[0-9]+%" | head -1 | grep -oE "[0-9]+" || echo "0")

# Parse type errors
TYPE_ERRORS=$(echo "$OUTPUT" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" | head -1 || echo "0")

# Parse linting
if echo "$OUTPUT" | grep -q "All checks passed"; then
    LINTING_ERRORS=0
else
    LINTING_ERRORS=$(echo "$OUTPUT" | grep -oE "Found [0-9]+ error" | grep -oE "[0-9]+" | head -1 || echo "0")
fi

# Parse dead code
DEAD_CODE=$(echo "$OUTPUT" | grep -c "unused" || echo "0")

# Parse execution time
EXEC_TIME=$(echo "$OUTPUT" | grep -oE "Total time: [0-9]+s" | grep -oE "[0-9]+" | head -1 || echo "0")

# Output JSON
cat <<EOF
{
  "tests": {
    "passed": $PASSED,
    "failed": $FAILED,
    "skipped": $SKIPPED
  },
  "coverage": $COVERAGE,
  "type_errors": $TYPE_ERRORS,
  "linting_errors": $LINTING_ERRORS,
  "dead_code": $DEAD_CODE,
  "execution_time": $EXEC_TIME
}
EOF
```

**Usage:**
```bash
./scripts/check_all.sh > /tmp/quality-output.txt 2>&1
./parse-quality-metrics.sh /tmp/quality-output.txt
```

---

## Summary

**Metrics covered:**
1. ✅ Tests (passed, failed, skipped, execution time)
2. ✅ Coverage (percentage)
3. ✅ Type errors (count, locations, details)
4. ✅ Linting errors (count, details)
5. ✅ Dead code (count, unused items)
6. ✅ Combined output (check_all.sh)

**Parsing strategies:**
- ✅ Primary patterns (most common formats)
- ✅ Fallback patterns (alternative formats)
- ✅ Error handling (empty output, parsing failures)
- ✅ Manual extraction (when patterns fail)

**Common issues addressed:**
- ✅ Format changes (multiple patterns)
- ✅ Empty output (distinguish from failure)
- ✅ Multi-line matches (awk, sed)
- ✅ Locale issues (number formatting)

---

**Last Updated:** 2025-10-16
**Version:** 1.0.0
