# Provider Reference - dependency-injector Library

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [generate_provider.py](../examples/generate_provider.py) - Auto-generates provider code for dependency injection
- [detect_circular_deps.py](../examples/detect_circular_deps.py) - Detects circular dependencies in DI container with graph visualization
- [validate_di_patterns.py](../examples/validate_di_patterns.py) - Validates dependency injection patterns throughout codebase

---

## Overview

The `dependency-injector` library provides declarative dependency injection for Python. This reference covers the provider types, patterns, and API used in your_project.

## Provider Types

### 1. Singleton Provider

**Purpose:** Creates a single instance shared across all requests.

**Syntax:**
```python
my_service = providers.Singleton(
    ServiceClass,
    dependency1=some_provider,
    dependency2=another_provider,
)
```

**Lifecycle:**
- Instance created on first access
- Same instance returned for all subsequent calls
- Persists for container lifetime

**When to Use:**
- Stateful services (caches, registries)
- Expensive initialization (database connections, ML models)
- Shared resources (connection pools)
- Application/Infrastructure services

**Example:**
```python
embedding_service = providers.Singleton(
    create_embedding_service,
    settings=settings,
)
```

**Behavior:**
```python
service1 = container.embedding_service()
service2 = container.embedding_service()
assert service1 is service2  # True - same instance
```

---

### 2. Factory Provider

**Purpose:** Creates a new instance on each invocation.

**Syntax:**
```python
my_handler = providers.Factory(
    HandlerClass,
    dependency1=some_provider,
    dependency2=another_provider,
)
```

**Lifecycle:**
- New instance created on every call
- No state sharing between invocations
- Instance discarded after use

**When to Use:**
- Stateless operations
- Request handlers (Command/Query handlers)
- Short-lived objects
- Concurrent request handling

**Example:**
```python
search_code_handler = providers.Factory(
    SearchCodeHandler,
    search_repository=search_repository,
    embedding_service=embedding_service,
)
```

**Behavior:**
```python
handler1 = container.search_code_handler()
handler2 = container.search_code_handler()
assert handler1 is not handler2  # True - different instances
```

---

### 3. Dependency Provider

**Purpose:** Declares external dependency that must be provided at runtime.

**Syntax:**
```python
settings = providers.Dependency(instance_of=Settings)
neo4j_driver = providers.Dependency(instance_of=AsyncDriver)
```

**Lifecycle:**
- No instance created by container
- Must be overridden before use
- Raises error if accessed without override

**When to Use:**
- Configuration objects
- External connections (drivers, clients)
- Services from outside container
- Runtime-provided dependencies

**Example:**
```python
class Container(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)
    neo4j_driver = providers.Dependency(instance_of=AsyncDriver)

# Later, at runtime:
container.settings.override(actual_settings)
container.neo4j_driver.override(actual_driver)
```

**Behavior:**
```python
# Before override
try:
    settings = container.settings()  # Raises error
except Exception as e:
    print("Dependency not set")

# After override
container.settings.override(actual_settings)
settings = container.settings()  # Returns actual_settings
```

---

## Advanced Patterns

### Factory Functions

**Purpose:** Complex initialization that cannot be done in `__init__`.

**Pattern:**
```python
def create_complex_service(dep1, dep2, settings):
    """Factory function for complex initialization."""
    service = ComplexService(dep1, dep2)

    # Post-construction configuration
    if settings.feature_x_enabled:
        service.register_plugin(PluginX())

    return service

complex_service = providers.Singleton(
    create_complex_service,
    dep1=dependency1,
    dep2=dependency2,
    settings=settings,
)
```

**Use Cases:**
- Conditional configuration
- Multiple registration steps
- Post-construction setup
- Complex initialization logic

---

### Lambda Extractors

**Purpose:** Extract specific configuration values from Settings.

**Pattern:**
```python
service = providers.Singleton(
    Service,
    max_retries=providers.Factory(
        lambda s: s.retry.max_attempts,
        s=settings,
    ),
    timeout_ms=providers.Factory(
        lambda s: s.timeout.milliseconds,
        s=settings,
    ),
    settings=settings,
)
```

**Benefits:**
- Makes dependencies explicit
- Easier to test (inject specific values)
- Documents what config service uses
- Enables configuration evolution

---

### Override Pattern

**Purpose:** Replace dependencies for testing or runtime configuration.

**Pattern:**
```python
# Define in container
class Container(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)

# Override at runtime
def initialize_container(actual_settings):
    container = Container()
    container.settings.override(actual_settings)
    return container

# Override in tests
@pytest.fixture
def container(test_settings):
    container = Container()
    container.settings.override(test_settings)
    return container
```

**Common Overrides:**
- `settings` - Application configuration
- `neo4j_driver` - Database connection
- `repository_monitor` - Monitoring service
- `neo4j_rag` - RAG service instance

---

## Dependency Resolution

### Resolution Order

Container resolves dependencies in definition order:

```python
# ✅ CORRECT - dependencies before dependents
dependency1 = providers.Singleton(Dependency1, settings=settings)
service = providers.Singleton(Service, dep=dependency1)

# ❌ WRONG - service defined before dependency
service = providers.Singleton(Service, dep=dependency1)  # Error!
dependency1 = providers.Singleton(Dependency1, settings=settings)
```

**Rule:** Define all dependencies before services that use them.

---

### Lazy Evaluation

Providers are lazily evaluated:

```python
# Provider defined
my_service = providers.Singleton(MyService, settings=settings)

# Instance NOT created yet

# Instance created on first access
instance = container.my_service()
```

**Benefits:**
- Faster container initialization
- Only create what's needed
- Circular dependency prevention

---

### Wiring

Container automatically wires dependencies:

```python
class Service:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.settings = settings

# Container automatically passes dependencies
service = providers.Singleton(
    Service,
    repository=repository_provider,
    settings=settings_provider,
)

# Usage - no manual wiring needed
instance = container.service()  # Dependencies injected automatically
```

---

## Type Safety

### Type Annotations

Use `instance_of` for type checking:

```python
# ✅ CORRECT - type-safe
settings = providers.Dependency(instance_of=Settings)

# ❌ WRONG - no type checking
settings = providers.Dependency()
```

**Benefits:**
- Runtime type validation
- IDE autocomplete support
- Clearer dependency contracts
- Early error detection

---

### Pyright Integration

Container definitions work with Pyright:

```python
class Container(containers.DeclarativeContainer):
    settings: providers.Dependency[Settings]
    my_service: providers.Singleton[MyService]

# Type-safe access
container = Container()
service: MyService = container.my_service()  # Type correctly inferred
```

---

## Common Patterns in your_project

### Pattern 1: Repository with Driver and Settings

```python
code_repository = providers.Singleton(
    Neo4jCodeRepository,
    driver=neo4j_driver,
    settings=settings,
)
```

**Why:** Repositories need database connection and configuration.

---

### Pattern 2: Service with Repository Dependency

```python
search_service = providers.Singleton(
    SearchService,
    repository=search_repository,
    settings=settings,
)
```

**Why:** Services coordinate business logic using repositories.

---

### Pattern 3: Handler with Multiple Services

```python
search_handler = providers.Factory(
    SearchCodeHandler,
    search_repository=search_repository,
    embedding_service=embedding_service,
    settings=settings,
    graphrag_pipeline=graphrag_pipeline,
)
```

**Why:** Handlers orchestrate multiple services per request.

---

### Pattern 4: Registry with Factory Function

```python
def create_extractor_registry(python_ext):
    registry = ExtractorRegistry()
    registry.register(python_ext)
    return registry

extractor_registry = providers.Singleton(
    create_extractor_registry,
    python_ext=python_extractor,
)
```

**Why:** Registry needs post-construction configuration.

---

## Error Handling

### Error: Dependency Not Set

```python
Error: Dependency 'settings' is not defined
```

**Cause:** Dependency provider not overridden before use.

**Solution:**
```python
container.settings.override(actual_settings)
```

---

### Error: Circular Dependency

```python
Error while resolving dependencies
```

**Cause:** Two providers depend on each other.

**Solutions:**
1. Reorder providers (dependencies first)
2. Extract shared dependency
3. Use factory function with lazy evaluation

See `circular-dependency-guide.md` for detailed strategies.

---

### Error: Provider Not Found

```python
AttributeError: 'Container' object has no attribute 'my_service'
```

**Cause:** Provider not defined in Container class.

**Solution:** Add provider to Container.

---

## Testing Patterns

### Pattern 1: Override External Dependencies

```python
@pytest.fixture
def container(real_settings):
    container = Container()
    container.settings.override(real_settings)
    container.neo4j_driver.override(AsyncMock())
    return container
```

---

### Pattern 2: Verify Dependency Injection

```python
def test_service_receives_dependencies(container):
    service = container.my_service()
    assert service.settings is not None
    assert service.repository is not None
```

---

### Pattern 3: Test Singleton Behavior

```python
def test_singleton_behavior(container):
    instance1 = container.my_service()
    instance2 = container.my_service()
    assert instance1 is instance2
```

---

### Pattern 4: Test Factory Behavior

```python
def test_factory_behavior(container):
    instance1 = container.my_handler()
    instance2 = container.my_handler()
    assert instance1 is not instance2
```

---

## API Reference

### Container Class

```python
class Container(containers.DeclarativeContainer):
    """Base container class."""
    pass
```

**Methods:**
- `provider_name()` - Access provider (creates instance if needed)
- `provider_name.override(value)` - Override provider with specific value
- `provider_name.reset_override()` - Remove override

---

### Singleton Provider

```python
providers.Singleton(
    provides,           # Class or callable
    *args,              # Positional dependencies
    **kwargs,           # Keyword dependencies
)
```

---

### Factory Provider

```python
providers.Factory(
    provides,           # Class or callable
    *args,              # Positional dependencies
    **kwargs,           # Keyword dependencies
)
```

---

### Dependency Provider

```python
providers.Dependency(
    instance_of=None,   # Type constraint (optional)
)
```

---

## Best Practices

1. **Use Singleton for services, Factory for handlers**
2. **Define dependencies before dependents**
3. **Always use `instance_of` for type safety**
4. **Validate dependencies in `__init__`**
5. **Never make Settings/Config optional**
6. **Override Dependency providers in tests**
7. **Use factory functions for complex initialization**
8. **Extract config values with lambda when needed**
9. **Order providers by layer (Infrastructure → Application → Interface)**
10. **Keep container definition declarative (avoid imperative logic)**

---

## Further Reading

- Official docs: https://python-dependency-injector.ets-labs.org/
- Project container: `src/your_project/interfaces/mcp/container.py`
- Project factory: `src/your_project/interfaces/mcp/container_factory.py`
- Test examples: `tests/integration/container/test_settings_injection.py`
