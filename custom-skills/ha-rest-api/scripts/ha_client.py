#!/usr/bin/env python3
"""Home Assistant REST API client helper."""

import os
import requests
from typing import Any


class HomeAssistantClient:
    """Simple client for Home Assistant REST API."""

    def __init__(self, url: str | None = None, token: str | None = None):
        """Initialize client with URL and token from environment or parameters."""
        self.url = url or os.environ.get("HA_URL", "http://192.168.68.123:8123")
        self.token = token or os.environ["HA_LONG_LIVED_TOKEN"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get_all_entities(self) -> list[dict]:
        """Get all entity states."""
        response = requests.get(
            f"{self.url}/api/states",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_entity_state(self, entity_id: str) -> dict:
        """Get state for specific entity."""
        response = requests.get(
            f"{self.url}/api/states/{entity_id}",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str,
        **kwargs: Any,
    ) -> list[dict]:
        """Call a Home Assistant service."""
        data = {"entity_id": entity_id, **kwargs}
        response = requests.post(
            f"{self.url}/api/services/{domain}/{service}",
            headers=self.headers,
            json=data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def discover_entities(self, pattern: str) -> dict[str, str]:
        """Discover entities matching a pattern."""
        entities = {}
        for state in self.get_all_entities():
            entity_id = state["entity_id"]
            if pattern.lower() in entity_id.lower():
                entities[entity_id] = state["state"]
        return entities

    def get_services(self) -> list[dict]:
        """Get all available services."""
        response = requests.get(
            f"{self.url}/api/services",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_config(self) -> dict:
        """Get Home Assistant configuration."""
        response = requests.get(
            f"{self.url}/api/config",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    # Example usage
    client = HomeAssistantClient()

    # Test connection
    config = client.get_config()
    print(f"Connected to Home Assistant {config['version']}")
    print(f"Location: {config['location_name']} ({config['time_zone']})")

    # Discover climate entities
    climate = client.discover_entities("climate.")
    print(f"\nFound {len(climate)} climate entities:")
    for entity_id, state in climate.items():
        print(f"  {entity_id}: {state}")

    # Get office temperature
    temp = client.get_entity_state("sensor.officeht_temperature")
    print(f"\nOffice Temperature: {temp['state']}{temp['attributes']['unit_of_measurement']}")
