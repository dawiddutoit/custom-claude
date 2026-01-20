#!/usr/bin/env bash
# Check OpenSCAD text labeling library installations

set -euo pipefail

# Determine OpenSCAD libraries directory based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    LIB_DIR="$HOME/Documents/OpenSCAD/libraries"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    LIB_DIR="$HOME/.local/share/OpenSCAD/libraries"
else
    echo "⚠️  Unknown OS: $OSTYPE"
    echo "Please manually check your OpenSCAD libraries directory"
    exit 1
fi

echo "================================================"
echo "OpenSCAD Text Labeling Library Status"
echo "================================================"
echo ""
echo "Libraries directory: $LIB_DIR"
echo ""

# Check if libraries directory exists
if [[ ! -d "$LIB_DIR" ]]; then
    echo "❌ Libraries directory not found"
    echo "   Expected: $LIB_DIR"
    exit 1
fi

echo "Checking installed libraries..."
echo ""

# Function to check library
check_library() {
    local name=$1
    local path=$2
    local required=$3

    if [[ -d "$LIB_DIR/$path" ]]; then
        echo "✅ $name"
        echo "   Location: $LIB_DIR/$path"
    else
        if [[ "$required" == "required" ]]; then
            echo "❌ $name (REQUIRED)"
        else
            echo "⚠️  $name (optional)"
        fi
        echo "   Not found at: $LIB_DIR/$path"
    fi
    echo ""
}

# Check core libraries
check_library "BOSL2" "BOSL2" "required"

# Check text labeling libraries
check_library "text_on_OpenSCAD" "text_on_OpenSCAD" "optional"
check_library "attachable_text3d" "openscad_attachable_text3d" "optional"

echo "================================================"
echo "Installation Instructions"
echo "================================================"
echo ""

if [[ ! -d "$LIB_DIR/text_on_OpenSCAD" ]]; then
    echo "To install text_on_OpenSCAD (curved surfaces):"
    echo "  cd $LIB_DIR"
    echo "  git clone https://github.com/brodykenrick/text_on_OpenSCAD.git"
    echo ""
fi

if [[ ! -d "$LIB_DIR/openscad_attachable_text3d" ]]; then
    echo "To install attachable_text3d (BOSL2-compatible):"
    echo "  cd $LIB_DIR"
    echo "  git clone https://github.com/jon-gilbert/openscad_attachable_text3d.git"
    echo ""
fi

# Check if BOSL2 is missing (critical)
if [[ ! -d "$LIB_DIR/BOSL2" ]]; then
    echo "⚠️  BOSL2 is REQUIRED for this project"
    echo "To install BOSL2:"
    echo "  cd $LIB_DIR"
    echo "  git clone https://github.com/BelfrySCAD/BOSL2.git"
    echo ""
fi

echo "================================================"
echo "Library Feature Comparison"
echo "================================================"
echo ""
echo "BOSL2 + text():"
echo "  ✅ Flat surfaces with semantic positioning"
echo "  ✅ Already installed"
echo "  ❌ No curved surface support"
echo ""
echo "text_on_OpenSCAD:"
echo "  ✅ Cylinders, spheres, curved surfaces"
echo "  ✅ Internationalization (RTL, vertical text)"
echo "  ❌ No BOSL2 integration"
echo ""
echo "attachable_text3d:"
echo "  ✅ BOSL2 attachable integration"
echo "  ✅ Accurate font metrics"
echo "  ❌ Flat surfaces only"
echo ""

exit 0
