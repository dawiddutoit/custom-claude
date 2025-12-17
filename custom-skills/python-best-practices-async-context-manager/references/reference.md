# Reference - Implement Async Context Manager

## Python Example Scripts

The following utility scripts demonstrate practical usage patterns:

- [generate_async_context_manager.py](../examples/generate_async_context_manager.py) - Generates async context manager implementations from function signatures using AST parsing
- [convert_sync_to_async_cm.py](../examples/convert_sync_to_async_cm.py) - Converts existing synchronous context managers to async versions
- [validate_context_managers.py](../examples/validate_context_managers.py) - Validates async context manager implementations for correctness and type safety

---

## API Reference

### @asynccontextmanager Decorator

**Module**: `contextlib`

**Signature**:
```python
def asynccontextmanager(func: Callable[..., AsyncIterator[T]]) -> Callable[..., AsyncContextManager[T]]
```

**Purpose**: Transforms an async generator function into an async context manager.

**Requirements**:
- Function must be async (`async def`)
- Function must yield exactly once
- Return type must be `AsyncIterator[T]`
- Cleanup code goes after yield in finally block

---

## Type Hints

### AsyncIterator

**Import**: `from collections.abc import AsyncIterator`

**Usage**:
```python
from collections.abc import AsyncIterator

@asynccontextmanager
async def manager() -> AsyncIterator[ResourceType]:
    yield resource
```

**Why AsyncIterator**:
- `@asynccontextmanager` expects an async generator
- Async generators have return type `AsyncIterator[T]`
- More specific than `AsyncContextManager[T]`
- Proper type checking with mypy/pyright

### Generic Context Managers

```python
from typing import TypeVar
from collections.abc import AsyncIterator

T = TypeVar("T")

@asynccontextmanager
async def generic_manager(factory: Callable[[], T]) -> AsyncIterator[T]:
    """Generic context manager for any resource type."""
    resource = factory()
    try:
        yield resource
    finally:
        if hasattr(resource, 'close'):
            await resource.close()
```

---

## Architecture

### Async Context Manager Protocol

**Python Protocol**:
```python
class AsyncContextManager(Protocol[T]):
    async def __aenter__(self) -> T:
        """Enter the runtime context."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Exit the runtime context."""
        ...
```

**How @asynccontextmanager Works**:
1. Decorator transforms generator into context manager
2. Code before `yield` becomes `__aenter__`
3. Yielded value is returned from `__aenter__`
4. Code in `finally` after `yield` becomes `__aexit__`
5. Exception handling is automatic

**Equivalent Manual Implementation**:
```python
# Using @asynccontextmanager
@asynccontextmanager
async def auto_manager() -> AsyncIterator[Resource]:
    resource = await create_resource()
    try:
        yield resource
    finally:
        await resource.close()

# Equivalent manual implementation
class ManualManager:
    async def __aenter__(self) -> Resource:
        self.resource = await create_resource()
        return self.resource

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.resource.close()
        return None  # Don't suppress exceptions
```

---

## Advanced Configuration

### Context Manager with Parameters

```python
@asynccontextmanager
async def configurable_manager(
    database: str,
    timeout: float = 30.0,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> AsyncIterator[Session]:
    """Context manager with extensive configuration."""
    if not database:
        raise ValueError("Database is required")

    session = None
    try:
        session = await create_session(
            database=database,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        yield session
    finally:
        if session:
            await session.close()
```

### Dependency Injection Pattern

```python
@asynccontextmanager
async def injected_manager(
    settings: Settings,  # Required - injected config
    driver: AsyncDriver,  # Required - injected dependency
    metrics: MetricsCollector | None = None  # Optional - can be None
) -> AsyncIterator[Session]:
    """Context manager with dependency injection."""
    if not settings:
        raise ValueError("Settings is required")
    if not driver:
        raise ValueError("Driver is required")

    session = None
    try:
        if metrics:
            metrics.sessions_created += 1

        session = driver.session(
            database=settings.database_name,
            fetch_size=settings.fetch_size
        )
        yield session
    finally:
        if metrics:
            metrics.sessions_closed += 1
        if session:
            await session.close()
```

---

## Troubleshooting

### Issue 1: RuntimeError: generator didn't stop

**Cause**: Yielding more than once in the async generator.

**Wrong**:
```python
@asynccontextmanager
async def broken_manager():
    yield resource1
    yield resource2  # Error: can only yield once
```

**Fix**: Only yield once:
```python
@asynccontextmanager
async def fixed_manager():
    yield (resource1, resource2)  # Yield tuple
```

---

### Issue 2: AsyncIterator vs AsyncContextManager Type

**Wrong**:
```python
@asynccontextmanager
async def wrong_type() -> AsyncContextManager[Resource]:  # Wrong type
    yield resource
```

**Correct**:
```python
@asynccontextmanager
async def correct_type() -> AsyncIterator[Resource]:  # Correct type
    yield resource
```

**Explanation**: The decorated function IS an async generator (AsyncIterator), the decorator CREATES an AsyncContextManager.

---

### Issue 3: Cleanup Exceptions Hide Original Error

**Problem**: Cleanup failure overwrites original exception.

**Wrong**:
```python
@asynccontextmanager
async def bad_cleanup():
    resource = await create()
    try:
        yield resource
    finally:
        await resource.close()  # If this fails, original error is lost
```

**Fix**: Catch cleanup exceptions:
```python
@asynccontextmanager
async def good_cleanup():
    resource = await create()
    try:
        yield resource
    finally:
        try:
            await resource.close()
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
            # Original exception preserved
```

---

### Issue 4: None Resource in Cleanup

**Problem**: Cleanup tries to close None resource when creation fails.

**Wrong**:
```python
@asynccontextmanager
async def unsafe():
    try:
        resource = await create()  # May fail
        yield resource
    finally:
        await resource.close()  # Crashes if create failed
```

**Fix**: Track resource state:
```python
@asynccontextmanager
async def safe():
    resource = None  # Initialize tracking variable
    try:
        resource = await create()
        yield resource
    finally:
        if resource:  # Only cleanup if created
            await resource.close()
```

---

## Performance Considerations

### Connection Pooling

**Issue**: Creating new connections on each context manager usage is expensive.

**Solution**: Pool connections, use context manager for acquire/release:

```python
class ConnectionPool:
    def __init__(self, max_size: int = 10):
        self._connections: list[Connection] = []
        self._available: asyncio.Queue[Connection] = asyncio.Queue()
        self._max_size = max_size

    @asynccontextmanager
    async def acquire(self, timeout: float = 30.0) -> AsyncIterator[Connection]:
        """Acquire connection from pool, create if needed."""
        conn = None
        try:
            # Try to get existing connection
            conn = await asyncio.wait_for(
                self._available.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            # Create new if pool not full
            if len(self._connections) < self._max_size:
                conn = await create_connection()
                self._connections.append(conn)
            else:
                raise PoolExhaustedError()

        try:
            yield conn
        finally:
            # Return to pool
            await self._available.put(conn)
```

---

### Resource Warming

**Issue**: First usage is slow due to connection/initialization overhead.

**Solution**: Pre-warm resources on application startup:

```python
@asynccontextmanager
async def warmed_pool(config: Config) -> AsyncIterator[Pool]:
    """Pre-warmed connection pool."""
    pool = Pool(config)

    # Warm pool before yielding
    await pool.initialize()
    for _ in range(config.min_connections):
        conn = await pool.create_connection()
        await pool.release(conn)

    try:
        yield pool
    finally:
        await pool.shutdown()
```

---

## Integration Patterns

### With ServiceResult Pattern

```python
from your_project.domain.common.service_result import ServiceResult

@asynccontextmanager
async def result_aware_manager(
    config: Config
) -> AsyncIterator[ServiceResult[Resource]]:
    """Context manager that yields ServiceResult."""
    resource = None
    try:
        resource = await create_resource(config)
        yield ServiceResult.ok(resource)
    except Exception as e:
        yield ServiceResult.fail(str(e), error_type=type(e).__name__)
    finally:
        if resource:
            await resource.close()

# Usage
async with result_aware_manager(config) as result:
    if result.is_success:
        await result.data.operate()
    else:
        logger.error(f"Failed: {result.error}")
```

---

### With Clean Architecture

**Layer Separation**:

```python
# Domain Layer: Abstract interface
class ISessionManager(Protocol):
    @asynccontextmanager
    async def create_session(self) -> AsyncIterator[Session]:
        ...

# Infrastructure Layer: Concrete implementation
class Neo4jSessionManager:
    def __init__(self, driver: AsyncDriver, settings: Settings):
        if not driver or not settings:
            raise ValueError("Driver and settings required")
        self._driver = driver
        self._settings = settings

    @asynccontextmanager
    async def create_session(self) -> AsyncIterator[AsyncSession]:
        """Implementation of session management."""
        session = None
        try:
            session = self._driver.session(
                database=self._settings.neo4j.database_name
            )
            yield session
        finally:
            if session:
                await session.close()

# Application Layer: Uses interface
class CodeSearchService:
    def __init__(self, session_manager: ISessionManager):
        self._session_manager = session_manager

    async def search(self, query: str) -> ServiceResult[list[CodeEntity]]:
        async with self._session_manager.create_session() as session:
            result = await session.run(query)
            return ServiceResult.ok(list(result))
```

---

### With Dependency Injection

```python
from functools import partial

# Factory function for dependency injection
def create_session_manager(
    driver: AsyncDriver,
    settings: Settings
) -> Callable[[], AsyncContextManager[AsyncSession]]:
    """Create session manager factory with injected dependencies."""

    @asynccontextmanager
    async def session_manager() -> AsyncIterator[AsyncSession]:
        session = None
        try:
            session = driver.session(database=settings.neo4j.database_name)
            yield session
        finally:
            if session:
                await session.close()

    return session_manager

# Usage in application
session_factory = create_session_manager(driver, settings)
async with session_factory() as session:
    await session.run("MATCH (n) RETURN n")
```

---

## Testing Strategies

### Mocking Context Managers

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_context_manager_with_mock():
    """Test code that uses async context manager."""

    # Create mock context manager
    mock_session = AsyncMock()
    mock_session.run.return_value = [{"result": "data"}]

    # Mock the context manager itself
    mock_manager = MagicMock()
    mock_manager.__aenter__.return_value = mock_session
    mock_manager.__aexit__.return_value = None

    # Test code that uses context manager
    async with mock_manager as session:
        result = await session.run("query")
        assert result == [{"result": "data"}]

    # Verify cleanup was called
    mock_manager.__aexit__.assert_called_once()
```

### Testing Cleanup Behavior

```python
@pytest.mark.asyncio
async def test_cleanup_on_exception():
    """Verify cleanup happens even when exception raised."""
    cleanup_called = False

    @asynccontextmanager
    async def test_manager() -> AsyncIterator[str]:
        nonlocal cleanup_called
        try:
            yield "resource"
        finally:
            cleanup_called = True

    with pytest.raises(ValueError):
        async with test_manager():
            raise ValueError("Test error")

    assert cleanup_called is True
```

---

## Security Considerations

### 1. Resource Leaks

**Risk**: Resources not properly cleaned up on errors.

**Mitigation**:
- Always use try/finally pattern
- Track resource state (None check)
- Log cleanup failures
- Monitor resource metrics (active count)

### 2. Timeout Protection

**Risk**: Operations hang indefinitely.

**Mitigation**:
```python
@asynccontextmanager
async def timeout_protected(
    timeout: float = 30.0
) -> AsyncIterator[Resource]:
    """Context manager with timeout protection."""
    try:
        resource = await asyncio.wait_for(
            create_resource(),
            timeout=timeout
        )
        yield resource
    except asyncio.TimeoutError:
        raise ServiceTimeoutError(
            operation="create_resource",
            timeout_seconds=timeout
        )
    finally:
        if resource:
            await resource.close()
```

### 3. Concurrency Control

**Risk**: Concurrent access to single-use resources.

**Mitigation**:
```python
import asyncio

class SingletonResource:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._resource = None

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[Resource]:
        """Thread-safe resource access."""
        async with self._lock:
            if not self._resource:
                self._resource = await create_resource()
            yield self._resource
```

---

## Best Practices Summary

### ✅ Do These Things

1. **Always use try/finally** for cleanup guarantee
2. **Track resource state** with `resource = None` pattern
3. **Validate inputs early** before try block
4. **Type hint return** as `AsyncIterator[T]`
5. **Handle cleanup errors** gracefully (log, don't raise)
6. **Document resource lifecycle** in docstring
7. **Make config required** (no optional parameters)
8. **Test cleanup behavior** in unit tests
9. **Monitor resource metrics** (active count, leaks)
10. **Use dependency injection** for testability

### ❌ Avoid These Mistakes

1. **Don't yield multiple times** (only one yield allowed)
2. **Don't raise in finally** (hides original exception)
3. **Don't skip state tracking** (cleanup may fail on None)
4. **Don't use AsyncContextManager type** (use AsyncIterator)
5. **Don't create config defaults** (violates fail-fast)
6. **Don't ignore cleanup failures** (log them)
7. **Don't forget timeout protection** (operations can hang)
8. **Don't skip testing cleanup** (critical behavior)
9. **Don't mix sync/async** (use async all the way)
10. **Don't violate Single Responsibility** (one resource per manager)
