# Complete Dashboard Section Examples

## Temperature Section (Full Implementation)

```python
from ha_card_utils import (
    create_bubble_separator,
    create_info_card,
    add_static_title_to_mini_graph,
    add_color_gradient_to_mini_graph,
    COLOR_SCHEMES,
)

def create_temperature_section(entities: list[dict]):
    """
    Create complete temperature section.

    Args:
        entities: List of dicts with keys:
            - entity_id: Entity ID (e.g., "sensor.office_temperature")
            - name: Display name (e.g., "Office")
            - color: Graph line color (e.g., "#2ecc71")
    """
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
            # Section header
            create_bubble_separator("Temperature", "mdi:thermometer", enhanced=True),

            # Current readings sub-section
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Current Temperatures",
                "icon": "mdi:home-thermometer",
            },

            # Mushroom template cards showing current values
            {
                "type": "grid",
                "columns": 3,
                "cards": [
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": e["name"],
                        "secondary": "{{ states('" + e["entity_id"] + "') }}°C",
                        "icon": "mdi:thermometer",
                        "icon_color": "blue",
                    }
                    for e in entities
                ],
            },

            # History sub-section
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Temperature History",
                "icon": "mdi:chart-line",
            },

            # Three-graph row with color gradients
            {
                "type": "horizontal-stack",
                "cards": [
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Hour",
                            "hours_to_show": 1,
                            "entities": graph_entities,
                        }),
                        temp_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last 24 Hours",
                            "hours_to_show": 24,
                            "entities": graph_entities,
                        }),
                        temp_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Week",
                            "hours_to_show": 168,
                            "entities": graph_entities,
                        }),
                        temp_thresholds
                    ),
                ],
            },
        ],
    }

# Usage
entities = [
    {"entity_id": "sensor.office_temperature", "name": "Office", "color": "#2ecc71"},
    {"entity_id": "sensor.bedroom_temperature", "name": "Bedroom", "color": "#3498db"},
    {"entity_id": "sensor.living_room_temperature", "name": "Living", "color": "#e74c3c"},
]

temp_section = create_temperature_section(entities)
```

## Humidity Section

```python
def create_humidity_section(entities: list[dict]):
    """Create humidity section with U-shaped gradient (dry/comfortable/high)."""
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
            create_bubble_separator("Humidity", "mdi:water-percent", enhanced=True),
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Current Humidity",
                "icon": "mdi:water",
            },
            {
                "type": "grid",
                "columns": 3,
                "cards": [
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": e["name"],
                        "secondary": "{{ states('" + e["entity_id"] + "') }}%",
                        "icon": "mdi:water-percent",
                        "icon_color": "cyan",
                    }
                    for e in entities
                ],
            },
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Humidity History",
                "icon": "mdi:chart-line",
            },
            {
                "type": "horizontal-stack",
                "cards": [
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Hour",
                            "hours_to_show": 1,
                            "entities": graph_entities,
                        }),
                        humidity_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last 24 Hours",
                            "hours_to_show": 24,
                            "entities": graph_entities,
                        }),
                        humidity_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Week",
                            "hours_to_show": 168,
                            "entities": graph_entities,
                        }),
                        humidity_thresholds
                    ),
                ],
            },
        ],
    }
```

## Air Quality Section (Gas Sensors)

```python
def create_air_quality_section(oxidising_entity: str, reducing_entity: str):
    """Create air quality section with explanation cards."""
    oxidising_thresholds = [
        COLOR_SCHEMES["air_quality"]["oxidising"]["poor"],
        COLOR_SCHEMES["air_quality"]["oxidising"]["moderate"],
        COLOR_SCHEMES["air_quality"]["oxidising"]["good"],
        COLOR_SCHEMES["air_quality"]["oxidising"]["excellent"],
    ]

    reducing_thresholds = [
        COLOR_SCHEMES["air_quality"]["reducing"]["poor"],
        COLOR_SCHEMES["air_quality"]["reducing"]["moderate"],
        COLOR_SCHEMES["air_quality"]["reducing"]["good"],
        COLOR_SCHEMES["air_quality"]["reducing"]["excellent"],
    ]

    return {
        "type": "vertical-stack",
        "cards": [
            create_bubble_separator("Air Quality", "mdi:air-filter", enhanced=True),

            # Info card explaining gas sensors
            create_info_card(
                "**Gas sensor readings:** Lower resistance = more pollution detected. "
                "Good air quality typically shows >100 kΩ for oxidising, >200 kΩ for reducing.",
                "#3498db"
            ),

            # Oxidising gas sub-section
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Oxidising Gas (NO2, CO)",
                "icon": "mdi:molecule",
            },
            {
                "type": "horizontal-stack",
                "cards": [
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Hour",
                            "hours_to_show": 1,
                            "entities": [{"entity": oxidising_entity, "name": "Oxidising"}],
                        }),
                        oxidising_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last 24 Hours",
                            "hours_to_show": 24,
                            "entities": [{"entity": oxidising_entity, "name": "Oxidising"}],
                        }),
                        oxidising_thresholds
                    ),
                ],
            },

            # Reducing gas sub-section
            {
                "type": "custom:bubble-card",
                "card_type": "separator",
                "name": "Reducing Gas (CO, H2S)",
                "icon": "mdi:molecule",
            },
            {
                "type": "horizontal-stack",
                "cards": [
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last Hour",
                            "hours_to_show": 1,
                            "entities": [{"entity": reducing_entity, "name": "Reducing"}],
                        }),
                        reducing_thresholds
                    ),
                    add_color_gradient_to_mini_graph(
                        add_static_title_to_mini_graph({
                            "type": "custom:mini-graph-card",
                            "name": "Last 24 Hours",
                            "hours_to_show": 24,
                            "entities": [{"entity": reducing_entity, "name": "Reducing"}],
                        }),
                        reducing_thresholds
                    ),
                ],
            },
        ],
    }
```

## Multi-Sensor Dashboard (Complete)

```python
def create_environmental_dashboard(config: dict):
    """
    Create complete environmental dashboard.

    Args:
        config: Dict with keys:
            - temperature_entities: List of temp sensor dicts
            - humidity_entities: List of humidity sensor dicts
            - oxidising_entity: Oxidising gas sensor entity ID
            - reducing_entity: Reducing gas sensor entity ID
    """
    return {
        "views": [
            {
                "title": "Environmental Monitoring",
                "path": "environmental-monitoring",
                "cards": [
                    # Temperature section
                    create_temperature_section(config["temperature_entities"]),

                    # Spacer
                    {"type": "markdown", "content": "---"},

                    # Humidity section
                    create_humidity_section(config["humidity_entities"]),

                    # Spacer
                    {"type": "markdown", "content": "---"},

                    # Air quality section
                    create_air_quality_section(
                        config["oxidising_entity"],
                        config["reducing_entity"]
                    ),
                ],
            }
        ]
    }

# Usage
dashboard_config = create_environmental_dashboard({
    "temperature_entities": [
        {"entity_id": "sensor.office_temperature", "name": "Office", "color": "#2ecc71"},
        {"entity_id": "sensor.bedroom_temperature", "name": "Bedroom", "color": "#3498db"},
    ],
    "humidity_entities": [
        {"entity_id": "sensor.office_humidity", "name": "Office", "color": "#2ecc71"},
        {"entity_id": "sensor.bedroom_humidity", "name": "Bedroom", "color": "#3498db"},
    ],
    "oxidising_entity": "sensor.enviro_oxidising",
    "reducing_entity": "sensor.enviro_reducing",
})
```

## Section Structure Best Practices

1. **Enhanced separator** for major sections (Temperature, Humidity, Air Quality)
2. **Standard separator** for sub-sections (Current Readings, History)
3. **Grid layout** for current value cards (Mushroom template cards)
4. **Horizontal-stack** for time-range graphs (1hr, 24hr, 1wk)
5. **Info cards** for context (gas sensor explanations, warnings)
6. **Spacers** between major sections (markdown with `---`)

## Color Consistency

Use consistent colors across sections:
- **Blue** (`#3498db`) - Cold, water, informational
- **Green** (`#2ecc71`) - Comfortable, normal, good
- **Yellow** (`#f1c40f`) - Warm, moderate, caution
- **Orange** (`#e67e22`) - Warning, moderate concern
- **Red** (`#e74c3c`) - Hot, critical, poor quality
- **Cyan** (`#1abc9c`) - Humidity, moisture

## Testing Checklist

- [ ] Static titles remain fixed on hover
- [ ] Color gradients display correctly
- [ ] Separators render with proper styling
- [ ] Info cards have correct border colors
- [ ] All entity IDs exist in Home Assistant
- [ ] Graphs show data for all time ranges
- [ ] Mobile layout displays correctly
- [ ] Browser console shows no errors
