# Sections View (HA 2024+)

Modern drag-and-drop dashboard layout system introduced in Home Assistant 2024.3.

## Overview

Sections View uses a Z-Grid layout with drag-and-drop editing and automatic mobile responsiveness.

```yaml
views:
  - title: Home
    type: sections  # Default in HA 2024.3+
    sections:
      - title: Climate
        type: grid
        cards:
          - type: thermostat
            entity: climate.living_room
          - type: sensor
            entity: sensor.temperature
```

## Key Features

1. **Drag-and-drop positioning** - Reorder cards and sections in UI
2. **Z-Grid layout** - Sections flow left-to-right, wrap to new rows
3. **Automatic mobile reflow** - Columns adjust based on screen width
4. **Width adjustment** - UI slider controls card width (no YAML)

## Z-Grid Behavior

- Sections flow left-to-right
- Wrap to new row when current row is full
- Row height = tallest section in that row
- Column widths remain constant

## Mobile Responsiveness

- Automatic column reflow based on screen width
- Test on mobile during editing (card behavior differs from desktop)
- Keep frequently-used controls in top-left (first to load)

## Example: Multi-Section Dashboard

```yaml
views:
  - title: Home
    type: sections
    sections:
      # Section 1: Status
      - type: grid
        cards:
          - type: custom:mushroom-chips-card
            chips:
              - type: weather
                entity: weather.home
              - type: template
                icon: mdi:lightbulb
                content: "{{ states('sensor.lights_on') }}"

      # Section 2: Climate
      - title: Climate
        type: grid
        columns: 2
        cards:
          - type: thermostat
            entity: climate.living_room
          - type: sensor
            entity: sensor.temperature

      # Section 3: Quick Actions
      - title: Quick Actions
        type: grid
        columns: 2
        cards:
          - type: button
            entity: light.all_lights
            name: All Lights
          - type: button
            name: Good Night
            tap_action:
              action: perform-action
              perform_action: script.good_night
```

## When to Use

- **Use Sections View when:**
  - Building new dashboards (recommended default)
  - Want drag-and-drop editing
  - Need automatic mobile responsiveness
  - Prefer visual layout adjustments over YAML

- **Use traditional layouts when:**
  - Need programmatic control (dashboard_builder.py scripts)
  - Require precise CSS Grid control
  - Working with existing dashboards
  - Need complex nested structures

## Official Documentation

- [Sections View - Home Assistant](https://www.home-assistant.io/dashboards/sections/)
