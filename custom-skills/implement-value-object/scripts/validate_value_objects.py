#!/usr/bin/env python3
"""Validate value object patterns in the codebase.

This script scans for value objects and checks compliance with patterns:
- frozen=True for immutability
- Validation in __post_init__
- No mutable defaults
- No direct field assignment (should use object.__setattr__)
- Complete type hints

Usage:
    python validate_value_objects.py
    python validate_value_objects.py --path src/project_watch_mcp/domain/value_objects
    python validate_value_objects.py --fix  # Auto-fix simple issues
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# Setup: Add .claude to path for skill_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skill_utils import ensure_path_setup, get_project_root

ensure_path_setup()


@dataclass(frozen=True)
class ValidationIssue:
    """Represents a validation issue found in a value object."""

    file: Path
    line: int
    severity: str  # "error", "warning", "info"
    category: str
    message: str
    fix_suggestion: str | None = None


class ValueObjectValidator(ast.NodeVisitor):
    """AST visitor to validate value object patterns."""

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        self.issues: list[ValidationIssue] = []
        self.current_class: str | None = None
        self.current_class_lineno: int = 0
        self.is_frozen: bool = False
        self.has_post_init: bool = False
        self.fields: list[tuple[str, ast.expr | None]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition to check if it's a value object.

        Args:
            node: AST class definition node.
        """
        self.current_class = node.name
        self.current_class_lineno = node.lineno
        self.is_frozen = False
        self.has_post_init = False
        self.fields = []

        # Check for @dataclass decorator
        has_dataclass = False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                has_dataclass = True
                self._add_issue(
                    line=node.lineno,
                    severity="error",
                    category="missing_frozen",
                    message=f"Class {node.name} uses @dataclass without frozen=True",
                    fix_suggestion="Use @dataclass(frozen=True) for value objects",
                )

            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                    has_dataclass = True
                    self._check_frozen_keyword(decorator, node)

        # Check class body
        if has_dataclass:
            self.generic_visit(node)

            # Check if __post_init__ exists
            if not self.has_post_init:
                self._add_issue(
                    line=node.lineno,
                    severity="warning",
                    category="missing_validation",
                    message=f"Value object {node.name} missing __post_init__ validation",
                    fix_suggestion="Add __post_init__ method with validation logic",
                )

        self.current_class = None

    def _check_frozen_keyword(self, decorator: ast.Call, node: ast.ClassDef) -> None:
        """Check if frozen=True is set on a dataclass decorator.

        Args:
            decorator: The @dataclass(...) call node.
            node: The class definition node.
        """
        for keyword in decorator.keywords:
            if keyword.arg == "frozen":
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    self.is_frozen = True
                    return
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is False:
                    self._add_issue(
                        line=node.lineno,
                        severity="error",
                        category="not_frozen",
                        message=f"Value object {node.name} has frozen=False",
                        fix_suggestion="Set frozen=True for immutability",
                    )
                    return

        # No frozen keyword found
        self._add_issue(
            line=node.lineno,
            severity="error",
            category="missing_frozen",
            message=f"Value object {node.name} missing frozen=True",
            fix_suggestion="Add frozen=True to @dataclass decorator",
        )

    def _add_issue(
        self,
        line: int,
        severity: str,
        category: str,
        message: str,
        fix_suggestion: str | None = None,
    ) -> None:
        """Add a validation issue to the issues list.

        Args:
            line: Line number of the issue.
            severity: Issue severity (error, warning, info).
            category: Issue category for grouping.
            message: Human-readable issue description.
            fix_suggestion: Optional suggestion for fixing the issue.
        """
        self.issues.append(
            ValidationIssue(
                file=self.filepath,
                line=line,
                severity=severity,
                category=category,
                message=message,
                fix_suggestion=fix_suggestion,
            )
        )

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignment (field definition).

        Args:
            node: AST annotated assignment node.
        """
        if self.current_class and isinstance(node.target, ast.Name):
            field_name = node.target.id

            # Check for type annotation
            if node.annotation is None:
                self._add_issue(
                    line=node.lineno,
                    severity="error",
                    category="missing_type_hint",
                    message=f"Field {field_name} missing type annotation",
                    fix_suggestion="Add type annotation to all fields",
                )

            # Check for mutable defaults
            if node.value and isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                self._add_issue(
                    line=node.lineno,
                    severity="error",
                    category="mutable_default",
                    message=f"Field {field_name} has mutable default value",
                    fix_suggestion="Use field(default_factory=...) for mutable defaults",
                )

            self.fields.append((field_name, node.annotation))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition.

        Args:
            node: AST function definition node.
        """
        if self.current_class and node.name == "__post_init__":
            self._check_post_init(node)

        # Check for type hints on methods
        if self.current_class and node.name not in ("__init__", "__post_init__"):
            if node.returns is None:
                self._add_issue(
                    line=node.lineno,
                    severity="warning",
                    category="missing_return_type",
                    message=f"Method {node.name} missing return type annotation",
                    fix_suggestion="Add return type annotation to all methods",
                )

        self.generic_visit(node)

    def _check_post_init(self, node: ast.FunctionDef) -> None:
        """Check __post_init__ method for validation logic.

        Args:
            node: AST function definition node for __post_init__.
        """
        self.has_post_init = True

        # Check for validation logic
        has_validation = False

        for stmt in ast.walk(node):
            # Check for validation (raises ValueError)
            if isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Call):
                if isinstance(stmt.exc.func, ast.Name) and stmt.exc.func.id == "ValueError":
                    has_validation = True

            # Check for direct field assignment (should use object.__setattr__)
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            if self.is_frozen:
                                self._add_issue(
                                    line=getattr(stmt, "lineno", self.current_class_lineno),
                                    severity="error",
                                    category="direct_assignment",
                                    message=f"Direct assignment to frozen field {target.attr}",
                                    fix_suggestion="Use object.__setattr__(self, 'field', value) in frozen context",
                                )

        if not has_validation:
            self._add_issue(
                line=node.lineno,
                severity="warning",
                category="no_validation",
                message=f"__post_init__ in {self.current_class} has no validation logic",
                fix_suggestion="Add validation that raises ValueError on invalid input",
            )


def scan_file(filepath: Path) -> list[ValidationIssue]:
    """Scan a Python file for value object validation issues.

    Args:
        filepath: Path to the Python file to scan.

    Returns:
        List of validation issues found in the file.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))

        validator = ValueObjectValidator(filepath)
        validator.visit(tree)

        return validator.issues
    except SyntaxError as e:
        return [
            ValidationIssue(
                file=filepath,
                line=e.lineno or 0,
                severity="error",
                category="syntax_error",
                message=f"Syntax error: {e.msg}",
                fix_suggestion=None,
            )
        ]


def scan_directory(path: Path) -> list[ValidationIssue]:
    """Scan a directory recursively for value object files.

    Args:
        path: Directory path to scan recursively.

    Returns:
        List of all validation issues found.
    """
    all_issues: list[ValidationIssue] = []

    for py_file in path.rglob("*.py"):
        # Skip __init__.py and test files
        if py_file.name == "__init__.py" or py_file.name.startswith("test_"):
            continue

        issues = scan_file(py_file)
        all_issues.extend(issues)

    return all_issues


def format_issue(issue: ValidationIssue) -> str:
    """Format a validation issue for display.

    Args:
        issue: Validation issue to format.

    Returns:
        Formatted string representation of the issue.
    """
    severity_markers = {"error": "[ERROR]", "warning": "[WARN]", "info": "[INFO]"}
    marker = severity_markers.get(issue.severity, "[?]")

    lines = [
        f"{marker} {issue.file}:{issue.line}",
        f"   {issue.category}: {issue.message}",
    ]

    if issue.fix_suggestion:
        lines.append(f"   Fix: {issue.fix_suggestion}")

    return "\n".join(lines)


def group_by_category(issues: list[ValidationIssue]) -> dict[str, list[ValidationIssue]]:
    """Group issues by category.

    Args:
        issues: List of validation issues to group.

    Returns:
        Dictionary mapping category names to lists of issues.
    """
    grouped: dict[str, list[ValidationIssue]] = {}

    for issue in issues:
        if issue.category not in grouped:
            grouped[issue.category] = []
        grouped[issue.category].append(issue)

    return grouped


def print_summary(issues: list[ValidationIssue]) -> None:
    """Print summary of validation issues.

    Args:
        issues: List of validation issues to summarize.
    """
    if not issues:
        print("No validation issues found.")
        return

    # Count by severity
    error_count = sum(1 for i in issues if i.severity == "error")
    warning_count = sum(1 for i in issues if i.severity == "warning")
    info_count = sum(1 for i in issues if i.severity == "info")

    print("\nSummary:")
    print(f"  Errors:   {error_count}")
    print(f"  Warnings: {warning_count}")
    print(f"  Info:     {info_count}")

    # Group by category
    grouped = group_by_category(issues)
    print("\nBy category:")
    for category, category_issues in sorted(grouped.items()):
        print(f"  {category}: {len(category_issues)}")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 for success, 1 if errors found.
    """
    parser = argparse.ArgumentParser(
        description="Validate value object patterns in codebase"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Path to scan (default: auto-detect from project root)",
    )
    parser.add_argument(
        "--category",
        help="Filter by category (e.g., missing_frozen, mutable_default)",
    )
    parser.add_argument(
        "--severity",
        choices=["error", "warning", "info"],
        help="Filter by severity",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Show summary only, no detailed issues",
    )

    args = parser.parse_args()

    # Determine scan path
    scan_path = args.path
    if scan_path is None:
        project_root = get_project_root()
        if project_root is not None:
            scan_path = project_root / "src"
        else:
            scan_path = Path.cwd()

    if not scan_path.exists():
        print(f"Error: Path does not exist: {scan_path}", file=sys.stderr)
        return 1

    # Scan for issues
    issues = scan_directory(scan_path)

    # Filter issues
    if args.category:
        issues = [i for i in issues if i.category == args.category]
    if args.severity:
        issues = [i for i in issues if i.severity == args.severity]

    # Print results
    if not args.summary_only:
        for issue in sorted(issues, key=lambda x: (str(x.file), x.line)):
            print(format_issue(issue))
            print()

    print_summary(issues)

    # Exit with error code if errors found
    error_count = sum(1 for i in issues if i.severity == "error")
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
