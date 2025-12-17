# Pattern Guide - implement-repository-pattern

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [generate_repository.py](../examples/generate_repository.py) - Generates repository pattern files with protocol and implementation
- [analyze_queries.py](../examples/analyze_queries.py) - Analyzes Cypher queries in repositories
- [validate_repository_patterns.py](../examples/validate_repository_patterns.py) - Validates repository pattern compliance

---

## Repository Pattern Overview

The Repository Pattern provides an abstraction layer between domain logic and data access. In Clean Architecture, repositories are defined as **Protocols** (interfaces) in the domain layer and **implemented** in the infrastructure layer.

### Why Repository Pattern?

1. **Dependency Inversion**: Domain doesn't depend on infrastructure
2. **Testability**: Easy to mock for unit tests
3. **Flexibility**: Swap implementations (Neo4j → PostgreSQL → MongoDB)
4. **Separation of Concerns**: Business logic separate from data access

---

## Core Patterns

### Pattern 1: Protocol Definition

**Location:** `domain/repositories/`

**Structure:**
```python
from abc import ABC, abstractmethod
from your_project.domain.common import ServiceResult

class {Name}Repository(ABC):
    """Port for {purpose}.

    This interface defines the contract for {operations}.
    Concrete implementations will be provided in infrastructure layer.
    """

    @abstractmethod
    async def operation_name(
        self,
        param: Type
    ) -> ServiceResult[ReturnType]:
        """Brief operation description.

        Args:
            param: Parameter description

        Returns:
            ServiceResult[ReturnType]: Success with data or Failure on errors
        """
        pass
```

**Key Elements:**
- Inherit from `ABC`
- Use `@abstractmethod` decorator
- Return `ServiceResult[T]` for all operations
- Use `async` for all methods (I/O operations)
- Document args, returns, and error cases

---

### Pattern 2: Neo4j Implementation

**Location:** `infrastructure/neo4j/`

**Structure:**
```python
from neo4j import AsyncDriver, RoutingControl
from your_project.domain.repositories.{name}_repository import {Name}Repository
from your_project.domain.services.resource_manager import ManagedResource

class Neo4j{Name}Repository({Name}Repository, ManagedResource):
    """Neo4j adapter implementing {Name}Repository."""

    def __init__(self, driver: AsyncDriver, settings: Settings):
        # Validation
        if not driver:
            raise ValueError("Neo4j driver is required")
        if not settings:
            raise ValueError("Settings is required")

        # Store dependencies
        self.driver = driver
        self.settings = settings
        self.database = settings.neo4j.database_name

    async def operation_name(
        self, param: Type
    ) -> ServiceResult[ReturnType]:
        """Implement operation."""
        query = CypherQueries.OPERATION_NAME
        params = {"param": param}

        result = await self._execute_with_retry(query, params)
        if result.is_failure:
            return ServiceResult.fail(f"Operation failed: {result.error}")

        # Transform data
        data = self._transform_result(result.data)
        return ServiceResult.ok(data)

    async def close(self) -> None:
        """Cleanup resources."""
        # Repository-specific cleanup
        pass
```

**Key Elements:**
- Implement Protocol interface
- Inherit from `ManagedResource`
- Validate constructor parameters
- Use `_execute_with_retry()` for all database ops
- Return `ServiceResult[T]` consistently
- Implement `close()` for cleanup

---

### Pattern 3: Query Execution with Retry

**Purpose:** Handle transient failures and validate parameters

**Structure:**
```python
async def _execute_with_retry(
    self,
    query: str,
    parameters: dict[str, Any] | None = None,
    routing: RoutingControl = RoutingControl.WRITE,
) -> ServiceResult[list[dict]]:
    """Execute query with validation and retry logic."""
    # Step 1: Validate query parameters
    validation_result = validate_and_build_query(query, parameters, strict=True)
    if validation_result.is_failure:
        logger.error(f"Query validation failed: {validation_result.error}")
        return ServiceResult.fail(f"Validation failed: {validation_result.error}")

    validated_query = validation_result.data
    assert validated_query is not None

    # Step 2: Log warnings
    if validated_query.validation_result.warnings:
        for warning in validated_query.validation_result.warnings:
            logger.warning(f"Query validation warning: {warning}")

    # Step 3: Execute with driver
    try:
        records, _, _ = await self.driver.execute_query(
            cast(LiteralString, validated_query.query),
            validated_query.parameters,
            database_=self.database,
            routing_=routing,
        )
        return ServiceResult.ok([dict(record) for record in records])
    except ServiceUnavailable as e:
        logger.error(f"Neo4j service unavailable: {e}")
        return ServiceResult.fail(f"Database unavailable: {str(e)}")
    except Neo4jError as e:
        logger.error(f"Neo4j error: {e}")
        return ServiceResult.fail(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ServiceResult.fail(f"Unexpected error: {str(e)}")
```

**Benefits:**
- **Parameter Validation**: Catches injection risks before execution
- **Type Safety**: Uses `LiteralString` for Cypher queries
- **Error Handling**: Distinguishes database vs validation errors
- **Automatic Retry**: Driver handles transient failures
- **Logging**: Tracks warnings and errors for debugging

---

## Query Patterns

### Pattern 4: MERGE for Upsert

**Purpose:** Create or update nodes/relationships idempotently

**Structure:**
```python
MERGE (n:Label {id: $id})
SET n.property = $value
SET n.updated_at = datetime()
RETURN n
```

**When to Use:**
- Creating or updating entities
- Ensuring uniqueness
- Idempotent operations

**Example:**
```python
async def save_entity(self, entity_id: str, data: dict) -> ServiceResult[None]:
    """Save or update entity."""
    cypher = """
    MERGE (e:Entity {id: $id})
    SET e += $data
    SET e.updated_at = datetime()
    """

    result = await self._execute_with_retry(
        cypher,
        {"id": entity_id, "data": data}
    )
    return ServiceResult.ok(None) if result.is_success else result
```

---

### Pattern 5: UNWIND for Batch Operations

**Purpose:** Process multiple items in single transaction

**Structure:**
```python
UNWIND $items AS item
MERGE (n:Label {id: item.id})
SET n += item.properties
```

**When to Use:**
- Bulk inserts/updates
- Processing lists of entities
- Reducing round trips

**Example:**
```python
async def save_entities_batch(
    self, entities: list[dict]
) -> ServiceResult[int]:
    """Save multiple entities in one transaction."""
    cypher = """
    UNWIND $entities AS entity
    MERGE (e:Entity {id: entity.id})
    SET e += entity.data
    RETURN count(e) AS saved_count
    """

    result = await self._execute_with_retry(
        cypher,
        {"entities": entities}
    )
    if result.is_failure:
        return result

    count = result.data[0]["saved_count"] if result.data else 0
    return ServiceResult.ok(count)
```

---

### Pattern 6: OPTIONAL MATCH for Nullable Relationships

**Purpose:** Handle cases where relationships may not exist

**Structure:**
```python
MATCH (n:Node {id: $id})
OPTIONAL MATCH (n)-[r:REL]->(m:Related)
RETURN n, collect(m) AS related
```

**When to Use:**
- Fetching entity with optional relationships
- Avoiding empty result sets
- Building domain aggregates

**Example:**
```python
async def get_entity_with_relations(
    self, entity_id: str
) -> ServiceResult[dict]:
    """Get entity with optional relationships."""
    cypher = """
    MATCH (e:Entity {id: $id})
    OPTIONAL MATCH (e)-[:USES]->(dep:Dependency)
    OPTIONAL MATCH (e)<-[:DEPENDS_ON]-(dependent:Entity)
    RETURN e,
           collect(DISTINCT dep) AS dependencies,
           collect(DISTINCT dependent) AS dependents
    """

    result = await self._execute_with_retry(
        cypher,
        {"id": entity_id},
        routing=RoutingControl.READ
    )
    if result.is_failure:
        return result

    if not result.data:
        return ServiceResult.fail(f"Entity {entity_id} not found")

    record = result.data[0]
    return ServiceResult.ok({
        "entity": record["e"],
        "dependencies": record["dependencies"],
        "dependents": record["dependents"],
    })
```

---

## ServiceResult Patterns

### Pattern 7: Early Return on Failure

**Purpose:** Propagate errors without nesting

**Structure:**
```python
result = await self._execute_with_retry(query, params)
if result.is_failure:
    return ServiceResult.fail(f"Context: {result.error}")

# Success path continues
data = self._transform(result.data)
return ServiceResult.ok(data)
```

**Benefits:**
- Reduces nesting
- Clear error context
- Easy to trace failures

---

### Pattern 8: Chaining ServiceResults

**Purpose:** Compose operations that return ServiceResult

**Structure:**
```python
async def complex_operation(self, id: str) -> ServiceResult[dict]:
    """Perform multi-step operation."""
    # Step 1
    entity_result = await self.get_entity(id)
    if entity_result.is_failure:
        return entity_result  # Propagate failure

    entity = entity_result.data

    # Step 2
    relations_result = await self.get_relations(id)
    if relations_result.is_failure:
        return relations_result  # Propagate failure

    # Combine results
    return ServiceResult.ok({
        "entity": entity,
        "relations": relations_result.data,
    })
```

---

### Pattern 9: Transforming Success Results

**Purpose:** Map database records to domain models

**Structure:**
```python
result = await self._execute_with_retry(query, params)
if result.is_failure:
    return result

# Transform records to domain models
entities = [self._to_domain_model(r) for r in result.data]
return ServiceResult.ok(entities)
```

**Example:**
```python
def _to_domain_model(self, record: dict) -> Entity:
    """Convert Neo4j record to domain Entity."""
    return Entity(
        identity=Identity(
            value=record["id"],
            entity_type=record["type"],
            project_name=record["project_name"],
        ),
        name=record["name"],
        file_path=record["file_path"],
        start_line=record["start_line"],
        end_line=record["end_line"],
    )
```

---

## Resource Management Patterns

### Pattern 10: ManagedResource Lifecycle

**Purpose:** Ensure proper resource cleanup

**Structure:**
```python
class Neo4jRepository(Repository, ManagedResource):
    """Repository with managed lifecycle."""

    def __init__(self, driver: AsyncDriver, settings: Settings):
        # Initialize resources
        self.driver = driver
        self._connection_pool = None

    async def close(self) -> None:
        """Cleanup repository-specific resources."""
        try:
            # Close any repository-specific resources
            if self._connection_pool:
                await self._connection_pool.close()

            logger.debug(f"{self.__class__.__name__} cleanup complete")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            # Don't raise - cleanup should be best-effort
```

**Key Points:**
- Driver is managed externally by container
- Only cleanup repository-specific resources
- Log cleanup for debugging
- Don't raise exceptions (best-effort)

---

## Container Registration Patterns

### Pattern 11: Protocol Return Type

**Purpose:** Return interface, not implementation

**Structure:**
```python
# Container method
async def entity_repository(self) -> EntityRepository:
    """Provide EntityRepository implementation.

    Returns Protocol type, not concrete implementation.
    """
    driver = await self.neo4j_driver()
    settings = await self.settings()
    return Neo4jEntityRepository(driver, settings)
```

**Benefits:**
- Clients depend on abstraction
- Easy to swap implementations
- Follows Dependency Inversion Principle

---

### Pattern 12: Lazy Initialization

**Purpose:** Create repositories only when needed

**Structure:**
```python
@cached_property
async def entity_repository(self) -> EntityRepository:
    """Lazy-load entity repository."""
    if not hasattr(self, "_entity_repository"):
        driver = await self.neo4j_driver()
        settings = await self.settings()
        self._entity_repository = Neo4jEntityRepository(driver, settings)
    return self._entity_repository
```

**Benefits:**
- Reduces startup time
- Saves memory for unused repositories
- Initializes only once

---

## Testing Patterns

### Pattern 13: Mock Driver Setup

**Purpose:** Unit test repository without database

**Structure:**
```python
@pytest.fixture
def mock_driver():
    """Create mock Neo4j driver."""
    driver = AsyncMock()
    driver.execute_query = AsyncMock()
    return driver

@pytest.mark.asyncio
async def test_save_entity(mock_driver, settings):
    """Test entity save operation."""
    # Arrange
    repo = Neo4jEntityRepository(mock_driver, settings)
    mock_driver.execute_query.return_value = ([], None, None)

    # Act
    result = await repo.save_entity("test-id", {"name": "Test"})

    # Assert
    assert result.is_success
    mock_driver.execute_query.assert_called_once()
```

---

### Pattern 14: Integration Test Cleanup

**Purpose:** Ensure clean state between tests

**Structure:**
```python
@pytest.fixture
async def cleanup_neo4j(neo4j_driver, settings):
    """Cleanup Neo4j after test."""
    yield
    # Cleanup after test
    await neo4j_driver.execute_query(
        "MATCH (n) WHERE n.test_marker = 'integration_test' DETACH DELETE n",
        database_=settings.neo4j.database_name,
    )

@pytest.mark.integration
@pytest.mark.asyncio
async def test_with_real_db(neo4j_driver, settings, cleanup_neo4j):
    """Test with real Neo4j instance."""
    repo = Neo4jEntityRepository(neo4j_driver, settings)
    # Test operations...
```

---

## Error Handling Patterns

### Pattern 15: Context-Specific Error Messages

**Purpose:** Provide actionable error information

**Structure:**
```python
async def get_entity(self, id: str) -> ServiceResult[Entity | None]:
    """Get entity by ID."""
    result = await self._execute_with_retry(query, {"id": id})
    if result.is_failure:
        # Add context to error
        return ServiceResult.fail(
            f"Failed to retrieve entity '{id}': {result.error}"
        )

    if not result.data:
        # Success with None (not found is not an error)
        return ServiceResult.ok(None)

    return ServiceResult.ok(self._to_domain_model(result.data[0]))
```

---

### Pattern 16: Distinguish Not Found vs Error

**Purpose:** Separate normal "not found" from actual errors

**Structure:**
```python
async def get_optional_entity(
    self, id: str
) -> ServiceResult[Entity | None]:
    """Get entity, None if not found.

    Returns:
        ServiceResult[Entity | None]: Success with Entity if found,
                                       Success with None if not found,
                                       Failure on database errors
    """
    result = await self._execute_with_retry(query, params)
    if result.is_failure:
        return ServiceResult.fail(f"Database error: {result.error}")

    # Not found is a success case
    if not result.data:
        return ServiceResult.ok(None)

    return ServiceResult.ok(self._to_domain_model(result.data[0]))

async def get_required_entity(
    self, id: str
) -> ServiceResult[Entity]:
    """Get entity, fail if not found.

    Returns:
        ServiceResult[Entity]: Success with Entity if found,
                               Failure if not found or database error
    """
    result = await self._execute_with_retry(query, params)
    if result.is_failure:
        return ServiceResult.fail(f"Database error: {result.error}")

    if not result.data:
        return ServiceResult.fail(f"Entity '{id}' not found")

    return ServiceResult.ok(self._to_domain_model(result.data[0]))
```

---

## Performance Patterns

### Pattern 17: Read vs Write Routing

**Purpose:** Optimize read operations with routing control

**Structure:**
```python
# Write operation (default)
async def save_entity(self, entity: Entity) -> ServiceResult[None]:
    """Save entity (write operation)."""
    result = await self._execute_with_retry(
        query,
        params,
        routing=RoutingControl.WRITE  # Explicit write
    )
    return result

# Read operation (optimized)
async def get_entity(self, id: str) -> ServiceResult[Entity | None]:
    """Get entity (read operation)."""
    result = await self._execute_with_retry(
        query,
        params,
        routing=RoutingControl.READ  # Read from replica
    )
    return result
```

---

### Pattern 18: Projection for Large Objects

**Purpose:** Return only needed fields

**Structure:**
```python
async def get_entity_summary(
    self, id: str
) -> ServiceResult[dict]:
    """Get entity summary (minimal fields)."""
    cypher = """
    MATCH (e:Entity {id: $id})
    RETURN e.id AS id,
           e.name AS name,
           e.type AS type
    """  # Only return needed fields, not entire node

    result = await self._execute_with_retry(
        cypher,
        {"id": id},
        routing=RoutingControl.READ
    )
    # ... transform and return
```

---

## Advanced Patterns

### Pattern 19: Transaction Management

**Purpose:** Execute multiple operations atomically

**Structure:**
```python
async def transfer_ownership(
    self,
    entity_id: str,
    old_owner: str,
    new_owner: str
) -> ServiceResult[None]:
    """Transfer entity ownership atomically."""
    # Note: driver.execute_query handles transactions automatically
    cypher = """
    MATCH (e:Entity {id: $entity_id})
    MATCH (old:User {id: $old_owner})-[r:OWNS]->(e)
    MATCH (new:User {id: $new_owner})
    DELETE r
    CREATE (new)-[:OWNS]->(e)
    """

    result = await self._execute_with_retry(
        cypher,
        {
            "entity_id": entity_id,
            "old_owner": old_owner,
            "new_owner": new_owner,
        }
    )
    return ServiceResult.ok(None) if result.is_success else result
```

---

### Pattern 20: Aggregation with Relationships

**Purpose:** Build domain aggregates from graph data

**Structure:**
```python
async def get_file_with_entities(
    self, file_path: str, project_name: str
) -> ServiceResult[dict]:
    """Get file with all its entities and chunks."""
    cypher = """
    MATCH (f:File {path: $file_path, project_name: $project_name})
    OPTIONAL MATCH (f)-[:CONTAINS]->(e:Entity)
    OPTIONAL MATCH (f)-[:HAS_CHUNK]->(c:Chunk)
    RETURN f,
           collect(DISTINCT e) AS entities,
           collect(DISTINCT c) AS chunks
    """

    result = await self._execute_with_retry(
        cypher,
        {"file_path": file_path, "project_name": project_name},
        routing=RoutingControl.READ
    )
    if result.is_failure:
        return result

    if not result.data:
        return ServiceResult.fail(f"File {file_path} not found")

    record = result.data[0]
    return ServiceResult.ok({
        "file": self._to_file_model(record["f"]),
        "entities": [self._to_entity_model(e) for e in record["entities"]],
        "chunks": [self._to_chunk_model(c) for c in record["chunks"]],
    })
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Optional Settings

**Wrong:**
```python
def __init__(self, driver: AsyncDriver, settings: Settings | None = None):
    self.driver = driver
    self.settings = settings or Settings()  # Creates default!
```

**Right:**
```python
def __init__(self, driver: AsyncDriver, settings: Settings):
    if not driver:
        raise ValueError("Neo4j driver is required")
    if not settings:
        raise ValueError("Settings is required")

    self.driver = driver
    self.settings = settings
```

---

### ❌ Anti-Pattern 2: Returning None on Error

**Wrong:**
```python
async def get_entity(self, id: str) -> Entity | None:
    try:
        result = await self._execute_with_retry(query, params)
        return result.data[0] if result.data else None
    except Exception:
        return None  # Hides error!
```

**Right:**
```python
async def get_entity(self, id: str) -> ServiceResult[Entity | None]:
    result = await self._execute_with_retry(query, params)
    if result.is_failure:
        return ServiceResult.fail(f"Failed to get entity: {result.error}")

    if not result.data:
        return ServiceResult.ok(None)

    return ServiceResult.ok(self._to_domain_model(result.data[0]))
```

---

### ❌ Anti-Pattern 3: Direct Driver Usage

**Wrong:**
```python
async def save_entity(self, entity: Entity) -> ServiceResult[None]:
    # Skips validation!
    records, _, _ = await self.driver.execute_query(
        "MERGE (e:Entity {id: $id})",
        {"id": entity.id}
    )
    return ServiceResult.ok(None)
```

**Right:**
```python
async def save_entity(self, entity: Entity) -> ServiceResult[None]:
    # Uses validation and retry logic
    result = await self._execute_with_retry(
        CypherQueries.SAVE_ENTITY,
        {"id": entity.id, "data": entity.to_dict()}
    )
    return ServiceResult.ok(None) if result.is_success else result
```

---

## Summary

### Must-Have Patterns
1. ✅ Protocol in domain layer
2. ✅ Implementation in infrastructure layer
3. ✅ ServiceResult for all operations
4. ✅ ManagedResource for lifecycle
5. ✅ Parameter validation in constructor
6. ✅ _execute_with_retry for database ops
7. ✅ Proper error handling and context

### Optional Patterns (Use When Needed)
- Batch operations (UNWIND)
- Pagination (cursor-based)
- Aggregates (OPTIONAL MATCH)
- Transaction management
- Read/write routing optimization

### Always Avoid
- Optional settings parameters
- Returning None on errors
- Direct driver usage
- Skipping parameter validation
- Synchronous methods
- Missing tests
