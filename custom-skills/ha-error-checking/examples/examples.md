# Error Checking Examples

Comprehensive workflows for debugging and validating Home Assistant dashboards.

## Complete Dashboard Validation Workflow

```python
def comprehensive_dashboard_check(url_path: str):
    """Perform comprehensive dashboard error checking."""
    ws = connect_to_ha()
    errors = []
    warnings = []

    # 1. Validate URL path format
    is_valid, error = validate_url_path(url_path)
    if not is_valid:
        errors.append(f"URL path invalid: {error}")

    # 2. Check dashboard exists
    dashboards = get_dashboards(ws)
    if url_path not in [d["url_path"] for d in dashboards]:
        errors.append(f"Dashboard '{url_path}' does not exist")
        return {"errors": errors, "warnings": warnings}

    # 3. Get dashboard config
    config = get_dashboard_config(ws, url_path)

    # 4. Check system logs
    logs = get_system_logs(ws)
    lovelace_errors = [
        log for log in logs
        if "lovelace" in log.get("name", "").lower()
        and log.get("level") == "ERROR"
    ]
    if lovelace_errors:
        for log in lovelace_errors:
            errors.append(f"System log: {log['message']}")

    # 5. Validate entities
    all_entities = set(get_all_entity_ids(ws))
    missing_entities = validate_dashboard_entities(config, all_entities)
    if missing_entities:
        warnings.append(f"Missing entities: {missing_entities}")

    # 6. Validate custom cards
    for view in config.get("views", []):
        for card in view.get("cards", []):
            card_type = card.get("type", "")

            # Check ApexCharts span
            if card_type == "custom:apexcharts-card":
                is_valid, error = validate_apexcharts_span(card)
                if not is_valid:
                    errors.append(f"ApexCharts config: {error}")

    ws.close()

    return {
        "errors": errors,
        "warnings": warnings,
        "config": config,
    }

# Usage
result = comprehensive_dashboard_check("climate-control")
if result["errors"]:
    print("ERRORS:")
    for error in result["errors"]:
        print(f"  - {error}")
if result["warnings"]:
    print("WARNINGS:")
    for warning in result["warnings"]:
        print(f"  - {warning}")
```

## Entity Extraction and Validation

```python
def extract_entities_from_config(config: dict) -> set[str]:
    """Extract all entity IDs used in a dashboard config."""
    entities = set()

    for view in config.get("views", []):
        for card in view.get("cards", []):
            # Handle different card types
            if "entity" in card:
                entities.add(card["entity"])

            if "entities" in card:
                for entity in card["entities"]:
                    # Handle both string and dict formats
                    if isinstance(entity, str):
                        entities.add(entity)
                    elif isinstance(entity, dict) and "entity" in entity:
                        entities.add(entity["entity"])

            # Handle nested cards (vertical-stack, grid, etc.)
            if "cards" in card:
                # Recursively extract from nested cards
                nested_config = {"views": [{"cards": card["cards"]}]}
                entities.update(extract_entities_from_config(nested_config))

    return entities

def validate_dashboard_entities(config: dict, available_entities: set[str]) -> list[str]:
    """Validate all entities in dashboard exist.

    Returns:
        List of missing entity IDs
    """
    used_entities = extract_entities_from_config(config)
    missing = [e for e in used_entities if e not in available_entities]
    return missing

# Usage
dashboard_config = get_dashboard_config(ws, "climate-control")
all_entities = set(get_all_entity_ids(ws))
missing = validate_dashboard_entities(dashboard_config, all_entities)

if missing:
    print(f"Warning: Missing entities: {missing}")
```

## Entity Pattern Matching

```python
def find_entities_by_pattern(pattern: str, all_entities: list[str]) -> list[str]:
    """Find entities matching a pattern (e.g., 'sensor.enviro_*')."""
    import fnmatch
    return [e for e in all_entities if fnmatch.fnmatch(e, pattern)]

# Examples
enviro_sensors = find_entities_by_pattern("sensor.enviro_*", entity_ids)
climate_devices = find_entities_by_pattern("climate.*", entity_ids)
office_sensors = find_entities_by_pattern("sensor.officeht_*", entity_ids)
```

## HACS Card Installation Check

```python
def check_hacs_card_installed(ws, repository_id: int) -> bool:
    """Check if a HACS card is installed by repository ID."""
    ws.send(json.dumps({
        "id": 1,
        "type": "hacs/repositories/list"
    }))
    response = json.loads(ws.recv())

    repositories = response.get("result", [])
    installed = [r for r in repositories if r.get("id") == repository_id]

    return len(installed) > 0

# Known repository IDs
HACS_CARDS = {
    "mini-graph-card": 151280062,
    "bubble-card": 680112919,
    "modern-circular-gauge": 871730343,
    "lovelace-mushroom": 444350375,
    "apexcharts-card": 331701152,
}

# Check installation
if check_hacs_card_installed(ws, HACS_CARDS["apexcharts-card"]):
    print("ApexCharts card is installed")
else:
    print("ApexCharts card NOT installed - install via HACS first")
```

## Install HACS Card Programmatically

```python
def install_hacs_card(ws, repository_id: int, msg_id: int = 1) -> bool:
    """Install a HACS card by repository ID.

    Returns:
        True if successful, False otherwise
    """
    ws.send(json.dumps({
        "id": msg_id,
        "type": "hacs/repository/download",
        "repository": repository_id,
    }))
    response = json.loads(ws.recv())

    return response.get("success", False)

# Install ApexCharts
success = install_hacs_card(ws, HACS_CARDS["apexcharts-card"])
if success:
    print("ApexCharts installed successfully - restart HA to activate")
else:
    print("Failed to install ApexCharts")
```

## ApexCharts Span Validation

```python
VALID_SPAN_END_VALUES = ["minute", "hour", "day", "week", "month", "year", "isoWeek"]

def validate_apexcharts_span(card_config: dict) -> tuple[bool, str]:
    """Validate ApexCharts span configuration.

    Returns:
        (is_valid, error_message)
    """
    if "span" not in card_config:
        return True, ""  # span is optional

    span = card_config["span"]
    if "end" not in span:
        return True, ""  # end is optional within span

    end_value = span["end"]
    if end_value not in VALID_SPAN_END_VALUES:
        return False, f"Invalid span.end: '{end_value}'. Must be one of: {VALID_SPAN_END_VALUES}"

    return True, ""

# Usage
apexcharts_card = {
    "type": "custom:apexcharts-card",
    "span": {"end": "now"}  # ❌ Invalid
}

is_valid, error = validate_apexcharts_span(apexcharts_card)
if not is_valid:
    print(f"Error: {error}")
    # Fix it
    apexcharts_card["span"]["end"] = "hour"  # ✅ Valid
```

## Dashboard URL Path Validation

```python
def validate_url_path(url_path: str) -> tuple[bool, str]:
    """Validate dashboard URL path format.

    Returns:
        (is_valid, error_message)
    """
    if "-" not in url_path:
        return False, f"URL path must contain hyphen: '{url_path}' -> '{url_path}-view'"

    if " " in url_path:
        return False, f"URL path cannot contain spaces: '{url_path}'"

    if not url_path.islower():
        return False, f"URL path must be lowercase: '{url_path}'"

    return True, ""

# Examples
validate_url_path("climate")         # ❌ (False, "URL path must contain hyphen...")
validate_url_path("climate-control") # ✅ (True, "")
validate_url_path("Climate-Control") # ❌ (False, "URL path must be lowercase...")
```

## Filter Lovelace Errors from System Logs

```python
lovelace_errors = [
    log for log in logs
    if "lovelace" in log.get("name", "").lower()
    or "frontend" in log.get("name", "").lower()
]

for error in lovelace_errors:
    print(f"[{error['level']}] {error['name']}: {error['message']}")
```

## Custom Card Type Validation

```python
KNOWN_CUSTOM_CARDS = [
    "custom:apexcharts-card",
    "custom:mini-graph-card",
    "custom:bubble-card",
    "custom:modern-circular-gauge",
    "custom:mushroom-climate-card",
    "custom:mushroom-entity-card",
]

def validate_custom_card(card_config: dict, installed_cards: list[str]) -> tuple[bool, str]:
    """Validate custom card is installed.

    Returns:
        (is_valid, error_message)
    """
    card_type = card_config.get("type", "")

    if not card_type.startswith("custom:"):
        return True, ""  # Not a custom card

    if card_type not in installed_cards:
        return False, f"Custom card not installed: {card_type}"

    return True, ""
```
