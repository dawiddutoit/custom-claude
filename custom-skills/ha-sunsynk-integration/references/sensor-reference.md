# Complete Sunsynk/SolarSynkV3 Sensor Reference

This document provides a comprehensive reference for all sensors created by the SolarSynkV3 add-on integration.

## Entity Naming Pattern

All entities follow this format:

```
sensor.solarsynkv3_{INVERTER_SERIAL}_{SENSOR_NAME}
```

Replace `{INVERTER_SERIAL}` with your inverter serial number (e.g., `2305178402`).

## Sensor Categories

### Battery Sensors (9)

| Entity ID Suffix | Description | Unit | Type | Notes |
|-----------------|-------------|------|------|-------|
| `battery_soc` | State of Charge | % | measurement | Primary battery status indicator |
| `battery_power` | Charge/discharge power | W | measurement | Negative = charging, Positive = discharging |
| `battery_voltage` | Battery voltage | V | measurement | Nominal 48V system |
| `battery_current` | Battery current | A | measurement | Negative = charging current |
| `battery_temperature` | Battery temperature | °C | measurement | Monitor for overheating |
| `battery_capacity` | Battery capacity | Ah | measurement | Total capacity (e.g., 280Ah) |
| `battery_etoday_charge` | Today charged | kWh | total_increasing | Resets daily |
| `battery_etoday_discharge` | Today discharged | kWh | total_increasing | Resets daily |
| `battery_status` | Battery status | - | - | Charging/Discharging/Standby |

**Key Metrics:**
- **SOC**: Primary indicator for automations (charge/discharge triggers)
- **Power**: Real-time charge/discharge rate
- **Temperature**: Safety monitoring (typically 0-45°C)

### PV/Solar Sensors (12+)

| Entity ID Suffix | Description | Unit | Type | Notes |
|-----------------|-------------|------|------|-------|
| `pv_pac` | Total PV power | W | measurement | Sum of all MPPT strings |
| `pv_etoday` | Today's solar yield | kWh | total_increasing | Resets at midnight |
| `pv_etotal` | Lifetime solar yield | kWh | total | Cumulative since installation |
| `pv_mppt0_power` | MPPT1 power | W | measurement | String 1 |
| `pv_mppt0_voltage` | MPPT1 voltage | V | measurement | String 1 |
| `pv_mppt0_current` | MPPT1 current | A | measurement | String 1 |
| `pv_mppt1_power` | MPPT2 power | W | measurement | String 2 |
| `pv_mppt1_voltage` | MPPT2 voltage | V | measurement | String 2 |
| `pv_mppt1_current` | MPPT2 current | A | measurement | String 2 |

**MPPT Analysis:**
- Compare MPPT string outputs to identify shading or panel issues
- Typical voltage: 200-500V DC per string
- Current varies with panel configuration

### Grid Sensors (8)

| Entity ID Suffix | Description | Unit | Type | Notes |
|-----------------|-------------|------|------|-------|
| `grid_pac` | Grid power | W | measurement | Positive = import, Negative = export |
| `grid_etoday_from` | Today imported | kWh | total_increasing | From grid to home |
| `grid_etoday_to` | Today exported | kWh | total_increasing | From solar to grid |
| `grid_etotal_from` | Total imported | kWh | total | Cumulative import |
| `grid_etotal_to` | Total exported | kWh | total | Cumulative export |
| `grid_status` | Grid connection | - | - | Connected/Disconnected |
| `grid_voltage` | Grid voltage | V | measurement | Typically 220-240V AC |
| `grid_frequency` | Grid frequency | Hz | measurement | 50Hz (SA/EU) or 60Hz (US) |

**Grid Power Sign Convention:**
- **Positive** (`grid_pac > 0`): Importing from grid (buying)
- **Negative** (`grid_pac < 0`): Exporting to grid (selling)
- **Zero** (`grid_pac ≈ 0`): Self-sufficient (no grid interaction)

### Load Sensors (3)

| Entity ID Suffix | Description | Unit | Type | Notes |
|-----------------|-------------|------|------|-------|
| `load_total_power` | Total load | W | measurement | All consumption (AC + DC) |
| `load_daily_used` | Today's consumption | kWh | total_increasing | Resets daily |
| `load_total_used` | Total consumption | kWh | total | Cumulative usage |

**Load Calculation:**
```
Load = PV + Battery + Grid (all positive values)
```

### Inverter Sensors (6)

| Entity ID Suffix | Description | Unit | Type | Notes |
|-----------------|-------------|------|------|-------|
| `inverter_power` | Inverter output | W | measurement | AC output power |
| `inverter_frequency` | AC frequency | Hz | measurement | Should be stable (50/60Hz) |
| `inverter_ac_temperature` | AC side temp | °C | measurement | Monitor for overheating |
| `inverter_dc_temperature` | DC side temp | °C | measurement | Monitor for overheating |
| `runstatus` | Inverter status | - | - | Normal/Fault/Standby |
| `inverter_efficiency` | Efficiency | % | measurement | DC-to-AC conversion efficiency |

**Temperature Guidelines:**
- **Normal**: 30-50°C under load
- **Warning**: 50-70°C (reduced efficiency)
- **Critical**: >70°C (thermal throttling)

### Energy Totals (4)

| Entity ID Suffix | Description | Unit | Type | Notes |
|-----------------|-------------|------|------|-------|
| `etoday` | Today's generation | kWh | total_increasing | Solar + Battery discharge |
| `etotal` | Lifetime generation | kWh | total | Since installation |
| `emonth` | This month | kWh | total_increasing | Resets monthly |
| `eyear` | This year | kWh | total_increasing | Resets annually |

### Additional Sensors (Varies by Model)

Some inverter models expose additional sensors:

| Entity ID Suffix | Description | Unit | Notes |
|-----------------|-------------|------|-------|
| `aux_power` | Auxiliary load | W | Generator or backup load |
| `dc_transformer_temp` | Transformer temp | °C | High-power models |
| `ambient_temp` | Ambient temperature | °C | Some models have sensor |
| `total_backup_load` | Backup load | W | Off-grid systems |

## Power Flow Understanding

### Basic Power Flow

```
Solar (PV) → Inverter → [Priority 1: Load] → [Priority 2: Battery] → [Priority 3: Grid]
                      ↑
                  [Grid Import if needed]
```

### Scenarios

**1. Daytime - Excess Solar:**
```
PV: 5000W
Load: 2000W
Battery: -2000W (charging)
Grid: -1000W (exporting)
```

**2. Daytime - Insufficient Solar:**
```
PV: 1000W
Load: 3000W
Battery: 1500W (discharging)
Grid: 500W (importing)
```

**3. Nighttime - Battery Discharge:**
```
PV: 0W
Load: 1500W
Battery: 1500W (discharging)
Grid: 0W (using battery only)
```

**4. Nighttime - Grid Import:**
```
PV: 0W
Load: 2000W
Battery: 0W (low SOC, protecting battery)
Grid: 2000W (importing)
```

## Energy Efficiency Metrics

### Self-Sufficiency Ratio
```
SSR = (PV Generation - Grid Export) / Total Load
```

- **100%**: Completely self-sufficient (no grid import)
- **>100%**: Net exporter (selling to grid)
- **<100%**: Partial grid dependence

### Battery Utilization
```
Battery Cycles Per Day = (Daily Discharge kWh) / (Battery Capacity kWh)
```

- **0.5-1.0 cycles**: Typical daily usage
- **>1.0 cycles**: Heavy battery use
- **<0.5 cycles**: Underutilized battery

### Solar Yield Factor
```
Yield Factor = (Daily PV kWh) / (System Size kW)
```

- **3-5 kWh/kW**: Typical South African summer
- **2-3 kWh/kW**: Winter or cloudy conditions
- **<2 kWh/kW**: Poor weather or system issues

## Automation Examples

### Battery Management

**Low Battery Alert:**
```yaml
automation:
  - alias: Battery Low Warning
    trigger:
      platform: numeric_state
      entity_id: sensor.solarsynkv3_2305178402_battery_soc
      below: 20
    action:
      service: notify.mobile_app
      data:
        message: "Battery low: {{ states('sensor.solarsynkv3_2305178402_battery_soc') }}%"
```

**Grid Export Limit:**
```yaml
automation:
  - alias: Stop Export at 95% SOC
    trigger:
      platform: numeric_state
      entity_id: sensor.solarsynkv3_2305178402_battery_soc
      above: 95
    action:
      service: switch.turn_off
      target:
        entity_id: switch.inverter_grid_export  # If available
```

### Load Management

**High Load Alert:**
```yaml
automation:
  - alias: High Consumption Warning
    trigger:
      platform: numeric_state
      entity_id: sensor.solarsynkv3_2305178402_load_total_power
      above: 5000
      for:
        minutes: 5
    action:
      service: notify.mobile_app
      data:
        message: "High load detected: {{ states('sensor.solarsynkv3_2305178402_load_total_power') }}W"
```

### Temperature Monitoring

**Inverter Overheat Alert:**
```yaml
automation:
  - alias: Inverter Temperature Warning
    trigger:
      - platform: numeric_state
        entity_id: sensor.solarsynkv3_2305178402_inverter_ac_temperature
        above: 65
      - platform: numeric_state
        entity_id: sensor.solarsynkv3_2305178402_inverter_dc_temperature
        above: 65
    action:
      service: notify.mobile_app
      data:
        message: "Inverter temperature high: {{ trigger.to_state.state }}°C"
```

## Dashboard Best Practices

### Real-Time Monitoring

**Essential Sensors:**
1. `battery_soc` - Battery status (gauge)
2. `pv_pac` - Solar power (gauge)
3. `load_total_power` - Consumption (gauge)
4. `grid_pac` - Grid import/export (gauge)

### Historical Trends

**24-Hour Graphs:**
- PV power (yellow line)
- Battery power (blue line, positive/negative)
- Grid power (red line, positive/negative)
- Load power (gray line)

**Daily Energy Bars:**
- Solar yield (`pv_etoday`)
- Consumption (`load_daily_used`)
- Grid import (`grid_etoday_from`)
- Grid export (`grid_etoday_to`)

### Status Overview

**Critical Indicators:**
- Inverter status (`runstatus`)
- Grid status (`grid_status`)
- Battery SOC (`battery_soc`)
- Temperature warnings (AC/DC temps)

## Troubleshooting Sensor Values

### Unrealistic Values

**Problem:** Sensor shows 0W or 999999W
**Cause:** API communication error or invalid data
**Solution:** Check add-on logs, verify API connection

**Problem:** Battery SOC stuck at 100%
**Cause:** Battery not calibrated or BMS issue
**Solution:** Perform battery calibration cycle (discharge to 20%, charge to 100%)

### Missing Sensors

**Problem:** Not all sensors appearing
**Cause:** Inverter model differences, firmware version
**Solution:** Some sensors are model-specific, check inverter documentation

### Incorrect Units

**Problem:** Power shown in kW instead of W
**Cause:** API version differences
**Solution:** Use templates to convert units if needed

## API Query Examples

### Get Current Power Flow
```bash
curl -s "http://<ha_ip>:8123/api/states/sensor.solarsynkv3_2305178402_pv_pac" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | jq '.state'
```

### Get All Battery Sensors
```bash
curl -s "http://<ha_ip>:8123/api/states" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | \
  jq '.[] | select(.entity_id | contains("battery"))'
```

### Calculate Self-Sufficiency
```python
import requests

pv_today = float(get_sensor("pv_etoday"))
grid_export = float(get_sensor("grid_etoday_to"))
load_used = float(get_sensor("load_daily_used"))

self_sufficiency = ((pv_today - grid_export) / load_used) * 100
print(f"Self-sufficiency: {self_sufficiency:.1f}%")
```

## Notes

- Sensor availability varies by inverter model (Deye 5kW vs 8kW vs 12kW)
- Some sensors require specific firmware versions
- Cloud API refresh rate is 300 seconds (5 minutes) by default
- Local Modbus integrations have faster update rates (10-30 seconds)
