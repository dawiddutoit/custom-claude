#!/usr/bin/env python3
"""Analyze codebase to find operations that need retry logic.

This script scans Python files for operations that may fail transiently and
suggests adding retry logic. Detects:
- Network calls (aiohttp, requests, urllib)
- Database operations (neo4j, postgresql, mongodb)
- External API calls
- File I/O operations
- Async operations without error handling

Usage:
    python analyze_retryable_operations.py [paths...]

Examples:
    # Analyze single file
    python analyze_retryable_operations.py src/services/api_service.py

    # Analyze directory
    python analyze_retryable_operations.py src/services/

    # Generate report with priority levels
    python analyze_retryable_operations.py src/ --priority high

    # Output as JSON for processing
    python analyze_retryable_operations.py src/ --format json
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RetryableOperation:
    """Represents an operation that should have retry logic."""

    file_path: str
    line_number: int
    method_name: str
    operation_type: str  # "network", "database", "api", "file_io"
    priority: str  # "high", "medium", "low"
    description: str
    suggested_exceptions: list[str] = field(default_factory=list)
    has_retry: bool = False
    has_error_handling: bool = False

    @property
    def risk_score(self) -> int:
        """Calculate risk score (0-10) based on factors."""
        score = 0

        # Base score by operation type
        type_scores = {
            "network": 8,
            "database": 7,
            "api": 9,
            "file_io": 5,
            "unknown": 3,
        }
        score += type_scores.get(self.operation_type, 3)

        # Reduce score if has error handling
        if self.has_error_handling:
            score -= 2

        # Reduce score if already has retry
        if self.has_retry:
            score -= 5

        return max(0, min(10, score))


@dataclass
class AnalysisResult:
    """Results of retryable operations analysis."""

    file_path: str
    operations: list[RetryableOperation] = field(default_factory=list)
    total_async_methods: int = 0
    methods_with_retry: int = 0

    @property
    def high_priority_operations(self) -> list[RetryableOperation]:
        """Get high priority operations."""
        return [op for op in self.operations if op.priority == "high"]

    @property
    def methods_needing_retry(self) -> int:
        """Count methods needing retry logic."""
        return len([op for op in self.operations if not op.has_retry])


class RetryableOperationAnalyzer(ast.NodeVisitor):
    """AST visitor that finds operations needing retry logic."""

    # Network operation patterns
    NETWORK_CALLS = {
        "aiohttp.ClientSession",
        "aiohttp.request",
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "urllib.request.urlopen",
        "httpx.AsyncClient",
        "httpx.Client",
    }

    # Database operation patterns
    DATABASE_CALLS = {
        "neo4j.AsyncGraphDatabase",
        "neo4j.GraphDatabase",
        "asyncpg.connect",
        "psycopg2.connect",
        "pymongo.MongoClient",
        "motor.motor_asyncio.AsyncIOMotorClient",
        "execute_query",
        "run_query",
        "execute_write",
        "execute_read",
    }

    # API client patterns
    API_PATTERNS = {
        "openai.ChatCompletion",
        "anthropic.Anthropic",
        "voyage.Client",
        "embeddings",
        "generate",
    }

    def __init__(self, file_path: str) -> None:
        """Initialize analyzer.

        Args:
            file_path: Path to file being analyzed
        """
        self.file_path = file_path
        self.result = AnalysisResult(file_path=file_path)
        self.current_method: str | None = None
        self.current_method_has_retry = False
        self.current_method_has_error_handling = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self.result.total_async_methods += 1
        self.current_method = node.name
        self.current_method_has_retry = self._has_retry_loop(node)
        self.current_method_has_error_handling = self._has_try_except(node)

        if self.current_method_has_retry:
            self.result.methods_with_retry += 1

        # Analyze the method body
        self.generic_visit(node)

        self.current_method = None
        self.current_method_has_retry = False
        self.current_method_has_error_handling = False

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to detect retryable operations."""
        if not self.current_method:
            self.generic_visit(node)
            return

        # Get full call name
        call_name = self._get_call_name(node)

        # Check for network operations
        if any(pattern in call_name for pattern in self.NETWORK_CALLS):
            self._add_operation(
                node=node,
                operation_type="network",
                description=f"Network call: {call_name}",
                suggested_exceptions=[
                    "aiohttp.ClientConnectionError",
                    "aiohttp.ServerDisconnectedError",
                    "TimeoutError",
                    "ConnectionError",
                ],
            )

        # Check for database operations
        elif any(pattern in call_name for pattern in self.DATABASE_CALLS):
            self._add_operation(
                node=node,
                operation_type="database",
                description=f"Database operation: {call_name}",
                suggested_exceptions=[
                    "neo4j.exceptions.ServiceUnavailable",
                    "neo4j.exceptions.SessionExpired",
                    "ConnectionError",
                    "TimeoutError",
                ],
            )

        # Check for API calls
        elif any(pattern in call_name for pattern in self.API_PATTERNS):
            self._add_operation(
                node=node,
                operation_type="api",
                description=f"External API call: {call_name}",
                suggested_exceptions=[
                    "TimeoutError",
                    "ConnectionError",
                    "aiohttp.ClientError",
                ],
            )

        # Check for file operations
        elif "open(" in call_name or "read(" in call_name or "write(" in call_name:
            self._add_operation(
                node=node,
                operation_type="file_io",
                description=f"File I/O operation: {call_name}",
                suggested_exceptions=["IOError", "OSError"],
            )

        self.generic_visit(node)

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract full call name from call node.

        Args:
            node: Call node

        Returns:
            String representation of call name
        """
        try:
            return ast.unparse(node.func)
        except Exception:
            return "unknown"

    def _add_operation(
        self,
        node: ast.Call,
        operation_type: str,
        description: str,
        suggested_exceptions: list[str],
    ) -> None:
        """Add retryable operation to results.

        Args:
            node: AST node of operation
            operation_type: Type of operation
            description: Human-readable description
            suggested_exceptions: List of exception types to handle
        """
        # Determine priority based on operation type and current error handling
        priority = self._calculate_priority(operation_type)

        operation = RetryableOperation(
            file_path=self.file_path,
            line_number=node.lineno,
            method_name=self.current_method or "unknown",
            operation_type=operation_type,
            priority=priority,
            description=description,
            suggested_exceptions=suggested_exceptions,
            has_retry=self.current_method_has_retry,
            has_error_handling=self.current_method_has_error_handling,
        )

        self.result.operations.append(operation)

    def _calculate_priority(self, operation_type: str) -> str:
        """Calculate priority level for operation.

        Args:
            operation_type: Type of operation

        Returns:
            Priority level: "high", "medium", or "low"
        """
        # If already has retry, low priority
        if self.current_method_has_retry:
            return "low"

        # No error handling at all - high priority
        if not self.current_method_has_error_handling:
            if operation_type in ("network", "api", "database"):
                return "high"
            return "medium"

        # Has error handling but no retry
        if operation_type in ("network", "api"):
            return "high"
        if operation_type == "database":
            return "medium"
        return "low"

    def _has_retry_loop(self, node: ast.AsyncFunctionDef) -> bool:
        """Check if function has retry loop.

        Args:
            node: Function definition node

        Returns:
            True if retry loop found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.For) and isinstance(child.iter, ast.Call):
                if isinstance(child.iter.func, ast.Name) and child.iter.func.id == "range":
                    # Check if variable name suggests retry
                    if isinstance(child.target, ast.Name) and (
                        "retry" in child.target.id.lower()
                        or "attempt" in child.target.id.lower()
                    ):
                        return True
        return False

    def _has_try_except(self, node: ast.AsyncFunctionDef) -> bool:
        """Check if function has try/except block.

        Args:
            node: Function definition node

        Returns:
            True if try/except found
        """
        return any(isinstance(child, ast.Try) for child in ast.walk(node))


def analyze_file(file_path: Path) -> AnalysisResult:
    """Analyze single file for retryable operations.

    Args:
        file_path: Path to Python file

    Returns:
        AnalysisResult with operations found
    """
    try:
        source_code = file_path.read_text()
        tree = ast.parse(source_code)

        analyzer = RetryableOperationAnalyzer(str(file_path))
        analyzer.visit(tree)

        return analyzer.result

    except SyntaxError:
        return AnalysisResult(file_path=str(file_path))

    except Exception:
        return AnalysisResult(file_path=str(file_path))


def analyze_directory(directory: Path) -> list[AnalysisResult]:
    """Analyze all Python files in directory.

    Args:
        directory: Path to directory

    Returns:
        List of AnalysisResults
    """
    results = []
    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and test files
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue

        result = analyze_file(py_file)
        if result.operations:
            results.append(result)

    return results


def print_results(
    results: list[AnalysisResult],
    output_format: str = "text",
    priority_filter: str | None = None,
) -> None:
    """Print analysis results.

    Args:
        results: List of analysis results
        output_format: Output format ("text" or "json")
        priority_filter: Filter by priority ("high", "medium", "low")
    """
    # Filter operations by priority if specified
    filtered_results = results
    if priority_filter:
        filtered_results = []
        for result in results:
            filtered_ops = [op for op in result.operations if op.priority == priority_filter]
            if filtered_ops:
                filtered_result = AnalysisResult(
                    file_path=result.file_path,
                    operations=filtered_ops,
                    total_async_methods=result.total_async_methods,
                    methods_with_retry=result.methods_with_retry,
                )
                filtered_results.append(filtered_result)

    if output_format == "json":
        output = {
            "summary": {
                "total_files": len(filtered_results),
                "total_operations": sum(len(r.operations) for r in filtered_results),
                "high_priority": sum(len(r.high_priority_operations) for r in filtered_results),
                "methods_needing_retry": sum(r.methods_needing_retry for r in filtered_results),
            },
            "files": [
                {
                    "path": r.file_path,
                    "async_methods": r.total_async_methods,
                    "methods_with_retry": r.methods_with_retry,
                    "operations": [
                        {
                            "line": op.line_number,
                            "method": op.method_name,
                            "type": op.operation_type,
                            "priority": op.priority,
                            "risk_score": op.risk_score,
                            "description": op.description,
                            "has_retry": op.has_retry,
                            "suggested_exceptions": op.suggested_exceptions,
                        }
                        for op in r.operations
                    ],
                }
                for r in filtered_results
            ],
        }
        print(json.dumps(output, indent=2))
        return

    # Text format
    total_operations = sum(len(r.operations) for r in filtered_results)
    high_priority = sum(len(r.high_priority_operations) for r in filtered_results)
    methods_needing_retry = sum(r.methods_needing_retry for r in filtered_results)

    print("\n=== Retryable Operations Analysis ===")
    print(f"Total operations found: {total_operations}")
    print(f"High priority: {high_priority}")
    print(f"Methods needing retry: {methods_needing_retry}")

    # Group by priority
    for priority_level in ["high", "medium", "low"]:
        priority_ops = [
            (r, op)
            for r in filtered_results
            for op in r.operations
            if op.priority == priority_level
        ]

        if not priority_ops:
            continue

        print(f"\n--- {priority_level.upper()} Priority ---")
        for _result, operation in priority_ops:
            status = "[HAS RETRY]" if operation.has_retry else "[NEEDS RETRY]"
            print(f"  {status} {operation.file_path}:{operation.line_number}")
            print(f"    Method: {operation.method_name}")
            print(f"    {operation.description}")
            if operation.suggested_exceptions and not operation.has_retry:
                print(f"    Suggested exceptions: {', '.join(operation.suggested_exceptions)}")

    if high_priority > 0:
        print(f"\n[!] {high_priority} high-priority operations need retry logic")

    if methods_needing_retry > 0:
        print("\nRun: python add_retry_logic.py <file> <method> to add retry logic")




def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze codebase for operations needing retry logic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files or directories to analyze",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--priority",
        choices=["high", "medium", "low"],
        help="Filter by priority level",
    )

    args = parser.parse_args()

    # Collect all results
    all_results: list[AnalysisResult] = []

    for path in args.paths:
        if not path.exists():
            return 1

        if path.is_file():
            result = analyze_file(path)
            if result.operations:
                all_results.append(result)
        elif path.is_dir():
            results = analyze_directory(path)
            all_results.extend(results)

    if not all_results:
        return 0

    # Print results
    print_results(all_results, output_format=args.format, priority_filter=args.priority)

    return 0


if __name__ == "__main__":
    sys.exit(main())
