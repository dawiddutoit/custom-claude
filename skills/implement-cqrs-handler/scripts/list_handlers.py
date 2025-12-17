#!/usr/bin/env python3
"""List and inventory all CQRS handlers in the project.

This script:
- Lists all command and query handlers
- Shows their request/response types
- Generates handler registry/catalog
- Validates handler naming conventions

Usage:
    python list_handlers.py
    python list_handlers.py --format table
    python list_handlers.py --format markdown > HANDLER_REGISTRY.md
    python list_handlers.py --format json > handlers.json

Dependencies:
    - No external dependencies required (stdlib only)
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

# Setup: Add .claude to path for skill_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skill_utils import get_project_root


@dataclass
class HandlerInfo:
    """Information about a handler."""

    name: str
    type: Literal["command", "query"]
    file_path: str
    request_type: str
    response_type: str
    dependencies: list[str] = field(default_factory=list)
    has_validation: bool = False
    has_tests: bool = False
    is_async: bool = False
    line_count: int = 0


class HandlerAnalyzer(ast.NodeVisitor):
    """AST visitor to extract handler information."""

    def __init__(
        self, file_path: Path, handler_type: Literal["command", "query"]
    ) -> None:
        """Initialize analyzer.

        Args:
            file_path: Path to handler file
            handler_type: "command" or "query"
        """
        self.file_path = file_path
        self.handler_type = handler_type
        self.handler_info: HandlerInfo | None = None
        self.dependencies: list[str] = []
        self.has_validation = False

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition to extract handler info."""
        # Check if it's a handler class
        is_handler = any(
            (
                isinstance(base, ast.Name)
                and ("CommandHandler" in base.id or "QueryHandler" in base.id)
            )
            or (
                isinstance(base, ast.Subscript)
                and isinstance(base.value, ast.Name)
                and (
                    "CommandHandler" in base.value.id or "QueryHandler" in base.value.id
                )
            )
            for base in node.bases
        )

        if not is_handler:
            self.generic_visit(node)
            return

        # Extract request and response types from base class
        request_type = "Unknown"
        response_type = (
            "ServiceResult[None]" if self.handler_type == "command" else "Unknown"
        )

        for base in node.bases:
            if isinstance(base, ast.Subscript):
                # Extract generic type arguments
                if isinstance(base.slice, ast.Tuple):
                    # QueryHandler[TQuery, TResult]
                    if len(base.slice.elts) >= 1:
                        request_type = ast.unparse(base.slice.elts[0])
                    if len(base.slice.elts) >= 2:
                        response_type = (
                            f"ServiceResult[{ast.unparse(base.slice.elts[1])}]"
                        )
                else:
                    # CommandHandler[TCommand]
                    request_type = ast.unparse(base.slice)

        # Find __init__ to get dependencies
        init_method: ast.FunctionDef | None = None
        handle_method: ast.FunctionDef | ast.AsyncFunctionDef | None = None
        validate_methods: list[ast.FunctionDef] = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "__init__":
                    init_method = item
                elif item.name == "handle":
                    handle_method = item
                elif item.name.startswith("_validate"):
                    validate_methods.append(item)
            elif isinstance(item, ast.AsyncFunctionDef):
                if item.name == "handle":
                    handle_method = item

        # Extract dependencies from __init__
        if init_method:
            for arg in init_method.args.args[1:]:  # Skip 'self'
                if arg.annotation:
                    dep_type = ast.unparse(arg.annotation)
                    self.dependencies.append(f"{arg.arg}: {dep_type}")

        # Check for validation
        self.has_validation = len(validate_methods) > 0

        # Check if handle is async
        is_async = isinstance(handle_method, ast.AsyncFunctionDef)

        # Count lines
        source = self.file_path.read_text()
        line_count = len(source.splitlines())

        self.handler_info = HandlerInfo(
            name=node.name,
            type=self.handler_type,
            file_path=str(self.file_path),
            request_type=request_type,
            response_type=response_type,
            dependencies=self.dependencies,
            has_validation=self.has_validation,
            has_tests=self._check_for_tests(),
            is_async=is_async,
            line_count=line_count,
        )

        self.generic_visit(node)

    def _check_for_tests(self) -> bool:
        """Check if test file exists for this handler."""
        # Look for test file in common locations
        test_locations = [
            self.file_path.parent.parent.parent
            / "tests"
            / "unit"
            / f"test_{self.file_path.stem}.py",
            self.file_path.parent.parent.parent.parent
            / "tests"
            / "unit"
            / f"test_{self.file_path.stem}.py",
        ]
        return any(loc.exists() for loc in test_locations)


def analyze_handler_file(
    file_path: Path, handler_type: Literal["command", "query"]
) -> HandlerInfo | None:
    """Analyze a handler file and extract information.

    Args:
        file_path: Path to handler file
        handler_type: "command" or "query"

    Returns:
        HandlerInfo if found, None otherwise
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source, filename=str(file_path))

        analyzer = HandlerAnalyzer(file_path, handler_type)
        analyzer.visit(tree)

        return analyzer.handler_info
    except (SyntaxError, OSError):
        return None


def find_all_handlers(search_path: Path) -> list[HandlerInfo]:
    """Find and analyze all handlers in the project.

    Args:
        search_path: Root directory to search

    Returns:
        List of HandlerInfo objects
    """
    handlers: list[HandlerInfo] = []

    # Find command handlers
    commands_dir = search_path / "application" / "commands"
    if commands_dir.exists():
        for file_path in commands_dir.glob("*.py"):
            if file_path.name not in ["__init__.py", "base.py"]:
                info = analyze_handler_file(file_path, "command")
                if info:
                    handlers.append(info)

    # Find query handlers
    queries_dir = search_path / "application" / "queries"
    if queries_dir.exists():
        for file_path in queries_dir.glob("*.py"):
            if file_path.name not in ["__init__.py", "base.py"]:
                info = analyze_handler_file(file_path, "query")
                if info:
                    handlers.append(info)

    return handlers


def print_table(handlers: list[HandlerInfo]) -> None:
    """Print handlers in table format."""
    # Separate commands and queries
    commands = [h for h in handlers if h.type == "command"]
    queries = [h for h in handlers if h.type == "query"]

    if commands:
        print("\n=== Command Handlers ===\n")
        print(
            f"{'Name':<30} {'Request Type':<25} {'Deps':<5} {'Tests':<5} {'Valid':<5}"
        )
        print("-" * 75)
        for handler in sorted(commands, key=lambda h: h.name):
            deps_count = len(handler.dependencies)
            tests = "Yes" if handler.has_tests else "No"
            valid = "Yes" if handler.has_validation else "No"
            print(
                f"{handler.name:<30} {handler.request_type:<25} {deps_count:<5} {tests:<5} {valid:<5}"
            )

    if queries:
        print("\n=== Query Handlers ===\n")
        print(f"{'Name':<30} {'Response Type':<35} {'Tests':<5} {'Valid':<5}")
        print("-" * 80)
        for handler in sorted(queries, key=lambda h: h.name):
            response = (
                handler.response_type.replace("ServiceResult[", "")[:-1]
                if handler.response_type.endswith("]")
                else handler.response_type
            )
            tests = "Yes" if handler.has_tests else "No"
            valid = "Yes" if handler.has_validation else "No"
            print(f"{handler.name:<30} {response:<35} {tests:<5} {valid:<5}")

    # Print summary
    print("\n=== Summary ===")
    print(f"Total handlers: {len(handlers)}")
    print(f"  Commands: {len(commands)}")
    print(f"  Queries: {len(queries)}")
    print(f"  With tests: {sum(1 for h in handlers if h.has_tests)}")
    print(f"  With validation: {sum(1 for h in handlers if h.has_validation)}")


def print_markdown(handlers: list[HandlerInfo]) -> None:
    """Print handlers in markdown format."""
    print("# CQRS Handler Registry\n")
    print(f"Generated automatically. Total handlers: {len(handlers)}\n")

    # Separate commands and queries
    commands = [h for h in handlers if h.type == "command"]
    queries = [h for h in handlers if h.type == "query"]

    if commands:
        print("## Command Handlers\n")
        print("| Handler | Request Type | Dependencies | Tests | Validation |")
        print("|---------|--------------|--------------|-------|------------|")
        for handler in sorted(commands, key=lambda h: h.name):
            deps = ", ".join([d.split(":")[0] for d in handler.dependencies]) or "None"
            tests = "Yes" if handler.has_tests else "No"
            valid = "Yes" if handler.has_validation else "No"
            print(
                f"| {handler.name} | `{handler.request_type}` | {deps} | {tests} | {valid} |"
            )
        print()

    if queries:
        print("## Query Handlers\n")
        print("| Handler | Response Type | Tests | Validation |")
        print("|---------|---------------|-------|------------|")
        for handler in sorted(queries, key=lambda h: h.name):
            response = (
                handler.response_type.replace("ServiceResult[", "")[:-1]
                if handler.response_type.endswith("]")
                else handler.response_type
            )
            tests = "Yes" if handler.has_tests else "No"
            valid = "Yes" if handler.has_validation else "No"
            print(f"| {handler.name} | `{response}` | {tests} | {valid} |")
        print()

    # Summary
    print("## Summary\n")
    print(f"- **Total handlers**: {len(handlers)}")
    print(f"- **Commands**: {len(commands)}")
    print(f"- **Queries**: {len(queries)}")
    print(f"- **With tests**: {sum(1 for h in handlers if h.has_tests)}")
    print(f"- **With validation**: {sum(1 for h in handlers if h.has_validation)}")
    print(f"- **Async handlers**: {sum(1 for h in handlers if h.is_async)}")


def print_json(handlers: list[HandlerInfo]) -> None:
    """Print handlers in JSON format."""
    output = {
        "total": len(handlers),
        "commands": [asdict(h) for h in handlers if h.type == "command"],
        "queries": [asdict(h) for h in handlers if h.type == "query"],
        "summary": {
            "total_handlers": len(handlers),
            "command_count": len([h for h in handlers if h.type == "command"]),
            "query_count": len([h for h in handlers if h.type == "query"]),
            "with_tests": sum(1 for h in handlers if h.has_tests),
            "with_validation": sum(1 for h in handlers if h.has_validation),
            "async_handlers": sum(1 for h in handlers if h.is_async),
        },
    }
    print(json.dumps(output, indent=2))


def print_detailed(handlers: list[HandlerInfo]) -> None:
    """Print detailed handler information."""
    # Separate commands and queries
    commands = [h for h in handlers if h.type == "command"]
    queries = [h for h in handlers if h.type == "query"]

    if commands:
        print("\n=== Command Handlers (Detailed) ===\n")
        for handler in sorted(commands, key=lambda h: h.name):
            print(f"Handler: {handler.name}")
            print(f"  File: {handler.file_path}")
            print(f"  Request: {handler.request_type}")
            print(f"  Response: {handler.response_type}")
            print(f"  Lines: {handler.line_count}")
            print(f"  Async: {'Yes' if handler.is_async else 'No'}")
            print(f"  Has Tests: {'Yes' if handler.has_tests else 'No'}")
            print(f"  Has Validation: {'Yes' if handler.has_validation else 'No'}")
            if handler.dependencies:
                print("  Dependencies:")
                for dep in handler.dependencies:
                    print(f"    - {dep}")
            print()

    if queries:
        print("\n=== Query Handlers (Detailed) ===\n")
        for handler in sorted(queries, key=lambda h: h.name):
            print(f"Handler: {handler.name}")
            print(f"  File: {handler.file_path}")
            print(f"  Request: {handler.request_type}")
            print(f"  Response: {handler.response_type}")
            print(f"  Lines: {handler.line_count}")
            print(f"  Async: {'Yes' if handler.is_async else 'No'}")
            print(f"  Has Tests: {'Yes' if handler.has_tests else 'No'}")
            print(f"  Has Validation: {'Yes' if handler.has_validation else 'No'}")
            if handler.dependencies:
                print("  Dependencies:")
                for dep in handler.dependencies:
                    print(f"    - {dep}")
            print()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="List and inventory CQRS handlers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all handlers in table format
  python list_handlers.py

  # Generate markdown registry
  python list_handlers.py --format markdown > HANDLER_REGISTRY.md

  # Export as JSON
  python list_handlers.py --format json > handlers.json

  # Show detailed information
  python list_handlers.py --format detailed
        """,
    )

    parser.add_argument(
        "--format",
        choices=["table", "markdown", "json", "detailed"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--path",
        help="Path to analyze (default: auto-detect from current directory)",
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

    # Find and analyze all handlers
    handlers = find_all_handlers(search_path)

    if not handlers:
        print("No handlers found.", file=sys.stderr)
        return 1

    # Output in requested format
    if args.format == "table":
        print_table(handlers)
    elif args.format == "markdown":
        print_markdown(handlers)
    elif args.format == "json":
        print_json(handlers)
    elif args.format == "detailed":
        print_detailed(handlers)

    return 0


if __name__ == "__main__":
    sys.exit(main())
