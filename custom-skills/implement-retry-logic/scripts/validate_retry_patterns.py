#!/usr/bin/env python3
"""Validate retry logic implementations against best practices.

This script analyzes Python files to find retry implementations and validates
them against project standards:
- Exponential backoff with jitter
- Settings-based configuration (no hardcoded values)
- Proper error classification
- ServiceResult usage

Usage:
    python validate_retry_patterns.py [paths...]

Examples:
    # Validate single file
    python validate_retry_patterns.py src/services/api_service.py

    # Validate directory
    python validate_retry_patterns.py src/services/

    # Validate entire codebase
    python validate_retry_patterns.py src/

    # JSON output for CI/CD
    python validate_retry_patterns.py src/ --format json
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationIssue:
    """Represents a validation issue found in code."""

    severity: str  # "error", "warning", "info"
    message: str
    file_path: str
    line_number: int
    method_name: str
    fix_suggestion: str = ""


@dataclass
class ValidationResult:
    """Results of retry pattern validation."""

    file_path: str
    issues: list[ValidationIssue] = field(default_factory=list)
    retry_methods_found: int = 0
    compliant_methods: int = 0

    def add_issue(
        self,
        severity: str,
        message: str,
        line: int,
        method: str,
        fix: str = "",
    ) -> None:
        """Add validation issue."""
        self.issues.append(
            ValidationIssue(
                severity=severity,
                message=message,
                file_path=self.file_path,
                line_number=line,
                method_name=method,
                fix_suggestion=fix,
            )
        )

    @property
    def has_errors(self) -> bool:
        """Check if any errors found."""
        return any(issue.severity == "error" for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        """Check if any warnings found."""
        return any(issue.severity == "warning" for issue in self.issues)


class RetryPatternValidator(ast.NodeVisitor):
    """AST visitor that validates retry patterns."""

    def __init__(self, file_path: str) -> None:
        """Initialize validator.

        Args:
            file_path: Path to file being validated
        """
        self.file_path = file_path
        self.result = ValidationResult(file_path=file_path)
        self.current_method: str | None = None
        self.in_retry_loop = False
        self.has_jitter = False
        self.has_backoff = False
        self.uses_settings = False
        self.has_hardcoded_retries = False
        self.hardcoded_values: list[tuple[int, Any]] = []

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self.current_method = node.name

        # Check if method contains retry logic
        has_retry = self._has_retry_loop(node)

        if has_retry:
            self.result.retry_methods_found += 1

            # Reset state for this method
            self.in_retry_loop = True
            self.has_jitter = False
            self.has_backoff = False
            self.uses_settings = False
            self.has_hardcoded_retries = False
            self.hardcoded_values = []

            # Analyze retry implementation
            self.generic_visit(node)

            # Validate findings
            self._validate_retry_implementation(node)

        self.current_method = None
        self.in_retry_loop = False

    def _has_retry_loop(self, node: ast.AsyncFunctionDef) -> bool:
        """Check if function contains retry loop.

        Args:
            node: Function definition node

        Returns:
            True if retry loop found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.For):
                # Check for "range(max_retries)" or "range(self.max_retries)"
                if isinstance(child.iter, ast.Call):
                    if isinstance(child.iter.func, ast.Name) and child.iter.func.id == "range":
                        return True
        return False

    def visit_For(self, node: ast.For) -> None:
        """Visit for loops (detect retry loops)."""
        if not self.in_retry_loop:
            return

        # Check for hardcoded retry count: range(3), range(5), etc.
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                if node.iter.args and isinstance(node.iter.args[0], ast.Constant):
                    self.has_hardcoded_retries = True
                    self.hardcoded_values.append((node.lineno, node.iter.args[0].value))

                # Check if uses settings
                elif node.iter.args and isinstance(node.iter.args[0], ast.Attribute):
                    attr = node.iter.args[0]
                    if isinstance(attr.value, ast.Attribute):
                        # self.settings.max_retries
                        if attr.value.attr == "settings":
                            self.uses_settings = True

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Visit binary operations (detect backoff calculation)."""
        if not self.in_retry_loop:
            return

        # Check for exponential backoff: base * (2 ** attempt)
        if isinstance(node.op, ast.Mult):
            # Check if right side is power operation
            if isinstance(node.right, ast.BinOp) and isinstance(node.right.op, ast.Pow):
                # Check if base is 2
                if isinstance(node.right.left, ast.Constant) and node.right.left.value == 2:
                    self.has_backoff = True

        # Check for jitter: delay * 0.2
        if isinstance(node.op, ast.Mult) and isinstance(node.right, ast.Constant):
            # Jitter factor typically 0.1-0.3
            if 0.1 <= node.right.value <= 0.3:
                self.has_jitter = True

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls (detect time.time() for jitter)."""
        if not self.in_retry_loop:
            return

        # Check for time.time() % 1 (jitter randomness)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "time":
            self.has_jitter = True

        self.generic_visit(node)

    def _validate_retry_implementation(self, node: ast.AsyncFunctionDef) -> None:
        """Validate retry implementation against best practices.

        Args:
            node: Function definition node
        """
        method_name = self.current_method or "unknown"

        # Check 1: Hardcoded retry values
        if self.has_hardcoded_retries:
            for line, value in self.hardcoded_values:
                self.result.add_issue(
                    severity="error",
                    message=f"Hardcoded retry count ({value}) - should use settings",
                    line=line,
                    method=method_name,
                    fix="Replace with self.settings.max_retries or self.settings.<service>.max_retries",
                )

        # Check 2: Missing settings usage
        if not self.uses_settings:
            self.result.add_issue(
                severity="warning",
                message="Retry count not from settings - may be hardcoded",
                line=node.lineno,
                method=method_name,
                fix="Use self.settings.max_retries for configuration",
            )

        # Check 3: Missing exponential backoff
        if not self.has_backoff:
            self.result.add_issue(
                severity="error",
                message="Missing exponential backoff - using fixed delay?",
                line=node.lineno,
                method=method_name,
                fix="Use: delay = min(base_delay * (2 ** attempt), 30.0)",
            )

        # Check 4: Missing jitter
        if not self.has_jitter:
            self.result.add_issue(
                severity="warning",
                message="Missing jitter - may cause thundering herd",
                line=node.lineno,
                method=method_name,
                fix="Add jitter: jitter = delay * 0.2 * (2 * (time.time() % 1) - 1)",
            )

        # Check 5: Verify ServiceResult usage
        if not self._returns_service_result(node):
            self.result.add_issue(
                severity="error",
                message="Method should return ServiceResult[T]",
                line=node.lineno,
                method=method_name,
                fix="Change return type to ServiceResult[T] and return ServiceResult.ok() or ServiceResult.fail()",
            )

        # If all checks pass, mark as compliant
        if (
            not self.has_hardcoded_retries
            and self.has_backoff
            and self.has_jitter
            and self.uses_settings
        ):
            self.result.compliant_methods += 1

    def _returns_service_result(self, node: ast.AsyncFunctionDef) -> bool:
        """Check if function returns ServiceResult.

        Args:
            node: Function definition node

        Returns:
            True if returns ServiceResult
        """
        if node.returns:
            return_str = ast.unparse(node.returns)
            return "ServiceResult" in return_str
        return False


def validate_file(file_path: Path) -> ValidationResult:
    """Validate retry patterns in a single file.

    Args:
        file_path: Path to Python file

    Returns:
        ValidationResult with issues found
    """
    try:
        source_code = file_path.read_text()
        tree = ast.parse(source_code)

        validator = RetryPatternValidator(str(file_path))
        validator.visit(tree)

        return validator.result

    except SyntaxError as e:
        result = ValidationResult(file_path=str(file_path))
        result.add_issue(
            severity="error",
            message=f"Syntax error: {e}",
            line=getattr(e, "lineno", 0),
            method="N/A",
        )
        return result

    except Exception as e:
        result = ValidationResult(file_path=str(file_path))
        result.add_issue(
            severity="error",
            message=f"Validation error: {e}",
            line=0,
            method="N/A",
        )
        return result


def validate_directory(directory: Path) -> list[ValidationResult]:
    """Validate all Python files in directory.

    Args:
        directory: Path to directory

    Returns:
        List of ValidationResults
    """
    results = []
    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and test files for now
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue

        result = validate_file(py_file)
        if result.retry_methods_found > 0 or result.issues:
            results.append(result)

    return results


def print_results(results: list[ValidationResult], output_format: str = "text") -> None:
    """Print validation results.

    Args:
        results: List of validation results
        output_format: Output format ("text" or "json")
    """
    if output_format == "json":
        output = {
            "summary": {
                "total_files": len(results),
                "total_retry_methods": sum(r.retry_methods_found for r in results),
                "compliant_methods": sum(r.compliant_methods for r in results),
                "total_errors": sum(
                    len([i for i in r.issues if i.severity == "error"]) for r in results
                ),
                "total_warnings": sum(
                    len([i for i in r.issues if i.severity == "warning"]) for r in results
                ),
            },
            "files": [
                {
                    "path": r.file_path,
                    "retry_methods": r.retry_methods_found,
                    "compliant_methods": r.compliant_methods,
                    "issues": [
                        {
                            "severity": i.severity,
                            "message": i.message,
                            "line": i.line_number,
                            "method": i.method_name,
                            "fix": i.fix_suggestion,
                        }
                        for i in r.issues
                    ],
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
        return

    # Text format
    total_retry_methods = sum(r.retry_methods_found for r in results)
    compliant_methods = sum(r.compliant_methods for r in results)
    total_errors = sum(len([i for i in r.issues if i.severity == "error"]) for r in results)
    total_warnings = sum(len([i for i in r.issues if i.severity == "warning"]) for r in results)

    print("\n=== Retry Pattern Validation ===")
    print(f"Files analyzed: {len(results)}")
    print(f"Retry methods found: {total_retry_methods}")
    print(f"Compliant methods: {compliant_methods}")
    print(f"Errors: {total_errors}, Warnings: {total_warnings}")

    for result in results:
        if not result.issues:
            continue

        print(f"\n--- {result.file_path} ---")
        for issue in result.issues:
            severity_prefix = "[ERROR]" if issue.severity == "error" else "[WARN]"
            print(f"  {severity_prefix} Line {issue.line_number} ({issue.method_name})")
            print(f"    {issue.message}")
            if issue.fix_suggestion:
                print(f"    Fix: {issue.fix_suggestion}")

    if total_errors == 0 and total_warnings == 0:
        print("\n[OK] All retry implementations are compliant!")
    elif total_errors == 0:
        print(f"\n[OK] No errors, but {total_warnings} warnings to review")
    else:
        print(f"\n[FAIL] {total_errors} errors must be fixed")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate retry logic implementations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files or directories to validate",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Collect all results
    all_results: list[ValidationResult] = []

    for path in args.paths:
        if not path.exists():
            return 1

        if path.is_file():
            result = validate_file(path)
            if result.retry_methods_found > 0 or result.issues:
                all_results.append(result)
        elif path.is_dir():
            results = validate_directory(path)
            all_results.extend(results)

    if not all_results:
        return 0

    # Print results
    print_results(all_results, output_format=args.format)

    # Return exit code based on errors
    has_errors = any(r.has_errors for r in all_results)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
