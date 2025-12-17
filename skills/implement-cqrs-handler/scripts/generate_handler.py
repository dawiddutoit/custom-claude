#!/usr/bin/env python3
"""Auto-generate CQRS handler boilerplate code.

This script generates:
- Request object (Command or Query)
- Handler class with proper structure
- DTO (for queries)
- Test file with constructor validation
- Container registration snippet

Usage:
    python generate_handler.py command IndexFile --deps repository:CodeRepository service:EmbeddingService
    python generate_handler.py query SearchCode --result "list[SearchResultDTO]" --deps repository:SearchRepository

Dependencies:
    - No external dependencies required (stdlib only)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Literal

# Setup: Add .claude to path for skill_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skill_utils import get_project_root, to_snake_case


def parse_dependencies(deps_str: str | None) -> list[tuple[str, str]]:
    """Parse dependency string into list of (name, type) tuples.

    Args:
        deps_str: String like "repository:CodeRepository service:EmbeddingService"

    Returns:
        List of tuples like [("repository", "CodeRepository"), ...]
    """
    if not deps_str:
        return []

    deps: list[tuple[str, str]] = []
    for dep in deps_str.split():
        if ":" not in dep:
            continue
        name, type_name = dep.split(":", 1)
        deps.append((name, type_name))
    return deps


def generate_command_request(handler_name: str, output_dir: Path) -> Path:
    """Generate command request object.

    Args:
        handler_name: Name of the handler in PascalCase
        output_dir: Directory to write the file to

    Returns:
        Path to the generated file
    """
    snake_name = to_snake_case(handler_name)
    class_name = f"{handler_name}Command"

    content = f'''"""Command for {snake_name} operation."""

from dataclasses import dataclass

from project_watch_mcp.application.commands.base import Command


@dataclass
class {class_name}(Command):
    """Command to {snake_name.replace("_", " ")}.

    Contains all data needed for the operation.
    """

    # Add your command parameters here
    # Example:
    # file_path: str
    # force: bool = False
    pass
'''

    file_path = output_dir / f"{snake_name}_command.py"
    file_path.write_text(content)
    return file_path


def generate_query_request(handler_name: str, output_dir: Path) -> Path:
    """Generate query request object.

    Args:
        handler_name: Name of the handler in PascalCase
        output_dir: Directory to write the file to

    Returns:
        Path to the generated file
    """
    snake_name = to_snake_case(handler_name)
    class_name = f"{handler_name}Query"

    content = f'''"""Query for {snake_name} operation."""

from dataclasses import dataclass

from project_watch_mcp.application.queries.base import Query


@dataclass
class {class_name}(Query):
    """Query to {snake_name.replace("_", " ")}.

    Contains parameters for data retrieval.
    """

    # Add your query parameters here
    # Example:
    # query_text: str
    # limit: int = 10
    pass
'''

    file_path = output_dir / f"{snake_name}.py"
    file_path.write_text(content)
    return file_path


def _build_dependency_imports(deps: list[tuple[str, str]]) -> str:
    """Build import statements for dependencies.

    Args:
        deps: List of (name, type) tuples

    Returns:
        Import statements as a string
    """
    dep_imports: list[str] = []
    for _dep_name, dep_type in deps:
        if "Repository" in dep_type:
            base_name = dep_type.replace("Repository", "")
            dep_imports.append(
                f"from project_watch_mcp.domain.repositories."
                f"{to_snake_case(base_name)} import {dep_type}"
            )
        elif "Service" in dep_type:
            base_name = dep_type.replace("Service", "_service")
            dep_imports.append(
                f"from project_watch_mcp.application.services."
                f"{to_snake_case(base_name)} import {dep_type}"
            )
    return (
        "\n".join(dep_imports) if dep_imports else "# Add your dependency imports here"
    )


def _build_init_components(
    deps: list[tuple[str, str]],
) -> tuple[str, str, str]:
    """Build __init__ method components.

    Args:
        deps: List of (name, type) tuples

    Returns:
        Tuple of (params_str, validations_str, assignments_str)
    """
    init_params: list[str] = []
    init_validations: list[str] = []
    init_assignments: list[str] = []

    for dep_name, dep_type in deps:
        init_params.append(f"        {dep_name}: {dep_type},")
        init_validations.append(f"        if not {dep_name}:")
        init_validations.append(f'            raise ValueError("{dep_name} required")')
        init_assignments.append(f"        self.{dep_name} = {dep_name}")

    params_str = (
        "\n".join(init_params)
        if init_params
        else "        # Add your dependencies here"
    )
    validations_str = (
        "\n".join(init_validations)
        if init_validations
        else "        # Validate dependencies"
    )
    assignments_str = (
        "\n".join(init_assignments)
        if init_assignments
        else "        # Store dependencies"
    )

    return params_str, validations_str, assignments_str


def generate_command_handler(
    handler_name: str, output_dir: Path, deps: list[tuple[str, str]]
) -> Path:
    """Generate command handler class.

    Args:
        handler_name: Name of the handler in PascalCase
        output_dir: Directory to write the file to
        deps: List of (name, type) dependency tuples

    Returns:
        Path to the generated file
    """
    snake_name = to_snake_case(handler_name)
    class_name = f"{handler_name}Handler"
    command_class = f"{handler_name}Command"

    imports_str = _build_dependency_imports(deps)
    params_str, validations_str, assignments_str = _build_init_components(deps)

    content = f'''"""Handler for {snake_name} command."""

from project_watch_mcp.application.commands.base import CommandHandler
from project_watch_mcp.application.commands.{snake_name}_command import {command_class}
from project_watch_mcp.core.monitoring import get_logger, traced
from project_watch_mcp.domain.common import ServiceResult

{imports_str}

logger = get_logger(__name__)


class {class_name}(CommandHandler[{command_class}]):
    """Handler for {command_class}.

    Orchestrates the {snake_name.replace("_", " ")} operation using domain services.
    Commands modify system state and return ServiceResult[None].
    """

    def __init__(
        self,
{params_str}
    ) -> None:
        """Initialize the handler with required services.

        Args:
            Add your dependency documentation here
        """
{validations_str}
{assignments_str}

    @traced
    async def handle(self, command: {command_class}) -> ServiceResult[None]:
        """Execute the {snake_name.replace("_", " ")} command.

        Args:
            command: The command to execute

        Returns:
            ServiceResult indicating success or failure.
            Commands always return ServiceResult[None].
        """
        try:
            logger.info(f"Executing {snake_name}: {{command}}")

            # Step 1: Validate command parameters
            validation = self._validate(command)
            if not validation.success:
                logger.warning(f"Validation failed: {{validation.error}}")
                return validation

            # Step 2: Execute business logic
            # TODO: Implement business logic here

            # Step 3: Persist changes if needed
            # TODO: Implement persistence here

            # Step 4: Return success
            logger.info("{snake_name.replace("_", " ")} completed successfully")
            return ServiceResult.ok(
                None,
                operation="{snake_name}",
            )

        except ValueError as e:
            logger.warning(f"Validation error: {{e!s}}")
            return ServiceResult.fail(f"Invalid input: {{e!s}}")

        except Exception as e:
            logger.exception(f"Unexpected error in {snake_name}: {{e!s}}")
            return ServiceResult.fail(f"System error: {{e!s}}")

    def _validate(self, command: {command_class}) -> ServiceResult[None]:
        """Validate command parameters.

        Args:
            command: The command to validate

        Returns:
            ServiceResult indicating validation success or failure
        """
        # TODO: Add validation logic
        _ = command  # Suppress unused argument warning
        return ServiceResult.ok(None)
'''

    file_path = output_dir / f"{snake_name}.py"
    file_path.write_text(content)
    return file_path


def generate_query_handler(
    handler_name: str, output_dir: Path, deps: list[tuple[str, str]], result_type: str
) -> Path:
    """Generate query handler class.

    Args:
        handler_name: Name of the handler in PascalCase
        output_dir: Directory to write the file to
        deps: List of (name, type) dependency tuples
        result_type: The result type for the query

    Returns:
        Path to the generated file
    """
    snake_name = to_snake_case(handler_name)
    class_name = f"{handler_name}Handler"
    query_class = f"{handler_name}Query"

    imports_str = _build_dependency_imports(deps)
    params_str, validations_str, assignments_str = _build_init_components(deps)

    # Determine if we need DTO import
    dto_import = ""
    if "DTO" in result_type:
        dto_name = (
            result_type.split("[")[1].rstrip("]") if "[" in result_type else result_type
        )
        dto_import = (
            f"from project_watch_mcp.application.dto."
            f"{to_snake_case(dto_name.replace('DTO', ''))} import {dto_name}"
        )

    content = f'''"""Handler for {snake_name} query."""

from project_watch_mcp.application.queries.base import QueryHandler
from project_watch_mcp.application.queries.{snake_name} import {query_class}
from project_watch_mcp.core.monitoring import get_logger, traced
from project_watch_mcp.domain.common import ServiceResult

{dto_import}
{imports_str}

logger = get_logger(__name__)


class {class_name}(QueryHandler[{query_class}, {result_type}]):
    """Handler for {query_class}.

    Retrieves data without modifying system state.
    Queries return ServiceResult[TResult] with the requested data.
    """

    def __init__(
        self,
{params_str}
    ) -> None:
        """Initialize the handler with required services.

        Args:
            Add your dependency documentation here
        """
{validations_str}
{assignments_str}

    @traced
    async def handle(self, query: {query_class}) -> ServiceResult[{result_type}]:
        """Execute the {snake_name.replace("_", " ")} query.

        Args:
            query: The query to execute

        Returns:
            ServiceResult containing the requested data or error.
            Queries return ServiceResult[TResult], not ServiceResult[None].
        """
        try:
            logger.info(f"Executing {snake_name}: {{query}}")

            # Step 1: Validate query parameters
            if not self._validate_query(query):
                return ServiceResult.fail("Invalid query parameters")

            # Step 2: Fetch data from repository
            # TODO: Implement data retrieval here

            # Step 3: Convert to DTOs
            # TODO: Implement DTO conversion here
            results: {result_type} = []  # Replace with actual results

            # Step 4: Return results
            logger.info("{snake_name.replace("_", " ")} returned {{len(results)}} results")
            return ServiceResult.ok(
                results,
                metadata={{
                    "total_results": len(results),
                }},
            )

        except ValueError as e:
            logger.warning(f"Validation error: {{e!s}}")
            return ServiceResult.fail(f"Invalid query: {{e!s}}")

        except Exception as e:
            logger.exception(f"Unexpected error in {snake_name}: {{e!s}}")
            return ServiceResult.fail(f"System error: {{e!s}}")

    def _validate_query(self, query: {query_class}) -> bool:
        """Validate query parameters.

        Args:
            query: The query to validate

        Returns:
            True if valid, False otherwise
        """
        # TODO: Add validation logic
        _ = query  # Suppress unused argument warning
        return True
'''

    file_path = output_dir / f"{snake_name}.py"
    file_path.write_text(content)
    return file_path


def generate_dto(dto_name: str, output_dir: Path) -> Path:
    """Generate DTO class.

    Args:
        dto_name: Name of the DTO class
        output_dir: Directory to write the file to

    Returns:
        Path to the generated file
    """
    snake_name = to_snake_case(dto_name.replace("DTO", ""))

    content = f'''"""Data transfer object for {snake_name}."""

from dataclasses import dataclass
from typing import Any, Self


@dataclass
class {dto_name}:
    """Data transfer object for {snake_name.replace("_", " ")}.

    Carries data from application layer to interface layer.
    Contains only data, no business logic.
    """

    # Add your fields here
    # Example:
    # id: str
    # name: str
    # value: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {{
            # Add your fields here
        }}

    @classmethod
    def from_entity(cls, entity: Any) -> Self:
        """Create DTO from domain entity.

        Args:
            entity: Domain entity to convert

        Returns:
            DTO instance populated from entity data
        """
        _ = entity  # Suppress unused argument warning
        return cls(
            # Map entity attributes to DTO fields
        )
'''

    file_path = output_dir / f"{snake_name}_dto.py"
    file_path.write_text(content)
    return file_path


def generate_test_file(
    handler_name: str,
    handler_type: Literal["command", "query"],
    output_dir: Path,
    deps: list[tuple[str, str]],
) -> Path:
    """Generate test file with constructor validation.

    Args:
        handler_name: Name of the handler in PascalCase
        handler_type: "command" or "query"
        output_dir: Directory to write the file to
        deps: List of (name, type) dependency tuples

    Returns:
        Path to the generated file
    """
    snake_name = to_snake_case(handler_name)
    class_name = f"{handler_name}Handler"
    request_class = (
        f"{handler_name}Command"
        if handler_type == "command"
        else f"{handler_name}Query"
    )

    # Build mock fixtures
    mock_fixtures: list[str] = []
    for dep_name, _ in deps:
        mock_fixtures.extend(
            [
                "@pytest.fixture",
                f"def mock_{dep_name}() -> AsyncMock:",
                f'    """Mock {dep_name} for testing."""',
                "    return AsyncMock()",
                "",
            ]
        )

    fixtures_str = "\n".join(mock_fixtures)

    # Build handler initialization
    handler_args = ", ".join([f"mock_{dep_name}" for dep_name, _ in deps])
    handler_args_list = "\n".join([f"        mock_{dep_name}," for dep_name, _ in deps])

    # Build constructor validation tests
    validation_tests: list[str] = []
    for dep_name, _ in deps:
        other_deps = [f"mock_{name}" for name, _ in deps if name != dep_name]
        other_deps_str = ", ".join(other_deps)

        validation_tests.extend(
            [
                f"    def test_constructor_validates_{dep_name}(self, {other_deps_str}) -> None:",
                f'        """Test that constructor validates {dep_name} is required."""',
                f'        with pytest.raises(ValueError, match="{dep_name} required"):',
                f"            {class_name}(",
            ]
        )
        for name, _ in deps:
            if name == dep_name:
                validation_tests.append(
                    f"                {name}=None,  # type: ignore[arg-type]"
                )
            else:
                validation_tests.append(f"                {name}=mock_{name},")
        validation_tests.extend(["            )", "", ""])

    validations_str = "\n".join(validation_tests)

    module_path = "commands" if handler_type == "command" else "queries"
    suffix = "_command" if handler_type == "command" else ""

    content = f'''"""Tests for {class_name}."""

import pytest
from unittest.mock import AsyncMock

from project_watch_mcp.application.{module_path}.{snake_name}{suffix} import {request_class}
from project_watch_mcp.application.{module_path}.{snake_name} import {class_name}


{fixtures_str}

@pytest.fixture
def handler({handler_args}) -> {class_name}:
    """Create handler instance for testing."""
    return {class_name}(
{handler_args_list}
    )


class TestConstructor:
    """Test handler constructor validation."""

{validations_str}

class TestHandle:
    """Test handler execution."""

    @pytest.mark.asyncio
    async def test_handle_success(self, handler: {class_name}) -> None:
        """Test successful handling."""
        request = {request_class}()

        result = await handler.handle(request)

        assert result.success
        # Add more assertions here

    @pytest.mark.asyncio
    async def test_handle_validation_failure(self, handler: {class_name}) -> None:
        """Test validation failure."""
        # TODO: Create invalid request
        request = {request_class}()

        result = await handler.handle(request)

        # TODO: Assert validation failure
        # assert not result.success
        # assert "validation error" in result.error.lower()
        _ = result  # Suppress unused variable warning
'''

    file_path = output_dir / f"test_{snake_name}.py"
    file_path.write_text(content)
    return file_path


def generate_container_snippet(
    handler_name: str,
    handler_type: Literal["command", "query"],
    deps: list[tuple[str, str]],
) -> str:
    """Generate container registration snippet.

    Args:
        handler_name: Name of the handler in PascalCase
        handler_type: "command" or "query"
        deps: List of (name, type) dependency tuples

    Returns:
        Container registration code snippet
    """
    snake_name = to_snake_case(handler_name)
    class_name = f"{handler_name}Handler"

    module_path = "commands" if handler_type == "command" else "queries"
    import_path = f"project_watch_mcp.application.{module_path}.{snake_name}"
    import_line = f"from {import_path} import {class_name}"

    provider_deps: list[str] = []
    for dep_name, _ in deps:
        provider_deps.append(f"        {dep_name}={dep_name},")

    provider_deps_str = (
        "\n".join(provider_deps) if provider_deps else "        # Add dependencies here"
    )

    return f"""
# Add to container.py imports:
{import_line}

# Add to Container class:
{snake_name}_handler = providers.Singleton(
    {class_name},
{provider_deps_str}
)
"""


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate CQRS handler boilerplate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate command handler
  python generate_handler.py command IndexFile --deps repository:CodeRepository service:EmbeddingService

  # Generate query handler
  python generate_handler.py query SearchCode --result "list[SearchResultDTO]" --deps repository:SearchRepository

  # Specify output directory
  python generate_handler.py command MyCommand --output src/project_watch_mcp/application/commands
        """,
    )

    parser.add_argument(
        "handler_type", choices=["command", "query"], help="Type of handler to generate"
    )
    parser.add_argument(
        "handler_name", help="Name of handler (PascalCase, e.g., IndexFile)"
    )
    parser.add_argument(
        "--deps",
        help='Dependencies in format "name:Type name2:Type2" (e.g., "repository:CodeRepository service:EmbeddingService")',
    )
    parser.add_argument(
        "--result",
        default="list[Any]",
        help="Result type for query handler (default: list[Any])",
    )
    parser.add_argument(
        "--output",
        help="Output directory (default: src/project_watch_mcp/application/commands or queries)",
    )

    args = parser.parse_args()

    # Determine output directories
    project_root = get_project_root()
    if project_root is None:
        print(
            "Error: Could not find project root (no src/ directory found)",
            file=sys.stderr,
        )
        return 1

    handler_type: Literal["command", "query"] = args.handler_type  # type: ignore[assignment]

    if args.output:
        handler_output = Path(args.output)
    else:
        module_path = "commands" if handler_type == "command" else "queries"
        handler_output = (
            project_root / "src" / "project_watch_mcp" / "application" / module_path
        )

    dto_output = project_root / "src" / "project_watch_mcp" / "application" / "dto"
    test_output = project_root / "tests" / "unit"

    # Create directories if needed
    handler_output.mkdir(parents=True, exist_ok=True)
    dto_output.mkdir(parents=True, exist_ok=True)
    test_output.mkdir(parents=True, exist_ok=True)

    # Parse dependencies
    deps = parse_dependencies(args.deps)

    print(f"Generating {handler_type} handler: {args.handler_name}")

    # Generate request object
    if handler_type == "command":
        request_path = generate_command_request(args.handler_name, handler_output)
        print(f"  Created: {request_path}")
    else:
        request_path = generate_query_request(args.handler_name, handler_output)
        print(f"  Created: {request_path}")

    # Generate handler
    if handler_type == "command":
        handler_path = generate_command_handler(args.handler_name, handler_output, deps)
    else:
        handler_path = generate_query_handler(
            args.handler_name, handler_output, deps, args.result
        )
    print(f"  Created: {handler_path}")

    # Generate DTO if needed (queries only)
    if handler_type == "query" and "DTO" in args.result:
        dto_name = (
            args.result.split("[")[1].rstrip("]") if "[" in args.result else args.result
        )
        dto_path = generate_dto(dto_name, dto_output)
        print(f"  Created: {dto_path}")

    # Generate test file
    test_path = generate_test_file(args.handler_name, handler_type, test_output, deps)
    print(f"  Created: {test_path}")

    # Generate container snippet
    container_snippet = generate_container_snippet(
        args.handler_name, handler_type, deps
    )
    snippet_file = (
        handler_output / f"{to_snake_case(args.handler_name)}_container_snippet.txt"
    )
    snippet_file.write_text(container_snippet)
    print(f"  Created: {snippet_file}")

    print("\nGeneration complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
