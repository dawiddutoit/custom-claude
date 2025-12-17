# Sunsynk/Deye Solar System Integration Skill

## Overview

This skill provides comprehensive guidance for integrating Sunsynk and Deye solar inverters with Home Assistant using the SolarSynkV3 cloud API add-on.

## Quick Reference

**Add-on:** `d4ae3b04_solar_synkv3`
**Repository:** https://github.com/martinville/solarsynkv3
**Critical:** Use **inverter serial** (NOT dongle serial) in configuration

## Files

### Core Documentation
- **SKILL.md** - Main skill file with setup, configuration, and troubleshooting

### Examples
- **examples/dashboard-config.yaml** - Complete solar dashboard with ApexCharts, gauges, and energy summary
- **examples/api-queries.sh** - Bash script for querying Sunsynk entities via REST API

### References
- **references/sensor-reference.md** - Complete list of 300+ sensors with descriptions, units, and automation examples
- **references/entity_reference.md** - Legacy reference (kept for completeness)
- **references/dashboard_examples.md** - Additional dashboard patterns
- **references/troubleshooting.md** - Extended troubleshooting scenarios

### Scripts
- **scripts/entity-discovery.py** - Python script to discover and categorize all Sunsynk entities
- **scripts/discover_entities.py** - Legacy discovery script (kept for completeness)

## Key Concepts

### Serial Number Gotcha

The #1 cause of "No Permissions" errors:

```
Inverter Serial:  2305178402        ✓ USE THIS
Dongle Serial:    E47W23428459      ✗ NOT THIS
```

Find inverter serial at: sunsynk.net → Inverter menu

### Entity Naming Pattern

```
sensor.solarsynkv3_{INVERTER_SERIAL}_{SENSOR_NAME}
```

Example:
```
sensor.solarsynkv3_2305178402_battery_soc
sensor.solarsynkv3_2305178402_pv_pac
```

### Essential Sensors

| Category | Sensor | Purpose |
|----------|--------|---------|
| Battery | `battery_soc` | State of Charge (%) |
| Solar | `pv_pac` | Total solar power (W) |
| Grid | `grid_pac` | Import/export (W) |
| Load | `load_total_power` | Consumption (W) |
| Status | `runstatus` | Inverter status |

### WiFi Dongle Limitation

Stock Sunsynk WiFi dongles are **cloud-only** - no local Modbus access. SolarSynkV3 (cloud API) is the recommended integration method.

## Usage Examples

### Quick Status Check

```bash
# Source HA token
source ~/.zshrc

# Run discovery script
python ~/.claude/skills/ha-sunsynk-integration/scripts/entity-discovery.py

# Or use quick API queries
~/.claude/skills/ha-sunsynk-integration/examples/api-queries.sh
```

### Dashboard Creation

Copy `examples/dashboard-config.yaml` and replace `2305178402` with your inverter serial:

```bash
sed 's/2305178402/YOUR_SERIAL/g' \
  ~/.claude/skills/ha-sunsynk-integration/examples/dashboard-config.yaml
```

## Troubleshooting Checklist

- [ ] Using inverter serial (NOT dongle serial)
- [ ] Correct API server for region (api.sunsynk.net for SA)
- [ ] Valid sunsynk.net account credentials
- [ ] HA long-lived token is current
- [ ] Add-on shows "Connected to API" in logs
- [ ] Entities appear in Developer Tools > States

## Integration Status

**Working:** Cloud API via SolarSynkV3 add-on
**Not Working:** Local Modbus (stock dongle lacks open ports)

## Support

- **GitHub Issues:** https://github.com/martinville/solarsynkv3/issues
- **HA Forum:** community.home-assistant.io
- **Sunsynk Support:** support@sunsynk.net

## Version

Skill created: 2025-12-15
Based on: SolarSynkV3 v3.0.31, Home Assistant 2025.12.3
