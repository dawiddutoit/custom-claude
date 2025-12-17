# Reference - Validate Fail-Fast Imports

## Complete Anti-Pattern Reference

This document provides detailed technical documentation for fail-fast import validation.

---

## Detection Patterns

### Pattern 1: try/except ImportError

**Detection Regex**: `try:\s+import\s+\w+.*?except\s+ImportError:`

**Examples**:

```python
# ❌ VIOLATION 1a: Optional import with flag
try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

# ❌ VIOLATION 1b: Optional import with None fallback
try:
    import optional_module
except ImportError:
    optional_module = None

# ❌ VIOLATION 1c: Import with error suppression
try:
    from external_lib import feature
except ImportError:
    pass  # Silently fail
```

**Impact**: HIGH - Missing dependencies not detected until runtime

**Fix**: Import at top, fail fast. Add to requirements.txt.

---

### Pattern 2: Conditional Imports

**Detection Regex**: `if\s+.*?:\s*(import|from\s+\w+\s+import)`

**Examples**:

```python
# ❌ VIOLATION 2a: Config-based import
if USE_NEO4J:
    from neo4j import AsyncGraphDatabase
else:
    from sqlite3 import Connection as AsyncGraphDatabase

# ❌ VIOLATION 2b: Platform-specific import
if sys.platform == "linux":
    import linux_specific
else:
    import generic_fallback

# ❌ VIOLATION 2c: Feature flag import
if ENABLE_FEATURE_X:
    from features import feature_x
```

**Impact**: HIGH - Runtime import failures, inconsistent behavior

**Fix**: Import all at top, use config at usage site.

---

### Pattern 3: Lazy Imports (Function-Level)

**Detection Pattern**: Indented `import` statements inside `def` or `class` blocks

**Examples**:

```python
# ❌ VIOLATION 3a: Import inside function
def search_code(query: str):
    from application.services import SearchService  # Lazy
    return SearchService().search(query)

# ❌ VIOLATION 3b: Import inside method
class Handler:
    def handle(self):
        from domain.models import Entity  # Lazy
        return Entity()

# ❌ VIOLATION 3c: Import in loop
for file in files:
    from parsers import get_parser  # Repeatedly importing
    parser = get_parser(file)
```

**Impact**: MEDIUM - ImportError mid-execution, performance overhead

**Fix**: Move imports to module top level.

---

### Pattern 4: Import with Fallback

**Detection Regex**: `try:.*?import.*?except\s+ImportError:.*?import`

**Examples**:

```python
# ❌ VIOLATION 4a: Performance fallback
try:
    from fast_library import fast_function
except ImportError:
    from slow_library import slow_function as fast_function

# ❌ VIOLATION 4b: Version fallback
try:
    from new_module import new_api
except ImportError:
    from old_module import old_api as new_api

# ❌ VIOLATION 4c: Optional optimization
try:
    from native_extension import optimized
except ImportError:
    from pure_python import unoptimized as optimized
```

**Impact**: HIGH - Silent performance degradation, unclear dependencies

**Fix**: Pick one library, make required, document in requirements.txt.

---

### Pattern 5: Optional Dependencies Flag

**Detection Regex**: `\w+_AVAILABLE\s*=\s*(True|False)`

**Examples**:

```python
# ❌ VIOLATION 5a: Availability flag
try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

# Later in code
if TREE_SITTER_AVAILABLE:
    use_tree_sitter()
else:
    use_fallback()
```

**Impact**: HIGH - Feature availability varies by environment, exponential test matrix

**Fix**: Make dependencies required, remove optional behavior.

---

### Pattern 6: Circular Import Workaround

**Detection Pattern**: Imports inside functions with comment about circular imports

**Examples**:

```python
# ❌ VIOLATION 6a: Delayed import for circular dependency
def get_repository():
    # Import here to avoid circular dependency
    from infrastructure.repositories import CodeRepository
    return CodeRepository()

# ❌ VIOLATION 6b: TYPE_CHECKING imports (acceptable exception)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models import Entity  # Only for type hints
```

**Impact**: MEDIUM - Circular dependencies indicate design problem

**Fix**: Use dependency inversion (interfaces) or TYPE_CHECKING for type hints only.

---

## Acceptable Exceptions

### Exception 1: TYPE_CHECKING Imports

**✅ ALLOWED**:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models import Entity  # For type hints only
```

**Rationale**: Type hints are static, not runtime. This doesn't hide missing deps.

---

### Exception 2: Platform-Specific Standard Library

**✅ ALLOWED (with caution)**:

```python
import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
```

**Rationale**: Python version compatibility is explicit and predictable.

---

## Import Best Practices

### Standard Import Organization

```python
"""Module docstring"""

# 1. Standard library imports
import os
import sys
from typing import Optional

# 2. Third-party imports
from neo4j import AsyncGraphDatabase
from pydantic import BaseModel

# 3. Local application imports
from project_watch_mcp.domain.models import Entity
from project_watch_mcp.application.services import SearchService

# 4. Conditional imports (only TYPE_CHECKING)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.repositories import CodeRepository  # Type hints only
```

---

### Fail-Fast Import Rules

#### Rule 1: All Imports at Top

**✅ CORRECT**:
```python
from application.services import SearchService

def search_code(query: str):
    return SearchService().search(query)
```

**❌ WRONG**:
```python
def search_code(query: str):
    from application.services import SearchService  # Inside function
    return SearchService().search(query)
```

---

#### Rule 2: No Try/Except for Imports

**✅ CORRECT**:
```python
import tree_sitter  # Fail if missing
```

**❌ WRONG**:
```python
try:
    import tree_sitter
    AVAILABLE = True
except ImportError:
    AVAILABLE = False
```

---

#### Rule 3: No Conditional Imports

**✅ CORRECT**:
```python
from neo4j import AsyncGraphDatabase
from sqlite3 import Connection

# Config controls usage, not imports
if config.use_neo4j:
    db = AsyncGraphDatabase(...)
else:
    db = Connection(...)
```

**❌ WRONG**:
```python
if config.use_neo4j:
    from neo4j import AsyncGraphDatabase  # Conditional import
else:
    from sqlite3 import Connection as AsyncGraphDatabase
```

---

#### Rule 4: No Import Fallbacks

**✅ CORRECT**:
```python
from fast_library import fast_function
# Document: requires fast_library in requirements.txt
```

**❌ WRONG**:
```python
try:
    from fast_library import fast_function
except ImportError:
    from slow_library import slow_function as fast_function
```

---

## Circular Import Resolution

### Problem: Circular Dependencies

```python
# ❌ WRONG: Circular dependency
# module_a.py
from module_b import ClassB

class ClassA:
    def use_b(self):
        return ClassB()

# module_b.py
from module_a import ClassA  # Circular!

class ClassB:
    def use_a(self):
        return ClassA()
```

---

### Solution 1: Dependency Inversion

```python
# ✅ CORRECT: Use interfaces (Clean Architecture)

# domain/repositories.py (abstract)
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def save(self, entity): ...

# infrastructure/neo4j_repository.py
from domain.repositories import Repository

class Neo4jRepository(Repository):
    def save(self, entity):
        ...

# No circular dependency!
```

---

### Solution 2: TYPE_CHECKING

```python
# ✅ CORRECT: Use TYPE_CHECKING for type hints only

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from module_b import ClassB  # Only for type checker

class ClassA:
    def use_b(self) -> "ClassB":  # String literal for forward ref
        from module_b import ClassB  # Runtime import
        return ClassB()
```

**Note**: This is acceptable as a last resort, but better to fix architecture.

---

## Common Fixes

### Fix 1: try/except ImportError → Required Import

**Before (Violation)**:
```python
# src/services/parser.py
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Language = None
    Parser = None

class CodeParser:
    def parse(self, code: str):
        if TREE_SITTER_AVAILABLE:
            parser = Parser()
            return parser.parse(code)
        else:
            return self._basic_parse(code)
```

**After (Fixed)**:
```python
# src/services/parser.py
from tree_sitter import Language, Parser

class CodeParser:
    def parse(self, code: str):
        parser = Parser()
        return parser.parse(code)
```

**Steps**:
1. Remove try/except block
2. Remove `_AVAILABLE` flag
3. Remove fallback logic
4. Add to `pyproject.toml`: `tree-sitter>=0.20.0`
5. Run `uv pip install -e .`

---

### Fix 2: Conditional Import → Import All, Use Config

**Before (Violation)**:
```python
# src/config/database.py
import os

USE_NEO4J = os.getenv("USE_NEO4J", "true").lower() == "true"

if USE_NEO4J:
    from neo4j import AsyncGraphDatabase
    DatabaseDriver = AsyncGraphDatabase
else:
    from sqlite3 import Connection
    DatabaseDriver = Connection

class DatabaseService:
    def __init__(self):
        self.driver = DatabaseDriver(...)
```

**After (Fixed)**:
```python
# src/config/database.py
import os
from neo4j import AsyncGraphDatabase
from sqlite3 import Connection

USE_NEO4J = os.getenv("USE_NEO4J", "true").lower() == "true"

class DatabaseService:
    def __init__(self):
        if USE_NEO4J:
            self.driver = AsyncGraphDatabase(...)
        else:
            self.driver = Connection(...)
```

**Steps**:
1. Import both libraries at top
2. Move conditional logic to usage site
3. Ensure both libraries in dependencies
4. Test both code paths

---

### Fix 3: Lazy Import → Top-Level Import

**Before (Violation)**:
```python
# src/handlers/search_handler.py
from typing import Any

class SearchHandler:
    def handle(self, query: str) -> Any:
        # Lazy import to avoid circular dependency
        from application.services import SearchService

        service = SearchService()
        return service.search(query)
```

**After (Fixed) - Option A: Move import to top**:
```python
# src/handlers/search_handler.py
from typing import Any
from application.services import SearchService

class SearchHandler:
    def handle(self, query: str) -> Any:
        service = SearchService()
        return service.search(query)
```

**After (Fixed) - Option B: Use dependency injection (best)**:
```python
# src/handlers/search_handler.py
from typing import Any
from application.services import SearchService

class SearchHandler:
    def __init__(self, search_service: SearchService):
        self.search_service = search_service

    def handle(self, query: str) -> Any:
        return self.search_service.search(query)
```

---

### Fix 4: Import Fallback → Pick One Library

**Before (Violation)**:
```python
# src/utils/json_loader.py
try:
    import orjson as json  # Fast JSON library
    USE_ORJSON = True
except ImportError:
    import json  # Standard library fallback
    USE_ORJSON = False

def load_json(data: str):
    if USE_ORJSON:
        return json.loads(data)
    else:
        return json.loads(data)  # Same API, different performance
```

**After (Fixed)**:
```python
# src/utils/json_loader.py
import orjson as json  # Required

def load_json(data: str):
    return json.loads(data)
```

**Steps**:
1. Pick the better library (usually faster)
2. Remove try/except and fallback
3. Add to dependencies: `orjson>=3.9.0`
4. Document performance requirements

---

### Fix 5: Optional Dependency Flag → Make Required

**Before (Violation)**:
```python
# src/embedding/service.py
INFINITY_AVAILABLE = False

try:
    from infinity_emb import AsyncEmbeddingEngine
    INFINITY_AVAILABLE = True
except ImportError:
    AsyncEmbeddingEngine = None

class EmbeddingService:
    def __init__(self):
        if not INFINITY_AVAILABLE:
            raise RuntimeError("Infinity embedding not available")
        self.engine = AsyncEmbeddingEngine()
```

**After (Fixed)**:
```python
# src/embedding/service.py
from infinity_emb import AsyncEmbeddingEngine

class EmbeddingService:
    def __init__(self):
        self.engine = AsyncEmbeddingEngine()
```

---

### Fix 6: Circular Import → Dependency Inversion

**Before (Violation)**:
```python
# domain/models/entity.py
from dataclasses import dataclass

@dataclass
class Entity:
    name: str

    def save(self):
        # Import here to avoid circular dependency
        from infrastructure.repositories import EntityRepository
        repo = EntityRepository()
        repo.save(self)
```

**After (Fixed)**:

Step 1 - Create interface in domain:
```python
# domain/repositories/entity_repository.py
from abc import ABC, abstractmethod
from domain.models import Entity

class EntityRepository(ABC):
    @abstractmethod
    def save(self, entity: Entity):
        pass
```

Step 2 - Domain model doesn't know about persistence:
```python
# domain/models/entity.py
from dataclasses import dataclass

@dataclass
class Entity:
    name: str
    # No save() method - that's not domain logic
```

Step 3 - Infrastructure implements interface:
```python
# infrastructure/repositories/neo4j_entity_repository.py
from domain.repositories import EntityRepository
from domain.models import Entity

class Neo4jEntityRepository(EntityRepository):
    def save(self, entity: Entity):
        # Save to Neo4j
        pass
```

Step 4 - Application layer orchestrates:
```python
# application/services/entity_service.py
from domain.models import Entity
from domain.repositories import EntityRepository

class EntityService:
    def __init__(self, repository: EntityRepository):
        self.repository = repository

    def save_entity(self, name: str):
        entity = Entity(name=name)
        self.repository.save(entity)
```

---

## Testing Implications

### With Fail-Fast Imports

**Benefits**:
```python
# test_search.py
from application.services import SearchService

def test_search():
    # Easy to mock, clear dependencies
    service = SearchService(mock_repository)
    result = service.search("query")
    assert result.success
```

**Advantages**:
- Clear what needs to be mocked
- Imports fail early in test collection if dependencies missing
- No conditional logic to test multiple import paths

---

### Without Fail-Fast (Anti-Pattern)

**Problems**:
```python
# With optional imports
try:
    import optional_dep
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

def test_with_optional():
    if not AVAILABLE:
        pytest.skip("optional_dep not available")
    # Test with optional_dep

def test_without_optional():
    if AVAILABLE:
        pytest.skip("Testing fallback, but optional_dep is available")
    # Test fallback
```

**Issues**:
- Must test both paths
- Can't easily control which path is taken
- Inconsistent test results across environments

---

## Performance Considerations

### Import Cost Reality

**Myth**: "Lazy imports are faster"

**Reality**:
- Module imports are cached after first import
- Import time is negligible compared to runtime
- Top-level imports make dependencies explicit

**Measurement**:
```python
import timeit

# Top-level import (one-time cost)
setup_top = "from application.services import SearchService"
time_top = timeit.timeit("SearchService", setup=setup_top, number=10000)
# Result: ~0.0001s (cached)

# Lazy import (repeated cost)
time_lazy = timeit.timeit(
    "from application.services import SearchService; SearchService()",
    number=10000
)
# Result: ~0.01s (10x slower!)
```

---

## Detection Commands

Use these Grep commands to find violations:

```bash
# Find all try/except ImportError patterns
grep -rn "except ImportError:" src/

# Find optional dependency flags
grep -rn "_AVAILABLE = False" src/

# Find conditional imports (excluding TYPE_CHECKING)
grep -rn "if.*import" src/ | grep -v "TYPE_CHECKING"

# Find lazy imports (indented imports - requires manual review)
grep -rn "^    import\|^    from.*import" src/
```

---

## Summary: Import Validation Checklist

When reviewing code for fail-fast imports, verify:

- [ ] All imports at module top level
- [ ] No try/except ImportError patterns
- [ ] No conditional imports (except TYPE_CHECKING)
- [ ] No lazy imports inside functions
- [ ] No `_AVAILABLE` flags
- [ ] Dependencies listed in pyproject.toml
- [ ] Import order: stdlib → third-party → local
- [ ] TYPE_CHECKING used only for type hints
- [ ] No circular import workarounds (fix architecture instead)

---

## Quick Reference Table

| Situation | Correct Approach |
|-----------|------------------|
| Need a library | Import at top, add to requirements |
| Library might be missing | Make it required, fail fast |
| Circular dependency | Use dependency inversion (interfaces) |
| Type hint only | Use TYPE_CHECKING |
| Platform-specific | Document and make explicit |
| Performance concern | Profile first, imports are fast |
| Optional feature | Remove, make required, or plugin architecture |

---

**Last Updated**: 2025-10-17
**Related**: [SKILL.md](./SKILL.md) - Main skill documentation
