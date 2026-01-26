# Basic Sunsynk Integration Setup Example

This example shows a complete setup of the SolarSynkV3 add-on for a typical home solar installation.

## Scenario

- Location: South Africa (Region 2)
- Inverter: Deye 8kW Hybrid
- Inverter Serial: 2305178402
- WiFi Dongle Serial: E47W23428459 (NOT used)
- Home Assistant IP: 192.168.68.123

## Step 1: Install Add-on

1. Navigate to Settings > Add-ons > Add-on Store
2. Click ⋮ > Repositories
3. Add repository: `https://github.com/martinville/solarsynkv3`
4. Install "SolarSynkV3"

## Step 2: Configure Add-on

```yaml
sunsynk_user: "user@example.com"
sunsynk_pass: "your_password"
sunsynk_serial: "2305178402"  # INVERTER serial (from portal)
Home_Assistant_IP: "192.168.68.123"
Home_Assistant_PORT: 8123
HA_LongLiveToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
Refresh_rate: 300  # 5 minutes
API_Server: "api.sunsynk.net"  # Region 2
use_internal_api: false
Enable_HTTPS: false
```

## Step 3: Start Add-on

Click "Start" and monitor logs:

```bash
ha addons logs d4ae3b04_solar_synkv3
```

Expected output:
```
[INFO] Connected to Sunsynk API
[INFO] Found inverter 2305178402
[INFO] Creating sensors...
[INFO] Created 300+ entities
```

## Step 4: Verify Entities

Check Developer Tools > States for entities:

```
sensor.solarsynkv3_2305178402_battery_soc
sensor.solarsynkv3_2305178402_pv_pac
sensor.solarsynkv3_2305178402_grid_pac
sensor.solarsynkv3_2305178402_load_total_power
```

## Step 5: Test with REST API

```bash
# Get battery state of charge
curl -s "http://192.168.68.123:8123/api/states/sensor.solarsynkv3_2305178402_battery_soc" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | jq '.state'

# Output: "75.0"
```

## Common Issues

### "No Permissions" Error

**Symptom:** Add-on logs show "No Permissions" error.

**Fix:** Verify you're using the inverter serial (2305178402) not the dongle serial (E47W23428459).

### No Entities Created

**Symptom:** Add-on running but no sensors appear.

**Fix:** Check HA long-lived token is valid and Home Assistant IP is correct. Restart HA core.

## Success Criteria

✅ Add-on status shows "Running"
✅ Logs show "Connected to Sunsynk API"
✅ 300+ entities created in Developer Tools
✅ Battery SOC sensor shows current percentage
✅ PV power sensor shows solar generation (W)
