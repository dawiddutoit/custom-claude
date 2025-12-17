#!/usr/bin/env python3
"""Analyze trace coverage in Python service files.

This script generates coverage reports for OpenTelemetry instrumentation:
- Count instrumented vs uninstrumented methods
- Generate coverage report by module/layer
- Prioritize by service criticality
- Show gap analysis

Usage:
    python analyze_traces.py <directory> [--format=text|json|html] [--min-coverage=75]

Examples:
    # Analyze entire project
    python analyze_traces.py src/project_watch_mcp/

    # Analyze with HTML report
    python analyze_traces.py src/ --format=html > coverage_report.html

    # Analyze with minimum coverage threshold
    python analyze_traces.py src/ --min-coverage=80

    # JSON output for CI/CD
    python analyze_traces.py src/ --format=json
"""

import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class MethodInfo:
    """Information about a method."""

    name: str
    line: int
    is_traced: bool
    is_async: bool
    is_public: bool
    has_logging: bool


@dataclass
class FileAnalysis:
    """Analysis results for a file."""

    file: str
    layer: str  # "application", "infrastructure", "interface", "domain", "core"
    total_methods: int
    traced_methods: int
    untraced_methods: int
    coverage_percent: float
    methods: list[MethodInfo] = field(default_factory=list)
    priority: str = "medium"  # "critical", "high", "medium", "low"


@dataclass
class LayerAnalysis:
    """Analysis results for an architectural layer."""

    layer: str
    total_methods: int
    traced_methods: int
    coverage_percent: float
    files: list[FileAnalysis] = field(default_factory=list)


@dataclass
class OverallAnalysis:
    """Overall analysis results."""

    total_files: int
    total_methods: int
    traced_methods: int
    coverage_percent: float
    layers: dict[str, LayerAnalysis] = field(default_factory=dict)
    files: list[FileAnalysis] = field(default_factory=list)
    critical_gaps: list[FileAnalysis] = field(default_factory=list)


class TraceAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze trace coverage."""

    def __init__(self, file_path: str) -> None:
        """Initialize analyzer."""
        self.file_path = file_path
        self.methods: list[MethodInfo] = []
        self.current_class = ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        self.current_class = node.name

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._analyze_method(item)

        self.generic_visit(node)
        self.current_class = ""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if not self.current_class:
            self._analyze_method(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        if not self.current_class:
            self._analyze_method(node)
        self.generic_visit(node)

    def _analyze_method(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Analyze a method for tracing."""
        # Determine if method is public
        is_public = not node.name.startswith("_") or node.name == "__init__"

        # Skip dunder methods except __init__
        if node.name.startswith("__") and node.name.endswith("__") and node.name != "__init__":
            return

        # Check if traced
        is_traced = any(self._is_traced_decorator(dec) for dec in node.decorator_list)

        # Check if has logging
        has_logging = self._has_logging(node)

        # Build method name
        method_name = f"{self.current_class}.{node.name}" if self.current_class else node.name

        self.methods.append(
            MethodInfo(
                name=method_name,
                line=node.lineno,
                is_traced=is_traced,
                is_async=isinstance(node, ast.AsyncFunctionDef),
                is_public=is_public,
                has_logging=has_logging,
            )
        )

    def _is_traced_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is @traced."""
        if isinstance(decorator, ast.Name):
            return decorator.id == "traced"
        return False

    def _has_logging(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method has logger calls."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute):
                if isinstance(stmt.func.value, ast.Name):
                    if stmt.func.value.id == "logger":
                        return True
        return False


def determine_layer(file_path: Path) -> str:
    """Determine architectural layer from file path."""
    path_str = str(file_path)

    if "/application/" in path_str:
        return "application"
    if "/infrastructure/" in path_str:
        return "infrastructure"
    if "/interface/" in path_str or "/interfaces/" in path_str:
        return "interface"
    if "/domain/" in path_str:
        return "domain"
    if "/core/" in path_str:
        return "core"
    return "other"


def determine_priority(file_analysis: FileAnalysis) -> str:
    """Determine priority based on layer and coverage."""
    # Critical: Interface and Application layers with low coverage
    if file_analysis.layer in ["interface", "application"]:
        if file_analysis.coverage_percent < 50:
            return "critical"
        if file_analysis.coverage_percent < 75:
            return "high"
        return "medium"

    # High: Infrastructure with low coverage
    if file_analysis.layer == "infrastructure":
        if file_analysis.coverage_percent < 50:
            return "high"
        if file_analysis.coverage_percent < 75:
            return "medium"
        return "low"

    # Domain and Core layers are lower priority for tracing
    return "low"


def analyze_file(file_path: Path) -> FileAnalysis:
    """Analyze a Python file for trace coverage.

    Args:
        file_path: Path to Python file

    Returns:
        FileAnalysis with coverage information
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Analyze
        analyzer = TraceAnalyzer(str(file_path))
        analyzer.visit(tree)

        # Filter to public methods only
        public_methods = [m for m in analyzer.methods if m.is_public]

        total = len(public_methods)
        traced = sum(1 for m in public_methods if m.is_traced)
        coverage = (traced / total * 100) if total > 0 else 100.0

        layer = determine_layer(file_path)

        file_analysis = FileAnalysis(
            file=str(file_path),
            layer=layer,
            total_methods=total,
            traced_methods=traced,
            untraced_methods=total - traced,
            coverage_percent=coverage,
            methods=public_methods,
        )

        file_analysis.priority = determine_priority(file_analysis)

        return file_analysis

    except Exception:
        return FileAnalysis(
            file=str(file_path),
            layer="unknown",
            total_methods=0,
            traced_methods=0,
            untraced_methods=0,
            coverage_percent=0.0,
        )


def analyze_directory(directory: Path) -> OverallAnalysis:
    """Analyze all Python files in a directory.

    Args:
        directory: Path to directory

    Returns:
        OverallAnalysis with complete coverage report
    """
    file_analyses: list[FileAnalysis] = []

    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and similar
        if "__pycache__" in str(py_file):
            continue

        # Skip test files
        if "test_" in py_file.name or py_file.parent.name in ["tests", "test"]:
            continue

        analysis = analyze_file(py_file)
        if analysis.total_methods > 0:  # Only include files with methods
            file_analyses.append(analysis)

    # Group by layer
    layers: dict[str, LayerAnalysis] = {}
    for file_analysis in file_analyses:
        layer = file_analysis.layer
        if layer not in layers:
            layers[layer] = LayerAnalysis(
                layer=layer,
                total_methods=0,
                traced_methods=0,
                coverage_percent=0.0,
                files=[],
            )

        layers[layer].total_methods += file_analysis.total_methods
        layers[layer].traced_methods += file_analysis.traced_methods
        layers[layer].files.append(file_analysis)

    # Calculate layer coverage percentages
    for layer_analysis in layers.values():
        if layer_analysis.total_methods > 0:
            layer_analysis.coverage_percent = (
                layer_analysis.traced_methods / layer_analysis.total_methods * 100
            )

    # Calculate overall metrics
    total_methods = sum(f.total_methods for f in file_analyses)
    traced_methods = sum(f.traced_methods for f in file_analyses)
    coverage = (traced_methods / total_methods * 100) if total_methods > 0 else 100.0

    # Identify critical gaps (high priority files with low coverage)
    critical_gaps = [f for f in file_analyses if f.priority in ["critical", "high"]]
    critical_gaps.sort(key=lambda f: f.coverage_percent)

    return OverallAnalysis(
        total_files=len(file_analyses),
        total_methods=total_methods,
        traced_methods=traced_methods,
        coverage_percent=coverage,
        layers=layers,
        files=file_analyses,
        critical_gaps=critical_gaps,
    )


def format_text_report(analysis: OverallAnalysis, min_coverage: float = 0) -> str:
    """Format analysis as text report."""
    lines = []

    lines.append("=" * 80)
    lines.append("OPENTELEMETRY TRACE COVERAGE ANALYSIS")
    lines.append("=" * 80)
    lines.append("")

    # Overall summary
    lines.append("OVERALL SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total files analyzed: {analysis.total_files}")
    lines.append(f"Total public methods: {analysis.total_methods}")
    lines.append(f"Traced methods: {analysis.traced_methods}")
    lines.append(f"Untraced methods: {analysis.total_methods - analysis.traced_methods}")
    lines.append(f"Coverage: {analysis.coverage_percent:.1f}%")
    lines.append("")

    # Layer breakdown
    lines.append("COVERAGE BY LAYER")
    lines.append("-" * 80)
    for layer_name in ["interface", "application", "infrastructure", "domain", "core", "other"]:
        if layer_name in analysis.layers:
            layer = analysis.layers[layer_name]
            status = "✓" if layer.coverage_percent >= min_coverage else "✗"
            lines.append(
                f"{status} {layer.layer.upper()}: {layer.coverage_percent:.1f}% "
                f"({layer.traced_methods}/{layer.total_methods})"
            )
    lines.append("")

    # Critical gaps
    if analysis.critical_gaps:
        lines.append("CRITICAL GAPS (Priority: High/Critical)")
        lines.append("-" * 80)
        for file_analysis in analysis.critical_gaps[:10]:  # Top 10
            # Handle both absolute and relative paths
            file_path = Path(file_analysis.file)
            try:
                relative_path = file_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = file_path

            lines.append(
                f"[{file_analysis.priority.upper()}] {relative_path} - "
                f"{file_analysis.coverage_percent:.1f}% coverage "
                f"({file_analysis.traced_methods}/{file_analysis.total_methods})"
            )

            # Show untraced methods
            untraced = [m for m in file_analysis.methods if not m.is_traced]
            for method in untraced[:5]:  # Show up to 5 methods
                lines.append(f"    Line {method.line}: {method.name}")

            if len(untraced) > 5:
                lines.append(f"    ... and {len(untraced) - 5} more")

        lines.append("")

    # Low coverage files by layer
    lines.append("LOW COVERAGE FILES BY LAYER (< 75%)")
    lines.append("-" * 80)
    for layer_name in ["interface", "application", "infrastructure"]:
        if layer_name in analysis.layers:
            layer = analysis.layers[layer_name]
            low_coverage = [f for f in layer.files if f.coverage_percent < 75]

            if low_coverage:
                lines.append(f"\n{layer_name.upper()}:")
                for file_analysis in low_coverage:
                    # Handle both absolute and relative paths
                    file_path = Path(file_analysis.file)
                    try:
                        relative_path = file_path.relative_to(Path.cwd())
                    except ValueError:
                        relative_path = file_path

                    lines.append(
                        f"  {file_analysis.coverage_percent:5.1f}% - {relative_path} "
                        f"({file_analysis.traced_methods}/{file_analysis.total_methods})"
                    )

    lines.append("")
    lines.append("=" * 80)

    # Final status
    if analysis.coverage_percent >= min_coverage:
        lines.append(f"✓ Coverage meets threshold ({min_coverage}%)")
    else:
        lines.append(
            f"✗ Coverage below threshold (actual: {analysis.coverage_percent:.1f}%, "
            f"required: {min_coverage}%)"
        )

    lines.append("=" * 80)

    return "\n".join(lines)


def format_json_report(analysis: OverallAnalysis) -> str:
    """Format analysis as JSON."""
    output = {
        "summary": {
            "total_files": analysis.total_files,
            "total_methods": analysis.total_methods,
            "traced_methods": analysis.traced_methods,
            "coverage_percent": round(analysis.coverage_percent, 2),
        },
        "layers": {
            layer_name: {
                "total_methods": layer.total_methods,
                "traced_methods": layer.traced_methods,
                "coverage_percent": round(layer.coverage_percent, 2),
                "files": len(layer.files),
            }
            for layer_name, layer in analysis.layers.items()
        },
        "critical_gaps": [
            {
                "file": f.file,
                "layer": f.layer,
                "priority": f.priority,
                "coverage_percent": round(f.coverage_percent, 2),
                "total_methods": f.total_methods,
                "traced_methods": f.traced_methods,
                "untraced_methods": [
                    {"name": m.name, "line": m.line} for m in f.methods if not m.is_traced
                ],
            }
            for f in analysis.critical_gaps
        ],
    }

    return json.dumps(output, indent=2)


def format_html_report(analysis: OverallAnalysis) -> str:
    """Format analysis as HTML."""
    # Use double braces to escape CSS curly braces
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OTEL Trace Coverage Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .layer {{ margin: 20px 0; }}
        .progress-bar {{ background: #e0e0e0; height: 30px; border-radius: 5px; overflow: hidden; }}
        .progress-fill {{ background: #4caf50; height: 100%; text-align: center; line-height: 30px; color: white; font-weight: bold; }}
        .critical {{ color: #d32f2f; }}
        .high {{ color: #f57c00; }}
        .medium {{ color: #fbc02d; }}
        .low {{ color: #388e3c; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4caf50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>OpenTelemetry Trace Coverage Report</h1>

    <div class="summary">
        <h2>Overall Summary</h2>
        <p><strong>Total Files:</strong> {analysis.total_files}</p>
        <p><strong>Total Methods:</strong> {analysis.total_methods}</p>
        <p><strong>Traced Methods:</strong> {analysis.traced_methods}</p>
        <p><strong>Coverage:</strong> {analysis.coverage_percent:.1f}%</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {analysis.coverage_percent:.1f}%">{analysis.coverage_percent:.1f}%</div>
        </div>
    </div>

    <h2>Coverage by Layer</h2>
"""

    for layer_name in ["interface", "application", "infrastructure", "domain", "core"]:
        if layer_name in analysis.layers:
            layer = analysis.layers[layer_name]
            html += f"""
    <div class="layer">
        <h3>{layer_name.upper()}</h3>
        <p>Methods: {layer.traced_methods}/{layer.total_methods}</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {layer.coverage_percent:.1f}%">{layer.coverage_percent:.1f}%</div>
        </div>
    </div>
"""

    if analysis.critical_gaps:
        html += """
    <h2>Critical Gaps</h2>
    <table>
        <tr>
            <th>Priority</th>
            <th>File</th>
            <th>Layer</th>
            <th>Coverage</th>
            <th>Methods</th>
        </tr>
"""
        for file_analysis in analysis.critical_gaps[:20]:
            html += f"""
        <tr>
            <td class="{file_analysis.priority}">{file_analysis.priority.upper()}</td>
            <td>{Path(file_analysis.file).name}</td>
            <td>{file_analysis.layer}</td>
            <td>{file_analysis.coverage_percent:.1f}%</td>
            <td>{file_analysis.traced_methods}/{file_analysis.total_methods}</td>
        </tr>
"""

        html += """
    </table>
"""

    html += """
</body>
</html>
"""

    return html


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_traces.py <directory> [--format=text|json|html] [--min-coverage=75]")
        print("\nExamples:")
        print("  # Analyze entire project")
        print("  python analyze_traces.py src/project_watch_mcp/")
        print("\n  # Analyze with HTML report")
        print("  python analyze_traces.py src/ --format=html > coverage_report.html")
        print("\n  # Analyze with minimum coverage threshold")
        print("  python analyze_traces.py src/ --min-coverage=80")
        print("\n  # JSON output for CI/CD")
        print("  python analyze_traces.py src/ --format=json")
        sys.exit(1)

    target_path = Path(sys.argv[1])

    # Parse arguments
    format_type = "text"
    min_coverage = 0.0

    for arg in sys.argv[2:]:
        if arg.startswith("--format="):
            format_type = arg.split("=")[1]
        elif arg.startswith("--min-coverage="):
            min_coverage = float(arg.split("=")[1])

    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}")
        sys.exit(1)

    if not target_path.is_dir():
        print(f"Error: Path is not a directory: {target_path}")
        sys.exit(1)

    # Analyze
    analysis = analyze_directory(target_path)

    # Format output
    if format_type == "json":
        print(format_json_report(analysis))
    elif format_type == "html":
        print(format_html_report(analysis))
    else:
        print(format_text_report(analysis, min_coverage))

    # Exit code based on coverage
    if analysis.coverage_percent >= min_coverage:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
