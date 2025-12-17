#!/usr/bin/env python3
"""Skill Packager - Creates a distributable .skill file from a skill folder.

Packages a skill directory into a compressed .skill archive (zip format)
after validating the skill structure.

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]

Examples:
    python package_skill.py skills/public/my-skill
    python package_skill.py skills/public/my-skill ./dist
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from quick_validate import validate_skill

if TYPE_CHECKING:
    pass


class PackageError(Exception):
    """Error during skill packaging."""

    pass


def _validate_skill_path(skill_path: Path) -> None:
    """Validate the skill path exists and is a directory.

    Args:
        skill_path: Resolved path to validate.

    Raises:
        PackageError: If path doesn't exist or isn't a directory.
    """
    if not skill_path.exists():
        raise PackageError(f"Skill folder not found: {skill_path}")

    if not skill_path.is_dir():
        raise PackageError(f"Path is not a directory: {skill_path}")

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise PackageError(f"SKILL.md not found in {skill_path}")


def _create_output_directory(output_dir: str | Path | None) -> Path:
    """Create and return the output directory path.

    Args:
        output_dir: Optional output directory path.

    Returns:
        Resolved path to output directory.
    """
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    return Path.cwd()


def _create_skill_archive(
    skill_path: Path,
    output_file: Path,
) -> list[str]:
    """Create the .skill zip archive.

    Args:
        skill_path: Path to the skill directory.
        output_file: Path for the output .skill file.

    Returns:
        List of files added to the archive.

    Raises:
        PackageError: If archive creation fails.
    """
    added_files: list[str] = []

    try:
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    added_files.append(str(arcname))
    except OSError as e:
        raise PackageError(f"Failed to create archive: {e}") from e

    return added_files


def package_skill(
    skill_path: str | Path,
    output_dir: str | Path | None = None,
) -> Path | None:
    """Package a skill folder into a .skill file.

    Validates the skill structure, then creates a compressed archive
    containing all skill files.

    Args:
        skill_path: Path to the skill folder.
        output_dir: Optional output directory for the .skill file
            (defaults to current directory).

    Returns:
        Path to the created .skill file, or None if error.
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder
    try:
        _validate_skill_path(skill_path)
    except PackageError as e:
        print(f"Error: {e}")
        return None

    # Run validation before packaging
    print("Validating skill...")
    result = validate_skill(skill_path)
    if not result.valid:
        print(f"Validation failed: {result.message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"OK: {result.message}\n")

    # Determine output location
    output_path = _create_output_directory(output_dir)
    skill_filename = output_path / f"{skill_path.name}.skill"

    # Create the .skill file
    try:
        added_files = _create_skill_archive(skill_path, skill_filename)
        for file in added_files:
            print(f"  Added: {file}")
        print(f"\nSuccessfully packaged skill to: {skill_filename}")
        return skill_filename
    except PackageError as e:
        print(f"Error: {e}")
        return None


def main() -> int:
    """Main entry point for CLI usage.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < 2:
        print(
            "Usage: python package_skill.py <path/to/skill-folder> [output-directory]"
        )
        print("\nExamples:")
        print("  python package_skill.py skills/public/my-skill")
        print("  python package_skill.py skills/public/my-skill ./dist")
        return 1

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
