#!/usr/bin/env python3
"""
Complete example: Create Home Assistant dashboard via WebSocket API.

Usage:
    export HA_LONG_LIVED_TOKEN="your_token_here"
    python create_dashboard.py
"""

import json
import os
import websocket


HA_URL = "http://192.168.68.123:8123"
HA_TOKEN = os.environ.get("HA_LONG_LIVED_TOKEN")

if not HA_TOKEN:
    raise ValueError("HA_LONG_LIVED_TOKEN environment variable not set")


def create_dashboard(url_path: str, title: str, config: dict):
    """Create or update a dashboard.

    Args:
        url_path: Dashboard URL path (must contain hyphen, e.g., "climate-control")
        title: Dashboard display title
        config: Dashboard configuration dict with views and cards
    """
    # Validate url_path contains hyphen
    if "-" not in url_path:
        raise ValueError(f"url_path must contain hyphen: '{url_path}' -> '{url_path}-view'")

    ws_url = HA_URL.replace("http://", "ws://") + "/api/websocket"
    ws = websocket.create_connection(ws_url)
    msg_id = 1

    # 1. Receive auth_required
    auth_required = ws.recv()
    print(f"Auth required: {auth_required}")

    # 2. Send auth
    ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
    auth_result = ws.recv()
    print(f"Auth result: {auth_result}")

    # 3. Check if dashboard exists
    ws.send(json.dumps({"id": msg_id, "type": "lovelace/dashboards/list"}))
    msg_id += 1
    response = json.loads(ws.recv())
    exists = any(d["url_path"] == url_path for d in response.get("result", []))
    print(f"Dashboard exists: {exists}")

    # 4. Create if doesn't exist
    if not exists:
        print(f"Creating dashboard: {url_path}")
        ws.send(json.dumps({
            "id": msg_id,
            "type": "lovelace/dashboards/create",
            "url_path": url_path,
            "title": title,
            "icon": "mdi:view-dashboard",
            "show_in_sidebar": True,
        }))
        msg_id += 1
        create_result = json.loads(ws.recv())
        print(f"Create result: {create_result}")

    # 5. Save configuration
    print(f"Saving configuration...")
    ws.send(json.dumps({
        "id": msg_id,
        "type": "lovelace/config/save",
        "url_path": url_path,
        "config": config,
    }))
    save_result = json.loads(ws.recv())
    print(f"Save result: {save_result}")

    ws.close()
    print(f"Dashboard created/updated: {HA_URL}/{url_path}")


def validate_entities(ws, msg_id: int, dashboard_config: dict) -> list[str]:
    """Validate all entities in dashboard exist.

    Returns:
        List of missing entity IDs
    """
    # Get all available entities
    ws.send(json.dumps({"id": msg_id, "type": "get_states"}))
    response = json.loads(ws.recv())
    available_entities = {state["entity_id"] for state in response.get("result", [])}

    # Extract entities from dashboard
    used_entities = []
    for view in dashboard_config.get("views", []):
        for card in view.get("cards", []):
            if "entity" in card:
                used_entities.append(card["entity"])
            if "entities" in card:
                for entity in card["entities"]:
                    entity_id = entity if isinstance(entity, str) else entity.get("entity")
                    if entity_id:
                        used_entities.append(entity_id)

    # Find missing entities
    missing = [e for e in used_entities if e not in available_entities]
    return missing


# Example dashboard configuration
example_dashboard = {
    "views": [
        {
            "title": "Overview",
            "path": "overview",
            "cards": [
                {
                    "type": "entities",
                    "title": "Climate",
                    "entities": [
                        "climate.snorlug",
                        "climate.val_hella_wam",
                        "climate.mines_of_moria",
                    ],
                },
                {
                    "type": "grid",
                    "columns": 3,
                    "square": False,
                    "cards": [
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
                        },
                        {
                            "type": "gauge",
                            "entity": "sensor.officeht_humidity",
                            "name": "Humidity",
                            "min": 0,
                            "max": 100,
                            "severity": {
                                "green": 40,
                                "yellow": 30,
                                "red": 20,
                            },
                        },
                    ],
                },
            ],
        },
    ],
}


if __name__ == "__main__":
    # Create example dashboard
    create_dashboard(
        url_path="climate-control",
        title="Climate Control",
        config=example_dashboard
    )
