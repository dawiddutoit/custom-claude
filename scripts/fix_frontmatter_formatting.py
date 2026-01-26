#!/usr/bin/env python3
"""Fix malformed YAML frontmatter in SKILL.md files."""

import re
import sys
from pathlib import Path


def fix_frontmatter(skill_path: Path) -> bool:
    """
    Fix common frontmatter formatting issues:
    1. Missing newline after opening ---
    2. Content outside proper YAML fields before closing ---

    Returns True if modified, False otherwise.
    """
    try:
        content = skill_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR reading {skill_path}: {e}")
        return False

    # Check if file has frontmatter
    if not content.startswith('---'):
        return False

    # Fix case 1: ---name: should be ---\nname:
    if content.startswith('---name:') or content.startswith('---description:'):
        content = '---\n' + content[3:]
        modified = True
    else:
        modified = False

    # Split into parts
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"SKIP {skill_path.parent.name}: Invalid frontmatter structure")
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Fix case 2: Find lines that look like content but aren't YAML fields
    # These are lines that don't match key: value pattern and aren't part of multiline values
    lines = frontmatter.split('\n')
    new_lines = []
    in_multiline = False
    orphaned_lines = []

    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            new_lines.append(line)
            continue

        # Check if this is a YAML field (key: value)
        if re.match(r'^\s*[\w-]+\s*:', line):
            # Start of a field
            in_multiline = line.strip().endswith('|') or line.strip().endswith('>')
            new_lines.append(line)
        elif line.startswith('  ') or line.startswith('\t'):
            # Indented line - part of previous field
            new_lines.append(line)
        elif line.strip().startswith('-'):
            # List item
            new_lines.append(line)
        else:
            # This looks like orphaned content
            if line.strip() and not re.match(r'^\s*[\w-]+\s*:', line):
                orphaned_lines.append(line.strip())
                modified = True
            # Don't add orphaned lines to new_lines

    if modified:
        # Reconstruct the file
        new_frontmatter = '\n'.join(new_lines)

        # If we found orphaned lines, add them to the body
        if orphaned_lines:
            orphaned_text = '\n'.join(orphaned_lines)
            # Add to start of body with proper spacing
            body = f"\n\n{orphaned_text}\n{body.lstrip()}"

        new_content = f"---{new_frontmatter}---{body}"

        try:
            skill_path.write_text(new_content, encoding='utf-8')
            print(f"FIXED {skill_path.parent.name}")
            if orphaned_lines:
                print(f"  Moved orphaned content to body: {orphaned_lines}")
            return True
        except Exception as e:
            print(f"ERROR writing {skill_path}: {e}")
            return False

    return False


def main():
    skills_dir = Path('/Users/dawiddutoit/projects/claude/custom-claude/skills')

    if not skills_dir.exists():
        print(f"ERROR: Skills directory not found: {skills_dir}")
        sys.exit(1)

    # Find all SKILL.md files
    skill_files = list(skills_dir.glob('*/SKILL.md'))

    print(f"Found {len(skill_files)} SKILL.md files\n")

    fixed_count = 0
    skipped_count = 0

    for skill_file in sorted(skill_files):
        if fix_frontmatter(skill_file):
            fixed_count += 1
        else:
            skipped_count += 1

    print(f"\n{'='*60}")
    print(f"Total files: {len(skill_files)}")
    print(f"Fixed: {fixed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
