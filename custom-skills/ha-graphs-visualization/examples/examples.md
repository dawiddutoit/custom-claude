# Graph Examples

Comprehensive, copy-paste-ready examples for Home Assistant graph configurations.

## Climate Dashboard (Temperature + Humidity) - VALIDATED

```yaml
type: vertical-stack
cards:
  # Current values
  - type: grid
    columns: 2
    cards:
      - type: sensor
        entity: sensor.temperature
        name: Temperature
        graph: line
      - type: sensor
        entity: sensor.humidity
        name: Humidity
        graph: line

  # 24-hour history
  - type: custom:apexcharts-card
    header:
      show: true
      title: 24 Hour History
      show_states: true
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
        color: '#e74c3c'
        stroke_width: 2
      - entity: sensor.humidity
        name: Humidity
        yaxis_id: humidity
        color: '#3498db'
        stroke_width: 2
```

## Air Quality Monitoring (Enviro+ Sensors)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Air Quality (24h)
  show_states: true
graph_span: 24h
span:
  end: hour
yaxis:
  - min: 0
    max: 100
    decimals: 1
series:
  - entity: sensor.enviro_pm1_0
    name: PM1.0
    color: '#3498db'
    stroke_width: 2
  - entity: sensor.enviro_pm2_5
    name: PM2.5
    color: '#e67e22'
    stroke_width: 2
  - entity: sensor.enviro_pm10
    name: PM10
    color: '#e74c3c'
    stroke_width: 2
```

## Energy Usage (Bar Chart)

```yaml
type: custom:apexcharts-card
header:
  title: Energy Usage (7 Days)
graph_span: 7d
span:
  end: day
series:
  - entity: sensor.daily_energy
    type: column
    color: '#2ecc71'
    group_by:
      func: sum
      duration: 1d
```

## Multi-Room Temperature Comparison

```yaml
type: custom:mini-graph-card
name: Temperature Comparison
entities:
  - entity: sensor.temperature_bedroom
    name: Bedroom
    color: '#e74c3c'
  - entity: sensor.temperature_living_room
    name: Living Room
    color: '#3498db'
  - entity: sensor.temperature_office
    name: Office
    color: '#2ecc71'
hours_to_show: 24
points_per_hour: 2
line_width: 2
show:
  legend: true
  labels: true
  state: true
```

## Comparison Chart (This Week vs Last Week)

```yaml
type: custom:apexcharts-card
header:
  title: This Week vs Last Week
graph_span: 7d
span:
  end: day
series:
  - entity: sensor.energy_daily
    name: This Week
    offset: 0d
  - entity: sensor.energy_daily
    name: Last Week
    offset: -7d
    color: gray
    opacity: 0.5
```

## Bar Chart with Aggregation

```yaml
type: custom:apexcharts-card
header:
  title: Energy Usage (30 Days)
graph_span: 30d
span:
  end: day
series:
  - entity: sensor.power_consumption
    type: column
    color: '#2ecc71'
    group_by:
      func: sum
      duration: 1d
```

## Annotations (Sunrise/Sunset)

**WARNING:** JavaScript template annotations may cause errors. Use with caution.

```yaml
type: custom:apexcharts-card
header:
  title: 24 Hour History
graph_span: 24h
span:
  end: hour
apex_config:
  annotations:
    xaxis:
      - x: "${ new Date(states['sun.sun'].attributes.next_rising).getTime() }"
        borderColor: '#FFA500'
        label:
          text: Sunrise
          style:
            color: '#fff'
            background: '#FFA500'
      - x: "${ new Date(states['sun.sun'].attributes.next_setting).getTime() }"
        borderColor: '#4169E1'
        label:
          text: Sunset
          style:
            color: '#fff'
            background: '#4169E1'
series:
  - entity: sensor.temperature
    stroke_width: 2
```

**Note:** If JavaScript annotations cause configuration errors, remove them or use static timestamps instead.

## Area Chart with Fill

```yaml
type: custom:apexcharts-card
graph_span: 24h
span:
  end: hour
series:
  - entity: sensor.solar_production
    type: area
    curve: smooth
    opacity: 0.3
    color: '#f1c40f'
    stroke_width: 2
```
