#!/usr/bin/env python3
"""Generate value objects with validation, factory methods, and tests.

This script automates the creation of frozen dataclass value objects following
the project's patterns. It generates both the value object and its test file.

Usage:
    python generate_value_object.py --name EmailAddress --field email --type str
    python generate_value_object.py --name UserId --field value --type int --factory from_string
    python generate_value_object.py --config value_object_spec.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Setup: Add .claude to path for skill_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skill_utils import ensure_path_setup, get_project_root, to_snake_case

ensure_path_setup()


@dataclass(frozen=True)
class FieldSpec:
    """Specification for a value object field."""

    name: str
    type: str
    optional: bool = False
    default: str | None = None


@dataclass(frozen=True)
class ValidationRule:
    """Validation rule for a value object."""

    type: str  # "empty", "format", "range", "custom"
    message: str
    pattern: str | None = None  # For format validation
    min_value: float | int | None = None  # For range validation
    max_value: float | int | None = None  # For range validation
    code: str | None = None  # For custom validation


@dataclass(frozen=True)
class ValueObjectSpec:
    """Complete specification for generating a value object."""

    name: str
    domain_concept: str
    encapsulated_logic: str
    fields: tuple[FieldSpec, ...]
    validations: tuple[ValidationRule, ...]
    factory_methods: tuple[str, ...]  # from_string, from_dict, from_content, etc.
    location: str  # "value_objects" or "values"
    needs_normalization: bool = False
    normalization_code: str | None = None


def generate_imports(spec: ValueObjectSpec) -> str:
    """Generate import statements based on spec.

    Args:
        spec: Value object specification.

    Returns:
        Python import statements as a string.
    """
    imports: list[str] = [
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
    ]

    # Check if Path type is used
    if any("Path" in f.type for f in spec.fields):
        imports.append("from pathlib import Path")

    # Check if regex validation is used
    if any(v.pattern for v in spec.validations):
        imports.insert(2, "import re")

    # Add typing imports if needed (Self for factory methods)
    if spec.factory_methods:
        imports.append("from typing import Self")

    return "\n".join(imports)


def generate_field_definitions(spec: ValueObjectSpec) -> str:
    """Generate field definitions for the dataclass.

    Args:
        spec: Value object specification.

    Returns:
        Python field definition lines as a string.
    """
    lines: list[str] = []
    for field_spec in spec.fields:
        field_type = field_spec.type
        if field_spec.optional:
            field_type = f"{field_type} | None"

        if field_spec.default is not None or field_spec.optional:
            default = field_spec.default if field_spec.default else "None"
            lines.append(f"    {field_spec.name}: {field_type} = {default}")
        else:
            lines.append(f"    {field_spec.name}: {field_type}")

    return "\n".join(lines)


def generate_validation_code(spec: ValueObjectSpec) -> str:
    """Generate validation code for __post_init__.

    Args:
        spec: Value object specification.

    Returns:
        Python validation code for __post_init__ method.
    """
    lines: list[str] = []

    for validation in spec.validations:
        if validation.type == "empty":
            # Find the field to validate
            field_name = validation.message.split()[0].lower()
            lines.append(f"        if not self.{field_name}:")
            lines.append(f'            raise ValueError("{validation.message}")')

        elif validation.type == "format":
            field_name = validation.message.split()[0].lower()
            if validation.pattern:
                lines.append(
                    f'        if not re.match(r"{validation.pattern}", self.{field_name}):'
                )
                lines.append(f'            raise ValueError("{validation.message}")')

        elif validation.type == "range":
            field_name = validation.message.split()[0].lower()
            if validation.min_value is not None:
                lines.append(f"        if self.{field_name} < {validation.min_value}:")
                lines.append(f'            raise ValueError("{validation.message}")')
            if validation.max_value is not None:
                lines.append(f"        if self.{field_name} > {validation.max_value}:")
                lines.append(f'            raise ValueError("{validation.message}")')

        elif validation.type == "custom" and validation.code:
            lines.append(f"        {validation.code}")

    # Add normalization if specified
    if spec.needs_normalization and spec.normalization_code:
        lines.append("")
        lines.append("        # Normalization in frozen context")
        lines.append(f"        {spec.normalization_code}")

    return "\n".join(lines) if lines else "        pass"


def generate_factory_methods(spec: ValueObjectSpec) -> str:
    """Generate factory methods.

    Args:
        spec: Value object specification.

    Returns:
        Python factory method definitions as a string.
    """
    methods: list[str] = []
    primary_field = spec.fields[0].name

    if "from_string" in spec.factory_methods:
        methods.append(f"""
    @classmethod
    def from_string(cls, value_str: str) -> Self:
        \"\"\"Create {spec.name} from string representation.

        Args:
            value_str: String to parse

        Returns:
            {spec.name} instance

        Raises:
            ValueError: If string format is invalid
        \"\"\"
        return cls({primary_field}=value_str)""")

    if "from_dict" in spec.factory_methods:
        field_args = ", ".join(
            f'{f.name}=data["{f.name}"]' for f in spec.fields if not f.optional
        )
        methods.append(f"""
    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        \"\"\"Create {spec.name} from dictionary representation.

        Args:
            data: Dictionary with value object data

        Returns:
            {spec.name} instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If validation fails
        \"\"\"
        return cls({field_args})""")

    if "from_content" in spec.factory_methods:
        methods.append(f"""
    @classmethod
    def from_content(cls, content: str) -> Self:
        \"\"\"Create {spec.name} from content.

        Args:
            content: Raw content to process

        Returns:
            {spec.name} instance
        \"\"\"
        import xxhash

        if content is None:
            content = ""

        hash_value = xxhash.xxh64(content.encode("utf-8")).hexdigest()
        return cls({primary_field}=hash_value)""")

    return "".join(methods)


def generate_string_methods(spec: ValueObjectSpec) -> str:
    """Generate __str__ and __repr__ methods.

    Args:
        spec: Value object specification.

    Returns:
        Python __str__ and __repr__ method definitions.
    """
    primary_field = spec.fields[0].name

    return f"""
    def __str__(self) -> str:
        \"\"\"User-friendly string representation.

        Returns:
            The {primary_field} as a string
        \"\"\"
        return str(self.{primary_field})

    def __repr__(self) -> str:
        \"\"\"Developer-friendly representation.

        Returns:
            String showing class and {primary_field}
        \"\"\"
        return f"{spec.name}('{{self.{primary_field}}}')\""""


def generate_to_dict_method(spec: ValueObjectSpec) -> str:
    """Generate to_dict serialization method.

    Args:
        spec: Value object specification.

    Returns:
        Python to_dict method definition.
    """
    fields = ", ".join(f'"{f.name}": self.{f.name}' for f in spec.fields)
    # Determine value type for dict annotation
    primary_type = spec.fields[0].type if spec.fields else "str"

    return f"""
    def to_dict(self) -> dict[str, {primary_type}]:
        \"\"\"Convert to dictionary representation.

        Returns:
            Dictionary with value object data
        \"\"\"
        return {{
            {fields}
        }}"""


def generate_value_object(spec: ValueObjectSpec) -> str:
    """Generate complete value object code.

    Args:
        spec: Value object specification.

    Returns:
        Complete Python source code for the value object module.
    """
    imports = generate_imports(spec)
    field_defs = generate_field_definitions(spec)
    validation_code = generate_validation_code(spec)
    factory_methods = generate_factory_methods(spec)
    string_methods = generate_string_methods(spec)
    to_dict_method = generate_to_dict_method(spec)

    return f'''"""Value object for {spec.domain_concept}.

This module defines the {spec.name} value object following Clean Architecture principles.
Value objects are immutable and represent domain concepts.
"""

{imports}


@dataclass(frozen=True)
class {spec.name}:
    """Immutable value object representing {spec.domain_concept}.

    Encapsulates {spec.encapsulated_logic}.
    """

{field_defs}

    def __post_init__(self) -> None:
        """Validate {spec.name} constraints.

        Raises:
            ValueError: If validation fails
        """
{validation_code}
{string_methods}
{factory_methods}
{to_dict_method}
'''


def generate_test_file(spec: ValueObjectSpec, import_path: str | None = None) -> str:
    """Generate pytest test file for the value object.

    Args:
        spec: Value object specification.
        import_path: Optional custom import path for the value object module.

    Returns:
        Complete Python test file source code.
    """
    primary_field = spec.fields[0].name
    test_class_name = f"Test{spec.name}"
    module_import = import_path or f"domain.{spec.location}.{to_snake_case(spec.name)}"

    # Generate validation tests
    validation_tests: list[str] = []
    for validation in spec.validations:
        if validation.type == "empty":
            validation_tests.append(f"""
    def test_empty_{primary_field}_raises(self) -> None:
        \"\"\"Test validation raises on empty {primary_field}.\"\"\"
        with pytest.raises(ValueError, match="cannot be empty"):
            {spec.name}({primary_field}="")""")

        elif validation.type == "format":
            validation_tests.append(f"""
    def test_invalid_format_raises(self) -> None:
        \"\"\"Test validation raises on invalid format.\"\"\"
        with pytest.raises(ValueError):
            {spec.name}({primary_field}="invalid-format")""")

    # Generate factory method tests
    factory_tests: list[str] = []
    if "from_string" in spec.factory_methods:
        factory_tests.append(f"""
    def test_from_string_factory(self) -> None:
        \"\"\"Test from_string factory method.\"\"\"
        obj = {spec.name}.from_string("test_value")
        assert obj.{primary_field} == "test_value\"""")

    if "from_dict" in spec.factory_methods:
        field_dict = ", ".join(
            f'"{f.name}": "test_{f.name}"' for f in spec.fields if not f.optional
        )
        factory_tests.append(f"""
    def test_from_dict_factory(self) -> None:
        \"\"\"Test from_dict factory method.\"\"\"
        data = {{{field_dict}}}
        obj = {spec.name}.from_dict(data)
        assert obj.{primary_field} == "test_{primary_field}\"""")

    return f'''"""Tests for {spec.name} value object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from {module_import} import {spec.name}


class {test_class_name}:
    """Test suite for {spec.name} value object."""

    def test_construction_success(self) -> None:
        \"\"\"Test successful construction.\"\"\"
        obj = {spec.name}({primary_field}="test_value")
        assert obj.{primary_field} == "test_value"

    def test_immutability(self) -> None:
        \"\"\"Test frozen dataclass immutability.\"\"\"
        obj = {spec.name}({primary_field}="test_value")

        with pytest.raises(FrozenInstanceError):
            obj.{primary_field} = "changed"
{"".join(validation_tests)}
{"".join(factory_tests)}

    def test_equality(self) -> None:
        \"\"\"Test value-based equality.\"\"\"
        obj1 = {spec.name}({primary_field}="test_value")
        obj2 = {spec.name}({primary_field}="test_value")
        assert obj1 == obj2

    def test_to_dict(self) -> None:
        \"\"\"Test dictionary serialization.\"\"\"
        obj = {spec.name}({primary_field}="test_value")
        data = obj.to_dict()
        assert "{primary_field}" in data
        assert data["{primary_field}"] == "test_value"

    def test_string_representation(self) -> None:
        \"\"\"Test __str__ and __repr__.\"\"\"
        obj = {spec.name}({primary_field}="test_value")
        assert str(obj) == "test_value"
        assert "{spec.name}" in repr(obj)
'''


def load_spec_from_json(json_path: Path) -> ValueObjectSpec:
    """Load value object specification from JSON file.

    Args:
        json_path: Path to the JSON specification file.

    Returns:
        ValueObjectSpec parsed from the JSON file.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the JSON is invalid.
        KeyError: If required fields are missing from the JSON.
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    fields = tuple(FieldSpec(**f) for f in data["fields"])
    validations = tuple(ValidationRule(**v) for v in data["validations"])
    factory_methods = tuple(data.get("factory_methods", ["from_string", "from_dict"]))

    return ValueObjectSpec(
        name=data["name"],
        domain_concept=data["domain_concept"],
        encapsulated_logic=data["encapsulated_logic"],
        fields=fields,
        validations=validations,
        factory_methods=factory_methods,
        location=data.get("location", "value_objects"),
        needs_normalization=data.get("needs_normalization", False),
        normalization_code=data.get("normalization_code"),
    )


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    parser = argparse.ArgumentParser(description="Generate value objects and tests")
    parser.add_argument("--name", help="Value object class name (e.g., EmailAddress)")
    parser.add_argument("--field", help="Primary field name (e.g., email, value)")
    parser.add_argument("--type", help="Field type (e.g., str, int, Path)")
    parser.add_argument("--domain", help="Domain concept description")
    parser.add_argument("--logic", help="Encapsulated logic description")
    parser.add_argument("--factory", action="append", help="Factory methods to generate")
    parser.add_argument("--config", type=Path, help="JSON config file with full spec")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: auto-detect from project root)",
    )
    parser.add_argument(
        "--test-output",
        type=Path,
        default=None,
        help="Test output directory (default: auto-detect from project root)",
    )

    args = parser.parse_args()

    # Load spec from config or CLI args
    spec: ValueObjectSpec
    if args.config:
        if not args.config.exists():
            print(f"Error: Config file not found: {args.config}", file=sys.stderr)
            return 1
        spec = load_spec_from_json(args.config)
    elif args.name and args.field and args.type:
        # Build minimal spec from CLI args
        factory_methods = tuple(args.factory) if args.factory else ("from_string", "from_dict")
        spec = ValueObjectSpec(
            name=args.name,
            domain_concept=args.domain or args.name,
            encapsulated_logic=args.logic or f"{args.field} validation and immutability",
            fields=(FieldSpec(name=args.field, type=args.type),),
            validations=(ValidationRule(type="empty", message=f"{args.field} cannot be empty"),),
            factory_methods=factory_methods,
            location="value_objects",
        )
    else:
        parser.error("Either --config or --name/--field/--type required")
        return 1  # Unreachable but makes type checker happy

    # Determine output paths
    project_root = get_project_root()
    if project_root is None:
        project_root = Path.cwd()

    output_dir = args.output or project_root / "src" / "domain" / spec.location
    test_output_dir = args.test_output or project_root / "tests" / "unit" / "domain" / spec.location

    # Generate files
    output_dir.mkdir(parents=True, exist_ok=True)
    test_output_dir.mkdir(parents=True, exist_ok=True)

    # Write value object
    vo_file = output_dir / f"{to_snake_case(spec.name)}.py"
    vo_code = generate_value_object(spec)
    vo_file.write_text(vo_code, encoding="utf-8")
    print(f"Created value object: {vo_file}")

    # Write test file
    test_file = test_output_dir / f"test_{to_snake_case(spec.name)}.py"
    test_code = generate_test_file(spec)
    test_file.write_text(test_code, encoding="utf-8")
    print(f"Created test file: {test_file}")

    # Update __init__.py if it exists
    init_file = output_dir / "__init__.py"
    if init_file.exists():
        init_content = init_file.read_text(encoding="utf-8")
        import_line = f"from .{to_snake_case(spec.name)} import {spec.name}\n"
        if import_line not in init_content:
            # Add to imports
            init_file.write_text(init_content + import_line, encoding="utf-8")
            print(f"Updated __init__.py with import for {spec.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
