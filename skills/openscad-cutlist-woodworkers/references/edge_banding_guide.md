# Edge Banding Guide for woodworkers-lib

Best practices for specifying, interpreting, and applying edge banding in OpenSCAD furniture designs.

## What is Edge Banding?

Edge banding is thin veneer or plastic tape applied to the exposed edges of plywood, MDF, or particle board panels to:
- Hide raw edge grain and core layers
- Provide durable, finished appearance
- Match panel surface color/texture
- Protect edges from moisture and damage

**Common materials:**
- **ABS plastic:** Durable, pre-glued, heat-activated (most common)
- **PVC:** Flexible, pre-glued
- **Wood veneer:** Real wood, requires adhesive
- **Melamine:** For melamine-coated panels

## Edge Banding in woodworkers-lib

### Parameter System

Edge banding is specified using `a`-prefix parameters:

| Parameter | Edge Location | Applies To |
|-----------|---------------|------------|
| `al` | Left | Top/Bottom/Front/Back planes |
| `ar` | Right | Top/Bottom/Front/Back planes |
| `at` | Top | Left/Right/Front/Back planes |
| `ab` | Bottom | Left/Right/Front/Back planes |
| `af` | Front | Left/Right/Top/Bottom planes |
| `aB` | Back | Left/Right/Top/Bottom planes |

**Values:** Thickness of edge band tape in mm (typically 4mm for ABS, 2mm for thin veneer)

### Example

```scad
// Top panel with edge bands on front, left, and right
planeTop(cabinet, f=-1, af=4, al=4, ar=4);

// ECHO output: "plane (top): 782(4,4) × 378(4) × 18"
//                               ^^        ^
//                          left,right   front
// Back edge omitted (against wall, not visible)
```

## Which Edges Need Banding?

### General Rule: Band Visible Edges Only

**Band these edges:**
- All front-facing edges (visible from room)
- Top edges on waist-height furniture
- Edges around door/drawer fronts (all 4 sides)
- Shelf front edges

**Skip these edges:**
- Back edges (against walls)
- Hidden joints (inside dado grooves)
- Internal frame edges (covered by other panels)
- Bottom edges (against floor)

### Edge Selection by Panel Type

#### Side Panels (Left/Right)

```scad
// Typical: front edge only
planeLeft(cabinet, f=-1, t=-1, b=-1, af=4);

// Freestanding: front + top
planeLeft(cabinet, f=-1, t=-1, b=-1, af=4, at=4);

// Display: front + top + bottom (rare)
planeLeft(cabinet, f=-1, t=-1, b=-1, af=4, at=4, ab=4);
```

**Decision tree:**
- Against wall? → Front only
- Freestanding? → Front + top
- Glass/see-through? → Front + top + bottom

#### Top Panels

```scad
// Built-in cabinet: front + sides (3 edges)
planeTop(cabinet, f=-1, af=4, al=4, ar=4);

// Island/freestanding: all 4 edges
planeTop(cabinet, af=4, al=4, ar=4, aB=4);

// Under-counter: sides only (front covered by face frame)
planeTop(cabinet, f=-1, al=4, ar=4);
```

**Decision tree:**
- Built-in? → Front + sides (3 edges)
- Freestanding? → All 4 edges
- Face frame? → Sides only (2 edges)

#### Bottom Panels

```scad
// Same as top, but often no edge banding if on floor
planeBottom(cabinet, f=-1, af=4, al=4, ar=4);

// Elevated/visible bottom: same rules as top
```

#### Shelves

```scad
// Standard: front edge only
translate([0, 0, 400])
    planeBottom(cabinet, l=-1, r=-1, f=-1, af=4);

// Glass-front cabinet: front + sides
translate([0, 0, 400])
    planeBottom(cabinet, l=-1, r=-1, f=-1, af=4, al=4, ar=4);
```

**Decision tree:**
- Solid doors? → Front only
- Glass doors? → Front + sides
- Open shelving? → Front + sides + back (rare)

#### Door Panels

```scad
// All 4 edges (full perimeter)
planeFront(cabinet, ll=-4, rr=-4, tt=-4, bb=-4,
           al=4, ar=4, at=4, ab=4);
```

**Always:** All 4 edges on doors and drawer fronts

#### Back Panels

```scad
// Never edge band (thin fiberboard, hidden)
planeBack(cabinet, thick=4);
```

**Never:** Back panels don't get edge banding

## Edge Banding Specifications

### Standard Thicknesses

| Material | Thickness | Use Case |
|----------|-----------|----------|
| ABS tape | 0.4-0.5mm | Standard (use `af=4` in params) |
| Thin veneer | 0.2mm | Delicate/premium (use `af=2`) |
| Thick ABS | 1-2mm | Heavy-duty commercial |
| PVC | 0.4-1mm | Flexible applications |

**In woodworkers-lib:** Use the tape thickness in mm (typically 4 for standard ABS)

### Standard Widths

| Width | Use Case |
|-------|----------|
| 19mm | Most common (3/4" panel edges) |
| 22mm | Thicker panels (20-25mm) |
| 40mm | Wide edges (thick countertops) |

**Note:** Width doesn't affect ECHO notation (only thickness matters for fit calculations)

### Color Matching

When ordering edge banding:
1. Match panel surface color/finish
2. Request samples if unsure
3. Common colors: white, black, maple, oak, cherry, walnut

## ECHO Output Interpretation

### Reading Edge Band Notation

```
ECHO: "plane (top): 782(4,4) × 378(4) × 18"
                     ^^^^^^^    ^^^^^
                     dimension  dimension
                     (edges)    (edges)
```

**Notation rules:**
- `782(4)` → one 4mm edge on the 782mm side
- `782(4,4)` → two 4mm edges on opposite sides of 782mm dimension
- `782(4,2)` → one 4mm edge + one 2mm edge
- `782` → no edge banding on this dimension

### Calculating Total Edge Banding Length

**Method 1: Manual calculation**
```
For panel: 782(4,4) × 378(4) × 18

Edge 1: 782mm × 1 = 782mm (4mm tape)
Edge 2: 782mm × 1 = 782mm (4mm tape)
Edge 3: 378mm × 1 = 378mm (4mm tape)

Total: 782 + 782 + 378 = 1942mm = 1.94m per panel
```

**Method 2: Script**
```bash
python3 scripts/validate_cutlist.py cutlist.csv
# Outputs total edge banding length with 10% waste factor
```

### Example: Complete Wardrobe

```
ECHO: "plane (left):   18 × 378(4) × 1164"       → 1× 378mm = 0.38m
ECHO: "plane (right):  18 × 378(4) × 1164"       → 1× 378mm = 0.38m
ECHO: "plane (top):    782(4,4) × 378(4) × 18"   → 782+782+378 = 1.94m
ECHO: "plane (bottom): 782(4,4) × 378(4) × 18"   → 1.94m
ECHO: "plane (front):  487(4,4,4,4) × 18 × 1192(4,4,4,4)" → 2×(487+1192) = 3.36m
ECHO: "plane (front):  487(4,4,4,4) × 18 × 1192(4,4,4,4)" → 3.36m
ECHO: "plane (back):   1000 × 4 × 1200"          → 0m (no edges)
ECHO: "plane (bottom): 964(4) × 378 × 18" (×3)   → 3× 964mm = 2.89m

Total: 0.38 + 0.38 + 1.94 + 1.94 + 3.36 + 3.36 + 2.89 = 14.25m
Order: 14.25m × 1.1 (waste) = 15.7m ≈ 16m of 4mm ABS tape
```

## Application Methods

### 1. Iron-On ABS Tape (Most Common)

**Process:**
1. Cut panel to exact dimensions from ECHO output
2. Apply 4mm ABS tape with household iron (medium heat)
3. Trim excess with edge trimmer tool
4. Sand edges flush with panel surface

**Pros:**
- No special equipment needed
- Pre-glued, ready to use
- Durable finish

**Cons:**
- Requires practice for clean application
- Can delaminate if not heated properly

### 2. Edge Bander Machine

**Process:**
1. Feed panel through edge bander
2. Machine applies glue, tape, trims, and sands in one pass

**Pros:**
- Professional finish
- Fast for multiple panels
- Consistent results

**Cons:**
- Expensive equipment
- Requires workshop space

### 3. Contact Cement (Wood Veneer)

**Process:**
1. Apply contact cement to panel edge and veneer
2. Let dry to tacky (5-10 min)
3. Press veneer firmly to edge
4. Trim and sand flush

**Pros:**
- Strong bond for wood veneer
- No heat required

**Cons:**
- Messy application
- No repositioning (instant bond)

## Design Tips

### 1. Plan for Application Order

Apply edge banding in this order:
1. **End grain first** (short edges, will be hidden)
2. **Long grain second** (long edges, will hide end grain edges)

Example: For a shelf (964×378mm)
1. Apply to 378mm ends first
2. Apply to 964mm front edge second (covers end grain edges)

### 2. Account for Tape Thickness in Tight Fits

**Problem:** Edge band adds thickness to panel edge

**Solution 1:** Compensate with absolute increments
```scad
// Drawer front must fit 500mm opening exactly
// Panel width: 500mm - 8mm (2× 4mm edge bands)
planeFront(cabinet, ll=-4, rr=-4, al=4, ar=4);
// Result: 492mm panel + 8mm tape = 500mm total
```

**Solution 2:** Apply edge band, then trim to final size
```scad
// Cut panel slightly oversized
planeFront(cabinet, ll=2, rr=2, al=4, ar=4);
// After edge banding, trim to exact 500mm
```

### 3. Match Grain Direction

For wood veneer edge banding:
- Match grain direction to panel surface
- Use book-matched veneer for symmetry
- Note in CSV "notes" column: "Grain direction: length"

### 4. Pre-Finished Panels

If using pre-finished plywood:
- Order edge banding in matching finish
- Some suppliers offer color-matched edge tape
- Test fit on scrap before full application

## Quality Control Checklist

Before ordering materials:

- [ ] All visible edges have edge band parameters (`af, al, ar, at, ab, aB`)
- [ ] Hidden edges (back, internal) have no edge bands
- [ ] Door/drawer fronts have all 4 edges specified
- [ ] Edge band thickness matches tape type (4mm for ABS, 2mm for veneer)
- [ ] Total edge banding length calculated (use `validate_cutlist.py`)
- [ ] Edge banding color/finish matches panel surface
- [ ] Ordered 10-15% extra for waste/mistakes

After cut list generation:

- [ ] ECHO output shows edge notation: `782(4)` format
- [ ] Edge count matches visual inspection of 3D model
- [ ] No edge bands on back panels (fiberboard)
- [ ] Shelf quantities match number of shelves in design

## Common Mistakes

### 1. Over-Banding

**Mistake:**
```scad
// Adding edge bands to all edges unnecessarily
planeLeft(cabinet, af=4, aB=4, at=4, ab=4);
```

**Problem:** Wastes material, adds cost, bands hidden edges

**Fix:**
```scad
// Only front edge visible
planeLeft(cabinet, af=4);
```

### 2. Under-Banding

**Mistake:**
```scad
// Door with no edge banding
planeFront(cabinet, ll=-4, rr=-4);
```

**Problem:** Raw edges exposed on visible surface

**Fix:**
```scad
// All 4 edges on doors
planeFront(cabinet, ll=-4, rr=-4, al=4, ar=4, at=4, ab=4);
```

### 3. Wrong Edge Parameters

**Mistake:**
```scad
// Using 'l' instead of 'al' for edge banding
planeTop(cabinet, l=4);  // WRONG - this is thickness-relative!
```

**Problem:** Panel dimension changes, no edge band added

**Fix:**
```scad
// Use 'al' prefix for edge banding
planeTop(cabinet, al=4);  // CORRECT
```

### 4. Forgetting Compensation

**Mistake:**
```scad
// Tight-fit drawer front without compensation
planeFront(cabinet, al=4, ar=4);
// Panel too wide by 8mm (4mm × 2 edges)
```

**Fix:**
```scad
// Compensate for edge band thickness
planeFront(cabinet, ll=-4, rr=-4, al=4, ar=4);
// Now fits correctly
```

## Resources

### Suppliers

- **EdgeSupply.com** - Wide selection of ABS, PVC, wood veneer
- **VeneerSupplies.com** - Premium wood veneer edge banding
- **FastCap.com** - Pre-glued edge banding and applicator tools
- **Rockler.com** - Edge banding tape and tools

### Tools

- **Edge trimmer** - Trims excess tape flush with panel
- **Household iron** - Applies heat-activated tape
- **J-roller** - Presses tape firmly after heating
- **Sanding block** - Smooths edges after trimming

### Tutorials

- YouTube: "How to Apply Edge Banding" (Wood Whisperer)
- YouTube: "Edge Banding Tips and Tricks" (3x3Custom)
- Article: "Edge Banding Like a Pro" (Fine Woodworking magazine)

## Advanced Techniques

### Two-Tone Edge Banding

```scad
// Top with contrasting edge color
planeTop(cabinet, af=4, al=2, ar=2);
// af=4: Black ABS on front
// al/ar=2: Natural wood veneer on sides
```

**Use:** Accent edges, design feature

### Thick Edge Banding

```scad
// Countertop with thick solid wood edge
planeTop(countertop, af=25, al=25, ar=25);
// 25mm thick solid wood banding
```

**Note:** Requires custom milling, not standard tape

### Radius Edge Banding

For curved edges, use flexible PVC tape:
```scad
// Curved front edge
planeTop(cabinet, af=4);
// Use flexible PVC, apply with heat gun
```

**Tip:** Pre-bend tape to match curve before application
