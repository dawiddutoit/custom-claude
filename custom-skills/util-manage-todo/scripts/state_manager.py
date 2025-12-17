#!/usr/bin/env python3
"""Task state management and validation for manage-todo skill.

This module provides functions to validate state transitions, map states to emojis,
and parse task details from markdown format.

Note: This module uses string literals for states rather than the TaskState enum
from todo_types.py. This is intentional for backward compatibility with existing
markdown parsing code. Consider migrating to use todo_types.TaskState for new code.

Example usage:
    # Validate a state transition
    is_valid = validate_state_transition("not_started", "in_progress")

    # Get emoji for state
    emoji = format_state_emoji("in_progress")  # Returns "🟡"

    # Parse task from markdown
    task = parse_task_from_markdown(markdown_text)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final, Literal, TypedDict

# Setup: Add .claude to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
if str(_claude_root) not in sys.path:
    sys.path.insert(0, str(_claude_root))

from skill_utils import ensure_path_setup

ensure_path_setup()


# Type aliases for state management
type TaskState = Literal["not_started", "in_progress", "completed", "blocked"]
type StateEmoji = Literal["🔴", "🟡", "🟢", "⚫"]

# Valid state transitions mapping (immutable reference)
_STATE_TRANSITIONS: Final[dict[TaskState, list[TaskState]]] = {
    "not_started": ["in_progress", "blocked", "not_started"],
    "in_progress": ["completed", "blocked", "not_started", "in_progress"],
    "completed": ["in_progress", "completed"],
    "blocked": ["in_progress", "not_started", "blocked"],
}

# State to emoji mapping (immutable reference)
_STATE_TO_EMOJI: Final[dict[TaskState, StateEmoji]] = {
    "not_started": "🔴",
    "in_progress": "🟡",
    "completed": "🟢",
    "blocked": "⚫",
}

# Emoji to state mapping (immutable reference)
_EMOJI_TO_STATE: Final[dict[StateEmoji, TaskState]] = {
    "🔴": "not_started",
    "🟡": "in_progress",
    "🟢": "completed",
    "⚫": "blocked",
}


def validate_state_transition(current_state: TaskState, new_state: TaskState) -> bool:
    """Validate if state transition is allowed.

    Valid transitions per reference.md:
    - not_started → in_progress, blocked
    - in_progress → completed, blocked, not_started
    - completed → in_progress
    - blocked → in_progress, not_started

    Args:
        current_state: Current task state
        new_state: Desired new task state

    Returns:
        True if transition is valid, False otherwise

    Example:
        >>> validate_state_transition("not_started", "in_progress")
        True
        >>> validate_state_transition("not_started", "completed")
        False
    """
    if current_state not in _STATE_TRANSITIONS:
        return False

    return new_state in _STATE_TRANSITIONS[current_state]


def format_state_emoji(state: TaskState) -> StateEmoji:
    """Map task state to emoji.

    Mapping:
    - not_started → 🔴
    - in_progress → 🟡
    - completed → 🟢
    - blocked → ⚫

    Args:
        state: Task state to convert

    Returns:
        Emoji representing the state

    Example:
        >>> format_state_emoji("in_progress")
        "🟡"
    """
    return _STATE_TO_EMOJI[state]


def parse_state_from_emoji(emoji: StateEmoji) -> TaskState:
    """Parse task state from emoji (reverse of format_state_emoji).

    Args:
        emoji: Emoji to convert to state

    Returns:
        Task state corresponding to emoji

    Example:
        >>> parse_state_from_emoji("🟡")
        "in_progress"
    """
    return _EMOJI_TO_STATE[emoji]


def _extract_title(lines: list[str]) -> str | None:
    """Extract title from markdown heading."""
    for line in lines:
        if line.startswith("###"):
            return line.replace("###", "").strip()
    return None


def _extract_status(lines: list[str]) -> TaskState | None:
    """Extract status from **Status:** line."""
    status_pattern = r"\*\*Status:\*\*\s+(🔴|🟡|🟢|⚫)"
    for line in lines:
        match = re.search(status_pattern, line)
        if match:
            emoji = match.group(1)
            return parse_state_from_emoji(emoji)  # type: ignore
    return None


def _extract_priority(lines: list[str]) -> str | None:
    """Extract priority from **Priority:** line."""
    priority_pattern = r"\*\*Priority:\*\*\s+(\w+)"
    for line in lines:
        match = re.search(priority_pattern, line)
        if match:
            return match.group(1)
    return None


def _extract_dependencies(lines: list[str]) -> list[str]:
    """Extract dependencies from **Dependencies:** line."""
    dep_pattern = r"\*\*Dependencies:\*\*\s+(.+)"
    for line in lines:
        match = re.search(dep_pattern, line)
        if match:
            deps_text = match.group(1)
            return [d.strip() for d in deps_text.split(",")]
    return []


def _extract_description(lines: list[str]) -> str | None:
    """Extract description from **Description:** section."""
    desc_start = -1
    for i, line in enumerate(lines):
        if "**Description:**" in line:
            desc_start = i + 1
            break

    if desc_start <= 0:
        return None

    desc_lines = []
    for i in range(desc_start, len(lines)):
        line = lines[i]
        # Stop at next section
        if line.startswith("**") and line.endswith("**"):
            break
        if line.strip():
            desc_lines.append(line.strip())

    if desc_lines:
        return "\n".join(desc_lines)
    return None


def _extract_acceptance_criteria(lines: list[str]) -> list[str]:
    """Extract acceptance criteria from **Acceptance Criteria:** section."""
    ac_start = -1
    for i, line in enumerate(lines):
        if "**Acceptance Criteria:**" in line:
            ac_start = i + 1
            break

    if ac_start <= 0:
        return []

    criteria = []
    for i in range(ac_start, len(lines)):
        line = lines[i].strip()
        # Look for checklist items
        if line.startswith(("- [ ]", "- [x]")):
            # Extract text after checkbox
            criterion = line[5:].strip()
            criteria.append(criterion)
        # Stop at next section or end of checklist
        elif line.startswith("**") and not line.startswith("- "):
            break

    return criteria


class ParsedTask(TypedDict):
    """Type definition for parsed task data from markdown."""

    title: str | None
    status: TaskState | None
    priority: str | None
    description: str | None
    acceptance_criteria: list[str]
    dependencies: list[str]


def parse_task_from_markdown(markdown_text: str) -> ParsedTask:
    """Extract task details from markdown section.

    Parses a markdown task section and extracts:
    - title: Task title from heading
    - status: Task state (parsed from emoji)
    - priority: Priority level (if present)
    - description: Task description (if present)
    - acceptance_criteria: List of acceptance criteria items
    - dependencies: List of dependency references

    Args:
        markdown_text: Markdown text containing task details

    Returns:
        ParsedTask TypedDict with extracted task details

    Example:
        >>> markdown = '''### Task 1: Implementation
        ... **Status:** 🔴 Not Started
        ... **Priority:** High
        ... '''
        >>> task = parse_task_from_markdown(markdown)
        >>> task["title"]
        "Task 1: Implementation"
    """
    lines = markdown_text.strip().split("\n")

    return ParsedTask(
        title=_extract_title(lines),
        status=_extract_status(lines),
        priority=_extract_priority(lines),
        description=_extract_description(lines),
        acceptance_criteria=_extract_acceptance_criteria(lines),
        dependencies=_extract_dependencies(lines),
    )


class StateManager:
    """Manager class for task state operations.

    Provides encapsulated access to state validation, formatting, and parsing functions.
    All methods are static and delegate to module-level functions.
    """

    @staticmethod
    def validate_state_transition(current_state: TaskState, new_state: TaskState) -> bool:
        """Validate if state transition is allowed.

        Args:
            current_state: Current task state
            new_state: Desired new task state

        Returns:
            True if transition is valid, False otherwise
        """
        return validate_state_transition(current_state, new_state)

    @staticmethod
    def format_state_emoji(state: TaskState) -> StateEmoji:
        """Map task state to emoji.

        Args:
            state: Task state to convert

        Returns:
            Emoji representing the state
        """
        return format_state_emoji(state)

    @staticmethod
    def parse_state_from_emoji(emoji: StateEmoji) -> TaskState:
        """Parse task state from emoji.

        Args:
            emoji: Emoji to convert to state

        Returns:
            Task state corresponding to emoji
        """
        return parse_state_from_emoji(emoji)

    @staticmethod
    def parse_task_from_markdown(markdown_text: str) -> ParsedTask:
        """Extract task details from markdown section.

        Args:
            markdown_text: Markdown text containing task details

        Returns:
            ParsedTask TypedDict with extracted task details
        """
        return parse_task_from_markdown(markdown_text)
