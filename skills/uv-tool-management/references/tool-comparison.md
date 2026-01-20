# Tool Execution Methods: uvx vs uv tool vs uv run

## Quick Decision Matrix

```
Question 1: How often will I use this tool?
├─ Once or rarely → UVEX
└─ Regularly/daily → Step 2

Question 2: Do I use it across multiple projects?
├─ No, only in this project → UVX or UV RUN
│  └─ Does it need access to project code/libs?
│     ├─ Yes (pytest, ruff on project) → UV RUN
│     └─ No (standalone utility) → UVX
│
└─ Yes, multiple projects → UVX or UV TOOL INSTALL
   └─ Is it a standalone utility?
      ├─ Yes (httpie, mkdocs) → UV TOOL INSTALL
      └─ No (language server, plugin) → Consider context
```

## Detailed Comparison

### uvx (Ephemeral Execution)

**What it does:**
- Runs a CLI tool in an isolated environment
- Tool is fetched and cached locally
- Environment is created on-demand
- No modification to system PATH or global state
- Each invocation ensures correct dependencies

**Pros:**
- Zero installation footprint
- No system pollution
- Automatic dependency resolution
- Easy to try tools before committing
- Perfect for CI/CD (stateless)
- No version conflicts with other tools
- Caching means repeat runs are fast

**Cons:**
- Slight delay first time (fetches + caches)
- Can't easily customize tool environment
- Not suitable for interactive tools requiring setup

**When to use:**
```bash
# Try before you buy
uvx httpie https://httpbin.org/get

# One-off analysis
uvx ruff check --statistics .

# CI/CD workflows
uvx pytest tests/

# Cross-project comparison (different versions)
uvx ruff@0.3.0 check .
cd other-project
uvx ruff@0.4.0 check .
```

**Command patterns:**
```bash
# Basic
uvx <tool> <args>

# Specify version
uvx <tool>@<version> <args>
uvx --from '<tool>>=<min>,<max>' <tool> <args>

# Different package name
uvx --from <package> <command> <args>

# With extras
uvx --from '<tool>[extra]' <tool> <args>

# Additional dependencies
uvx --with <package> <tool> <args>

# Specific Python version
uvx --python <version> <tool> <args>

# From git
uvx --from 'git+<url>' <tool> <args>
```

---

### uv tool install (Persistent Installation)

**What it does:**
- Installs tool globally in isolated environment
- Creates symlink in `~/.local/bin/` (Unix) or `%PATH%` (Windows)
- Tool becomes available in shell PATH
- Persists across shell sessions
- One install, many uses

**Pros:**
- No installation delay on use
- Tool immediately available in PATH
- Single command for all invocations
- Familiar experience (like old pipx)
- Suitable for team documentation
- Great for tools used daily

**Cons:**
- Takes disk space (persistent environment)
- Updates require explicit upgrade
- Tool versions are system-global
- Different projects might need different versions
- Can create PATH conflicts (rare)

**When to use:**
```bash
# Tools you use every day
uv tool install ruff
ruff check .

# Team standard tools
uv tool install black
black --check src/

# Development utilities
uv tool install mkdocs
mkdocs serve

# Cross-project analysis
uv tool install pre-commit
# Use in every project
```

**Command patterns:**
```bash
# Install
uv tool install <tool>
uv tool install <tool>@<version>
uv tool install '<tool>[extra]'

# List
uv tool list

# Upgrade
uv tool upgrade <tool>
uv tool upgrade --all

# Uninstall
uv tool uninstall <tool>

# Run after install
<tool> <args>
```

---

### uv run (Project Environment)

**What it does:**
- Runs command in project's virtual environment
- Uses project's `pyproject.toml` and `uv.lock`
- All project dependencies available
- Tool inherits project's Python version
- Project-scoped execution

**Pros:**
- Tool sees all project dependencies
- Uses exact locked versions (reproducible)
- Works for testing, linting, formatting code
- Perfect for team consistency
- Integrated with project workflow
- No global state required

**Cons:**
- Only works in project directory (with pyproject.toml)
- Requires `uv sync` setup
- Tools must be in dev dependencies or groups
- Not suitable for tools not needing project access

**When to use:**
```bash
# Run tests (need project modules)
uv run pytest tests/

# Lint project code (consistent versions)
uv run ruff check .

# Format project code (locked version)
uv run black src/

# Type check project (sees all types)
uv run mypy src/

# Run project-specific scripts
uv run python scripts/setup.py
```

**Command patterns:**
```bash
# Run command in project env
uv run <command> <args>

# Run Python script
uv run python <script.py>

# Run module
uv run python -m <module>

# With project setup
uv sync --all-groups
uv run <tool>
```

---

## Scenario Examples

### Scenario 1: Trying New Linter

**Situation:** Heard about `flake8`, want to test it on code

**Best choice:** `uvx`

```bash
# Try without installing
uvx flake8 .

# Review output
# If you like it:
# Install for regular use
uv tool install flake8
```

**Why:** No commitment, instant feedback, no system changes

---

### Scenario 2: Regular Project Linting

**Situation:** Team uses ruff daily on project code

**Best choice:** `uv run` (with dev dependency)

```toml
# pyproject.toml
[dependency-groups]
lint = ["ruff>=0.1.0"]
```

```bash
# Sync and run
uv sync --group lint
uv run ruff check .
```

**Why:** Locked version, reproducible, team-consistent, project-local

---

### Scenario 3: Multi-Project Code Formatting

**Situation:** Same black config for 10 projects

**Best choice:** `uv tool install`

```bash
# Install once
uv tool install black

# Use everywhere
cd project-a && black src/
cd project-b && black src/
```

**Why:** Convenience, consistency across projects, no setup per project

---

### Scenario 4: CI/CD Pipeline

**Situation:** GitHub Actions needs ruff, mypy, pytest

**Best choice:** Mix of `uvx` and `uv run`

```yaml
# .github/workflows/ci.yml
- name: Lint
  run: uvx ruff check .              # Standalone tool

- name: Type check
  run: uvx mypy src/                 # Standalone tool

- name: Test
  run: |                             # Needs project
    uv sync --group test
    uv run pytest tests/
```

**Why:** Stateless, fast, no installation side effects, clean logs

---

### Scenario 5: Tool With Conflicting Dependencies

**Situation:** Need to use tool-a (deps: lib v1.0) and tool-b (deps: lib v2.0)

**Best choice:** `uvx` for both

```bash
# Each runs in isolated environment
uvx tool-a analyze code
uvx tool-b analyze code

# No version conflict
```

**Why:** Isolation by design, no dependency hell

---

### Scenario 6: Complex Tool Setup

**Situation:** mkdocs with material theme, plugins, custom config

**Best choice:** `uv tool install` or `uv run` (depending on frequency)

```bash
# For daily development
uv tool install 'mkdocs[material]'
mkdocs serve

# OR in project for team consistency
[dependency-groups]
artifacts = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]

uv sync --group artifacts
uv run mkdocs serve
```

**Why:** Tool setup persists, but team consistency if in project

---

## Edge Cases

### Case 1: Tool Needs Specific Python Version

```bash
# Tool only works on Python 3.10
# But you have Python 3.12 installed

# Use uvx to specify version
uvx --python 3.10 old-tool

# Or install specific Python + tool
uv python install 3.10
uv tool install old-tool
# Then need to specify which Python when running
```

### Case 2: Tool Not in PyPI

```bash
# Tool on GitHub
uvx --from 'git+https://github.com/user/tool' tool-command

# Or install from git
uv tool install 'git+https://github.com/user/tool'
```

### Case 3: Tool is Actually a Module

```bash
# httpie installs 'http' command, but package is 'httpie'
uvx --from httpie http https://example.com

# Or install and use
uv tool install httpie
http https://example.com
```

### Case 4: Tool Needs Project Context But Not Dev Dependency

```bash
# Custom script using project libraries
# Don't want to add pytest, but need project installed

uv sync --no-dev              # Install only main dependencies
uv run python scripts/analyze.py
```

---

## Performance Comparison

| Operation | uvx | uv tool run | uv run |
|-----------|-----|-----------|--------|
| First run (cold) | ~2-3s | N/A | ~1s |
| Subsequent run (cached) | ~0.5s | ~0.1s | ~0.3s |
| Installation overhead | None | ~5-10s | ~1s |
| Disk space | Shared cache | Persistent env | Project .venv |
| Update required | None | Manual `uv tool upgrade` | `uv lock --upgrade` |

---

## Troubleshooting

### Tool Not Found in uvx

```bash
# Command works but tool not found
uvx ruff check .
# Error: ruff not found

# Solution: Package name != command name
uvx --from <package> <command>

# Example: ruffle is tool, but command might be different
uvx --from ruffle ruffle check .
```

### Tool Doesn't See Project

```bash
# Using uvx but tool needs project dependencies
uvx pytest tests/
# Error: Module not found

# Solution: Use uv run instead
uv run pytest tests/
```

### Version Conflicts

```bash
# Tool A needs lib v1.0, Tool B needs lib v2.0
# Using uv tool install for both

# Solution: Use uvx to isolate
uvx tool-a
uvx tool-b
```

### Tool Not in PATH After Install

```bash
# Installed tool but can't run it
uv tool install ruff
ruff --version
# Command not found

# Solution: Restart shell or source PATH
exec $SHELL
ruff --version
```

---

## Team Guidance

### Project Setup (pyproject.toml)

```toml
[dependency-groups]
# Tools for project-specific work
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
]
lint = [
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
format = [
    "black>=23.11.0",
]
docs = [
    "mkdocs>=1.5.0",
]
```

### Team README

```markdown
## Development Setup

# Install development dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Format code
uv run black src/

# Build docs
uv run mkdocs serve
```

### Global Tool Installation (optional team standard)

```bash
# For tools used across projects
uv tool install ruff
uv tool install black
uv tool install mypy

# Document in team wiki
```

---

## Decision Tree for Code

```python
def choose_execution_method(tool: str, context: str) -> str:
    """Recommend execution method for a tool."""

    # Is it a project-scoped operation?
    if context == "testing" or context == "linting_own_code":
        return "uv run (with dev dependency)"

    # Does it need to run across projects?
    if context == "daily_development":
        # Is it a standalone utility?
        if is_standalone_utility(tool):
            return "uv tool install"
        else:
            return "uv run (per project)"

    # Is this a one-time or experimental operation?
    if context == "trying" or context == "ci_pipeline":
        return "uvx"

    # Is team consistency critical?
    if context == "team_workflow":
        return "uv run (with dev dependency)"

    # Default: ephemeral is safest
    return "uvx"
```
