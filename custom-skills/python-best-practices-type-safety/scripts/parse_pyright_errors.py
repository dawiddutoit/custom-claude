#!/usr/bin/env python3
"""Parse Pyright Errors - Categorize and analyze pyright type checking errors.

Categorizes errors by:
- Missing annotations (return types, parameters, variables)
- Type mismatches (assignment, arguments, returns)
- Optional/None handling (member access, subscript, call)
- Generic types (missing arguments, incompatible types)
- Attribute/method errors (unknown members, cannot access)
- Import/module errors (missing imports, stubs, cycles)

Usage:
    uv run pyright src/ | python parse_pyright_errors.py
    uv run pyright src/ > errors.txt
    python parse_pyright_errors.py errors.txt --json

Returns:
    Exit 0: Errors parsed successfully
    Exit 1: Parse error or file not found
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final


@dataclass(slots=True)
class TypeErrorInfo:
    """Structured type error information."""

    file: str
    line: int
    column: int
    category: str
    error_code: str
    message: str
    severity: str = "error"


# Error category patterns with regex and associated pyright error codes
ERROR_PATTERNS: Final[dict[str, list[tuple[str, str]]]] = {
    "missing_annotations": [
        (r"Return type.*is unknown", "reportUnknownReturnType"),
        (r"Type of parameter.*is unknown", "reportUnknownParameterType"),
        (r"Type of.*is unknown", "reportUnknownVariableType"),
        (r"Type of member.*is unknown", "reportUnknownMemberType"),
    ],
    "type_mismatch": [
        (r"cannot be assigned to parameter", "reportArgumentType"),
        (r"cannot be assigned to declared type", "reportAssignmentType"),
        (r"is not assignable to", "reportAssignmentType"),
        (r"Return type.*is not assignable", "reportReturnType"),
        (r"is incompatible with", "reportIncompatibleMethodOverride"),
    ],
    "optional_handling": [
        (r"Cannot access member.*None", "reportOptionalMemberAccess"),
        (r"Cannot subscript.*None", "reportOptionalSubscript"),
        (r"Cannot call.*None", "reportOptionalCall"),
        (r"Object of type.*None.*cannot be used as iterable", "reportOptionalIterable"),
        (r"None.*cannot be used in.*statement", "reportOptionalContextManager"),
    ],
    "generic_types": [
        (r"Expected \d+ type argument", "reportMissingTypeArgument"),
        (r"Type argument.*is missing", "reportMissingTypeArgument"),
        (r"Type.*is incompatible with.*\[", "reportGeneralTypeIssues"),
        (r"cannot be assigned to TypeVar", "reportInvariantTypeVar"),
    ],
    "attribute_method": [
        (r"Cannot access member", "reportAttributeAccessIssue"),
        (r"is not a known member", "reportUnknownMemberType"),
        (r"Cannot call", "reportCallIssue"),
        (r"Cannot subscript", "reportIndexIssue"),
    ],
    "import_module": [
        (r"Import.*could not be resolved", "reportMissingImports"),
        (r"Stub file not found", "reportMissingTypeStubs"),
        (r"creates import cycle", "reportImportCycles"),
        (r"is not exported from", "reportPrivateImportUsage"),
    ],
}

# Fix templates by category
FIX_TEMPLATES: Final[dict[str, str]] = {
    "missing_annotations": """
**Fix Template: Add Type Annotations**

```python
# Missing return type
def func(param: str) -> str:  # Add -> ReturnType
    return param.upper()

# Missing parameter type
def func(param: str):  # Add param: Type
    return param
```
""",
    "type_mismatch": """
**Fix Template: Correct Type Annotations**

```python
# Fix variable type
result: ServiceResult[dict] = service.get_data()  # Match actual type

# Fix argument type
def process(data: dict):  # Ensure argument matches signature
    pass
```
""",
    "optional_handling": """
**Fix Template: Add None Checks**

```python
# Add fail-fast None check
def process(config: Settings | None) -> str:
    if not config:
        raise ValueError("Config required")
    return config.value  # Safe after check
```
""",
    "generic_types": """
**Fix Template: Specify Generic Type Arguments**

```python
# Add type arguments
items: list[str] = []  # Not: list
data: dict[str, int] = {}  # Not: dict
```
""",
    "attribute_method": """
**Fix Template: Fix Attribute Access**

```python
# Use type guard for union types
def process(value: str | int) -> str:
    if isinstance(value, int):
        return str(value)
    return value.strip()  # Safe after guard
```
""",
    "import_module": """
**Fix Template: Fix Import Issues**

```python
# Fix import path
from project_watch_mcp.domain import Entity  # Use full package name

# Handle missing stubs
import voyageai  # type: ignore[import-untyped]

```
""",
}


def parse_pyright_line(line: str) -> TypeErrorInfo | None:
    """Parse a single pyright error line."""
    # Pattern: /path/to/file.py:23:9 - error: Message (errorCode)
    pattern = r"^(.+?):(\d+):(\d+)\s+-\s+(error|warning):\s+(.+?)(?:\s+\((\w+)\))?$"
    match = re.match(pattern, line.strip())

    if not match:
        return None

    file_path, line_num, col_num, severity, message, error_code = match.groups()

    # Categorize error
    category = "unknown"
    if not error_code:
        error_code = "unknown"

    for cat_name, patterns in ERROR_PATTERNS.items():
        for msg_pattern, _ in patterns:
            if re.search(msg_pattern, message, re.IGNORECASE):
                category = cat_name
                break
        if category != "unknown":
            break

    return TypeErrorInfo(
        file=file_path,
        line=int(line_num),
        column=int(col_num),
        category=category,
        error_code=error_code,
        message=message,
        severity=severity,
    )


def group_errors_by_file(
    errors: list[TypeErrorInfo],
) -> dict[str, list[TypeErrorInfo]]:
    """Group errors by file path."""
    grouped: dict[str, list[TypeErrorInfo]] = defaultdict(list)
    for error in errors:
        grouped[error.file].append(error)
    return dict(grouped)


def group_errors_by_category(
    errors: list[TypeErrorInfo],
) -> dict[str, list[TypeErrorInfo]]:
    """Group errors by category."""
    grouped: dict[str, list[TypeErrorInfo]] = defaultdict(list)
    for error in errors:
        grouped[error.category].append(error)
    return dict(grouped)


def generate_report(errors: list[TypeErrorInfo], output_format: str = "text") -> str:
    """Generate error report."""
    if output_format == "json":
        return json.dumps(
            {
                "total_errors": len(errors),
                "by_category": {
                    cat: [asdict(e) for e in errs]
                    for cat, errs in group_errors_by_category(errors).items()
                },
                "by_file": {
                    file: [asdict(e) for e in errs]
                    for file, errs in group_errors_by_file(errors).items()
                },
            },
            indent=2,
        )

    # Text report
    report_parts = []
    report_parts.append("=" * 80)
    report_parts.append("PYRIGHT ERROR ANALYSIS")
    report_parts.append("=" * 80)
    report_parts.append(f"\nTotal Errors: {len(errors)}\n")

    # Summary by category
    by_category = group_errors_by_category(errors)
    report_parts.append("\n" + "─" * 80)
    report_parts.append("ERRORS BY CATEGORY")
    report_parts.append("─" * 80)

    for category, cat_errors in sorted(
        by_category.items(), key=lambda x: len(x[1]), reverse=True
    ):
        count = len(cat_errors)
        percentage = (count / len(errors)) * 100
        report_parts.append(
            f"\n📊 {category.upper().replace('_', ' ')}: {count} errors ({percentage:.1f}%)"
        )

        # Show top 3 files with most errors in this category
        file_counts: dict[str, int] = defaultdict(int)
        for err in cat_errors:
            file_counts[err.file] += 1

        top_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_files:
            report_parts.append("   Top affected files:")
            for file_path, file_count in top_files:
                file_name = Path(file_path).name
                report_parts.append(f"   - {file_name}: {file_count} errors")

        # Show fix template
        if category in FIX_TEMPLATES:
            report_parts.append("\n" + FIX_TEMPLATES[category].strip())

    # Detailed errors by file
    report_parts.append("\n\n" + "─" * 80)
    report_parts.append("ERRORS BY FILE")
    report_parts.append("─" * 80)

    by_file = group_errors_by_file(errors)
    for file_path, file_errors in sorted(
        by_file.items(), key=lambda x: len(x[1]), reverse=True
    ):
        report_parts.append(f"\n📄 {file_path} ({len(file_errors)} errors)")

        # Group by category within file
        file_by_cat = group_errors_by_category(file_errors)
        for category, cat_errors in file_by_cat.items():
            report_parts.append(
                f"\n  {category.replace('_', ' ').title()} ({len(cat_errors)}):"
            )
            for error in sorted(cat_errors, key=lambda e: e.line)[:5]:  # Show first 5
                report_parts.append(
                    f"    Line {error.line}:{error.column} - {error.message[:80]}"
                )
            if len(cat_errors) > 5:
                report_parts.append(f"    ... and {len(cat_errors) - 5} more")

    # Quick fixes summary
    report_parts.append("\n\n" + "─" * 80)
    report_parts.append("QUICK FIXES")
    report_parts.append("─" * 80)

    for category, cat_errors in sorted(
        by_category.items(), key=lambda x: len(x[1]), reverse=True
    ):
        report_parts.append(f"\n{category.upper().replace('_', ' ')}:")
        # Find files with most errors in this category
        file_counts = defaultdict(int)
        for err in cat_errors:
            file_counts[err.file] += 1

        top_file = (
            max(file_counts.items(), key=lambda x: x[1])[0] if file_counts else None
        )
        if top_file:
            report_parts.append(f"  Start with: {Path(top_file).name}")
            report_parts.append(f"  Command: uv run pyright {top_file}")

    report_parts.append("\n" + "=" * 80)

    return "\n".join(report_parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse and categorize pyright type errors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse from stdin
  uv run pyright src/ | python parse_pyright_errors.py

  # Parse from file
  uv run pyright src/ > errors.txt
  python parse_pyright_errors.py errors.txt

  # JSON output
  python parse_pyright_errors.py errors.txt --json

  # Focus on specific category
  python parse_pyright_errors.py errors.txt --category missing_annotations
        """,
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        help="Pyright output file (or stdin if not provided)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--category",
        choices=list(ERROR_PATTERNS.keys()),
        help="Filter by error category",
    )
    parser.add_argument(
        "--file",
        help="Filter by file path (partial match)",
    )

    args = parser.parse_args()

    # Read input
    if args.input_file:
        try:
            with open(args.input_file) as f:
                lines = f.readlines()
        except FileNotFoundError:
            sys.exit(1)
    else:
        lines = sys.stdin.readlines()

    # Parse errors
    errors = []
    for line in lines:
        error = parse_pyright_line(line)
        if error:
            errors.append(error)

    if not errors:
        sys.exit(0)

    # Apply filters
    if args.category:
        errors = [e for e in errors if e.category == args.category]

    if args.file:
        errors = [e for e in errors if args.file in e.file]

    # Generate and print report
    output_format = "json" if args.json else "text"
    report = generate_report(errors, output_format)
    print(report)

    sys.exit(0)


if __name__ == "__main__":
    main()
