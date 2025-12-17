#!/usr/bin/env python3
"""MQTT auto-discovery publisher for Home Assistant."""

import json
import paho.mqtt.client as mqtt
from typing import Any


class DiscoveryPublisher:
    """Publish MQTT auto-discovery configurations to Home Assistant."""

    def __init__(self, broker: str, port: int = 1883):
        """Initialize MQTT discovery publisher."""
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def connect(self):
        """Connect to MQTT broker."""
        self.client.connect(self.broker, self.port, 60)

    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.disconnect()

    def publish_sensor(
        self,
        device_id: str,
        sensor_key: str,
        name: str,
        device_class: str | None = None,
        unit: str | None = None,
        state_class: str = "measurement",
        device_info: dict[str, Any] | None = None,
    ) -> str:
        """
        Publish sensor discovery configuration.

        Returns the unique_id of the created sensor.
        """
        unique_id = f"{device_id}_{sensor_key}"
        discovery_topic = f"homeassistant/sensor/{unique_id}/config"
        state_topic = f"{device_id}/{sensor_key}/state"

        config = {
            "name": name,
            "unique_id": unique_id,
            "state_topic": state_topic,
            "state_class": state_class,
        }

        if device_class:
            config["device_class"] = device_class
        if unit:
            config["unit_of_measurement"] = unit
        if device_info:
            config["device"] = device_info

        self.client.publish(discovery_topic, json.dumps(config), qos=1, retain=True)
        print(f"Published discovery: sensor.{device_id}_{sensor_key}")
        return unique_id

    def publish_sensors(
        self,
        device_id: str,
        sensors: dict[str, dict],
        device_info: dict[str, Any],
    ):
        """Publish multiple sensors for a device."""
        for sensor_key, sensor_config in sensors.items():
            self.publish_sensor(
                device_id=device_id,
                sensor_key=sensor_key,
                name=sensor_config["name"],
                device_class=sensor_config.get("device_class"),
                unit=sensor_config.get("unit_of_measurement"),
                state_class=sensor_config.get("state_class", "measurement"),
                device_info=device_info,
            )

    def remove_sensor(self, device_id: str, sensor_key: str):
        """Remove a sensor by publishing empty config."""
        unique_id = f"{device_id}_{sensor_key}"
        discovery_topic = f"homeassistant/sensor/{unique_id}/config"
        self.client.publish(discovery_topic, "", qos=1, retain=True)
        print(f"Removed: sensor.{device_id}_{sensor_key}")


if __name__ == "__main__":
    # Example: Enviro+ environmental sensor
    BROKER = "192.168.68.123"
    DEVICE_ID = "enviroplus"

    SENSORS = {
        "temperature": {
            "name": "Temperature",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
        },
        "humidity": {
            "name": "Humidity",
            "device_class": "humidity",
            "unit_of_measurement": "%",
        },
        "pressure": {
            "name": "Pressure",
            "device_class": "atmospheric_pressure",
            "unit_of_measurement": "hPa",
        },
        "pm2_5": {
            "name": "PM2.5",
            "device_class": "pm25",
            "unit_of_measurement": "µg/m³",
        },
    }

    DEVICE_INFO = {
        "identifiers": [DEVICE_ID],
        "name": "Enviro+ Environmental Sensor",
        "manufacturer": "Pimoroni",
        "model": "Enviro+",
        "sw_version": "1.0.0",
    }

    # Publish discovery
    publisher = DiscoveryPublisher(BROKER)
    publisher.connect()
    publisher.publish_sensors(DEVICE_ID, SENSORS, DEVICE_INFO)
    publisher.disconnect()

    print("\nSensors published successfully!")
    print("\nPublish values with:")
    for sensor_key in SENSORS:
        print(f"  mosquitto_pub -h {BROKER} -t '{DEVICE_ID}/{sensor_key}/state' -m '<value>'")
