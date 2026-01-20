# woodworkers-lib Parameter Reference

Complete parameter documentation for all plane modules with visual diagrams and calculation formulas.

## Module Signatures

### Front/Back Planes (XZ orientation)

```scad
module planeFront(
    dim,                    // [width, depth, height] of furniture
    l=0, r=0, t=0, b=0,     // Thickness-relative increments (left, right, top, bottom)
    ll=0, rr=0, tt=0, bb=0, // Absolute increments (mm)
    al=0, ar=0, at=0, ab=0, // ABS edge banding (mm)
    thick=thick             // Panel thickness override
)

module planeBack(
    dim,                    // Same as planeFront
    l=0, r=0, t=0, b=0,
    ll=0, rr=0, tt=0, bb=0,
    al=0, ar=0, at=0, ab=0,
    thick=thick
)
```

**Orientation:**
- Width dimension: X-axis (left to right)
- Height dimension: Z-axis (bottom to top)
- Thickness: Y-axis (18mm default)

**Parameter mapping:**
- `l, r` → adjust width (X)
- `t, b` → adjust height (Z)
- `al, ar` → edge bands on left/right edges
- `at, ab` → edge bands on top/bottom edges

### Left/Right Planes (YZ orientation)

```scad
module planeLeft(
    dim,                    // [width, depth, height] of furniture
    f=0, B=0, t=0, b=0,     // Thickness-relative (front, Back, top, bottom)
    ff=0, BB=0, tt=0, bb=0, // Absolute increments
    af=0, aB=0, at=0, ab=0, // ABS edge banding
    thick=thick
)

module planeRight(
    dim,                    // Same as planeLeft
    f=0, B=0, t=0, b=0,
    ff=0, BB=0, tt=0, bb=0,
    af=0, aB=0, at=0, ab=0,
    thick=thick
)
```

**Orientation:**
- Width dimension: Y-axis (front to back)
- Height dimension: Z-axis (bottom to top)
- Thickness: X-axis (18mm default)

**Parameter mapping:**
- `f, B` → adjust depth (Y)
- `t, b` → adjust height (Z)
- `af, aB` → edge bands on front/back edges
- `at, ab` → edge bands on top/bottom edges

**Note:** Capital `B` = Back (to distinguish from `b` = bottom)

### Top/Bottom Planes (XY orientation)

```scad
module planeTop(
    dim,                    // [width, depth, height] of furniture
    l=0, r=0, f=0, B=0,     // Thickness-relative (left, right, front, Back)
    ll=0, rr=0, ff=0, BB=0, // Absolute increments
    al=0, ar=0, af=0, aB=0, // ABS edge banding
    thick=thick
)

module planeBottom(
    dim,                    // Same as planeTop
    l=0, r=0, f=0, B=0,
    ll=0, rr=0, ff=0, BB=0,
    al=0, ar=0, af=0, aB=0,
    thick=thick
)
```

**Orientation:**
- Width dimension: X-axis (left to right)
- Depth dimension: Y-axis (front to back)
- Thickness: Z-axis (18mm default)

**Parameter mapping:**
- `l, r` → adjust width (X)
- `f, B` → adjust depth (Y)
- `al, ar` → edge bands on left/right edges
- `af, aB` → edge bands on front/back edges

## Parameter Types Explained

### 1. Thickness-Relative Increments

**Parameters:** `l, r, t, b, f, B` (single letter, lowercase except B)

**Calculation:**
```
effective_dimension = base_dimension + (parameter × thick)
```

**Common patterns:**

| Pattern | Value | Result | Use Case |
|---------|-------|--------|----------|
| No adjustment | `0` | Full dimension | Top/bottom of frame |
| Fit inside | `-1` | Shortened by 18mm | Side panels between top/bottom |
| Fit between two | `-2` | Shortened by 36mm | Internal divider between two panels |
| Extend over | `1` | Extended by 18mm | Rarely used (overlap) |

**Example:**
```scad
thick = 18;
cabinet = [800, 400, 1200];  // W×D×H

// Side panel fits between top and bottom
planeLeft(cabinet, t=-1, b=-1);
// Effective height: 1200 + (-1×18) + (-1×18) = 1164mm
```

### 2. Absolute Increments

**Parameters:** `ll, rr, tt, bb, ff, BB` (double letter)

**Calculation:**
```
effective_dimension = base_dimension + (thickness_relative × thick) + absolute_increment
```

**Common patterns:**

| Pattern | Value | Result | Use Case |
|---------|-------|--------|----------|
| Door gap | `-4` | 4mm narrower | Clearance around doors |
| Extension | `10` | 10mm longer | Shelf overhangs |
| Recess | `-10` | 10mm shorter | Back panel inset |

**Example:**
```scad
// Door panel with 4mm clearance on each side
planeFront(cabinet, ll=-4, rr=-4);
// Width: 800 + 0 + (-4) + (-4) = 792mm

// Shelf extending 10mm past front edge
planeBottom(cabinet, l=-1, r=-1, ff=10);
// Depth: 400 + 0 + 10 = 410mm
```

### 3. ABS Edge Banding

**Parameters:** `al, ar, at, ab, af, aB` (prefix `a`)

**Effect:**
1. **Visual:** Adds 3D edge band visualization (small lip)
2. **ECHO output:** Adds notation to dimension: `782(4)` = 782mm with 4mm edge
3. **Dimension adjustment:** Edge band thickness is SUBTRACTED from effective dimension

**Calculation:**
```
effective_dimension = base_dimension + (thickness_relative × thick) + absolute_increment - edge_band_thickness
```

**Common patterns:**

| Pattern | Value | Result | Use Case |
|---------|-------|--------|----------|
| No edge band | `0` | No change | Hidden/back edges |
| Standard ABS | `4` | 4mm edge tape | Visible edges (most common) |
| Thin edge | `2` | 2mm edge tape | Delicate edges |

**Example:**
```scad
// Top panel with front, left, right edge bands
planeTop(cabinet, f=-1, af=4, al=4, ar=4);

// ECHO output: "plane (top): 782(4,4) × 378(4) × 18"
//                               ^^        ^
//                          left,right   front

// Width calculation: 800 + 0 + 0 - 4 - 4 = 792mm (but reported as 782(4,4))
```

**Important:** The ECHO output shows the dimension BEFORE edge banding is applied. The notation `(4,4)` indicates two 4mm edge bands should be applied to that dimension.

## Parameter Interaction Rules

### Order of Operations

For any dimension, the calculation order is:

1. Start with base dimension from `dim` parameter
2. Add thickness-relative adjustment: `+ (relative × thick)`
3. Add absolute increment: `+ absolute`
4. **Subtract edge band thickness:** `- edge_band`

**Example with all parameters:**
```scad
thick = 18;
cabinet = [1000, 400, 1200];

planeTop(cabinet, l=-1, ll=5, al=4);

// Left edge calculation:
// 1. Base: 1000mm
// 2. Thickness-relative: -1 × 18 = -18mm
// 3. Absolute: +5mm
// 4. Edge band: -4mm
// Final: 1000 - 18 + 5 - 4 = 983mm
// ECHO: "983(4) × ... × 18"
```

### Edge Band and Absolute Interaction

Critical rule: Edge banding REDUCES the effective dimension.

**Common mistake:**
```scad
// WRONG: Expecting 782mm with edge band
planeTop(cabinet, f=-1, af=4);
// Actual result: 782(4) in ECHO, but dimension is 378mm

// CORRECT: Compensate for edge band if exact dimension needed
planeTop(cabinet, f=-1, ff=4, af=4);
// Now: (400 - 18 + 4 - 4) = 382mm, reported as 382(4)
```

**When to compensate:**
- Tight-fit joints where edge band affects fit
- Drawer fronts that must match specific openings
- Door panels with precise clearances

**When NOT to compensate:**
- Decorative edge banding (doesn't affect structure)
- Shelves with front edge band only
- Standard cabinet construction (edge band applied after cutting)

## Visual Diagrams

### Front/Back Panel Orientation

```
        TOP (t, tt, at)
         ____________
        |            |
LEFT    |   FRONT    |  RIGHT
(l,ll)  |   PANEL    |  (r,rr)
(al)    |            |  (ar)
        |____________|

       BOTTOM (b, bb, ab)

Thickness (into page): 18mm default
```

### Left/Right Panel Orientation

```
        TOP (t, tt, at)
         ____________
        |            |
FRONT   |    LEFT    |  BACK
(f,ff)  |   PANEL    |  (B,BB)
(af)    |            |  (aB)
        |____________|

       BOTTOM (b, bb, ab)

Thickness (into page): 18mm default
```

### Top/Bottom Panel Orientation

```
        BACK (B, BB, aB)
         ____________
        |            |
LEFT    |    TOP     |  RIGHT
(l,ll)  |   PANEL    |  (r,rr)
(al)    |            |  (ar)
        |____________|

       FRONT (f, ff, af)

Thickness (up): 18mm default
```

## ECHO Output Interpretation

### Output Format

```
ECHO: "plane (FACE):  DIM1(edges) × DIM2(edges) × THICK"
```

### Edge Band Notation Rules

1. **Single edge:** `782(4)` = one 4mm edge on this dimension
2. **Two edges:** `782(4,4)` = two 4mm edges (opposite sides)
3. **Different widths:** `782(4,2)` = one 4mm edge, one 2mm edge
4. **No edges:** `782` = no edge banding on this dimension

### Determining Edge Locations

The edge notation appears on the dimension where edges are applied:

**Example 1:**
```
ECHO: "plane (top): 782(4,4) × 378(4) × 18"
```
- 782mm dimension has 2 edges (left + right)
- 378mm dimension has 1 edge (front)
- Total: 3 edge bands
- Missing: back edge (against wall, not visible)

**Example 2:**
```
ECHO: "plane (front): 487(4,4,4,4) × 18 × 1192(4,4,4,4)"
```
- Door panel with edge bands on all 4 edges
- Width (487mm) has edge bands on left + right
- Height (1192mm) has edge bands on top + bottom
- Full perimeter edge banding

### Edge Count Formula

```
total_edges = count(all_numbers_in_parentheses)
```

**Examples:**
- `782(4,4) × 378(4)` → 2 + 1 = 3 edges
- `487(4,4,4,4) × 18` → 4 edges
- `1000 × 4 × 1200` → 0 edges

## Common Patterns Cheat Sheet

### Frame Construction

```scad
cabinet = [800, 400, 1200];

// Outer frame (sides fit between top/bottom)
planeLeft(cabinet, f=-1, t=-1, b=-1, af=4);
planeRight(cabinet, f=-1, t=-1, b=-1, af=4);
planeTop(cabinet, f=-1, af=4, al=4, ar=4);
planeBottom(cabinet, f=-1, af=4, al=4, ar=4);
```

### Internal Shelf

```scad
// Shelf fits between sides, recessed from front
translate([0, 0, 400])
    planeBottom(cabinet, l=-1, r=-1, f=-1, af=4);
```

### Door with Gap

```scad
// 4mm gap on all sides
planeFront(cabinet, ll=-4, rr=-4, tt=-4, bb=-4,
           al=4, ar=4, at=4, ab=4);
```

### Back Panel (Thin Fiberboard)

```scad
// 4mm thick, no edge banding, recessed 4mm from back
color("brown")
translate([0, 4, 0])
planeBack(cabinet, thick=4);
```

### Vertical Divider

```scad
// Full height divider at center
translate([cabinet[0]/2, 0, 0])
    planeLeft(cabinet, f=-1, t=-1, b=-1, af=4);
```

## Troubleshooting Guide

### Panel dimensions wrong

**Symptom:** ECHO shows unexpected sizes

**Check:**
1. Verify `thick=18` matches your material
2. Count thickness-relative adjustments: `-1` per adjacent panel
3. Check absolute increments: `ll, rr, tt, bb, ff, BB`
4. Account for edge bands: they reduce effective dimension

### Edge bands missing in ECHO

**Symptom:** No `(4)` notation in output

**Check:**
1. Edge band parameters use `a` prefix: `af, aB, al, ar, at, ab`
2. Edge band value is non-zero: `af=4` not `af=0`
3. Correct parameter for plane orientation (e.g., `af` for front edge)

### Panels overlap in 3D view

**Symptom:** Visual overlaps in OpenSCAD preview

**Check:**
1. Thickness-relative adjustments: sides should have `t=-1, b=-1`
2. Translation positions: shelves need `translate([0,0,height])`
3. Verify `thick` global variable matches panel thickness

### Duplicate panels in cut list

**Symptom:** Same dimensions appear multiple times

**Possible causes:**
1. Intentional: multiple shelves at different heights (correct)
2. Accidental: copy-paste error (review code)
3. Solution: Use `validate_cutlist.py` to check quantities
