#!/usr/bin/env python3
"""Analyze Cypher queries in repository implementations.

This script extracts and analyzes Cypher queries from repository code:
- Extract all queries from repositories
- Check for parameter validation
- Flag potential injection risks
- Suggest index usage
- Analyze query complexity

Usage:
    python analyze_queries.py                          # Analyze all repositories
    python analyze_queries.py --file path.py           # Analyze specific file
    python analyze_queries.py --export queries.json    # Export queries to JSON
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# Note: This script is designed to be run standalone with no external dependencies
# beyond Python's standard library.


@dataclass
class QueryAnalysis:
    """Analysis result for a Cypher query."""

    file: str
    class_name: str
    method_name: str
    query: str
    parameters: list[str]
    has_validation: bool
    injection_risk: str  # SAFE, WARNING, DANGER
    complexity: str  # SIMPLE, MODERATE, COMPLEX
    suggestions: list[str]
    line_number: int


@dataclass
class IndexSuggestion:
    """Suggested index based on query patterns."""

    node_label: str
    property_name: str
    query_count: int
    queries: list[str]


class CypherQueryExtractor(ast.NodeVisitor):
    """AST visitor to extract Cypher queries."""

    def __init__(self, file_path: Path) -> None:
        """Initialize extractor.

        Args:
            file_path: Path to file being analyzed
        """
        self.file_path = file_path
        self.queries: list[QueryAnalysis] = []
        self.current_class: str | None = None
        self.current_method: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self.current_method = node.name
        self.generic_visit(node)
        self.current_method = None

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment statement to find query definitions."""
        # Check if assigning a string (potential query)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            query_str = node.value.value.strip()
            if self._looks_like_cypher(query_str):
                self._analyze_query(query_str, node.lineno)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Visit attribute access to find CypherQueries usage."""
        # Check for CypherQueries.QUERY_NAME
        if isinstance(node.value, ast.Name) and node.value.id == "CypherQueries":
            # This is a reference to a query constant
            # We'll analyze these separately by parsing queries.py
            pass

        self.generic_visit(node)

    def _looks_like_cypher(self, text: str) -> bool:
        """Check if text looks like a Cypher query.

        Args:
            text: Text to check

        Returns:
            True if text looks like Cypher
        """
        cypher_keywords = [
            "MATCH",
            "CREATE",
            "MERGE",
            "DELETE",
            "RETURN",
            "WHERE",
            "SET",
            "WITH",
        ]
        upper_text = text.upper()
        return any(keyword in upper_text for keyword in cypher_keywords)

    def _analyze_query(self, query: str, line_number: int) -> None:
        """Analyze a Cypher query.

        Args:
            query: Cypher query string
            line_number: Line number where query appears
        """
        # Extract parameters
        parameters = self._extract_parameters(query)

        # Check for validation (look for validate_and_build_query in context)
        has_validation = False  # Will be set later by analyzing method body

        # Assess injection risk
        injection_risk = self._assess_injection_risk(query, parameters)

        # Assess complexity
        complexity = self._assess_complexity(query)

        # Generate suggestions
        suggestions = self._generate_suggestions(query, parameters)

        analysis = QueryAnalysis(
            file=str(self.file_path),
            class_name=self.current_class or "Unknown",
            method_name=self.current_method or "Unknown",
            query=query,
            parameters=parameters,
            has_validation=has_validation,
            injection_risk=injection_risk,
            complexity=complexity,
            suggestions=suggestions,
            line_number=line_number,
        )

        self.queries.append(analysis)

    def _extract_parameters(self, query: str) -> list[str]:
        """Extract parameter names from query.

        Args:
            query: Cypher query string

        Returns:
            List of parameter names
        """
        # Find $param_name patterns
        pattern = r"\$(\w+)"
        matches = re.findall(pattern, query)
        return sorted(set(matches))

    def _assess_injection_risk(self, query: str, parameters: list[str]) -> str:
        """Assess SQL injection risk.

        Args:
            query: Cypher query string
            parameters: List of parameter names

        Returns:
            Risk level: SAFE, WARNING, DANGER
        """
        # Python f-string interpolation is dangerous (look for f-string pattern)
        # Check for f"{variable}" pattern but not ${ (which is Cypher syntax)
        if re.search(r'f["\'].*\{[^$]', query):
            return "DANGER"

        # String .format() is dangerous
        if ".format(" in query:
            return "DANGER"

        # % formatting is dangerous
        if "%" in query and '"' in query:
            return "WARNING"

        # Dynamic property names without validation
        if "$prop" in query or "+" in query:  # String concatenation
            return "WARNING"

        return "SAFE"

    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity.

        Args:
            query: Cypher query string

        Returns:
            Complexity level: SIMPLE, MODERATE, COMPLEX
        """
        upper_query = query.upper()

        # Count clauses
        match_count = upper_query.count("MATCH")
        create_count = upper_query.count("CREATE")
        merge_count = upper_query.count("MERGE")
        with_count = upper_query.count("WITH")

        total_clauses = match_count + create_count + merge_count + with_count

        if total_clauses <= 1:
            return "SIMPLE"
        if total_clauses <= 3:
            return "MODERATE"
        return "COMPLEX"

    def _generate_suggestions(self, query: str, parameters: list[str]) -> list[str]:
        """Generate optimization suggestions.

        Args:
            query: Cypher query string
            parameters: List of parameter names

        Returns:
            List of suggestions
        """
        suggestions = []
        upper_query = query.upper()

        # Check for missing indexes
        if "MATCH" in upper_query:
            # Extract node labels and properties being matched
            match_patterns = re.findall(r"MATCH\s+\((\w+):(\w+)\s+{([^}]+)}", query)
            for _var, label, props in match_patterns:
                # Suggest indexes for lookup properties
                if "project_name" in props.lower() or "id" in props.lower():
                    suggestions.append(
                        f"Consider index on :{label}(project_name) and :{label}(id)"
                    )

        # Check for MERGE without constraints
        if "MERGE" in upper_query:
            suggestions.append(
                "Ensure unique constraints exist for MERGE properties to avoid duplicates"
            )

        # Check for missing LIMIT on collection queries
        if (
            "MATCH" in upper_query
            and "RETURN" in upper_query
            and "LIMIT" not in upper_query
        ):
            if "collect(" in query.lower() or "[" in query:
                suggestions.append("Consider adding LIMIT to prevent large result sets")

        # Check for timestamp management
        if "CREATE" in upper_query or "MERGE" in upper_query:
            if "created_at" not in query.lower() and "updated_at" not in query.lower():
                suggestions.append("Consider adding created_at/updated_at timestamps")

        # Check for parameter validation
        if parameters and "validate_and_build_query" not in query:
            suggestions.append("Ensure parameters are validated before execution")

        return suggestions


def extract_queries_from_file(file_path: Path) -> list[QueryAnalysis]:
    """Extract queries from a Python file.

    Args:
        file_path: Path to Python file

    Returns:
        List of query analyses
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source, filename=str(file_path))

        extractor = CypherQueryExtractor(file_path)
        extractor.visit(tree)

        # Post-process to check for validation
        for query in extractor.queries:
            # Check if file contains validate_and_build_query
            if "validate_and_build_query" in source:
                query.has_validation = True

        return extractor.queries
    except (OSError, SyntaxError) as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return []


def extract_queries_from_cypher_queries_class(file_path: Path) -> list[QueryAnalysis]:
    """Extract queries from CypherQueries class.

    Args:
        file_path: Path to queries.py file

    Returns:
        List of query analyses
    """
    queries: list[QueryAnalysis] = []

    try:
        source = file_path.read_text()
        tree = ast.parse(source, filename=str(file_path))

        # Find CypherQueries class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "CypherQueries":
                # Extract all string assignments
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                const_name = target.id
                                if isinstance(item.value, ast.Constant) and isinstance(
                                    item.value.value, str
                                ):
                                    query_str = item.value.value.strip()

                                    # Analyze query
                                    extractor = CypherQueryExtractor(file_path)
                                    analysis = QueryAnalysis(
                                        file=str(file_path),
                                        class_name="CypherQueries",
                                        method_name=const_name,
                                        query=query_str,
                                        parameters=extractor._extract_parameters(
                                            query_str
                                        ),
                                        has_validation=True,  # Assume queries.py queries are validated
                                        injection_risk=extractor._assess_injection_risk(
                                            query_str,
                                            extractor._extract_parameters(query_str),
                                        ),
                                        complexity=extractor._assess_complexity(
                                            query_str
                                        ),
                                        suggestions=extractor._generate_suggestions(
                                            query_str,
                                            extractor._extract_parameters(query_str),
                                        ),
                                        line_number=item.lineno,
                                    )
                                    queries.append(analysis)

    except (OSError, SyntaxError) as e:
        print(
            f"Warning: Could not parse CypherQueries from {file_path}: {e}",
            file=sys.stderr,
        )

    return queries


def suggest_indexes(queries: list[QueryAnalysis]) -> list[IndexSuggestion]:
    """Suggest indexes based on query patterns.

    Args:
        queries: List of query analyses

    Returns:
        List of index suggestions
    """
    # Track label:property usage
    usage: dict[tuple[str, str], list[str]] = {}

    for query_analysis in queries:
        query = query_analysis.query

        # Extract MATCH patterns with property filters
        patterns = re.findall(
            r"MATCH\s+\([^:]*:(\w+)\s+{[^}]*(\w+):\s*\$", query, re.IGNORECASE
        )

        for label, prop in patterns:
            key = (label, prop)
            usage.setdefault(key, []).append(query_analysis.method_name)

    # Generate suggestions for frequently used patterns
    suggestions = []
    for (label, prop), methods in usage.items():
        if len(methods) >= 2:  # Used in 2+ queries
            suggestions.append(
                IndexSuggestion(
                    node_label=label,
                    property_name=prop,
                    query_count=len(methods),
                    queries=methods,
                )
            )

    return sorted(suggestions, key=lambda x: x.query_count, reverse=True)


def print_analysis_report(
    queries: list[QueryAnalysis], index_suggestions: list[IndexSuggestion]
) -> None:
    """Print analysis report.

    Args:
        queries: List of query analyses
        index_suggestions: List of index suggestions
    """
    # Summary
    total = len(queries)
    safe_count = sum(1 for q in queries if q.injection_risk == "SAFE")
    warning_count = sum(1 for q in queries if q.injection_risk == "WARNING")
    danger_count = sum(1 for q in queries if q.injection_risk == "DANGER")

    print("\n=== Query Analysis Report ===")
    print(f"Total queries analyzed: {total}")
    print(f"  SAFE: {safe_count}")
    print(f"  WARNING: {warning_count}")
    print(f"  DANGER: {danger_count}")

    # Complexity distribution
    simple_count = sum(1 for q in queries if q.complexity == "SIMPLE")
    moderate_count = sum(1 for q in queries if q.complexity == "MODERATE")
    complex_count = sum(1 for q in queries if q.complexity == "COMPLEX")

    print("\nComplexity distribution:")
    print(f"  SIMPLE: {simple_count}")
    print(f"  MODERATE: {moderate_count}")
    print(f"  COMPLEX: {complex_count}")

    # Dangerous queries
    dangerous = [q for q in queries if q.injection_risk == "DANGER"]
    if dangerous:
        print("\n!!! DANGEROUS QUERIES (potential injection risk) !!!")
        for q in dangerous:
            print(f"  {q.file}:{q.line_number} - {q.class_name}.{q.method_name}")
            print(f"    Query: {q.query[:80]}...")

    # Queries with warnings
    warnings_list = [q for q in queries if q.injection_risk == "WARNING"]
    if warnings_list:
        print("\n--- Queries with warnings ---")
        for q in warnings_list[:5]:  # Show first 5
            print(f"  {q.file}:{q.line_number} - {q.class_name}.{q.method_name}")
            for suggestion in q.suggestions:
                print(f"    Suggestion: {suggestion}")

    # Index suggestions
    if index_suggestions:
        print("\n--- Index Suggestions ---")
        for suggestion in index_suggestions:
            print(
                f"  :{suggestion.node_label}({suggestion.property_name}) - used in {suggestion.query_count} queries"
            )
            if len(suggestion.queries) > 3:
                print(f"    Methods: {', '.join(suggestion.queries[:3])}...")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Cypher queries in repositories"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Analyze specific file",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("src/project_watch_mcp"),
        help="Base directory (default: src/project_watch_mcp)",
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Export analysis to JSON file",
    )
    parser.add_argument(
        "--queries-file",
        type=Path,
        help="Also analyze CypherQueries class (default: infrastructure/neo4j/queries.py)",
    )

    args = parser.parse_args()

    # Find files to analyze
    files: list[Path] = []
    if args.file:
        files = [args.file]
    else:
        # Find all repository implementations
        infra_dir = args.base_dir / "infrastructure" / "neo4j"
        if infra_dir.exists():
            files.extend(infra_dir.glob("*_repository.py"))

    if not files:
        return 0

    # Extract queries
    all_queries: list[QueryAnalysis] = []
    for file_path in files:
        queries = extract_queries_from_file(file_path)
        all_queries.extend(queries)

    # Also extract from queries.py if exists
    queries_file = (
        args.queries_file or args.base_dir / "infrastructure" / "neo4j" / "queries.py"
    )
    if queries_file.exists():
        cypher_queries = extract_queries_from_cypher_queries_class(queries_file)
        all_queries.extend(cypher_queries)

    if not all_queries:
        return 0

    # Analyze and suggest indexes
    index_suggestions = suggest_indexes(all_queries)

    # Export if requested
    if args.export:
        data = {
            "queries": [asdict(q) for q in all_queries],
            "index_suggestions": [asdict(s) for s in index_suggestions],
        }
        args.export.write_text(json.dumps(data, indent=2))

    # Print report
    print_analysis_report(all_queries, index_suggestions)

    # Return error code if dangerous queries found
    has_danger = any(q.injection_risk == "DANGER" for q in all_queries)
    return 1 if has_danger else 0


if __name__ == "__main__":
    sys.exit(main())
