# Troubleshooting - implement-repository-pattern

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [validate_repository_patterns.py](../examples/validate_repository_patterns.py) - Validates repository pattern compliance
- [analyze_queries.py](../examples/analyze_queries.py) - Analyzes Cypher queries in repositories
- [generate_repository.py](../examples/generate_repository.py) - Generates repository pattern files with protocol and implementation

---

## Common Issues and Solutions

### Issue 1: "Neo4j driver is required" ValueError

**Symptom:**
```
ValueError: Neo4j driver is required
```

**Cause:** Driver parameter is None in constructor

**Solution:**
Ensure driver is injected via container:
```python
# In container.py
async def {name}_repository(self) -> {Name}Repository:
    driver = await self.neo4j_driver()  # ← Ensure this is called
    settings = await self.settings()
    return Neo4j{Name}Repository(driver, settings)
```

**Test:**
```python
# Verify driver is not None
driver = await container.neo4j_driver()
assert driver is not None
```

---

### Issue 2: "Parameter validation failed: missing required parameter"

**Symptom:**
```
ServiceResult.fail: Parameter validation failed: missing required parameter 'id'
```

**Cause:** Query parameters don't match Cypher query placeholders

**Solution:**
Check parameter names match query:
```python
# Query uses $entity_id
cypher = "MATCH (e:Entity {id: $entity_id})"

# Parameters must use entity_id (not id)
parameters = {"entity_id": entity_id}  # ✅ Correct
parameters = {"id": entity_id}          # ❌ Wrong
```

**Debugging:**
```python
# Log query and parameters before execution
logger.debug(f"Query: {query}")
logger.debug(f"Parameters: {parameters}")
```

---

### Issue 3: ServiceResult returns dict instead of domain model

**Symptom:**
```
AttributeError: 'dict' object has no attribute 'name'
```

**Cause:** Forgot to convert Neo4j record to domain model

**Solution:**
Add transformation step:
```python
# ❌ Wrong - returns raw dict
result = await self._execute_with_retry(query, params)
return ServiceResult.ok(result.data[0])

# ✅ Correct - converts to domain model
result = await self._execute_with_retry(query, params)
if result.is_failure:
    return result

entity_data = result.data[0]["e"]
entity = self._to_domain_model(entity_data)
return ServiceResult.ok(entity)
```

---

### Issue 4: Tests fail with "mock_X not called"

**Symptom:**
```
AssertionError: Expected 'execute_query' to be called once. Called 0 times.
```

**Cause:** Query validation failed before driver call

**Solution:**
Check query validation passes:
```python
# Mock validation to succeed
from your_project.infrastructure.neo4j.query_builder import (
    ValidatedQuery,
    ValidationResult,
)

mock_validation = ValidatedQuery(
    query="MATCH (e:Entity) RETURN e",
    parameters={"id": "test"},
    validation_result=ValidationResult(is_valid=True, errors=[], warnings=[]),
)

# Patch validate_and_build_query
with patch("..validate_and_build_query") as mock_validate:
    mock_validate.return_value = ServiceResult.ok(mock_validation)
    # Now test will proceed to driver call
```

---

### Issue 5: Integration tests fail with "Database unavailable"

**Symptom:**
```
ServiceResult.fail: Database unavailable: Unable to connect to localhost:7687
```

**Cause:** Neo4j not running or wrong connection settings

**Solution:**
1. Start Neo4j Desktop
2. Verify connection settings:
```python
# In tests/conftest.py
@pytest.fixture
def neo4j_settings():
    return Settings(
        neo4j=Neo4jSettings(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            database_name="neo4j",
        )
    )
```

3. Test connection:
```bash
cypher-shell -u neo4j -p password "RETURN 1"
```

---

### Issue 6: "Entity not found" when it exists

**Symptom:**
Repository returns None for existing entity

**Cause:** Query returns no results due to missing project_name filter

**Solution:**
Always include project_name in queries:
```python
# ❌ Wrong - no project filter
cypher = "MATCH (e:Entity {id: $id}) RETURN e"

# ✅ Correct - includes project_name
cypher = "MATCH (e:Entity {id: $id, project_name: $project_name}) RETURN e"
parameters = {"id": entity_id, "project_name": project_name}
```

---

### Issue 7: Circular import when importing domain models

**Symptom:**
```
ImportError: cannot import name '{Model}' from partially initialized module
```

**Cause:** Domain models importing from infrastructure

**Solution:**
1. Move import inside method (lazy import):
```python
async def get_entity(self, id: str) -> ServiceResult[Entity]:
    from your_project.domain.models.entity import Entity  # ← Inside method
    # ...
```

2. Or fix domain layer imports (never import from infrastructure):
```python
# In domain/models/entity.py
# ❌ Wrong
from your_project.infrastructure.neo4j import Neo4jCodeRepository

# ✅ Correct - only import from domain
from your_project.domain.repositories.code_repository import CodeRepository
```

---

### Issue 8: Type checker complains about async methods

**Symptom:**
```
error: Method must have at least one argument [misc]
```

**Cause:** Forgot `self` parameter or `async` keyword

**Solution:**
```python
# ❌ Wrong
async def get_entity() -> ServiceResult[Entity]:
    pass

# ✅ Correct
async def get_entity(self, id: str) -> ServiceResult[Entity]:
    pass
```

---

### Issue 9: Repository not registered in container

**Symptom:**
```
AttributeError: 'Container' object has no attribute '{name}_repository'
```

**Cause:** Forgot to add repository method to container

**Solution:**
Add to `src/your_project/infrastructure/container.py`:
```python
async def {name}_repository(self) -> {Name}Repository:
    """Provide {Name}Repository implementation."""
    driver = await self.neo4j_driver()
    settings = await self.settings()
    return Neo4j{Name}Repository(driver, settings)
```

---

### Issue 10: Query returns empty list instead of None

**Symptom:**
Repository returns `[]` when expecting `None`

**Cause:** Didn't handle empty result set correctly

**Solution:**
Distinguish between "not found" and "empty list":
```python
# For get_entity (single result)
result = await self._execute_with_retry(query, params)
if not result.data:
    return ServiceResult.ok(None)  # Not found

# For get_entities (list result)
result = await self._execute_with_retry(query, params)
if not result.data:
    return ServiceResult.ok([])  # Empty list, not None
```

---

### Issue 11: Transaction rollback on validation error

**Symptom:**
```
Neo4j.TransactionError: Transaction already closed
```

**Cause:** Validation error after transaction started

**Solution:**
Always validate BEFORE starting transaction:
```python
# ✅ Correct - validate first
validation_result = validate_and_build_query(query, parameters, strict=True)
if validation_result.is_failure:
    return ServiceResult.fail(f"Validation failed: {validation_result.error}")

# Then execute (transaction starts here)
records, _, _ = await self.driver.execute_query(...)
```

---

### Issue 12: Memory leak from unclosed repositories

**Symptom:**
Tests slow down over time, memory usage increases

**Cause:** Not calling `close()` on repositories

**Solution:**
Use context manager or ensure cleanup:
```python
# Option 1: Manual cleanup
repo = Neo4j{Name}Repository(driver, settings)
try:
    result = await repo.get_entity("test-id")
finally:
    await repo.close()

# Option 2: Pytest fixture with cleanup
@pytest.fixture
async def repository(neo4j_driver, settings):
    repo = Neo4j{Name}Repository(neo4j_driver, settings)
    yield repo
    await repo.close()
```

---

### Issue 13: ServiceResult.ok() called with wrong type

**Symptom:**
```
Type error: Expected 'None' but got 'dict'
```

**Cause:** Method signature says `ServiceResult[None]` but returns data

**Solution:**
Match return type to signature:
```python
# ❌ Wrong
async def save_entity(self, entity: Entity) -> ServiceResult[None]:
    result = await self._execute_with_retry(...)
    return ServiceResult.ok(result.data)  # Returns dict, not None!

# ✅ Correct
async def save_entity(self, entity: Entity) -> ServiceResult[None]:
    result = await self._execute_with_retry(...)
    if result.is_failure:
        return result
    return ServiceResult.ok(None)  # Returns None as signature says
```

---

### Issue 14: Batch operation creates duplicates

**Symptom:**
UNWIND creates multiple nodes when expecting one

**Cause:** Using CREATE instead of MERGE

**Solution:**
Use MERGE for idempotent batch operations:
```python
# ❌ Wrong - creates duplicates
cypher = """
UNWIND $entities AS entity
CREATE (e:Entity {id: entity.id})
"""

# ✅ Correct - merges (upsert)
cypher = """
UNWIND $entities AS entity
MERGE (e:Entity {id: entity.id})
SET e += entity.data
"""
```

---

### Issue 15: Query timeout on large result sets

**Symptom:**
```
Neo4j.ClientError: Query execution timed out
```

**Cause:** Fetching too many records without LIMIT

**Solution:**
Always use LIMIT for potentially large queries:
```python
# ❌ Wrong - no limit
cypher = """
MATCH (e:Entity {project_name: $project_name})
RETURN e
"""

# ✅ Correct - with limit
cypher = """
MATCH (e:Entity {project_name: $project_name})
RETURN e
LIMIT $limit
"""
parameters = {"project_name": project_name, "limit": 1000}
```

---

## Debugging Checklist

When repository operations fail:

1. **Check Logs:**
   ```bash
   tail -f logs/your_project.log | grep -i "neo4j\|repository"
   ```

2. **Verify Database Connection:**
   ```bash
   cypher-shell -u neo4j -p password "RETURN 1"
   ```

3. **Test Query Directly:**
   ```python
   # In cypher-shell
   MATCH (e:Entity {id: "test-id", project_name: "test"}) RETURN e;
   ```

4. **Check Parameter Types:**
   ```python
   # Log parameter types
   logger.debug(f"Parameters: {parameters}")
   logger.debug(f"Types: {[(k, type(v)) for k, v in parameters.items()]}")
   ```

5. **Validate Query Syntax:**
   ```python
   # Test validation
   from your_project.infrastructure.neo4j.query_builder import validate_and_build_query
   result = validate_and_build_query(query, parameters, strict=True)
   print(result.error if result.is_failure else "Valid")
   ```

6. **Run Unit Tests:**
   ```bash
   uv run pytest tests/unit/infrastructure/neo4j/test_{name}_repository.py -v
   ```

7. **Run Integration Tests:**
   ```bash
   uv run pytest tests/integration/infrastructure/neo4j/test_{name}_repository.py -v
   ```

8. **Check Quality Gates:**
   ```bash
   ./scripts/check_all.sh
   ```

---

## Getting Help

If issue persists:

1. **Check Logs:** Look for ERROR/WARNING messages
2. **Review Examples:** See [examples/examples.md](../examples/examples.md)
3. **Consult Pattern Guide:** See [pattern-guide.md](./pattern-guide.md)
4. **Run Diagnostics:**
   ```bash
   # Check Neo4j status
   python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity(); print('Connected')"

   # Check settings
   python -c "from your_project.config.settings import Settings; s = Settings(); print(f'Neo4j URI: {s.neo4j.uri}')"
   ```

5. **Ask for Help:** Provide:
   - Error message (full traceback)
   - Relevant code snippet
   - Query and parameters
   - Log excerpt showing failure
