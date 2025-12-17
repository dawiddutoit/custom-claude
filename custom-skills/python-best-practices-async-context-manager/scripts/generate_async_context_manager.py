#!/usr/bin/env python3
"""Generate async context manager from template.

This script generates a properly structured async context manager with:
- @asynccontextmanager decorator
- Proper type hints (AsyncIterator)
- State tracking (resource = None)
- Error handling (try/finally)
- Fail-fast validation

Usage:
    python generate_async_context_manager.py \\
        --resource-name "database_session" \\
        --resource-type "AsyncSession" \\
        --config-type "Settings" \\
        --setup "session = driver.session(database=config.database_name)" \\
        --cleanup "await session.close()" \\
        --output src/my_module.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import NamedTuple


class ContextManagerConfig(NamedTuple):
    """Configuration for generating context manager."""

    manager_name: str
    resource_type: str
    config_type: str
    description: str
    setup_code: str
    cleanup_code: str
    resource_error: str = "Exception"
    include_stats: bool = False
    output_path: Path | None = None


def generate_basic_context_manager(config: ContextManagerConfig) -> str:
    """Generate basic async context manager code.

    Args:
        config: Configuration for context manager generation

    Returns:
        str: Generated Python code
    """
    setup_indented = _indent_code(config.setup_code, 2)
    cleanup_indented = _indent_code(config.cleanup_code, 4)

    return f'''from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def {config.manager_name}(
    config: {config.config_type},
) -> AsyncIterator[{config.resource_type}]:
    """{config.description}

    Args:
        config: Configuration for {config.resource_type} creation (required)

    Yields:
        {config.resource_type}: Active resource instance

    Raises:
        ValueError: If config is None
        {config.resource_error}: If resource creation fails

    Example:
        async with {config.manager_name}(config) as resource:
            # Use resource here
            pass
    """
    # Fail-fast validation
    if not config:
        raise ValueError("Config is required for {config.manager_name}")

    # Initialize state tracking
    resource = None

    try:
        # Setup phase - create and initialize resource
        {setup_indented}

        # Yield resource to caller
        yield resource

    finally:
        # Cleanup phase - always runs
        if resource:
            try:
                {cleanup_indented}
            except Exception as e:
                # Log cleanup failures but don't raise
                logger.warning(f"Cleanup failed for {config.manager_name}: {{e}}")
'''


def generate_context_manager_with_stats(config: ContextManagerConfig) -> str:
    """Generate context manager with statistics tracking.

    Args:
        config: Configuration for context manager generation

    Returns:
        str: Generated Python code with stats tracking
    """
    setup_indented = _indent_code(config.setup_code, 2)
    cleanup_indented = _indent_code(config.cleanup_code, 4)

    return f'''from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class {config.resource_type}Stats:
    """Statistics for {config.resource_type} management."""

    active_count: int = 0
    total_created: int = 0
    total_errors: int = 0
    cleanup_errors: int = 0


@asynccontextmanager
async def {config.manager_name}_with_stats(
    config: {config.config_type},
    stats: {config.resource_type}Stats,
) -> AsyncIterator[{config.resource_type}]:
    """{config.description}

    Args:
        config: Configuration for resource creation (required)
        stats: Statistics tracker (required)

    Yields:
        {config.resource_type}: Active resource instance

    Raises:
        ValueError: If config or stats is None
        {config.resource_error}: If resource creation fails
    """
    if not config:
        raise ValueError("Config is required")
    if not stats:
        raise ValueError("Stats is required")

    resource = None

    try:
        # Track resource creation
        stats.active_count += 1
        stats.total_created += 1

        # Setup phase
        {setup_indented}

        yield resource

    except Exception as e:
        # Track errors
        stats.total_errors += 1
        logger.error(f"Resource operation failed: {{e}}")
        raise

    finally:
        # Update statistics
        stats.active_count -= 1

        # Cleanup resource
        if resource:
            try:
                {cleanup_indented}
            except Exception as cleanup_error:
                stats.cleanup_errors += 1
                logger.warning(f"Cleanup failed: {{cleanup_error}}")
'''


def generate_test_code(config: ContextManagerConfig) -> str:
    """Generate pytest test code for context manager.

    Args:
        config: Configuration for context manager generation

    Returns:
        str: Generated pytest test code
    """
    return f'''import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_{config.manager_name}_cleanup_on_success():
    """Verify cleanup happens on successful completion."""
    cleanup_called = False

    @asynccontextmanager
    async def test_manager() -> AsyncIterator[{config.resource_type}]:
        nonlocal cleanup_called
        resource = None  # Replace with actual resource creation
        try:
            yield resource
        finally:
            cleanup_called = True

    async with test_manager() as resource:
        pass

    assert cleanup_called is True


@pytest.mark.asyncio
async def test_{config.manager_name}_cleanup_on_exception():
    """Verify cleanup happens even when exception occurs."""
    cleanup_called = False

    @asynccontextmanager
    async def test_manager() -> AsyncIterator[{config.resource_type}]:
        nonlocal cleanup_called
        try:
            resource = None  # Replace with actual resource creation
            yield resource
        finally:
            cleanup_called = True

    with pytest.raises(ValueError):
        async with test_manager():
            raise ValueError("Test error")

    assert cleanup_called is True


@pytest.mark.asyncio
async def test_{config.manager_name}_validates_config():
    """Verify config validation at entry."""
    with pytest.raises(ValueError, match="Config is required"):
        async with {config.manager_name}(None) as resource:
            pass


@pytest.mark.asyncio
async def test_{config.manager_name}_with_mock():
    """Test context manager with mocked resource."""
    # Create mock resource
    mock_resource = AsyncMock(spec={config.resource_type})
    mock_config = MagicMock(spec={config.config_type})

    # Test would use actual {config.manager_name}
    # This is a template - replace with actual test logic
    pass
'''


def _indent_code(code: str, levels: int) -> str:
    """Indent code by specified number of levels (4 spaces per level).

    Args:
        code: Code to indent
        levels: Number of indentation levels

    Returns:
        str: Indented code (single line if code is single expression)
    """
    # Strip the code first
    code = code.strip()

    # If it's a single line, just return it (will be placed inline)
    if "\n" not in code:
        return code

    # Multi-line code needs proper indentation
    indent = "    " * levels
    lines = code.split("\n")
    return "\n".join(indent + line if line.strip() else "" for line in lines)


def validate_python_syntax(code: str) -> bool:
    """Validate that generated code is valid Python syntax.

    Args:
        code: Python code to validate

    Returns:
        bool: True if valid syntax, False otherwise
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate async context manager from template"
    )
    parser.add_argument(
        "--resource-name",
        required=True,
        help="Name of context manager function (e.g., database_session)",
    )
    parser.add_argument(
        "--resource-type",
        required=True,
        help="Type of resource being managed (e.g., AsyncSession)",
    )
    parser.add_argument(
        "--config-type",
        required=True,
        help="Type of configuration object (e.g., Settings)",
    )
    parser.add_argument(
        "--description",
        default="Manage resource lifecycle with automatic cleanup",
        help="Description of what this context manager does",
    )
    parser.add_argument(
        "--setup",
        required=True,
        help="Setup code to create resource (e.g., 'resource = await create()')",
    )
    parser.add_argument(
        "--cleanup",
        required=True,
        help="Cleanup code (e.g., 'await resource.close()')",
    )
    parser.add_argument(
        "--resource-error",
        default="Exception",
        help="Exception type for resource errors (default: Exception)",
    )
    parser.add_argument(
        "--with-stats",
        action="store_true",
        help="Generate version with statistics tracking",
    )
    parser.add_argument(
        "--with-tests",
        action="store_true",
        help="Also generate test file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (prints to stdout if not specified)",
    )

    args = parser.parse_args()

    # Create configuration
    config = ContextManagerConfig(
        manager_name=args.resource_name,
        resource_type=args.resource_type,
        config_type=args.config_type,
        description=args.description,
        setup_code=args.setup,
        cleanup_code=args.cleanup,
        resource_error=args.resource_error,
        include_stats=args.with_stats,
        output_path=args.output,
    )

    # Generate code
    if args.with_stats:
        code = generate_context_manager_with_stats(config)
    else:
        code = generate_basic_context_manager(config)

    # Validate syntax
    if not validate_python_syntax(code):
        print("Error: Generated code has invalid syntax", file=sys.stderr)
        sys.exit(1)

    # Output code
    if args.output:
        args.output.write_text(code)
        print(f"Generated: {args.output}")

        # Generate tests if requested
        if args.with_tests:
            test_path = args.output.parent / f"test_{args.output.stem}.py"
            test_code = generate_test_code(config)
            test_path.write_text(test_code)
            print(f"Generated: {test_path}")
    else:
        # Print to stdout when no output file specified
        print(code)


if __name__ == "__main__":
    main()
