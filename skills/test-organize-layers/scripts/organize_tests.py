#!/usr/bin/env python3
"""Master script to organize tests across pyramid layers.

This script orchestrates all three test organization utilities:
1. validate_test_placement.py - Find misplaced tests
2. move_test.py - Fix test placement
3. analyze_test_pyramid.py - Verify distribution

Usage:
    python organize_tests.py --check
    python organize_tests.py --fix
    python organize_tests.py --interactive
    python organize_tests.py --report
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class TestOrganizer:
    """Orchestrate test organization across all layers."""

    def __init__(self, test_dir: Path = Path("tests")) -> None:
        """Initialize organizer.

        Args:
            test_dir: Directory containing tests to organize.
        """
        self.test_dir = test_dir
        self.script_dir = Path(__file__).parent

    def run_validation(self, output_format: str = "text") -> list[dict[str, Any]] | dict[str, Any]:
        """Run test placement validation.

        Args:
            output_format: Either "text" or "json".

        Returns:
            List of test analysis dicts (for json format) or dict with output/returncode.
        """
        cmd = [
            sys.executable,
            str(self.script_dir / "validate_test_placement.py"),
            str(self.test_dir),
            "--format",
            output_format,
        ]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if output_format == "json" and result.stdout.strip():
            try:
                parsed = json.loads(result.stdout)
                if isinstance(parsed, list):
                    return parsed
                return {"output": result.stdout, "returncode": result.returncode}
            except json.JSONDecodeError:
                return {"output": result.stdout, "returncode": result.returncode}
        return {"output": result.stdout, "returncode": result.returncode}

    def run_pyramid_analysis(self, output_format: str = "text") -> dict[str, Any]:
        """Run test pyramid analysis.

        Args:
            output_format: Either "text" or "json".

        Returns:
            Dictionary with pyramid analysis results.
        """
        cmd = [
            sys.executable,
            str(self.script_dir / "analyze_test_pyramid.py"),
            str(self.test_dir),
            "--format",
            output_format,
        ]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if output_format == "json" and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout, "returncode": result.returncode}
        return {"output": result.stdout, "returncode": result.returncode}

    def move_test(
        self, source: Path, *, auto: bool = True, dry_run: bool = False
    ) -> dict[str, Any]:
        """Move a test file to correct layer.

        Args:
            source: Path to the test file.
            auto: If True, auto-detect target layer.
            dry_run: If True, only report changes.

        Returns:
            Dictionary with move operation results.
        """
        cmd = [
            sys.executable,
            str(self.script_dir / "move_test.py"),
            str(source),
        ]
        if auto:
            cmd.append("--auto")
        if dry_run:
            cmd.append("--dry-run")

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return {
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode,
        }

    def check_status(self) -> None:
        """Check current test organization status and print results."""
        print("=" * 80)
        print("TEST PLACEMENT VALIDATION")
        print("=" * 80)

        # Run validation (text format returns dict)
        validation_result = self.run_validation("text")
        if isinstance(validation_result, dict):
            print(validation_result.get("output", ""))

        print("\n" + "=" * 80)
        print("TEST PYRAMID ANALYSIS")
        print("=" * 80)

        # Run pyramid analysis
        pyramid_result = self.run_pyramid_analysis("text")
        print(pyramid_result.get("output", ""))

    def fix_all(self, *, interactive: bool = False) -> None:
        """Fix all misplaced tests.

        Args:
            interactive: If True, prompt before each move.
        """
        print("Analyzing test placement...")

        # Get validation results
        validation_results = self.run_validation("json")

        # Handle non-list results (error case)
        if not isinstance(validation_results, list):
            print("Error: Could not parse validation results")
            return

        # Filter misplaced tests
        misplaced = [t for t in validation_results if not t.get("is_correct", True)]

        if not misplaced:
            print("All tests are correctly placed!")
            return

        print(f"Found {len(misplaced)} misplaced test(s)")

        moved_count = 0
        skipped_count = 0

        for test in misplaced:
            source_file = Path(test["file"])
            print(f"\nProcessing: {source_file}")
            print(f"  Current: {test.get('current_layer', 'unknown')}")
            print(f"  Should be: {test.get('detected_layer', 'unknown')}")

            if interactive:
                # Show dry run
                result = self.move_test(source_file, auto=True, dry_run=True)
                print(result.get("output", ""))

                # Ask for confirmation
                response = input("\nApply this move? [y/n/q] ").strip().lower()
                if response == "q":
                    print("Aborted by user")
                    break
                if response != "y":
                    skipped_count += 1
                    continue

            # Execute move
            result = self.move_test(source_file, auto=True, dry_run=False)
            if result["returncode"] == 0:
                moved_count += 1
                print("  Moved successfully")
            else:
                skipped_count += 1
                print(f"  Failed: {result.get('error', 'Unknown error')}")

        # Summary
        print(f"\nSummary: {moved_count} moved, {skipped_count} skipped")

        # Re-run analysis
        if moved_count > 0:
            print("\nUpdated pyramid analysis:")
            pyramid_result = self.run_pyramid_analysis("text")
            print(pyramid_result.get("output", ""))

    def generate_report(self, output_file: Path | None = None) -> None:
        """Generate comprehensive organization report.

        Args:
            output_file: Optional path to write JSON report.
        """
        print("Generating comprehensive report...")

        # Get all data
        validation = self.run_validation("json")
        pyramid = self.run_pyramid_analysis("json")

        # Handle non-list validation results
        if not isinstance(validation, list):
            print("Error: Could not parse validation results")
            validation = []

        # Compute statistics
        total_tests = len(validation)
        misplaced = [t for t in validation if not t.get("is_correct", True)]
        misplaced_count = len(misplaced)

        report: dict[str, Any] = {
            "summary": {
                "total_tests": total_tests,
                "correctly_placed": total_tests - misplaced_count,
                "misplaced": misplaced_count,
                "accuracy": (total_tests - misplaced_count) / total_tests * 100
                if total_tests > 0
                else 0.0,
            },
            "pyramid": pyramid,
            "misplaced_tests": misplaced,
        }

        if output_file:
            output_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"Report written to: {output_file}")
        else:
            print(json.dumps(report, indent=2))

        if misplaced_count > 0:
            print(f"\nWarning: {misplaced_count} test(s) need to be moved")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 for success, 1 if help shown.
    """
    parser = argparse.ArgumentParser(
        description="Master script for test organization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check current status
  python organize_tests.py --check

  # Fix all misplaced tests
  python organize_tests.py --fix

  # Interactive mode (review each change)
  python organize_tests.py --interactive

  # Generate comprehensive report
  python organize_tests.py --report
  python organize_tests.py --report --output report.json
        """,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current test organization status",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix all misplaced tests automatically",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode - review each change",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive report",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for report (JSON)",
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("tests"),
        help="Test directory to organize (default: tests/)",
    )

    args = parser.parse_args()

    organizer = TestOrganizer(test_dir=args.test_dir)

    if args.check:
        organizer.check_status()
    elif args.fix:
        organizer.fix_all(interactive=False)
    elif args.interactive:
        organizer.fix_all(interactive=True)
    elif args.report:
        organizer.generate_report(output_file=args.output)
    else:
        # Default: show help
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
