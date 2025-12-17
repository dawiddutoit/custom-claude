#!/usr/bin/env python3
"""Example usage of the log analyzer tools.

This example demonstrates using the shared .claude/ Python environment
to run log analysis tasks without requiring external dependencies.

The log analyzer provides:
- OpenTelemetry log parsing with trace/span extraction
- Error extraction with surrounding context
- Multiple output formats (text, markdown, JSON)
- Trace-based error grouping

Usage:
    cd ~/.claude && python3 skills/observability-analyze-logs/scripts/example_usage.py

Note: Replace LOG_DIR and LOG_FILE with your project's actual log location.
"""

import sys
from pathlib import Path

# Add tools directory to path for imports
_tools_dir = Path(__file__).parent.parent.parent.parent / "tools"
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from otel_logging import (  # noqa: E402  # type: ignore[import-not-found]
    ErrorExtractor,
    LogReportFormatter,
    OTelLogParser,
)


def example_basic_analysis(log_path: Path) -> None:
    """Example 1: Basic log analysis workflow.

    Demonstrates the most common usage pattern:
    1. Parse log file
    2. Extract errors with context
    3. Generate summary report
    """
    print("=" * 60)
    print("Example 1: Basic Log Analysis")
    print("=" * 60)

    # Parse the log file
    parser = OTelLogParser()
    entries = parser.parse_file(log_path)
    print(f"Parsed {len(entries)} log entries")

    # Extract errors with 3 lines of context
    extractor = ErrorExtractor(context_lines=3)
    errors = extractor.extract_errors(entries)
    print(f"Found {len(errors)} errors")

    # Group by trace to see related errors
    traces = parser.group_by_trace(entries)
    print(f"Across {len(traces)} unique traces")

    # Format as summary
    formatter = LogReportFormatter()
    report = formatter.format_summary(
        errors,
        total_entries=len(entries),
        total_traces=len(traces),
        output_format="text",
    )
    print()
    print(report)


def example_markdown_report(log_path: Path) -> None:
    """Example 2: Generate markdown report.

    Shows how to generate a detailed markdown report
    suitable for documentation or issue tracking.
    """
    print("\n" + "=" * 60)
    print("Example 2: Markdown Report")
    print("=" * 60)

    parser = OTelLogParser()
    entries = parser.parse_file(log_path)

    extractor = ErrorExtractor(context_lines=3)
    errors = extractor.extract_errors(entries)

    traces = parser.group_by_trace(entries)

    formatter = LogReportFormatter()
    report = formatter.format_summary(
        errors,
        total_entries=len(entries),
        total_traces=len(traces),
        output_format="markdown",
    )
    print(report)


def example_error_detail(log_path: Path) -> None:
    """Example 3: Detailed error investigation.

    Shows how to get full details for a specific error,
    including context before/after and related errors.
    """
    print("\n" + "=" * 60)
    print("Example 3: Error Detail View")
    print("=" * 60)

    parser = OTelLogParser()
    entries = parser.parse_file(log_path)

    extractor = ErrorExtractor(context_lines=5)
    errors = extractor.extract_errors(entries)

    if not errors:
        print("No errors found to investigate")
        return

    # Get detailed view of first error
    formatter = LogReportFormatter()
    detail = formatter.format_error_detail(
        errors[0],
        error_id=1,
        output_format="markdown",
    )
    print(detail)


def example_trace_analysis(log_path: Path) -> None:
    """Example 4: Trace-based debugging.

    Shows how to analyze a complete execution trace,
    useful for understanding the flow leading to errors.
    """
    print("\n" + "=" * 60)
    print("Example 4: Trace Analysis")
    print("=" * 60)

    parser = OTelLogParser()
    entries = parser.parse_file(log_path)

    traces = parser.group_by_trace(entries)

    if not traces:
        print("No traces found")
        return

    # Find a trace with errors
    trace_with_errors = None
    for trace in traces.values():
        if trace.has_errors:
            trace_with_errors = trace
            break

    if trace_with_errors is None:
        # Just show first trace if no errors
        trace_with_errors = next(iter(traces.values()))
        print("No traces with errors found, showing first trace:")
    else:
        print(f"Found trace with {len(trace_with_errors.errors)} errors:")

    formatter = LogReportFormatter()
    report = formatter.format_trace(trace_with_errors, output_format="text")
    print(report)


def example_filter_by_file(log_path: Path, file_pattern: str) -> None:
    """Example 5: Filter errors by file.

    Shows how to find all errors from a specific source file.
    """
    print("\n" + "=" * 60)
    print(f"Example 5: Filter by File ({file_pattern})")
    print("=" * 60)

    parser = OTelLogParser()
    entries = parser.parse_file(log_path)

    extractor = ErrorExtractor()
    errors = extractor.extract_errors(entries)

    # Group by file
    by_file = extractor.group_by_file(errors)

    print("Errors by file:")
    for file_name, file_errors in sorted(by_file.items()):
        if file_pattern in file_name:
            print(f"\n{file_name}: {len(file_errors)} errors")
            for ctx in file_errors[:3]:
                err = ctx.error
                msg_preview = (
                    err.message[:60] + "..." if len(err.message) > 60 else err.message
                )
                print(f"  Line {err.line}: {msg_preview}")


def example_json_export(log_path: Path) -> None:
    """Example 6: JSON export for programmatic use.

    Shows how to generate JSON output suitable for
    further processing or integration with other tools.
    """
    print("\n" + "=" * 60)
    print("Example 6: JSON Export")
    print("=" * 60)

    parser = OTelLogParser()
    entries = parser.parse_file(log_path)

    extractor = ErrorExtractor()
    errors = extractor.extract_errors(entries)

    traces = parser.group_by_trace(entries)

    formatter = LogReportFormatter()
    json_output = formatter.format_summary(
        errors[:5],  # Limit for example
        total_entries=len(entries),
        total_traces=len(traces),
        output_format="json",
    )
    print(json_output)


def create_sample_log_file(path: Path) -> None:
    """Create a sample log file for demonstration purposes."""
    sample_logs = """\
2025-10-16 14:32:15 - [trace:abc123def456 | span:span001] - app.database - INFO - [database.py:45] - connect() - Connecting to database
2025-10-16 14:32:16 - [trace:abc123def456 | span:span002] - app.database - ERROR - [database.py:67] - execute_query() - Connection timeout after 5000ms
2025-10-16 14:32:16 - [trace:abc123def456 | span:span003] - app.database - INFO - [database.py:89] - retry() - Retrying connection
2025-10-16 14:32:17 - [trace:abc123def456 | span:span004] - app.database - ERROR - [database.py:67] - execute_query() - Retry failed: max attempts exceeded
2025-10-16 14:32:18 - [trace:xyz789ghi012 | span:span005] - app.api - INFO - [api.py:23] - handle_request() - Processing GET /users
2025-10-16 14:32:19 - [trace:xyz789ghi012 | span:span006] - app.api - WARNING - [api.py:45] - validate() - Missing optional header: X-Request-ID
2025-10-16 14:32:20 - [trace:xyz789ghi012 | span:span007] - app.api - INFO - [api.py:67] - respond() - Request completed in 234ms
2025-10-16 14:32:21 - [trace:mno345pqr678 | span:span008] - app.auth - INFO - [auth.py:12] - authenticate() - Validating token
2025-10-16 14:32:22 - [trace:mno345pqr678 | span:span009] - app.auth - ERROR - [auth.py:34] - verify_token() - Invalid signature: token expired
2025-10-16 14:32:23 - [trace:mno345pqr678 | span:span010] - app.auth - INFO - [auth.py:56] - cleanup() - Session invalidated
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sample_logs, encoding="utf-8")
    print(f"Created sample log file: {path}")


def main() -> int:
    """Run all examples.

    Returns:
        Exit code (0 for success).
    """
    # Determine log file path
    # Check for user-specified path via command line
    if len(sys.argv) > 1:
        log_path = Path(sys.argv[1])
        if not log_path.exists():
            print(f"Error: Log file not found: {log_path}", file=sys.stderr)
            return 1
    else:
        # Use a sample log file in temp directory
        log_path = Path("/tmp/sample_otel.log")
        if not log_path.exists():
            print("No log file specified. Creating sample log file...")
            create_sample_log_file(log_path)

    print(f"Analyzing log file: {log_path}")
    print()

    try:
        # Run examples
        example_basic_analysis(log_path)
        example_markdown_report(log_path)
        example_error_detail(log_path)
        example_trace_analysis(log_path)
        example_filter_by_file(log_path, "database")
        example_json_export(log_path)

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
