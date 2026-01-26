# Home Assistant Button Card Actions Reference

## Available Actions

| Action | Description | Example Use |
|--------|-------------|-------------|
| `none` | Do nothing | Disable interaction |
| `toggle` | Toggle entity on/off | Lights, switches |
| `more-info` | Show entity details dialog | View sensor history |
| `navigate` | Go to another view/dashboard | Room navigation |
| `url` | Open external URL | Documentation, web apps |
| `perform-action` (was `call-service`) | Execute HA service | Scripts, automations, scenes |
| `assist` | Trigger voice assistant | Voice commands |

## Action Configuration

### Toggle Action

```yaml
tap_action:
  action: toggle
```

### More Info Action

```yaml
tap_action:
  action: more-info
```

### Navigation Action

```yaml
tap_action:
  action: navigate
  navigation_path: /lovelace/bedroom
```

### URL Action

```yaml
tap_action:
  action: url
  url_path: https://www.home-assistant.io
```

### Service Call Action

```yaml
tap_action:
  action: perform-action
  perform_action: light.turn_on
  data:
    entity_id: light.living_room
    brightness: 255
```

### Assist Action

```yaml
tap_action:
  action: assist
  pipeline_id: preferred
  start_listening: true
```
