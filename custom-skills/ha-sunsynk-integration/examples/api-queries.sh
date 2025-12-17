#!/bin/bash
# Sunsynk Solar System REST API Query Examples
# Source your HA_LONG_LIVED_TOKEN before running

# Set your configuration
HA_URL="${HA_URL:-http://192.168.68.123:8123}"
INVERTER_SERIAL="${INVERTER_SERIAL:-2305178402}"

# Check if token is set
if [ -z "$HA_LONG_LIVED_TOKEN" ]; then
    echo "Error: HA_LONG_LIVED_TOKEN not set"
    echo "Run: source ~/.zshrc"
    exit 1
fi

# Helper function for API calls
ha_api() {
    local endpoint="$1"
    curl -s "${HA_URL}/api/${endpoint}" \
        -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
        -H "Content-Type: application/json"
}

# Get specific sensor value
get_sensor() {
    local sensor="$1"
    ha_api "states/sensor.solarsynkv3_${INVERTER_SERIAL}_${sensor}" | jq -r '.state'
}

echo "=== Sunsynk Solar System Status ==="
echo

# Battery Status
echo "Battery:"
echo "  SOC:         $(get_sensor battery_soc)%"
echo "  Power:       $(get_sensor battery_power)W"
echo "  Voltage:     $(get_sensor battery_voltage)V"
echo "  Temperature: $(get_sensor battery_temperature)°C"
echo

# Solar Production
echo "Solar:"
echo "  Current:     $(get_sensor pv_pac)W"
echo "  Today:       $(get_sensor pv_etoday)kWh"
echo "  Lifetime:    $(get_sensor pv_etotal)kWh"
echo

# Grid Status
echo "Grid:"
echo "  Current:     $(get_sensor grid_pac)W"
echo "  Import Today: $(get_sensor grid_etoday_from)kWh"
echo "  Export Today: $(get_sensor grid_etoday_to)kWh"
echo

# Load
echo "Load:"
echo "  Current:     $(get_sensor load_total_power)W"
echo "  Today:       $(get_sensor load_daily_used)kWh"
echo

# Inverter Status
echo "Inverter:"
echo "  Status:      $(get_sensor runstatus)"
echo "  Power:       $(get_sensor inverter_power)W"
echo "  Frequency:   $(get_sensor inverter_frequency)Hz"
echo

# Get all Sunsynk entities
echo "=== All Sunsynk Entities ==="
ha_api "states" | jq -r '.[] | select(.entity_id | startswith("sensor.solarsynkv3")) | .entity_id' | sort

# Get specific entity with full details
echo
echo "=== Battery SOC Details ==="
ha_api "states/sensor.solarsynkv3_${INVERTER_SERIAL}_battery_soc" | jq '.'

# Check entity history (last 24 hours)
echo
echo "=== Battery SOC History (last 24h) ==="
# History API requires timestamp format: 2024-12-15T00:00:00+00:00
START_TIME=$(date -u -v-1d +"%Y-%m-%dT%H:%M:%S+00:00")
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")

curl -s "${HA_URL}/api/history/period/${START_TIME}?filter_entity_id=sensor.solarsynkv3_${INVERTER_SERIAL}_battery_soc&end_time=${END_TIME}" \
    -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" | \
    jq '.[0] | .[] | {time: .last_changed, value: .state}' | head -20
