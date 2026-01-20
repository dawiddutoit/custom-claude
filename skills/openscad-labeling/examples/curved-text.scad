// Curved surface text examples for OpenSCAD
// Demonstrates text_on_OpenSCAD library usage

// NOTE: Requires text_on_OpenSCAD library installation
// Install: cd ~/Documents/OpenSCAD/libraries && git clone https://github.com/brodykenrick/text_on_OpenSCAD.git

use <text_on_OpenSCAD/text_on.scad>

// Select which example to render (uncomment one)
//example = "cylinder_label";
//example = "sphere_label";
//example = "pipe_label";
example = "all_curved";

// ============================================
// Example 1: Cylinder Label
// ============================================
module cylinder_label(label_text, r=15, h=30) {
    difference() {
        cylinder(r=r, h=h, center=true);

        // Text wrapped around cylinder
        text_on_cylinder(
            label_text,
            r=r + 0.5,  // Slightly larger to cut into surface
            h=h,
            size=4,
            font="Liberation Sans",
            direction="ltr"
        );
    }
}

// ============================================
// Example 2: Sphere Label (Hemisphere)
// ============================================
module sphere_label(label_text, r=20) {
    difference() {
        sphere(r=r);

        // Text on sphere surface
        text_on_sphere(
            label_text,
            r=r + 0.5,
            size=5,
            font="Liberation Sans"
        );
    }
}

// ============================================
// Example 3: Pipe with Rotated Labels
// ============================================
module labeled_pipe(labels, r=12, h=60) {
    difference() {
        // Pipe (hollow cylinder)
        difference() {
            cylinder(r=r, h=h, center=true);
            cylinder(r=r-3, h=h+1, center=true);
        }

        // Multiple labels around circumference
        for (i = [0:len(labels)-1]) {
            rotate([0, 0, i * 360 / len(labels)])
                translate([0, 0, 0])
                    text_on_cylinder(
                        labels[i],
                        r=r + 0.5,
                        h=h,
                        size=3,
                        font="Liberation Mono",
                        direction="ltr"
                    );
        }
    }
}

// ============================================
// Example 4: Bottle Cap with Embossed Text
// ============================================
module bottle_cap(label_text, r=20, h=10) {
    difference() {
        // Cap body
        union() {
            cylinder(r=r, h=h);
            translate([0, 0, h])
                cylinder(r1=r, r2=r-2, h=3);
        }

        // Raised text on top
        translate([0, 0, h + 2])
            text_on_cylinder(
                label_text,
                r=r * 0.7,
                h=2,
                size=3,
                font="Liberation Sans"
            );
    }
}

// ============================================
// Example 5: Cylinder with Vertical Text
// ============================================
module vertical_cylinder_label(label_text, r=15, h=40) {
    difference() {
        cylinder(r=r, h=h, center=true);

        // Vertical text (top-to-bottom)
        text_on_cylinder(
            label_text,
            r=r + 0.5,
            h=h,
            size=4,
            font="Liberation Sans",
            direction="ttb"  // Top-to-bottom
        );
    }
}

// ============================================
// Example 6: Globe with Country Name
// ============================================
module globe_label(r=25) {
    difference() {
        sphere(r=r);

        // Multiple labels at different latitudes
        text_on_sphere("NORTH", r=r + 0.5, size=4);

        rotate([60, 0, 0])
            text_on_sphere("EQUATOR", r=r + 0.5, size=5);

        rotate([120, 0, 0])
            text_on_sphere("SOUTH", r=r + 0.5, size=4);
    }
}

// ============================================
// Render Selected Example
// ============================================

if (example == "cylinder_label") {
    cylinder_label("LABEL-001");
}
else if (example == "sphere_label") {
    sphere_label("GLOBE");
}
else if (example == "pipe_label") {
    labeled_pipe(["INLET", "OUTLET", "DRAIN"], r=15, h=80);
}
else if (example == "all_curved") {
    // Display all examples in a row

    // Cylinder with horizontal text
    right(0) cylinder_label("HORIZ", r=12, h=30);

    // Cylinder with vertical text
    right(40) vertical_cylinder_label("VERT", r=12, h=35);

    // Labeled pipe
    right(80) labeled_pipe(["A", "B", "C"], r=12, h=60);

    // Sphere
    right(130) sphere_label("SPHERE", r=18);

    // Bottle cap
    right(180) bottle_cap("CAP", r=18, h=8);

    // Globe
    right(230) globe_label(r=20);
}

// ============================================
// Library Check Helper
// ============================================

// If text_on_OpenSCAD is not installed, you'll see an error:
// "Can't find library 'text_on_OpenSCAD/text_on.scad'"
//
// Install it with:
// cd ~/Documents/OpenSCAD/libraries
// git clone https://github.com/brodykenrick/text_on_OpenSCAD.git

// ============================================
// Usage Notes
// ============================================

// 1. text_on_cylinder parameters:
//    - r: radius (slightly larger than object to cut in)
//    - h: height
//    - size: text size
//    - font: font name
//    - direction: "ltr", "rtl", "ttb", "btt"

// 2. text_on_sphere parameters:
//    - r: radius (slightly larger than object)
//    - size: text size
//    - font: font name

// 3. For engraved text, use difference() and r slightly larger than object
// 4. For raised text, use union() and r slightly smaller than object
// 5. Adjust size relative to radius (typically r/5 to r/3)
