#!/usr/bin/env python3
"""
Extract cut list from woodworkers-lib OpenSCAD files.

Parses ECHO output from OpenSCAD rendering to generate CSV cut lists
for import into CutListOptimizer or other sheet optimization tools.

Features:
- Automatic grain direction based on panel orientation
- Numbered duplicate panels (e.g., "Left Panel 1", "Left Panel 2")
- Material name mapping (18mm → "18mm Birch Ply")

Usage:
    python3 extract_cutlist.py input.scad -o cutlist.csv
    python3 extract_cutlist.py input.scad --format json
    openscad --render input.scad 2>&1 | python3 extract_cutlist.py --stdin -o cutlist.csv
"""

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Material name mapping: thickness (mm) → full material name
DEFAULT_MATERIAL_MAP = {
    18.0: "18mm Birch Ply",
    9.0: "9mm Birch Ply",
    6.0: "6mm Ply",
    12.0: "12mm Birch Ply",
    15.0: "15mm Birch Ply",
}


class Panel:
    """Represents a single panel from the cut list."""

    def __init__(self, face: str, dimensions: Tuple[float, float, float],
                 edge_bands: Dict[str, List[float]]):
        self.face = face  # left, right, top, bottom, front, back

        # Woodworkers-lib outputs dimensions in different orders based on orientation:
        # - left/right: [thickness, depth, height]
        # - front/back: [width, thickness, height]
        # - top/bottom: [width, depth, thickness]
        # We need to normalize to [width, height, thickness]

        face_lower = face.lower()
        if 'left' in face_lower or 'right' in face_lower:
            # [thickness, depth, height] → [depth, height, thickness]
            self.width = dimensions[1]
            self.height = dimensions[2]
            self.thickness = dimensions[0]
        elif 'front' in face_lower or 'back' in face_lower:
            # [width, thickness, height] → [width, height, thickness]
            self.width = dimensions[0]
            self.height = dimensions[2]
            self.thickness = dimensions[1]
        else:  # top, bottom, or other
            # [width, depth, thickness] → [width, depth, thickness]
            self.width = dimensions[0]
            self.height = dimensions[1]
            self.thickness = dimensions[2]

        self.edge_bands = edge_bands  # {dimension_index: [band_widths]}

    def __repr__(self):
        return f"Panel({self.face}, {self.width}×{self.height}×{self.thickness}mm, edges={self.edge_bands})"

    def get_grain_locked(self) -> bool:
        """Determine if grain direction should be locked based on panel orientation.

        - Vertical panels (left/right/dividers): grain runs vertically → locked
        - Horizontal panels (top/bottom): grain direction less critical → not locked
        - Back panels: typically thin material, grain less critical → not locked
        """
        face_lower = self.face.lower()

        # Vertical orientation panels - grain should run along height
        if any(keyword in face_lower for keyword in ['left', 'right', 'divider', 'side', 'front', 'door']):
            return True

        # Horizontal orientation panels - grain direction less critical
        if any(keyword in face_lower for keyword in ['top', 'bottom', 'shelf', 'back']):
            return False

        # Default: lock grain for safety
        return True

    def to_dict(self, material_map: Dict[float, str] = None, panel_number: int = None) -> Dict:
        """Convert to dictionary for CSV/JSON export.

        Args:
            material_map: Mapping of thickness to material names
            panel_number: Number to append to duplicate panel names (e.g., "Left Panel 2")
        """
        material_map = material_map or DEFAULT_MATERIAL_MAP

        # Determine edge banding on 4 edges (assume rectangular panel)
        edges = [0, 0, 0, 0]
        for dim_idx, bands in self.edge_bands.items():
            if bands:
                # Assign edge band thickness (take first if multiple)
                edge_thickness = int(bands[0])
                if dim_idx == 0:  # Width dimension
                    edges[0] = edge_thickness  # Top edge
                    if len(bands) > 1:
                        edges[2] = int(bands[1])  # Bottom edge
                elif dim_idx == 1:  # Height dimension
                    edges[1] = edge_thickness  # Right edge
                    if len(bands) > 1:
                        edges[3] = int(bands[1])  # Left edge

        # Generate panel name with optional numbering
        face_name = self.face.capitalize()
        if panel_number is not None and panel_number > 1:
            part_name = f'{face_name} Panel {panel_number}'
        else:
            part_name = f'{face_name} Panel'

        # Get material name from mapping
        material = material_map.get(self.thickness, f"{int(self.thickness)}mm")

        return {
            'part_name': part_name,
            'width': self.width,
            'height': self.height,
            'thickness': self.thickness,
            'material': material,
            'quantity': 1,
            'grain_locked': 'Yes' if self.get_grain_locked() else 'No',
            'edge1': edges[0],
            'edge2': edges[1],
            'edge3': edges[2],
            'edge4': edges[3],
            'notes': f'{self.face} panel'
        }


def parse_echo_line(line: str) -> Optional[Panel]:
    """
    Parse a single ECHO line from woodworkers-lib output.

    Example input:
        ECHO: "plane (left):   18 × 378 × 1164(4)"
        ECHO: "plane (top):    782(4,4) × 378(4) × 18"

    Returns Panel object or None if not a valid plane ECHO.
    """
    # Match: ECHO: "plane (FACE):  DIM × DIM × DIM"
    # Updated regex to handle multi-word face names like "drawer front large"
    match = re.search(r'ECHO:\s*"plane\s*\(([^)]+)\):\s*(.+)"', line)
    if not match:
        return None

    face = match.group(1).lower()
    dims_str = match.group(2)

    # Split by × (multiply sign) or x
    dims_parts = re.split(r'\s*[×x]\s*', dims_str)
    if len(dims_parts) != 3:
        return None

    dimensions = []
    edge_bands = {}

    for idx, part in enumerate(dims_parts):
        # Extract dimension and optional edge bands: "782(4,4)" → 782, [4, 4]
        dim_match = re.match(r'(\d+(?:\.\d+)?)\s*(?:\(([0-9,\s]+)\))?', part.strip())
        if not dim_match:
            return None

        dimension = float(dim_match.group(1))
        dimensions.append(dimension)

        # Parse edge bands
        if dim_match.group(2):
            bands = [float(b.strip()) for b in dim_match.group(2).split(',')]
            edge_bands[idx] = bands

    return Panel(face, tuple(dimensions), edge_bands)


def extract_from_scad(scad_file: Path) -> List[Panel]:
    """
    Render OpenSCAD file and extract cut list from ECHO output.

    Args:
        scad_file: Path to .scad file

    Returns:
        List of Panel objects
    """
    try:
        result = subprocess.run(
            ['openscad', '--render', str(scad_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        print("ERROR: OpenSCAD rendering timed out (>60s)", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: 'openscad' command not found. Is OpenSCAD installed?", file=sys.stderr)
        sys.exit(1)

    panels = []
    for line in output.split('\n'):
        panel = parse_echo_line(line)
        if panel:
            panels.append(panel)

    return panels


def extract_from_stdin() -> List[Panel]:
    """Extract cut list from stdin (piped OpenSCAD output)."""
    panels = []
    for line in sys.stdin:
        panel = parse_echo_line(line)
        if panel:
            panels.append(panel)
    return panels


def consolidate_panels(panels: List[Panel], material_map: Dict[float, str] = None) -> List[Dict]:
    """
    Consolidate duplicate panels and count quantities.

    Args:
        panels: List of Panel objects
        material_map: Material name mapping

    Returns:
        List of panel dictionaries with quantities
    """
    material_map = material_map or DEFAULT_MATERIAL_MAP
    panel_map = {}

    # First pass: number panels by face type
    face_counts: Dict[str, int] = {}
    face_current: Dict[str, int] = {}

    for panel in panels:
        face = panel.face.lower()
        face_counts[face] = face_counts.get(face, 0) + 1

    # Second pass: consolidate with numbering
    for panel in panels:
        face = panel.face.lower()

        # Determine panel number
        if face_counts[face] > 1:
            face_current[face] = face_current.get(face, 0) + 1
            panel_number = face_current[face]
        else:
            panel_number = None

        # Create unique key based on dimensions, edge banding, AND face name
        # (so "Left Panel 1" and "Left Panel 2" remain separate even if same dimensions)
        key = (panel.face, panel.width, panel.height, panel.thickness,
               tuple(sorted(panel.edge_bands.items())))

        if key in panel_map:
            panel_map[key]['quantity'] += 1
        else:
            panel_dict = panel.to_dict(material_map=material_map, panel_number=panel_number)
            panel_map[key] = panel_dict

    return list(panel_map.values())


def write_csv(panels: List[Dict], output_file: Path):
    """Write cut list to CSV file."""
    if not panels:
        print("WARNING: No panels found in output", file=sys.stderr)
        return

    fieldnames = ['part_name', 'width', 'height', 'thickness', 'material', 'quantity',
                  'grain_locked', 'edge1', 'edge2', 'edge3', 'edge4', 'notes']

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(panels)

    print(f"Cut list written to: {output_file}")


def write_json(panels: List[Dict], output_file: Path):
    """Write cut list to JSON file."""
    with open(output_file, 'w') as f:
        json.dump({'panels': panels}, f, indent=2)

    print(f"Cut list written to: {output_file}")


def print_summary(panels: List[Dict]):
    """Print cut list summary to console."""
    print("\n=== Cut List Summary ===\n")
    print(f"Total unique panels: {len(panels)}")
    print(f"Total panels (with quantities): {sum(p['quantity'] for p in panels)}\n")

    # Group by thickness
    by_thickness = {}
    for panel in panels:
        thick = panel['thickness']
        if thick not in by_thickness:
            by_thickness[thick] = []
        by_thickness[thick].append(panel)

    for thick in sorted(by_thickness.keys()):
        panel_list = by_thickness[thick]
        total_qty = sum(p['quantity'] for p in panel_list)
        total_area = sum(p['width'] * p['height'] * p['quantity'] / 1_000_000 for p in panel_list)
        print(f"{thick}mm panels: {total_qty} total ({len(panel_list)} unique)")
        print(f"  Total area: {total_area:.2f} m²\n")

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
                total_edge_length += length * qty / 1000  # Convert to meters

    if total_edge_length > 0:
        print(f"Total edge banding: {total_edge_length:.1f}m\n")


def main():
    parser = argparse.ArgumentParser(
        description='Extract cut list from woodworkers-lib OpenSCAD files'
    )
    parser.add_argument('input', nargs='?', help='.scad file to process')
    parser.add_argument('-o', '--output', help='Output file (CSV or JSON)')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                        help='Output format (default: csv)')
    parser.add_argument('--stdin', action='store_true',
                        help='Read from stdin instead of rendering .scad file')
    parser.add_argument('--no-consolidate', action='store_true',
                        help='Do not consolidate duplicate panels')

    args = parser.parse_args()

    # Extract panels
    if args.stdin:
        panels = extract_from_stdin()
    elif args.input:
        scad_file = Path(args.input)
        if not scad_file.exists():
            print(f"ERROR: File not found: {scad_file}", file=sys.stderr)
            sys.exit(1)
        panels = extract_from_scad(scad_file)
    else:
        parser.print_help()
        sys.exit(1)

    if not panels:
        print("No panels found in output", file=sys.stderr)
        sys.exit(1)

    # Material mapping
    material_map = DEFAULT_MATERIAL_MAP

    # Consolidate duplicates (or convert to dicts without consolidation)
    if not args.no_consolidate:
        panel_dicts = consolidate_panels(panels, material_map=material_map)
    else:
        # No consolidation - number panels individually
        face_counts: Dict[str, int] = {}
        face_current: Dict[str, int] = {}
        for panel in panels:
            face = panel.face.lower()
            face_counts[face] = face_counts.get(face, 0) + 1

        panel_dicts = []
        for panel in panels:
            face = panel.face.lower()
            if face_counts[face] > 1:
                face_current[face] = face_current.get(face, 0) + 1
                panel_number = face_current[face]
            else:
                panel_number = None
            panel_dicts.append(panel.to_dict(material_map=material_map, panel_number=panel_number))

    # Print summary
    print_summary(panel_dicts)

    # Write output
    if args.output:
        output_file = Path(args.output)
        if args.format == 'csv':
            write_csv(panel_dicts, output_file)
        else:
            write_json(panel_dicts, output_file)
    else:
        # Print to stdout
        if args.format == 'csv':
            fieldnames = ['part_name', 'width', 'height', 'thickness', 'quantity',
                          'edge1', 'edge2', 'edge3', 'edge4', 'notes']
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(panel_dicts)
        else:
            print(json.dumps({'panels': panel_dicts}, indent=2))


if __name__ == '__main__':
    main()
