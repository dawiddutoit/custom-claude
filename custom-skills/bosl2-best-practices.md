---
identifier: bosl2-best-practices
type: instruction
description: BOSL2 library best practices for semantic modeling, attachments, boolean operations, and parametric design
version: 1.0.0
tags: [openscad, bosl2, libraries, modeling, best-practices]
---

# BOSL2 Best Practices

## Core Principles

### 1. Always Use Semantic Positioning Over translate()
Replace basic translate() calls with BOSL2 semantic functions for clearer intent:

```openscad
// Good - clear semantic meaning
up(10) sphere(d=5);
left(20) cuboid([10, 10, 10]);
attach(TOP) cyl(d=15, h=20);

// Avoid - unclear intent
translate([0, 0, 10]) sphere(d=5);
translate([-20, 0, 0]) cuboid([10, 10, 10]);
```

Available semantic functions: `up()`, `down()`, `left()`, `right()`, `fwd()`, `back()`

### 2. Master Attachments for Relative Positioning
Use BOSL2's attachment system instead of manual calculations:

```openscad
// Attachments automatically handle alignment
cuboid([30, 30, 10], rounding=2, edges="Z") {
    attach(TOP)           // Attach to top face
        cyl(d=15, h=20, rounding2=3, anchor=BOT);

    attach(FRONT)         // Attach to front face
        cuboid([10, 5, 8], anchor=BACK);

    attach([RIGHT+FRONT]) // Attach to corner (edge intersection)
        sphere(d=6);
}
```

### 3. Use diff() with tag("remove") for Boolean Operations
BOSL2's diff() is more readable and maintainable than traditional difference():

```openscad
// Good - clear intent with tagging
diff()
cuboid([20, 20, 10])
    attach(TOP) tag("remove") cyl(d=5, h=15);

// Also good for multiple removals
diff()
cuboid([40, 30, 20], rounding=3)
    attach(TOP) tag("remove") cyl(d=8, h=25)
    attach([TOP+FRONT]) tag("remove") sphere(d=5);
```

### 4. Leverage BOSL2 Parametric Shapes
Use BOSL2 modules instead of basic cubes/cylinders for better control:

```openscad
// BOSL2 cuboid with rounding control
cuboid([40, 30, 20], rounding=3, edges="Z");  // Round only Z edges

// BOSL2 cyl with control
cyl(d=15, h=20, rounding2=3);  // Add top rounding

// Chamfer option
cuboid([25, 25, 15], chamfer=3, edges=BOTTOM);  // Chamfer bottom edges
```

### 5. Use Distribution Functions for Arrays
Instead of manual xcopies, use BOSL2's distribution:

```openscad
// Linear copies with spacing
xcopies(spacing=12, n=5) sphere(d=8);

// 2D grid copies
grid_copies(spacing=15, n=[4, 3]) cuboid([10, 10, 5]);

// Arc distribution
arc_copies(r=25, n=8, sa=0, ea=270) cyl(d=6, h=10);
```

### 6. Preview vs Render Quality Settings
Implement preview-aware $fn for fast iteration:

```openscad
// Preview-aware quality (place at top of file)
$fn = $preview ? 32 : 64;

// Or for finer control with variables
$preview_fn = 32;
$render_fn = 64;
$fn = $preview ? $preview_fn : $render_fn;
```

### 7. Anchoring and Spacing
Use anchor parameter consistently:

```openscad
// Center on origin
cuboid([20, 20, 10], anchor=CENTER);

// Bottom-center (standard for printing)
cuboid([20, 20, 10], anchor=BOTTOM);

// Top-left-back corner
cuboid([20, 20, 10], anchor=[LEFT, BACK, TOP]);
```

## Common BOSL2 Modules Reference

| Module | Purpose | Example |
|--------|---------|---------|
| `cuboid()` | Smart box with rounding/chamfer | `cuboid([40, 30, 20], rounding=3, edges="Z")` |
| `cyl()` | Cylinder with top rounding | `cyl(d=15, h=20, rounding2=3)` |
| `sphere()` | Standard sphere | `sphere(d=10)` |
| `diff()` | Boolean difference with tagging | `diff() parent() tag("remove") child()` |
| `attach()` | Position relative to face | `attach(TOP, CENTER) child()` |
| `up/down/left/right/fwd/back()` | Semantic translation | `up(10) object()` |
| `xcopies/ycopies/zcopies()` | Linear array | `xcopies(12, n=5) object()` |
| `grid_copies()` | 2D grid array | `grid_copies(15, n=[4,3]) object()` |
| `arc_copies()` | Circular array | `arc_copies(r=25, n=8) object()` |

## BOSL2 Include Pattern

```openscad
// Always include at top of file
include <BOSL2/std.scad>

// For specific features, add additional includes:
include <BOSL2/gears.scad>        // For gear generation
include <BOSL2/threading.scad>    // For threaded parts
include <BOSL2/screws.scad>       // For screw utilities
include <BOSL2/hinges.scad>       // For hinge generation
```

## When to Use BOSL2 vs Raw OpenSCAD

Use BOSL2 when:
- You need semantic positioning and attachments
- Building parametric shapes with common rounding/chamfering
- Creating arrays and distributions
- Leveraging specialized modules (gears, threads, screws)

Use raw OpenSCAD when:
- Rapid prototyping with simple geometry
- Performance-critical boolean operations
- Complex mathematical expressions
- Custom algorithms
