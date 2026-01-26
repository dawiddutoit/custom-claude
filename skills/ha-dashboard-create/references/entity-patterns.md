# Entity ID Patterns

Common entity patterns for HA dashboard creation.

## Enviro+ Sensors

```python
enviro_sensors = [
    "sensor.enviro_sensor_temperature",
    "sensor.enviro_sensor_humidity",
    "sensor.enviro_sensor_pressure",
    "sensor.enviro_sensor_light",
    "sensor.enviro_sensor_pm1_0",
    "sensor.enviro_sensor_pm2_5",
    "sensor.enviro_sensor_pm10",
]
```

## Office Sensors

```python
office_sensors = [
    "sensor.officeht_temperature",
    "sensor.officeht_humidity",
    "sensor.officeht_battery",
]
```

## Climate Devices

```python
climate_devices = [
    "climate.snorlug",
    "climate.val_hella_wam",
    "climate.mines_of_moria",
]
```

## Shelly Power Monitoring

```python
power_sensors = [
    "sensor.shellyplus1pm_*_switch_0_power",
    "sensor.shellyswitch25_*_channel_1_power",
]
```

## Entity Validation

### Verify Entity IDs Before Creating Dashboard

```python
def get_entity_ids(ws) -> list[str]:
    """Get all available entity IDs from HA."""
    ws.send(json.dumps({"id": 1, "type": "get_states"}))
    response = json.loads(ws.recv())
    return [state["entity_id"] for state in response.get("result", [])]

def validate_dashboard_entities(config: dict, available_entities: set[str]) -> list[str]:
    """Validate all entities in dashboard exist.

    Returns:
        List of missing entity IDs
    """
    used_entities = []
    missing = []

    for view in config.get("views", []):
        for card in view.get("cards", []):
            # Extract entities from card (handles different card types)
            if "entity" in card:
                used_entities.append(card["entity"])
            if "entities" in card:
                used_entities.extend(card["entities"])

    for entity in used_entities:
        # Handle entity strings and dicts
        entity_id = entity if isinstance(entity, str) else entity.get("entity")
        if entity_id and entity_id not in available_entities:
            missing.append(entity_id)

    return missing

# Usage
ws = connect_to_ha()
available = set(get_entity_ids(ws))
missing = validate_dashboard_entities(dashboard_config, available)

if missing:
    print(f"Warning: Missing entities: {missing}")
```
