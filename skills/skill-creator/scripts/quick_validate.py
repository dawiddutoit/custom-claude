#!/usr/bin/env python3
"""Quick validation script for Claude Code skills.

Validates SKILL.md frontmatter against the skill specification:
- Required fields: name, description
- Optional fields: license, allowed-tools, metadata
- Name: hyphen-case, max 64 characters
- Description: no angle brackets, max 1024 characters

Usage:
    python quick_validate.py <skill_directory>

Examples:
    python quick_validate.py ./skills/my-skill
    python quick_validate.py /path/to/skill-folder
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from typing import Any

# Skill specification constants
ALLOWED_FRONTMATTER_KEYS: frozenset[str] = frozenset(
    {"name", "description", "license", "allowed-tools", "metadata"}
)
MAX_NAME_LENGTH: int = 64
MAX_DESCRIPTION_LENGTH: int = 1024
HYPHEN_CASE_PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9-]+$")


class ValidationResult:
    """Result of skill validation."""

    __slots__ = ("valid", "message")

    def __init__(self, valid: bool, message: str) -> None:
        self.valid = valid
        self.message = message

    def __iter__(self):
        """Support tuple unpacking for backward compatibility."""
        return iter((self.valid, self.message))


def _extract_frontmatter(content: str) -> tuple[str, str] | None:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content.

    Returns:
        Tuple of (frontmatter_text, remaining_content) or None if no frontmatter.
    """
    if not content.startswith("---"):
        return None

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    return match.group(1), content[match.end() :]


def _validate_name(name: Any) -> str | None:
    """Validate skill name field.

    Args:
        name: Value from frontmatter.

    Returns:
        Error message if invalid, None if valid.
    """
    if not isinstance(name, str):
        return f"Name must be a string, got {type(name).__name__}"

    name = name.strip()
    if not name:
        return "Name cannot be empty"

    if not HYPHEN_CASE_PATTERN.match(name):
        return (
            f"Name '{name}' should be hyphen-case "
            "(lowercase letters, digits, and hyphens only)"
        )

    if name.startswith("-") or name.endswith("-") or "--" in name:
        return (
            f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        )

    if len(name) > MAX_NAME_LENGTH:
        return (
            f"Name is too long ({len(name)} characters). "
            f"Maximum is {MAX_NAME_LENGTH} characters."
        )

    return None


def _validate_description(description: Any) -> str | None:
    """Validate skill description field.

    Args:
        description: Value from frontmatter.

    Returns:
        Error message if invalid, None if valid.
    """
    if not isinstance(description, str):
        return f"Description must be a string, got {type(description).__name__}"

    description = description.strip()
    if not description:
        return "Description cannot be empty"

    if "<" in description or ">" in description:
        return "Description cannot contain angle brackets (< or >)"

    if len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            f"Description is too long ({len(description)} characters). "
            f"Maximum is {MAX_DESCRIPTION_LENGTH} characters."
        )

    return None


def validate_skill(skill_path: str | Path) -> ValidationResult:
    """Validate a skill directory against the skill specification.

    Args:
        skill_path: Path to the skill directory containing SKILL.md.

    Returns:
        ValidationResult with valid flag and message.
    """
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ValidationResult(False, "SKILL.md not found")

    # Read and validate frontmatter
    content = skill_md.read_text(encoding="utf-8")

    extracted = _extract_frontmatter(content)
    if extracted is None:
        return ValidationResult(False, "No YAML frontmatter found")

    frontmatter_text, _ = extracted

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return ValidationResult(False, "Frontmatter must be a YAML dictionary")
    except yaml.YAMLError as e:
        return ValidationResult(False, f"Invalid YAML in frontmatter: {e}")

    # Check for unexpected properties
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected_keys:
        return ValidationResult(
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}",
        )

    # Check required fields
    if "name" not in frontmatter:
        return ValidationResult(False, "Missing 'name' in frontmatter")
    if "description" not in frontmatter:
        return ValidationResult(False, "Missing 'description' in frontmatter")

    # Validate name
    name_error = _validate_name(frontmatter["name"])
    if name_error:
        return ValidationResult(False, name_error)

    # Validate description
    desc_error = _validate_description(frontmatter["description"])
    if desc_error:
        return ValidationResult(False, desc_error)

    return ValidationResult(True, "Skill is valid!")


def main() -> int:
    """Main entry point for CLI usage.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        return 1

    result = validate_skill(sys.argv[1])
    print(result.message)
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
