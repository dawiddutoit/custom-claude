# Circular Dependency Resolution Guide

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [detect_circular_deps.py](../examples/detect_circular_deps.py) - Detects circular dependencies in DI container with graph visualization
- [validate_di_patterns.py](../examples/validate_di_patterns.py) - Validates dependency injection patterns throughout codebase
- [generate_provider.py](../examples/generate_provider.py) - Auto-generates provider code for dependency injection

---

## What is a Circular Dependency?

A circular dependency occurs when two or more providers depend on each other, creating a resolution cycle that the container cannot resolve.

**Example:**
```python
# ServiceA depends on ServiceB
service_a = providers.Singleton(ServiceA, service_b=service_b)

# ServiceB depends on ServiceA - CIRCULAR!
service_b = providers.Singleton(ServiceB, service_a=service_a)
```

**Error Message:**
```
Error while resolving dependencies
```

---

## Detection Strategies

### 1. Definition Order Check

If you can't define ServiceA before ServiceB AND can't define ServiceB before ServiceA, you have a circular dependency.

**Test:**
```
Can ServiceA be fully defined without ServiceB existing? NO
Can ServiceB be fully defined without ServiceA existing? NO
→ Circular dependency detected
```

---

### 2. Import Analysis

Look for bidirectional imports between modules:

```bash
# Find potential circular imports
grep -r "from your_project.application import ServiceA" src/
grep -r "from your_project.application import ServiceB" src/
```

If Module A imports B AND Module B imports A, you likely have circular dependency.

---

### 3. Container Resolution Trace

Add logging to container initialization:

```python
# In container_factory.py
import logging
logger = logging.getLogger(__name__)

def initialize_container_and_services(...):
    logger.info("Resolving service_a...")
    _ = container.service_a()  # Triggers dependency resolution
    logger.info("✓ service_a resolved")
```

If resolution hangs or errors, you've found the cycle.

---

## Resolution Strategies

### Strategy 1: Reorder Providers (Simplest)

**When to Use:** One dependency can be made independent.

**Before:**
```python
# service_a needs service_b
service_a = providers.Singleton(ServiceA, service_b=service_b)

# service_b needs service_a - CIRCULAR
service_b = providers.Singleton(ServiceB, service_a=service_a)
```

**After:**
```python
# Make service_b independent (or depend only on shared deps)
service_b = providers.Singleton(ServiceB, settings=settings)

# service_a now defined after service_b
service_a = providers.Singleton(ServiceA, service_b=service_b)
```

**Steps:**
1. Identify which service can be made independent
2. Remove circular dependency from that service
3. Define independent service first
4. Define dependent service second

**Example from Codebase:**
```python
# EntityConstructionService doesn't depend on ExtractorFactory
entity_construction_service = providers.Singleton(
    EntityConstructionService,
)

# ExtractorFactory depends on EntityConstructionService
extractor_factory = providers.Singleton(
    ExtractorFactory,
    entity_construction_service=entity_construction_service,
)
```

---

### Strategy 2: Extract Shared Dependency

**When to Use:** Both services need the same underlying dependency.

**Before:**
```python
# Both services depend on each other
service_a = providers.Singleton(ServiceA, service_b=service_b)
service_b = providers.Singleton(ServiceB, service_a=service_a)
```

**After:**
```python
# Extract what both really need
shared_repository = providers.Singleton(
    SharedRepository,
    driver=neo4j_driver,
    settings=settings,
)

# Both depend on repository, not each other
service_a = providers.Singleton(ServiceA, repository=shared_repository)
service_b = providers.Singleton(ServiceB, repository=shared_repository)
```

**Steps:**
1. Identify what both services actually need
2. Extract shared concern into separate provider
3. Inject shared provider into both services
4. Remove direct dependency between services

**Example Pattern:**
```python
# Both need database access
code_repository = providers.Singleton(
    Neo4jCodeRepository,
    driver=neo4j_driver,
    settings=settings,
)

# Services depend on repository, not each other
indexing_service = providers.Singleton(IndexingService, repository=code_repository)
search_service = providers.Singleton(SearchService, repository=code_repository)
```

---

### Strategy 3: Use Factory Functions with Lazy Evaluation

**When to Use:** Complex initialization, cannot easily reorder.

**Before:**
```python
service_a = providers.Singleton(ServiceA, service_b=service_b)
service_b = providers.Singleton(ServiceB, service_a=service_a)
```

**After:**
```python
def create_service_a(get_service_b):
    """Factory function with lazy service_b access."""
    service_b = get_service_b()  # Evaluated lazily
    return ServiceA(service_b)

service_b = providers.Singleton(ServiceB, settings=settings)

service_a = providers.Singleton(
    create_service_a,
    get_service_b=providers.Factory(lambda: container.service_b()),
)
```

**How It Works:**
- Factory function receives callable, not instance
- `service_b` created first (no dependency on `service_a`)
- `service_a` factory receives lambda that will call `service_b()` when needed
- Lazy evaluation breaks the cycle

**Example from Codebase:**
```python
def create_extractor_registry(python_ext):
    """Factory function breaks potential cycles."""
    registry = ExtractorRegistry()
    registry.register(python_ext)  # Evaluated here, not at provider definition
    return registry

extractor_registry = providers.Singleton(
    create_extractor_registry,
    python_ext=python_extractor,
)
```

---

### Strategy 4: Redesign Service Boundaries

**When to Use:** Circular dependency indicates poor separation of concerns.

**Anti-Pattern:**
```python
class UserService:
    def __init__(self, order_service):
        self.order_service = order_service

    def get_user_orders(self, user_id):
        return self.order_service.get_by_user(user_id)

class OrderService:
    def __init__(self, user_service):
        self.user_service = user_service

    def get_user_for_order(self, order_id):
        order = self.get_order(order_id)
        return self.user_service.get_user(order.user_id)
```

**Correct Design:**
```python
# Extract query coordination into separate handler
class UserOrderRepository:
    def __init__(self, driver):
        self.driver = driver

    def get_user_orders(self, user_id):
        # Query both user and orders together
        pass

class UserService:
    def __init__(self, repository):
        self.repository = repository

class OrderService:
    def __init__(self, repository):
        self.repository = repository

# No circular dependency
user_order_repository = providers.Singleton(UserOrderRepository, driver=driver)
user_service = providers.Singleton(UserService, repository=user_order_repository)
order_service = providers.Singleton(OrderService, repository=user_order_repository)
```

**Principles:**
- Services should not depend on other services at same layer
- Extract coordination into higher-level handler/orchestrator
- Share repositories, not services
- Follow dependency flow: Domain ← Application ← Infrastructure

---

## Real-World Example: GraphRAG Pipeline

**Context:** `GraphRAGPipeline` creates `IndexingOrchestrator` internally to avoid circular dependency with `neo4j_rag`.

**Problem:**
```python
# IndexingOrchestrator needs IndexingModule
indexing_orchestrator = providers.Singleton(
    IndexingOrchestrator,
    indexing_module=???  # Created by neo4j_rag.indexing_module
)

# But neo4j_rag needs to be provided externally
neo4j_rag = providers.Dependency()

# CIRCULAR: Can't get indexing_module without neo4j_rag being initialized
```

**Solution:**
```python
# GraphRAGPipeline creates IndexingOrchestrator internally
graphrag_pipeline = providers.Singleton(
    GraphRAGPipeline,
    driver=neo4j_driver,
    embedder=embedding_service,
    config=settings,
    sync_driver=neo4j_sync_driver,
    code_repository=code_repository,
)

# GraphRAGPipeline.__init__ does:
# self.indexing_module = neo4j_rag.indexing_module
# self.orchestrator = IndexingOrchestrator(self.indexing_module, ...)
```

**Key Insight:** Move complex wiring into service constructor, not container definition.

---

## Common Patterns in your_project

### Pattern 1: Repository First, Services After

```python
# ✅ CORRECT ORDER
# Repositories don't depend on services
code_repository = providers.Singleton(Neo4jCodeRepository, driver=neo4j_driver)
search_repository = providers.Singleton(Neo4jSearchRepository, driver=neo4j_driver)

# Services depend on repositories
entity_service = providers.Singleton(EntityService, repository=code_repository)
search_service = providers.Singleton(SearchService, repository=search_repository)

# Handlers depend on services
search_handler = providers.Factory(SearchCodeHandler, service=search_service)
```

**Rule:** Infrastructure → Application → Interface

---

### Pattern 2: Settings Always Independent

```python
# ✅ Settings never depends on anything
settings = providers.Dependency(instance_of=Settings)

# Everything else can depend on settings
code_repository = providers.Singleton(Neo4jCodeRepository, settings=settings)
chunking_service = providers.Singleton(ChunkingService, settings=settings)
```

**Rule:** Configuration is leaf dependency, never depends on services.

---

### Pattern 3: External Dependencies First

```python
# ✅ External dependencies defined first
settings = providers.Dependency(instance_of=Settings)
neo4j_driver = providers.Dependency(instance_of=AsyncDriver)
repository_monitor = providers.Dependency()

# Then infrastructure using external deps
code_repository = providers.Singleton(Neo4jCodeRepository, driver=neo4j_driver)

# Then application using infrastructure
entity_service = providers.Singleton(EntityService, repository=code_repository)
```

**Rule:** External → Infrastructure → Application → Interface

---

## Debugging Checklist

When encountering circular dependency:

- [ ] Draw dependency graph (ServiceA → ServiceB → ServiceA?)
- [ ] Check definition order in container.py
- [ ] Identify shared dependencies both services need
- [ ] Verify layer boundaries (Infrastructure vs Application)
- [ ] Consider if services should depend on each other at all
- [ ] Look for factory functions that could break cycle
- [ ] Check if redesign needed (poor separation of concerns)
- [ ] Validate against Clean Architecture principles

---

## Prevention Guidelines

### 1. Follow Dependency Rule

**Clean Architecture Dependency Rule:**
```
Domain ← Application ← Infrastructure ← Interface
```

Dependencies only flow inward. Never:
- Domain depending on Application
- Application depending on Infrastructure
- Services at same layer depending on each other

---

### 2. Prefer Composition over Cross-Dependencies

**❌ WRONG:**
```python
class ServiceA:
    def __init__(self, service_b: ServiceB):
        self.service_b = service_b

class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a
```

**✅ CORRECT:**
```python
class ServiceA:
    def __init__(self, repository: Repository):
        self.repository = repository

class ServiceB:
    def __init__(self, repository: Repository):
        self.repository = repository

# Coordination happens in handler
class CoordinatingHandler:
    def __init__(self, service_a: ServiceA, service_b: ServiceB):
        self.service_a = service_a
        self.service_b = service_b
```

---

### 3. Use Handlers for Orchestration

**Anti-Pattern:**
```python
# Services orchestrating other services
class UserService:
    def create_user_with_orders(self, user_data, order_data):
        user = self.create_user(user_data)
        self.order_service.create_orders(user.id, order_data)  # Bad!
```

**Correct Pattern:**
```python
# Handler orchestrates multiple services
class CreateUserWithOrdersHandler:
    def __init__(self, user_service, order_service):
        self.user_service = user_service
        self.order_service = order_service

    async def handle(self, command):
        user = await self.user_service.create_user(command.user_data)
        await self.order_service.create_orders(user.id, command.order_data)
```

---

### 4. Test Dependency Graph

Add test to detect cycles:

```python
def test_no_circular_dependencies():
    """Test that container can be initialized without circular deps."""
    container = Container()

    # Override external dependencies
    container.settings.override(test_settings)
    container.neo4j_driver.override(mock_driver)

    # Try to resolve all services - will fail if circular
    try:
        for provider_name in dir(container):
            if not provider_name.startswith('_'):
                provider = getattr(container, provider_name)
                if callable(provider):
                    _ = provider()  # Force resolution
    except Exception as e:
        pytest.fail(f"Circular dependency detected: {e}")
```

---

## Further Reading

- Clean Architecture principles: ARCHITECTURE.md
- Container definition: `src/your_project/interfaces/mcp/container.py`
- Layer boundaries: `.claude/skills/validate-layer-boundaries/SKILL.md`
- Dependency injection reference: `provider-reference.md`
