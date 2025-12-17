#!/usr/bin/env python3
"""Convert regular fixtures to factory fixtures.

Takes existing pytest fixtures and converts them to factory pattern,
allowing customization through parameters.

Usage:
    python convert_fixture_to_factory.py <fixture_name>
    python convert_fixture_to_factory.py mock_service --file tests/unit/conftest.py
    python convert_fixture_to_factory.py mock_service --dry-run
    python convert_fixture_to_factory.py mock_service --params "dimensions:int=384,success:bool=True"
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


# Constants
DOCSTRING_QUOTE_COUNT = 2  # Number of quotes for single-line docstring


@dataclass(frozen=True)
class ParameterSpec:
    """Specification for a factory parameter."""

    name: str
    type_hint: str
    default: str


@dataclass(frozen=True)
class FixtureInfo:
    """Information about a found fixture."""

    name: str
    node: ast.FunctionDef
    code: str
    line_start: int
    line_end: int
    content: str
    lines: tuple[str, ...]


class FixtureFinder(ast.NodeVisitor):
    """Find pytest fixture by name and extract its definition."""

    def __init__(self, fixture_name: str) -> None:
        self.fixture_name = fixture_name
        self.fixture_node: ast.FunctionDef | None = None
        self.line_start: int | None = None
        self.line_end: int | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition to find fixture."""
        has_fixture_decorator = any(
            (isinstance(d, ast.Name) and d.id == "fixture")
            or (isinstance(d, ast.Attribute) and d.attr == "fixture")
            for d in node.decorator_list
        )

        if has_fixture_decorator and node.name == self.fixture_name:
            self.fixture_node = node
            self.line_start = node.lineno
            self.line_end = node.end_lineno

        self.generic_visit(node)


def find_fixture(conftest_path: Path, fixture_name: str) -> FixtureInfo | None:
    """Find fixture definition in conftest file.

    Args:
        conftest_path: Path to conftest.py
        fixture_name: Name of fixture to find

    Returns:
        FixtureInfo with fixture details, or None if not found
    """
    if not conftest_path.exists():
        return None

    content = conftest_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    finder = FixtureFinder(fixture_name)
    finder.visit(tree)

    if (
        finder.fixture_node is None
        or finder.line_start is None
        or finder.line_end is None
    ):
        return None

    original_code = "\n".join(lines[finder.line_start - 1 : finder.line_end])

    return FixtureInfo(
        name=fixture_name,
        node=finder.fixture_node,
        code=original_code,
        line_start=finder.line_start,
        line_end=finder.line_end,
        content=content,
        lines=tuple(lines),
    )


def parse_param_spec(param_spec: str) -> list[ParameterSpec]:
    """Parse parameter specification string.

    Args:
        param_spec: Comma-separated params like "dimensions:int=384,success:bool=True"

    Returns:
        List of ParameterSpec objects
    """
    if not param_spec:
        return []

    params: list[ParameterSpec] = []
    for param in param_spec.split(","):
        param = param.strip()
        if not param:
            continue

        # Parse format: name:type=default
        match = re.match(r"(\w+)(?::(\w+))?(?:=(.+))?", param)
        if match:
            name, type_hint, default = match.groups()
            params.append(
                ParameterSpec(
                    name=name,
                    type_hint=type_hint or "Any",
                    default=default or "None",
                )
            )

    return params


def _extract_body_content(original_code: str) -> str:
    """Extract body content from fixture code, removing decorators and docstring.

    Args:
        original_code: Original fixture code

    Returns:
        Body content with adjusted indentation
    """
    body_lines = original_code.split("\n")

    # Skip decorators and function def
    body_start = 0
    for i, line in enumerate(body_lines):
        if line.strip().startswith("def "):
            body_start = i + 1
            break

    # Skip docstring if present
    in_docstring = False
    for i in range(body_start, len(body_lines)):
        line = body_lines[i].strip()
        if '"""' in line or "'''" in line:
            if not in_docstring:
                in_docstring = True
                if (
                    line.count('"""') == DOCSTRING_QUOTE_COUNT
                    or line.count("'''") == DOCSTRING_QUOTE_COUNT
                ):
                    # Single-line docstring
                    body_start = i + 1
                    break
            else:
                # End of multi-line docstring
                body_start = i + 1
                break
        elif not in_docstring and line and not line.startswith("#"):
            # Found actual code
            break

    # Get body content (adjust indentation for nested function)
    body_content = "\n".join(body_lines[body_start:])
    return re.sub(r"^    ", "        ", body_content, flags=re.MULTILINE)


def convert_to_factory(
    fixture_info: FixtureInfo,
    params: Sequence[ParameterSpec],
) -> str:
    """Convert regular fixture to factory fixture.

    Args:
        fixture_info: Original fixture information
        params: List of parameters to add to factory

    Returns:
        Converted factory fixture code
    """
    original_name = fixture_info.name
    original_node = fixture_info.node

    # Extract docstring
    docstring = ast.get_docstring(original_node)
    if not docstring:
        docstring = f"Create a factory for custom {original_name}."

    # Generate factory name
    factory_name = original_name
    if not factory_name.endswith("_factory"):
        factory_name += "_factory"

    # Generate inner function name
    inner_name = original_name.replace("mock_", "").replace("_factory", "")
    create_func_name = f"create_{inner_name}"

    # Generate parameter list
    if params:
        param_list = [f"{p.name}: {p.type_hint} = {p.default}" for p in params]
        params_str = ",\n        ".join(param_list)

        # Generate docstring for parameters
        param_docs = [
            f"            {p.name}: {p.type_hint} (default: {p.default})"
            for p in params
        ]
        param_docs_str = "\n".join(param_docs)
    else:
        params_str = "**kwargs"
        param_docs_str = "            **kwargs: Custom parameters for fixture"

    # Extract body content
    body_content = _extract_body_content(fixture_info.code)

    # Build factory fixture
    return f'''@pytest.fixture
def {factory_name}():
    """{docstring}

    Returns:
        callable: Function that creates {inner_name} with custom parameters

    Example:
        def test_something({factory_name}):
            instance = {factory_name}(param1=value1)
            # Use instance in test
    """

    def {create_func_name}(
        {params_str}
    ):
        """Create custom {inner_name}.

        Args:
{param_docs_str}

        Returns:
            Custom {inner_name} instance
        """
{body_content}

    return {create_func_name}
'''


def replace_fixture_in_file(
    conftest_path: Path,
    fixture_info: FixtureInfo,
    new_code: str,
) -> None:
    """Replace fixture in conftest.py file.

    Args:
        conftest_path: Path to conftest.py
        fixture_info: Original fixture information
        new_code: New factory fixture code
    """
    lines = list(fixture_info.lines)

    # Replace lines
    before = lines[: fixture_info.line_start - 1]
    after = lines[fixture_info.line_end :]

    new_lines = before + new_code.split("\n") + after

    conftest_path.write_text("\n".join(new_lines), encoding="utf-8")


def find_conftest_files(search_root: Path) -> list[Path]:
    """Find all conftest.py files.

    Args:
        search_root: Root directory to search

    Returns:
        List of conftest.py paths
    """
    return list(search_root.rglob("conftest.py"))


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Convert regular fixtures to factory fixtures"
    )
    parser.add_argument(
        "fixture_name",
        help="Name of fixture to convert",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to conftest.py file (default: search in tests/)",
    )
    parser.add_argument(
        "--params",
        help='Parameters to add (format: "name:type=default,...")',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying file",
    )

    args = parser.parse_args(argv)

    # Parse parameters
    params = parse_param_spec(args.params) if args.params else []

    # Find conftest file
    if args.file:
        conftest_files = [args.file]
    else:
        # Search in tests/
        search_root = Path.cwd() / "tests"
        conftest_files = find_conftest_files(search_root)

    if not conftest_files:
        print("Error: No conftest.py files found", file=sys.stderr)
        return 1

    # Find fixture
    fixture_info: FixtureInfo | None = None
    conftest_path: Path | None = None

    for path in conftest_files:
        info = find_fixture(path, args.fixture_name)
        if info:
            fixture_info = info
            conftest_path = path
            break

    if not fixture_info or not conftest_path:
        print(f"Error: Fixture '{args.fixture_name}' not found", file=sys.stderr)
        return 1

    # Convert to factory
    factory_code = convert_to_factory(fixture_info, params)

    if args.dry_run:
        print("=== Dry Run: Generated Factory Code ===")
        print(factory_code)
        print(f"\nWould modify: {conftest_path}")
    else:
        replace_fixture_in_file(conftest_path, fixture_info, factory_code)
        print(f"Converted {args.fixture_name} to factory in {conftest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
