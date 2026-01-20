#!/usr/bin/env python3
"""
Generate HTML comparison report from tab data.

Creates side-by-side visual comparison with screenshots and extracted data.
"""

import base64
import json
import sys
from pathlib import Path
from typing import Any


def load_template(template_path: Path) -> str:
    """Load HTML template."""
    with open(template_path) as f:
        return f.read()


def encode_image(image_path: Path) -> str:
    """Encode image to base64 for embedding."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_report(tabs: list[dict[str, Any]], template: str, output_path: Path) -> None:
    """Generate HTML comparison report."""
    # Build tab cards HTML
    tab_cards = []
    for i, tab in enumerate(tabs):
        screenshot_data = ""
        if "screenshot" in tab and Path(tab["screenshot"]).exists():
            screenshot_data = encode_image(Path(tab["screenshot"]))

        card_html = f"""
        <div class="tab-card">
            <div class="tab-header">
                <h3>Tab {i + 1}</h3>
                <a href="{tab['url']}" target="_blank">{tab['url']}</a>
            </div>
            <div class="tab-screenshot">
                {"<img src='data:image/png;base64," + screenshot_data + "' alt='Screenshot'>" if screenshot_data else "<p>No screenshot available</p>"}
            </div>
            <div class="tab-data">
                <h4>Extracted Data</h4>
                <pre>{json.dumps(tab.get('data', {}), indent=2)}</pre>
            </div>
            <div class="tab-stats">
                <p><strong>Elements:</strong> {tab.get('element_count', 0)}</p>
                <p><strong>Timestamp:</strong> {tab.get('timestamp', 'N/A')}</p>
            </div>
        </div>
        """
        tab_cards.append(card_html)

    # Replace placeholders in template
    report_html = template.replace("{{TAB_CARDS}}", "\n".join(tab_cards))
    report_html = report_html.replace("{{TOTAL_TABS}}", str(len(tabs)))

    # Write output
    with open(output_path, "w") as f:
        f.write(report_html)


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_comparison_report.py <tab-data.json> <output.html>")
        sys.exit(1)

    data_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not data_file.exists():
        print(f"Error: File not found: {data_file}")
        sys.exit(1)

    # Load tab data
    with open(data_file) as f:
        tabs = json.load(f)

    # Load template
    skill_dir = Path(__file__).parent.parent
    template_path = skill_dir / "assets" / "report-template.html"

    if not template_path.exists():
        print(f"Error: Template not found: {template_path}")
        sys.exit(1)

    template = load_template(template_path)

    # Generate report
    generate_report(tabs, template, output_file)

    print(f"✅ Comparison report generated: {output_file}")


if __name__ == "__main__":
    main()
