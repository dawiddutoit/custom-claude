#!/usr/bin/env python3
"""Convert synchronous context managers to async context managers.

This script automatically converts:
- @contextmanager -> @asynccontextmanager
- def -> async def
- Sync operations -> async equivalents
- Iterator -> AsyncIterator
- __enter__/__exit__ -> __aenter__/__aexit__

Usage:
    python convert_sync_to_async_cm.py src/module.py --output src/async_module.py
    python convert_sync_to_async_cm.py --find-candidates src/
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import NamedTuple, cast


class ConversionCandidate(NamedTuple):
    """Represents a context manager that could be converted."""

    file_path: Path
    line_number: int
    function_name: str
    is_decorator_form: bool  # True for @contextmanager, False for __enter__/__exit__
    conversion_complexity: str  # "simple", "moderate", "complex"


class SyncToAsyncConverter(ast.NodeTransformer):
    """AST transformer to convert sync context managers to async."""

    def __init__(self) -> None:
        """Initialize converter."""
        self.conversions_made: list[str] = []
        self.sync_operations: set[str] = {
            "open",
            "close",
            "read",
            "write",
            "connect",
            "disconnect",
            "acquire",
            "release",
            "send",
            "recv",
            "execute",
            "commit",
            "rollback",
        }

    def visit_FunctionDef(
        self, node: ast.FunctionDef
    ) -> ast.AsyncFunctionDef | ast.FunctionDef:
        """Convert sync function to async if it's a context manager.

        Args:
            node: Function definition node

        Returns:
            Converted async function or original function
        """
        # Check if this is a context manager
        is_context_manager = any(
            self._is_contextmanager_decorator(dec) for dec in node.decorator_list
        )

        if is_context_manager:
            return self._convert_to_async_function(node)

        # Visit children and return the node unchanged (generic_visit returns AST)
        self.generic_visit(node)
        return node

    def _is_contextmanager_decorator(self, node: ast.expr) -> bool:
        """Check if decorator is @contextmanager.

        Args:
            node: Decorator node

        Returns:
            bool: True if contextmanager decorator
        """
        if isinstance(node, ast.Name):
            return node.id == "contextmanager"
        if isinstance(node, ast.Attribute):
            return node.attr == "contextmanager"
        return False

    def _convert_to_async_function(self, node: ast.FunctionDef) -> ast.AsyncFunctionDef:
        """Convert function to async function.

        Args:
            node: Sync function definition

        Returns:
            Async function definition
        """
        # Create async function
        async_func = ast.AsyncFunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=self._convert_decorators(node.decorator_list),
            returns=self._convert_return_type(node.returns),
            type_comment=node.type_comment,
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Convert function body
        async_func.body = [self.visit(stmt) for stmt in node.body]

        self.conversions_made.append(f"Converted function '{node.name}' to async")

        return async_func

    def _convert_decorators(self, decorators: list[ast.expr]) -> list[ast.expr]:
        """Convert @contextmanager to @asynccontextmanager.

        Args:
            decorators: List of decorator nodes

        Returns:
            List of converted decorators
        """
        new_decorators = []

        for dec in decorators:
            if isinstance(dec, ast.Name) and dec.id == "contextmanager":
                new_decorators.append(
                    ast.Name(id="asynccontextmanager", ctx=ast.Load())
                )
                self.conversions_made.append(
                    "Converted @contextmanager to @asynccontextmanager"
                )
            elif isinstance(dec, ast.Attribute) and dec.attr == "contextmanager":
                new_dec = ast.Attribute(
                    value=dec.value, attr="asynccontextmanager", ctx=ast.Load()
                )
                new_decorators.append(new_dec)
                self.conversions_made.append(
                    "Converted @contextmanager to @asynccontextmanager"
                )
            else:
                new_decorators.append(dec)

        return new_decorators

    def _convert_return_type(self, returns: ast.expr | None) -> ast.expr | None:
        """Convert Iterator to AsyncIterator.

        Args:
            returns: Return type annotation

        Returns:
            Converted return type
        """
        if not returns:
            return None

        # Convert Iterator to AsyncIterator
        if isinstance(returns, ast.Subscript) and isinstance(returns.value, ast.Name):
            if returns.value.id == "Iterator":
                returns.value.id = "AsyncIterator"
                self.conversions_made.append("Converted Iterator to AsyncIterator")
            elif returns.value.id == "Generator":
                returns.value.id = "AsyncGenerator"
                self.conversions_made.append("Converted Generator to AsyncGenerator")

        return returns

    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        """Convert expressions, adding await where needed.

        Args:
            node: Expression node

        Returns:
            Converted expression
        """
        # Check if expression is a call to sync operation
        if isinstance(node.value, ast.Call) and self._needs_await(node.value):
            # Wrap in await
            node.value = ast.Await(value=node.value)
            self.conversions_made.append(f"Added await to {ast.unparse(node.value)}")

        self.generic_visit(node)
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        """Convert assignments, adding await where needed.

        Args:
            node: Assignment node

        Returns:
            Converted assignment
        """
        if isinstance(node.value, ast.Call) and self._needs_await(node.value):
            node.value = ast.Await(value=node.value)
            self.conversions_made.append("Added await to assignment")

        self.generic_visit(node)
        return node

    def visit_With(self, node: ast.With) -> ast.AsyncWith:
        """Convert 'with' to 'async with'.

        Args:
            node: With statement node

        Returns:
            AsyncWith node
        """
        async_with = ast.AsyncWith(
            items=node.items,
            body=node.body,
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        self.conversions_made.append("Converted 'with' to 'async with'")

        # Visit children of the new async_with node
        async_with.body = [cast(ast.stmt, self.visit(stmt)) for stmt in async_with.body]
        return async_with

    def _needs_await(self, call: ast.Call) -> bool:
        """Determine if a call needs await.

        Args:
            call: Call node

        Returns:
            bool: True if call should be awaited
        """
        if isinstance(call.func, ast.Name):
            return call.func.id in self.sync_operations
        if isinstance(call.func, ast.Attribute):
            return call.func.attr in self.sync_operations
        return False


def find_conversion_candidates(directory: Path) -> list[ConversionCandidate]:
    """Find sync context managers that could be converted.

    Args:
        directory: Directory to scan

    Returns:
        List of conversion candidates
    """
    candidates: list[ConversionCandidate] = []

    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            source = py_file.read_text()
            tree = ast.parse(source)

            for node in ast.walk(tree):
                # Check for @contextmanager decorator
                if isinstance(node, ast.FunctionDef):
                    has_contextmanager = any(
                        (isinstance(d, ast.Name) and d.id == "contextmanager")
                        or (isinstance(d, ast.Attribute) and d.attr == "contextmanager")
                        for d in node.decorator_list
                    )

                    if has_contextmanager:
                        # Determine complexity
                        complexity = _estimate_complexity(node)

                        candidates.append(
                            ConversionCandidate(
                                file_path=py_file,
                                line_number=node.lineno,
                                function_name=node.name,
                                is_decorator_form=True,
                                conversion_complexity=complexity,
                            )
                        )

        except (SyntaxError, UnicodeDecodeError):
            # Skip files with errors
            continue

    return candidates


def _estimate_complexity(node: ast.FunctionDef) -> str:
    """Estimate conversion complexity.

    Args:
        node: Function definition node

    Returns:
        str: "simple", "moderate", or "complex"
    """
    # Count operations in function
    operation_count = 0
    has_nested_context = False

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            operation_count += 1
        elif isinstance(child, ast.With):
            has_nested_context = True
        # ast.Try nodes don't affect complexity calculation

    # Simple: few operations, no nesting
    if operation_count < 5 and not has_nested_context:
        return "simple"
    # Complex: many operations or nested contexts
    if operation_count > 10 or has_nested_context:
        return "complex"
    # Moderate: everything else
    return "moderate"


def convert_file(input_path: Path, output_path: Path | None = None) -> None:
    """Convert sync context managers in file to async.

    Args:
        input_path: Source file path
        output_path: Destination path (or None for in-place)
    """
    # Read source code
    source = input_path.read_text()

    # Parse AST
    tree = ast.parse(source)

    # Convert
    converter = SyncToAsyncConverter()
    new_tree = converter.visit(tree)

    # Fix missing locations
    ast.fix_missing_locations(new_tree)

    # Generate new code
    new_code = ast.unparse(new_tree)

    # Update imports
    new_code = _update_imports(new_code)

    # Write output
    if output_path:
        output_path.write_text(new_code)
    else:
        input_path.write_text(new_code)

    # Print conversion summary
    if converter.conversions_made:
        print(f"Converted {input_path} -> {output_path or input_path}")
        for conversion in converter.conversions_made:
            print(f"  - {conversion}")


def _update_imports(code: str) -> str:
    """Update imports to async versions.

    Args:
        code: Source code

    Returns:
        Updated code with async imports
    """
    # Replace imports
    code = code.replace(
        "from contextlib import contextmanager",
        "from contextlib import asynccontextmanager",
    )
    code = code.replace(
        "from typing import Iterator", "from collections.abc import AsyncIterator"
    )
    code = code.replace("import Iterator", "from collections.abc import AsyncIterator")

    # Add AsyncIterator if Iterator was used
    if "Iterator" in code and "AsyncIterator" not in code:
        # Find first import and add AsyncIterator
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("from collections.abc import"):
                # Add AsyncIterator to existing import
                if "AsyncIterator" not in line:
                    line = line.rstrip()
                    if line.endswith(")"):
                        line = line[:-1] + ", AsyncIterator)"
                    else:
                        line = line + ", AsyncIterator"
                    lines[i] = line
                break
        else:
            # No collections.abc import found, add one
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    lines.insert(i + 1, "from collections.abc import AsyncIterator")
                    break

        code = "\n".join(lines)

    return code


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Convert sync context managers to async"
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        help="File to convert (omit to find candidates)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: overwrite input)",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Modify file in-place",
    )
    parser.add_argument(
        "--find-candidates",
        type=Path,
        help="Find conversion candidates in directory",
    )

    args = parser.parse_args()

    # Find candidates mode
    if args.find_candidates:
        candidates = find_conversion_candidates(args.find_candidates)

        if not candidates:
            print("No sync context managers found.")
            return

        # Group by complexity
        simple = [c for c in candidates if c.conversion_complexity == "simple"]
        moderate = [c for c in candidates if c.conversion_complexity == "moderate"]
        complex_candidates = [
            c for c in candidates if c.conversion_complexity == "complex"
        ]

        print(f"Found {len(candidates)} conversion candidate(s):\n")

        if simple:
            print("Simple (recommended for auto-conversion):")
            for candidate in simple:
                print(
                    f"  {candidate.file_path}:{candidate.line_number} - {candidate.function_name}"
                )

        if moderate:
            print("\nModerate (review recommended):")
            for candidate in moderate:
                print(
                    f"  {candidate.file_path}:{candidate.line_number} - {candidate.function_name}"
                )

        if complex_candidates:
            print("\nComplex (manual conversion recommended):")
            for candidate in complex_candidates:
                print(
                    f"  {candidate.file_path}:{candidate.line_number} - {candidate.function_name}"
                )

        return

    # Convert mode
    if not args.path:
        parser.error("Path required for conversion (or use --find-candidates)")

    if not args.path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    output_path = args.output if args.output else (args.path if args.in_place else None)

    if not output_path and not args.in_place:
        # Default: create new file with _async suffix
        output_path = args.path.parent / f"{args.path.stem}_async{args.path.suffix}"

    # Perform conversion
    convert_file(args.path, output_path)


if __name__ == "__main__":
    main()
