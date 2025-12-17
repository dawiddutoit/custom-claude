#!/usr/bin/env python3
"""Validate constructor validation test coverage.

This script scans test files to ensure all constructor parameters have
corresponding validation tests. It compares service constructors with their
test classes and reports:
- Missing validation tests
- Parameters without tests
- Coverage statistics

Usage:
    python validate_constructor_tests.py --scan-all
    python validate_constructor_tests.py --test-dir tests/unit --service-dir src/

Examples:
    # Validate specific test/service pair
    python validate_constructor_tests.py \\
        tests/unit/application/services/test_user_service.py \\
        src/services/user_service.py

    # Scan all tests and services
    python validate_constructor_tests.py --scan-all

    # Custom directories
    python validate_constructor_tests.py \\
        --test-dir tests/unit/application \\
        --service-dir src/app/application
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# Setup: Add .claude to path for skill_utils and tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.ast_utils import parse_python_file
from tools.skill_utils import ensure_path_setup

ensure_path_setup()


# Constants
FULL_COVERAGE_PERCENT = 100.0
MIN_TEST_METHOD_PARTS = (
    5  # test_constructor_fails_when_{param}_is_none has at least 5 parts
)


@dataclass
class ValidationResult:
    """Result of validation check."""

    service_name: str
    service_file: Path
    test_file: Path | None
    parameters: list[str]
    tested_parameters: list[str]
    missing_tests: list[str]
    has_success_test: bool
    coverage_percent: float


class ConstructorValidator:
    """Validate constructor validation test coverage."""

    def __init__(self, test_file: Path, service_file: Path) -> None:
        """Initialize validator.

        Args:
            test_file: Path to test file
            service_file: Path to service file
        """
        self.test_file = test_file
        self.service_file = service_file

    def extract_service_parameters(self) -> tuple[str, list[str]]:
        """Extract service name and constructor parameters.

        Returns:
            Tuple of (service_name, parameter_names)
        """
        tree = parse_python_file(self.service_file)
        if tree is None:
            return "", []

        # Find service class
        service_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("Test"):
                service_class = node
                break

        if not service_class:
            return "", []

        # Find __init__ method
        init_method = None
        for node in service_class.body:
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                init_method = node
                break

        if not init_method:
            return service_class.name, []

        # Extract parameter names (excluding self)
        parameters = [arg.arg for arg in init_method.args.args if arg.arg != "self"]

        return service_class.name, parameters

    def extract_tested_parameters(self, service_name: str) -> tuple[list[str], bool]:
        """Extract tested parameters from test file.

        Args:
            service_name: Name of service class

        Returns:
            Tuple of (tested_parameter_names, has_success_test)
        """
        if not self.test_file.exists():
            return [], False

        tree = parse_python_file(self.test_file)
        if tree is None:
            return [], False

        # Find test class
        test_class_name = f"Test{service_name}Constructor"
        test_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == test_class_name:
                test_class = node
                break

        if not test_class:
            return [], False

        tested_params = set()
        has_success_test = False

        # Find validation test methods
        for node in test_class.body:
            if isinstance(node, ast.FunctionDef):
                # Check for success test
                if "initializes_with_valid_dependencies" in node.name:
                    has_success_test = True

                # Check for validation tests (test_constructor_fails_when_X_is_none)
                if node.name.startswith("test_constructor_fails_when_"):
                    # Extract parameter name from test method name
                    # Format: test_constructor_fails_when_{param}_is_none
                    parts = node.name.split("_")
                    if (
                        len(parts) >= MIN_TEST_METHOD_PARTS
                        and parts[-2] == "is"
                        and parts[-1] == "none"
                    ):
                        # Join middle parts as parameter name
                        param_name = "_".join(parts[4:-2])
                        tested_params.add(param_name)

        return list(tested_params), has_success_test

    def validate(self) -> ValidationResult:
        """Validate test coverage.

        Returns:
            ValidationResult with coverage information
        """
        service_name, parameters = self.extract_service_parameters()

        if not service_name:
            return ValidationResult(
                service_name="<unknown>",
                service_file=self.service_file,
                test_file=self.test_file if self.test_file.exists() else None,
                parameters=[],
                tested_parameters=[],
                missing_tests=[],
                has_success_test=False,
                coverage_percent=0.0,
            )

        tested_params, has_success_test = self.extract_tested_parameters(service_name)

        missing_tests = [p for p in parameters if p not in tested_params]

        coverage = (len(tested_params) / len(parameters) * 100) if parameters else 100.0

        return ValidationResult(
            service_name=service_name,
            service_file=self.service_file,
            test_file=self.test_file if self.test_file.exists() else None,
            parameters=parameters,
            tested_parameters=tested_params,
            missing_tests=missing_tests,
            has_success_test=has_success_test,
            coverage_percent=coverage,
        )


class ProjectScanner:
    """Scan project for service/test pairs."""

    def __init__(self, test_dir: Path, service_dir: Path) -> None:
        """Initialize scanner.

        Args:
            test_dir: Directory containing test files
            service_dir: Directory containing service files
        """
        self.test_dir = test_dir
        self.service_dir = service_dir

    def find_service_files(self) -> list[Path]:
        """Find all service Python files.

        Returns:
            List of service file paths
        """
        return list(self.service_dir.rglob("*.py"))

    def find_test_file(self, service_file: Path) -> Path | None:
        """Find corresponding test file for service.

        Args:
            service_file: Path to service file

        Returns:
            Path to test file or None if not found
        """
        # Try to find test file by naming convention
        service_name = service_file.stem
        test_name = f"test_{service_name}.py"

        # Search in test directory structure
        for test_file in self.test_dir.rglob(test_name):
            return test_file

        return None

    def scan(self) -> list[ValidationResult]:
        """Scan all services and validate test coverage.

        Returns:
            List of validation results
        """
        results = []

        service_files = self.find_service_files()

        for service_file in service_files:
            # Skip __init__.py and test files
            if service_file.name == "__init__.py" or service_file.name.startswith(
                "test_"
            ):
                continue

            test_file = self.find_test_file(service_file)

            if test_file:
                validator = ConstructorValidator(test_file, service_file)
                result = validator.validate()
                results.append(result)
            else:
                # No test file found
                results.append(
                    ValidationResult(
                        service_name=service_file.stem,
                        service_file=service_file,
                        test_file=None,
                        parameters=[],
                        tested_parameters=[],
                        missing_tests=[],
                        has_success_test=False,
                        coverage_percent=0.0,
                    )
                )

        return results


def print_validation_report(results: list[ValidationResult]) -> None:
    """Print validation report to stdout.

    Args:
        results: List of validation results
    """
    # Sort by coverage (lowest first)
    results = sorted(results, key=lambda r: r.coverage_percent)

    total_params = sum(len(r.parameters) for r in results)
    total_tested = sum(len(r.tested_parameters) for r in results)
    total_missing = sum(len(r.missing_tests) for r in results)

    print("\n=== Constructor Validation Test Coverage Report ===\n")

    # Summary statistics
    if total_params > 0:
        overall_coverage = (total_tested / total_params) * 100
        print(f"Overall Coverage: {overall_coverage:.1f}%")
        print(f"  Total parameters: {total_params}")
        print(f"  Tested: {total_tested}")
        print(f"  Missing: {total_missing}")
    else:
        print("No constructor parameters found.")

    # Services with missing tests
    incomplete_services = [
        r for r in results if r.coverage_percent < FULL_COVERAGE_PERCENT
    ]

    if incomplete_services:
        print(f"\n--- Incomplete Coverage ({len(incomplete_services)} services) ---\n")

        for result in incomplete_services:
            print(f"{result.service_name}: {result.coverage_percent:.1f}% coverage")
            print(f"  File: {result.service_file}")

            if result.parameters:
                print(f"  Parameters: {', '.join(result.parameters)}")

            if result.missing_tests:
                print(f"  Missing tests for: {', '.join(result.missing_tests)}")

            if not result.has_success_test:
                print(
                    "  Missing: success test (test_constructor_initializes_with_valid_dependencies)"
                )
            print()
    else:
        print("\nAll services have complete constructor validation tests.")

    # Perfect coverage services
    complete_services = [
        r for r in results if r.coverage_percent == FULL_COVERAGE_PERCENT
    ]

    if complete_services:
        print(f"\n--- Complete Coverage ({len(complete_services)} services) ---\n")
        for result in complete_services:
            if result.parameters:  # Only show services with parameters
                print(f"  {result.service_name} ({len(result.parameters)} params)")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate constructor validation test coverage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1] if __doc__ and "Usage:" in __doc__ else "",
    )

    parser.add_argument(
        "test_file",
        nargs="?",
        type=Path,
        help="Path to test file (optional)",
    )

    parser.add_argument(
        "service_file",
        nargs="?",
        type=Path,
        help="Path to service file (optional)",
    )

    parser.add_argument(
        "--scan-all",
        action="store_true",
        help="Scan entire project",
    )

    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("tests/unit"),
        help="Test directory (default: tests/unit)",
    )

    parser.add_argument(
        "--service-dir",
        type=Path,
        default=Path("src"),
        help="Service directory (default: src)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.scan_all:
        # Check directories exist
        if not args.test_dir.exists():
            print(f"Error: Test directory not found: {args.test_dir}", file=sys.stderr)
            sys.exit(1)

        if not args.service_dir.exists():
            print(
                f"Error: Service directory not found: {args.service_dir}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Scan entire project
        scanner = ProjectScanner(args.test_dir, args.service_dir)
        results = scanner.scan()
        print_validation_report(results)

    elif args.test_file and args.service_file:
        # Validate specific pair
        if not args.test_file.exists():
            print(f"Error: Test file not found: {args.test_file}", file=sys.stderr)
            sys.exit(1)

        if not args.service_file.exists():
            print(
                f"Error: Service file not found: {args.service_file}", file=sys.stderr
            )
            sys.exit(1)

        validator = ConstructorValidator(args.test_file, args.service_file)
        result = validator.validate()

        print(f"\n=== Validation Result for {result.service_name} ===\n")
        print(f"Coverage: {result.coverage_percent:.1f}%")

        if result.parameters:
            print(f"\nConstructor parameters ({len(result.parameters)}):")
            for param in result.parameters:
                status = "tested" if param in result.tested_parameters else "MISSING"
                print(f"  - {param}: {status}")

        if result.missing_tests:
            print(f"\nMissing validation tests ({len(result.missing_tests)}):")
            for param in result.missing_tests:
                print(f"  - test_constructor_fails_when_{param}_is_none")

        if not result.has_success_test:
            print("\nMissing success test:")
            print("  - test_constructor_initializes_with_valid_dependencies")

        if result.coverage_percent == FULL_COVERAGE_PERCENT and result.has_success_test:
            print("\nResult: PASS - All constructor validation tests present")
        else:
            print("\nResult: FAIL - Missing constructor validation tests")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
