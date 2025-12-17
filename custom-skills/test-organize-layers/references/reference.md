# Reference - organize-test-layers

## Python Example Scripts

The following utility scripts demonstrate practical test layer organization:

- [analyze_test_pyramid.py](../examples/analyze_test_pyramid.py) - Analyzes test distribution across unit/integration/e2e layers and compares to ideal pyramid ratios
- [move_test.py](../examples/move_test.py) - Moves test files between layers with automatic fixture and import updates
- [organize_tests.py](../examples/organize_tests.py) - Master script for comprehensive test organization with check, fix, and interactive modes
- [validate_test_placement.py](../examples/validate_test_placement.py) - Validates test placement in pyramid layers and suggests corrections

---

## Test Pyramid Theory

### Classic Test Pyramid

```
        /\
       /  \
      / E2E \      ← 10% (Slow, expensive, high value)
     /────────\
    /          \
   /Integration\   ← 20% (Medium speed, component tests)
  /──────────────\
 /                \
/      Unit        \ ← 70% (Fast, cheap, many tests)
/────────────────────\
```

**Principles**:
1. **More unit tests than integration tests**
2. **More integration tests than E2E tests**
3. **Faster tests run more frequently**
4. **Higher-level tests provide more confidence**

### your_project Test Distribution

**Current Distribution** (217 test files):
- Unit: ~152 files (70%)
- Integration: ~43 files (20%)
- E2E: ~22 files (10%)

**Speed Targets**:
- Unit: <10ms per test
- Integration: <500ms per test
- E2E: 1-10s per test

---

## Fixture Scope Reference

### Scope Types

| Scope      | Lifecycle                     | Use Case                               |
|------------|-------------------------------|----------------------------------------|
| `function` | Created/destroyed per test    | Test isolation, default scope          |
| `class`    | Shared across test class      | Related tests sharing setup            |
| `module`   | Shared across test module     | Expensive setup used by many tests     |
| `session`  | Created once per test session | Very expensive (database initialization)|

### Fixture Scope by Test Layer

**Unit Test Fixtures** (always `function` scope):
```python
@pytest.fixture  # Default: scope="function"
def mock_config():
    """Fresh mock for each test - ensures isolation."""
    return Mock(spec=Settings)
```

**Integration Test Fixtures** (function or module scope):
```python
@pytest_asyncio.fixture(scope="function")
async def neo4j_database(real_settings):
    """Function scope ensures test isolation."""
    db = Neo4jDatabase(settings=real_settings)
    await db.initialize()
    yield db
    await db.shutdown()
```

**E2E Test Fixtures** (session scope for expensive operations):
```python
@pytest.fixture(scope="session")
def indexed_real_codebase():
    """Index codebase ONCE per test session - very expensive."""
    asyncio.run(index_codebase())
    yield
```

---

## Mocking Patterns

### When to Mock

**Unit Tests**: Mock EVERYTHING external
- Database connections
- File system operations
- Network calls (HTTP, embeddings, LLMs)
- Time (datetime.now)
- Random number generation

**Integration Tests**: Mock ONLY external services
- External APIs (embeddings, LLMs) → Mock
- Database (Neo4j) → Real
- File system → Real (with cleanup)

**E2E Tests**: Mock NOTHING
- All services real
- All infrastructure real
- Test complete workflows

### Mock Specification Patterns

**Always use `spec` for type safety**:
```python
# ✅ CORRECT - Type-safe mock
from unittest.mock import Mock
mock_db = Mock(spec=Neo4jDatabase)
mock_db.execute_query.return_value = ServiceResult.success(data=[])

# ❌ WRONG - No spec, typos not caught
mock_db = Mock()
mock_db.exeucte_query.return_value = []  # Typo not caught!
```

### AsyncMock for Async Functions

```python
from unittest.mock import AsyncMock

# ✅ CORRECT - AsyncMock for async methods
mock_service = AsyncMock(spec=EmbeddingService)
mock_service.embed_query.return_value = [0.1, 0.2, 0.3]

result = await mock_service.embed_query("test")  # Works correctly

# ❌ WRONG - Regular Mock for async method
mock_service = Mock(spec=EmbeddingService)
result = await mock_service.embed_query("test")  # Runtime error!
```

---

## Fixture Dependency Patterns

### Unit Test Fixtures (No Dependencies)

```python
# tests/unit/conftest.py
@pytest.fixture
def temp_dir():
    """Isolated temporary directory - no dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_config(temp_dir):
    """Mock config depends on temp_dir fixture."""
    return Settings(
        project=ProjectSettings(repository_path=temp_dir, ...)
    )
```

### Integration Test Fixtures (Real Settings → Real Database)

```python
# tests/integration/conftest.py
@pytest.fixture
def real_settings():
    """Load settings from environment - base fixture."""
    return Settings.from_env()

@pytest_asyncio.fixture
async def neo4j_database(real_settings):
    """Real database depends on real_settings."""
    db = Neo4jDatabase(settings=real_settings)
    await db.initialize()
    yield db
    await db.shutdown()

@pytest_asyncio.fixture
async def neo4j_driver(neo4j_database):
    """Driver depends on database fixture."""
    yield neo4j_database.driver
```

### E2E Test Fixtures (Full Dependency Chain)

```python
# tests/e2e/conftest.py
@pytest.fixture(scope="session")
def indexed_real_codebase():
    """Session fixture - indexes codebase once."""
    asyncio.run(index_repository())
    yield

@pytest_asyncio.fixture
async def neo4j_driver(indexed_real_codebase):
    """Driver depends on indexed codebase being ready."""
    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    yield driver
    await driver.close()

@pytest_asyncio.fixture
async def search_handler(neo4j_driver, test_settings):
    """Search handler depends on driver and settings."""
    embedding_service = create_embedding_service(test_settings)
    search_repository = Neo4jSearchRepository(neo4j_driver, test_settings)

    handler = SearchCodeHandler(
        search_repository=search_repository,
        embedding_service=embedding_service,
        settings=test_settings
    )
    yield handler
```

---

## Test Isolation Strategies

### Unit Test Isolation (Fast Reset)

```python
@pytest.fixture
def isolated_service():
    """Fresh instance per test - automatic isolation."""
    return ChunkingService(settings=mock_settings)
```

**Isolation Method**: Create new instance per test.

### Integration Test Isolation (Database Cleanup)

```python
@pytest_asyncio.fixture
async def test_database(neo4j_database, real_settings):
    """Clean database before and after each test."""
    database_name = real_settings.neo4j.database_name

    # Clean BEFORE test
    await neo4j_database.execute_query(
        "MATCH (n) DETACH DELETE n",
        database=database_name
    )

    yield database_name

    # Clean AFTER test
    await neo4j_database.execute_query(
        "MATCH (n) DETACH DELETE n",
        database=database_name
    )
```

**Isolation Method**: Database cleanup between tests.

### E2E Test Isolation (Unique Identifiers)

```python
@pytest.fixture
def unique_project_name():
    """Generate unique project name per test."""
    import uuid
    return f"test-project-{uuid.uuid4()}"

async def test_search(search_handler, unique_project_name):
    """Use unique project name to avoid conflicts."""
    query = SearchCodeQuery(
        query_text="test",
        project_name=unique_project_name,  # Unique per test
        search_type=SearchType.SEMANTIC
    )
    result = await search_handler.handle(query)
```

**Isolation Method**: Unique identifiers prevent test interference.

---

## Clean Architecture Test Mapping

### Domain Layer Tests (Pure Logic)

**Location**: `tests/unit/core/`

**Characteristics**:
- No external dependencies
- Pure functions
- Value objects, entities, domain logic
- No mocks needed (pure data)

**Example**:
```python
# tests/unit/core/test_service_result.py
def test_service_result_success():
    """Test domain object - no mocks needed."""
    result = ServiceResult.success(data={"key": "value"})
    assert result.success is True
```

### Application Layer Tests (Business Logic)

**Location**: `tests/unit/application/`

**Characteristics**:
- Mock all infrastructure dependencies
- Test use cases, commands, queries
- Focus on business rules

**Example**:
```python
# tests/unit/application/queries/test_search_code.py
async def test_search_validates_query(mock_repository):
    """Test application logic with mocked infrastructure."""
    handler = SearchCodeHandler(search_repository=mock_repository, ...)
    result = await handler.handle(invalid_query)
    assert not result.success
```

### Infrastructure Layer Tests (Unit + Integration)

**Unit Tests** (`tests/unit/infrastructure/`):
- Mock external services
- Test adapter logic

**Integration Tests** (`tests/integration/infrastructure/`):
- Real infrastructure
- Test actual persistence/communication

**Example**:
```python
# Unit: tests/unit/infrastructure/neo4j/test_code_repository.py
async def test_repository_builds_query():
    """Test query building logic - mocked driver."""
    mock_driver = Mock(spec=AsyncDriver)
    repository = Neo4jCodeRepository(mock_driver, settings)
    # Test query construction without executing

# Integration: tests/integration/infrastructure/neo4j/test_code_repository.py
async def test_repository_stores_chunk(neo4j_database):
    """Test actual storage - real database."""
    repository = Neo4jCodeRepository(neo4j_database.driver, settings)
    result = await repository.store_chunk(chunk)
    # Verify data persisted in real DB
```

### Interface Layer Tests (E2E)

**Location**: `tests/e2e/`

**Characteristics**:
- Test MCP tools end-to-end
- Test FastMCP server integration
- Test complete user workflows

**Example**:
```python
# tests/e2e/test_mcp_protocol_workflows.py
async def test_search_code_tool_workflow(mcp_client):
    """Test MCP tool from client perspective."""
    result = await mcp_client.call_tool(
        "search_code",
        {"query": "validation", "search_type": "semantic"}
    )
    assert result["total_matches"] > 0
```

---

## Test Naming Conventions

### Unit Test Names

**Pattern**: `test_{what}_{condition}_{expected_behavior}`

```python
def test_chunk_size_exceeds_limit_splits_chunk():
    """Test what happens when chunk exceeds size limit."""
    pass

def test_service_result_failure_sets_error_message():
    """Test failure case sets error correctly."""
    pass
```

### Integration Test Names

**Pattern**: `test_{component}_{interaction}_{database_state}`

```python
async def test_repository_stores_chunk_creates_node():
    """Test repository creates Neo4j node."""
    pass

async def test_validator_finds_orphaned_chunks_returns_list():
    """Test validator query returns orphaned chunk list."""
    pass
```

### E2E Test Names

**Pattern**: `test_{user_action}_{expected_outcome}`

```python
async def test_search_for_methods_returns_ranked_results():
    """Test user searching for methods gets ranked results."""
    pass

async def test_initialize_repository_indexes_all_files():
    """Test repository initialization indexes entire codebase."""
    pass
```

---

## Troubleshooting Test Placement

### Symptom: Test is Slow

**Possible Issues**:
1. Unit test with real database → Move to integration
2. Integration test with full indexing → Split into smaller tests
3. E2E test testing single function → Move to unit

**Solution**: Check test speed against targets:
- Unit: <10ms
- Integration: <500ms
- E2E: 1-10s

### Symptom: Test Fails Randomly

**Possible Issues**:
1. Missing test isolation → Add cleanup fixtures
2. Shared state between tests → Use `scope="function"`
3. Real external dependencies in unit test → Add mocks

**Solution**: Add isolation:
```python
@pytest.fixture(scope="function")  # Force function scope
async def isolated_database(neo4j_database):
    """Clean database before each test."""
    await clean_database()
    yield neo4j_database
    await clean_database()
```

### Symptom: Test is Too Complex

**Possible Issues**:
1. E2E test testing too much → Split into focused tests
2. Integration test with too many mocks → Move to unit
3. Unit test with complex setup → Extract fixtures

**Solution**: Simplify or split:
```python
# ❌ Too complex
async def test_everything():
    setup_a()
    setup_b()
    test_feature_x()
    test_feature_y()
    test_feature_z()

# ✅ Split into focused tests
async def test_feature_x():
    setup_a()
    test_feature_x()

async def test_feature_y():
    setup_b()
    test_feature_y()
```

---

## Advanced Patterns

### Pattern: Shared Fixtures with Parameterization

```python
@pytest.mark.parametrize("chunk_size", [100, 500, 1000])
async def test_chunking_with_various_sizes(chunk_size, mock_config):
    """Test multiple scenarios using same fixture."""
    mock_config.chunking.max_chunk_lines = chunk_size
    service = ChunkingService(settings=mock_config)
    # Test with parameterized value
```

### Pattern: Fixture Factories

```python
@pytest.fixture
def make_chunk():
    """Factory fixture to create test chunks."""
    def _make_chunk(content: str, file_path: str):
        return Chunk(
            chunk_hash=hash(content),
            file_path=file_path,
            content=content,
            start_line=1,
            end_line=10
        )
    return _make_chunk

def test_with_factory(make_chunk):
    """Use factory to create multiple test objects."""
    chunk1 = make_chunk("content 1", "file1.py")
    chunk2 = make_chunk("content 2", "file2.py")
    # Test with multiple chunks
```

### Pattern: Conditional Fixtures

```python
@pytest.fixture
def database_or_mock(request):
    """Use real DB if available, otherwise mock."""
    if request.config.getoption("--use-real-db"):
        return real_database_fixture()
    else:
        return Mock(spec=Neo4jDatabase)
```

---

## pytest Markers Reference

### Built-in Markers

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.e2e          # End-to-end test
@pytest.mark.skip         # Skip test
@pytest.mark.skipif       # Conditional skip
@pytest.mark.parametrize  # Parameterized test
@pytest.mark.asyncio      # Async test (pytest-asyncio)
```

### Custom Markers (your_project)

```python
@pytest.mark.requires_neo4j   # Requires running Neo4j
@pytest.mark.requires_voyage  # Requires Voyage API key
@pytest.mark.slow            # Slow test (>1s)
```

### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Run E2E tests
pytest -m e2e

# Run all except slow tests
pytest -m "not slow"

# Run integration tests that require Neo4j
pytest -m "integration and requires_neo4j"
```

---

## Configuration Reference

### pytest.ini / pyproject.toml

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (real infrastructure)",
    "e2e: End-to-end tests (full stack)",
    "slow: Slow tests (>1s)",
    "requires_neo4j: Tests requiring Neo4j",
    "requires_voyage: Tests requiring Voyage API"
]

# Async support
asyncio_mode = "auto"

# Test discovery
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

---

## Summary

- **Three Layers**: Unit (70%), Integration (20%), E2E (10%)
- **Fixture Scopes**: function (isolation), module (shared setup), session (expensive operations)
- **Mocking Strategy**: Unit (mock all), Integration (mock external APIs), E2E (mock nothing)
- **Isolation**: Fresh instances (unit), database cleanup (integration), unique IDs (E2E)
- **Speed Targets**: Unit <10ms, Integration <500ms, E2E 1-10s
- **Clean Architecture Mapping**: Domain → Unit, Application → Unit/Integration, Infrastructure → Integration, Interface → E2E
