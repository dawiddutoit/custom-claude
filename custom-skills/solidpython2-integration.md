---
identifier: solidpython2-integration
type: instruction
description: SolidPython2 integration patterns for programmatic OpenSCAD model generation with Python
version: 1.0.0
tags: [solidpython2, python, openscad, automation, code-generation]
---

# SolidPython2 Integration

SolidPython2 enables writing OpenSCAD models in Python, useful for complex parametric designs, batch processing, and code reuse.

## Environment Setup

### Virtual Environment Location
```bash
/home/unit/openscad-python
```

### Activation
```bash
source /home/unit/openscad-python/bin/activate
```

### Installed Packages
- `solidpython2` - Main library for Python OpenSCAD generation
- `openpyscad` - Lightweight alternative wrapper (optional)
- `openscad_runner` - Render SCAD files programmatically (optional)

### Verify Installation
```bash
python -c "from solid2 import *; print('SolidPython2 OK')"
```

## Basic Pattern

### Minimal Example
```python
from solid2 import *

# Set default resolution
set_global_fn(64)

# Create a simple model
def main():
    model = cube([20, 20, 10], center=True)
    return model

if __name__ == "__main__":
    rendered = main()
    rendered.save_as_scad("output.scad")
    print("Generated: output.scad")
```

### Save and Render Workflow
```python
from solid2 import *

def create_model():
    return cuboid([40, 30, 20], rounding=3)

if __name__ == "__main__":
    model = create_model()

    # Save as .scad for inspection
    model.save_as_scad("model.scad")

    # Optionally render directly to STL
    # (requires OpenSCAD installed)
    # render_to_file(model, "output.stl")
```

## BOSL2 Integration

### Import BOSL2 Extensions
```python
from solid2 import *
from solid2.extensions.bosl2 import *

set_global_fn(64)

# Now you have access to BOSL2 functions
def rounded_box():
    # BOSL2's cuboid with rounding
    return cuboid([40, 30, 20], rounding=3, edges="Z")
```

### BOSL2 Module Example
```python
from solid2 import *
from solid2.extensions.bosl2 import *

def rounded_box_with_hole():
    """Create a rounded box with a center hole using BOSL2."""
    # BOSL2's cuboid with rounding
    box = cuboid([40, 30, 20], rounding=3, edges="Z")

    # Hole from top (cylinder)
    hole = cylinder(d=10, h=25, center=True)
    hole = hole.up(5)

    # Boolean difference
    return box - hole

def main():
    return rounded_box_with_hole()

if __name__ == "__main__":
    model = main()
    model.save_as_scad("box_hole.scad")
```

## Common Operations

### Positioning
```python
from solid2 import *

# Translation
box = cube([20, 20, 10])
box_moved = box.up(10)           # Move up
box_moved = box.right(15)         # Move right
box_moved = box.translate([5, 10, 15])  # Arbitrary translation

# Note: up/down/left/right are not BOSL2 but work in SolidPython2
```

### Boolean Operations
```python
# Union (combining)
model = cube([20, 20, 10]) + cube([15, 15, 10]).up(10)

# Difference (subtraction)
model = cube([30, 30, 20]) - cylinder(d=15, h=25, center=True)

# Intersection
model = cube([30, 30, 20]) & cylinder(d=25, h=30, center=True)
```

### Arrays and Copies
```python
from solid2 import *

# Linear array
copies = [
    cube([10, 10, 10]).translate([i*15, 0, 0])
    for i in range(5)
]
model = union()(copies)

# More efficient: use distribute if available
# grid_copies, xcopies, etc.
```

### Color and Rendering
```python
# Set color
colored = cube([20, 20, 10]).set_color("red")
colored = cube([20, 20, 10]).set_color([1, 0, 0])  # RGB

# Preview vs render quality
def preview_aware_model():
    # SolidPython2 doesn't directly support $preview
    # Use environment variable or separate functions
    return cube([20, 20, 10], $fn=32)
```

## Advanced Pattern: Parametric Bin Generator

Practical example generating Gridfinity bins:

```python
from solid2 import *
from solid2.extensions.bosl2 import *

def gridfinity_bin(
    grid_x=1,
    grid_y=1,
    height_units=5,
    wall=2,
    bottom=2,
    include_lip=True
):
    """
    Generate a Gridfinity-compatible bin.

    Args:
        grid_x: Grid units wide (42mm per unit)
        grid_y: Grid units deep (42mm per unit)
        height_units: Height in 7mm units
        wall: Wall thickness (mm)
        bottom: Bottom thickness (mm)
        include_lip: Add Gridfinity lip (bool)

    Returns:
        OpenSCAD solid object
    """
    set_global_fn(64)

    # Calculate dimensions
    outer_x = (grid_x * 42) - 0.5
    outer_y = (grid_y * 42) - 0.5
    outer_z = height_units * 7

    # Base box with rounded corners
    bin_body = cuboid(
        [outer_x, outer_y, outer_z],
        rounding=4.65,
        edges="Z"
    )

    # Inner cavity
    inner_x = outer_x - (2 * wall)
    inner_y = outer_y - (2 * wall)
    inner_z = outer_z - bottom

    cavity = cuboid(
        [inner_x, inner_y, inner_z],
        anchor=BOTTOM
    ).up(bottom)

    # Create hollow bin
    bin_hollow = bin_body - cavity

    # Optional: Add Gridfinity lip
    if include_lip:
        lip_height = 2.4
        lip_inset = 2.0
        lip_thickness = 1.5

        lip_x = outer_x - (2 * lip_inset)
        lip_y = outer_y - (2 * lip_inset)

        lip = cuboid(
            [lip_x, lip_y, lip_height],
            rounding=2
        ).down((outer_z - lip_height) / 2)

        bin_hollow = bin_hollow + lip

    return bin_hollow

def main():
    # Generate a 2x2 bin, 5 units tall
    model = gridfinity_bin(
        grid_x=2,
        grid_y=2,
        height_units=5,
        wall=2,
        bottom=2,
        include_lip=True
    )
    return model

if __name__ == "__main__":
    model = main()
    model.save_as_scad("gridfinity_bin.scad")
    print("Generated: gridfinity_bin.scad")
```

## Batch Processing

Generate multiple models programmatically:

```python
from solid2 import *
from solid2.extensions.bosl2 import *

def create_bin(size, height):
    """Create bin with specific size/height."""
    return cuboid(
        [size*42-0.5, size*42-0.5, height*7],
        rounding=4.65,
        edges="Z"
    )

def main():
    # Create range of bin sizes
    bin_configs = [
        {"size": 1, "height": 3, "name": "small"},
        {"size": 2, "height": 5, "name": "medium"},
        {"size": 3, "height": 5, "name": "large"},
    ]

    for config in bin_configs:
        model = create_bin(config["size"], config["height"])
        filename = f"bin_{config['name']}.scad"
        model.save_as_scad(filename)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    main()
```

## Integration with OpenSCAD Customizer

Convert Python model to parameterized OpenSCAD:

```python
# This generates a .scad file with Customizer sections
from solid2 import *

def create_configurable_box():
    """Generate box with Customizer sections."""
    scad_code = """
/* [Box Dimensions] */
width = 40;
depth = 30;
height = 20;

/* [Hole] */
hole_d = 8;
hole_depth = 15;

$fn = $preview ? 32 : 64;

module main() {
    diff()
    cuboid([width, depth, height], rounding=3, edges="Z")
        attach(TOP) tag("remove") cyl(d=hole_d, h=hole_depth+1);
}

main();
"""
    with open("customizable_box.scad", "w") as f:
        f.write(scad_code)

# Better approach: Generate Python, then convert to SCAD
def generate_dynamic_model(width=40, depth=30, height=20):
    """Generate model with parameters."""
    model = cuboid([width, depth, height], rounding=3, edges="Z")
    hole = cylinder(d=8, h=height+1, center=True).up(height/2)
    return model - hole
```

## Workflow Integration

### Typical Development Cycle

1. **Prototype in Python**
   ```bash
   source /home/unit/openscad-python/bin/activate
   python src/examples/bin_generator.py
   ```

2. **Inspect Generated SCAD**
   ```bash
   cat generated.scad  # Review before rendering
   ```

3. **Render to STL**
   ```bash
   openscad -o stl/model.stl generated.scad
   ```

4. **Prepare for Printing**
   ```bash
   # Use MCP 3d-printer tools
   center_model stl/model.stl
   lay_flat stl/model.stl
   ```

### Python → SCAD → STL → Print Pipeline
```
Python script
    ↓
.save_as_scad()
    ↓
openscad -o model.stl
    ↓
MCP: center_model, lay_flat, slice_stl
    ↓
Print
```

## Best Practices

### 1. Activate Virtual Environment
Always activate before running Python scripts:
```bash
source /home/unit/openscad-python/bin/activate
```

### 2. Use BOSL2 Extensions
Import BOSL2 for semantic functions and better readability:
```python
from solid2.extensions.bosl2 import *
```

### 3. Set Global Resolution
```python
set_global_fn(64)  # Production quality
# For preview: set_global_fn(32)
```

### 4. Save as SCAD First
Always save as .scad for inspection before rendering:
```python
model.save_as_scad("output.scad")
```

### 5. Document Parameters
Use docstrings for all generative functions:
```python
def my_module(width=10, height=20):
    """
    Generate something.

    Args:
        width: Width in mm
        height: Height in mm

    Returns:
        Solid object
    """
    pass
```

### 6. Use Comments for Complex Logic
```python
# Gridfinity spec: 42mm base unit
grid_spacing = 42

# Standard bin height: 7mm per unit
bin_height = height_units * 7
```

## Comparison: Python vs Direct OpenSCAD

| Task | Python (SolidPython2) | Direct OpenSCAD |
|------|----------------------|-----------------|
| Simple geometry | More verbose | Concise |
| Batch generation | Excellent | Tedious |
| Parameterization | Flexible | Customizer UI |
| Array operations | Pythonic loops | Functional |
| Complex math | Easier | Basic |
| Code reuse | Full Python modules | $include |
| Debugging | Python tooling | Print statements |

## Resources

- Virtual environment: `/home/unit/openscad-python`
- Example file: `/mnt/e/projects/openscad/src/examples/python_example.py`
- SolidPython2 docs: https://github.com/SolidCode/SolidPython
