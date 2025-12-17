# Custom Cards Reference

Technical depth for HACS custom card configurations and advanced patterns.

## Color Schemes

### Environmental Gauges

```yaml
# Temperature (10-40°C)
segments:
  - from: 10
    color: "#3498db"    # Blue (cold)
  - from: 18
    color: "#2ecc71"    # Green (comfortable)
  - from: 26
    color: "#f1c40f"    # Yellow (warm)
  - from: 32
    color: "#e74c3c"    # Red (hot)

# Humidity (0-100%)
segments:
  - from: 0
    color: "#e74c3c"    # Red (too dry)
  - from: 30
    color: "#f1c40f"    # Yellow (dry)
  - from: 40
    color: "#2ecc71"    # Green (comfortable)
  - from: 60
    color: "#f1c40f"    # Yellow (humid)
  - from: 70
    color: "#e74c3c"    # Red (too humid)

# PM2.5 Air Quality (0-100 µg/m³)
segments:
  - from: 0
    color: "#2ecc71"    # Green (good)
  - from: 12
    color: "#f1c40f"    # Yellow (moderate)
  - from: 35
    color: "#e67e22"    # Orange (unhealthy for sensitive)
  - from: 55
    color: "#e74c3c"    # Red (unhealthy)
```

## HACS Installation

### Via WebSocket API (VALIDATED)

```python
import json
import websocket

ws_url = "ws://192.168.68.123:8123/api/websocket"
ws = websocket.create_connection(ws_url)

# 1. Receive auth_required
ws.recv()

# 2. Send auth
ws.send(json.dumps({
    "type": "auth",
    "access_token": os.environ["HA_LONG_LIVED_TOKEN"]
}))
ws.recv()  # auth_ok

# 3. Install card by repository ID
ws.send(json.dumps({
    "id": 1,
    "type": "hacs/repository/download",
    "repository": 151280062,  # mini-graph-card
}))
response = json.loads(ws.recv())

ws.close()
```

**Repository IDs for programmatic installation:**
- mini-graph-card: 151280062
- bubble-card: 680112919
- modern-circular-gauge: 871730343
- lovelace-mushroom: 444350375
- apexcharts-card: 331701152

### Via UI

1. Open HACS → Frontend
2. Search for card name
3. Click Download
4. Restart Home Assistant

## ApexCharts Advanced Features

### Valid Span Configuration (VALIDATED)

**CRITICAL:** Always use one of these valid values for `span.end`:

```yaml
span:
  end: minute   # Start of current minute
  end: hour     # Start of current hour
  end: day      # Start of current day
  end: week     # Start of current week
  end: month    # Start of current month
  end: year     # Start of current year
  end: isoWeek  # Start of ISO week (Monday)
```

**Never use:** `"now"` or other string values - these cause errors.

### Dual Y-Axis

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Temperature & Humidity
graph_span: 24h
span:
  end: hour
yaxis:
  - id: temp
    min: 0
    max: 50
    decimals: 1
  - id: humidity
    opposite: true
    min: 0
    max: 100
series:
  - entity: sensor.temperature
    name: Temperature
    yaxis_id: temp
    color: "#e74c3c"
    stroke_width: 2
  - entity: sensor.humidity
    name: Humidity
    yaxis_id: humidity
    color: "#3498db"
    stroke_width: 2
```

### Annotations (Sunrise/Sunset)

**WARNING:** JavaScript template annotations may cause errors. Use with caution.

```yaml
apex_config:
  annotations:
    xaxis:
      - x: "${ new Date(states['sun.sun'].attributes.next_rising).getTime() }"
        borderColor: "#FFA500"
        label:
          text: Sunrise
          style:
            background: "#FFA500"
```

**Note:** If annotations cause configuration errors, remove them or use static timestamps instead.

### Time Formatting

```yaml
apex_config:
  xaxis:
    type: datetime
    labels:
      datetimeFormatter:
        hour: "HH:mm"
        day: "dd MMM"
```

## Error Checking

### Check for Dashboard Errors via API

```python
# 1. Check system logs for lovelace errors
ws.send(json.dumps({"id": 1, "type": "system_log/list"}))
logs = json.loads(ws.recv())
# Filter for 'lovelace' or 'frontend' errors

# 2. Validate dashboard configuration
ws.send(json.dumps({
    "id": 2,
    "type": "lovelace/config",
    "url_path": "dashboard-name"
}))
config = json.loads(ws.recv())

# 3. Validate entity IDs exist
ws.send(json.dumps({"id": 3, "type": "get_states"}))
states = json.loads(ws.recv())
entity_ids = [s["entity_id"] for s in states["result"]]
```

### Common Error Patterns

1. **ApexCharts span error**: Check `span.end` uses valid value (hour/day/week/month/year)
2. **Entity not found**: Verify entity exists in Developer Tools → States
3. **Card not loading**: Check HACS installation and browser console (F12)
4. **JavaScript template error**: Remove or simplify template annotations

## Best Practices

1. **Use meaningful colors**: Red for warnings/hot, blue for cold/water, green for normal
2. **Test incrementally**: Add cards one at a time and validate
3. **Check browser console**: View errors in browser console (F12)
4. **Validate entities**: Ensure entity IDs exist before using in cards
5. **Restart HA after HACS install**: Custom cards require restart to activate

## Troubleshooting

### Card Not Loading

- Verify HACS installation (Frontend category)
- Clear browser cache (Ctrl+Shift+R)
- Check Lovelace resources
- View browser console for errors (F12)

### JavaScript Template Errors

If annotations cause errors:
- Remove apex_config.annotations section
- Use static timestamps instead of JavaScript templates
- Check browser console for specific error messages

### Gauge Not Showing Values

- Verify entity exists (Developer Tools → States)
- Check entity has numeric state value
- Ensure min/max values are appropriate for sensor range

## Official Documentation

- [Mini-Graph-Card GitHub](https://github.com/kalkih/mini-graph-card)
- [ApexCharts Card GitHub](https://github.com/RomRider/apexcharts-card)
- [Bubble Card GitHub](https://github.com/Clooos/Bubble-Card)
- [Modern Circular Gauge GitHub](https://github.com/sdelliot/lovelace-modern-circular-gauge)
- [Mushroom Cards GitHub](https://github.com/piitaya/lovelace-mushroom)
