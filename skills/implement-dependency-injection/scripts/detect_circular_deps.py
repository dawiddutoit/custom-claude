#!/usr/bin/env python3
"""Detect circular dependencies in dependency injection container.

Analyzes container.py to build a dependency graph and detect circular
dependencies between providers. Suggests fixes when cycles are found.

Usage:
    python detect_circular_deps.py [path/to/container.py]
    python detect_circular_deps.py --graph  # Generate visual graph

Examples:
    python detect_circular_deps.py
    python detect_circular_deps.py src/myapp/container.py
    python detect_circular_deps.py --graph --output deps.dot
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

# Setup: Add .claude/tools to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_claude_root))

from tools.skill_utils import ensure_path_setup, find_container_path, get_project_root  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Iterator

ensure_path_setup()


@dataclass(frozen=True)
class ProviderInfo:
    """Information about a provider in the container."""

    name: str
    provider_type: str  # "Singleton", "Factory", "Dependency"
    service_class: str
    dependencies: tuple[str, ...]
    line_number: int


class ContainerAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze container providers."""

    def __init__(self) -> None:
        self.providers: dict[str, ProviderInfo] = {}
        self._in_container_class: bool = False

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition (Container class)."""
        if "Container" in node.name:
            self._in_container_class = True
            self.generic_visit(node)
            self._in_container_class = False
        else:
            self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment to extract provider definitions."""
        if not self._in_container_class:
            self.generic_visit(node)
            return

        # Extract provider variable name
        if not node.targets or not isinstance(node.targets[0], ast.Name):
            self.generic_visit(node)
            return

        provider_name = node.targets[0].id

        # Check if it's a provider assignment
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            func = node.value.func
            if isinstance(func.value, ast.Name) and func.value.id == "providers":
                provider_type = func.attr  # Singleton, Factory, Dependency

                # Extract service class (first argument)
                service_class = ""
                if node.value.args:
                    arg = node.value.args[0]
                    if isinstance(arg, ast.Name):
                        service_class = arg.id

                # Extract dependencies from keyword arguments
                dependencies = self._extract_dependencies(node.value)

                self.providers[provider_name] = ProviderInfo(
                    name=provider_name,
                    provider_type=provider_type,
                    service_class=service_class,
                    dependencies=tuple(dependencies),
                    line_number=node.lineno,
                )

        self.generic_visit(node)

    def _extract_dependencies(self, call_node: ast.Call) -> list[str]:
        """Extract dependency references from provider call."""
        dependencies: list[str] = []

        for keyword in call_node.keywords:
            if keyword.value:
                # Extract provider references
                deps = self._extract_provider_refs(keyword.value)
                dependencies.extend(deps)

        return dependencies

    def _extract_provider_refs(self, node: ast.AST) -> list[str]:
        """Recursively extract provider references from AST node."""
        refs: list[str] = []

        if isinstance(node, ast.Name):
            # Direct reference: repository=code_repository
            refs.append(node.id)

        elif isinstance(node, ast.Call):
            # Function call: lambda, Factory
            if isinstance(node.func, ast.Attribute):
                # providers.Factory(lambda...)
                for arg in node.args:
                    refs.extend(self._extract_provider_refs(arg))
                for kw in node.keywords:
                    if kw.value:
                        refs.extend(self._extract_provider_refs(kw.value))

        elif isinstance(node, ast.Lambda):
            # Lambda body
            refs.extend(self._extract_provider_refs(node.body))

        elif isinstance(node, ast.Attribute):
            # Attribute access: settings.chunking
            if isinstance(node.value, ast.Name):
                refs.append(node.value.id)

        return refs


@dataclass
class DependencyGraph:
    """Dependency graph for cycle detection."""

    providers: dict[str, ProviderInfo]
    graph: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

    def __post_init__(self) -> None:
        """Build adjacency list representation after initialization."""
        self._build_graph()

    def _build_graph(self) -> None:
        """Build adjacency list representation."""
        for provider_name, provider_info in self.providers.items():
            for dep in provider_info.dependencies:
                # Only add if dependency is a known provider
                if dep in self.providers:
                    self.graph[provider_name].append(dep)

    def find_cycles(self) -> list[list[str]]:
        """Find all cycles in the dependency graph.

        Returns:
            List of cycles, where each cycle is a list of provider names.
        """
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = [*path[cycle_start:], neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.remove(node)

        for provider_name in self.providers:
            if provider_name not in visited:
                dfs(provider_name, [])

        return cycles

    def get_dependency_chain(self, start: str, end: str) -> list[str] | None:
        """Find dependency chain from start to end provider.

        Args:
            start: Starting provider name.
            end: Ending provider name.

        Returns:
            List of provider names forming the chain, or None if no path exists.
        """
        if start not in self.providers or end not in self.providers:
            return None

        visited: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> bool:
            if node in visited:
                return False

            visited.add(node)
            path.append(node)

            if node == end:
                return True

            for neighbor in self.graph.get(node, []):
                if dfs(neighbor):
                    return True

            path.pop()
            return False

        if dfs(start):
            return path

        return None

    def to_dot_format(self) -> str:
        """Generate GraphViz DOT format for visualization.

        Returns:
            DOT format string for visualization with graphviz.
        """
        lines = ["digraph DependencyGraph {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box];")
        lines.append("")

        # Add nodes with labels
        for provider_name, provider_info in self.providers.items():
            label = f"{provider_name}\\n({provider_info.provider_type})"
            lines.append(f'    "{provider_name}" [label="{label}"];')

        lines.append("")

        # Add edges
        for provider_name, neighbors in self.graph.items():
            for neighbor in neighbors:
                lines.append(f'    "{provider_name}" -> "{neighbor}";')

        lines.append("}")
        return "\n".join(lines)

    def get_statistics(self) -> dict[str, int]:
        """Get statistics about the dependency graph.

        Returns:
            Dictionary with provider type counts.
        """
        type_counts: dict[str, int] = defaultdict(int)
        for provider_info in self.providers.values():
            type_counts[provider_info.provider_type] += 1
        return dict(type_counts)

    def get_max_dependency_providers(self) -> Iterator[tuple[ProviderInfo, int]]:
        """Get providers with the maximum number of dependencies.

        Yields:
            Tuples of (provider_info, dependency_count) for max-dependency providers.
        """
        if not self.providers:
            return

        max_deps = max((len(p.dependencies) for p in self.providers.values()), default=0)
        if max_deps > 0:
            for provider_info in self.providers.values():
                if len(provider_info.dependencies) == max_deps:
                    yield provider_info, max_deps


def analyze_container(container_path: Path) -> dict[str, ProviderInfo]:
    """Analyze container.py and extract provider information.

    Args:
        container_path: Path to container.py file.

    Returns:
        Dictionary mapping provider names to ProviderInfo.
    """
    if not container_path.exists():
        return {}

    with container_path.open(encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(container_path))
        except SyntaxError:
            return {}

    analyzer = ContainerAnalyzer()
    analyzer.visit(tree)

    return analyzer.providers


def format_cycle(cycle: list[str], providers: dict[str, ProviderInfo]) -> str:
    """Format a dependency cycle for display.

    Args:
        cycle: List of provider names in the cycle.
        providers: Dictionary of all providers.

    Returns:
        Formatted string describing the cycle.
    """
    lines = []
    for i, provider_name in enumerate(cycle[:-1]):
        provider_info = providers.get(provider_name)
        next_provider = cycle[i + 1]
        if provider_info:
            lines.append(f"  {provider_name} ({provider_info.provider_type}) -> {next_provider}")
        else:
            lines.append(f"  {provider_name} -> {next_provider}")
    return "\n".join(lines)


def print_cycles(cycles: list[list[str]], providers: dict[str, ProviderInfo]) -> None:
    """Print detected cycles with details."""
    if not cycles:
        print("No circular dependencies detected.")
        return

    print(f"\nFound {len(cycles)} circular dependency cycle(s):\n")

    for i, cycle in enumerate(cycles, 1):
        print(f"Cycle {i}:")
        print(format_cycle(cycle, providers))
        print()

    # Suggest fixes
    print("Suggestions to fix circular dependencies:")
    print("  1. Use Factory provider with lazy initialization")
    print("  2. Extract shared logic into a separate service")
    print("  3. Use an event/message bus for decoupling")
    print("  4. Introduce an interface/protocol to break the cycle")


def print_statistics(graph: DependencyGraph) -> None:
    """Print container statistics."""
    if not graph.providers:
        print("No providers found.")
        return

    print("\nContainer Statistics:")
    print(f"  Total providers: {len(graph.providers)}")

    # Count by provider type
    type_counts = graph.get_statistics()
    for provider_type, count in sorted(type_counts.items()):
        print(f"  {provider_type}: {count}")

    # Find providers with most dependencies
    print("\nProviders with most dependencies:")
    for provider_info, dep_count in graph.get_max_dependency_providers():
        print(f"  {provider_info.name}: {dep_count} dependencies")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Detect circular dependencies in DI container"
    )
    parser.add_argument(
        "container_path",
        nargs="?",
        help="Path to container.py (auto-detected if not provided)",
    )
    parser.add_argument("--graph", action="store_true", help="Generate GraphViz DOT format")
    parser.add_argument("--output", "-o", help="Output file for graph (default: stdout)")
    parser.add_argument("--stats", action="store_true", help="Show container statistics")

    args = parser.parse_args()

    # Find container path
    if args.container_path:
        container_path = Path(args.container_path)
    else:
        found_path = find_container_path(get_project_root())
        if found_path is None:
            print("Error: Could not find container.py. Please specify path.", file=sys.stderr)
            return 1
        container_path = found_path

    if not container_path.exists():
        print(f"Error: Container file not found: {container_path}", file=sys.stderr)
        return 1

    print(f"Analyzing: {container_path}")

    # Analyze container
    providers = analyze_container(container_path)
    if not providers:
        print("Warning: No providers found in container.", file=sys.stderr)
        return 1

    # Build dependency graph
    dep_graph = DependencyGraph(providers)

    # Find cycles
    cycles = dep_graph.find_cycles()

    # Print results
    if args.graph:
        dot_output = dep_graph.to_dot_format()
        if args.output:
            output_path = Path(args.output)
            with output_path.open("w", encoding="utf-8") as f:
                f.write(dot_output)
            print(f"Graph written to: {args.output}")
        else:
            print(dot_output)
    else:
        print_cycles(cycles, providers)

        if args.stats:
            print_statistics(dep_graph)

    # Return non-zero if cycles found
    return 1 if cycles else 0


if __name__ == "__main__":
    sys.exit(main())
