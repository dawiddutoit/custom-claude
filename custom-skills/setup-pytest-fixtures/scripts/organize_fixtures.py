#!/usr/bin/env python3
"""Reorganize pytest fixtures by layer and update imports.

This script organizes fixtures according to project structure:
- tests/utils/ - Centralized reusable fixtures
- tests/unit/conftest.py - Unit test specific fixtures
- tests/integration/conftest.py - Integration test specific fixtures
- tests/e2e/conftest.py - E2E test specific fixtures
- tests/conftest.py - Main conftest with imports

Usage:
    # Dry run to preview changes
    python organize_fixtures.py --dry-run

    # Move fixtures to proper locations
    python organize_fixtures.py --move

    # Validate organization
    python organize_fixtures.py --validate

    # Generate conftest.py imports
    python organize_fixtures.py --generate-imports

Examples:
    # Preview organization changes
    python organize_fixtures.py --dry-run

    # Move fixtures and update imports
    python organize_fixtures.py --move --update-imports

    # Validate current organization
    python organize_fixtures.py --validate

    # Generate main conftest.py with all imports
    python organize_fixtures.py --generate-imports --output tests/conftest.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any, Literal

# Setup: Add .claude/tools to path for shared utilities
_CLAUDE_ROOT = Path(__file__).parent.parent.parent.parent
if str(_CLAUDE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CLAUDE_ROOT))

from tools.skill_utils import ensure_path_setup  # noqa: E402

ensure_path_setup()

# Type aliases
FixtureCategory = Literal["settings", "drivers", "services", "helpers", "other"]


class FixtureOrganizer:
    """Organize fixtures by layer and maintain imports."""

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize fixture organizer.

        Args:
            project_root: Path to project root (auto-detected if None)
        """
        self.project_root = project_root or self._find_project_root()
        self.fixtures: dict[str, dict[str, Any]] = {}
        self.moves: list[dict[str, Any]] = []

    @staticmethod
    def _find_project_root() -> Path:
        """Find project root by looking for pyproject.toml.

        Returns:
            Path to project root directory.
        """
        from tools.skill_utils import get_project_root

        return get_project_root()

    def analyze_fixtures(self) -> None:
        """Analyze all fixtures and determine proper organization."""
        # Find all fixtures
        test_files = list((self.project_root / "tests").rglob("*.py"))

        for test_file in test_files:
            if test_file.name.startswith("__"):
                continue

            self._analyze_file(test_file)

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze fixtures in a file.

        Args:
            file_path: Path to file to analyze
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if self._is_fixture_decorator(decorator):
                            fixture_info = self._extract_fixture_info(node, file_path)
                            self.fixtures[node.name] = fixture_info

                            # Determine target location
                            target = self._determine_target_location(fixture_info)
                            if target != file_path:
                                self.moves.append(
                                    {
                                        "fixture": node.name,
                                        "from": file_path,
                                        "to": target,
                                        "reason": self._get_move_reason(fixture_info),
                                    }
                                )

        except Exception:
            pass

    def _is_fixture_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is a pytest fixture."""
        if isinstance(decorator, ast.Name):
            return decorator.id == "fixture"
        if isinstance(decorator, ast.Attribute):
            return decorator.attr == "fixture"
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id == "fixture"
            if isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr == "fixture"
        return False

    def _extract_fixture_info(
        self, node: ast.FunctionDef, file_path: Path
    ) -> dict[str, Any]:
        """Extract fixture information."""
        return {
            "name": node.name,
            "file": file_path,
            "is_mock": node.name.startswith("mock_"),
            "is_factory": "factory" in node.name,
            "is_helper": any(
                word in node.name
                for word in ["helper", "env", "clean", "custom", "test_settings"]
            ),
            "is_real": node.name.startswith("real_"),
            "category": self._categorize_fixture(node.name),
        }

    def _categorize_fixture(self, name: str) -> FixtureCategory:
        """Categorize fixture by type.

        Args:
            name: Fixture name

        Returns:
            Category name (settings, drivers, services, helpers, or other)
        """
        if "setting" in name or "config" in name:
            return "settings"
        if "driver" in name or "connection" in name:
            return "drivers"
        if "service" in name or "repository" in name:
            return "services"
        if "env" in name or "helper" in name:
            return "helpers"
        return "other"

    def _determine_target_location(self, fixture_info: dict[str, Any]) -> Path:
        """Determine where fixture should be located.

        Args:
            fixture_info: Fixture information

        Returns:
            Path: Target file path
        """
        current_file = fixture_info["file"]

        # If fixture is reusable (mock/factory), it belongs in tests/utils/
        if (
            fixture_info["is_mock"]
            or fixture_info["is_factory"]
            or fixture_info["is_helper"]
        ):
            # Determine utils file based on category
            category = fixture_info["category"]
            if category == "settings":
                return self.project_root / "tests" / "utils" / "mock_settings.py"
            if category == "drivers":
                return self.project_root / "tests" / "utils" / "mock_drivers.py"
            if category == "services":
                return self.project_root / "tests" / "utils" / "mock_services.py"
            if category == "helpers":
                return (
                    self.project_root / "tests" / "utils" / "environmental_helpers.py"
                )
            return self.project_root / "tests" / "utils" / f"mock_{category}.py"

        # If fixture is in a test file, it should move to layer conftest
        if current_file.name.startswith("test_"):
            # Determine layer
            if "unit" in str(current_file):
                return self.project_root / "tests" / "unit" / "conftest.py"
            if "integration" in str(current_file):
                return self.project_root / "tests" / "integration" / "conftest.py"
            if "e2e" in str(current_file):
                return self.project_root / "tests" / "e2e" / "conftest.py"

        # Already in correct location
        return current_file

    def _get_move_reason(self, fixture_info: dict[str, Any]) -> str:
        """Get reason for moving fixture.

        Args:
            fixture_info: Fixture information

        Returns:
            str: Reason for move
        """
        if fixture_info["is_mock"]:
            return f"Mock fixture belongs in tests/utils/mock_{fixture_info['category']}.py"
        if fixture_info["is_factory"]:
            return "Factory fixture is reusable, belongs in tests/utils/"
        if fixture_info["is_helper"]:
            return "Helper fixture belongs in tests/utils/environmental_helpers.py"
        return "Layer-specific fixture belongs in layer conftest.py"

    def generate_conftest_imports(self) -> str:
        """Generate main conftest.py with imports.

        Returns:
            str: Generated conftest.py content
        """
        # Group fixtures by file
        fixtures_by_file: dict[Path, list[str]] = {}

        for fixture_name, info in self.fixtures.items():
            target = self._determine_target_location(info)
            if target not in fixtures_by_file:
                fixtures_by_file[target] = []
            fixtures_by_file[target].append(fixture_name)

        # Generate imports
        imports = []
        all_fixtures = []

        # Sort by utils file
        utils_files = sorted([f for f in fixtures_by_file if "utils" in str(f)])

        for file_path in utils_files:
            module_name = file_path.stem  # e.g., mock_settings
            fixtures = sorted(fixtures_by_file[file_path])

            if fixtures:
                import_line = f"from tests.utils.{module_name} import (\n"
                import_line += ",\n".join(f"    {fixture}" for fixture in fixtures)
                import_line += ",\n)"
                imports.append(import_line)
                all_fixtures.extend(fixtures)

        # Generate __all__
        all_section = "__all__ = [\n"
        all_section += ",\n".join(
            f'    "{fixture}"' for fixture in sorted(all_fixtures)
        )
        all_section += ",\n]"

        # Combine
        conftest_content = '''"""Main conftest file to make fixtures available to all tests."""

from pathlib import Path

# Load .env file for integration tests
try:
    from dotenv import load_dotenv

    # Find .env file in project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded .env from {env_file}")
except ImportError:
    # python-dotenv not installed, skip
    pass

# Import fixtures from utils to make them available throughout test suite
'''

        conftest_content += "\n".join(imports)
        conftest_content += "\n\n"
        conftest_content += all_section
        conftest_content += "\n"

        return conftest_content

    def validate_organization(self) -> dict[str, Any]:
        """Validate current fixture organization.

        Returns:
            dict: Validation results
        """
        issues = []
        warnings = []

        for fixture_name, info in self.fixtures.items():
            current = info["file"]
            target = self._determine_target_location(info)

            # Check if fixture is in wrong location
            if current != target:
                issues.append(
                    {
                        "fixture": fixture_name,
                        "current": str(current.relative_to(self.project_root)),
                        "expected": str(target.relative_to(self.project_root)),
                        "reason": self._get_move_reason(info),
                    }
                )

            # Check for naming conventions
            if info["is_mock"] and not fixture_name.startswith("mock_"):
                warnings.append(
                    {
                        "fixture": fixture_name,
                        "issue": "Mock fixture should start with 'mock_'",
                    }
                )

            if info["is_factory"] and not fixture_name.endswith("_factory"):
                warnings.append(
                    {
                        "fixture": fixture_name,
                        "issue": "Factory fixture should end with '_factory'",
                    }
                )

        return {
            "total_fixtures": len(self.fixtures),
            "misplaced_fixtures": len(issues),
            "warnings": len(warnings),
            "issues": issues,
            "warnings_list": warnings,
        }

    def move_fixtures(self, dry_run: bool = True) -> None:
        """Move fixtures to proper locations.

        Args:
            dry_run: If True, only show what would be moved
        """
        if not self.moves:
            print("No fixtures need to be moved.")
            return

        print(f"\n=== {'Proposed' if dry_run else 'Executing'} Fixture Moves ===\n")

        for move in self.moves:
            from_path = move["from"].relative_to(self.project_root)
            to_path = move["to"].relative_to(self.project_root)
            print(f"  {move['fixture']}: {from_path} -> {to_path}")
            print(f"    Reason: {move['reason']}")

            if not dry_run:
                self._perform_move(move)

        if not dry_run:
            print(f"\nMoved {len(self.moves)} fixtures.")

    def _perform_move(self, move: dict[str, Any]) -> None:
        """Actually move a fixture.

        Args:
            move: Move information
        """
        # Read source file
        source_content = move["from"].read_text()
        tree = ast.parse(source_content)

        # Find fixture function
        fixture_code = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == move["fixture"]:
                fixture_code = ast.get_source_segment(source_content, node)
                break

        if not fixture_code:
            return

        # Append to target file
        target = move["to"]
        target.parent.mkdir(parents=True, exist_ok=True)

        if not target.exists():
            # Create new file with header
            header = '''"""Reusable mock fixtures for test components."""

from unittest.mock import MagicMock
import pytest

'''
            target.write_text(header)

        with target.open("a") as f:
            f.write("\n\n")
            f.write(fixture_code)
            f.write("\n")

        # TODO: Remove from source file (requires more sophisticated parsing)

    def print_report(self, validation: dict[str, Any]) -> None:
        """Print validation report to stdout.

        Args:
            validation: Validation results
        """
        print("\n=== Fixture Organization Report ===\n")
        print(f"Total fixtures: {validation['total_fixtures']}")
        print(f"Misplaced fixtures: {validation['misplaced_fixtures']}")
        print(f"Warnings: {validation['warnings']}")

        if validation["issues"]:
            print("\n--- Misplaced Fixtures ---")
            for issue in validation["issues"]:
                print(f"\n  {issue['fixture']}:")
                print(f"    Current: {issue['current']}")
                print(f"    Expected: {issue['expected']}")
                print(f"    Reason: {issue['reason']}")

        if validation["warnings_list"]:
            print("\n--- Naming Warnings ---")
            for warning in validation["warnings_list"]:
                print(f"  {warning['fixture']}: {warning['issue']}")

        if not validation["issues"] and not validation["warnings_list"]:
            print("\nAll fixtures are properly organized.")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Organize pytest fixtures by layer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without moving"
    )
    parser.add_argument(
        "--move", action="store_true", help="Move fixtures to proper locations"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate current organization"
    )
    parser.add_argument(
        "--generate-imports", action="store_true", help="Generate conftest.py imports"
    )
    parser.add_argument("--output", help="Output file path for generated conftest.py")

    args = parser.parse_args()

    # Create organizer
    organizer = FixtureOrganizer()
    organizer.analyze_fixtures()

    # Handle commands
    if args.validate:
        validation = organizer.validate_organization()
        organizer.print_report(validation)

    elif args.generate_imports:
        conftest_content = organizer.generate_conftest_imports()

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(conftest_content)
            print(f"Generated conftest.py written to: {output_path}")
        else:
            print("\n=== Generated conftest.py ===\n")
            print(conftest_content)

    elif args.move:
        organizer.move_fixtures(dry_run=args.dry_run)

    else:
        # Default: show what would be moved
        organizer.move_fixtures(dry_run=True)


if __name__ == "__main__":
    main()
