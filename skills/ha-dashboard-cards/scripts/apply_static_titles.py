#!/usr/bin/env python3
"""
Apply static titles to all mini-graph-card cards in a dashboard.

This script connects to Home Assistant via WebSocket API, retrieves a dashboard
configuration, applies static title CSS to all mini-graph-card instances, and
saves the updated configuration back to Home Assistant.

Usage:
    python apply_static_titles.py [dashboard_url_path]

Examples:
    python apply_static_titles.py enviro-plus
    python apply_static_titles.py climate-weather

Environment Variables:
    HA_URL - Home Assistant URL (default: http://192.168.68.123:8123)
    HA_LONG_LIVED_TOKEN - Long-lived access token (required)
"""

import json
import os
import sys
import websocket


def add_static_title_css(card: dict) -> dict:
    """Add card_mod CSS to force static title on mini-graph-card."""
    if card.get("type") != "custom:mini-graph-card":
        return card

    card_name = card.get("name", "Graph")

    # Add card_mod to force static title
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


def process_cards_recursive(cards: list) -> int:
    """
    Recursively process all cards in a list, applying static title CSS.

    Args:
        cards: List of card dictionaries

    Returns:
        Count of mini-graph-card cards processed
    """
    count = 0

    for card in cards:
        if not isinstance(card, dict):
            continue

        # Process this card if it's a mini-graph-card
        if card.get("type") == "custom:mini-graph-card":
            add_static_title_css(card)
            count += 1
            print(f"  ✓ Applied to: {card.get('name', 'Unnamed graph')}")

        # Recursively process nested cards
        if "cards" in card:
            count += process_cards_recursive(card["cards"])

    return count


def apply_static_titles_to_dashboard(url_path: str) -> bool:
    """
    Apply static titles to all mini-graph cards in a dashboard.

    Args:
        url_path: Dashboard URL path (e.g., "enviro-plus")

    Returns:
        True if successful, False otherwise
    """
    ha_url = os.environ.get("HA_URL", "http://192.168.68.123:8123")
    ha_token = os.environ.get("HA_LONG_LIVED_TOKEN")

    if not ha_token:
        print("❌ Error: HA_LONG_LIVED_TOKEN environment variable not set")
        print("   Run: source ~/.zshrc")
        return False

    # Connect to WebSocket API
    ws_url = ha_url.replace("http://", "ws://").replace("https://", "wss://")
    ws_url = f"{ws_url}/api/websocket"

    print(f"Connecting to {ws_url}...")

    try:
        ws = websocket.create_connection(ws_url, timeout=30)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    msg_id = 1

    try:
        # 1. Receive auth_required
        auth_required = json.loads(ws.recv())
        if auth_required.get("type") != "auth_required":
            print(f"❌ Unexpected message: {auth_required}")
            return False

        # 2. Send auth
        ws.send(json.dumps({
            "type": "auth",
            "access_token": ha_token,
        }))

        # 3. Receive auth_ok
        auth_result = json.loads(ws.recv())
        if auth_result.get("type") != "auth_ok":
            print(f"❌ Authentication failed: {auth_result}")
            return False

        print("✓ Authenticated")

        # 4. Get dashboard config
        print(f"Fetching dashboard: {url_path}")
        ws.send(json.dumps({
            "id": msg_id,
            "type": "lovelace/config",
            "url_path": url_path,
        }))
        msg_id += 1

        config_result = json.loads(ws.recv())
        if not config_result.get("success"):
            print(f"❌ Failed to get dashboard config: {config_result.get('error')}")
            return False

        config = config_result["result"]
        print(f"✓ Dashboard loaded ({len(config.get('views', []))} views)")

        # 5. Process all cards in all views
        total_processed = 0
        for view in config.get("views", []):
            view_title = view.get("title", "Untitled")
            print(f"\nProcessing view: {view_title}")

            if "cards" in view:
                count = process_cards_recursive(view["cards"])
                total_processed += count

        if total_processed == 0:
            print("\n⚠️  No mini-graph-card cards found in dashboard")
            return True

        print(f"\n✓ Processed {total_processed} mini-graph-card(s)")

        # 6. Save updated config
        print("\nSaving updated dashboard...")
        ws.send(json.dumps({
            "id": msg_id,
            "type": "lovelace/config/save",
            "url_path": url_path,
            "config": config,
        }))
        msg_id += 1

        save_result = json.loads(ws.recv())
        if not save_result.get("success"):
            print(f"❌ Failed to save dashboard: {save_result.get('error')}")
            return False

        print("✓ Dashboard updated successfully")
        print(f"\nView dashboard at: {ha_url}/{url_path}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        ws.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python apply_static_titles.py [dashboard_url_path]")
        print("\nExamples:")
        print("  python apply_static_titles.py enviro-plus")
        print("  python apply_static_titles.py climate-weather")
        print("\nTo list available dashboards:")
        print("  python list_dashboards.py")
        sys.exit(1)

    url_path = sys.argv[1]
    success = apply_static_titles_to_dashboard(url_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
