// Engraved vs Embossed text comparison examples
// Demonstrates difference between raised and cut text

include <BOSL2/std.scad>

// Select which example to render
//example = "engraved";
//example = "embossed";
//example = "comparison";
example = "all_techniques";

// ============================================
// Engraved Text (Debossed, Cut Into Surface)
// ============================================
module engraved_text(label_text, base_size=[60, 40, 10]) {
    diff()
    cuboid(base_size, rounding=2, edges="Z")
        attach(TOP, BOT, inside=true)
            tag("remove")
            linear_extrude(1)  // Depth of cut
                text(
                    label_text,
                    size=base_size.x/8,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Embossed Text (Raised Above Surface)
// ============================================
module embossed_text(label_text, base_size=[60, 40, 10]) {
    cuboid(base_size, rounding=2, edges="Z")
        attach(TOP, BOT)
            linear_extrude(1.5)  // Height of raised text
                text(
                    label_text,
                    size=base_size.x/8,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Shallow Engraving (Fine Detail)
// ============================================
module shallow_engraved(label_text, base_size=[60, 40, 10]) {
    diff()
    cuboid(base_size, rounding=2, edges="Z")
        attach(TOP, BOT, inside=true)
            tag("remove")
            linear_extrude(0.3)  // Very shallow (0.3mm)
                text(
                    label_text,
                    size=base_size.x/10,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Deep Engraving (Bold Look)
// ============================================
module deep_engraved(label_text, base_size=[60, 40, 10]) {
    diff()
    cuboid(base_size, rounding=2, edges="Z")
        attach(TOP, BOT, inside=true)
            tag("remove")
            linear_extrude(2)  // Deep cut (2mm)
                text(
                    label_text,
                    size=base_size.x/8,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Side Engraving (Edge Labeling)
// ============================================
module side_engraved(label_text, base_size=[60, 40, 10]) {
    diff()
    cuboid(base_size, rounding=2, edges="Z")
        attach(FRONT, BACK, inside=true)
            tag("remove")
            linear_extrude(0.5)
                text(
                    label_text,
                    size=base_size.z/3,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
}

// ============================================
// Multi-Face Engraving
// ============================================
module multi_face_engraved(labels, base_size=[50, 40, 30]) {
    faces = [TOP, FRONT, LEFT];
    label_texts = [labels[0], labels[1], labels[2]];

    diff()
    cuboid(base_size, rounding=2, edges="Z")
        for (i = [0:2])
            if (label_texts[i] != "")
                attach(faces[i], BOT, inside=true)
                    tag("remove")
                    linear_extrude(0.8)
                        text(
                            label_texts[i],
                            size=base_size.x/12,
                            font="Liberation Sans",
                            halign="center",
                            valign="center"
                        );
}

// ============================================
// Embossed with Shadow (3D Effect)
// ============================================
module embossed_with_shadow(label_text, base_size=[60, 40, 10]) {
    cuboid(base_size, rounding=2, edges="Z") {
        // Main raised text
        attach(TOP, BOT)
            color("white")
            linear_extrude(1.5)
                text(
                    label_text,
                    size=base_size.x/8,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );

        // Shadow (slightly offset, darker)
        attach(TOP, BOT)
            translate([0.5, -0.5, -0.2])
            color("gray")
            linear_extrude(1.3)
                text(
                    label_text,
                    size=base_size.x/8,
                    font="Liberation Sans",
                    halign="center",
                    valign="center"
                );
    }
}

// ============================================
// Comparison Example (Side by Side)
// ============================================
module engraved_vs_embossed(label_text) {
    // Engraved on left
    left(35) {
        engraved_text(label_text);
        down(20)
            color("red")
            linear_extrude(0.5)
                text("ENGRAVED", size=4, halign="center");
    }

    // Embossed on right
    right(35) {
        embossed_text(label_text);
        down(20)
            color("red")
            linear_extrude(0.5)
                text("EMBOSSED", size=4, halign="center");
    }
}

// ============================================
// Render Selected Example
// ============================================

if (example == "engraved") {
    engraved_text("ENGRAVED");
}
else if (example == "embossed") {
    embossed_text("RAISED");
}
else if (example == "comparison") {
    engraved_vs_embossed("LABEL");
}
else if (example == "all_techniques") {
    // Display all techniques in a grid

    // Row 1: Basic engraved vs embossed
    back(0) left(40) engraved_text("CUT", [50, 30, 8]);
    back(0) right(40) embossed_text("RAISED", [50, 30, 8]);

    // Row 2: Depth variations
    back(50) left(60) shallow_engraved("SHALLOW", [50, 30, 8]);
    back(50) left(0) engraved_text("MEDIUM", [50, 30, 8]);
    back(50) right(60) deep_engraved("DEEP", [50, 30, 8]);

    // Row 3: Advanced techniques
    back(100) left(40) side_engraved("SIDE", [50, 30, 8]);
    back(100) right(40) multi_face_engraved(["TOP", "FRONT", "LEFT"], [40, 30, 25]);
}

// ============================================
// Guidelines
// ============================================

// Engraved (Debossed) Text:
// ✓ Better for paint-filled labels
// ✓ Protected from surface wear
// ✓ Gives professional look
// ✗ Harder to read at small sizes
// ✗ Can weaken thin parts if too deep
//
// Recommended depths:
// - Fine detail: 0.3-0.5mm
// - Standard: 0.8-1.0mm
// - Bold: 1.5-2.0mm

// Embossed (Raised) Text:
// ✓ Easier to read
// ✓ Tactile (can feel with fingers)
// ✓ No material removal
// ✗ Can break off on impact
// ✗ Harder to clean around letters
//
// Recommended heights:
// - Low profile: 0.5-1.0mm
// - Standard: 1.5-2.0mm
// - High relief: 2.5-3.0mm

// Usage tips:
// 1. Use engraved for parts that will be handled (won't break off)
// 2. Use embossed for display labels (more visible)
// 3. Scale text size to 1/8 to 1/10 of surface width
// 4. Test print small samples to verify readability
// 5. Consider paint-filling engraved text for contrast
