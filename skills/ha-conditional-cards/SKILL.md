---
name: ha-conditional-cards
description: "Configure conditional visibility for Home Assistant dashboard cards based on entity states, numeric values, screen size, users, time, and complex logic (and/or). Use when hiding/showing cards dynamically, creating responsive layouts, implementing user-specific views, or building context-aware dashboards."
---

# Home Assistant Conditional Cards

Control card visibility dynamically based on states, users, screen size, and complex conditions.

## Overview

Home Assistant provides two approaches for conditional visibility:
- **Conditional Card** (wrapper): Shows/hides entire card based on conditions
- **Per-Card Visibility**: Native `visibility` property on any card

Both support multiple condition types:
- **state**: Entity matches specific state
- **numeric_state**: Sensor value within range
- **screen**: Screen width/media queries
- **user**: Current user matches list
- **time**: Current time within range
- **and/or**: Complex logic combinations

## Quick Start

### Conditional Card (Wrapper)

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

### Per-Card Visibility (Native)

```yaml
type: entities
entities:
  - light.bedroom
visibility:
  - condition: state
    entity: person.john
    state: home
```

## Condition Types Reference

| Condition | Parameters | Use Case |
|-----------|------------|----------|
| `state` | `entity`, `state` | Show when entity has specific state |
| `numeric_state` | `entity`, `above`, `below` | Show when sensor in range |
| `screen` | `media_query` | Show based on screen width |
| `user` | `users` (list of user IDs) | Show for specific users only |
| `time` | `after`, `before` | Show during specific time window |
| `and` | List of conditions | All conditions must be true |
| `or` | List of conditions | At least one condition must be true |

## State Conditions

### Basic State Match

```yaml
type: conditional
conditions:
  - condition: state
    entity: binary_sensor.motion_living_room
    state: "on"
card:
  type: camera
  entity: camera.living_room
```

### Multiple State Options

```yaml
visibility:
  - condition: state
    entity: climate.living_room
    state_not:
      - "off"
      - unavailable
```

### State with Attributes (Workaround)

**Note:** Native conditional cards don't support attribute conditions. Create a template sensor instead.

```yaml
# In configuration.yaml
template:
  - sensor:
      - name: "AC Mode Cool"
        state: "{{ state_attr('climate.living_room', 'hvac_mode') == 'cool' }}"

# In dashboard
visibility:
  - condition: state
    entity: sensor.ac_mode_cool
    state: "True"
```

## Numeric State Conditions

### Temperature Range

```yaml
type: entities
entities:
  - climate.bedroom
visibility:
  - condition: numeric_state
    entity: sensor.temperature
    above: 18
    below: 30
```

### Above Threshold

```yaml
visibility:
  - condition: numeric_state
    entity: sensor.battery
    below: 20  # Show when battery < 20%
```

### Between Values

```yaml
visibility:
  - condition: numeric_state
    entity: sensor.humidity
    above: 40
    below: 60  # Show when 40% < humidity < 60%
```

## Screen/Responsive Conditions

### Mobile Only

```yaml
visibility:
  - condition: screen
    media_query: "(max-width: 600px)"
```

### Desktop Only

```yaml
visibility:
  - condition: screen
    media_query: "(min-width: 1280px)"
```

### Tablet Range

```yaml
visibility:
  - condition: screen
    media_query: "(min-width: 601px) and (max-width: 1279px)"
```

### Common Media Queries

```yaml
# Mobile (portrait)
media_query: "(max-width: 600px)"

# Tablet (portrait)
media_query: "(min-width: 601px) and (max-width: 900px)"

# Desktop
media_query: "(min-width: 1280px)"

# Landscape orientation
media_query: "(orientation: landscape)"

# Portrait orientation
media_query: "(orientation: portrait)"
```

## User Conditions

### Single User

```yaml
visibility:
  - condition: user
    users:
      - 1234567890abcdef  # User ID (not username)
```

### Multiple Users (Admin Access)

```yaml
type: entities
entities:
  - switch.advanced_settings
visibility:
  - condition: user
    users:
      - 1234567890abcdef  # Admin user 1
      - fedcba0987654321  # Admin user 2
```

**Finding User IDs:**
1. Go to Settings → People
2. Click on user
3. User ID is in the URL: `/config/person/USER_ID_HERE`

## Time Conditions

### During Daytime

```yaml
visibility:
  - condition: time
    after: "06:00:00"
    before: "22:00:00"
```

### Night Mode Cards

```yaml
visibility:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"
```

### Business Hours

```yaml
visibility:
  - condition: time
    after: "09:00:00"
    before: "17:00:00"
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
```

## Complex Logic (AND/OR)

### AND Condition (All Must Be True)

```yaml
visibility:
  - condition: and
    conditions:
      - condition: state
        entity: person.john
        state: home
      - condition: numeric_state
        entity: sensor.temperature
        below: 18
      - condition: time
        after: "06:00:00"
        before: "23:00:00"
```

### OR Condition (At Least One Must Be True)

```yaml
visibility:
  - condition: or
    conditions:
      - condition: state
        entity: person.john
        state: home
      - condition: state
        entity: person.jane
        state: home
```

### Nested Logic

```yaml
visibility:
  - condition: and
    conditions:
      # Show during daytime...
      - condition: time
        after: "06:00:00"
        before: "22:00:00"
      # ...AND (someone is home OR security is armed)
      - condition: or
        conditions:
          - condition: state
            entity: person.john
            state: home
          - condition: state
            entity: alarm_control_panel.home
            state: armed_away
```

## Real-World Patterns

### Show Camera When Motion Detected

```yaml
type: conditional
conditions:
  - condition: state
    entity: binary_sensor.motion_living_room
    state: "on"
card:
  type: camera
  entity: camera.living_room
```

### Climate Controls When Someone Home

```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.living_room
    visibility:
      - condition: or
        conditions:
          - condition: state
            entity: person.john
            state: home
          - condition: state
            entity: person.jane
            state: home
```

### Low Battery Alert

```yaml
type: entities
title: Low Battery Devices
entities:
  - sensor.motion_sensor_battery
  - sensor.door_sensor_battery
visibility:
  - condition: or
    conditions:
      - condition: numeric_state
        entity: sensor.motion_sensor_battery
        below: 20
      - condition: numeric_state
        entity: door_sensor_battery
        below: 20
```

### Temperature Warning

```yaml
type: markdown
content: "⚠️ Temperature outside normal range!"
visibility:
  - condition: or
    conditions:
      - condition: numeric_state
        entity: sensor.temperature
        below: 18
      - condition: numeric_state
        entity: sensor.temperature
        above: 28
```

### Admin-Only Controls

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: "## Advanced Settings"

  - type: entities
    entities:
      - switch.developer_mode
      - switch.debug_logging
      - input_boolean.maintenance_mode
visibility:
  - condition: user
    users:
      - 1234567890abcdef  # Admin user ID
```

### Mobile vs Desktop Layout

```yaml
# Mobile: Show compact chips
type: custom:mushroom-chips-card
chips:
  - type: entity
    entity: sensor.temperature
  - type: weather
    entity: weather.home
visibility:
  - condition: screen
    media_query: "(max-width: 600px)"

---

# Desktop: Show detailed cards
type: grid
columns: 3
cards:
  - type: sensor
    entity: sensor.temperature
  - type: weather-forecast
    entity: weather.home
visibility:
  - condition: screen
    media_query: "(min-width: 1280px)"
```

### Occupied Room Indicators

```yaml
type: entities
title: Bedroom
entities:
  - light.bedroom
  - climate.bedroom
  - sensor.temperature_bedroom
visibility:
  - condition: state
    entity: binary_sensor.bedroom_occupied
    state: "on"
```

### After-Hours Emergency Button

```yaml
type: button
name: Emergency Contact
icon: mdi:phone-alert
tap_action:
  action: perform-action
  perform_action: notify.mobile_app
  data:
    message: "Emergency call requested"
visibility:
  - condition: time
    after: "17:00:00"
    before: "09:00:00"
```

## Best Practices

### 1. Combine Conditional with State-Based Visibility

```yaml
# Use conditional card for complex logic
type: conditional
conditions:
  - condition: and
    conditions:
      - condition: state
        entity: person.john
        state: home
      - condition: time
        after: "18:00:00"

# Use per-card visibility for simple conditions
visibility:
  - condition: state
    entity: light.bedroom
    state: "on"
```

### 2. Test Conditions in Edit Mode

Cards with `visibility` always render in edit mode. **Exit edit mode to test visibility behavior.**

### 3. Use Helper Entities for Complex Logic

Create template sensors for complex attribute-based conditions:

```yaml
# configuration.yaml
template:
  - binary_sensor:
      - name: "AC Cooling"
        state: "{{ state_attr('climate.living_room', 'hvac_mode') == 'cool' }}"

# Dashboard
visibility:
  - condition: state
    entity: binary_sensor.ac_cooling
    state: "on"
```

### 4. Combine with Mushroom Template Cards

```yaml
type: custom:mushroom-template-card
primary: "Windows Open"
secondary: "{{ states('sensor.windows_open') }} windows"
icon: mdi:window-open
visibility:
  - condition: numeric_state
    entity: sensor.windows_open
    above: 0
```

### 5. Use Screen Conditions for Responsive Design

```yaml
# Mobile: Compact view
type: custom:mushroom-chips-card
visibility:
  - condition: screen
    media_query: "(max-width: 600px)"

# Desktop: Detailed view
type: grid
columns: 3
visibility:
  - condition: screen
    media_query: "(min-width: 1280px)"
```

## Limitations

### Cannot Directly Check Attributes

❌ This doesn't work:
```yaml
visibility:
  - condition: state
    entity: climate.living_room
    attribute: hvac_mode
    state: "cool"
```

✅ Workaround: Create template sensor
```yaml
# configuration.yaml
template:
  - sensor:
      - name: "AC Mode"
        state: "{{ state_attr('climate.living_room', 'hvac_mode') }}"

# Dashboard
visibility:
  - condition: state
    entity: sensor.ac_mode
    state: "cool"
```

### No Template Support in Conditions

❌ This doesn't work:
```yaml
visibility:
  - condition: template
    value_template: "{{ states('sensor.temperature') | float > 25 }}"
```

✅ Workaround: Create template binary sensor

### Always Visible in Edit Mode

Cards with `visibility` always show in edit mode. Must exit edit mode to test visibility.

## Troubleshooting

### Card Not Hiding

- Exit edit mode (cards always visible when editing)
- Check entity state (Developer Tools → States)
- Verify condition syntax (YAML indentation)
- Check for typos in entity_id

### User Condition Not Working

- Verify user ID (not username)
- Find ID in URL: Settings → People → (click user)
- Use user ID, not email or name

### Time Condition Not Working

- Use 24-hour format (`"23:00:00"` not `"11:00 PM"`)
- Check Home Assistant timezone (Settings → System → General)
- Verify `after` is before `before`

### Numeric Condition Not Working

- Check sensor has numeric state (not "unknown" or "unavailable")
- Use proper comparison (`above`/`below`, not `>` or `<`)
- Verify sensor unit matches expectation

### Screen Condition Not Working

- Test on actual device (browser resize ≠ responsive behavior)
- Use correct media query syntax
- Check for conflicting conditions

## Official Documentation

- [Conditional card - Home Assistant](https://www.home-assistant.io/dashboards/conditional/)
- [Card Visibility - Home Assistant](https://www.home-assistant.io/dashboards/cards/#card-visibility)
- [Template Sensors - Home Assistant](https://www.home-assistant.io/integrations/template/)
