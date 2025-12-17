# Query Patterns - implement-repository-pattern

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [analyze_queries.py](../examples/analyze_queries.py) - Analyzes Cypher queries in repositories
- [generate_repository.py](../examples/generate_repository.py) - Generates repository pattern files with protocol and implementation
- [validate_repository_patterns.py](../examples/validate_repository_patterns.py) - Validates repository pattern compliance

---

## Common Cypher Query Patterns for Repositories

This guide provides tested Cypher query patterns for common repository operations.

---

## Basic CRUD Patterns

### Pattern 1: Create or Update (MERGE)

**Purpose:** Idempotent upsert operation

**Query:**
```cypher
MERGE (e:Entity {id: $id, project_name: $project_name})
SET e.name = $name,
    e.type = $type,
    e.updated_at = datetime()
RETURN e
```

**Usage in Repository:**
```python
SAVE_ENTITY = """
MERGE (e:Entity {id: $id, project_name: $project_name})
SET e += $properties
SET e.updated_at = datetime()
RETURN e
"""
```

**Benefits:**
- Creates if doesn't exist, updates if exists
- Safe for concurrent operations
- Automatic timestamp management

---

### Pattern 2: Read by ID

**Purpose:** Fetch single entity by unique identifier

**Query:**
```cypher
MATCH (e:Entity {id: $id, project_name: $project_name})
RETURN e
```

**Usage in Repository:**
```python
GET_ENTITY = """
MATCH (e:Entity {id: $id, project_name: $project_name})
RETURN e
"""
```

**Returns:**
- Single record if found
- Empty result if not found

---

### Pattern 3: Read All by Project

**Purpose:** Fetch all entities for a project

**Query:**
```cypher
MATCH (e:Entity {project_name: $project_name})
RETURN e
ORDER BY e.name
LIMIT $limit
```

**Usage in Repository:**
```python
GET_ENTITIES_BY_PROJECT = """
MATCH (e:Entity {project_name: $project_name})
RETURN e
ORDER BY e.name
LIMIT $limit
"""
```

**Best Practices:**
- Always include LIMIT
- Use ORDER BY for consistent results
- Include project_name filter

---

### Pattern 4: Delete by ID

**Purpose:** Remove entity and its relationships

**Query:**
```cypher
MATCH (e:Entity {id: $id, project_name: $project_name})
DETACH DELETE e
RETURN count(e) AS deleted_count
```

**Usage in Repository:**
```python
DELETE_ENTITY = """
MATCH (e:Entity {id: $id, project_name: $project_name})
DETACH DELETE e
RETURN count(e) AS deleted_count
"""
```

**Notes:**
- `DETACH DELETE` removes relationships automatically
- Returns count for verification

---

### Pattern 5: Check Existence

**Purpose:** Verify entity exists without fetching data

**Query:**
```cypher
MATCH (e:Entity {id: $id, project_name: $project_name})
RETURN count(e) > 0 AS exists
```

**Usage in Repository:**
```python
ENTITY_EXISTS = """
MATCH (e:Entity {id: $id, project_name: $project_name})
RETURN count(e) > 0 AS exists
"""
```

**Benefits:**
- Efficient (doesn't fetch properties)
- Returns boolean
- Faster than fetching full entity

---

## Relationship Patterns

### Pattern 6: Create Relationship

**Purpose:** Link two entities

**Query:**
```cypher
MATCH (source:Entity {id: $source_id, project_name: $project_name})
MATCH (target:Entity {id: $target_id, project_name: $project_name})
MERGE (source)-[r:USES]->(target)
SET r.created_at = datetime()
RETURN r
```

**Usage in Repository:**
```python
CREATE_RELATIONSHIP = """
MATCH (source:Entity {id: $source_id, project_name: $project_name})
MATCH (target:Entity {id: $target_id, project_name: $project_name})
MERGE (source)-[r:USES]->(target)
SET r.created_at = datetime()
RETURN r
"""
```

---

### Pattern 7: Get Related Entities

**Purpose:** Fetch entities with specific relationship

**Query:**
```cypher
MATCH (e:Entity {id: $id, project_name: $project_name})-[r:USES]->(related:Entity)
RETURN related, type(r) AS relationship_type
ORDER BY related.name
LIMIT $limit
```

**Usage in Repository:**
```python
GET_RELATED_ENTITIES = """
MATCH (e:Entity {id: $id, project_name: $project_name})-[r:USES]->(related:Entity)
RETURN related, type(r) AS relationship_type
ORDER BY related.name
LIMIT $limit
"""
```

---

### Pattern 8: Delete Relationship

**Purpose:** Remove specific relationship

**Query:**
```cypher
MATCH (source:Entity {id: $source_id})-[r:USES]->(target:Entity {id: $target_id})
WHERE source.project_name = $project_name
DELETE r
RETURN count(r) AS deleted_count
```

**Usage in Repository:**
```python
DELETE_RELATIONSHIP = """
MATCH (source:Entity {id: $source_id})-[r:USES]->(target:Entity {id: $target_id})
WHERE source.project_name = $project_name
DELETE r
RETURN count(r) AS deleted_count
"""
```

---

## Batch Operation Patterns

### Pattern 9: Batch Create/Update

**Purpose:** Process multiple entities in single transaction

**Query:**
```cypher
UNWIND $entities AS entity
MERGE (e:Entity {id: entity.id, project_name: entity.project_name})
SET e += entity.properties
SET e.updated_at = datetime()
RETURN count(e) AS saved_count
```

**Usage in Repository:**
```python
SAVE_ENTITIES_BATCH = """
UNWIND $entities AS entity
MERGE (e:Entity {id: entity.id, project_name: entity.project_name})
SET e += entity.properties
SET e.updated_at = datetime()
RETURN count(e) AS saved_count
"""

# Call with list of dicts
entities = [
    {"id": "1", "project_name": "proj", "properties": {"name": "Entity1"}},
    {"id": "2", "project_name": "proj", "properties": {"name": "Entity2"}},
]
```

---

### Pattern 10: Batch Delete

**Purpose:** Delete multiple entities by IDs

**Query:**
```cypher
MATCH (e:Entity)
WHERE e.id IN $ids AND e.project_name = $project_name
DETACH DELETE e
RETURN count(e) AS deleted_count
```

**Usage in Repository:**
```python
DELETE_ENTITIES_BATCH = """
MATCH (e:Entity)
WHERE e.id IN $ids AND e.project_name = $project_name
DETACH DELETE e
RETURN count(e) AS deleted_count
"""
```

---

## Aggregation Patterns

### Pattern 11: Count Entities

**Purpose:** Get count without fetching data

**Query:**
```cypher
MATCH (e:Entity {project_name: $project_name})
RETURN count(e) AS entity_count
```

**Usage in Repository:**
```python
COUNT_ENTITIES = """
MATCH (e:Entity {project_name: $project_name})
RETURN count(e) AS entity_count
"""
```

---

### Pattern 12: Group and Count

**Purpose:** Count entities by type

**Query:**
```cypher
MATCH (e:Entity {project_name: $project_name})
RETURN e.type AS entity_type,
       count(e) AS count
ORDER BY count DESC
```

**Usage in Repository:**
```python
COUNT_ENTITIES_BY_TYPE = """
MATCH (e:Entity {project_name: $project_name})
RETURN e.type AS entity_type,
       count(e) AS count
ORDER BY count DESC
"""
```

---

### Pattern 13: Get Statistics

**Purpose:** Aggregate metrics for dashboard

**Query:**
```cypher
MATCH (e:Entity {project_name: $project_name})
WITH count(e) AS total_entities,
     collect(DISTINCT e.type) AS entity_types
OPTIONAL MATCH (e2:Entity {project_name: $project_name})-[r]->()
WITH total_entities, entity_types, count(r) AS total_relationships
RETURN total_entities,
       entity_types,
       total_relationships,
       total_relationships * 1.0 / total_entities AS avg_relationships_per_entity
```

---

## Optional Relationship Patterns

### Pattern 14: Fetch with Optional Relationships

**Purpose:** Get entity even if relationships don't exist

**Query:**
```cypher
MATCH (e:Entity {id: $id, project_name: $project_name})
OPTIONAL MATCH (e)-[:USES]->(dependency:Entity)
OPTIONAL MATCH (e)<-[:USES]-(dependent:Entity)
RETURN e,
       collect(DISTINCT dependency) AS dependencies,
       collect(DISTINCT dependent) AS dependents
```

**Usage in Repository:**
```python
GET_ENTITY_WITH_RELATIONSHIPS = """
MATCH (e:Entity {id: $id, project_name: $project_name})
OPTIONAL MATCH (e)-[:USES]->(dependency:Entity)
OPTIONAL MATCH (e)<-[:USES]-(dependent:Entity)
RETURN e,
       collect(DISTINCT dependency) AS dependencies,
       collect(DISTINCT dependent) AS dependents
"""
```

**Benefits:**
- Always returns entity
- Empty collections for missing relationships
- No need for multiple queries

---

## Pagination Patterns

### Pattern 15: Offset-Based Pagination

**Purpose:** Simple pagination for small datasets

**Query:**
```cypher
MATCH (e:Entity {project_name: $project_name})
RETURN e
ORDER BY e.name
SKIP $offset
LIMIT $page_size
```

**Usage in Repository:**
```python
GET_ENTITIES_PAGINATED = """
MATCH (e:Entity {project_name: $project_name})
RETURN e
ORDER BY e.name
SKIP $offset
LIMIT $page_size
"""

# Calculate offset
page = 2
page_size = 20
offset = (page - 1) * page_size
```

**Warning:** Inefficient for large offsets (offset 10000 scans 10000 records)

---

### Pattern 16: Cursor-Based Pagination

**Purpose:** Efficient pagination for large datasets

**Query:**
```cypher
MATCH (e:Entity {project_name: $project_name})
WHERE ($cursor IS NULL OR e.created_at < datetime($cursor))
RETURN e
ORDER BY e.created_at DESC
LIMIT $page_size + 1
```

**Usage in Repository:**
```python
GET_ENTITIES_CURSOR_PAGINATED = """
MATCH (e:Entity {project_name: $project_name})
WHERE ($cursor IS NULL OR e.created_at < datetime($cursor))
RETURN e
ORDER BY e.created_at DESC
LIMIT $page_size + 1
"""

# In repository method
async def get_entities_paginated(
    self, project_name: str, cursor: str | None = None, page_size: int = 20
) -> ServiceResult[dict]:
    result = await self._execute_with_retry(
        query,
        {"project_name": project_name, "cursor": cursor, "page_size": page_size}
    )
    items = result.data
    has_more = len(items) > page_size
    if has_more:
        items = items[:page_size]
    next_cursor = items[-1]["created_at"] if has_more and items else None

    return ServiceResult.ok({
        "items": items,
        "next_cursor": next_cursor,
        "has_more": has_more,
    })
```

---

## Search Patterns

### Pattern 17: Full-Text Search

**Purpose:** Search by text content

**Prerequisite:**
```cypher
CREATE FULLTEXT INDEX entity_name_fulltext IF NOT EXISTS
FOR (e:Entity) ON EACH [e.name, e.description]
```

**Query:**
```cypher
CALL db.index.fulltext.queryNodes('entity_name_fulltext', $search_term)
YIELD node, score
WHERE node.project_name = $project_name
RETURN node AS e, score
ORDER BY score DESC
LIMIT $limit
```

**Usage in Repository:**
```python
SEARCH_ENTITIES_FULLTEXT = """
CALL db.index.fulltext.queryNodes('entity_name_fulltext', $search_term)
YIELD node, score
WHERE node.project_name = $project_name
RETURN node AS e, score
ORDER BY score DESC
LIMIT $limit
"""
```

---

### Pattern 18: Pattern Matching Search

**Purpose:** Search with wildcards

**Query:**
```cypher
MATCH (e:Entity {project_name: $project_name})
WHERE e.name =~ $pattern
RETURN e
ORDER BY e.name
LIMIT $limit
```

**Usage in Repository:**
```python
SEARCH_ENTITIES_PATTERN = """
MATCH (e:Entity {project_name: $project_name})
WHERE e.name =~ $pattern
RETURN e
ORDER BY e.name
LIMIT $limit
"""

# Use case-insensitive pattern
pattern = f"(?i).*{search_term}.*"
```

---

## Graph Traversal Patterns

### Pattern 19: Find Path

**Purpose:** Find relationship path between entities

**Query:**
```cypher
MATCH path = shortestPath(
    (source:Entity {id: $source_id, project_name: $project_name})-[*..5]->
    (target:Entity {id: $target_id, project_name: $project_name})
)
RETURN path,
       length(path) AS path_length,
       [node IN nodes(path) | node.name] AS entity_names
```

**Usage in Repository:**
```python
FIND_PATH_BETWEEN_ENTITIES = """
MATCH path = shortestPath(
    (source:Entity {id: $source_id, project_name: $project_name})-[*..5]->
    (target:Entity {id: $target_id, project_name: $project_name})
)
RETURN path,
       length(path) AS path_length,
       [node IN nodes(path) | node.name] AS entity_names
"""
```

---

### Pattern 20: Variable Depth Traversal

**Purpose:** Find all entities within N hops

**Query:**
```cypher
MATCH (e:Entity {id: $id, project_name: $project_name})-[*1..$max_depth]->(related:Entity)
RETURN DISTINCT related,
       length(shortestPath((e)-[*]->(related))) AS distance
ORDER BY distance, related.name
LIMIT $limit
```

**Usage in Repository:**
```python
GET_RELATED_ENTITIES_WITHIN_DEPTH = """
MATCH (e:Entity {id: $id, project_name: $project_name})-[*1..$max_depth]->(related:Entity)
RETURN DISTINCT related,
       length(shortestPath((e)-[*]->(related))) AS distance
ORDER BY distance, related.name
LIMIT $limit
"""
```

---

## Index Creation Patterns

### Pattern 21: Create Indexes

**Purpose:** Optimize query performance

**Query:**
```cypher
-- Unique constraint (creates index automatically)
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE (e.id, e.project_name) IS UNIQUE

-- Regular index
CREATE INDEX entity_name_idx IF NOT EXISTS
FOR (e:Entity) ON (e.name)

-- Composite index
CREATE INDEX entity_project_type_idx IF NOT EXISTS
FOR (e:Entity) ON (e.project_name, e.type)

-- Full-text index
CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
FOR (e:Entity) ON EACH [e.name, e.description]
```

**Usage in Repository:**
```python
async def create_indexes(self) -> ServiceResult[None]:
    """Create database indexes for entities."""
    indexes = [
        """
        CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
        FOR (e:Entity) REQUIRE (e.id, e.project_name) IS UNIQUE
        """,
        """
        CREATE INDEX entity_name_idx IF NOT EXISTS
        FOR (e:Entity) ON (e.name)
        """,
        """
        CREATE INDEX entity_project_type_idx IF NOT EXISTS
        FOR (e:Entity) ON (e.project_name, e.type)
        """,
    ]

    for index_query in indexes:
        result = await self._execute_with_retry(index_query)
        if result.is_failure:
            logger.warning(f"Failed to create index: {result.error}")

    return ServiceResult.ok(None)
```

---

## Best Practices

### Always Include
1. **project_name filter** - Isolate multi-tenant data
2. **LIMIT clause** - Prevent unbounded queries
3. **ORDER BY** - Ensure consistent results
4. **datetime()** for timestamps - Server-side time
5. **DISTINCT** when collecting - Avoid duplicates

### Avoid
1. **Returning entire nodes** unnecessarily - Use projection
2. **No LIMIT** on unbounded queries - Always limit
3. **Complex WHERE clauses** - Use indexes instead
4. **Cartesian products** - Use MATCH patterns carefully
5. **String concatenation** in queries - Use parameters

### Performance Tips
1. Use `PROFILE` to analyze query performance
2. Create indexes for frequently queried properties
3. Use `EXPLAIN` to see execution plan
4. Batch operations with `UNWIND`
5. Use `MERGE` for idempotent operations
6. Prefer `OPTIONAL MATCH` over multiple queries

---

## Reference

See also:
- [pattern-guide.md](./pattern-guide.md) - Repository implementation patterns
- [examples/examples.md](../examples/examples.md) - Complete working examples
- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/current/
