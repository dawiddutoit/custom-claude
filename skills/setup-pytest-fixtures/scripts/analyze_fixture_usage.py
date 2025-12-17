#!/usr/bin/env python3
"""Analyze pytest fixture usage across the test suite.

This script analyzes fixture usage to identify:
- Unused fixtures
- Fixture dependency graph
- Scope issues (fixtures with incompatible scopes)
- Optimization opportunities
- Coverage statistics

Usage:
    # Analyze all fixtures
    python analyze_fixture_usage.py

    # Show unused fixtures only
    python analyze_fixture_usage.py --unused

    # Show dependency graph
    python analyze_fixture_usage.py --graph

    # Detailed analysis with recommendations
    python analyze_fixture_usage.py --detailed

    # Export to JSON
    python analyze_fixture_usage.py --output report.json

Examples:
    # Find unused fixtures for cleanup
    python analyze_fixture_usage.py --unused

    # Visualize fixture dependencies
    python analyze_fixture_usage.py --graph --output fixture_graph.dot

    # Get optimization recommendations
    python analyze_fixture_usage.py --detailed --optimize
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Setup: Add .claude/tools to path for shared utilities
_CLAUDE_ROOT = Path(__file__).parent.parent.parent.parent
if str(_CLAUDE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CLAUDE_ROOT))

from tools.skill_utils import ensure_path_setup  # noqa: E402


ensure_path_setup()


class FixtureAnalyzer:
    """Analyze pytest fixture usage patterns."""

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize fixture analyzer.

        Args:
            project_root: Path to project root (auto-detected if None)
        """
        self.project_root = project_root or self._find_project_root()
        self.fixtures: dict[str, dict[str, Any]] = {}
        self.usage: dict[str, list[str]] = defaultdict(list)
        self.dependencies: dict[str, list[str]] = defaultdict(list)

    @staticmethod
    def _find_project_root() -> Path:
        """Find project root by looking for pyproject.toml.

        Returns:
            Path to project root directory.
        """
        from tools.skill_utils import get_project_root

        return get_project_root()

    def find_fixtures(self) -> None:
        """Find all fixtures in the project."""
        test_dirs = [
            self.project_root / "tests" / "utils",
            self.project_root / "tests" / "unit",
            self.project_root / "tests" / "integration",
            self.project_root / "tests" / "e2e",
            self.project_root / "tests",
        ]

        for test_dir in test_dirs:
            if not test_dir.exists():
                continue

            # Find all Python files
            for py_file in test_dir.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                self._parse_fixtures_in_file(py_file)

    def _parse_fixtures_in_file(self, file_path: Path) -> None:
        """Parse fixtures from a Python file.

        Args:
            file_path: Path to Python file
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for pytest.fixture decorator
                    for decorator in node.decorator_list:
                        if self._is_fixture_decorator(decorator):
                            fixture_info = self._extract_fixture_info(
                                node, decorator, file_path
                            )
                            self.fixtures[node.name] = fixture_info
                            break

        except Exception:
            pass

    def _is_fixture_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is a pytest fixture.

        Args:
            decorator: AST decorator node

        Returns:
            bool: True if decorator is pytest.fixture or pytest_asyncio.fixture
        """
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
        self,
        node: ast.FunctionDef,
        decorator: ast.expr,
        file_path: Path,
    ) -> dict[str, Any]:
        """Extract information about a fixture.

        Args:
            node: Function definition node
            decorator: Fixture decorator node
            file_path: Path to file containing fixture

        Returns:
            dict: Fixture information
        """
        # Check if function is async
        is_async = isinstance(node, ast.AsyncFunctionDef) or any(
            isinstance(d, ast.Name) and "async" in d.id for d in node.decorator_list
        )

        info = {
            "name": node.name,
            "file": str(file_path.relative_to(self.project_root)),
            "scope": "function",  # default
            "is_async": is_async,
            "params": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node) or "",
            "is_factory": "factory" in node.name,
        }

        # Extract scope from decorator
        if isinstance(decorator, ast.Call):
            for keyword in decorator.keywords:
                if keyword.arg == "scope":
                    if isinstance(keyword.value, ast.Constant):
                        info["scope"] = keyword.value.value

        # Extract dependencies from parameters
        self.dependencies[node.name] = [
            param for param in info["params"] if param not in {"request", "self"}
        ]

        return info

    def find_usage(self) -> None:
        """Find all fixture usage in tests."""
        test_files = list((self.project_root / "tests").rglob("test_*.py"))

        for test_file in test_files:
            self._parse_usage_in_file(test_file)

    def _parse_usage_in_file(self, file_path: Path) -> None:
        """Parse fixture usage in a test file.

        Args:
            file_path: Path to test file
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    # Get function parameters (fixtures used)
                    for arg in node.args.args:
                        fixture_name = arg.arg
                        if fixture_name in self.fixtures:
                            self.usage[fixture_name].append(
                                str(file_path.relative_to(self.project_root))
                            )

        except Exception:
            pass

    def get_unused_fixtures(self) -> list[dict[str, Any]]:
        """Get list of unused fixtures.

        Returns:
            list: List of unused fixture information
        """
        unused = []
        for name, info in self.fixtures.items():
            if name not in self.usage or len(self.usage[name]) == 0:
                # Check if it's a dependency of other fixtures
                is_dependency = any(name in deps for deps in self.dependencies.values())
                if not is_dependency:
                    unused.append({**info, "name": name})
        return unused

    def get_fixture_graph(self) -> dict[str, Any]:
        """Get fixture dependency graph.

        Returns:
            dict: Graph structure with nodes and edges
        """
        nodes = []
        edges = []

        for name, info in self.fixtures.items():
            nodes.append(
                {
                    "id": name,
                    "label": name,
                    "scope": info["scope"],
                    "is_factory": info["is_factory"],
                    "is_async": info["is_async"],
                    "usage_count": len(self.usage.get(name, [])),
                }
            )

        for fixture, deps in self.dependencies.items():
            for dep in deps:
                if dep in self.fixtures:
                    edges.append({"from": fixture, "to": dep})

        return {"nodes": nodes, "edges": edges}

    def get_scope_issues(self) -> list[dict[str, Any]]:
        """Find scope compatibility issues.

        Returns:
            list: List of scope issues
        """
        issues = []

        for fixture, deps in self.dependencies.items():
            if fixture not in self.fixtures:
                continue

            fixture_scope = self.fixtures[fixture]["scope"]
            scope_order = {"function": 0, "class": 1, "module": 2, "session": 3}

            for dep in deps:
                if dep not in self.fixtures:
                    continue

                dep_scope = self.fixtures[dep]["scope"]

                # Narrower scope can't use broader scope
                if scope_order.get(fixture_scope, 0) > scope_order.get(dep_scope, 0):
                    issues.append(
                        {
                            "fixture": fixture,
                            "fixture_scope": fixture_scope,
                            "dependency": dep,
                            "dependency_scope": dep_scope,
                            "issue": f"{fixture} (scope={fixture_scope}) depends on {dep} (scope={dep_scope})",
                        }
                    )

        return issues

    def get_optimization_opportunities(self) -> list[dict[str, Any]]:
        """Find optimization opportunities.

        Returns:
            list: List of optimization suggestions
        """
        opportunities = []

        for name, info in self.fixtures.items():
            usage_count = len(self.usage.get(name, []))

            # Suggest factory pattern for frequently customized fixtures
            if usage_count > 5 and not info["is_factory"]:
                opportunities.append(
                    {
                        "fixture": name,
                        "type": "factory_pattern",
                        "reason": f"Used {usage_count} times - consider factory pattern for customization",
                        "current_scope": info["scope"],
                    }
                )

            # Suggest broader scope for frequently used fixtures
            if usage_count > 10 and info["scope"] == "function":
                opportunities.append(
                    {
                        "fixture": name,
                        "type": "scope_optimization",
                        "reason": f"Used {usage_count} times - consider module or session scope",
                        "current_scope": info["scope"],
                        "suggested_scope": "module",
                    }
                )

            # Suggest async for I/O-bound fixtures
            if "driver" in name or "client" in name or "connection" in name:
                if not info["is_async"]:
                    opportunities.append(
                        {
                            "fixture": name,
                            "type": "async_pattern",
                            "reason": "I/O-bound fixture should be async",
                            "current_type": "sync",
                        }
                    )

        return opportunities

    def get_statistics(self) -> dict[str, Any]:
        """Get fixture usage statistics.

        Returns:
            dict: Statistics about fixtures
        """
        total_fixtures = len(self.fixtures)
        unused_fixtures = len(self.get_unused_fixtures())
        factory_fixtures = sum(1 for f in self.fixtures.values() if f["is_factory"])
        async_fixtures = sum(1 for f in self.fixtures.values() if f["is_async"])

        scope_counts = defaultdict(int)
        for fixture in self.fixtures.values():
            scope_counts[fixture["scope"]] += 1

        usage_counts = {name: len(uses) for name, uses in self.usage.items()}
        avg_usage = (
            sum(usage_counts.values()) / len(usage_counts) if usage_counts else 0
        )
        most_used = sorted(usage_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_fixtures": total_fixtures,
            "unused_fixtures": unused_fixtures,
            "factory_fixtures": factory_fixtures,
            "async_fixtures": async_fixtures,
            "scope_distribution": dict(scope_counts),
            "average_usage": round(avg_usage, 2),
            "most_used_fixtures": [
                {"name": name, "count": count} for name, count in most_used
            ],
        }

    def analyze(self) -> dict[str, Any]:
        """Run complete fixture analysis.

        Returns:
            dict: Complete analysis results
        """
        self.find_fixtures()
        self.find_usage()

        return {
            "statistics": self.get_statistics(),
            "unused": self.get_unused_fixtures(),
            "scope_issues": self.get_scope_issues(),
            "optimizations": self.get_optimization_opportunities(),
            "graph": self.get_fixture_graph(),
        }

    def print_report(self, analysis: dict[str, Any], detailed: bool = False) -> None:
        """Print analysis report to stdout.

        Args:
            analysis: Analysis results
            detailed: Whether to print detailed report
        """
        stats = analysis["statistics"]

        print("\n=== Fixture Analysis Report ===\n")
        print(f"Total fixtures: {stats['total_fixtures']}")
        print(f"Unused fixtures: {stats['unused_fixtures']}")
        print(f"Factory fixtures: {stats['factory_fixtures']}")
        print(f"Async fixtures: {stats['async_fixtures']}")
        print(f"Average usage: {stats['average_usage']}")

        print("\n--- Scope Distribution ---")
        for scope, count in stats["scope_distribution"].items():
            print(f"  {scope}: {count}")

        if stats["most_used_fixtures"]:
            print("\n--- Most Used Fixtures ---")
            for fixture in stats["most_used_fixtures"][:5]:
                print(f"  {fixture['name']}: {fixture['count']} uses")

        if analysis["unused"]:
            print("\n--- Unused Fixtures ---")
            for fixture in analysis["unused"]:
                print(f"  {fixture['name']} ({fixture['file']})")

        if analysis["scope_issues"]:
            print("\n--- Scope Issues ---")
            for issue in analysis["scope_issues"]:
                print(f"  {issue['issue']}")

        if analysis["optimizations"]:
            print("\n--- Optimization Opportunities ---")
            for opp in analysis["optimizations"]:
                print(f"  {opp['fixture']}: {opp['reason']}")

        if detailed:
            print("\n--- Detailed Fixture Information ---")
            for name, info in sorted(self.fixtures.items()):
                usage_count = len(self.usage.get(name, []))
                print(f"\n  {name}:")
                print(f"    File: {info['file']}")
                print(f"    Scope: {info['scope']}")
                print(f"    Usage count: {usage_count}")
                if info["docstring"]:
                    first_line = info["docstring"].split("\n")[0]
                    print(f"    Description: {first_line}")

    def export_dot_graph(self, output_path: Path) -> None:
        """Export fixture dependency graph as Graphviz DOT format.

        Args:
            output_path: Path to write DOT file
        """
        graph = self.get_fixture_graph()

        dot_lines = ["digraph fixtures {"]
        dot_lines.append("  rankdir=LR;")
        dot_lines.append("  node [shape=box];")

        # Add nodes
        for node in graph["nodes"]:
            color = "lightblue" if node["is_factory"] else "lightgray"
            if node["is_async"]:
                color = "lightgreen"
            label = f"{node['id']}\\n({node['scope']})\\n{node['usage_count']} uses"
            dot_lines.append(
                f'  "{node["id"]}" [label="{label}", fillcolor={color}, style=filled];'
            )

        # Add edges
        for edge in graph["edges"]:
            dot_lines.append(f'  "{edge["from"]}" -> "{edge["to"]}";')

        dot_lines.append("}")

        output_path.write_text("\n".join(dot_lines))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze pytest fixture usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--unused", action="store_true", help="Show only unused fixtures"
    )
    parser.add_argument(
        "--graph", action="store_true", help="Generate dependency graph"
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Show detailed analysis"
    )
    parser.add_argument(
        "--optimize", action="store_true", help="Show optimization opportunities"
    )
    parser.add_argument("--output", help="Output file path (JSON or DOT format)")

    args = parser.parse_args()

    # Run analysis
    analyzer = FixtureAnalyzer()
    analysis = analyzer.analyze()

    # Handle output
    if args.output:
        output_path = Path(args.output)

        if output_path.suffix == ".json":
            output_path.write_text(json.dumps(analysis, indent=2))
        elif output_path.suffix == ".dot" or args.graph:
            analyzer.export_dot_graph(output_path)
        else:
            return

    # Print report
    if args.unused:
        print("\n=== Unused Fixtures ===")
        if analysis["unused"]:
            for fixture in analysis["unused"]:
                print(f"  {fixture['name']} ({fixture['file']})")
        else:
            print("  No unused fixtures found.")
    elif args.optimize:
        print("\n=== Optimization Opportunities ===")
        if analysis["optimizations"]:
            for opp in analysis["optimizations"]:
                print(f"  {opp['fixture']}: {opp['reason']}")
        else:
            print("  No optimization opportunities found.")
    else:
        analyzer.print_report(analysis, detailed=args.detailed)


if __name__ == "__main__":
    main()
