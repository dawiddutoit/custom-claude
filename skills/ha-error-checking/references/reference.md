# Error Checking Reference

Technical depth for Home Assistant error checking patterns and troubleshooting.

## Common Error Log Patterns

| Error Pattern | Meaning | Solution |
|---------------|---------|----------|
| `"Invalid value for span.end"` | ApexCharts span config wrong | Use hour/day/week/month/year |
| `"Custom element doesn't exist"` | HACS card not installed | Install via HACS |
| `"Entity not found"` | Entity ID doesn't exist | Check entity ID in Developer Tools |
| `"Unexpected token"` | YAML syntax error | Validate YAML structure |
| `"Failed to call service"` | Service call error | Check service exists and parameters |

## Known Entity ID Patterns (from HA Instance)

```python
# Enviro+ environmental sensors
ENVIRO_SENSORS = [
    "sensor.enviro_sensor_temperature",
    "sensor.enviro_sensor_humidity",
    "sensor.enviro_sensor_pressure",
    "sensor.enviro_sensor_light",
    "sensor.enviro_sensor_pm1_0",
    "sensor.enviro_sensor_pm2_5",
    "sensor.enviro_sensor_pm10",
    "sensor.enviro_sensor_gas_oxidising",
    "sensor.enviro_sensor_gas_reducing",
    "sensor.enviro_sensor_gas_nh3",
]

# Office H&T sensor
OFFICE_SENSORS = [
    "sensor.officeht_temperature",
    "sensor.officeht_humidity",
    "sensor.officeht_battery",
]

# Climate devices (LG ThinQ ACs)
CLIMATE_DEVICES = [
    "climate.snorlug",
    "climate.val_hella_wam",
    "climate.mines_of_moria",
]

# Shelly power monitoring (pattern matching)
SHELLY_POWER_PATTERNS = [
    "sensor.shellyplus1pm_*_switch_0_power",
    "sensor.shellyswitch25_*_channel_1_power",
]
```

## HACS Repository IDs

**For programmatic installation:**

```python
HACS_CARDS = {
    "mini-graph-card": 151280062,
    "bubble-card": 680112919,
    "modern-circular-gauge": 871730343,
    "lovelace-mushroom": 444350375,
    "apexcharts-card": 331701152,
}
```

## Common Error Solutions

### 1. ApexCharts Span Error

**Error:** `"Invalid value for span.end: now"`

**Cause:** Using `"span": {"end": "now"}` instead of valid values

**Solution:**
```python
# WRONG
card = {
    "type": "custom:apexcharts-card",
    "span": {"end": "now"}  # ❌
}

# CORRECT
card = {
    "type": "custom:apexcharts-card",
    "span": {"end": "hour"}  # ✅
}
```

### 2. Dashboard URL Path Missing Hyphen

**Error:** Dashboard doesn't appear in sidebar

**Cause:** URL path doesn't contain hyphen (e.g., "climate" instead of "climate-control")

**Solution:**
```python
# WRONG
url_path = "climate"  # ❌

# CORRECT
url_path = "climate-control"  # ✅
```

### 3. Entity Not Found

**Error:** `"Entity not found: sensor.temperature"`

**Cause:** Entity ID doesn't exist or is misspelled

**Solution:**
```python
# Check entity exists
all_entities = get_all_entity_ids(ws)
if "sensor.temperature" not in all_entities:
    print("Entity not found - check spelling in Developer Tools → States")

    # Find similar entities
    similar = [e for e in all_entities if "temperature" in e]
    print(f"Did you mean: {similar}")
```

### 4. Custom Card Not Loading

**Error:** `"Custom element doesn't exist: apexcharts-card"`

**Cause:** HACS card not installed

**Solution:**
```python
# Check installation
if not check_hacs_card_installed(ws, HACS_CARDS["apexcharts-card"]):
    print("Installing ApexCharts...")
    install_hacs_card(ws, HACS_CARDS["apexcharts-card"])
    print("Restart Home Assistant to activate")
```

### 5. JavaScript Template Errors

**Error:** Annotations cause configuration parse errors

**Cause:** JavaScript template syntax like `${ new Date(...) }` may fail

**Solution:**
```python
# If annotations cause errors, remove them
apexcharts_config = {
    "type": "custom:apexcharts-card",
    # Remove apex_config.annotations section
    "series": [...]
}
```

## WebSocket API Error Handling

### Connection Errors

```python
import websocket
import json

try:
    ws_url = "ws://192.168.68.123:8123/api/websocket"
    ws = websocket.create_connection(ws_url, timeout=5)
except websocket.WebSocketTimeoutException:
    print("Connection timeout - check HA is running")
except ConnectionRefusedError:
    print("Connection refused - check HA URL and port")
```

### Authentication Errors

```python
# Send auth
ws.send(json.dumps({
    "type": "auth",
    "access_token": token
}))

auth_response = json.loads(ws.recv())
if auth_response.get("type") == "auth_invalid":
    print("Authentication failed - check token")
elif auth_response.get("type") == "auth_ok":
    print("Authenticated successfully")
```

### API Call Errors

```python
ws.send(json.dumps({
    "id": 1,
    "type": "lovelace/config",
    "url_path": "invalid-path"
}))

response = json.loads(ws.recv())
if "error" in response:
    error = response["error"]
    print(f"API Error: {error['code']} - {error['message']}")
```

## Browser Console Debugging

For frontend errors, check browser console (F12):

```javascript
// Common patterns to search for in browser console:

// 1. ApexCharts errors
// Look for: "Invalid configuration"

// 2. Custom card not loading
// Look for: "Custom element doesn't exist"

// 3. Entity not found
// Look for: "Entity not available"

// 4. JavaScript errors
// Look for: "Uncaught" or "SyntaxError"
```

## Best Practices

1. **Always validate before saving**: Check entities exist before adding to dashboard
2. **Check URL path format**: Ensure hyphen in dashboard URL path
3. **Validate custom cards**: Verify HACS cards installed before use
4. **Check system logs**: Review logs after dashboard updates
5. **Use valid values**: ApexCharts span.end must use valid enum values
6. **Test incrementally**: Add cards one at a time and validate

## Troubleshooting Checklist

- [ ] Dashboard URL path contains hyphen
- [ ] All entity IDs exist in HA
- [ ] Custom cards installed via HACS
- [ ] ApexCharts span.end uses valid value (hour/day/week/month/year)
- [ ] No system log errors for lovelace/frontend
- [ ] Browser console shows no errors (F12)
- [ ] Dashboard config is valid JSON/YAML
- [ ] Entity `state_class` set correctly for sensors

## Resources

- Developer Tools → States (check entity IDs)
- Developer Tools → Statistics (check long-term stats)
- HACS → Frontend (install/update custom cards)
- Browser Console (F12) (frontend errors)
- System Logs (Settings → System → Logs)
