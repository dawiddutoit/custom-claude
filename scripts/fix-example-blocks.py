#!/usr/bin/env python3
"""
Remove invalid <example> blocks from skill descriptions.

The <example> block pattern is NOT part of the official Agent Skills specification
and causes validation issues. This script removes them from all SKILL.md files.
"""

import re
import sys
from pathlib import Path
from typing import Tuple


def extract_frontmatter(content: str) -> Tuple[str, str]:
    """Extract YAML frontmatter and body from SKILL.md content."""
    lines = content.split('\n')

    if not lines or lines[0].strip() != '---':
        raise ValueError("SKILL.md must start with YAML frontmatter (---)")

    # Find second delimiter
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("Could not find closing --- for YAML frontmatter")

    frontmatter = '\n'.join(lines[1:end_idx])
    body = '\n'.join(lines[end_idx + 1:])

    return frontmatter, body


def remove_example_blocks(frontmatter: str) -> str:
    """Remove <example>...</example> blocks from description field in YAML."""
    # Pattern to match <example> blocks (including newlines and indentation)
    # This matches across multiple lines within the description field
    pattern = r'\s*<example>.*?</example>\s*'

    cleaned = re.sub(pattern, '\n', frontmatter, flags=re.DOTALL)

    # Clean up excessive blank lines that may result
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned


def process_skill_file(skill_path: Path, dry_run: bool = False) -> bool:
    """Process a single SKILL.md file to remove example blocks."""
    try:
        content = skill_path.read_text(encoding='utf-8')

        # Check if file has example blocks
        if '<example>' not in content:
            return False  # No changes needed

        # Extract frontmatter and body
        frontmatter, body = extract_frontmatter(content)

        # Check if example blocks are in frontmatter
        if '<example>' not in frontmatter:
            return False  # Example blocks only in body, which is fine

        # Remove example blocks from frontmatter
        cleaned_frontmatter = remove_example_blocks(frontmatter)

        if cleaned_frontmatter == frontmatter:
            return False  # No changes made

        # Reconstruct file
        new_content = f"---\n{cleaned_frontmatter}\n---\n{body}"

        if dry_run:
            print(f"[DRY RUN] Would fix: {skill_path}")
            return True

        # Write back
        skill_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Fixed: {skill_path}")
        return True

    except Exception as e:
        print(f"❌ Error processing {skill_path}: {e}", file=sys.stderr)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove invalid <example> blocks from skill descriptions"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    parser.add_argument(
        "skills_dir",
        nargs="?",
        default="skills",
        help="Directory containing skills (default: skills)"
    )

    args = parser.parse_args()

    skills_dir = Path(args.skills_dir)
    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all SKILL.md files
    skill_files = list(skills_dir.glob("*/SKILL.md"))

    if not skill_files:
        print(f"No SKILL.md files found in {skills_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(skill_files)} skill files")

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified\n")

    # Process each file
    fixed_count = 0
    for skill_file in sorted(skill_files):
        if process_skill_file(skill_file, dry_run=args.dry_run):
            fixed_count += 1

    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {fixed_count} out of {len(skill_files)} skills")

    if args.dry_run and fixed_count > 0:
        print("\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
