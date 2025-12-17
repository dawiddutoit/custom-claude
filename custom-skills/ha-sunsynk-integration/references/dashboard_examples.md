# Sunsynk Dashboard Examples

Complete dashboard configurations for various solar monitoring use cases.

All examples use serial number `2305178402` - replace with your inverter serial.

## Table of Contents

1. Complete Solar Dashboard
2. Energy Flow Visualization
3. Battery Monitoring Dashboard
4. Grid Import/Export Tracker
5. PV Production Analysis
6. System Health Monitor

## 1. Complete Solar Dashboard

Full-featured dashboard with all key metrics.

```yaml
title: Solar System
path: solar-system
icon: mdi:solar-power
type: sections
max_columns: 3

sections:
  # Status Bar
  - type: grid
    cards:
      - type: custom:bubble-card
        card_type: horizontal-buttons-stack
        name: System Status
        buttons:
          - entity: sensor.solarsynkv3_2305178402_overall_state
            name: Status
            icon: mdi:state-machine
          - entity: sensor.solarsynkv3_2305178402_pv_pac
            name: Solar
            icon: mdi:solar-power
          - entity: sensor.solarsynkv3_2305178402_battery_soc
            name: Battery
            icon: mdi:battery
          - entity: sensor.solarsynkv3_2305178402_grid_pac
            name: Grid
            icon: mdi:transmission-tower

  # Power Flow Gauges
  - type: grid
    title: Power Flow
    cards:
      - type: custom:modern-circular-gauge
        entity: sensor.solarsynkv3_2305178402_pv_pac
        name: Solar Production
        min: 0
        max: 8000
        unit: W
        needle: true
        segments:
          - from: 0
            color: "#95a5a6"
          - from: 1000
            color: "#f39c12"
          - from: 4000
            color: "#e74c3c"

      - type: custom:modern-circular-gauge
        entity: sensor.solarsynkv3_2305178402_battery_soc
        name: Battery
        min: 0
        max: 100
        unit: "%"
        needle: true
        segments:
          - from: 0
            color: "#e74c3c"
          - from: 30
            color: "#f39c12"
          - from: 70
            color: "#2ecc71"

      - type: custom:modern-circular-gauge
        entity: sensor.solarsynkv3_2305178402_load_total_power
        name: Load
        min: 0
        max: 5000
        unit: W
        needle: true
        segments:
          - from: 0
            color: "#2ecc71"
          - from: 2000
            color: "#f39c12"
          - from: 3500
            color: "#e74c3c"

  # 24-Hour Graphs
  - type: grid
    title: 24 Hour History
    cards:
      - type: custom:apexcharts-card
        header:
          show: true
          title: Power Flow
          show_states: true
        graph_span: 24h
        span:
          end: now
        yaxis:
          - id: power
            min: ~
            decimals: 0
            apex_config:
              title:
                text: Power (W)
        apex_config:
          chart:
            height: 250
          xaxis:
            type: datetime
        series:
          - entity: sensor.solarsynkv3_2305178402_pv_pac
            name: Solar
            color: "#f39c12"
            stroke_width: 2
            type: area
          - entity: sensor.solarsynkv3_2305178402_load_total_power
            name: Load
            color: "#3498db"
            stroke_width: 2
          - entity: sensor.solarsynkv3_2305178402_battery_power
            name: Battery
            color: "#2ecc71"
            stroke_width: 2

      - type: custom:apexcharts-card
        header:
          show: true
          title: Battery SOC
          show_states: true
        graph_span: 24h
        yaxis:
          - id: soc
            min: 0
            max: 100
            decimals: 0
            apex_config:
              title:
                text: SOC (%)
        apex_config:
          chart:
            height: 250
        series:
          - entity: sensor.solarsynkv3_2305178402_battery_soc
            name: SOC
            color: "#2ecc71"
            stroke_width: 2

  # Daily Energy
  - type: grid
    title: Today's Energy
    cards:
      - type: entities
        entities:
          - entity: sensor.solarsynkv3_2305178402_pv_etoday
            name: Solar Produced
            icon: mdi:solar-power
          - entity: sensor.solarsynkv3_2305178402_load_daily_used
            name: Load Consumed
            icon: mdi:home-lightning-bolt
          - entity: sensor.solarsynkv3_2305178402_battery_charge_today
            name: Battery Charged
            icon: mdi:battery-charging
          - entity: sensor.solarsynkv3_2305178402_battery_discharge_today
            name: Battery Discharged
            icon: mdi:battery-minus
          - entity: sensor.solarsynkv3_2305178402_grid_etoday_from
            name: Grid Import
            icon: mdi:transmission-tower-import
          - entity: sensor.solarsynkv3_2305178402_grid_etoday_to
            name: Grid Export
            icon: mdi:transmission-tower-export

  # System Details
  - type: grid
    title: System Details
    cards:
      - type: entities
        title: Battery
        entities:
          - sensor.solarsynkv3_2305178402_battery_voltage
          - sensor.solarsynkv3_2305178402_battery_current
          - sensor.solarsynkv3_2305178402_battery_temperature

      - type: entities
        title: Grid
        entities:
          - sensor.solarsynkv3_2305178402_grid_voltage
          - sensor.solarsynkv3_2305178402_grid_frequency
          - sensor.solarsynkv3_2305178402_grid_current

      - type: entities
        title: Inverter
        entities:
          - sensor.solarsynkv3_2305178402_inverter_ac_temperature
          - sensor.solarsynkv3_2305178402_inverter_dc_temperature
          - sensor.solarsynkv3_2305178402_inverter_status
```

## 2. Energy Flow Visualization

Sankey-style energy flow diagram using custom card.

**Prerequisites:** Install `energy-flow-card-plus` from HACS

```yaml
type: custom:energy-flow-card-plus
entities:
  grid:
    entity: sensor.solarsynkv3_2305178402_grid_pac
    name: Grid
    icon: mdi:transmission-tower
  solar:
    entity: sensor.solarsynkv3_2305178402_pv_pac
    name: Solar
    icon: mdi:solar-power
  battery:
    entity: sensor.solarsynkv3_2305178402_battery_power
    name: Battery
    icon: mdi:battery
  home:
    entity: sensor.solarsynkv3_2305178402_load_total_power
    name: Home
    icon: mdi:home
inverted_entities:
  - sensor.solarsynkv3_2305178402_grid_pac  # Negative = export
  - sensor.solarsynkv3_2305178402_battery_power  # Negative = charging
display_zero_state: true
```

## 3. Battery Monitoring Dashboard

Detailed battery health and performance monitoring.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    name: Battery Monitoring
    icon: mdi:battery

  # Battery Overview
  - type: grid
    columns: 2
    cards:
      - type: gauge
        entity: sensor.solarsynkv3_2305178402_battery_soc
        name: State of Charge
        min: 0
        max: 100
        needle: true
        severity:
          red: 0
          yellow: 30
          green: 70

      - type: gauge
        entity: sensor.solarsynkv3_2305178402_battery_temperature
        name: Temperature
        min: 0
        max: 60
        needle: true
        severity:
          green: 0
          yellow: 40
          red: 50

  # Battery Power Graph
  - type: custom:apexcharts-card
    header:
      show: true
      title: Battery Power (24h)
      show_states: true
    graph_span: 24h
    yaxis:
      - id: power
        min: ~
        decimals: 0
        apex_config:
          title:
            text: Power (W)
    apex_config:
      chart:
        height: 200
      annotations:
        yaxis:
          - y: 0
            borderColor: "#999"
            strokeDashArray: 5
            label:
              text: "Zero Line"
              style:
                background: "#999"
    series:
      - entity: sensor.solarsynkv3_2305178402_battery_power
        name: Battery Power
        color: "#2ecc71"
        stroke_width: 2
        # Negative = charging, Positive = discharging

  # Battery Voltage/Current
  - type: custom:apexcharts-card
    header:
      show: true
      title: Battery Voltage & Current (24h)
    graph_span: 24h
    yaxis:
      - id: voltage
        min: 45
        max: 58
        decimals: 1
        apex_config:
          title:
            text: Voltage (V)
      - id: current
        opposite: true
        min: ~
        decimals: 1
        apex_config:
          title:
            text: Current (A)
    apex_config:
      chart:
        height: 200
    series:
      - entity: sensor.solarsynkv3_2305178402_battery_voltage
        name: Voltage
        yaxis_id: voltage
        color: "#3498db"
        stroke_width: 2
      - entity: sensor.solarsynkv3_2305178402_battery_current
        name: Current
        yaxis_id: current
        color: "#e74c3c"
        stroke_width: 2

  # Daily Cycle Stats
  - type: entities
    title: Today's Battery Cycles
    entities:
      - entity: sensor.solarsynkv3_2305178402_battery_charge_today
        name: Energy Charged
        icon: mdi:battery-charging-100
      - entity: sensor.solarsynkv3_2305178402_battery_discharge_today
        name: Energy Discharged
        icon: mdi:battery-minus
      - type: divider
      - entity: sensor.solarsynkv3_2305178402_battery_charge_total
        name: Lifetime Charged
      - entity: sensor.solarsynkv3_2305178402_battery_discharge_total
        name: Lifetime Discharged
```

## 4. Grid Import/Export Tracker

Monitor grid usage for time-of-use optimization.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    name: Grid Analysis
    icon: mdi:transmission-tower

  # Grid Power Flow
  - type: custom:apexcharts-card
    header:
      show: true
      title: Grid Power (24h)
      show_states: true
    graph_span: 24h
    yaxis:
      - id: power
        min: ~
        decimals: 0
        apex_config:
          title:
            text: Power (W)
    apex_config:
      chart:
        height: 200
      annotations:
        yaxis:
          - y: 0
            borderColor: "#999"
            strokeDashArray: 5
            label:
              text: "Zero Export/Import"
              style:
                background: "#999"
        xaxis:
          # Peak hours 06:00-09:00 and 17:00-20:00
          - x: new Date().setHours(6,0,0,0)
            x2: new Date().setHours(9,0,0,0)
            fillColor: "#f39c12"
            opacity: 0.1
            label:
              text: "Peak AM"
          - x: new Date().setHours(17,0,0,0)
            x2: new Date().setHours(20,0,0,0)
            fillColor: "#e74c3c"
            opacity: 0.1
            label:
              text: "Peak PM"
    series:
      - entity: sensor.solarsynkv3_2305178402_grid_pac
        name: Grid Power
        color: "#3498db"
        stroke_width: 2
        # Negative = export, Positive = import

  # Grid Stats
  - type: grid
    columns: 2
    cards:
      - type: statistic
        entity: sensor.solarsynkv3_2305178402_grid_etoday_from
        name: Imported Today
        icon: mdi:transmission-tower-import
        stat_type: change
        period:
          calendar:
            period: day

      - type: statistic
        entity: sensor.solarsynkv3_2305178402_grid_etoday_to
        name: Exported Today
        icon: mdi:transmission-tower-export
        stat_type: change
        period:
          calendar:
            period: day

  # Grid Quality
  - type: entities
    title: Grid Quality
    entities:
      - entity: sensor.solarsynkv3_2305178402_grid_voltage
        name: Voltage
        icon: mdi:sine-wave
      - entity: sensor.solarsynkv3_2305178402_grid_frequency
        name: Frequency
        icon: mdi:waveform
      - entity: sensor.solarsynkv3_2305178402_grid_current
        name: Current
        icon: mdi:current-ac

  # Weekly Import/Export Comparison
  - type: custom:apexcharts-card
    header:
      show: true
      title: Weekly Import vs Export
    graph_span: 7d
    span:
      end: day
    yaxis:
      - id: energy
        min: 0
        decimals: 1
        apex_config:
          title:
            text: Energy (kWh)
    apex_config:
      chart:
        height: 200
        type: bar
    series:
      - entity: sensor.solarsynkv3_2305178402_grid_etoday_from
        name: Import
        color: "#e74c3c"
        type: column
        group_by:
          func: last
          duration: 1d
      - entity: sensor.solarsynkv3_2305178402_grid_etoday_to
        name: Export
        color: "#2ecc71"
        type: column
        group_by:
          func: last
          duration: 1d
```

## 5. PV Production Analysis

Detailed solar panel performance monitoring.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    name: Solar Production
    icon: mdi:solar-panel

  # MPPT String Comparison
  - type: grid
    columns: 2
    cards:
      - type: custom:mini-graph-card
        entities:
          - entity: sensor.solarsynkv3_2305178402_pv_mppt0_power
            name: String 1
            color: "#f39c12"
        name: MPPT 1
        icon: mdi:solar-panel-large
        hours_to_show: 12
        line_width: 2
        points_per_hour: 12
        show:
          state: true

      - type: custom:mini-graph-card
        entities:
          - entity: sensor.solarsynkv3_2305178402_pv_mppt1_power
            name: String 2
            color: "#e67e22"
        name: MPPT 2
        icon: mdi:solar-panel-large
        hours_to_show: 12
        line_width: 2
        points_per_hour: 12
        show:
          state: true

  # Combined PV Production
  - type: custom:apexcharts-card
    header:
      show: true
      title: Solar Production (Today)
      show_states: true
    graph_span: 1d
    span:
      start: day
      end: day
    yaxis:
      - id: power
        min: 0
        decimals: 0
        apex_config:
          title:
            text: Power (W)
    apex_config:
      chart:
        height: 250
      annotations:
        xaxis:
          - x: new Date().setHours(6,0,0,0)
            borderColor: "#FFA500"
            strokeDashArray: 3
            label:
              text: Sunrise
          - x: new Date().setHours(18,0,0,0)
            borderColor: "#4169E1"
            strokeDashArray: 3
            label:
              text: Sunset
    series:
      - entity: sensor.solarsynkv3_2305178402_pv_pac
        name: Total PV
        color: "#f39c12"
        stroke_width: 2
        type: area
      - entity: sensor.solarsynkv3_2305178402_pv_mppt0_power
        name: String 1
        color: "#e67e22"
        stroke_width: 1
      - entity: sensor.solarsynkv3_2305178402_pv_mppt1_power
        name: String 2
        color: "#d35400"
        stroke_width: 1

  # Daily Production Stats
  - type: entities
    title: Today's Production
    entities:
      - entity: sensor.solarsynkv3_2305178402_pv_etoday
        name: Energy Produced
        icon: mdi:solar-power
      - entity: sensor.solarsynkv3_2305178402_pv_pac
        name: Current Power
        icon: mdi:flash
      - type: divider
      - entity: sensor.solarsynkv3_2305178402_pv_mppt0_voltage
        name: String 1 Voltage
      - entity: sensor.solarsynkv3_2305178402_pv_mppt0_current
        name: String 1 Current
      - entity: sensor.solarsynkv3_2305178402_pv_mppt1_voltage
        name: String 2 Voltage
      - entity: sensor.solarsynkv3_2305178402_pv_mppt1_current
        name: String 2 Current

  # 7-Day Production History
  - type: custom:apexcharts-card
    header:
      show: true
      title: Weekly Production
    graph_span: 7d
    span:
      end: day
    yaxis:
      - id: energy
        min: 0
        decimals: 1
        apex_config:
          title:
            text: Energy (kWh)
    apex_config:
      chart:
        height: 200
        type: bar
    series:
      - entity: sensor.solarsynkv3_2305178402_pv_etoday
        name: Daily Production
        color: "#f39c12"
        type: column
        group_by:
          func: last
          duration: 1d
```

## 6. System Health Monitor

Monitor inverter health and detect issues.

```yaml
type: vertical-stack
cards:
  - type: custom:bubble-card
    card_type: separator
    name: System Health
    icon: mdi:heart-pulse

  # Status Overview
  - type: entities
    title: System Status
    entities:
      - entity: sensor.solarsynkv3_2305178402_overall_state
        name: Overall State
        icon: mdi:state-machine
      - entity: sensor.solarsynkv3_2305178402_inverter_status
        name: Inverter Status
        icon: mdi:solar-power-variant
      - entity: sensor.solarsynkv3_2305178402_fault_code
        name: Fault Code
        icon: mdi:alert-circle

  # Temperature Monitoring
  - type: custom:apexcharts-card
    header:
      show: true
      title: Inverter Temperature (24h)
    graph_span: 24h
    yaxis:
      - id: temp
        min: 0
        max: 80
        decimals: 0
        apex_config:
          title:
            text: Temperature (°C)
    apex_config:
      chart:
        height: 200
      annotations:
        yaxis:
          - y: 70
            borderColor: "#e74c3c"
            strokeDashArray: 5
            label:
              text: "High Temp Warning"
              style:
                background: "#e74c3c"
    series:
      - entity: sensor.solarsynkv3_2305178402_inverter_ac_temperature
        name: AC Side
        color: "#e74c3c"
        stroke_width: 2
      - entity: sensor.solarsynkv3_2305178402_inverter_dc_temperature
        name: DC Side
        color: "#3498db"
        stroke_width: 2
      - entity: sensor.solarsynkv3_2305178402_battery_temperature
        name: Battery
        color: "#2ecc71"
        stroke_width: 2

  # Temperature Gauges
  - type: grid
    columns: 3
    cards:
      - type: gauge
        entity: sensor.solarsynkv3_2305178402_inverter_ac_temperature
        name: Inverter AC
        min: 0
        max: 80
        severity:
          green: 0
          yellow: 60
          red: 70

      - type: gauge
        entity: sensor.solarsynkv3_2305178402_inverter_dc_temperature
        name: Inverter DC
        min: 0
        max: 80
        severity:
          green: 0
          yellow: 60
          red: 70

      - type: gauge
        entity: sensor.solarsynkv3_2305178402_battery_temperature
        name: Battery
        min: 0
        max: 60
        severity:
          green: 0
          yellow: 40
          red: 50

  # Lifetime Stats
  - type: entities
    title: Lifetime Statistics
    entities:
      - entity: sensor.solarsynkv3_2305178402_pv_etotal
        name: Total Solar Produced
        icon: mdi:solar-power
      - entity: sensor.solarsynkv3_2305178402_load_total_used
        name: Total Energy Consumed
        icon: mdi:home-lightning-bolt
      - entity: sensor.solarsynkv3_2305178402_grid_etotal_from
        name: Total Grid Import
        icon: mdi:transmission-tower-import
      - entity: sensor.solarsynkv3_2305178402_grid_etotal_to
        name: Total Grid Export
        icon: mdi:transmission-tower-export
      - type: divider
      - entity: sensor.solarsynkv3_2305178402_battery_charge_total
        name: Total Battery Charged
      - entity: sensor.solarsynkv3_2305178402_battery_discharge_total
        name: Total Battery Discharged
```

## Mobile-Optimized Dashboard

Compact dashboard for mobile devices:

```yaml
title: Solar Mobile
path: solar-mobile
icon: mdi:solar-power
panel: false
type: sections

sections:
  - type: grid
    cards:
      # Status Bar
      - type: custom:mushroom-chips-card
        chips:
          - type: entity
            entity: sensor.solarsynkv3_2305178402_pv_pac
            icon: mdi:solar-power
          - type: entity
            entity: sensor.solarsynkv3_2305178402_battery_soc
            icon: mdi:battery
          - type: entity
            entity: sensor.solarsynkv3_2305178402_load_total_power
            icon: mdi:home-lightning-bolt
          - type: entity
            entity: sensor.solarsynkv3_2305178402_grid_pac
            icon: mdi:transmission-tower

      # Quick Stats
      - type: custom:mushroom-entity-card
        entity: sensor.solarsynkv3_2305178402_pv_etoday
        name: Solar Today
        icon: mdi:solar-power
        primary_info: state
        secondary_info: name

      - type: custom:mushroom-entity-card
        entity: sensor.solarsynkv3_2305178402_load_daily_used
        name: Used Today
        icon: mdi:home-lightning-bolt
        primary_info: state
        secondary_info: name

      - type: custom:mushroom-entity-card
        entity: sensor.solarsynkv3_2305178402_battery_soc
        name: Battery
        icon: mdi:battery
        primary_info: state
        secondary_info: name

      # Sparklines
      - type: custom:mini-graph-card
        entities:
          - sensor.solarsynkv3_2305178402_pv_pac
        name: Solar
        hours_to_show: 12
        line_width: 2
        points_per_hour: 4
        show:
          labels: false
          legend: false

      - type: custom:mini-graph-card
        entities:
          - sensor.solarsynkv3_2305178402_battery_power
        name: Battery
        hours_to_show: 12
        line_width: 2
        points_per_hour: 4
        show:
          labels: false
          legend: false
```

## Notes

- Replace `2305178402` with your actual inverter serial
- All ApexCharts examples require HACS `apexcharts-card`
- Circular gauges require HACS `modern-circular-gauge`
- Bubble cards require HACS `bubble-card`
- Mini graphs require HACS `mini-graph-card`
- Mushroom cards require HACS `lovelace-mushroom`
- Energy flow requires HACS `energy-flow-card-plus`
- Adjust gauge max values based on your system capacity
- Customize colors to match your theme
