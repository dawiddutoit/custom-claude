# Integration Guide

How to integrate the openscad-labeling skill into your project.

## Automatic Discovery

This skill is automatically discovered if installed in:
- `~/.claude/skills/openscad-labeling/` (global user skills)
- `.claude/skills/openscad-labeling/` (project-local skills)

No configuration changes needed - Claude will find and invoke it based on trigger phrases.

## Testing Discovery

Try these phrases to verify the skill is discoverable:

```
"How do I label a cube in OpenSCAD?"
"Add text to the TOP face"
"Install text_on_OpenSCAD library"
"Text on cylinder in OpenSCAD"
"Label this model with part numbers"
```

## Adding to Project CLAUDE.md (Optional)

If you want explicit documentation in your project's CLAUDE.md, add this entry to the skills list:

```markdown
### OpenSCAD & CAD Design

- [openscad-labeling](~/.claude/skills/openscad-labeling/SKILL.md) - Add text labels to OpenSCAD models using BOSL2's face/anchor system and specialized labeling libraries. Use when labeling model faces, adding part numbers, dimension annotations, or wrapping text on curved surfaces.
```

**Note:** This is purely for documentation. The skill will work without being listed in CLAUDE.md.

## Project Integration Examples

### Workshop Parts Labeling

For the plans repository workshop models:

```openscad
// workshop/workbenches/labeled-drawer.scad
include <BOSL2/std.scad>

module labeled_drawer_front(part_num, size=[400, 150, 18]) {
    diff()
    cuboid(size, rounding=2, edges="Z")
        attach(FRONT, BACK)
            up(size.y/3)
            linear_extrude(1)
                text(
                    part_num,
                    size=size.y/12,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
}
```

### Tool Storage Bins

For gridfinity-style labeled bins:

```openscad
include <BOSL2/std.scad>

module tool_bin(label, grid_x=2, grid_y=2, height_units=5) {
    bin_size = [grid_x * 42, grid_y * 42, height_units * 7];

    diff()
    cuboid(bin_size, rounding=3, edges="Z") {
        // Hollow interior
        attach(TOP, BOT, inside=true)
            tag("remove")
            down(2)
            cuboid([bin_size.x-6, bin_size.y-6, bin_size.z], rounding=2);

        // Front label
        attach(FRONT, BACK)
            up(bin_size.z/4)
            linear_extrude(1.5)
                text(
                    label,
                    size=bin_size.y/8,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
    }
}

tool_bin("DRILL BITS");
```

### Cabinet Part Labels

For workshop cabinet components:

```openscad
include <BOSL2/std.scad>

// Add part numbers to cut list exports
module labeled_panel(part_num, size) {
    cuboid(size, rounding=1, edges="Z")
        attach(TOP, BOT)
            right(size.x/2 - 15)
            back(size.y/2 - 8)
            linear_extrude(0.3)
                text(
                    part_num,
                    size=4,
                    font="Liberation Mono",
                    halign="center",
                    valign="center"
                );
}
```

## Workflow Integration

### 1. Design Phase

Use dimension annotations for debugging:

```openscad
module debug_dimensions(obj_size) {
    // Your object here
    cube(obj_size);

    // Add dimension annotations
    color("red", 0.8) {
        translate([obj_size.x/2, -10, obj_size.z + 5])
            linear_extrude(0.5)
                text(str(obj_size.x, "mm"), size=4, halign="center");

        translate([obj_size.x + 10, obj_size.y/2, obj_size.z/2])
            rotate([90, 0, 90])
            linear_extrude(0.5)
                text(str(obj_size.y, "mm"), size=4, halign="center");
    }
}
```

### 2. Assembly Phase

Add part numbers matching cut list:

```openscad
// Generate cut list with part numbers
// Then add matching labels to 3D model
module cabinet_with_part_numbers() {
    // Each panel gets its cut list part number
    labeled_panel("PN-001", [800, 600, 18]);  // Top
    labeled_panel("PN-002", [800, 600, 18]);  // Bottom
    labeled_panel("PN-003", [600, 500, 18]);  // Side L
    // etc.
}
```

### 3. Documentation Phase

Generate labeled assembly instructions:

```openscad
// Exploded view with labels
module exploded_assembly() {
    // Bottom
    labeled_panel("1. BOTTOM", [800, 600, 18]);

    // Sides (exploded up)
    up(100) {
        labeled_panel("2. LEFT", [600, 500, 18]);
        right(820) labeled_panel("3. RIGHT", [600, 500, 18]);
    }

    // Top (exploded further up)
    up(200)
        labeled_panel("4. TOP", [800, 600, 18]);
}
```

## Library Requirements Check

Run this before starting a project that needs curved text:

```bash
~/.claude/skills/openscad-labeling/scripts/check-text-libraries.sh
```

Expected output:
```
✅ BOSL2
✅ text_on_OpenSCAD
⚠️  attachable_text3d (optional)
```

## Common Patterns for Workshop Project

### Pattern 1: Storage Bin Labels (Most Common)

```openscad
include <BOSL2/std.scad>

// Reusable labeled bin module
module workshop_bin(label, size=[100, 100, 50]) {
    diff()
    cuboid(size, rounding=3, edges="Z") {
        attach(TOP, BOT, inside=true)
            tag("remove")
            down(2)
            cuboid([size.x-6, size.y-6, size.z], rounding=2);

        attach(FRONT, BACK)
            up(size.z/4)
            linear_extrude(2)
                text(label, size=6, halign="center", valign="center");
    }
}
```

### Pattern 2: Cut List Part Numbers

```openscad
// Add to woodworkers-lib workflow
include <woodworkers-lib/std.scad>

module labeled_plywood_panel(part_num, dims) {
    planeCustom(dims)
        attach(TOP, BOT)
            right(dims[0]/2 - 20)
            back(dims[1]/2 - 10)
            linear_extrude(0.5)
                text(part_num, size=5, font="Liberation Mono", halign="center");
}
```

### Pattern 3: Tool Stations

```openscad
// Label tool mounting positions
module tool_station_label(tool_name, pos) {
    translate(pos)
        linear_extrude(1)
            text(tool_name, size=8, font="Liberation Sans", halign="center");
}

// Use in workshop layout
tool_station_label("DRILL PRESS", [1000, 2000, 0]);
tool_station_label("MITRE SAW", [3000, 500, 0]);
```

## Troubleshooting

### Issue: Skill not triggering

**Check skill location:**
```bash
ls -la ~/.claude/skills/openscad-labeling/SKILL.md
```

**Verify YAML is valid:**
```bash
python3 -c "
import yaml
with open('~/.claude/skills/openscad-labeling/SKILL.md') as f:
    lines = []
    delim = 0
    for line in f:
        if line.strip() == '---':
            delim += 1
            if delim == 2: break
        if delim > 0: lines.append(line)
    yaml.safe_load(''.join(lines))
    print('✅ Valid')
"
```

### Issue: Examples not rendering

**Check library installations:**
```bash
~/.claude/skills/openscad-labeling/scripts/check-text-libraries.sh
```

**Test with minimal example:**
```openscad
include <BOSL2/std.scad>

cuboid([50, 30, 20])
    attach(TOP, BOT)
        linear_extrude(2)
            text("TEST", size=8, halign="center", valign="center");
```

### Issue: Text backwards or wrong orientation

**Use BOSL2 attach (not manual rotation):**
```openscad
// ✅ CORRECT
attach(TOP, BOT) text("LABEL");

// ❌ WRONG
translate([...]) rotate([...]) text("LABEL");
```

## Next Steps

1. Copy practical-labels.scad patterns into your workshop models
2. Add part number labels to match cut lists
3. Create labeled storage bins for tool organization
4. Use dimension annotations during design phase
5. Install curved text libraries if needed for pipe/cylinder labeling

## Resources

- Skill documentation: `~/.claude/skills/openscad-labeling/SKILL.md`
- Library comparison: `~/.claude/skills/openscad-labeling/references/library-comparison.md`
- Font reference: `~/.claude/skills/openscad-labeling/references/font-reference.md`
- Practical examples: `~/.claude/skills/openscad-labeling/examples/`
- Installation check: `~/.claude/skills/openscad-labeling/scripts/check-text-libraries.sh`
