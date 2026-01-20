// Practical labeling examples for OpenSCAD
// Demonstrates common labeling patterns for workshop parts

include <BOSL2/std.scad>

// Select which example to render (uncomment one)
//example = "part_label";
//example = "storage_bin";
//example = "dimension_annotation";
//example = "multi_face_box";
example = "all_examples";

// ============================================
// Example 1: Part Number Label Tag
// ============================================
module part_label(part_num, size=[40, 15, 2]) {
    diff()
    cuboid(size, rounding=1, edges="Z")
        attach(TOP, BOT, inside=true)
            tag("remove")
            linear_extrude(0.5)
                text(
                    part_num,
                    size=size.y * 0.5,
                    font="Liberation Mono",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Example 2: Labeled Storage Bin
// ============================================
module storage_bin(label_text, bin_size=[100, 100, 50]) {
    diff()
    cuboid(bin_size, rounding=3, edges="Z") {
        // Hollow out interior
        attach(TOP, BOT, inside=true)
            tag("remove")
            down(2)
            cuboid([bin_size.x-6, bin_size.y-6, bin_size.z], rounding=2);

        // Label on front face
        attach(FRONT, BACK)
            up(bin_size.z/4)
            linear_extrude(2)
                text(
                    label_text,
                    size=bin_size.y/10,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
    }
}

// ============================================
// Example 3: Dimension Annotation (Debug)
// ============================================
module dimension_annotation(length, pos=[0,0,0], rot=[0,0,0]) {
    translate(pos) rotate(rot) {
        color("red", 0.8) {
            // Dimension line
            cube([length, 0.5, 0.5], center=true);

            // End markers
            translate([-length/2, 0, 0]) sphere(d=2);
            translate([length/2, 0, 0]) sphere(d=2);

            // Dimension text
            translate([0, 0, 5])
                linear_extrude(0.5)
                    text(
                        str(length, "mm"),
                        size=4,
                        font="Liberation Mono",
                        halign="center",
                        valign="center"
                    );
        }
    }
}

// ============================================
// Example 4: Multi-Face Labeled Box
// ============================================
module labeled_box(size, labels) {
    // labels array: [TOP, BOTTOM, FRONT, BACK, LEFT, RIGHT]
    faces = [TOP, BOTTOM, FRONT, BACK, LEFT, RIGHT];

    diff()
    cuboid(size, rounding=1, edges="Z")
        for (i = [0:5])
            if (labels[i] != "")
                attach(faces[i], BOT)
                    tag("remove")
                    linear_extrude(1)
                        text(
                            labels[i],
                            size=size.x/10,
                            font="Liberation Sans",
                            halign="center",
                            valign="center"
                        );
}

// ============================================
// Example 5: Serial Number Label (Small)
// ============================================
module serial_number_label(sn) {
    size = [30, 10, 1.5];
    diff()
    cuboid(size, rounding=0.5, edges="Z")
        attach(TOP, BOT, inside=true)
            tag("remove")
            linear_extrude(0.3)
                text(
                    str("SN:", sn),
                    size=3,
                    font="Liberation Mono",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Example 6: Multi-Line Label
// ============================================
module multiline_label(lines, size=[50, 30, 3], text_size=6) {
    line_height = text_size * 1.5;
    total_height = len(lines) * line_height;

    diff()
    cuboid(size, rounding=1, edges="Z")
        attach(TOP, BOT, inside=true)
            tag("remove")
            linear_extrude(0.5) {
                for (i = [0:len(lines)-1]) {
                    offset = (len(lines) - 1 - i) * line_height - total_height/2 + line_height/2;
                    translate([0, offset, 0])
                        text(
                            lines[i],
                            size=text_size,
                            font="Liberation Sans",
                            halign="center",
                            valign="center"
                        );
                }
            }
}

// ============================================
// Example 7: Raised Text (Embossed)
// ============================================
module embossed_label(label_text, base_size=[60, 40, 5]) {
    cuboid(base_size, rounding=2, edges="Z")
        attach(TOP, BOT)
            linear_extrude(1.5)
                text(
                    label_text,
                    size=base_size.x/8,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Render Selected Example
// ============================================

if (example == "part_label") {
    part_label("PART-001");
}
else if (example == "storage_bin") {
    storage_bin("SCREWS");
}
else if (example == "dimension_annotation") {
    // Show dimension annotation on a cube
    cube([50, 30, 20]);
    dimension_annotation(50, pos=[25, -20, 25], rot=[0, 0, 0]);
    dimension_annotation(30, pos=[55, 15, 10], rot=[0, 0, 90]);
}
else if (example == "multi_face_box") {
    labeled_box([50, 40, 30], ["TOP", "BOT", "FRONT", "BACK", "L", "R"]);
}
else if (example == "all_examples") {
    // Display all examples in a grid
    right(0) part_label("PN-001");
    right(50) serial_number_label("123456");
    right(100) embossed_label("RAISED");

    back(30) right(0) storage_bin("BINS", [60, 60, 40]);
    back(30) right(80) labeled_box([40, 30, 25], ["T", "B", "F", "K", "L", "R"]);
    back(30) right(140) multiline_label(["LINE 1", "LINE 2"], [50, 30, 3], 5);
}

// Usage notes:
// 1. Change 'example' variable at top to render specific example
// 2. Customize dimensions and text as needed
// 3. Copy modules into your projects
// 4. Adjust text sizes relative to part dimensions
