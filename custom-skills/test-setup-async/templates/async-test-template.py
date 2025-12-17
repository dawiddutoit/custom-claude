"""Template: Async Test with Fixtures and Mocks

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {{SERVICE_NAME}}: Service class name (e.g., ChunkingService)
- {{METHOD_NAME}}: Method name to test (e.g., process_file)
- {{FIXTURE_NAME}}: Fixture name (e.g., mock_embedding_service)

Usage:
1. Copy this template to your test file
2. Replace all {{PLACEHOLDERS}} with your values
3. Customize fixtures and test logic for your use case

Example:
- {{SERVICE_NAME}} -> ChunkingService
- {{METHOD_NAME}} -> process_file
- {{FIXTURE_NAME}} -> mock_embedding_service
"""

import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from {{PROJECT_NAME}}.domain.values.service_result import ServiceResult

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_settings():
    """Create mock Settings for testing.

    Customize this with the settings your service needs.
    """
    settings = MagicMock()
    settings.chunking = MagicMock()
    settings.chunking.max_chunk_size = 1000
    settings.chunking.overlap = 100
    return settings


@pytest.fixture
def mock_{{FIXTURE_NAME}}():
    """Create mock {{SERVICE_NAME}} for testing.

    This is a SYNC fixture that creates AsyncMock instances.
    Use this pattern for creating mocks.
    """
    service = AsyncMock()

    # Configure default return values
    service.{{METHOD_NAME}}.return_value = ServiceResult.success({
        "result": "success",
        "data": ["item1", "item2"]
    })

    # Configure other methods as needed
    service.get_status.return_value = {"status": "ready"}

    return service


@pytest_asyncio.fixture
async def async_resource() -> AsyncGenerator[Resource, None]:
    """Create async resource with setup and cleanup.

    This is an ASYNC fixture for resources that need async initialization.
    Use this pattern for database connections, clients, etc.
    """
    # Async setup
    resource = await create_resource()
    await resource.initialize()

    yield resource

    # Async cleanup
    await resource.shutdown()
    await resource.close()


@pytest.fixture
def mock_neo4j_driver():
    """Create mock Neo4j driver with async session support.

    Use this pattern for mocking async context managers.
    """
    # Driver itself is sync
    driver = MagicMock()

    # Create async session mock
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Configure session methods
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[{"n": {"id": 1}}])
    mock_session.run = AsyncMock(return_value=mock_result)

    # Wire up driver.session() to return session
    driver.session = MagicMock(return_value=mock_session)

    return driver


# ============================================================================
# TESTS - Basic Patterns
# ============================================================================


@pytest.mark.asyncio
async def test_{{METHOD_NAME}}_success(mock_{{FIXTURE_NAME}}, mock_settings):
    """Test {{METHOD_NAME}} succeeds with valid input.

    Pattern: Basic async test with mocked dependencies.
    """
    from {{PROJECT_NAME}}.application.services.{{SERVICE_NAME}} import {{SERVICE_NAME}}

    # Arrange: Create service with mocked dependencies
    service = {{SERVICE_NAME}}(
        dependency=mock_{{FIXTURE_NAME}},
        settings=mock_settings
    )

    # Act: Call async method
    result = await service.{{METHOD_NAME}}("test_input")

    # Assert: Verify result
    assert result.is_success()
    assert result.value["result"] == "success"

    # Assert: Verify mock was called correctly
    mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.assert_awaited_once_with("test_input")


@pytest.mark.asyncio
async def test_{{METHOD_NAME}}_handles_error(mock_{{FIXTURE_NAME}}, mock_settings):
    """Test {{METHOD_NAME}} handles errors gracefully.

    Pattern: Testing error handling with side_effect.
    """
    from {{PROJECT_NAME}}.application.services.{{SERVICE_NAME}} import {{SERVICE_NAME}}

    # Arrange: Configure mock to raise exception
    mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.side_effect = Exception("Service unavailable")

    service = {{SERVICE_NAME}}(
        dependency=mock_{{FIXTURE_NAME}},
        settings=mock_settings
    )

    # Act: Call method that should handle error
    result = await service.{{METHOD_NAME}}("test_input")

    # Assert: Verify ServiceResult.failure() was returned
    assert not result.is_success()
    assert "Service unavailable" in result.error

    # Assert: Verify error was logged (if applicable)
    # service.logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_{{METHOD_NAME}}_with_retry(mock_{{FIXTURE_NAME}}, mock_settings):
    """Test {{METHOD_NAME}} retries on failure.

    Pattern: Testing retry logic with side_effect sequence.
    """
    from {{PROJECT_NAME}}.application.services.{{SERVICE_NAME}} import {{SERVICE_NAME}}

    # Arrange: First two calls fail, third succeeds
    mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.side_effect = [
        Exception("Timeout"),
        Exception("Connection reset"),
        ServiceResult.success({"result": "success"})
    ]

    service = {{SERVICE_NAME}}(
        dependency=mock_{{FIXTURE_NAME}},
        settings=mock_settings
    )

    # Act: Call method with retry logic
    result = await service.{{METHOD_NAME}}("test_input")

    # Assert: Verify final result is success
    assert result.is_success()

    # Assert: Verify retry count
    assert mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.await_count == 3


# ============================================================================
# TESTS - Context Manager Pattern
# ============================================================================


@pytest.mark.asyncio
async def test_with_neo4j_session(mock_neo4j_driver):
    """Test code that uses Neo4j async context manager.

    Pattern: Testing async context manager usage.
    """
    # Act: Use driver in async context manager
    async with mock_neo4j_driver.session() as session:
        result = await session.run("MATCH (n) RETURN n")
        data = await result.data()

    # Assert: Verify query execution
    assert len(data) == 1
    assert data[0]["n"]["id"] == 1

    # Assert: Verify session was created
    mock_neo4j_driver.session.assert_called_once()


# ============================================================================
# TESTS - Parametrized Async Tests
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize("input_value,expected_output", [
    ("input1", "output1"),
    ("input2", "output2"),
    ("input3", "output3"),
])
async def test_{{METHOD_NAME}}_with_parameters(
    mock_{{FIXTURE_NAME}},
    mock_settings,
    input_value,
    expected_output
):
    """Test {{METHOD_NAME}} with various inputs.

    Pattern: Parametrized async tests.
    """
    from {{PROJECT_NAME}}.application.services.{{SERVICE_NAME}} import {{SERVICE_NAME}}

    # Arrange: Configure mock for specific input
    mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.return_value = ServiceResult.success(
        {"output": expected_output}
    )

    service = {{SERVICE_NAME}}(
        dependency=mock_{{FIXTURE_NAME}},
        settings=mock_settings
    )

    # Act
    result = await service.{{METHOD_NAME}}(input_value)

    # Assert
    assert result.is_success()
    assert result.value["output"] == expected_output


# ============================================================================
# TESTS - Concurrent Operations
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_processing(mock_{{FIXTURE_NAME}}, mock_settings):
    """Test processing multiple items concurrently.

    Pattern: Testing concurrent async operations.
    """
    import asyncio
    from {{PROJECT_NAME}}.application.services.{{SERVICE_NAME}} import {{SERVICE_NAME}}

    # Arrange: Configure mock to handle multiple calls
    async def mock_process(item):
        await asyncio.sleep(0.01)  # Simulate async work
        return ServiceResult.success(f"processed_{item}")

    mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.side_effect = mock_process

    service = {{SERVICE_NAME}}(
        dependency=mock_{{FIXTURE_NAME}},
        settings=mock_settings
    )

    # Act: Process items concurrently
    items = ["item1", "item2", "item3"]
    results = await asyncio.gather(*[
        service.{{METHOD_NAME}}(item) for item in items
    ])

    # Assert: All items processed
    assert len(results) == 3
    assert all(r.is_success() for r in results)

    # Assert: Mock called for each item
    assert mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.await_count == 3


# ============================================================================
# TESTS - Custom Side Effect Function
# ============================================================================


@pytest.mark.asyncio
async def test_conditional_behavior(mock_{{FIXTURE_NAME}}, mock_settings):
    """Test conditional behavior with custom side effect.

    Pattern: Using custom function for complex mock behavior.
    """
    from {{PROJECT_NAME}}.application.services.{{SERVICE_NAME}} import {{SERVICE_NAME}}

    # Arrange: Define custom behavior
    async def custom_behavior(input_value):
        if input_value == "error":
            raise ValueError("Invalid input")
        if input_value == "empty":
            return ServiceResult.success([])
        return ServiceResult.success([f"result_for_{input_value}"])

    mock_{{FIXTURE_NAME}}.{{METHOD_NAME}}.side_effect = custom_behavior

    service = {{SERVICE_NAME}}(
        dependency=mock_{{FIXTURE_NAME}},
        settings=mock_settings
    )

    # Act & Assert: Test success case
    result = await service.{{METHOD_NAME}}("valid")
    assert result.is_success()
    assert len(result.value) == 1

    # Act & Assert: Test empty case
    result = await service.{{METHOD_NAME}}("empty")
    assert result.is_success()
    assert len(result.value) == 0

    # Act & Assert: Test error case
    result = await service.{{METHOD_NAME}}("error")
    assert not result.is_success()


# ============================================================================
# INTEGRATION TEST EXAMPLE
# ============================================================================


@pytest.mark.asyncio
async def test_integration_with_real_resource(async_resource):
    """Integration test using real async resource.

    Pattern: Integration test with real dependencies.
    """
    # Act: Use real resource (no mocks)
    result = await async_resource.execute_operation()

    # Assert: Verify real behavior
    assert result is not None

    # Note: async_resource will be cleaned up automatically
    # by the async fixture's teardown code


# ============================================================================
# HELPER FUNCTIONS (Optional)
# ============================================================================


async def create_resource():
    """Helper to create resource for async fixture.

    Customize this based on your resource type.
    """
    # Simulate async initialization
    import asyncio
    await asyncio.sleep(0.01)

    # Return mock resource
    from unittest.mock import AsyncMock
    resource = AsyncMock()
    resource.initialize = AsyncMock()
    resource.shutdown = AsyncMock()
    resource.close = AsyncMock()
    resource.execute_operation = AsyncMock(return_value="result")
    return resource
