---
identifier: openscad-code-organization
type: instruction
description: OpenSCAD code organization patterns, file structure, customizer conventions, and module design
version: 1.0.0
tags: [openscad, organization, conventions, code-structure, customizer]
---

# OpenSCAD Code Organization

## File Structure Pattern

Standard project structure for OpenSCAD files:

```
project/
├── src/
│   ├── main.scad              # Entry point, parameter definitions
│   ├── modules/
│   │   ├── cabinet.scad       # Cabinet assembly module
│   │   ├── drawer.scad        # Drawer box modules
│   │   ├── _helpers.scad      # Private helper functions
│   │   └── _joinery.scad      # Joinery and construction helpers
│   ├── lib/                   # Project-specific libraries
│   └── examples/
│       ├── bosl2_demo.scad    # BOSL2 feature demonstrations
│       └── python_example.py  # SolidPython2 examples
├── lib/                       # Local project libraries
├── stl/                       # Rendered STL output files
└── images/                    # Preview PNG images
```

## Main File Template

Structure for the primary OpenSCAD file with proper sections:

```openscad
// ============================================================================
// Project Name: Brief Description
// Version: 1.0.0
// Purpose: What this model does
// ============================================================================

// ============ LIBRARY INCLUDES ============
include <BOSL2/std.scad>
include <BOSL2/gears.scad>      // Add as needed
use <MCAD/stepper.scad>

// ============ CUSTOMIZER SECTIONS ============

/* [Main Parameters] */
// Overall width of assembly
width = 40;
// Overall depth of assembly
depth = 30;
// Overall height of assembly
height = 20;

/* [Hole Parameters] */
// Hole diameter
hole_d = 8;
// Hole depth
hole_depth = 15;

/* [Material & Color] */
// Primary color (RGB normalized)
color_primary = [0.8, 0.2, 0.2];
// Secondary color (RGB normalized)
color_secondary = [0.2, 0.8, 0.2];

/* [Rendering] */
// Preview quality ($fn for preview)
$preview_fn = 32;
// Render quality ($fn for final render)
$render_fn = 64;

/* [Display] */
// Show component A
show_a = true;
// Show component B
show_b = true;
// Explode view distance (0 = closed)
explode = 0;

// ============ GLOBAL SETTINGS ============

// Preview-aware resolution
$fn = $preview ? $preview_fn : $render_fn;

// Overlap epsilon for boolean operations
epsilon = 0.01;

// ============ CALCULATED VALUES ============
// Derived dimensions calculated from parameters
inner_width = width - 2*wall;
inner_depth = depth - 2*wall;

// ============ PRIVATE MODULES (Prefix with _) ============

// Helper for rounded corners
module _rounded_box(w, d, h, r) {
    diff()
    cuboid([w, d, h], rounding=r, edges="Z")
        tag("remove")
        sphere(r=r, $fn=$fn);
}

// Hole pattern helper
module _hole_pattern(count, spacing) {
    for(i = [0:count-1])
        translate([i*spacing, 0, 0])
            cylinder(d=hole_d, h=hole_depth, center=true);
}

// ============ PUBLIC MODULES ============

// Main assembly - combines all components
module main() {
    if (show_a) component_a();
    if (show_b) up(height + explode) component_b();
}

// Component A: description
module component_a() {
    color(color_primary)
    diff()
    cuboid([width, depth, height/2], rounding=3, edges="Z")
        attach(TOP) tag("remove") _hole_pattern(2, 10);
}

// Component B: description
module component_b() {
    color(color_secondary)
    cuboid([width, depth, height/4]);
}

// ============ ENTRY POINT ============
main();
```

## Customizer Parameter Conventions

### Bracket Section Comments
Always use bracketed section comments for Customizer organization:

```openscad
/* [Section Name] */
// Short description (max ~80 chars)
parameter_name = default_value;
```

### Customizer Best Practices

1. **Group related parameters** in logical sections
2. **Provide meaningful descriptions** as comments
3. **Set sensible defaults** that work out-of-box
4. **Use dropdown syntax** for enums:
   ```openscad
   /* [Quality] */
   // Resolution level
   quality = "medium"; // [low, medium, high]
   ```
5. **Range validation** via naming:
   ```openscad
   /* [Constraints] */
   // Wall thickness (1-5mm)
   wall = 2;
   ```

## Module Naming Conventions

| Pattern | Use Case | Example |
|---------|----------|---------|
| `module_name()` | Public module, used in assembly | `cabinet_shell()` |
| `_helper_name()` | Private helper function | `_dado_profile()` |
| `demo_feature()` | Demo/example module | `demo_attachments()` |
| UPPERCASE | Constants (non-parameterizable) | `EPSILON = 0.01` |

## Boolean Operation Pattern

Preferred pattern using BOSL2's diff() with tagging:

```openscad
// Create solid with removals
diff()
cuboid([width, depth, height], rounding=3)
    // Tag all removal features
    attach(TOP) tag("remove") cyl(d=8, h=height+1)
    attach(FRONT) tag("remove") cuboid([width-2, 5, 5])
    attach([corners]) tag("remove") sphere(d=5);
```

## Assembly and Explosion Pattern

For complex assemblies with show/hide and explode view:

```openscad
// Parameters for display
show_frame = true;
show_panels = true;
show_hardware = true;
explode_z = 0;      // Vertical explosion
explode_xy = 0;     // Horizontal explosion

// Assembly module
module assembly() {
    if (show_frame)
        frame_structure();

    if (show_panels)
        up(explode_z)
        panels();

    if (show_hardware)
        translate([0, 0, explode_z + 5])
        hardware_set();
}
```

## Comment Organization Hierarchy

```openscad
// ============================================================================
// SECTION HEADER (use for major divisions)
// ============================================================================

// ===== Subsection Header (use for logical groups)

// Single line comments for specific lines/parameters
```

## Parametric Module Pattern

For reusable, parametric modules:

```openscad
// Parametric drawer box with sensible defaults
module drawer_box(
    width = 100,
    depth = 150,
    height = 50,
    wall = 3,
    bottom = 3
) {
    outer_w = width + 2*wall;
    outer_d = depth + 2*wall;
    outer_h = height + bottom;

    diff()
    cuboid([outer_w, outer_d, outer_h], anchor=BOTTOM)
        tag("remove")
        up(bottom)
        cuboid([width, depth, height+epsilon], anchor=BOTTOM);
}

// Usage with defaults
drawer_box();

// Usage with custom values
drawer_box(width=120, depth=180, height=60, wall=4);
```

## Advanced Organization: Joinery Pattern

For projects with complex joints (dado, rabbets, etc.):

```openscad
// Separate file: src/modules/_joinery.scad

// Calculate dado positions
function dado_x_positions() = [
    section1_width - panel,
    section1_width + section2_width - 2*panel
];

// Reusable dado cutter
module dado_cutter(x_pos, width, depth, height) {
    translate([x_pos, -1, -dado_depth])
    cube([width, depth+2, dado_depth+1]);
}

// Apply dados to panel
module panel_with_dados(base_dims, dado_list) {
    difference() {
        cube(base_dims);
        for(dado = dado_list)
            dado_cutter(dado[0], dado[1], dado[2], dado[3]);
    }
}
```

## Modular Import Pattern

Use `use` and `include` strategically:

```openscad
// main.scad - master file

// Full library import (all functions/modules available)
include <BOSL2/std.scad>

// Conditional module imports
use <src/modules/drawer.scad>
use <src/modules/cabinet.scad>
use <src/modules/_joinery.scad>

// Local custom library
use <lib/hardware.scad>
```

## Performance Optimization

### 1. Use Preview-Aware $fn
```openscad
$fn = $preview ? 32 : 64;  // Fast preview, quality render
```

### 2. Conditionally Render Components
```openscad
/* [Display] */
show_frame = true;
show_hardware = true;

if (show_frame) frame();
if (show_hardware) hardware();
```

### 3. Recursive Operations (Avoid in Preview)
```openscad
// For expensive operations
if (!$preview) {
    complex_pattern_recursion();
}
```

## Version Control Best Practices

Include version info and comments:

```openscad
// VERSION: 1.2.3
// Last Modified: 2024-12-16
// Known Issues: Tolerance on 506mm drawer is tight at 0.5mm
// Next: Add magnetic pocket support
```

## Documentation Comment Block

For complex modules, include parameter documentation:

```openscad
// Creates a parametric bin matching Gridfinity spec
//
// Parameters:
//   grid_x (int)    - Grid units wide (42mm per unit)
//   grid_y (int)    - Grid units deep (42mm per unit)
//   height_u (int)  - Height in 7mm units (e.g., 5u = 35mm)
//   wall (float)    - Wall thickness in mm (default 2)
//   has_lip (bool)  - Include Gridfinity lip (default true)
//
// Returns: Solid bin module ready for printing
module gridfinity_bin(grid_x, grid_y, height_u, wall=2, has_lip=true) {
    // Implementation...
}
```
