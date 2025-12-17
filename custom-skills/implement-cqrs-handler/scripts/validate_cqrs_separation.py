#!/usr/bin/env python3
"""Validate CQRS pattern separation in handlers.

This script enforces CQRS patterns by scanning handlers for violations:
- Commands MUST return ServiceResult[None]
- Queries MUST return ServiceResult[TResult] (not None)
- Commands should not read and return data
- Queries should not modify state

Usage:
    python validate_cqrs_separation.py
    python validate_cqrs_separation.py --verbose
    python validate_cqrs_separation.py --path src/project_watch_mcp/application/commands
    python validate_cqrs_separation.py --json

Dependencies:
    - No external dependencies required (stdlib only)
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Setup: Add .claude to path for skill_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skill_utils import get_project_root


@dataclass
class Violation:
    """CQRS pattern violation."""

    severity: Literal["error", "warning"]
    file_path: Path
    line_number: int
    rule: str
    message: str
    suggestion: str | None = None


class CQRSVisitor(ast.NodeVisitor):
    """AST visitor to detect CQRS violations."""

    def __init__(
        self, file_path: Path, handler_type: Literal["command", "query"]
    ) -> None:
        """Initialize visitor.

        Args:
            file_path: Path to file being analyzed
            handler_type: "command" or "query"
        """
        self.file_path = file_path
        self.handler_type = handler_type
        self.violations: list[Violation] = []
        self.current_class: str | None = None
        self.current_method: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        self.current_class = node.name

        # Check if it's a handler
        is_command_handler = any(
            (isinstance(base, ast.Name) and "CommandHandler" in base.id)
            or (
                isinstance(base, ast.Subscript)
                and isinstance(base.value, ast.Name)
                and "CommandHandler" in base.value.id
            )
            for base in node.bases
        )
        is_query_handler = any(
            (isinstance(base, ast.Name) and "QueryHandler" in base.id)
            or (
                isinstance(base, ast.Subscript)
                and isinstance(base.value, ast.Name)
                and "QueryHandler" in base.value.id
            )
            for base in node.bases
        )

        if is_command_handler:
            self._check_command_handler(node)
        elif is_query_handler:
            self._check_query_handler(node)

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        self.current_method = node.name

        if node.name == "handle":
            self._check_handle_method(node)

        self.generic_visit(node)
        self.current_method = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self.current_method = node.name
        # Async handle methods are fine, no warning needed
        self.generic_visit(node)
        self.current_method = None

    def _check_command_handler(self, node: ast.ClassDef) -> None:
        """Check command handler follows patterns."""
        # Find handle method
        handle_method: ast.FunctionDef | ast.AsyncFunctionDef | None = None
        for item in node.body:
            if (
                isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name == "handle"
            ):
                handle_method = item
                break

        if not handle_method:
            self.violations.append(
                Violation(
                    severity="error",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule="CQRS-001",
                    message=f"Command handler '{node.name}' missing handle() method",
                    suggestion="Add async def handle(self, command: TCommand) -> ServiceResult[None]",
                )
            )
            return

        # Check return type annotation
        if handle_method.returns:
            return_annotation = ast.unparse(handle_method.returns)
            if "ServiceResult[None]" not in return_annotation:
                self.violations.append(
                    Violation(
                        severity="error",
                        file_path=self.file_path,
                        line_number=handle_method.lineno,
                        rule="CQRS-002",
                        message=f"Command handler must return ServiceResult[None], got: {return_annotation}",
                        suggestion="Change return type to ServiceResult[None]",
                    )
                )

    def _check_query_handler(self, node: ast.ClassDef) -> None:
        """Check query handler follows patterns."""
        # Find handle method
        handle_method: ast.FunctionDef | ast.AsyncFunctionDef | None = None
        for item in node.body:
            if (
                isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name == "handle"
            ):
                handle_method = item
                break

        if not handle_method:
            self.violations.append(
                Violation(
                    severity="error",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule="CQRS-003",
                    message=f"Query handler '{node.name}' missing handle() method",
                    suggestion="Add async def handle(self, query: TQuery) -> ServiceResult[TResult]",
                )
            )
            return

        # Check return type annotation
        if handle_method.returns:
            return_annotation = ast.unparse(handle_method.returns)
            if "ServiceResult[None]" in return_annotation:
                self.violations.append(
                    Violation(
                        severity="error",
                        file_path=self.file_path,
                        line_number=handle_method.lineno,
                        rule="CQRS-004",
                        message="Query handler cannot return ServiceResult[None] - queries must return data",
                        suggestion="Change return type to ServiceResult[TResult] where TResult is your data type",
                    )
                )

    def _check_handle_method(self, node: ast.FunctionDef) -> None:
        """Check handle() method implementation."""
        # Check if it's async (only for non-async FunctionDef)
        if not isinstance(node, ast.AsyncFunctionDef):
            self.violations.append(
                Violation(
                    severity="warning",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    rule="CQRS-005",
                    message="handle() should be async for I/O operations",
                    suggestion="Change 'def handle' to 'async def handle'",
                )
            )

        # Check for state-modifying operations in queries
        if self.handler_type == "query":
            state_modifiers = self._find_state_modifiers(node)
            for lineno, operation in state_modifiers:
                self.violations.append(
                    Violation(
                        severity="warning",
                        file_path=self.file_path,
                        line_number=lineno,
                        rule="CQRS-006",
                        message=f"Query handler should not modify state: {operation}",
                        suggestion="Queries should only read data, not modify it",
                    )
                )

    def _find_state_modifiers(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[tuple[int, str]]:
        """Find potential state-modifying operations in method.

        Args:
            node: Function node to analyze

        Returns:
            List of (line_number, operation) tuples
        """
        modifiers: list[tuple[int, str]] = []

        for child in ast.walk(node):
            # Look for .save(), .delete(), .update(), .create() calls
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                method_name = child.func.attr
                if method_name in [
                    "save",
                    "delete",
                    "update",
                    "create",
                    "insert",
                    "remove",
                ]:
                    modifiers.append((child.lineno, f".{method_name}()"))

        return modifiers


def find_handler_files(search_path: Path) -> dict[str, list[Path]]:
    """Find all handler files.

    Args:
        search_path: Directory to search

    Returns:
        Dict with 'commands' and 'queries' keys containing file paths
    """
    handlers: dict[str, list[Path]] = {"commands": [], "queries": []}

    # Find command handlers
    commands_dir = search_path / "application" / "commands"
    if commands_dir.exists():
        for file_path in commands_dir.glob("*.py"):
            if file_path.name not in ["__init__.py", "base.py"]:
                handlers["commands"].append(file_path)

    # Find query handlers
    queries_dir = search_path / "application" / "queries"
    if queries_dir.exists():
        for file_path in queries_dir.glob("*.py"):
            if file_path.name not in ["__init__.py", "base.py"]:
                handlers["queries"].append(file_path)

    return handlers


def analyze_handler(
    file_path: Path, handler_type: Literal["command", "query"]
) -> list[Violation]:
    """Analyze a handler file for CQRS violations.

    Args:
        file_path: Path to handler file
        handler_type: "command" or "query"

    Returns:
        List of violations found
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source, filename=str(file_path))

        visitor = CQRSVisitor(file_path, handler_type)
        visitor.visit(tree)

        return visitor.violations
    except SyntaxError as e:
        return [
            Violation(
                severity="error",
                file_path=file_path,
                line_number=e.lineno or 0,
                rule="SYNTAX",
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax error before validating CQRS patterns",
            )
        ]
    except OSError as e:
        return [
            Violation(
                severity="error",
                file_path=file_path,
                line_number=0,
                rule="IO",
                message=f"Failed to read file: {e!s}",
                suggestion="Check file permissions",
            )
        ]


def print_violations(
    violations: list[Violation], *, show_suggestions: bool = True
) -> None:
    """Print violations in a formatted way.

    Args:
        violations: List of violations to print
        show_suggestions: Whether to show fix suggestions
    """
    if not violations:
        return

    # Group by severity
    errors = [v for v in violations if v.severity == "error"]
    warnings = [v for v in violations if v.severity == "warning"]

    if errors:
        print("\nErrors:")
        for v in errors:
            print(f"  [{v.rule}] {v.file_path}:{v.line_number}")
            print(f"    {v.message}")
            if show_suggestions and v.suggestion:
                print(f"    Suggestion: {v.suggestion}")

    if warnings:
        print("\nWarnings:")
        for v in warnings:
            print(f"  [{v.rule}] {v.file_path}:{v.line_number}")
            print(f"    {v.message}")
            if show_suggestions and v.suggestion:
                print(f"    Suggestion: {v.suggestion}")


def print_summary(all_violations: dict[str, list[Violation]]) -> None:
    """Print summary of all violations.

    Args:
        all_violations: Dict mapping file paths to violations
    """
    total_errors = sum(
        1
        for violations in all_violations.values()
        for v in violations
        if v.severity == "error"
    )
    total_warnings = sum(
        1
        for violations in all_violations.values()
        for v in violations
        if v.severity == "warning"
    )

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    print(f"Files with violations: {len(all_violations)}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")

    if total_errors == 0 and total_warnings == 0:
        print("\nAll handlers follow CQRS patterns!")
    elif total_errors == 0:
        print("\nNo errors found, but there are warnings to review.")
    else:
        print(f"\nFound {total_errors} error(s) that must be fixed.")


def print_json_output(
    all_violations: dict[str, list[Violation]],
    total_files: int,
) -> None:
    """Print violations in JSON format.

    Args:
        all_violations: Dict mapping file paths to violations
        total_files: Total number of files analyzed
    """
    output = {
        "total_files": total_files,
        "files_with_violations": len(all_violations),
        "violations": [
            {
                "file": str(v.file_path),
                "line": v.line_number,
                "severity": v.severity,
                "rule": v.rule,
                "message": v.message,
                "suggestion": v.suggestion,
            }
            for violations in all_violations.values()
            for v in violations
        ],
        "summary": {
            "total_errors": sum(
                1
                for violations in all_violations.values()
                for v in violations
                if v.severity == "error"
            ),
            "total_warnings": sum(
                1
                for violations in all_violations.values()
                for v in violations
                if v.severity == "warning"
            ),
        },
    }
    print(json.dumps(output, indent=2))


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for errors found)
    """
    parser = argparse.ArgumentParser(
        description="Validate CQRS pattern separation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all handlers
  python validate_cqrs_separation.py

  # Validate specific directory
  python validate_cqrs_separation.py --path src/project_watch_mcp/application/commands

  # Show detailed suggestions
  python validate_cqrs_separation.py --verbose

  # Output as JSON
  python validate_cqrs_separation.py --json
        """,
    )

    parser.add_argument(
        "--path",
        help="Path to analyze (default: auto-detect from current directory)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed suggestions for fixes",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Find project root
    if args.path:
        search_path = Path(args.path)
    else:
        project_root = get_project_root()
        if project_root is None:
            print(
                "Error: Could not find project root (no src/ directory found)",
                file=sys.stderr,
            )
            return 1
        search_path = project_root / "src" / "project_watch_mcp"

    if not search_path.exists():
        print(f"Error: Search path does not exist: {search_path}", file=sys.stderr)
        return 1

    if not args.json:
        print(f"Validating CQRS patterns in: {search_path}")

    # Find all handler files
    handlers = find_handler_files(search_path)

    total_files = len(handlers["commands"]) + len(handlers["queries"])

    if total_files == 0:
        if args.json:
            print_json_output({}, 0)
        else:
            print("No handler files found.", file=sys.stderr)
        return 1

    if not args.json:
        print(
            f"Found {len(handlers['commands'])} command handlers and {len(handlers['queries'])} query handlers"
        )

    # Analyze each handler
    all_violations: dict[str, list[Violation]] = {}

    for file_path in handlers["commands"]:
        violations = analyze_handler(file_path, "command")
        if violations:
            all_violations[str(file_path)] = violations

    for file_path in handlers["queries"]:
        violations = analyze_handler(file_path, "query")
        if violations:
            all_violations[str(file_path)] = violations

    # Output results
    if args.json:
        print_json_output(all_violations, total_files)
    else:
        # Print violations per file
        for file_path, violations in all_violations.items():
            print(f"\n{file_path}:")
            print_violations(violations, show_suggestions=args.verbose)

        # Print summary
        print_summary(all_violations)

    # Return exit code based on errors
    has_errors = any(
        v.severity == "error"
        for violations in all_violations.values()
        for v in violations
    )
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
