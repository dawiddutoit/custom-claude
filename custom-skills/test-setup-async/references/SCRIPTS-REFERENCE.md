# Async Testing Automation Scripts

Powerful automation utilities to validate, convert, and generate async test patterns.

## Python Example Scripts

The following Python scripts are available in the `examples/` directory:
- [validate_async_tests.py](../examples/validate_async_tests.py) - Validate async test patterns and detect anti-patterns
- [convert_to_async.py](../examples/convert_to_async.py) - Convert synchronous tests to async patterns
- [generate_async_fixture.py](../examples/generate_async_fixture.py) - Generate async fixture boilerplate code

## Scripts Overview

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `validate_async_tests.py` | Validate async test patterns | Test file/directory | Validation report |
| `convert_to_async.py` | Convert sync tests to async | Test file | Converted code |
| `generate_async_fixture.py` | Generate fixture boilerplate | Fixture spec | Complete fixture code |

---

## 1. validate_async_tests.py

**Validate async test patterns and detect anti-patterns.**

### Features
- ✅ Detects async fixtures using `@pytest.fixture` instead of `@pytest_asyncio.fixture`
- ✅ Finds async fixtures missing `AsyncGenerator` type hints
- ✅ Identifies async tests without `await` statements
- ✅ Flags `Mock()` used where `AsyncMock()` is needed
- ✅ Warns about sync mocks on likely async methods

### Usage

```bash
# Validate single file
python validate_async_tests.py tests/unit/test_service.py

# Validate entire directory
python validate_async_tests.py tests/unit/

# Show all issues including warnings
python validate_async_tests.py tests/unit/ --severity warning

# JSON output for CI/CD
python validate_async_tests.py tests/unit/ --format json > violations.json
```

### Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| AT001 | error | Async fixture must use `@pytest_asyncio.fixture` |
| AT002 | warning | Async fixture with yield should have `AsyncGenerator[T, None]` type hint |
| AT003 | warning | Async test has no await statements |
| AT004 | warning | Variable suggests async usage but uses sync Mock |

### Examples

**Example: Valid Test (No Errors)**
```python
@pytest_asyncio.fixture
async def neo4j_driver() -> AsyncGenerator[AsyncDriver, None]:
    driver = await create_driver()
    yield driver
    await driver.close()

@pytest.mark.asyncio
async def test_query(neo4j_driver):
    result = await neo4j_driver.execute_query("MATCH (n) RETURN n")
    assert result is not None
```

**Example: Invalid Test (Will Report AT001)**
```python
# ❌ AT001: Should use @pytest_asyncio.fixture
@pytest.fixture
async def neo4j_driver():
    driver = await create_driver()
    yield driver
    await driver.close()
```

**Example: Missing Type Hint (Will Report AT002)**
```python
# ⚠️ AT002: Missing AsyncGenerator type hint
@pytest_asyncio.fixture
async def neo4j_driver():  # Missing -> AsyncGenerator[AsyncDriver, None]
    driver = await create_driver()
    yield driver
    await driver.close()
```

### Integration with CI/CD

```yaml
# .github/workflows/test.yml
- name: Validate async test patterns
  run: |
    python .claude/skills/setup-async-testing/scripts/validate_async_tests.py tests/ \
      --format json \
      > async-violations.json

    # Fail if any errors found
    if [ $(jq 'length' async-violations.json) -gt 0 ]; then
      echo "Async test violations found!"
      cat async-violations.json
      exit 1
    fi
```

---

## 2. convert_to_async.py

**Convert synchronous tests to async patterns automatically.**

### Features
- 🔄 Converts `Mock` → `AsyncMock` for async methods
- 🔄 Adds `@pytest_asyncio.fixture` to async fixtures
- 🔄 Adds `AsyncGenerator` type hints
- 🔄 Converts test functions to async
- 🔄 Adds required imports automatically

### Usage

```bash
# Preview changes (dry-run)
python convert_to_async.py tests/unit/test_service.py --dry-run

# Convert and save to new file
python convert_to_async.py tests/unit/test_service.py \
  --output tests/unit/test_service_async.py

# Convert in-place (overwrites original)
python convert_to_async.py tests/unit/test_service.py --in-place

# Pipe to stdout
python convert_to_async.py tests/unit/test_service.py > converted.py
```

### Conversion Examples

**Before (Sync):**
```python
from unittest.mock import Mock
import pytest

@pytest.fixture
def database():
    db = create_connection()
    yield db
    db.close()

def test_query(database):
    result = database.execute("SELECT * FROM users")
    assert len(result) > 0
```

**After (Async):**
```python
from unittest.mock import AsyncMock
import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator

@pytest_asyncio.fixture
async def database() -> AsyncGenerator[Connection, None]:
    db = await create_connection()
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_query(database):
    result = await database.execute("SELECT * FROM users")
    assert len(result) > 0
```

### What Gets Converted

- ✅ `@pytest.fixture` → `@pytest_asyncio.fixture` (for async fixtures)
- ✅ `Mock()` → `AsyncMock()` (for async methods)
- ✅ Function → Async function (if contains await)
- ✅ Missing imports added automatically
- ✅ Type hints updated to `AsyncGenerator`

### What Doesn't Get Converted

- ❌ Business logic (you must review and adjust)
- ❌ Assertions (may need manual adjustment)
- ❌ Complex mock configurations (review side_effect)

### Best Practices

1. **Always review converted code** - Automation is not perfect
2. **Test the converted file** - Run `pytest` to ensure tests still pass
3. **Use dry-run first** - Preview changes before committing
4. **Backup original** - Keep original file until tests pass

---

## 3. generate_async_fixture.py

**Generate async fixture boilerplate for common resource types.**

### Features
- 🏗️ Database connection fixtures (Neo4j, PostgreSQL, etc.)
- 🏗️ API/HTTP client fixtures
- 🏗️ Mock service fixtures
- 🏗️ Session-scoped fixtures
- 🏗️ Custom resource fixtures
- 📝 Complete with docstrings and examples

### Usage

```bash
# Generate Neo4j driver fixture
python generate_async_fixture.py neo4j_driver database

# Generate mock service fixture
python generate_async_fixture.py mock_embedding_service mock

# Generate API client with authentication
python generate_async_fixture.py api_client client --with-auth

# Session-scoped database fixture
python generate_async_fixture.py shared_database database --scope session

# Custom return type
python generate_async_fixture.py my_fixture custom \
  --return-type "MyCustomResource"

# Save to file
python generate_async_fixture.py neo4j_driver database \
  --output tests/fixtures/neo4j.py

# Copy to clipboard (macOS)
python generate_async_fixture.py mock_service mock | pbcopy
```

### Resource Types

| Type | Use Case | Example |
|------|----------|---------|
| `database` | Database connections | Neo4j, PostgreSQL, MongoDB |
| `client` | HTTP/API clients | httpx, aiohttp |
| `mock` | Mock services | AsyncMock for services |
| `session` | Session-scoped resources | Shared expensive resources |
| `custom` | Generic resources | Custom async resources |

### Generated Examples

#### Database Fixture

```bash
python generate_async_fixture.py neo4j_driver database
```

**Output:**
```python
import pytest_asyncio
from collections.abc import AsyncGenerator

# Database-specific imports
# from neo4j import AsyncDriver, AsyncGraphDatabase

@pytest_asyncio.fixture(scope="function")
async def neo4j_driver() -> AsyncGenerator[AsyncDriver, None]:
    """Create async database connection with cleanup.

    Yields:
        AsyncDriver: Database connection/driver instance

    Example:
        @pytest.mark.asyncio
        async def test_query(neo4j_driver):
            async with neo4j_driver.session() as session:
                result = await session.run("MATCH (n) RETURN n")
                data = await result.data()
                assert len(data) > 0
    """
    # Setup: Create database connection
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )

    yield driver

    # Cleanup: Close connection
    await driver.close()
```

#### Mock Service Fixture

```bash
python generate_async_fixture.py mock_service mock
```

**Output:**
```python
import pytest_asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

@pytest.fixture
def mock_service():
    """Create mock service for testing.

    Returns:
        AsyncMock: Mock service with configured return values

    Example:
        @pytest.mark.asyncio
        async def test_service(mock_service):
            result = await mock_service.fetch_data()
            assert result.is_success()
            mock_service.fetch_data.assert_awaited_once()
    """
    from your_project.domain.values.service_result import ServiceResult

    service = AsyncMock()
    service.fetch_data.return_value = ServiceResult.success({"data": "test"})
    service.save.return_value = ServiceResult.success(None)

    return service
```

#### API Client Fixture

```bash
python generate_async_fixture.py api_client client --with-auth
```

**Output:**
```python
import pytest_asyncio
from collections.abc import AsyncGenerator
import httpx

@pytest_asyncio.fixture(scope="function")
async def api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async HTTP client with cleanup.

    Example:
        @pytest.mark.asyncio
        async def test_api_call(api_client):
            response = await api_client.get("/api/endpoint")
            assert response.status_code == 200
    """
    # Setup: Configure authentication
    headers = {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }
    client = httpx.AsyncClient(
        base_url="http://localhost:8000",
        headers=headers
    )

    yield client

    # Cleanup: Close client
    await client.aclose()
```

---

## Common Workflows

### Workflow 1: Validate Existing Tests

```bash
# 1. Check all tests for issues
python validate_async_tests.py tests/ --severity warning

# 2. Fix issues manually or use convert_to_async.py
python convert_to_async.py tests/unit/test_service.py --dry-run

# 3. Validate again
python validate_async_tests.py tests/unit/test_service.py
```

### Workflow 2: Add New Async Test

```bash
# 1. Generate fixture
python generate_async_fixture.py neo4j_driver database > tests/fixtures/neo4j.py

# 2. Write test using fixture
# (Edit tests/unit/test_my_feature.py)

# 3. Validate patterns
python validate_async_tests.py tests/unit/test_my_feature.py

# 4. Run tests
pytest tests/unit/test_my_feature.py -v
```

### Workflow 3: Convert Legacy Tests

```bash
# 1. Backup original
cp tests/unit/test_legacy.py tests/unit/test_legacy.py.bak

# 2. Preview conversion
python convert_to_async.py tests/unit/test_legacy.py --dry-run

# 3. Convert in-place
python convert_to_async.py tests/unit/test_legacy.py --in-place

# 4. Review changes
git diff tests/unit/test_legacy.py

# 5. Run tests
pytest tests/unit/test_legacy.py -v

# 6. Validate patterns
python validate_async_tests.py tests/unit/test_legacy.py
```

---

## Pre-commit Hook Integration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-async-tests
        name: Validate Async Test Patterns
        entry: python .claude/skills/setup-async-testing/scripts/validate_async_tests.py
        language: system
        files: ^tests/.*test.*\.py$
        pass_filenames: true
```

---

## Troubleshooting

### Issue: "Module 'ast' has no attribute 'unparse'"

**Solution:** Requires Python 3.9+. Update Python or use `astor` library.

```bash
# Check Python version
python --version

# If < 3.9, install astor
pip install astor
```

### Issue: Validation reports false positives

**Solution:** Scripts use heuristics. Review and adjust code or add exemptions.

```python
# Suppress specific warnings with comments
@pytest.fixture  # noqa: AT001 - Intentionally sync fixture
def my_fixture():
    return "value"
```

### Issue: Conversion breaks tests

**Solution:** Always use `--dry-run` first and manually review changes.

```bash
# Preview first
python convert_to_async.py test_file.py --dry-run

# Review carefully before committing
```

---

## Architecture

### validate_async_tests.py

- Uses Python `ast` module for parsing
- `AsyncTestValidator` visitor pattern
- Violation tracking with severity levels
- JSON output for CI/CD integration

### convert_to_async.py

- `ast.NodeTransformer` for code modification
- Preserves code structure and comments
- Tracks necessary import additions
- Safe in-place or file-output modes

### generate_async_fixture.py

- Template-based code generation
- Resource type enumeration
- Configuration dataclass pattern
- Customizable scopes and options

---

## Testing the Scripts

```bash
# Test validate_async_tests.py
python validate_async_tests.py tests/unit/infrastructure/neo4j/test_code_repository.py

# Test generate_async_fixture.py
python generate_async_fixture.py test_fixture database

# Test convert_to_async.py (dry-run)
python convert_to_async.py tests/unit/test_service.py --dry-run
```

---

## Contributing

To improve these scripts:

1. **Add new validation rules** - Extend `AsyncTestValidator.visit_*` methods
2. **Add new resource types** - Extend `ResourceType` enum and add generator
3. **Improve conversions** - Enhance `AsyncConverter` transformation logic

---

## License

Part of the your_project project. See main project LICENSE.

---

**Last Updated:** 2025-10-18
**Python Version:** 3.11+
**Dependencies:** None (pure Python `ast` module)
