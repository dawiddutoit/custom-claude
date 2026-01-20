#!/usr/bin/env bash
# List fonts available to OpenSCAD

set -euo pipefail

echo "================================================"
echo "Fonts Available to OpenSCAD"
echo "================================================"
echo ""

# Check OS and use appropriate command
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Platform: macOS"
    echo ""

    # Check if fontconfig is installed
    if command -v fc-list &> /dev/null; then
        echo "Using fontconfig (fc-list)..."
        echo ""
        echo "All fonts:"
        fc-list : family | sort | uniq | nl
    else
        echo "⚠️  fontconfig (fc-list) not found"
        echo "Install with: brew install fontconfig"
        echo ""
        echo "Listing fonts directory instead:"
        echo ""
        ls -1 /Library/Fonts/*.ttf /Library/Fonts/*.otf 2>/dev/null | \
            xargs -I {} basename {} | \
            sed 's/\.[^.]*$//' | \
            sort | uniq | nl
    fi

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Platform: Linux"
    echo ""

    if command -v fc-list &> /dev/null; then
        echo "Using fontconfig (fc-list)..."
        echo ""
        echo "All fonts:"
        fc-list : family | sort | uniq | nl
    else
        echo "❌ fontconfig not found"
        echo "Install with:"
        echo "  Ubuntu/Debian: sudo apt-get install fontconfig"
        echo "  Fedora/RHEL: sudo dnf install fontconfig"
        exit 1
    fi

else
    echo "⚠️  Unknown OS: $OSTYPE"
    echo "Please use your system's font viewer"
    exit 1
fi

echo ""
echo "================================================"
echo "Cross-Platform Fonts (Always Available)"
echo "================================================"
echo ""
echo "These fonts work on all platforms:"
echo "  - Liberation Sans"
echo "  - Liberation Mono"
echo "  - Liberation Serif"
echo ""
echo "Use these for maximum compatibility."
echo ""

echo "================================================"
echo "Testing Fonts in OpenSCAD"
echo "================================================"
echo ""
echo "Create a test file to verify font rendering:"
echo ""
cat << 'EOF'
// font-test.scad
fonts = ["Liberation Sans", "Liberation Mono", "Liberation Serif"];

for (i = [0:len(fonts)-1]) {
    translate([0, -i*15, 0])
        linear_extrude(1)
            text(fonts[i], size=8, font=fonts[i]);
}
EOF
echo ""
echo "Then render with: openscad font-test.scad"
echo ""

exit 0
