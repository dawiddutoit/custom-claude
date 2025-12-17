#!/usr/bin/env python3
"""Validate OpenTelemetry instrumentation in Python service files.

This script checks for:
- Methods missing @traced decorator
- Use of print() instead of logger
- Missing trace context
- Proper logger initialization
- Inconsistent instrumentation patterns

Usage:
    python validate_instrumentation.py <file_or_directory> [--strict] [--json]

Examples:
    # Validate a single file
    python validate_instrumentation.py src/project_watch_mcp/application/services/embedding_service.py

    # Validate all services
    python validate_instrumentation.py src/project_watch_mcp/application/services/

    # Strict mode (fail on any issues)
    python validate_instrumentation.py src/ --strict

    # JSON output for CI/CD integration
    python validate_instrumentation.py src/ --json
"""

import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ValidationIssue:
    """Represents a validation issue."""

    file: str
    line: int
    severity: str  # "error", "warning", "info"
    message: str
    category: str  # "missing_traced", "print_statement", "missing_logger", etc.


@dataclass
class ValidationResult:
    """Validation result for a file."""

    file: str
    success: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)


class InstrumentationValidator(ast.NodeVisitor):
    """AST visitor to validate OTEL instrumentation."""

    def __init__(self, file_path: str) -> None:
        """Initialize validator."""
        self.file_path = file_path
        self.issues: list[ValidationIssue] = []
        self.has_logger_import = False
        self.has_traced_import = False
        self.has_logger_init = False
        self.public_methods: list[tuple[str, int, bool]] = []  # (name, line, has_traced)
        self.print_statements: list[int] = []
        self.current_class = ""

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for OTEL imports."""
        if node.module == "project_watch_mcp.core.monitoring":
            for alias in node.names:
                if alias.name == "get_logger":
                    self.has_logger_import = True
                if alias.name == "traced":
                    self.has_traced_import = True
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check for logger initialization."""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "logger":
                # Check if initialized with get_logger
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        if node.value.func.id == "get_logger":
                            self.has_logger_init = True
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        self.current_class = node.name

        # Check if this is a service/handler/repository class
        is_service_class = any(
            name in node.name
            for name in ["Service", "Handler", "Repository", "Orchestrator", "Factory"]
        )

        if is_service_class:
            # Analyze methods in the class
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._check_method(item)

        self.generic_visit(node)
        self.current_class = ""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        # Check module-level functions (e.g., MCP tools)
        if not self.current_class:
            self._check_method(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        if not self.current_class:
            self._check_method(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for print() statements."""
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.print_statements.append(node.lineno)
            self.issues.append(
                ValidationIssue(
                    file=self.file_path,
                    line=node.lineno,
                    severity="error",
                    message="Using print() instead of logger - violates fail-fast principle",
                    category="print_statement",
                )
            )
        self.generic_visit(node)

    def _check_method(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check if a method has proper instrumentation."""
        # Skip private methods
        if node.name.startswith("_") and node.name != "__init__":
            return

        # Skip dunder methods
        if node.name.startswith("__") and node.name.endswith("__"):
            return

        # Check if method has @traced decorator
        has_traced = any(self._is_traced_decorator(dec) for dec in node.decorator_list)

        # Record public method
        method_name = f"{self.current_class}.{node.name}" if self.current_class else node.name
        self.public_methods.append((method_name, node.lineno, has_traced))

        if not has_traced:
            self.issues.append(
                ValidationIssue(
                    file=self.file_path,
                    line=node.lineno,
                    severity="warning",
                    message=f"Method '{method_name}' missing @traced decorator",
                    category="missing_traced",
                )
            )

        # Check if method has logging
        has_logging = self._has_logging(node)
        if not has_logging and has_traced:
            self.issues.append(
                ValidationIssue(
                    file=self.file_path,
                    line=node.lineno,
                    severity="info",
                    message=f"Method '{method_name}' has @traced but no logging statements",
                    category="missing_logging",
                )
            )

    def _is_traced_decorator(self, decorator: ast.expr) -> bool:
        """Check if a decorator is @traced."""
        if isinstance(decorator, ast.Name):
            return decorator.id == "traced"
        return False

    def _has_logging(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method has logger calls."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute):
                if isinstance(stmt.func.value, ast.Name):
                    if stmt.func.value.id == "logger":
                        return True
        return False

    def get_issues(self) -> list[ValidationIssue]:
        """Get all validation issues."""
        # Add issues for missing imports
        if self.public_methods and not self.has_traced_import:
            self.issues.append(
                ValidationIssue(
                    file=self.file_path,
                    line=1,
                    severity="error",
                    message="Missing import: traced from project_watch_mcp.core.monitoring",
                    category="missing_import",
                )
            )

        if (self.public_methods or self.print_statements) and not self.has_logger_import:
            self.issues.append(
                ValidationIssue(
                    file=self.file_path,
                    line=1,
                    severity="error",
                    message="Missing import: get_logger from project_watch_mcp.core.monitoring",
                    category="missing_import",
                )
            )

        if self.has_logger_import and not self.has_logger_init:
            self.issues.append(
                ValidationIssue(
                    file=self.file_path,
                    line=1,
                    severity="error",
                    message="Missing logger initialization: logger = get_logger(__name__)",
                    category="missing_logger_init",
                )
            )

        return self.issues


def validate_file(file_path: Path) -> ValidationResult:
    """Validate a Python file for OTEL instrumentation.

    Args:
        file_path: Path to Python file

    Returns:
        ValidationResult with issues found
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Validate
        validator = InstrumentationValidator(str(file_path))
        validator.visit(tree)

        issues = validator.get_issues()

        # Calculate stats
        stats = {
            "total_methods": len(validator.public_methods),
            "traced_methods": sum(1 for _, _, has_traced in validator.public_methods if has_traced),
            "untraced_methods": sum(
                1 for _, _, has_traced in validator.public_methods if not has_traced
            ),
            "print_statements": len(validator.print_statements),
            "errors": sum(1 for issue in issues if issue.severity == "error"),
            "warnings": sum(1 for issue in issues if issue.severity == "warning"),
            "info": sum(1 for issue in issues if issue.severity == "info"),
        }

        success = stats["errors"] == 0 and stats["warnings"] == 0

        return ValidationResult(
            file=str(file_path),
            success=success,
            issues=issues,
            stats=stats,
        )

    except Exception as e:
        return ValidationResult(
            file=str(file_path),
            success=False,
            issues=[
                ValidationIssue(
                    file=str(file_path),
                    line=0,
                    severity="error",
                    message=f"Failed to parse file: {e!s}",
                    category="parse_error",
                )
            ],
            stats={},
        )


def validate_directory(directory: Path) -> list[ValidationResult]:
    """Validate all Python files in a directory.

    Args:
        directory: Path to directory

    Returns:
        List of validation results
    """
    results = []

    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and similar
        if "__pycache__" in str(py_file):
            continue

        # Skip test files (they have different patterns)
        if "test_" in py_file.name or py_file.parent.name in ["tests", "test"]:
            continue

        result = validate_file(py_file)
        results.append(result)

    return results


def print_summary(results: list[ValidationResult], strict: bool = False) -> None:
    """Print summary of validation results."""
    total_files = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total_files - passed

    total_errors = sum(r.stats.get("errors", 0) for r in results)
    total_warnings = sum(r.stats.get("warnings", 0) for r in results)
    total_info = sum(r.stats.get("info", 0) for r in results)

    print("\n" + "=" * 80)
    print("OPENTELEMETRY INSTRUMENTATION VALIDATION RESULTS")
    print("=" * 80)

    print(f"\nFiles checked: {total_files}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"\nTotal errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")
    print(f"Total info: {total_info}")

    # Print details for files with issues
    if failed > 0:
        print("\nFILES WITH ISSUES:")
        print("-" * 80)

        for result in results:
            if not result.success or result.issues:

                # Group issues by severity
                errors = [i for i in result.issues if i.severity == "error"]
                warnings = [i for i in result.issues if i.severity == "warning"]
                info_issues = [i for i in result.issues if i.severity == "info"]

                if errors or warnings or (info_issues and strict):
                    print(f"\n{result.file}:")

                    if errors:
                        print("  ERRORS:")
                        for issue in errors:
                            print(f"    Line {issue.line}: {issue.message}")

                    if warnings:
                        print("  WARNINGS:")
                        for issue in warnings:
                            print(f"    Line {issue.line}: {issue.message}")

                    if info_issues and strict:
                        print("  INFO:")
                        for issue in info_issues:
                            print(f"    Line {issue.line}: {issue.message}")

    # Overall status
    overall_success = failed == 0 and total_warnings == 0 if strict else total_errors == 0

    print("\n" + "=" * 80)
    if overall_success:
        print("✓ VALIDATION PASSED")
    else:
        if strict:
            print("✗ VALIDATION FAILED (strict mode: errors and warnings)")
        else:
            print("✗ VALIDATION FAILED (errors found)")
    print("=" * 80)



def print_json(results: list[ValidationResult]) -> None:
    """Print results as JSON."""
    output = {
        "summary": {
            "total_files": len(results),
            "passed": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "total_errors": sum(r.stats.get("errors", 0) for r in results),
            "total_warnings": sum(r.stats.get("warnings", 0) for r in results),
            "total_info": sum(r.stats.get("info", 0) for r in results),
        },
        "files": [
            {
                "file": r.file,
                "success": r.success,
                "stats": r.stats,
                "issues": [
                    {
                        "line": i.line,
                        "severity": i.severity,
                        "category": i.category,
                        "message": i.message,
                    }
                    for i in r.issues
                ],
            }
            for r in results
        ],
    }
    print(json.dumps(output, indent=2))



def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_instrumentation.py <file_or_directory> [--strict] [--json]")
        print("\nExamples:")
        print("  # Validate a single file")
        print("  python validate_instrumentation.py src/project_watch_mcp/application/services/embedding_service.py")
        print("\n  # Validate all services")
        print("  python validate_instrumentation.py src/project_watch_mcp/application/services/")
        print("\n  # Strict mode (fail on any issues)")
        print("  python validate_instrumentation.py src/ --strict")
        print("\n  # JSON output for CI/CD integration")
        print("  python validate_instrumentation.py src/ --json")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    strict = "--strict" in sys.argv
    json_output = "--json" in sys.argv

    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}")
        sys.exit(1)

    if target_path.is_file():
        result = validate_file(target_path)
        results = [result]
    else:
        results = validate_directory(target_path)

    if json_output:
        print_json(results)
    else:
        print_summary(results, strict)

    # Exit code for CI/CD
    if strict:
        exit_code = 0 if all(r.success for r in results) else 1
    else:
        exit_code = 0 if sum(r.stats.get("errors", 0) for r in results) == 0 else 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
