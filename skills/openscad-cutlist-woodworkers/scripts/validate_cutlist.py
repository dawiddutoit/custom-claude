#!/usr/bin/env python3
"""
Validate cut list for common issues.

Checks for:
- Duplicate panels (potential over-ordering)
- Unusual thicknesses
- Panels exceeding standard sheet size
- Missing edge bands on large visible panels
- Zero or negative dimensions

Usage:
    python3 validate_cutlist.py cutlist.csv
    python3 validate_cutlist.py cutlist.json
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple


# Standard sheet sizes (width, height in mm)
STANDARD_SHEETS = [
    (2440, 1220),  # Standard plywood/MDF
    (2800, 2070),  # Large format
    (1220, 1220),  # Square sheet
]

# Standard thicknesses (mm)
STANDARD_THICKNESSES = [3, 4, 6, 9, 12, 15, 16, 18, 22, 25]

# Maximum panel dimension without warning (mm)
MAX_PANEL_DIMENSION = 2440

# Minimum edge length for edge banding consideration (mm)
MIN_EDGE_BAND_LENGTH = 100


class ValidationIssue:
    """Represents a validation warning or error."""

    def __init__(self, level: str, message: str, panel: Dict = None):
        self.level = level  # 'warning' or 'error'
        self.message = message
        self.panel = panel

    def __str__(self):
        prefix = "⚠️ " if self.level == 'warning' else "❌"
        return f"{prefix} {self.message}"


def load_cutlist(file_path: Path) -> List[Dict]:
    """Load cut list from CSV or JSON file."""
    if file_path.suffix.lower() == '.json':
        with open(file_path) as f:
            data = json.load(f)
            return data.get('panels', [])
    else:  # Assume CSV
        panels = []
        with open(file_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                panel = {
                    'part_name': row.get('part_name', row.get('Part Name', '')),
                    'width': float(row.get('width', row.get('Width', 0))),
                    'height': float(row.get('height', row.get('Height', 0))),
                    'thickness': float(row.get('thickness', row.get('Thickness', 0))),
                    'quantity': int(row.get('quantity', row.get('Quantity', 1))),
                    'edge1': int(row.get('edge1', row.get('Edge1', 0))),
                    'edge2': int(row.get('edge2', row.get('Edge2', 0))),
                    'edge3': int(row.get('edge3', row.get('Edge3', 0))),
                    'edge4': int(row.get('edge4', row.get('Edge4', 0))),
                    'notes': row.get('notes', row.get('Notes', '')),
                }
                panels.append(panel)
        return panels


def validate_dimensions(panels: List[Dict]) -> List[ValidationIssue]:
    """Check for invalid dimensions (zero, negative, or too large)."""
    issues = []

    for panel in panels:
        width = panel['width']
        height = panel['height']
        thickness = panel['thickness']

        if width <= 0 or height <= 0 or thickness <= 0:
            issues.append(ValidationIssue(
                'error',
                f"Panel '{panel['part_name']}' has invalid dimensions: "
                f"{width}×{height}×{thickness}mm (must be positive)",
                panel
            ))

        if width > MAX_PANEL_DIMENSION or height > MAX_PANEL_DIMENSION:
            issues.append(ValidationIssue(
                'warning',
                f"Panel '{panel['part_name']}' ({width}×{height}mm) exceeds "
                f"standard sheet size ({MAX_PANEL_DIMENSION}mm). May require joining.",
                panel
            ))

    return issues


def validate_thicknesses(panels: List[Dict]) -> List[ValidationIssue]:
    """Check for non-standard thicknesses."""
    issues = []

    for panel in panels:
        thickness = panel['thickness']
        if thickness not in STANDARD_THICKNESSES:
            issues.append(ValidationIssue(
                'warning',
                f"Panel '{panel['part_name']}' uses non-standard thickness: {thickness}mm. "
                f"Verify supplier availability. Standard: {STANDARD_THICKNESSES}",
                panel
            ))

    return issues


def validate_duplicates(panels: List[Dict]) -> List[ValidationIssue]:
    """Check for potential duplicate panels."""
    issues = []
    seen = {}

    for panel in panels:
        # Create key based on dimensions only (ignore name/notes)
        key = (panel['width'], panel['height'], panel['thickness'])

        if key in seen:
            # Duplicate dimensions found
            other = seen[key]
            total_qty = panel['quantity'] + other['quantity']
            issues.append(ValidationIssue(
                'warning',
                f"Duplicate panel dimensions: {panel['width']}×{panel['height']}×{panel['thickness']}mm "
                f"appears {total_qty} times ('{panel['part_name']}' and '{other['part_name']}'). "
                f"Confirm quantity is correct.",
                panel
            ))
        else:
            seen[key] = panel

    return issues


def validate_edge_banding(panels: List[Dict]) -> List[ValidationIssue]:
    """Check for missing edge banding on large visible panels."""
    issues = []

    for panel in panels:
        width = panel['width']
        height = panel['height']
        edges = [panel['edge1'], panel['edge2'], panel['edge3'], panel['edge4']]

        # Skip if panel is too small or is a back panel (typically no edge banding)
        if 'back' in panel['part_name'].lower():
            continue

        # Check if large panel has no edge banding
        if (width > MIN_EDGE_BAND_LENGTH or height > MIN_EDGE_BAND_LENGTH) and sum(edges) == 0:
            issues.append(ValidationIssue(
                'warning',
                f"Panel '{panel['part_name']}' ({width}×{height}mm) has no edge banding. "
                f"Add edge bands if visible edges present.",
                panel
            ))

    return issues


def validate_sheet_fit(panels: List[Dict]) -> Tuple[List[ValidationIssue], Dict]:
    """
    Validate panels fit on standard sheets and calculate material requirements.

    Returns:
        Tuple of (issues, material_summary)
    """
    issues = []
    by_thickness = {}

    for panel in panels:
        thick = panel['thickness']
        if thick not in by_thickness:
            by_thickness[thick] = []

        for _ in range(panel['quantity']):
            by_thickness[thick].append((panel['width'], panel['height']))

    material_summary = {}

    for thick, panels_list in by_thickness.items():
        total_area = sum(w * h for w, h in panels_list) / 1_000_000  # m²

        # Find best-fitting standard sheet
        best_sheet = None
        min_sheets = float('inf')

        for sheet_w, sheet_h in STANDARD_SHEETS:
            sheet_area = (sheet_w * sheet_h) / 1_000_000
            estimated_sheets = total_area / (sheet_area * 0.85)  # Assume 85% efficiency
            if estimated_sheets < min_sheets:
                min_sheets = estimated_sheets
                best_sheet = (sheet_w, sheet_h)

        material_summary[thick] = {
            'panel_count': len(panels_list),
            'total_area_m2': total_area,
            'recommended_sheet': best_sheet,
            'estimated_sheets': max(1, round(min_sheets))
        }

    return issues, material_summary


def print_validation_report(panels: List[Dict], issues: List[ValidationIssue],
                             material_summary: Dict):
    """Print comprehensive validation report."""
    print("\n" + "="*60)
    print("CUT LIST VALIDATION REPORT")
    print("="*60 + "\n")

    # Summary
    print(f"Total unique panels: {len(panels)}")
    print(f"Total panels (with quantities): {sum(p['quantity'] for p in panels)}\n")

    # Issues
    errors = [i for i in issues if i.level == 'error']
    warnings = [i for i in issues if i.level == 'warning']

    if errors:
        print(f"\n❌ ERRORS FOUND ({len(errors)}):\n")
        for issue in errors:
            print(f"  {issue}")
        print()

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):\n")
        for issue in warnings:
            print(f"  {issue}")
        print()

    if not errors and not warnings:
        print("✅ No validation issues found!\n")

    # Material summary
    print("\nMATERIAL REQUIREMENTS:\n")
    for thick, summary in sorted(material_summary.items()):
        print(f"{thick}mm panels:")
        print(f"  Panels: {summary['panel_count']}")
        print(f"  Total area: {summary['total_area_m2']:.2f} m²")
        print(f"  Recommended sheet: {summary['recommended_sheet'][0]}×{summary['recommended_sheet'][1]}mm")
        print(f"  Estimated sheets: {summary['estimated_sheets']}")
        print()

    # Edge banding summary
    total_edge_length = 0
    for panel in panels:
        width = panel['width']
        height = panel['height']
        qty = panel['quantity']
        edges = [panel['edge1'], panel['edge2'], panel['edge3'], panel['edge4']]

        for i, edge in enumerate(edges):
            if edge > 0:
                length = width if i in [0, 2] else height
                total_edge_length += length * qty / 1000

    if total_edge_length > 0:
        print(f"EDGE BANDING:")
        print(f"  Total length: {total_edge_length:.1f}m")
        print(f"  Recommended order: {total_edge_length * 1.1:.1f}m (with 10% waste)\n")

    print("="*60)

    # Exit code
    if errors:
        print("\n❌ Validation FAILED - fix errors before proceeding")
        return 1
    elif warnings:
        print("\n⚠️  Validation passed with warnings - review before ordering")
        return 0
    else:
        print("\n✅ Validation PASSED - ready for optimization")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate cut list for common issues'
    )
    parser.add_argument('cutlist', help='Cut list file (CSV or JSON)')
    parser.add_argument('--strict', action='store_true',
                        help='Treat warnings as errors')

    args = parser.parse_args()

    cutlist_file = Path(args.cutlist)
    if not cutlist_file.exists():
        print(f"ERROR: File not found: {cutlist_file}", file=sys.stderr)
        sys.exit(1)

    # Load cut list
    try:
        panels = load_cutlist(cutlist_file)
    except Exception as e:
        print(f"ERROR: Failed to load cut list: {e}", file=sys.stderr)
        sys.exit(1)

    if not panels:
        print("ERROR: No panels found in cut list", file=sys.stderr)
        sys.exit(1)

    # Run validations
    issues = []
    issues.extend(validate_dimensions(panels))
    issues.extend(validate_thicknesses(panels))
    issues.extend(validate_duplicates(panels))
    issues.extend(validate_edge_banding(panels))

    sheet_issues, material_summary = validate_sheet_fit(panels)
    issues.extend(sheet_issues)

    # Print report
    exit_code = print_validation_report(panels, issues, material_summary)

    # Strict mode: treat warnings as errors
    if args.strict and any(i.level == 'warning' for i in issues):
        exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
