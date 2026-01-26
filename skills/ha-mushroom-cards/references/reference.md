# Mushroom Cards Reference

## Table of Contents

1. [Best Practices](#best-practices)
2. [Troubleshooting](#troubleshooting)
3. [Card-Mod Advanced Styling](#card-mod-advanced-styling)
4. [Official Documentation](#official-documentation)

## Best Practices

### 1. Use Collapsible Controls

```yaml
type: custom:mushroom-climate-card
entity: climate.living_room
collapsible_controls: true  # Hides controls until tapped (mobile-friendly)
```

### 2. Combine with Chips for Status

```yaml
# Put chips at top of view for quick status
- type: custom:mushroom-chips-card
  chips:
    - type: weather
    - type: template (lights count)
    - type: template (windows open)
```

### 3. Use Title Cards for Sections

```yaml
- type: custom:mushroom-title-card
  title: Section Name

- type: grid
  columns: 2
  cards: [...]
```

### 4. Enable use_light_color

```yaml
type: custom:mushroom-light-card
entity: light.bedroom
use_light_color: true  # Shows actual light color
```

### 5. Template for Dynamic Content

```yaml
# Use template cards for counts, calculations, conditional text
type: custom:mushroom-template-card
primary: "{{ states('sensor.lights_on') }} Lights"
```

## Troubleshooting

### Card Not Loading

**Symptoms:**
- Card shows error or blank space
- "Custom element doesn't exist: mushroom-*-card"

**Solutions:**
- Verify HACS installation (Frontend category)
- Clear browser cache (Ctrl+Shift+R)
- Check Lovelace resources (Settings → Dashboards → Resources)
- Restart Home Assistant after installation

### Icons Not Showing

**Symptoms:**
- Icon placeholder or broken icon displayed

**Solutions:**
- Use valid MDI icon names (`mdi:icon-name`)
- Check icon name at [https://pictogrammers.com/library/mdi/](https://pictogrammers.com/library/mdi/)
- Ensure icon name is lowercase with hyphens

### Card-Mod Not Working

**Symptoms:**
- Styles not applied
- Card appearance unchanged

**Solutions:**
- Ensure card-mod is installed as a Frontend module (HACS)
- Verify CSS syntax using browser DevTools (F12)
- Check for conflicting card-mod styles
- Clear browser cache

### Templates Not Updating

**Symptoms:**
- Template shows old value
- Template shows "unknown" or error

**Solutions:**
- Verify Jinja2 syntax
- Test templates in Developer Tools → Template
- Check entity_id exists in HA
- Ensure entity updates are being recorded

## Card-Mod Advanced Styling

### Grid Spanning

Make cards take multiple columns or rows:

```yaml
type: custom:mushroom-entity-card
entity: sensor.temperature
card_mod:
  style:
    .: |
      :host {
        grid-column: span 2;  # Take 2 columns
        grid-row: span 1;     # Take 1 row
      }
```

### Animated Cards

Add animations for attention or visual interest:

```yaml
type: custom:mushroom-chips-card
chips:
  - type: template
    icon: mdi:lightbulb
    content: "{{ states('sensor.lights_on') }}"
card_mod:
  style: |
    ha-card {
      animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
```

### Conditional Color Based on State

```yaml
type: custom:mushroom-entity-card
entity: sensor.temperature
card_mod:
  style: |
    :host {
      {% if states('sensor.temperature') | float > 25 %}
        --card-mod-icon-color: red;
      {% elif states('sensor.temperature') | float < 18 %}
        --card-mod-icon-color: blue;
      {% else %}
        --card-mod-icon-color: green;
      {% endif %}
    }
```

### Shadow and Depth Effects

```yaml
type: custom:mushroom-entity-card
entity: sensor.temperature
card_mod:
  style: |
    ha-card {
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
      transform: translateZ(0);
      transition: transform 0.2s;
    }
    ha-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
```

## Official Documentation

- [Mushroom Cards GitHub](https://github.com/piitaya/lovelace-mushroom)
- [Card-Mod GitHub](https://github.com/thomasloven/lovelace-card-mod)
- [Mushroom Styling Guide (Community)](https://community.home-assistant.io/t/mushroom-cards-card-mod-styling-config-guide/600472)
- [Material Design Icons](https://pictogrammers.com/library/mdi/)
