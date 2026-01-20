# Font Reference for OpenSCAD

Comprehensive guide to fonts, text parameters, and cross-platform compatibility in OpenSCAD.

## Cross-Platform Fonts (Always Available)

These fonts are bundled with OpenSCAD and work on all platforms:

```openscad
// Liberation family (recommended)
text("Sample", font="Liberation Sans");      // Sans-serif
text("Sample", font="Liberation Mono");      // Monospace
text("Sample", font="Liberation Serif");     // Serif
```

**Font characteristics:**

| Font | Style | Use Case |
|------|-------|----------|
| Liberation Sans | Sans-serif, clean | Labels, part numbers, UI text |
| Liberation Mono | Monospace, fixed-width | Code, dimensions, technical specs |
| Liberation Serif | Serif, traditional | Decorative, traditional designs |

## System Fonts

OpenSCAD can use any installed system font, but availability varies by platform.

**List available fonts:**
```bash
# macOS
fc-list : family | sort | uniq

# Linux
fc-list : family | sort | uniq

# Windows
dir %WINDIR%\Fonts
```

**Common system fonts by platform:**

**macOS:**
- Helvetica, Arial, Courier, Times
- San Francisco (system font)
- Menlo, Monaco (monospace)

**Linux:**
- DejaVu Sans, DejaVu Mono, DejaVu Serif
- Ubuntu, Ubuntu Mono
- Noto Sans, Noto Mono

**Windows:**
- Arial, Calibri, Consolas
- Segoe UI
- Times New Roman, Courier New

**Using system fonts:**
```openscad
// Only works if font is installed
text("Hello", font="Arial");
text("Code", font="Courier New");
text("Modern", font="Segoe UI");
```

**Portability warning:** Projects using system fonts may render differently on other machines.

## Text Parameters

### text() Function Signature

```openscad
text(
    text,                  // String to display
    size=10,               // Font size in units
    font="Liberation Sans", // Font name
    halign="left",         // Horizontal alignment
    valign="baseline",     // Vertical alignment
    spacing=1,             // Character spacing multiplier
    direction="ltr",       // Text direction
    language="en",         // Language hint
    script="latin"         // Script hint
);
```

### Size Parameter

```openscad
// Size in mm (if using mm units)
text("Small", size=5);
text("Medium", size=10);
text("Large", size=20);

// Size relative to object
cube_size = [50, 30, 20];
text("Label", size=cube_size.x / 8);  // 1/8 of width
```

**Guidelines:**
- Part labels: 6-10mm
- Debug annotations: 4-6mm
- Large labels: 12-20mm
- Fine detail: 3-5mm

### Alignment Parameters

#### halign (Horizontal Alignment)

```openscad
// "left" - Default, text starts at origin
text("LEFT", size=10, halign="left");

// "center" - Text centered at origin
text("CENTER", size=10, halign="center");

// "right" - Text ends at origin
text("RIGHT", size=10, halign="right");
```

Visual reference:
```
halign="left":     |Sample Text
halign="center":   Sample |Text
halign="right":    Sample Text|
                   ^ origin
```

#### valign (Vertical Alignment)

```openscad
// "baseline" - Default, text sits on baseline
text("BASELINE", size=10, valign="baseline");

// "center" - Vertical center at origin
text("CENTER", size=10, valign="center");

// "top" - Top of text at origin
text("TOP", size=10, valign="top");

// "bottom" - Bottom of text at origin
text("BOTTOM", size=10, valign="bottom");
```

Visual reference:
```
valign="top":      Sample Text
                   ------------ origin
valign="center":   Sample Text
valign="baseline": Sample Text
                   ------------ origin (baseline)
valign="bottom":   Sample Text
                   ------------ origin
```

**Best practice for labeling:**
```openscad
text("LABEL", size=8, halign="center", valign="center");
```

### Spacing Parameter

```openscad
// Default spacing
text("NORMAL", size=10, spacing=1);

// Tight spacing (80%)
text("TIGHT", size=10, spacing=0.8);

// Loose spacing (120%)
text("LOOSE", size=10, spacing=1.2);

// Very loose (150%)
text("SPACED", size=10, spacing=1.5);
```

**Use cases:**
- `spacing=0.8` - Compact labels on small parts
- `spacing=1.0` - Normal (default)
- `spacing=1.2` - Easier readability for engraved text

### Direction Parameter

```openscad
// Left-to-right (default, English)
text("Hello", direction="ltr");

// Right-to-left (Arabic, Hebrew)
text("مرحبا", direction="rtl");

// Top-to-bottom (vertical Chinese/Japanese)
text("日本", direction="ttb");

// Bottom-to-top (vertical upward)
text("Text", direction="btt");
```

**Note:** Requires appropriate font with script support.

### Language and Script Parameters

```openscad
// English (default)
text("Hello", language="en", script="latin");

// Arabic
text("مرحبا", language="ar", script="arabic");

// Chinese
text("你好", language="zh", script="hans");

// Japanese
text("こんにちは", language="ja", script="hiragana");
```

**Common scripts:**
- `latin` - Western languages
- `arabic` - Arabic script
- `hans` - Simplified Chinese
- `hant` - Traditional Chinese
- `hiragana`, `katakana` - Japanese
- `cyrillic` - Russian, Ukrainian, etc.

## Practical Examples

### Centered Label on Face

```openscad
include <BOSL2/std.scad>

cuboid([50, 30, 20])
    attach(TOP, BOT)
        linear_extrude(2)
            text(
                "PART-001",
                size=6,
                font="Liberation Sans",
                halign="center",
                valign="center"
            );
```

### Multi-line Text

```openscad
include <BOSL2/std.scad>

module multiline_label(lines, size, line_height) {
    for (i = [0:len(lines)-1]) {
        down(i * line_height)
            text(lines[i], size=size, halign="center", valign="center");
    }
}

cuboid([60, 40, 20])
    attach(TOP, BOT)
        linear_extrude(1)
            multiline_label(["PART", "001"], size=8, line_height=10);
```

### Dimension Annotation

```openscad
module dimension_text(length) {
    color("red")
        linear_extrude(0.5)
            text(
                str(length, "mm"),
                size=4,
                font="Liberation Mono",
                halign="center",
                valign="center"
            );
}
```

### Engraved Serial Number

```openscad
include <BOSL2/std.scad>

module serial_number(sn) {
    diff()
    cuboid([40, 15, 2], rounding=1, edges="Z")
        attach(TOP, BOT, inside=true)
            tag("remove")
            linear_extrude(0.3)
                text(
                    str("SN:", sn),
                    size=4,
                    font="Liberation Mono",
                    halign="center",
                    valign="center"
                );
}

serial_number("001234");
```

## Font Selection Guidelines

### Use Liberation Sans when:
- ✅ General labeling
- ✅ Part numbers
- ✅ UI/interface text
- ✅ Clean, modern look

### Use Liberation Mono when:
- ✅ Serial numbers
- ✅ Dimensions
- ✅ Code/technical specs
- ✅ Fixed-width alignment needed

### Use Liberation Serif when:
- ✅ Decorative designs
- ✅ Traditional aesthetics
- ✅ Formal/classical look

### Use system fonts when:
- ⚠️ You control the build environment
- ⚠️ Specific branding required
- ⚠️ Acceptable for renders to fail on other machines

## Text Rendering Performance

**Optimization for preview mode:**

```openscad
$fn = $preview ? 16 : 64;

text("LABEL", size=10);
```

**Impact on render time:**

| Text Size | Preview $fn | Render $fn | Relative Speed |
|-----------|-------------|------------|----------------|
| 10mm | 16 | 64 | 1x (baseline) |
| 10mm | 32 | 64 | 2x slower |
| 10mm | 16 | 128 | 4x slower |

**Recommendation:** Use `$fn=16` for preview, `$fn=64` for final render.

## Common Issues and Solutions

### Issue: Text not visible

**Causes:**
- Text size too small
- Wrong face attachment
- Color matches background

**Solutions:**
```openscad
// Make text larger
text("LABEL", size=10);  // was: size=1

// Check face orientation
attach(TOP, BOT)  // was: attach(TOP, TOP)

// Add color
color("red") text("LABEL");
```

### Issue: Text backwards or upside down

**Cause:** Wrong attachment point or manual rotation

**Solution:** Use BOSL2 attach (handles orientation automatically)
```openscad
// ✅ CORRECT
attach(TOP, BOT) text("LABEL");

// ❌ WRONG (manual positioning)
translate(...) rotate(...) text("LABEL");
```

### Issue: Text not centered

**Cause:** Missing halign/valign parameters

**Solution:**
```openscad
// ✅ CORRECT
text("LABEL", halign="center", valign="center");

// ❌ WRONG (default is bottom-left)
text("LABEL");
```

### Issue: Font not found

**Cause:** System font not installed

**Solution:** Use Liberation fonts (always available)
```openscad
// ✅ CORRECT (cross-platform)
text("LABEL", font="Liberation Sans");

// ❌ RISKY (may not exist)
text("LABEL", font="Arial");
```

## Font Metrics (Advanced)

OpenSCAD does not provide direct font metric queries in 2021.01 (fixed in 2025+ with `textmetrics()`).

**Approximation method:**

```openscad
// Approximate text width (rough)
function text_width(str, size) =
    len(str) * size * 0.6;  // ~60% of size

// Approximate text height
function text_height(size) = size;

// Example usage
label = "PART-001";
size = 8;
width = text_width(label, size);

echo("Estimated width:", width);
```

**Better approach:** Use attachable_text3d for accurate metrics.

```openscad
include <BOSL2/std.scad>
use <openscad_attachable_text3d/attachable_text3d.scad>

// Provides accurate bounding box
attachable_text3d("LABEL", size=10, h=2);
```

## Resources

**Check installed fonts:**
```bash
# Run script from skill
~/.claude/skills/openscad-labeling/scripts/list-system-fonts.sh
```

**Test font rendering:**
```openscad
// Create font test sheet
for (i = [0:2]) {
    fonts = ["Liberation Sans", "Liberation Mono", "Liberation Serif"];
    translate([0, -i*15, 0])
        text(fonts[i], size=8, font=fonts[i]);
}
```

**OpenSCAD font documentation:**
https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Text
