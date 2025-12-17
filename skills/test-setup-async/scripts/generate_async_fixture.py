#!/usr/bin/env python3
"""Generate async fixture boilerplate code.

This script generates properly typed async fixtures with cleanup for common resource types.
Supports Neo4j drivers, database connections, API clients, and custom resources.

Usage:
    python generate_async_fixture.py <fixture_name> <resource_type>
    python generate_async_fixture.py neo4j_driver database
    python generate_async_fixture.py mock_service mock
    python generate_async_fixture.py api_client client

Resource Types:
    - database: Database connection (Neo4j, PostgreSQL, etc.)
    - client: API/HTTP client
    - mock: AsyncMock service
    - session: Session-scoped resource
    - custom: Generic async resource

Examples:
    # Generate Neo4j driver fixture
    python generate_async_fixture.py neo4j_driver database

    # Generate mock service fixture
    python generate_async_fixture.py mock_embedding_service mock

    # Generate API client fixture
    python generate_async_fixture.py api_client client --with-auth

    # Copy to clipboard (macOS)
    python generate_async_fixture.py my_fixture database | pbcopy
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ResourceType(Enum):
    """Types of async resources for fixture generation."""

    DATABASE = "database"
    CLIENT = "client"
    MOCK = "mock"
    SESSION = "session"
    CUSTOM = "custom"


@dataclass
class FixtureConfig:
    """Configuration for fixture generation."""

    name: str
    resource_type: ResourceType
    scope: str = "function"
    with_auth: bool = False
    with_cleanup: bool = True
    return_type: str | None = None


class AsyncFixtureGenerator:
    """Generate async fixture boilerplate."""

    def __init__(self, config: FixtureConfig) -> None:
        self.config = config

    def generate(self) -> str:
        """Generate complete fixture code."""
        parts = [
            self._generate_imports(),
            "",
            self._generate_fixture_code(),
        ]

        return "\n".join(parts)

    def _generate_imports(self) -> str:
        """Generate necessary imports."""
        imports = [
            "import pytest_asyncio",
            "from collections.abc import AsyncGenerator",
        ]

        if self.config.resource_type == ResourceType.MOCK:
            imports.append("from unittest.mock import AsyncMock, MagicMock")

        if self.config.resource_type == ResourceType.DATABASE:
            imports.extend(
                [
                    "",
                    "# Database-specific imports",
                    "# from neo4j import AsyncDriver, AsyncGraphDatabase",
                    "# from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine",
                ]
            )

        if self.config.resource_type == ResourceType.CLIENT:
            imports.extend(
                [
                    "",
                    "# Client-specific imports",
                    "# import httpx",
                    "# from your_module import AsyncClient",
                ]
            )

        return "\n".join(imports)

    def _generate_fixture_code(self) -> str:
        """Generate fixture function code."""
        if self.config.resource_type == ResourceType.DATABASE:
            return self._generate_database_fixture()
        if self.config.resource_type == ResourceType.MOCK:
            return self._generate_mock_fixture()
        if self.config.resource_type == ResourceType.CLIENT:
            return self._generate_client_fixture()
        if self.config.resource_type == ResourceType.SESSION:
            return self._generate_session_fixture()
        return self._generate_custom_fixture()

    def _generate_database_fixture(self) -> str:
        """Generate database connection fixture."""
        return_type = self.config.return_type or "AsyncDriver"

        return f'''@pytest_asyncio.fixture(scope="{self.config.scope}")
async def {self.config.name}() -> AsyncGenerator[{return_type}, None]:
    """Create async database connection with cleanup.

    Provides a database connection for testing with automatic cleanup.
    The connection is initialized before each test and closed after.

    Yields:
        {return_type}: Database connection/driver instance

    Example:
        @pytest.mark.asyncio
        async def test_query({self.config.name}):
            async with {self.config.name}.session() as session:
                result = await session.run("MATCH (n) RETURN n")
                data = await result.data()
                assert len(data) > 0
    """
    # Setup: Create database connection
    # TODO: Replace with actual database connection
    # Example for Neo4j:
    # driver = AsyncGraphDatabase.driver(
    #     "bolt://localhost:7687",
    #     auth=("neo4j", "password")
    # )

    # Example for PostgreSQL:
    # engine = create_async_engine(
    #     "postgresql+asyncpg://user:password@localhost/testdb"
    # )

    # Placeholder implementation
    from unittest.mock import AsyncMock

    driver = AsyncMock()

    # Optional: Clear test data before test
    # async with driver.session() as session:
    #     await session.run("MATCH (n:TestNode) DETACH DELETE n")

    yield driver

    # Cleanup: Close connection
    # await driver.close()
    pass'''

    def _generate_mock_fixture(self) -> str:
        """Generate mock service fixture."""
        return_type = self.config.return_type or "AsyncMock"

        return f'''@pytest.fixture
def {self.config.name}() -> {return_type}:
    """Create mock service for testing.

    This is a SYNC fixture that creates AsyncMock instances.
    Use this pattern for creating async service mocks.

    Returns:
        {return_type}: Mock service with configured return values

    Example:
        @pytest.mark.asyncio
        async def test_service({self.config.name}):
            result = await {self.config.name}.fetch_data()
            assert result is not None
            {self.config.name}.fetch_data.assert_awaited_once()
    """
    # Create mock service
    service = AsyncMock()

    # Configure default return values
    # Example: service.fetch_data.return_value = {{"data": "test"}}
    service.fetch_data.return_value = {{"data": "test"}}
    service.save.return_value = None
    service.delete.return_value = None

    # Configure other methods as needed
    # service.method_name.return_value = expected_value
    # service.method_name.side_effect = Exception("Error message")

    return service'''

    def _generate_client_fixture(self) -> str:
        """Generate API client fixture."""
        return_type = self.config.return_type or "httpx.AsyncClient"

        auth_code = ""
        if self.config.with_auth:
            auth_code = """
    # Setup: Configure authentication
    headers = {{
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }}
    client = httpx.AsyncClient(
        base_url="http://localhost:8000",
        headers=headers
    )"""
        else:
            auth_code = """
    # Setup: Create HTTP client
    client = httpx.AsyncClient(base_url="http://localhost:8000")"""

        return f'''@pytest_asyncio.fixture(scope="{self.config.scope}")
async def {self.config.name}() -> AsyncGenerator[{return_type}, None]:
    """Create async HTTP client with cleanup.

    Provides an HTTP client for testing API endpoints.
    The client is created before each test and closed after.

    Yields:
        {return_type}: Async HTTP client instance

    Example:
        @pytest.mark.asyncio
        async def test_api_call({self.config.name}):
            response = await {self.config.name}.get("/api/endpoint")
            assert response.status_code == 200
            data = response.json()
            assert "result" in data
    """
    import httpx
{auth_code}

    yield client

    # Cleanup: Close client
    await client.aclose()'''

    def _generate_session_fixture(self) -> str:
        """Generate session-scoped fixture."""
        return_type = self.config.return_type or "Resource"

        return f'''@pytest_asyncio.fixture(scope="session")
async def {self.config.name}() -> AsyncGenerator[{return_type}, None]:
    """Create session-scoped resource (shared across all tests).

    This fixture is initialized once at the start of the test session
    and cleaned up once at the end. Use for expensive resources.

    WARNING: Session-scoped fixtures are shared across tests. Ensure
    tests clean up their own test data to avoid interference.

    Yields:
        {return_type}: Shared resource instance

    Example:
        @pytest.mark.asyncio
        async def test_with_shared_resource({self.config.name}):
            result = await {self.config.name}.execute_operation()
            assert result is not None
    """
    # Setup: Create expensive resource (once per session)
    # TODO: Replace with actual resource initialization
    # resource = await create_resource()
    # await resource.initialize()

    # Placeholder implementation
    from unittest.mock import AsyncMock

    resource = AsyncMock()

    yield resource

    # Cleanup: Shutdown resource (once at end of session)
    # await resource.shutdown()
    # await resource.close()
    pass'''

    def _generate_custom_fixture(self) -> str:
        """Generate custom async fixture template."""
        return_type = self.config.return_type or "CustomResource"

        return f'''@pytest_asyncio.fixture(scope="{self.config.scope}")
async def {self.config.name}() -> AsyncGenerator[{return_type}, None]:
    """Create custom async resource with cleanup.

    TODO: Add description of what this fixture provides.

    Yields:
        {return_type}: Custom resource instance

    Example:
        @pytest.mark.asyncio
        async def test_with_resource({self.config.name}):
            result = await {self.config.name}.do_something()
            assert result is not None
    """
    # Setup: Initialize resource
    # TODO: Replace with actual resource creation
    # resource = await create_resource()
    # await resource.initialize()

    # Placeholder implementation
    from unittest.mock import AsyncMock

    resource = AsyncMock()

    # Optional: Configure resource
    # resource.configure(option="value")

    yield resource

    # Cleanup: Release resource
    # TODO: Add cleanup logic
    # await resource.cleanup()
    # await resource.close()
    pass'''


def main() -> int:
    """Main entry point for async fixture generator.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate async fixture boilerplate code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Neo4j driver fixture
  python generate_async_fixture.py neo4j_driver database

  # Generate mock service fixture
  python generate_async_fixture.py mock_service mock

  # Generate API client with auth
  python generate_async_fixture.py api_client client --with-auth

  # Session-scoped fixture
  python generate_async_fixture.py shared_db database --scope session

  # Custom return type
  python generate_async_fixture.py my_fixture custom --return-type "MyResource"
        """,
    )

    parser.add_argument("name", help="Fixture name (e.g., neo4j_driver, mock_service)")
    parser.add_argument(
        "type",
        choices=[t.value for t in ResourceType],
        help="Resource type",
    )
    parser.add_argument(
        "--scope",
        choices=["function", "class", "module", "session"],
        default="function",
        help="Fixture scope (default: function)",
    )
    parser.add_argument(
        "--with-auth",
        action="store_true",
        help="Include authentication setup (for client type)",
    )
    parser.add_argument(
        "--return-type",
        help="Custom return type annotation (e.g., AsyncDriver, MyClient)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Save to file instead of stdout",
    )

    args = parser.parse_args()

    # Create configuration
    config = FixtureConfig(
        name=args.name,
        resource_type=ResourceType(args.type),
        scope=args.scope,
        with_auth=args.with_auth,
        return_type=args.return_type,
    )

    # Generate fixture
    generator = AsyncFixtureGenerator(config)
    code = generator.generate()

    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Fixture code written to {args.output}", file=sys.stderr)
    else:
        print(code)

    return 0


if __name__ == "__main__":
    sys.exit(main())
