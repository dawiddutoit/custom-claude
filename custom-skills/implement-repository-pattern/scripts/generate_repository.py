#!/usr/bin/env python3
"""Generate repository pattern files with domain protocol and infrastructure implementation.

This script automates repository creation following Clean Architecture principles:
- Protocol (ABC) in domain/repositories/
- Neo4j implementation in infrastructure/neo4j/
- Test files with proper mocking
- Container registration hints

Usage:
    python generate_repository.py <entity_name> [--methods METHOD1,METHOD2]
    python generate_repository.py SearchHistory --methods save_query,get_recent
    python generate_repository.py User --methods save,get,delete,exists
"""

import argparse
import re
import sys
from pathlib import Path

# Note: This script is designed to be run standalone with no external dependencies
# beyond Python's standard library.


# Templates
PROTOCOL_TEMPLATE = '''"""Repository interface for {purpose}.

This module defines the {{name}}Repository port following Clean Architecture principles.
This is a port (interface) that will be implemented by adapters in the infrastructure layer.
"""

from abc import ABC, abstractmethod

from project_watch_mcp.domain.common import ServiceResult
# TODO: Import domain models as needed
# from project_watch_mcp.domain.models.<model> import <Model>


class {pascal_name}Repository(ABC):
    """Port for {purpose} storage and retrieval.

    This interface defines the contract for {brief_description}.
    Concrete implementations will be provided in the infrastructure layer
    (e.g., Neo4j{pascal_name}Repository).
    """

{methods}
'''

METHOD_PROTOCOL_TEMPLATE = '''    @abstractmethod
    async def {method_name}(self{params}) -> ServiceResult[{return_type}]:
        """{docstring}

        Args:{arg_docs}

        Returns:
            ServiceResult[{return_type}]: {return_doc}
        """
        pass
'''

IMPLEMENTATION_TEMPLATE = '''"""Neo4j implementation of the {pascal_name}Repository interface.

This module provides the concrete implementation of the {pascal_name}Repository port
for Neo4j database storage, following Clean Architecture principles.
"""

from typing import Any, LiteralString, cast

from neo4j import AsyncDriver, RoutingControl
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from project_watch_mcp.config.settings import Settings
from project_watch_mcp.core.monitoring import get_logger
from project_watch_mcp.domain.common import ServiceResult
from project_watch_mcp.domain.repositories.{snake_name}_repository import {pascal_name}Repository
from project_watch_mcp.domain.services.resource_manager import ManagedResource
# TODO: Import domain models as needed
# from project_watch_mcp.domain.models.<model> import <Model>
from project_watch_mcp.infrastructure.neo4j.queries import CypherQueries
from project_watch_mcp.infrastructure.neo4j.query_builder import validate_and_build_query

logger = get_logger(__name__)


class Neo4j{pascal_name}Repository({pascal_name}Repository, ManagedResource):
    """Neo4j adapter implementing the {pascal_name}Repository interface.

    This adapter handles all {purpose} operations using Neo4j graph database,
    including connection pooling, retries, and explicit database specification.
    """

    def __init__(self, driver: AsyncDriver, settings: Settings):
        """Initialize the Neo4j {snake_name} repository.

        Args:
            driver: Neo4j async driver instance
            settings: Application settings containing Neo4j configuration

        Raises:
            ValueError: If driver or settings is None
        """
        if not driver:
            raise ValueError("Neo4j driver is required")
        if not settings:
            raise ValueError("Settings is required")

        self.driver = driver
        self.settings = settings
        self.database = settings.neo4j.database_name
        self.max_retries = settings.neo4j.max_retries
        self.initial_retry_delay = settings.neo4j.initial_retry_delay
        self.retry_delay_multiplier = settings.neo4j.retry_delay_multiplier
        self.max_retry_delay = settings.neo4j.max_retry_delay

    async def _execute_with_retry(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        routing: RoutingControl = RoutingControl.WRITE,
    ) -> ServiceResult[list[dict]]:
        """Execute a query with parameter validation and retry logic.

        Args:
            query: Cypher query to execute
            parameters: Query parameters
            routing: Routing control for read/write operations

        Returns:
            ServiceResult containing query results or validation error
        """
        # VALIDATE BEFORE EXECUTING
        validation_result = validate_and_build_query(query, parameters, strict=True)
        if validation_result.is_failure:
            logger.error(f"Query validation failed: {{validation_result.error}}")
            return ServiceResult.fail(f"Parameter validation failed: {{validation_result.error}}")

        validated_query = validation_result.data
        assert validated_query is not None

        # Log validation warnings even if query is valid
        if validated_query.validation_result.warnings:
            for warning in validated_query.validation_result.warnings:
                logger.warning(f"Query validation warning: {{warning}}")

        # Use driver.execute_query for automatic transaction management and retries
        try:
            # Driver.execute_query returns tuple (records, summary, keys)
            # Use validated parameters
            records, _, _ = await self.driver.execute_query(
                cast(LiteralString, validated_query.query),
                validated_query.parameters,
                database_=self.database,
                routing_=routing,
            )
            # Convert records to list of dicts
            data = [dict(record) for record in records]
            return ServiceResult.ok(data)
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {{e}}")
            return ServiceResult.fail(f"Database unavailable: {{str(e)}}")
        except Neo4jError as e:
            logger.error(f"Neo4j error: {{e}}")
            return ServiceResult.fail(f"Database error: {{str(e)}}")
        except Exception as e:
            logger.error(f"Unexpected error executing query: {{e}}")
            return ServiceResult.fail(f"Unexpected error: {{str(e)}}")

{methods}

    async def close(self) -> None:
        """Close and cleanup Neo4j driver resources.

        Implements the ManagedResource protocol for proper resource cleanup.
        This method is idempotent and handles errors gracefully.

        Note: The driver itself is managed externally (by container),
        so we don't close it here. This is a placeholder for any
        repository-specific cleanup if needed in the future.
        """
        try:
            # Currently no repository-specific resources to clean up
            # The driver is managed by the container
            logger.debug(f"Neo4j{pascal_name}Repository cleanup complete")
        except Exception as e:
            logger.error(f"Error during Neo4j{pascal_name}Repository cleanup: {{e}}")
            # Don't raise - cleanup should be best-effort
'''

METHOD_IMPLEMENTATION_TEMPLATE = '''    async def {method_name}(self{params}) -> ServiceResult[{return_type}]:
        """{docstring}

        Args:{arg_docs}

        Returns:
            ServiceResult[{return_type}]: {return_doc}
        """
        # TODO: Implement query
        query = CypherQueries.{query_const}
        parameters = {{
            # TODO: Add parameters
        }}

        result = await self._execute_with_retry(
            query,
            parameters,
            routing=RoutingControl.{routing}
        )
        if result.is_failure:
            logger.error(f"Failed to {method_name}: {{result.error}}")
            return ServiceResult.fail(f"Failed to {method_name}: {{result.error}}")

        # TODO: Transform result data if needed
        return ServiceResult.ok({default_return})
'''

TEST_TEMPLATE = '''"""Unit tests for Neo4j{pascal_name}Repository.

Tests the Neo4j implementation of the {pascal_name}Repository interface,
verifying correct parameter validation, query execution, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from project_watch_mcp.config.settings import Settings
from project_watch_mcp.domain.common import ServiceResult
from project_watch_mcp.infrastructure.neo4j.{snake_name}_repository import Neo4j{pascal_name}Repository


@pytest.fixture
def mock_driver():
    """Create mock Neo4j async driver."""
    driver = MagicMock()
    driver.execute_query = AsyncMock()
    return driver


@pytest.fixture
def settings():
    """Create test settings."""
    s = MagicMock(spec=Settings)
    s.neo4j.database_name = "test_db"
    s.neo4j.max_retries = 3
    s.neo4j.initial_retry_delay = 0.1
    s.neo4j.retry_delay_multiplier = 2.0
    s.neo4j.max_retry_delay = 5.0
    return s


@pytest.fixture
def repository(mock_driver, settings):
    """Create repository instance."""
    return Neo4j{pascal_name}Repository(mock_driver, settings)


@pytest.mark.asyncio
class TestNeo4j{pascal_name}Repository:
    """Test suite for Neo4j{pascal_name}Repository."""

    async def test_constructor_validates_driver(self, settings):
        """Test constructor fails fast if driver is None."""
        with pytest.raises(ValueError, match="Neo4j driver is required"):
            Neo4j{pascal_name}Repository(None, settings)  # type: ignore[arg-type]

    async def test_constructor_validates_settings(self, mock_driver):
        """Test constructor fails fast if settings is None."""
        with pytest.raises(ValueError, match="Settings is required"):
            Neo4j{pascal_name}Repository(mock_driver, None)  # type: ignore[arg-type]

{test_methods}

    async def test_close_is_idempotent(self, repository):
        """Test close can be called multiple times safely."""
        await repository.close()
        await repository.close()  # Should not raise
'''

TEST_METHOD_TEMPLATE = '''    async def test_{method_name}_success(self, repository, mock_driver):
        """Test successful {method_name} operation."""
        # Arrange
        mock_driver.execute_query.return_value = (
            [{{}}],  # TODO: Add expected return data
            None,
            None,
        )

        # Act
        result = await repository.{method_name}({test_params})

        # Assert
        assert result.is_success
        # TODO: Add more specific assertions

    async def test_{method_name}_database_error(self, repository, mock_driver):
        """Test {method_name} handles database errors."""
        # Arrange
        from neo4j.exceptions import Neo4jError
        mock_driver.execute_query.side_effect = Neo4jError("Connection failed")

        # Act
        result = await repository.{method_name}({test_params})

        # Assert
        assert result.is_failure
        assert "Database error" in result.error
'''


class MethodDefinition:
    """Represents a repository method definition."""

    def __init__(self, name: str) -> None:
        """Initialize method definition.

        Args:
            name: Method name (e.g., save, get, delete)
        """
        self.name = name
        self.pascal_name = to_pascal_case(name)
        self.params = self._infer_params()
        self.return_type = self._infer_return_type()
        self.docstring = self._generate_docstring()
        self.arg_docs = self._generate_arg_docs()
        self.return_doc = self._generate_return_doc()
        self.routing = self._infer_routing()
        self.default_return = self._infer_default_return()
        self.test_params = self._generate_test_params()

    def _infer_params(self) -> str:
        """Infer parameter signature from method name."""
        if self.name.startswith("save"):
            return ", entity: Any"
        if self.name.startswith("get") and "by" in self.name:
            return ", project_name: str"
        if (
            self.name.startswith("get")
            or self.name.startswith("delete")
            or self.name.endswith("exists")
        ):
            return ", entity_id: str, project_name: str"
        return ""

    def _infer_return_type(self) -> str:
        """Infer return type from method name."""
        if self.name.endswith("exists"):
            return "bool"
        if self.name.startswith("save") or self.name.startswith("delete"):
            return "None"
        if self.name.startswith("get") and "by" in self.name:
            return "list[Any]"
        if self.name.startswith("get"):
            return "Any | None"
        return "Any"

    def _infer_routing(self) -> str:
        """Infer routing control from method name."""
        if self.name.startswith("get") or self.name.endswith("exists"):
            return "READ"
        return "WRITE"

    def _infer_default_return(self) -> str:
        """Infer default return value."""
        if self.return_type == "None":
            return "None"
        if self.return_type == "bool":
            return "result.data[0].get('exists', False) if result.data else False"
        if "list" in self.return_type:
            return "[]"
        return "result.data[0] if result.data else None"

    def _generate_docstring(self) -> str:
        """Generate method docstring."""
        action = self.name.split("_")[0].capitalize()
        entity = self.name.replace(self.name.split("_")[0] + "_", "")
        return f"{action} {entity}"

    def _generate_arg_docs(self) -> str:
        """Generate argument documentation."""
        if not self.params:
            return ""

        docs = []
        for param in self.params.split(","):
            param = param.strip()
            if not param or param == "self":
                continue
            param_name = param.split(":")[0].strip()
            docs.append(f"\n            {param_name}: Description of {param_name}")
        return "".join(docs) if docs else ""

    def _generate_return_doc(self) -> str:
        """Generate return documentation."""
        if self.return_type == "None":
            return "Success if operation completed, Failure on errors"
        if self.return_type == "bool":
            return "Success with True/False, Failure on errors"
        if "list" in self.return_type:
            return "Success with list (empty if none found), Failure on errors"
        return "Success with data if found, Success with None if not found, Failure on errors"

    def _generate_test_params(self) -> str:
        """Generate test method parameters."""
        if "entity: Any" in self.params:
            return "entity={}"
        if "project_name" in self.params and "entity_id" in self.params:
            return '"test_id", "test_project"'
        if "project_name" in self.params:
            return '"test_project"'
        return ""


def to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    # Insert underscore before uppercase letters
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    # Insert underscore before uppercase letter in acronyms
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    words = text.replace("-", "_").replace(" ", "_").split("_")
    return "".join(word.capitalize() for word in words if word)


def generate_protocol(entity_name: str, methods: list[str], purpose: str) -> str:
    """Generate protocol (ABC) code.

    Args:
        entity_name: Name of entity (PascalCase)
        methods: List of method names
        purpose: Description of repository purpose

    Returns:
        Protocol file content
    """
    pascal_name = to_pascal_case(entity_name)
    snake_name = to_snake_case(entity_name)

    method_defs = [MethodDefinition(m) for m in methods]
    method_code = "\n".join(
        METHOD_PROTOCOL_TEMPLATE.format(
            method_name=m.name,
            params=m.params,
            return_type=m.return_type,
            docstring=m.docstring,
            arg_docs=m.arg_docs,
            return_doc=m.return_doc,
        )
        for m in method_defs
    )

    return PROTOCOL_TEMPLATE.format(
        name=snake_name,
        pascal_name=pascal_name,
        purpose=purpose,
        brief_description=f"{purpose} operations",
        methods=method_code,
    )


def generate_implementation(entity_name: str, methods: list[str], purpose: str) -> str:
    """Generate Neo4j implementation code.

    Args:
        entity_name: Name of entity (PascalCase)
        methods: List of method names
        purpose: Description of repository purpose

    Returns:
        Implementation file content
    """
    pascal_name = to_pascal_case(entity_name)
    snake_name = to_snake_case(entity_name)

    method_defs = [MethodDefinition(m) for m in methods]
    method_code = "\n".join(
        METHOD_IMPLEMENTATION_TEMPLATE.format(
            method_name=m.name,
            params=m.params,
            return_type=m.return_type,
            docstring=m.docstring,
            arg_docs=m.arg_docs,
            return_doc=m.return_doc,
            query_const=m.name.upper(),
            routing=m.routing,
            default_return=m.default_return,
        )
        for m in method_defs
    )

    return IMPLEMENTATION_TEMPLATE.format(
        pascal_name=pascal_name,
        snake_name=snake_name,
        purpose=purpose,
        methods=method_code,
    )


def generate_tests(entity_name: str, methods: list[str]) -> str:
    """Generate test code.

    Args:
        entity_name: Name of entity (PascalCase)
        methods: List of method names

    Returns:
        Test file content
    """
    pascal_name = to_pascal_case(entity_name)
    snake_name = to_snake_case(entity_name)

    method_defs = [MethodDefinition(m) for m in methods]
    test_code = "\n".join(
        TEST_METHOD_TEMPLATE.format(
            method_name=m.name,
            test_params=m.test_params,
        )
        for m in method_defs
    )

    return TEST_TEMPLATE.format(
        pascal_name=pascal_name,
        snake_name=snake_name,
        test_methods=test_code,
    )


def generate_queries(entity_name: str, methods: list[str]) -> str:
    """Generate Cypher query constants.

    Args:
        entity_name: Name of entity (PascalCase)
        methods: List of method names

    Returns:
        Query constant definitions
    """
    pascal_name = to_pascal_case(entity_name)
    label = pascal_name

    queries = [f"# {pascal_name}Repository Queries"]

    for method in methods:
        const_name = method.upper()
        if method.startswith("save"):
            queries.append(
                f"""
{const_name} = \"\"\"
MERGE (e:{label} {{project_name: $project_name, id: $id}})
SET e += $properties
SET e.updated_at = datetime()
RETURN e
\"\"\"
"""
            )
        elif method.startswith("get") and "by" in method:
            queries.append(
                f"""
{const_name} = \"\"\"
MATCH (e:{label} {{project_name: $project_name}})
RETURN e
\"\"\"
"""
            )
        elif method.startswith("get"):
            queries.append(
                f"""
{const_name} = \"\"\"
MATCH (e:{label} {{project_name: $project_name, id: $id}})
RETURN e
\"\"\"
"""
            )
        elif method.startswith("delete"):
            queries.append(
                f"""
{const_name} = \"\"\"
MATCH (e:{label} {{project_name: $project_name, id: $id}})
DETACH DELETE e
\"\"\"
"""
            )
        elif method.endswith("exists"):
            queries.append(
                f"""
{const_name} = \"\"\"
MATCH (e:{label} {{project_name: $project_name, id: $id}})
RETURN count(e) > 0 AS exists
\"\"\"
"""
            )

    return "\n".join(queries)


def generate_container_hint(entity_name: str) -> str:
    """Generate container registration hint.

    Args:
        entity_name: Name of entity (PascalCase)

    Returns:
        Container registration code snippet
    """
    pascal_name = to_pascal_case(entity_name)
    snake_name = to_snake_case(entity_name)

    return f"""
# Add to src/project_watch_mcp/interfaces/mcp/container.py:

from project_watch_mcp.infrastructure.neo4j.{snake_name}_repository import Neo4j{pascal_name}Repository

# Inside Container class:
{snake_name}_repository = providers.Singleton(
    Neo4j{pascal_name}Repository,
    driver=neo4j_driver,
    settings=settings,
)
"""


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate repository pattern files with protocol and implementation"
    )
    parser.add_argument("entity_name", help="Entity name (e.g., SearchHistory, User)")
    parser.add_argument(
        "--methods",
        default="save,get,delete,exists",
        help="Comma-separated method names (default: save,get,delete,exists)",
    )
    parser.add_argument(
        "--purpose",
        default=None,
        help="Repository purpose description (default: auto-generated)",
    )
    parser.add_argument(
        "--output-dir",
        default="src/project_watch_mcp",
        help="Base output directory (default: src/project_watch_mcp)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files without writing",
    )

    args = parser.parse_args()

    # Parse inputs
    entity_name = args.entity_name
    pascal_name = to_pascal_case(entity_name)
    snake_name = to_snake_case(entity_name)
    methods = [m.strip() for m in args.methods.split(",")]
    purpose = args.purpose or f"{pascal_name.lower()} storage and retrieval"

    # Define paths
    base_dir = Path(args.output_dir)
    protocol_path = base_dir / "domain" / "repositories" / f"{snake_name}_repository.py"
    impl_path = base_dir / "infrastructure" / "neo4j" / f"{snake_name}_repository.py"
    test_path = (
        base_dir.parent
        / "tests"
        / "unit"
        / "infrastructure"
        / "neo4j"
        / f"test_{snake_name}_repository.py"
    )

    # Generate code
    protocol_code = generate_protocol(entity_name, methods, purpose)
    impl_code = generate_implementation(entity_name, methods, purpose)
    test_code = generate_tests(entity_name, methods)
    query_code = generate_queries(entity_name, methods)
    container_hint = generate_container_hint(entity_name)

    if args.dry_run:
        print(f"=== Would generate files for {pascal_name}Repository ===\n")
        print(f"--- Protocol: {protocol_path} ---")
        print(protocol_code[:500] + "...\n")
        print(f"--- Implementation: {impl_path} ---")
        print(impl_code[:500] + "...\n")
        print(f"--- Tests: {test_path} ---")
        print(test_code[:500] + "...\n")
        print("--- Query constants (add to queries.py) ---")
        print(query_code)
        print(container_hint)

        return 0

    # Write files
    protocol_path.parent.mkdir(parents=True, exist_ok=True)
    protocol_path.write_text(protocol_code)
    print(f"Created: {protocol_path}")

    impl_path.parent.mkdir(parents=True, exist_ok=True)
    impl_path.write_text(impl_code)
    print(f"Created: {impl_path}")

    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(test_code)
    print(f"Created: {test_path}")

    print("\n--- Add these query constants to queries.py ---")
    print(query_code)
    print(container_hint)

    return 0


if __name__ == "__main__":
    sys.exit(main())
