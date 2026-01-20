# OpenSCAD Collision Detection Technical Reference

Technical depth, mathematical foundations, and advanced patterns for collision detection.

## Table of Contents

1. [Boolean Operations Theory](#boolean-operations-theory)
2. [Geometry Engine Comparison](#geometry-engine-comparison)
3. [Mathematical Clearance Calculations](#mathematical-clearance-calculations)
4. [Performance Optimization](#performance-optimization)
5. [Color Theory for Visualization](#color-theory-for-visualization)
6. [Integration Patterns](#integration-patterns)
7. [Validation Checklists](#validation-checklists)
8. [Advanced Techniques](#advanced-techniques)

## Boolean Operations Theory

### CSG (Constructive Solid Geometry)

OpenSCAD uses CSG modeling where complex shapes are built from primitives using boolean operations.

#### Core Operations

| Operation | Symbol | Description | Collision Detection Use |
|-----------|--------|-------------|------------------------|
| `union()` | ∪ | Combine volumes | Show all parts |
| `difference()` | - | Subtract volumes | Create cutouts |
| `intersection()` | ∩ | Keep only overlaps | **Reveal collisions** |

#### intersection() Deep Dive

```openscad
intersection() {
    cube([50, 50, 50]);
    translate([25, 25, 25]) sphere(r=30, $fn=32);
}
```

**How it works:**
1. Compute both geometries independently
2. Find overlapping volume using CSG tree evaluation
3. Return only the shared region
4. If result is empty → no collision
5. If result has volume → collision exists

**Mathematical representation:**
```
V_collision = V₁ ∩ V₂
where V₁, V₂ are solid volumes
```

### Topology Considerations

#### Manifold vs Non-Manifold Geometry

**Manifold geometry:**
- Every edge connects exactly 2 faces
- No zero-thickness walls
- Watertight volumes
- **Preferred for collision detection**

**Non-manifold geometry:**
- Edges connect 3+ faces or 1 face
- Zero-thickness surfaces
- May cause false collision positives
- Common with imported STL files

**Fix non-manifold issues:**
```bash
# Use Manifold engine (default in 2025)
openscad --backend Manifold model.scad

# Fallback to CGAL if issues
openscad --backend CGAL model.scad
```

## Geometry Engine Comparison

### Manifold vs CGAL

| Feature | Manifold (2025 Default) | CGAL (Legacy) |
|---------|------------------------|---------------|
| **Speed** | 10-100x faster | Baseline |
| **Precision** | Floating point (fast) | Exact arithmetic (slow) |
| **Edge cases** | Better with non-manifold | Strict manifold only |
| **Intersection accuracy** | Very good | Exact |
| **Preview performance** | Excellent | Good |
| **Render performance** | Excellent | Poor |
| **Recommended for collision** | ✅ Yes | Fallback only |

### When to Use CGAL

Use `--backend CGAL` only if:
1. Manifold produces incorrect intersection results
2. Working with extremely precise mechanical fits (<0.01mm)
3. Debugging suspected engine bug
4. Legacy compatibility required

### Engine Selection

```bash
# Command line
openscad --backend Manifold model.scad    # Default
openscad --backend CGAL model.scad        # Fallback

# In .scad file (not possible - set via CLI or preferences)
```

## Mathematical Clearance Calculations

### Drawer Clearances

#### Side Clearance (Horizontal)

```
Given:
  cabinet_width = W_c
  panel_thickness = t_p
  drawer_width = W_d

Interior width:
  W_i = W_c - 2·t_p

Total clearance:
  C_total = W_i - W_d

Per-side clearance:
  C_side = (W_i - W_d) / 2

Constraint:
  C_side ≥ 2mm (minimum for smooth operation)
```

**OpenSCAD implementation:**
```openscad
cabinet_width = 800;
panel = 18;
drawer_width = 764;

interior_width = cabinet_width - 2*panel;  // 764
clearance_total = interior_width - drawer_width;  // 0
clearance_side = clearance_total / 2;  // 0

assert(clearance_side >= 2,
       str("Side clearance (", clearance_side, "mm) < 2mm minimum"));
```

#### Depth Clearance

```
Given:
  cabinet_depth = D_c
  back_panel_thickness = t_b
  drawer_depth = D_d

Interior depth:
  D_i = D_c - t_b

Depth clearance:
  C_depth = D_i - D_d

Constraint:
  C_depth ≥ 5mm (minimum for back panel)
```

#### Vertical Clearance

```
Given:
  cabinet_height = H_c
  panel_thickness = t_p
  num_drawers = n
  drawer_height = H_d

Interior height:
  H_i = H_c - 2·t_p

Available per drawer:
  H_available = H_i / n

Clearance per drawer:
  C_vertical = H_available - H_d

Constraint:
  C_vertical ≥ 5mm (minimum for smooth operation)
```

### Door Swing Calculations

#### Arc Swept by Door

```
Given:
  door_width = W_door
  swing_angle = θ (radians)
  hinge_offset = h

Arc length:
  L_arc = (W_door - h) · θ

Maximum Y displacement:
  Y_max = (W_door - h) · sin(θ)

Maximum X displacement:
  X_max = (W_door - h) · (1 - cos(θ))

For θ = 90° = π/2:
  Y_max ≈ W_door - h
  X_max ≈ W_door - h
```

**OpenSCAD visualization:**
```openscad
module door_sweep(door_width, swing_angle, hinge_offset=0) {
    radius = door_width - hinge_offset;

    linear_extrude(720)
        rotate([0, 0, -swing_angle])
        translate([hinge_offset, 0])
        square([radius, 5]);
}

door_sweep(door_width=400, swing_angle=90, hinge_offset=0);
```

#### Clearance to Adjacent Object

```
Given:
  door_width = W_door
  swing_angle = θ = 90°
  adjacent_distance = D_adj (from hinge)

Clearance:
  C = D_adj - W_door

Constraint:
  C ≥ 10mm (minimum for safe operation)
```

### Shelf Spacing

#### Uniform Spacing

```
Given:
  cabinet_height = H_c
  top_panel = t_top
  bottom_panel = t_bottom
  num_shelves = n (excluding top/bottom)
  shelf_thickness = t_s

Interior height:
  H_i = H_c - t_top - t_bottom

Spacing between shelves:
  S = H_i / (n + 1)

Available height per section:
  H_section = S - t_s

Constraint:
  H_section ≥ H_item (item height)
```

#### Non-Uniform Spacing

```
Given:
  shelf_positions = [z₀, z₁, z₂, ..., zₙ]
  shelf_thickness = t_s

For each pair (zᵢ, zᵢ₊₁):
  Available height = zᵢ₊₁ - zᵢ - t_s

Constraint:
  zᵢ₊₁ - zᵢ - t_s ≥ H_item
```

## Performance Optimization

### Preview vs Render

| Mode | Hotkey | Speed | Accuracy | Use For |
|------|--------|-------|----------|---------|
| Preview | F5 | Fast | Approximate | Collision detection |
| Render | F6 | Slow | Exact | Final validation |

**Recommendation:** Use Preview (F5) for all collision detection work.

### $fn Optimization

```openscad
// Adaptive resolution based on mode
$fn = $preview ? 16 : 64;

module fast_cylinder() {
    cylinder(d=50, h=100);  // Uses $fn from parent
}
```

**Impact on collision detection:**
- Lower $fn in preview = faster intersection computation
- Cylinders, spheres, arcs benefit most
- Rectangles/cubes unaffected

### Avoiding Nested Intersections

```openscad
// ❌ SLOW: Nested intersections
intersection() {
    intersection() {
        obj1();
        obj2();
    }
    obj3();
}

// ✅ FAST: Flat intersection
intersection() {
    obj1();
    obj2();
    obj3();
}
```

**Reason:** Each nested intersection creates new CSG tree node, increasing computation depth.

### Caching Geometry

```openscad
// ❌ SLOW: Recompute every time
module slow_check() {
    intersection() {
        complex_cabinet();  // Recomputed
        complex_drawer();   // Recomputed
    }
}

// ✅ FAST: Cache as children
module fast_check() {
    intersection() {
        children(0);  // Pre-computed
        children(1);  // Pre-computed
    }
}

fast_check() {
    complex_cabinet();
    complex_drawer();
}
```

### Disabling Complex Features

```openscad
COLLISION_CHECK_MODE = true;

module detailed_cabinet() {
    if (COLLISION_CHECK_MODE) {
        // Simple bounding box for collision detection
        cube([800, 500, 720]);
    } else {
        // Full detail for rendering
        complex_cabinet_with_details();
    }
}
```

## Color Theory for Visualization

### Additive Color Model

Overlapping transparent colors create visual feedback:

```
Red (1, 0, 0) + Green (0, 1, 0) = Yellow (1, 1, 0)
Red (1, 0, 0) + Blue (0, 0, 1) = Magenta (1, 0, 1)
Green (0, 1, 0) + Blue (0, 0, 1) = Cyan (0, 1, 1)
```

**OpenSCAD usage:**
```openscad
color("red", 0.3) drawer();     // RGB: (1, 0, 0)
color("green", 0.3) cabinet();  // RGB: (0, 1, 0)
// Overlapping regions appear yellow
```

### Recommended Color Scheme

| Object Type | Color | RGB | Alpha | Purpose |
|-------------|-------|-----|-------|---------|
| **Collision** | Red | `"red"` | 0.8 | Highlight problems |
| **Clearance zone** | Yellow | `"yellow"` | 0.2-0.3 | Show required space |
| **Moving parts** | Green | `"green"` | 0.5 | Active components |
| **Fixed structure** | Blue | `"blue"` | 0.2-0.3 | Reference geometry |
| **Reference** | Gray | `"gray"` | 0.3 | Walls, floor |
| **Hardware** | Silver | `[0.8, 0.8, 0.8]` | 0.8 | Hinges, slides |
| **Wood** | Brown | `"BurlyWood"` | 0.5 | Panels |

### Alpha Channel Best Practices

```openscad
// ❌ BAD: Opaque colors hide collisions
color("red") obj1();
color("green") obj2();

// ✅ GOOD: Transparent colors show overlaps
color("red", 0.3) obj1();
color("green", 0.3) obj2();

// ✅ BETTER: High alpha for collision, low for reference
color("blue", 0.2) reference();     // Ghost
color("red", 0.8) collision();      // Highlight
```

## Integration Patterns

### With woodworkers-lib

```openscad
include <woodworkers-lib/std.scad>

module ww_drawer_clearance_check(cabinet_dim, drawer_dim, panel=18) {
    // Cabinet shell (ghost)
    %color("blue", 0.2) {
        planeBottom(cabinet_dim);
        planeTop(cabinet_dim);
        planeLeft(cabinet_dim, t=-1, b=-1);
        planeRight(cabinet_dim, t=-1, b=-1);
        planeBack(cabinet_dim, l=-1, r=-1, t=-1, b=-1, thick=6);
    }

    // Drawer (solid)
    color("green", 0.5) {
        translate([panel, 0, panel]) {
            planeBottom(drawer_dim);
            planeTop(drawer_dim);
            planeLeft(drawer_dim, t=-1, b=-1);
            planeRight(drawer_dim, t=-1, b=-1);
            planeFront(drawer_dim, l=-1, r=-1, t=-1, b=-1);
        }
    }

    // Collision check
    interior_w = cabinet_dim[0] - 2*panel;
    interior_d = cabinet_dim[1] - panel;
    interior_h = cabinet_dim[2] - 2*panel;

    color("red") intersection() {
        translate([panel, 0, panel])
            cube([interior_w, interior_d, interior_h]);
        translate([panel, 0, panel])
            cube(drawer_dim);
    }
}
```

### With BOSL2 Attachments

```openscad
include <BOSL2/std.scad>

module bosl2_collision_check() {
    // Base object
    cuboid([100, 100, 50])
        // Attach cylinder on top
        attach(TOP) down(15)  // Penetrates 15mm
            cyl(d=30, h=30);

    // Check penetration
    color("red") intersection() {
        cuboid([100, 100, 50]);
        position(TOP) down(15) cyl(d=30, h=30);
    }
}
```

### With labels.scad

```openscad
include <lib/labels.scad>

module labeled_collision_visualization() {
    // Labeled objects for clarity
    labeled_cuboid([800, 400, 100],
        name="DRAWER",
        box_color="green",
        label_color=LABEL_COLOR_PANEL,
        name_face=TOP
    );

    translate([0, 0, 95])
    labeled_cuboid([800, 400, 18],
        name="SHELF",
        box_color="brown",
        label_color=LABEL_COLOR_DIVIDER,
        name_face=BOTTOM
    );

    // Collision check
    color("red", 0.8) intersection() {
        cube([800, 400, 100]);
        translate([0, 0, 95]) cube([800, 400, 18]);
    }
}
```

## Validation Checklists

### Pre-Fabrication Checklist

- [ ] **All clearances calculated** (side, depth, vertical)
- [ ] **Minimum clearances met** (≥2mm sides, ≥5mm top/depth)
- [ ] **No red regions in collision check**
- [ ] **Echo statements confirm dimensions**
- [ ] **Parametric validation passes** (assert statements)
- [ ] **Door swing tested at full angle**
- [ ] **Drawer extension tested at full travel**
- [ ] **Shelf spacing validated for item heights**
- [ ] **Hardware clearances checked** (hinges, slides)
- [ ] **Assembly sequence validated** (no impossible fits)

### Collision Detection Workflow

1. **Isolate** - Use `!` to test components individually
2. **Ghost** - Use `%` to show reference geometry
3. **Intersect** - Use `intersection()` to reveal overlaps
4. **Measure** - Use `echo()` to report clearances
5. **Validate** - Use `assert()` to enforce constraints
6. **Document** - Add comments explaining clearance decisions
7. **Test edge cases** - Try extreme parameter values
8. **Render final** - Use F6 for exact validation (if critical)

### Common Failure Modes

| Issue | Symptom | Detection | Fix |
|-------|---------|-----------|-----|
| **Insufficient side clearance** | Drawer binds | Red regions on sides | Reduce drawer width by 4mm |
| **Drawer hits back panel** | Can't close fully | Red at back | Reduce drawer depth |
| **Shelf spacing too tight** | Items don't fit | Red between shelves | Increase shelf spacing |
| **Door swing blocked** | Can't open fully | Red in sweep path | Reposition adjacent object |
| **Hinge interference** | Door binds | Red at hinge | Increase hinge-to-door gap |
| **Vertical stacking collision** | Drawers overlap | Red between drawers | Increase vertical spacing |

## Advanced Techniques

### Swept Volume Analysis

For moving parts, analyze entire motion path:

```openscad
module swept_volume(start_pos, end_pos, steps=10) {
    for (i = [0:steps-1]) {
        t = i / (steps - 1);
        pos = start_pos + t * (end_pos - start_pos);

        %translate(pos) children();
    }

    // Check collision at each step
    color("red", 0.3)
        for (i = [0:steps-1]) {
            t = i / (steps - 1);
            pos = start_pos + t * (end_pos - start_pos);

            intersection() {
                translate(pos) children(0);
                children(1);
            }
        }
}

// Usage
swept_volume(start_pos=[0, 0, 0], end_pos=[0, -300, 0], steps=20) {
    cube([764, 480, 100]);  // Drawer
    cabinet_interior();     // Fixed structure
}
```

### Tolerance Stack-Up Analysis

```openscad
module tolerance_analysis(nominal, tolerance_plus, tolerance_minus) {
    // Worst-case minimum
    worst_min = nominal + tolerance_minus;  // Negative tolerance

    // Worst-case maximum
    worst_max = nominal + tolerance_plus;

    echo(str("Nominal: ", nominal, "mm"));
    echo(str("Worst-case min: ", worst_min, "mm"));
    echo(str("Worst-case max: ", worst_max, "mm"));
    echo(str("Total tolerance: ", worst_max - worst_min, "mm"));

    // Visual representation
    %cube([nominal, 50, 50]);
    color("yellow", 0.3) cube([worst_max, 50, 50]);
    color("red", 0.3) cube([worst_min, 50, 50]);
}

// Example: Panel thickness 18mm ±0.5mm
tolerance_analysis(nominal=18, tolerance_plus=0.5, tolerance_minus=-0.5);
```

### Probabilistic Clearance

```openscad
module monte_carlo_clearance(iterations=100) {
    // Simulate manufacturing variation
    for (i = [0:iterations-1]) {
        // Random variation ±0.5mm
        panel_var = rands(-0.5, 0.5, 1)[0];
        drawer_var = rands(-0.5, 0.5, 1)[0];

        panel = 18 + panel_var;
        drawer_width = 764 + drawer_var;

        interior = 800 - 2*panel;
        clearance = interior - drawer_width;

        if (clearance < 2) {
            echo(str("Iteration ", i, ": FAIL (clearance=", clearance, "mm)"));
        }
    }
}

monte_carlo_clearance(iterations=1000);
// Reveals probability of clearance failure
```

### Continuous Collision Detection

For animated mechanisms:

```openscad
module continuous_collision(time) {
    // Animate drawer opening (0 to -300mm)
    drawer_pos = -300 * time;

    // Drawer
    translate([18, drawer_pos, 100])
        color("green", 0.5)
        cube([764, 480, 100]);

    // Door opening (0 to 90°)
    door_angle = 90 * time;

    translate([0, 0, 0])
        rotate([0, 0, -door_angle])
        color("blue", 0.5)
        cube([400, 18, 720]);

    // Check collision at current time
    color("red") intersection() {
        translate([18, drawer_pos, 100]) cube([764, 480, 100]);
        rotate([0, 0, -door_angle]) cube([400, 18, 720]);
    }
}

// Animate with $t (0.0 to 1.0)
continuous_collision(time=$t);
```

Run with: `openscad --animate 50 model.scad` (50 frames)

### Parametric Optimization

Find optimal dimensions automatically:

```openscad
module optimize_drawer_width(cabinet_width, target_clearance=9) {
    panel = 18;
    interior = cabinet_width - 2*panel;
    drawer_width = interior - 2*target_clearance;

    echo(str("Cabinet width: ", cabinet_width, "mm"));
    echo(str("Interior: ", interior, "mm"));
    echo(str("Optimal drawer width: ", drawer_width, "mm"));
    echo(str("Clearance per side: ", target_clearance, "mm"));

    // Validate
    assert(target_clearance >= 2, "Clearance must be ≥2mm");
    assert(drawer_width > 0, "Drawer width must be positive");

    // Visual
    %color("blue", 0.2)
        translate([panel, 0, 0])
        cube([interior, 400, 300]);

    color("green", 0.5)
        translate([panel + target_clearance, 0, 0])
        cube([drawer_width, 380, 280]);
}

optimize_drawer_width(cabinet_width=800, target_clearance=9);
```

## See Also

- SKILL.md - Core patterns and quick reference
- examples/examples.md - Comprehensive examples
- docs/OPENSCAD-COLLISION-DETECTION.md - Full guide
