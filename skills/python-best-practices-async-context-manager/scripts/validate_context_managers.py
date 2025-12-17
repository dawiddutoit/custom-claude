#!/usr/bin/env python3
"""Validate async context manager patterns in codebase.

This script checks for common anti-patterns and missing best practices:
- Missing resource = None initialization
- Missing error handling in cleanup
- Missing AsyncIterator return type
- Raising errors in finally blocks
- Optional config parameters
- Missing fail-fast validation

Usage:
    python validate_context_managers.py src/
    python validate_context_managers.py src/module.py --strict
    python validate_context_managers.py src/ --report report.json
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple


class ValidationIssue(NamedTuple):
    """Represents a validation issue found in code."""

    file_path: Path
    line_number: int
    function_name: str
    severity: str  # "error", "warning", "info"
    issue_type: str
    message: str
    suggestion: str | None = None


@dataclass
class ValidationReport:
    """Summary of validation results."""

    total_context_managers: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)
    files_checked: int = 0

    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return sum(1 for issue in self.issues if issue.severity == "warning")


class ContextManagerValidator(ast.NodeVisitor):
    """AST visitor to validate async context manager patterns."""

    def __init__(self, file_path: Path) -> None:
        """Initialize validator.

        Args:
            file_path: Path to file being validated
        """
        self.file_path = file_path
        self.issues: list[ValidationIssue] = []
        self.context_manager_count = 0

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition.

        Args:
            node: AST node for async function
        """
        # Check if this is a context manager (has @asynccontextmanager decorator)
        is_context_manager = any(
            self._is_asynccontextmanager_decorator(dec) for dec in node.decorator_list
        )

        if is_context_manager:
            self.context_manager_count += 1
            self._validate_context_manager(node)

        self.generic_visit(node)

    def _is_asynccontextmanager_decorator(self, node: ast.expr) -> bool:
        """Check if decorator is @asynccontextmanager.

        Args:
            node: Decorator AST node

        Returns:
            bool: True if asynccontextmanager decorator
        """
        if isinstance(node, ast.Name):
            return node.id == "asynccontextmanager"
        if isinstance(node, ast.Attribute):
            return node.attr == "asynccontextmanager"
        return False

    def _validate_context_manager(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async context manager function.

        Args:
            node: AST node for async function
        """
        func_name = node.name

        # Check 1: Validate return type annotation
        self._check_return_type(node, func_name)

        # Check 2: Validate has try/finally structure
        self._check_try_finally(node, func_name)

        # Check 3: Check for resource state tracking
        self._check_resource_tracking(node, func_name)

        # Check 4: Check for fail-fast validation
        self._check_fail_fast_validation(node, func_name)

        # Check 5: Check for optional config parameters
        self._check_optional_config(node, func_name)

        # Check 6: Check cleanup error handling
        self._check_cleanup_error_handling(node, func_name)

    def _check_return_type(self, node: ast.AsyncFunctionDef, func_name: str) -> None:
        """Check for proper AsyncIterator return type.

        Args:
            node: Function AST node
            func_name: Name of function
        """
        if not node.returns:
            self.issues.append(
                ValidationIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    severity="error",
                    issue_type="missing_return_type",
                    message="Missing return type annotation",
                    suggestion="Add -> AsyncIterator[ResourceType] return type",
                )
            )
            return

        # Check if return type is AsyncIterator
        return_type_str = ast.unparse(node.returns)
        if (
            "AsyncIterator" not in return_type_str
            and "AsyncGenerator" not in return_type_str
        ):
            self.issues.append(
                ValidationIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    severity="warning",
                    issue_type="wrong_return_type",
                    message=f"Return type should be AsyncIterator, got: {return_type_str}",
                    suggestion="Use AsyncIterator[T] from collections.abc",
                )
            )

    def _check_try_finally(self, node: ast.AsyncFunctionDef, func_name: str) -> None:
        """Check for try/finally structure.

        Args:
            node: Function AST node
            func_name: Name of function
        """
        has_try_finally = False

        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Try) and stmt.finalbody:
                has_try_finally = True
                break

        if not has_try_finally:
            self.issues.append(
                ValidationIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    severity="error",
                    issue_type="missing_try_finally",
                    message="Context manager missing try/finally block",
                    suggestion="Wrap yield in try/finally to ensure cleanup",
                )
            )

    def _check_resource_tracking(
        self, node: ast.AsyncFunctionDef, func_name: str
    ) -> None:
        """Check for resource = None pattern.

        Args:
            node: Function AST node
            func_name: Name of function
        """
        has_resource_init = False

        # Look for "resource = None" or similar pattern
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        # Check if assigned to None or Constant(None)
                        if (
                            isinstance(stmt.value, ast.Constant)
                            and stmt.value.value is None
                        ):
                            has_resource_init = True
                            break

        if not has_resource_init:
            self.issues.append(
                ValidationIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    severity="warning",
                    issue_type="missing_resource_tracking",
                    message="Missing resource state tracking (resource = None)",
                    suggestion="Initialize resource = None before try block",
                )
            )

    def _check_fail_fast_validation(
        self, node: ast.AsyncFunctionDef, func_name: str
    ) -> None:
        """Check for fail-fast validation at function entry.

        Args:
            node: Function AST node
            func_name: Name of function
        """
        has_validation = False

        # Look for validation in first few statements
        for stmt in node.body[:3]:
            if isinstance(stmt, ast.If):
                # Check for "if not config:" or similar
                if isinstance(stmt.test, ast.UnaryOp) and isinstance(
                    stmt.test.op, ast.Not
                ):
                    has_validation = True
                    break

        if not has_validation and len(node.args.args) > 0:
            # Only warn if function has parameters
            self.issues.append(
                ValidationIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    severity="info",
                    issue_type="missing_validation",
                    message="Consider adding fail-fast parameter validation",
                    suggestion="Add 'if not config: raise ValueError(...)' at entry",
                )
            )

    def _check_optional_config(
        self, node: ast.AsyncFunctionDef, func_name: str
    ) -> None:
        """Check for optional config/settings parameters.

        Args:
            node: Function AST node
            func_name: Name of function
        """
        for arg in node.args.args:
            # Check if parameter has type annotation
            if not arg.annotation:
                continue

            annotation_str = ast.unparse(arg.annotation)

            # Check for Optional or Union with None
            if (
                "Optional" in annotation_str
                or "| None" in annotation_str
                or "None |" in annotation_str
            ):
                # Check if parameter name suggests it's a config
                param_name = arg.arg.lower()
                if any(
                    keyword in param_name
                    for keyword in ["config", "settings", "driver", "session"]
                ):
                    self.issues.append(
                        ValidationIssue(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            function_name=func_name,
                            severity="error",
                            issue_type="optional_config",
                            message=f"Config parameter '{arg.arg}' should not be Optional",
                            suggestion=f"Make {arg.arg}: {annotation_str.replace(' | None', '').replace('Optional[', '').rstrip(']')} required",
                        )
                    )

    def _check_cleanup_error_handling(
        self, node: ast.AsyncFunctionDef, func_name: str
    ) -> None:
        """Check for proper error handling in cleanup (finally block).

        Args:
            node: Function AST node
            func_name: Name of function
        """
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Try) and stmt.finalbody:
                # Check if finally block has error handling
                has_error_handling = any(
                    isinstance(s, ast.Try)
                    for s in ast.walk(ast.Module(body=stmt.finalbody))
                )

                if not has_error_handling:
                    self.issues.append(
                        ValidationIssue(
                            file_path=self.file_path,
                            line_number=stmt.lineno,
                            function_name=func_name,
                            severity="warning",
                            issue_type="missing_cleanup_error_handling",
                            message="Cleanup code should handle errors gracefully",
                            suggestion="Wrap cleanup code in try/except to avoid hiding original errors",
                        )
                    )


def validate_file(file_path: Path) -> ValidationReport:
    """Validate async context managers in a single file.

    Args:
        file_path: Path to Python file

    Returns:
        ValidationReport: Validation results
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source)

        validator = ContextManagerValidator(file_path)
        validator.visit(tree)

        return ValidationReport(
            total_context_managers=validator.context_manager_count,
            issues=validator.issues,
            files_checked=1,
        )

    except SyntaxError as e:
        # File has syntax errors, can't validate
        return ValidationReport(
            issues=[
                ValidationIssue(
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    function_name="",
                    severity="error",
                    issue_type="syntax_error",
                    message=f"Syntax error: {e.msg}",
                )
            ],
            files_checked=1,
        )


def validate_directory(directory: Path) -> ValidationReport:
    """Validate all Python files in directory.

    Args:
        directory: Directory to scan

    Returns:
        ValidationReport: Combined validation results
    """
    combined_report = ValidationReport()

    for py_file in directory.rglob("*.py"):
        # Skip test files and __pycache__
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue

        report = validate_file(py_file)
        combined_report.total_context_managers += report.total_context_managers
        combined_report.issues.extend(report.issues)
        combined_report.files_checked += report.files_checked

    return combined_report


def print_report(report: ValidationReport) -> None:
    """Print validation report to console.

    Args:
        report: Validation results to print
    """
    print("\nValidation Summary:")
    print(f"  Files checked: {report.files_checked}")
    print(f"  Context managers found: {report.total_context_managers}")
    print(f"  Errors: {report.error_count}")
    print(f"  Warnings: {report.warning_count}")

    if not report.issues:
        print("\nNo issues found.")
        return

    # Group issues by severity
    errors = [i for i in report.issues if i.severity == "error"]
    warnings = [i for i in report.issues if i.severity == "warning"]
    info = [i for i in report.issues if i.severity == "info"]

    if errors:
        print("\nErrors:")
        for issue in errors:
            print(f"  {issue.file_path}:{issue.line_number} [{issue.function_name}]")
            print(f"    {issue.message}")
            if issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")

    if warnings:
        print("\nWarnings:")
        for issue in warnings:
            print(f"  {issue.file_path}:{issue.line_number} [{issue.function_name}]")
            print(f"    {issue.message}")
            if issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")

    if info:
        print("\nInfo:")
        for issue in info:
            print(f"  {issue.file_path}:{issue.line_number} [{issue.function_name}]")
            print(f"    {issue.message}")
            if issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")


def export_json_report(report: ValidationReport, output_path: Path) -> None:
    """Export validation report as JSON.

    Args:
        report: Validation results
        output_path: Path to save JSON report
    """
    data = {
        "summary": {
            "files_checked": report.files_checked,
            "context_managers_found": report.total_context_managers,
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "total_issues": len(report.issues),
        },
        "issues": [
            {
                "file": str(issue.file_path),
                "line": issue.line_number,
                "function": issue.function_name,
                "severity": issue.severity,
                "type": issue.issue_type,
                "message": issue.message,
                "suggestion": issue.suggestion,
            }
            for issue in report.issues
        ],
    }

    output_path.write_text(json.dumps(data, indent=2))


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Validate async context manager patterns"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to validate",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Export JSON report to file",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit code 1 if any warnings)",
    )

    args = parser.parse_args()

    # Validate path exists
    if not args.path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Run validation
    report = (
        validate_file(args.path)
        if args.path.is_file()
        else validate_directory(args.path)
    )

    # Print results
    print_report(report)

    # Export JSON if requested
    if args.report:
        export_json_report(report, args.report)

    # Exit with error code if issues found
    if (
        args.strict and (report.error_count > 0 or report.warning_count > 0)
    ) or report.error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
