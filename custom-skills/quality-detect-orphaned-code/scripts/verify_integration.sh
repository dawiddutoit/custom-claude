#!/bin/bash
# scripts/verify_integration.sh
# Detects orphaned modules (created but never imported in production code)

set -e

echo "=== Integration Verification ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

orphaned=0
checked=0
orphaned_files=""

echo "Checking for orphaned modules in src/..."
echo ""

for file in $(find src/ -name "*.py" -type f 2>/dev/null | sort); do
    module=$(basename "$file" .py)
    dir=$(dirname "$file")

    # Skip __init__.py, test files, main entry points
    [[ "$module" == "__init__" ]] && continue
    [[ "$module" == *"test"* ]] && continue
    [[ "$module" == "main" ]] && continue
    [[ "$module" == "__main__" ]] && continue

    checked=$((checked + 1))

    # Check if module is imported anywhere in src/ (excluding itself)
    imports=$(grep -r -E "import\s+.*\b${module}\b|from\s+.*\b${module}\b\s+import" src/ --include="*.py" 2>/dev/null | grep -v "$file" | grep -v "test_" | grep -v "__pycache__" | wc -l | tr -d ' ')

    if [ "$imports" -eq 0 ]; then
        # Check if exported via __init__.py
        init_file="$dir/__init__.py"
        init_export=0
        if [ -f "$init_file" ]; then
            init_export=$(grep -c "\b$module\b" "$init_file" 2>/dev/null || echo "0")
        fi

        if [ "$init_export" -eq 0 ]; then
            echo -e "${YELLOW}⚠️  ORPHANED:${NC} $file"
            echo "   No production imports found for module '$module'"
            orphaned=$((orphaned + 1))
            orphaned_files="$orphaned_files\n   - $file"
        fi
    fi
done

echo ""
echo "=== Results ==="
echo "Modules checked: $checked"

if [ $orphaned -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ ERROR: $orphaned orphaned module(s) found${NC}"
    echo -e "${RED}Orphaned files:${NC}$orphaned_files"
    echo ""
    echo "These files exist but are never imported in production code."
    echo ""
    echo "To fix, either:"
    echo "  1. Wire them up (add imports and call-sites)"
    echo "  2. Remove them if no longer needed"
    echo "  3. Export via __init__.py if they're part of the public API"
    exit 1
fi

echo -e "${GREEN}✅ All modules are integrated${NC}"
exit 0
