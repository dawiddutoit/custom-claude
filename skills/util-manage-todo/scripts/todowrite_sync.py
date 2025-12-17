#!/usr/bin/env python3
"""TodoWrite synchronization module.

This module handles synchronization between todo.md files and the TodoWrite tool.
Ensures todo.md remains the single source of truth while keeping TodoWrite in sync.

Core principle: todo.md -> TodoWrite (one-way sync from file to tool)

The sync flow:
1. Parse todo.md file into Todo object
2. Map Todo tasks to TodoWrite format
3. Call TodoWrite with mapped tasks
4. Validate sync by comparing states
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, TypedDict

# Setup: Add .claude to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
if str(_claude_root) not in sys.path:
    sys.path.insert(0, str(_claude_root))

from skill_utils import ensure_path_setup

ensure_path_setup()

# Add scripts directory for sibling imports
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from todo_types import TaskState, Todo


# State mapping: todo.md TaskState -> TodoWrite status (immutable)
_STATE_TO_TODOWRITE_MAP: Final[dict[TaskState, str]] = {
    TaskState.PENDING: "pending",
    TaskState.IN_PROGRESS: "in_progress",
    TaskState.COMPLETED: "completed",
    TaskState.BLOCKED: "pending",  # Blocked maps to pending with blocker note
}

# Reverse mapping: TodoWrite status -> todo.md TaskState (immutable)
_TODOWRITE_TO_STATE_MAP: Final[dict[str, TaskState]] = {
    "pending": TaskState.PENDING,
    "in_progress": TaskState.IN_PROGRESS,
    "completed": TaskState.COMPLETED,
}


def map_state_to_todowrite(state: TaskState) -> str:
    """Map TaskState enum to TodoWrite status string.

    Args:
        state: TaskState enum value

    Returns:
        TodoWrite status string (pending, in_progress, completed)

    Note:
        BLOCKED state maps to "pending" with blocker note added to content
    """
    return _STATE_TO_TODOWRITE_MAP[state]


def map_todowrite_to_state(todowrite_status: str) -> TaskState:
    """Map TodoWrite status string to TaskState enum.

    Args:
        todowrite_status: TodoWrite status (pending, in_progress, completed)

    Returns:
        TaskState enum value
    """
    return _TODOWRITE_TO_STATE_MAP.get(todowrite_status, TaskState.PENDING)


class TodoWriteTask(TypedDict):
    """Task format expected by the TodoWrite tool."""

    content: str
    status: str  # "pending" | "in_progress" | "completed"
    activeForm: str


class TodoWritePayload(TypedDict):
    """Payload format for TodoWrite tool call."""

    todos: list[TodoWriteTask]


# Type alias for TodoWrite callback function
type TodoWriteFunc = Callable[[TodoWritePayload], Any]


def sync_todo_to_todowrite(todo: Todo, todowrite_func: TodoWriteFunc) -> None:
    """Sync todo.md data to TodoWrite tool.

    Args:
        todo: Todo object to sync (source of truth)
        todowrite_func: TodoWrite function to call with task list.
            Should accept a TodoWritePayload dict.

    Side effects:
        - Calls todowrite_func with formatted task list
        - Overwrites TodoWrite state with todo.md state
    """
    todowrite_tasks: list[TodoWriteTask] = []

    for i, task in enumerate(todo.tasks, 1):
        # Map state
        status = map_state_to_todowrite(task.status)

        # Build content
        content = f"Task {i}: {task.title}"

        # Add blocker note for blocked tasks
        if task.status == TaskState.BLOCKED and task.blocker:
            content += f" (BLOCKED: {task.blocker})"

        # Build active form (present continuous)
        active_form = task.title

        todowrite_task = TodoWriteTask(
            content=content,
            status=status,
            activeForm=active_form,
        )
        todowrite_tasks.append(todowrite_task)

    # Call TodoWrite with task list
    todowrite_func(TodoWritePayload(todos=todowrite_tasks))


class CountMismatch(TypedDict):
    """Represents a task count mismatch between todo.md and TodoWrite."""

    type: str  # Always "count_mismatch"
    todo_count: int
    todowrite_count: int


class StateMismatch(TypedDict):
    """Represents a task state mismatch between todo.md and TodoWrite."""

    type: str  # Always "state_mismatch"
    task_index: int
    todo_state: str
    todowrite_state: str


# Union type for mismatch records
type SyncMismatch = CountMismatch | StateMismatch


@dataclass(slots=True)
class SyncReport:
    """Report of synchronization validation.

    Attributes:
        synced: Whether todo.md and TodoWrite are in sync
        total_tasks: Total number of tasks checked
        mismatches: List of mismatches found
    """

    synced: bool
    total_tasks: int
    mismatches: list[SyncMismatch] = field(default_factory=list)

    def get_summary(self) -> str:
        """Get human-readable summary of sync status.

        Returns:
            Summary string describing sync status
        """
        if self.synced:
            return f"Synced: {self.total_tasks} tasks in sync"

        mismatch_count = len(self.mismatches)
        return f"Out of sync: {mismatch_count} mismatches found, total tasks: {self.total_tasks}"


def validate_sync(todo: Todo, todowrite_tasks: list[TodoWriteTask]) -> SyncReport:
    """Validate that todo.md and TodoWrite are in sync.

    Args:
        todo: Todo object (source of truth)
        todowrite_tasks: List of TodoWrite tasks

    Returns:
        SyncReport with validation results

    Checks:
        1. Task count matches
        2. Task states match
    """
    mismatches: list[SyncMismatch] = []
    total_tasks = len(todo.tasks)

    # Check count mismatch
    if len(todo.tasks) != len(todowrite_tasks):
        mismatches.append(
            CountMismatch(
                type="count_mismatch",
                todo_count=len(todo.tasks),
                todowrite_count=len(todowrite_tasks),
            )
        )
        # If counts don't match, can't validate individual tasks
        return SyncReport(synced=False, total_tasks=total_tasks, mismatches=mismatches)

    # Check each task state
    for i, (task, tw_task) in enumerate(zip(todo.tasks, todowrite_tasks, strict=True)):
        todo_state_str = map_state_to_todowrite(task.status)
        tw_state_str = tw_task["status"]

        if todo_state_str != tw_state_str:
            mismatches.append(
                StateMismatch(
                    type="state_mismatch",
                    task_index=i,
                    todo_state=task.status.value,
                    todowrite_state=tw_state_str,
                )
            )

    synced = len(mismatches) == 0
    return SyncReport(synced=synced, total_tasks=total_tasks, mismatches=mismatches)
