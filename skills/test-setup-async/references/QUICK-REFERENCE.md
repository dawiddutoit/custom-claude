# Quick Reference - Async Testing Scripts

One-page reference for the async testing automation scripts.

---

## Scripts at a Glance

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `validate_async_tests.py` | Find async pattern violations | Test file/dir | Error report |
| `convert_to_async.py` | Convert sync → async | Test file | Converted code |
| `generate_async_fixture.py` | Create fixture template | Spec | Fixture code |

---

## validate_async_tests.py

**Validate async test patterns**

```bash
# Single file
python validate_async_tests.py tests/unit/test_service.py

# Directory
python validate_async_tests.py tests/unit/

# Include warnings
python validate_async_tests.py tests/ --severity warning

# JSON output (for CI/CD)
python validate_async_tests.py tests/ --format json > violations.json
```

**Error Codes:**
- `AT001` - Async fixture must use `@pytest_asyncio.fixture`
- `AT002` - Missing `AsyncGenerator[T, None]` type hint
- `AT003` - Async test without await statements
- `AT004` - Sync Mock on likely async method

---

## convert_to_async.py

**Convert sync tests to async patterns**

```bash
# Preview changes (recommended first step)
python convert_to_async.py test_file.py --dry-run

# Save to new file
python convert_to_async.py test_file.py --output test_async.py

# Modify in-place (use with caution)
python convert_to_async.py test_file.py --in-place

# Print to stdout
python convert_to_async.py test_file.py
```

**What Gets Converted:**
- `Mock()` → `AsyncMock()`
- `@pytest.fixture` → `@pytest_asyncio.fixture`
- Function → Async function (if contains async calls)
- Missing imports added automatically

---

## generate_async_fixture.py

**Generate async fixture boilerplate**

```bash
# Database fixture
python generate_async_fixture.py neo4j_driver database

# Mock service
python generate_async_fixture.py mock_service mock

# API client with auth
python generate_async_fixture.py api_client client --with-auth

# Session-scoped
python generate_async_fixture.py shared_db database --scope session

# Custom return type
python generate_async_fixture.py my_fixture custom --return-type "MyResource"

# Save to file
python generate_async_fixture.py my_fixture database -o tests/fixtures/db.py
```

**Resource Types:**
- `database` - Database connections (Neo4j, PostgreSQL, etc.)
- `client` - HTTP/API clients (httpx, aiohttp)
- `mock` - Mock services (AsyncMock)
- `session` - Session-scoped resources
- `custom` - Generic async resources

**Scopes:**
- `function` (default) - New instance per test
- `class` - Shared within test class
- `module` - Shared within test module
- `session` - Shared across all tests

---

## Common Workflows

### Workflow 1: Validate Tests

```bash
# Check for issues
python validate_async_tests.py tests/ --severity warning

# Fix issues
# (manually or use convert_to_async.py)

# Validate again
python validate_async_tests.py tests/
```

### Workflow 2: Create New Test

```bash
# 1. Generate fixture
python generate_async_fixture.py my_fixture database > fixtures.py

# 2. Write test using fixture
# (edit test file)

# 3. Validate
python validate_async_tests.py tests/unit/test_new.py

# 4. Run test
pytest tests/unit/test_new.py -v
```

### Workflow 3: Convert Legacy Test

```bash
# 1. Backup
cp test_old.py test_old.py.bak

# 2. Preview
python convert_to_async.py test_old.py --dry-run

# 3. Convert
python convert_to_async.py test_old.py --in-place

# 4. Review
git diff test_old.py

# 5. Test
pytest test_old.py -v
```

---

## Command-Line Options

### validate_async_tests.py

```
python validate_async_tests.py PATH [OPTIONS]

Options:
  --severity {error,warning}  Minimum severity (default: error)
  --format {text,json}        Output format (default: text)
  --help                      Show help
```

### convert_to_async.py

```
python convert_to_async.py FILE [OPTIONS]

Options:
  --output, -o FILE    Save to file (default: stdout)
  --in-place, -i       Modify file in-place
  --dry-run            Preview changes only
  --help               Show help
```

### generate_async_fixture.py

```
python generate_async_fixture.py NAME TYPE [OPTIONS]

Options:
  --scope {function,class,module,session}  Fixture scope
  --with-auth                              Include auth (client only)
  --return-type TYPE                       Custom return type
  --output, -o FILE                        Save to file
  --help                                   Show help
```

---

## Generated Fixture Examples

### Database Fixture

```python
@pytest_asyncio.fixture(scope="function")
async def neo4j_driver() -> AsyncGenerator[AsyncDriver, None]:
    driver = AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    yield driver
    await driver.close()
```

### Mock Service Fixture

```python
@pytest.fixture
def mock_service():
    service = AsyncMock()
    service.fetch_data.return_value = ServiceResult.success({"data": "test"})
    return service
```

### API Client Fixture

```python
@pytest_asyncio.fixture
async def api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    client = httpx.AsyncClient(base_url="http://localhost:8000")
    yield client
    await client.aclose()
```

---

## Tips & Tricks

### Copy to Clipboard (macOS)

```bash
python generate_async_fixture.py my_fixture database | pbcopy
```

### Copy to Clipboard (Linux)

```bash
python generate_async_fixture.py my_fixture database | xclip -selection clipboard
```

### Batch Process

```bash
for file in tests/unit/test_*.py; do
    python validate_async_tests.py "$file"
done
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-async-tests
        name: Validate Async Test Patterns
        entry: python .claude/skills/setup-async-testing/scripts/validate_async_tests.py
        language: system
        files: ^tests/.*test.*\.py$
```

### Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias validate-async='python .claude/skills/setup-async-testing/scripts/validate_async_tests.py'
alias convert-async='python .claude/skills/setup-async-testing/scripts/convert_to_async.py'
alias gen-fixture='python .claude/skills/setup-async-testing/scripts/generate_async_fixture.py'
```

---

## Error Codes Reference

| Code | Severity | Fix |
|------|----------|-----|
| AT001 | error | Change `@pytest.fixture` → `@pytest_asyncio.fixture` |
| AT002 | warning | Add `AsyncGenerator[T, None]` type hint |
| AT003 | warning | Add `await` or remove `async` |
| AT004 | warning | Change `Mock()` → `AsyncMock()` |

---

## CI/CD Integration

```bash
# GitHub Actions
python validate_async_tests.py tests/ --format json > violations.json
if [ $(jq 'length' violations.json) -gt 0 ]; then
  exit 1
fi

# GitLab CI
script:
  - python validate_async_tests.py tests/ --format json --severity error

# Jenkins
sh 'python validate_async_tests.py tests/ --format json > violations.json'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Module 'ast' has no attribute 'unparse'` | Requires Python 3.9+ |
| False positive warnings | Add `# noqa: AT001` comment |
| Conversion breaks tests | Use `--dry-run` first |
| Generated fixture doesn't match project | Use as template, customize |

---

## Documentation Links

- **[SCRIPTS-REFERENCE.md](./SCRIPTS-REFERENCE.md)** - Complete reference
- **[../examples/SCRIPT-EXAMPLES.md](../examples/SCRIPT-EXAMPLES.md)** - Real-world examples
- **[IMPLEMENTATION-SUMMARY.md](./IMPLEMENTATION-SUMMARY.md)** - Technical details
- **[../SKILL.md](../SKILL.md)** - Async testing skill guide

---

**Last Updated:** 2025-10-18
**Quick help:** `python <script>.py --help`
