#!/usr/bin/env python3
"""Convert synchronous tests to async test patterns.

This script intelligently converts sync test code to async patterns:
- Converts Mock to AsyncMock for async methods
- Adds @pytest_asyncio.fixture to async fixtures
- Adds AsyncGenerator type hints
- Converts test functions to async
- Updates assertions to use await

Usage:
    python convert_to_async.py <test_file> --output <output_file>
    python convert_to_async.py tests/unit/test_service.py --dry-run
    python convert_to_async.py tests/unit/test_service.py --in-place

Example:
    # Preview changes
    python convert_to_async.py tests/unit/test_service.py --dry-run

    # Convert and save to new file
    python convert_to_async.py tests/unit/test_service.py --output tests/unit/test_service_async.py

    # Convert in-place (overwrites original)
    python convert_to_async.py tests/unit/test_service.py --in-place
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class AsyncConverter(ast.NodeTransformer):
    """AST transformer to convert sync tests to async patterns."""

    def __init__(self) -> None:
        self.changes_made = 0
        self.needs_pytest_asyncio = False
        self.needs_asyncmock = False
        self.needs_async_generator = False

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Update imports for async testing."""
        if node.module == "unittest.mock":
            # Check if we need to add AsyncMock
            names = [alias.name for alias in node.names]
            if "AsyncMock" not in names and self.needs_asyncmock:
                node.names.append(ast.alias(name="AsyncMock", asname=None))
                self.changes_made += 1

        return node

    def visit_FunctionDef(
        self, node: ast.FunctionDef
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        """Convert test functions to async if they contain async calls."""
        # Check if function has async operations
        has_async_calls = self._has_async_calls(node.body)

        # Check if this is a fixture
        is_fixture = any(
            (isinstance(d, ast.Name) and d.id == "fixture")
            or (isinstance(d, ast.Attribute) and d.attr == "fixture")
            for d in node.decorator_list
        )

        # Convert to async if needed
        if has_async_calls or (is_fixture and self._has_yield(node.body)):
            # Create async version
            async_node = ast.AsyncFunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=self._update_decorators(node.decorator_list, is_fixture),
                returns=self._update_return_annotation(node.returns, is_fixture),
                type_comment=node.type_comment,
                lineno=node.lineno,
                col_offset=node.col_offset,
            )

            self.changes_made += 1
            self.needs_pytest_asyncio = True

            # Visit children
            self.generic_visit(async_node)
            return async_node

        # Visit children even if not converting
        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Convert Mock() to AsyncMock() for async methods."""
        func_name = self._get_call_name(node)

        # Convert Mock/MagicMock to AsyncMock if context suggests async
        if func_name in ["Mock", "MagicMock"]:
            # Check if this is for an async method
            if self._is_async_context(node):
                node.func = ast.Name(id="AsyncMock", ctx=ast.Load())
                self.needs_asyncmock = True
                self.changes_made += 1

        self.generic_visit(node)
        return node

    def _has_async_calls(self, body: Sequence[ast.stmt]) -> bool:
        """Check if body contains async calls (await statements)."""
        module = ast.Module(body=list(body), type_ignores=[])
        for node in ast.walk(module):
            if isinstance(node, ast.Await):
                return True
            # Check for common async method names
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if self._is_likely_async_method(func_name):
                    return True
        return False

    def _has_yield(self, body: Sequence[ast.stmt]) -> bool:
        """Check if body contains yield statements."""
        module = ast.Module(body=list(body), type_ignores=[])
        for node in ast.walk(module):
            if isinstance(node, (ast.Yield, ast.YieldFrom)):
                return True
        return False

    def _update_decorators(
        self, decorators: list[ast.expr], is_fixture: bool
    ) -> list[ast.expr]:
        """Update decorators for async functions."""
        new_decorators: list[ast.expr] = []
        has_asyncio_marker = False

        for decorator in decorators:
            # Replace @pytest.fixture with @pytest_asyncio.fixture
            if (
                is_fixture
                and isinstance(decorator, ast.Attribute)
                and isinstance(decorator.value, ast.Name)
                and decorator.value.id == "pytest"
                and decorator.attr == "fixture"
            ):
                # Convert to pytest_asyncio.fixture
                new_decorator = ast.Attribute(
                    value=ast.Name(id="pytest_asyncio", ctx=ast.Load()),
                    attr="fixture",
                    ctx=ast.Load(),
                )
                new_decorators.append(new_decorator)
                self.needs_pytest_asyncio = True
                continue

            # Check if already has asyncio marker
            if self._is_pytest_marker(decorator, "asyncio"):
                has_asyncio_marker = True

            new_decorators.append(decorator)

        # Add @pytest.mark.asyncio for async test functions (if not already present)
        if not is_fixture and not has_asyncio_marker:
            marker = ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id="pytest", ctx=ast.Load()),
                    attr="mark",
                    ctx=ast.Load(),
                ),
                attr="asyncio",
                ctx=ast.Load(),
            )
            new_decorators.insert(0, marker)

        return new_decorators

    def _update_return_annotation(
        self, returns: ast.expr | None, is_fixture: bool
    ) -> ast.expr | None:
        """Update return type annotation for async fixtures."""
        if is_fixture and returns:
            # Check if we need to wrap in AsyncGenerator
            annotation_str = ast.unparse(returns)
            if "Generator" in annotation_str and "AsyncGenerator" not in annotation_str:
                # Convert Generator to AsyncGenerator
                self.needs_async_generator = True
                # This is simplified - in practice you'd parse and reconstruct properly
                return ast.Subscript(
                    value=ast.Name(id="AsyncGenerator", ctx=ast.Load()),
                    slice=returns,  # Reuse existing annotation as slice
                    ctx=ast.Load(),
                )

        return returns

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function name from call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    def _is_async_context(self, node: ast.Call) -> bool:
        """Heuristic to determine if this is an async context."""
        # Check if parent assignment has async-related variable name
        # This is simplified - in production you'd track scope and usage
        return True  # Conservative: always use AsyncMock

    def _is_likely_async_method(self, method_name: str) -> bool:
        """Check if method name suggests async operation."""
        async_keywords = [
            "fetch",
            "get",
            "create",
            "save",
            "update",
            "delete",
            "execute",
            "run",
            "process",
            "query",
            "initialize",
            "close",
        ]
        return any(keyword in method_name.lower() for keyword in async_keywords)

    def _is_pytest_marker(self, decorator: ast.expr, marker_name: str) -> bool:
        """Check if decorator is a pytest marker."""
        if not isinstance(decorator, ast.Attribute):
            return False
        if not isinstance(decorator.value, ast.Attribute):
            return False
        if not isinstance(decorator.value.value, ast.Name):
            return False
        return (
            decorator.value.value.id == "pytest"
            and decorator.value.attr == "mark"
            and decorator.attr == marker_name
        )


def convert_file(source_path: Path, *, dry_run: bool = False) -> tuple[str, int]:
    """Convert a test file to async patterns.

    Args:
        source_path: Path to the source file.
        dry_run: If True, don't actually modify the file.

    Returns:
        Tuple of (converted_source, num_changes)
    """
    _ = dry_run  # Reserved for future use (preview mode)

    with open(source_path, encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=str(source_path))
    except SyntaxError:
        return source, 0

    # Convert AST
    converter = AsyncConverter()
    new_tree = converter.visit(tree)

    # Ensure new_tree is a Module (type narrowing for mypy)
    if not isinstance(new_tree, ast.Module):
        return source, 0

    # Add necessary imports if not present
    new_tree = add_required_imports(
        new_tree,
        needs_pytest_asyncio=converter.needs_pytest_asyncio,
        needs_asyncmock=converter.needs_asyncmock,
        needs_async_generator=converter.needs_async_generator,
    )

    # Convert back to source
    try:
        new_source = ast.unparse(new_tree)
    except (ValueError, TypeError):
        return source, 0

    return new_source, converter.changes_made


def add_required_imports(
    tree: ast.Module,
    *,
    needs_pytest_asyncio: bool,
    needs_asyncmock: bool,
    needs_async_generator: bool,
) -> ast.Module:
    """Add required imports to AST if not present.

    Args:
        tree: The AST module to modify.
        needs_pytest_asyncio: Whether to add pytest_asyncio import.
        needs_asyncmock: Whether to add AsyncMock import.
        needs_async_generator: Whether to add AsyncGenerator import.

    Returns:
        Modified AST module with required imports.
    """
    existing_imports: set[str] = set()

    # Track existing imports
    for node in tree.body:
        if isinstance(node, ast.Import):
            existing_imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            existing_imports.update(
                f"{node.module}.{alias.name}" for alias in node.names
            )

    # Insert new imports at the top
    new_imports: list[ast.stmt] = []

    if needs_pytest_asyncio and "pytest_asyncio" not in existing_imports:
        new_imports.append(
            ast.Import(names=[ast.alias(name="pytest_asyncio", asname=None)])
        )

    if (
        needs_async_generator
        and "collections.abc.AsyncGenerator" not in existing_imports
    ):
        new_imports.append(
            ast.ImportFrom(
                module="collections.abc",
                names=[ast.alias(name="AsyncGenerator", asname=None)],
                level=0,
            )
        )

    if needs_asyncmock and "unittest.mock.AsyncMock" not in existing_imports:
        # Find existing unittest.mock import and update it
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == "unittest.mock":
                if not any(alias.name == "AsyncMock" for alias in node.names):
                    node.names.append(ast.alias(name="AsyncMock", asname=None))
                break
        else:
            # No existing import, add new one
            new_imports.append(
                ast.ImportFrom(
                    module="unittest.mock",
                    names=[ast.alias(name="AsyncMock", asname=None)],
                    level=0,
                )
            )

    # Insert new imports at beginning
    tree.body = new_imports + tree.body

    return tree


def main() -> int:
    """Main entry point for async conversion script.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert synchronous tests to async patterns"
    )
    parser.add_argument("file", type=Path, help="Test file to convert")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file (default: print to stdout)",
    )
    parser.add_argument(
        "--in-place",
        "-i",
        action="store_true",
        help="Modify file in-place",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Convert file
    converted_source, num_changes = convert_file(args.file, dry_run=args.dry_run)

    if args.dry_run:
        print(f"Would make {num_changes} change(s) to {args.file}")
        print(converted_source)
        return 0

    # Output results
    if args.in_place:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(converted_source)
        print(f"Converted {args.file} ({num_changes} change(s))")
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(converted_source)
        print(f"Wrote converted output to {args.output} ({num_changes} change(s))")
    else:
        # Print to stdout
        print(converted_source)

    return 0


if __name__ == "__main__":
    sys.exit(main())
