# Example Output: Simple OpenSCAD File

## Input File: `workshop/tool-stations/drill-press-station.scad`

```openscad
include <BOSL2/std.scad>
use <lib/labels.scad>

/* [Dimensions] */
base_width = 600;      // Base width in mm
base_depth = 400;      // Base depth in mm
base_height = 100;     // Base height in mm

/* [Display] */
show_labels = true;    // Show part labels

module drill_press_base() {
    diff()
    cuboid([base_width, base_depth, base_height])
        attach(TOP) tag("remove") cyl(d=50, h=20);
}

module drill_press_shelf() {
    cuboid([base_width - 100, base_depth - 50, 18]);
}

module main() {
    drill_press_base();
    up(base_height + 200) drill_press_shelf();
}

main();
```

## Output

```
========================================
OpenSCAD File Context: drill-press-station.scad
========================================

File: /Users/dawiddutoit/projects/play/plans/workshop/tool-stations/drill-press-station.scad
Size: 0.8 KB
Lines: 31

Dependency Tree:
----------------
drill-press-station.scad
├── BOSL2/std.scad (system library)
│   ├── BOSL2/transforms.scad
│   ├── BOSL2/attachments.scad
│   ├── BOSL2/shapes3d.scad
│   └── BOSL2/boolean.scad
└── lib/labels.scad (project lib)

Dependencies Loaded: 6 files
Max Depth Reached: 2 levels

Available Modules (Public):
----------------------------
- drill_press_base() - Base platform with mounting hole
- drill_press_shelf() - Storage shelf
- main() - Entry point module

Available Functions (Public):
------------------------------
- None

Customizer Parameters:
----------------------
/* [Dimensions] */
base_width = 600;      // Base width in mm
base_depth = 400;      // Base depth in mm
base_height = 100;     // Base height in mm

/* [Display] */
show_labels = true;    // Show part labels

Configuration Variables:
------------------------
None (all parameters in customizer)

BOSL2 Functions Available:
---------------------------
(from BOSL2/std.scad - common subset)
Transforms: up(), down(), left(), right(), fwd(), back()
Attachments: attach(), tag(), diff()
Shapes: cuboid(), cyl(), cube(), cylinder()
Boolean: diff(), union(), intersection()

Key Insights:
-------------
✓ Simple 3-module design
✓ Uses BOSL2 attachments (diff/attach/tag)
✓ Parametric via customizer
✓ Entry point: main()
✓ No complex dependencies

Next Steps:
-----------
- Adjust customizer parameters to resize
- Add more shelf levels with up()
- Customize hole pattern with attach()
- Add labels using lib/labels.scad module
========================================
```

## Key Features Demonstrated

1. **Simple dependency tree** - Only 2 direct dependencies, 6 total files
2. **Customizer sections** - Two sections: Dimensions and Display
3. **Public modules** - All modules are public (no underscore prefix)
4. **No custom functions** - Uses BOSL2 functions only
5. **Entry point pattern** - `main()` module called at bottom
6. **BOSL2 integration** - Uses diff(), attach(), tag() for boolean operations
7. **Parametric design** - All dimensions configurable via customizer

## Parsing Notes

**Dependencies extracted:**
- Line 1: `include <BOSL2/std.scad>` → Resolved to `~/Documents/OpenSCAD/libraries/BOSL2/std.scad`
- Line 2: `use <lib/labels.scad>` → Resolved to `{project_root}/lib/labels.scad`

**Modules extracted:**
- Line 14: `module drill_press_base()`
- Line 20: `module drill_press_shelf()`
- Line 24: `module main()`

**Customizer sections:**
- Line 4: `/* [Dimensions] */` → Section marker
- Lines 5-7: Parameters (base_width, base_depth, base_height)
- Line 9: `/* [Display] */` → Section marker
- Line 10: Parameter (show_labels)

**No circular dependencies detected** - Simple linear dependency chain
