#!/usr/bin/env python3
"""Auto-generate provider code for dependency injection container.

Analyzes a service class and generates the appropriate provider registration
code for container.py based on constructor signature and class type.

Usage:
    python generate_provider.py path/to/service.py ClassName
    python generate_provider.py --interactive  # Interactive mode

Examples:
    python generate_provider.py src/services/user_service.py UserService
    python generate_provider.py src/repositories/file_repo.py FileRepository --provider-type singleton
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# Setup: Add .claude/tools to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_claude_root))

from tools.skill_utils import (  # noqa: E402
    ensure_path_setup,
    file_path_to_module,
    get_project_root,
    to_snake_case,
)

ensure_path_setup()


@dataclass(frozen=True)
class ConstructorParam:
    """A constructor parameter with name and type annotation."""

    name: str
    type_annotation: str


@dataclass(frozen=True)
class ServiceInfo:
    """Information about a service class."""

    class_name: str
    file_path: str
    module_path: str
    constructor_params: tuple[ConstructorParam, ...]
    recommended_provider: str  # "Singleton" or "Factory"


class ServiceAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze service class."""

    def __init__(self, target_class: str) -> None:
        self.target_class = target_class
        self.service_info: ServiceInfo | None = None
        self.found: bool = False

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to find target service."""
        if node.name == self.target_class:
            self.found = True
            # Analyze __init__ method
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    params = self._extract_params(item)
                    provider_type = self._recommend_provider(node.name)

                    self.service_info = ServiceInfo(
                        class_name=node.name,
                        file_path="",  # Set later
                        module_path="",  # Set later
                        constructor_params=tuple(params),
                        recommended_provider=provider_type,
                    )
                    break

        self.generic_visit(node)

    def _extract_params(self, node: ast.FunctionDef) -> list[ConstructorParam]:
        """Extract constructor parameters (excluding self)."""
        params: list[ConstructorParam] = []

        for arg in node.args.args[1:]:  # Skip self
            param_name = arg.arg
            param_type = ""

            if arg.annotation:
                param_type = ast.unparse(arg.annotation)

            params.append(ConstructorParam(name=param_name, type_annotation=param_type))

        return params

    def _recommend_provider(self, class_name: str) -> str:
        """Recommend provider type based on class name conventions.

        Args:
            class_name: Name of the service class.

        Returns:
            Recommended provider type: "Singleton" or "Factory".
        """
        # Handlers are typically Factory (stateless, per-request)
        if "Handler" in class_name:
            return "Factory"

        # Repositories are typically Singleton (stateful, expensive)
        if "Repository" in class_name:
            return "Singleton"

        # Services can be either, default to Singleton
        if "Service" in class_name:
            # Check for specific patterns that suggest Factory
            factory_keywords = ("Command", "Query", "Request", "Processor")
            if any(keyword in class_name for keyword in factory_keywords):
                return "Factory"
            return "Singleton"

        # Default to Singleton
        return "Singleton"


def analyze_service(file_path: Path, class_name: str) -> ServiceInfo | None:
    """Analyze service class and extract information.

    Args:
        file_path: Path to Python file containing the service.
        class_name: Name of the service class.

    Returns:
        ServiceInfo if found, None otherwise.
    """
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return None

    with file_path.open(encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError as e:
            print(f"Error: Syntax error in {file_path}: {e}", file=sys.stderr)
            return None

    analyzer = ServiceAnalyzer(class_name)
    analyzer.visit(tree)

    if not analyzer.found:
        print(f"Error: Class '{class_name}' not found in {file_path}", file=sys.stderr)
        return None

    if not analyzer.service_info:
        print(f"Error: Could not analyze class '{class_name}'", file=sys.stderr)
        return None

    # Create new ServiceInfo with file path and module path set
    project_root = get_project_root()
    module_path = file_path_to_module(file_path, project_root)

    return ServiceInfo(
        class_name=analyzer.service_info.class_name,
        file_path=str(file_path),
        module_path=module_path,
        constructor_params=analyzer.service_info.constructor_params,
        recommended_provider=analyzer.service_info.recommended_provider,
    )


def generate_import_statement(service_info: ServiceInfo) -> str:
    """Generate import statement for the service.

    Args:
        service_info: Information about the service.

    Returns:
        Import statement string.
    """
    return f"from {service_info.module_path} import {service_info.class_name}"


def _guess_provider_reference(param: ConstructorParam) -> str:
    """Guess the provider reference based on parameter name and type.

    Args:
        param: Constructor parameter with name and type.

    Returns:
        Guessed provider reference name.
    """
    param_name = param.name
    param_type = param.type_annotation

    # Special cases based on type or name
    if param_name == "settings" or "Settings" in param_type:
        return "settings"

    if param_name == "driver" or "Driver" in param_type:
        return "neo4j_driver"

    if param_name == "repository_monitor" or "RepositoryMonitor" in param_type:
        return "repository_monitor"

    # Default: use parameter name as-is (likely matches provider name)
    return param_name


def generate_provider_code(
    service_info: ServiceInfo,
    provider_var_name: str | None = None,
) -> str:
    """Generate provider registration code.

    Args:
        service_info: Information about the service.
        provider_var_name: Variable name for provider (default: snake_case of class name).

    Returns:
        Generated provider code as string.
    """
    # Generate variable name if not provided
    if not provider_var_name:
        provider_var_name = to_snake_case(service_info.class_name)

    # Generate parameter mappings
    param_lines: list[str] = []
    for param in service_info.constructor_params:
        provider_ref = _guess_provider_reference(param)
        param_lines.append(f"        {param.name}={provider_ref},")

    params_str = "\n".join(param_lines)

    # Generate provider code
    return f"""    # {service_info.class_name}
    {provider_var_name} = providers.{service_info.recommended_provider}(
        {service_info.class_name},
{params_str}
    )"""


def print_instructions(
    service_info: ServiceInfo,
    import_stmt: str,
    provider_code: str,
) -> None:
    """Print instructions for adding to container.py.

    Args:
        service_info: Information about the service.
        import_stmt: Generated import statement.
        provider_code: Generated provider code.
    """
    print("\n" + "=" * 60)
    print("Generated Provider Code")
    print("=" * 60)

    print("\n1. Add this import to container.py:\n")
    print(f"   {import_stmt}")

    print("\n2. Add this provider registration inside Container class:\n")
    print(provider_code)

    print("\n3. Wire dependencies - verify these mappings:")
    for param in service_info.constructor_params:
        provider_ref = _guess_provider_reference(param)
        print(f"   {param.name} ({param.type_annotation}) -> {provider_ref}")

    print("\n" + "=" * 60)


def interactive_mode() -> int:
    """Run in interactive mode.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    print("Provider Generator - Interactive Mode")
    print("-" * 40)

    # Get file path
    file_path_str = input("Enter path to service file: ").strip()
    if not file_path_str:
        print("Error: File path required.", file=sys.stderr)
        return 1

    file_path = Path(file_path_str)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    # Get class name
    class_name = input("Enter service class name: ").strip()

    if not class_name:
        print("Error: Class name required.", file=sys.stderr)
        return 1

    # Analyze service
    service_info = analyze_service(file_path, class_name)
    if not service_info:
        return 1

    # Generate code
    import_stmt = generate_import_statement(service_info)
    provider_code = generate_provider_code(service_info)

    # Print instructions
    print_instructions(service_info, import_stmt, provider_code)

    return 0


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Auto-generate provider code for dependency injection"
    )
    parser.add_argument("file_path", nargs="?", help="Path to Python file")
    parser.add_argument("class_name", nargs="?", help="Name of service class")
    parser.add_argument(
        "--provider-type",
        choices=["singleton", "factory"],
        help="Override provider type recommendation",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--var-name", help="Custom variable name for provider (default: snake_case)"
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        return interactive_mode()

    # Validate required arguments
    if not args.file_path or not args.class_name:
        parser.print_help()
        return 1

    file_path = Path(args.file_path)

    # Analyze service
    service_info = analyze_service(file_path, args.class_name)
    if not service_info:
        return 1

    # Override provider type if specified
    if args.provider_type:
        # Create new ServiceInfo with overridden provider type
        new_provider = "Singleton" if args.provider_type == "singleton" else "Factory"
        service_info = ServiceInfo(
            class_name=service_info.class_name,
            file_path=service_info.file_path,
            module_path=service_info.module_path,
            constructor_params=service_info.constructor_params,
            recommended_provider=new_provider,
        )

    # Generate code
    import_stmt = generate_import_statement(service_info)
    provider_code = generate_provider_code(service_info, args.var_name)

    # Print instructions
    print_instructions(service_info, import_stmt, provider_code)

    return 0


if __name__ == "__main__":
    sys.exit(main())
