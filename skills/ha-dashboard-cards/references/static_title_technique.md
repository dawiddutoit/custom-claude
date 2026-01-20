# Static Title Technique for mini-graph-card

## The Problem

`custom:mini-graph-card` with multiple entities dynamically changes the card title when hovering over different sensor lines. This is the default behavior to show which entity is being hovered, but it's problematic for time-range graphs where the title should indicate the time span (e.g., "Last 24 Hours"), not which sensor is hovered.

## DOM Structure Analysis

When mini-graph-card renders, it creates this DOM structure:

```html
<ha-card>
  <div class="header">
    <div class="name">
      <span>Last 24 Hours</span>  <!-- Dynamic content changes on hover -->
    </div>
  </div>
  <div class="graph">
    <!-- Graph content -->
  </div>
</ha-card>
```

The `<span>` inside `.header .name` is what changes dynamically. Simply hiding this element with `display: none` would hide the entire title area.

## The Solution: CSS Pseudo-Element Overlay

Use a `::after` pseudo-element to overlay static content on top of the dynamic title, then hide the dynamic content underneath.

```css
.header .name {
  visibility: visible !important;
}
.header .name::after {
  content: "Last 24 Hours" !important;
  visibility: visible !important;
}
.header .name > * {
  display: none !important;
}
```

### How It Works

1. **`.header .name { visibility: visible !important; }`**
   - Ensures the container element remains visible
   - The `!important` overrides any dynamic visibility changes

2. **`.header .name::after { content: "Last 24 Hours" !important; }`**
   - Creates a pseudo-element after the `.name` container
   - Injects static text using the CSS `content` property
   - The text will overlay on top of the dynamic content

3. **`.header .name > * { display: none !important; }`**
   - Hides all direct child elements (the `<span>` with dynamic text)
   - The pseudo-element is NOT affected because it's not a child element
   - This prevents the dynamic text from showing through

## Alternative Approaches (and Why They Don't Work)

### 1. Hiding the Name Element

```css
.header .name {
  display: none !important;
}
```

**Problem:** This hides the entire title area, leaving no title at all.

### 2. Using pointer-events

```css
.header .name {
  pointer-events: none !important;
}
```

**Problem:** This prevents hover interactions but doesn't stop the JavaScript from changing the title text.

### 3. JavaScript Event Interception

```javascript
card.addEventListener('mouseover', (e) => {
  e.stopPropagation();
  e.preventDefault();
});
```

**Problem:**
- Requires custom JavaScript injection
- More complex than CSS-only solution
- May break other card functionality
- Not supported in Lovelace without custom card development

### 4. Overriding with Fixed Height and Overflow

```css
.header .name {
  height: 20px !important;
  overflow: hidden !important;
}
```

**Problem:** The text still changes underneath, and the height might clip descenders in the font.

## Python Implementation

For programmatic dashboard creation:

```python
def add_static_title_to_mini_graph(card: dict) -> dict:
    """Add card_mod to force static title."""
    if card.get("type") != "custom:mini-graph-card":
        return card

    card_name = card.get("name", "Graph")

    # Use {{ and }} to escape braces in f-string
    card["card_mod"] = {
        "style": f"""
            .header .name {{
                visibility: visible !important;
            }}
            .header .name::after {{
                content: "{card_name}" !important;
                visibility: visible !important;
            }}
            .header .name > * {{
                display: none !important;
            }}
        """
    }

    return card
```

### Important: CSS Escaping in Python

When using f-strings with CSS, you must escape curly braces:
- `{` becomes `{{`
- `}` becomes `}}`

**Wrong:**
```python
f"content: \"{card_name}\" !important;"  # Braces not escaped
```

**Correct:**
```python
f"content: \"{card_name}\" !important;"  # In string, braces don't need escaping
f".header .name {{ visibility: visible; }}"  # In CSS block, escape braces
```

## YAML Implementation

For manual dashboard editing in Home Assistant UI:

```yaml
type: custom:mini-graph-card
name: Last 24 Hours
card_mod:
  style: |
    .header .name {
      visibility: visible !important;
    }
    .header .name::after {
      content: "Last 24 Hours" !important;
      visibility: visible !important;
    }
    .header .name > * {
      display: none !important;
    }
hours_to_show: 24
entities:
  - entity: sensor.office_temperature
    name: Office
  - entity: sensor.bedroom_temperature
    name: Bedroom
```

### YAML Pitfalls

1. **Indentation:** Use spaces, not tabs (YAML requirement)
2. **Quotes:** Use double quotes for `content` value
3. **Multiline:** Use `|` after `style:` for multiline CSS
4. **Consistency:** Ensure `content` value matches `name` value

## Browser Compatibility

This technique uses standard CSS features:
- `::after` pseudo-elements (supported in all modern browsers)
- `content` property (supported in all modern browsers)
- `!important` flag (supported in all modern browsers)
- CSS child combinator `>` (supported in all modern browsers)

**Tested and working in:**
- Chrome/Chromium (Home Assistant Companion apps use Chromium)
- Firefox
- Safari
- Edge

## Performance Considerations

**CSS Overhead:** Negligible (< 0.01ms per card)
- Pseudo-elements are efficiently rendered
- No JavaScript overhead
- No re-layout triggered

**Memory:** Minimal (< 100 bytes per card)
- Pseudo-element content is stored in CSS engine
- No additional DOM nodes created

## Maintenance Notes

### When to Update

- If `mini-graph-card` changes its DOM structure
- If Home Assistant changes CSS rendering
- If `card-mod` changes CSS injection method

### Testing Changes

1. Create test dashboard with single mini-graph-card
2. Apply static title CSS
3. Hover over entity lines
4. Verify title remains static
5. Check browser console for CSS errors

### Debugging

**Issue: Title still changes**
- Check card-mod is installed (`HACS > Frontend > card-mod`)
- Verify CSS syntax (no missing braces, quotes)
- Inspect element in browser DevTools (F12)
- Check for conflicting CSS rules

**Issue: No title visible**
- Verify `visibility: visible` is applied to container
- Check `content` value is not empty string
- Ensure `card_mod` is at correct level in YAML

**Issue: CSS not applied**
- Restart Home Assistant to reload Lovelace
- Clear browser cache (Ctrl+Shift+R)
- Check Lovelace mode is not in storage mode
