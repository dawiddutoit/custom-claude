#!/usr/bin/env python3
"""Auto-add OpenTelemetry instrumentation to Python service files.

This script automatically adds:
- Import statements for OTEL components (get_logger, traced)
- get_logger(__name__) initialization at module level
- @traced decorator to public methods
- Structured logging calls to methods

Usage:
    python add_tracing.py <file_or_directory> [--dry-run] [--skip-tests]

Examples:
    # Add tracing to a single file
    python add_tracing.py src/project_watch_mcp/application/services/embedding_service.py

    # Add tracing to all services in a directory
    python add_tracing.py src/project_watch_mcp/application/services/

    # Dry run (preview changes without applying)
    python add_tracing.py src/project_watch_mcp/application/services/ --dry-run

    # Skip test files
    python add_tracing.py src/ --skip-tests
"""

import ast
import sys
from pathlib import Path
from typing import Any

class TracingTransformer(ast.NodeTransformer):
    """AST transformer to add OTEL instrumentation."""

    def __init__(self) -> None:
        """Initialize the transformer."""
        self.needs_logger = False
        self.needs_traced = False
        self.has_logger = False
        self.has_traced_import = False
        self.methods_to_trace: list[str] = []

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Visit module node to add imports."""
        # First pass: analyze what's needed
        self.generic_visit(node)

        # Second pass: add imports if needed
        if self.needs_logger or self.needs_traced:
            new_body = []
            import_added = False

            for item in node.body:
                # Add import after existing imports but before other code
                if not import_added and not isinstance(item, (ast.Import, ast.ImportFrom)):
                    # Determine what to import
                    import_names = []
                    if self.needs_logger and not self.has_logger:
                        import_names.append("get_logger")
                    if self.needs_traced and not self.has_traced_import:
                        import_names.append("traced")

                    if import_names:
                        import_node = ast.ImportFrom(
                            module="project_watch_mcp.core.monitoring",
                            names=[ast.alias(name=name, asname=None) for name in import_names],
                            level=0,
                        )
                        new_body.append(import_node)
                        new_body.append(ast.Expr(value=ast.Constant(value="")))  # Blank line

                    import_added = True

                new_body.append(item)

            # Add logger initialization after imports if needed
            if self.needs_logger and not self.has_logger:
                logger_assign = ast.Assign(
                    targets=[ast.Name(id="logger", ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id="get_logger", ctx=ast.Load()),
                        args=[ast.Name(id="__name__", ctx=ast.Load())],
                        keywords=[],
                    ),
                )
                # Find position after imports
                insert_pos = 0
                for idx, item in enumerate(new_body):
                    if not isinstance(item, (ast.Import, ast.ImportFrom, ast.Expr)):
                        insert_pos = idx
                        break

                new_body.insert(insert_pos, logger_assign)
                new_body.insert(insert_pos + 1, ast.Expr(value=ast.Constant(value="")))

            node.body = new_body

        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Check for existing OTEL imports."""
        if node.module == "project_watch_mcp.core.monitoring":
            for alias in node.names:
                if alias.name == "get_logger":
                    self.has_logger = True
                if alias.name == "traced":
                    self.has_traced_import = True
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        """Check for existing logger initialization."""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "logger":
                self.has_logger = True
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Visit class definitions to find methods to instrument."""
        # Check if class is a service, handler, or repository
        is_service_class = any(
            name in node.name for name in ["Service", "Handler", "Repository", "Orchestrator"]
        )

        if is_service_class:
            new_body = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check if method should be traced
                    should_trace = self._should_trace_method(item)

                    if should_trace:
                        # Check if already has @traced decorator
                        has_traced = any(
                            self._is_traced_decorator(dec) for dec in item.decorator_list
                        )

                        if not has_traced:
                            # Add @traced decorator
                            traced_decorator = ast.Name(id="traced", ctx=ast.Load())
                            item.decorator_list.insert(0, traced_decorator)
                            self.needs_traced = True
                            self.methods_to_trace.append(f"{node.name}.{item.name}")

                        # Add logging statement at the beginning of the method
                        item = self._add_logging_to_method(item)

                new_body.append(item)

            node.body = new_body

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Visit function definitions (module-level functions, e.g., MCP tools)."""
        # Check if this is likely an MCP tool or public function
        if not node.name.startswith("_"):
            # Check if already has @traced decorator
            has_traced = any(self._is_traced_decorator(dec) for dec in node.decorator_list)

            if not has_traced and self._should_trace_function(node):
                # Add @traced decorator
                traced_decorator = ast.Name(id="traced", ctx=ast.Load())
                node.decorator_list.insert(0, traced_decorator)
                self.needs_traced = True
                self.methods_to_trace.append(node.name)

            # Add logging statement at the beginning
            node = self._add_logging_to_method(node)

        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Visit async function definitions."""
        return self.visit_FunctionDef(node)  # type: ignore

    def _should_trace_method(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Determine if a method should be traced."""
        # Skip private methods (start with _)
        if node.name.startswith("_") and node.name != "__init__":
            return False

        # Skip __init__, __str__, __repr__, etc.
        if node.name.startswith("__") and node.name.endswith("__"):
            return False

        # Public methods should be traced
        return True

    def _should_trace_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Determine if a module-level function should be traced."""
        # Only trace async functions or functions with ServiceResult return type
        if isinstance(node, ast.AsyncFunctionDef):
            return True

        # Check return annotation for ServiceResult
        if node.returns:
            return_str = ast.unparse(node.returns)
            if "ServiceResult" in return_str or "dict" in return_str:
                return True

        return False

    def _is_traced_decorator(self, decorator: ast.expr) -> bool:
        """Check if a decorator is @traced."""
        if isinstance(decorator, ast.Name):
            return decorator.id == "traced"
        return False

    def _add_logging_to_method(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        """Add a logging statement to the beginning of a method."""
        # Check if method already has logging
        has_logging = False
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Attribute) and (
                    isinstance(stmt.value.func.value, ast.Name)
                    and stmt.value.func.value.id == "logger"
                ):
                    has_logging = True
                    break

        if not has_logging:
            # Create logging statement
            # logger.info(f"Method {method_name} called")
            log_msg = f"Method {node.name} called"
            if node.args.args:
                # Add parameter info (skip self/cls)
                params = [arg.arg for arg in node.args.args if arg.arg not in ["self", "cls"]]
                if params:
                    param_str = ", ".join(params)
                    log_msg = f"{node.name} called with params: {param_str}"

            log_call = ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="logger", ctx=ast.Load()),
                        attr="info",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=f"{log_msg}")],
                    keywords=[],
                )
            )

            # Insert logging statement after docstring (if present)
            insert_pos = 0
            if node.body and isinstance(node.body[0], ast.Expr):
                if isinstance(node.body[0].value, ast.Constant):
                    if isinstance(node.body[0].value.value, str):
                        # Has docstring, insert after it
                        insert_pos = 1

            node.body.insert(insert_pos, log_call)
            self.needs_logger = True

        return node


def process_file(file_path: Path, dry_run: bool = False) -> dict[str, Any]:
    """Process a Python file to add OTEL instrumentation.

    Args:
        file_path: Path to Python file
        dry_run: If True, don't modify file, just report changes

    Returns:
        Dictionary with processing results
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Transform AST
        transformer = TracingTransformer()
        new_tree = transformer.visit(tree)

        # Fix missing locations
        ast.fix_missing_locations(new_tree)

        # Generate new source code
        new_source = ast.unparse(new_tree)

        # Check if changes were made
        changes_made = (
            transformer.needs_logger
            or transformer.needs_traced
            or len(transformer.methods_to_trace) > 0
        )

        result = {
            "file": str(file_path),
            "success": True,
            "changes_made": changes_made,
            "methods_traced": transformer.methods_to_trace,
            "added_logger": transformer.needs_logger and not transformer.has_logger,
            "added_traced_import": transformer.needs_traced and not transformer.has_traced_import,
        }

        if changes_made and not dry_run:
            # Write modified source back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_source)
            result["modified"] = True
        else:
            result["modified"] = False

        return result

    except Exception as e:
        return {
            "file": str(file_path),
            "success": False,
            "error": str(e),
        }


def process_directory(
    directory: Path, dry_run: bool = False, skip_tests: bool = False
) -> list[dict[str, Any]]:
    """Process all Python files in a directory.

    Args:
        directory: Path to directory
        dry_run: If True, don't modify files
        skip_tests: If True, skip test files

    Returns:
        List of processing results
    """
    results = []

    for py_file in directory.rglob("*.py"):
        # Skip test files if requested
        if skip_tests and ("test_" in py_file.name or py_file.parent.name in ["tests", "test"]):
            continue

        # Skip __pycache__ and similar
        if "__pycache__" in str(py_file):
            continue

        result = process_file(py_file, dry_run)
        results.append(result)

    return results


def print_summary(results: list[dict[str, Any]], dry_run: bool = False) -> None:
    """Print summary of processing results."""
    total_files = len(results)
    successful = sum(1 for r in results if r.get("success", False))
    modified = sum(1 for r in results if r.get("modified", False))
    changed = sum(1 for r in results if r.get("changes_made", False))

    print("\n" + "=" * 80)
    print("OPENTELEMETRY INSTRUMENTATION SUMMARY")
    print("=" * 80)

    if dry_run:
        print("MODE: Dry Run (no files modified)")
    else:
        print("MODE: Apply Changes")

    print(f"\nTotal files processed: {total_files}")
    print(f"Successful: {successful}")
    print(f"Files with changes: {changed}")
    print(f"Files modified: {modified}")

    for result in results:
        if result.get("changes_made", False):
            print(f"\nModified: {result.get('file', 'unknown')}")

            if result.get("added_logger", False):
                print("  + Added logger initialization")

            if result.get("added_traced_import", False):
                print("  + Added @traced import")

            if result.get("methods_traced", []):
                print(f"  + Instrumented {len(result['methods_traced'])} methods:")
                for method in result["methods_traced"]:
                    print(f"    - {method}")

        elif not result.get("success", True):
            print(f"\nError in {result.get('file', 'unknown')}: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 80)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python add_tracing.py <file_or_directory> [--dry-run] [--skip-tests]")
        print("\nExamples:")
        print("  # Add tracing to a single file")
        print("  python add_tracing.py src/project_watch_mcp/application/services/embedding_service.py")
        print("\n  # Add tracing to all services in a directory")
        print("  python add_tracing.py src/project_watch_mcp/application/services/")
        print("\n  # Dry run (preview changes without applying)")
        print("  python add_tracing.py src/ --dry-run")
        print("\n  # Skip test files")
        print("  python add_tracing.py src/ --skip-tests")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv
    skip_tests = "--skip-tests" in sys.argv

    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}")
        sys.exit(1)

    if dry_run:
        print("Running in DRY-RUN mode (no files will be modified)")
    if skip_tests:
        print("Skipping test files")

    if target_path.is_file():
        result = process_file(target_path, dry_run)
        print_summary([result], dry_run)
    else:
        results = process_directory(target_path, dry_run, skip_tests)
        print_summary(results, dry_run)


if __name__ == "__main__":
    main()
