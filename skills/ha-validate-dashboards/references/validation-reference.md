# Home Assistant Validation Reference

Comprehensive API reference and code examples for Home Assistant dashboard validation.

## Table of Contents

1. REST API Reference
2. WebSocket API Reference
3. MCP Chrome Extension Tools
4. Complete Validation Functions
5. Entity State Validation
6. Log Analysis Techniques

## 1. REST API Reference

### Key Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/` | GET | Test connection | Yes |
| `/api/states` | GET | Get all entity states | Yes |
| `/api/states/<entity_id>` | GET | Get specific entity state | Yes |
| `/api/error_log` | GET | Get error log | Yes |
| `/api/config` | GET | Get HA configuration | Yes |
| `/api/services` | GET | List available services | Yes |

### Authentication

```bash
# Header format
Authorization: Bearer <long_lived_token>

# Get token from environment
-H "Authorization: Bearer $HA_LONG_LIVED_TOKEN"
```

### Entity State Response

```json
{
  "entity_id": "sensor.enviro_temperature",
  "state": "22.5",
  "attributes": {
    "unit_of_measurement": "°C",
    "friendly_name": "Enviro Temperature",
    "device_class": "temperature"
  },
  "last_changed": "2026-01-15T10:30:00.123456+00:00",
  "last_updated": "2026-01-15T10:30:00.123456+00:00"
}
```

## 2. WebSocket API Reference

### Connection Flow

```python
import websocket
import json

ws = websocket.create_connection("ws://192.168.68.123:8123/api/websocket", timeout=10)

# 1. Receive auth_required
auth_required = json.loads(ws.recv())
# {"type": "auth_required", "ha_version": "2025.12.3"}

# 2. Send auth
ws.send(json.dumps({
    "type": "auth",
    "access_token": token
}))

# 3. Receive auth_ok or auth_invalid
auth_result = json.loads(ws.recv())
# {"type": "auth_ok", "ha_version": "2025.12.3"}

# 4. Send commands with incrementing IDs
ws.send(json.dumps({
    "id": 1,
    "type": "lovelace/dashboards/list"
}))

# 5. Receive result
result = json.loads(ws.recv())
# {"id": 1, "type": "result", "success": true, "result": [...]}
```

### WebSocket Commands

#### List Dashboards

```json
{
  "id": 1,
  "type": "lovelace/dashboards/list"
}

// Response
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": [
    {
      "id": "dashboard_id",
      "url_path": "climate-dashboard",
      "title": "Climate",
      "icon": "mdi:home-thermometer",
      "show_in_sidebar": true,
      "require_admin": false
    }
  ]
}
```

#### Get Dashboard Config

```json
{
  "id": 2,
  "type": "lovelace/config",
  "url_path": "climate-dashboard"
}

// Response
{
  "id": 2,
  "type": "result",
  "success": true,
  "result": {
    "views": [
      {
        "title": "Climate",
        "path": "climate",
        "cards": [...]
      }
    ]
  }
}
```

#### Save Dashboard Config

```json
{
  "id": 3,
  "type": "lovelace/config/save",
  "url_path": "climate-dashboard",
  "config": {
    "views": [...]
  }
}

// Success response
{
  "id": 3,
  "type": "result",
  "success": true
}

// Error response
{
  "id": 3,
  "type": "result",
  "success": false,
  "error": {
    "code": "invalid_format",
    "message": "Invalid configuration format"
  }
}
```

#### List Lovelace Resources

```json
{
  "id": 4,
  "type": "lovelace/resources"
}

// Response
{
  "id": 4,
  "type": "result",
  "success": true,
  "result": [
    {
      "id": "resource_id",
      "type": "module",
      "url": "/hacsfiles/mini-graph-card/mini-graph-card-bundle.js"
    }
  ]
}
```

## 3. MCP Chrome Extension Tools

### Available Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `navigate` | Navigate to URL | `{"url": "..."}` |
| `read_console_messages` | Read browser console | `{}` |
| `computer` | Take screenshot/interact | `{"action": "screenshot"}` |
| `read_page` | Extract page content | `{}` |
| `read_network_requests` | Monitor network calls | `{}` |

### Tool Usage Examples

#### Navigate to Dashboard

```bash
mcp-cli call claude-in-chrome/navigate '{
  "url": "http://192.168.68.123:8123/climate-dashboard"
}'

# Response
{
  "success": true,
  "url": "http://192.168.68.123:8123/climate-dashboard"
}
```

#### Read Console Messages

```bash
mcp-cli call claude-in-chrome/read_console_messages '{}'

# Response
{
  "console_messages": [
    {
      "level": "error",
      "text": "Custom element doesn't exist: custom:mini-graph-card",
      "timestamp": "2026-01-15T10:30:45.123Z",
      "source": "https://example.com/script.js:123"
    },
    {
      "level": "warning",
      "text": "Entity sensor.test is unavailable",
      "timestamp": "2026-01-15T10:30:46.456Z"
    }
  ]
}
```

#### Take Screenshot

```bash
mcp-cli call claude-in-chrome/computer '{
  "action": "screenshot"
}'

# Response
{
  "success": true,
  "path": "/tmp/screenshot_20260115_103045.png",
  "timestamp": "2026-01-15T10:30:45.123Z"
}
```

#### Read Page Content

```bash
mcp-cli call claude-in-chrome/read_page '{}'

# Response
{
  "title": "Climate - Home Assistant",
  "text": "Climate\n\nTemperature: 22.5°C\nHumidity: 55%\n...",
  "links": ["http://..."],
  "forms": []
}
```

#### Read Network Requests

```bash
mcp-cli call claude-in-chrome/read_network_requests '{}'

# Response
{
  "requests": [
    {
      "url": "http://192.168.68.123:8123/api/states",
      "method": "GET",
      "status": 200,
      "timestamp": "2026-01-15T10:30:45.123Z"
    },
    {
      "url": "http://192.168.68.123:8123/api/error_log",
      "method": "GET",
      "status": 404,
      "timestamp": "2026-01-15T10:30:46.456Z",
      "error": "Not Found"
    }
  ]
}
```

## 4. Complete Validation Functions

### Safe Dashboard Publishing

```python
import websocket
import json
import os


def publish_dashboard_safely(
    url_path: str,
    config: dict
) -> tuple[bool, str]:
    """
    Publish dashboard with pre-validation and error handling.

    Args:
        url_path: Dashboard URL path (e.g., "climate-dashboard")
        config: Dashboard configuration dict

    Returns:
        (success, message)
    """
    # 1. Validate config structure
    is_valid, validation_errors = validate_dashboard_config(config)
    if not is_valid:
        return False, f"Validation failed:\n" + "\n".join(validation_errors)

    # 2. Extract and verify all entity IDs
    entity_ids = extract_all_entity_ids(config)
    existence_map = verify_entities_exist(entity_ids)
    missing = [eid for eid, exists in existence_map.items() if not exists]

    if missing:
        return False, f"Missing entities: {', '.join(missing)}"

    # 3. Attempt publish via WebSocket
    try:
        ws = websocket.create_connection(
            "ws://192.168.68.123:8123/api/websocket",
            timeout=10
        )

        # Auth flow
        ws.recv()
        ws.send(json.dumps({
            "type": "auth",
            "access_token": os.environ["HA_LONG_LIVED_TOKEN"]
        }))
        auth_result = json.loads(ws.recv())

        if auth_result.get("type") != "auth_ok":
            return False, "Authentication failed"

        # Publish config
        ws.send(json.dumps({
            "id": 1,
            "type": "lovelace/config/save",
            "url_path": url_path,
            "config": config
        }))

        result = json.loads(ws.recv())

        if result.get("success"):
            return True, f"Dashboard '{url_path}' published successfully"
        else:
            error_msg = result.get("error", {}).get("message", "Unknown error")
            return False, f"Publish failed: {error_msg}"

    except Exception as e:
        return False, f"Exception during publish: {str(e)}"
    finally:
        ws.close()
```

### Card Validation

```python
def validate_card(card: dict, view_idx: int, card_idx: int) -> list[str]:
    """Validate individual card configuration."""
    errors = []

    # Required fields
    if "type" not in card:
        errors.append(f"View {view_idx}, Card {card_idx}: Missing required 'type'")
        return errors

    card_type = card["type"]

    # Custom card validation
    if card_type.startswith("custom:"):
        known_custom_cards = [
            "custom:mini-graph-card",
            "custom:bubble-card",
            "custom:apexcharts-card",
            "custom:modern-circular-gauge",
        ]
        if card_type not in known_custom_cards:
            errors.append(
                f"View {view_idx}, Card {card_idx}: "
                f"Unknown custom card '{card_type}' - verify HACS installation"
            )

    # Entity validation for cards that require entities
    entity_required_types = [
        "entities",
        "entity",
        "gauge",
        "sensor",
        "custom:mini-graph-card",
        "custom:modern-circular-gauge",
    ]

    if card_type in entity_required_types:
        if "entity" not in card and "entities" not in card:
            errors.append(
                f"View {view_idx}, Card {card_idx}: "
                f"Card type '{card_type}' requires 'entity' or 'entities'"
            )

    return errors
```

## 5. Entity State Validation

### Validate Entity State

```python
import requests
from datetime import datetime, timedelta


def validate_entity_state(entity_id: str) -> tuple[bool, str]:
    """
    Validate entity state is reasonable for dashboard display.

    Returns:
        (is_valid, message)
    """
    url = f"http://192.168.68.123:8123/api/states/{entity_id}"
    headers = {"Authorization": f"Bearer {os.environ['HA_LONG_LIVED_TOKEN']}"}

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 404:
            return False, f"Entity '{entity_id}' does not exist"

        state_data = response.json()
        state = state_data["state"]

        # Check for problematic states
        if state == "unavailable":
            return False, f"Entity '{entity_id}' is unavailable"

        if state == "unknown":
            return False, f"Entity '{entity_id}' has unknown state"

        # Check last_changed - warn if stale (>24h)
        last_changed_str = state_data["last_changed"]
        last_changed = datetime.fromisoformat(last_changed_str.replace('+00:00', ''))
        age = datetime.utcnow() - last_changed

        if age > timedelta(hours=24):
            return False, f"Entity '{entity_id}' hasn't updated in {age.days} days"

        return True, f"Entity '{entity_id}' is valid (state: {state})"

    except requests.exceptions.RequestException as e:
        return False, f"API error: {str(e)}"
```

### Batch Entity State Check

```python
def batch_validate_entities(entity_ids: list[str]) -> dict:
    """
    Validate multiple entities in one API call.

    Returns:
        {
            "valid": list[str],       # Entities that exist and are available
            "invalid": list[str],     # Entities that don't exist
            "unavailable": list[str]  # Entities with state "unavailable"
        }
    """
    url = "http://192.168.68.123:8123/api/states"
    headers = {"Authorization": f"Bearer {os.environ['HA_LONG_LIVED_TOKEN']}"}

    response = requests.get(url, headers=headers, timeout=10)
    all_states = {
        state["entity_id"]: state["state"]
        for state in response.json()
    }

    result = {
        "valid": [],
        "invalid": [],
        "unavailable": []
    }

    for entity_id in entity_ids:
        if entity_id not in all_states:
            result["invalid"].append(entity_id)
        elif all_states[entity_id] == "unavailable":
            result["unavailable"].append(entity_id)
        else:
            result["valid"].append(entity_id)

    return result
```

## 6. Log Analysis Techniques

### Diff-Based Log Analysis

```bash
#!/bin/bash
# Compare logs before/after deployment

# Capture baseline
curl -s "http://192.168.68.123:8123/api/error_log" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" > pre-deploy.log

# Make changes (deploy dashboard)

# Wait for errors to propagate
sleep 5

# Capture post-deployment
curl -s "http://192.168.68.123:8123/api/error_log" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" > post-deploy.log

# Show new errors only
diff pre-deploy.log post-deploy.log | grep "^>" | sed 's/^> //'
```

### Pattern-Based Log Filtering

```bash
# Filter for dashboard-related errors
curl -s "http://192.168.68.123:8123/api/error_log" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | \
  grep -i "lovelace\|dashboard\|frontend" | \
  tail -20

# Filter for specific error types
curl -s "http://192.168.68.123:8123/api/error_log" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | \
  grep -E "ERROR|CRITICAL" | \
  grep -i "entity"

# Get errors from last 5 minutes
curl -s "http://192.168.68.123:8123/api/error_log" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | \
  awk -v cutoff="$(date -u -d '5 minutes ago' '+%Y-%m-%d %H:%M')" \
    '$0 >= cutoff'
```

### Python Log Analysis

```python
import requests
import re
from datetime import datetime, timedelta


def analyze_logs_for_errors(
    component: str = "lovelace",
    since_minutes: int = 5
) -> list[dict]:
    """
    Analyze HA logs for errors in specific component.

    Args:
        component: Component to filter for (e.g., "lovelace", "frontend")
        since_minutes: Only return errors from last N minutes

    Returns:
        List of error dicts with timestamp, level, message
    """
    url = "http://192.168.68.123:8123/api/error_log"
    headers = {"Authorization": f"Bearer {os.environ['HA_LONG_LIVED_TOKEN']}"}

    response = requests.get(url, headers=headers, timeout=10)
    log_text = response.text

    # Parse log entries
    errors = []
    cutoff_time = datetime.utcnow() - timedelta(minutes=since_minutes)

    # Pattern: YYYY-MM-DD HH:MM:SS LEVEL (component) Message
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (ERROR|WARNING|CRITICAL) \(([^)]+)\) (.*)'

    for match in re.finditer(pattern, log_text):
        timestamp_str, level, comp, message = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

        # Filter by time and component
        if timestamp >= cutoff_time and component.lower() in comp.lower():
            errors.append({
                "timestamp": timestamp_str,
                "level": level,
                "component": comp,
                "message": message.strip()
            })

    return errors


# Usage
recent_errors = analyze_logs_for_errors("lovelace", since_minutes=5)
if recent_errors:
    print("Recent errors detected:")
    for error in recent_errors:
        print(f"  [{error['timestamp']}] {error['level']}: {error['message']}")
else:
    print("No recent errors")
```

## Error Pattern Reference

### Common Error Messages

| Error Message | Meaning | Validation Check |
|---------------|---------|------------------|
| `Custom element doesn't exist: custom:*-card` | HACS card not installed | HACS card verification |
| `Entity not available: sensor.*` | Entity offline or doesn't exist | Entity existence check |
| `Error while loading page lovelace` | Config syntax error | Config structure validation |
| `Invalid configuration for card` | Missing required card fields | Card field validation |
| `Failed to load resource: /local/*` | Custom resource file missing | Resource file check |
| `Cannot read property 'state' of undefined` | Entity ID mismatch in JS | Entity ID validation |
| `WebSocket connection failed` | Network/auth issue | Connection test |

### Error Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **DEBUG** | Diagnostic information | Ignore unless debugging |
| **INFO** | Normal operations | Ignore |
| **WARNING** | Potential issues | Review, may need fixing |
| **ERROR** | Component failures | Fix immediately |
| **CRITICAL** | System failures | Fix urgently |

## Validation Checklist

Pre-deployment checklist for dashboard changes:

- [ ] **Config structure** - All required fields present (`views`, `title`, `cards`)
- [ ] **Entity IDs** - All referenced entities exist in HA
- [ ] **HACS cards** - All custom cards installed and loaded
- [ ] **Card types** - All card types are valid (no typos)
- [ ] **Syntax** - JSON structure is valid (no trailing commas, missing brackets)
- [ ] **Log baseline** - Captured pre-deployment error log
- [ ] **Test dashboard** - Changes tested on test-dashboard first
- [ ] **Backup config** - Current config backed up for rollback
- [ ] **Visual check** - Dashboard rendered correctly in browser
- [ ] **Console clean** - No JavaScript errors in browser console
- [ ] **Network requests** - All API calls successful (no 404s)
- [ ] **Post-deployment logs** - No new errors after deployment
