#!/usr/bin/env python3
"""Todo manager - Core CRUD operations for todo lists.

This module provides functions to create, read, update, and delete todos
and tasks. It handles both in-memory todo objects and markdown file I/O.

All functions use the Todo and Task dataclasses from todo_types module.
"""

from __future__ import annotations

import contextlib
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

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

from todo_types import (
    EMOJI_STATE_MAP,
    STATE_EMOJI_MAP,
    ProgressSummary,
    Task,
    TaskState,
    Todo,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class TodoParseError(ValueError):
    """Raised when parsing a todo markdown file fails."""


class TaskIndexError(IndexError):
    """Raised when a task index is out of range."""


def create_todo(
    title: str,
    date_str: str,
    project: str = "",
    memory: str = "",
    objective: str = "",
) -> Todo:
    """Create a new Todo object.

    Args:
        title: Todo title
        date_str: Date string in YYYY-MM-DD format
        project: Optional project name
        memory: Optional memory identifier
        objective: Optional objective description

    Returns:
        New Todo object

    Raises:
        TodoParseError: If date_str is not in valid YYYY-MM-DD format
    """
    try:
        todo_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        msg = f"Invalid date format: {date_str}. Expected YYYY-MM-DD"
        raise TodoParseError(msg) from e

    return Todo(
        title=title,
        date=todo_date,
        project=project,
        memory=memory,
        objective=objective,
    )


def add_task(
    todo: Todo,
    title: str,
    *,
    status: TaskState = TaskState.PENDING,
    priority: str = "Medium",
    description: str = "",
    assigned: str = "",
    dependencies: Sequence[str] | None = None,
    acceptance_criteria: Sequence[str] | None = None,
    implementation_checklist: Sequence[str] | None = None,
) -> None:
    """Add a task to the todo list.

    Args:
        todo: Todo object to add task to (modified in place)
        title: Task title
        status: Task state (defaults to PENDING)
        priority: Priority level (High | Medium | Low)
        description: Task description
        assigned: Assignee (e.g., @agent-name or person)
        dependencies: List of dependency task titles
        acceptance_criteria: List of acceptance criteria
        implementation_checklist: List of implementation steps
    """
    task = Task(
        title=title,
        status=status,
        priority=priority,
        description=description,
        assigned=assigned,
        dependencies=dependencies or [],
        acceptance_criteria=acceptance_criteria or [],
        implementation_checklist=implementation_checklist or [],
    )
    todo.tasks.append(task)


def update_task_state(
    todo: Todo,
    task_index: int,
    new_state: TaskState,
    blocker: str = "",
) -> None:
    """Update a task's state.

    Args:
        todo: Todo object containing the task (modified in place)
        task_index: Index of task to update (0-based)
        new_state: New state to set
        blocker: Optional blocker description (for BLOCKED state)

    Raises:
        TaskIndexError: If task_index is out of range

    Side effects:
        - Sets started date when transitioning to IN_PROGRESS
        - Sets completed date when transitioning to COMPLETED
        - Sets blocker description when transitioning to BLOCKED
    """
    if task_index < 0 or task_index >= len(todo.tasks):
        msg = f"Task index {task_index} out of range (0-{len(todo.tasks) - 1})"
        raise TaskIndexError(msg)

    task = todo.tasks[task_index]
    task.status = new_state

    # Set started date when moving to IN_PROGRESS
    if new_state == TaskState.IN_PROGRESS and task.started is None:
        task.started = date.today()

    # Set completed date when moving to COMPLETED
    if new_state == TaskState.COMPLETED and task.completed is None:
        task.completed = date.today()

    # Set blocker description when moving to BLOCKED
    if new_state == TaskState.BLOCKED:
        task.blocker = blocker


def remove_task(todo: Todo, task_index: int) -> None:
    """Remove a task from the todo list.

    Args:
        todo: Todo object to remove task from (modified in place)
        task_index: Index of task to remove (0-based)

    Raises:
        TaskIndexError: If task_index is out of range
    """
    if task_index < 0 or task_index >= len(todo.tasks):
        msg = f"Task index {task_index} out of range (0-{len(todo.tasks) - 1})"
        raise TaskIndexError(msg)

    del todo.tasks[task_index]


def get_task_by_index(todo: Todo, task_index: int) -> Task:
    """Get a task by its index.

    Args:
        todo: Todo object containing the task
        task_index: Index of task to retrieve (0-based)

    Returns:
        Task object

    Raises:
        TaskIndexError: If task_index is out of range
    """
    if task_index < 0 or task_index >= len(todo.tasks):
        msg = f"Task index {task_index} out of range (0-{len(todo.tasks) - 1})"
        raise TaskIndexError(msg)

    return todo.tasks[task_index]


def calculate_progress(todo: Todo) -> ProgressSummary:
    """Calculate progress summary for a todo list.

    Args:
        todo: Todo object to calculate progress for

    Returns:
        ProgressSummary with task counts and completion percentage
    """
    total = len(todo.tasks)
    completed = sum(1 for task in todo.tasks if task.status == TaskState.COMPLETED)
    in_progress = sum(1 for task in todo.tasks if task.status == TaskState.IN_PROGRESS)
    blocked = sum(1 for task in todo.tasks if task.status == TaskState.BLOCKED)
    pending = sum(1 for task in todo.tasks if task.status == TaskState.PENDING)

    return ProgressSummary(
        total_tasks=total,
        completed=completed,
        in_progress=in_progress,
        blocked=blocked,
        pending=pending,
    )


def render_todo_to_markdown(todo: Todo) -> str:
    """Render a Todo object to markdown format.

    Args:
        todo: Todo object to render

    Returns:
        Markdown formatted string
    """
    lines = []

    # Header
    header_prefix = "Refactor:" if todo.adr_reference else "Todo:"
    lines.append(f"# {header_prefix} {todo.title}")
    lines.append(f"Date: {todo.date}")

    # Optional metadata
    if todo.project:
        lines.append(f"Project: {todo.project}")
    if todo.memory:
        lines.append(f"Memory: {todo.memory}")
    if todo.adr_reference:
        lines.append(f"ADR: {todo.adr_reference}")

    lines.append("")

    # Objective
    if todo.objective:
        lines.append("## Objective")
        lines.append(todo.objective)
        lines.append("")

    # Refactor context
    if todo.refactor_context:
        lines.append("## Refactor Context")
        for key, value in todo.refactor_context.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")

    # Tasks
    lines.append("## Tasks")
    lines.append("")

    for i, task in enumerate(todo.tasks, 1):
        emoji = STATE_EMOJI_MAP[task.status]
        state_text = _state_to_text(task.status)

        lines.append(f"### Task {i}: {task.title}")
        lines.append(f"**Status:** {emoji} {state_text}")
        lines.append(f"**Priority:** {task.priority}")

        if task.assigned:
            lines.append(f"**Assigned:** {task.assigned}")
        if task.started:
            lines.append(f"**Started:** {task.started}")
        if task.completed:
            lines.append(f"**Completed:** {task.completed}")

        if task.description:
            lines.append("")
            lines.append("**Description:**")
            lines.append(task.description)

        if task.dependencies:
            lines.append("")
            lines.append("**Dependencies:**")
            for dep in task.dependencies:
                lines.append(f"- {dep}")

        if task.acceptance_criteria:
            lines.append("")
            lines.append("**Acceptance Criteria:**")
            for criterion in task.acceptance_criteria:
                lines.append(f"- [ ] {criterion}")

        if task.implementation_checklist:
            lines.append("")
            lines.append("**Implementation Checklist:**")
            for item in task.implementation_checklist:
                lines.append(f"- [ ] {item}")

        if task.blocker:
            lines.append("")
            lines.append(f"**Blocker:** {task.blocker}")

        lines.append("")

    # Progress summary
    progress = calculate_progress(todo)
    lines.append("## Progress Summary")
    lines.append(f"- Total Tasks: {progress.total_tasks}")
    if progress.total_tasks > 0:
        lines.append(f"- Completed: {progress.completed} ({progress.completion_percentage:.0f}%)")
        if progress.in_progress > 0:
            lines.append(f"- In Progress: {progress.in_progress}")
        if progress.blocked > 0:
            lines.append(f"- Blocked: {progress.blocked}")
        if progress.pending > 0:
            lines.append(f"- Pending: {progress.pending}")

    return "\n".join(lines)


def _state_to_text(state: TaskState) -> str:
    """Convert task state enum to display text.

    Args:
        state: TaskState enum value

    Returns:
        Human-readable state text
    """
    state_text_map = {
        TaskState.PENDING: "Not Started",
        TaskState.IN_PROGRESS: "In Progress",
        TaskState.COMPLETED: "Complete",
        TaskState.BLOCKED: "Blocked",
    }
    return state_text_map[state]


def parse_todo_file(content: str) -> Todo:
    """Parse a markdown todo file into a Todo object.

    Args:
        content: Markdown content to parse

    Returns:
        Todo object

    Raises:
        TodoParseError: If required fields (title, date) are missing
    """
    lines = content.split("\n")

    # Extract title
    title_line = lines[0] if lines else ""
    title_match = re.search(r"^# (?:Todo|Refactor): (.+)$", title_line)
    if not title_match:
        msg = "Missing title in todo file"
        raise TodoParseError(msg)
    title = title_match.group(1).strip()

    # Extract date
    date_match = None
    for line in lines:
        if line.startswith("Date:"):
            date_match = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2})", line)
            break
    if not date_match:
        msg = "Missing date in todo file"
        raise TodoParseError(msg)
    date_str = date_match.group(1)

    # Create todo
    todo = create_todo(title, date_str)

    # Extract optional fields
    for line in lines:
        if line.startswith("Project:"):
            todo.project = line.replace("Project:", "").strip()
        elif line.startswith("Memory:"):
            todo.memory = line.replace("Memory:", "").strip()
        elif line.startswith("ADR:"):
            todo.adr_reference = line.replace("ADR:", "").strip()

    # Extract objective
    objective_lines = []
    in_objective = False
    for line in lines:
        if line.strip() == "## Objective":
            in_objective = True
            continue
        if in_objective:
            if line.strip().startswith("##"):
                break
            if line.strip():
                objective_lines.append(line.strip())
    if objective_lines:
        todo.objective = " ".join(objective_lines)

    # Extract refactor context
    in_refactor_context = False
    for line in lines:
        if line.strip() == "## Refactor Context":
            in_refactor_context = True
            continue
        if in_refactor_context:
            if line.strip().startswith("##"):
                break
            # Parse lines like "- **ADR Reference:** ADR-015"
            context_match = re.match(r"^- \*\*(.+?):\*\* (.+)$", line.strip())
            if context_match:
                key = context_match.group(1)
                value = context_match.group(2)
                todo.refactor_context[key] = value

    # Extract tasks
    in_tasks = False
    current_task = None
    current_section = None

    for line in lines:
        stripped = line.strip()

        # Start of tasks section
        if stripped == "## Tasks":
            in_tasks = True
            continue

        # End of tasks section
        if in_tasks and stripped.startswith("## ") and stripped != "## Tasks":
            in_tasks = False
            if current_task:
                todo.tasks.append(current_task)
                current_task = None  # Reset so we don't add it again after loop
            break

        if not in_tasks:
            continue

        # New task
        task_match = re.match(r"^### Task \d+: (.+)$", stripped)
        if task_match:
            if current_task:
                todo.tasks.append(current_task)
            current_task = Task(title=task_match.group(1))
            current_section = None
            continue

        if current_task is None:
            continue

        # Task fields
        if stripped.startswith("**Status:**"):
            # Extract emoji and parse state
            status_match = re.search(r"\*\*Status:\*\*\s*([🔴🟡🟢⚫])", stripped)
            if status_match:
                emoji = status_match.group(1)
                current_task.status = EMOJI_STATE_MAP.get(emoji, TaskState.PENDING)

        elif stripped.startswith("**Priority:**"):
            priority = stripped.replace("**Priority:**", "").strip()
            current_task.priority = priority

        elif stripped.startswith("**Assigned:**"):
            assigned = stripped.replace("**Assigned:**", "").strip()
            current_task.assigned = assigned

        elif stripped.startswith("**Started:**"):
            date_str = stripped.replace("**Started:**", "").strip()
            with contextlib.suppress(ValueError):
                current_task.started = datetime.strptime(date_str, "%Y-%m-%d").date()

        elif stripped.startswith("**Completed:**"):
            date_str = stripped.replace("**Completed:**", "").strip()
            with contextlib.suppress(ValueError):
                current_task.completed = datetime.strptime(date_str, "%Y-%m-%d").date()

        elif stripped.startswith("**Blocker:**"):
            blocker = stripped.replace("**Blocker:**", "").strip()
            current_task.blocker = blocker

        elif stripped == "**Description:**":
            current_section = "description"

        elif stripped == "**Dependencies:**":
            current_section = "dependencies"

        elif stripped == "**Acceptance Criteria:**":
            current_section = "acceptance_criteria"

        elif stripped == "**Implementation Checklist:**":
            current_section = "implementation_checklist"

        elif stripped.startswith("- ") and current_section:
            item = stripped[2:].strip()
            # Remove checkbox markers
            item = re.sub(r"^\[[ x]\]\s*", "", item)

            if current_section == "dependencies":
                current_task.dependencies.append(item)
            elif current_section == "acceptance_criteria":
                current_task.acceptance_criteria.append(item)
            elif current_section == "implementation_checklist":
                current_task.implementation_checklist.append(item)

        elif current_section == "description" and stripped and not stripped.startswith("**"):
            # Append to description
            if current_task.description:
                current_task.description += " " + stripped
            else:
                current_task.description = stripped

    # Add last task
    if current_task:
        todo.tasks.append(current_task)

    return todo


class TodoManager:
    """Manager class for todo CRUD operations.

    Provides encapsulated access to todo creation, task management, and file operations.
    All methods are static and delegate to module-level functions.

    This class exists primarily for namespace organization and backward compatibility.
    The module-level functions can be used directly for a more functional style.
    """

    @staticmethod
    def create_todo(
        title: str,
        date_str: str,
        project: str = "",
        memory: str = "",
        objective: str = "",
    ) -> Todo:
        """Create a new Todo object.

        Args:
            title: Todo title
            date_str: Date string in YYYY-MM-DD format
            project: Optional project name
            memory: Optional memory identifier
            objective: Optional objective description

        Returns:
            New Todo object

        Raises:
            TodoParseError: If date_str is not in valid YYYY-MM-DD format
        """
        return create_todo(title, date_str, project, memory, objective)

    @staticmethod
    def add_task(
        todo: Todo,
        title: str,
        status: TaskState = TaskState.PENDING,
        priority: str = "Medium",
        description: str = "",
        assigned: str = "",
        dependencies: list[str] | None = None,
        acceptance_criteria: list[str] | None = None,
        implementation_checklist: list[str] | None = None,
    ) -> None:
        """Add a task to the todo list.

        Args:
            todo: Todo object to add task to
            title: Task title
            status: Task state (defaults to PENDING)
            priority: Priority level (High | Medium | Low)
            description: Task description
            assigned: Assignee (e.g., @agent-name or person)
            dependencies: List of dependency task titles
            acceptance_criteria: List of acceptance criteria
            implementation_checklist: List of implementation steps
        """
        return add_task(
            todo,
            title,
            status,
            priority,
            description,
            assigned,
            dependencies,
            acceptance_criteria,
            implementation_checklist,
        )

    @staticmethod
    def update_task_state(
        todo: Todo,
        task_index: int,
        new_state: TaskState,
        blocker: str = "",
    ) -> None:
        """Update a task's state.

        Args:
            todo: Todo object containing the task
            task_index: Index of task to update (0-based)
            new_state: New state to set
            blocker: Optional blocker description

        Raises:
            TaskIndexError: If task_index is out of range
        """
        return update_task_state(todo, task_index, new_state, blocker)

    @staticmethod
    def remove_task(todo: Todo, task_index: int) -> None:
        """Remove a task from the todo list.

        Args:
            todo: Todo object to remove task from
            task_index: Index of task to remove (0-based)

        Raises:
            TaskIndexError: If task_index is out of range
        """
        return remove_task(todo, task_index)

    @staticmethod
    def get_task_by_index(todo: Todo, task_index: int) -> Task:
        """Get a task by its index.

        Args:
            todo: Todo object containing the task
            task_index: Index of task to retrieve (0-based)

        Returns:
            Task object

        Raises:
            TaskIndexError: If task_index is out of range
        """
        return get_task_by_index(todo, task_index)

    @staticmethod
    def calculate_progress(todo: Todo) -> ProgressSummary:
        """Calculate progress summary for a todo list.

        Args:
            todo: Todo object to calculate progress for

        Returns:
            ProgressSummary with task counts and completion percentage
        """
        return calculate_progress(todo)

    @staticmethod
    def render_todo_to_markdown(todo: Todo) -> str:
        """Render a Todo object to markdown format.

        Args:
            todo: Todo object to render

        Returns:
            Markdown formatted string
        """
        return render_todo_to_markdown(todo)

    @staticmethod
    def parse_todo_file(content: str) -> Todo:
        """Parse a markdown todo file into a Todo object.

        Args:
            content: Markdown content to parse

        Returns:
            Todo object

        Raises:
            TodoParseError: If required fields (title, date) are missing
        """
        return parse_todo_file(content)
