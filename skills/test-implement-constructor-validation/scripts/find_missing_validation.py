#!/usr/bin/env python3
"""Find services missing constructor validation tests.

This script scans all service files and identifies which ones are missing
constructor validation tests. It prioritizes services by:
- Number of constructor parameters
- Service criticality (based on location/usage)
- Whether test file exists at all

Output includes actionable recommendations for which tests to write first.

Usage:
    cd <project-root>
    python -m skills.test-implement-constructor-validation.scripts.find_missing_validation
    python -m skills.test-implement-constructor-validation.scripts.find_missing_validation --json
    python -m skills.test-implement-constructor-validation.scripts.find_missing_validation --top 10
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

# Setup: Add .claude to path for skill_utils and tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.ast_utils import parse_python_file
from tools.skill_utils import ensure_path_setup

if TYPE_CHECKING:
    import ast

ensure_path_setup()


# Constants
MIN_TEST_METHOD_PARTS = (
    5  # test_constructor_fails_when_{param}_is_none has at least 5 parts
)


@dataclass
class MissingTest:
    """Information about a missing test."""

    service_name: str
    service_file: str
    test_file: str | None
    parameter_count: int
    parameters: list[str]
    has_test_file: bool
    has_test_class: bool
    missing_validation_count: int
    missing_success_test: bool
    priority_score: int
    criticality: str


class ServiceAnalyzer:
    """Analyze service files for constructor validation tests."""

    def __init__(self, service_dir: Path, test_dir: Path) -> None:
        """Initialize analyzer.

        Args:
            service_dir: Directory containing service files
            test_dir: Directory containing test files
        """
        self.service_dir = service_dir
        self.test_dir = test_dir

    def calculate_criticality(self, service_file: Path) -> str:
        """Calculate service criticality based on location.

        Args:
            service_file: Path to service file

        Returns:
            Criticality level: HIGH, MEDIUM, LOW
        """
        path_str = str(service_file)

        # High criticality patterns
        high_patterns = [
            "orchestrat",
            "pipeline",
            "indexing",
            "embedding",
            "search",
        ]
        if any(pattern in path_str.lower() for pattern in high_patterns):
            return "HIGH"

        # Medium criticality patterns
        medium_patterns = [
            "service",
            "handler",
            "processor",
            "manager",
        ]
        if any(pattern in path_str.lower() for pattern in medium_patterns):
            return "MEDIUM"

        return "LOW"

    def extract_constructor_params(self, service_file: Path) -> tuple[str, list[str]]:
        """Extract service name and constructor parameters.

        Args:
            service_file: Path to service file

        Returns:
            Tuple of (service_name, parameter_names)
        """
        import ast

        tree = parse_python_file(service_file)
        if tree is None:
            return "", []

        # Find service class (non-test class)
        service_class: ast.ClassDef | None = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("Test"):
                service_class = node
                break

        if not service_class:
            return "", []

        # Find __init__ method
        init_method: ast.FunctionDef | None = None
        for node in service_class.body:
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                init_method = node
                break

        if not init_method:
            return service_class.name, []

        # Extract parameters (excluding self)
        parameters = [arg.arg for arg in init_method.args.args if arg.arg != "self"]

        return service_class.name, parameters

    def find_test_file(self, service_file: Path) -> Path | None:
        """Find corresponding test file.

        Args:
            service_file: Path to service file

        Returns:
            Path to test file or None
        """
        test_name = f"test_{service_file.stem}.py"

        for test_file in self.test_dir.rglob(test_name):
            return test_file

        return None

    def check_test_coverage(
        self, test_file: Path | None, service_name: str, parameters: list[str]
    ) -> tuple[bool, bool, int]:
        """Check test coverage for service.

        Args:
            test_file: Path to test file
            service_name: Name of service class
            parameters: List of constructor parameters

        Returns:
            Tuple of (has_test_class, has_success_test, missing_validation_count)
        """
        import ast

        if not test_file or not test_file.exists():
            return False, False, len(parameters)

        tree = parse_python_file(test_file)
        if tree is None:
            return False, False, len(parameters)

        # Find test class
        test_class_name = f"Test{service_name}Constructor"
        test_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == test_class_name:
                test_class = node
                break

        if not test_class:
            return False, False, len(parameters)

        # Check for tests
        has_success_test = False
        tested_params = set()

        for node in test_class.body:
            if isinstance(node, ast.FunctionDef):
                # Success test
                if "initializes_with_valid_dependencies" in node.name:
                    has_success_test = True

                # Validation tests
                if node.name.startswith("test_constructor_fails_when_"):
                    parts = node.name.split("_")
                    if (
                        len(parts) >= MIN_TEST_METHOD_PARTS
                        and parts[-2] == "is"
                        and parts[-1] == "none"
                    ):
                        param_name = "_".join(parts[4:-2])
                        tested_params.add(param_name)

        missing_count = len([p for p in parameters if p not in tested_params])

        return True, has_success_test, missing_count

    def calculate_priority(
        self,
        param_count: int,
        criticality: str,
        missing_count: int,
        has_test_file: bool,
    ) -> int:
        """Calculate priority score for fixing missing tests.

        Higher score = higher priority.

        Args:
            param_count: Number of constructor parameters
            criticality: Service criticality level
            missing_count: Number of missing validation tests
            has_test_file: Whether test file exists

        Returns:
            Priority score (0-100)
        """
        score = 0

        # Weight by number of parameters (more params = higher priority)
        score += min(param_count * 5, 30)

        # Weight by criticality
        criticality_weights = {"HIGH": 30, "MEDIUM": 20, "LOW": 10}
        score += criticality_weights.get(criticality, 10)

        # Weight by missing count
        score += min(missing_count * 3, 20)

        # Penalty if test file exists but incomplete (easier to fix)
        if has_test_file:
            score += 10

        return min(score, 100)

    def analyze(self) -> list[MissingTest]:
        """Analyze all services and find missing tests.

        Returns:
            List of MissingTest objects
        """
        missing_tests = []

        service_files = list(self.service_dir.rglob("*.py"))

        for service_file in service_files:
            # Skip __init__.py and test files
            if service_file.name == "__init__.py" or service_file.name.startswith(
                "test_"
            ):
                continue

            # Extract constructor info
            service_name, parameters = self.extract_constructor_params(service_file)

            if not service_name or not parameters:
                # Skip services without constructors or parameters
                continue

            # Find test file
            test_file = self.find_test_file(service_file)

            # Check coverage
            has_test_class, has_success_test, missing_count = self.check_test_coverage(
                test_file, service_name, parameters
            )

            # Only include if missing tests
            if missing_count > 0 or not has_success_test:
                criticality = self.calculate_criticality(service_file)
                priority = self.calculate_priority(
                    len(parameters),
                    criticality,
                    missing_count,
                    test_file is not None,
                )

                missing = MissingTest(
                    service_name=service_name,
                    service_file=str(service_file),
                    test_file=str(test_file) if test_file else None,
                    parameter_count=len(parameters),
                    parameters=parameters,
                    has_test_file=test_file is not None,
                    has_test_class=has_test_class,
                    missing_validation_count=missing_count,
                    missing_success_test=not has_success_test,
                    priority_score=priority,
                    criticality=criticality,
                )

                missing_tests.append(missing)

        # Sort by priority (highest first)
        missing_tests.sort(key=lambda m: m.priority_score, reverse=True)

        return missing_tests


def print_text_report(
    missing_tests: list[MissingTest], top_n: int | None = None
) -> None:
    """Print text report of missing tests.

    Args:
        missing_tests: List of missing test information
        top_n: Show only top N results, or None for all
    """
    if top_n:
        missing_tests = missing_tests[:top_n]

    if not missing_tests:
        print("All services have complete constructor validation tests.")
        return

    # Summary by criticality
    high = [m for m in missing_tests if m.criticality == "HIGH"]
    medium = [m for m in missing_tests if m.criticality == "MEDIUM"]
    low = [m for m in missing_tests if m.criticality == "LOW"]

    print(
        f"\nFound {len(missing_tests)} services missing constructor validation tests:"
    )
    print(f"  HIGH criticality: {len(high)}")
    print(f"  MEDIUM criticality: {len(medium)}")
    print(f"  LOW criticality: {len(low)}")

    # Detailed list
    print("\n--- Services Missing Tests ---\n")
    for i, missing in enumerate(missing_tests, 1):
        print(f"{i}. {missing.service_name} (Priority: {missing.priority_score})")
        print(f"   File: {missing.service_file}")
        print(f"   Criticality: {missing.criticality}")
        print(f"   Parameters: {len(missing.parameters)}")

        if missing.missing_validation_count > 0:
            print(f"   Missing validation tests: {missing.missing_validation_count}")

        if missing.missing_success_test:
            print("   Missing success test: Yes")

        if not missing.has_test_file:
            print("   Status: No test file exists")
        elif not missing.has_test_class:
            print("   Status: Test file exists but no constructor test class")
        else:
            print("   Status: Test class exists but incomplete")
        print()

    # Actionable recommendations
    print("\n--- Recommendations ---\n")

    if high:
        print(f"1. Focus on HIGH criticality services first ({len(high)} services)")

    no_test_file = [m for m in missing_tests if not m.has_test_file]
    if no_test_file:
        print(
            f"2. Create test files for {len(no_test_file)} services without test files"
        )

    incomplete = [m for m in missing_tests if m.has_test_file and not m.has_test_class]
    if incomplete:
        print(
            f"3. Add test classes for {len(incomplete)} services with incomplete tests"
        )

    if missing_tests:
        first = missing_tests[0]
        print(f"\nSuggested first target: {first.service_name}")
        if first.test_file:
            print(f"  Edit: {first.test_file}")
        else:
            suggested_path = first.service_file.replace("src/", "tests/unit/").replace(
                ".py", "_test.py"
            )
            print(f"  Create: {suggested_path}")


def print_json_report(missing_tests: list[MissingTest]) -> None:
    """Print JSON report of missing tests.

    Args:
        missing_tests: List of missing test information
    """
    report = {
        "total": len(missing_tests),
        "by_criticality": {
            "high": len([m for m in missing_tests if m.criticality == "HIGH"]),
            "medium": len([m for m in missing_tests if m.criticality == "MEDIUM"]),
            "low": len([m for m in missing_tests if m.criticality == "LOW"]),
        },
        "services": [asdict(m) for m in missing_tests],
    }
    print(json.dumps(report, indent=2))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Find services missing constructor validation tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1] if __doc__ and "Usage:" in __doc__ else "",
    )

    parser.add_argument(
        "--service-dir",
        type=Path,
        default=Path("src"),
        help="Service directory to scan (default: src)",
    )

    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("tests/unit"),
        help="Test directory (default: tests/unit)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (for automation)",
    )

    parser.add_argument(
        "--top",
        type=int,
        metavar="N",
        help="Show only top N priorities",
    )

    args = parser.parse_args()

    # Validate directories
    if not args.service_dir.exists():
        print(
            f"Error: Service directory not found: {args.service_dir}", file=sys.stderr
        )
        sys.exit(1)

    if not args.test_dir.exists():
        print(f"Error: Test directory not found: {args.test_dir}", file=sys.stderr)
        sys.exit(1)

    # Analyze services
    analyzer = ServiceAnalyzer(args.service_dir, args.test_dir)
    missing_tests = analyzer.analyze()

    # Output results
    if args.json:
        print_json_report(missing_tests)
    else:
        print_text_report(missing_tests, args.top)


if __name__ == "__main__":
    main()
