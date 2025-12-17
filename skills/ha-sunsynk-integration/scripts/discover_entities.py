#!/usr/bin/env python3
"""
Sunsynk Entity Discovery Script

Discovers all Sunsynk entities in Home Assistant and saves them to a JSON file.

Usage:
    python3 discover_entities.py --serial 2305178402 --output sunsynk_entities.json
    python3 discover_entities.py --serial 2305178402 --pattern battery
"""

import argparse
import json
import os
import sys
from typing import Any

import requests


def get_ha_config() -> tuple[str, str]:
    """Get Home Assistant URL and token from environment."""
    ha_url = os.environ.get("HA_URL", "http://192.168.68.123:8123")
    ha_token = os.environ.get("HA_LONG_LIVED_TOKEN")

    if not ha_token:
        print("Error: HA_LONG_LIVED_TOKEN not set in environment", file=sys.stderr)
        print("Run: source ~/.zshrc", file=sys.stderr)
        sys.exit(1)

    return ha_url, ha_token


def discover_entities(
    serial: str, pattern: str | None = None
) -> dict[str, dict[str, Any]]:
    """
    Discover Sunsynk entities from Home Assistant.

    Args:
        serial: Inverter serial number
        pattern: Optional filter pattern (e.g., 'battery', 'pv', 'grid')

    Returns:
        Dictionary mapping entity IDs to their state information
    """
    ha_url, ha_token = get_ha_config()

    url = f"{ha_url}/api/states"
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error connecting to Home Assistant: {e}", file=sys.stderr)
        sys.exit(1)

    entities = {}
    search_pattern = f"solarsynkv3_{serial}"

    for state in response.json():
        entity_id = state["entity_id"]

        # Filter by serial number
        if search_pattern not in entity_id:
            continue

        # Filter by optional pattern
        if pattern and pattern.lower() not in entity_id.lower():
            continue

        entities[entity_id] = {
            "state": state["state"],
            "unit": state["attributes"].get("unit_of_measurement"),
            "device_class": state["attributes"].get("device_class"),
            "friendly_name": state["attributes"].get("friendly_name"),
            "last_updated": state["last_updated"],
        }

    return entities


def main():
    parser = argparse.ArgumentParser(
        description="Discover Sunsynk entities in Home Assistant"
    )
    parser.add_argument(
        "--serial", required=True, help="Inverter serial number (e.g., 2305178402)"
    )
    parser.add_argument(
        "--pattern",
        help="Filter entities by pattern (e.g., battery, pv, grid)",
        default=None,
    )
    parser.add_argument(
        "--output", help="Output JSON file", default="sunsynk_entities.json"
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args()

    print(f"Discovering Sunsynk entities for serial: {args.serial}")
    if args.pattern:
        print(f"Filtering by pattern: {args.pattern}")

    entities = discover_entities(args.serial, args.pattern)

    if not entities:
        print(
            f"No entities found for serial {args.serial}",
            file=sys.stderr,
        )
        print(
            "Check that SolarSynkV3 add-on is running and creating entities",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nFound {len(entities)} entities:")
    for entity_id in sorted(entities.keys()):
        state_info = entities[entity_id]
        unit = state_info["unit"] or ""
        print(f"  {entity_id}: {state_info['state']} {unit}")

    # Save to file
    indent = 2 if args.pretty else None
    with open(args.output, "w") as f:
        json.dump(entities, f, indent=indent, sort_keys=True)

    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
