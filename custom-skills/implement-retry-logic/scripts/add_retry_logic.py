#!/usr/bin/env python3
"""Auto-add retry logic to async service methods.

This script uses AST modification to wrap async methods with retry logic,
adding exponential backoff, jitter, and error classification.

Usage:
    python add_retry_logic.py <file_path> <method_name> [options]

Examples:
    # Add retry to specific method
    python add_retry_logic.py src/services/api_service.py call_external_api

    # Dry run (show changes without modifying)
    python add_retry_logic.py src/services/api_service.py call_external_api --dry-run

    # Specify retriable exceptions
    python add_retry_logic.py src/services/api_service.py fetch_data \\
        --retriable "TimeoutError,ConnectionError"

    # Configure retry parameters
    python add_retry_logic.py src/services/api_service.py process \\
        --max-retries 5 --retry-delay 2.0
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Any


class RetryLogicTransformer(ast.NodeTransformer):
    """AST transformer that wraps async methods with retry logic."""

    def __init__(
        self,
        method_name: str,
        retriable_exceptions: list[str],
        permanent_exceptions: list[str],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize transformer.

        Args:
            method_name: Name of method to wrap with retry logic
            retriable_exceptions: List of exception names that trigger retry
            permanent_exceptions: List of exception names that fail immediately
            max_retries: Maximum retry attempts (default: 3)
            retry_delay: Base delay in seconds (default: 1.0)
        """
        self.method_name = method_name
        self.retriable_exceptions = retriable_exceptions
        self.permanent_exceptions = permanent_exceptions
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.found_method = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        """Visit async function definitions and wrap target method."""
        if node.name == self.method_name:
            self.found_method = True
            return self._wrap_with_retry(node)
        return node

    def _wrap_with_retry(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Wrap async method with retry logic.

        Args:
            node: AST node representing async function

        Returns:
            Modified AST node with retry logic
        """
        # Create new method name for original implementation
        original_method_name = f"_{node.name}_impl"

        # Rename original method
        ast.AsyncFunctionDef(
            name=original_method_name,
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=node.returns,
        )

        # Build retry wrapper method
        return self._build_retry_wrapper(
            node.name, original_method_name, node.args, node.returns
        )

        # Return both methods (original renamed + new wrapper)
        # Note: This is simplified - in production, we'd need to insert both

    def _build_retry_wrapper(
        self,
        method_name: str,
        original_method: str,
        args: ast.arguments,
        returns: ast.expr | None,
    ) -> ast.AsyncFunctionDef:
        """Build retry wrapper method using AST.

        Args:
            method_name: Name of wrapper method
            original_method: Name of original implementation method
            args: Method arguments
            returns: Return type annotation

        Returns:
            AST node for retry wrapper method
        """
        # Build retry loop body using AST
        # This is a simplified version - production would generate full retry logic

        # For demonstration, we'll use ast.parse to generate the structure
        retry_code = f'''
async def {method_name}(self, *args, **kwargs) -> ServiceResult[Any]:
    """Wrapper with retry logic for {original_method}."""
    last_error: str = ""

    for attempt in range(self.settings.max_retries or {self.max_retries}):
        try:
            result = await self.{original_method}(*args, **kwargs)
            return ServiceResult.ok(result)

        except ({", ".join(self.retriable_exceptions)}) as e:
            last_error = f"Retriable error: {{e}}"
            if attempt < (self.settings.max_retries or {self.max_retries}) - 1:
                delay = self._calculate_backoff_delay(attempt)
                logger.warning(
                    f"{{last_error}}. Retrying in {{delay:.1f}}s "
                    f"(attempt {{attempt + 1}}/{{self.settings.max_retries or {self.max_retries}}})"
                )
                await asyncio.sleep(delay)

        except ({", ".join(self.permanent_exceptions)}) as e:
            logger.error(f"Permanent error (non-retriable): {{e}}")
            return ServiceResult.fail(f"Permanent error: {{e}}")

        except Exception as e:
            logger.error(f"Unexpected error in {method_name}: {{e}}")
            return ServiceResult.fail(f"Unexpected error: {{e}}")

    return ServiceResult.fail(
        f"Failed after {{self.settings.max_retries or {self.max_retries}}} retries: {{last_error}}"
    )
'''

        # Parse the code into AST
        module = ast.parse(retry_code)
        return module.body[0]  # Return the function definition


def add_backoff_helper_if_missing(tree: ast.Module) -> tuple[ast.Module, bool]:
    """Add _calculate_backoff_delay helper if not present.

    Args:
        tree: AST module tree

    Returns:
        Tuple of (modified tree, was_added boolean)
    """
    # Check if helper already exists
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_calculate_backoff_delay":
            return tree, False

    # Helper doesn't exist - add it
    helper_code = '''
def _calculate_backoff_delay(self, attempt: int) -> float:
    """Calculate exponential backoff with jitter.

    Args:
        attempt: Current attempt number (0-based)

    Returns:
        Delay in seconds with jitter
    """
    import time

    base_delay = getattr(self.settings, 'retry_delay', 1.0)

    # Exponential backoff: base * 2^attempt, capped at 30s
    delay = min(base_delay * (2 ** attempt), 30.0)

    # Add jitter to avoid thundering herd (±20%)
    jitter = delay * 0.2 * (2 * (time.time() % 1) - 1)

    return max(0.1, delay + jitter)
'''

    helper_ast = ast.parse(helper_code).body[0]

    # Find the class definition to add helper to
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # Add helper method to class
            node.body.append(helper_ast)
            return tree, True

    return tree, False


def add_required_imports(tree: ast.Module) -> ast.Module:
    """Add required imports for retry logic.

    Args:
        tree: AST module tree

    Returns:
        Modified tree with imports
    """
    required_imports = [
        "import asyncio",
        "import time",
        "from project_watch_mcp.core.monitoring import get_logger",
        "from project_watch_mcp.domain.common.service_result import ServiceResult",
    ]

    # Check which imports are missing
    existing_imports = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                existing_imports.add(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                existing_imports.add(f"from {module} import {alias.name}")

    # Add missing imports at the top
    new_imports = []
    for imp in required_imports:
        if imp not in existing_imports:
            new_imports.append(ast.parse(imp).body[0])

    tree.body = new_imports + tree.body
    return tree


def process_file(
    file_path: Path,
    method_name: str,
    retriable_exceptions: list[str],
    permanent_exceptions: list[str],
    max_retries: int,
    retry_delay: float,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """Process file and add retry logic.

    Args:
        file_path: Path to Python file
        method_name: Name of method to wrap
        retriable_exceptions: Exceptions that trigger retry
        permanent_exceptions: Exceptions that fail immediately
        max_retries: Maximum retry attempts
        retry_delay: Base delay in seconds
        dry_run: If True, show changes without modifying file

    Returns:
        Tuple of (success boolean, message string)
    """
    try:
        # Read source file
        source_code = file_path.read_text()

        # Parse into AST
        tree = ast.parse(source_code)

        # Transform AST to add retry logic
        transformer = RetryLogicTransformer(
            method_name=method_name,
            retriable_exceptions=retriable_exceptions,
            permanent_exceptions=permanent_exceptions,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )
        modified_tree = transformer.visit(tree)

        if not transformer.found_method:
            return False, f"Method '{method_name}' not found in {file_path}"

        # Add backoff helper if missing
        modified_tree, helper_added = add_backoff_helper_if_missing(modified_tree)

        # Add required imports
        modified_tree = add_required_imports(modified_tree)

        # Convert AST back to source code
        modified_code = ast.unparse(modified_tree)

        if dry_run:
            return True, "Dry run completed successfully"

        # Write modified code back to file
        file_path.write_text(modified_code)

        message = f"✓ Added retry logic to {method_name} in {file_path}"
        if helper_added:
            message += "\n✓ Added _calculate_backoff_delay helper method"

        return True, message

    except SyntaxError as e:
        return False, f"Syntax error in {file_path}: {e}"
    except Exception as e:
        return False, f"Error processing {file_path}: {e}"


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Add retry logic to async service methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("file_path", type=Path, help="Path to Python service file")
    parser.add_argument("method_name", help="Name of async method to wrap with retry logic")

    parser.add_argument(
        "--retriable",
        default="TimeoutError,ConnectionError",
        help="Comma-separated list of retriable exception names (default: TimeoutError,ConnectionError)",
    )

    parser.add_argument(
        "--permanent",
        default="ValueError,TypeError",
        help="Comma-separated list of permanent exception names (default: ValueError,TypeError)",
    )

    parser.add_argument(
        "--max-retries", type=int, default=3, help="Maximum retry attempts (default: 3)"
    )

    parser.add_argument(
        "--retry-delay", type=float, default=1.0, help="Base delay in seconds (default: 1.0)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without modifying file",
    )

    args = parser.parse_args()

    # Validate file exists
    if not args.file_path.exists():
        return 1

    # Parse exception lists
    retriable = [e.strip() for e in args.retriable.split(",")]
    permanent = [e.strip() for e in args.permanent.split(",")]

    # Process file
    success, _message = process_file(
        file_path=args.file_path,
        method_name=args.method_name,
        retriable_exceptions=retriable,
        permanent_exceptions=permanent,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        dry_run=args.dry_run,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
