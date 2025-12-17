#!/usr/bin/env python3
"""Auto-generate pytest fixtures with proper decorators and type hints.

This script generates pytest fixtures following project-watch-mcp patterns:
- Factory fixtures for customization
- Async fixtures for async code
- Proper type hints and docstrings
- Cleanup code when needed
- Writes to appropriate conftest.py or utils files

Usage:
    # Basic fixture
    python generate_fixture.py --name mock_service --type basic --scope function

    # Factory fixture
    python generate_fixture.py --name mock_settings --type factory --scope function

    # Async fixture with cleanup
    python generate_fixture.py --name neo4j_driver --type async --scope function --cleanup

    # Generate in specific file
    python generate_fixture.py --name mock_repository --type basic --output tests/utils/mock_repositories.py

Examples:
    # Generate basic mock fixture
    python generate_fixture.py --name mock_embedding_service --type basic

    # Generate factory fixture with attributes
    python generate_fixture.py --name mock_settings --type factory --attributes project_name,database_name,chunk_size

    # Generate async fixture with cleanup
    python generate_fixture.py --name real_neo4j_driver --type async --cleanup --scope session

    # Generate to specific utils file
    python generate_fixture.py --name mock_repository --type basic --output tests/utils/mock_repositories.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Literal

# Setup: Add .claude/tools to path for shared utilities
_CLAUDE_ROOT = Path(__file__).parent.parent.parent.parent
if str(_CLAUDE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CLAUDE_ROOT))

from tools.skill_utils import ensure_path_setup  # noqa: E402

ensure_path_setup()

# Type aliases
FixtureType = Literal["basic", "factory", "async", "service_result"]
ScopeType = Literal["function", "module", "session"]


class FixtureGenerator:
    """Generate pytest fixtures following project patterns."""

    BASIC_TEMPLATE = '''
@pytest.fixture{scope}
def {name}(){type_hint}:
    """Create mock {component} for testing.

    Returns:
        MagicMock: Mock {component} with common attributes
    """
    mock = MagicMock()
{attributes}
    return mock
'''

    FACTORY_TEMPLATE = '''
@pytest.fixture{scope}
def {name}(){type_hint}:
    """Factory for custom {component}.

    Returns:
        callable: Function that creates {component} with custom attributes

    Example:
        def test_something({name}):
            instance = {name}({example_usage})
    """
    def create_{component}(**kwargs):
        """Create {component} with custom attributes.

        Args:
            **kwargs: Attributes to customize

        Returns:
            MagicMock: Custom {component}
        """
        instance = MagicMock()
{factory_attributes}
        return instance

    return create_{component}
'''

    ASYNC_TEMPLATE = '''
@pytest_asyncio.fixture{scope}
async def {name}(){type_hint}:
    """Create async {component} for testing.

    Yields:
        {return_type}: Async {component} instance
    """
    # Setup
    resource = {setup_code}
{init_code}
    yield resource
{cleanup_code}
'''

    SERVICE_RESULT_TEMPLATE = '''
@pytest.fixture{scope}
def {name}(){type_hint}:
    """Factory for ServiceResult mocks with success/failure states.

    Returns:
        callable: Function that creates ServiceResult instances

    Example:
        success = {name}(success=True, data="result")
        failure = {name}(success=False, error="error msg")
    """
    def create_result(success=True, data=None, error=None):
        """Create ServiceResult mock with specified state.

        Args:
            success: Whether operation succeeds
            data: Data for successful result
            error: Error message for failure

        Returns:
            MagicMock: Mock ServiceResult
        """
        result = MagicMock()
        result.is_success = success
        result.is_failure = not success

        if success:
            result.data = data
            result.unwrap = MagicMock(return_value=data)
            result.error = None
        else:
            result.data = None
            result.error = error or "Operation failed"
            result.unwrap = MagicMock(side_effect=ValueError(result.error))

        return result

    return create_result
'''

    def __init__(self) -> None:
        """Initialize fixture generator."""
        self.project_root = self._find_project_root()

    @staticmethod
    def _find_project_root() -> Path:
        """Find project root by looking for pyproject.toml.

        Returns:
            Path to project root directory.
        """
        from tools.skill_utils import get_project_root

        return get_project_root()

    def generate_basic_fixture(
        self,
        name: str,
        scope: ScopeType = "function",
        attributes: list[str] | None = None,
    ) -> str:
        """Generate basic fixture code.

        Args:
            name: Fixture name (e.g., 'mock_settings')
            scope: Fixture scope (function, module, session)
            attributes: List of attribute names to configure

        Returns:
            str: Generated fixture code
        """
        # Extract component name from fixture name
        component = name.replace("mock_", "").replace("_", " ")

        # Build scope decorator
        scope_str = f'(scope="{scope}")' if scope != "function" else ""

        # Build attributes
        if attributes:
            attrs_code = "\n".join(
                f"    mock.{attr} = None  # TODO: Set default value"
                for attr in attributes
            )
        else:
            attrs_code = "    # TODO: Add attributes"

        # Build type hint
        type_hint = " -> MagicMock"

        return self.BASIC_TEMPLATE.format(
            name=name,
            component=component,
            scope=scope_str,
            attributes=attrs_code,
            type_hint=type_hint,
        ).strip()

    def generate_factory_fixture(
        self,
        name: str,
        scope: ScopeType = "function",
        attributes: list[str] | None = None,
    ) -> str:
        """Generate factory fixture code.

        Args:
            name: Fixture name (e.g., 'mock_settings_factory')
            scope: Fixture scope
            attributes: List of attribute names

        Returns:
            str: Generated fixture code
        """
        # Extract component name
        component = name.replace("mock_", "").replace("_factory", "").replace("_", " ")
        component_snake = component.replace(" ", "_")

        # Build scope decorator
        scope_str = f'(scope="{scope}")' if scope != "function" else ""

        # Build factory attributes
        if attributes:
            factory_attrs = []
            example_params = []
            for attr in attributes:
                factory_attrs.append(
                    f'        instance.{attr} = kwargs.get("{attr}", None)  # TODO: Set default'
                )
                example_params.append(f'{attr}="value"')

            factory_attrs_code = "\n".join(factory_attrs)
            example_usage = ", ".join(example_params)
        else:
            factory_attrs_code = "        # TODO: Add attributes with defaults"
            example_usage = "attribute='value'"

        return self.FACTORY_TEMPLATE.format(
            name=name,
            component=component_snake,
            scope=scope_str,
            factory_attributes=factory_attrs_code,
            example_usage=example_usage,
            type_hint=" -> callable",
        ).strip()

    def generate_async_fixture(
        self,
        name: str,
        scope: ScopeType = "function",
        cleanup: bool = False,
        return_type: str = "AsyncDriver",
    ) -> str:
        """Generate async fixture code.

        Args:
            name: Fixture name
            scope: Fixture scope
            cleanup: Whether to add cleanup code
            return_type: Type hint for returned resource

        Returns:
            str: Generated fixture code
        """
        component = name.replace("real_", "").replace("mock_", "").replace("_", " ")

        scope_str = f'(scope="{scope}")' if scope != "function" else ""

        setup_code = "await create_resource()  # TODO: Implement setup"
        init_code = ""
        cleanup_code = ""

        if cleanup:
            cleanup_code = "\n    # Cleanup\n    await resource.close()"

        type_hint = f" -> AsyncGenerator[{return_type}, None]"

        return self.ASYNC_TEMPLATE.format(
            name=name,
            component=component,
            scope=scope_str,
            setup_code=setup_code,
            init_code=init_code,
            cleanup_code=cleanup_code,
            return_type=return_type,
            type_hint=type_hint,
        ).strip()

    def generate_service_result_fixture(
        self,
        name: str = "mock_service_result",
        scope: ScopeType = "function",
    ) -> str:
        """Generate ServiceResult fixture code.

        Args:
            name: Fixture name
            scope: Fixture scope

        Returns:
            str: Generated fixture code
        """
        scope_str = f'(scope="{scope}")' if scope != "function" else ""
        return self.SERVICE_RESULT_TEMPLATE.format(
            name=name,
            scope=scope_str,
            type_hint=" -> callable",
        ).strip()

    def add_imports_to_file(self, file_path: Path, fixture_type: FixtureType) -> None:
        """Add necessary imports to fixture file.

        Args:
            file_path: Path to fixture file
            fixture_type: Type of fixture being added
        """
        if not file_path.exists():
            # Create new file with header
            header = '''"""Reusable mock fixtures for test components.

This module provides centralized mock fixtures that can be used across all tests.
"""

from unittest.mock import MagicMock
import pytest
'''
            if fixture_type == "async":
                header += "\nimport pytest_asyncio\nfrom collections.abc import AsyncGenerator\n"

            file_path.write_text(header + "\n")
            return

        # Read existing file
        content = file_path.read_text()
        tree = ast.parse(content)

        # Check if imports exist
        has_pytest = False
        has_magicmock = False
        has_pytest_asyncio = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "pytest":
                        has_pytest = True
            elif isinstance(node, ast.ImportFrom):
                if node.module == "unittest.mock" and any(
                    alias.name == "MagicMock" for alias in node.names
                ):
                    has_magicmock = True
                if node.module == "pytest_asyncio":
                    has_pytest_asyncio = True

        # Add missing imports
        imports_to_add = []
        if not has_pytest:
            imports_to_add.append("import pytest")
        if not has_magicmock:
            imports_to_add.append("from unittest.mock import MagicMock")
        if fixture_type == "async" and not has_pytest_asyncio:
            imports_to_add.append("import pytest_asyncio")
            imports_to_add.append("from collections.abc import AsyncGenerator")

        if imports_to_add:
            # Find where to insert imports (after module docstring)
            lines = content.split("\n")
            insert_pos = 0

            # Skip module docstring
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Find end of docstring
                    if line.count('"""') >= 2 or line.count("'''") >= 2:
                        insert_pos = i + 1
                        break
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            insert_pos = j + 1
                            break
                    break

            # Insert imports
            lines.insert(insert_pos, "\n".join(imports_to_add) + "\n")
            file_path.write_text("\n".join(lines))

    def write_fixture(
        self, code: str, output_path: Path, fixture_type: FixtureType
    ) -> None:
        """Write fixture code to file.

        Args:
            code: Generated fixture code
            output_path: Path to write fixture to
            fixture_type: Type of fixture
        """
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Add imports if needed
        self.add_imports_to_file(output_path, fixture_type)

        # Append fixture code
        with output_path.open("a") as f:
            f.write("\n\n")
            f.write(code)
            f.write("\n")

    def generate(
        self,
        name: str,
        fixture_type: FixtureType,
        scope: ScopeType = "function",
        attributes: list[str] | None = None,
        cleanup: bool = False,
        output: str | None = None,
        return_type: str = "AsyncDriver",
    ) -> str:
        """Generate fixture code.

        Args:
            name: Fixture name
            fixture_type: Type of fixture (basic, factory, async, service_result)
            scope: Fixture scope
            attributes: List of attributes
            cleanup: Add cleanup code
            output: Output file path
            return_type: Return type for async fixtures

        Returns:
            str: Generated fixture code
        """
        # Generate code based on type
        if fixture_type == "basic":
            code = self.generate_basic_fixture(name, scope, attributes)
        elif fixture_type == "factory":
            code = self.generate_factory_fixture(name, scope, attributes)
        elif fixture_type == "async":
            code = self.generate_async_fixture(name, scope, cleanup, return_type)
        elif fixture_type == "service_result":
            code = self.generate_service_result_fixture(name, scope)
        else:
            msg = f"Unknown fixture type: {fixture_type}"
            raise ValueError(msg)

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            # Default to tests/utils/mock_{component}.py
            component = name.replace("mock_", "").replace("_factory", "").split("_")[0]
            output_path = (
                self.project_root / "tests" / "utils" / f"mock_{component}s.py"
            )

        # Write fixture
        self.write_fixture(code, output_path, fixture_type)

        return code


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate pytest fixtures following project patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--name", required=True, help="Fixture name (e.g., mock_settings)"
    )
    parser.add_argument(
        "--type",
        choices=["basic", "factory", "async", "service_result"],
        default="basic",
        help="Fixture type",
    )
    parser.add_argument(
        "--scope",
        choices=["function", "module", "session"],
        default="function",
        help="Fixture scope",
    )
    parser.add_argument(
        "--attributes",
        help="Comma-separated list of attributes (e.g., project_name,database_name)",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Add cleanup code (for async fixtures)"
    )
    parser.add_argument(
        "--output", help="Output file path (default: tests/utils/mock_{component}s.py)"
    )
    parser.add_argument(
        "--return-type",
        default="AsyncDriver",
        help="Return type for async fixtures",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print code without writing file"
    )

    args = parser.parse_args()

    # Parse attributes
    attributes = None
    if args.attributes:
        attributes = [attr.strip() for attr in args.attributes.split(",")]

    # Generate fixture
    generator = FixtureGenerator()
    generator.generate(
        name=args.name,
        fixture_type=args.type,
        scope=args.scope,
        attributes=attributes,
        cleanup=args.cleanup,
        output=args.output,
        return_type=args.return_type,
    )

    if args.dry_run:
        # Generate code but don't write
        if args.type == "basic":
            code = generator.generate_basic_fixture(args.name, args.scope, attributes)
        elif args.type == "factory":
            code = generator.generate_factory_fixture(args.name, args.scope, attributes)
        elif args.type == "async":
            code = generator.generate_async_fixture(
                args.name, args.scope, args.cleanup, args.return_type
            )
        elif args.type == "service_result":
            code = generator.generate_service_result_fixture(args.name, args.scope)
        else:
            msg = f"Unknown fixture type: {args.type}"
            raise ValueError(msg)
        print("\n=== Generated Fixture Code (dry-run) ===\n")
        print(code)
    else:
        output_path = Path(args.output) if args.output else None
        if output_path:
            print(f"Fixture written to: {output_path}")
        else:
            component = (
                args.name.replace("mock_", "").replace("_factory", "").split("_")[0]
            )
            default_path = (
                generator.project_root / "tests" / "utils" / f"mock_{component}s.py"
            )
            print(f"Fixture written to: {default_path}")


if __name__ == "__main__":
    main()
