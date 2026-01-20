// Different cabinet configurations to demonstrate cut list variations
// Run each section independently by commenting out others

include <woodworkers-lib/std.scad>

thick = 18;
rounding = 2;

// VARIATION 1: Simple box (no doors, no edge banding)
// Uncomment to render:
/*
simple_box = [600, 400, 800];
planeLeft(simple_box, t=-1, b=-1);
planeRight(simple_box, t=-1, b=-1);
planeTop(simple_box);
planeBottom(simple_box);
planeBack(simple_box, thick=4);

// Expected output (5 panels):
// ECHO: "plane (left):   18 × 382 × 764"
// ECHO: "plane (right):  18 × 382 × 764"
// ECHO: "plane (top):    600 × 382 × 18"
// ECHO: "plane (bottom): 600 × 382 × 18"
// ECHO: "plane (back):   600 × 4 × 800"
*/

// VARIATION 2: Cabinet with single shelf and full edge banding
// Uncomment to render:
/*
shelf_cabinet = [800, 500, 1000];
translate([0, 0, 0]) {
    planeLeft(shelf_cabinet, f=-1, t=-1, b=-1, af=4, at=4, ab=4);
    planeRight(shelf_cabinet, f=-1, t=-1, b=-1, af=4, at=4, ab=4);
    planeTop(shelf_cabinet, f=-1, af=4, al=4, ar=4);
    planeBottom(shelf_cabinet, f=-1, af=4, al=4, ar=4);
    planeBack(shelf_cabinet, thick=4);

    // Middle shelf
    translate([0, 0, 500])
        planeBottom(shelf_cabinet, l=-1, r=-1, f=-1, af=4);
}

// Expected output (6 panels):
// - 2× sides: 18×482(4,4,4)×964(4,4,4) (3 edges each)
// - 2× top/bottom: 782(4,4,4)×482×18 (3 edges)
// - 1× shelf: 764(4)×482×18 (1 edge)
// - 1× back: 800×4×1000 (no edges)
*/

// VARIATION 3: Drawer cabinet with dividers
// Uncomment to render:
/*
drawer_cabinet = [600, 450, 900];
translate([100, 0, 0]) {
    // Outer frame
    planeLeft(drawer_cabinet, f=-1, t=-1, b=-1, af=4);
    planeRight(drawer_cabinet, f=-1, t=-1, b=-1, af=4);
    planeTop(drawer_cabinet, f=-1, af=4, al=4, ar=4);
    planeBottom(drawer_cabinet, f=-1, af=4, al=4, ar=4);

    // Horizontal dividers (3 drawer compartments)
    translate([0, 0, 300])
        planeBottom(drawer_cabinet, l=-1, r=-1, f=-1, af=4);
    translate([0, 0, 600])
        planeBottom(drawer_cabinet, l=-1, r=-1, f=-1, af=4);

    // Vertical divider (half-width)
    translate([drawer_cabinet[0]/2, 0, 0])
        planeLeft([drawer_cabinet[0]/2, drawer_cabinet[1], drawer_cabinet[2]],
                  f=-1, t=-1, b=-1, af=4);
}

// Expected output (7 panels):
// - 3× sides (2 outer + 1 divider): 18×432(4)×864
// - 4× horizontal (top, bottom, 2 shelves): various widths×432×18
*/

// VARIATION 4: Wall-mounted cabinet (no bottom, back recess)
// Uncomment to render:
wall_cabinet = [1200, 350, 600];
translate([200, 0, 0]) {
    planeLeft(wall_cabinet, f=-1, t=-1, af=4, at=4);
    planeRight(wall_cabinet, f=-1, t=-1, af=4, at=4);
    planeTop(wall_cabinet, f=-1, af=4, al=4, ar=4);

    // Back panel recessed 10mm from edges
    translate([10, 10, 0])
        planeBack([wall_cabinet[0]-20, wall_cabinet[1]-10, wall_cabinet[2]],
                  thick=4);

    // Two shelves
    translate([0, 0, 200])
        planeBottom(wall_cabinet, l=-1, r=-1, f=-1, af=4);
    translate([0, 0, 400])
        planeBottom(wall_cabinet, l=-1, r=-1, f=-1, af=4);
}

// Expected output (6 panels):
// - 2× sides: 18×332(4,4)×582
// - 1× top: 1182(4,4,4)×332×18
// - 2× shelves: 1164(4)×332×18
// - 1× back: 1180×4×600 (custom size due to recess)

// TIPS FOR USING THESE VARIATIONS:
// 1. Render one variation at a time (comment out others)
// 2. Compare ECHO output to expected dimensions
// 3. Note how edge banding changes based on visible edges
// 4. Observe how thickness-relative parameters (-1) automatically adjust sizes
// 5. Use these as templates for your own designs
