#!/usr/bin/env python3
"""
Remove invalid <example> blocks from skill descriptions.

The <example> block pattern is NOT part of the official Agent Skills specification
and causes validation issues. This script removes them from all skill descriptions.
"""

import re
from pathlib import Path
import sys


def remove_example_blocks(description: str) -> str:
    """Remove <example>...</example> blocks from description."""
    # Pattern to match <example> blocks (including newlines)
    pattern = r'\s*<example>.*?</example>\s*'
    cleaned = re.sub(pattern, '\n', description, flags=re.DOTALL)

    # Clean up extra whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = cleaned.strip()

    return cleaned


def fix_skill_file(skill_path: Path) -> tuple[bool, str]:
    """
    Fix a single SKILL.md file by removing <example> blocks.

    Returns:
        (changed, message) - whether file was changed and status message
    """
    try:
        content = skill_path.read_text()

        # Split frontmatter and body
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "No YAML frontmatter found"

        frontmatter = parts[1]
        body = parts[2]

        # Check if description contains <example> blocks
        if '<example>' not in frontmatter:
            return False, "No <example> blocks found"

        # Remove <example> blocks from frontmatter
        fixed_frontmatter = remove_example_blocks(frontmatter)

        # Reconstruct file with proper formatting
        new_content = f"---\n{fixed_frontmatter}\n---{body}"

        # Write back
        skill_path.write_text(new_content)

        return True, "Fixed"

    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Fix all skills in the skills/ directory."""
    skills_dir = Path("skills")

    if not skills_dir.exists():
        print("Error: skills/ directory not found")
        print("Run this script from the repository root")
        sys.exit(1)

    # Find all SKILL.md files
    skill_files = list(skills_dir.glob("*/SKILL.md"))

    print(f"Found {len(skill_files)} skills")
    print("Removing <example> blocks from descriptions...\n")

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for skill_file in sorted(skill_files):
        skill_name = skill_file.parent.name
        changed, message = fix_skill_file(skill_file)

        if changed:
            fixed_count += 1
            print(f"✅ {skill_name:50s} - {message}")
        elif "Error" in message:
            error_count += 1
            print(f"❌ {skill_name:50s} - {message}")
        else:
            skipped_count += 1
            # Don't print skipped ones to reduce noise

    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  Fixed:   {fixed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors:  {error_count}")
    print(f"{'='*70}")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
