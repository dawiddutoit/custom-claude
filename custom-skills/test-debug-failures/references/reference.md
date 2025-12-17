# Debug Test Failures - Advanced Reference

## Advanced Debugging Techniques

### Technique 1: Bisection for Flaky Tests

**Problem:** Test passes sometimes, fails other times.

**Solution:** Use binary search to isolate the issue.

```bash
# Run test 10 times to confirm flakiness
for i in {1..10}; do
  echo "Run $i:"
  uv run pytest tests/test_flaky.py -v || echo "FAILED"
done

# If 5/10 fail, it's flaky
```

**Common causes:**
1. **Shared state between tests**
   - Solution: Ensure fixtures have correct scope
   - Use `--forceExit` (Jest) or `pytest-xdist` (pytest)

2. **Async timing issues**
   - Solution: Use proper awaits, not timeouts
   - Add explicit synchronization points

3. **Order dependency**
   - Solution: Run with `pytest --random-order` to find dependencies
   - Fix tests to be independent

**Debugging flaky tests:**
```bash
# pytest: randomize order
uv run pytest tests/ --random-order-bucket=global

# pytest: run in parallel (exposes shared state issues)
uv run pytest tests/ -n auto

# Jest: run serially
npm test -- --runInBand

# Jest: detect open handles
npm test -- --detectOpenHandles
```

### Technique 2: Debugging Mock Call Arguments

**Problem:** Mock called but with wrong arguments.

**Python/pytest:**
```python
# See all calls made to mock
print(mock_function.call_args_list)

# See specific call arguments
print(mock_function.call_args)

# Assert with partial matching
mock_function.assert_called_with(
    arg1="expected",
    arg2=unittest.mock.ANY  # Match any value
)

# Check call count
assert mock_function.call_count == 2
```

**JavaScript/Jest:**
```javascript
// See all calls
console.log(mockFunction.mock.calls);

// See specific call
console.log(mockFunction.mock.calls[0]);

// Assert with partial matching
expect(mockFunction).toHaveBeenCalledWith(
  expect.objectContaining({ key: 'value' })
);

// Check call count
expect(mockFunction).toHaveBeenCalledTimes(2);
```

### Technique 3: Debugging Async Issues

**Problem:** Async operations not completing before assertions.

**Python/pytest (async):**
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result.success

# Common issue: forgot @pytest.mark.asyncio
def test_async_operation():  # ❌ Missing decorator
    result = await async_function()  # SyntaxError: await outside async
```

**JavaScript/Jest:**
```javascript
// ✅ CORRECT: Return promise
test('async operation', () => {
  return asyncFunction().then(result => {
    expect(result).toBe('success');
  });
});

// ✅ CORRECT: Use async/await
test('async operation', async () => {
  const result = await asyncFunction();
  expect(result).toBe('success');
});

// ❌ WRONG: Not waiting for promise
test('async operation', () => {
  asyncFunction().then(result => {
    expect(result).toBe('success');  // Never runs!
  });
  // Test completes before promise resolves
});
```

**Debugging async timing:**
```javascript
// Add timeout
test('async operation', async () => {
  const result = await asyncFunction();
  expect(result).toBe('success');
}, 10000);  // 10 second timeout

// Or globally in jest.config.js
module.exports = {
  testTimeout: 10000
};
```

### Technique 4: Debugging Fixture Lifecycle

**Problem:** Fixture cleanup not happening correctly.

**Python/pytest:**
```python
@pytest.fixture
def resource():
    print("SETUP: Creating resource")
    res = create_resource()

    yield res  # Test runs here

    print("TEARDOWN: Cleaning up resource")
    res.cleanup()

# Run with output to see lifecycle
# pytest tests/ -v -s
```

**Fixture scope debugging:**
```python
@pytest.fixture(scope="function")  # Fresh for each test
def function_scope():
    print(f"Function scope created: {id(self)}")
    yield

@pytest.fixture(scope="class")  # Shared within test class
def class_scope():
    print(f"Class scope created: {id(self)}")
    yield

@pytest.fixture(scope="module")  # Shared within module
def module_scope():
    print(f"Module scope created: {id(self)}")
    yield

@pytest.fixture(scope="session")  # Shared across entire session
def session_scope():
    print(f"Session scope created: {id(self)}")
    yield
```

**Debugging fixture dependency order:**
```python
@pytest.fixture
def fixture_a():
    print("A setup")
    yield "A"
    print("A teardown")

@pytest.fixture
def fixture_b(fixture_a):
    print(f"B setup (depends on {fixture_a})")
    yield "B"
    print("B teardown")

def test_order(fixture_b):
    print(f"Test running with {fixture_b}")

# Output:
# A setup
# B setup (depends on A)
# Test running with B
# B teardown
# A teardown
```

### Technique 5: Debugging Test Isolation

**Problem:** Tests affect each other's state.

**Identify test isolation issues:**
```bash
# Run tests in different orders
pytest tests/ -v  # Normal order
pytest tests/ -v --reverse  # Reverse order

# If results differ, tests are not isolated
```

**Common isolation issues:**

**1. Global State:**
```python
# ❌ WRONG: Global variable modified
counter = 0

def test_increment():
    global counter
    counter += 1
    assert counter == 1  # Fails on second run!

# ✅ CORRECT: Use fixture
@pytest.fixture
def counter():
    return {"count": 0}

def test_increment(counter):
    counter["count"] += 1
    assert counter["count"] == 1
```

**2. Database State:**
```python
# ❌ WRONG: Database persists between tests
def test_create_user():
    user = User(id="123", name="Alice")
    db.save(user)
    assert db.count() == 1  # Fails if run after another test

# ✅ CORRECT: Clean database before each test
@pytest.fixture(autouse=True)
def clean_database():
    db.delete_all()
    yield
    db.delete_all()

def test_create_user():
    user = User(id="123", name="Alice")
    db.save(user)
    assert db.count() == 1
```

**3. File System State:**
```python
# ❌ WRONG: Files persist
def test_create_file():
    write_file("test.txt", "content")
    assert file_exists("test.txt")  # Fails if file exists

# ✅ CORRECT: Use temporary directory
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path)

def test_create_file(temp_dir):
    file_path = os.path.join(temp_dir, "test.txt")
    write_file(file_path, "content")
    assert file_exists(file_path)
```

### Technique 6: Debugging Parametrized Tests

**Problem:** One parameter case fails, others pass.

**Python/pytest:**
```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    ("invalid", False),
    ("edge_case", True),  # Which one fails?
])
def test_validation(input, expected):
    result = validate(input)
    assert result == expected

# Run specific parameter case
pytest tests/test_validation.py::test_validation[edge_case-True] -vv
```

**Debugging parametrized failures:**
```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    ("invalid", False),
    pytest.param("edge_case", True, marks=pytest.mark.xfail),  # Mark expected failure
])
def test_validation(input, expected):
    result = validate(input)
    assert result == expected
```

**JavaScript/Jest:**
```javascript
test.each([
  ['valid', true],
  ['invalid', false],
  ['edge_case', true],
])('validation for %s', (input, expected) => {
  const result = validate(input);
  expect(result).toBe(expected);
});

// Run specific case
npm test -- --testNamePattern="validation for edge_case"
```

### Technique 7: Debugging Coverage Gaps

**Problem:** Test passes but doesn't actually test the code.

**Check coverage:**
```bash
# Python
uv run pytest tests/ --cov=src --cov-report=term-missing

# JavaScript
npm test -- --coverage
```

**Example of false-passing test:**
```python
def test_division():
    result = divide(10, 2)
    # ❌ No assertion! Test always passes
```

**Enable strict assertion checking:**
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
# Warn on tests with no assertions
python_files = test_*.py
python_functions = test_*
# Use pytest-testmon to track what code is actually executed
addopts = --strict-markers
```

### Technique 8: Debugging Complex Mock Hierarchies

**Problem:** Mock has nested attributes that need configuration.

**Python:**
```python
# ❌ WRONG: AttributeError on nested access
mock_service = Mock()
mock_service.repository.find()  # AttributeError

# ✅ CORRECT: Configure nested mocks
mock_service = Mock()
mock_service.repository.find.return_value = User(id="123")

# Or use spec to match real interface
mock_service = Mock(spec=RealService)
mock_service.repository = Mock(spec=Repository)
mock_service.repository.find.return_value = User(id="123")
```

**JavaScript:**
```javascript
// ❌ WRONG: TypeError on nested access
const mockService = jest.fn();
mockService.repository.find();  // TypeError

// ✅ CORRECT: Configure nested mocks
const mockService = {
  repository: {
    find: jest.fn().mockResolvedValue({ id: '123' })
  }
};
```

### Technique 9: Debugging Test Performance

**Problem:** Tests take too long.

**Identify slow tests:**
```bash
# Python: Show slowest tests
uv run pytest tests/ --durations=10

# JavaScript: Show test timing
npm test -- --verbose
```

**Common performance issues:**

**1. Unnecessary setup:**
```python
# ❌ SLOW: Creates database for every test
@pytest.fixture
def db_with_data():
    db = create_database()
    for i in range(10000):  # Slow!
        db.insert(User(id=str(i)))
    return db

# ✅ FAST: Use module scope for read-only fixtures
@pytest.fixture(scope="module")
def db_with_data():
    db = create_database()
    for i in range(10000):
        db.insert(User(id=str(i)))
    yield db
    db.cleanup()
```

**2. Serial execution:**
```bash
# Run tests in parallel
uv run pytest tests/ -n auto  # Use all CPU cores
```

**3. Unnecessary waits:**
```python
# ❌ SLOW: Arbitrary sleep
def test_async_operation():
    start_operation()
    time.sleep(5)  # Wait 5 seconds
    assert operation_complete()

# ✅ FAST: Poll with timeout
def test_async_operation():
    start_operation()
    wait_until(lambda: operation_complete(), timeout=5)
```

## Error Pattern Reference

### Pattern: Mock Not Called

**Signature:**
```
AssertionError: Expected 'method' to have been called once. Called 0 times.
```

**Common Causes:**
1. Early return before mock called
2. Exception preventing execution
3. Wrong code path executed
4. Conditional logic skipping call

**Investigation Checklist:**
- [ ] Check for early returns
- [ ] Check for exceptions (add try/except logging)
- [ ] Verify code path with debugger/print statements
- [ ] Check conditional logic

### Pattern: Wrong Mock Return Type

**Signature:**
```
AttributeError: 'dict' object has no attribute 'success'
TypeError: 'Mock' object is not subscriptable
```

**Common Causes:**
1. Mock returns dict when object expected
2. Mock returns object when dict expected
3. Mock returns None when value expected
4. Missing return_value configuration

**Investigation Checklist:**
- [ ] Check mock return_value type
- [ ] Check what implementation expects
- [ ] Verify interface contract
- [ ] Use spec=Interface to catch mismatches

### Pattern: Async Not Awaited

**Signature:**
```
RuntimeWarning: coroutine 'function' was never awaited
TypeError: object Response can't be used in 'await' expression
```

**Common Causes:**
1. Forgot `await` keyword
2. Forgot `async` on test function
3. Mock returns coroutine when value expected
4. Mixing sync and async incorrectly

**Investigation Checklist:**
- [ ] Check all async calls have `await`
- [ ] Check test function is `async def`
- [ ] Check mock configuration for async functions
- [ ] Verify async/sync boundary

### Pattern: Fixture Not Found

**Signature:**
```
fixture 'db_session' not found
E       available fixtures: cache, capfd, capsys, ...
```

**Common Causes:**
1. Fixture not in scope (wrong conftest.py)
2. Typo in fixture name
3. Fixture in different package
4. Circular fixture dependency

**Investigation Checklist:**
- [ ] Check conftest.py location
- [ ] Verify fixture name spelling
- [ ] Check fixture is defined
- [ ] Look for circular dependencies

### Pattern: Import Error

**Signature:**
```
ImportError: cannot import name 'X' from 'module'
ModuleNotFoundError: No module named 'X'
```

**Common Causes:**
1. Module not installed
2. Circular import
3. Typo in import path
4. Module in wrong location

**Investigation Checklist:**
- [ ] Check module is installed (pip list, npm list)
- [ ] Check for circular imports
- [ ] Verify import path
- [ ] Check PYTHONPATH / NODE_PATH

### Pattern: Database Connection Error

**Signature:**
```
ServiceUnavailable: Failed to establish connection
Connection refused
```

**Common Causes:**
1. Database not running
2. Wrong connection string
3. Network issue
4. Authentication failure

**Investigation Checklist:**
- [ ] Check database is running (docker ps, systemctl status)
- [ ] Verify connection string
- [ ] Test network connectivity
- [ ] Check credentials

## Debugging Command Reference

### Python/pytest Advanced Commands

```bash
# Show fixture setup/teardown
pytest tests/ -v -s --setup-show

# Run only last failed tests
pytest --lf -v

# Run failed tests first, then others
pytest --ff -v

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show local variables in traceback
pytest -l

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on error
pytest --pdbcls=IPython.terminal.debugger:Pdb

# Show coverage gaps
pytest --cov=src --cov-report=term-missing --cov-report=html

# Profile test performance
pytest --profile

# Run in parallel
pytest -n auto

# Random order (find order dependencies)
pytest --random-order

# Strict markers (fail on unknown markers)
pytest --strict-markers

# Collect tests without running
pytest --collect-only
```

### JavaScript/Jest Advanced Commands

```bash
# Show coverage
npm test -- --coverage --coverageReporters=text --coverageReporters=html

# Run only changed tests
npm test -- --onlyChanged

# Run tests related to changed files
npm test -- --changedSince=main

# Debug with Chrome DevTools
node --inspect-brk node_modules/.bin/jest --runInBand

# Show all test timing
npm test -- --verbose

# Find open handles (async leaks)
npm test -- --detectOpenHandles

# Force exit (don't wait for async)
npm test -- --forceExit

# Run serially (no parallelism)
npm test -- --runInBand

# Clear cache
npm test -- --clearCache

# Show test coverage for specific file
npm test -- --collectCoverageFrom=src/service.js --coverage
```

### Go Testing Advanced Commands

```bash
# Verbose output
go test -v ./...

# Show test coverage
go test -cover ./...

# Generate coverage HTML
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run tests with race detection
go test -race ./...

# Run specific test
go test -run TestSpecificFunction

# Run tests matching pattern
go test -run "Test.*Service"

# Benchmark tests
go test -bench=.

# Show memory allocations
go test -benchmem -bench=.

# Run tests with timeout
go test -timeout 30s ./...

# Parallel execution
go test -parallel 4 ./...

# Verbose + fail fast
go test -v -failfast ./...
```

## Quality Gate Integration

### Pre-Commit Hook for Tests

**Python (.git/hooks/pre-commit):**
```bash
#!/bin/bash
set -e

echo "Running tests..."
uv run pytest tests/ -x  # Stop on first failure

echo "Running type check..."
uv run pyright

echo "Running linter..."
uv run ruff check src/

echo "All checks passed!"
```

**JavaScript (.git/hooks/pre-commit):**
```bash
#!/bin/bash
set -e

echo "Running tests..."
npm test -- --bail  # Stop on first failure

echo "Running type check..."
npx tsc --noEmit

echo "Running linter..."
npx eslint src/

echo "All checks passed!"
```

### CI/CD Integration

**GitHub Actions (.github/workflows/test.yml):**
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e .[dev]

      - name: Run tests
        run: uv run pytest tests/ -vv --cov=src

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices Summary

1. **Always run tests before making changes**
   - See actual errors, not assumed errors

2. **Read error messages completely**
   - Stack traces contain all the information you need

3. **Distinguish test from implementation issues**
   - Is the test wrong or is the code wrong?

4. **Search for all occurrences**
   - Fix pattern everywhere, not just first instance

5. **Use MultiEdit for efficiency**
   - Multiple edits to same file in one operation

6. **Validate thoroughly**
   - Run specific test, full suite, quality gates

7. **Document root cause**
   - Understanding prevents recurrence

8. **Maintain test isolation**
   - Tests should not depend on each other

9. **Use appropriate fixture scope**
   - Function scope for test isolation, module/session for performance

10. **Monitor test performance**
    - Slow tests indicate architectural issues

## Further Reading

- **pytest documentation:** https://docs.pytest.org/
- **Jest documentation:** https://jestjs.io/docs/getting-started
- **Testing Best Practices:** https://testingjavascript.com/
- **Clean Test Code:** Robert C. Martin, "Clean Code" Chapter 9
- **Test Isolation:** https://martinfowler.com/bliki/TestIsolation.html

## Related Skills

- **code-review-expert:** For architectural test issues
- **architecture-guardian:** For test structure validation
- **debugging-expert:** For complex debugging scenarios
- **python-developer:** For Python-specific test patterns

## Changelog

- **2025-10-16:** Initial version created as project skill
