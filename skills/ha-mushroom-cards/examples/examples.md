# Mushroom Cards Examples

Real-world dashboard examples using Mushroom cards.

## Climate Control Panel

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Climate
    subtitle: All AC units

  - type: grid
    columns: 2
    cards:
      - type: custom:mushroom-climate-card
        entity: climate.snorlug
        show_temperature_control: true
        collapsible_controls: true

      - type: custom:mushroom-climate-card
        entity: climate.mines_of_moria
        show_temperature_control: true
        collapsible_controls: true
```

## Status Chips Bar

Full status bar with weather, lights, windows, and temperature.

## Best Practices

### 1. Use Collapsible Controls

Mobile-friendly pattern that hides controls until user interaction.

### 2. Combine with Chips for Status

Quick status indicators at top of view.

### 3. Use Title Cards for Sections

Clear visual organization with headers.

### 4. Enable use_light_color

Shows actual light color for better visual feedback.

### 5. Template for Dynamic Content

Use template cards for counts, calculations, conditional text.
