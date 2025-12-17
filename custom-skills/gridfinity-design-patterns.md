---
identifier: gridfinity-design-patterns
type: knowledge
description: Gridfinity standard dimensions, formulas, and design patterns for bins, baseplates, and storage systems
version: 1.0.0
tags: [gridfinity, storage, design, parametric, dimensions]
---

# Gridfinity Design Patterns

## Fundamental Grid Unit
The Gridfinity system is based on a 42mm base unit that divides evenly for modular storage.

### Base Unit: 42mm x 42mm
This is the fundamental building block. All other dimensions derive from multiples of 42mm.

## Baseplate Dimensions

Baseplates are standard modular sizes for mounting bins:

| Grid | Dimensions | Cells | Use Case |
|------|------------|-------|----------|
| 1x1 | 42mm x 42mm | 1 | Single small item |
| 2x2 | 84mm x 84mm | 4 | Compact storage |
| 3x3 | 126mm x 126mm | 9 | Small drawer |
| 4x4 | 168mm x 168mm | 16 | Medium drawer |
| 5x5 | 210mm x 210mm | 25 | Large drawer |
| 6x6 | 252mm x 252mm | 36 | Standard drawer |
| 7x7 | 294mm x 294mm | 49 | Large drawer |

Calculate cell count: `grid_x * grid_y = total_cells`

## Height Units (7mm per unit)

Heights are measured in 7mm units for consistent stacking:

| Height Units | Millimeters | Use Case |
|--------------|------------|----------|
| 3u | 21mm | Shallow (screws, small parts) |
| 5u | 35mm | Standard small (electronics, clips) |
| 7u | 49mm | Medium (batteries, drill bits) |
| 10u | 70mm | Large (tools, components) |

## Bin Design Formulas

### Outer Dimensions
```openscad
// Calculate bin outer dimensions
bin_width = (grid_units_x * 42) - 0.5;    // e.g., 2x = 83.5mm
bin_depth = (grid_units_y * 42) - 0.5;    // Subtract 0.5mm clearance
bin_height = height_units * 7;             // e.g., 5u = 35mm
```

### Critical Tolerances
| Dimension | Value | Purpose |
|-----------|-------|---------|
| Bin clearance | 0.5mm total (0.25mm per side) | Loose fit between bin and baseplate |
| Corner radius | 4.65mm | Standard Gridfinity rounded corners |
| Wall thickness | 1.5mm - 2mm | Strong 3D-printed walls |
| Bottom thickness | 1.5mm - 2mm | Durable bottom |

### Lip/Tab Design
Gridfinity bins have a lip that grips the baseplate:

```openscad
// Lip dimensions (from Gridfinity spec)
lip_height = 2.4mm;      // Height of bottom lip
lip_inset = 2.0mm;       // Inset from edge
lip_thickness = 1.5mm;   // Thickness of lip
```

### Magnet Pocket (Optional)
For magnetic attachment to metal baseplates:

```openscad
// Standard 6x2mm magnet pockets
magnet_hole_diameter = 6.5mm;  // Tolerance fit for 6mm magnets
magnet_hole_depth = 2.4mm;     // Flush with bottom
magnet_recess_corner = 4.65mm; // Corner radius in pockets
```

## Common Bin Configurations

### Small Bins (for screws, electronics)
```openscad
bin_x = 1;              // 1 grid unit wide
bin_y = 1;              // 1 grid unit deep
height_u = 3;           // 3u height = 21mm

bin_width = 41.5;       // 42 - 0.5
bin_depth = 41.5;
bin_height = 21;        // 3 * 7
```

### Standard Drawer Bins (12x12 grid)
```openscad
bin_x = 12;             // 12 grid units
bin_y = 12;             // 12 grid units
height_u = 5;           // 5u height = 35mm

bin_width = 503.5;      // (12 * 42) - 0.5
bin_depth = 503.5;
bin_height = 35;        // 5 * 7

// This fits standard 506mm x 506mm drawer space (2mm clearance)
```

### Drawer Stack Spacing
For stacked drawers with slides:

```openscad
drawer_internal_width = 506;    // Net interior space
drawer_internal_depth = 506;

// Gridfinity grid to fit inside:
grid_units = 12;                // 12x12 grid
grid_total = 504;               // 12 * 42

// Clearance: (506 - 504) / 2 = 1mm per side

// Drawer slides require additional clearance:
slide_clearance_per_side = 13;  // Typical ball-bearing slide
drawer_wall_thickness = 18;     // Common 3/4" plywood equivalent
```

## Baseplate Pocket Design

Gridfinity baseplates have a grid of mounting pockets:

```openscad
// Pocket dimensions (for bin lips to grip)
pocket_width = 42;              // Matches grid unit
pocket_depth = 42;
pocket_height = 2.4;            // Lip height
pocket_lip_clearance = 0.5;     // 0.5mm gap for bin to settle

// Pocket spacing (center to center)
pocket_spacing = 42;            // Exact grid unit spacing
```

## Design Workflow Pattern

### 1. Determine Cabinet Constraints
```openscad
cabinet_interior_width = 506;
cabinet_interior_depth = 506;

// Calculate maximum grid
max_grid = floor(cabinet_interior_width / 42);  // = 12
```

### 2. Calculate Bin Outer Dimensions
```openscad
grid_x = 12;
grid_y = 12;
height_units = 5;

outer_width = (grid_x * 42) - 0.5;
outer_depth = (grid_y * 42) - 0.5;
outer_height = height_units * 7;
```

### 3. Plan Wall Thickness
```openscad
wall_thickness = 2;        // 2mm walls
bottom_thickness = 2;      // 2mm floor

// Interior becomes:
inner_width = outer_width - (2 * wall_thickness);
inner_depth = outer_depth - (2 * wall_thickness);
inner_height = outer_height - bottom_thickness;
```

### 4. Design Interior Layout
Based on inner dimensions, plan compartments, dividers, and features.

## Integration with Cabinet Drawers

For a drawer stack with multiple bins:

```openscad
// Drawer specifications
num_drawers = 8;
drawer_width_internal = 506;
drawer_depth_internal = 506;

// Gridfinity grid per drawer
gridfinity_units = 12;  // 12x12 fits in 506mm

// Total storage capacity
cells_per_drawer = gridfinity_units * gridfinity_units;
total_cells = num_drawers * cells_per_drawer;

// Example: 8 drawers × 144 cells = 1,152 total Gridfinity cells
```

## Quick Reference Formulas

```openscad
// Grid spacing
spacing_mm = grid_units * 42;

// Interior space (approximation)
interior_x = bin_outer_x - (2 * wall_thickness);
interior_y = bin_outer_y - (2 * wall_thickness);
interior_z = bin_outer_z - bottom_thickness;

// Height in millimeters
height_mm = height_units * 7;

// Total volume (for capacity planning)
volume_mm3 = interior_x * interior_y * interior_z;

// Number of cells (grid points)
total_cells = grid_x_units * grid_y_units;
```

## Material & Print Settings Recommendations

### For 3D Printed Bins
- **Minimum wall thickness:** 1.5mm (2mm preferred)
- **Layer height:** 0.2mm (0.1mm for better lip fit)
- **Infill:** 15-20% (bins are primarily structural walls)
- **Support:** Minimal if printed right-side-up

### For Machined/Laser-Cut Bins
- **Material:** Acrylic, wood, aluminum
- **Wall thickness:** Match original 3D print specs (1.5-2mm equivalent)
- **Finish:** Deburr all edges for smooth sliding

### For Baseplates
- **3D Print Infill:** 100% (structural integrity)
- **Pocket depth tolerance:** ±0.2mm (critical for bin fit)
- **Material:** PETG or ASA (more durable than PLA for baseplate wear)
