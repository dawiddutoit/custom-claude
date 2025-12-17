#!/usr/bin/env python3
"""Move test files to correct layer with automatic import and fixture updates.

This script intelligently moves test files between layers (unit/integration/e2e),
automatically updating imports, fixture dependencies, and conftest references.

Usage:
    python move_test.py tests/unit/test_foo.py tests/integration/test_foo.py
    python move_test.py tests/unit/test_foo.py --auto
    python move_test.py tests/unit/test_foo.py --dry-run
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any, Literal

type TestLayer = Literal["unit", "integration", "e2e", "unknown"]


class ImportUpdater(ast.NodeTransformer):
    """AST transformer to update imports when moving between layers."""

    def __init__(self, old_layer: str, new_layer: str) -> None:
        self.old_layer = old_layer
        self.new_layer = new_layer
        self.changes_made = 0

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Update relative imports."""
        if node.module and "conftest" in node.module:
            # Update conftest imports
            if self.old_layer in node.module:
                node.module = node.module.replace(self.old_layer, self.new_layer)
                self.changes_made += 1
        return node


def detect_layer(file_path: Path) -> TestLayer:
    """Detect test layer from file path.

    Args:
        file_path: Path to the test file.

    Returns:
        The detected layer based on directory structure.
    """
    parts = file_path.parts
    if "unit" in parts:
        return "unit"
    if "integration" in parts:
        return "integration"
    if "e2e" in parts:
        return "e2e"
    return "unknown"


def get_fixture_mapping(old_layer: str, new_layer: str) -> dict[str, str]:
    """Get fixture name mappings when moving between layers.

    Args:
        old_layer: Source layer name.
        new_layer: Target layer name.

    Returns:
        Dictionary mapping old fixture names to new fixture names.
    """
    # Map old fixtures to new fixtures
    if old_layer == "unit" and new_layer == "integration":
        return {
            "mock_config": "real_settings",
            "mock_neo4j_rag": "neo4j_database",
            "temp_dir": "test_database",
        }
    if old_layer == "integration" and new_layer == "unit":
        return {
            "real_settings": "mock_config",
            "neo4j_database": "mock_neo4j_rag",
            "neo4j_driver": "mock_neo4j_rag",
        }
    if old_layer == "unit" and new_layer == "e2e":
        return {
            "mock_config": "real_settings",
            "mock_neo4j_rag": "search_handler",
        }
    if old_layer == "integration" and new_layer == "e2e":
        return {
            "neo4j_database": "indexed_real_codebase",
        }
    return {}


def update_fixtures_in_content(content: str, fixture_mapping: dict[str, str]) -> str:
    """Update fixture names in test content.

    Args:
        content: The file content to update.
        fixture_mapping: Dictionary mapping old fixture names to new ones.

    Returns:
        Updated content with fixture names replaced.
    """
    for old_fixture, new_fixture in fixture_mapping.items():
        # Update function parameters
        content = re.sub(
            rf"\b{old_fixture}\b(?=\s*[,)])",
            new_fixture,
            content,
        )
    return content


def update_pytest_markers(content: str, old_layer: str, new_layer: str) -> str:
    """Update pytest.mark decorators.

    Args:
        content: The file content to update.
        old_layer: The source layer name.
        new_layer: The target layer name.

    Returns:
        Updated content with pytest markers replaced.
    """
    return re.sub(
        rf"@pytest\.mark\.{old_layer}\b",
        f"@pytest.mark.{new_layer}",
        content,
    )


def update_imports_for_layer(content: str, new_layer: str) -> str:
    """Update imports based on target layer.

    Args:
        content: The file content to update.
        new_layer: The target layer name.

    Returns:
        Updated content with imports adjusted for the target layer.
    """
    lines = content.split("\n")
    updated_lines: list[str] = []

    for line in lines:
        # Remove mock imports if moving to integration/e2e
        if new_layer in ["integration", "e2e"]:
            if "from unittest.mock import" in line or "import unittest.mock" in line:
                # Keep the line but add comment
                if line.strip():
                    updated_lines.append(
                        f"# {line}  # TODO: Remove mocks for {new_layer} test"
                    )
                continue

        updated_lines.append(line)

    # Add mock import for unit tests if not present
    if new_layer == "unit":
        has_mock_import = any(
            "from unittest.mock import" in line for line in updated_lines
        )
        if not has_mock_import:
            # Find first import and insert after
            for i, line in enumerate(updated_lines):
                if line.startswith(("import ", "from ")):
                    updated_lines.insert(i, "from unittest.mock import AsyncMock, Mock")
                    break

    return "\n".join(updated_lines)


def move_test_file(
    source: Path,
    target: Path,
    *,
    dry_run: bool = False,
    update_content: bool = True,
) -> dict[str, Any]:
    """Move test file and update its contents.

    Args:
        source: Source file path.
        target: Target file path.
        dry_run: If True, only report changes without moving.
        update_content: If True, update markers/fixtures/imports.

    Returns:
        Dictionary with success status, changes made, and paths.
    """
    if not source.exists():
        return {
            "success": False,
            "error": f"Source file does not exist: {source}",
        }

    old_layer = detect_layer(source)
    new_layer = detect_layer(target)

    if old_layer == "unknown" or new_layer == "unknown":
        return {
            "success": False,
            "error": f"Cannot determine layer from paths: {source} -> {target}",
        }

    changes: list[str] = []

    # Read original content
    content = source.read_text(encoding="utf-8")
    original_content = content

    if update_content:
        # Update pytest markers
        content = update_pytest_markers(content, old_layer, new_layer)
        changes.append(f"Updated pytest.mark.{old_layer} -> pytest.mark.{new_layer}")

        # Update fixtures
        fixture_mapping = get_fixture_mapping(old_layer, new_layer)
        if fixture_mapping:
            content = update_fixtures_in_content(content, fixture_mapping)
            changes.append(f"Updated fixtures: {', '.join(fixture_mapping.keys())}")

        # Update imports
        content = update_imports_for_layer(content, new_layer)
        changes.append(f"Updated imports for {new_layer} layer")

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "changes": changes,
            "old_path": str(source),
            "new_path": str(target),
            "content_changed": content != original_content,
        }

    # Create target directory
    target.parent.mkdir(parents=True, exist_ok=True)

    # Write updated content to target
    target.write_text(content, encoding="utf-8")

    # Remove source file
    source.unlink()

    return {
        "success": True,
        "dry_run": False,
        "changes": changes,
        "old_path": str(source),
        "new_path": str(target),
        "content_changed": content != original_content,
    }


def auto_detect_target(source: Path) -> Path:
    """Auto-detect target path based on test analysis.

    Uses validate_test_placement module to analyze the test file
    and determine the correct layer.

    Args:
        source: Source file path.

    Returns:
        Target path (same as source if correctly placed, or new path).
    """
    # Import from validation script (sibling module)
    script_dir = Path(__file__).parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    try:
        from validate_test_placement import analyze_test_file

        analysis = analyze_test_file(source)
        if analysis.is_correct:
            return source

        # Generate target path
        new_parts = list(source.parts)
        for i, part in enumerate(new_parts):
            if part in ["unit", "integration", "e2e"]:
                new_parts[i] = analysis.detected_layer
                break

        return Path(*new_parts)
    except ImportError:
        # Fallback: return source unchanged
        return source


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    parser = argparse.ArgumentParser(
        description="Move test files between layers with automatic updates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Manual move
  python move_test.py tests/unit/test_foo.py tests/integration/test_foo.py

  # Auto-detect target layer
  python move_test.py tests/unit/test_foo.py --auto

  # Preview changes without moving
  python move_test.py tests/unit/test_foo.py tests/integration/test_foo.py --dry-run
        """,
    )
    parser.add_argument("source", help="Source test file path")
    parser.add_argument("target", nargs="?", help="Target test file path")
    parser.add_argument("--auto", action="store_true", help="Auto-detect target layer")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without moving"
    )
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Move file without updating content",
    )

    args = parser.parse_args()

    source = Path(args.source)

    if args.auto:
        target = auto_detect_target(source)
        if target == source:
            print(f"Test already in correct layer: {source}")
            return 0
    elif args.target:
        target = Path(args.target)
    else:
        print("Error: Either --auto or target path required", file=sys.stderr)
        return 1

    result = move_test_file(
        source=source,
        target=target,
        dry_run=args.dry_run,
        update_content=not args.no_update,
    )

    if not result["success"]:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        return 1

    # Print results
    mode = "[DRY RUN] " if result.get("dry_run") else ""
    print(f"{mode}Move: {result['old_path']} -> {result['new_path']}")

    if result.get("changes"):
        print("Changes:")
        for change in result["changes"]:
            print(f"  - {change}")

    if result.get("content_changed"):
        print("Content was modified")

    if result.get("dry_run"):
        print("\nNo files were modified (dry run)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
