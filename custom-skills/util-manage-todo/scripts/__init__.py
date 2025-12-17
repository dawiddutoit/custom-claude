#!/usr/bin/env python3
"""Manage-todo skill scripts for Python automation.

This package provides Python scripts for managing todo.md files programmatically:
- template_loader: Load and fill todo templates
- state_manager: Manage task state transitions
- todo_manager: CRUD operations on todo files
- todowrite_sync: Synchronize with TodoWrite tool
- refactor_validator: Validate refactor/ADR requirements

Dependencies (from pyproject.toml):
- pydantic>=2.9.0 (optional, for validation)
- structlog>=24.4.0 (optional, for logging)
- pyyaml>=6.0 (optional, for YAML parsing)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Setup: Add .claude to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
if str(_claude_root) not in sys.path:
    sys.path.insert(0, str(_claude_root))

from skill_utils import ensure_path_setup

ensure_path_setup()

__all__ = [
    "refactor_validator",
    "state_manager",
    "template_loader",
    "todo_manager",
    "todowrite_sync",
]
