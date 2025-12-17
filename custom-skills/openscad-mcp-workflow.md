---
identifier: openscad-mcp-workflow
type: workflow
trigger: render scad|preview model|print model|process stl
description: Integrated workflow for OpenSCAD development using MCP servers (openscad-render and 3d-printer) for preview, rendering, and printing
version: 1.0.0
tags: [openscad, mcp, workflow, rendering, 3d-printing, automation]
---

# OpenSCAD MCP Workflow

This workflow integrates two MCP servers for a complete OpenSCAD-to-print pipeline:

- **openscad-render**: Visual preview without GUI
- **3d-printer**: STL manipulation, slicing, and printing

## Quick Workflow Reference

### 1. Quick Preview (No GUI)
Render current model to PNG for quick visual verification:

```bash
# Render from CLI using mcp__openscad-render__render_single
# View multiple angles: front, back, top, isometric
```

Use the MCP tool: `mcp__openscad-render__render_single`
- scad_file: /path/to/main.scad
- view: "isometric" or "front"
- image_size: [800, 600]

### 2. Full Render to STL
Generate production-quality STL from OpenSCAD:

```bash
# Command from CLAUDE.md:
openscad -o stl/output.stl src/main.scad
```

### 3. STL Preparation for Printing
Use MCP 3d-printer tools to prepare STL before slicing:

**Center model on build platform:**
```bash
mcp__3d-printer__center_model stl_path=/path/to/model.stl
```

**Lay flat for optimal printing:**
```bash
mcp__3d-printer__lay_flat stl_path=/path/to/model.stl
```

**Scale if needed (1.0 = no change):**
```bash
mcp__3d-printer__scale_stl stl_path=/path/to/model.stl scale_factor=0.95
```

**Rotate for better orientation:**
```bash
mcp__3d-printer__rotate_stl stl_path=/path/to/model.stl rotate_z=45
```

### 4. Slice for Printing
Generate G-code using PrusaSlicer, OrcaSlicer, or Cura:

```bash
mcp__3d-printer__slice_stl stl_path=/path/to/prepared.stl
```

Default slicer from environment or specify:
- slicer_type: "prusaslicer", "cura", "slic3r", "orcaslicer"

### 5. Send to Printer
Print directly to connected printer (OctoPrint, Klipper, Bambu Lab, Prusa Connect):

```bash
# For Bambu Lab printer with .3mf file:
mcp__3d-printer__print_3mf three_mf_path=/path/to/file.3mf
```

Or use the comprehensive workflow tool:

```bash
mcp__3d-printer__process_and_print_stl
  stl_path=/path/to/model.stl
  extension_inches=0.1
  bed_temp=60
  extruder_temp=200
```

## Workflow: From OpenSCAD to Print

### Complete Workflow Example

**Step 1: Edit and Preview**
```bash
# Edit src/main.scad (locally or via IDE)
# Use MCP to preview without opening OpenSCAD GUI
render scad file to isometric view at 800x600
```

**Step 2: Final Render**
```bash
openscad -o stl/model_final.stl src/main.scad
```

**Step 3: Prepare STL**
```bash
# Check dimensions and optimize orientation
get_stl_info: stl/model_final.stl

# Center on build platform
center_model: stl/model_final.stl

# Lay flat for best print quality
lay_flat: stl/model_final.stl

# Optional: Scale if file too large/small
scale_stl: stl/model_final.stl scale_factor=0.95
```

**Step 4: Verify Temperatures**
```bash
# After slicing, confirm temperature settings
confirm_temperatures:
  gcode_path=/path/to/sliced.gcode
  bed_temp=60
  extruder_temp=200
```

**Step 5: Print**
```bash
# Send to printer
print_3mf: three_mf_path=/path/to/file.3mf bed_temperature=60 nozzle_temperature=200
```

## MCP Server Reference

### openscad-render
**Purpose:** Generate PNG previews of OpenSCAD models

**Key Tools:**
- `render_single`: Single view render with camera control
- `check_openscad`: Verify OpenSCAD installation

**Usage:**
```
render_single(
  scad_file: string,           # Path to .scad file
  view: "front"|"back"|"top"|"bottom"|"left"|"right"|"isometric"|"dimetric",
  camera_position: [x,y,z],   # Optional camera override
  image_size: [width, height]  # Default [800, 600]
)
```

**View Suggestions:**
- "front" - Primary detail view
- "isometric" - Best overall impression
- "top" - Verify flat surfaces and alignment
- "dimetric" - Professional-looking alternative to isometric

### 3d-printer
**Purpose:** Complete STL-to-print workflow

**STL Manipulation:**
- `get_stl_info`: Dimensions, bounds, vertex count
- `center_model`: Move to origin (0,0,0)
- `lay_flat`: Rotate so largest face is on XY plane
- `scale_stl`: Uniform or axis-specific scaling
- `rotate_stl`: Rotate around X/Y/Z axes
- `translate_stl`: Move along axes (mm)
- `merge_vertices`: Clean up floating vertices
- `modify_stl_section`: Transform specific regions

**Slicing & Printing:**
- `slice_stl`: Generate G-code for printing
- `confirm_temperatures`: Verify slicer settings
- `print_3mf`: Direct print to Bambu Lab
- `process_and_print_stl`: All-in-one workflow

**Printer Support:**
- OctoPrint (via API)
- Klipper/Moonraker (via network)
- Bambu Lab (direct .3mf printing)
- Prusa Connect
- Creality Cloud

## Best Practices

### 1. Use Preview-Aware $fn
```openscad
$fn = $preview ? 32 : 64;  // Fast preview, quality final render
```

### 2. Optimize STL Before Slicing
Always run these in order:

```bash
1. get_stl_info              # Understand dimensions
2. center_model              # Ensure proper origin
3. lay_flat                  # Optimize printing orientation
4. Then slice                # Generate G-code
```

### 3. Temperature Management
Confirm temperatures match your filament:

```bash
# PETG typical: 230C nozzle, 80C bed
# PLA typical: 200C nozzle, 60C bed
# ASA typical: 240C nozzle, 100C bed
```

### 4. Scaling Workflow
If model is too large/small:

```bash
# Check size first
get_stl_info: model.stl

# Calculate scale factor
# If too large by 5%, scale to 0.95
# If too small by 10%, scale to 1.10

scale_stl: model.stl scale_factor=0.95
```

### 5. Visual Verification Pipeline

```
Edit SCAD
    ↓
render_single (preview) → Check geometry
    ↓
render to STL (final)
    ↓
get_stl_info → Check dimensions
    ↓
center_model + lay_flat → Optimize
    ↓
slice_stl → Generate print file
    ↓
confirm_temperatures → Verify settings
    ↓
print_3mf/send to printer → Print!
```

## Troubleshooting

### Model too small/large in preview
- Use camera_position parameter in render_single
- Adjust image_size for detail

### STL has floating vertices
- Run merge_vertices with 0.01mm tolerance
- Reslice after merging

### Print orientation issues
- Use rotate_stl before lay_flat
- lay_flat finds largest face, rotate if needed

### Printer temperature mismatches
- Use confirm_temperatures before printing
- Override with bed_temperature/nozzle_temperature in print_3mf

### Slicing fails
- Verify STL using get_stl_info
- Check for non-manifold geometry (run merge_vertices)
- Ensure slicer_type is available: prusaslicer, cura, slic3r, orcaslicer

## Integration with Project Workflow

### Typical Session
```bash
# 1. Edit parameters in main.scad

# 2. Quick preview
render_single(scad_file=src/main.scad, view=isometric)

# 3. Make adjustments, repeat step 2

# 4. Final render
openscad -o stl/model.stl src/main.scad

# 5. Prep and print
center_model(stl/model.stl)
lay_flat(stl/model.stl)
slice_stl(stl/model.stl)

# 6. Check settings
confirm_temperatures(gcode_path=model.gcode, bed_temp=60, extruder_temp=200)

# 7. Print
print_3mf(three_mf_path=model.3mf)
```

### Watch for Optimization Opportunities
- If frequently adjusting specific parameters, use Customizer UI
- If batch processing multiple models, create Python helper
- If testing tolerances, use scale_stl between iterations
