#!/usr/bin/env python3
"""Complete dashboard section examples using ha_card_utils.

These examples show full sensor sections with:
- Enhanced separators for major sections
- Sub-section labels for organization
- Current value cards (Mushroom template cards)
- Info cards for context
- Three-graph rows with static titles and color gradients

IMPORTANT: This example requires ha_card_utils.py from your HA project.
Copy it from: /Users/dawiddutoit/projects/play/ha/ha_card_utils.py
Or adjust sys.path below to point to your HA project directory.
"""

import sys
from pathlib import Path

# Try to import from skill directory first, then HA project directory
skill_dir = Path(__file__).parent.parent  # Go up to skill root
ha_project_dir = Path.home() / "projects" / "play" / "ha"

if skill_dir.exists():
    sys.path.insert(0, str(skill_dir))
if ha_project_dir.exists():
    sys.path.insert(0, str(ha_project_dir))

from ha_card_utils import (  # type: ignore
    add_static_title_to_mini_graph,
    add_color_gradient_to_mini_graph,
    enable_mini_graph_extrema,
    create_bubble_separator,
    create_info_card,
    COLOR_SCHEMES,
)


def create_temperature_section():
    """Complete temperature section with current values and history."""
    # Define entities
    entities = [
        {
            "entity_id": "sensor.enviro_temperature",
            "name": "Enviro",
            "color": "#2ecc71",
        },
        {
            "entity_id": "sensor.officeht_temperature",
            "name": "Office",
            "color": "#3498db",
        },
    ]

    # Build temperature thresholds
    temp_thresholds = [
        COLOR_SCHEMES["temperature"]["cold"],
        COLOR_SCHEMES["temperature"]["comfortable"],
        COLOR_SCHEMES["temperature"]["warm"],
        COLOR_SCHEMES["temperature"]["hot"],
    ]

    # Build graph entities
    graph_entities = [
        {"entity": e["entity_id"], "name": e["name"], "color": e["color"]}
        for e in entities
    ]

    return {
        "type": "vertical-stack",
        "cards": [
            # Major section header
            create_bubble_separator("Temperature", "mdi:thermometer", enhanced=True),

            # Sub-section: Current readings
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Current Temperatures",
                "icon": "mdi:home-thermometer",
            },

            # Current value cards (Mushroom template)
            {
                "type": "horizontal-stack",
                "cards": [
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Enviro",
                        "secondary": "{{ states('sensor.enviro_temperature') }}°C",
                        "icon": "mdi:thermometer",
                        "icon_color": "green",
                    },
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Office",
                        "secondary": "{{ states('sensor.officeht_temperature') }}°C",
                        "icon": "mdi:thermometer",
                        "icon_color": "blue",
                    },
                ],
            },

            # Sub-section: Temperature history
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Temperature History",
                "icon": "mdi:chart-line",
            },

            # Three-graph row with static titles and color gradients
            {
                "type": "horizontal-stack",
                "cards": [
                    add_color_gradient_to_mini_graph(
                        enable_mini_graph_extrema(
                            add_static_title_to_mini_graph({
                                "type": "custom:mini-graph-card",
                                "name": "Last Hour",
                                "hours_to_show": 1,
                                "points_per_hour": 60,
                                "line_width": 2,
                                "entities": graph_entities,
                            })
                        ),
                        temp_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last 24 Hours",
                            "hours_to_show": 24,
                            "points_per_hour": 4,
                            "line_width": 2,
                            "entities": graph_entities,
                        }),
                        temp_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Week",
                            "hours_to_show": 168,
                            "points_per_hour": 1,
                            "line_width": 2,
                            "entities": graph_entities,
                        }),
                        temp_thresholds
                    ),
                ],
            },
        ],
    }


def create_humidity_section():
    """Complete humidity section with context info card."""
    entities = [
        {
            "entity_id": "sensor.enviro_humidity",
            "name": "Enviro",
            "color": "#3498db",
        },
        {
            "entity_id": "sensor.officeht_humidity",
            "name": "Office",
            "color": "#2ecc71",
        },
    ]

    humidity_thresholds = [
        COLOR_SCHEMES["humidity"]["dry"],
        COLOR_SCHEMES["humidity"]["low"],
        COLOR_SCHEMES["humidity"]["comfortable"],
        COLOR_SCHEMES["humidity"]["high"],
    ]

    graph_entities = [
        {"entity": e["entity_id"], "name": e["name"], "color": e["color"]}
        for e in entities
    ]

    return {
        "type": "vertical-stack",
        "cards": [
            # Major section header
            create_bubble_separator("Humidity", "mdi:water-percent", enhanced=True),

            # Info card explaining humidity ranges
            create_info_card(
                "**Optimal humidity:** 30-60% prevents mold growth and maintains comfort.",
                "#3498db"
            ),

            # Sub-section: Current readings
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Current Humidity",
                "icon": "mdi:water-outline",
            },

            # Current value cards
            {
                "type": "horizontal-stack",
                "cards": [
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Enviro",
                        "secondary": "{{ states('sensor.enviro_humidity') }}%",
                        "icon": "mdi:water-percent",
                        "icon_color": "blue",
                    },
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Office",
                        "secondary": "{{ states('sensor.officeht_humidity') }}%",
                        "icon": "mdi:water-percent",
                        "icon_color": "green",
                    },
                ],
            },

            # Sub-section: Humidity history
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Humidity History",
                "icon": "mdi:chart-line",
            },

            # Three-graph row
            {
                "type": "horizontal-stack",
                "cards": [
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Hour",
                            "hours_to_show": 1,
                            "points_per_hour": 60,
                            "line_width": 2,
                            "entities": graph_entities,
                        }),
                        humidity_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last 24 Hours",
                            "hours_to_show": 24,
                            "points_per_hour": 4,
                            "line_width": 2,
                            "entities": graph_entities,
                        }),
                        humidity_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Week",
                            "hours_to_show": 168,
                            "points_per_hour": 1,
                            "line_width": 2,
                            "entities": graph_entities,
                        }),
                        humidity_thresholds
                    ),
                ],
            },
        ],
    }


def create_air_quality_section():
    """Complete air quality section with gas sensors."""
    # Oxidising gas entities (lower resistance = more pollution)
    oxidising_entity = {
        "entity_id": "sensor.enviro_gas_oxidising",
        "name": "Oxidising",
        "color": "#e74c3c",
    }

    # Build thresholds
    oxidising_thresholds = [
        COLOR_SCHEMES["air_quality"]["oxidising"]["poor"],
        COLOR_SCHEMES["air_quality"]["oxidising"]["moderate"],
        COLOR_SCHEMES["air_quality"]["oxidising"]["good"],
        COLOR_SCHEMES["air_quality"]["oxidising"]["excellent"],
    ]

    return {
        "type": "vertical-stack",
        "cards": [
            # Major section header
            create_bubble_separator("Air Quality", "mdi:air-filter", enhanced=True),

            # Info card explaining gas sensors
            create_info_card(
                "**Lower resistance = more pollution.** "
                "Good air quality: >100 kΩ for oxidising gas, >200 kΩ for reducing gas.",
                "#e74c3c"
            ),

            # Sub-section: Oxidising gas
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Oxidising Gas (NO2, O3)",
                "icon": "mdi:molecule",
            },

            # Current value card
            {
                "type": "custom:mushroom-template-card",
                "primary": "Oxidising Gas Resistance",
                "secondary": "{{ states('sensor.enviro_gas_oxidising') }} kΩ",
                "icon": "mdi:gas-cylinder",
                "icon_color": "{% if states('sensor.enviro_gas_oxidising') | float > 100 %}green{% elif states('sensor.enviro_gas_oxidising') | float > 30 %}yellow{% else %}red{% endif %}",
            },

            # Sub-section: History
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Oxidising Gas History",
                "icon": "mdi:chart-line",
            },

            # Three-graph row with inverted color scale
            {
                "type": "horizontal-stack",
                "cards": [
                    add_color_gradient_to_mini_graph(
                        enable_mini_graph_extrema(
                            add_static_title_to_mini_graph({
                                "type": "custom:mini-graph-card",
                                "name": "Last Hour",
                                "hours_to_show": 1,
                                "points_per_hour": 60,
                                "line_width": 2,
                                "lower_bound": 0,
                                "upper_bound": 150,
                                "entities": [
                                    {
                                        "entity": oxidising_entity["entity_id"],
                                        "name": oxidising_entity["name"],
                                    }
                                ],
                            })
                        ),
                        oxidising_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last 24 Hours",
                            "hours_to_show": 24,
                            "points_per_hour": 4,
                            "line_width": 2,
                            "lower_bound": 0,
                            "upper_bound": 150,
                            "entities": [
                                {
                                    "entity": oxidising_entity["entity_id"],
                                    "name": oxidising_entity["name"],
                                }
                            ],
                        }),
                        oxidising_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Week",
                            "hours_to_show": 168,
                            "points_per_hour": 1,
                            "line_width": 2,
                            "lower_bound": 0,
                            "upper_bound": 150,
                            "entities": [
                                {
                                    "entity": oxidising_entity["entity_id"],
                                    "name": oxidising_entity["name"],
                                }
                            ],
                        }),
                        oxidising_thresholds
                    ),
                ],
            },
        ],
    }


def create_complete_dashboard():
    """Create a complete dashboard with all sections."""
    return {
        "views": [
            {
                "title": "Environmental Sensors",
                "path": "environment",
                "cards": [
                    create_temperature_section(),
                    create_humidity_section(),
                    create_air_quality_section(),
                ],
            }
        ],
    }


if __name__ == "__main__":
    import json

    dashboard = create_complete_dashboard()
    print(json.dumps(dashboard, indent=2))
    print("\n✓ Dashboard configuration generated successfully")
    print(f"✓ Total sections: 3 (Temperature, Humidity, Air Quality)")
    print(f"✓ Total graph cards: 9 (3 sections × 3 time ranges)")
    print(f"✓ All titles static: True")
    print(f"✓ Color gradients applied: True")
