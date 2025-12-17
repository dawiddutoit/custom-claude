#!/usr/bin/env python3
"""
Check Home Assistant dashboard for errors.

Usage:
    python check_dashboard.py climate-control
"""

import json
import os
import sys
import websocket

HA_URL = "http://192.168.68.123:8123"
HA_TOKEN = os.environ.get("HA_LONG_LIVED_TOKEN")

VALID_SPAN_END_VALUES = ["minute", "hour", "day", "week", "month", "year", "isoWeek"]

HACS_CARDS = {
    "mini-graph-card": 151280062,
    "bubble-card": 680112919,
    "modern-circular-gauge": 871730343,
    "lovelace-mushroom": 444350375,
    "apexcharts-card": 331701152,
}


def connect_to_ha():
    """Connect to Home Assistant WebSocket API."""
    ws_url = HA_URL.replace("http://", "ws://") + "/api/websocket"
    ws = websocket.create_connection(ws_url)

    # Auth
    ws.recv()  # auth_required
    ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
    ws.recv()  # auth_ok

    return ws


def validate_url_path(url_path: str) -> tuple[bool, str]:
    """Validate dashboard URL path format."""
    if "-" not in url_path:
        return False, f"URL path must contain hyphen: '{url_path}' -> '{url_path}-view'"

    if " " in url_path:
        return False, f"URL path cannot contain spaces: '{url_path}'"

    if not url_path.islower():
        return False, f"URL path must be lowercase: '{url_path}'"

    return True, ""


def validate_apexcharts_span(card_config: dict) -> tuple[bool, str]:
    """Validate ApexCharts span configuration."""
    if "span" not in card_config:
        return True, ""

    span = card_config["span"]
    if "end" not in span:
        return True, ""

    end_value = span["end"]
    if end_value not in VALID_SPAN_END_VALUES:
        return False, f"Invalid span.end: '{end_value}'. Must be one of: {VALID_SPAN_END_VALUES}"

    return True, ""


def check_dashboard_errors(url_path: str):
    """Check for errors in a specific dashboard."""
    ws = connect_to_ha()
    msg_id = 1
    errors = []
    warnings = []

    # 1. Validate URL path format
    is_valid, error = validate_url_path(url_path)
    if not is_valid:
        errors.append(f"URL path invalid: {error}")

    # 2. Check system logs for lovelace errors
    ws.send(json.dumps({"id": msg_id, "type": "system_log/list"}))
    msg_id += 1
    logs = json.loads(ws.recv())

    lovelace_errors = [
        log for log in logs.get("result", [])
        if "lovelace" in log.get("name", "").lower()
        or "frontend" in log.get("name", "").lower()
    ]

    if lovelace_errors:
        for log in lovelace_errors:
            errors.append(f"[{log['level']}] {log['name']}: {log['message'][:100]}")

    # 3. Validate dashboard config
    ws.send(json.dumps({
        "id": msg_id,
        "type": "lovelace/config",
        "url_path": url_path
    }))
    msg_id += 1
    config_response = json.loads(ws.recv())

    if "error" in config_response:
        errors.append(f"Dashboard not found: {url_path}")
        ws.close()
        return {"errors": errors, "warnings": warnings}

    config = config_response.get("result", {})

    # 4. Get all entity states
    ws.send(json.dumps({"id": msg_id, "type": "get_states"}))
    msg_id += 1
    states_response = json.loads(ws.recv())
    available_entities = {s["entity_id"] for s in states_response.get("result", [])}

    # 5. Validate cards
    for view in config.get("views", []):
        for card in view.get("cards", []):
            card_type = card.get("type", "")

            # Check ApexCharts span
            if card_type == "custom:apexcharts-card":
                is_valid, error = validate_apexcharts_span(card)
                if not is_valid:
                    errors.append(f"ApexCharts config: {error}")

            # Check entities exist
            if "entity" in card and card["entity"] not in available_entities:
                warnings.append(f"Entity not found: {card['entity']}")

            if "entities" in card:
                for entity in card["entities"]:
                    entity_id = entity if isinstance(entity, str) else entity.get("entity")
                    if entity_id and entity_id not in available_entities:
                        warnings.append(f"Entity not found: {entity_id}")

    ws.close()

    return {
        "errors": errors,
        "warnings": warnings,
        "config": config,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_dashboard.py <dashboard-url-path>")
        sys.exit(1)

    url_path = sys.argv[1]
    result = check_dashboard_errors(url_path)

    print(f"\n=== Dashboard Check: {url_path} ===\n")

    if result["errors"]:
        print("ERRORS:")
        for error in result["errors"]:
            print(f"  ❌ {error}")
        print()

    if result["warnings"]:
        print("WARNINGS:")
        for warning in result["warnings"]:
            print(f"  ⚠️  {warning}")
        print()

    if not result["errors"] and not result["warnings"]:
        print("✅ No errors or warnings found!\n")

    sys.exit(1 if result["errors"] else 0)
