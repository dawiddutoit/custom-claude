#!/usr/bin/env python3
"""
Initialize test environment directory structure for E2E tests.

Usage:
    python setup_test_env.py [output_dir]

Creates:
    output_dir/
    ├── snapshots/
    ├── screenshots/
    ├── reports/
    ├── logs/
    └── .gitignore
"""

import argparse
from pathlib import Path


def setup_test_env(output_dir: Path):
    """Create test environment directory structure."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (output_dir / "snapshots").mkdir(exist_ok=True)
    (output_dir / "screenshots").mkdir(exist_ok=True)
    (output_dir / "reports").mkdir(exist_ok=True)
    (output_dir / "logs").mkdir(exist_ok=True)

    # Create .gitignore
    gitignore_content = """# E2E Test Artifacts
*.png
*.jpg
*.json
*.log

# Keep reports
!reports/
reports/*.md

# Keep directory structure
!.gitignore
"""
    (output_dir / ".gitignore").write_text(gitignore_content)

    print(f"✅ Test environment initialized: {output_dir}")
    print("\nDirectory structure:")
    print(f"  {output_dir}/")
    print(f"  ├── snapshots/")
    print(f"  ├── screenshots/")
    print(f"  ├── reports/")
    print(f"  ├── logs/")
    print(f"  └── .gitignore")


def main():
    parser = argparse.ArgumentParser(description="Setup E2E test environment")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="test-artifacts",
        help="Output directory (default: test-artifacts)"
    )
    args = parser.parse_args()

    output_path = Path(args.output_dir)
    setup_test_env(output_path)


if __name__ == "__main__":
    main()
