#!/usr/bin/env python3
"""
Discover all Sunsynk/SolarSynkV3 entities in Home Assistant.

Usage:
    export HA_URL="http://192.168.68.123:8123"
    export HA_LONG_LIVED_TOKEN="your_token"
    python entity-discovery.py
"""

import os
import sys
import json
import requests
from typing import Dict, List
from collections import defaultdict

HA_URL = os.environ.get("HA_URL", "http://192.168.68.123:8123")
HA_TOKEN = os.environ.get("HA_LONG_LIVED_TOKEN")

if not HA_TOKEN:
    print("Error: HA_LONG_LIVED_TOKEN environment variable not set")
    print("Run: source ~/.zshrc")
    sys.exit(1)


def get_all_entities() -> List[Dict]:
    """Fetch all entity states from Home Assistant."""
    url = f"{HA_URL}/api/states"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def filter_sunsynk_entities(entities: List[Dict]) -> List[Dict]:
    """Filter entities belonging to Sunsynk integration."""
    return [
        e for e in entities
        if "solarsynkv3" in e["entity_id"] or "sunsynk" in e["entity_id"]
    ]


def categorize_sensors(entities: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize sensors by type (battery, pv, grid, load, inverter)."""
    categories = defaultdict(list)
    
    for entity in entities:
        entity_id = entity["entity_id"]
        
        if "battery" in entity_id:
            categories["Battery"].append(entity)
        elif "pv" in entity_id or "mppt" in entity_id:
            categories["Solar/PV"].append(entity)
        elif "grid" in entity_id:
            categories["Grid"].append(entity)
        elif "load" in entity_id:
            categories["Load"].append(entity)
        elif "inverter" in entity_id:
            categories["Inverter"].append(entity)
        elif any(x in entity_id for x in ["etoday", "etotal", "emonth", "eyear"]):
            categories["Energy Totals"].append(entity)
        else:
            categories["Other"].append(entity)
    
    return dict(categories)


def print_entity_summary(entities: List[Dict]):
    """Print summary of discovered entities."""
    print(f"\n{'='*80}")
    print(f"Sunsynk Solar Integration - Entity Discovery")
    print(f"{'='*80}\n")
    
    if not entities:
        print("No Sunsynk entities found!")
        print("\nTroubleshooting:")
        print("1. Check add-on is running: http://<ha_ip>:8123/hassio/addon/d4ae3b04_solar_synkv3")
        print("2. Verify add-on configuration (inverter serial, credentials)")
        print("3. Check add-on logs: ha addons logs d4ae3b04_solar_synkv3")
        return
    
    print(f"Total Sunsynk entities found: {len(entities)}\n")
    
    categories = categorize_sensors(entities)
    
    for category, category_entities in sorted(categories.items()):
        print(f"\n{category} ({len(category_entities)} entities)")
        print("-" * 80)
        
        for entity in sorted(category_entities, key=lambda x: x["entity_id"]):
            entity_id = entity["entity_id"]
            state = entity["state"]
            unit = entity.get("attributes", {}).get("unit_of_measurement", "")
            friendly_name = entity.get("attributes", {}).get("friendly_name", entity_id)
            
            # Format state value
            if unit:
                state_str = f"{state} {unit}"
            else:
                state_str = state
            
            print(f"  {entity_id:<70} = {state_str}")


def export_to_json(entities: List[Dict], filename: str = "sunsynk_entities.json"):
    """Export entity list to JSON file."""
    output = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "total_entities": len(entities),
        "entities": [
            {
                "entity_id": e["entity_id"],
                "state": e["state"],
                "unit": e.get("attributes", {}).get("unit_of_measurement"),
                "friendly_name": e.get("attributes", {}).get("friendly_name"),
                "device_class": e.get("attributes", {}).get("device_class"),
            }
            for e in entities
        ]
    }
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nEntity list exported to: {filename}")


def main():
    """Main entry point."""
    try:
        print("Connecting to Home Assistant...")
        all_entities = get_all_entities()
        
        sunsynk_entities = filter_sunsynk_entities(all_entities)
        
        print_entity_summary(sunsynk_entities)
        
        # Export to JSON
        if sunsynk_entities:
            export_to_json(sunsynk_entities)
        
        print(f"\n{'='*80}\n")
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Home Assistant: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
