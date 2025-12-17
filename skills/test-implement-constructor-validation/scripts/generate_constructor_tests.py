#!/usr/bin/env python3
"""Auto-generate constructor validation tests from service class signatures.

This script parses a service class using AST, extracts the constructor signature,
and generates a complete pytest test class with:
- One fixture per parameter
- Success test (all valid parameters)
- Validation test per parameter (parameter set to None)
- Proper type: ignore comments
- Error message assertions

Usage:
    python generate_constructor_tests.py path/to/service.py
    python generate_constructor_tests.py path/to/service.py --stdout
    python generate_constructor_tests.py path/to/service.py --output path/to/test.py

Examples:
    # Generate from a service file
    python generate_constructor_tests.py src/services/user_service.py

    # Generate and write to test file
    python generate_constructor_tests.py src/services/user_service.py \\
        --output tests/unit/services/test_user_service.py

    # Specify class name explicitly (auto-detected by default)
    python generate_constructor_tests.py src/app/services/chunking_service.py \\
        --class-name ChunkingService
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# Setup: Add .claude to path for skill_utils and tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.skill_utils import ensure_path_setup

ensure_path_setup()


@dataclass
class Parameter:
    """Represents a constructor parameter."""

    name: str
    type_annotation: str
    is_self: bool = False


@dataclass
class ConstructorInfo:
    """Extracted constructor information."""

    class_name: str
    parameters: list[Parameter]
    module_path: str
    import_paths: dict[str, str]  # type_name -> import_path


class ServiceConstructorParser:
    """Parse service class constructors using AST."""

    def __init__(self, file_path: Path) -> None:
        """Initialize parser with file path.

        Args:
            file_path: Path to Python source file
        """
        self.file_path = file_path
        self.source = file_path.read_text()
        self.tree = ast.parse(self.source)

    def find_class(self, class_name: str | None = None) -> ast.ClassDef | None:
        """Find class definition in AST.

        Args:
            class_name: Specific class name to find, or None for first class

        Returns:
            ClassDef node or None if not found
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                if class_name is None or node.name == class_name:
                    # Skip test classes
                    if not node.name.startswith("Test"):
                        return node
        return None

    def extract_constructor(self, class_def: ast.ClassDef) -> ast.FunctionDef | None:
        """Extract __init__ method from class.

        Args:
            class_def: ClassDef AST node

        Returns:
            FunctionDef node for __init__ or None
        """
        for node in class_def.body:
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                return node
        return None

    def get_type_annotation(self, annotation: ast.expr | None) -> str:
        """Convert AST annotation to string.

        Args:
            annotation: AST annotation node

        Returns:
            String representation of type
        """
        if annotation is None:
            return "Any"

        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Constant):
            return str(annotation.value)
        if isinstance(annotation, ast.Subscript):
            # Handle generic types like list[str]
            value = self.get_type_annotation(annotation.value)
            slice_val = self.get_type_annotation(annotation.slice)
            return f"{value}[{slice_val}]"
        if isinstance(annotation, ast.BinOp):
            # Handle union types (Type | None)
            left = self.get_type_annotation(annotation.left)
            right = self.get_type_annotation(annotation.right)
            return f"{left} | {right}"
        if isinstance(annotation, ast.Attribute):
            # Handle qualified names like module.Type
            return f"{self.get_type_annotation(annotation.value)}.{annotation.attr}"
        return "Any"

    def extract_imports(self) -> dict[str, str]:
        """Extract import statements for type annotations.

        Returns:
            Dict mapping type names to import paths
        """
        imports = {}

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    type_name = alias.asname or alias.name
                    imports[type_name] = module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    type_name = alias.asname or alias.name
                    imports[type_name] = alias.name

        return imports

    def parse(self, class_name: str | None = None) -> ConstructorInfo | None:
        """Parse service class and extract constructor info.

        Args:
            class_name: Specific class name or None for auto-detect

        Returns:
            ConstructorInfo or None if not found
        """
        class_def = self.find_class(class_name)
        if not class_def:
            return None

        constructor = self.extract_constructor(class_def)
        if not constructor:
            return None

        parameters = []
        for arg in constructor.args.args:
            if arg.arg == "self":
                continue

            param = Parameter(
                name=arg.arg,
                type_annotation=self.get_type_annotation(arg.annotation),
                is_self=False,
            )
            parameters.append(param)

        imports = self.extract_imports()

        # Determine module path from file path
        parts = self.file_path.parts
        if "src" in parts:
            src_idx = parts.index("src")
            module_parts = list(parts[src_idx + 1 :])
            module_parts[-1] = module_parts[-1].replace(".py", "")
            module_path = ".".join(module_parts)
        else:
            module_path = str(self.file_path.stem)

        return ConstructorInfo(
            class_name=class_def.name,
            parameters=parameters,
            module_path=module_path,
            import_paths=imports,
        )


class TestGenerator:
    """Generate test code from constructor information."""

    def __init__(self, constructor_info: ConstructorInfo) -> None:
        """Initialize generator with constructor info.

        Args:
            constructor_info: Parsed constructor information
        """
        self.info = constructor_info

    def generate_imports(self) -> str:
        """Generate import statements.

        Returns:
            Import block as string
        """
        lines = [
            "import pytest",
            "from unittest.mock import MagicMock",
            "",
        ]

        # Import the service class
        lines.append(f"from {self.info.module_path} import {self.info.class_name}")

        # Import parameter types
        type_imports = {}
        for param in self.info.parameters:
            # Clean type annotation (remove | None, quotes, etc)
            base_type = param.type_annotation.strip('"').split("|")[0].strip()

            if base_type in self.info.import_paths:
                import_path = self.info.import_paths[base_type]
                if import_path not in type_imports:
                    type_imports[import_path] = []
                if base_type not in type_imports[import_path]:
                    type_imports[import_path].append(base_type)

        for import_path, types in sorted(type_imports.items()):
            types_str = ", ".join(sorted(types))
            lines.append(f"from {import_path} import {types_str}")

        return "\n".join(lines)

    def generate_fixture(self, param: Parameter) -> str:
        """Generate pytest fixture for a parameter.

        Args:
            param: Parameter to create fixture for

        Returns:
            Fixture code as string
        """
        fixture_name = f"mock_{param.name}"
        base_type = param.type_annotation.strip('"').split("|")[0].strip()

        lines = [
            "    @pytest.fixture",
            f"    def {fixture_name}(self):",
            f'        """Create mock {base_type}."""',
            f"        return MagicMock(spec={base_type})",
            "",
        ]

        return "\n".join(lines)

    def generate_success_test(self) -> str:
        """Generate test for successful initialization.

        Returns:
            Test method code as string
        """
        # Method signature
        fixture_params = [f"mock_{p.name}" for p in self.info.parameters]
        params_str = ", ".join(["self", *fixture_params])

        lines = [
            "    def test_constructor_initializes_with_valid_dependencies(",
            f"        {params_str},",
            "    ):",
            '        """Test that constructor properly initializes with all valid dependencies."""',
        ]

        # Instantiation
        lines.append(f"        instance = {self.info.class_name}(")
        for param in self.info.parameters:
            lines.append(f"            {param.name}=mock_{param.name},")
        lines.append("        )")
        lines.append("")

        # Assertions
        for param in self.info.parameters:
            lines.append(f"        assert instance.{param.name} is mock_{param.name}")

        return "\n".join(lines)

    def generate_validation_test(self, test_param: Parameter) -> str:
        """Generate validation test for a specific parameter.

        Args:
            test_param: Parameter to test for None

        Returns:
            Test method code as string
        """
        # Method signature - exclude the fixture being tested
        fixture_params = [
            f"mock_{p.name}" for p in self.info.parameters if p.name != test_param.name
        ]
        params_str = ", ".join(["self", *fixture_params])

        base_type = test_param.type_annotation.strip('"').split("|")[0].strip()

        lines = [
            f"    def test_constructor_fails_when_{test_param.name}_is_none(",
            f"        {params_str},",
            "    ):",
            f'        """Test that constructor raises ValueError when {base_type} is None."""',
            "        with pytest.raises(ValueError) as exc_info:",
            f"            {self.info.class_name}(",
        ]

        # Constructor call with None for test parameter
        for param in self.info.parameters:
            if param.name == test_param.name:
                lines.append(f"                {param.name}=None,  # type: ignore")
            else:
                lines.append(f"                {param.name}=mock_{param.name},")

        lines.append("            )")
        lines.append("")

        # Error message assertion
        lines.append(
            f'        assert "{base_type} is required for {self.info.class_name}" in str(exc_info.value)'
        )

        return "\n".join(lines)

    def generate(self) -> str:
        """Generate complete test class.

        Returns:
            Complete test file content as string
        """
        lines = [self.generate_imports(), "", ""]

        # Class definition
        lines.append(f"class Test{self.info.class_name}Constructor:")
        lines.append(
            f'    """Test {self.info.class_name} constructor and initialization."""'
        )
        lines.append("")

        # Fixtures
        lines.append("    # ===== FIXTURES =====")
        lines.append("")
        for param in self.info.parameters:
            lines.append(self.generate_fixture(param))

        # Success test
        lines.append("    # ===== SUCCESS CASE =====")
        lines.append("")
        lines.append(self.generate_success_test())
        lines.append("")

        # Validation tests
        lines.append("    # ===== VALIDATION TESTS =====")
        lines.append("")
        for param in self.info.parameters:
            lines.append(self.generate_validation_test(param))
            lines.append("")

        return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-generate constructor validation tests from service class",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1] if __doc__ and "Usage:" in __doc__ else "",
    )

    parser.add_argument(
        "service_file",
        type=Path,
        help="Path to service Python file",
    )

    parser.add_argument(
        "--class-name",
        help="Specific class name to extract (auto-detected if not provided)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output test file path (default: stdout)",
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Force output to stdout",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.service_file.exists():
        print(f"Error: Service file not found: {args.service_file}", file=sys.stderr)
        sys.exit(1)

    # Parse service constructor
    parser_obj = ServiceConstructorParser(args.service_file)
    constructor_info = parser_obj.parse(args.class_name)

    if not constructor_info:
        if args.class_name:
            print(
                f"Error: Class '{args.class_name}' not found in {args.service_file}",
                file=sys.stderr,
            )
        else:
            print(
                f"Error: No class with constructor found in {args.service_file}",
                file=sys.stderr,
            )
        sys.exit(1)

    # Generate test code
    generator = TestGenerator(constructor_info)
    test_code = generator.generate()

    # Output
    if args.stdout or not args.output:
        print(test_code)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(test_code)
        print(f"Generated test file: {args.output}")


if __name__ == "__main__":
    main()
