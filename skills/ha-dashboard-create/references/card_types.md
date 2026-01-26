# Home Assistant Card Types Reference

## Table of Contents

1. Display Cards
2. Control Cards
3. Layout Cards
4. Media Cards
5. Custom Cards (HACS)
6. Card Configuration Patterns

## 1. Display Cards

### Entities Card

Display multiple entities in a list.

```yaml
type: entities
title: Living Room
entities:
  - light.living_room
  - switch.fan
  - sensor.temperature
  - entity: climate.living_room
    name: Thermostat
```

**Options:**
- `title` - Card title
- `show_header_toggle` - Show toggle all button
- `state_color` - Color entities based on state

### Entity Card

Display single entity with large format.

```yaml
type: entity
entity: light.bedroom
name: Bedroom Light
icon: mdi:lightbulb
```

### Sensor Card

Display sensor value with graph.

```yaml
type: sensor
entity: sensor.temperature
name: Temperature
graph: line
detail: 2
hours_to_show: 24
```

### Gauge Card

Display value as gauge/dial.

```yaml
type: gauge
entity: sensor.temperature
name: Temperature
min: 0
max: 50
severity:
  green: 18
  yellow: 26
  red: 35
needle: true
```

### Markdown Card

Display formatted text.

```yaml
type: markdown
content: |
  # Welcome
  Current time: {{ now().strftime("%H:%M") }}
  Temperature: {{ states('sensor.temperature') }}°C
```

**Supports:**
- Markdown formatting
- Templates ({{ }})
- HTML (limited)

## 2. Control Cards

### Button Card

Single button for entity control.

```yaml
type: button
entity: light.living_room
name: Living Room
icon: mdi:lightbulb
tap_action:
  action: toggle
hold_action:
  action: more-info
```

**Actions:**
- `toggle` - Toggle entity
- `more-info` - Show more info dialog
- `navigate` - Navigate to path
- `call-service` - Call service
- `url` - Open URL

### Thermostat Card

Climate control interface.

```yaml
type: thermostat
entity: climate.living_room
name: Living Room AC
```

**Features:**
- Temperature control
- Mode selection (heat/cool/auto)
- Fan control

### Alarm Panel Card

Alarm control panel.

```yaml
type: alarm-panel
entity: alarm_control_panel.home
states:
  - armed_home
  - armed_away
  - armed_night
```

### Light Card

Light control with brightness slider.

```yaml
type: light
entity: light.bedroom
name: Bedroom Light
```

## 3. Layout Cards

### Horizontal Stack

Arrange cards side by side.

```yaml
type: horizontal-stack
cards:
  - type: entity
    entity: sensor.temperature
  - type: entity
    entity: sensor.humidity
```

**Use when:** 2-3 cards side by side (more gets cramped on mobile)

### Vertical Stack

Stack cards vertically.

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: sensor.temperature
  - type: entity
    entity: sensor.humidity
  - type: entity
    entity: sensor.pressure
```

**Use when:** Organizing related cards in a column

### Grid Card

Multi-column responsive grid.

```yaml
type: grid
columns: 3
square: false
cards:
  - type: button
    entity: light.office
  - type: button
    entity: light.bedroom
  - type: button
    entity: light.living_room
```

**Options:**
- `columns` - Number of columns (auto-stacks on mobile)
- `square` - Force equal width/height

### Conditional Card

Show card based on conditions.

```yaml
type: conditional
conditions:
  - condition: state
    entity: person.john
    state: home
card:
  type: entities
  entities:
    - light.bedroom
```

## 4. Media Cards

### Picture Card

Display image with optional tap action.

```yaml
type: picture
image: /local/image.jpg
tap_action:
  action: navigate
  navigation_path: /lovelace/cameras
```

### Picture Entity Card

Image with entity state overlay.

```yaml
type: picture-entity
entity: light.living_room
image: /local/living_room.jpg
show_name: true
show_state: true
```

### Picture Glance Card

Image with multiple entity badges.

```yaml
type: picture-glance
title: Living Room
image: /local/living_room.jpg
entities:
  - light.living_room
  - binary_sensor.motion_living_room
  - sensor.temperature_living_room
```

### Camera Card

Live camera feed.

```yaml
type: picture-entity
entity: camera.front_door
camera_view: live
```

### Map Card

Map with device trackers.

```yaml
type: map
entities:
  - person.john
  - person.jane
  - device_tracker.phone
default_zoom: 12
```

## 5. Custom Cards (HACS)

### ApexCharts Card

Advanced time-series graphs.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: 24 Hour History
graph_span: 24h
span:
  end: hour
series:
  - entity: sensor.temperature
    name: Temperature
    stroke_width: 2
```

### Mini Graph Card

Compact sparkline graphs.

```yaml
type: custom:mini-graph-card
entity: sensor.temperature
name: Temperature
hours_to_show: 24
line_color: blue
line_width: 2
```

### Mushroom Cards

Modern entity cards with icons.

```yaml
type: custom:mushroom-entity-card
entity: light.living_room
name: Living Room
icon: mdi:lightbulb
```

**Mushroom Types:**
- `mushroom-entity-card` - Basic entity
- `mushroom-light-card` - Light with brightness
- `mushroom-climate-card` - Climate control
- `mushroom-chips-card` - Compact horizontal chips
- `mushroom-template-card` - Custom template card

### Bubble Card

Section separators and buttons.

```yaml
type: custom:bubble-card
card_type: separator
name: Section Name
icon: mdi:home
```

### Modern Circular Gauge

Beautiful circular gauges.

```yaml
type: custom:modern-circular-gauge
entity: sensor.temperature
name: Temperature
min: 0
max: 50
needle: true
segments:
  - from: 0
    color: "#3498db"
  - from: 18
    color: "#2ecc71"
  - from: 26
    color: "#f1c40f"
  - from: 35
    color: "#e74c3c"
```

## 6. Card Configuration Patterns

### Card with Visibility

```yaml
type: entities
entities:
  - light.bedroom
visibility:
  - condition: state
    entity: person.john
    state: home
```

### Card with card_mod (Custom CSS)

```yaml
type: entities
entities:
  - light.bedroom
card_mod:
  style: |
    ha-card {
      background: rgba(0,0,0,0.3);
      border-radius: 15px;
    }
```

### Card with Tap/Hold Actions

```yaml
type: button
entity: light.living_room
tap_action:
  action: toggle
hold_action:
  action: more-info
double_tap_action:
  action: navigate
  navigation_path: /lovelace/lights
```

### Entity Row with Custom Name/Icon

```yaml
type: entities
entities:
  - entity: sensor.temperature
    name: Office Temperature
    icon: mdi:thermometer
    secondary_info: last-changed
```

## Common Entity Patterns

### Climate Devices

```yaml
entities:
  - climate.living_room
  - climate.bedroom
  - climate.office
```

### Sensors

```yaml
entities:
  - sensor.temperature
  - sensor.humidity
  - sensor.pressure
  - sensor.air_quality
```

### Lights

```yaml
entities:
  - light.living_room
  - light.bedroom
  - light.kitchen
  - light.office
```

### Switches

```yaml
entities:
  - switch.fan
  - switch.heater
  - switch.humidifier
```

### Binary Sensors

```yaml
entities:
  - binary_sensor.motion_living_room
  - binary_sensor.door_front
  - binary_sensor.window_bedroom
```

## Card Best Practices

1. **Use appropriate card types**: Gauge for single values, entities for lists, grid for buttons
2. **Limit horizontal-stack**: Max 2-3 cards for mobile compatibility
3. **Use grid for responsive layouts**: Automatically stacks on mobile
4. **Test on mobile devices**: Browser resize doesn't match mobile behavior
5. **Validate entities exist**: Check Developer Tools → States before creating cards
6. **Use consistent naming**: Match card titles to room/function names
7. **Group related cards**: Use vertical-stack or sections to organize
8. **Add context with markdown**: Explain complex sensors or controls

## Troubleshooting

### Card Not Displaying

- Check entity exists (Developer Tools → States)
- Verify YAML syntax (quotes, indentation)
- Check browser console (F12) for errors
- Ensure custom card installed (if using HACS cards)

### Card Shows Error

- Check entity ID spelling
- Verify entity has valid state (not "unknown" or "unavailable")
- Check for unsupported options (some cards don't support all features)
- Review Home Assistant logs (Settings → System → Logs)

### Custom Card Not Loading

- Install via HACS (HACS → Frontend)
- Restart Home Assistant after installation
- Clear browser cache (Ctrl+Shift+R)
- Check card compatibility with HA version
