# Home Assistant Service Call Examples

Practical examples for calling Home Assistant services via REST API.

## Setup

All examples assume .env is sourced:

```bash
source /Users/dawiddutoit/projects/play/network-infrastructure/.env
```

## Light Control

### Turn On Light

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room"
  }'
```

### Turn On with Brightness

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room",
    "brightness": 200
  }'
```

**Brightness:** 0-255

### Turn On with Color

```bash
# RGB color
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room",
    "rgb_color": [255, 0, 0]
  }'

# Color temperature (warm to cool)
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room",
    "color_temp": 400
  }'
```

**Color temp:** 153-500 mireds (warm=500, cool=153)

### Turn Off Light

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/turn_off" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room"
  }'
```

### Toggle Light

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/toggle" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room"
  }'
```

### Control Multiple Lights

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": ["light.living_room", "light.kitchen", "light.bedroom"],
    "brightness": 150
  }'
```

## Switch Control

### Turn On Switch

```bash
curl -X POST "${HA_BASE_URL}/api/services/switch/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "switch.sprinkler_zone_1"
  }'
```

### Turn Off Switch

```bash
curl -X POST "${HA_BASE_URL}/api/services/switch/turn_off" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "switch.sprinkler_zone_1"
  }'
```

### Toggle Switch

```bash
curl -X POST "${HA_BASE_URL}/api/services/switch/toggle" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "switch.sprinkler_zone_1"
  }'
```

## Climate Control

### Set Temperature

```bash
curl -X POST "${HA_BASE_URL}/api/services/climate/set_temperature" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "climate.living_room",
    "temperature": 22
  }'
```

### Set HVAC Mode

```bash
curl -X POST "${HA_BASE_URL}/api/services/climate/set_hvac_mode" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "climate.living_room",
    "hvac_mode": "heat"
  }'
```

**HVAC modes:** off, heat, cool, heat_cool, auto, dry, fan_only

### Set Fan Mode

```bash
curl -X POST "${HA_BASE_URL}/api/services/climate/set_fan_mode" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "climate.living_room",
    "fan_mode": "auto"
  }'
```

## Automation Control

### Trigger Automation

```bash
curl -X POST "${HA_BASE_URL}/api/services/automation/trigger" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "automation.infrastructure_alert_handler"
  }'
```

### Turn On Automation

```bash
curl -X POST "${HA_BASE_URL}/api/services/automation/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "automation.infrastructure_alert_handler"
  }'
```

### Turn Off Automation

```bash
curl -X POST "${HA_BASE_URL}/api/services/automation/turn_off" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "automation.infrastructure_alert_handler"
  }'
```

### Reload Automations

```bash
curl -X POST "${HA_BASE_URL}/api/services/automation/reload" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

## Script Execution

### Run Script

```bash
curl -X POST "${HA_BASE_URL}/api/services/script/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "script.infrastructure_recovery"
  }'
```

### Run Script with Variables

```bash
curl -X POST "${HA_BASE_URL}/api/services/script/infrastructure_recovery" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "component": "tunnel",
      "action": "restart"
    }
  }'
```

## Scene Activation

### Activate Scene

```bash
curl -X POST "${HA_BASE_URL}/api/services/scene/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "scene.infrastructure_alert"
  }'
```

## Input Controls

### Set Input Boolean

```bash
curl -X POST "${HA_BASE_URL}/api/services/input_boolean/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "input_boolean.infrastructure_maintenance_mode"
  }'
```

### Set Input Number

```bash
curl -X POST "${HA_BASE_URL}/api/services/input_number/set_value" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "input_number.alert_threshold",
    "value": 5
  }'
```

### Set Input Select

```bash
curl -X POST "${HA_BASE_URL}/api/services/input_select/select_option" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "input_select.infrastructure_status",
    "option": "degraded"
  }'
```

### Set Input Text

```bash
curl -X POST "${HA_BASE_URL}/api/services/input_text/set_value" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "input_text.last_alert_message",
    "value": "Tunnel auto-recovered at 2026-01-20 10:30"
  }'
```

## Media Player Control

### Play Media

```bash
curl -X POST "${HA_BASE_URL}/api/services/media_player/play_media" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "media_content_id": "https://example.com/alert.mp3",
    "media_content_type": "music"
  }'
```

### Volume Control

```bash
curl -X POST "${HA_BASE_URL}/api/services/media_player/volume_set" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "volume_level": 0.5
  }'
```

## System Services

### Restart Home Assistant

```bash
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/restart" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Stop Home Assistant

```bash
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/stop" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Reload Core Configuration

```bash
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/reload_core_config" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Check Configuration

```bash
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/check_config" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Update Entity

```bash
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/update_entity" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "sensor.infrastructure_status"
  }'
```

## Shell Commands

If shell commands are configured in HA:

```bash
curl -X POST "${HA_BASE_URL}/api/services/shell_command/restart_tunnel" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

**Configuration example (configuration.yaml):**

```yaml
shell_command:
  restart_tunnel: 'ssh pi@192.168.68.136 "cd /home/dawiddutoit/projects/network && docker restart cloudflared"'
  check_infrastructure: '/home/dawiddutoit/projects/network/scripts/health-check.sh'
```

## Infrastructure-Specific Examples

### Create Infrastructure Status Sensor

```bash
# Update custom sensor state
curl -X POST "${HA_BASE_URL}/api/states/sensor.infrastructure_status" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "healthy",
    "attributes": {
      "last_check": "2026-01-20T10:30:00",
      "tunnel": "connected",
      "dns": "responding",
      "caddy": "running",
      "certificates": "valid"
    }
  }'
```

### Trigger Infrastructure Alert Automation

```bash
curl -X POST "${HA_BASE_URL}/api/services/automation/trigger" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "automation.infrastructure_critical_alert",
    "skip_condition": true
  }'
```

### Update Maintenance Mode

```bash
curl -X POST "${HA_BASE_URL}/api/services/input_boolean/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "input_boolean.infrastructure_maintenance"
  }'
```

## Error Handling in Scripts

```bash
#!/bin/bash
source /Users/dawiddutoit/projects/play/network-infrastructure/.env

call_ha_service() {
    local domain="$1"
    local service="$2"
    local entity_id="$3"
    local extra_data="${4:-}"

    local payload
    if [[ -n "$extra_data" ]]; then
        payload="{\"entity_id\": \"$entity_id\", $extra_data}"
    else
        payload="{\"entity_id\": \"$entity_id\"}"
    fi

    local response
    response=$(curl -s -X POST "${HA_BASE_URL}/api/services/${domain}/${service}" \
        -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time 10 \
        2>&1)

    local exit_code=$?

    if [[ $exit_code -ne 0 ]]; then
        echo "ERROR: Failed to call service ${domain}.${service}: $response" >&2
        return 1
    fi

    echo "$response"
    return 0
}

# Usage
call_ha_service "light" "turn_on" "light.living_room" '"brightness": 200'
call_ha_service "switch" "turn_off" "switch.sprinkler"
call_ha_service "automation" "trigger" "automation.infrastructure_alert"
```

## Bulk Operations

### Turn Off All Lights

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/turn_off" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "all"
  }'
```

### Turn On All Lights in Group

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "group.living_room_lights"
  }'
```

## Common Patterns

### Check Then Act

```bash
# Get current state
current_state=$(curl -s "${HA_BASE_URL}/api/states/light.living_room" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | jq -r .state)

# Act based on state
if [[ "$current_state" == "off" ]]; then
    curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
      -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{"entity_id": "light.living_room"}'
fi
```

### Sequential Service Calls

```bash
# Turn on lights
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "group.infrastructure_alerts"}'

# Send notification
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Alert lights activated", "title": "Infrastructure Alert"}'

# Trigger automation
curl -X POST "${HA_BASE_URL}/api/services/automation/trigger" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.infrastructure_alert_handler"}'
```

## Testing Service Calls

### Verify Service Exists

```bash
# List all services in domain
curl -s "${HA_BASE_URL}/api/services" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | \
  jq '.[] | select(.domain == "light") | .services'
```

### Test with Dry Run (No Action)

Use input_boolean for testing:

```bash
# Create test input_boolean in HA configuration.yaml:
# input_boolean:
#   test_service_call:
#     name: Test Service Call

# Test service call
curl -X POST "${HA_BASE_URL}/api/services/input_boolean/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_boolean.test_service_call"}'
```

## See Also

- HA REST API Reference: `references/api-endpoints.md`
- Notification Examples: `examples/notification-examples.md`
- Main SKILL.md: Section 3.5 (Calling HA Services)
