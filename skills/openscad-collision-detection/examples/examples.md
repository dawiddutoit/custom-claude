# OpenSCAD Collision Detection Examples

Comprehensive examples for detecting and visualizing collisions in woodworking and furniture projects.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Drawer Scenarios](#drawer-scenarios)
3. [Door Scenarios](#door-scenarios)
4. [Shelf Scenarios](#shelf-scenarios)
5. [Hinge Scenarios](#hinge-scenarios)
6. [Room Layout Scenarios](#room-layout-scenarios)
7. [Assembly Scenarios](#assembly-scenarios)
8. [Advanced Patterns](#advanced-patterns)

## Basic Examples

### Example 1: Simple Overlap Detection

```openscad
// Two overlapping cubes
module basic_overlap() {
    // First cube (transparent)
    %color("blue", 0.3)
        cube([30, 20, 10]);

    // Second cube (solid)
    color("green", 0.5)
        translate([10, 0, 0])
        cube([30, 20, 10]);

    // Show overlap region
    color("red", 0.8)
        intersection() {
            cube([30, 20, 10]);
            translate([10, 0, 0]) cube([30, 20, 10]);
        }
}

basic_overlap();
```

**Expected result:** 20×20×10mm red overlap region.

### Example 2: Reusable Collision Checker

```openscad
module check_collision(show_overlap=true, overlap_color="red") {
    if (show_overlap) {
        color(overlap_color, 0.8) intersection() {
            children(0);
            children(1);
        }
    }
    %children(0);
    children(1);
}

// Usage
check_collision() {
    cube([50, 50, 50]);
    translate([25, 25, 25]) sphere(r=30, $fn=32);
}
```

### Example 3: No Collision (Clearance Validation)

```openscad
module clearance_validation() {
    // Cabinet interior
    interior_width = 782;

    // Drawer with clearance
    drawer_width = 764;
    clearance = (interior_width - drawer_width) / 2;

    echo(str("Clearance per side: ", clearance, "mm"));

    // Visual check
    %color("blue", 0.2)
        translate([0, 0, 0])
        cube([interior_width, 400, 300]);

    color("green", 0.5)
        translate([clearance, 0, 0])
        cube([drawer_width, 380, 280]);

    // Collision check (should be empty)
    color("red")
        intersection() {
            cube([interior_width, 400, 300]);
            translate([clearance, 0, 0]) cube([drawer_width, 380, 280]);
        }
}

clearance_validation();
// ECHO: "Clearance per side: 9mm" (no red region)
```

## Drawer Scenarios

### Example 4: Drawer Side Clearance

```openscad
include <woodworkers-lib/std.scad>

module drawer_side_clearance() {
    panel = 18;
    cabinet_dim = [800, 500, 720];
    drawer_dim = [764, 480, 100];

    interior_w = cabinet_dim[0] - 2*panel;
    side_clearance = (interior_w - drawer_dim[0]) / 2;

    echo(str("Cabinet interior width: ", interior_w, "mm"));
    echo(str("Drawer width: ", drawer_dim[0], "mm"));
    echo(str("Side clearance: ", side_clearance, "mm per side"));

    // Cabinet interior (ghost)
    %color("blue", 0.2)
        translate([panel, 0, panel])
        cube([interior_w, cabinet_dim[1]-panel, cabinet_dim[2]-2*panel]);

    // Drawer
    color("green", 0.5)
        translate([panel + side_clearance, 0, panel])
        cube(drawer_dim);

    // Collision check
    color("red")
        intersection() {
            translate([panel, 0, panel])
                cube([interior_w, cabinet_dim[1]-panel, cabinet_dim[2]-2*panel]);
            translate([panel + side_clearance, 0, panel])
                cube(drawer_dim);
        }
}

drawer_side_clearance();
// Expected: 9mm per side, no collision
```

### Example 5: Drawer Depth Collision

```openscad
module drawer_depth_collision() {
    panel = 18;
    back_panel = 6;
    cabinet_depth = 500;
    drawer_depth = 490;  // TOO DEEP - will hit back panel

    interior_depth = cabinet_depth - back_panel;

    echo(str("Interior depth: ", interior_depth, "mm"));
    echo(str("Drawer depth: ", drawer_depth, "mm"));

    if (drawer_depth > interior_depth) {
        echo("ERROR: Drawer extends beyond back panel!");
    }

    // Cabinet interior
    %color("blue", 0.2)
        cube([800, interior_depth, 300]);

    // Back panel
    %color("brown")
        translate([0, interior_depth, 0])
        cube([800, back_panel, 300]);

    // Drawer (extends too far)
    color("green", 0.5)
        cube([764, drawer_depth, 100]);

    // Show collision with back panel
    color("red")
        intersection() {
            translate([0, interior_depth, 0]) cube([800, back_panel, 300]);
            cube([764, drawer_depth, 100]);
        }
}

drawer_depth_collision();
// Shows 4mm overlap with back panel
```

### Example 6: Drawer Vertical Clearance

```openscad
module drawer_vertical_clearance() {
    panel = 18;
    drawer_height = 100;
    drawer_positions = [panel, panel+120, panel+240];  // Stack of 3 drawers

    top_clearance = 5;  // Minimum clearance above drawer

    for (i = [0:len(drawer_positions)-1]) {
        z = drawer_positions[i];

        // Drawer
        color("green", 0.5)
            translate([18, 0, z])
            cube([764, 480, drawer_height]);

        // Check if next drawer collides
        if (i < len(drawer_positions)-1) {
            next_z = drawer_positions[i+1];
            gap = next_z - (z + drawer_height);

            echo(str("Gap above drawer ", i, ": ", gap, "mm"));

            if (gap < top_clearance) {
                echo(str("ERROR: Insufficient clearance (", gap, "mm < ", top_clearance, "mm)"));

                // Highlight problem area
                color("red", 0.8)
                    translate([18, 0, z + drawer_height])
                    cube([764, 480, gap]);
            }
        }
    }
}

drawer_vertical_clearance();
// Expected: 2mm gaps - highlights red warning regions
```

### Example 7: Drawer Fully Extended

```openscad
module drawer_extended_clearance() {
    cabinet_depth = 500;
    drawer_depth = 480;
    extension = 400;  // Drawer slides extend 400mm

    // Cabinet
    %color("blue", 0.2)
        cube([800, cabinet_depth, 300]);

    // Drawer in closed position
    *color("green", 0.3)
        translate([18, 0, 100])
        cube([764, drawer_depth, 100]);

    // Drawer fully extended
    color("green", 0.6)
        translate([18, -extension, 100])
        cube([764, drawer_depth, 100]);

    // Check clearance in front of cabinet
    front_clearance = 50;  // Obstacle 50mm from cabinet front
    if (extension > front_clearance) {
        echo("WARNING: Drawer extends beyond available space!");

        // Show collision zone
        color("red", 0.5)
            translate([18, -extension, 100])
            cube([764, extension - front_clearance, 100]);
    }
}

drawer_extended_clearance();
```

## Door Scenarios

### Example 8: Door Swing Clearance

```openscad
module door_swing_clearance() {
    door_width = 400;
    door_thick = 18;
    swing_angle = 90;

    // Cabinet
    %color("brown", 0.3)
        cube([800, 500, 720]);

    // Door in closed position
    *color("blue", 0.3)
        translate([-door_thick, 0, 0])
        cube([door_thick, door_width, 720]);

    // Door swing path (transparent yellow)
    color("yellow", 0.2)
        linear_extrude(720)
        rotate([0, 0, -swing_angle])
        translate([0, 0, 0])
        square([door_width, door_thick]);

    // Adjacent object (wall or furniture)
    adjacent_distance = 350;
    color("gray", 0.5)
        translate([-adjacent_distance, 0, 0])
        cube([50, 500, 720]);

    // Check collision
    color("red")
        intersection() {
            linear_extrude(720)
                rotate([0, 0, -swing_angle])
                square([door_width, door_thick]);
            translate([-adjacent_distance, 0, 0])
                cube([50, 500, 720]);
        }

    clearance = adjacent_distance - door_width;
    echo(str("Door clearance: ", clearance, "mm"));
}

door_swing_clearance();
```

### Example 9: Double Door Interference

```openscad
module double_door_interference() {
    door_width = 400;
    door_thick = 18;
    swing_angle = 110;  // Opens beyond 90°

    // Left door swing
    color("blue", 0.3)
        linear_extrude(720)
        rotate([0, 0, -swing_angle])
        square([door_width, door_thick]);

    // Right door swing
    color("green", 0.3)
        translate([800, 0, 0])
        linear_extrude(720)
        rotate([0, 0, swing_angle])
        translate([-door_width, 0])
        square([door_width, door_thick]);

    // Check if doors collide when both open
    color("red")
        intersection() {
            linear_extrude(720)
                rotate([0, 0, -swing_angle])
                square([door_width, door_thick]);

            translate([800, 0, 0])
                linear_extrude(720)
                rotate([0, 0, swing_angle])
                translate([-door_width, 0])
                square([door_width, door_thick]);
        }
}

double_door_interference();
```

### Example 10: Door Hits Drawer Front

```openscad
module door_drawer_collision() {
    door_width = 400;

    // Cabinet
    %color("brown", 0.3)
        cube([800, 500, 720]);

    // Door open 90°
    color("blue", 0.4)
        translate([0, 0, 0])
        rotate([0, 0, -90])
        cube([door_width, 18, 720]);

    // Drawer extended 300mm
    drawer_extension = 300;
    drawer_z = 200;

    color("green", 0.5)
        translate([18, -drawer_extension, drawer_z])
        cube([764, 480, 100]);

    // Check collision between door and drawer
    color("red")
        intersection() {
            rotate([0, 0, -90]) cube([door_width, 18, 720]);
            translate([18, -drawer_extension, drawer_z]) cube([764, 480, 100]);
        }
}

door_drawer_collision();
// Shows collision - need to close drawer before opening door
```

## Shelf Scenarios

### Example 11: Shelf Spacing for Standard Items

```openscad
module shelf_spacing_check() {
    cabinet_dim = [800, 400, 1200];
    panel = 18;

    // Shelf positions (Z coordinates)
    shelf_positions = [0, 300, 550, 900];  // 250mm gap at index 1-2

    // Item height requirements
    item_height = 300;

    // Draw shelves
    for (z = shelf_positions) {
        translate([0, 0, z])
            %color("brown")
            cube([cabinet_dim[0], cabinet_dim[1], panel]);
    }

    // Check spacing between consecutive shelves
    for (i = [0:len(shelf_positions)-2]) {
        spacing = shelf_positions[i+1] - shelf_positions[i] - panel;

        echo(str("Shelf ", i, " to ", i+1, " spacing: ", spacing, "mm"));

        if (spacing < item_height) {
            echo(str("ERROR: Space (", spacing, "mm) < required (", item_height, "mm)"));

            // Highlight insufficient spacing
            translate([0, 0, shelf_positions[i] + panel])
                color("red", 0.5)
                cube([cabinet_dim[0], cabinet_dim[1], spacing]);
        } else {
            // Show available space (green)
            translate([100, 100, shelf_positions[i] + panel])
                color("green", 0.3)
                cube([200, 200, item_height]);
        }
    }
}

shelf_spacing_check();
// Highlights 250mm gap as insufficient (red)
```

### Example 12: Adjustable Shelf Collision

```openscad
module adjustable_shelf_collision() {
    cabinet_height = 1200;
    panel = 18;

    // Fixed shelves
    fixed_positions = [0, cabinet_height - panel];

    // Adjustable shelf (user-defined position)
    adjustable_z = 400;

    // Minimum spacing
    min_spacing = 250;

    // Draw fixed shelves
    for (z = fixed_positions) {
        translate([0, 0, z])
            %color("brown")
            cube([800, 400, panel]);
    }

    // Draw adjustable shelf
    translate([0, 0, adjustable_z])
        color("blue", 0.5)
        cube([800, 400, panel]);

    // Check spacing to nearest shelf
    for (z = fixed_positions) {
        spacing = abs(adjustable_z - z) - panel;

        if (spacing < min_spacing && adjustable_z != z) {
            echo(str("ERROR: Adjustable shelf too close (", spacing, "mm)"));

            // Highlight problem
            color("red", 0.5) {
                translate([0, 0, min(adjustable_z, z) + panel])
                    cube([800, 400, spacing]);
            }
        }
    }
}

adjustable_shelf_collision();
```

### Example 13: Shelf Sag Under Load

```openscad
module shelf_sag_visualization() {
    shelf_length = 800;
    shelf_thickness = 18;
    max_sag = 5;  // Maximum acceptable sag at center

    // Shelf (approximated sag with linear_extrude)
    color("brown", 0.5)
        translate([0, 0, 0])
        linear_extrude(shelf_thickness, scale=[1, 0.99])
        square([shelf_length, 400]);

    // Items on shelf
    translate([100, 100, shelf_thickness])
        color("green", 0.5)
        cube([200, 200, 300]);

    // Bottom shelf
    translate([0, 0, -300])
        %color("brown")
        cube([shelf_length, 400, shelf_thickness]);

    // Check if sag causes collision
    sag_clearance = 300 - max_sag - shelf_thickness;
    min_clearance = 250;

    if (sag_clearance < min_clearance) {
        echo(str("WARNING: Sag reduces clearance to ", sag_clearance, "mm"));

        color("red", 0.5)
            translate([shelf_length/2 - 50, 0, -max_sag])
            cube([100, 400, max_sag]);
    }
}

shelf_sag_visualization();
```

## Hinge Scenarios

### Example 14: Hinge Cup to Door Clearance

```openscad
module hinge_cup_clearance() {
    panel = 18;
    hinge_cup_diameter = 35;
    hinge_cup_depth = 12;
    door_thickness = 18;

    // Cabinet side panel
    %color("brown")
        cube([panel, 400, 720]);

    // Hinge (Blum-style cup hinge)
    translate([panel, 100, 360])
        color("silver")
        rotate([0, 90, 0])
        cylinder(d=hinge_cup_diameter, h=hinge_cup_depth, $fn=32);

    // Hinge arm
    translate([panel + hinge_cup_depth, 100, 360])
        color("silver")
        cube([20, 5, 15]);

    // Door panel
    translate([panel + hinge_cup_depth + 2, 0, 0])  // 2mm gap
        color("blue", 0.5)
        cube([door_thickness, 400, 720]);

    // Check collision between hinge cup and door
    color("red")
        intersection() {
            translate([panel, 100, 360])
                rotate([0, 90, 0])
                cylinder(d=hinge_cup_diameter, h=hinge_cup_depth + 5);

            translate([panel + hinge_cup_depth + 2, 0, 0])
                cube([door_thickness, 400, 720]);
        }

    gap = 2;
    echo(str("Hinge-to-door gap: ", gap, "mm"));
}

hinge_cup_clearance();
```

### Example 15: Soft-Close Mechanism Interference

```openscad
module soft_close_interference() {
    panel = 18;
    drawer_side_height = 100;
    soft_close_height = 40;  // Soft-close damper height

    // Drawer side
    color("green", 0.5)
        cube([panel, 480, drawer_side_height]);

    // Soft-close damper mounted below
    translate([0, 480 - 50, 0])
        color("gray")
        cube([50, 50, soft_close_height]);

    // Cabinet bottom
    translate([0, 0, -panel])
        %color("brown")
        cube([800, 500, panel]);

    // Check if damper extends below drawer bottom
    if (soft_close_height > drawer_side_height) {
        echo("ERROR: Soft-close extends below drawer!");

        color("red")
            translate([0, 480 - 50, 0])
            cube([50, 50, soft_close_height - drawer_side_height]);
    }
}

soft_close_interference();
```

## Room Layout Scenarios

### Example 16: Workbench Against Wall

```openscad
// Workshop coordinate system (NW origin)
module workbench_wall_check() {
    room_ew = 6440;
    room_ns = 6070;

    // South wall
    translate([0, -room_ns, 0])
        %color("gray", 0.3)
        cube([room_ew, 10, 2480]);

    // Workbench dimensions
    bench_width = 2000;
    bench_depth = 700;  // Check if this fits!
    bench_height = 900;

    // Available depth from south wall
    available_depth = 650;

    // Place workbench against south wall
    translate([1000, -room_ns + 10, 0])
        color("brown", 0.5)
        cube([bench_width, bench_depth, bench_height]);

    // Check collision with wall
    if (bench_depth > available_depth) {
        echo(str("ERROR: Workbench depth (", bench_depth,
                 "mm) > available (", available_depth, "mm)"));

        // Highlight overhang
        translate([1000, -room_ns + 10 + available_depth, 0])
            color("red", 0.8)
            cube([bench_width, bench_depth - available_depth, bench_height]);
    }
}

workbench_wall_check();
```

### Example 17: Cabinet Door Opens Into Walkway

```openscad
module door_walkway_clearance() {
    room_ns = 6070;
    walkway_width = 1000;  // Minimum walkway requirement

    // Cabinet against wall
    translate([0, -room_ns + 10, 0])
        %color("brown", 0.3)
        cube([800, 500, 720]);

    // Door open 90°
    door_width = 400;
    translate([0, -room_ns + 10, 0])
        color("blue", 0.4)
        rotate([0, 0, -90])
        cube([door_width, 18, 720]);

    // Walkway boundary
    walkway_boundary_y = -room_ns + 10 + 500 + walkway_width;

    %color("yellow", 0.1)
        translate([0, -room_ns + 10 + 500, 0])
        cube([6440, walkway_width, 10]);

    // Check if door intrudes into walkway
    remaining_width = abs((-room_ns + 10 - door_width) - walkway_boundary_y);

    echo(str("Walkway width with door open: ", remaining_width, "mm"));

    if (remaining_width < walkway_width) {
        echo("WARNING: Door blocks walkway!");

        color("red", 0.5)
            translate([0, -room_ns + 10 - door_width, 0])
            cube([800, door_width - (500 + walkway_width - remaining_width), 720]);
    }
}

door_walkway_clearance();
```

## Assembly Scenarios

### Example 18: Multi-Part Assembly Check

```openscad
module multi_part_assembly() {
    explode = $preview;  // Explode in preview, assemble in render
    spacing = explode ? 100 : 0;

    // Part 1: Cabinet shell
    color("brown", 0.5)
        cube([800, 500, 720]);

    // Part 2: Drawer (3 positions)
    for (i = [0:2]) {
        translate([18, spacing * (i+1), 100 + i*150])
            color("green", 0.5)
            cube([764, 480, 100]);
    }

    // Part 3: Door
    translate([-18 - spacing, 0, 0])
        color("blue", 0.5)
        cube([18, 400, 720]);

    // Check collisions when assembled (explode=false)
    if (!explode) {
        // Check each drawer against cabinet
        for (i = [0:2]) {
            color("red", 0.3)
                intersection() {
                    cube([800, 500, 720]);
                    translate([18, 0, 100 + i*150])
                        cube([764, 480, 100]);
                }
        }
    }
}

multi_part_assembly();
```

### Example 19: Stacked Cabinets

```openscad
module stacked_cabinets() {
    lower_height = 720;
    upper_height = 900;
    gap = 50;  // Gap between cabinets

    // Lower cabinet
    color("brown", 0.5)
        cube([800, 500, lower_height]);

    // Upper cabinet
    translate([0, 0, lower_height + gap])
        color("brown", 0.5)
        cube([800, 400, upper_height]);

    // Check vertical alignment
    upper_depth = 400;
    lower_depth = 500;

    if (upper_depth != lower_depth) {
        overhang = abs(upper_depth - lower_depth);
        echo(str("Depth mismatch: ", overhang, "mm overhang"));

        // Visualize overhang
        translate([0, min(upper_depth, lower_depth), lower_height + gap])
            color("yellow", 0.5)
            cube([800, overhang, upper_height]);
    }
}

stacked_cabinets();
```

## Advanced Patterns

### Example 20: Parametric Collision Validation

```openscad
module parametric_validation(
    cabinet_width = 800,
    drawer_width = 764,
    min_clearance = 4
) {
    panel = 18;
    interior_width = cabinet_width - 2*panel;
    clearance = interior_width - drawer_width;

    // Validate clearance
    assert(clearance >= min_clearance,
           str("Insufficient clearance: ", clearance, "mm < ", min_clearance, "mm"));

    echo(str("✓ Clearance validation passed: ", clearance, "mm"));

    // Visual check
    %color("blue", 0.2)
        translate([panel, 0, 0])
        cube([interior_width, 400, 300]);

    color("green", 0.5)
        translate([panel + clearance/2, 0, 0])
        cube([drawer_width, 380, 280]);
}

// Test with various parameters
parametric_validation(cabinet_width=800, drawer_width=764, min_clearance=4);
```

### Example 21: Batch Collision Testing

```openscad
module batch_collision_test() {
    test_cases = [
        [800, 764, "Standard cabinet"],     // Should pass
        [800, 774, "Tight fit"],           // Should pass
        [800, 780, "Too wide"],            // Should fail
    ];

    for (i = [0:len(test_cases)-1]) {
        cabinet_w = test_cases[i][0];
        drawer_w = test_cases[i][1];
        label = test_cases[i][2];

        panel = 18;
        interior = cabinet_w - 2*panel;
        clearance = interior - drawer_w;

        echo(str("Test ", i, " (", label, "): clearance = ", clearance, "mm"));

        if (clearance < 4) {
            echo(str("  FAIL: Insufficient clearance"));
        } else {
            echo(str("  PASS"));
        }

        // Visual representation
        translate([0, i * 500, 0]) {
            %color("blue", 0.2)
                translate([panel, 0, 0])
                cube([interior, 400, 100]);

            color(clearance >= 4 ? "green" : "red", 0.5)
                translate([panel + clearance/2, 0, 0])
                cube([drawer_w, 380, 80]);
        }
    }
}

batch_collision_test();
```

### Example 22: Automated Clearance Reporting

```openscad
module clearance_report(cabinet_dim, drawer_dim, panel=18) {
    interior_w = cabinet_dim[0] - 2*panel;
    interior_d = cabinet_dim[1] - panel;
    interior_h = cabinet_dim[2] - 2*panel;

    side_clearance = (interior_w - drawer_dim[0]) / 2;
    depth_clearance = interior_d - drawer_dim[1];
    top_clearance = interior_h - drawer_dim[2];

    echo("=== CLEARANCE REPORT ===");
    echo(str("Cabinet interior: ", interior_w, "×", interior_d, "×", interior_h));
    echo(str("Drawer size: ", drawer_dim[0], "×", drawer_dim[1], "×", drawer_dim[2]));
    echo(str("Side clearance: ", side_clearance, "mm per side"));
    echo(str("Depth clearance: ", depth_clearance, "mm"));
    echo(str("Top clearance: ", top_clearance, "mm"));

    issues = 0;
    if (side_clearance < 2) {
        echo("ERROR: Side clearance < 2mm");
        issues = issues + 1;
    }
    if (depth_clearance < 5) {
        echo("ERROR: Depth clearance < 5mm");
        issues = issues + 1;
    }
    if (top_clearance < 5) {
        echo("ERROR: Top clearance < 5mm");
        issues = issues + 1;
    }

    if (issues == 0) {
        echo("✓ All clearances within spec");
    } else {
        echo(str("✗ ", issues, " clearance issues found"));
    }
}

clearance_report(
    cabinet_dim=[800, 500, 720],
    drawer_dim=[764, 480, 100],
    panel=18
);
```

## Usage Tips

1. **Start simple** - Use basic examples to understand concepts
2. **Adapt to your needs** - Modify parameters to match your project
3. **Use echo statements** - Console output reveals dimension problems
4. **Test edge cases** - Try extreme parameter values
5. **Combine patterns** - Mix multiple techniques for complex scenarios
6. **Document clearances** - Add comments explaining minimums
7. **Create reusable modules** - Build library of collision checks
8. **Validate before fabrication** - Always run collision checks

## See Also

- SKILL.md - Core collision detection patterns
- references/reference.md - Technical depth and theory
- docs/OPENSCAD-COLLISION-DETECTION.md - Comprehensive guide
