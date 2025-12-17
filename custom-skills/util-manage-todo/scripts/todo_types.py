#!/usr/bin/env python3
"""Type definitions for manage-todo skill.

This module defines the data structures used for todo management including
tasks, todos, and state enums.

All dataclasses use slots=True for memory efficiency and follow immutability
principles where practical. Task and Todo are mutable to support in-place updates.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Final

# Setup: Add .claude to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
if str(_claude_root) not in sys.path:
    sys.path.insert(0, str(_claude_root))

from skill_utils import ensure_path_setup

ensure_path_setup()


class TaskState(str, Enum):
    """Task state enumeration matching todo.md emoji conventions.

    States:
        PENDING: Not yet started (displayed as red circle)
        IN_PROGRESS: Currently being worked on (displayed as yellow circle)
        COMPLETED: Finished (displayed as green circle)
        BLOCKED: Cannot proceed due to blocker (displayed as black circle)
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


# Type alias for priority levels
type Priority = str  # "High" | "Medium" | "Low"

# Emoji mapping for display (immutable)
STATE_EMOJI_MAP: Final[dict[TaskState, str]] = {
    TaskState.PENDING: "🔴",
    TaskState.IN_PROGRESS: "🟡",
    TaskState.COMPLETED: "🟢",
    TaskState.BLOCKED: "⚫",
}

# Reverse mapping for parsing (immutable)
EMOJI_STATE_MAP: Final[dict[str, TaskState]] = {
    emoji: state for state, emoji in STATE_EMOJI_MAP.items()
}


@dataclass(slots=True)
class Task:
    """Represents a single task in a todo list.

    Attributes:
        title: The task title/name
        status: Current task state (PENDING, IN_PROGRESS, COMPLETED, BLOCKED)
        priority: Priority level (High, Medium, Low)
        description: Detailed task description
        assigned: Who is assigned to this task (e.g., @agent-name)
        dependencies: List of tasks this depends on
        acceptance_criteria: Conditions for task completion
        implementation_checklist: Steps to implement
        started: Date when work began
        completed: Date when task was finished
        blocker: Description of what is blocking progress
    """

    title: str
    status: TaskState = TaskState.PENDING
    priority: Priority = "Medium"
    description: str = ""
    assigned: str = ""
    dependencies: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    implementation_checklist: list[str] = field(default_factory=list)
    started: date | None = None
    completed: date | None = None
    blocker: str = ""


@dataclass(slots=True)
class Todo:
    """Represents a complete todo list.

    Attributes:
        title: Todo list title
        date: Creation date
        project: Associated project name
        memory: Memory identifier for persistence
        objective: High-level goal description
        tasks: List of tasks in this todo
        adr_reference: Associated ADR document (e.g., "ADR-015")
        refactor_context: Additional context for refactor work
    """

    title: str
    date: date
    project: str = ""
    memory: str = ""
    objective: str = ""
    tasks: list[Task] = field(default_factory=list)
    adr_reference: str = ""
    refactor_context: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProgressSummary:
    """Immutable summary of progress across all tasks.

    This is a frozen dataclass since progress summaries are computed
    values that should not be modified after creation.

    Attributes:
        total_tasks: Total number of tasks
        completed: Number of completed tasks
        in_progress: Number of tasks in progress
        blocked: Number of blocked tasks
        pending: Number of pending tasks
    """

    total_tasks: int
    completed: int
    in_progress: int
    blocked: int
    pending: int

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage.

        Returns:
            Percentage of tasks completed (0.0-100.0).
            Returns 0.0 if there are no tasks.
        """
        if self.total_tasks == 0:
            return 0.0
        return (self.completed / self.total_tasks) * 100
