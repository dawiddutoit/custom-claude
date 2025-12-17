#!/usr/bin/env python3
"""Validate test placement across test pyramid layers.

This script scans all test files and validates they are placed in the correct
layer (unit/integration/e2e) based on their dependencies, mocking patterns,
and test scope.

Usage:
    python validate_test_placement.py tests/
    python validate_test_placement.py tests/unit/
    python validate_test_placement.py --format json
    python validate_test_placement.py --fix
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

type TestLayer = Literal["unit", "integration", "e2e", "unknown"]


@dataclass(frozen=True, slots=True)
class TestAnalysis:
    """Analysis result for a test file."""

    file_path: Path
    current_layer: TestLayer
    detected_layer: TestLayer
    is_correct: bool
    reasons: tuple[str, ...]
    fixtures_used: tuple[str, ...]
    mocks_count: int
    real_fixtures_count: int
    imports: tuple[str, ...]
    pytest_markers: tuple[str, ...]


class TestLayerDetector(ast.NodeVisitor):
    """AST visitor to detect test layer from code patterns."""

    # Known fixture patterns (class-level constants)
    UNIT_FIXTURES: frozenset[str] = frozenset(
        {
            "mock_config",
            "temp_dir",
            "mock_neo4j_rag",
            "mock_repository_monitor",
            "mcp_client_with_mocks",
        }
    )
    INTEGRATION_FIXTURES: frozenset[str] = frozenset(
        {
            "real_settings",
            "neo4j_database",
            "neo4j_driver",
            "test_database",
            "real_neo4j_driver",
        }
    )
    E2E_FIXTURES: frozenset[str] = frozenset(
        {
            "indexed_real_codebase",
            "search_handler",
            "real_embeddings_provider",
            "real_neo4j_rag",
        }
    )

    def __init__(self) -> None:
        """Initialize the detector."""
        self.fixtures_used: set[str] = set()
        self.mocks_count: int = 0
        self.real_fixtures: set[str] = set()
        self.imports: list[str] = []
        self.pytest_markers: list[str] = []
        self.has_async_tests: bool = False
        self.has_database_calls: bool = False
        self.has_network_calls: bool = False

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports."""
        for alias in node.names:
            self.imports.append(alias.name)
            if "mock" in alias.name.lower():
                self.mocks_count += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        if node.module:
            self.imports.append(node.module)
            if "mock" in node.module.lower():
                self.mocks_count += 1
        for alias in node.names:
            if "mock" in alias.name.lower():
                self.mocks_count += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze test functions."""
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Analyze async test functions."""
        self.has_async_tests = True
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Common analysis for sync and async functions."""
        # Check pytest markers
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if (
                    isinstance(decorator.value, ast.Name)
                    and decorator.value.id == "pytest"
                ):
                    if isinstance(decorator.attr, str):
                        self.pytest_markers.append(decorator.attr)
            elif isinstance(decorator, ast.Call):
                if (
                    isinstance(decorator.func, ast.Attribute)
                    and isinstance(decorator.func.value, ast.Name)
                    and decorator.func.value.id == "pytest"
                    and isinstance(decorator.func.attr, str)
                ):
                    self.pytest_markers.append(decorator.func.attr)

        # Extract fixtures from parameters
        for arg in node.args.args:
            fixture_name = arg.arg
            self.fixtures_used.add(fixture_name)

            # Classify fixtures
            if (
                fixture_name in self.INTEGRATION_FIXTURES
                or fixture_name in self.E2E_FIXTURES
            ):
                self.real_fixtures.add(fixture_name)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect mock usage and database/network calls."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if "mock" in func_name.lower():
                self.mocks_count += 1

        # Check for database calls
        if isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            if attr_name in ["execute_query", "run", "fetch", "session"]:
                self.has_database_calls = True

        self.generic_visit(node)


def detect_current_layer(file_path: Path) -> TestLayer:
    """Detect current layer from file path.

    Args:
        file_path: Path to the test file.

    Returns:
        The layer based on directory structure.
    """
    parts = file_path.parts
    if "unit" in parts:
        return "unit"
    if "integration" in parts:
        return "integration"
    if "e2e" in parts:
        return "e2e"
    return "unknown"


def analyze_test_file(file_path: Path) -> TestAnalysis:
    """Analyze a test file and determine correct layer.

    Args:
        file_path: Path to the test file.

    Returns:
        TestAnalysis with current layer, detected layer, and reasons.
    """
    current_layer = detect_current_layer(file_path)

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        return TestAnalysis(
            file_path=file_path,
            current_layer=current_layer,
            detected_layer="unknown",
            is_correct=False,
            reasons=(f"Syntax error: {e}",),
            fixtures_used=(),
            mocks_count=0,
            real_fixtures_count=0,
            imports=(),
            pytest_markers=(),
        )
    except OSError as e:
        return TestAnalysis(
            file_path=file_path,
            current_layer=current_layer,
            detected_layer="unknown",
            is_correct=False,
            reasons=(f"Read error: {e}",),
            fixtures_used=(),
            mocks_count=0,
            real_fixtures_count=0,
            imports=(),
            pytest_markers=(),
        )

    detector = TestLayerDetector()
    detector.visit(tree)

    reasons: list[str] = []

    # Determine detected layer based on patterns
    real_fixtures_count = len(detector.real_fixtures)
    mocks_count = detector.mocks_count

    # Decision logic
    detected_layer: TestLayer = "unknown"

    # E2E indicators
    if any(
        fixture in detector.fixtures_used for fixture in TestLayerDetector.E2E_FIXTURES
    ):
        detected_layer = "e2e"
        reasons.append("Uses E2E fixtures (indexed_real_codebase, search_handler)")
    elif detector.has_database_calls and mocks_count == 0:
        detected_layer = "e2e"
        reasons.append("Direct database calls without mocks")
    # Integration indicators
    elif real_fixtures_count > 0:
        detected_layer = "integration"
        reasons.append(f"Uses {real_fixtures_count} real infrastructure fixtures")
    elif detector.has_database_calls and mocks_count > 0:
        detected_layer = "integration"
        reasons.append("Uses real database with some mocking")
    # Unit indicators
    elif mocks_count > 0 and real_fixtures_count == 0:
        detected_layer = "unit"
        reasons.append("Uses mocks without real infrastructure")
    elif not detector.has_database_calls and not detector.has_network_calls:
        detected_layer = "unit"
        reasons.append("No external dependencies detected")

    # Check pytest markers
    if "unit" in detector.pytest_markers:
        if detected_layer != "unit":
            reasons.append(f"Marker says 'unit' but detected as '{detected_layer}'")
        detected_layer = "unit"
    elif "integration" in detector.pytest_markers:
        if detected_layer != "integration":
            reasons.append(
                f"Marker says 'integration' but detected as '{detected_layer}'"
            )
        detected_layer = "integration"
    elif "e2e" in detector.pytest_markers:
        if detected_layer != "e2e":
            reasons.append(f"Marker says 'e2e' but detected as '{detected_layer}'")
        detected_layer = "e2e"

    is_correct = current_layer == detected_layer

    return TestAnalysis(
        file_path=file_path,
        current_layer=current_layer,
        detected_layer=detected_layer,
        is_correct=is_correct,
        reasons=tuple(reasons),
        fixtures_used=tuple(detector.fixtures_used),
        mocks_count=mocks_count,
        real_fixtures_count=real_fixtures_count,
        imports=tuple(detector.imports),
        pytest_markers=tuple(detector.pytest_markers),
    )


def scan_tests(test_dir: Path) -> list[TestAnalysis]:
    """Scan all test files in directory.

    Args:
        test_dir: Directory to scan.

    Returns:
        List of TestAnalysis results.
    """
    results: list[TestAnalysis] = []
    for test_file in test_dir.rglob("test_*.py"):
        if "__pycache__" in str(test_file):
            continue
        results.append(analyze_test_file(test_file))
    return results


def generate_report(
    analyses: list[TestAnalysis], output_format: Literal["text", "json"] = "text"
) -> str:
    """Generate validation report.

    Args:
        analyses: List of test analysis results.
        output_format: Either "text" or "json".

    Returns:
        Formatted report string.
    """
    if output_format == "json":
        return json.dumps(
            [
                {
                    "file": str(a.file_path),
                    "current_layer": a.current_layer,
                    "detected_layer": a.detected_layer,
                    "is_correct": a.is_correct,
                    "reasons": list(a.reasons),
                    "fixtures": list(a.fixtures_used),
                    "mocks": a.mocks_count,
                    "real_fixtures": a.real_fixtures_count,
                }
                for a in analyses
            ],
            indent=2,
        )

    # Text report
    total = len(analyses)
    if total == 0:
        return "No test files found"

    correct = sum(1 for a in analyses if a.is_correct)
    incorrect = total - correct

    report_lines: list[str] = [
        "=" * 80,
        "TEST LAYER VALIDATION REPORT",
        "=" * 80,
        "",
        f"Total tests analyzed: {total}",
        f"Correctly placed: {correct} ({correct / total * 100:.1f}%)",
        f"Incorrectly placed: {incorrect} ({incorrect / total * 100:.1f}%)",
        "",
    ]

    # Layer distribution
    layer_counts: dict[str, int] = defaultdict(int)
    for analysis in analyses:
        layer_counts[analysis.current_layer] += 1

    report_lines.append("Current distribution:")
    for layer, count in sorted(layer_counts.items()):
        pct = count / total * 100
        report_lines.append(f"  {layer}: {count} ({pct:.1f}%)")
    report_lines.append("")

    # Misplaced tests
    if incorrect > 0:
        report_lines.append("MISPLACED TESTS:")
        report_lines.append("-" * 80)
        for analysis in analyses:
            if not analysis.is_correct:
                report_lines.append(f"\nFile: {analysis.file_path}")
                report_lines.append(f"   Current: {analysis.current_layer}")
                report_lines.append(f"   Should be: {analysis.detected_layer}")
                report_lines.append("   Reasons:")
                for reason in analysis.reasons:
                    report_lines.append(f"     - {reason}")
                fixtures_str = ", ".join(analysis.fixtures_used) or "None"
                report_lines.append(f"   Fixtures: {fixtures_str}")
                report_lines.append(f"   Mocks: {analysis.mocks_count}")
                report_lines.append(f"   Real fixtures: {analysis.real_fixtures_count}")
    else:
        report_lines.append("[OK] All tests are correctly placed!")

    return "\n".join(report_lines)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 if all tests correctly placed, 1 otherwise.
    """
    parser = argparse.ArgumentParser(
        description="Validate test placement in test pyramid layers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="tests",
        help="Path to scan (default: tests/)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Generate move commands for misplaced tests",
    )

    args = parser.parse_args()

    test_dir = Path(args.path)
    if not test_dir.exists():
        print(f"Error: Directory not found: {test_dir}", file=sys.stderr)
        return 1

    analyses = scan_tests(test_dir)
    report = generate_report(analyses, args.format)
    print(report)

    if args.fix:
        misplaced = [a for a in analyses if not a.is_correct]
        if misplaced:
            print("\nSuggested move commands:")
            for analysis in misplaced:
                old_path = analysis.file_path
                # Generate new path
                new_parts = list(old_path.parts)
                for i, part in enumerate(new_parts):
                    if part in ["unit", "integration", "e2e"]:
                        new_parts[i] = analysis.detected_layer
                        break
                new_path = Path(*new_parts)
                print(f"  python move_test.py {old_path} {new_path}")

    # Exit with error if any tests are misplaced
    incorrect_count = sum(1 for a in analyses if not a.is_correct)
    return 1 if incorrect_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
