#!/bin/bash
# detect_project_type.sh - Detect project language and framework

set -euo pipefail

# Detect project type based on files present
detect_project_type() {
    local project_dir="${1:-.}"

    # Python
    if [ -f "$project_dir/pyproject.toml" ] || \
       [ -f "$project_dir/requirements.txt" ] || \
       [ -f "$project_dir/setup.py" ] || \
       [ -f "$project_dir/Pipfile" ]; then
        echo "python"
        return 0
    fi

    # JavaScript/TypeScript
    if [ -f "$project_dir/package.json" ]; then
        if [ -f "$project_dir/tsconfig.json" ]; then
            echo "typescript"
        else
            echo "javascript"
        fi
        return 0
    fi

    # Go
    if [ -f "$project_dir/go.mod" ]; then
        echo "go"
        return 0
    fi

    # Rust
    if [ -f "$project_dir/Cargo.toml" ]; then
        echo "rust"
        return 0
    fi

    # Ruby
    if [ -f "$project_dir/Gemfile" ]; then
        echo "ruby"
        return 0
    fi

    # Java
    if [ -f "$project_dir/pom.xml" ] || [ -f "$project_dir/build.gradle" ]; then
        echo "java"
        return 0
    fi

    # C#
    if compgen -G "$project_dir/*.csproj" > /dev/null 2>&1 || \
       compgen -G "$project_dir/*.sln" > /dev/null 2>&1; then
        echo "csharp"
        return 0
    fi

    # Unknown
    echo "unknown"
    return 1
}

# Detect quality gate tools available
detect_quality_tools() {
    local project_type="$1"
    local tools=()

    case "$project_type" in
        python)
            command -v pyright >/dev/null 2>&1 && tools+=("pyright")
            command -v mypy >/dev/null 2>&1 && tools+=("mypy")
            command -v ruff >/dev/null 2>&1 && tools+=("ruff")
            command -v pylint >/dev/null 2>&1 && tools+=("pylint")
            command -v vulture >/dev/null 2>&1 && tools+=("vulture")
            command -v pytest >/dev/null 2>&1 && tools+=("pytest")
            ;;

        typescript|javascript)
            command -v tsc >/dev/null 2>&1 && tools+=("tsc")
            command -v eslint >/dev/null 2>&1 && tools+=("eslint")
            command -v jest >/dev/null 2>&1 && tools+=("jest")
            command -v vitest >/dev/null 2>&1 && tools+=("vitest")
            command -v prettier >/dev/null 2>&1 && tools+=("prettier")
            ;;

        go)
            command -v go >/dev/null 2>&1 && tools+=("go")
            command -v golangci-lint >/dev/null 2>&1 && tools+=("golangci-lint")
            ;;

        rust)
            command -v cargo >/dev/null 2>&1 && tools+=("cargo")
            ;;

        *)
            echo "Unknown project type: $project_type" >&2
            return 1
            ;;
    esac

    # Only print tools if array is not empty
    if [ ${#tools[@]} -gt 0 ]; then
        printf "%s\n" "${tools[@]}"
    fi
}

# Detect unified check script
detect_check_script() {
    local project_dir="${1:-.}"

    # Check for common check scripts
    if [ -x "$project_dir/scripts/check_all.sh" ]; then
        echo "$project_dir/scripts/check_all.sh"
        return 0
    fi

    if [ -f "$project_dir/Makefile" ] && grep -q "^check:" "$project_dir/Makefile"; then
        echo "make check"
        return 0
    fi

    if [ -f "$project_dir/package.json" ] && grep -q '"check"' "$project_dir/package.json"; then
        echo "npm run check"
        return 0
    fi

    # No unified script found
    return 1
}

# Main execution
main() {
    local project_dir="${1:-.}"

    echo "=== Project Detection ==="

    # Detect project type
    local project_type
    project_type=$(detect_project_type "$project_dir")
    echo "Project Type: $project_type"

    # Detect quality tools
    echo ""
    echo "=== Available Quality Tools ==="
    if ! detect_quality_tools "$project_type"; then
        echo "Warning: No quality tools detected" >&2
        return 1
    fi

    # Detect check script
    echo ""
    echo "=== Check Script ==="
    if detect_check_script "$project_dir"; then
        echo "Found unified check script"
    else
        echo "No unified check script (will use individual tools)"
    fi

    return 0
}

# Run if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
