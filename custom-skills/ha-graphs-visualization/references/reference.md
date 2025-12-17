# Graph Configuration Reference

Technical depth, advanced patterns, and performance optimization for Home Assistant graphs.

## Performance Optimization

### 1. Reduce Data Point Density

```yaml
# Mini-graph-card
type: custom:mini-graph-card
entities:
  - sensor.temperature
hours_to_show: 24
points_per_hour: 1  # Lower = faster (default: 2)
```

### 2. Use Statistics for Long Time Ranges

```yaml
# For graphs >48 hours, use statistics-graph
type: statistics-graph
entities:
  - sensor.temperature
stat_types:
  - mean
period:
  calendar:
    period: month
```

### 3. Avoid Complex Data Generators

```yaml
# ApexCharts - avoid data_generator on high-traffic views
# Use native series configuration instead
series:
  - entity: sensor.power_consumption
    # Avoid: data_generator: |
```

### 4. Limit Graph Count Per View

- Maximum 3-4 complex graphs per dashboard view
- Use conditional cards to lazy-load heavy graphs
- Consider separate views for detailed analytics

## ApexCharts Advanced Configuration

### Valid Span End Values (CRITICAL)

**Always use one of these valid values for `span.end`:**

```yaml
span:
  end: minute   # Start of current minute
  end: hour     # Start of current hour (RECOMMENDED)
  end: day      # Start of current day
  end: week     # Start of current week
  end: month    # Start of current month
  end: year     # Start of current year
  end: isoWeek  # Start of ISO week (Monday)
```

**Never use:** `"now"` or other string values - these cause errors.

### Time Range Configuration (VALIDATED)

```yaml
# Simple duration
graph_span: 24h      # Last 24 hours
graph_span: 7d       # Last 7 days
graph_span: 1h25     # Last 1 hour 25 minutes

# Precise control with start/end
span:
  start: day         # Start of current day
  end: hour          # MUST be: minute/hour/day/week/month/year/isoWeek
  offset: -7d        # 7 days ago

# Common valid end values
end: minute        # Start of current minute
end: hour          # Start of current hour
end: day           # Start of current day (midnight)
end: week          # Start of current week (Monday)
end: month         # Start of current month
end: year          # Start of current year
end: isoWeek       # Start of ISO week (Monday)
```

### Data Aggregation

```yaml
type: custom:apexcharts-card
graph_span: 30d
span:
  end: day
series:
  - entity: sensor.temperature
    group_by:
      func: avg       # avg, min, max, sum, median, last
      duration: 1h    # Group data into 1-hour buckets
```

## Mini-Graph-Card Configuration Options

```yaml
type: custom:mini-graph-card
entities:
  - sensor.temperature
hours_to_show: 24         # Time window
points_per_hour: 2        # Data point density (lower = faster)
line_width: 2             # Line thickness
font_size: 75             # Text size (%)
animate: true             # Animated transitions
smoothing: true           # Smooth line curves
show:
  name: true              # Show card title
  icon: true              # Show entity icon
  state: true             # Show current value
  graph: line             # Graph type (line/bar)
  labels: true            # Y-axis labels
  labels_secondary: true  # Secondary Y-axis labels
  points: false           # Show data points
  legend: true            # Show legend
  fill: fade              # Fill area under line (false/fade/solid)
```

### Color Thresholds

```yaml
type: custom:mini-graph-card
entities:
  - sensor.temperature
color_thresholds:
  - value: 0
    color: '#0066ff'  # Blue (cold)
  - value: 18
    color: '#00ff00'  # Green (comfortable)
  - value: 25
    color: '#ffaa00'  # Orange (warm)
  - value: 30
    color: '#ff0000'  # Red (hot)
color_thresholds_transition: smooth
line_width: 3
points_per_hour: 4
```

### Sparkline (No Axes)

```yaml
type: custom:mini-graph-card
entities:
  - sensor.temperature
hours_to_show: 12
line_width: 2
show:
  name: false
  icon: false
  state: true
  graph: line
  labels: false
  points: false
```

## Statistics Graph Configuration

### Stat Types

| Stat Type | Description | Use Case |
|-----------|-------------|----------|
| `mean` | Average value | Temperature trends |
| `min` | Minimum value | Lowest temp of day |
| `max` | Maximum value | Peak power usage |
| `sum` | Total (for metered entities) | Daily energy consumption |
| `change` | Difference first/last | Net change over period |

### Period Options

- `hour`: Hourly statistics
- `day`: Daily rollup
- `week`: Weekly rollup
- `month`: Monthly rollup
- Custom calendar periods

### Daily Energy Usage

```yaml
type: statistics-graph
title: Energy Usage (This Month)
entities:
  - sensor.power_consumption
stat_types:
  - sum
period:
  calendar:
    period: month
chart_type: bar
```

## Best Practices

### 1. Choose the Right Graph Type

- **Line**: Continuous data (temperature, humidity)
- **Bar/Column**: Discrete data (daily energy, events)
- **Area**: Cumulative data (solar production, rainfall)

### 2. Use Meaningful Colors

- Red: High temperatures, alerts, energy consumption
- Blue: Low temperatures, water, humidity
- Green: Normal values, success, efficiency
- Orange: Warnings, moderate values

### 3. Label Your Axes

```yaml
yaxis:
  - id: temp
    decimals: 1
    min: 0
    max: 50
```

### 4. Show Current State

```yaml
header:
  show_states: true  # Shows current value in header
```

### 5. Use Appropriate Time Ranges

- Real-time monitoring: 1-6 hours
- Daily patterns: 24 hours
- Weekly trends: 7 days
- Monthly analysis: 30 days
- Long-term: statistics-graph

## Troubleshooting

### No Data Showing

- Verify entity exists (Developer Tools → States)
- Check recorder retention period
- Ensure sensor has `state_class: measurement`
- Check long-term statistics (Developer Tools → Statistics)

### Graph Performance Slow

- Reduce `points_per_hour` (mini-graph-card)
- Shorten `graph_span` or `hours_to_show`
- Use statistics-graph for long ranges
- Limit number of series

### Thin/Bold Line Mix (History Graph)

- Bold = recorder data (recent)
- Thin = long-term statistics (old data)
- This is expected behavior when `hours_to_show` exceeds recorder retention

### Custom Card Not Loading

- Verify HACS installation (Frontend category)
- Clear browser cache (Ctrl+Shift+R)
- Check Lovelace resources
- View browser console for errors (F12)

### ApexCharts Span Error

**Error:** `"Invalid value for span.end"`

**Solution:** Change `span.end` to one of: minute, hour, day, week, month, year, isoWeek

```yaml
# WRONG
span:
  end: now  # ❌ Causes error

# CORRECT
span:
  end: hour  # ✅ Valid value
```

## Official Documentation

- [History graph card - Home Assistant](https://www.home-assistant.io/dashboards/history-graph)
- [Statistics graph card - Home Assistant](https://www.home-assistant.io/dashboards/statistics-graph)
- [Mini-Graph-Card GitHub](https://github.com/kalkih/mini-graph-card)
- [ApexCharts Card GitHub](https://github.com/RomRider/apexcharts-card)
