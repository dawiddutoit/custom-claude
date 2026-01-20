# Real-World Tool Management Scenarios

Practical examples showing how to manage tools in various situations.

## Scenario 1: Setting Up a New Project

**Situation:** Starting a new Python project from scratch with linting, formatting, and testing.

```bash
# Initialize project
uv init my-project
cd my-project

# Add main dependencies
uv add fastapi uvicorn

# Add development dependencies
uv add --group test pytest pytest-cov pytest-asyncio
uv add --group lint ruff mypy
uv add --group format black isort

# Sync environment
uv sync --all-groups

# Create .gitignore entry for project environment
echo ".venv/" >> .gitignore

# Now ready to work
uv run black src/
uv run ruff check --fix .
uv run mypy src/
uv run pytest tests/
```

**Key points:**
- All tools pinned in `uv.lock` for reproducibility
- Team members get identical versions
- No global tool installation needed
- Each tool invocation uses `uv run`

---

## Scenario 2: Team Working on Existing Project

**Situation:** Three developers working on same project, need identical tooling.

**Repository structure:**
```
my-project/
├── pyproject.toml
├── uv.lock
├── src/
├── tests/
└── .github/workflows/ci.yml
```

**pyproject.toml:**
```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "sqlalchemy>=2.0.0",
]

[dependency-groups]
test = ["pytest>=8.0.0", "pytest-cov>=4.1.0"]
lint = ["ruff>=0.1.0", "mypy>=1.7.0"]
format = ["black>=23.11.0"]
```

**Developer workflow:**
```bash
# Developer 1 clones repo
git clone <repo>
cd my-project

# Get exact same environment as teammates
uv sync --all-groups

# Work and commit
# Edit src/main.py
uv run black src/
uv run ruff check --fix src/
uv run mypy src/
uv run pytest tests/

git add .
git commit -m "Add feature"
git push
```

**CI/CD workflow (GitHub Actions):**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync --all-groups

      - name: Format check
        run: uv run black --check src/

      - name: Lint
        run: uv run ruff check src/

      - name: Type check
        run: uv run mypy src/

      - name: Test
        run: uv run pytest tests/ --cov=src
```

**Result:** All three developers and CI use identical tools and versions.

---

## Scenario 3: One-Off Code Analysis

**Situation:** Need to quickly analyze code with unfamiliar tool without commitment.

```bash
# Developer needs to check code complexity
# Discovers radon tool but never used it

# Try it first via uvx (no installation)
uvx radon cc src/ -a

# Review output
# If useful, install globally for future use
uv tool install radon

# Now can use in any project
cd other-project
radon mi src/

cd third-project
radon cc src/
```

**Benefits:**
- No "tool bloat" in global environment
- Easy to try multiple tools
- Quick decision to keep or discard
- Zero installation overhead for one-time use

---

## Scenario 4: CI/CD Pipeline with Mixed Tools

**Situation:** Pipeline needs linters, formatters, test runners, and doc builders.

```yaml
# .github/workflows/quality.yml
name: Quality Checks

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6

      # Standalone tools via uvx (fast, no overhead)
      - name: Lint with ruff
        run: uvx ruff check .

      - name: Type check with mypy
        run: uvx mypy src/

      - name: Format check with black
        run: uvx black --check .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ['3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync --all-groups
        env:
          UV_PYTHON: ${{ matrix.python }}

      # Project tools via uv run (consistent, locked versions)
      - name: Run tests
        run: uv run pytest tests/ --cov

  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6

      # Tool install if only used once per job
      - name: Build documentation
        run: |
          uv tool install mkdocs
          uv tool install mkdocs-material
          mkdocs build

      # Or via uv run if in project
      # - name: Build artifacts
      #   run: |
      #     uv sync --group artifacts
      #     uv run mkdocs build
```

---

## Scenario 5: Global Tool Management Across Projects

**Situation:** Developer uses specific tools daily across multiple projects.

```bash
# Install frequently-used tools globally
uv tool install ruff
uv tool install black
uv tool install mypy
uv tool install mkdocs
uv tool install pre-commit

# Check what's installed
uv tool list

# Output:
# black           23.11.0  ~/.local/bin/black
# mkdocs          1.5.3    ~/.local/bin/mkdocs
# mypy            1.7.1    ~/.local/bin/mypy
# pre-commit      3.5.0    ~/.local/bin/pre-commit
# ruff            0.3.0    ~/.local/bin/ruff

# Now available everywhere
cd project-a && ruff check .
cd ../project-b && black --check src/
cd ../project-c && mkdocs serve

# Periodic upgrades
uv tool upgrade --all

# Or upgrade specific tool
uv tool upgrade ruff@0.4.0
```

**Trade-offs:**
- Pro: No `uv run` needed, instant execution
- Pro: Single source of truth for tool versions
- Con: Tools version-locked globally (all projects use same)
- Con: Takes disk space (persistent environments)

**Best use:** Tools that don't need to match project requirements (mkdocs, pre-commit, httpie)

---

## Scenario 6: Handling Tool Version Conflicts

**Situation:** Need to use tool with two different versions (e.g., testing compatibility).

```bash
# Problem: ruff 0.3.0 vs 0.4.0 compatibility
# Can't install both globally

# Solution: Use uvx with version specification

# Test with old version
uvx ruff@0.3.0 check .
# Output shows results with 0.3.0

# Test with new version
uvx ruff@0.4.0 check .
# Output shows results with 0.4.0

# Compare findings
# No conflicts, no installation overhead
```

**Script for compatibility testing:**
```bash
#!/bin/bash
# scripts/test-tool-versions.sh

tool="ruff"
versions=("0.3.0" "0.4.0" "0.5.0")

for version in "${versions[@]}"; do
  echo "=== Testing with $tool@$version ==="
  uvx "$tool@$version" check .
  echo ""
done
```

---

## Scenario 7: Complex Tool Setup with Dependencies

**Situation:** mkdocs with multiple plugins for full documentation pipeline.

```bash
# Option 1: Install globally with all dependencies
uv tool install mkdocs
uv tool install mkdocs-material
uv tool install mkdocs-mermaid2

# Then use anywhere
mkdocs serve

# Option 2: Use with uvx for one-time build
uvx --with mkdocs-material --with mkdocs-mermaid2 mkdocs build

# Option 3: Project-local for team consistency
# pyproject.toml
[dependency-groups]
artifacts = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocs-mermaid2>=1.0.0",
    "mkdocs-awesome-pages-plugin>=2.9.0",
]

# Use
uv sync --group artifacts
uv run mkdocs serve
```

**Recommendation:** Use Option 3 for team projects, Option 1 for personal use.

---

## Scenario 8: Python Version-Specific Tool Execution

**Situation:** Need to test code on Python 3.10 minimum, but have Python 3.12 installed.

```bash
# Test on specific Python versions
for version in 3.10 3.11 3.12; do
  echo "Testing on Python $version"
  uvx --python $version pytest tests/
  uvx --python $version mypy src/
done

# Or selective testing
# Old tool only supports Python 3.9
uvx --python 3.9 old-linter src/

# Modern tool requires Python 3.11+
uvx --python 3.11 modern-analyzer src/
```

**In project context:**
```toml
# pyproject.toml
[project]
requires-python = ">=3.11"  # Minimum version for project

# But tool might need to run on older Python for compatibility
```

```bash
# Run project tests
uv run pytest tests/  # Uses Python 3.11+ from project

# Test on minimum supported version
uvx --python 3.11 pytest tests/
```

---

## Scenario 9: Pre-commit Hooks with uv

**Situation:** Team uses pre-commit for automated checks before every commit.

```bash
# Install pre-commit globally
uv tool install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: ruff check
        language: system
        types: [python]

      - id: black
        name: black
        entry: black
        language: system
        types: [python]

      - id: mypy
        name: mypy
        entry: mypy src/
        language: system
        pass_filenames: false
        types: [python]
EOF

# Setup hooks
pre-commit install

# First run
pre-commit run --all-files

# Now runs automatically before every commit
git commit -m "Fix issue"  # pre-commit runs first
```

**Alternative: Pre-commit with uv project tools**
```bash
# Instead of global install
uv sync --group lint
uv sync --group format

# Use project tools in hooks
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: uv run ruff
        language: system
        types: [python]
EOF
```

---

## Scenario 10: Documentation Site with Built-in Serving

**Situation:** Develop documentation locally with live reload, deploy to production.

```bash
# Local development
uv tool install mkdocs
uv tool install mkdocs-material

mkdocs serve
# Navigate to http://localhost:8000
# Edit artifacts, auto-refreshes

# Build for production
mkdocs build
# Output in ./site/

# Deploy
# (rsync, git push, etc.)
```

**Or with project setup:**
```toml
[dependency-groups]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]
```

```bash
# Team setup
uv sync --group artifacts

# Local development (same version as CI)
uv run mkdocs serve

# CI/CD build
uv run mkdocs build
```

---

## Decision Summary for Each Scenario

| Scenario | Method | Rationale |
|----------|--------|-----------|
| New project setup | `uv add --group` + `uv run` | Locked versions, team consistency |
| Team existing project | `uv sync` + `uv run` | One-time setup, reproducible |
| One-off analysis | `uvx` | Try before committing |
| CI/CD pipeline | Mix of `uvx` and `uv run` | Stateless, fast, clean |
| Global daily tools | `uv tool install` | Convenience, no per-project setup |
| Version compatibility testing | `uvx <tool>@<version>` | No conflicts, isolated environments |
| Complex tool setup | `uv run` if team, `uv tool install` if personal | Consistency vs convenience |
| Pre-commit hooks | `uv tool install pre-commit` | Global availability |
| Documentation | `uv tool install mkdocs` or `uv run mkdocs` | Depends on team needs |
| Python version testing | `uvx --python <version>` | Isolated execution per version |
