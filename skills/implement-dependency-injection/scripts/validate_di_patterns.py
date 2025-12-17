#!/usr/bin/env python3
"""Validate dependency injection patterns in codebase.

Scans the codebase for common DI anti-patterns:
- Services with direct instantiation instead of container injection
- Missing provider registrations in container.py
- Services not registered in container
- Optional config/settings parameters (anti-pattern)

Usage:
    python validate_di_patterns.py [path_to_src]
    python validate_di_patterns.py --fix  # Auto-fix some issues
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Setup: Add .claude/tools to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_claude_root))

from tools.skill_utils import (  # noqa: E402
    ensure_path_setup,
    find_container_path,
    find_src_directory,
    get_project_root,
    is_service_class,
)

ensure_path_setup()


class Severity(Enum):
    """Severity level for violations."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class DIViolation:
    """Represents a DI pattern violation."""

    file_path: str
    line_number: int
    violation_type: str
    message: str
    severity: Severity


class DIPatternValidator(ast.NodeVisitor):
    """AST visitor to detect DI anti-patterns."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.violations: list[DIViolation] = []
        self.service_classes: list[str] = []
        self._current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to identify services."""
        self._current_class = node.name

        # Check if it's a service/repository/handler
        if is_service_class(node.name):
            self.service_classes.append(node.name)

            # Check __init__ method
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    self._check_init_method(item, node.name)

        self.generic_visit(node)
        self._current_class = None

    def _check_init_method(self, node: ast.FunctionDef, class_name: str) -> None:
        """Check __init__ method for DI anti-patterns."""
        # Check for optional Settings/Config parameters
        for arg in node.args.args[1:]:  # Skip self
            if arg.annotation:
                annotation_str = ast.unparse(arg.annotation)

                # Check for Optional[Settings] or Settings | None
                if "Settings" in annotation_str or "Config" in annotation_str:
                    if "Optional" in annotation_str or " | None" in annotation_str:
                        self.violations.append(
                            DIViolation(
                                file_path=self.file_path,
                                line_number=arg.lineno,
                                violation_type="optional_config",
                                message=(
                                    f"{class_name}.__init__ has optional Settings/Config "
                                    f"parameter '{arg.arg}'. Settings must be required, not Optional."
                                ),
                                severity=Severity.ERROR,
                            )
                        )

        # Check for missing validation
        has_validation = False
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                # Check if it validates settings
                test_str = ast.unparse(stmt.test)
                if "settings" in test_str.lower() or "config" in test_str.lower():
                    has_validation = True
                    break

        # Check if Settings parameter exists
        has_settings = any(
            arg.annotation
            and (
                "Settings" in ast.unparse(arg.annotation)
                or "Config" in ast.unparse(arg.annotation)
            )
            for arg in node.args.args[1:]
        )

        if has_settings and not has_validation:
            self.violations.append(
                DIViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    violation_type="missing_validation",
                    message=(
                        f"{class_name}.__init__ missing Settings validation. "
                        f"Add: if not settings: raise ValueError('Settings required')"
                    ),
                    severity=Severity.WARNING,
                )
            )

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to detect direct instantiation."""
        # Check for direct service instantiation (Service(), Repository(), etc.)
        if isinstance(node.func, ast.Name) and is_service_class(node.func.id):
            # Check if it's NOT in __init__ (which is OK for factories)
            if self._current_class and "Factory" not in self._current_class:
                self.violations.append(
                    DIViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        violation_type="direct_instantiation",
                        message=(
                            f"Direct instantiation of {node.func.id}(). "
                            f"Should be injected from container."
                        ),
                        severity=Severity.WARNING,
                    )
                )

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Detect try/except ImportError patterns (anti-pattern)."""
        for handler in node.handlers:
            if handler.type and isinstance(handler.type, ast.Name):
                if handler.type.id == "ImportError":
                    self.violations.append(
                        DIViolation(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            violation_type="optional_import",
                            message=(
                                "try/except ImportError pattern detected. "
                                "All imports must be at top, fail fast if missing."
                            ),
                            severity=Severity.ERROR,
                        )
                    )

        self.generic_visit(node)


class ContainerAnalyzer:
    """Analyze container.py for registered services."""

    def __init__(self, container_path: Path) -> None:
        self.container_path = container_path
        self.registered_services: set[str] = set()

    def analyze(self) -> None:
        """Parse container.py and extract registered services."""
        if not self.container_path.exists():
            return

        with self.container_path.open(encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(self.container_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Look for providers.Singleton/Factory assignments
                if isinstance(node.value, ast.Call) and isinstance(
                    node.value.func, ast.Attribute
                ):
                    if (
                        isinstance(node.value.func.value, ast.Name)
                        and node.value.func.value.id == "providers"
                    ):
                        # Extract service class name from first argument
                        if node.value.args:
                            arg = node.value.args[0]
                            if isinstance(arg, ast.Name):
                                self.registered_services.add(arg.id)


def scan_directory(
    root_path: Path,
    container_path: Path,
) -> tuple[list[DIViolation], set[str]]:
    """Scan directory for DI pattern violations.

    Args:
        root_path: Root directory to scan.
        container_path: Path to container.py.

    Returns:
        Tuple of (violations, unregistered_services).
    """
    violations: list[DIViolation] = []
    all_services: set[str] = set()

    # Analyze container first
    container_analyzer = ContainerAnalyzer(container_path)
    container_analyzer.analyze()

    # Scan all Python files
    for py_file in root_path.rglob("*.py"):
        # Skip test files and __pycache__
        if "test" in str(py_file) or "__pycache__" in str(py_file):
            continue

        try:
            with py_file.open(encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            validator = DIPatternValidator(str(py_file))
            validator.visit(tree)
            violations.extend(validator.violations)
            all_services.update(validator.service_classes)

        except SyntaxError as e:
            violations.append(
                DIViolation(
                    file_path=str(py_file),
                    line_number=e.lineno or 0,
                    violation_type="syntax_error",
                    message=f"Syntax error: {e}",
                    severity=Severity.ERROR,
                )
            )

    # Find unregistered services
    unregistered = all_services - container_analyzer.registered_services

    # Add violations for unregistered services
    for service in sorted(unregistered):
        violations.append(
            DIViolation(
                file_path=str(container_path),
                line_number=0,
                violation_type="unregistered_service",
                message=f"Service '{service}' not registered in container.py",
                severity=Severity.INFO,
            )
        )

    return violations, unregistered


def _get_severity_color(severity: Severity) -> str:
    """Get ANSI color code for severity level."""
    colors = {
        Severity.ERROR: "\033[91m",  # Red
        Severity.WARNING: "\033[93m",  # Yellow
        Severity.INFO: "\033[94m",  # Blue
    }
    return colors.get(severity, "")


def _reset_color() -> str:
    """Get ANSI reset color code."""
    return "\033[0m"


def print_violations(violations: list[DIViolation]) -> None:
    """Print violations grouped by severity."""
    # Group by severity
    errors = [v for v in violations if v.severity == Severity.ERROR]
    warnings = [v for v in violations if v.severity == Severity.WARNING]
    info = [v for v in violations if v.severity == Severity.INFO]

    def print_group(title: str, viols: list[DIViolation], severity: Severity) -> None:
        if not viols:
            return

        color = _get_severity_color(severity)
        reset = _reset_color()

        print(f"\n{color}{title}{reset} ({len(viols)}):")
        print("-" * 60)
        for v in viols:
            print(f"  {v.file_path}:{v.line_number}")
            print(f"    [{v.violation_type}] {v.message}")

    print_group("ERRORS", errors, Severity.ERROR)
    print_group("WARNINGS", warnings, Severity.WARNING)
    print_group("INFO", info, Severity.INFO)

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Info: {len(info)}")
    print(f"  Total: {len(violations)}")
    print("=" * 60)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for errors found).
    """
    parser = argparse.ArgumentParser(
        description="Validate dependency injection patterns in codebase"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to source directory (auto-detected if not provided)",
    )
    parser.add_argument(
        "--container",
        help="Path to container.py (auto-detected if not provided)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix some issues (not implemented yet)",
    )

    args = parser.parse_args()

    project_root = get_project_root()

    # Find source directory
    if args.path:
        root_path = Path(args.path)
    else:
        found_src = find_src_directory(project_root)
        if found_src is None:
            print("Error: Could not find src directory. Please specify path.", file=sys.stderr)
            return 1
        root_path = found_src

    # Find container path
    if args.container:
        container_path = Path(args.container)
    else:
        found_container = find_container_path(project_root)
        if found_container is None:
            print(
                "Warning: Could not find container.py. Skipping registration check.",
                file=sys.stderr,
            )
            container_path = Path("container.py")  # Non-existent fallback
        else:
            container_path = found_container

    if not root_path.exists():
        print(f"Error: Source directory not found: {root_path}", file=sys.stderr)
        return 1

    print(f"Scanning: {root_path}")
    if container_path.exists():
        print(f"Container: {container_path}")

    violations, _unregistered = scan_directory(root_path, container_path)

    print_violations(violations)

    # Return non-zero if errors found
    error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
