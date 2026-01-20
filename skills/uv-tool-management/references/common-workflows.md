# Common uv Tool Workflows

Ready-to-use command patterns for typical scenarios.

## Code Quality Tools

### Running ruff (Linter)

```bash
# One-time check
uvx ruff check .

# Project-specific with team consistency
uv sync --group lint
uv run ruff check .

# Fix issues
uv run ruff check --fix .

# Check with detailed output
uv run ruff check --statistics .
```

### Running black (Formatter)

```bash
# Check formatting without changes
uvx black --check src/

# Format code
uv run black src/

# Check specific file
uv run black --check src/main.py
```

### Running mypy (Type Checker)

```bash
# Quick type check
uvx mypy src/

# With project context (better)
uv sync --group lint
uv run mypy src/

# Strict mode
uv run mypy --strict src/
```

### Running pylint

```bash
# As standalone tool
uvx pylint src/

# Or with project context
uv run pylint src/
```

---

## Testing and Coverage

### Running pytest

```bash
# Setup and run tests
uv sync --group test
uv run pytest tests/

# Run with coverage
uv run pytest --cov=src tests/

# Run specific test file
uv run pytest tests/test_auth.py

# Run test matching pattern
uv run pytest tests/ -k "test_login"

# Run with verbose output
uv run pytest -v tests/
```

### Running specific Python version tests

```bash
# Test with Python 3.10
uvx --python 3.10 pytest tests/

# Test with Python 3.12
uvx --python 3.12 pytest tests/

# Run matrix of Python versions
for version in 3.10 3.11 3.12; do
  echo "Testing on Python $version"
  uvx --python $version pytest tests/
done
```

---

## Documentation

### Building with mkdocs

```bash
# Install globally if used frequently
uv tool install mkdocs

# Then use anywhere
mkdocs serve
mkdocs build

# OR run per-project
uv sync --group artifacts
uv run mkdocs serve
```

### With material theme

```bash
# Install with theme
uv tool install 'mkdocs[material]'
# OR
uv tool install mkdocs
uv tool install mkdocs-material

# Use
mkdocs serve

# OR via uvx with theme
uvx --with mkdocs-material mkdocs serve
```

---

## CLI Tools and Utilities

### HTTP Testing with httpie

```bash
# One-time usage
uvx httpie https://api.github.com/users/github

# Or with http alias
uvx --from httpie http https://api.github.com/repos/astral-sh/uv

# With authentication
uvx --from httpie http --auth user:pass https://example.com/api
```

### JSON Manipulation with jq

```bash
# Use jq via uvx
curl -s https://api.github.com/users/github | uvx jq '.repos_url'
```

### Pre-commit Hooks

```bash
# Install globally
uv tool install pre-commit

# Setup
pre-commit install
pre-commit run --all-files

# OR per-project
uv sync --group dev
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## CI/CD Workflows

### GitHub Actions

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6

      - name: Set up Python
        run: uv python install

      # Option 1: Standalone tools via uvx
      - name: Lint with ruff
        run: uvx ruff check .

      - name: Type check with mypy
        run: uvx mypy src/

      - name: Format check with black
        run: uvx black --check .

      # Option 2: Project tools via uv run
      - name: Run tests
        run: |
          uv sync --group test
          uv run pytest tests/

      # Option 3: Global tool install
      - name: Lint docs
        run: |
          uv tool install markdownlint-cli2
          markdownlint-cli2 "docs/**/*.md"
```

### GitLab CI

```yaml
lint:
  image: python:3.12
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.cargo/bin:$PATH"
  script:
    # Via uvx
    - uv run python -m ruff check .
    - uv run python -m mypy src/

    # Via uv run
    - uv sync --group test
    - uv run pytest tests/
```

### LocalCI/Dev Scripts

```bash
#!/bin/bash
# scripts/check.sh - Run all quality checks

set -e

echo "Running linter..."
uvx ruff check .

echo "Type checking..."
uvx mypy src/

echo "Format check..."
uvx black --check .

echo "Tests..."
uv sync --group test
uv run pytest tests/ --cov

echo "All checks passed!"
```

---

## Development Environment Setup

### Project with Multiple Dependency Groups

```toml
# pyproject.toml

[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "httpx>=0.27.0",
]

[dependency-groups]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
]
lint = [
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
format = [
    "black>=23.11.0",
    "isort>=5.13.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]
dev = [
    "pre-commit>=3.5.0",
    "ipython>=8.17.0",
]
```

```bash
# Install everything
uv sync --all-groups

# Install specific groups
uv sync --group test --group lint

# Install for production only
uv sync --no-dev

# Run specific tools
uv run pytest tests/
uv run ruff check .
uv run black src/
uv run mypy src/
uv run mkdocs serve
```

---

## Advanced Patterns

### Running Tool with Multiple Versions

```bash
# Test tool compatibility
for version in 0.3.0 0.4.0 0.5.0; do
  echo "Testing ruff $version"
  uvx ruff@$version check .
done
```

### Tool with Custom Python Version

```bash
# Old tool needs Python 3.9
uvx --python 3.9 legacy-tool analyze code

# Modern tool on Python 3.12
uvx --python 3.12 modern-tool process data
```

### Combining Tools in Pipeline

```bash
# Format code, then lint it
uv run black src/
uv run ruff check --fix src/

# Or in pipeline
uv run black src/ && uv run ruff check src/
```

### Tool Requiring Additional Dependencies

```bash
# mkdocs with material theme
uvx --with mkdocs-material mkdocs serve

# OR install persistently
uv tool install mkdocs
uv tool install mkdocs-material

# Then use
mkdocs serve
```

---

## Troubleshooting Workflows

### "Command not found" with uvx

```bash
# Problem: uvx tool <args>
# Error: command not found

# Solution 1: Check tool package name
uvx --from httpie http https://example.com
# (tool is 'httpie', command is 'http')

# Solution 2: Install instead
uv tool install <tool>
<tool> <args>
```

### Tool Needs Project Context

```bash
# Problem: Tool can't find project modules
uvx pytest tests/
# Error: ModuleNotFoundError

# Solution: Use uv run
uv sync --group test
uv run pytest tests/
```

### Tool Version Mismatch in Team

```bash
# Problem: Different developers have different versions

# Solution: Add to project dev dependencies
[dependency-groups]
lint = ["ruff==0.3.0"]  # Pinned version

# Everyone syncs same version
uv sync --group lint
uv run ruff check .
```

### Tool Takes Long to Start

```bash
# Problem: First uvx execution slow

# Solution: Use uv tool install for frequently used tools
uv tool install ruff
# Now runs instantly
ruff check .

# Keep uvx for rarely used tools
uvx rarely-used-tool
```

---

## Best Practices Checklist

```bash
# Before committing code:

# 1. Format code
uv run black src/

# 2. Lint code
uv run ruff check --fix .

# 3. Type check
uv run mypy src/

# 4. Run tests
uv run pytest tests/ --cov

# 5. Check documentation
# uv run mkdocs build
```

```bash
# Maintenance commands:

# Update all installed tools
uv tool upgrade --all

# Clean up cache
uv cache prune

# List installed tools
uv tool list

# Check for tool updates
uv tool list  # Shows current versions
```

---

## Command Reference Quick Index

| Tool | Purpose | Command |
|------|---------|---------|
| **ruff** | Lint Python | `uv run ruff check .` |
| **black** | Format Python | `uv run black src/` |
| **mypy** | Type check | `uv run mypy src/` |
| **pytest** | Test | `uv run pytest tests/` |
| **mkdocs** | Docs | `uv tool install mkdocs` then `mkdocs serve` |
| **httpie** | HTTP client | `uvx --from httpie http https://example.com` |
| **pre-commit** | Git hooks | `uv tool install pre-commit` then `pre-commit run` |
| **sqlfluff** | SQL lint | `uvx sqlfluff lint sql/` |
| **pylint** | Lint | `uv run pylint src/` |
| **coverage** | Coverage | `uv run pytest --cov=src tests/` |
