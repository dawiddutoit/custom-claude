# Reference - Implement CQRS Handler

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [generate_handler.py](../examples/generate_handler.py) - Generates CQRS handler boilerplate (command or query)
- [list_handlers.py](../examples/list_handlers.py) - Inventories and lists all CQRS handlers in a project
- [validate_cqrs_separation.py](../examples/validate_cqrs_separation.py) - Validates CQRS pattern separation (commands vs queries)

---

## CQRS Pattern Overview

**CQRS (Command Query Responsibility Segregation)** separates read operations (queries) from write operations (commands), enabling optimized handling of each concern.

### Core Principle

> "A method should either change state or return data, never both." - Bertrand Meyer, Command-Query Separation

### In This Project

- **Commands**: Modify system state, return `ServiceResult[None]`
- **Queries**: Read data, return `ServiceResult[TResult]` with DTOs
- **Handlers**: Execute commands/queries using injected dependencies
- **ServiceResult**: Wraps all results with success/failure state

---

## Command Pattern

### Definition

Commands represent **intent to change state** and contain all data needed to perform the operation.

### Characteristics

- **Write operations**: Create, update, delete
- **Side effects**: Modify database, files, external systems
- **Return type**: `ServiceResult[None]` (no data returned)
- **Idempotent**: Where possible, safe to retry
- **Validation**: Strict parameter checking before execution

### Command Flow

```
1. MCP Tool receives request
2. Creates Command object with parameters
3. Passes to CommandHandler.handle()
4. Handler validates inputs
5. Handler orchestrates domain services
6. Handler persists changes
7. Returns ServiceResult[None] with metadata
```

### When to Use Commands

| Use Command For | Examples |
|----------------|----------|
| Creating entities | IndexFile, InitializeProject |
| Modifying state | UpdateFile, RefreshRepository |
| Deleting data | DeleteFile, ClearIndex |
| Side effects | SendNotification, TriggerBuild |

### Command Structure

```python
# 1. Command object (data container)
@dataclass
class IndexFileCommand(Command):
    file_path: Path
    project_name: str
    force_reindex: bool = False

# 2. Handler (business logic)
class IndexFileHandler(CommandHandler[IndexFileCommand]):
    def __init__(self, repository: CodeRepository, service: IndexingService):
        self.repository = repository
        self.service = service

    async def handle(self, command: IndexFileCommand) -> ServiceResult[None]:
        # Validate → Execute → Persist → Return
        return ServiceResult.ok(None)
```

---

## Query Pattern

### Definition

Queries represent **requests for data** without changing system state.

### Characteristics

- **Read operations**: Fetch, search, filter
- **No side effects**: Database reads only, no modifications
- **Return type**: `ServiceResult[TResult]` with data
- **DTOs**: Use Data Transfer Objects for structured results
- **Caching**: Safe to cache (no state changes)

### Query Flow

```
1. MCP Tool receives request
2. Creates Query object with parameters
3. Passes to QueryHandler.handle()
4. Handler validates query
5. Handler fetches data from repository
6. Handler converts to DTOs
7. Returns ServiceResult[TResult] with DTOs
```

### When to Use Queries

| Use Query For | Examples |
|--------------|----------|
| Searching data | SearchCode, FindRelated |
| Retrieving statistics | GetStats, GetFileInfo |
| Listing entities | ListFiles, ListEntities |
| Filtering results | FilterByLanguage, FilterByType |

### Query Structure

```python
# 1. Query object (filter parameters)
@dataclass
class SearchCodeQuery(Query):
    query_text: str
    project_name: str
    limit: int = 10

# 2. DTO (result structure)
@dataclass
class SearchResultDTO:
    file_path: str
    content: str
    score: float

# 3. Handler (data retrieval)
class SearchCodeHandler(QueryHandler[SearchCodeQuery, list[SearchResultDTO]]):
    def __init__(self, repository: SearchRepository):
        self.repository = repository

    async def handle(self, query: SearchCodeQuery) -> ServiceResult[list[SearchResultDTO]]:
        # Validate → Fetch → Convert → Return
        return ServiceResult.ok(dtos)
```

---

## ServiceResult Pattern

### Definition

`ServiceResult[T]` wraps operation results with success/failure state, eliminating `None` returns and exceptions for control flow.

### Structure

```python
@dataclass
class ServiceResult(Generic[T]):
    success: bool
    data: T | None
    error: str | None
    metadata: dict[str, Any]

    @staticmethod
    def ok(data: T, **metadata) -> ServiceResult[T]:
        """Create success result."""
        return ServiceResult(success=True, data=data, error=None, metadata=metadata)

    @staticmethod
    def fail(error: str, **metadata) -> ServiceResult[T]:
        """Create failure result."""
        return ServiceResult(success=False, data=None, error=error, metadata=metadata)
```

### Usage Patterns

**Success with metadata:**
```python
return ServiceResult.ok(
    None,
    items_processed=10,
    duration_ms=250
)
```

**Failure with context:**
```python
return ServiceResult.fail(
    "File not found",
    file_path=str(path),
    operation="index_file"
)
```

**Chaining results:**
```python
result = await self.repository.fetch_data()
if not result.success:
    return ServiceResult.fail(result.error)

# Continue with result.data
```

---

## Dependency Injection

### Container Registration

All handlers are registered in `src/your_project/interfaces/mcp/container.py`:

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # 1. Define configuration
    settings = providers.Dependency(instance_of=Settings)

    # 2. Define repositories
    code_repository = providers.Singleton(
        Neo4jCodeRepository,
        driver=neo4j_driver,
        settings=settings,
    )

    # 3. Define services
    embedding_service = providers.Singleton(
        create_embedding_service,
        settings=settings,
    )

    # 4. Define handlers (inject dependencies)
    index_file_handler = providers.Singleton(
        IndexFileHandler,
        code_repository=code_repository,  # Auto-resolved
        embedding_service=embedding_service,
    )
```

### Handler Constructor Pattern

**Always validate dependencies (fail-fast):**

```python
def __init__(
    self,
    repository: CodeRepository,
    service: EmbeddingService,
):
    """Initialize with required dependencies.

    Args:
        repository: Code repository (required)
        service: Embedding service (required)

    Raises:
        ValueError: If any dependency is None
    """
    if not repository:
        raise ValueError("CodeRepository required")
    if not service:
        raise ValueError("EmbeddingService required")

    self.repository = repository
    self.service = service
```

**Why:**
- Fails at construction time, not runtime
- Makes dependencies explicit and testable
- Prevents `None` reference errors
- Enforces configuration injection

---

## DTO (Data Transfer Object) Pattern

### Purpose

DTOs carry data between layers without exposing domain entities to the interface layer.

### Characteristics

- **Immutable**: Use `@dataclass` (frozen optional)
- **No business logic**: Pure data containers
- **Serializable**: Can convert to/from dict/JSON
- **Layer boundary**: Application → Interface

### DTO Guidelines

**1. Create DTO for complex results:**
```python
@dataclass
class SearchResultDTO:
    file_path: str
    line_number: int
    content: str
    similarity_score: float
    metadata: dict[str, Any]
```

**2. Provide conversion methods:**
```python
def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for JSON serialization."""
    return {
        "file_path": self.file_path,
        "line_number": self.line_number,
        "content": self.content,
        "similarity_score": self.similarity_score,
        "metadata": self.metadata,
    }

@classmethod
def from_entity(cls, entity: Chunk) -> "SearchResultDTO":
    """Create DTO from domain entity."""
    return cls(
        file_path=entity.file_path,
        line_number=entity.start_line,
        content=entity.content,
        similarity_score=0.0,  # Set by search
        metadata={},
    )
```

**3. Keep DTOs in `application/dto/`:**
```
src/your_project/application/dto/
├── search_result.py
├── stats_dto.py
└── file_info_dto.py
```

---

## Handler Testing

### Unit Test Structure

```python
import pytest
from unittest.mock import AsyncMock
from your_project.domain.common import ServiceResult

@pytest.mark.asyncio
async def test_command_handler_success():
    """Test successful command execution."""
    # Arrange
    mock_repository = AsyncMock()
    mock_repository.save.return_value = ServiceResult.ok(None)

    handler = MyCommandHandler(repository=mock_repository)
    command = MyCommand(param1="test")

    # Act
    result = await handler.handle(command)

    # Assert
    assert result.success
    assert result.data is None  # Commands return None
    mock_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_query_handler_success():
    """Test successful query execution."""
    # Arrange
    mock_data = [{"id": "1", "name": "test"}]
    mock_repository = AsyncMock()
    mock_repository.fetch.return_value = ServiceResult.ok(mock_data)

    handler = MyQueryHandler(repository=mock_repository)
    query = MyQuery(filter="test", limit=10)

    # Act
    result = await handler.handle(query)

    # Assert
    assert result.success
    assert len(result.data) > 0  # Queries return data
    assert isinstance(result.data[0], MyDTO)
```

### Test Coverage Requirements

**Must test:**
1. ✅ Successful execution path
2. ✅ Validation failures (invalid inputs)
3. ✅ Repository failures (propagate errors)
4. ✅ Exception handling (unexpected errors)
5. ✅ Dependency validation (constructor fails)

---

## Common Patterns

### Pattern 1: Fallback Handling

```python
# Try primary approach, fallback to secondary
async def handle(self, query: SearchQuery) -> ServiceResult[list[DTO]]:
    # Try semantic search
    embedding_result = await self.embedding_service.generate_embedding(query.text)

    if embedding_result.success:
        return await self.repository.semantic_search(
            embedding=embedding_result.data,
            limit=query.limit
        )

    # Fallback to pattern search
    logger.warning("Embedding failed, falling back to pattern search")
    return await self.repository.pattern_search(
        query=query.text,
        limit=query.limit
    )
```

### Pattern 2: Batch Operations

```python
async def handle(self, command: BatchCommand) -> ServiceResult[None]:
    results = []
    for item in command.items:
        result = await self.service.process_item(item)
        if not result.success:
            # Either fail-fast or collect errors
            return ServiceResult.fail(f"Item failed: {result.error}")
        results.append(result.data)

    # Save all results atomically
    save_result = await self.repository.save_batch(results)
    if not save_result.success:
        return ServiceResult.fail(save_result.error)

    return ServiceResult.ok(None, items_processed=len(results))
```

### Pattern 3: Conditional Processing

```python
async def handle(self, command: IndexCommand) -> ServiceResult[None]:
    # Check if already indexed (unless forced)
    if not command.force_reindex:
        exists = await self.repository.file_exists(command.file_path)
        if exists.success and exists.data:
            logger.info("File already indexed, skipping")
            return ServiceResult.ok(None, skipped=True, reason="already_indexed")

    # Proceed with indexing
    return await self._index_file(command)
```

---

## Anti-Patterns to Avoid

### ❌ Returning None on Error

```python
# WRONG
async def handle(self, command: MyCommand) -> ServiceResult[None] | None:
    if error:
        return None  # Violates ServiceResult pattern

# CORRECT
async def handle(self, command: MyCommand) -> ServiceResult[None]:
    if error:
        return ServiceResult.fail("Error message")
```

### ❌ Query with Side Effects

```python
# WRONG
class GetStatsHandler(QueryHandler):
    async def handle(self, query: GetStatsQuery):
        stats = await self.repository.get_stats()
        await self.repository.update_last_accessed()  # Side effect!
        return ServiceResult.ok(stats)

# CORRECT - Use separate command for updates
class GetStatsHandler(QueryHandler):
    async def handle(self, query: GetStatsQuery):
        stats = await self.repository.get_stats()
        return ServiceResult.ok(stats)  # No side effects
```

### ❌ Command Returning Data

```python
# WRONG
class CreateFileHandler(CommandHandler):
    async def handle(self, command: CreateFileCommand) -> ServiceResult[File]:
        file = await self.repository.create(command.data)
        return ServiceResult.ok(file)  # Commands should return None

# CORRECT
class CreateFileHandler(CommandHandler):
    async def handle(self, command: CreateFileCommand) -> ServiceResult[None]:
        result = await self.repository.create(command.data)
        if not result.success:
            return ServiceResult.fail(result.error)
        return ServiceResult.ok(None, file_id=result.data.id)  # Metadata OK
```

### ❌ Optional Dependencies

```python
# WRONG
def __init__(self, repository: CodeRepository | None = None):
    self.repository = repository or create_default_repository()  # No defaults!

# CORRECT
def __init__(self, repository: CodeRepository):
    if not repository:
        raise ValueError("CodeRepository required")
    self.repository = repository
```

---

## Architecture Integration

### Clean Architecture Layers

```
Interface Layer (MCP Tools)
    ↓ calls
Application Layer (Handlers)
    ↓ uses
Domain Layer (Entities, Services)
    ↑ implements
Infrastructure Layer (Repositories)
```

**Dependencies flow inward:**
- Interface → Application → Domain ← Infrastructure
- Handlers orchestrate but don't implement business logic
- Repositories implement domain interfaces

### Handler Responsibilities

**Handlers SHOULD:**
- ✅ Validate inputs
- ✅ Orchestrate domain services
- ✅ Convert between DTOs and entities
- ✅ Return ServiceResult[T]
- ✅ Log operations with OpenTelemetry

**Handlers SHOULD NOT:**
- ❌ Implement business logic (use domain services)
- ❌ Know about database details (use repositories)
- ❌ Return domain entities (use DTOs)
- ❌ Handle HTTP/MCP protocol (interface layer concern)

---

## OpenTelemetry Integration

### Tracing with @traced

**All handlers use `@traced` decorator:**

```python
from your_project.core.monitoring import get_logger, traced

logger = get_logger(__name__)

class MyHandler(CommandHandler[MyCommand]):
    @traced  # Automatically creates trace span
    async def handle(self, command: MyCommand) -> ServiceResult[None]:
        logger.info("Starting operation")
        # Implementation
        logger.info("Operation completed")
        return ServiceResult.ok(None)
```

**Benefits:**
- Automatic span creation with handler name
- Distributed tracing across service calls
- Performance metrics (duration, throughput)
- Error tracking and context

### Logging Patterns

**Use structured logging:**

```python
# Include context in log messages
logger.info(f"Indexing file: {command.file_path} (project: {command.project_name})")

# Log errors with details
logger.error(f"Failed to index: {result.error}", extra={
    "file_path": str(command.file_path),
    "project": command.project_name,
    "error": result.error
})

# Use exception() for stacktraces
logger.exception(f"Unexpected error: {str(e)}")
```

---

## Decision Trees

### Should I Create a Command or Query?

```
Does this operation modify state?
├─ Yes → Command (returns ServiceResult[None])
│   ├─ Creates data? → Command
│   ├─ Updates data? → Command
│   ├─ Deletes data? → Command
│   └─ Has side effects? → Command
└─ No → Query (returns ServiceResult[TResult])
    ├─ Reads data? → Query
    ├─ Searches? → Query
    ├─ Filters? → Query
    └─ Aggregates? → Query
```

### Do I Need a DTO?

```
Is the query result complex?
├─ Single primitive value? → No DTO needed
│   └─ ServiceResult[int] / ServiceResult[str]
├─ Simple dict? → No DTO needed
│   └─ ServiceResult[dict[str, Any]]
└─ Complex/structured data? → Yes, create DTO
    ├─ Multiple fields? → DTO
    ├─ Nested structures? → DTO
    ├─ Needs serialization? → DTO
    └─ Cross-layer transfer? → DTO
```

---

## Performance Considerations

### Batch Processing

**For multiple items, batch repository calls:**

```python
# SLOW - N database calls
for chunk in chunks:
    await self.repository.save_chunk(chunk)

# FAST - 1 database call
await self.repository.save_chunks_batch(chunks)
```

### Async Operations

**Use `asyncio.gather()` for parallel operations:**

```python
# Sequential (slow)
embeddings1 = await self.service.generate_embedding(text1)
embeddings2 = await self.service.generate_embedding(text2)

# Parallel (fast)
embeddings1, embeddings2 = await asyncio.gather(
    self.service.generate_embedding(text1),
    self.service.generate_embedding(text2)
)
```

### Validation Performance

**Validate early, fail fast:**

```python
async def handle(self, command: MyCommand) -> ServiceResult[None]:
    # Validate BEFORE expensive operations
    if not command.file_path.exists():
        return ServiceResult.fail("File not found")  # Fast failure

    # Expensive operations only if validated
    content = command.file_path.read_text()
    result = await self.expensive_processing(content)
```

---

## References

- **CQRS Pattern**: https://martinfowler.com/bliki/CQRS.html
- **Command-Query Separation**: https://martinfowler.com/bliki/CommandQuerySeparation.html
- **Clean Architecture**: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- **ServiceResult Pattern**: Inspired by Rust's `Result<T, E>` type
- **Dependency Injection**: https://python-dependency-injector.ets-labs.org/
