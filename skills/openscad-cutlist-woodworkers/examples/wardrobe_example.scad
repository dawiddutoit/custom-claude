// Complete wardrobe example from woodworkers-lib README
// Demonstrates all features: panels, edge banding, shelves, and legs
// Run: openscad wardrobe_example.scad 2>&1 | grep "ECHO: \"plane"

include <woodworkers-lib/std.scad>

// Override defaults
thick = 18;      // Panel thickness (mm)
rounding = 2;    // Edge rounding radius (mm)

// Main dimensions [width, depth, height]
wardrobe = [1000, 400, 1200];

// Position wardrobe 10mm from origin
translate([10, 0, 0]) {

    // FRAME: Left and right side panels
    // f=-1: shorten by 1×thick on front (fit inside frame)
    // t=-1, b=-1: shorten on top and bottom (fit between top/bottom panels)
    // af=4: add 4mm ABS edge band on front edge (visible edge)
    planeLeft(wardrobe, f=-1, t=-1, b=-1, af=4);
    planeRight(wardrobe, f=-1, t=-1, b=-1, af=4);

    // FRAME: Top and bottom panels
    // f=-1: shorten on front (recessed from doors)
    // af=4, al=4, ar=4: edge band on front, left, and right (3 visible edges)
    planeTop(wardrobe, f=-1, af=4, al=4, ar=4);
    planeBottom(wardrobe, f=-1, af=4, al=4, ar=4);

    // DOORS: Two front panels (semi-transparent for visualization)
    // rr=-wardrobe[0]/2-1: right door extends to center minus 1mm gap
    // ll=-4: left edge shortened by 4mm (gap at center)
    // al=4, at=4, ar=4, ab=4: edge band on all 4 edges (full door edges)
    #planeFront(wardrobe, rr=-wardrobe[0]/2-1, ll=-4, al=4, at=4, ar=4, ab=4);
    #planeFront(wardrobe, ll=-wardrobe[0]/2-1, rr=-4, al=4, at=4, ar=4, ab=4);

    // BACK PANEL: Thin fiberboard
    // thick=4: override default 18mm to 4mm fiberboard
    // translate([0,4,0]): move 4mm from back edge (recessed)
    color("brown")
    translate([0, 4, 0])
    planeBack(wardrobe, thick=4);

    // SHELVES: Three internal shelves at 120mm intervals
    // l=-1, r=-1: fit between left and right panels
    // f=-1: recessed from front
    // af=4: edge band on front (visible) edge only
    translate([0, 0, 120])
        planeBottom(wardrobe, l=-1, r=-1, f=-1, af=4);
    translate([0, 0, 120*2])
        planeBottom(wardrobe, l=-1, r=-1, f=-1, af=4);
    translate([0, 0, 120*3])
        planeBottom(wardrobe, l=-1, r=-1, f=-1, af=4);

    // LEGS: Four cylindrical legs extending 30mm below wardrobe
    // l=2, r=2: position 2×thick from left/right edges
    // f=3, B=2: position 3×thick from front, 2×thick from back
    legH = 30;
    translate([0, 0, -legH]) {
        leg(wardrobe, legH, l=2, f=3);  // Front-left
        leg(wardrobe, legH, r=2, f=3);  // Front-right
        leg(wardrobe, legH, l=2, B=2);  // Back-left
        leg(wardrobe, legH, r=2, B=2);  // Back-right
    }
}

// EXPECTED CUT LIST OUTPUT:
// ECHO: "plane (left):   18 × 378(4) × 1164"
// ECHO: "plane (right):  18 × 378(4) × 1164"
// ECHO: "plane (top):    992(4,4,4) × 378 × 18"
// ECHO: "plane (bottom): 992(4,4,4) × 378 × 18"
// ECHO: "plane (front):  487(4,4,4,4) × 18 × 1192(4,4,4,4)"
// ECHO: "plane (front):  487(4,4,4,4) × 18 × 1192(4,4,4,4)"
// ECHO: "plane (back):   1000 × 4 × 1200"
// ECHO: "plane (bottom): 964(4) × 378 × 18"
// ECHO: "plane (bottom): 964(4) × 378 × 18"
// ECHO: "plane (bottom): 964(4) × 378 × 18"

// INTERPRETATION:
// - 2× side panels: 18mm thick, 378×1164mm, one edge band (front)
// - 2× top/bottom: 18mm thick, 992×378mm, three edge bands (front, left, right)
// - 2× door panels: 18mm thick, 487×1192mm, four edge bands (all edges)
// - 1× back panel: 4mm fiberboard, 1000×1200mm, no edge banding
// - 3× shelves: 18mm thick, 964×378mm, one edge band (front)
//
// Total panels: 10 (7× 18mm, 3× 4mm fiberboard for back)
// Total edge banding: 24 edges × 4mm ABS tape
