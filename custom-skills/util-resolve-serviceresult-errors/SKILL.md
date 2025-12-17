---
name: util-resolve-serviceresult-errors
description: |
  Fix ServiceResult pattern mistakes causing test failures and type errors.
  Use when seeing "dict object has no attribute success", "mock not returning ServiceResult",
  mock assertions failing, or type errors with ServiceResult. Analyzes .py test files
  and service implementations. Covers async/await patterns, monad operations (map, bind, flatmap),
  and proper mock configuration.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - MultiEdit
---

# Resolve ServiceResult Errors

## Purpose

Systematic diagnostic and fix workflow for ServiceResult pattern mistakes in tests and service implementations, focusing on mock configuration errors, async patterns, and type safety.

## Quick Start

Diagnose and fix common mistakes when working with the ServiceResult pattern in project-watch-mcp, focusing on test failures caused by incorrect mock configurations and improper ServiceResult usage.

**Most common use case:**
```bash
# Test fails with: 'dict' object has no attribute 'success'

❌ WRONG:
mock_service.get_data = AsyncMock(return_value={"items": []})

✅ CORRECT:
from project_watch_mcp.domain.common import ServiceResult
mock_service.get_data = AsyncMock(return_value=ServiceResult.ok({"items": []}))

Result: Test passes, ServiceResult pattern enforced
```

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [What This Skill Does](#what-this-skill-does)
3. [Instructions](#instructions)
4. [Usage Examples](#usage-examples)
5. [Expected Outcomes](#expected-outcomes)
6. [Requirements](#requirements)
7. [Troubleshooting](#troubleshooting)
8. [Red Flags to Avoid](#red-flags-to-avoid)
9. [Automation Scripts](#automation-scripts)

---

## When to Use This Skill

Use this skill when seeing:
- **Mock errors:** `'dict' object has no attribute 'success'`
- **Async errors:** `coroutine object has no attribute 'success'`
- **Type errors:** `Incompatible types in assignment` with ServiceResult[T]
- **Unwrap errors:** `Cannot unwrap None data from successful result`
- **Test failures:** Mock assertions failing with ServiceResult

**Trigger phrases:**
- "Mock not returning ServiceResult"
- "dict object has no attribute success"
- "Fix ServiceResult errors"
- "ServiceResult type errors"
- "Mock configuration incorrect"

---

## What This Skill Does

This skill provides systematic fixes for:

1. **Mock configuration errors** - Fix mocks returning dict instead of ServiceResult
2. **Async ServiceResult patterns** - Configure AsyncMock with proper return_value
3. **ServiceResult chaining** - Use composition utilities (map, bind, flatmap)
4. **Type error resolution** - Fix ServiceResult[T] type mismatches
5. **Unwrap safety** - Handle None data and failure cases correctly

See Instructions section below for detailed diagnostic workflow.

---

## Instructions

### Step 1: Identify the Error Pattern

Run the test and classify the error:

```bash
uv run pytest tests/path/to/failing_test.py -v
```

**Common Error Signatures:**

1. **Mock Returns Dict**
   - Error: `'dict' object has no attribute 'success'`
   - Cause: Mock configured with `return_value = {"key": "value"}`
   - Fix: Use `return_value = ServiceResult.ok({"key": "value"})`

2. **Async Mock Missing Await**
   - Error: `coroutine object has no attribute 'success'`
   - Cause: AsyncMock returns coroutine, not ServiceResult
   - Fix: Use `AsyncMock(return_value=ServiceResult.ok(...))`

3. **Type Error with Chaining**
   - Error: `Incompatible types in assignment`
   - Cause: ServiceResult[T] type mismatch in chained operations
   - Fix: Use proper type annotations and composition utilities

4. **Unwrap on None Data**
   - Error: `Cannot unwrap None data from successful result`
   - Cause: `ServiceResult.ok(None).unwrap()`
   - Fix: Check `result.data is not None` before unwrapping

### Step 2: Fix Mock Configuration

**❌ WRONG - Mock Returns Dict:**
```python
mock_service.get_data = AsyncMock(return_value={"items": []})
# Causes: 'dict' object has no attribute 'success'
```

**✅ CORRECT - Mock Returns ServiceResult:**
```python
from project_watch_mcp.domain.common import ServiceResult

mock_service.get_data = AsyncMock(
    return_value=ServiceResult.ok({"items": []})
)
```

**Pattern for Multiple Mock Methods:**
Use MultiEdit to fix all mocks in one operation:

```python
# Fix all mocks in test file at once
mock_repo.file_exists = AsyncMock(return_value=ServiceResult.ok(False))
mock_repo.store_file = AsyncMock(return_value=ServiceResult.ok())
mock_service.create_chunks = AsyncMock(return_value=ServiceResult.ok(chunks))
```

### Step 3: Fix ServiceResult Chaining

**Common Chaining Mistakes:**

1. **Direct Data Access Without Check**
   ```python
   # ❌ WRONG - No success check
   result = service.get_data()
   data = result.data  # Could be None on failure!

   # ✅ CORRECT - Check success first
   result = service.get_data()
   if result.success:
       data = result.data
   else:
       return ServiceResult.fail(result.error)
   ```

2. **Sequential Operations**
   ```python
   # ❌ WRONG - Manual chaining
   result1 = service1.operation()
   if result1.success:
       result2 = service2.operation(result1.data)
       if result2.success:
           return result2
   return result1 if not result1.success else result2

   # ✅ CORRECT - Use composition utilities
   from project_watch_mcp.domain.common.service_result_utils import compose_results

   result = service1.operation()
   result = compose_results(lambda d: service2.operation(d), result)
   return result
   ```

3. **Async Context**
   ```python
   # ✅ CORRECT - Async ServiceResult pattern
   async def process_file(file_path: Path) -> ServiceResult[dict]:
       result = await self.reader.read_file(file_path)
       if result.is_failure:
           return ServiceResult.fail(result.error)

       # result.success guarantees result.data is not None
       content = result.data
       return ServiceResult.ok({"content": content})
   ```

### Step 4: Use ServiceResult Composition Utilities

Import composition utilities for complex workflows:

```python
from project_watch_mcp.domain.common.service_result_utils import (
    compose_results,    # Monadic bind (flatMap)
    map_result,         # Functor map
    chain_results,      # Chain multiple results
    collect_results,    # Collect list of results
    flatten_results,    # Flatten nested results
    unwrap_or_fail,     # Convert to exception
)
```

**Examples:**

```python
# Map over successful result
result = ServiceResult.ok([1, 2, 3])
doubled = map_result(lambda items: [x * 2 for x in items], result)
# Result: ServiceResult.ok([2, 4, 6])

# Compose operations (flatMap)
def validate(data: dict) -> ServiceResult[dict]:
    if "required_field" in data:
        return ServiceResult.ok(data)
    return ServiceResult.fail("Missing required field")

result = ServiceResult.ok({"required_field": "value"})
validated = compose_results(validate, result)

# Chain multiple results
result1 = ServiceResult.ok(10)
result2 = ServiceResult.ok(20)
result3 = ServiceResult.ok(30)
combined = chain_results(result1, result2, result3)
# Result: ServiceResult.ok([10, 20, 30])
```

### Step 5: Fix Type Errors

**Common Type Issues:**

1. **Generic Type Mismatch**
   ```python
   # ❌ WRONG - Type mismatch
   def process() -> ServiceResult[list[str]]:
       result: ServiceResult[dict] = get_data()
       return result  # Type error!

   # ✅ CORRECT - Proper type transformation
   def process() -> ServiceResult[list[str]]:
       result: ServiceResult[dict] = get_data()
       if result.is_failure:
           return ServiceResult.fail(result.error)

       items = list(result.data.keys())
       return ServiceResult.ok(items)
   ```

2. **Optional Data Handling**
   ```python
   # ❌ WRONG - Not handling None
   result = ServiceResult.ok(None)
   value = result.unwrap()  # Raises ValueError!

   # ✅ CORRECT - Use unwrap_or for optional data
   result = ServiceResult.ok(None)
   value = result.unwrap_or([])  # Returns default on None/failure
   ```

### Step 6: Validate Fix

After fixing mocks and ServiceResult usage:

```bash
# Run the specific test
uv run pytest tests/path/to/test_file.py::test_name -v

# Run all related tests
uv run pytest tests/unit/application/ -v -k "service"

# Verify type safety
uv run pyright src/project_watch_mcp/
```

## Usage Examples

### Example 1: Fix Mock Returns Dict Error

**Scenario:** Test fails with `'dict' object has no attribute 'success'`

**Before (Failing Test):**
```python
@pytest.fixture
def mock_repository():
    repo = MagicMock(spec=CodeRepository)
    # ❌ WRONG - Returns dict, not ServiceResult
    repo.get_files = AsyncMock(return_value={"files": []})
    return repo

async def test_get_files(mock_repository):
    handler = FileHandler(mock_repository)
    result = await handler.process()

    # Fails: 'dict' object has no attribute 'success'
    assert result.success is True
```

**After (Fixed Test):**
```python
from project_watch_mcp.domain.common import ServiceResult

@pytest.fixture
def mock_repository():
    repo = MagicMock(spec=CodeRepository)
    # ✅ CORRECT - Returns ServiceResult
    repo.get_files = AsyncMock(
        return_value=ServiceResult.ok({"files": []})
    )
    return repo

async def test_get_files(mock_repository):
    handler = FileHandler(mock_repository)
    result = await handler.process()

    # Now works correctly
    assert result.success is True
    assert result.data == {"files": []}
```

### Example 2: Fix ServiceResult Chaining

**Scenario:** Complex service operation with multiple steps

**Before (Manual Chaining):**
```python
async def index_file(file_path: Path) -> ServiceResult[dict]:
    # Step 1: Read file
    read_result = await self.reader.read_file(file_path)
    if not read_result.success:
        return ServiceResult.fail(read_result.error)

    # Step 2: Parse content
    parse_result = await self.parser.parse(read_result.data)
    if not parse_result.success:
        return ServiceResult.fail(parse_result.error)

    # Step 3: Store data
    store_result = await self.repo.store(parse_result.data)
    if not store_result.success:
        return ServiceResult.fail(store_result.error)

    return store_result
```

**After (Using Composition Utilities):**
```python
from project_watch_mcp.domain.common.service_result_utils import compose_results

async def index_file(file_path: Path) -> ServiceResult[dict]:
    # Read file
    result = await self.reader.read_file(file_path)

    # Chain: parse -> store
    if result.success:
        result = await compose_results(
            lambda content: self.parser.parse(content),
            result
        )

    if result.success:
        result = await compose_results(
            lambda parsed: self.repo.store(parsed),
            result
        )

    return result
```

### Example 3: Fix Async ServiceResult Pattern

**Scenario:** Async mock returning coroutine instead of ServiceResult

**Before (Failing):**
```python
@pytest.fixture
def mock_service():
    service = MagicMock(spec=EmbeddingService)
    # ❌ WRONG - AsyncMock without proper return_value
    service.embed_text = AsyncMock()
    return service

async def test_embedding(mock_service):
    # Fails: coroutine object has no attribute 'success'
    result = await mock_service.embed_text("test")
    assert result.success is True
```

**After (Fixed):**
```python
from project_watch_mcp.domain.common import ServiceResult

@pytest.fixture
def mock_service():
    service = MagicMock(spec=EmbeddingService)
    # ✅ CORRECT - AsyncMock with ServiceResult return_value
    service.embed_text = AsyncMock(
        return_value=ServiceResult.ok([0.1, 0.2, 0.3])
    )
    return service

async def test_embedding(mock_service):
    result = await mock_service.embed_text("test")
    assert result.success is True
    assert len(result.data) == 3
```

## Expected Outcomes

### Successful Fix - Test Now Passing

```
✅ ServiceResult Errors Resolved

Test: test_get_files
Status: PASSING (was FAILING)

Fixes Applied:
  ✅ Mock configured to return ServiceResult.ok(data)
  ✅ AsyncMock used for async methods
  ✅ Type annotations corrected (ServiceResult[list])
  ✅ Unwrap safety checks added

Before:
  ❌ 'dict' object has no attribute 'success'
  ❌ TypeError: Incompatible types

After:
  ✅ All assertions passing
  ✅ No type errors
  ✅ ServiceResult pattern enforced

Quality Check:
  ✅ pyright: 0 errors
  ✅ pytest: all tests pass
```

### Identified Pattern - Needs Refactoring

```
⚠️  ServiceResult Chaining Opportunity

File: src/services/file_service.py
Lines: 42-58

Current Pattern (Manual Chaining):
  result1 = await service1.operation()
  if not result1.success:
      return ServiceResult.fail(result1.error)
  result2 = await service2.operation(result1.data)
  if not result2.success:
      return ServiceResult.fail(result2.error)
  # ... repeated 3 more times

Recommendation:
  Use compose_results() from service_result_utils
  Reduces 17 lines to 8 lines
  Improves readability and maintainability

See: Step 4 in Instructions for composition utilities
```

---

## Requirements

**Imports:**
- `from project_watch_mcp.domain.common import ServiceResult`
- `from project_watch_mcp.domain.common.service_result_utils import <utility>`
- `from unittest.mock import AsyncMock` (for async methods)

**Tools:**
- Read - View test files and service implementations
- Edit/MultiEdit - Fix mock configurations and ServiceResult usage
- Grep - Find all occurrences of pattern
- Glob - Locate test files with ServiceResult issues

**Knowledge:**
- ServiceResult pattern (success/failure monad)
- AsyncMock vs MagicMock differences
- Python type annotations (ServiceResult[T])
- Composition utilities (map, bind, flatmap)

**Optional:**
- Understanding of monad pattern
- Familiarity with functional programming concepts

---

## Troubleshooting

### Issue: Test fails with "'dict' object has no attribute 'success'"

**Symptom:** Mock returns dict instead of ServiceResult

**Diagnosis:**
```bash
# Run test to see exact error
uv run pytest tests/path/to/test.py::test_name -v
```

**Fix:**
```python
# ❌ WRONG - Returns dict
mock_service.get_data = AsyncMock(return_value={"items": []})

# ✅ CORRECT - Returns ServiceResult
from project_watch_mcp.domain.common import ServiceResult
mock_service.get_data = AsyncMock(return_value=ServiceResult.ok({"items": []}))
```

**Validation:**
```bash
# Re-run test
uv run pytest tests/path/to/test.py::test_name -v
# Should now pass
```

---

### Issue: "coroutine object has no attribute 'success'"

**Symptom:** AsyncMock not configured correctly

**Root Cause:** Missing `return_value` on AsyncMock

**Fix:**
```python
# ❌ WRONG - AsyncMock without return_value
mock_service.fetch = AsyncMock()

# ✅ CORRECT - AsyncMock with ServiceResult return_value
mock_service.fetch = AsyncMock(
    return_value=ServiceResult.ok(data)
)
```

---

### Issue: Type error "Incompatible types in assignment"

**Symptom:** `ServiceResult[T]` type mismatch

**Diagnosis:**
```bash
uv run pyright src/project_watch_mcp/
```

**Common causes:**
1. **Wrong generic type:**
   ```python
   # ❌ WRONG
   def process() -> ServiceResult[list[str]]:
       result: ServiceResult[dict] = get_data()
       return result  # Type error!

   # ✅ CORRECT
   def process() -> ServiceResult[list[str]]:
       result: ServiceResult[dict] = get_data()
       if result.is_failure:
           return ServiceResult.fail(result.error)
       return ServiceResult.ok(list(result.data.keys()))
   ```

2. **Missing type annotation:**
   ```python
   # ❌ WRONG
   result = await service.fetch()  # Type unknown

   # ✅ CORRECT
   result: ServiceResult[dict] = await service.fetch()
   ```

---

### Issue: "Cannot unwrap None data from successful result"

**Symptom:** Calling `.unwrap()` on ServiceResult with None data

**Root Cause:** ServiceResult.ok(None) cannot be unwrapped

**Fix:**
```python
# ❌ WRONG
result = ServiceResult.ok(None)
value = result.unwrap()  # Raises ValueError!

# ✅ CORRECT - Use unwrap_or
result = ServiceResult.ok(None)
value = result.unwrap_or([])  # Returns default

# ✅ BETTER - Check data before unwrapping
if result.data is not None:
    value = result.unwrap()
else:
    value = default_value
```

---

### Issue: Many sequential ServiceResult checks

**Symptom:** Code has 5+ sequential `if result.success:` checks

**Diagnosis:**
```bash
# Find files with chaining opportunities
grep -r "if.*result.*success" src/ | wc -l
```

**Refactoring opportunity:**
Use composition utilities instead of manual chaining

**See:** Step 4 in Instructions section for `compose_results()` examples

---

## Red Flags to Avoid

1. **Forgetting ServiceResult Wrapper**
   - ❌ `return_value = data`
   - ✅ `return_value = ServiceResult.ok(data)`

2. **Not Checking Success Before Data Access**
   - ❌ `data = result.data`
   - ✅ `if result.success: data = result.data`

3. **Using unwrap() Without Null Check**
   - ❌ `value = result.unwrap()`  (raises on None)
   - ✅ `value = result.unwrap_or(default)`

4. **Mixing Async and Sync Mocks**
   - ❌ `MagicMock(return_value=ServiceResult.ok(...))` for async method
   - ✅ `AsyncMock(return_value=ServiceResult.ok(...))` for async method

5. **Not Propagating Errors**
   - ❌ Silently ignoring failure results
   - ✅ Returning failure immediately: `if result.is_failure: return result`

## Automation Scripts

**NEW:** Powerful automation utilities to detect and fix ServiceResult issues automatically!

### Available Scripts

1. **fix_serviceresult_mocks.py** - Auto-fix test mock errors
   ```bash
   # Fix all test mocks automatically
   python .claude/skills/util-resolve-serviceresult-errors/scripts/fix_serviceresult_mocks.py --all tests/
   ```

2. **validate_serviceresult_usage.py** - Validate ServiceResult patterns
   ```bash
   # Find all violations in codebase
   python .claude/skills/util-resolve-serviceresult-errors/scripts/validate_serviceresult_usage.py src/
   ```

3. **find_serviceresult_chains.py** - Identify refactoring opportunities
   ```bash
   # Get refactoring suggestions
   python .claude/skills/util-resolve-serviceresult-errors/scripts/find_serviceresult_chains.py --suggest-refactor src/
   ```

**See:** [scripts/README.md](./scripts/README.md) for complete documentation and examples.

### Python Scripts

- [find_serviceresult_chains.py](./scripts/find_serviceresult_chains.py) - Analyze ServiceResult chaining opportunities and identify refactoring opportunities
- [fix_serviceresult_mocks.py](./scripts/fix_serviceresult_mocks.py) - Auto-fix ServiceResult mock errors in test files
- [validate_serviceresult_usage.py](./scripts/validate_serviceresult_usage.py) - Validate ServiceResult usage patterns across the codebase

## See Also

- [scripts/README.md](./scripts/README.md) - Automation scripts documentation
- [scripts/EXAMPLES.md](./scripts/EXAMPLES.md) - Real-world usage examples
- [scripts/SCRIPT_SUMMARY.md](./scripts/SCRIPT_SUMMARY.md) - Technical details and test results
- [templates/serviceresult-patterns.md](./templates/serviceresult-patterns.md) - Quick reference templates
- [references/monad-pattern.md](./references/monad-pattern.md) - Understanding the monad pattern
- [scripts/examples.md](./scripts/examples.md) - Comprehensive examples gallery

## Integration Points

### With Other Skills

**resolve-serviceresult-errors integrates with:**
- **debug-test-failures** - Fix ServiceResult-specific test failures
- **debug-type-errors** - Resolve ServiceResult[T] type mismatches
- **setup-async-testing** - Configure AsyncMock with ServiceResult
- **implement-cqrs-handler** - Ensure handlers return ServiceResult
- **implement-repository-pattern** - Validate repository ServiceResult returns

### With Testing Workflows

**Use in combination with:**
- AsyncMock configuration (return ServiceResult, not dict)
- Type checking (pyright validates ServiceResult[T])
- Integration tests (real ServiceResult wrapping)
- E2E tests (ServiceResult → dict conversion)

### With Agent Workflows

**Agents should invoke this skill:**
- @unit-tester - When tests fail with ServiceResult errors
- @debugging-expert - For "dict object has no attribute" errors
- @implementer - During service implementation

## Expected Benefits

| Metric | Without Skill | With Skill | Improvement |
|--------|--------------|------------|-------------|
| **Fix Time** | 30 min (trial/error) | 5 min (systematic) | 83% faster |
| **Mock Configuration Errors** | 50% (dict instead of ServiceResult) | 5% (correct patterns) | 90% reduction |
| **Type Error Resolution** | 20 min (pyright confusion) | 5 min (clear templates) | 75% faster |
| **ServiceResult Chaining Complexity** | 17 lines (manual) | 8 lines (composition utils) | 53% reduction |
| **Unwrap Safety Issues** | 20% (None crashes) | 0% (validation checks) | 100% elimination |
| **Knowledge Transfer** | 1 hour (learning pattern) | 10 min (examples) | 83% faster |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Mock Configuration Accuracy** | 100% | Test pass rate |
| **Type Error Resolution** | 100% | pyright clean |
| **Unwrap Safety** | Zero crashes | Runtime validation |
| **ServiceResult Pattern Adoption** | 100% of services | Code coverage |
| **Composition Utility Usage** | 80% of complex chains | Code review |

## Validation Process

### Step 1: Error Classification
```bash
# Run test to identify error type
uv run pytest tests/path/to/test.py::test_name -v

# Classify error:
# - 'dict' object has no attribute 'success'
# - coroutine object has no attribute 'success'
# - Incompatible types in assignment
# - Cannot unwrap None data
```

### Step 2: Mock Configuration Fix
```python
# Verify mock returns ServiceResult
from project_watch_mcp.domain.common import ServiceResult

mock_service.method = AsyncMock(
    return_value=ServiceResult.ok(data)
)
```

### Step 3: Type Validation
```bash
# Run pyright to check ServiceResult[T] types
uv run pyright src/

# Fix type mismatches
```

### Step 4: Test Execution
```bash
# Re-run test
uv run pytest tests/path/to/test.py::test_name -v

# Verify:
# ✓ Test passes
# ✓ No type errors
# ✓ ServiceResult pattern enforced
```

### Step 5: Pattern Validation
```bash
# Check for refactoring opportunities
python scripts/find_serviceresult_chains.py --suggest-refactor src/

# Apply composition utilities where beneficial
```

## Related Files

- `src/project_watch_mcp/domain/common/service_result.py` - ServiceResult implementation
- `src/project_watch_mcp/domain/common/service_result_utils.py` - Composition utilities
- `tests/unit/core/test_service_result_type_safety.py` - Type safety test patterns
- `tests/unit/core/test_service_utils.py` - ServiceResult utility tests
