# Stage-by-Stage Deep Dive - implement-feature-complete

This reference provides detailed explanations for each of the 10 stages in the feature implementation workflow.

---

## Stage 1: Planning & Location

### Purpose

Determine the correct architectural location and patterns before writing any code. This prevents architectural drift and ensures the feature fits into the existing system design.

### Clean Architecture Layer Decision

**Decision Tree:**

```
Is it a business rule or validation logic?
  └─ YES → Domain Layer (src/your_project/domain/)
      ├─ Entity: Has identity, mutable state
      ├─ Value Object: No identity, immutable, self-validating
      └─ Repository Protocol: Interface for data access

Is it a use case or orchestration logic?
  └─ YES → Application Layer (src/your_project/application/)
      ├─ Command: Modifies state (CQRS write)
      ├─ Query: Reads state (CQRS read)
      └─ Handler: Executes command/query

Is it interacting with external systems?
  └─ YES → Infrastructure Layer (src/your_project/infrastructure/)
      ├─ Repository Implementation: Neo4j, file system
      ├─ Configuration: Settings, environment variables
      └─ Container: Dependency injection

Is it exposing functionality to users?
  └─ YES → Interface Layer (src/your_project/interface/)
      ├─ MCP Tools: FastMCP tool definitions
      └─ CLI: Command-line interface (if applicable)
```

### CQRS Pattern Decision

**Command (Write):**
- Changes system state
- Returns success/failure (minimal data)
- Examples: CreateProject, IndexFile, DeleteEntity

**Query (Read):**
- No side effects
- Returns data
- Examples: SearchCode, GetEntity, ListProjects

**Rule:** If it reads AND writes, split into separate command and query.

### Dependency Analysis

**Questions to Ask:**

1. **What repositories are needed?**
   - CodeRepository? ProjectRepository? EntityRepository?
   - Do they have the required methods?
   - Need to extend protocol?

2. **What services are needed?**
   - Embedding service? Parser service?
   - Already registered in DI container?

3. **What configuration is needed?**
   - New settings? Environment variables?
   - Add to Settings dataclass?

4. **What value objects are needed?**
   - Need validation logic?
   - Reusable across features?

### Common Patterns by Use Case

**File Processing:**
- Layer: Infrastructure → Application → Interface
- Pattern: Command (ingest) + Repository (store)

**Search/Retrieval:**
- Layer: Application (Query) → Infrastructure (Repository)
- Pattern: Query + Handler + Repository

**Validation/Business Rules:**
- Layer: Domain (Value Object) → Application (Handler)
- Pattern: Value Object + Command/Query

---

## Stage 2: TDD - Red (Write Failing Test)

### Purpose

Define expected behavior through tests BEFORE implementing. This ensures code is testable, has clear requirements, and prevents over-engineering.

### Test Structure

**Unit Test Anatomy:**

```python
# tests/unit/<layer>/<feature>.py

import pytest
from unittest.mock import AsyncMock

from your_project.<layer>.<feature> import (
    MyQuery,
    MyHandler,
)
from your_project.application.utils.service_result import ServiceResult


class TestMyQuery:
    """Tests for MyQuery class."""

    def test_constructor_requires_required_param(self):
        """Test fail-fast: None raises ValueError."""
        with pytest.raises(ValueError, match="param required"):
            MyQuery(param=None)

    def test_constructor_validates_param(self):
        """Test business rule validation."""
        with pytest.raises(ValueError, match="invalid param"):
            MyQuery(param="invalid")

    def test_constructor_normalizes_param(self):
        """Test normalization logic."""
        query = MyQuery(param="  VALUE  ")
        assert query.param == "value"


class TestMyHandler:
    """Tests for MyHandler class."""

    def test_constructor_requires_repository(self):
        """Test fail-fast: None raises ValueError."""
        with pytest.raises(ValueError, match="repository required"):
            MyHandler(repository=None)

    @pytest.mark.asyncio
    async def test_execute_calls_repository(self):
        """Test handler delegates to repository."""
        # Arrange: Mock repository
        mock_repo = AsyncMock()
        mock_repo.my_method.return_value = ServiceResult.success([])

        # Act: Execute handler
        handler = MyHandler(repository=mock_repo)
        query = MyQuery(param="value")
        result = await handler.execute(query)

        # Assert: Verify interaction
        mock_repo.my_method.assert_called_once_with("value")
        assert result.success

    @pytest.mark.asyncio
    async def test_execute_propagates_failure(self):
        """Test handler propagates repository failures."""
        # Arrange: Mock failure
        mock_repo = AsyncMock()
        mock_repo.my_method.return_value = ServiceResult.failure("error")

        # Act
        handler = MyHandler(repository=mock_repo)
        result = await handler.execute(MyQuery(param="value"))

        # Assert
        assert not result.success
        assert result.error == "error"
```

### Constructor Validation Tests

**Why Constructor Validation?**
- Fail-fast principle: Catch errors at construction, not during execution
- Makes objects immutable and valid-by-construction
- Prevents None/invalid state propagation

**Required Constructor Tests:**
1. **None check:** `with pytest.raises(ValueError, match="X required")`
2. **Empty check:** Test empty strings, empty lists, zero values
3. **Type validation:** Test invalid types (if applicable)
4. **Business rules:** Test domain-specific validation

### Mocking Best Practices

**Use AsyncMock for async methods:**
```python
mock_repo = AsyncMock()
mock_repo.async_method.return_value = ServiceResult.success([])
```

**Use Mock for sync methods:**
```python
from unittest.mock import Mock
mock_service = Mock()
mock_service.sync_method.return_value = "result"
```

**Verify mock calls:**
```python
# Exact call verification
mock_repo.method.assert_called_once_with("expected_arg")

# Any call verification
mock_repo.method.assert_called()

# No call verification
mock_repo.method.assert_not_called()
```

### Running Tests to See Failures

```bash
# Run specific test file
uv run pytest tests/unit/application/queries/test_my_feature.py -v

# Run with verbose output
uv run pytest tests/unit/application/queries/test_my_feature.py -vv

# Run single test
uv run pytest tests/unit/application/queries/test_my_feature.py::TestMyQuery::test_constructor_requires_param -v
```

**Expected RED output:**
```
ERROR: cannot import name 'MyQuery'
ModuleNotFoundError: No module named 'your_project.application.queries.my_feature'
```

This is CORRECT - tests should fail because code doesn't exist yet.

---

## Stage 3: Consistent Naming

### Purpose

Follow project conventions to maintain codebase consistency and discoverability.

### Naming Conventions by Layer

**Domain Layer:**
- **Entities:** Noun (e.g., `Project`, `CodeEntity`, `Chunk`)
- **Value Objects:** Descriptive noun (e.g., `FileType`, `ProjectPath`, `Embedding`)
- **Protocols:** Interface name with Protocol suffix (e.g., `CodeRepository`, `EmbeddingService`)

**Application Layer:**
- **Commands:** Verb + Noun + "Command" (e.g., `IndexFileCommand`, `CreateProjectCommand`)
- **Queries:** Verb + Noun + "Query" (e.g., `SearchCodeQuery`, `GetEntityQuery`)
- **Handlers:** Match command/query name + "Handler" (e.g., `IndexFileHandler`, `SearchCodeHandler`)

**Infrastructure Layer:**
- **Repositories:** Implementation name + "Repository" (e.g., `Neo4jCodeRepository`, `FileSystemProjectRepository`)
- **Services:** Implementation name + "Service" (e.g., `VoyageEmbeddingService`)

**Interface Layer:**
- **MCP Tools:** Snake_case verb + noun (e.g., `search_code`, `index_repository`, `get_entities`)

### File Naming

**Rule:** File name matches primary class name in snake_case.

```
Class: SearchCodeQuery
File: search_code_query.py (NOT search_code.py)

Class: FileType
File: file_type.py

Class: Neo4jCodeRepository
File: neo4j_code_repository.py
```

### Method Naming

**Commands (state-changing):**
- Use imperative verbs: `create`, `update`, `delete`, `index`
- Examples: `create_project()`, `index_file()`, `delete_entity()`

**Queries (read-only):**
- Use descriptive verbs: `get`, `find`, `search`, `list`
- Examples: `get_entity()`, `search_code()`, `list_projects()`

**Private methods:**
- Prefix with underscore: `_execute_query()`, `_normalize_path()`

### Searching for Patterns

```python
# Find existing queries
search_code("class.*Query:", search_type="pattern")

# Find existing handlers
search_code("class.*Handler:", search_type="pattern")

# Find repository methods
search_code("async def (get|search|find|list)", search_type="pattern")

# Find MCP tools
search_code("@mcp.tool", search_type="pattern")
```

---

## Stage 4: Extract Common (DRY Principle)

### Purpose

Identify and centralize shared logic to avoid duplication and create reusable components.

### When to Extract

**Extract to Value Object when:**
- Validation logic is duplicated
- Same normalization in multiple places
- Business rule applies to a concept
- Need immutable, self-validating type

**Extract to Utility Function when:**
- Pure function (no side effects)
- Used in multiple layers
- Simple transformation/computation
- No domain-specific validation

**Extract to Service when:**
- Complex orchestration logic
- Interacts with external systems
- Needs dependency injection
- Has mocked interfaces

### Value Object Pattern

**Example: FileType Value Object**

```python
# src/your_project/domain/values/file_type.py
from dataclasses import dataclass


@dataclass(frozen=True)
class FileType:
    """Normalized file type value object."""

    extension: str

    def __post_init__(self):
        """Validate and normalize."""
        if not self.extension or not self.extension.strip():
            raise ValueError("file_type required")

        # Normalize
        normalized = self.extension.strip().lstrip(".").lower()

        if not normalized:
            raise ValueError("file_type required")

        # Immutable update
        object.__setattr__(self, "extension", normalized)

    def __str__(self) -> str:
        return self.extension

    def with_dot(self) -> str:
        return f".{self.extension}"
```

**Usage:**
```python
# Before (duplicated in multiple places):
file_type = file_type.strip().lstrip(".").lower()

# After (centralized):
file_type = FileType(extension=user_input)
normalized = str(file_type)
```

### Utility Function Pattern

**Example: File Path Utilities**

```python
# src/your_project/application/utils/file_utils.py
from pathlib import Path


def normalize_path(path: str) -> Path:
    """Normalize file path to absolute Path object."""
    if not path:
        raise ValueError("path required")
    return Path(path).resolve()


def get_file_extension(path: str) -> str:
    """Extract file extension from path."""
    if not path:
        raise ValueError("path required")
    return Path(path).suffix.lstrip(".").lower()
```

### Searching for Duplication

```python
# Search for similar normalization
search_code("\.strip\(\).*\.lower\(\)", search_type="pattern")

# Search for similar validation
search_code("if not .* raise ValueError", search_type="pattern")

# Search for similar transformations
search_code("normalize", search_type="semantic")
```

### Testing Extracted Components

**Always test value objects and utilities separately:**

```python
# tests/unit/domain/values/test_file_type.py
class TestFileType:
    def test_normalizes_extension(self):
        assert str(FileType(extension=".PY")) == "py"

    def test_requires_extension(self):
        with pytest.raises(ValueError, match="file_type required"):
            FileType(extension="")

    def test_with_dot(self):
        assert FileType(extension="py").with_dot() == ".py"
```

---

## Stage 5: Implementation - Green (Make Test Pass)

### Purpose

Write minimum code to make tests pass. No gold plating, no extra features, just pass the tests.

### Implementation Order

1. **Create Query/Command class**
   - Frozen dataclass
   - Constructor validation in `__post_init__`
   - Use extracted value objects

2. **Create Handler class**
   - Constructor with DI
   - Single `execute()` method
   - Return ServiceResult

3. **Add Repository method** (if needed)
   - Update protocol (domain layer)
   - Implement in concrete class (infrastructure layer)
   - Return ServiceResult

4. **Wire to DI Container**
   - Register handler
   - Inject dependencies via lambda

### Query/Command Implementation

```python
# src/your_project/application/queries/my_feature.py
from dataclasses import dataclass
from typing import TYPE_CHECKING

from your_project.domain.values.file_type import FileType

if TYPE_CHECKING:
    from your_project.domain.repositories.code_repository import CodeRepository


@dataclass(frozen=True)
class MyQuery:
    """Query for my feature."""

    param: str

    def __post_init__(self):
        """Validate and normalize."""
        if not self.param:
            raise ValueError("param required")

        # Use value object for normalization
        normalized = SomeValueObject(value=self.param)
        object.__setattr__(self, "param", str(normalized))
```

### Handler Implementation

```python
from your_project.application.utils.service_result import ServiceResult


class MyHandler:
    """Handler for my feature."""

    def __init__(self, repository: "CodeRepository"):
        """Initialize with dependencies."""
        if not repository:
            raise ValueError("repository required")
        self._repository = repository

    async def execute(self, query: MyQuery) -> ServiceResult[list[dict]]:
        """Execute query."""
        # Delegate to repository
        return await self._repository.my_method(query.param)
```

### Repository Implementation

```python
# src/your_project/domain/repositories/code_repository.py (Protocol)
from typing import Protocol, runtime_checkable


@runtime_checkable
class CodeRepository(Protocol):
    """Protocol for code repository."""

    async def my_method(self, param: str) -> ServiceResult[list[dict]]:
        """My method description."""
        ...


# src/your_project/infrastructure/repositories/neo4j_code_repository.py (Implementation)
async def my_method(self, param: str) -> ServiceResult[list[dict]]:
    """My method implementation."""
    if not param:
        return ServiceResult.failure("param required")

    query = """
    MATCH (n:Node)
    WHERE n.property = $param
    RETURN n
    """

    try:
        async with self._driver.session(database=self._database) as session:
            result = await session.run(query, {"param": param})
            records = await result.data()
            return ServiceResult.success(records)
    except Exception as e:
        return ServiceResult.failure(f"Query failed: {e}")
```

### DI Container Registration

```python
# src/your_project/infrastructure/container.py
from your_project.application.queries.my_feature import MyHandler


class Container:
    def _register_query_handlers(self) -> None:
        """Register query handlers."""
        self.register(
            MyHandler,
            lambda: MyHandler(
                repository=self.resolve(CodeRepository)
            ),
        )
```

### Running Tests (Expect GREEN)

```bash
uv run pytest tests/unit/application/queries/test_my_feature.py -v

# Expected output:
# test_my_feature.py::TestMyQuery::test_constructor_requires_param PASSED
# test_my_feature.py::TestMyHandler::test_execute_calls_repository PASSED
# ... all PASSED ✅
```

---

## Stage 6: Refactor - Clean (Quality Gates)

### Purpose

Clean up code while keeping tests passing. Extract magic values, add documentation, fix quality gate failures.

### Quality Gate Checks

```bash
# Run all checks
./scripts/check_all.sh

# Individual checks
uv run pyright          # Type checking
uv run ruff check src/  # Linting
uv run vulture src/     # Dead code detection
uv run pytest tests/    # Tests
```

### Common Issues and Fixes

**Type Errors (Pyright):**

```python
# Error: Type of "result" is partially unknown
# Fix: Annotate return type explicitly
async def execute(self, query: MyQuery) -> ServiceResult[list[dict]]:
    result: ServiceResult[list[dict]] = await self._repository.my_method(query.param)
    return result
```

**Linting Errors (Ruff):**

```python
# Error: F401 [*] `typing.TYPE_CHECKING` imported but unused
# Fix: Remove or use it
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from your_project.domain.repositories.code_repository import CodeRepository

# Error: E501 Line too long (82 > 80)
# Fix: Break line
result = await self._repository.my_very_long_method_name(
    param1, param2, param3
)
```

**Dead Code (Vulture):**

```python
# Warning: unused import 'datetime'
# Fix: Remove it (or add to vulture whitelist if needed for type hints)
```

### Extracting Magic Values

```python
# ❌ BEFORE (magic strings)
query = "MATCH (n:Node) WHERE n.status = 'active' RETURN n"
if len(results) > 100:
    return results[:100]

# ✅ AFTER (extracted to constants/config)
class Neo4jCodeRepository:
    _QUERY_ACTIVE_NODES = "MATCH (n:Node) WHERE n.status = 'active' RETURN n"
    _MAX_RESULTS = 100

    async def get_active_nodes(self) -> ServiceResult[list]:
        results = await self._execute_query(self._QUERY_ACTIVE_NODES)
        if len(results) > self._MAX_RESULTS:
            return results[:self._MAX_RESULTS]
```

### Adding Docstrings

```python
class MyHandler:
    """
    Handler for executing my feature.

    This handler accepts a MyQuery and delegates to the repository
    to fetch the required data. Results are returned as ServiceResult
    to maintain consistent error handling.

    Args:
        repository: Code repository for querying data

    Returns:
        ServiceResult containing list of results or error message

    Raises:
        ValueError: If repository is None (fail-fast validation)
    """

    def __init__(self, repository: CodeRepository):
        """Initialize handler with injected dependencies."""
        if not repository:
            raise ValueError("repository required")
        self._repository = repository

    async def execute(self, query: MyQuery) -> ServiceResult[list[dict]]:
        """
        Execute the query.

        Args:
            query: Query object containing search parameters

        Returns:
            ServiceResult with list of matching results or error
        """
        return await self._repository.my_method(query.param)
```

---

## Stage 7: Integration Testing (Real Dependencies)

### Purpose

Test feature with real external dependencies (Neo4j, file system) to catch integration issues.

### Integration Test Structure

```python
# tests/integration/application/queries/test_my_feature_integration.py
import pytest

from your_project.application.queries.my_feature import (
    MyQuery,
    MyHandler,
)


@pytest.mark.integration
class TestMyFeatureIntegration:
    """Integration tests with real dependencies."""

    @pytest.mark.asyncio
    async def test_with_real_database(
        self,
        neo4j_repository,      # Real Neo4j connection
        indexed_test_data,     # Fixture that creates test data
    ):
        """Test with real Neo4j database."""
        handler = MyHandler(repository=neo4j_repository)
        query = MyQuery(param="test_value")

        result = await handler.execute(query)

        assert result.success
        assert len(result.value) > 0
        # Verify actual data properties
        assert result.value[0]["property"] == "expected_value"
```

### Creating Integration Fixtures

```python
# tests/integration/conftest.py
import pytest
from neo4j import AsyncGraphDatabase

from your_project.infrastructure.repositories.neo4j_code_repository import (
    Neo4jCodeRepository,
)
from your_project.infrastructure.config.settings import Settings


@pytest.fixture
async def neo4j_repository(settings: Settings):
    """Provide real Neo4j repository."""
    repository = Neo4jCodeRepository(settings=settings)
    yield repository
    await repository.close()


@pytest.fixture
async def indexed_test_data(neo4j_repository):
    """Create test data in database."""
    # Insert test data
    query = """
    CREATE (n:Node {property: 'test_value', status: 'active'})
    RETURN n
    """
    await neo4j_repository._execute_query(query)

    yield

    # Cleanup: Delete test data
    cleanup_query = "MATCH (n:Node {property: 'test_value'}) DELETE n"
    await neo4j_repository._execute_query(cleanup_query)
```

### Running Integration Tests

```bash
# Ensure Neo4j is running
neo4j status

# Run integration tests
uv run pytest tests/integration/ -v -m integration

# Run specific integration test
uv run pytest tests/integration/application/queries/test_my_feature_integration.py -v
```

### Verifying Database State

```cypher
// Open Neo4j Browser: http://localhost:7474

// Check test data exists
MATCH (n:Node {property: 'test_value'})
RETURN n

// Verify query results
MATCH (n:Node)
WHERE n.status = 'active'
RETURN count(n)
```

---

## Stage 8: E2E Testing (MCP Interface)

### Purpose

Test feature through the MCP tool interface (how users actually use it) to verify end-to-end flow.

### Creating MCP Tools

```python
# src/your_project/interface/mcp_tools/my_tools.py
from fastmcp import FastMCP

from your_project.application.queries.my_feature import (
    MyQuery,
    MyHandler,
)
from your_project.infrastructure.container import Container

mcp = FastMCP("my-tools")
container = Container()


@mcp.tool()
async def my_feature_tool(param: str) -> dict:
    """
    Execute my feature via MCP.

    Args:
        param: Parameter for feature execution

    Returns:
        Dict with 'success' (bool) and 'results' (list) or 'error' (str)
    """
    handler = container.resolve(MyHandler)
    query = MyQuery(param=param)
    result = await handler.execute(query)

    if result.success:
        return {"success": True, "results": result.value}
    return {"success": False, "error": result.error}
```

### E2E Test Structure

```python
# tests/e2e/test_my_feature_e2e.py
import pytest

from your_project.interface.mcp_tools.my_tools import my_feature_tool


@pytest.mark.e2e
class TestMyFeatureE2E:
    """E2E tests calling MCP tools directly."""

    @pytest.mark.asyncio
    async def test_via_mcp_tool(self, initialized_repository):
        """Test feature through MCP tool interface."""
        result = await my_feature_tool(param="test_value")

        assert result["success"] is True
        assert "results" in result
        assert len(result["results"]) > 0

    @pytest.mark.asyncio
    async def test_error_handling_via_mcp(self):
        """Test error handling through MCP interface."""
        result = await my_feature_tool(param="")

        assert result["success"] is False
        assert "error" in result
        assert "required" in result["error"].lower()
```

### Running E2E Tests

```bash
uv run pytest tests/e2e/ -v -m e2e

# Run specific E2E test
uv run pytest tests/e2e/test_my_feature_e2e.py -v
```

### Monitoring Logs During E2E Tests

```bash
# Terminal 1: Run tests
uv run pytest tests/e2e/test_my_feature_e2e.py -v

# Terminal 2: Watch logs
tail -f logs/your_project.log | grep -i "my_feature"

# Expected log entries:
# [INFO] MCP tool invoked: my_feature_tool(param='test_value')
# [DEBUG] Created MyQuery with param='test_value'
# [DEBUG] Executing repository method
# [INFO] Query returned 5 results in 23ms
# [INFO] MCP tool completed successfully
```

---

## Stage 9: Real Usage Validation (Manual Testing)

### Purpose

Test feature in actual Claude Code usage to catch issues that automated tests miss.

### Starting MCP Server

```bash
# Start server with logging
./run-mcp-server.sh

# Or start manually with verbose logging
uv run fastmcp run src/your_project/interface/mcp_tools/my_tools.py --log-level DEBUG
```

### Testing in Claude Code

**Natural Language Testing:**

```
User: "Use my feature to find test_value"

Claude: I'll use the my_feature_tool to search for that.
[Invokes: my_feature_tool(param="test_value")]

Results: Found 5 matching items:
- Item 1: ...
- Item 2: ...
...
```

**Direct Tool Invocation:**

```
User: "Call my_feature_tool with param='test'"

Claude: [Invokes: my_feature_tool(param="test")]
Results: { "success": true, "results": [...] }
```

### Monitoring Real-Time Logs

```bash
# Watch all logs
tail -f logs/your_project.log

# Filter for specific feature
tail -f logs/your_project.log | grep -i "my_feature"

# Watch for errors only
tail -f logs/your_project.log | grep -E "ERROR|EXCEPTION|FAILED"

# Watch for slow queries
tail -f logs/your_project.log | grep -E "[0-9]{3,}ms"
```

### Testing Edge Cases

**Common Edge Cases to Test:**

1. **Empty/null inputs:**
   ```
   my_feature_tool(param="")
   my_feature_tool(param=None)
   ```

2. **Special characters:**
   ```
   my_feature_tool(param="<script>alert('xss')</script>")
   my_feature_tool(param="'; DROP TABLE users;--")
   ```

3. **Unusual formats:**
   ```
   my_feature_tool(param="UPPERCASE")
   my_feature_tool(param="  whitespace  ")
   my_feature_tool(param="非英語文字")
   ```

4. **Non-existent data:**
   ```
   my_feature_tool(param="nonexistent_value_xyz")
   ```

5. **Performance limits:**
   ```
   # Large results
   # Complex queries
   # Concurrent requests
   ```

### Verifying Results

**Accuracy Check:**
- Do results match expectations?
- Are results complete (not truncated)?
- Are results in correct format?

**Performance Check:**
- Response time < 100ms (preferred)?
- No timeout errors?
- Consistent performance across requests?

**Error Handling Check:**
- Fail-fast on invalid input?
- Clear error messages?
- No stack traces exposed to user?

---

## Stage 10: Production Monitoring (OTEL + Final Validation)

### Purpose

Ensure feature is production-ready with comprehensive monitoring and final quality validation.

### OTEL Trace Analysis

```bash
# Analyze logs for OTEL traces
python3 .claude/tools/utils/log_analyzer.py logs/your_project.log

# Expected output:
# === OTEL Trace Analysis ===
# Total traces: 10
# Successful traces: 10 (100%)
# Failed traces: 0 (0%)
#
# === Performance Metrics ===
# Average query time: 18ms
# P95 query time: 45ms
# P99 query time: 67ms
#
# === Errors ===
# No errors detected ✅
```

### Performance Validation

**Query Performance Targets:**
- Average: < 50ms
- P95: < 100ms
- P99: < 200ms

**Neo4j Query Profiling:**

```cypher
// Open Neo4j Browser
// Profile query to check performance

PROFILE MATCH (n:Node)
WHERE n.status = 'active'
RETURN n

// Check for:
// - No full table scans (Cypher uses indexes)
// - DB hits reasonable for result size
// - Execution time < 100ms
```

**Adding Indexes (if needed):**

```cypher
// Create index on frequently queried property
CREATE INDEX node_status_index FOR (n:Node) ON (n.status)

// Verify index created
SHOW INDEXES
```

### Final Quality Gate Validation

```bash
./scripts/check_all.sh

# Must show:
# ✅ pyright: Type checking passed (0 errors)
# ✅ ruff: Linting passed (0 errors)
# ✅ vulture: Dead code detection passed (0 issues)
# ✅ pytest: All tests passed (N passed, 0 failed)
#
# === All quality gates PASSED ===
```

### Documentation Checklist

**Code Documentation:**
- [ ] All classes have docstrings
- [ ] All public methods documented
- [ ] Parameters and return types documented
- [ ] Exceptions documented

**API Documentation:**
- [ ] MCP tool parameters documented
- [ ] Return format documented
- [ ] Example usage provided

**Architecture Documentation:**
- [ ] ADR created (if new pattern introduced)
- [ ] ARCHITECTURE.md updated (if layer changes)
- [ ] Breaking changes noted in CHANGELOG

### Production Readiness Checklist

**Functionality:**
- [ ] All tests pass (unit + integration + E2E)
- [ ] Feature works in Claude Code
- [ ] Edge cases handled correctly

**Performance:**
- [ ] Query time < 100ms (average)
- [ ] No performance regressions
- [ ] Indexes created (if needed)

**Quality:**
- [ ] All quality gates pass
- [ ] No type errors
- [ ] No dead code
- [ ] Code reviewed (if team process)

**Monitoring:**
- [ ] OTEL traces clean
- [ ] No errors in logs
- [ ] Proper error messages

**Documentation:**
- [ ] Code documented
- [ ] API documented
- [ ] ADR created (if applicable)

**If ALL checkboxes are checked:** ✅ PRODUCTION READY

---

## Summary: The 10-Stage Flow

```
Stage 1: Planning (5-10 min)
  ↓ Know where it goes, what patterns to use
Stage 2: TDD - Red (10-15 min)
  ↓ Tests written, FAILING
Stage 3: Naming (5 min)
  ↓ Consistent names chosen
Stage 4: Extract Common (10 min)
  ↓ Duplication eliminated
Stage 5: Implementation - Green (20-30 min)
  ↓ Tests PASSING
Stage 6: Refactor (10-15 min)
  ↓ Quality gates PASSING
Stage 7: Integration Testing (15-20 min)
  ↓ Real dependencies tested
Stage 8: E2E Testing (15-20 min)
  ↓ MCP interface tested
Stage 9: Real Usage (10-15 min)
  ↓ Validated in Claude Code
Stage 10: Production Monitoring (5-10 min)
  ↓ OTEL traces clean, ready for production

✅ PRODUCTION READY
```

**Total Time:** ~2-3 hours for complete feature (simple to moderate complexity)

**Key Principle:** Each stage validates the previous stage. If a stage fails, return to the previous stage and fix before proceeding.
