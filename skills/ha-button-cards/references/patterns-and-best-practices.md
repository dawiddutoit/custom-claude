# Home Assistant Button Cards: Patterns and Best Practices

## Real-World Patterns

### Irrigation Controller Grid

```yaml
type: grid
columns: 2
cards:
  # Individual zone controls
  - type: custom:button-card
    entity: switch.s01_left_top_patio_lawn_station_enabled
    name: Left Top Patio
    icon: mdi:sprinkler
    show_state: true
    tap_action:
      action: toggle

  - type: custom:button-card
    entity: switch.s02_right_top_patio_lawn_station_enabled
    name: Right Top Patio
    icon: mdi:sprinkler
    show_state: true
    tap_action:
      action: toggle

  # All zones off
  - type: custom:button-card
    name: Stop All Zones
    icon: mdi:stop
    tap_action:
      action: perform-action
      perform_action: switch.turn_off
      target:
        entity_id:
          - switch.s01_left_top_patio_lawn_station_enabled
          - switch.s02_right_top_patio_lawn_station_enabled
    styles:
      card:
        - background-color: rgb(231, 76, 60)
```

### Device Status with Navigation

```yaml
type: custom:button-card
entity: sensor.motion_sensor_living_room_battery
name: Living Room Motion
icon: mdi:motion-sensor
show_state: true
color: |
  [[[
    const battery = states['sensor.motion_sensor_living_room_battery'].state;
    if (battery < 20) return 'red';
    if (battery < 50) return 'orange';
    return 'green';
  ]]]
tap_action:
  action: more-info
hold_action:
  action: navigate
  navigation_path: /lovelace/sensors
```

## Best Practices

### 1. Use Descriptive Names

```yaml
# Good
type: button
name: Turn Off All Lights
icon: mdi:lightbulb-off

# Bad
type: button
name: Off
icon: mdi:lightbulb-off
```

### 2. Disable Unused Actions

```yaml
type: button
entity: light.bedroom
tap_action:
  action: toggle
hold_action:
  action: none  # Disable hold if not needed
double_tap_action:
  action: none  # Disable double-tap if not needed
```

### 3. Show State for Toggles

```yaml
type: button
entity: light.living_room
show_state: true  # User sees on/off state
tap_action:
  action: toggle
```

### 4. Use Icons Consistently

- `mdi:lightbulb` for lights
- `mdi:air-conditioner` for climate
- `mdi:sprinkler` for irrigation
- `mdi:home` for home/back navigation
- `mdi:bed` for bedroom
- `mdi:sofa` for living room

### 5. Group Related Actions

```yaml
type: grid
columns: 3
cards:
  # Group all light controls together
  - type: button
    entity: light.all_lights
  - type: button
    name: Bright
    tap_action:
      action: perform-action
      perform_action: light.turn_on
      data:
        entity_id: light.all_lights
        brightness: 255
  - type: button
    name: Dim
    tap_action:
      action: perform-action
      perform_action: light.turn_on
      data:
        entity_id: light.all_lights
        brightness: 50
```

### 6. Leverage Templates for Consistency

```yaml
button_card_templates:
  standard_light:
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    show_state: true
    icon: mdi:lightbulb
```

### 7. Test All Actions

Before deploying:
- Test tap action
- Test hold action (if configured)
- Test double-tap action (if configured)
- Verify entity updates correctly
- Check icon and state display

### 8. Use Confirmation for Destructive Actions

```yaml
type: button
name: Turn Off All Systems
tap_action:
  action: perform-action
  perform_action: script.shutdown_all
  confirmation:
    text: "Are you sure you want to turn off all systems?"
```

### 9. Optimize for Mobile

- Use large enough touch targets
- Test on mobile devices
- Avoid overly complex grids
- Ensure icons are recognizable

### 10. Document Complex Configurations

```yaml
# This button triggers a complex automation that:
# 1. Turns off all lights
# 2. Locks all doors
# 3. Sets alarm to away mode
type: button
name: Goodbye
tap_action:
  action: perform-action
  perform_action: script.goodbye_routine
```
