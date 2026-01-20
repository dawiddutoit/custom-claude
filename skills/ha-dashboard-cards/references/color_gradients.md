# Color Gradients for Dashboard Cards

## Overview

Color gradients provide visual feedback on sensor values by changing graph colors based on thresholds. This makes it easy to spot when values enter warning zones (too hot, too cold, poor air quality, etc.).

## How Color Thresholds Work

`mini-graph-card` supports `color_thresholds` to change line color based on the current value:

```yaml
color_thresholds:
  - value: 0
    color: '#3498db'  # Blue: Cold
  - value: 20
    color: '#2ecc71'  # Green: Comfortable
  - value: 30
    color: '#e74c3c'  # Red: Hot
```

**Behavior:**
- When sensor value is 0-19.9: Blue
- When sensor value is 20-29.9: Green
- When sensor value is 30+: Red

The graph line changes color dynamically as values cross thresholds.

## Important: Entity Colors vs Color Thresholds

**Entity colors override color thresholds.** If you define both, the entity color wins.

**Wrong:**
```yaml
color_thresholds:
  - value: 0
    color: '#3498db'
  - value: 20
    color: '#2ecc71'
entities:
  - entity: sensor.temperature
    color: '#ff0000'  # This overrides the gradient!
```

**Correct:**
```yaml
color_thresholds:
  - value: 0
    color: '#3498db'
  - value: 20
    color: '#2ecc71'
entities:
  - entity: sensor.temperature
    # No color property - gradient will work
```

The `add_color_gradient_to_mini_graph()` utility automatically removes entity colors.

## Recommended Color Palettes

### Temperature (Cold → Comfortable → Warm → Hot)

```python
thresholds = [
    {"value": 10, "color": "#3498db"},   # Cold: Blue
    {"value": 18, "color": "#2ecc71"},   # Comfortable: Green
    {"value": 26, "color": "#f1c40f"},   # Warm: Yellow
    {"value": 32, "color": "#e74c3c"},   # Hot: Red
]
```

**Visual representation:**
```
0°C          10°C         18°C         26°C         32°C
|------------|------------|------------|------------|
   Blue         Blue        Green       Yellow       Red
```

### Humidity (Dry → Comfortable → High)

```python
thresholds = [
    {"value": 0, "color": "#e74c3c"},    # Dry: Red
    {"value": 30, "color": "#2ecc71"},   # Low: Green
    {"value": 60, "color": "#f1c40f"},   # Comfortable: Yellow
    {"value": 80, "color": "#e74c3c"},   # High: Red
]
```

**Visual representation:**
```
0%           30%          60%          80%
|------------|------------|------------|
   Red        Green       Yellow       Red
```

### Air Quality - Oxidising Gas (Lower = Worse)

For sensors where **lower resistance = more pollution**:

```python
thresholds = [
    {"value": 0, "color": "#e74c3c"},     # Poor: Red
    {"value": 10, "color": "#e67e22"},    # Moderate: Orange
    {"value": 30, "color": "#2ecc71"},    # Good: Green
    {"value": 100, "color": "#3498db"},   # Excellent: Blue
]
```

**Visual representation:**
```
0 kΩ         10 kΩ        30 kΩ        100 kΩ
|------------|------------|------------|
   Red        Orange       Green        Blue
```

### Air Quality - Reducing Gas (Lower = Worse)

```python
thresholds = [
    {"value": 0, "color": "#e74c3c"},     # Poor: Red
    {"value": 100, "color": "#e67e22"},   # Moderate: Orange
    {"value": 200, "color": "#2ecc71"},   # Good: Green
    {"value": 500, "color": "#3498db"},   # Excellent: Blue
]
```

### Battery Level (High → Medium → Low → Critical)

```python
thresholds = [
    {"value": 0, "color": "#e74c3c"},     # Critical: Red
    {"value": 20, "color": "#e67e22"},    # Low: Orange
    {"value": 50, "color": "#f1c40f"},    # Medium: Yellow
    {"value": 80, "color": "#2ecc71"},    # Good: Green
]
```

## Color Palette Reference

### Standard Colors

| Color | Hex | Use Case |
|-------|-----|----------|
| Blue | `#3498db` | Cold, Excellent air quality, Water |
| Green | `#2ecc71` | Comfortable, Good, Normal |
| Yellow | `#f1c40f` | Warm, Caution, Moderate |
| Orange | `#e67e22` | Warning, Moderate pollution |
| Red | `#e74c3c` | Hot, Danger, Poor, Critical |

### Extended Palette

| Color | Hex | Use Case |
|-------|-----|----------|
| Purple | `#9b59b6` | Night mode, Humidity variations |
| Teal | `#1abc9c` | Secondary comfortable range |
| Dark Blue | `#2c3e50` | Very cold |
| Light Red | `#e57373` | Slightly elevated |
| Dark Red | `#c0392b` | Extreme danger |

## Custom Threshold Examples

### Freezer Temperature (-20°C to 0°C)

```python
thresholds = [
    {"value": -20, "color": "#3498db"},   # Optimal: Blue
    {"value": -10, "color": "#2ecc71"},   # Good: Green
    {"value": -5, "color": "#f1c40f"},    # Warning: Yellow
    {"value": 0, "color": "#e74c3c"},     # Danger: Red
]
```

### Power Consumption (0W to 3000W)

```python
thresholds = [
    {"value": 0, "color": "#2ecc71"},     # Low: Green
    {"value": 1000, "color": "#f1c40f"},  # Moderate: Yellow
    {"value": 2000, "color": "#e67e22"},  # High: Orange
    {"value": 2500, "color": "#e74c3c"},  # Very High: Red
]
```

### Soil Moisture (0% to 100%)

```python
thresholds = [
    {"value": 0, "color": "#e74c3c"},     # Dry: Red
    {"value": 20, "color": "#f1c40f"},    # Low: Yellow
    {"value": 40, "color": "#2ecc71"},    # Optimal: Green
    {"value": 80, "color": "#3498db"},    # Wet: Blue
    {"value": 90, "color": "#9b59b6"},    # Saturated: Purple
]
```

## Python Implementation

### Using Presets

```python
from ha_card_utils import COLOR_SCHEMES, add_color_gradient_to_mini_graph

# Use preset color scheme
temp_thresholds = [
    COLOR_SCHEMES["temperature"]["cold"],
    COLOR_SCHEMES["temperature"]["comfortable"],
    COLOR_SCHEMES["temperature"]["warm"],
    COLOR_SCHEMES["temperature"]["hot"],
]

card = {
    "type": "custom:mini-graph-card",
    "name": "Temperature",
    "entities": [{"entity": "sensor.temperature"}],
}

add_color_gradient_to_mini_graph(card, temp_thresholds)
```

### Custom Thresholds

```python
from ha_card_utils import add_color_gradient_to_mini_graph

# Define custom thresholds
custom_thresholds = [
    {"value": 15, "color": "#3498db"},   # Custom cold threshold
    {"value": 22, "color": "#2ecc71"},   # Custom comfortable
    {"value": 28, "color": "#e74c3c"},   # Custom hot
]

card = {
    "type": "custom:mini-graph-card",
    "name": "Temperature",
    "entities": [{"entity": "sensor.temperature"}],
}

add_color_gradient_to_mini_graph(card, custom_thresholds)
```

## YAML Implementation

```yaml
type: custom:mini-graph-card
name: Temperature Trend
hours_to_show: 24
color_thresholds:
  - value: 10
    color: '#3498db'
  - value: 18
    color: '#2ecc71'
  - value: 26
    color: '#f1c40f'
  - value: 32
    color: '#e74c3c'
entities:
  - entity: sensor.office_temperature
    # No color property - let gradient work
```

## Best Practices

1. **Use 3-5 thresholds** - Too few lacks nuance, too many is confusing
2. **Order matters** - Always order thresholds from lowest to highest value
3. **Start at sensor minimum** - First threshold should be at or below sensor's lowest expected value
4. **Remove entity colors** - Always remove fixed colors when using gradients
5. **Test with real data** - Verify thresholds match actual sensor value ranges
6. **Be consistent** - Use the same color scheme across similar sensors
7. **Consider colorblind users** - Blue/yellow contrasts work better than red/green
8. **Document thresholds** - Add info cards explaining what colors mean

## Troubleshooting

### Issue: Gradient not visible

**Cause:** Entity color overrides gradient

**Fix:**
```python
# Remove entity colors
for entity in card.get("entities", []):
    if isinstance(entity, dict) and "color" in entity:
        del entity["color"]
```

### Issue: Wrong colors showing

**Cause:** Threshold order incorrect or values don't match sensor range

**Fix:** Check threshold values match sensor's actual min/max:
```python
# Print sensor state to verify range
curl -s "http://192.168.68.123:8123/api/states/sensor.temperature" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | jq '.state'
```

### Issue: Sudden color changes look jarring

**Solution:** Add intermediate thresholds for smoother transitions:
```python
# Before (2 thresholds - abrupt change)
thresholds = [
    {"value": 0, "color": "#3498db"},
    {"value": 30, "color": "#e74c3c"},
]

# After (4 thresholds - gradual change)
thresholds = [
    {"value": 0, "color": "#3498db"},
    {"value": 15, "color": "#2ecc71"},
    {"value": 25, "color": "#f1c40f"},
    {"value": 30, "color": "#e74c3c"},
]
```

## Accessibility Considerations

### Colorblind-Friendly Palettes

**Deuteranopia (Red-Green Colorblindness) - Most Common:**
```python
# Use Blue-Orange-Purple instead of Blue-Green-Red
thresholds = [
    {"value": 0, "color": "#3498db"},    # Blue
    {"value": 20, "color": "#f39c12"},   # Orange
    {"value": 30, "color": "#9b59b6"},   # Purple
]
```

**Protanopia (Red Colorblindness):**
```python
# Use Blue-Yellow-Brown
thresholds = [
    {"value": 0, "color": "#3498db"},    # Blue
    {"value": 20, "color": "#f1c40f"},   # Yellow
    {"value": 30, "color": "#795548"},   # Brown
]
```

### Always Include Text Indicators

Don't rely solely on color - also use:
- Info cards explaining threshold meanings
- Entity state values (current temperature)
- Extrema markers (`show: {extrema: true}`)

## Performance Notes

- **Threshold count:** No performance impact up to 10 thresholds
- **Color transitions:** Handled by browser, no JS overhead
- **Memory usage:** ~50 bytes per threshold
- **Render time:** < 1ms per graph with gradients
