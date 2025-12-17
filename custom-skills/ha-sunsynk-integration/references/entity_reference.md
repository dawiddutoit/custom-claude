# Sunsynk Entity Reference

Comprehensive reference for all Sunsynk entity IDs created by the SolarSynkV3 add-on.

All entities follow the pattern: `sensor.solarsynkv3_{serial}_{sensor_name}`

Example serial: `2305178402`

## Battery Entities

| Entity ID | Description | Unit | Device Class | Notes |
|-----------|-------------|------|--------------|-------|
| `sensor.solarsynkv3_{serial}_battery_soc` | State of Charge | % | battery | 0-100, target for charge/discharge logic |
| `sensor.solarsynkv3_{serial}_battery_power` | Current power flow | W | power | Negative = charging, Positive = discharging |
| `sensor.solarsynkv3_{serial}_battery_voltage` | DC voltage | V | voltage | Typically 48-58V for 48V battery |
| `sensor.solarsynkv3_{serial}_battery_current` | DC current | A | current | Negative = charging, Positive = discharging |
| `sensor.solarsynkv3_{serial}_battery_temperature` | Battery temp | °C | temperature | Monitor for thermal management |
| `sensor.solarsynkv3_{serial}_battery_charge_today` | Energy charged today | kWh | energy | Daily cycle tracking |
| `sensor.solarsynkv3_{serial}_battery_discharge_today` | Energy discharged today | kWh | energy | Daily cycle tracking |
| `sensor.solarsynkv3_{serial}_battery_charge_total` | Total energy charged | kWh | energy | Lifetime tracking |
| `sensor.solarsynkv3_{serial}_battery_discharge_total` | Total energy discharged | kWh | energy | Lifetime tracking |

**Key Use Cases:**
- SOC-based automations (start generator at 20%)
- Battery health monitoring (temperature, voltage)
- Energy arbitrage calculations (daily charge/discharge)

## PV (Solar Panel) Entities

| Entity ID | Description | Unit | Device Class | Notes |
|-----------|-------------|------|--------------|-------|
| `sensor.solarsynkv3_{serial}_pv_pac` | Total PV power (all MPPTs) | W | power | Sum of all MPPT inputs |
| `sensor.solarsynkv3_{serial}_pv_mppt0_power` | MPPT 1 power | W | power | String 1 production |
| `sensor.solarsynkv3_{serial}_pv_mppt1_power` | MPPT 2 power | W | power | String 2 production |
| `sensor.solarsynkv3_{serial}_pv_mppt0_voltage` | MPPT 1 voltage | V | voltage | String 1 voltage |
| `sensor.solarsynkv3_{serial}_pv_mppt1_voltage` | MPPT 2 voltage | V | voltage | String 2 voltage |
| `sensor.solarsynkv3_{serial}_pv_mppt0_current` | MPPT 1 current | A | current | String 1 current |
| `sensor.solarsynkv3_{serial}_pv_mppt1_current` | MPPT 2 current | A | current | String 2 current |
| `sensor.solarsynkv3_{serial}_pv_etoday` | Energy produced today | kWh | energy | Daily solar harvest |
| `sensor.solarsynkv3_{serial}_pv_etotal` | Total energy produced | kWh | energy | Lifetime solar harvest |

**Key Use Cases:**
- Production monitoring dashboards
- String imbalance detection (compare MPPT1 vs MPPT2)
- Performance ratio calculations
- Shading analysis

## Grid Entities

| Entity ID | Description | Unit | Device Class | Notes |
|-----------|-------------|------|--------------|-------|
| `sensor.solarsynkv3_{serial}_grid_pac` | Grid power flow | W | power | Negative = export, Positive = import |
| `sensor.solarsynkv3_{serial}_grid_voltage` | Grid voltage | V | voltage | Typically 220-240V (single phase) |
| `sensor.solarsynkv3_{serial}_grid_current` | Grid current | A | current | Current flow to/from grid |
| `sensor.solarsynkv3_{serial}_grid_frequency` | Grid frequency | Hz | frequency | Typically 50Hz (EU/ZA) or 60Hz (US) |
| `sensor.solarsynkv3_{serial}_grid_etoday_from` | Energy from grid today | kWh | energy | Daily grid import |
| `sensor.solarsynkv3_{serial}_grid_etoday_to` | Energy to grid today | kWh | energy | Daily grid export |
| `sensor.solarsynkv3_{serial}_grid_etotal_from` | Total energy from grid | kWh | energy | Lifetime grid import |
| `sensor.solarsynkv3_{serial}_grid_etotal_to` | Total energy to grid | kWh | energy | Lifetime grid export |

**Key Use Cases:**
- Grid export limiting (compliance with regulations)
- Zero-export control
- Time-of-use optimization
- Grid stability monitoring (frequency/voltage)

## Load (Consumption) Entities

| Entity ID | Description | Unit | Device Class | Notes |
|-----------|-------------|------|--------------|-------|
| `sensor.solarsynkv3_{serial}_load_total_power` | Total household load | W | power | Real-time consumption |
| `sensor.solarsynkv3_{serial}_load_l1_power` | Phase 1 load | W | power | Single-phase or phase 1 of 3-phase |
| `sensor.solarsynkv3_{serial}_load_l2_power` | Phase 2 load | W | power | Phase 2 (3-phase systems) |
| `sensor.solarsynkv3_{serial}_load_l3_power` | Phase 3 load | W | power | Phase 3 (3-phase systems) |
| `sensor.solarsynkv3_{serial}_load_daily_used` | Energy consumed today | kWh | energy | Daily consumption |
| `sensor.solarsynkv3_{serial}_load_total_used` | Total energy consumed | kWh | energy | Lifetime consumption |

**Key Use Cases:**
- Load shedding automations
- Peak demand monitoring
- Phase imbalance detection (3-phase systems)
- Energy usage analytics

## Inverter Status Entities

| Entity ID | Description | Unit | Device Class | Notes |
|-----------|-------------|------|--------------|-------|
| `sensor.solarsynkv3_{serial}_inverter_power` | Inverter output power | W | power | AC power delivered |
| `sensor.solarsynkv3_{serial}_inverter_ac_temperature` | AC side temperature | °C | temperature | Monitor for overheating |
| `sensor.solarsynkv3_{serial}_inverter_dc_temperature` | DC side temperature | °C | temperature | Monitor for overheating |
| `sensor.solarsynkv3_{serial}_overall_state` | System state | - | - | Text: "Normal", "Fault", etc. |
| `sensor.solarsynkv3_{serial}_fault_code` | Current fault code | - | - | 0 = no fault |
| `sensor.solarsynkv3_{serial}_inverter_status` | Inverter status | - | - | Text: "Running", "Standby", etc. |

**Key Use Cases:**
- Fault detection and alerting
- Thermal management (derating warnings)
- System health monitoring
- Performance tracking

## Calculated/Derived Entities

These entities may be available depending on add-on configuration:

| Entity ID | Description | Unit | Calculation |
|-----------|-------------|------|-------------|
| `sensor.solarsynkv3_{serial}_self_consumption_rate` | Self-consumption % | % | (Load - Grid Import) / Load * 100 |
| `sensor.solarsynkv3_{serial}_self_sufficiency_rate` | Self-sufficiency % | % | Solar / Load * 100 |
| `sensor.solarsynkv3_{serial}_export_rate` | Export rate % | % | Grid Export / Solar * 100 |

## Entity State Interpretations

### Power Flow Sign Conventions

**Battery Power:**
- **Negative** (-500W) = Charging
- **Positive** (+500W) = Discharging

**Grid Power:**
- **Negative** (-1000W) = Exporting to grid
- **Positive** (+1000W) = Importing from grid

### Overall State Values

| State | Meaning | Action |
|-------|---------|--------|
| `Normal` | All systems operational | None |
| `Standby` | No solar, battery charged | None |
| `Fault` | System fault detected | Check fault_code |
| `Off` | Inverter powered off | Check physical switch |
| `GridWait` | Waiting for stable grid | None (auto-recover) |

### Fault Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 0 | No fault | - |
| 1 | Grid overvoltage | Wait for grid to stabilize |
| 2 | Grid undervoltage | Wait for grid to stabilize |
| 3 | Grid overfrequency | Contact utility |
| 4 | Grid underfrequency | Contact utility |
| 5 | Battery overvoltage | Check battery BMS |
| 6 | Battery undervoltage | Charge battery |
| 7 | Inverter overtemperature | Check ventilation |
| 8 | DC overvoltage | Check PV strings |

## Dashboard Integration Examples

### Energy Flow Sankey Diagram

Calculate energy flows:
```yaml
# Solar to Load (direct consumption)
solar_to_load = min(pv_pac, load_total_power)

# Solar to Battery (excess solar)
solar_to_battery = max(0, pv_pac - load_total_power) if battery_power < 0 else 0

# Solar to Grid (export)
solar_to_grid = pv_pac - solar_to_load - solar_to_battery

# Battery to Load (discharge)
battery_to_load = battery_power if battery_power > 0 else 0

# Grid to Load (import)
grid_to_load = grid_pac if grid_pac > 0 else 0
```

### Self-Consumption Template Sensor

Create in `configuration.yaml`:
```yaml
template:
  - sensor:
      - name: "Solar Self-Consumption Rate"
        unique_id: solar_self_consumption_rate
        unit_of_measurement: "%"
        state: >
          {% set pv = states('sensor.solarsynkv3_2305178402_pv_pac') | float(0) %}
          {% set export = states('sensor.solarsynkv3_2305178402_grid_pac') | float(0) %}
          {% set self_used = pv - min(0, export) %}
          {% if pv > 0 %}
            {{ ((self_used / pv) * 100) | round(1) }}
          {% else %}
            0
          {% endif %}
```

## Entity Grouping

Group entities for easier management:

```yaml
# configuration.yaml
group:
  sunsynk_battery:
    name: "Battery"
    entities:
      - sensor.solarsynkv3_2305178402_battery_soc
      - sensor.solarsynkv3_2305178402_battery_power
      - sensor.solarsynkv3_2305178402_battery_voltage
      - sensor.solarsynkv3_2305178402_battery_temperature

  sunsynk_solar:
    name: "Solar Production"
    entities:
      - sensor.solarsynkv3_2305178402_pv_pac
      - sensor.solarsynkv3_2305178402_pv_mppt0_power
      - sensor.solarsynkv3_2305178402_pv_mppt1_power
      - sensor.solarsynkv3_2305178402_pv_etoday

  sunsynk_grid:
    name: "Grid"
    entities:
      - sensor.solarsynkv3_2305178402_grid_pac
      - sensor.solarsynkv3_2305178402_grid_voltage
      - sensor.solarsynkv3_2305178402_grid_frequency
      - sensor.solarsynkv3_2305178402_grid_etoday_from
      - sensor.solarsynkv3_2305178402_grid_etoday_to
```

## Automation Examples

### Low Battery Alert

```yaml
automation:
  - alias: "Sunsynk: Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solarsynkv3_2305178402_battery_soc
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "Low Battery"
          message: "Battery SOC is {{ states('sensor.solarsynkv3_2305178402_battery_soc') }}%"
```

### Grid Export Limiting

```yaml
automation:
  - alias: "Sunsynk: Limit Grid Export"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solarsynkv3_2305178402_grid_pac
        below: -3000  # Exporting more than 3kW
    action:
      - service: number.set_value
        target:
          entity_id: number.sunsynk_max_sell_power
        data:
          value: 2000  # Limit to 2kW export
```

## Notes

- Entity availability depends on inverter model and firmware
- Some entities may show "unavailable" if feature not supported
- Entity IDs are case-sensitive
- Use Developer Tools → States to explore available entities
- Add-on must be running for entities to update
