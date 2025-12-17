#!/usr/bin/env python3
"""Validate fixture patterns and suggest factory conversions.

Analyzes pytest fixtures to identify anti-patterns and opportunities
for factory pattern adoption.

Usage:
    python validate_fixtures.py
    python validate_fixtures.py --file tests/unit/conftest.py
    python validate_fixtures.py --report fixtures_report.md
    python validate_fixtures.py --only-candidates
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


# Constants
COMPLEX_SETUP_THRESHOLD = 5  # Number of assignments indicating complex setup
MANY_ATTRIBUTES_THRESHOLD = 10  # Number of attributes suggesting kwargs pattern
MAX_CANDIDATES_TO_SHOW = 5  # Maximum candidates to show in summary


@dataclass(frozen=True)
class FixtureIssue:
    """Issue found in a fixture."""

    issue_type: str
    severity: str  # "high", "medium", "low", "info"
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class FixtureInfo:
    """Information about an analyzed fixture."""

    name: str
    line: int
    params: list[str]
    has_type_hints: bool
    is_factory: bool
    issues: list[FixtureIssue] = field(default_factory=list)


@dataclass
class FileAnalysisResult:
    """Result of analyzing a file."""

    file_path: str
    fixtures: list[FixtureInfo] = field(default_factory=list)
    error: str | None = None


class FixtureAnalyzer(ast.NodeVisitor):
    """Analyze fixtures for anti-patterns and factory opportunities."""

    def __init__(self) -> None:
        self.fixtures: list[FixtureInfo] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition to analyze fixtures."""
        has_fixture_decorator = any(
            (isinstance(d, ast.Name) and d.id == "fixture")
            or (isinstance(d, ast.Attribute) and d.attr == "fixture")
            for d in node.decorator_list
        )

        if has_fixture_decorator:
            self._analyze_fixture(node)

        self.generic_visit(node)

    def _analyze_fixture(self, node: ast.FunctionDef) -> None:
        """Analyze individual fixture for issues."""
        fixture_info = FixtureInfo(
            name=node.name,
            line=node.lineno,
            params=[arg.arg for arg in node.args.args],
            has_type_hints=any(arg.annotation for arg in node.args.args),
            is_factory=self._is_factory_fixture(node),
        )

        # Check for anti-patterns
        fixture_info.issues.extend(self._check_hardcoded_values(node))
        fixture_info.issues.extend(self._check_missing_type_hints(node))
        fixture_info.issues.extend(
            self._check_factory_candidate(node, fixture_info.is_factory)
        )
        fixture_info.issues.extend(self._check_repeated_setup(node))

        self.fixtures.append(fixture_info)

    def _is_factory_fixture(self, node: ast.FunctionDef) -> bool:
        """Check if fixture is already a factory (returns callable)."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                if isinstance(child.value, ast.Name):
                    return True
                if isinstance(child.value, ast.Lambda):
                    return True
        return False

    def _check_hardcoded_values(self, node: ast.FunctionDef) -> list[FixtureIssue]:
        """Check for hardcoded values that should be parameters."""
        hardcoded_values: list[tuple[int, object]] = []

        for child in ast.walk(node):
            if isinstance(child, ast.Constant):
                if isinstance(child.value, int | float):
                    # Ignore common test values
                    if child.value not in {0, 1, -1, None}:
                        hardcoded_values.append((child.lineno, child.value))

        if hardcoded_values:
            return [
                FixtureIssue(
                    issue_type="hardcoded_values",
                    severity="medium",
                    message=f"Found {len(hardcoded_values)} hardcoded values",
                    details={"values": hardcoded_values},
                )
            ]
        return []

    def _check_missing_type_hints(self, node: ast.FunctionDef) -> list[FixtureIssue]:
        """Check for missing type hints."""
        if not node.returns:
            return [
                FixtureIssue(
                    issue_type="missing_return_type",
                    severity="low",
                    message="Missing return type hint",
                )
            ]
        return []

    def _check_factory_candidate(
        self, node: ast.FunctionDef, is_factory: bool
    ) -> list[FixtureIssue]:
        """Check if fixture would benefit from factory pattern."""
        if is_factory:
            return []

        indicators: list[str] = []

        # 1. Fixture creates mocks
        creates_mocks = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id in {"MagicMock", "AsyncMock", "Mock"}:
                    creates_mocks = True
                    break

        if creates_mocks:
            indicators.append("creates_mocks")

        # 2. Fixture has complex setup
        num_assignments = sum(
            1 for child in ast.walk(node) if isinstance(child, ast.Assign)
        )
        if num_assignments > COMPLEX_SETUP_THRESHOLD:
            indicators.append("complex_setup")

        # 3. Fixture name suggests variations needed
        if any(
            word in node.name.lower()
            for word in ["default", "basic", "simple", "minimal"]
        ):
            indicators.append("suggests_variations")

        if indicators:
            return [
                FixtureIssue(
                    issue_type="factory_candidate",
                    severity="info",
                    message="Consider converting to factory pattern",
                    details={"indicators": indicators},
                )
            ]
        return []

    def _check_repeated_setup(self, node: ast.FunctionDef) -> list[FixtureIssue]:
        """Check for repeated setup patterns (suggest extraction)."""
        attribute_sets: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Attribute):
                        attribute_sets.append(target.attr)

        if len(attribute_sets) > MANY_ATTRIBUTES_THRESHOLD:
            return [
                FixtureIssue(
                    issue_type="many_attributes",
                    severity="low",
                    message=f"Setting {len(attribute_sets)} attributes - consider **kwargs pattern",
                )
            ]
        return []


def analyze_file(file_path: Path) -> FileAnalysisResult:
    """Analyze a conftest.py file for fixture issues.

    Args:
        file_path: Path to conftest.py file

    Returns:
        FileAnalysisResult with analysis data
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except SyntaxError as e:
        return FileAnalysisResult(file_path=str(file_path), error=str(e))
    except OSError as e:
        return FileAnalysisResult(file_path=str(file_path), error=str(e))

    analyzer = FixtureAnalyzer()
    analyzer.visit(tree)

    return FileAnalysisResult(
        file_path=str(file_path),
        fixtures=analyzer.fixtures,
    )


def generate_report(results: list[FileAnalysisResult]) -> str:
    """Generate markdown report from analysis results.

    Args:
        results: List of analysis results

    Returns:
        Markdown formatted report
    """
    report = "# Fixture Validation Report\n\n"

    # Summary
    total_fixtures = sum(len(r.fixtures) for r in results)
    total_issues = sum(sum(len(f.issues) for f in r.fixtures) for r in results)
    factory_candidates = sum(
        1
        for r in results
        for f in r.fixtures
        for issue in f.issues
        if issue.issue_type == "factory_candidate"
    )

    report += "## Summary\n\n"
    report += f"- **Total Fixtures:** {total_fixtures}\n"
    report += f"- **Total Issues:** {total_issues}\n"
    report += f"- **Factory Candidates:** {factory_candidates}\n\n"

    # Details by file
    for result in results:
        if result.error:
            report += f"## {result.file_path}\n\n"
            report += f"**Error:** {result.error}\n\n"
            continue

        if not result.fixtures:
            continue

        report += f"## {result.file_path}\n\n"
        report += f"**Fixtures:** {len(result.fixtures)}\n\n"

        # Group issues by severity
        issues_by_severity: dict[str, list[tuple[str, FixtureIssue]]] = defaultdict(
            list
        )
        for fixture in result.fixtures:
            for issue in fixture.issues:
                issues_by_severity[issue.severity].append((fixture.name, issue))

        # High severity
        if "high" in issues_by_severity:
            report += "### High Priority\n\n"
            for fixture_name, issue in issues_by_severity["high"]:
                report += (
                    f"- **{fixture_name}** ({issue.issue_type}): {issue.message}\n"
                )
            report += "\n"

        # Medium severity
        if "medium" in issues_by_severity:
            report += "### Medium Priority\n\n"
            for fixture_name, issue in issues_by_severity["medium"]:
                report += (
                    f"- **{fixture_name}** ({issue.issue_type}): {issue.message}\n"
                )
            report += "\n"

        # Factory candidates
        if "info" in issues_by_severity:
            candidates = [
                (fn, i)
                for fn, i in issues_by_severity["info"]
                if i.issue_type == "factory_candidate"
            ]
            if candidates:
                report += "### Factory Pattern Candidates\n\n"
                for fixture_name, issue in candidates:
                    indicators = issue.details.get("indicators", [])
                    report += f"- **{fixture_name}**\n"
                    report += (
                        f"  - Indicators: {', '.join(str(i) for i in indicators)}\n"
                    )
                    report += f"  - Command: `python convert_fixture_to_factory.py {fixture_name} --file {result.file_path}`\n"
                report += "\n"

        # Low severity
        if "low" in issues_by_severity:
            report += "<details>\n<summary>Low Priority Issues</summary>\n\n"
            for fixture_name, issue in issues_by_severity["low"]:
                report += (
                    f"- **{fixture_name}** ({issue.issue_type}): {issue.message}\n"
                )
            report += "\n</details>\n\n"

    return report


def print_summary(results: list[FileAnalysisResult]) -> None:
    """Print summary to console.

    Args:
        results: List of analysis results
    """
    total_fixtures = sum(len(r.fixtures) for r in results)
    total_issues = sum(sum(len(f.issues) for f in r.fixtures) for r in results)

    print(f"\nAnalyzed {len(results)} file(s)")
    print(f"Total fixtures: {total_fixtures}")
    print(f"Total issues: {total_issues}")

    # Count by severity
    severity_counts: dict[str, int] = defaultdict(int)
    for result in results:
        for fixture in result.fixtures:
            for issue in fixture.issues:
                severity_counts[issue.severity] += 1

    if severity_counts:
        print("\nIssues by severity:")
        severity_icons = {"high": "[!]", "medium": "[~]", "low": "[-]", "info": "[i]"}
        for severity in ["high", "medium", "low", "info"]:
            if severity in severity_counts:
                icon = severity_icons[severity]
                print(f"  {icon} {severity}: {severity_counts[severity]}")

    # Factory candidates
    factory_candidates: list[tuple[str, str, FixtureIssue]] = [
        (r.file_path, f.name, issue)
        for r in results
        for f in r.fixtures
        for issue in f.issues
        if issue.issue_type == "factory_candidate"
    ]

    if factory_candidates:
        print(f"\nFactory candidates ({len(factory_candidates)}):")
        for file_path, fixture_name, issue in factory_candidates[
            :MAX_CANDIDATES_TO_SHOW
        ]:
            indicators = issue.details.get("indicators", [])
            print(f"  - {fixture_name} ({', '.join(str(i) for i in indicators)})")

        if len(factory_candidates) > MAX_CANDIDATES_TO_SHOW:
            remaining = len(factory_candidates) - MAX_CANDIDATES_TO_SHOW
            print(f"  ... and {remaining} more")


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Validate fixture patterns and suggest improvements"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to specific conftest.py file",
    )
    parser.add_argument(
        "--only-candidates",
        action="store_true",
        help="Only show factory pattern candidates",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Generate detailed markdown report",
    )

    args = parser.parse_args(argv)

    # Find files to analyze
    if args.file:
        files = [args.file]
    else:
        # Find all conftest.py files
        search_root = Path.cwd() / "tests"
        files = list(search_root.rglob("conftest.py"))

    if not files:
        print("Error: No conftest.py files found", file=sys.stderr)
        return 1

    # Analyze files
    results: list[FileAnalysisResult] = []
    for file_path in files:
        result = analyze_file(file_path)
        results.append(result)

    # Filter if only showing candidates
    if args.only_candidates:
        filtered_results: list[FileAnalysisResult] = []
        for r in results:
            filtered_fixtures = [
                FixtureInfo(
                    name=f.name,
                    line=f.line,
                    params=f.params,
                    has_type_hints=f.has_type_hints,
                    is_factory=f.is_factory,
                    issues=[i for i in f.issues if i.issue_type == "factory_candidate"],
                )
                for f in r.fixtures
                if any(i.issue_type == "factory_candidate" for i in f.issues)
            ]
            filtered_results.append(
                FileAnalysisResult(
                    file_path=r.file_path,
                    fixtures=filtered_fixtures,
                    error=r.error,
                )
            )
        results = filtered_results

    # Generate report if requested
    if args.report:
        report = generate_report(results)
        args.report.write_text(report, encoding="utf-8")
        print(f"Report written to: {args.report}")

    # Print summary
    print_summary(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
