#!/usr/bin/env python3
"""
Remove invalid TODO comments about <example> blocks from skill descriptions.

The <example> block pattern is NOT part of the official Agent Skills specification.
This script removes TODO comments that instruct adding example blocks.
"""

import sys
from pathlib import Path


def remove_example_todos(skill_path: Path, dry_run: bool = False) -> bool:
    """Remove TODO comments about example blocks from SKILL.md."""
    try:
        content = skill_path.read_text(encoding='utf-8')

        # Check if file has the TODO comment
        todo_pattern = "  # TODO: Add <example> block to description"
        if todo_pattern not in content:
            return False  # No changes needed

        # Remove the TODO line
        new_content = content.replace(todo_pattern + "\n", "")

        if new_content == content:
            return False  # No changes made

        if dry_run:
            print(f"[DRY RUN] Would fix: {skill_path.relative_to('.')}")
            return True

        # Write back
        skill_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Fixed: {skill_path.relative_to('.')}")
        return True

    except Exception as e:
        print(f"❌ Error processing {skill_path}: {e}", file=sys.stderr)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove invalid TODO comments about <example> blocks from skills"
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
        if remove_example_todos(skill_file, dry_run=args.dry_run):
            fixed_count += 1

    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {fixed_count} out of {len(skill_files)} skills")

    if args.dry_run and fixed_count > 0:
        print("\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
