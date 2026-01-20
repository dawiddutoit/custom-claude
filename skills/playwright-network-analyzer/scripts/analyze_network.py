#!/usr/bin/env python3
"""
Network Request Analyzer for Playwright MCP browser_network_requests output.

Categorizes HTTP requests into API calls, static resources, failed requests,
and slow requests. Generates Markdown reports with actionable insights.

Usage:
    python analyze_network.py requests.json
    python analyze_network.py requests.json --threshold 2000
    python analyze_network.py requests.json --domain api.example.com
    python analyze_network.py requests.json -o report.md
    python analyze_network.py requests.json --csv output.csv
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class NetworkAnalyzer:
    """Analyzes network requests from Playwright browser_network_requests."""

    STATIC_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".webp",
        ".ico",
        ".css",
        ".js",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp4",
        ".webm",
        ".mp3",
    }

    def __init__(self, threshold_ms: int = 1000, domain_filter: str | None = None):
        self.threshold_ms = threshold_ms
        self.domain_filter = domain_filter
        self.requests: list[dict[str, Any]] = []
        self.api_calls: list[dict[str, Any]] = []
        self.static_resources: list[dict[str, Any]] = []
        self.failed_requests: list[dict[str, Any]] = []
        self.slow_requests: list[dict[str, Any]] = []
        self.redirects: list[dict[str, Any]] = []

    def load_requests(self, filepath: Path) -> None:
        """Load network requests from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
            if isinstance(data, list):
                self.requests = data
            elif isinstance(data, dict) and "requests" in data:
                self.requests = data["requests"]
            else:
                raise ValueError(
                    "Invalid JSON format. Expected array or object with 'requests' key"
                )

    def is_static_resource(self, url: str) -> bool:
        """Check if URL is a static resource based on file extension."""
        parsed = urlparse(url)
        path = Path(parsed.path)
        return path.suffix.lower() in self.STATIC_EXTENSIONS

    def matches_domain_filter(self, url: str) -> bool:
        """Check if URL matches domain filter (if set)."""
        if not self.domain_filter:
            return True
        parsed = urlparse(url)
        return self.domain_filter in parsed.netloc

    def categorize_requests(self) -> None:
        """Categorize requests into API calls, static resources, failures, slow."""
        for req in self.requests:
            url = req.get("url", "")
            status = req.get("status", 0)
            timing = req.get("timing", {})
            duration_ms = timing.get("total", 0) if timing else 0

            # Apply domain filter
            if not self.matches_domain_filter(url):
                continue

            # Categorize by status code
            if 400 <= status < 600:
                self.failed_requests.append(req)
            elif 300 <= status < 400:
                self.redirects.append(req)

            # Categorize by resource type
            if self.is_static_resource(url):
                self.static_resources.append(req)
            else:
                self.api_calls.append(req)

            # Check for slow requests
            if duration_ms > self.threshold_ms:
                self.slow_requests.append(req)

    def detect_patterns(self) -> list[str]:
        """Detect common network patterns (N+1 queries, etc.)."""
        patterns = []

        # Detect N+1 queries (multiple similar URLs)
        url_counts = defaultdict(int)
        url_base_counts = defaultdict(list)

        for req in self.api_calls:
            url = req.get("url", "")
            parsed = urlparse(url)
            base_path = parsed.path.rsplit("/", 1)[0] if "/" in parsed.path else parsed.path
            url_counts[url] += 1
            url_base_counts[base_path].append(url)

        # Flag if base path has multiple similar URLs
        for base_path, urls in url_base_counts.items():
            if len(urls) >= 5 and len(set(urls)) >= 5:
                patterns.append(
                    f"N+1 Query Pattern: {len(urls)} requests to {base_path}/* "
                    f"(consider batch endpoint)"
                )

        # Detect authentication issues (multiple 401s)
        auth_failures = [r for r in self.failed_requests if r.get("status") == 401]
        if len(auth_failures) >= 3:
            patterns.append(
                f"Authentication Issues: {len(auth_failures)} requests failed with 401 "
                f"(check auth flow)"
            )

        # Detect server errors (multiple 500s)
        server_errors = [r for r in self.failed_requests if 500 <= r.get("status", 0) < 600]
        if len(server_errors) >= 2:
            patterns.append(
                f"Server Errors: {len(server_errors)} requests failed with 5xx "
                f"(backend issues)"
            )

        return patterns

    def generate_markdown_report(self) -> str:
        """Generate Markdown report with categorized analysis."""
        lines = ["# Network Analysis Report\n"]

        # Summary
        total_requests = len(
            [r for r in self.requests if self.matches_domain_filter(r.get("url", ""))]
        )
        lines.append(f"**Total Requests:** {total_requests}\n")
        lines.append(f"**API Calls:** {len(self.api_calls)}")
        lines.append(f"**Static Resources:** {len(self.static_resources)}")
        lines.append(f"**Failed Requests:** {len(self.failed_requests)}")
        lines.append(f"**Slow Requests (>{self.threshold_ms}ms):** {len(self.slow_requests)}\n")

        # Failed Requests
        if self.failed_requests:
            lines.append("## Failed Requests\n")
            for req in self.failed_requests:
                method = req.get("method", "GET")
                url = req.get("url", "")
                status = req.get("status", 0)
                timing = req.get("timing", {})
                duration = timing.get("total", 0) if timing else 0
                lines.append(f"- {method} `{url}` - **{status}** ({duration}ms)")
            lines.append("")

        # Slow Requests
        if self.slow_requests:
            lines.append(f"## Slow Requests (>{self.threshold_ms}ms)\n")
            for req in sorted(
                self.slow_requests,
                key=lambda r: r.get("timing", {}).get("total", 0) if r.get("timing") else 0,
                reverse=True,
            ):
                method = req.get("method", "GET")
                url = req.get("url", "")
                status = req.get("status", 0)
                timing = req.get("timing", {})
                duration = timing.get("total", 0) if timing else 0
                lines.append(f"- {method} `{url}` - {status} ({duration}ms)")
            lines.append("")

        # Patterns
        patterns = self.detect_patterns()
        if patterns:
            lines.append("## Detected Patterns\n")
            for pattern in patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        # API Calls Summary
        if self.api_calls:
            lines.append("## API Calls\n")
            successful = [r for r in self.api_calls if 200 <= r.get("status", 0) < 300]
            lines.append(f"**Total:** {len(self.api_calls)} ({len(successful)} successful)\n")
            for req in self.api_calls[:10]:  # Limit to first 10
                method = req.get("method", "GET")
                url = req.get("url", "")
                status = req.get("status", 0)
                timing = req.get("timing", {})
                duration = timing.get("total", 0) if timing else 0
                lines.append(f"- {method} `{url}` - {status} ({duration}ms)")
            if len(self.api_calls) > 10:
                lines.append(f"- ... and {len(self.api_calls) - 10} more")
            lines.append("")

        return "\n".join(lines)

    def generate_csv(self) -> str:
        """Generate CSV report with all request details."""
        lines = ["Method,URL,Status,Duration (ms),Type"]

        all_requests = [r for r in self.requests if self.matches_domain_filter(r.get("url", ""))]

        for req in all_requests:
            method = req.get("method", "GET")
            url = req.get("url", "")
            status = req.get("status", 0)
            timing = req.get("timing", {})
            duration = timing.get("total", 0) if timing else 0
            request_type = "Static" if self.is_static_resource(url) else "API"

            # CSV escaping
            url_escaped = url.replace('"', '""')
            lines.append(f'{method},"{url_escaped}",{status},{duration},{request_type}')

        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze network requests from Playwright browser_network_requests"
    )
    parser.add_argument("input", type=Path, help="JSON file with network requests")
    parser.add_argument(
        "--threshold",
        type=int,
        default=1000,
        help="Threshold in ms for slow requests (default: 1000)",
    )
    parser.add_argument("--domain", help="Filter requests to specific domain")
    parser.add_argument("-o", "--output", type=Path, help="Output file for Markdown report")
    parser.add_argument("--csv", type=Path, help="Output file for CSV export")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    analyzer = NetworkAnalyzer(threshold_ms=args.threshold, domain_filter=args.domain)

    try:
        analyzer.load_requests(args.input)
        analyzer.categorize_requests()

        # Generate Markdown report
        markdown_report = analyzer.generate_markdown_report()

        if args.output:
            args.output.write_text(markdown_report)
            print(f"Markdown report written to {args.output}")
        else:
            print(markdown_report)

        # Generate CSV if requested
        if args.csv:
            csv_report = analyzer.generate_csv()
            args.csv.write_text(csv_report)
            print(f"CSV report written to {args.csv}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
