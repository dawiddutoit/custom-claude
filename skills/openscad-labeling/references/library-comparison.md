# Text Labeling Library Comparison

Detailed comparison of OpenSCAD text labeling libraries.

## Feature Matrix

| Library | Flat Surfaces | Curved Surfaces | BOSL2 Compatible | Font Metrics | Installation |
|---------|---------------|-----------------|------------------|--------------|--------------|
| **BOSL2 + text()** | ✅ | ❌ | ✅ | ❌ | Pre-installed |
| **text_on_OpenSCAD** | ✅ | ✅ | ❌ | ❌ | Manual git clone |
| **attachable_text3d** | ✅ | ❌ | ✅ | ✅ | Manual git clone |
| **Write.scad** | ✅ | ✅ | ❌ | ❌ | Manual install |

## BOSL2 + text() (Recommended for Flat Surfaces)

**Repository:** Part of BOSL2 standard library
**Installation:** Already included with BOSL2

**Best for:**
- Flat surface labeling with precise positioning
- Projects already using BOSL2
- Tight integration with BOSL2's attach/diff system

**Strengths:**
- Semantic face positioning (TOP, BOTTOM, etc.)
- No manual coordinate calculations
- Works seamlessly with diff() for engraved text
- Zero additional dependencies

**Limitations:**
- Curved surfaces require manual projection
- No automatic text bounding box calculations
- Font metrics must be estimated

**Example:**
```openscad
include <BOSL2/std.scad>

diff()
cuboid([50, 30, 20])
    attach(TOP, BOT, inside=true)
        tag("remove")
        linear_extrude(1)
            text("PART-001", size=6, halign="center", valign="center");
```

## text_on_OpenSCAD (Best for Curved Surfaces)

**Repository:** https://github.com/brodykenrick/text_on_OpenSCAD
**Installation:** `git clone` into OpenSCAD libraries directory

**Best for:**
- Cylinders, spheres, and curved surfaces
- Internationalization (RTL, vertical text)
- Projects needing multiple language support

**Strengths:**
- Wraps text naturally around curves
- Support for RTL, TTB, BTT text direction
- Handles non-Latin scripts (Arabic, Chinese, Japanese)
- Dedicated functions per surface type

**Limitations:**
- Not BOSL2-aware (manual positioning needed)
- No attach() integration
- Steeper learning curve

**Example:**
```openscad
use <text_on_OpenSCAD/text_on.scad>

// Text wrapped around cylinder
text_on_cylinder(
    "LABEL-TEXT",
    r=15,
    h=30,
    size=4,
    font="Liberation Sans",
    direction="ltr"
);

// Text on sphere hemisphere
text_on_sphere(
    "GLOBE",
    r=20,
    size=5,
    font="Liberation Mono"
);
```

**Parameters:**
- `direction` - "ltr", "rtl", "ttb", "btt"
- `language` - "en", "cn", "jp", "ar"
- `script` - "latin", "arabic", "hiragana", "katakana"

## attachable_text3d (Best BOSL2 Integration)

**Repository:** https://github.com/jon-gilbert/openscad_attachable_text3d
**Installation:** `git clone` into OpenSCAD libraries directory
**Requires:** BOSL2

**Best for:**
- BOSL2 projects needing accurate text bounds
- When text size must be precisely measured
- Complex assemblies with text positioning

**Strengths:**
- Full BOSL2 attachable integration
- Accurate font metrics and bounding boxes
- Works with attach(), diff(), etc.
- Better alignment than raw text()

**Limitations:**
- Requires BOSL2 (not standalone)
- Flat surfaces only
- Extra dependency to install

**Example:**
```openscad
include <BOSL2/std.scad>
use <openscad_attachable_text3d/attachable_text3d.scad>

cuboid([50, 30, 20])
    attach(TOP)
        attachable_text3d(
            "LABEL",
            size=10,
            h=2,
            font="Liberation Sans"
        );
```

**Benefits over BOSL2 + text():**
- Proper bounding box for anchor calculations
- More accurate centering
- Better multi-line text handling

## Write.scad (Classic Fallback)

**Source:** Legacy library (multiple forks)
**Installation:** Manual download (not always available)

**Best for:**
- Legacy projects
- When no other curved text options available
- Simple curved text needs

**Strengths:**
- Simple API
- Dedicated functions per surface
- Long history (well-tested)

**Limitations:**
- Not maintained actively
- Multiple incompatible forks exist
- No BOSL2 integration
- Installation path varies

**Example:**
```openscad
use <Write.scad>

writecube("FRONT", [50, 30, 20], face="front", t=2, h=8);
writesphere("GLOBE", 25, t=2, h=6);
writecylinder("LABEL", r=15, h=30, t=2);
```

**Note:** Availability varies by OpenSCAD distribution.

## Decision Matrix

**Use BOSL2 + text() when:**
- ✅ Labeling flat faces
- ✅ Already using BOSL2
- ✅ Need tight integration with diff/attach
- ✅ Want zero extra dependencies

**Use text_on_OpenSCAD when:**
- ✅ Labeling cylinders or spheres
- ✅ Need RTL or vertical text
- ✅ Working with non-Latin scripts
- ✅ Wrapping text around curves

**Use attachable_text3d when:**
- ✅ Using BOSL2
- ✅ Need accurate font metrics
- ✅ Precise text positioning critical
- ✅ Can install extra library

**Use Write.scad when:**
- ✅ Legacy project compatibility
- ✅ Simple curved text needs
- ✅ Other options unavailable

## Installation Quick Reference

```bash
# macOS
cd ~/Documents/OpenSCAD/libraries
# Linux
cd ~/.local/share/OpenSCAD/libraries

# text_on_OpenSCAD
git clone https://github.com/brodykenrick/text_on_OpenSCAD.git

# attachable_text3d (requires BOSL2)
git clone https://github.com/jon-gilbert/openscad_attachable_text3d.git

# Verify installations
ls -la
```

## Performance Considerations

**Rendering speed (fastest to slowest):**
1. BOSL2 + text() - Native OpenSCAD
2. attachable_text3d - Thin wrapper
3. text_on_OpenSCAD - Complex projection
4. Write.scad - Legacy approach

**Preview mode optimization:**
```openscad
$fn = $preview ? 16 : 64;  // Fewer segments in preview
```

## Compatibility Notes

**OpenSCAD versions:**
- BOSL2 + text() - Requires OpenSCAD 2021.01+
- text_on_OpenSCAD - Works with OpenSCAD 2019.05+
- attachable_text3d - Requires BOSL2 (2021.01+)
- Write.scad - Works with OpenSCAD 2015+

**Platform support:**
All libraries work on macOS, Linux, Windows.

**Font availability:**
Cross-platform fonts (always available):
- Liberation Sans
- Liberation Mono
- Liberation Serif
