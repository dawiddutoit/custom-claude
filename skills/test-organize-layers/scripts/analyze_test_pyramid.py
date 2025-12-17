#!/usr/bin/env python3
"""Analyze test distribution across the test pyramid.

This script analyzes the test suite's distribution across layers and compares
it to the ideal test pyramid (70% unit, 20% integration, 10% e2e).

Usage:
    python analyze_test_pyramid.py tests/
    python analyze_test_pyramid.py --format json
    python analyze_test_pyramid.py --ideal-unit 60 --ideal-integration 30 --ideal-e2e 10
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True, slots=True)
class PyramidMetrics:
    """Metrics for test pyramid analysis."""

    total_tests: int
    unit_count: int
    integration_count: int
    e2e_count: int
    unknown_count: int

    @property
    def unit_percentage(self) -> float:
        """Calculate unit test percentage."""
        return (
            (self.unit_count / self.total_tests * 100) if self.total_tests > 0 else 0.0
        )

    @property
    def integration_percentage(self) -> float:
        """Calculate integration test percentage."""
        return (
            (self.integration_count / self.total_tests * 100)
            if self.total_tests > 0
            else 0.0
        )

    @property
    def e2e_percentage(self) -> float:
        """Calculate e2e test percentage."""
        return (
            (self.e2e_count / self.total_tests * 100) if self.total_tests > 0 else 0.0
        )

    @property
    def unknown_percentage(self) -> float:
        """Calculate unknown test percentage."""
        return (
            (self.unknown_count / self.total_tests * 100)
            if self.total_tests > 0
            else 0.0
        )


@dataclass(frozen=True, slots=True)
class PyramidHealth:
    """Health assessment of test pyramid."""

    score: float  # 0-100
    status: Literal["excellent", "good", "needs-improvement", "poor"]
    recommendations: tuple[str, ...]
    warnings: tuple[str, ...]


def count_test_functions(file_path: Path) -> int:
    """Count number of test functions in a file.

    Args:
        file_path: Path to the test file.

    Returns:
        Number of test functions found (functions starting with test_).
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        matches = re.findall(
            r"^\s*(?:async\s+)?def\s+(test_\w+)", content, re.MULTILINE
        )
        return len(matches)
    except OSError:
        return 0


def detect_layer(file_path: Path) -> Literal["unit", "integration", "e2e", "unknown"]:
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


def analyze_pyramid(test_dir: Path) -> PyramidMetrics:
    """Analyze test pyramid distribution.

    Args:
        test_dir: Directory containing test files.

    Returns:
        PyramidMetrics with counts for each layer.
    """
    layer_counts: dict[str, int] = defaultdict(int)

    for test_file in test_dir.rglob("test_*.py"):
        if "__pycache__" in str(test_file):
            continue

        layer = detect_layer(test_file)
        test_count = count_test_functions(test_file)
        layer_counts[layer] += test_count

    total = sum(layer_counts.values())

    return PyramidMetrics(
        total_tests=total,
        unit_count=layer_counts["unit"],
        integration_count=layer_counts["integration"],
        e2e_count=layer_counts["e2e"],
        unknown_count=layer_counts["unknown"],
    )


def assess_pyramid_health(
    metrics: PyramidMetrics, ideal_ratios: dict[str, float]
) -> PyramidHealth:
    """Assess the health of the test pyramid.

    Args:
        metrics: The pyramid metrics to assess.
        ideal_ratios: Target percentages for each layer.

    Returns:
        PyramidHealth with score, status, and recommendations.
    """
    recommendations: list[str] = []
    warnings: list[str] = []

    # Compare to ideal ratios
    if metrics.total_tests == 0:
        return PyramidHealth(
            score=0.0,
            status="poor",
            recommendations=("No tests found - start by adding unit tests",),
            warnings=("Test suite is empty",),
        )

    # Calculate deviations
    unit_deviation = abs(metrics.unit_percentage - ideal_ratios["unit"])
    integration_deviation = abs(
        metrics.integration_percentage - ideal_ratios["integration"]
    )
    e2e_deviation = abs(metrics.e2e_percentage - ideal_ratios["e2e"])

    deviations = [unit_deviation, integration_deviation, e2e_deviation]
    avg_deviation = sum(deviations) / len(deviations)

    # Unit tests analysis
    if metrics.unit_percentage < ideal_ratios["unit"] - 10:
        recommendations.append(
            f"Add more unit tests (current: {metrics.unit_percentage:.1f}%, "
            f"target: {ideal_ratios['unit']}%)"
        )
        recommendations.append(
            "Unit tests should test business logic in isolation with mocks"
        )
    elif metrics.unit_percentage > ideal_ratios["unit"] + 10:
        warnings.append(
            f"Too many unit tests (current: {metrics.unit_percentage:.1f}%, "
            f"target: {ideal_ratios['unit']}%)"
        )
        recommendations.append(
            "Consider if some unit tests should be integration tests"
        )

    # Integration tests analysis
    if metrics.integration_percentage < ideal_ratios["integration"] - 5:
        recommendations.append(
            f"Add more integration tests (current: {metrics.integration_percentage:.1f}%, "
            f"target: {ideal_ratios['integration']}%)"
        )
        recommendations.append(
            "Integration tests should verify component interactions with real infrastructure"
        )
    elif metrics.integration_percentage > ideal_ratios["integration"] + 10:
        warnings.append(
            f"Too many integration tests (current: {metrics.integration_percentage:.1f}%, "
            f"target: {ideal_ratios['integration']}%)"
        )

    # E2E tests analysis
    if metrics.e2e_percentage < ideal_ratios["e2e"] - 5:
        recommendations.append(
            f"Add more E2E tests (current: {metrics.e2e_percentage:.1f}%, "
            f"target: {ideal_ratios['e2e']}%)"
        )
        recommendations.append("E2E tests should verify complete user workflows")
    elif metrics.e2e_percentage > ideal_ratios["e2e"] + 10:
        warnings.append(
            f"Too many E2E tests (current: {metrics.e2e_percentage:.1f}%, "
            f"target: {ideal_ratios['e2e']}%)"
        )
        recommendations.append(
            "E2E tests are slow - consider moving some to integration layer"
        )

    # Unknown tests
    if metrics.unknown_count > 0:
        warnings.append(
            f"{metrics.unknown_count} tests ({metrics.unknown_percentage:.1f}%) "
            "are not in unit/integration/e2e directories"
        )
        recommendations.append("Move tests to appropriate layer directories")

    # Calculate score (0-100)
    # Score decreases with deviation from ideal ratios
    score = max(0.0, 100.0 - avg_deviation * 2)

    # Determine status
    status: Literal["excellent", "good", "needs-improvement", "poor"]
    if score >= 90:
        status = "excellent"
    elif score >= 75:
        status = "good"
    elif score >= 50:
        status = "needs-improvement"
    else:
        status = "poor"

    return PyramidHealth(
        score=score,
        status=status,
        recommendations=tuple(recommendations),
        warnings=tuple(warnings),
    )


def generate_visual_pyramid(metrics: PyramidMetrics) -> str:
    """Generate ASCII art pyramid visualization.

    Args:
        metrics: The pyramid metrics to visualize.

    Returns:
        Multi-line string with ASCII bar chart.
    """
    if metrics.total_tests == 0:
        return "No tests found"

    # Calculate bar widths (max 60 chars)
    max_width = 60

    unit_width = int((metrics.unit_count / metrics.total_tests) * max_width)
    integration_width = int(
        (metrics.integration_count / metrics.total_tests) * max_width
    )
    e2e_width = int((metrics.e2e_count / metrics.total_tests) * max_width)

    lines: list[str] = [
        "Test Pyramid Visualization:",
        "",
    ]

    # E2E (top - smallest)
    e2e_bar = "#" * e2e_width
    lines.append(
        f"E2E        [{e2e_bar:<{max_width}}] {metrics.e2e_count} ({metrics.e2e_percentage:.1f}%)"
    )

    # Integration (middle)
    int_bar = "#" * integration_width
    lines.append(
        f"Integration[{int_bar:<{max_width}}] {metrics.integration_count} "
        f"({metrics.integration_percentage:.1f}%)"
    )

    # Unit (bottom - largest)
    unit_bar = "#" * unit_width
    lines.append(
        f"Unit       [{unit_bar:<{max_width}}] {metrics.unit_count} ({metrics.unit_percentage:.1f}%)"
    )

    if metrics.unknown_count > 0:
        unknown_width = int((metrics.unknown_count / metrics.total_tests) * max_width)
        unknown_bar = "?" * unknown_width
        lines.append(
            f"Unknown    [{unknown_bar:<{max_width}}] {metrics.unknown_count} "
            f"({metrics.unknown_percentage:.1f}%)"
        )

    return "\n".join(lines)


def generate_report(
    metrics: PyramidMetrics,
    health: PyramidHealth,
    ideal_ratios: dict[str, float],
    output_format: Literal["text", "json"] = "text",
) -> str:
    """Generate test pyramid analysis report.

    Args:
        metrics: The pyramid metrics.
        health: The health assessment.
        ideal_ratios: Target percentages for comparison.
        output_format: Either "text" or "json".

    Returns:
        Formatted report string.
    """
    if output_format == "json":
        return json.dumps(
            {
                "metrics": {
                    "total_tests": metrics.total_tests,
                    "unit": {
                        "count": metrics.unit_count,
                        "percentage": metrics.unit_percentage,
                    },
                    "integration": {
                        "count": metrics.integration_count,
                        "percentage": metrics.integration_percentage,
                    },
                    "e2e": {
                        "count": metrics.e2e_count,
                        "percentage": metrics.e2e_percentage,
                    },
                    "unknown": {
                        "count": metrics.unknown_count,
                        "percentage": metrics.unknown_percentage,
                    },
                },
                "health": {
                    "score": health.score,
                    "status": health.status,
                    "recommendations": list(health.recommendations),
                    "warnings": list(health.warnings),
                },
                "ideal_ratios": ideal_ratios,
            },
            indent=2,
        )

    # Text report
    report_lines: list[str] = [
        "=" * 80,
        "TEST PYRAMID ANALYSIS",
        "=" * 80,
        "",
        f"Total tests: {metrics.total_tests}",
        "",
        generate_visual_pyramid(metrics),
        "",
        "Ideal vs Actual Distribution:",
        "-" * 80,
    ]

    # Status indicators (ASCII-safe)
    unit_ok = (
        "[OK]" if abs(metrics.unit_percentage - ideal_ratios["unit"]) < 10 else "[!!]"
    )
    int_ok = (
        "[OK]"
        if abs(metrics.integration_percentage - ideal_ratios["integration"]) < 5
        else "[!!]"
    )
    e2e_ok = "[OK]" if abs(metrics.e2e_percentage - ideal_ratios["e2e"]) < 5 else "[!!]"

    report_lines.extend(
        [
            f"Unit:        {metrics.unit_percentage:5.1f}% (ideal: {ideal_ratios['unit']}%) {unit_ok}",
            f"Integration: {metrics.integration_percentage:5.1f}% (ideal: {ideal_ratios['integration']}%) {int_ok}",
            f"E2E:         {metrics.e2e_percentage:5.1f}% (ideal: {ideal_ratios['e2e']}%) {e2e_ok}",
            "",
        ]
    )

    # Health assessment
    status_indicator = {
        "excellent": "[EXCELLENT]",
        "good": "[GOOD]",
        "needs-improvement": "[NEEDS WORK]",
        "poor": "[POOR]",
    }
    report_lines.append(
        f"Health Score: {health.score:.1f}/100 {status_indicator.get(health.status, '')} ({health.status})"
    )
    report_lines.append("")

    # Warnings
    if health.warnings:
        report_lines.append("WARNINGS:")
        for warning in health.warnings:
            report_lines.append(f"  - {warning}")
        report_lines.append("")

    # Recommendations
    if health.recommendations:
        report_lines.append("RECOMMENDATIONS:")
        for rec in health.recommendations:
            report_lines.append(f"  - {rec}")
        report_lines.append("")

    return "\n".join(report_lines)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 for success, 1 for poor health or missing directory.
    """
    parser = argparse.ArgumentParser(
        description="Analyze test pyramid distribution and health",
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
        "--ideal-unit",
        type=float,
        default=70.0,
        help="Ideal unit test percentage (default: 70)",
    )
    parser.add_argument(
        "--ideal-integration",
        type=float,
        default=20.0,
        help="Ideal integration test percentage (default: 20)",
    )
    parser.add_argument(
        "--ideal-e2e",
        type=float,
        default=10.0,
        help="Ideal E2E test percentage (default: 10)",
    )

    args = parser.parse_args()

    test_dir = Path(args.path)
    if not test_dir.exists():
        print(f"Error: Directory not found: {test_dir}", file=sys.stderr)
        return 1

    ideal_ratios: dict[str, float] = {
        "unit": args.ideal_unit,
        "integration": args.ideal_integration,
        "e2e": args.ideal_e2e,
    }

    metrics = analyze_pyramid(test_dir)
    health = assess_pyramid_health(metrics, ideal_ratios)
    report = generate_report(metrics, health, ideal_ratios, args.format)
    print(report)

    # Exit with error if health is poor
    return 1 if health.status == "poor" else 0


if __name__ == "__main__":
    sys.exit(main())
