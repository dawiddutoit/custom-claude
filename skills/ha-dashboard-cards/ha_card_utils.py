"""Home Assistant Card Utilities - Reusable functions for dashboard cards."""


def add_static_title_to_mini_graph(card: dict) -> dict:
    """
    Force mini-graph-card title to be static using card_mod CSS.

    Problem: mini-graph-card with multiple entities changes the title to the
    entity name when hovering over different sensor lines.

    Solution: Use card_mod CSS to overlay static text via ::after pseudo-element
    and hide the dynamic title.

    Args:
        card: mini-graph-card configuration dictionary

    Returns:
        Modified card with card_mod CSS applied for static title

    Example:
        >>> card = {
        ...     "type": "custom:mini-graph-card",
        ...     "name": "Last Hour",
        ...     "entities": [{"entity": "sensor.temp"}]
        ... }
        >>> add_static_title_to_mini_graph(card)
        {
            "type": "custom:mini-graph-card",
            "name": "Last Hour",
            "card_mod": {
                "style": "... CSS to force static title ..."
            },
            "entities": [{"entity": "sensor.temp"}]
        }

    Reference: See REFERENCE_static_graph_titles.md for full documentation
    """
    if card.get("type") != "custom:mini-graph-card":
        return card

    # Get the card name to use as static title
    card_name = card.get("name", "Graph")

    # Add card_mod to force static title
    # CSS explanation:
    # 1. .header .name - ensure container is visible
    # 2. ::after - inject static content over dynamic title
    # 3. .header .name > * - hide all child elements (dynamic title)
    card["card_mod"] = {
        "style": f"""
            .header .name {{
                visibility: visible !important;
            }}
            .header .name::after {{
                content: "{card_name}" !important;
                visibility: visible !important;
            }}
            .header .name > * {{
                display: none !important;
            }}
        """
    }

    return card


def add_color_gradient_to_mini_graph(
    card: dict,
    thresholds: list[dict]
) -> dict:
    """
    Add color gradient thresholds to mini-graph-card.

    Args:
        card: mini-graph-card configuration dictionary
        thresholds: List of threshold dicts with 'value' and 'color' keys
                   Example: [
                       {"value": 0, "color": "#e74c3c"},
                       {"value": 50, "color": "#f1c40f"},
                       {"value": 100, "color": "#2ecc71"}
                   ]

    Returns:
        Modified card with color_thresholds applied

    Example:
        >>> card = {"type": "custom:mini-graph-card", "name": "Temp"}
        >>> thresholds = [
        ...     {"value": 0, "color": "#3498db"},
        ...     {"value": 20, "color": "#2ecc71"},
        ...     {"value": 30, "color": "#e74c3c"}
        ... ]
        >>> add_color_gradient_to_mini_graph(card, thresholds)
    """
    if card.get("type") != "custom:mini-graph-card":
        return card

    card["color_thresholds"] = thresholds

    # Remove fixed entity colors so gradient can take effect
    for entity in card.get("entities", []):
        if isinstance(entity, dict) and "color" in entity:
            del entity["color"]

    return card


def enable_mini_graph_extrema(card: dict) -> dict:
    """
    Enable min/max extrema markers on mini-graph-card.

    Args:
        card: mini-graph-card configuration dictionary

    Returns:
        Modified card with extrema enabled
    """
    if card.get("type") != "custom:mini-graph-card":
        return card

    if "show" not in card:
        card["show"] = {}

    card["show"]["extrema"] = True

    return card


def create_bubble_separator(
    name: str,
    icon: str,
    enhanced: bool = False
) -> dict:
    """
    Create a bubble-card separator for dashboard sections.

    Args:
        name: Section name displayed in separator
        icon: Material Design Icon (e.g., "mdi:thermometer")
        enhanced: If True, applies gradient background and larger styling

    Returns:
        Bubble-card separator configuration

    Example:
        >>> create_bubble_separator("Temperature", "mdi:thermometer", enhanced=True)
    """
    card = {
        "type": "custom:bubble-card",
        "card_type": "separator",
        "name": name,
        "icon": icon,
    }

    if enhanced:
        card["card_mod"] = {
            "style": """
                ha-card {
                    margin-top: 24px !important;
                    margin-bottom: 16px !important;
                    background: linear-gradient(90deg,
                        transparent 0%,
                        rgba(var(--rgb-primary-text-color), 0.12) 20%,
                        rgba(var(--rgb-primary-text-color), 0.12) 80%,
                        transparent 100%) !important;
                    border-radius: 8px !important;
                    padding: 8px 0 !important;
                }
                .bubble-line {
                    opacity: 1 !important;
                    height: 2px !important;
                }
                .bubble-name {
                    font-size: 18px !important;
                    font-weight: 600 !important;
                }
            """
        }

    return card


def create_info_card(
    content: str,
    border_color: str,
    background_color: str | None = None
) -> dict:
    """
    Create a markdown info card with colored border.

    Args:
        content: Markdown content for the card
        border_color: Hex color for left border (e.g., "#e74c3c")
        background_color: Optional hex color for background
                         (defaults to semi-transparent version of border)

    Returns:
        Markdown card configuration with styling

    Example:
        >>> create_info_card(
        ...     "**Important:** This is critical info",
        ...     "#e74c3c"
        ... )
    """
    if background_color is None:
        # Convert hex to rgba with 8% opacity
        # e.g., #e74c3c -> rgba(231, 76, 60, 0.08)
        hex_color = border_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        background_color = f"rgba({r}, {g}, {b}, 0.08)"

    return {
        "type": "markdown",
        "content": content,
        "card_mod": {
            "style": f"""
                ha-card {{
                    background: {background_color} !important;
                    border-left: 3px solid {border_color} !important;
                    font-size: 13px !important;
                    padding: 10px 14px !important;
                    margin: 6px 0 12px 0 !important;
                    box-shadow: none !important;
                }}
                ha-markdown {{
                    padding: 0 !important;
                }}
            """
        }
    }


# Preset color schemes
COLOR_SCHEMES = {
    "air_quality": {
        "oxidising": {
            "excellent": {"value": 100, "color": "#3498db"},  # Blue
            "good": {"value": 30, "color": "#2ecc71"},        # Green
            "moderate": {"value": 10, "color": "#e67e22"},    # Orange
            "poor": {"value": 0, "color": "#e74c3c"},         # Red
        },
        "reducing": {
            "excellent": {"value": 500, "color": "#3498db"},
            "good": {"value": 200, "color": "#2ecc71"},
            "moderate": {"value": 100, "color": "#e67e22"},
            "poor": {"value": 0, "color": "#e74c3c"},
        },
    },
    "temperature": {
        "cold": {"value": 10, "color": "#3498db"},
        "comfortable": {"value": 18, "color": "#2ecc71"},
        "warm": {"value": 26, "color": "#f1c40f"},
        "hot": {"value": 32, "color": "#e74c3c"},
    },
    "humidity": {
        "dry": {"value": 0, "color": "#e74c3c"},
        "low": {"value": 30, "color": "#2ecc71"},
        "comfortable": {"value": 60, "color": "#f1c40f"},
        "high": {"value": 80, "color": "#e74c3c"},
    },
}
