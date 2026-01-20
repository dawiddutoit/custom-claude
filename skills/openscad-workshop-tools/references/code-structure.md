# OpenSCAD Workshop Tool Code Structure

## File Template

```openscad
/* Tool Name and Model
 * Brief description of the tool.
 * Usage context in workshop.
 *
 * SPECIFICATIONS (from manufacturer):
 * - Dimensions: W x D x H mm
 * - Weight: X kg
 * - Power: X W (if applicable)
 * - Key features...
 */

/* [Dimensions] */
// Primary dimension comments
length = 000;
width = 000;
height = 000;

/* [Details] */
// Feature toggles
show_feature = true;
feature_size = 00;

/* [Colors] */
// Brand color (RGB normalized 0-1)
body_color = [0.00, 0.00, 0.00];
accent_color = [0.00, 0.00, 0.00];

/* [Quality] */
$fn = $preview ? 32 : 64;

// ============ Calculated Values ============
// Derived dimensions here

// ============ Modules ============

module component_name() {
    color(body_color) {
        // geometry
    }
}

// ============ Main Assembly ============

module tool_name() {
    floor_plane();
    component_a();
    component_b();
    // ...
}

// ============ Render ============

tool_name();

// Debug info
echo("=== Tool Name ===");
echo(str("Dimensions: ", length, " x ", width, " x ", height, " mm"));
```

## Brand Colors (RGB normalized 0-1)

| Brand | Primary | Accent |
|-------|---------|--------|
| **Bosch DIY (green)** | `[0.18, 0.45, 0.34]` | `[0.75, 0.15, 0.15]` (red) |
| **Bosch Pro (blue)** | `[0.00, 0.40, 0.60]` | `[0.10, 0.10, 0.10]` |
| **Festool** | `[0.51, 0.77, 0.20]` | `[0.20, 0.22, 0.24]` |
| **Makita** | `[0.00, 0.60, 0.60]` (teal) | `[0.10, 0.10, 0.10]` |
| **DeWalt** | `[0.95, 0.75, 0.10]` (yellow) | `[0.10, 0.10, 0.10]` |
| **Milwaukee** | `[0.70, 0.10, 0.10]` (red) | `[0.10, 0.10, 0.10]` |

## Common Materials

| Material | Color | Use For |
|----------|-------|---------|
| Chrome/steel | `[0.85, 0.85, 0.88]` | Columns, rods, shafts |
| Cast aluminum | `[0.75, 0.75, 0.75]` | Base plates, housings |
| Dark steel | `[0.20, 0.20, 0.22]` | Chucks, gears |
| Rubber/grip | `[0.12, 0.12, 0.12]` | Wheels, handles |
| Translucent floor | `[0.3, 0.3, 0.3, 0.3]` | Reference plane |

## Component Decomposition Patterns

### Stationary Tools (drill press, bandsaw, etc.)
- Base plate (with mounting features)
- Column/frame
- Motor/head unit
- Work table/surface
- Controls (switches, dials)
- Adjustment mechanisms

### Portable Power Tools (circular saw, router, etc.)
- Base plate / shoe
- Motor housing
- Handle assembly
- Blade/bit guard
- Dust port
- Adjustment controls

### Dust Extractors / Vacuums
- Body container
- Wheels / casters
- Handle
- Hose port(s)
- Control panel
- Filter housing

### Storage / Systainers
- Main box body
- Lid
- Latches
- Stacking features
- Handle
