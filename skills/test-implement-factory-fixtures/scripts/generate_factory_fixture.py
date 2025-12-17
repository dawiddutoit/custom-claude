#!/usr/bin/env python3
"""Generate factory fixtures from class definitions.

Auto-generates factory fixtures for test classes, extracting constructor
parameters and creating customizable factory functions.

Usage:
    python generate_factory_fixture.py <class_name>
    python generate_factory_fixture.py EmbeddingService --name mock_embedder
    python generate_factory_fixture.py EmbeddingService --output tests/unit/conftest.py
    python generate_factory_fixture.py EmbeddingService --real --print
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class ClassParameter:
    """Information about a class constructor parameter."""

    name: str
    type_hint: str | None = None
    default: str | None = None


@dataclass
class ClassInfo:
    """Information about an analyzed class."""

    class_name: str
    import_path: str
    params: list[ClassParameter] = field(default_factory=list)


class ClassAnalyzer(ast.NodeVisitor):
    """Analyze class to extract constructor parameters."""

    def __init__(self, target_class: str) -> None:
        self.target_class = target_class
        self.class_name: str | None = None
        self.init_params: list[ClassParameter] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition to extract name and __init__ parameters."""
        if node.name != self.target_class:
            self.generic_visit(node)
            return

        self.class_name = node.name

        # Find __init__ method
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                self._extract_init_params(item)
                break

        self.generic_visit(node)

    def _extract_init_params(self, init_node: ast.FunctionDef) -> None:
        """Extract parameters from __init__ method."""
        params: list[ClassParameter] = []

        # Extract parameters (skip self)
        for arg in init_node.args.args[1:]:
            param_name = arg.arg
            type_hint = ast.unparse(arg.annotation) if arg.annotation else None
            params.append(ClassParameter(name=param_name, type_hint=type_hint))

        # Extract defaults (right-aligned with parameters)
        defaults = init_node.args.defaults
        if defaults:
            num_params = len(params)
            num_defaults = len(defaults)
            start_idx = num_params - num_defaults

            for i, default in enumerate(defaults):
                param_idx = start_idx + i
                params[param_idx] = ClassParameter(
                    name=params[param_idx].name,
                    type_hint=params[param_idx].type_hint,
                    default=ast.unparse(default),
                )

        self.init_params = params


def find_class_in_codebase(class_name: str, search_root: Path) -> Path | None:
    """Find class definition file in codebase.

    Args:
        class_name: Name of class to find
        search_root: Root directory to search

    Returns:
        Path to file containing class, or None if not found
    """
    for py_file in search_root.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    return py_file
        except (SyntaxError, OSError):
            continue

    return None


def _compute_import_path(class_file: Path, project_root: Path) -> str:
    """Compute the import path for a class file.

    Args:
        class_file: Path to Python file containing the class
        project_root: Root directory of the project

    Returns:
        Dotted import path string
    """
    src_root = project_root / "src"
    if src_root.exists() and src_root in class_file.parents:
        rel_path = class_file.relative_to(src_root)
        import_parts = [*list(rel_path.parent.parts), rel_path.stem]
        return ".".join(import_parts)
    else:
        # Fallback: use file stem
        return class_file.stem


def analyze_class(class_file: Path, class_name: str) -> ClassInfo:
    """Analyze class file to extract constructor information.

    Args:
        class_file: Path to Python file containing class
        class_name: Name of class to analyze

    Returns:
        ClassInfo with class analysis results
    """
    content = class_file.read_text(encoding="utf-8")
    tree = ast.parse(content)

    analyzer = ClassAnalyzer(class_name)
    analyzer.visit(tree)

    # Determine import path
    project_root = Path.cwd()
    import_path = _compute_import_path(class_file, project_root)

    return ClassInfo(
        class_name=class_name,
        import_path=import_path,
        params=analyzer.init_params,
    )


def _get_default_for_type(type_hint: str | None, has_default: bool) -> str:
    """Get a sensible default value based on type hint.

    Args:
        type_hint: Python type hint string
        has_default: Whether the parameter already has a default

    Returns:
        Default value string
    """
    if has_default:
        return ""  # Will use actual default
    if not type_hint:
        return "=None"
    if "int" in type_hint:
        return "=0"
    if "str" in type_hint:
        return '=""'
    if "bool" in type_hint:
        return "=True"
    if "float" in type_hint:
        return "=0.0"
    return "=None"


def generate_mock_factory(class_info: ClassInfo, fixture_name: str) -> str:
    """Generate mock factory fixture code.

    Args:
        class_info: Class analysis information
        fixture_name: Name for the fixture

    Returns:
        Generated factory fixture code
    """
    class_name = class_info.class_name
    params = class_info.params

    # Generate parameter list with defaults
    param_list: list[str] = []
    for param in params:
        param_str = param.name
        if param.default:
            param_str += f"={param.default}"
        else:
            default = _get_default_for_type(param.type_hint, param.default is not None)
            param_str += default
        param_list.append(param_str)

    # Always add success/error params for mocks
    param_list.extend(["success: bool = True", "error_message: str | None = None"])
    params_str = ",\n        ".join(param_list)

    # Generate docstring parameters
    doc_params: list[str] = []
    for param in params:
        type_str = param.type_hint or "Any"
        default_str = param.default or "None"
        doc_params.append(
            f"            {param.name}: {type_str} (default: {default_str})"
        )
    doc_params.extend(
        [
            "            success: Whether the mock should return success (default: True)",
            "            error_message: Error message for failure cases (default: None)",
        ]
    )
    doc_params_str = "\n".join(doc_params)

    return f'''@pytest.fixture
def {fixture_name}_factory():
    """Create a factory for custom mock {class_name}.

    Returns:
        callable: Function that creates {class_name} with custom parameters

    Example:
        def test_something({fixture_name}_factory):
            instance = {fixture_name}_factory(param1=value1)
            # Use instance in test
    """
    from unittest.mock import AsyncMock

    def create_{fixture_name}(
        {params_str}
    ):
        """Create custom mock {class_name}.

        Args:
{doc_params_str}

        Returns:
            AsyncMock: Custom {class_name} instance
        """
        mock = AsyncMock()

        if success:
            # Configure success behavior
            # TODO: Add method mocking based on class interface
            pass
        else:
            # Configure failure behavior
            mock.side_effect = Exception(error_message or "Mock error")

        return mock

    return create_{fixture_name}
'''


def generate_real_factory(class_info: ClassInfo, fixture_name: str) -> str:
    """Generate real instance factory fixture code.

    Args:
        class_info: Class analysis information
        fixture_name: Name for the fixture

    Returns:
        Generated factory fixture code
    """
    class_name = class_info.class_name
    import_path = class_info.import_path
    params = class_info.params

    # Identify dependencies (parameters with type hints and no defaults)
    dependencies = [p for p in params if p.type_hint and not p.default]
    dep_fixtures = [f"mock_{p.name}" for p in dependencies]

    # Generate fixture dependency list
    fixture_deps = ",\n    ".join(dep_fixtures) if dep_fixtures else ""

    # Generate parameter extraction
    param_extracts: list[str] = []
    for param in params:
        default = param.default or "None"
        param_extracts.append(
            f'        {param.name} = kwargs.get("{param.name}", {default})'
        )
    param_extract_str = "\n".join(param_extracts)

    # Generate constructor call
    constructor_params = [f"{p.name}={p.name}" for p in params]
    constructor_str = ",\n            ".join(constructor_params)

    # Build fixture with dependencies
    dep_args = f"\n    {fixture_deps}," if fixture_deps else ""
    dep_docs = ""
    for dep_fixture in dep_fixtures:
        dep_docs += f"        {dep_fixture}: Mock dependency\n"

    return f'''@pytest.fixture
def {fixture_name}_factory({dep_args}
):
    """Create a factory for real {class_name} instances with mock dependencies.

    Args:
{dep_docs}
    Returns:
        callable: Function that creates real {class_name} instances

    Example:
        def test_something({fixture_name}_factory):
            instance = {fixture_name}_factory(param1=value1)
            # Use real instance with mocked dependencies
    """

    def create_instance(**kwargs):
        """Create real {class_name} instance with custom settings.

        Args:
            **kwargs: Parameters to customize instance creation

        Returns:
            {class_name}: Real instance with mocked dependencies
        """
        from {import_path} import {class_name}

        # Extract parameters with defaults
{param_extract_str}

        # Create real instance with injected mocks
        return {class_name}(
            {constructor_str}
        )

    return create_instance
'''


def append_to_conftest(conftest_path: Path, fixture_code: str) -> None:
    """Append fixture code to conftest.py file.

    Args:
        conftest_path: Path to conftest.py
        fixture_code: Generated fixture code to append
    """
    # Read existing content
    if conftest_path.exists():
        existing = conftest_path.read_text(encoding="utf-8")
    else:
        existing = ""

    # Check if pytest is imported
    if "import pytest" not in existing:
        imports = "import pytest\nfrom unittest.mock import AsyncMock, MagicMock\n\n"
        existing = imports + existing

    # Append new fixture with separator
    separator = (
        "\n\n# "
        + "=" * 75
        + "\n# Auto-generated factory fixture\n# "
        + "=" * 75
        + "\n\n"
    )

    conftest_path.write_text(
        existing.rstrip() + separator + fixture_code, encoding="utf-8"
    )


def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case.

    Args:
        name: String in CamelCase

    Returns:
        String in snake_case
    """
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Generate factory fixtures from class definitions"
    )
    parser.add_argument(
        "class_name",
        help="Name of class to generate factory for",
    )
    parser.add_argument(
        "--name",
        help="Custom fixture name (default: mock_<class_name_snake_case>)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output conftest.py file (default: tests/unit/conftest.py)",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Generate real instance factory (vs mock factory)",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_output",
        help="Print to stdout instead of writing to file",
    )

    args = parser.parse_args(argv)

    # Find class in codebase
    search_root = Path.cwd() / "src"
    if not search_root.exists():
        search_root = Path.cwd()

    class_file = find_class_in_codebase(args.class_name, search_root)

    if not class_file:
        print(
            f"Error: Class '{args.class_name}' not found in {search_root}",
            file=sys.stderr,
        )
        return 1

    print(f"Found class in: {class_file}")

    # Analyze class
    class_info = analyze_class(class_file, args.class_name)

    # Determine fixture name
    if args.name:
        fixture_name = args.name
    else:
        snake_case = to_snake_case(args.class_name)
        fixture_name = f"mock_{snake_case}"

    # Generate fixture code
    if args.real:
        fixture_code = generate_real_factory(class_info, fixture_name)
    else:
        fixture_code = generate_mock_factory(class_info, fixture_name)

    # Output
    if args.print_output:
        print("\n=== Generated Factory Fixture ===\n")
        print(fixture_code)
    else:
        # Determine output file
        conftest_path = args.output or Path.cwd() / "tests" / "unit" / "conftest.py"
        append_to_conftest(conftest_path, fixture_code)
        print(f"Appended factory fixture to: {conftest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
