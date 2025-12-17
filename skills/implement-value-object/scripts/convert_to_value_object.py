#!/usr/bin/env python3
"""Analyze codebase to suggest value object candidates.

This script scans method signatures and identifies primitives that should
be replaced with value objects. It suggests candidates based on:
- Semantic naming (email, path, id, hash, url, etc.)
- Repeated patterns
- Validation requirements

Usage:
    python convert_to_value_object.py
    python convert_to_value_object.py --path src/project_watch_mcp
    python convert_to_value_object.py --generate  # Generate value object stubs
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# Setup: Add .claude to path for skill_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skill_utils import ensure_path_setup, get_project_root, to_pascal_case

ensure_path_setup()


@dataclass(frozen=True)
class ValueObjectCandidate:
    """A candidate for conversion to value object."""

    name: str
    primitive_type: str
    reason: str
    occurrences: int
    files: tuple[Path, ...]
    example_usage: str


@dataclass(frozen=True)
class ParameterUsage:
    """Tracks parameter usage across the codebase."""

    param_name: str
    param_type: str
    file: Path
    line: int
    context: str  # function/method name


# Type alias for semantic pattern configuration
type SemanticPatternInfo = dict[str, list[str] | str]

# Patterns that suggest value objects
SEMANTIC_PATTERNS: dict[str, SemanticPatternInfo] = {
    "email": {"types": ["str"], "validation": "email format"},
    "url": {"types": ["str"], "validation": "URL format"},
    "path": {"types": ["str", "Path"], "validation": "path existence/format"},
    "id": {"types": ["str", "int"], "validation": "uniqueness/format"},
    "hash": {"types": ["str"], "validation": "hex format"},
    "uuid": {"types": ["str"], "validation": "UUID format"},
    "name": {"types": ["str"], "validation": "non-empty/identifier"},
    "phone": {"types": ["str"], "validation": "phone format"},
    "address": {"types": ["str"], "validation": "address format"},
    "version": {"types": ["str"], "validation": "version format"},
    "timestamp": {"types": ["int", "float"], "validation": "range"},
    "port": {"types": ["int"], "validation": "range 1-65535"},
    "username": {"types": ["str"], "validation": "identifier format"},
    "password": {"types": ["str"], "validation": "strength/length"},
    "token": {"types": ["str"], "validation": "format/expiry"},
    "code": {"types": ["str"], "validation": "format"},
    "key": {"types": ["str"], "validation": "format"},
}


class ValueObjectAnalyzer(ast.NodeVisitor):
    """AST visitor to find value object candidates."""

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        self.usages: list[ParameterUsage] = []
        self.current_function: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition to analyze parameters."""
        self.current_function = node.name

        for arg in node.args.args:
            if arg.annotation:
                param_name = arg.arg
                param_type = self._get_type_name(arg.annotation)

                # Check if parameter matches semantic pattern
                if self._matches_pattern(param_name, param_type):
                    self.usages.append(
                        ParameterUsage(
                            param_name=param_name,
                            param_type=param_type,
                            file=self.filepath,
                            line=node.lineno,
                            context=f"{self.current_function}()",
                        )
                    )

        self.generic_visit(node)
        self.current_function = None

    def _get_type_name(self, annotation: ast.expr) -> str:
        """Extract type name from annotation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Constant):
            return str(annotation.value)
        if isinstance(annotation, ast.Subscript):
            # Handle Optional[X], list[X], etc.
            return self._get_type_name(annotation.value)
        if isinstance(annotation, ast.BinOp):
            # Handle X | None (union types)
            if isinstance(annotation.op, ast.BitOr):
                return self._get_type_name(annotation.left)
        return "Unknown"

    def _matches_pattern(self, param_name: str, param_type: str) -> bool:
        """Check if parameter matches a value object pattern."""
        param_lower = param_name.lower()

        # Check exact matches
        for pattern, info in SEMANTIC_PATTERNS.items():
            types = info.get("types", [])
            if isinstance(types, list) and pattern in param_lower and param_type in types:
                return True

        # Check suffixes
        suffix_patterns: dict[str, list[str]] = {
            "_id": ["str"],
            "_path": ["str", "Path"],
            "_hash": ["str"],
            "_url": ["str"],
            "_email": ["str"],
        }
        for suffix, valid_types in suffix_patterns.items():
            if param_name.endswith(suffix) and param_type in valid_types:
                return True

        return False


def analyze_directory(path: Path) -> list[ParameterUsage]:
    """Analyze a directory for value object candidates.

    Args:
        path: Directory path to analyze recursively.

    Returns:
        List of parameter usages that match value object patterns.
    """
    all_usages: list[ParameterUsage] = []

    for py_file in path.rglob("*.py"):
        if py_file.name == "__init__.py" or py_file.name.startswith("test_"):
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))

            analyzer = ValueObjectAnalyzer(py_file)
            analyzer.visit(tree)

            all_usages.extend(analyzer.usages)
        except (SyntaxError, UnicodeDecodeError):
            continue

    return all_usages


def group_candidates(
    usages: list[ParameterUsage],
    min_occurrences: int = 2,
) -> list[ValueObjectCandidate]:
    """Group usages into value object candidates.

    Args:
        usages: List of parameter usages to group.
        min_occurrences: Minimum number of occurrences to suggest a candidate.

    Returns:
        List of value object candidates sorted by occurrence count (descending).
    """
    # Group by parameter name pattern
    groups: dict[str, list[ParameterUsage]] = defaultdict(list)

    for usage in usages:
        # Extract base name (remove prefixes/suffixes)
        base_name = extract_base_name(usage.param_name)
        groups[base_name].append(usage)

    # Create candidates
    candidates: list[ValueObjectCandidate] = []
    for base_name, group_usages in groups.items():
        if len(group_usages) < min_occurrences:
            continue

        # Get most common type
        type_counts: dict[str, int] = defaultdict(int)
        for usage in group_usages:
            type_counts[usage.param_type] += 1
        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0]

        # Determine reason
        reason = determine_reason(base_name, most_common_type)

        # Get unique files as tuple for frozen dataclass
        files = tuple({usage.file for usage in group_usages})

        # Get example usage
        example = f"{group_usages[0].context} in {group_usages[0].file.name}"

        candidates.append(
            ValueObjectCandidate(
                name=to_pascal_case(base_name),
                primitive_type=most_common_type,
                reason=reason,
                occurrences=len(group_usages),
                files=files,
                example_usage=example,
            )
        )

    # Sort by occurrence count (most used first)
    return sorted(candidates, key=lambda x: x.occurrences, reverse=True)


def extract_base_name(param_name: str) -> str:
    """Extract base semantic name from parameter.

    Removes common prefixes and suffixes to find the core semantic name.

    Args:
        param_name: Parameter name to process.

    Returns:
        Base semantic name without common prefixes/suffixes.
    """
    result = param_name

    # Remove common prefixes
    prefixes = ("src_", "dst_", "input_", "output_", "old_", "new_")
    for prefix in prefixes:
        if result.startswith(prefix):
            result = result[len(prefix) :]
            break  # Only remove one prefix

    # Remove common suffixes
    suffixes = ("_str", "_value", "_data")
    for suffix in suffixes:
        if result.endswith(suffix):
            result = result[: -len(suffix)]
            break  # Only remove one suffix

    return result


def determine_reason(base_name: str, param_type: str) -> str:
    """Determine why this should be a value object.

    Args:
        base_name: Base semantic name of the parameter.
        param_type: Python type of the parameter.

    Returns:
        Human-readable reason for converting to a value object.
    """
    base_lower = base_name.lower()

    # Pattern-based reason mapping
    reason_patterns: dict[tuple[str, ...], str] = {
        ("email",): "Email validation (format, domain check)",
        ("path", "file"): "Path normalization and validation",
        ("id", "uuid"): "ID uniqueness and format validation",
        ("hash",): "Hash format validation (hex)",
        ("url", "uri"): "URL format and scheme validation",
        ("name",): "Name validation (non-empty, identifier)",
        ("version",): "Version format validation (semver)",
        ("port",): "Port range validation (1-65535)",
    }

    for keywords, reason in reason_patterns.items():
        if any(keyword in base_lower for keyword in keywords):
            return reason

    return f"Type safety and {param_type} validation"


def generate_value_object_stub(candidate: ValueObjectCandidate) -> str:
    """Generate a value object stub for a candidate.

    Args:
        candidate: The value object candidate to generate code for.

    Returns:
        Python source code for a frozen dataclass value object.
    """
    field_name = "value"
    validation = get_validation_code(candidate.name.lower(), candidate.primitive_type)
    file_examples = "\n".join(f"# - {f}" for f in candidate.files[:5])

    return f'''"""Value object for {candidate.name}.

Generated candidate based on {candidate.occurrences} usages across codebase.
Reason: {candidate.reason}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class {candidate.name}:
    """Immutable {candidate.name} value object.

    {candidate.reason}
    """

    {field_name}: {candidate.primitive_type}

    def __post_init__(self) -> None:
        """Validate {candidate.name} constraints."""
{validation}

    def __str__(self) -> str:
        """String representation."""
        return str(self.{field_name})

    def __repr__(self) -> str:
        """Developer representation."""
        return f"{candidate.name}('{{self.{field_name}}}')"

    @classmethod
    def from_string(cls, value_str: str) -> Self:
        """Create from string."""
        return cls({field_name}=value_str)

    def to_dict(self) -> dict[str, {candidate.primitive_type}]:
        """Convert to dictionary."""
        return {{"{field_name}": self.{field_name}}}


# Example usage locations:
{file_examples}
'''


def get_validation_code(name: str, type_name: str) -> str:
    """Get appropriate validation code based on name.

    Args:
        name: Name pattern to determine validation type.
        type_name: Python type name (str, int, etc.).

    Returns:
        Python code string for __post_init__ validation.
    """
    # Validation code templates
    validation_templates: dict[tuple[str, ...], str] = {
        ("email",): """        if not self.value:
            raise ValueError("Email cannot be empty")
        if "@" not in self.value:
            raise ValueError(f"Invalid email format: {self.value}")""",
        ("path", "file"): """        if not self.value:
            raise ValueError("Path cannot be empty")
        # Add path validation/normalization as needed""",
        ("id", "uuid"): """        if not self.value:
            raise ValueError("ID cannot be empty")
        # Add ID format validation as needed""",
        ("hash",): """        if not self.value:
            raise ValueError("Hash cannot be empty")
        try:
            int(self.value, 16)
        except ValueError:
            raise ValueError(f"Invalid hash format: {self.value}") from None""",
        ("url",): """        if not self.value:
            raise ValueError("URL cannot be empty")
        # Add URL format validation as needed""",
        ("port",): """        if not (1 <= self.value <= 65535):
            raise ValueError(f"Port must be 1-65535, got {self.value}")""",
    }

    # Find matching template
    for keywords, template in validation_templates.items():
        if any(keyword in name for keyword in keywords):
            return template

    # Default validation
    return """        if not self.value:
            raise ValueError(f"{self.__class__.__name__} cannot be empty")"""


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 for success, 1 for errors.
    """
    parser = argparse.ArgumentParser(
        description="Analyze codebase for value object candidates"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Path to analyze (default: auto-detect from project root)",
    )
    parser.add_argument(
        "--min-occurrences",
        type=int,
        default=2,
        help="Minimum occurrences to suggest (default: 2)",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate value object stub files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for generated stubs",
    )

    args = parser.parse_args()

    # Determine analysis path
    analysis_path = args.path
    if analysis_path is None:
        project_root = get_project_root()
        if project_root is not None:
            analysis_path = project_root / "src"
        else:
            analysis_path = Path.cwd()

    if not analysis_path.exists():
        print(f"Error: Path does not exist: {analysis_path}", file=sys.stderr)
        return 1

    # Analyze codebase
    usages = analyze_directory(analysis_path)

    # Group into candidates
    candidates = group_candidates(usages, min_occurrences=args.min_occurrences)

    if not candidates:
        print("No value object candidates found.")
        return 0

    # Print candidates
    print(f"\nFound {len(candidates)} value object candidate(s):\n")
    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate.name}")
        print(f"   Type: {candidate.primitive_type}")
        print(f"   Occurrences: {candidate.occurrences}")
        print(f"   Reason: {candidate.reason}")
        print(f"   Example: {candidate.example_usage}")
        print()

    # Generate stubs if requested
    if args.generate:
        output_dir = args.output_dir or Path.cwd() / "generated_value_objects"
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Generating stubs in {output_dir}...")
        for candidate in candidates:
            stub_file = output_dir / f"{candidate.name.lower()}.py"
            stub_code = generate_value_object_stub(candidate)
            stub_file.write_text(stub_code, encoding="utf-8")
            print(f"  Created: {stub_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
