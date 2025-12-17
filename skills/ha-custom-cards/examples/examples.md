# Custom Cards Examples

Comprehensive examples for HACS custom card configurations.

## Environmental Dashboard Section

```yaml
type: vertical-stack
cards:
  # Separator
  - type: custom:bubble-card
    card_type: separator
    name: Environment
    icon: mdi:home-thermometer

  # Gauges
  - type: grid
    columns: 3
    cards:
      - type: custom:modern-circular-gauge
        entity: sensor.officeht_temperature
        name: Temperature
        min: 10
        max: 40
        needle: true
        segments:
          - from: 10
            color: "#3498db"
          - from: 18
            color: "#2ecc71"
          - from: 26
            color: "#f1c40f"
          - from: 32
            color: "#e74c3c"
      - type: custom:modern-circular-gauge
        entity: sensor.officeht_humidity
        name: Humidity
        min: 0
        max: 100
        needle: true
        segments:
          - from: 0
            color: "#e74c3c"
          - from: 30
            color: "#f1c40f"
          - from: 40
            color: "#2ecc71"
          - from: 60
            color: "#f1c40f"
          - from: 70
            color: "#e74c3c"
      - type: custom:modern-circular-gauge
        entity: sensor.enviro_pressure
        name: Pressure
        min: 980
        max: 1040
        needle: true

  # Time series graph
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
      - entity: sensor.officeht_temperature
        name: Temperature
        yaxis_id: temp
        color: "#e74c3c"
        stroke_width: 2
      - entity: sensor.officeht_humidity
        name: Humidity
        yaxis_id: humidity
        color: "#3498db"
        stroke_width: 2
```

## Grid Layout with Gauges

```yaml
type: grid
columns: 3
square: false
cards:
  - type: custom:modern-circular-gauge
    entity: sensor.officeht_temperature
    name: Temperature
    min: 10
    max: 40
    needle: true
    segments:
      - from: 10
        color: "#3498db"
      - from: 18
        color: "#2ecc71"
      - from: 26
        color: "#f1c40f"
      - from: 32
        color: "#e74c3c"
  - type: custom:modern-circular-gauge
    entity: sensor.officeht_humidity
    name: Humidity
    min: 0
    max: 100
    needle: true
    segments:
      - from: 0
        color: "#e74c3c"
      - from: 30
        color: "#f1c40f"
      - from: 40
        color: "#2ecc71"
      - from: 60
        color: "#f1c40f"
      - from: 70
        color: "#e74c3c"
```

## Mushroom Climate Card (VALIDATED)

```yaml
type: custom:mushroom-climate-card
entity: climate.ac_unit
name: AC Name
hvac_modes:
  - "off"
  - cool
  - heat
  - auto
show_temperature_control: true
collapsible_controls: true
```

## ApexCharts Dual Y-Axis

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

## ApexCharts Annotations (Sunrise/Sunset)

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
      - x: "${ new Date(states['sun.sun'].attributes.next_setting).getTime() }"
        borderColor: "#4169E1"
        label:
          text: Sunset
          style:
            background: "#4169E1"
```

**Note:** If annotations cause configuration errors, remove them or use static timestamps instead.

## ApexCharts Time Formatting

```yaml
apex_config:
  xaxis:
    type: datetime
    labels:
      datetimeFormatter:
        hour: "HH:mm"
        day: "dd MMM"
```

## Bubble Card Separator

```yaml
type: custom:bubble-card
card_type: separator
name: Section Name
icon: mdi:thermometer
```
