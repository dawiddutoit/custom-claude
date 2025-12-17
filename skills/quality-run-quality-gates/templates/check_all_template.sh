#!/usr/bin/env bash
# Quality gate script template
# Customize this template for your project's specific tools

set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Track results
CHECKS_PASSED=0
CHECKS_FAILED=0
FAILED_CHECKS=()

echo "🚦 Quality Check Results" >&2
echo "──────────────────────────────────────────────────" >&2

# Function to run a check and capture errors
run_check() {
    local name="$1"
    shift
    local cmd=("$@")

    local start=$(date +%s)
    local output_file=$(mktemp)
    local exit_code=0

    # Run command and capture output
    "${cmd[@]}" > "$output_file" 2>&1 || exit_code=$?

    local end=$(date +%s)
    local duration=$(( end - start ))

    if [[ $exit_code -eq 0 ]]; then
        echo "✅ ${name} [${duration}s]" >&2
        ((CHECKS_PASSED++))
    else
        echo "❌ ${name} [${duration}s]" >&2
        ((CHECKS_FAILED++))
        FAILED_CHECKS+=("$name")

        # Extract and show first 5 errors (customize extraction patterns)
        echo "" >&2
        echo "📋 $name failures:" >&2

        case "$name" in
            # Python type checker (pyright, mypy)
            pyright|mypy)
                grep -E "error:" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/ - error:/:/g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # Python test runner (pytest)
            pytest)
                grep -E "(ERROR collecting|FAILED)" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # Python linter (ruff, pylint, flake8)
            ruff|pylint|flake8)
                grep -E "\.py:[0-9]+:[0-9]+:" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # Python dead code detector (vulture)
            vulture)
                grep -E "\.py:[0-9]+:" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # TypeScript type checker (tsc)
            tsc)
                grep -E "error TS[0-9]+:" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # JavaScript/TypeScript linter (eslint)
            eslint)
                grep -E "error " "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # JavaScript/TypeScript test runner (jest, vitest)
            jest|vitest)
                grep -E "(FAIL|✕)" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # Go linter (golangci-lint)
            golangci-lint)
                grep -E "\.go:[0-9]+:[0-9]+:" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # Rust linter (clippy)
            clippy)
                grep -E "error\[" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # Formatter checks (ruff format, black, prettier, etc.)
            "ruff format"|black|prettier)
                grep -E "would reformat|would change" "$output_file" | head -5 | \
                    sed 's|'"$PROJECT_ROOT/"'||g' | \
                    sed 's/^/  /' >&2 || true
                ;;

            # Generic fallback: show last 5 lines of output
            *)
                tail -5 "$output_file" | sed 's/^/  /' >&2 || true
                ;;
        esac
        echo "" >&2
    fi

    rm -f "$output_file"
}

#############################################
# CUSTOMIZE THIS SECTION FOR YOUR PROJECT
#############################################

# Python project example
if [[ -f pyproject.toml ]]; then
    run_check "pyright" uv run pyright
    run_check "vulture" uv run vulture src/ --min-confidence 80
    run_check "pytest" uv run pytest tests/ -q --tb=no
    run_check "ruff" uv run ruff check src/ tests/
    run_check "ruff format" uv run ruff format src/ tests/ --check
fi

# JavaScript/TypeScript project example
if [[ -f package.json ]]; then
    if [[ -f tsconfig.json ]]; then
        run_check "tsc" npx tsc --noEmit
    fi
    run_check "eslint" npx eslint src/
    run_check "jest" npm test
    run_check "prettier" npx prettier --check src/
fi

# Go project example
if [[ -f go.mod ]]; then
    run_check "go build" go build ./...
    run_check "golangci-lint" golangci-lint run
    run_check "go test" go test ./...
    run_check "go fmt" test -z "$(gofmt -l .)"
fi

# Rust project example
if [[ -f Cargo.toml ]]; then
    run_check "cargo check" cargo check
    run_check "clippy" cargo clippy -- -D warnings
    run_check "cargo test" cargo test
    run_check "cargo fmt" cargo fmt --check
fi

#############################################
# END CUSTOMIZATION
#############################################

echo "──────────────────────────────────────────────────" >&2

# Summary
TOTAL_CHECKS=$((CHECKS_PASSED + CHECKS_FAILED))
if [[ $CHECKS_FAILED -eq 0 ]]; then
    echo "✅ All $TOTAL_CHECKS checks passed" >&2
    exit 0
else
    echo "❌ $CHECKS_FAILED of $TOTAL_CHECKS checks failed: ${FAILED_CHECKS[*]}" >&2
    exit 1
fi
