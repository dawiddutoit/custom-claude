#!/usr/bin/env python3
"""Refactor/migration ADR validation module.

This module validates that refactor and migration work has an associated ADR
document before allowing todo creation. Enforces project policy: all refactors
require ADRs.

Critical rule: No refactor/migration work without an ADR document.

The validation flow:
1. Check task description for refactor-related keywords
2. If keywords found, require an ADR reference
3. Verify the referenced ADR file exists in the ADR directory
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final, TypedDict

# Setup: Add .claude to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
if str(_claude_root) not in sys.path:
    sys.path.insert(0, str(_claude_root))

from skill_utils import ensure_path_setup

ensure_path_setup()


# Refactor keywords that trigger ADR requirement (immutable)
REFACTOR_KEYWORDS: Final[list[str]] = [
    "refactor",
    "migrate",
    "migration",
    "convert",
    "conversion",
    "breaking change",
    "multi-file",
    "system-wide",
    "deprecate",
    "adopt pattern",
]


def detect_refactor_keywords(text: str) -> bool:
    """Detect if text contains refactor-related keywords.

    Args:
        text: Text to search for refactor keywords

    Returns:
        True if refactor keywords detected, False otherwise
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in REFACTOR_KEYWORDS)


def find_adr_files(
    adr_dir: Path,
    adr_ref: str | None = None,
    topic: str | None = None,
) -> list[Path]:
    """Find ADR files matching reference or topic.

    Args:
        adr_dir: Directory containing ADR files (e.g., docs/adr/)
        adr_ref: ADR reference (e.g., "ADR-015")
        topic: Topic keyword to search in filenames

    Returns:
        List of matching ADR file paths

    Raises:
        ValueError: If neither adr_ref nor topic provided
    """
    if not adr_ref and not topic:
        msg = "Either adr_ref or topic must be provided"
        raise ValueError(msg)

    results = []

    # Search by ADR number
    if adr_ref:
        # Extract number from ADR-XXX format
        match = re.search(r"ADR-(\d+)", adr_ref, re.IGNORECASE)
        if match:
            adr_number = match.group(1)
            # Search in all subdirectories
            seen_paths = set()
            for subdir in ["not_started", "in_progress", "implemented", "."]:
                search_dir = adr_dir / subdir if subdir != "." else adr_dir
                pattern = f"{adr_number}-*.md"
                matches = list(search_dir.glob(pattern))
                for match in matches:
                    path_str = str(match)
                    if path_str not in seen_paths:
                        results.append(match)
                        seen_paths.add(path_str)

    # Search by topic keyword
    if topic and not results:
        topic_lower = topic.lower()
        # Search all markdown files
        for md_file in adr_dir.rglob("*.md"):
            if topic_lower in md_file.name.lower():
                results.append(md_file)

    return results


class ValidationResult(TypedDict):
    """Result of ADR validation check."""

    valid: bool
    message: str
    refactor_detected: bool
    adr_file: str | None


def validate_adr_exists(
    task_description: str,
    adr_ref: str | None,
    adr_dir: Path,
) -> ValidationResult:
    """Validate that ADR exists for refactor/migration work.

    Args:
        task_description: Task description to check for refactor keywords
        adr_ref: ADR reference if provided (e.g., "ADR-015")
        adr_dir: Directory containing ADR files

    Returns:
        ValidationResult TypedDict with keys:
            - valid: Whether validation passed
            - message: Human-readable validation message
            - refactor_detected: Whether refactor keywords found
            - adr_file: Path to ADR file if found, None otherwise

    Validation logic:
        1. If no refactor keywords -> validation passes (no ADR needed)
        2. If refactor keywords but no ADR ref -> validation fails
        3. If refactor keywords and ADR ref but file not found -> validation fails
        4. If refactor keywords and ADR file found -> validation passes
    """
    # Check for refactor keywords
    is_refactor = detect_refactor_keywords(task_description)

    # No refactor work detected -> no ADR needed -> validation passes
    if not is_refactor:
        return ValidationResult(
            valid=True,
            message="No refactor work detected. ADR not required.",
            refactor_detected=False,
            adr_file=None,
        )

    # Refactor work detected -> ADR required
    # Check if ADR reference provided
    if not adr_ref:
        return ValidationResult(
            valid=False,
            message=(
                "Refactor/migration work requires an ADR document. "
                "No ADR reference provided. "
                "Please create an ADR or provide ADR reference."
            ),
            refactor_detected=True,
            adr_file=None,
        )

    # Search for ADR file
    adr_files = find_adr_files(adr_dir=adr_dir, adr_ref=adr_ref)

    if not adr_files:
        return ValidationResult(
            valid=False,
            message=(
                f"Refactor/migration work requires an ADR document. "
                f"ADR reference '{adr_ref}' provided but file not found in {adr_dir}. "
                f"Please create the ADR document first."
            ),
            refactor_detected=True,
            adr_file=None,
        )

    # ADR file found -> validation passes
    adr_file = adr_files[0]  # Use first match
    return ValidationResult(
        valid=True,
        message=f"Refactor work detected. ADR found: {adr_file.name}. Validation passed.",
        refactor_detected=True,
        adr_file=str(adr_file),
    )
