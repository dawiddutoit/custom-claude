# Home Assistant REST API Endpoints Reference

Complete reference for Home Assistant REST API endpoints.

## Base URL

```
http://192.168.68.123:8123
```

## Authentication

All requests require a Bearer token in the Authorization header:

```
Authorization: Bearer <HA_LONG_LIVED_TOKEN>
```

## Core Endpoints

### GET /api/

API status check. Returns `{"message": "API running."}` if successful.

### GET /api/config

Returns the Home Assistant configuration:

```json
{
  "location_name": "Home",
  "latitude": -26.0,
  "longitude": 28.0,
  "elevation": 1400,
  "unit_system": {
    "length": "km",
    "mass": "g",
    "temperature": "°C",
    "volume": "L"
  },
  "time_zone": "Africa/Johannesburg",
  "version": "2025.12.3",
  "config_dir": "/config"
}
```

### GET /api/states

Returns array of all entity states:

```json
[
  {
    "entity_id": "sensor.temperature",
    "state": "22.5",
    "attributes": {
      "unit_of_measurement": "°C",
      "friendly_name": "Temperature",
      "device_class": "temperature"
    },
    "last_changed": "2025-12-14T10:30:00+00:00",
    "last_updated": "2025-12-14T10:30:00+00:00"
  }
]
```

### GET /api/states/:entity_id

Returns state for a specific entity:

```json
{
  "entity_id": "sensor.officeht_temperature",
  "state": "23.2",
  "attributes": {
    "unit_of_measurement": "°C",
    "device_class": "temperature",
    "friendly_name": "OfficeHT Temperature"
  },
  "last_changed": "2025-12-14T10:30:00+00:00",
  "last_updated": "2025-12-14T10:30:00+00:00"
}
```

### POST /api/states/:entity_id

Set or update entity state (requires appropriate permissions):

```json
{
  "state": "23.5",
  "attributes": {
    "unit_of_measurement": "°C"
  }
}
```

### GET /api/services

Returns all available services grouped by domain:

```json
[
  {
    "domain": "light",
    "services": {
      "turn_on": {
        "name": "Turn on",
        "description": "Turn on one or more lights.",
        "fields": {
          "brightness": {
            "description": "Number indicating brightness",
            "example": 120
          }
        }
      },
      "turn_off": {
        "name": "Turn off",
        "description": "Turn off one or more lights."
      }
    }
  }
]
```

### POST /api/services/:domain/:service

Call a service:

**URL:** `/api/services/light/turn_on`

**Request Body:**
```json
{
  "entity_id": "light.living_room_dimmer",
  "brightness": 150
}
```

**Response:**
```json
[
  {
    "entity_id": "light.living_room_dimmer",
    "state": "on",
    "attributes": {
      "brightness": 150
    }
  }
]
```

### GET /api/events

Returns all event types that can be subscribed to.

### POST /api/events/:event_type

Fire an event.

### GET /api/history/period/:timestamp

Get historical states for entities.

**Example:** `/api/history/period/2025-12-14T00:00:00`

**Query Parameters:**
- `filter_entity_id`: Comma-separated entity IDs
- `end_time`: End timestamp

### GET /api/error_log

Returns contents of the error log.

### GET /api/camera_proxy/:entity_id

Proxy camera image.

### POST /api/template

Render a template:

**Request:**
```json
{
  "template": "The temperature is {{ states('sensor.temperature') }}°C"
}
```

**Response:**
```
The temperature is 22.5°C
```

## Service Call Examples by Domain

### Light Domain

```bash
# Turn on
POST /api/services/light/turn_on
{
  "entity_id": "light.living_room_dimmer",
  "brightness": 150,
  "color_temp": 350
}

# Turn off
POST /api/services/light/turn_off
{
  "entity_id": "light.living_room_dimmer"
}

# Toggle
POST /api/services/light/toggle
{
  "entity_id": "light.living_room_dimmer"
}
```

### Climate Domain

```bash
# Turn on
POST /api/services/climate/turn_on
{
  "entity_id": "climate.snorlug"
}

# Set temperature
POST /api/services/climate/set_temperature
{
  "entity_id": "climate.snorlug",
  "temperature": 22
}

# Set HVAC mode
POST /api/services/climate/set_hvac_mode
{
  "entity_id": "climate.snorlug",
  "hvac_mode": "cool"
}
```

### Switch Domain

```bash
# Turn on
POST /api/services/switch/turn_on
{
  "entity_id": "switch.s01_left_top_patio_lawn_station_enabled"
}

# Turn off
POST /api/services/switch/turn_off
{
  "entity_id": "switch.s01_left_top_patio_lawn_station_enabled"
}
```

### Automation Domain

```bash
# Trigger
POST /api/services/automation/trigger
{
  "entity_id": "automation.morning_lights"
}

# Turn on
POST /api/services/automation/turn_on
{
  "entity_id": "automation.morning_lights"
}

# Turn off
POST /api/services/automation/turn_off
{
  "entity_id": "automation.morning_lights"
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid JSON or parameters) |
| 401 | Unauthorized (invalid token) |
| 404 | Entity or service not found |
| 405 | Method not allowed |
| 500 | Internal server error |

## Rate Limiting

Home Assistant does not enforce strict rate limits, but it's good practice to:
- Avoid polling faster than every 5 seconds
- Batch requests when possible
- Use WebSocket API for real-time updates instead of polling

## Error Response Format

```json
{
  "message": "Entity not found: sensor.nonexistent"
}
```
