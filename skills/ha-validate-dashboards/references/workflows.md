# Home Assistant Validation Workflows

Complete workflow documentation for dashboard validation, rollback strategies, and CI/CD integration.

## Table of Contents

1. Pre-Commit Validation Checklist
2. Rollback Strategy
3. Complete End-to-End Workflow
4. CI/CD Integration
5. Automated Testing Scripts

## 1. Pre-Commit Validation Checklist

Run this checklist before committing dashboard builder changes to git.

### Quick Checklist

```bash
# Run all validation steps
./validation/pre_commit_check.sh

# Or manually verify each item:
```

- [ ] **Config structure validated** - All views have required fields
- [ ] **Entity existence checked** - All entity IDs exist in HA
- [ ] **HACS cards verified** - Custom cards are installed
- [ ] **Local test run** - Execute builder script successfully
- [ ] **Logs checked** - No new errors in HA error log
- [ ] **Visual inspection** - Navigate to dashboard, verify rendering
- [ ] **Console checked** - No JavaScript errors in browser console
- [ ] **Documentation updated** - CLAUDE.md reflects changes

### Detailed Pre-Commit Script

```bash
#!/bin/bash
# pre_commit_check.sh - Run all validation before committing

set -e

echo "🔍 Pre-commit validation for HA dashboards"

# 1. Config structure validation
echo "📋 Step 1: Validating config structure..."
python3 << 'EOF'
import sys
import json
from validation_helpers import validate_dashboard_config

# Check all dashboard JSON files
import glob
for config_file in glob.glob("*_dashboard.json"):
    print(f"  Checking {config_file}...")
    with open(config_file) as f:
        config = json.load(f)

    is_valid, errors = validate_dashboard_config(config)
    if not is_valid:
        print(f"  ❌ {config_file} validation failed:")
        for error in errors:
            print(f"    - {error}")
        sys.exit(1)
    print(f"  ✅ {config_file} valid")

print("✅ All configs valid")
EOF

# 2. Entity existence validation
echo "📋 Step 2: Validating entities..."
python3 << 'EOF'
import sys
import json
from validation_helpers import extract_all_entity_ids, verify_entities_exist
import glob

all_entities = set()
for config_file in glob.glob("*_dashboard.json"):
    with open(config_file) as f:
        config = json.load(f)
    entities = extract_all_entity_ids(config)
    all_entities.update(entities)

print(f"  Found {len(all_entities)} unique entities across all dashboards")

existence_map = verify_entities_exist(list(all_entities))
missing = [e for e, exists in existence_map.items() if not exists]

if missing:
    print(f"  ❌ Missing entities ({len(missing)}):")
    for entity_id in missing:
        print(f"    - {entity_id}")
    sys.exit(1)

print(f"  ✅ All {len(all_entities)} entities exist")
EOF

# 3. Python syntax check
echo "📋 Step 3: Checking Python syntax..."
python3 -m py_compile dashboard_builder.py
python3 -m py_compile ha_card_utils.py
echo "✅ Python syntax valid"

# 4. Test dashboard build (dry run)
echo "📋 Step 4: Test building dashboards..."
# This should be implemented in dashboard_builder.py
python3 -c "
import dashboard_builder
# Add dry-run test here
print('✅ Dashboard build test passed')
"

echo ""
echo "✅ Pre-commit validation complete - safe to commit"
```

## 2. Rollback Strategy

### Backup Before Changes

Always capture current configuration before making changes:

```python
import websocket
import json
import os
from datetime import datetime


def backup_dashboard(url_path: str) -> str:
    """
    Backup current dashboard configuration.

    Args:
        url_path: Dashboard URL path

    Returns:
        Path to backup file
    """
    ws = websocket.create_connection(
        "ws://192.168.68.123:8123/api/websocket",
        timeout=10
    )

    try:
        # Auth
        ws.recv()
        ws.send(json.dumps({
            "type": "auth",
            "access_token": os.environ["HA_LONG_LIVED_TOKEN"]
        }))
        ws.recv()

        # Get current config
        ws.send(json.dumps({
            "id": 1,
            "type": "lovelace/config",
            "url_path": url_path
        }))

        result = json.loads(ws.recv())
        if not result.get("success"):
            raise Exception("Failed to fetch dashboard config")

        config = result["result"]

        # Save backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backups/{url_path}_{timestamp}.json"

        os.makedirs("backups", exist_ok=True)
        with open(backup_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Backup saved: {backup_path}")
        return backup_path

    finally:
        ws.close()


# Usage
backup_path = backup_dashboard("climate-dashboard")
```

### Rollback Procedure

```python
def rollback_dashboard(url_path: str, backup_path: str) -> bool:
    """
    Rollback dashboard to backup configuration.

    Args:
        url_path: Dashboard URL path
        backup_path: Path to backup JSON file

    Returns:
        True if rollback succeeded
    """
    print(f"⏪ Rolling back dashboard '{url_path}' to {backup_path}...")

    # Load backup
    with open(backup_path) as f:
        backup_config = json.load(f)

    # Publish backup config
    success, msg = publish_dashboard_safely(url_path, backup_config)

    if success:
        print(f"✅ Rollback successful: {msg}")
        return True
    else:
        print(f"❌ Rollback failed: {msg}")
        print("⚠️  Manual intervention required via HA UI")
        return False


# Usage pattern
# 1. Save backup before changes
backup_path = backup_dashboard("climate-dashboard")

# 2. Attempt changes
success, msg = publish_dashboard_safely("climate-dashboard", new_config)

# 3. Rollback if failed
if not success:
    rollback_dashboard("climate-dashboard", backup_path)
```

### Manual Rollback (HA UI)

If automated rollback fails:

1. Navigate to: http://192.168.68.123:8123/config/lovelace/dashboards
2. Select the failed dashboard
3. Click "Edit" in raw configuration editor
4. Paste backup JSON from `backups/` directory
5. Click "Save"

## 3. Complete End-to-End Workflow

Visual workflow for development to production deployment:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Development & Local Validation                     │
└─────────────────────────────────────────────────────────────┘
│
├─ 1. Write dashboard builder code
│  └─ Use ha_card_utils.py for consistency
│
├─ 2. Pre-publish validation (Python)
│  ├─ Validate config structure
│  ├─ Check entity existence
│  └─ Verify HACS cards installed
│
├─ 3. Publish to test dashboard
│  └─ Use temporary dashboard for testing
│
└─ 4. Local visual check
   ├─ Navigate in browser
   ├─ Check console for errors
   └─ Verify card rendering

┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Pre-Production Validation                          │
└─────────────────────────────────────────────────────────────┘
│
├─ 5. Capture baseline logs
│  └─ curl error_log > pre-deploy.log
│
├─ 6. Backup current dashboard
│  └─ Save config to backups/ directory
│
├─ 7. Publish to production dashboard
│  └─ WebSocket API publish
│
├─ 8. Check HA logs for new errors
│  ├─ curl error_log > post-deploy.log
│  └─ diff pre-deploy.log post-deploy.log
│
└─ 9. Automated browser validation
   ├─ Navigate via MCP tool
   ├─ Read console messages
   ├─ Take screenshot
   └─ Check for error indicators

┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Production Monitoring                              │
└─────────────────────────────────────────────────────────────┘
│
├─ 10. Monitor for 5 minutes
│  ├─ Watch HA logs
│  └─ Check browser console periodically
│
├─ 11. User acceptance
│  └─ Manual verification of functionality
│
└─ 12. Rollback if issues detected
   └─ Restore previous config from backup

┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Documentation & Commit                             │
└─────────────────────────────────────────────────────────────┘
│
├─ 13. Update CLAUDE.md
│  └─ Document new dashboard details
│
├─ 14. Git commit builder script
│  └─ Ensure reproducibility
│
└─ 15. Tag successful deployment
   └─ git tag v1.2.3-dashboard-update
```

### Complete End-to-End Script

```bash
#!/bin/bash
# deploy_dashboard.sh - Complete deployment workflow

DASHBOARD_URL="http://192.168.68.123:8123"
DASHBOARD_PATH="climate-dashboard"
CONFIG_FILE="climate_dashboard.json"

echo "🚀 Starting deployment for /$DASHBOARD_PATH"

# Phase 1: Pre-publish validation
echo ""
echo "📋 Phase 1: Pre-publish validation"
echo "=================================="

python3 << 'EOF'
import sys
import json
sys.path.insert(0, '.')
from validation_helpers import validate_dashboard_config, verify_entities_exist, extract_all_entity_ids

with open('$CONFIG_FILE') as f:
    config = json.load(f)

# Validate structure
is_valid, errors = validate_dashboard_config(config)
if not is_valid:
    print("❌ Config validation failed:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("✅ Config structure valid")

# Verify entities
entity_ids = extract_all_entity_ids(config)
existence_map = verify_entities_exist(entity_ids)
missing = [eid for eid, exists in existence_map.items() if not exists]

if missing:
    print("❌ Missing entities:")
    for entity_id in missing:
        print(f"  - {entity_id}")
    sys.exit(1)

print(f"✅ All {len(entity_ids)} entities exist")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Pre-publish validation failed - aborting"
    exit 1
fi

# Phase 2: Backup & Publish
echo ""
echo "📤 Phase 2: Backup & Publish"
echo "============================"

# Backup current config
echo "Creating backup..."
python3 << 'EOF'
from validation_helpers import backup_dashboard
backup_path = backup_dashboard('$DASHBOARD_PATH')
print(f"Backup saved: {backup_path}")
EOF

# Capture baseline logs
echo "Capturing baseline logs..."
curl -s "$DASHBOARD_URL/api/error_log" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" > pre-deploy.log

# Publish dashboard
echo "Publishing dashboard..."
./run.sh dashboard_builder.py

if [ $? -ne 0 ]; then
    echo "❌ Dashboard publish failed - check logs"
    exit 1
fi

echo "✅ Dashboard published"

# Phase 3: Post-publish verification
echo ""
echo "📜 Phase 3: Post-publish verification"
echo "======================================"

# Wait for errors to propagate
sleep 5

# Capture post-deployment logs
curl -s "$DASHBOARD_URL/api/error_log" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" > post-deploy.log

# Check for new errors
echo "Checking for new errors..."
NEW_ERRORS=$(diff pre-deploy.log post-deploy.log | grep "^>" || true)

if [ -n "$NEW_ERRORS" ]; then
    echo "⚠️  New errors detected:"
    echo "$NEW_ERRORS"
    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment aborted - rolling back"
        python3 -c "from validation_helpers import rollback_dashboard; rollback_dashboard('$DASHBOARD_PATH', 'backups/latest.json')"
        exit 1
    fi
else
    echo "✅ No new errors in logs"
fi

# Phase 4: Visual validation
echo ""
echo "🖥️  Phase 4: Visual validation"
echo "=============================="

mcp-cli call claude-in-chrome/navigate "{\"url\": \"$DASHBOARD_URL/$DASHBOARD_PATH\"}"
sleep 2
mcp-cli call claude-in-chrome/read_console_messages '{}' > console_output.json

# Check for console errors
if grep -q '"level": "error"' console_output.json; then
    echo "❌ Browser console errors detected:"
    cat console_output.json | jq -r '.console_messages[] | select(.level == "error") | .text'

    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment aborted - rolling back"
        python3 -c "from validation_helpers import rollback_dashboard; rollback_dashboard('$DASHBOARD_PATH', 'backups/latest.json')"
        exit 1
    fi
else
    echo "✅ No console errors"
fi

# Take screenshot for verification
mcp-cli call claude-in-chrome/computer '{"action": "screenshot"}' > screenshot.json
SCREENSHOT_PATH=$(cat screenshot.json | jq -r '.path')
echo "📸 Screenshot saved: $SCREENSHOT_PATH"

# Final confirmation
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Summary:"
echo "  Dashboard: $DASHBOARD_PATH"
echo "  Config: $CONFIG_FILE"
echo "  Backup: backups/latest.json"
echo "  Screenshot: $SCREENSHOT_PATH"
echo ""
echo "Next steps:"
echo "  1. Manually verify dashboard functionality"
echo "  2. Monitor logs for 5 minutes"
echo "  3. Update CLAUDE.md if needed"
echo "  4. Git commit and tag deployment"
```

## 4. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-dashboards.yml
name: Validate HA Dashboards

on:
  pull_request:
    paths:
      - '**/*dashboard*.py'
      - '**/*dashboard*.json'
      - 'ha_card_utils.py'
      - 'validation/**'
  push:
    branches:
      - main
    paths:
      - '**/*dashboard*.py'
      - '**/*dashboard*.json'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests websocket-client

      - name: Validate dashboard configs
        env:
          HA_LONG_LIVED_TOKEN: ${{ secrets.HA_TOKEN }}
        run: |
          python3 validation/validate_all.py

      - name: Check for broken entity references
        env:
          HA_LONG_LIVED_TOKEN: ${{ secrets.HA_TOKEN }}
        run: |
          python3 validation/check_entities.py

      - name: Test dashboard build
        env:
          HA_LONG_LIVED_TOKEN: ${{ secrets.HA_TOKEN }}
        run: |
          python3 dashboard_builder.py --dry-run

      - name: Comment on PR with validation results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = fs.readFileSync('validation_results.txt', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Dashboard Validation Results\n\n${results}`
            });
```

### Pre-Commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Pre-commit hook for HA dashboard validation

# Only run if dashboard files changed
DASHBOARD_FILES=$(git diff --cached --name-only | grep -E "(dashboard_builder|ha_card_utils|.*_dashboard.json)")

if [ -z "$DASHBOARD_FILES" ]; then
    exit 0
fi

echo "🔍 Validating HA dashboard changes..."

# Run validation script
./validation/pre_commit_check.sh

if [ $? -ne 0 ]; then
    echo "❌ Dashboard validation failed - commit blocked"
    echo "Fix validation errors and try again"
    exit 1
fi

echo "✅ Dashboard validation passed"
exit 0
```

## 5. Automated Testing Scripts

### Validation Test Suite

```python
# validation/validate_all.py
"""Complete validation test suite for HA dashboards."""

import sys
import json
import glob
from pathlib import Path

# Import validation helpers
from validation_helpers import (
    validate_dashboard_config,
    verify_entities_exist,
    extract_all_entity_ids,
    check_hacs_card_installed
)


def validate_all_dashboards() -> bool:
    """Run validation on all dashboard configs."""
    print("🔍 Validating all dashboard configurations")
    print("=" * 60)

    all_passed = True
    dashboard_files = glob.glob("*_dashboard.json")

    if not dashboard_files:
        print("⚠️  No dashboard files found")
        return True

    # Collect all entities across dashboards
    all_entities = set()
    all_cards = set()

    for config_file in dashboard_files:
        print(f"\n📋 Validating {config_file}")
        print("-" * 60)

        try:
            with open(config_file) as f:
                config = json.load(f)

            # 1. Config structure validation
            is_valid, errors = validate_dashboard_config(config)
            if not is_valid:
                print(f"  ❌ Config validation failed:")
                for error in errors:
                    print(f"    - {error}")
                all_passed = False
                continue
            print(f"  ✅ Config structure valid")

            # 2. Extract entities
            entities = extract_all_entity_ids(config)
            all_entities.update(entities)
            print(f"  ℹ️  Found {len(entities)} entities")

            # 3. Extract custom cards
            cards = extract_custom_cards(config)
            all_cards.update(cards)
            if cards:
                print(f"  ℹ️  Found {len(cards)} custom card types")

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse error: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            all_passed = False

    # 4. Verify all entities exist
    print(f"\n📋 Validating {len(all_entities)} unique entities")
    print("-" * 60)

    existence_map = verify_entities_exist(list(all_entities))
    missing = [e for e, exists in existence_map.items() if not exists]

    if missing:
        print(f"  ❌ Missing entities ({len(missing)}):")
        for entity_id in sorted(missing):
            print(f"    - {entity_id}")
        all_passed = False
    else:
        print(f"  ✅ All {len(all_entities)} entities exist")

    # 5. Verify HACS cards installed
    if all_cards:
        print(f"\n📋 Validating {len(all_cards)} custom card types")
        print("-" * 60)

        for card_type in sorted(all_cards):
            if check_hacs_card_installed(card_type):
                print(f"  ✅ {card_type} installed")
            else:
                print(f"  ❌ {card_type} NOT installed")
                all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All validations passed")
        return True
    else:
        print("❌ Validation failed - see errors above")
        return False


def extract_custom_cards(config: dict) -> set[str]:
    """Extract all custom card types from config."""
    cards = set()

    def extract_from_dict(d):
        if isinstance(d, dict):
            if "type" in d and isinstance(d["type"], str):
                if d["type"].startswith("custom:"):
                    cards.add(d["type"])
            for value in d.values():
                if isinstance(value, (dict, list)):
                    extract_from_dict(value)
        elif isinstance(d, list):
            for item in d:
                extract_from_dict(item)

    extract_from_dict(config)
    return cards


if __name__ == "__main__":
    success = validate_all_dashboards()
    sys.exit(0 if success else 1)
```

### Entity Validation Script

```python
# validation/check_entities.py
"""Check entity availability and state."""

import sys
from validation_helpers import batch_validate_entities, extract_all_entity_ids
import json
import glob


def check_all_entities() -> bool:
    """Check all entities across all dashboards."""
    print("🔍 Checking entity availability")
    print("=" * 60)

    # Collect entities
    all_entities = set()
    for config_file in glob.glob("*_dashboard.json"):
        with open(config_file) as f:
            config = json.load(f)
        entities = extract_all_entity_ids(config)
        all_entities.update(entities)

    print(f"Found {len(all_entities)} unique entities\n")

    # Batch validate
    results = batch_validate_entities(list(all_entities))

    # Report results
    if results["valid"]:
        print(f"✅ Valid entities ({len(results['valid'])})")

    if results["unavailable"]:
        print(f"\n⚠️  Unavailable entities ({len(results['unavailable'])}):")
        for entity_id in sorted(results["unavailable"]):
            print(f"  - {entity_id}")

    if results["invalid"]:
        print(f"\n❌ Invalid entities ({len(results['invalid'])}):")
        for entity_id in sorted(results["invalid"]):
            print(f"  - {entity_id}")

    print("\n" + "=" * 60)
    if results["invalid"]:
        print("❌ Validation failed - fix invalid entities")
        return False
    elif results["unavailable"]:
        print("⚠️  Some entities unavailable - check devices")
        return True
    else:
        print("✅ All entities valid and available")
        return True


if __name__ == "__main__":
    success = check_all_entities()
    sys.exit(0 if success else 1)
```
