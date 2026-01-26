#!/usr/bin/env python3
"""Add version field to all SKILL.md files that are missing it."""

import re
import sys
from pathlib import Path


def add_version_to_skill(skill_path: Path) -> bool:
    """
    Add version: 1.0.0 to a SKILL.md file if it's missing.

    Returns True if modified, False if already had version or error.
    """
    try:
        content = skill_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR reading {skill_path}: {e}")
        return False

    # Check if file has frontmatter
    if not content.startswith('---'):
        print(f"SKIP {skill_path.parent.name}: No frontmatter")
        return False

    # Split into frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"SKIP {skill_path.parent.name}: Invalid frontmatter")
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Check if version already exists
    if re.search(r'^\s*version\s*:', frontmatter, re.MULTILINE):
        return False

    # Find the description field and add version after it
    # Handle both single-line and multi-line descriptions
    lines = frontmatter.split('\n')
    new_lines = []
    inside_description = False
    version_added = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Check if we're starting a description field
        if re.match(r'^\s*description\s*:', line):
            inside_description = True
            # If it's a single-line description, add version on next line
            if not line.strip().endswith('|'):
                inside_description = False
                # Find indentation of current field
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + 'version: 1.0.0')
                version_added = True
        elif inside_description:
            # Check if we're ending the multi-line description
            # Description ends when we hit a non-indented line or another field
            if line.strip() and not line.startswith('  ') and not line.startswith('\t'):
                # This is a new field, add version before it
                # Find indentation by looking at previous fields
                indent = 0
                for prev_line in reversed(new_lines[:-1]):
                    if re.match(r'^\s*\w+\s*:', prev_line):
                        indent = len(prev_line) - len(prev_line.lstrip())
                        break
                new_lines.insert(-1, ' ' * indent + 'version: 1.0.0')
                version_added = True
                inside_description = False

    # If we never added it (description was last field), add at end
    if not version_added:
        # Find the indent of the last field
        indent = 0
        for line in reversed(lines):
            if re.match(r'^\s*\w+\s*:', line):
                indent = len(line) - len(line.lstrip())
                break
        new_lines.append(' ' * indent + 'version: 1.0.0')

    # Reconstruct the file
    new_frontmatter = '\n'.join(new_lines)
    new_content = f"---{new_frontmatter}---{body}"

    try:
        skill_path.write_text(new_content, encoding='utf-8')
        print(f"UPDATED {skill_path.parent.name}")
        return True
    except Exception as e:
        print(f"ERROR writing {skill_path}: {e}")
        return False


def main():
    skills_dir = Path('/Users/dawiddutoit/projects/claude/custom-claude/skills')

    if not skills_dir.exists():
        print(f"ERROR: Skills directory not found: {skills_dir}")
        sys.exit(1)

    # Find all SKILL.md files
    skill_files = list(skills_dir.glob('*/SKILL.md'))

    print(f"Found {len(skill_files)} SKILL.md files\n")

    modified_count = 0
    skipped_count = 0

    for skill_file in sorted(skill_files):
        if add_version_to_skill(skill_file):
            modified_count += 1
        else:
            skipped_count += 1

    print(f"\n{'='*60}")
    print(f"Total files: {len(skill_files)}")
    print(f"Modified: {modified_count}")
    print(f"Skipped: {skipped_count}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
