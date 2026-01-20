#!/usr/bin/env python3
"""
Generate comprehensive E2E test reports from evidence files.

Usage:
    python generate_test_report.py \\
        --test-name "Login Flow" \\
        --url "http://localhost:3000" \\
        --initial-snapshot initial-state.md \\
        --final-snapshot final-state.md \\
        --screenshots initial.png,final.png \\
        --console-logs console.json \\
        --network-requests network.json \\
        --output test-report.md
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def parse_args():
    parser = argparse.ArgumentParser(description="Generate E2E test report")
    parser.add_argument("--test-name", required=True, help="Test name")
    parser.add_argument("--url", required=True, help="Application URL")
    parser.add_argument("--initial-snapshot", help="Initial accessibility snapshot")
    parser.add_argument("--final-snapshot", help="Final accessibility snapshot")
    parser.add_argument("--screenshots", help="Comma-separated screenshot paths")
    parser.add_argument("--console-logs", help="Console logs JSON file")
    parser.add_argument("--network-requests", help="Network requests JSON file")
    parser.add_argument("--status", choices=["passed", "failed"], default="passed")
    parser.add_argument("--failure-reason", help="Reason for failure")
    parser.add_argument("--duration", type=float, help="Test duration in seconds")
    parser.add_argument("--output", required=True, help="Output report path")
    return parser.parse_args()


def load_json_file(path: Optional[str]) -> dict:
    """Load JSON file or return empty dict."""
    if not path or not Path(path).exists():
        return {}
    with open(path) as f:
        return json.load(f)


def format_console_logs(logs: dict) -> str:
    """Format console logs for report."""
    if not logs:
        return "No console logs captured.\n"

    errors = [log for log in logs.get("messages", []) if log.get("level") == "error"]
    warnings = [log for log in logs.get("messages", []) if log.get("level") == "warning"]

    output = []
    if errors:
        output.append("### Errors\n")
        for i, error in enumerate(errors, 1):
            output.append(f"{i}. `{error.get('text', 'Unknown error')}`\n")

    if warnings:
        output.append("\n### Warnings\n")
        for i, warning in enumerate(warnings, 1):
            output.append(f"{i}. `{warning.get('text', 'Unknown warning')}`\n")

    return "".join(output) if output else "No errors or warnings.\n"


def format_network_requests(requests: dict) -> str:
    """Format network requests for report."""
    if not requests:
        return "No network requests captured.\n"

    req_list = requests.get("requests", [])
    if not req_list:
        return "No network requests captured.\n"

    output = ["| Method | URL | Status | Type |\n", "|--------|-----|--------|------|\n"]

    for req in req_list:
        method = req.get("method", "?")
        url = req.get("url", "?")
        status = req.get("status", "?")
        req_type = req.get("resourceType", "?")

        # Truncate long URLs
        if len(url) > 60:
            url = url[:57] + "..."

        output.append(f"| {method} | {url} | {status} | {req_type} |\n")

    return "".join(output)


def format_screenshots(screenshots: Optional[str]) -> str:
    """Format screenshot gallery."""
    if not screenshots:
        return "No screenshots captured.\n"

    paths = [s.strip() for s in screenshots.split(",")]
    output = []

    for path in paths:
        name = Path(path).stem.replace("-", " ").title()
        output.append(f"### {name}\n\n")
        output.append(f"![{name}]({path})\n\n")

    return "".join(output)


def generate_recommendations(status: str, console_logs: dict, network_requests: dict) -> str:
    """Generate recommendations based on test results."""
    if status == "passed":
        return "Test passed successfully. No recommendations.\n"

    recommendations = []

    # Check for console errors
    errors = [log for log in console_logs.get("messages", []) if log.get("level") == "error"]
    if errors:
        recommendations.append("- Investigate console errors listed above")
        recommendations.append("- Add error handling for failed operations")

    # Check for network failures
    failed_requests = [
        req for req in network_requests.get("requests", [])
        if str(req.get("status", "200")).startswith(("4", "5"))
    ]
    if failed_requests:
        recommendations.append("- Review failed API requests")
        recommendations.append("- Verify API endpoint availability")
        recommendations.append("- Check request authentication/authorization")

    if not recommendations:
        recommendations.append("- Review test execution flow")
        recommendations.append("- Check application state before test")

    return "\n".join(recommendations) + "\n"


def generate_report(args):
    """Generate test report markdown."""
    timestamp = datetime.now().isoformat()
    console_logs = load_json_file(args.console_logs)
    network_requests = load_json_file(args.network_requests)

    status_emoji = "✅" if args.status == "passed" else "❌"
    status_text = "PASSED" if args.status == "passed" else "FAILED"

    report_lines = [
        f"# {status_emoji} E2E Test Report: {args.test_name}\n\n",
        f"**Status:** {status_text}\n",
        f"**Date:** {timestamp}\n",
        f"**URL:** {args.url}\n",
    ]

    if args.duration:
        report_lines.append(f"**Duration:** {args.duration:.2f}s\n")

    report_lines.append("\n---\n\n")

    # Test Summary
    report_lines.append("## Test Summary\n\n")

    console_error_count = len([
        log for log in console_logs.get("messages", [])
        if log.get("level") == "error"
    ])
    network_failure_count = len([
        req for req in network_requests.get("requests", [])
        if str(req.get("status", "200")).startswith(("4", "5"))
    ])

    report_lines.append(f"- Console Errors: {console_error_count}\n")
    report_lines.append(f"- Network Failures: {network_failure_count}\n\n")

    if args.failure_reason:
        report_lines.append(f"**Failure Reason:** {args.failure_reason}\n\n")

    # Console Logs
    report_lines.append("## Console Logs\n\n")
    report_lines.append(format_console_logs(console_logs))
    report_lines.append("\n")

    # Network Requests
    report_lines.append("## Network Requests\n\n")
    report_lines.append(format_network_requests(network_requests))
    report_lines.append("\n")

    # Screenshots
    if args.screenshots:
        report_lines.append("## Screenshots\n\n")
        report_lines.append(format_screenshots(args.screenshots))

    # Snapshots
    if args.initial_snapshot or args.final_snapshot:
        report_lines.append("## Accessibility Snapshots\n\n")
        if args.initial_snapshot:
            report_lines.append(f"- Initial State: [{args.initial_snapshot}]({args.initial_snapshot})\n")
        if args.final_snapshot:
            report_lines.append(f"- Final State: [{args.final_snapshot}]({args.final_snapshot})\n")
        report_lines.append("\n")

    # Recommendations
    report_lines.append("## Recommendations\n\n")
    report_lines.append(generate_recommendations(args.status, console_logs, network_requests))

    # Write report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(report_lines))

    print(f"✅ Report generated: {output_path}")
    print(f"   Status: {status_text}")
    print(f"   Console Errors: {console_error_count}")
    print(f"   Network Failures: {network_failure_count}")


if __name__ == "__main__":
    args = parse_args()
    generate_report(args)
