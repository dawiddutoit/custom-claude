#!/usr/bin/env python3
"""
Multi-tab comparison orchestration script.

Coordinates opening multiple tabs, capturing data, and generating comparison reports.
"""

import json
import sys
from pathlib import Path
from typing import Any


def load_tab_data(data_file: Path) -> list[dict[str, Any]]:
    """Load tab comparison data from JSON file."""
    with open(data_file) as f:
        return json.load(f)


def compare_snapshots(tabs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare accessibility snapshots across tabs."""
    comparison = {
        "total_tabs": len(tabs),
        "differences": [],
        "common_elements": [],
    }

    # Extract element counts (use existing or calculate from snapshot)
    for i, tab in enumerate(tabs):
        if "element_count" not in tab:
            snapshot = tab.get("snapshot", "")
            element_count = snapshot.count("\n") if snapshot else 0
            tab["element_count"] = element_count

    # Find differences
    if len(tabs) >= 2:
        baseline = tabs[0]
        for i, tab in enumerate(tabs[1:], start=1):
            diff_pct = abs(tab["element_count"] - baseline["element_count"]) / max(baseline["element_count"], 1) * 100
            if diff_pct > 10:  # >10% difference
                comparison["differences"].append({
                    "tab_index": i,
                    "url": tab["url"],
                    "diff_percentage": round(diff_pct, 2),
                    "baseline_elements": baseline["element_count"],
                    "current_elements": tab["element_count"],
                })

    return comparison


def generate_summary(tabs: list[dict[str, Any]], comparison: dict[str, Any]) -> str:
    """Generate text summary of comparison."""
    summary = ["# Multi-Tab Comparison Summary\n"]
    summary.append(f"**Total Tabs Compared:** {comparison['total_tabs']}\n")

    summary.append("\n## Pages Analyzed\n")
    for i, tab in enumerate(tabs):
        summary.append(f"{i + 1}. {tab['url']} ({tab['element_count']} elements)")

    if comparison["differences"]:
        summary.append("\n## Significant Differences Detected\n")
        for diff in comparison["differences"]:
            summary.append(
                f"- Tab {diff['tab_index'] + 1} ({diff['url']}): "
                f"{diff['diff_percentage']}% difference "
                f"({diff['current_elements']} vs {diff['baseline_elements']} elements)"
            )
    else:
        summary.append("\n**No significant structural differences detected** (within 10% threshold)")

    return "\n".join(summary)


def main():
    if len(sys.argv) < 2:
        print("Usage: compare_tabs.py <tab-data.json>")
        sys.exit(1)

    data_file = Path(sys.argv[1])
    if not data_file.exists():
        print(f"Error: File not found: {data_file}")
        sys.exit(1)

    tabs = load_tab_data(data_file)
    comparison = compare_snapshots(tabs)
    summary = generate_summary(tabs, comparison)

    print(summary)

    # Save comparison results
    output_file = data_file.parent / f"{data_file.stem}_comparison.json"
    with open(output_file, "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"\n✅ Comparison saved to: {output_file}")


if __name__ == "__main__":
    main()
