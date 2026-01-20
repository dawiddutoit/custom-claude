# Example Output: Complex Multi-Dependency Project File

## Input File: `workshop/workbenches/mini-workbench.scad`

Complex file with multiple dependencies, framework integration, and assembly patterns.

## Output

```
========================================
OpenSCAD File Context: mini-workbench.scad
========================================

File: /Users/dawiddutoit/projects/play/plans/workshop/workbenches/mini-workbench.scad
Size: 15.2 KB
Lines: 450

Dependency Tree:
----------------
mini-workbench.scad
├── lib/assembly-framework.scad (project lib)
│   ├── lib/materials.scad (project lib)
│   └── woodworkers-lib/std.scad (system library)
│       ├── woodworkers-lib/planes.scad
│       ├── woodworkers-lib/cutlist.scad
│       ├── woodworkers-lib/dimensions.scad
│       └── BOSL2/std.scad (system library)
│           ├── BOSL2/transforms.scad
│           ├── BOSL2/attachments.scad
│           ├── BOSL2/shapes3d.scad
│           └── [... 15 more BOSL2 files, max depth reached]
├── BOSL2/std.scad (already loaded)
└── lib/labels.scad (project lib)
    └── BOSL2/std.scad (already loaded)

Dependencies Loaded: 18 files (3 deduplicated)
Max Depth Reached: 4 levels (stopped at BOSL2 internals)

Available Modules (Public):
----------------------------
- mini_workbench() - Main assembly combining all components
- cabinet_shell() - Outer cabinet box (18mm plywood)
- dividers() - Vertical section dividers with runner clearance
- drawer_stack(section_width, x_start, drawer_start=0) - Parametric drawer stack
- drawer_tall(section_width, x_start) - Single tall drawer assembly
- tray_side_access(section_width, x_start, open_side="right") - Side-opening tray with shelf
- runners(section_width, x_start, y_positions) - Drawer runner pairs
- _drawer_box_with_runners(width, height, y_pos) - Internal helper for drawer construction
- _faceplate(width, height, reveal_top=0.05) - Internal helper for drawer faces

Available Functions (Public):
------------------------------
None (uses assembly framework functions)

Private Helpers (9):
--------------------
(Modules prefixed with _ for internal use)
- _drawer_box_with_runners()
- _faceplate()
- _calculate_reveal()
- _runner_y_position()
- _section_bounds()
- _validate_section()
- _drawer_dimensions()
- _faceplate_overlay()
- _cutlist_entry()

Customizer Parameters:
----------------------
/* [Display Options] */
show_cabinet = true;         // Show cabinet shell
show_drawers = true;         // Show drawer boxes
show_faceplates = true;      // Show drawer faces
show_runners = true;         // Show drawer runners
show_dividers = true;        // Show vertical dividers
show_labels = false;         // Show part labels (debug)

/* [Dimensions] */
total_width = 1650;          // Assembly total width
assembly_height = 500;       // Internal height (cabinet body)
assembly_depth = 580;        // Front-to-back depth

/* [Advanced] */
panel_thickness = 18;        // Wall panel thickness
runner_thickness = 13;       // Runner side thickness
drawer_wall = 9;             // Drawer box wall thickness
reveal_gap = 0.05;           // Gap between faceplates

Configuration Variables:
------------------------
(Set AFTER include statements, overriding framework defaults)

ASMFW_SECTION_IDS = ["A", "B", "C", "D", "E"]
ASMFW_SECTION_WIDTHS = [253, 562, 562, 153, 120]
ASMFW_TOTAL_WIDTH = 1650
ASMFW_ASSEMBLY_HEIGHT = 500
ASMFW_ASSEMBLY_DEPTH = 580
ASMFW_PANEL_THICKNESS = 18
ASMFW_RUNNER_THICKNESS = 13
ASMFW_DRAWER_WALL = 9
ASMFW_DRAWER_BOTTOM = 6
ASMFW_REVEAL_GAP = 0.05

Calculated Section Internals:
------------------------------
(Using framework functions)

sa_int = asmfw_section_internal_width("A")  // → 235mm
sb_int = asmfw_section_internal_width("B")  // → 544mm
sc_int = asmfw_section_internal_width("C")  // → 544mm
sd_int = asmfw_section_internal_width("D")  // → 135mm
se_int = asmfw_section_internal_width("E")  // → 102mm

Calculated Divider Positions:
------------------------------
div1_x = asmfw_section_x_end("A") - runner_thickness  // → 240mm
div2_x = asmfw_section_x_end("B") - runner_thickness  // → 802mm
div3_x = asmfw_section_x_end("C") - runner_thickness  // → 1364mm
div4_x = asmfw_section_x_end("D") - runner_thickness  // → 1517mm

Framework Functions Available:
-------------------------------
(from lib/assembly-framework.scad)

Section Dimensions:
- asmfw_section_internal_width(section_id) → width excluding panels
- asmfw_section_x_start(section_id) → X coordinate of section start
- asmfw_section_x_end(section_id) → X coordinate of section end
- asmfw_section_bounds(section_id) → [x_start, x_end, internal_width]

Drawer Calculations:
- asmfw_drawer_box_width(section_id) → drawer box width with runner clearance
- asmfw_faceplate_width(section_id) → faceplate width with reveals and overlay
- asmfw_drawer_box_height(faceplate_height) → drawer box height from faceplate

Runner Positioning:
- asmfw_runner_x_positions(section_id) → [left_x, right_x]

Validation:
- asmfw_validate_assembly(verbose=false) → check configuration consistency

Woodworkers-Lib Functions:
---------------------------
(from woodworkers-lib/std.scad)

Plane Modules (declarative panel construction):
- planeBottom(dim, l=0, r=0, f=0, b=0, thick=18)
- planeTop(dim, l=0, r=0, f=0, b=0, thick=18)
- planeLeft(dim, f=0, b=0, t=0, b=0, thick=18)
- planeRight(dim, f=0, b=0, t=0, b=0, thick=18)
- planeFront(dim, l=0, r=0, t=0, b=0, thick=18)
- planeBack(dim, l=0, r=0, t=0, b=0, thick=18)

Cutlist Integration:
- ww_part(name, dim, material, quantity=1)
- ww_cutlist_export() → echo all parts for extraction

BOSL2 Core Functions:
----------------------
(from BOSL2/std.scad - commonly used subset)

Transforms: up(), down(), left(), right(), fwd(), back(), move(), rot()
Attachments: attach(), position(), tag(), diff(), recolor()
Shapes: cuboid(), cyl(), prismoid(), rect_tube()
Boolean: diff(), union(), intersection(), hull()
Math: lerp(), clamp(), constrain(), modang()
Lists: select(), slice(), reverse(), shuffle()

Key Insights:
-------------
✓ Uses assembly-framework.scad for automatic positioning
✓ 5-section cabinet design (A=tall drawer, B/C=stacks, D=tray, E=narrow)
✓ Drawer stacks in sections B (4 drawers) and C (4 drawers)
✓ Side-access tray in section D with internal shelf
✓ All dimensions driven by framework configuration arrays
✓ Declarative planes via woodworkers-lib (no manual cube positioning)
✓ 9 private helper modules (good encapsulation)
✓ Customizer enables visual debugging (show/hide components)
✓ Framework handles all X positioning and width calculations
✓ Dividers automatically positioned at section boundaries

Architecture Pattern:
---------------------
1. Configuration Layer: ASMFW_* variables define section layout
2. Calculation Layer: Framework functions compute positions/widths
3. Component Layer: Modules use framework values (no manual math)
4. Assembly Layer: mini_workbench() combines all components
5. Entry Point: main() with customizer conditionals

Dependencies Explanation:
--------------------------
- assembly-framework.scad: Core positioning/calculation framework
  └── materials.scad: Material definitions (plywood, hardwood)
  └── woodworkers-lib: Declarative plane-based construction
      └── BOSL2: Geometric primitives and attachments

- BOSL2/std.scad: Imported directly for transforms and shapes
- lib/labels.scad: Optional text labels (when show_labels=true)
  └── BOSL2: Text primitives

Next Steps:
-----------
- Modify ASMFW_SECTION_WIDTHS to resize sections
- Add/remove drawers in drawer_stack() calls
- Adjust drawer heights in row arrays
- Change tray shelf position (shelf_position parameter)
- Toggle customizer display options for debugging
- Extract cutlist with cutlist-optimizer CLI
- Add labels to parts for assembly reference

Integration Points:
-------------------
- Cutlist extraction: Uses ww_part() for all components
- Labels: Uses labeled_cuboid() from lib/labels.scad
- Framework: Validates configuration with asmfw_validate_assembly()
- Materials: References materials.scad constants (PLYWOOD_18MM, etc.)

Common Operations:
------------------
1. Resize section: Change value in ASMFW_SECTION_WIDTHS array
2. Add drawer: Append height to drawer_stack rows array
3. Move divider: Adjust runner_thickness in calculation
4. Change reveals: Modify ASMFW_REVEAL_GAP constant
5. Debug positioning: Enable show_labels customizer param
========================================
```

## Key Differences from Simple Example

1. **Complex dependency tree** - 18 files across 4 depth levels
2. **Framework integration** - Uses assembly-framework.scad for automated positioning
3. **Multiple libraries** - BOSL2, woodworkers-lib, plus custom project libs
4. **Calculated values** - Section internals and divider positions computed from framework
5. **Private helpers** - 9 internal modules (good encapsulation practice)
6. **Configuration-driven** - Large ASMFW_* variable arrays define structure
7. **Three customizer sections** - Display, Dimensions, Advanced
8. **Declarative assembly** - Uses planes pattern, not manual cube positioning

## Complexity Metrics

- **Total files:** 18 (3 deduplicated, 21 total references)
- **Dependency depth:** 4 levels
- **Public modules:** 7
- **Private modules:** 9
- **Framework functions:** 10
- **Customizer parameters:** 12 (across 3 sections)
- **Configuration variables:** 10
- **Calculated values:** 9 (section widths, divider positions)

## Analysis Insights

**Framework pattern detected:**
- Configuration arrays define structure
- Framework calculates all positions
- Modules use framework functions (no manual math)
- Enables easy reconfiguration without touching module code

**Woodworkers-lib integration:**
- Uses declarative plane pattern
- All panels defined by bounding box + insets
- Automatic cutlist generation via ww_part()

**BOSL2 usage:**
- Transforms for positioning (up, down, left, right)
- Boolean operations (diff, tag, attach)
- Shapes (cuboid, cyl)

**Customizer design:**
- Display toggles for debugging (show_*)
- Dimension parameters for sizing
- Advanced section for material constants
- Good separation of concerns
