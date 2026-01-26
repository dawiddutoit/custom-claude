# Custom Button Card Templates Reference

## Template Basics

Custom button card supports JavaScript templates using `[[[ ]]]` syntax for dynamic content.

## State-Based Icon Template

```yaml
type: custom:button-card
entity: light.living_room
icon: |
  [[[
    if (entity.state === 'on') return 'mdi:lightbulb-on';
    return 'mdi:lightbulb-off';
  ]]]
```

## State-Based Color Template

```yaml
type: custom:button-card
entity: sensor.temperature
color: |
  [[[
    if (entity.state > 25) return 'red';
    if (entity.state > 20) return 'orange';
    return 'blue';
  ]]]
```

## Dynamic Name Template

```yaml
type: custom:button-card
entity: light.living_room
name: |
  [[[
    if (entity.state === 'on')
      return 'Living Room (On)';
    return 'Living Room (Off)';
  ]]]
```

## Multi-Entity Template

```yaml
type: custom:button-card
entity: light.living_room
label: |
  [[[
    const bedroom = states['light.bedroom'].state;
    const kitchen = states['light.kitchen'].state;
    const on = [bedroom, kitchen].filter(s => s === 'on').length;
    return `${on} lights on`;
  ]]]
```

## Conditional Styles

```yaml
type: custom:button-card
entity: light.living_room
styles:
  card:
    - background: |
        [[[
          if (entity.state === 'on') return 'rgba(255, 200, 0, 0.3)';
          return 'rgba(0, 0, 0, 0.1)';
        ]]]
  name:
    - font-weight: |
        [[[
          if (entity.state === 'on') return 'bold';
          return 'normal';
        ]]]
```

## Reusable Templates

Define templates in dashboard configuration:

```yaml
button_card_templates:
  light_button:
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    styles:
      card:
        - background: |
            [[[
              if (entity.state === 'on') return 'rgba(255, 200, 0, 0.3)';
              return 'rgba(0, 0, 0, 0.1)';
            ]]]

# Use template
type: custom:button-card
entity: light.living_room
template: light_button
```

## Advanced Template Example

```yaml
type: custom:button-card
entity: light.living_room
name: |
  [[[
    const brightness = entity.attributes.brightness || 0;
    const pct = Math.round(brightness / 2.55);
    return `Living Room ${pct}%`;
  ]]]
icon: |
  [[[
    const brightness = entity.attributes.brightness || 0;
    if (brightness > 200) return 'mdi:lightbulb';
    if (brightness > 100) return 'mdi:lightbulb-on-outline';
    if (brightness > 0) return 'mdi:lightbulb-outline';
    return 'mdi:lightbulb-off';
  ]]]
styles:
  icon:
    - color: |
        [[[
          if (entity.state === 'off') return 'gray';
          const brightness = entity.attributes.brightness || 0;
          const pct = brightness / 2.55;
          return `rgba(255, ${255 - pct}, 0, 1)`;
        ]]]
```
