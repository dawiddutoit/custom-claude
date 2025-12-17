#!/usr/bin/env python3
"""Fix Missing Annotations - Automatically add type hints to Python files.

Features:
- Infers return types from return statements
- Infers parameter types from usage
- Handles ServiceResult[T] pattern
- Preserves existing annotations
- Uses AST for accurate parsing

Usage:
    python fix_missing_annotations.py src/services/user_service.py --all
    python fix_missing_annotations.py src/services/user_service.py --return-types
    python fix_missing_annotations.py src/services/user_service.py --all --dry-run

Returns:
    Exit 0: Success (annotations added or dry run complete)
    Exit 1: Error (file not found, parse error, etc.)
"""

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FunctionInfo:
    """Information about a function needing annotations."""

    name: str
    lineno: int
    col_offset: int
    needs_return_type: bool
    needs_param_types: tuple[str, ...]
    inferred_return_type: str | None
    inferred_param_types: dict[str, str]


class TypeInferenceVisitor(ast.NodeVisitor):
    """AST visitor to find functions missing type annotations."""

    def __init__(self) -> None:
        self.functions: list[FunctionInfo] = []
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track current class for context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function for missing annotations."""
        # Skip if function already has complete annotations
        needs_return_type = node.returns is None
        needs_param_types: list[str] = []

        for arg in node.args.args:
            if arg.annotation is None and arg.arg not in {"self", "cls"}:
                needs_param_types.append(arg.arg)

        if not needs_return_type and not needs_param_types:
            self.generic_visit(node)
            return

        # Infer types
        inferred_return = self._infer_return_type(node)
        inferred_params = self._infer_param_types(node)

        self.functions.append(
            FunctionInfo(
                name=node.name,
                lineno=node.lineno,
                col_offset=node.col_offset,
                needs_return_type=needs_return_type,
                needs_param_types=tuple(needs_param_types),
                inferred_return_type=inferred_return,
                inferred_param_types=inferred_params,
            )
        )

        self.generic_visit(node)

    def _infer_return_type(self, node: ast.FunctionDef) -> str | None:
        """Infer return type from return statements."""
        return_types = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                if child.value is None:
                    return_types.add("None")
                elif isinstance(child.value, ast.Call):
                    # Check for ServiceResult pattern
                    if isinstance(child.value.func, ast.Attribute):
                        if child.value.func.attr in ("success", "failure"):
                            if isinstance(child.value.func.value, ast.Name):
                                if child.value.func.value.id == "ServiceResult":
                                    # Try to infer generic type
                                    if child.value.args:
                                        arg_type = self._infer_expr_type(
                                            child.value.args[0]
                                        )
                                        return_types.add(f"ServiceResult[{arg_type}]")
                                    else:
                                        return_types.add("ServiceResult[None]")
                    else:
                        # Generic function call
                        return_types.add("Any")
                elif isinstance(child.value, ast.Constant):
                    if isinstance(child.value.value, str):
                        return_types.add("str")
                    elif isinstance(child.value.value, int):
                        return_types.add("int")
                    elif isinstance(child.value.value, bool):
                        return_types.add("bool")
                    elif child.value.value is None:
                        return_types.add("None")
                elif isinstance(child.value, ast.List):
                    return_types.add("list[Any]")
                elif isinstance(child.value, ast.Dict):
                    return_types.add("dict[str, Any]")

        if not return_types:
            return None

        # If multiple return types, use union
        if len(return_types) == 1:
            return return_types.pop()
        if "None" in return_types:
            non_none = return_types - {"None"}
            if len(non_none) == 1:
                return f"{non_none.pop()} | None"
            return " | ".join(sorted(return_types))
        return " | ".join(sorted(return_types))

    def _infer_expr_type(self, expr: ast.expr) -> str:
        """Infer type from expression."""
        if isinstance(expr, ast.Constant):
            if isinstance(expr.value, str):
                return "str"
            if isinstance(expr.value, int):
                return "int"
            if isinstance(expr.value, bool):
                return "bool"
            if expr.value is None:
                return "None"
        elif isinstance(expr, ast.List):
            return "list[Any]"
        elif isinstance(expr, ast.Dict):
            return "dict[str, Any]"
        elif isinstance(expr, ast.Name):
            return expr.id
        return "Any"

    def _infer_param_types(self, node: ast.FunctionDef) -> dict[str, str]:
        """Infer parameter types from usage within function."""
        param_types: dict[str, str] = {}

        # Simple heuristics based on usage
        for param in node.args.args:
            if param.arg in ("self", "cls"):
                continue

            param_type = "Any"

            # Look for method calls or attribute access
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute):
                    if (
                        isinstance(child.value, ast.Name)
                        and child.value.id == param.arg
                    ):
                        # Parameter has attributes, likely an object
                        if child.attr in ("strip", "upper", "lower", "split"):
                            param_type = "str"
                        elif child.attr in ("append", "extend", "pop"):
                            param_type = "list[Any]"
                        elif child.attr in ("get", "keys", "values", "items"):
                            param_type = "dict[str, Any]"

                elif isinstance(child, ast.Call):
                    # Check if parameter is used in specific function calls
                    if isinstance(child.func, ast.Name):
                        if child.func.id == "len" and any(
                            isinstance(arg, ast.Name) and arg.id == param.arg
                            for arg in child.args
                        ):
                            param_type = "list[Any] | dict[str, Any] | str"

            param_types[param.arg] = param_type

        return param_types


def analyze_file(file_path: Path) -> list[FunctionInfo]:
    """Analyze a Python file for missing annotations."""
    try:
        with open(file_path) as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        visitor = TypeInferenceVisitor()
        visitor.visit(tree)
        return visitor.functions

    except SyntaxError:
        sys.exit(1)
    except FileNotFoundError:
        sys.exit(1)


def generate_annotations_patch(
    file_path: Path,
    functions: list[FunctionInfo],
    fix_returns: bool,
    fix_params: bool,
) -> list[str]:
    """Generate patch suggestions for missing annotations."""
    patches = []

    for func in functions:
        suggestions = []

        if fix_returns and func.needs_return_type and func.inferred_return_type:
            suggestions.append(f"  Add return type: -> {func.inferred_return_type}")

        if fix_params and func.needs_param_types:
            for param in func.needs_param_types:
                param_type = func.inferred_param_types.get(param, "Any")
                suggestions.append(f"  Add parameter type: {param}: {param_type}")

        if suggestions:
            patches.append(f"\n{file_path}:{func.lineno} - {func.name}()")
            patches.extend(suggestions)

    return patches


def apply_annotations(
    file_path: Path,
    functions: list[FunctionInfo],
    fix_returns: bool,
    fix_params: bool,
    dry_run: bool,
) -> int:
    """Apply type annotations to file."""
    if not functions:
        return 0

    # Read file
    with open(file_path) as f:
        lines = f.readlines()

    modifications = 0

    # Process each function (reverse order to preserve line numbers)
    for func in sorted(functions, key=lambda f: f.lineno, reverse=True):
        # Find function definition line
        func_line_idx = func.lineno - 1
        if func_line_idx >= len(lines):
            continue

        func_line = lines[func_line_idx]

        # Add return type annotation
        if fix_returns and func.needs_return_type and func.inferred_return_type:
            # Find the colon at end of function signature
            if ":" in func_line:
                # Insert return type before the colon
                parts = func_line.rsplit(":", 1)
                new_line = f"{parts[0]} -> {func.inferred_return_type}:{parts[1]}"
                lines[func_line_idx] = new_line
                modifications += 1

        # Note: Parameter annotations require more complex parsing
        # and are handled as suggestions only via generate_annotations_patch

    if dry_run:
        return modifications

    # Write back if not dry run
    if modifications > 0:
        with open(file_path, "w") as f:
            f.writelines(lines)

    return modifications


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automatically add type hints to Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Examples:
  # Add return type hints
  python fix_missing_annotations.py src/services/user_service.py --return-types

  # Add all annotations (dry run)
  python fix_missing_annotations.py src/services/user_service.py --all --dry-run

  # Process multiple files
  find src/ -name "*.py" -exec python fix_missing_annotations.py {} --return-types \;

Note:
  - Return type inference uses heuristics and may not be 100% accurate
  - Always review changes before committing
  - Run pyright after to verify correctness
        """,
    )

    parser.add_argument("file", type=Path, help="Python file to analyze")
    parser.add_argument(
        "--return-types",
        action="store_true",
        help="Add missing return type annotations",
    )
    parser.add_argument(
        "--parameter-types",
        action="store_true",
        help="Suggest parameter type annotations",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Add all missing annotations",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    if not args.return_types and not args.parameter_types and not args.all:
        sys.exit(1)

    fix_returns = args.return_types or args.all
    fix_params = args.parameter_types or args.all

    # Analyze file
    functions = analyze_file(args.file)

    if not functions:
        sys.exit(0)

    # Show summary
    missing_returns = sum(1 for f in functions if f.needs_return_type)
    missing_params = sum(1 for f in functions if f.needs_param_types)
    print(f"Found {len(functions)} functions with missing annotations:")
    print(f"  - Missing return types: {missing_returns}")
    print(f"  - Missing parameter types: {missing_params}")

    # Apply or show patches
    modifications = apply_annotations(
        args.file,
        functions,
        fix_returns,
        fix_params,
        args.dry_run,
    )

    if args.dry_run:
        patches = generate_annotations_patch(
            args.file,
            functions,
            fix_returns,
            fix_params,
        )
        print("\nSuggested changes:")
        for patch in patches:
            print(patch)
    else:
        print(f"\nApplied {modifications} modifications to {args.file}")

    sys.exit(0)


if __name__ == "__main__":
    main()
