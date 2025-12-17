# Quality Gate Tools by Ecosystem

Complete reference of quality gate tools organized by programming language and ecosystem.

## Python

### Type Checking

**pyright** (Recommended)
```bash
uv run pyright
# Fast, accurate, good error messages
# Config: pyproject.toml [tool.pyright]
```

**mypy**
```bash
uv run mypy src/
# Industry standard, strict typing
# Config: mypy.ini or pyproject.toml
```

**ty** (Experimental)
```bash
uv run ty check -q --exit-zero src/
# Next-gen type checker, very fast
# Still in beta
```

### Linting

**ruff** (Recommended)
```bash
uv run ruff check src/ tests/
# Extremely fast, replaces flake8/isort/etc
# Config: pyproject.toml [tool.ruff]
```

**pylint**
```bash
uv run pylint src/
# Comprehensive linting, slower
# Config: .pylintrc or pyproject.toml
```

**flake8**
```bash
uv run flake8 src/
# Classic linter, many plugins
# Config: .flake8 or setup.cfg
```

### Dead Code Detection

**vulture** (Recommended)
```bash
uv run vulture src/ --min-confidence 80
# Fast, accurate dead code detection
# Adjustable confidence threshold
```

**autoflake**
```bash
uv run autoflake --check --remove-unused-variables src/
# Removes unused imports/variables
# Can fix automatically
```

### Testing

**pytest** (Recommended)
```bash
uv run pytest tests/ -q
# Most popular Python test framework
# Config: pytest.ini or pyproject.toml
```

**unittest**
```bash
python -m unittest discover tests/
# Built-in Python test framework
# No external dependencies
```

### Formatting

**ruff format** (Recommended)
```bash
uv run ruff format --check src/ tests/
# Black-compatible, extremely fast
# Config: pyproject.toml [tool.ruff.format]
```

**black**
```bash
uv run black --check src/
# Opinionated formatter, no config
# Industry standard
```

### Security

**bandit**
```bash
uv run bandit -r src/
# Finds common security issues
# Config: .bandit or pyproject.toml
```

**safety**
```bash
uv run safety check
# Checks dependencies for vulnerabilities
# Requires requirements.txt or lockfile
```

## JavaScript/TypeScript

### Type Checking

**tsc** (TypeScript Compiler)
```bash
npx tsc --noEmit
# Official TypeScript type checker
# Config: tsconfig.json
```

**flow**
```bash
npx flow check
# Facebook's type checker
# Config: .flowconfig
```

### Linting

**eslint** (Recommended)
```bash
npx eslint src/
# Most popular JS/TS linter
# Config: .eslintrc.js or package.json
```

**biome**
```bash
npx @biomejs/biome check src/
# Fast linter and formatter (Rust-based)
# Config: biome.json
```

### Testing

**jest** (Recommended)
```bash
npm test
# or: npx jest
# Most popular React/Node test framework
# Config: jest.config.js or package.json
```

**vitest**
```bash
npx vitest run
# Vite-native testing, extremely fast
# Config: vite.config.ts
```

**mocha + chai**
```bash
npx mocha tests/
# Classic Node.js test framework
# Config: .mocharc.js
```

### Formatting

**prettier** (Recommended)
```bash
npx prettier --check src/
# Opinionated formatter
# Config: .prettierrc.js or package.json
```

**biome format**
```bash
npx @biomejs/biome format src/
# Fast formatter (part of biome)
```

## Go

### Type Checking / Building

**go build**
```bash
go build ./...
# Compiles and type-checks all packages
# No config needed
```

### Linting

**golangci-lint** (Recommended)
```bash
golangci-lint run
# Fast linter aggregator (runs many linters)
# Config: .golangci.yml
```

**staticcheck**
```bash
staticcheck ./...
# Advanced static analysis
# No config needed
```

### Testing

**go test**
```bash
go test ./... -v
# Built-in test framework
# No config needed
```

**go test with race detector**
```bash
go test -race ./...
# Detects race conditions
# Slower but catches concurrency bugs
```

### Formatting

**go fmt**
```bash
go fmt ./...
# Official formatter
# No config needed
```

**goimports**
```bash
goimports -w .
# Formats and manages imports
# No config needed
```

## Rust

### Type Checking / Building

**cargo check**
```bash
cargo check
# Fast type checking without building
# Config: Cargo.toml
```

**cargo build**
```bash
cargo build
# Full compilation
# Config: Cargo.toml
```

### Linting

**cargo clippy** (Recommended)
```bash
cargo clippy -- -D warnings
# Official linter with helpful suggestions
# Config: clippy.toml
```

### Testing

**cargo test**
```bash
cargo test
# Built-in test framework
# Config: Cargo.toml
```

**cargo nextest**
```bash
cargo nextest run
# Next-gen test runner (faster)
# Requires installation
```

### Formatting

**cargo fmt**
```bash
cargo fmt --check
# Official formatter (rustfmt)
# Config: rustfmt.toml
```

## Ruby

### Type Checking

**sorbet**
```bash
bundle exec srb tc
# Gradual type checker for Ruby
# Config: sorbet/config
```

**steep**
```bash
bundle exec steep check
# Ruby type checker using RBS
# Config: Steepfile
```

### Linting

**rubocop** (Recommended)
```bash
bundle exec rubocop
# Most popular Ruby linter
# Config: .rubocop.yml
```

### Testing

**rspec**
```bash
bundle exec rspec
# Most popular Ruby test framework
# Config: .rspec
```

**minitest**
```bash
bundle exec rake test
# Built-in Rails test framework
# Config: test_helper.rb
```

### Formatting

**rubocop with auto-correct**
```bash
bundle exec rubocop --auto-correct-all
# Can fix formatting automatically
```

## Java

### Type Checking / Building

**javac** (Java Compiler)
```bash
javac -Xlint:all src/**/*.java
# Built-in compiler with warnings
```

**maven compile**
```bash
mvn compile
# Maven build system
# Config: pom.xml
```

**gradle build**
```bash
./gradlew build
# Gradle build system
# Config: build.gradle
```

### Linting

**checkstyle**
```bash
mvn checkstyle:check
# Style checker
# Config: checkstyle.xml
```

**spotbugs**
```bash
mvn spotbugs:check
# Bug pattern detector
# Config: spotbugs.xml
```

**pmd**
```bash
mvn pmd:check
# Source code analyzer
# Config: pmd.xml
```

### Testing

**junit**
```bash
mvn test
# Standard Java test framework
# Config: pom.xml
```

**testng**
```bash
mvn testng:test
# Alternative test framework
# Config: testng.xml
```

### Formatting

**google-java-format**
```bash
java -jar google-java-format.jar --set-exit-if-changed src/
# Google's Java formatter
```

## C/C++

### Type Checking / Building

**gcc/g++**
```bash
gcc -Wall -Wextra -Werror *.c
# GNU compiler with warnings
```

**clang**
```bash
clang -Wall -Wextra -Werror *.c
# LLVM compiler with warnings
```

### Linting

**clang-tidy**
```bash
clang-tidy src/*.cpp
# Linter and static analyzer
# Config: .clang-tidy
```

**cppcheck**
```bash
cppcheck --enable=all src/
# Static analyzer for C/C++
# Config: cppcheck.xml
```

### Testing

**googletest**
```bash
./test_binary
# Google's C++ test framework
# Config: CMakeLists.txt
```

**catch2**
```bash
./test_binary
# Modern C++ test framework
```

### Formatting

**clang-format**
```bash
clang-format --dry-run --Werror src/*
# LLVM formatter
# Config: .clang-format
```

## Shell Scripts

### Linting

**shellcheck** (Recommended)
```bash
shellcheck *.sh
# Shell script linter
# Detects common issues
```

### Testing

**bats**
```bash
bats test/
# Bash Automated Testing System
```

**shunit2**
```bash
./test_script.sh
# Unit testing for shell scripts
```

### Formatting

**shfmt**
```bash
shfmt -d .
# Shell script formatter
# Config: .editorconfig
```

## Docker

### Linting

**hadolint**
```bash
hadolint Dockerfile
# Dockerfile linter
# Checks best practices
```

**docker build**
```bash
docker build --check .
# Validates Dockerfile syntax
```

## YAML

### Linting

**yamllint**
```bash
yamllint .
# YAML linter
# Config: .yamllint
```

## Markdown

### Linting

**markdownlint**
```bash
markdownlint '**/*.md'
# Markdown style checker
# Config: .markdownlint.json
```

## Multi-Language Projects

### Universal Tools

**pre-commit**
```bash
pre-commit run --all-files
# Runs multiple tools across languages
# Config: .pre-commit-config.yaml
```

**mega-linter**
```bash
mega-linter
# Runs 50+ linters for all languages
# Config: .mega-linter.yml
```

**trunk**
```bash
trunk check
# Modern multi-language linter
# Config: .trunk/trunk.yaml
```

## Tool Selection Guidelines

### Criteria for Recommended Tools

1. **Speed:** Fast execution (< 10s for typical project)
2. **Accuracy:** High precision (few false positives)
3. **Maintainability:** Actively maintained
4. **Adoption:** Widely used in industry
5. **Integration:** Easy to integrate with CI/CD
6. **Configuration:** Flexible but sensible defaults

### Tool Combinations

**Python Minimal:**
```bash
uv run pyright && uv run pytest
```

**Python Standard:**
```bash
uv run pyright && uv run ruff check && uv run pytest
```

**Python Comprehensive:**
```bash
uv run pyright && \
uv run vulture src/ && \
uv run pytest tests/ && \
uv run ruff check src/ && \
uv run ruff format --check src/ && \
uv run bandit -r src/
```

**JavaScript Minimal:**
```bash
npx tsc --noEmit && npm test
```

**JavaScript Standard:**
```bash
npx tsc --noEmit && npx eslint src/ && npm test
```

**JavaScript Comprehensive:**
```bash
npx tsc --noEmit && \
npx eslint src/ && \
npm test && \
npx prettier --check src/
```

## Tool Detection Algorithm

```python
def detect_quality_gates(project_root: str) -> dict[str, str]:
    """Detect quality gate tools based on project files."""

    tools = {}

    # Check for unified script first (highest priority)
    if os.path.exists(f"{project_root}/scripts/check_all.sh"):
        tools["runner"] = "./scripts/check_all.sh"
        return tools

    # Detect language and tools
    if os.path.exists(f"{project_root}/pyproject.toml"):
        # Python project
        tools["type_checker"] = "uv run pyright"
        tools["linter"] = "uv run ruff check"
        tools["dead_code"] = "uv run vulture src/"
        tools["tests"] = "uv run pytest tests/"
        tools["formatter"] = "uv run ruff format --check"

    elif os.path.exists(f"{project_root}/package.json"):
        # JavaScript/TypeScript project
        tools["type_checker"] = "npx tsc --noEmit"
        tools["linter"] = "npx eslint src/"
        tools["tests"] = "npm test"
        tools["formatter"] = "npx prettier --check src/"

    elif os.path.exists(f"{project_root}/go.mod"):
        # Go project
        tools["type_checker"] = "go build ./..."
        tools["linter"] = "golangci-lint run"
        tools["tests"] = "go test ./..."
        tools["formatter"] = "go fmt ./..."

    elif os.path.exists(f"{project_root}/Cargo.toml"):
        # Rust project
        tools["type_checker"] = "cargo check"
        tools["linter"] = "cargo clippy"
        tools["tests"] = "cargo test"
        tools["formatter"] = "cargo fmt --check"

    return tools
```

## Performance Benchmarks

Average execution times on typical projects:

| Tool | Small Project | Medium Project | Large Project |
|------|---------------|----------------|---------------|
| pyright | 0.5s | 2s | 5s |
| mypy | 1s | 3s | 10s |
| ruff check | 0.1s | 0.3s | 1s |
| pylint | 2s | 10s | 30s |
| vulture | 0.2s | 0.5s | 2s |
| pytest | 1s | 5s | 20s |
| tsc | 1s | 5s | 15s |
| eslint | 0.5s | 3s | 10s |
| jest | 2s | 10s | 30s |

**Recommendation:** Prefer fast tools (ruff over pylint, pyright over mypy) for developer experience.

## Tool Configuration Best Practices

### Keep Configuration in Project Root

```
project-root/
├── pyproject.toml        # Python tools config
├── tsconfig.json         # TypeScript config
├── .eslintrc.js          # ESLint config
├── .prettierrc.js        # Prettier config
├── .golangci.yml         # Go linter config
└── .pre-commit-config.yaml  # Pre-commit hooks
```

### Share Configuration Across Projects

For teams, create shared config packages:
- `@company/eslint-config`
- `company-pyproject-template`
- Shared `.golangci.yml` in template repo

### Document Required Tools

In `CLAUDE.md` or `README.md`:
```markdown
## Required Tools

- Python 3.11+
- uv (package manager)
- Node.js 18+ (for pre-commit hooks)

## Quality Gates

Run before committing:
```bash
./scripts/check_all.sh
```
```

## Troubleshooting

### Tool Not Found

```bash
# Python
uv pip install -e .  # Installs dev dependencies

# JavaScript
npm install  # Installs dependencies

# Go
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

### Conflicting Tool Versions

Use version managers:
- Python: `uv`, `pyenv`
- Node: `nvm`, `fnm`
- Go: `gvm`
- Rust: `rustup`

### Performance Issues

Run tools in parallel:
```bash
# Sequential (slow)
pyright && ruff check && pytest

# Parallel (fast)
pyright & ruff check & pytest &
wait
```

Or use `check_all.sh` which runs tools in parallel automatically.
