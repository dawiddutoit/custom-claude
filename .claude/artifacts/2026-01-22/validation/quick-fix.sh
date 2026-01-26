#!/bin/bash
# Quick Fix Script for Group 2 Skills Validation Issues
# Addresses Priority 1 & 2 issues automatically
#
# Usage: ./quick-fix.sh [--dry-run]

set -e

SKILLS_DIR="/Users/dawiddutoit/projects/claude/custom-claude/skills"
DRY_RUN=false

# Parse arguments
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
fi

# Group 2 skills (42-82)
SKILLS=(
    "gcp-gke-workload-identity" "gcp-pubsub" "github-webhook-setup"
    "gradle-ci-cd-integration" "gradle-dependency-management" "gradle-docker-jib"
    "gradle-performance-optimization" "gradle-spring-boot-integration" "gradle-testing-setup"
    "gradle-troubleshooting" "ha-button-cards" "ha-conditional-cards"
    "ha-custom-cards" "ha-dashboard-cards" "ha-dashboard-create"
    "ha-dashboard-layouts" "ha-error-checking" "ha-graphs-visualization"
    "ha-mqtt-autodiscovery" "ha-mushroom-cards" "ha-operations"
    "ha-rest-api" "ha-sunsynk-integration" "ha-validate-dashboards"
    "implement-cqrs-handler" "implement-dependency-injection" "implement-feature-complete"
    "implement-repository-pattern" "implement-retry-logic" "implement-value-object"
    "infra-manage-ssh-services" "infrastructure-backup-restore" "infrastructure-health-check"
    "infrastructure-monitoring-setup" "internal-comms" "java-best-practices-code-review"
    "java-best-practices-debug-analyzer" "java-best-practices-refactor-legacy"
    "java-best-practices-security-audit" "java-spring-service" "java-test-generator"
)

echo "======================================"
echo "Group 2 Skills Quick Fix Script"
echo "======================================"
echo ""

# Priority 1: Fix YAML Frontmatter
echo "Priority 1: Fixing YAML Frontmatter Delimiters"
echo "----------------------------------------------"

yaml_fixed=0
yaml_skipped=0

for skill in "${SKILLS[@]}"; do
    skill_file="${SKILLS_DIR}/${skill}/SKILL.md"

    if [[ ! -f "$skill_file" ]]; then
        echo "⚠️  ${skill}: SKILL.md not found"
        continue
    fi

    # Check if YAML delimiters already exist
    if head -n 1 "$skill_file" | grep -q "^---$"; then
        yaml_skipped=$((yaml_skipped + 1))
        continue
    fi

    # Check if file starts with YAML-like content (name:, description:, etc.)
    if head -n 1 "$skill_file" | grep -qE "^(name|description|allowed-tools|version):"; then
        echo "  Fixing ${skill}..."

        if [[ "$DRY_RUN" == false ]]; then
            # Find first markdown heading (starts with #)
            line_num=$(grep -n "^#" "$skill_file" | head -1 | cut -d: -f1)

            if [[ -n "$line_num" ]]; then
                # Add opening delimiter at start
                sed -i '' '1i\
---
' "$skill_file"

                # Add closing delimiter before first heading (now at line_num+1)
                sed -i '' "${line_num}i\\
---\\

" "$skill_file"

                yaml_fixed=$((yaml_fixed + 1))
                echo "    ✅ Fixed"
            else
                echo "    ⚠️  Could not find first heading"
            fi
        else
            yaml_fixed=$((yaml_fixed + 1))
            echo "    [DRY RUN] Would fix"
        fi
    else
        yaml_skipped=$((yaml_skipped + 1))
    fi
done

echo ""
echo "  Fixed: ${yaml_fixed}"
echo "  Skipped (already correct): ${yaml_skipped}"
echo ""

# Priority 2: Remove Backup Files
echo "Priority 2: Removing Backup Files"
echo "-----------------------------------"

backup_count=0

for skill in "${SKILLS[@]}"; do
    skill_dir="${SKILLS_DIR}/${skill}"

    if [[ ! -d "$skill_dir" ]]; then
        continue
    fi

    # Find .bak files in root directory only
    bak_files=$(find "$skill_dir" -maxdepth 1 -name "*.bak" -type f)

    if [[ -n "$bak_files" ]]; then
        echo "  Cleaning ${skill}..."

        for bak_file in $bak_files; do
            if [[ "$DRY_RUN" == false ]]; then
                rm "$bak_file"
                echo "    ✅ Removed $(basename "$bak_file")"
            else
                echo "    [DRY RUN] Would remove $(basename "$bak_file")"
            fi
            backup_count=$((backup_count + 1))
        done
    fi
done

echo ""
echo "  Removed: ${backup_count} backup files"
echo ""

# Summary
echo "======================================"
echo "Summary"
echo "======================================"
echo ""
echo "✅ YAML frontmatter fixed: ${yaml_fixed} skills"
echo "✅ Backup files removed: ${backup_count} files"
echo ""

if [[ "$DRY_RUN" == false ]]; then
    echo "Changes have been applied."
    echo ""
    echo "Next steps:"
    echo "  1. Review changes with: git diff"
    echo "  2. Re-run validation: python3 validate_group2.py"
    echo "  3. Commit if satisfied: git add . && git commit -m 'Fix Group 2 YAML frontmatter and cleanup'"
else
    echo "No changes made (dry run mode)."
    echo ""
    echo "To apply changes, run: ./quick-fix.sh"
fi

echo ""
echo "Note: Priority 3 (Progressive Disclosure) requires manual content reorganization."
echo "See group-2-summary.md for skills needing this work."
