# Home Assistant REST API Endpoint Reference

Complete reference for Home Assistant REST API endpoints commonly used in network infrastructure operations.

## Table of Contents

1. [Authentication](#authentication)
2. [Architecture Details](#architecture-details)
3. [Core API Endpoints](#core-api-endpoints)
4. [Response Codes](#response-codes)

## Authentication

All API requests require authentication via long-lived access token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     "${HA_BASE_URL}/api/endpoint"
```

## Core API Endpoints

### GET /api/

Returns API running message.

```bash
curl -s "${HA_BASE_URL}/api/" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}"

# Response:
# {"message": "API running."}
```

### GET /api/config

Returns Home Assistant configuration.

```bash
curl -s "${HA_BASE_URL}/api/config" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | jq .

# Response includes:
# - location_name
# - latitude/longitude
# - elevation
# - unit_system
# - time_zone
# - components (list of loaded integrations)
# - version
```

### GET /api/states

Returns all entity states.

```bash
curl -s "${HA_BASE_URL}/api/states" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | jq .

# Response: Array of entity objects
# [
#   {
#     "entity_id": "sensor.temperature",
#     "state": "22.5",
#     "attributes": {...},
#     "last_changed": "2026-01-20T10:00:00+00:00",
#     "last_updated": "2026-01-20T10:00:00+00:00"
#   },
#   ...
# ]
```

### GET /api/states/<entity_id>

Returns specific entity state.

```bash
curl -s "${HA_BASE_URL}/api/states/sensor.temperature" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | jq .

# Response:
# {
#   "entity_id": "sensor.temperature",
#   "state": "22.5",
#   "attributes": {
#     "unit_of_measurement": "°C",
#     "friendly_name": "Temperature"
#   },
#   "last_changed": "2026-01-20T10:00:00+00:00"
# }
```

### POST /api/states/<entity_id>

Updates entity state (use with caution).

```bash
curl -X POST "${HA_BASE_URL}/api/states/sensor.custom_sensor" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "online",
    "attributes": {
      "last_check": "2026-01-20T10:00:00"
    }
  }'
```

### GET /api/services

Returns all available services.

```bash
curl -s "${HA_BASE_URL}/api/services" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | jq .

# Response: Array of service domains with services
# [
#   {
#     "domain": "light",
#     "services": {
#       "turn_on": {...},
#       "turn_off": {...}
#     }
#   },
#   ...
# ]
```

### POST /api/services/<domain>/<service>

Calls a service.

```bash
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room",
    "brightness": 255,
    "color_temp": 400
  }'

# Response: Array of changed entities
# [
#   {
#     "entity_id": "light.living_room",
#     "state": "on",
#     ...
#   }
# ]
```

## Common Service Domains

### notify

Send notifications to various platforms.

```bash
# Mobile app notification
curl -X POST "${HA_BASE_URL}/api/services/notify/mobile_app_phone" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Infrastructure alert",
    "title": "Network Status",
    "data": {
      "priority": "high",
      "tag": "infrastructure"
    }
  }'

# Persistent notification (HA UI)
curl -X POST "${HA_BASE_URL}/api/services/notify/persistent_notification" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "This appears in HA UI",
    "title": "System Alert"
  }'
```

### light

Control lights.

```bash
# Turn on
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}'

# Turn off
curl -X POST "${HA_BASE_URL}/api/services/light/turn_off" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}'

# Set brightness and color
curl -X POST "${HA_BASE_URL}/api/services/light/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "light.living_room",
    "brightness": 200,
    "rgb_color": [255, 0, 0]
  }'
```

### switch

Control switches.

```bash
# Turn on
curl -X POST "${HA_BASE_URL}/api/services/switch/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.sprinkler"}'

# Turn off
curl -X POST "${HA_BASE_URL}/api/services/switch/turn_off" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.sprinkler"}'

# Toggle
curl -X POST "${HA_BASE_URL}/api/services/switch/toggle" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.sprinkler"}'
```

### automation

Control automations.

```bash
# Trigger automation
curl -X POST "${HA_BASE_URL}/api/services/automation/trigger" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.infrastructure_alert"}'

# Turn on automation
curl -X POST "${HA_BASE_URL}/api/services/automation/turn_on" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.infrastructure_alert"}'

# Turn off automation
curl -X POST "${HA_BASE_URL}/api/services/automation/turn_off" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.infrastructure_alert"}'
```

### homeassistant

Core HA services.

```bash
# Restart Home Assistant
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/restart" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}"

# Reload configuration
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/reload_config_entry" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}"

# Check configuration
curl -X POST "${HA_BASE_URL}/api/services/homeassistant/check_config" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}"
```

## Event Endpoints

### GET /api/events

Returns all event types.

```bash
curl -s "${HA_BASE_URL}/api/events" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | jq .

# Response: Array of event types
# [
#   {"event": "state_changed"},
#   {"event": "time_changed"},
#   {"event": "service_registered"},
#   ...
# ]
```

### POST /api/events/<event_type>

Fires an event.

```bash
curl -X POST "${HA_BASE_URL}/api/events/infrastructure_alert" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "high",
    "component": "cloudflare_tunnel",
    "message": "Tunnel reconnected"
  }'
```

## Error Logging

### POST /api/error_log

Writes to Home Assistant error log.

```bash
curl -X POST "${HA_BASE_URL}/api/error_log" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Custom error from infrastructure monitoring"
  }'
```

### GET /api/error_log

Retrieves error log.

```bash
curl -s "${HA_BASE_URL}/api/error_log" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}"
```

## Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request completed successfully |
| 201 | Created | Entity created successfully |
| 400 | Bad Request | Check request payload format |
| 401 | Unauthorized | Verify access token is valid |
| 404 | Not Found | Check endpoint or entity_id exists |
| 405 | Method Not Allowed | **EXPECTED for HEAD requests** - Use GET instead |
| 500 | Internal Server Error | Check HA logs for details |

## Important Notes

### HTTP 405 Method Not Allowed

**This is EXPECTED behavior for HEAD requests:**

```bash
# ❌ This returns 405 (but it's normal!)
curl -I "${HA_BASE_URL}/"
# HTTP/2 405 Method Not Allowed
# Allow: GET

# ✅ This works
curl -s "${HA_BASE_URL}/"
# Returns HTML page
```

**Why:** Home Assistant does not implement HEAD method for most endpoints. This is by design, not a bug.

**Solution:** Always use GET for health checks and availability verification.

### Authentication Headers

All requests except `/api/` health check require authentication:

```bash
-H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN"
```

### Content Type

POST requests require Content-Type header:

```bash
-H "Content-Type: application/json"
```

### Timeouts

Use timeouts to prevent hanging:

```bash
--max-time 10  # 10 second timeout
```

## Filtering and Querying with jq

```bash
# Get all lights that are on
curl -s "${HA_BASE_URL}/api/states" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | \
  jq '[.[] | select(.entity_id | startswith("light.")) | select(.state == "on")]'

# Get temperature sensors
curl -s "${HA_BASE_URL}/api/states" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | \
  jq '[.[] | select(.entity_id | startswith("sensor.")) | select(.attributes.device_class == "temperature")]'

# Get entities with low battery
curl -s "${HA_BASE_URL}/api/states" \
  -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" | \
  jq '[.[] | select(.attributes.battery_level) | select(.attributes.battery_level < 20)]'
```

## Official Documentation

- **REST API:** https://developers.home-assistant.io/docs/api/rest/
- **WebSocket API:** https://developers.home-assistant.io/docs/api/websocket/
- **Service Calls:** https://www.home-assistant.io/docs/scripts/service-calls/
