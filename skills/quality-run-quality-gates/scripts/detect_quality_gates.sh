#!/usr/bin/env bash
# Detect quality gate tools for the current project
# Returns JSON with detected tools and recommended runner

set -euo pipefail

PROJECT_ROOT="${1:-.}"
cd "$PROJECT_ROOT"

# Initialize result object
TOOLS='{"runner":"","type_checker":"","linter":"","dead_code":"","tests":"","formatter":"","project_type":"","detected":false}'

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to update JSON field
update_field() {
    local field="$1"
    local value="$2"
    TOOLS=$(echo "$TOOLS" | jq --arg f "$field" --arg v "$value" '.[$f] = $v')
}

# Check for unified script (highest priority)
if [[ -f scripts/check_all.sh ]]; then
    update_field "runner" "./scripts/check_all.sh"
    update_field "detected" "true"
    echo "$TOOLS"
    exit 0
elif [[ -f Makefile ]] && grep -q "^check:" Makefile 2>/dev/null; then
    update_field "runner" "make check"
    update_field "detected" "true"
    echo "$TOOLS"
    exit 0
fi

# Detect project type and tools
if [[ -f pyproject.toml ]] || [[ -f requirements.txt ]] || [[ -f setup.py ]]; then
    # Python project
    update_field "project_type" "python"

    # Type checker
    if command_exists uv && uv run pyright --version >/dev/null 2>&1; then
        update_field "type_checker" "uv run pyright"
    elif command_exists pyright; then
        update_field "type_checker" "pyright"
    elif command_exists mypy; then
        update_field "type_checker" "mypy src/"
    fi

    # Linter
    if command_exists uv && uv run ruff --version >/dev/null 2>&1; then
        update_field "linter" "uv run ruff check src/ tests/"
    elif command_exists ruff; then
        update_field "linter" "ruff check src/ tests/"
    elif command_exists pylint; then
        update_field "linter" "pylint src/"
    elif command_exists flake8; then
        update_field "linter" "flake8 src/"
    fi

    # Dead code detector
    if command_exists uv && uv run vulture --version >/dev/null 2>&1; then
        update_field "dead_code" "uv run vulture src/ --min-confidence 80"
    elif command_exists vulture; then
        update_field "dead_code" "vulture src/ --min-confidence 80"
    fi

    # Test runner
    if command_exists uv && uv run pytest --version >/dev/null 2>&1; then
        update_field "tests" "uv run pytest tests/ -q"
    elif command_exists pytest; then
        update_field "tests" "pytest tests/ -q"
    elif command_exists python && python -m unittest --help >/dev/null 2>&1; then
        update_field "tests" "python -m unittest discover tests/"
    fi

    # Formatter
    if command_exists uv && uv run ruff --version >/dev/null 2>&1; then
        update_field "formatter" "uv run ruff format --check src/ tests/"
    elif command_exists black; then
        update_field "formatter" "black --check src/"
    fi

    update_field "detected" "true"

elif [[ -f package.json ]]; then
    # JavaScript/TypeScript project
    update_field "project_type" "javascript"

    # Check for npm scripts first
    if grep -q '"check"' package.json 2>/dev/null; then
        update_field "runner" "npm run check"
        update_field "detected" "true"
        echo "$TOOLS"
        exit 0
    fi

    # Type checker
    if [[ -f tsconfig.json ]]; then
        if command_exists npx; then
            update_field "type_checker" "npx tsc --noEmit"
        fi
    fi

    # Linter
    if [[ -f .eslintrc.js ]] || [[ -f .eslintrc.json ]] || grep -q '"eslint"' package.json 2>/dev/null; then
        update_field "linter" "npx eslint src/"
    fi

    # Test runner
    if grep -q '"test"' package.json 2>/dev/null; then
        update_field "tests" "npm test"
    elif grep -q '"jest"' package.json 2>/dev/null; then
        update_field "tests" "npx jest"
    elif grep -q '"vitest"' package.json 2>/dev/null; then
        update_field "tests" "npx vitest run"
    fi

    # Formatter
    if [[ -f .prettierrc.js ]] || [[ -f .prettierrc.json ]] || grep -q '"prettier"' package.json 2>/dev/null; then
        update_field "formatter" "npx prettier --check src/"
    fi

    update_field "detected" "true"

elif [[ -f go.mod ]]; then
    # Go project
    update_field "project_type" "go"

    # Type checker (build)
    if command_exists go; then
        update_field "type_checker" "go build ./..."
    fi

    # Linter
    if command_exists golangci-lint; then
        update_field "linter" "golangci-lint run"
    elif command_exists staticcheck; then
        update_field "linter" "staticcheck ./..."
    fi

    # Test runner
    if command_exists go; then
        update_field "tests" "go test ./..."
    fi

    # Formatter
    if command_exists go; then
        update_field "formatter" "go fmt ./..."
    fi

    update_field "detected" "true"

elif [[ -f Cargo.toml ]]; then
    # Rust project
    update_field "project_type" "rust"

    # Type checker
    if command_exists cargo; then
        update_field "type_checker" "cargo check"
    fi

    # Linter
    if command_exists cargo; then
        update_field "linter" "cargo clippy -- -D warnings"
    fi

    # Test runner
    if command_exists cargo; then
        update_field "tests" "cargo test"
    fi

    # Formatter
    if command_exists cargo; then
        update_field "formatter" "cargo fmt --check"
    fi

    update_field "detected" "true"

elif [[ -f Gemfile ]]; then
    # Ruby project
    update_field "project_type" "ruby"

    # Type checker
    if grep -q "sorbet" Gemfile 2>/dev/null; then
        update_field "type_checker" "bundle exec srb tc"
    fi

    # Linter
    if grep -q "rubocop" Gemfile 2>/dev/null; then
        update_field "linter" "bundle exec rubocop"
    fi

    # Test runner
    if [[ -d spec ]]; then
        update_field "tests" "bundle exec rspec"
    elif [[ -d test ]]; then
        update_field "tests" "bundle exec rake test"
    fi

    update_field "detected" "true"

elif [[ -f pom.xml ]] || [[ -f build.gradle ]]; then
    # Java project
    update_field "project_type" "java"

    if [[ -f pom.xml ]]; then
        # Maven
        update_field "type_checker" "mvn compile"
        update_field "tests" "mvn test"

        if grep -q "checkstyle" pom.xml 2>/dev/null; then
            update_field "linter" "mvn checkstyle:check"
        fi
    elif [[ -f build.gradle ]]; then
        # Gradle
        update_field "type_checker" "./gradlew build"
        update_field "tests" "./gradlew test"

        if grep -q "checkstyle" build.gradle 2>/dev/null; then
            update_field "linter" "./gradlew checkstyleMain"
        fi
    fi

    update_field "detected" "true"
fi

# Check for .claude/quality-gates.json (explicit configuration)
if [[ -f .claude/quality-gates.json ]]; then
    TOOLS=$(cat .claude/quality-gates.json)
    update_field "detected" "true"
fi

# Output result
echo "$TOOLS"

# Exit code based on detection
if [[ $(echo "$TOOLS" | jq -r '.detected') == "true" ]]; then
    exit 0
else
    exit 1
fi
