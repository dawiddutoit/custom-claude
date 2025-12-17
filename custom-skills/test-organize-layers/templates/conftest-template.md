# Test Layer conftest.py Templates

## Unit Test conftest.py Template

**File**: `tests/unit/conftest.py`

```python
"""Shared pytest fixtures for all unit tests.

CRITICAL: Unit tests MUST mock ALL external dependencies.
No real database, filesystem, or network connections allowed.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from project_watch_mcp.config.settings import (
    Settings,
    ProjectSettings,
    Neo4jSettings,
    EmbeddingSettings,
    # Import all other settings...
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing.

    This is acceptable in unit tests because:
    - It's fast (<1ms)
    - It's isolated per test
    - No external system dependencies
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock configuration for testing.

    Returns complete Settings object with all required fields.
    Use this for dependency injection in unit tests.
    """
    return Settings(
        project=ProjectSettings(
            project_name="test_project",
            repository_path=temp_dir,
            include_patterns=["*.py"],
        ),
        neo4j=Neo4jSettings(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="testpassword",
            database_name="test",
        ),
        embedding=EmbeddingSettings(
            provider="voyage",
            model="voyage-code-3",
            api_key="test-api-key",
        ),
        # Add all other required settings...
    )


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver for unit tests.

    Use spec= for type safety - catches typos and wrong method calls.
    """
    from neo4j import AsyncDriver

    mock_driver = Mock(spec=AsyncDriver)
    mock_driver.execute_query = AsyncMock(return_value=([], None, None))
    return mock_driver


@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service for unit tests."""
    from project_watch_mcp.domain.interfaces.embedding_service import EmbeddingService

    mock_service = AsyncMock(spec=EmbeddingService)
    mock_service.embed_query.return_value = [0.1, 0.2, 0.3]  # Deterministic
    mock_service.embed_batch.return_value = [[0.1, 0.2, 0.3]]
    return mock_service


# Add more mock fixtures as needed for your unit tests
```

---

## Integration Test conftest.py Template

**File**: `tests/integration/conftest.py`

```python
"""Shared fixtures for integration tests with real infrastructure.

CRITICAL: Integration tests use PRODUCTION CODE for infrastructure.
DO NOT reimplement driver creation, session management, or database operations.
Use Neo4jDatabase from production code to ensure tests exercise real code paths.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from neo4j import AsyncDriver

from project_watch_mcp.config.settings import Settings
from project_watch_mcp.infrastructure.neo4j.database import Neo4jDatabase


@pytest.fixture
def real_settings():
    """Get real Settings for integration tests.

    Uses the actual Settings.from_env() that the application uses.
    This is the ONLY place where Settings.from_env() should be called in tests.
    """
    return Settings.from_env()


@pytest_asyncio.fixture(scope="function")
async def neo4j_database(
    real_settings: Settings,
) -> AsyncGenerator[Neo4jDatabase, None]:
    """Create Neo4jDatabase instance using PRODUCTION CODE.

    This fixture uses the actual Neo4jDatabase class that production uses,
    ensuring tests exercise the same code paths as the application.

    CRITICAL: Tests should use THIS fixture, not create their own drivers.
    """
    # Use production code to create database instance
    db = Neo4jDatabase(settings=real_settings)

    try:
        # Initialize using production initialization logic
        await db.initialize()

        # Verify connection works using production health check
        if not await db.health_check():
            pytest.skip("Neo4j health check failed. Please ensure Neo4j is running.")

        yield db
    except Exception as e:
        pytest.skip(
            f"Neo4j connection failed: {e}. "
            "Please ensure Neo4j is running and credentials are correct."
        )
    finally:
        # Use production shutdown logic
        await db.shutdown()


@pytest_asyncio.fixture(scope="function")
async def neo4j_driver(
    neo4j_database: Neo4jDatabase,
) -> AsyncGenerator[AsyncDriver, None]:
    """Get Neo4j driver from production Neo4jDatabase instance.

    This fixture provides the driver for tests that need direct driver access,
    but the driver comes from production code, not reimplemented here.

    IMPORTANT: Prefer using neo4j_database fixture when possible, as it provides
    more functionality (execute_query with retry logic, statistics, etc.).
    """
    yield neo4j_database.driver


@pytest_asyncio.fixture(scope="function")
async def test_database(
    neo4j_database: Neo4jDatabase, real_settings: Settings
) -> AsyncGenerator[str, None]:
    """Get the test database name and ensure it's clean.

    This fixture provides the database name and handles complete cleanup
    of ALL data before and after tests to ensure isolation.

    CRITICAL: Cleans ALL data, not just nodes with test_marker.
    Tests should use unique project_name or other identifiers if they
    need data isolation from parallel tests.
    """
    database_name = real_settings.neo4j.database_name

    # Clean up ALL existing data before test
    try:
        await neo4j_database.execute_query(
            "MATCH (n) DETACH DELETE n",
            database=database_name,
        )
    except Exception:
        # Database might not exist yet or query might fail
        pass

    yield database_name

    # Clean up ALL data after test
    try:
        await neo4j_database.execute_query(
            "MATCH (n) DETACH DELETE n",
            database=database_name,
        )
    except Exception:
        # Cleanup errors are not critical
        pass


# Make fixtures available for all integration tests
__all__ = [
    "real_settings",
    "neo4j_database",
    "neo4j_driver",
    "test_database",
]
```

---

## E2E Test conftest.py Template

**File**: `tests/e2e/conftest.py`

```python
"""Shared fixtures for E2E tests with real database and services.

E2E tests verify complete workflows using the full production stack.
All services are real, no mocking except for external paid APIs if needed.
"""

import asyncio
import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from neo4j import AsyncDriver, AsyncGraphDatabase

from project_watch_mcp.config.settings import Settings
from project_watch_mcp.application.queries.search_code import SearchCodeHandler


# ========== Layer 0: Session-Level Real Codebase Indexing ==========


@pytest.fixture(scope="session")
def indexed_real_codebase():
    """Session-level fixture that indexes the ACTUAL project codebase.

    This fixture runs ONCE per test session and indexes the real codebase into Neo4j.
    All E2E tests can then query against this indexed data.

    This is critical for E2E tests as they validate against real code patterns.
    """

    async def do_indexing():
        # Get the actual project root
        project_root = Path(__file__).parent.parent.parent

        # Load settings from environment
        settings = Settings.from_env()

        # Create driver
        driver = AsyncGraphDatabase.driver(
            settings.neo4j.uri,
            auth=(settings.neo4j.username, settings.neo4j.password),
        )

        try:
            await driver.verify_connectivity()
            print("✅ Neo4j connectivity verified")

            # Index the real codebase using production handlers
            from project_watch_mcp.application.commands.initialize_project import (
                InitializeProjectHandler,
                InitializeProjectCommand,
            )
            from project_watch_mcp.application.commands.refresh_repository import (
                RefreshRepositoryHandler,
                RefreshRepositoryCommand,
            )

            # Initialize and index repository
            # (Implementation details depend on your project structure)

            print("✅ Repository indexed successfully")

        except Exception as e:
            print(f"❌ Failed to setup indexed codebase: {e}")
            pytest.skip(f"Failed to setup indexed codebase: {e}")
        finally:
            await driver.close()

    # Run the async indexing in a new event loop
    try:
        asyncio.run(do_indexing())
        yield True
    except Exception as e:
        print(f"❌ Session indexing failed: {e}")
        pytest.skip(f"Session indexing failed: {e}")


# ========== Layer 1: Base Infrastructure Fixtures ==========


@pytest_asyncio.fixture
async def neo4j_driver(
    test_settings, indexed_real_codebase
) -> AsyncGenerator[AsyncDriver, None]:
    """Base fixture for Neo4j database connection.

    This provides the foundational database connection that other
    fixtures can build upon.

    Note: Depends on indexed_real_codebase to ensure database has data.
    """
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not uri or not username or not password:
        pytest.skip("NEO4J credentials not set")

    driver = AsyncGraphDatabase.driver(uri, auth=(username, password))

    try:
        await driver.verify_connectivity()
        yield driver
    except Exception as e:
        await driver.close()
        pytest.skip(f"Neo4j connection failed: {e}")
    finally:
        await driver.close()


# ========== Layer 2: Service Fixtures ==========


@pytest_asyncio.fixture
async def search_handler(
    neo4j_driver: AsyncDriver, test_settings
) -> AsyncGenerator[SearchCodeHandler, None]:
    """Fixture providing semantic search capability with all real dependencies.

    This builds on the neo4j_driver fixture to provide a fully configured
    SearchCodeHandler with real services - no mocking.
    """
    from project_watch_mcp.infrastructure.embeddings.factory import (
        create_embedding_service,
    )
    from project_watch_mcp.infrastructure.neo4j.search_repository import (
        Neo4jSearchRepository,
    )

    # Create real embedding service
    embedding_service = create_embedding_service(test_settings)

    # Create real search repository
    search_repository = Neo4jSearchRepository(neo4j_driver, test_settings)

    # Assemble the real search handler
    handler = SearchCodeHandler(
        search_repository=search_repository,
        embedding_service=embedding_service,
        settings=test_settings,
    )

    yield handler


# ========== Layer 3: Query/Command Fixtures ==========


@pytest.fixture
def semantic_search_query():
    """Standard semantic search query for testing."""
    from project_watch_mcp.application.queries.search_code import (
        SearchCodeQuery,
        SearchType,
    )

    return SearchCodeQuery(
        query_text="test query",
        project_name="your-project-name",
        search_type=SearchType.SEMANTIC,
        limit=10,
    )


# Make fixtures available for all E2E tests
__all__ = [
    "indexed_real_codebase",
    "neo4j_driver",
    "search_handler",
    "semantic_search_query",
]
```

---

## Usage Notes

1. **Copy the appropriate template** to your test layer's conftest.py
2. **Customize fixtures** based on your project's specific needs
3. **Add project-specific fixtures** following the same patterns
4. **Maintain fixture layering**: Base fixtures → Service fixtures → Query fixtures
5. **Document fixture dependencies** in docstrings
6. **Use type hints** for all fixture return types

---

## Template Principles

- **Unit**: Mock everything, fast, isolated
- **Integration**: Real infrastructure, production code paths
- **E2E**: Full stack, real workflows, session-level expensive operations
- **Fixture Scope**: function (default), module (shared), session (expensive)
- **Type Safety**: Always use `spec=` with Mock, type hints on fixtures
- **Documentation**: Clear docstrings explaining fixture purpose and dependencies
