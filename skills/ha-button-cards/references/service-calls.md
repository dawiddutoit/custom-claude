# Home Assistant Service Calls Reference

## Common Service Patterns

### Light Services

```yaml
# Turn on with brightness
tap_action:
  action: perform-action
  perform_action: light.turn_on
  data:
    entity_id: light.living_room
    brightness: 255

# Turn off all lights
tap_action:
  action: perform-action
  perform_action: light.turn_off
  data:
    entity_id: all
```

### Switch Services

```yaml
# Toggle switch
tap_action:
  action: perform-action
  perform_action: switch.toggle
  data:
    entity_id: switch.fan
```

### Climate Services

```yaml
# Set temperature
tap_action:
  action: perform-action
  perform_action: climate.set_temperature
  data:
    entity_id: climate.living_room
    temperature: 22
```

### Scene Activation

```yaml
# Activate scene
tap_action:
  action: perform-action
  perform_action: scene.turn_on
  data:
    entity_id: scene.movie_time
```

### Script Execution

```yaml
# Run script
tap_action:
  action: perform-action
  perform_action: script.turn_on
  data:
    entity_id: script.goodnight
```

### Automation Triggering

```yaml
# Trigger automation
tap_action:
  action: perform-action
  perform_action: automation.trigger
  data:
    entity_id: automation.motion_lights
```

## Advanced Service Calls

### Multiple Targets

```yaml
tap_action:
  action: perform-action
  perform_action: light.turn_on
  data:
    entity_id:
      - light.living_room
      - light.kitchen
      - light.bedroom
    brightness: 180
```

### Area-Based Services

```yaml
tap_action:
  action: perform-action
  perform_action: light.turn_off
  target:
    area_id: living_room
```

### Device-Based Services

```yaml
tap_action:
  action: perform-action
  perform_action: light.turn_on
  target:
    device_id: abc123def456
```
