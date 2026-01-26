# Dashboard Card Types

Complete reference for common Home Assistant dashboard card types.

## Common Card Types

### Entities Card

```python
{
    "type": "entities",
    "title": "Climate",
    "entities": [
        "climate.snorlug",
        "climate.val_hella_wam",
        "climate.mines_of_moria",
    ],
}
```

### Gauge Card

```python
{
    "type": "gauge",
    "entity": "sensor.officeht_temperature",
    "name": "Temperature",
    "min": 0,
    "max": 50,
    "severity": {
        "green": 18,
        "yellow": 26,
        "red": 35,
    },
}
```

### Grid Layout

```python
{
    "type": "grid",
    "columns": 3,
    "square": False,
    "cards": [
        # Cards here
    ],
}
```

### Vertical Stack

```python
{
    "type": "vertical-stack",
    "cards": [
        # Multiple cards stacked vertically
    ],
}
```

## Dashboard Configuration Structure

```python
dashboard_config = {
    "views": [
        {
            "title": "Overview",
            "path": "overview",  # View path (no hyphen required)
            "cards": [
                # Card configurations here
            ],
        },
        {
            "title": "Climate",
            "path": "climate",  # View path (no hyphen required)
            "cards": [
                # More cards
            ],
        },
    ],
}
```

**Note:** View paths (within a dashboard) don't require hyphens, only the dashboard `url_path` does.
