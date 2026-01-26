#!/usr/bin/env python3
"""
Fix skill descriptions to start with third-person action verbs.

Converts imperative verbs to third-person and removes TODO comments.
"""

import re
import sys
from pathlib import Path
from typing import Tuple, Optional


# Imperative to third-person verb conversions
VERB_CONVERSIONS = {
    'add': 'adds',
    'analyze': 'analyzes',
    'apply': 'applies',
    'automate': 'automates',
    'build': 'builds',
    'capture': 'captures',
    'configure': 'configures',
    'create': 'creates',
    'debug': 'debugs',
    'design': 'designs',
    'detect': 'detects',
    'develop': 'develops',
    'diagnose': 'diagnoses',
    'document': 'documents',
    'enable': 'enables',
    'execute': 'executes',
    'export': 'exports',
    'extract': 'extracts',
    'fix': 'fixes',
    'generate': 'generates',
    'guide': 'guides',
    'handle': 'handles',
    'help': 'helps',
    'identify': 'identifies',
    'implement': 'implements',
    'integrate': 'integrates',
    'manage': 'manages',
    'monitor': 'monitors',
    'optimize': 'optimizes',
    'organize': 'organizes',
    'perform': 'performs',
    'process': 'processes',
    'provide': 'provides',
    'record': 'records',
    'refactor': 'refactors',
    'resolve': 'resolves',
    'run': 'runs',
    'set up': 'sets up',
    'setup': 'sets up',
    'test': 'tests',
    'track': 'tracks',
    'troubleshoot': 'troubleshoots',
    'update': 'updates',
    'validate': 'validates',
    'verify': 'verifies',
}

# Third-person verbs that are already correct
THIRD_PERSON_VERBS = set(VERB_CONVERSIONS.values())


def extract_description(content: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """Extract description field from YAML frontmatter."""
    # Find description field
    pattern = r'(description:\s*[|]?\s*\n?\s*["\']?)(.*?)(["\']?\n(?:[a-z-]+:|\s*#|---|\n---))'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None, None, None

    prefix = match.group(1)
    desc = match.group(2).strip()
    suffix = match.group(3)

    start_pos = match.start(2)
    end_pos = match.end(2)

    return desc, start_pos, end_pos


def needs_verb_fix(desc: str) -> bool:
    """Check if description needs an action verb fix."""
    words = desc.strip().split()
    if not words:
        return False

    first_word = words[0].lower()

    # Check if it already starts with third-person verb
    if first_word in THIRD_PERSON_VERBS:
        return False

    # Check if entire phrase matches
    first_phrase = ' '.join(words[:2]).lower() if len(words) >= 2 else first_word
    if first_phrase in THIRD_PERSON_VERBS:
        return False

    return True


def fix_description_verb(desc: str) -> str:
    """Convert imperative verb to third-person in description."""
    words = desc.split()
    if not words:
        return desc

    first_word = words[0].lower()

    # Check two-word phrases first (like "set up")
    if len(words) >= 2:
        first_phrase = f"{first_word} {words[1].lower()}"
        if first_phrase in VERB_CONVERSIONS:
            # Replace two-word phrase
            words[0] = VERB_CONVERSIONS[first_phrase].split()[0].capitalize()
            words[1] = VERB_CONVERSIONS[first_phrase].split()[1]
            result = ' '.join(words)
            # Fix compound verbs (e.g., "and configure" -> "and configures")
            result = fix_compound_verbs(result)
            return result

    # Check single word
    if first_word in VERB_CONVERSIONS:
        # Preserve capitalization of original first word
        if words[0][0].isupper():
            words[0] = VERB_CONVERSIONS[first_word].capitalize()
        else:
            words[0] = VERB_CONVERSIONS[first_word]
        result = ' '.join(words)
        # Fix compound verbs
        result = fix_compound_verbs(result)
        return result

    # Special cases: starts with adjective/noun instead of verb
    # Add "Provides" prefix for these
    if first_word in ['comprehensive', 'systematic', 'complete', 'detailed', 'advanced']:
        return f"Provides {desc}"

    # If starts with "Guide for", change to "Guides"
    if desc.lower().startswith('guide for'):
        return desc.replace('Guide for', 'Guides for', 1).replace('guide for', 'Guides for', 1)

    return desc


def fix_compound_verbs(text: str) -> str:
    """Fix compound verb phrases like 'and implement', 'and configure', etc."""
    for imperative, third_person in VERB_CONVERSIONS.items():
        # Pattern: "and <imperative verb>" -> "and <third person verb>"
        pattern = rf'\band {re.escape(imperative)}\b'
        replacement = f'and {third_person}'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Pattern: "or <imperative verb>" -> "or <third person verb>"
        pattern = rf'\bor {re.escape(imperative)}\b'
        replacement = f'or {third_person}'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def process_skill_file(skill_path: Path, dry_run: bool = False) -> bool:
    """Process a single SKILL.md file to fix action verbs."""
    try:
        content = skill_path.read_text(encoding='utf-8')

        # Check if file has the TODO comment
        todo_pattern = "  # TODO: Add action verb to description (creates, manages, validates, analyzes, implements, configures, etc.)"
        if todo_pattern not in content:
            return False  # No changes needed

        # Extract description
        desc, start_pos, end_pos = extract_description(content)
        if desc is None:
            print(f"⚠️  Could not extract description: {skill_path.relative_to('.')}", file=sys.stderr)
            return False

        # Check if description needs fixing
        needs_fix = needs_verb_fix(desc)

        # Fix description if needed
        new_desc = fix_description_verb(desc) if needs_fix else desc

        # Replace description in content
        new_content = content[:start_pos] + new_desc + content[end_pos:]

        # Remove TODO comment
        new_content = new_content.replace(todo_pattern + "\n", "")

        if new_content == content:
            return False  # No changes made

        if dry_run:
            skill_name = skill_path.parent.name
            if needs_fix:
                print(f"[DRY RUN] Would fix: {skill_name}")
                print(f"  OLD: {desc[:80]}...")
                print(f"  NEW: {new_desc[:80]}...")
            else:
                print(f"[DRY RUN] Would remove TODO: {skill_name}")
            return True

        # Write back
        skill_path.write_text(new_content, encoding='utf-8')

        skill_name = skill_path.parent.name
        if needs_fix:
            print(f"✅ Fixed: {skill_name}")
        else:
            print(f"✅ Removed TODO: {skill_name}")
        return True

    except Exception as e:
        print(f"❌ Error processing {skill_path}: {e}", file=sys.stderr)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix action verbs in skill descriptions"
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

    # Find all SKILL.md files with the TODO
    todo_pattern = "# TODO: Add action verb to description"
    skill_files = []
    for skill_file in skills_dir.glob("*/SKILL.md"):
        content = skill_file.read_text()
        if todo_pattern in content:
            skill_files.append(skill_file)

    if not skill_files:
        print("No SKILL.md files found with action verb TODO", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(skill_files)} skill files with action verb TODO")

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
