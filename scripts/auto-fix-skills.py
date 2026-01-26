#!/usr/bin/env python3
"""
Auto-fix common skill validation issues.

Automatically fixes:
1. Numbered section headings (## 1. Section -> ## Section)
2. Empty directories (scripts/, examples/, templates/)
3. Adds TODO comments for missing WHAT statements (action verbs)

Usage:
    python auto-fix-skills.py --dry-run ~/.claude/skills/skill-name
    python auto-fix-skills.py --all --backup
    python auto-fix-skills.py ~/.claude/skills/skill-name --backup
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FixStats:
    """Statistics for a single fix type."""

    fixed_count: int = 0
    skill_names: tuple[str, ...] = ()

    def add(self, skill_name: str) -> "FixStats":
        """Return new stats with added skill."""
        return FixStats(
            fixed_count=self.fixed_count + 1,
            skill_names=self.skill_names + (skill_name,),
        )


@dataclass
class FixResult:
    """Results from fixing a single skill."""

    skill_name: str
    fixes_applied: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    directories_removed: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Check if any fixes were applied."""
        return bool(self.fixes_applied or self.directories_removed)


@dataclass
class SummaryStats:
    """Summary statistics across all skills."""

    numbered_sections: FixStats = field(default_factory=FixStats)
    empty_directories: FixStats = field(default_factory=FixStats)
    what_warnings: FixStats = field(default_factory=FixStats)
    context_warnings: FixStats = field(default_factory=FixStats)
    total_skills: int = 0
    total_changes: int = 0


# Action verbs that indicate a WHAT statement
ACTION_VERBS = (
    "creates",
    "manages",
    "validates",
    "analyzes",
    "implements",
    "configures",
    "provides",
    "enables",
    "supports",
    "handles",
    "processes",
    "generates",
    "builds",
    "detects",
    "enforces",
    "automates",
    "orchestrates",
    "guides",
    "adds",
)

# Directories to check for emptiness
EMPTY_DIR_CANDIDATES = ("scripts", "examples", "templates")


def parse_yaml_frontmatter(content: str) -> tuple[dict[str, str] | None, int, int]:
    """Extract YAML frontmatter from SKILL.md content.

    Returns:
        Tuple of (yaml_dict or None, start_line, end_line)
    """
    yaml_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not yaml_match:
        return None, 0, 0

    yaml_text = yaml_match.group(1)

    # Simple YAML parsing for description field
    result: dict[str, str] = {}
    current_key = None
    current_value_lines: list[str] = []

    for line in yaml_text.split("\n"):
        # Check for new key
        key_match = re.match(r"^([a-z-]+):\s*(.*)$", line)
        if key_match:
            # Save previous key if exists
            if current_key:
                result[current_key] = "\n".join(current_value_lines).strip()

            current_key = key_match.group(1)
            value = key_match.group(2).strip()
            if value == "|":
                current_value_lines = []
            else:
                current_value_lines = [value]
        elif current_key and line.startswith("  "):
            # Continuation of multi-line value
            current_value_lines.append(line.strip())

    # Save last key
    if current_key:
        result[current_key] = "\n".join(current_value_lines).strip()

    # Calculate line numbers
    yaml_start = 1  # After first ---
    yaml_end = content[: yaml_match.end()].count("\n") + 1

    return result, yaml_start, yaml_end


def fix_numbered_sections(content: str) -> tuple[str, list[str]]:
    """Remove numbered prefixes from section headings.

    Pattern: ## 1. Section -> ## Section

    Returns:
        Tuple of (fixed_content, list of fixes applied)
    """
    fixes: list[str] = []

    # Pattern matches: ## 1. Section or ## 2. Another Section
    pattern = re.compile(r"^(##\s+)\d+\.\s+(.+)$", re.MULTILINE)

    def replace_numbered(match: re.Match[str]) -> str:
        original = match.group(0)
        fixed = f"{match.group(1)}{match.group(2)}"
        fixes.append(f"'{original}' -> '{fixed}'")
        return fixed

    fixed_content = pattern.sub(replace_numbered, content)

    return fixed_content, fixes


def check_missing_what(description: str) -> bool:
    """Check if description is missing a WHAT statement.

    WHAT statement should start with an action verb.
    """
    if not description:
        return True

    description_lower = description.lower()

    # Check if any action verb appears in the description
    for verb in ACTION_VERBS:
        if verb in description_lower:
            return False

    return True


def add_yaml_todo_comment(
    content: str,
    yaml_end_line: int,
    missing_what: bool,
) -> tuple[str, list[str]]:
    """Add TODO comments to YAML frontmatter for missing WHAT (action verbs).

    Returns:
        Tuple of (modified_content, list of warnings added)
    """
    warnings: list[str] = []
    lines = content.split("\n")

    # Find the description field end (before the closing ---)
    yaml_end_idx = 0
    for i, line in enumerate(lines):
        if line == "---" and i > 0:
            yaml_end_idx = i
            break

    # Check if TODO comment already exists
    yaml_section = "\n".join(lines[:yaml_end_idx])
    has_what_todo = "TODO: Add action verb" in yaml_section

    todos_to_add: list[str] = []

    if missing_what and not has_what_todo:
        todos_to_add.append(
            "  # TODO: Add action verb to description "
            "(creates, manages, validates, analyzes, implements, configures, etc.)"
        )
        warnings.append("Added TODO: Missing WHAT statement (action verb)")

    if not todos_to_add:
        return content, warnings

    # Insert TODOs before the closing ---
    new_lines = lines[:yaml_end_idx] + todos_to_add + lines[yaml_end_idx:]

    return "\n".join(new_lines), warnings


def remove_empty_directories(skill_path: Path, dry_run: bool) -> list[str]:
    """Remove empty subdirectories.

    Returns:
        List of removed directory names
    """
    removed: list[str] = []

    for dir_name in EMPTY_DIR_CANDIDATES:
        dir_path = skill_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # Check if truly empty (no files, including hidden)
            contents = list(dir_path.iterdir())
            if not contents:
                if not dry_run:
                    dir_path.rmdir()
                removed.append(dir_name)

    return removed


def fix_skill(
    skill_path: Path,
    dry_run: bool = False,
    backup: bool = False,
) -> FixResult:
    """Fix all issues in a single skill.

    Args:
        skill_path: Path to skill directory
        dry_run: If True, don't make changes
        backup: If True, create .bak files before modifying

    Returns:
        FixResult with all fixes and warnings
    """
    result = FixResult(skill_name=skill_path.name)
    skill_md_path = skill_path / "SKILL.md"

    if not skill_md_path.exists():
        result.errors.append("SKILL.md not found")
        return result

    # Read content
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        result.errors.append(f"Failed to read SKILL.md: {e}")
        return result

    original_content = content

    # Fix 1: Remove numbered section headings
    content, numbered_fixes = fix_numbered_sections(content)
    if numbered_fixes:
        result.fixes_applied.append(f"Removed numbered sections ({len(numbered_fixes)} headings)")

    # Parse YAML for description checks
    yaml_data, yaml_start, yaml_end = parse_yaml_frontmatter(content)

    if yaml_data:
        description = yaml_data.get("description", "")

        # Check for missing WHAT (action verbs)
        missing_what = check_missing_what(description)

        # Fix 2: Add TODO comment for missing WHAT if needed
        if missing_what:
            content, todo_warnings = add_yaml_todo_comment(
                content, yaml_end, missing_what
            )
            result.warnings.extend(todo_warnings)

    # Write changes if any
    if content != original_content:
        if not dry_run:
            if backup:
                backup_path = skill_md_path.with_suffix(".md.bak")
                shutil.copy2(skill_md_path, backup_path)

            skill_md_path.write_text(content, encoding="utf-8")

    # Fix 4: Remove empty directories
    removed_dirs = remove_empty_directories(skill_path, dry_run)
    result.directories_removed = removed_dirs
    if removed_dirs:
        result.fixes_applied.append(f"Removed empty directories: {', '.join(removed_dirs)}")

    return result


def fix_all_skills(
    skills_dir: Path,
    dry_run: bool = False,
    backup: bool = False,
    verbose: bool = False,
) -> tuple[list[FixResult], SummaryStats]:
    """Fix all skills in a directory.

    Args:
        skills_dir: Path to skills directory
        dry_run: If True, don't make changes
        backup: If True, create .bak files before modifying
        verbose: If True, print progress for each skill

    Returns:
        Tuple of (list of FixResult, SummaryStats)
    """
    results: list[FixResult] = []
    stats = SummaryStats()

    skill_dirs = sorted(
        [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )

    print(f"{'[DRY RUN] ' if dry_run else ''}Auto-fixing skills...\n")

    for i, skill_dir in enumerate(skill_dirs, 1):
        result = fix_skill(skill_dir, dry_run=dry_run, backup=backup)
        results.append(result)

        # Update stats
        stats.total_skills += 1

        if result.fixes_applied:
            for fix in result.fixes_applied:
                stats.total_changes += 1
                if "numbered sections" in fix.lower():
                    stats.numbered_sections = stats.numbered_sections.add(result.skill_name)
                if "empty directories" in fix.lower():
                    stats.empty_directories = stats.empty_directories.add(result.skill_name)

        for warning in result.warnings:
            if "WHAT" in warning:
                stats.what_warnings = stats.what_warnings.add(result.skill_name)
            if "CONTEXT" in warning:
                stats.context_warnings = stats.context_warnings.add(result.skill_name)

        # Print progress
        if verbose or result.has_changes:
            status_icon = "  " if not result.has_changes else "  "
            print(f"[{i}/{len(skill_dirs)}] {result.skill_name}")

            for fix in result.fixes_applied:
                print(f"  [FIXED] {fix}")

            for warning in result.warnings:
                print(f"  [WARNING] {warning}")

            for error in result.errors:
                print(f"  [ERROR] {error}")

            if result.has_changes:
                print()

    return results, stats


def print_summary(stats: SummaryStats, dry_run: bool = False) -> None:
    """Print summary of all fixes."""
    print("\n" + "=" * 60)
    print(f"{'[DRY RUN] ' if dry_run else ''}Summary")
    print("=" * 60)

    print(f"\n  Numbered sections fixed: {stats.numbered_sections.fixed_count} skills")
    if stats.numbered_sections.skill_names:
        for name in stats.numbered_sections.skill_names[:5]:
            print(f"    - {name}")
        if len(stats.numbered_sections.skill_names) > 5:
            print(f"    ... and {len(stats.numbered_sections.skill_names) - 5} more")

    print(f"\n  Empty directories removed: {stats.empty_directories.fixed_count} skills")
    if stats.empty_directories.skill_names:
        for name in stats.empty_directories.skill_names[:5]:
            print(f"    - {name}")
        if len(stats.empty_directories.skill_names) > 5:
            print(f"    ... and {len(stats.empty_directories.skill_names) - 5} more")

    print(f"\n  WHAT warnings added: {stats.what_warnings.fixed_count} skills")
    if stats.what_warnings.skill_names:
        for name in stats.what_warnings.skill_names[:5]:
            print(f"    - {name}")
        if len(stats.what_warnings.skill_names) > 5:
            print(f"    ... and {len(stats.what_warnings.skill_names) - 5} more")

    print(f"\n  CONTEXT warnings added: {stats.context_warnings.fixed_count} skills")
    if stats.context_warnings.skill_names:
        for name in stats.context_warnings.skill_names[:5]:
            print(f"    - {name}")
        if len(stats.context_warnings.skill_names) > 5:
            print(f"    ... and {len(stats.context_warnings.skill_names) - 5} more")

    print(f"\n  Total skills processed: {stats.total_skills}")
    print(f"  Total changes made: {stats.total_changes}")
    print()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-fix common skill validation issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry-run on single skill (preview changes)
    python auto-fix-skills.py --dry-run ~/.claude/skills/skill-name

    # Fix all skills with backup
    python auto-fix-skills.py --all --backup

    # Fix single skill
    python auto-fix-skills.py ~/.claude/skills/skill-name

    # Fix all skills in custom directory
    python auto-fix-skills.py --all --skills-dir /path/to/skills
""",
    )
    parser.add_argument("skill_path", nargs="?", help="Path to skill directory")
    parser.add_argument("--all", action="store_true", help="Fix all skills")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create .bak files before modifying",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all skills, not just those with changes",
    )
    parser.add_argument(
        "--skills-dir",
        default=str(Path(__file__).parent.parent / "skills"),
        help="Skills directory (default: ../skills relative to script)",
    )

    args = parser.parse_args()

    if args.all:
        skills_dir = Path(args.skills_dir).expanduser()
        if not skills_dir.exists():
            print(f"Error: Skills directory not found: {skills_dir}")
            return 1

        results, stats = fix_all_skills(
            skills_dir,
            dry_run=args.dry_run,
            backup=args.backup,
            verbose=args.verbose,
        )
        print_summary(stats, dry_run=args.dry_run)

    elif args.skill_path:
        skill_path = Path(args.skill_path).expanduser()
        if not skill_path.exists():
            print(f"Error: Skill not found: {skill_path}")
            return 1

        result = fix_skill(skill_path, dry_run=args.dry_run, backup=args.backup)

        print(f"{'[DRY RUN] ' if args.dry_run else ''}Fixing skill: {result.skill_name}\n")

        if result.fixes_applied:
            print("Fixes applied:")
            for fix in result.fixes_applied:
                print(f"  [FIXED] {fix}")

        if result.warnings:
            print("\nWarnings added:")
            for warning in result.warnings:
                print(f"  [WARNING] {warning}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  [ERROR] {error}")

        if not result.has_changes and not result.warnings:
            print("  No issues found.")

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
