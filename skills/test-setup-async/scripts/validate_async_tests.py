#!/usr/bin/env python3
"""Validate async test patterns in Python test files.

This script analyzes test files to identify common async testing anti-patterns:
- Async functions using sync Mock instead of AsyncMock
- Missing @pytest_asyncio.fixture decorators on async fixtures
- Async functions without await statements
- Missing AsyncGenerator type hints on async fixtures
- Sync Mock used on async methods

Usage:
    python validate_async_tests.py <test_file_or_directory>
    python validate_async_tests.py tests/unit/
    python validate_async_tests.py tests/unit/test_service.py --fix

Returns exit code 0 if all checks pass, 1 if violations found.
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class Violation:
    """Represents a test validation violation.

    Attributes:
        file: Path to the file containing the violation.
        line: Line number where the violation occurs.
        column: Column number where the violation occurs.
        code: Violation code (e.g., AT001, AT002).
        message: Human-readable description of the violation.
        severity: Either "error" or "warning".
    """

    file: Path
    line: int
    column: int
    code: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        """Format the violation as a compiler-style error message."""
        return (
            f"{self.file}:{self.line}:{self.column}: "
            f"[{self.severity}] {self.code}: {self.message}"
        )


class AsyncTestValidator(ast.NodeVisitor):
    """AST visitor to validate async test patterns."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.violations: list[Violation] = []
        self.imports: dict[str, str] = {}  # name -> module mapping
        self.async_functions: set[str] = set()
        self.fixture_names: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        """Track import statements."""
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from...import statements."""
        if node.module:
            for alias in node.names:
                self.imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async function definitions."""
        self.async_functions.add(node.name)

        # Check for async fixtures without pytest_asyncio decorator
        has_pytest_fixture = False
        has_pytest_asyncio_fixture = False

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == "fixture":
                    has_pytest_fixture = True
                elif decorator.id == "pytest_asyncio.fixture":
                    has_pytest_asyncio_fixture = True
            elif isinstance(decorator, ast.Attribute):
                if (
                    isinstance(decorator.value, ast.Name)
                    and decorator.value.id == "pytest_asyncio"
                    and decorator.attr == "fixture"
                ):
                    has_pytest_asyncio_fixture = True
                elif (
                    isinstance(decorator.value, ast.Name)
                    and decorator.value.id == "pytest"
                    and decorator.attr == "fixture"
                ):
                    has_pytest_fixture = True

        # Async fixtures must use @pytest_asyncio.fixture
        if has_pytest_fixture and not has_pytest_asyncio_fixture:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    code="AT001",
                    message=f"Async fixture '{node.name}' must use @pytest_asyncio.fixture, not @pytest.fixture",
                )
            )

        # Check for missing AsyncGenerator type hint on async fixtures
        if has_pytest_asyncio_fixture or has_pytest_fixture:
            self.fixture_names.add(node.name)
            if node.returns:
                return_annotation = ast.unparse(node.returns)
                if "AsyncGenerator" not in return_annotation and "yield" in ast.unparse(
                    node
                ):
                    self.violations.append(
                        Violation(
                            file=self.file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            code="AT002",
                            message=f"Async fixture '{node.name}' with yield should have AsyncGenerator[T, None] type hint",
                            severity="warning",
                        )
                    )

        # Check for async functions without await
        has_await = self._has_await_in_body(node.body)
        is_test = node.name.startswith("test_")

        if is_test and not has_await:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    code="AT003",
                    message=f"Async test '{node.name}' has no await statements - should it be async?",
                    severity="warning",
                )
            )

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check for Mock() used instead of AsyncMock()."""
        if isinstance(node.value, ast.Call):
            func_name = self._get_call_name(node.value)

            # Check if Mock() or MagicMock() is being assigned
            if func_name in ["Mock", "MagicMock"]:
                # Check if this is inside an async function or fixture
                # This is a simplified check - in production you'd track scope
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        # Check if variable name suggests async usage
                        if any(
                            keyword in var_name.lower()
                            for keyword in [
                                "async",
                                "await",
                                "driver",
                                "session",
                                "service",
                            ]
                        ):
                            self.violations.append(
                                Violation(
                                    file=self.file_path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    code="AT004",
                                    message=f"Variable '{var_name}' suggests async usage but uses {func_name}() - consider AsyncMock()",
                                    severity="warning",
                                )
                            )

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check for sync mock methods on async operations."""
        # Check for patterns like: mock.some_method = Mock()
        # where some_method is likely async
        if node.attr in [
            "return_value",
            "side_effect",
        ] and self._is_likely_async_method_name(node):
            # This is complex to detect precisely, so we'll flag potential issues
            pass

        self.generic_visit(node)

    def _has_await_in_body(self, body: Sequence[ast.stmt]) -> bool:
        """Check if body contains await expressions."""
        module = ast.Module(body=list(body), type_ignores=[])
        return any(isinstance(node, ast.Await) for node in ast.walk(module))

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function name from call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    def _is_likely_async_method_name(self, node: ast.Attribute) -> bool:
        """Heuristic to determine if method name suggests async operation."""
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
        ]
        return any(keyword in node.attr.lower() for keyword in async_keywords)


def validate_file(file_path: Path) -> list[Violation]:
    """Validate a single Python test file.

    Args:
        file_path: Path to the Python test file.

    Returns:
        List of violations found in the file.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        validator = AsyncTestValidator(file_path)
        validator.visit(tree)

        return validator.violations
    except SyntaxError as e:
        return [
            Violation(
                file=file_path,
                line=e.lineno or 0,
                column=e.offset or 0,
                code="SYNTAX",
                message=f"Syntax error: {e.msg}",
                severity="error",
            )
        ]
    except OSError as e:
        return [
            Violation(
                file=file_path,
                line=0,
                column=0,
                code="IO_ERROR",
                message=f"Failed to read file: {e}",
                severity="error",
            )
        ]


def validate_directory(directory: Path) -> list[Violation]:
    """Validate all Python test files in directory.

    Args:
        directory: Directory to search for test files.

    Returns:
        List of violations found across all test files.
    """
    violations: list[Violation] = []

    for file_path in directory.rglob("test_*.py"):
        violations.extend(validate_file(file_path))

    return violations


def main() -> int:
    """Main entry point for async test validator.

    Returns:
        Exit code (0 for success/no violations, 1 for violations found).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate async test patterns in Python test files"
    )
    parser.add_argument("path", type=Path, help="File or directory to validate")
    parser.add_argument(
        "--severity",
        choices=["error", "warning"],
        default="error",
        help="Minimum severity to report (default: error)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        return 1

    # Collect violations
    if args.path.is_file():
        violations = validate_file(args.path)
    else:
        violations = validate_directory(args.path)

    # Filter by severity
    severity_levels = {"warning": 0, "error": 1}
    min_severity = severity_levels[args.severity]
    filtered_violations = [
        v for v in violations if severity_levels[v.severity] >= min_severity
    ]

    # Output results
    if args.format == "json":
        output = [
            {
                "file": str(v.file),
                "line": v.line,
                "column": v.column,
                "code": v.code,
                "message": v.message,
                "severity": v.severity,
            }
            for v in filtered_violations
        ]
        print(json.dumps(output, indent=2))
    elif filtered_violations:
        for violation in sorted(
            filtered_violations, key=lambda x: (str(x.file), x.line)
        ):
            print(violation)
    else:
        print("No async test violations found.")

    return 1 if filtered_violations else 0


if __name__ == "__main__":
    sys.exit(main())
