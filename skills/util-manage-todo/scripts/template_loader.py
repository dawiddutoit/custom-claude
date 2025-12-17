#!/usr/bin/env python3
"""Template loading and filling for manage-todo skill.

This module provides functions to load todo templates from files and fill them
with replacement values. Templates use {PLACEHOLDER} syntax for variable substitution.

Example usage:
    # Load a template
    template = load_template("simple_feature")

    # Fill with values
    filled = fill_template(template, {
        "TITLE": "Authentication",
        "DATE": "2025-10-17",
        "OBJECTIVE": "Implement user login"
    })
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

# Setup: Add .claude to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
if str(_claude_root) not in sys.path:
    sys.path.insert(0, str(_claude_root))

from skill_utils import ensure_path_setup

ensure_path_setup()


class TemplateLoadError(Exception):
    """Raised when template loading fails.

    This exception is raised when:
    - A template name is not recognized
    - The template file does not exist
    - The template section cannot be found in the file
    - File I/O errors occur
    """


# Template name to markdown section mapping (from todo-templates.md)
# Note: This mapping should be kept in sync with the actual template file
_TEMPLATE_SECTIONS: Final[dict[str, str]] = {
    "simple_feature": "## Template 1: Simple Feature Implementation",
    "bug_fix": "## Template 2: Complex Multi-Phase Project",  # Legacy mapping
    "refactor_migration": "## Template 3: Refactor/Migration Project",
    "spike_research": "## Template 5: Spike/Research Task",
    "complex_multi_phase": "## Template 2: Complex Multi-Phase Project",
}

# Type alias for template names
type TemplateName = str


def get_available_templates() -> list[str]:
    """Get list of available template names.

    Returns:
        List of valid template names that can be passed to load_template.
    """
    return list(_TEMPLATE_SECTIONS.keys())


def load_template(template_name: TemplateName, template_dir: Path | None = None) -> str:
    """Load a template from the templates directory.

    Args:
        template_name: Name of template to load (e.g., "simple_feature",
            "refactor_migration", "bug_fix", "spike_research", "complex_multi_phase")
        template_dir: Optional custom template directory path

    Returns:
        Template content as string

    Raises:
        TemplateLoadError: If template not found or cannot be loaded
    """
    if template_dir is None:
        # Default to templates directory relative to this script
        template_dir = Path(__file__).parent.parent / "templates"

    if template_name not in _TEMPLATE_SECTIONS:
        msg = (
            f"Unknown template: '{template_name}'. "
            f"Valid templates: {list(_TEMPLATE_SECTIONS.keys())}"
        )
        raise TemplateLoadError(
            msg
        )

    # Read the combined template file
    template_file = template_dir / "todo-templates.md"

    if not template_file.exists():
        msg = f"Template file not found: {template_file}"
        raise TemplateLoadError(msg)

    try:
        with open(template_file, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        msg = f"Failed to read template file: {e}"
        raise TemplateLoadError(msg) from e

    # Extract the specific template section
    section_header = _TEMPLATE_SECTIONS[template_name]
    template = _extract_template_section(content, section_header)

    if not template:
        msg = f"Template section not found: {section_header}"
        raise TemplateLoadError(msg)

    return template


def _extract_template_section(content: str, section_header: str) -> str:
    """Extract a template section from the combined template file.

    Args:
        content: Full file content
        section_header: Section header to find (e.g., "## Template 1: ...")

    Returns:
        Extracted template section as string
    """
    lines = content.split("\n")

    # Find the section start
    section_start = -1
    for i, line in enumerate(lines):
        if line.strip() == section_header:
            section_start = i
            break

    if section_start == -1:
        return ""

    # Find the next section header or end of file
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        # Next template section starts with "## Template"
        if lines[i].strip().startswith("## Template"):
            section_end = i
            break
        # Or end of templates section
        if lines[i].strip() == "---":
            section_end = i
            break

    # Extract the markdown code block from the section
    # Look for ```markdown ... ```
    template_lines = []
    in_code_block = False
    for i in range(section_start, section_end):
        line = lines[i]
        if line.strip() == "```markdown":
            in_code_block = True
            continue
        if in_code_block and line.strip() == "```":
            break
        if in_code_block:
            template_lines.append(line)

    return "\n".join(template_lines)


def fill_template(template: str, replacements: dict[str, str]) -> str:
    """Fill template placeholders with replacement values.

    Replaces all occurrences of {PLACEHOLDER} in the template with the
    corresponding value from the replacements dictionary. Placeholders
    that are not in the replacements dict are left unchanged.

    Args:
        template: Template string with {PLACEHOLDER} syntax
        replacements: Dictionary mapping placeholder names (without braces) to values

    Returns:
        Template with placeholders replaced

    Example:
        >>> template = "# Todo: {TITLE}\\nDate: {DATE}"
        >>> filled = fill_template(template, {"TITLE": "Feature X", "DATE": "2025-10-17"})
        >>> print(filled)
        # Todo: Feature X
        Date: 2025-10-17

    Note:
        This function performs simple string replacement. For more complex
        templating needs, consider using a dedicated templating library.
    """
    result = template
    for key, value in replacements.items():
        placeholder = "{" + key + "}"
        result = result.replace(placeholder, value)
    return result
