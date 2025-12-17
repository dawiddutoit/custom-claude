#!/usr/bin/env python3
"""Validate repository pattern compliance across the codebase.

This script enforces repository patterns using AST analysis:
- Protocol definitions in domain/repositories/ layer
- Implementations in infrastructure/neo4j/ layer
- All methods return ServiceResult
- No direct driver usage (must use _execute_with_retry)
- Proper ManagedResource implementation
- Constructor parameter validation

Usage:
    python validate_repository_patterns.py                    # Validate all
    python validate_repository_patterns.py --file path.py     # Validate specific file
    python validate_repository_patterns.py --fix              # Auto-fix violations
"""

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# Note: This script is designed to be run standalone with no external dependencies
# beyond Python's standard library.


@dataclass
class Violation:
    """Represents a pattern violation."""

    file: Path
    line: int
    column: int
    severity: str  # ERROR, WARNING
    rule: str
    message: str

    def __str__(self) -> str:
        """Format violation for display."""
        return f"{self.file}:{self.line}:{self.column}: {self.severity}: {self.rule}: {self.message}"


class RepositoryPatternValidator(ast.NodeVisitor):
    """AST visitor to validate repository patterns."""

    def __init__(self, file_path: Path) -> None:
        """Initialize validator.

        Args:
            file_path: Path to file being validated
        """
        self.file_path = file_path
        self.violations: list[Violation] = []
        self.is_protocol = "domain/repositories" in str(file_path)
        self.is_implementation = "infrastructure/neo4j" in str(file_path)
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        self.current_class = node.name

        # Check if this is a repository class
        if node.name.endswith("Repository"):
            self._validate_repository_class(node)

        self.generic_visit(node)
        self.current_class = None

    def _validate_repository_class(self, node: ast.ClassDef) -> None:
        """Validate repository class definition.

        Args:
            node: Class AST node
        """
        if self.is_protocol:
            self._validate_protocol_class(node)
        elif self.is_implementation:
            self._validate_implementation_class(node)

    def _validate_protocol_class(self, node: ast.ClassDef) -> None:
        """Validate protocol (ABC) class.

        Args:
            node: Class AST node
        """
        # Check ABC inheritance
        has_abc = any(
            isinstance(base, ast.Name) and base.id == "ABC" for base in node.bases
        )
        if not has_abc:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="PROTO001",
                    message=f"Protocol {node.name} must inherit from ABC",
                )
            )

        # Check methods
        for item in node.body:
            if isinstance(item, ast.AsyncFunctionDef):
                self._validate_protocol_method(item)

    def _validate_protocol_method(self, node: ast.AsyncFunctionDef) -> None:
        """Validate protocol method.

        Args:
            node: Method AST node
        """
        # Check @abstractmethod decorator
        has_abstract = any(
            isinstance(d, ast.Name) and d.id == "abstractmethod"
            for d in node.decorator_list
        )
        if not has_abstract:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="PROTO002",
                    message=f"Protocol method {node.name} must have @abstractmethod decorator",
                )
            )

        # Check return type is ServiceResult
        if node.returns:
            return_annotation = ast.unparse(node.returns)
            if "ServiceResult" not in return_annotation:
                self.violations.append(
                    Violation(
                        file=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        severity="ERROR",
                        rule="PROTO003",
                        message=f"Protocol method {node.name} must return ServiceResult[T], got {return_annotation}",
                    )
                )

        # Check body is just 'pass'
        if len(node.body) != 1 or not isinstance(node.body[0], ast.Pass):
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="WARNING",
                    rule="PROTO004",
                    message=f"Protocol method {node.name} should only contain 'pass'",
                )
            )

    def _validate_implementation_class(self, node: ast.ClassDef) -> None:
        """Validate implementation class.

        Args:
            node: Class AST node
        """
        # Check protocol and ManagedResource inheritance
        base_names = [
            b.id if isinstance(b, ast.Name) else ast.unparse(b) for b in node.bases
        ]

        has_protocol = any("Repository" in name for name in base_names)
        has_managed = "ManagedResource" in base_names

        if not has_protocol:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="IMPL001",
                    message=f"{node.name} must implement a Repository protocol",
                )
            )

        if not has_managed:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="IMPL002",
                    message=f"{node.name} must inherit from ManagedResource",
                )
            )

        # Check __init__ method
        init_method = next(
            (
                item
                for item in node.body
                if isinstance(item, ast.FunctionDef) and item.name == "__init__"
            ),
            None,
        )
        if init_method:
            self._validate_init_method(init_method)

        # Check for close() method
        has_close = any(
            isinstance(item, ast.AsyncFunctionDef) and item.name == "close"
            for item in node.body
        )
        if not has_close:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="IMPL003",
                    message=f"{node.name} must implement async close() method (ManagedResource)",
                )
            )

        # Check for _execute_with_retry method
        has_execute = any(
            isinstance(item, ast.AsyncFunctionDef)
            and item.name == "_execute_with_retry"
            for item in node.body
        )
        if not has_execute:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="WARNING",
                    rule="IMPL004",
                    message=f"{node.name} should implement _execute_with_retry() for query execution",
                )
            )

        # Check methods
        for item in node.body:
            if isinstance(item, ast.AsyncFunctionDef) and not item.name.startswith("_"):
                self._validate_implementation_method(item)

    def _validate_init_method(self, node: ast.FunctionDef) -> None:
        """Validate __init__ method.

        Args:
            node: Method AST node
        """
        # Check required parameters: driver and settings
        param_names = [arg.arg for arg in node.args.args if arg.arg != "self"]

        if "driver" not in param_names:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="IMPL005",
                    message="__init__ must have 'driver: AsyncDriver' parameter",
                )
            )

        if "settings" not in param_names:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="IMPL006",
                    message="__init__ must have 'settings: Settings' parameter",
                )
            )

        # Check for parameter validation
        has_driver_check = False
        has_settings_check = False

        for stmt in node.body:
            if isinstance(stmt, ast.If):
                condition = ast.unparse(stmt.test)
                if "not driver" in condition or "driver is None" in condition:
                    has_driver_check = True
                if "not settings" in condition or "settings is None" in condition:
                    has_settings_check = True

        if not has_driver_check:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="IMPL007",
                    message="__init__ must validate driver is not None (fail-fast)",
                )
            )

        if not has_settings_check:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity="ERROR",
                    rule="IMPL008",
                    message="__init__ must validate settings is not None (fail-fast)",
                )
            )

    def _validate_implementation_method(self, node: ast.AsyncFunctionDef) -> None:
        """Validate implementation method.

        Args:
            node: Method AST node
        """
        # Check return type is ServiceResult
        if node.returns:
            return_annotation = ast.unparse(node.returns)
            if "ServiceResult" not in return_annotation:
                self.violations.append(
                    Violation(
                        file=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        severity="ERROR",
                        rule="IMPL009",
                        message=f"Method {node.name} must return ServiceResult[T], got {return_annotation}",
                    )
                )

        # Check for direct driver usage (should use _execute_with_retry)
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Attribute):
                if stmt.attr in ["execute_query", "execute_write", "execute_read"]:
                    # Check if it's self.driver.execute_*
                    if (
                        isinstance(stmt.value, ast.Attribute)
                        and stmt.value.attr == "driver"
                    ):
                        self.violations.append(
                            Violation(
                                file=self.file_path,
                                line=getattr(stmt, "lineno", node.lineno),
                                column=getattr(stmt, "col_offset", node.col_offset),
                                severity="WARNING",
                                rule="IMPL010",
                                message=f"Method {node.name} should use _execute_with_retry() instead of direct driver calls",
                            )
                        )


def validate_file(file_path: Path) -> list[Violation]:
    """Validate a single file.

    Args:
        file_path: Path to Python file

    Returns:
        List of violations found
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source, filename=str(file_path))

        validator = RepositoryPatternValidator(file_path)
        validator.visit(tree)

        return validator.violations
    except SyntaxError as e:
        return [
            Violation(
                file=file_path,
                line=e.lineno or 0,
                column=e.offset or 0,
                severity="ERROR",
                rule="SYNTAX",
                message=f"Syntax error: {e.msg}",
            )
        ]
    except Exception as e:
        return [
            Violation(
                file=file_path,
                line=0,
                column=0,
                severity="ERROR",
                rule="INTERNAL",
                message=f"Internal error: {e!s}",
            )
        ]


def find_repository_files(base_dir: Path) -> list[Path]:
    """Find all repository files.

    Args:
        base_dir: Base directory to search

    Returns:
        List of repository file paths
    """
    files = []

    # Domain repositories (protocols)
    domain_repos = base_dir / "domain" / "repositories"
    if domain_repos.exists():
        files.extend(domain_repos.glob("*_repository.py"))

    # Infrastructure repositories (implementations)
    infra_repos = base_dir / "infrastructure" / "neo4j"
    if infra_repos.exists():
        files.extend(infra_repos.glob("*_repository.py"))

    return files


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate repository pattern compliance"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Validate specific file",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("src/project_watch_mcp"),
        help="Base directory (default: src/project_watch_mcp)",
    )
    parser.add_argument(
        "--severity",
        choices=["ERROR", "WARNING"],
        default="WARNING",
        help="Minimum severity to report (default: WARNING)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix violations (not implemented yet)",
    )

    args = parser.parse_args()

    if args.fix:
        print("Auto-fix is not implemented yet.", file=sys.stderr)
        return 1

    # Find files to validate
    files = [args.file] if args.file else find_repository_files(args.base_dir)

    if not files:
        return 0

    # Validate files
    all_violations: list[Violation] = []
    for file_path in files:
        violations = validate_file(file_path)
        all_violations.extend(violations)

    # Filter by severity
    filtered_violations = [
        v for v in all_violations if v.severity == "ERROR" or args.severity == "WARNING"
    ]

    # Report violations
    if not filtered_violations:
        print(f"All {len(files)} repository files pass validation.")
        return 0

    print("\n=== Repository Pattern Violations ===\n")

    # Group by file
    by_file: dict[Path, list[Violation]] = {}
    for v in filtered_violations:
        by_file.setdefault(v.file, []).append(v)

    for file_path, violations in sorted(by_file.items()):
        print(f"{file_path}:")
        for v in sorted(violations, key=lambda x: (x.line, x.column)):
            print(f"  {v}")

    # Summary
    errors = sum(1 for v in filtered_violations if v.severity == "ERROR")
    warnings = sum(1 for v in filtered_violations if v.severity == "WARNING")

    print(f"\nSummary: {errors} errors, {warnings} warnings in {len(by_file)} files")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
