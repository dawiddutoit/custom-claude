# MQTT Auto-Discovery Sensor Configurations

Complete reference of sensor configuration templates for Home Assistant MQTT auto-discovery.

## Device Classes

Comprehensive list of Home Assistant device classes with units and icons.

### Environmental

| Device Class | Unit | Icon | Purpose |
|--------------|------|------|---------|
| `temperature` | °C, °F | mdi:thermometer | Temperature sensors |
| `humidity` | % | mdi:water-percent | Relative humidity |
| `atmospheric_pressure` | hPa, mbar | mdi:gauge | Barometric pressure |
| `illuminance` | lx | mdi:brightness-5 | Light level |

### Air Quality

| Device Class | Unit | Icon | Purpose |
|--------------|------|------|---------|
| `pm1` | µg/m³ | mdi:blur | Particulate matter <1µm |
| `pm25` | µg/m³ | mdi:blur | Particulate matter <2.5µm |
| `pm10` | µg/m³ | mdi:blur | Particulate matter <10µm |
| `aqi` | - | mdi:air-filter | Air quality index |
| `co` | ppm | mdi:molecule-co | Carbon monoxide |
| `co2` | ppm | mdi:molecule-co2 | Carbon dioxide |
| `volatile_organic_compounds` | µg/m³ | mdi:air-filter | VOCs |

### Energy

| Device Class | Unit | Icon | Purpose |
|--------------|------|------|---------|
| `power` | W | mdi:flash | Power consumption |
| `energy` | kWh, Wh | mdi:lightning-bolt | Energy usage |
| `voltage` | V | mdi:sine-wave | Voltage |
| `current` | A | mdi:current-ac | Current |
| `power_factor` | % | mdi:angle-acute | Power factor |

### Physical

| Device Class | Unit | Icon | Purpose |
|--------------|------|------|---------|
| `distance` | m, cm | mdi:ruler | Distance measurement |
| `weight` | kg, g | mdi:weight | Weight |
| `volume` | L, m³ | mdi:cup | Volume |
| `speed` | m/s, km/h | mdi:speedometer | Speed |

### Other

| Device Class | Unit | Icon | Purpose |
|--------------|------|------|---------|
| `battery` | % | mdi:battery | Battery level |
| `signal_strength` | dB, dBm | mdi:wifi | WiFi/signal strength |
| `timestamp` | ISO 8601 | mdi:clock | Timestamp |
| `monetary` | currency | mdi:cash | Money/cost |

## Complete Sensor Templates

### Enviro+ Environmental Sensor

```python
ENVIRO_SENSORS = {
    "temperature": {
        "name": "Temperature",
        "unique_id": "enviroplus_temperature",
        "state_topic": "enviroplus/temperature/state",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
        "icon": "mdi:thermometer",
    },
    "humidity": {
        "name": "Humidity",
        "unique_id": "enviroplus_humidity",
        "state_topic": "enviroplus/humidity/state",
        "device_class": "humidity",
        "unit_of_measurement": "%",
        "state_class": "measurement",
        "icon": "mdi:water-percent",
    },
    "pressure": {
        "name": "Pressure",
        "unique_id": "enviroplus_pressure",
        "state_topic": "enviroplus/pressure/state",
        "device_class": "atmospheric_pressure",
        "unit_of_measurement": "hPa",
        "state_class": "measurement",
        "icon": "mdi:gauge",
    },
    "light": {
        "name": "Light",
        "unique_id": "enviroplus_light",
        "state_topic": "enviroplus/light/state",
        "device_class": "illuminance",
        "unit_of_measurement": "lx",
        "state_class": "measurement",
        "icon": "mdi:brightness-5",
    },
    "pm1": {
        "name": "PM1.0",
        "unique_id": "enviroplus_pm1",
        "state_topic": "enviroplus/pm1/state",
        "device_class": "pm1",
        "unit_of_measurement": "µg/m³",
        "state_class": "measurement",
        "icon": "mdi:blur",
    },
    "pm2_5": {
        "name": "PM2.5",
        "unique_id": "enviroplus_pm2_5",
        "state_topic": "enviroplus/pm2_5/state",
        "device_class": "pm25",
        "unit_of_measurement": "µg/m³",
        "state_class": "measurement",
        "icon": "mdi:blur",
    },
    "pm10": {
        "name": "PM10",
        "unique_id": "enviroplus_pm10",
        "state_topic": "enviroplus/pm10/state",
        "device_class": "pm10",
        "unit_of_measurement": "µg/m³",
        "state_class": "measurement",
        "icon": "mdi:blur",
    },
    "noise": {
        "name": "Noise",
        "unique_id": "enviroplus_noise",
        "state_topic": "enviroplus/noise/state",
        "unit_of_measurement": "dB",
        "state_class": "measurement",
        "icon": "mdi:volume-high",
    },
}
```

### Energy Monitor

```python
ENERGY_SENSORS = {
    "power": {
        "name": "Power",
        "unique_id": "energymon_power",
        "state_topic": "energymon/power/state",
        "device_class": "power",
        "unit_of_measurement": "W",
        "state_class": "measurement",
    },
    "energy_total": {
        "name": "Total Energy",
        "unique_id": "energymon_energy_total",
        "state_topic": "energymon/energy_total/state",
        "device_class": "energy",
        "unit_of_measurement": "kWh",
        "state_class": "total_increasing",
    },
    "voltage": {
        "name": "Voltage",
        "unique_id": "energymon_voltage",
        "state_topic": "energymon/voltage/state",
        "device_class": "voltage",
        "unit_of_measurement": "V",
        "state_class": "measurement",
    },
    "current": {
        "name": "Current",
        "unique_id": "energymon_current",
        "state_topic": "energymon/current/state",
        "device_class": "current",
        "unit_of_measurement": "A",
        "state_class": "measurement",
    },
}
```

### CO2 Monitor

```python
CO2_SENSORS = {
    "co2": {
        "name": "CO2",
        "unique_id": "co2mon_co2",
        "state_topic": "co2mon/co2/state",
        "device_class": "co2",
        "unit_of_measurement": "ppm",
        "state_class": "measurement",
        "icon": "mdi:molecule-co2",
    },
    "temperature": {
        "name": "Temperature",
        "unique_id": "co2mon_temperature",
        "state_topic": "co2mon/temperature/state",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
}
```

## Binary Sensors

For on/off sensors (motion, door, etc.):

```python
BINARY_SENSOR = {
    "name": "Motion",
    "unique_id": "pir_motion",
    "state_topic": "pir/motion/state",
    "device_class": "motion",  # motion, door, window, etc.
    "payload_on": "ON",
    "payload_off": "OFF",
}
```

Binary sensor device classes: `motion`, `door`, `window`, `smoke`, `gas`, `moisture`, `occupancy`, `opening`, `plug`, `power`, `presence`, `problem`, `running`, `safety`, `tamper`, `vibration`

## Full Device Configuration Example

```python
{
    "name": "Sensor Name",
    "unique_id": "device_sensor_unique",
    "state_topic": "device/sensor/state",
    "device_class": "temperature",
    "unit_of_measurement": "°C",
    "state_class": "measurement",
    "icon": "mdi:thermometer",
    "expire_after": 300,  # Sensor marked unavailable after 300s of no updates
    "force_update": false,
    "entity_category": "diagnostic",  # or "config"
    "device": {
        "identifiers": ["device_id"],
        "name": "Device Name",
        "manufacturer": "Manufacturer",
        "model": "Model",
        "sw_version": "1.0.0",
        "configuration_url": "http://192.168.1.100",
    },
}
```

## Advanced Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `expire_after` | Mark unavailable after X seconds | 300 |
| `force_update` | Always trigger on same value | false |
| `entity_category` | Category (diagnostic/config) | "diagnostic" |
| `value_template` | Jinja2 template for value | "{{ value \| float }}" |
| `json_attributes_topic` | Topic for JSON attributes | "device/attrs" |
| `availability_topic` | Separate online/offline topic | "device/status" |
| `payload_available` | Online payload | "online" |
| `payload_not_available` | Offline payload | "offline" |
