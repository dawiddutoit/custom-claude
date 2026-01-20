#!/usr/bin/env python3
"""
Validate screenshot dimensions match expected breakpoints.

Usage:
    python validate_screenshots.py screenshots/

Validates:
- Screenshot files exist
- Dimensions match expected breakpoints (within tolerance)
- File naming follows convention
- File sizes are reasonable

Exit codes:
    0 = All validations passed
    1 = Validation failures found
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


# Standard breakpoints (width, height)
STANDARD_BREAKPOINTS = {
    "mobile": (375, 667),
    "tablet": (768, 1024),
    "desktop": (1920, 1080),
}

# Tolerance for dimension matching (pixels)
DIMENSION_TOLERANCE = 5

# Expected file size ranges (KB) for PNG screenshots
SIZE_RANGES = {
    "mobile": (50, 500),      # 50KB - 500KB
    "tablet": (200, 1000),    # 200KB - 1MB
    "desktop": (500, 3000),   # 500KB - 3MB
}


def get_image_dimensions(filepath: Path) -> Tuple[int, int]:
    """
    Get image dimensions from PNG file.

    Simple PNG header parsing without external dependencies.
    """
    try:
        with open(filepath, 'rb') as f:
            # PNG signature
            signature = f.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                raise ValueError("Not a valid PNG file")

            # Read IHDR chunk
            f.read(4)  # Chunk length
            chunk_type = f.read(4)
            if chunk_type != b'IHDR':
                raise ValueError("IHDR chunk not found")

            # Read width and height (big-endian 32-bit integers)
            width_bytes = f.read(4)
            height_bytes = f.read(4)

            width = int.from_bytes(width_bytes, byteorder='big')
            height = int.from_bytes(height_bytes, byteorder='big')

            return width, height
    except Exception as e:
        print(f"❌ Error reading {filepath.name}: {e}")
        return (0, 0)


def validate_screenshot_file(filepath: Path) -> Dict[str, any]:
    """
    Validate a single screenshot file.

    Returns dict with validation results.
    """
    result = {
        "filename": filepath.name,
        "exists": filepath.exists(),
        "dimensions": None,
        "expected_breakpoint": None,
        "dimensions_match": False,
        "size_ok": False,
        "errors": []
    }

    if not result["exists"]:
        result["errors"].append("File does not exist")
        return result

    # Extract breakpoint from filename
    name = filepath.stem.lower()
    for breakpoint in STANDARD_BREAKPOINTS.keys():
        if breakpoint in name:
            result["expected_breakpoint"] = breakpoint
            break

    if not result["expected_breakpoint"]:
        result["errors"].append("Cannot determine breakpoint from filename")

    # Get actual dimensions
    width, height = get_image_dimensions(filepath)
    if width == 0 or height == 0:
        result["errors"].append("Invalid or unreadable image")
        return result

    result["dimensions"] = (width, height)

    # Validate dimensions against expected breakpoint
    if result["expected_breakpoint"]:
        expected_w, expected_h = STANDARD_BREAKPOINTS[result["expected_breakpoint"]]
        width_match = abs(width - expected_w) <= DIMENSION_TOLERANCE
        height_match = abs(height - expected_h) <= DIMENSION_TOLERANCE

        result["dimensions_match"] = width_match and height_match

        if not result["dimensions_match"]:
            result["errors"].append(
                f"Dimensions {width}×{height} do not match expected "
                f"{expected_w}×{expected_h} (tolerance: ±{DIMENSION_TOLERANCE}px)"
            )

    # Validate file size
    file_size_kb = filepath.stat().st_size / 1024

    if result["expected_breakpoint"]:
        min_size, max_size = SIZE_RANGES[result["expected_breakpoint"]]
        result["size_ok"] = min_size <= file_size_kb <= max_size

        if not result["size_ok"]:
            result["errors"].append(
                f"File size {file_size_kb:.1f}KB outside expected range "
                f"{min_size}-{max_size}KB"
            )

    return result


def validate_directory(directory: Path) -> List[Dict]:
    """
    Validate all PNG screenshots in directory.
    """
    if not directory.exists():
        print(f"❌ Directory does not exist: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        print(f"❌ Not a directory: {directory}")
        sys.exit(1)

    # Find all PNG files
    png_files = list(directory.glob("*.png"))

    if not png_files:
        print(f"⚠️  No PNG files found in {directory}")
        return []

    results = []
    for filepath in sorted(png_files):
        result = validate_screenshot_file(filepath)
        results.append(result)

    return results


def print_validation_report(results: List[Dict]) -> int:
    """
    Print validation report and return exit code.
    """
    if not results:
        return 0

    total = len(results)
    passed = sum(1 for r in results if not r["errors"])
    failed = total - passed

    print("\n" + "=" * 70)
    print("Screenshot Validation Report")
    print("=" * 70)

    for result in results:
        status = "✅" if not result["errors"] else "❌"
        print(f"\n{status} {result['filename']}")

        if result["dimensions"]:
            w, h = result["dimensions"]
            print(f"   Dimensions: {w}×{h}")

        if result["expected_breakpoint"]:
            expected_w, expected_h = STANDARD_BREAKPOINTS[result["expected_breakpoint"]]
            print(f"   Expected: {expected_w}×{expected_h} ({result['expected_breakpoint']})")

        if result["errors"]:
            for error in result["errors"]:
                print(f"   ⚠️  {error}")

    print("\n" + "=" * 70)
    print(f"Summary: {passed}/{total} passed, {failed}/{total} failed")
    print("=" * 70 + "\n")

    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Validate responsive screenshot dimensions and file properties"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing screenshot files"
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=DIMENSION_TOLERANCE,
        help=f"Dimension tolerance in pixels (default: {DIMENSION_TOLERANCE})"
    )

    args = parser.parse_args()

    # Update global tolerance if specified
    global DIMENSION_TOLERANCE
    DIMENSION_TOLERANCE = args.tolerance

    results = validate_directory(args.directory)
    exit_code = print_validation_report(results)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
