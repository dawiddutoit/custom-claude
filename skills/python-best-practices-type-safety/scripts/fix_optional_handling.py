#!/usr/bin/env python3
"""Fix Optional Handling - Automatically add None checks for Optional types.

Features:
- Detects Optional parameters without None checks
- Adds fail-fast None validation
- Handles Optional[T] and T | None syntax
- Suggests TypeGuard usage for complex cases
- Preserves code style and formatting

Usage:
    python fix_optional_handling.py src/services/user_service.py
    python fix_optional_handling.py src/services/user_service.py --dry-run
    python fix_optional_handling.py src/services/user_service.py --function save_user

Returns:
    Exit 0: Success (fixes applied or dry run complete)
    Exit 1: Error (file not found, parse error, etc.)
"""

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class OptionalIssue:
    """Information about an Optional handling issue."""

    function_name: str
    param_name: str
    lineno: int
    col_offset: int
    issue_type: str  # "member_access", "subscript", "call", "iteration"
    access_line: int
    suggested_fix: str


class OptionalCheckVisitor(ast.NodeVisitor):
    """AST visitor to find Optional parameters without None checks."""

    def __init__(self) -> None:
        self.issues: list[OptionalIssue] = []
        self.current_function: str | None = None
        self.optional_params: set[str] = set()
        self.checked_params: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function for Optional parameters."""
        old_function = self.current_function
        old_optional = self.optional_params.copy()
        old_checked = self.checked_params.copy()

        self.current_function = node.name
        self.optional_params = set()
        self.checked_params = set()

        # Find Optional parameters
        for arg in node.args.args:
            if arg.annotation and self._is_optional_type(arg.annotation):
                self.optional_params.add(arg.arg)

        # Check for None checks in function body
        for stmt in node.body:
            self._check_for_none_validation(stmt)

        # Check for unsafe usage of Optional parameters
        for stmt in node.body:
            self._check_for_unsafe_usage(stmt, node)

        self.current_function = old_function
        self.optional_params = old_optional
        self.checked_params = old_checked

        self.generic_visit(node)

    def _is_optional_type(self, annotation: ast.expr) -> bool:
        """Check if annotation is Optional or Union with None."""
        # Handle Optional[T] (which is Union[T, None])
        if isinstance(annotation, ast.Subscript) and isinstance(
            annotation.value, ast.Name
        ):
            if annotation.value.id == "Optional":
                return True
            if annotation.value.id == "Union":
                # Check if None is in the union
                if isinstance(annotation.slice, ast.Tuple):
                    for elt in annotation.slice.elts:
                        if isinstance(elt, ast.Constant) and elt.value is None:
                            return True

        # Handle T | None syntax (Python 3.10+)
        if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
            # Check if either side is None
            if (
                isinstance(annotation.right, ast.Constant)
                and annotation.right.value is None
            ):
                return True
            if (
                isinstance(annotation.left, ast.Constant)
                and annotation.left.value is None
            ):
                return True

        return False

    def _check_for_none_validation(self, node: ast.AST) -> None:
        """Check if statement validates None for Optional parameters."""
        if isinstance(node, ast.If):
            # Check for patterns like: if not param: or if param is None:
            test = node.test

            # Pattern: if not param:
            if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
                if isinstance(test.operand, ast.Name):
                    if test.operand.id in self.optional_params:
                        self.checked_params.add(test.operand.id)

            # Pattern: if param is None:
            elif isinstance(test, ast.Compare) and isinstance(test.left, ast.Name):
                if test.left.id in self.optional_params:
                    for comparator in test.comparators:
                        if (
                            isinstance(comparator, ast.Constant)
                            and comparator.value is None
                        ):
                            self.checked_params.add(test.left.id)

        # Recursively check nested statements
        for child in ast.iter_child_nodes(node):
            self._check_for_none_validation(child)

    def _check_for_unsafe_usage(
        self, node: ast.AST, func_node: ast.FunctionDef
    ) -> None:
        """Check for unsafe usage of Optional parameters."""
        # Member access: param.attribute
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and (
                node.value.id in self.optional_params
                and node.value.id not in self.checked_params
            ):
                self.issues.append(
                    OptionalIssue(
                        function_name=self.current_function or "unknown",
                        param_name=node.value.id,
                        lineno=func_node.lineno,
                        col_offset=func_node.col_offset,
                        issue_type="member_access",
                        access_line=node.lineno,
                        suggested_fix=self._generate_fix(
                            node.value.id, "member_access", func_node
                        ),
                    )
                )

        # Subscript: param[key]
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name) and (
                node.value.id in self.optional_params
                and node.value.id not in self.checked_params
            ):
                self.issues.append(
                    OptionalIssue(
                        function_name=self.current_function or "unknown",
                        param_name=node.value.id,
                        lineno=func_node.lineno,
                        col_offset=func_node.col_offset,
                        issue_type="subscript",
                        access_line=node.lineno,
                        suggested_fix=self._generate_fix(
                            node.value.id, "subscript", func_node
                        ),
                    )
                )

        # Function call: param()
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if (
                node.func.id in self.optional_params
                and node.func.id not in self.checked_params
            ):
                self.issues.append(
                    OptionalIssue(
                        function_name=self.current_function or "unknown",
                        param_name=node.func.id,
                        lineno=func_node.lineno,
                        col_offset=func_node.col_offset,
                        issue_type="call",
                        access_line=node.lineno,
                        suggested_fix=self._generate_fix(
                            node.func.id, "call", func_node
                        ),
                    )
                )

        # Recursively check children
        for child in ast.iter_child_nodes(node):
            self._check_for_unsafe_usage(child, func_node)

    def _generate_fix(
        self,
        param_name: str,
        issue_type: str,  # noqa: ARG002 - reserved for future use
        func_node: ast.FunctionDef,  # noqa: ARG002 - reserved for future use
    ) -> str:
        """Generate suggested fix for Optional issue."""
        # Generate a human-readable label from the parameter name
        label = param_name.replace("_", " ").title()
        return f"""    if not {param_name}:
        raise ValueError("{label} is required")"""


def analyze_file(
    file_path: Path, function_filter: str | None = None
) -> list[OptionalIssue]:
    """Analyze a Python file for Optional handling issues."""
    try:
        with open(file_path) as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        visitor = OptionalCheckVisitor()
        visitor.visit(tree)

        # Filter by function if specified
        if function_filter:
            return [
                issue
                for issue in visitor.issues
                if issue.function_name == function_filter
            ]

        return visitor.issues

    except SyntaxError:
        sys.exit(1)
    except FileNotFoundError:
        sys.exit(1)


def apply_fixes(
    file_path: Path,
    issues: list[OptionalIssue],
    dry_run: bool,
) -> int:
    """Apply None check fixes to file."""
    if not issues:
        return 0

    # Read file
    with open(file_path) as f:
        lines = f.readlines()

    modifications = 0

    # Group issues by function
    by_function: dict[str, list[OptionalIssue]] = {}
    for issue in issues:
        if issue.function_name not in by_function:
            by_function[issue.function_name] = []
        by_function[issue.function_name].append(issue)

    # Process each function
    for func_issues in by_function.values():
        # Get the function's first issue for line number
        first_issue = func_issues[0]
        func_line_idx = first_issue.lineno - 1

        if func_line_idx >= len(lines):
            continue

        # Find the first line of the function body (after the def line)
        # Look for first non-decorator, non-def line
        body_start_idx = func_line_idx + 1
        while body_start_idx < len(lines):
            line = lines[body_start_idx].strip()
            if line and not line.startswith(('"""', "'''", "#")):
                break
            body_start_idx += 1

        # Skip docstring if present
        if body_start_idx < len(lines):
            line = lines[body_start_idx].strip()
            if line.startswith(('"""', "'''")):
                # Find end of docstring
                quote = '"""' if line.startswith('"""') else "'''"
                body_start_idx += 1
                while body_start_idx < len(lines):
                    if quote in lines[body_start_idx]:
                        body_start_idx += 1
                        break
                    body_start_idx += 1

        # Insert None checks at the beginning of function body
        indent = "    "  # Assume 4-space indent
        check_lines = []

        for issue in func_issues:
            check_lines.append(f"{indent}{issue.suggested_fix.strip()}\n")
            check_lines.append("\n")  # Blank line after check

        if not dry_run:
            # Insert the checks
            for line in reversed(check_lines):
                lines.insert(body_start_idx, line)
            modifications += len(func_issues)

    if dry_run:
        return len(issues)

    # Write back if not dry run
    if modifications > 0:
        with open(file_path, "w") as f:
            f.writelines(lines)

    return modifications


def generate_report(file_path: Path, issues: list[OptionalIssue]) -> str:
    """Generate detailed report of Optional handling issues."""
    if not issues:
        return f"✅ {file_path.name}: No Optional handling issues found"

    report_parts = []
    report_parts.append("=" * 80)
    report_parts.append(f"OPTIONAL HANDLING ANALYSIS: {file_path.name}")
    report_parts.append("=" * 80)
    report_parts.append(f"\nTotal Issues: {len(issues)}\n")

    # Group by function
    by_function: dict[str, list[OptionalIssue]] = {}
    for issue in issues:
        if issue.function_name not in by_function:
            by_function[issue.function_name] = []
        by_function[issue.function_name].append(issue)

    # Group by issue type
    by_type: dict[str, int] = {}
    for issue in issues:
        by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1

    report_parts.append("📊 Issues by Type:")
    for issue_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        report_parts.append(f"   {issue_type.replace('_', ' ').title()}: {count}")

    report_parts.append("\n" + "─" * 80)
    report_parts.append("ISSUES BY FUNCTION")
    report_parts.append("─" * 80)

    for func_name, func_issues in sorted(by_function.items()):
        report_parts.append(f"\n📍 {func_name}() - Line {func_issues[0].lineno}")
        report_parts.append(f"   Issues: {len(func_issues)}")

        for issue in func_issues:
            report_parts.append(
                f"\n   ⚠️  {issue.param_name} ({issue.issue_type}) at line {issue.access_line}"
            )
            report_parts.append("   Suggested fix:")
            for line in issue.suggested_fix.split("\n"):
                report_parts.append(f"   {line}")

    report_parts.append("\n" + "─" * 80)
    report_parts.append("RECOMMENDED ACTIONS")
    report_parts.append("─" * 80)
    report_parts.append(
        f"\n1. Review {len(by_function)} function(s) with Optional parameters"
    )
    report_parts.append("2. Add None checks at start of each function (fail-fast)")
    report_parts.append(
        f"3. Run: python fix_optional_handling.py {file_path} (without --dry-run)"
    )
    report_parts.append(f"4. Verify: uv run pyright {file_path}")
    report_parts.append("5. Run tests to ensure no breakage")

    report_parts.append("\n" + "=" * 80)

    return "\n".join(report_parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix Optional/None handling issues in Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix all Optional issues in a file
  python fix_optional_handling.py src/services/user_service.py

  # Dry run to see what would be changed
  python fix_optional_handling.py src/services/user_service.py --dry-run

  # Generate detailed report
  python fix_optional_handling.py src/services/user_service.py --report

  # Fix specific function only
  python fix_optional_handling.py src/services/user_service.py --function save_user

Note:
  - Adds fail-fast None checks at start of functions
  - Follows project pattern: if not param: raise ValueError()
  - Always review changes before committing
  - Run pyright and tests after applying fixes
        """,
    )

    parser.add_argument("file", type=Path, help="Python file to analyze")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying file",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report of issues",
    )
    parser.add_argument(
        "--function",
        help="Only fix specific function",
    )

    args = parser.parse_args()

    # Analyze file
    issues = analyze_file(args.file, args.function)

    if not issues:
        sys.exit(0)

    # Generate report if requested
    if args.report:
        report = generate_report(args.file, issues)
        print(report)
        sys.exit(0)

    # Show summary
    by_function: dict[str, list[OptionalIssue]] = {}
    for issue in issues:
        if issue.function_name not in by_function:
            by_function[issue.function_name] = []
        by_function[issue.function_name].append(issue)

    print(
        f"Found {len(issues)} Optional handling issues in {len(by_function)} function(s)"
    )

    # Apply fixes
    modifications = apply_fixes(args.file, issues, args.dry_run)

    if args.dry_run:
        print(f"Would apply {modifications} fixes (dry run)")
    elif modifications > 0:
        print(f"Applied {modifications} fixes to {args.file}")

    sys.exit(0)


if __name__ == "__main__":
    main()
