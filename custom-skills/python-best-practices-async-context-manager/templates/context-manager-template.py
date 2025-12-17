#!/usr/bin/env python3
"""
Template: Async Context Manager

Usage:
    1. Copy this template
    2. Replace {{PLACEHOLDERS}} with actual values
    3. Implement resource creation and cleanup logic
    4. Add tests for cleanup behavior

Example:
    @asynccontextmanager
    async def database_session(config: Config) -> AsyncIterator[Session]:
        # Replace create_resource() with actual session creation
        # Replace resource.close() with actual cleanup
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import TypeVar

# Import your resource types
# from project.domain import {{RESOURCE_TYPE}}
# from project.config import {{CONFIG_TYPE}}

T = TypeVar("T")

# ==============================================================================
# BASIC TEMPLATE - Simple Resource Management
# ==============================================================================


@asynccontextmanager
async def {{MANAGER_NAME}}(
    config: {{CONFIG_TYPE}},  # Replace with actual config type
) -> AsyncIterator[{{RESOURCE_TYPE}}]:  # Replace with actual resource type
    """{{DESCRIPTION}} with automatic cleanup.

    Args:
        config: Configuration for {{RESOURCE_TYPE}} creation (required)

    Yields:
        {{RESOURCE_TYPE}}: Active resource instance

    Raises:
        ValueError: If config is None
        {{RESOURCE_ERROR}}: If resource creation fails

    Example:
        async with {{MANAGER_NAME}}(config) as resource:
            await resource.{{OPERATION}}()
    """
    # Fail-fast validation
    if not config:
        raise ValueError("Config is required")

    # Initialize state tracking
    resource = None

    try:
        # Setup phase - create and initialize resource
        resource = await create_{{RESOURCE_NAME}}(config)
        await resource.initialize()

        # Yield resource to caller
        yield resource

    finally:
        # Cleanup phase - always runs
        if resource:
            try:
                await resource.close()
            except Exception as e:
                # Log cleanup failures but don't raise
                logger.warning(f"Cleanup failed: {e}")


# ==============================================================================
# ADVANCED TEMPLATE - With Statistics and Error Handling
# ==============================================================================


@asynccontextmanager
async def {{MANAGER_NAME}}_with_stats(
    config: {{CONFIG_TYPE}},
    stats: {{STATS_TYPE}} | None = None,
) -> AsyncIterator[{{RESOURCE_TYPE}}]:
    """{{DESCRIPTION}} with statistics tracking.

    Args:
        config: Configuration for resource creation (required)
        stats: Optional statistics collector

    Yields:
        {{RESOURCE_TYPE}}: Active resource instance

    Raises:
        ValueError: If config is None
        {{RESOURCE_ERROR}}: If resource creation fails
    """
    if not config:
        raise ValueError("Config is required")

    resource = None

    try:
        # Track resource creation
        if stats:
            stats.active_count += 1
            stats.total_created += 1

        # Create resource
        resource = await create_{{RESOURCE_NAME}}(config)

        yield resource

    except Exception as e:
        # Track errors
        if stats:
            stats.error_count += 1
        logger.error(f"Resource operation failed: {e}")
        raise

    finally:
        # Update statistics
        if stats:
            stats.active_count -= 1

        # Cleanup resource
        if resource:
            try:
                await resource.close()
            except Exception as cleanup_error:
                if stats:
                    stats.cleanup_errors += 1
                logger.warning(f"Cleanup failed: {cleanup_error}")


# ==============================================================================
# POOLED TEMPLATE - Connection/Resource Pool
# ==============================================================================


@asynccontextmanager
async def {{POOL_NAME}}(
    pool: {{POOL_TYPE}},
    timeout: float = 30.0,
) -> AsyncIterator[{{RESOURCE_TYPE}}]:
    """Acquire {{RESOURCE_TYPE}} from pool with automatic release.

    Args:
        pool: Resource pool to acquire from (required)
        timeout: Maximum time to wait for resource (default: 30.0)

    Yields:
        {{RESOURCE_TYPE}}: Resource from pool

    Raises:
        ValueError: If pool is None
        TimeoutError: If resource acquisition times out
        PoolExhaustedError: If pool is full
    """
    if not pool:
        raise ValueError("Pool is required")

    resource = None

    try:
        # Acquire from pool with timeout
        resource = await pool.acquire(timeout=timeout)

        yield resource

    finally:
        # Always return to pool
        if resource:
            await pool.release(resource)


# ==============================================================================
# TRANSACTION TEMPLATE - Database Transactions
# ==============================================================================


@asynccontextmanager
async def {{TRANSACTION_NAME}}(
    session: {{SESSION_TYPE}},
    database: str | None = None,
) -> AsyncIterator[{{TRANSACTION_TYPE}}]:
    """Database transaction with automatic commit/rollback.

    Args:
        session: Active database session (required)
        database: Optional database name

    Yields:
        {{TRANSACTION_TYPE}}: Active transaction

    Raises:
        ValueError: If session is None

    Example:
        async with {{TRANSACTION_NAME}}(session) as tx:
            await tx.run("CREATE (n:Node)")
            # Commits automatically on success
            # Rolls back automatically on exception
    """
    if not session:
        raise ValueError("Session is required")

    tx = await session.begin_transaction()

    try:
        yield tx
        # Commit on successful completion
        await tx.commit()

    except Exception:
        # Rollback on any error
        await tx.rollback()
        raise


# ==============================================================================
# NESTED TEMPLATE - Multiple Dependent Resources
# ==============================================================================


@asynccontextmanager
async def {{NESTED_MANAGER_NAME}}(
    config: {{CONFIG_TYPE}},
) -> AsyncIterator[tuple[{{RESOURCE_TYPE_1}}, {{RESOURCE_TYPE_2}}]]:
    """Manage multiple dependent resources.

    Args:
        config: Configuration for resource creation (required)

    Yields:
        tuple: ({{RESOURCE_TYPE_1}}, {{RESOURCE_TYPE_2}})

    Example:
        async with {{NESTED_MANAGER_NAME}}(config) as (res1, res2):
            await res1.operation()
            await res2.operation()
    """
    if not config:
        raise ValueError("Config is required")

    # Use nested context managers
    async with {{MANAGER_1}}(config) as resource1:
        async with {{MANAGER_2}}(config, resource1) as resource2:
            yield resource1, resource2


# ==============================================================================
# RETRY TEMPLATE - Automatic Retry on Transient Failures
# ==============================================================================


@asynccontextmanager
async def {{RETRY_MANAGER_NAME}}(
    config: {{CONFIG_TYPE}},
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> AsyncIterator[{{RESOURCE_TYPE}}]:
    """Resource manager with automatic retry on transient failures.

    Args:
        config: Configuration for resource creation (required)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Base delay between retries in seconds (default: 1.0)

    Yields:
        {{RESOURCE_TYPE}}: Successfully created resource

    Raises:
        ValueError: If config is None
        {{RESOURCE_ERROR}}: If all retries fail
    """
    if not config:
        raise ValueError("Config is required")

    last_error = None

    for attempt in range(max_retries):
        resource = None
        try:
            # Attempt to create resource
            resource = await create_{{RESOURCE_NAME}}(config)

            # Success - yield and return
            try:
                yield resource
                return
            finally:
                await resource.close()

        except {{TRANSIENT_ERROR}} as e:
            last_error = e
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = retry_delay * (2**attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                # Final attempt failed
                logger.error(f"All {max_retries} attempts failed")
                raise last_error


# ==============================================================================
# TESTING TEMPLATE
# ==============================================================================


# Test file: test_{{MANAGER_NAME}}.py

"""
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_{{MANAGER_NAME}}_cleanup_on_success():
    '''Verify cleanup happens on successful completion.'''
    cleanup_called = False

    @asynccontextmanager
    async def test_manager() -> AsyncIterator[str]:
        nonlocal cleanup_called
        try:
            yield "resource"
        finally:
            cleanup_called = True

    async with test_manager() as resource:
        assert resource == "resource"

    assert cleanup_called is True


@pytest.mark.asyncio
async def test_{{MANAGER_NAME}}_cleanup_on_exception():
    '''Verify cleanup happens even when exception occurs.'''
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


@pytest.mark.asyncio
async def test_{{MANAGER_NAME}}_resource_state_tracking():
    '''Verify resource state is tracked correctly.'''
    stats = Stats()

    @asynccontextmanager
    async def tracked_manager() -> AsyncIterator[str]:
        stats.active_count += 1
        try:
            yield "resource"
        finally:
            stats.active_count -= 1

    assert stats.active_count == 0

    async with tracked_manager():
        assert stats.active_count == 1

    assert stats.active_count == 0


@pytest.mark.asyncio
async def test_{{MANAGER_NAME}}_with_mock():
    '''Test context manager with mocked resource.'''
    # Create mock resource
    mock_resource = AsyncMock()
    mock_resource.{{OPERATION}}.return_value = "result"

    # Create mock context manager
    mock_manager = MagicMock()
    mock_manager.__aenter__.return_value = mock_resource
    mock_manager.__aexit__.return_value = None

    # Test
    async with mock_manager as resource:
        result = await resource.{{OPERATION}}()
        assert result == "result"

    # Verify cleanup
    mock_manager.__aexit__.assert_called_once()
"""


# ==============================================================================
# REPLACEMENT GUIDE
# ==============================================================================

"""
PLACEHOLDERS TO REPLACE:

Core:
    {{MANAGER_NAME}}        - Name of context manager function (e.g., database_session)
    {{RESOURCE_TYPE}}       - Type of resource being managed (e.g., AsyncSession)
    {{CONFIG_TYPE}}         - Type of configuration object (e.g., Settings)
    {{DESCRIPTION}}         - Brief description of what this manages
    {{RESOURCE_NAME}}       - Resource name for function calls (e.g., session)
    {{RESOURCE_ERROR}}      - Exception type for resource errors
    {{OPERATION}}           - Example operation on resource (e.g., query)

Statistics:
    {{STATS_TYPE}}          - Type of statistics collector (e.g., QueryStats)

Pool:
    {{POOL_NAME}}           - Name of pool manager function
    {{POOL_TYPE}}           - Type of resource pool (e.g., ConnectionPool)

Transaction:
    {{TRANSACTION_NAME}}    - Name of transaction manager
    {{SESSION_TYPE}}        - Type of session (e.g., AsyncSession)
    {{TRANSACTION_TYPE}}    - Type of transaction (e.g., AsyncTransaction)

Nested:
    {{NESTED_MANAGER_NAME}} - Name of nested manager
    {{RESOURCE_TYPE_1}}     - First resource type
    {{RESOURCE_TYPE_2}}     - Second resource type
    {{MANAGER_1}}           - First context manager function
    {{MANAGER_2}}           - Second context manager function

Retry:
    {{RETRY_MANAGER_NAME}}  - Name of retry manager
    {{TRANSIENT_ERROR}}     - Exception type for transient errors

COMMON REPLACEMENTS:

Database Session:
    {{MANAGER_NAME}}     -> database_session
    {{RESOURCE_TYPE}}    -> AsyncSession
    {{CONFIG_TYPE}}      -> Settings
    {{RESOURCE_NAME}}    -> session
    {{RESOURCE_ERROR}}   -> DatabaseError
    {{OPERATION}}        -> run

Connection Pool:
    {{POOL_NAME}}        -> pooled_connection
    {{POOL_TYPE}}        -> ConnectionPool
    {{RESOURCE_TYPE}}    -> Connection

File Handler:
    {{MANAGER_NAME}}     -> async_file
    {{RESOURCE_TYPE}}    -> AsyncTextIOWrapper
    {{CONFIG_TYPE}}      -> Path
    {{OPERATION}}        -> write

HTTP Client:
    {{MANAGER_NAME}}     -> http_session
    {{RESOURCE_TYPE}}    -> ClientSession
    {{CONFIG_TYPE}}      -> HTTPConfig
    {{OPERATION}}        -> get
"""
