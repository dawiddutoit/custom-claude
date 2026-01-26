#!/usr/bin/env python3
"""
Validate Group 2 skills (42-82) against Anthropic's Official Best Practices
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

SKILLS_DIR = Path("/Users/dawiddutoit/projects/claude/custom-claude/skills")

GROUP_2_SKILLS = [
    "gcp-gke-workload-identity", "gcp-pubsub", "github-webhook-setup",
    "gradle-ci-cd-integration", "gradle-dependency-management", "gradle-docker-jib",
    "gradle-performance-optimization", "gradle-spring-boot-integration", "gradle-testing-setup",
    "gradle-troubleshooting", "ha-button-cards", "ha-conditional-cards",
    "ha-custom-cards", "ha-dashboard-cards", "ha-dashboard-create",
    "ha-dashboard-layouts", "ha-error-checking", "ha-graphs-visualization",
    "ha-mqtt-autodiscovery", "ha-mushroom-cards", "ha-operations",
    "ha-rest-api", "ha-sunsynk-integration", "ha-validate-dashboards",
    "implement-cqrs-handler", "implement-dependency-injection", "implement-feature-complete",
    "implement-repository-pattern", "implement-retry-logic", "implement-value-object",
    "infra-manage-ssh-services", "infrastructure-backup-restore", "infrastructure-health-check",
    "infrastructure-monitoring-setup", "internal-comms", "java-best-practices-code-review",
    "java-best-practices-debug-analyzer", "java-best-practices-refactor-legacy",
    "java-best-practices-security-audit", "java-spring-service", "java-test-generator"
]

def extract_frontmatter(skill_path: Path) -> Tuple[bool, Dict, List[str]]:
    """Extract and validate YAML frontmatter"""
    issues = []

    try:
        with open(skill_path, 'r') as f:
            content = f.read()

        # Extract frontmatter between --- delimiters
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return False, {}, ["No YAML frontmatter found"]

        frontmatter_text = match.group(1)

        # Parse YAML
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            return False, {}, [f"YAML parsing error: {e}"]

        # Validate required fields
        if 'name' not in frontmatter:
            issues.append("Missing 'name' field")
        elif not isinstance(frontmatter['name'], str):
            issues.append("'name' must be a string")
        elif len(frontmatter['name']) > 64:
            issues.append(f"'name' too long ({len(frontmatter['name'])} chars, max 64)")

        if 'description' not in frontmatter:
            issues.append("Missing 'description' field")
        elif not isinstance(frontmatter['description'], str):
            issues.append("'description' must be a string")
        elif len(frontmatter['description']) > 1024:
            issues.append(f"'description' too long ({len(frontmatter['description'])} chars, max 1024)")

        return len(issues) == 0, frontmatter, issues

    except FileNotFoundError:
        return False, {}, ["SKILL.md file not found"]
    except Exception as e:
        return False, {}, [f"Error reading file: {e}"]

def check_description_completeness(description: str) -> Tuple[int, List[str]]:
    """Check if description has WHAT, WHEN, TERMS, CONTEXT"""
    issues = []
    score = 0

    if not description:
        return 0, ["Description is empty"]

    # WHAT - typically first sentence
    if len(description) > 50:
        score += 2
    else:
        issues.append("Description too short (should describe WHAT)")

    # WHEN - trigger phrases
    trigger_keywords = ["use when", "triggers on", "when asked", "when you need", "when setting"]
    if any(keyword in description.lower() for keyword in trigger_keywords):
        score += 3
    else:
        issues.append("Missing WHEN triggers (should include trigger phrases)")

    # TERMS - technical keywords
    if len(description.split()) > 20:
        score += 2
    else:
        issues.append("Description lacks technical TERMS")

    # CONTEXT - works with, file types
    context_keywords = ["works with", "including", "file types", "technologies"]
    if any(keyword in description.lower() for keyword in context_keywords):
        score += 3
    else:
        issues.append("Missing CONTEXT (should mention 'works with')")

    return score, issues

def check_progressive_disclosure(skill_path: Path) -> Tuple[int, List[str]]:
    """Check if SKILL.md follows progressive disclosure (≤500 lines)"""
    issues = []

    try:
        with open(skill_path, 'r') as f:
            lines = f.readlines()

        line_count = len(lines)

        if line_count <= 350:
            return 3, []
        elif line_count <= 500:
            issues.append(f"SKILL.md has {line_count} lines (target ≤350)")
            return 2, issues
        else:
            issues.append(f"SKILL.md too long ({line_count} lines, max 500)")
            return 0, issues

    except Exception as e:
        return 0, [f"Error checking line count: {e}"]

def check_usage_section(skill_path: Path) -> Tuple[bool, List[str]]:
    """Check if skill has 'When to Use' or similar section"""
    try:
        with open(skill_path, 'r') as f:
            content = f.read().lower()

        usage_keywords = ["when to use", "usage", "purpose", "trigger"]
        if any(keyword in content for keyword in usage_keywords):
            return True, []
        else:
            return False, ["Missing 'When to Use' or 'Purpose' section"]

    except Exception as e:
        return False, [f"Error checking usage section: {e}"]

def check_directory_structure(skill_dir: Path) -> Tuple[Dict[str, bool], List[str]]:
    """Check supporting directory structure"""
    structure = {
        "examples": (skill_dir / "examples").is_dir(),
        "scripts": (skill_dir / "scripts").is_dir(),
        "templates": (skill_dir / "templates").is_dir(),
        "references": (skill_dir / "references").is_dir()
    }

    issues = []

    # Check for files in root (only SKILL.md allowed)
    root_files = [f for f in skill_dir.iterdir() if f.is_file()]
    non_skill_files = [f.name for f in root_files if f.name != "SKILL.md"]

    if non_skill_files:
        issues.append(f"Unexpected files in root: {', '.join(non_skill_files)}")

    return structure, issues

def validate_skill(skill_name: str) -> Dict:
    """Validate a single skill"""
    skill_dir = SKILLS_DIR / skill_name
    skill_path = skill_dir / "SKILL.md"

    result = {
        "skill": skill_name,
        "score": 0,
        "max_score": 10,
        "issues": [],
        "recommendations": []
    }

    if not skill_path.exists():
        result["issues"].append("SKILL.md not found")
        return result

    # 1. YAML Valid (2 points)
    yaml_valid, frontmatter, yaml_issues = extract_frontmatter(skill_path)
    if yaml_valid:
        result["score"] += 2
    else:
        result["issues"].extend(yaml_issues)
        result["recommendations"].append("Fix YAML frontmatter errors")

    # 2. Description Complete (3 points)
    if frontmatter and 'description' in frontmatter:
        desc_score, desc_issues = check_description_completeness(frontmatter['description'])
        result["score"] += min(desc_score, 3)  # Cap at 3 points
        result["issues"].extend(desc_issues)
        if desc_issues:
            result["recommendations"].append("Enhance description with WHAT, WHEN, TERMS, CONTEXT")

    # 3. Progressive Disclosure (3 points)
    disclosure_score, disclosure_issues = check_progressive_disclosure(skill_path)
    result["score"] += disclosure_score
    result["issues"].extend(disclosure_issues)
    if disclosure_issues:
        result["recommendations"].append("Move content to references/ or examples/ to keep SKILL.md lean")

    # 4. Usage Section (1 point)
    has_usage, usage_issues = check_usage_section(skill_path)
    if has_usage:
        result["score"] += 1
    else:
        result["issues"].extend(usage_issues)
        result["recommendations"].append("Add 'When to Use' section")

    # 5. Directory Structure (1 point)
    structure, struct_issues = check_directory_structure(skill_dir)
    if not struct_issues:
        result["score"] += 1
    else:
        result["issues"].extend(struct_issues)
        result["recommendations"].append("Move non-SKILL.md files to subdirectories")

    return result

def generate_report(results: List[Dict]) -> str:
    """Generate markdown report"""

    report = [
        "# Group 2 Skills Validation Report",
        "",
        f"**Date:** 2026-01-22",
        f"**Skills Validated:** {len(results)}",
        f"**Validation Criteria:** Anthropic Official Best Practices (2026-01-21)",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
    ]

    total_score = sum(r['score'] for r in results)
    max_possible = sum(r['max_score'] for r in results)
    avg_score = total_score / len(results) if results else 0

    report.extend([
        f"| Total Score | {total_score}/{max_possible} |",
        f"| Average Score | {avg_score:.1f}/10 |",
        f"| Skills with Score ≥8 | {len([r for r in results if r['score'] >= 8])} |",
        f"| Skills with Score <6 | {len([r for r in results if r['score'] < 6])} |",
        "",
        "## Detailed Results",
        ""
    ])

    # Sort by score (lowest first to highlight issues)
    sorted_results = sorted(results, key=lambda x: x['score'])

    for result in sorted_results:
        report.extend([
            f"### {result['skill']}",
            "",
            f"**Score:** {result['score']}/{result['max_score']}",
            ""
        ])

        if result['issues']:
            report.append("**Issues:**")
            for issue in result['issues']:
                report.append(f"- ❌ {issue}")
            report.append("")

        if result['recommendations']:
            report.append("**Recommendations:**")
            for rec in result['recommendations']:
                report.append(f"- 💡 {rec}")
            report.append("")

        if not result['issues']:
            report.append("✅ **No issues found**")
            report.append("")

        report.append("---")
        report.append("")

    return "\n".join(report)

def main():
    print(f"Validating {len(GROUP_2_SKILLS)} skills...")

    results = []
    for skill_name in GROUP_2_SKILLS:
        print(f"  Validating {skill_name}...")
        result = validate_skill(skill_name)
        results.append(result)

    report = generate_report(results)

    output_path = Path("/Users/dawiddutoit/projects/claude/custom-claude/.claude/artifacts/2026-01-22/validation/group-2-report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nReport generated: {output_path}")
    print(f"Total skills validated: {len(results)}")
    print(f"Average score: {sum(r['score'] for r in results) / len(results):.1f}/10")

if __name__ == "__main__":
    main()
