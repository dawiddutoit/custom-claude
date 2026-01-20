#!/usr/bin/env python3
"""
Parse validation error messages from browser snapshots.

This script extracts validation error messages from Playwright browser snapshot
files (.md format) and provides structured output for test reports.

Usage:
    python parse_validation_errors.py snapshot.md
    python parse_validation_errors.py snapshot.md --json
    python parse_validation_errors.py snapshot.md --field "Email"
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class ValidationError:
    """Represents a validation error found in a snapshot."""

    def __init__(self, field: str, message: str, error_type: str = "unknown"):
        self.field = field
        self.message = message
        self.error_type = error_type

    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
            "type": self.error_type
        }

    def __repr__(self) -> str:
        return f"ValidationError(field='{self.field}', message='{self.message}')"


class SnapshotParser:
    """Parses browser snapshots to extract validation errors."""

    # Common validation keywords
    VALIDATION_KEYWORDS = [
        "required", "invalid", "must", "minimum", "maximum",
        "please enter", "please select", "please provide",
        "cannot be", "should be", "must be", "too short",
        "too long", "does not match", "not valid", "error"
    ]

    def __init__(self, snapshot_path: Path):
        self.snapshot_path = snapshot_path
        self.content = self._read_snapshot()

    def _read_snapshot(self) -> str:
        """Read snapshot file content."""
        try:
            return self.snapshot_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to read snapshot: {e}")

    def extract_errors(self) -> List[ValidationError]:
        """Extract all validation errors from snapshot."""
        errors = []

        # Pattern 1: error: "message"
        errors.extend(self._extract_error_attribute())

        # Pattern 2: aria-invalid with aria-describedby
        errors.extend(self._extract_aria_errors())

        # Pattern 3: alert elements with error messages
        errors.extend(self._extract_alert_errors())

        # Pattern 4: text containing validation keywords
        errors.extend(self._extract_validation_text())

        return self._deduplicate_errors(errors)

    def _extract_error_attribute(self) -> List[ValidationError]:
        """Extract errors from error: 'message' pattern."""
        errors = []
        # Match: error: "message" or error: 'message'
        pattern = r'error:\s*["\']([^"\']+)["\']'

        for match in re.finditer(pattern, self.content, re.IGNORECASE):
            message = match.group(1)
            # Try to find associated field name before the error
            field = self._find_field_before_position(match.start())
            errors.append(ValidationError(field, message, "inline"))

        return errors

    def _extract_aria_errors(self) -> List[ValidationError]:
        """Extract errors from aria-invalid and aria-describedby."""
        errors = []

        # Find elements with aria-invalid="true"
        invalid_pattern = r'(\w+)\s+"([^"]+)"[^\n]*aria-invalid:\s*"true"'

        for match in re.finditer(invalid_pattern, self.content):
            element_type = match.group(1)
            field_name = match.group(2)

            # Look for associated error message via aria-describedby
            describedby_pattern = rf'aria-describedby:\s*"([^"]+)"'
            desc_match = re.search(describedby_pattern, self.content[match.start():match.end() + 200])

            if desc_match:
                error_id = desc_match.group(1)
                # Find the error message element
                error_msg = self._find_error_by_id(error_id)
                if error_msg:
                    errors.append(ValidationError(field_name, error_msg, "aria"))

        return errors

    def _extract_alert_errors(self) -> List[ValidationError]:
        """Extract errors from alert elements."""
        errors = []

        # Find alert elements
        alert_pattern = r'alert[^\n]*\n((?:\s+text:\s*"[^"]+"\n?)+)'

        for match in re.finditer(alert_pattern, self.content, re.IGNORECASE):
            alert_block = match.group(1)

            # Extract all text within the alert
            text_pattern = r'text:\s*"([^"]+)"'
            for text_match in re.finditer(text_pattern, alert_block):
                message = text_match.group(1)

                # Check if it's a validation message
                if self._is_validation_message(message):
                    # Try to extract field name from message
                    field = self._extract_field_from_message(message)
                    errors.append(ValidationError(field, message, "alert"))

        return errors

    def _extract_validation_text(self) -> List[ValidationError]:
        """Extract validation messages from general text elements."""
        errors = []

        # Look for text elements containing validation keywords
        text_pattern = r'text:\s*"([^"]+)"'

        for match in re.finditer(text_pattern, self.content):
            message = match.group(1)

            if self._is_validation_message(message):
                field = self._find_field_before_position(match.start())
                errors.append(ValidationError(field, message, "text"))

        return errors

    def _find_field_before_position(self, position: int, lookback: int = 500) -> str:
        """Find the field name before a given position in the content."""
        # Look back up to lookback characters
        start = max(0, position - lookback)
        section = self.content[start:position]

        # Common field patterns
        patterns = [
            r'(textbox|email|password|number|tel|url|search)\s+"([^"]+)"',
            r'(combobox|select|dropdown)\s+"([^"]+)"',
            r'(checkbox|radio)\s+"([^"]+)"',
        ]

        for pattern in patterns:
            matches = list(re.finditer(pattern, section, re.IGNORECASE))
            if matches:
                # Get the closest match (last one found)
                return matches[-1].group(2)

        return "Unknown Field"

    def _find_error_by_id(self, error_id: str) -> Optional[str]:
        """Find error message text by element ID."""
        # Look for element with matching ID
        pattern = rf'text\s+"{error_id}"[^\n]*\n\s+text:\s*"([^"]+)"'
        match = re.search(pattern, self.content)

        if match:
            return match.group(1)

        # Alternative: ID might be in id attribute
        pattern2 = rf'id:\s*"{error_id}"[^\n]*\n\s+text:\s*"([^"]+)"'
        match2 = re.search(pattern2, self.content)

        if match2:
            return match2.group(1)

        return None

    def _is_validation_message(self, text: str) -> bool:
        """Check if text is likely a validation message."""
        text_lower = text.lower()

        # Check for validation keywords
        return any(keyword in text_lower for keyword in self.VALIDATION_KEYWORDS)

    def _extract_field_from_message(self, message: str) -> str:
        """Try to extract field name from error message."""
        # Look for patterns like "Email is required" or "Password must..."
        pattern = r'^(\w+)\s+(is|must|should|cannot|does not)'
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            return match.group(1)

        return "Unknown Field"

    def _deduplicate_errors(self, errors: List[ValidationError]) -> List[ValidationError]:
        """Remove duplicate errors."""
        seen = set()
        unique_errors = []

        for error in errors:
            key = (error.field.lower(), error.message.lower())
            if key not in seen:
                seen.add(key)
                unique_errors.append(error)

        return unique_errors

    def get_field_errors(self, field_name: str) -> List[ValidationError]:
        """Get errors for a specific field."""
        all_errors = self.extract_errors()
        return [e for e in all_errors if e.field.lower() == field_name.lower()]


def main():
    parser = argparse.ArgumentParser(
        description="Parse validation errors from browser snapshots"
    )
    parser.add_argument(
        "snapshot",
        type=Path,
        help="Path to snapshot file (.md)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--field",
        type=str,
        help="Filter by field name"
    )

    args = parser.parse_args()

    if not args.snapshot.exists():
        print(f"Error: Snapshot file not found: {args.snapshot}", file=sys.stderr)
        sys.exit(1)

    try:
        snapshot_parser = SnapshotParser(args.snapshot)
        errors = snapshot_parser.extract_errors()

        # Filter by field if specified
        if args.field:
            errors = [e for e in errors if e.field.lower() == args.field.lower()]

        # Output
        if args.json:
            output = [e.to_dict() for e in errors]
            print(json.dumps(output, indent=2))
        else:
            if not errors:
                print("No validation errors found.")
            else:
                print(f"Found {len(errors)} validation error(s):\n")
                for i, error in enumerate(errors, 1):
                    print(f"{i}. Field: {error.field}")
                    print(f"   Message: {error.message}")
                    print(f"   Type: {error.error_type}")
                    print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
