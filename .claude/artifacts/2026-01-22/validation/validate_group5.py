#!/usr/bin/env python3
"""
Validation script for Group 5 skills (165-205)
Validates skills against Anthropic's Official Best Practices (2026-01-21)
"""

import os
import re
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ValidationResult:
    skill_name: str
    score: int
    issues: List[str]
    recommendations: List[str]

SKILLS_GROUP_5 = [
    "terraform-basics", "terraform-gcp-integration", "terraform-module-design",
    "terraform-secrets-management", "terraform-state-management", "terraform-troubleshooting",
    "test-debug-failures", "test-first-thinking", "test-implement-constructor-validation",
    "test-implement-factory-fixtures", "test-organize-layers", "test-property-based",
    "test-setup-async", "textual-app-lifecycle", "textual-data-display",
    "textual-event-messages", "textual-layout-styling", "textual-reactive-programming",
    "textual-snapshot-testing", "textual-test-fixtures", "textual-test-patterns",
    "textual-testing", "textual-widget-development", "theme-factory",
    "util-manage-todo", "util-multi-file-refactor", "util-research-library",
    "util-resolve-serviceresult-errors", "uv-ci-cd-integration", "uv-dependency-management",
    "uv-project-migration", "uv-project-setup", "uv-python-version-management",
    "uv-tool-management", "uv-troubleshooting", "validating-clickhouse-kafka-pipelines",
    "web-artifacts-builder", "webapp-testing", "work-with-adf", "write-atomic-tasks", "xlsx"
]

def extract_frontmatter(content: str) -> Optional[Dict]:
    """Extract YAML frontmatter from SKILL.md"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None

def count_lines(content: str) -> int:
    """Count non-empty lines"""
    return len([line for line in content.split('\n') if line.strip()])

def has_section(content: str, section: str) -> bool:
    """Check if content has a specific section"""
    patterns = [
        rf'#+\s*{re.escape(section)}',
        rf'#+\s*{re.escape(section.replace("-", " "))}',
        rf'##\s*{re.escape(section)}'
    ]
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)

def validate_description(desc: str) -> tuple[bool, List[str]]:
    """Validate description has WHAT, WHEN, TERMS, CONTEXT"""
    issues = []

    # Check length
    if len(desc) > 1024:
        issues.append(f"Description too long: {len(desc)} chars (max 1024)")

    # Check for trigger phrases (WHEN)
    trigger_indicators = ['use when', 'trigger', 'when asked', 'when you need']
    has_triggers = any(indicator in desc.lower() for indicator in trigger_indicators)
    if not has_triggers:
        issues.append("Missing trigger phrases (WHEN component)")

    # Check for context (CONTEXT)
    context_indicators = ['works with', 'covers', 'includes', 'supports']
    has_context = any(indicator in desc.lower() for indicator in context_indicators)
    if not has_context:
        issues.append("Missing context (CONTEXT component - file types/technologies)")

    # Check if description has substance (WHAT + TERMS)
    if len(desc.strip()) < 100:
        issues.append("Description too brief - needs more detail about WHAT and key TERMS")

    return len(issues) == 0, issues

def check_cross_references(content: str, skill_path: Path) -> List[str]:
    """Check if cross-references are valid"""
    issues = []

    # Find markdown links
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)

    for link_text, link_path in links:
        # Skip external URLs
        if link_path.startswith('http'):
            continue

        # Check relative paths
        if link_path.startswith('./') or link_path.startswith('../'):
            full_path = (skill_path.parent / link_path).resolve()
            if not full_path.exists():
                issues.append(f"Broken cross-reference: [{link_text}]({link_path})")

    return issues

def validate_skill(skills_dir: Path, skill_name: str) -> ValidationResult:
    """Validate a single skill"""
    skill_path = skills_dir / skill_name
    skill_md = skill_path / "SKILL.md"

    issues = []
    recommendations = []
    score = 10

    # Check 1: SKILL.md exists
    if not skill_md.exists():
        issues.append("SKILL.md missing")
        return ValidationResult(skill_name, 0, issues, ["Create SKILL.md file"])

    # Read content
    content = skill_md.read_text()

    # Check 2: YAML frontmatter valid
    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        issues.append("Invalid or missing YAML frontmatter")
        score -= 3
    else:
        # Check required fields
        if 'name' not in frontmatter:
            issues.append("Missing 'name' in frontmatter")
            score -= 1
        elif frontmatter['name'] != skill_name:
            issues.append(f"Name mismatch: '{frontmatter['name']}' != '{skill_name}'")
            score -= 1

        if 'description' not in frontmatter:
            issues.append("Missing 'description' in frontmatter")
            score -= 2
        else:
            desc_valid, desc_issues = validate_description(frontmatter['description'])
            if not desc_valid:
                issues.extend(desc_issues)
                score -= len(desc_issues) * 0.5

        # Check for version (optional but recommended)
        if 'version' not in frontmatter:
            recommendations.append("Add 'version' field to frontmatter")

    # Check 3: Progressive Disclosure (≤500 lines)
    line_count = count_lines(content)
    if line_count > 500:
        issues.append(f"SKILL.md too long: {line_count} lines (target ≤500)")
        score -= 1
        recommendations.append(f"Move {line_count - 500} lines to references/ or examples/")
    elif line_count > 400:
        recommendations.append(f"Consider moving content to references/ ({line_count} lines, approaching limit)")

    # Check 4: Usage section exists
    usage_sections = ['when to use', 'usage', 'when to use this skill']
    has_usage = any(has_section(content, section) for section in usage_sections)
    if not has_usage:
        issues.append("Missing 'When to Use' or 'Usage' section")
        score -= 1

    # Check 5: Advanced features justified (if present)
    if frontmatter and 'allowed-tools' in frontmatter:
        # Check if there's justification for tool restrictions
        if not has_section(content, 'requirements') and not has_section(content, 'constraints'):
            recommendations.append("Document why allowed-tools is restricted")

    if frontmatter and 'disable-model-invocation' in frontmatter:
        recommendations.append("Verify disable-model-invocation is necessary (side effects?)")

    # Check 6-9: Supporting directories structure
    examples_dir = skill_path / "examples"
    scripts_dir = skill_path / "scripts"
    templates_dir = skill_path / "templates"
    references_dir = skill_path / "references"

    if examples_dir.exists():
        example_files = list(examples_dir.glob("*.md"))
        if len(example_files) == 0:
            issues.append("examples/ directory exists but is empty")
            score -= 0.5

    if scripts_dir.exists():
        script_files = list(scripts_dir.glob("*"))
        script_files = [f for f in script_files if not f.name.startswith('.')]
        if len(script_files) == 0:
            issues.append("scripts/ directory exists but is empty")
            score -= 0.5
        else:
            # Check if scripts are documented in SKILL.md
            if not has_section(content, 'scripts') and not has_section(content, 'utility scripts'):
                recommendations.append("Document scripts/ utilities in SKILL.md")

    if templates_dir.exists():
        template_files = list(templates_dir.glob("*"))
        if len(template_files) == 0:
            issues.append("templates/ directory exists but is empty")
            score -= 0.5

    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        if len(ref_files) == 0:
            issues.append("references/ directory exists but is empty")
            score -= 0.5
        else:
            # Check if references are mentioned in SKILL.md
            for ref_file in ref_files:
                if ref_file.name not in content:
                    recommendations.append(f"Cross-reference {ref_file.name} in SKILL.md")

    # Check 10: Cross-references valid
    cross_ref_issues = check_cross_references(content, skill_path)
    if cross_ref_issues:
        issues.extend(cross_ref_issues)
        score -= len(cross_ref_issues) * 0.5

    # Ensure score is within bounds
    score = max(0, min(10, score))

    return ValidationResult(skill_name, round(score, 1), issues, recommendations)

def generate_report(results: List[ValidationResult], output_file: Path):
    """Generate markdown validation report"""

    report = []
    report.append("# Group 5 Skills Validation Report")
    report.append("")
    report.append("**Validation Date:** 2026-01-22")
    report.append(f"**Skills Validated:** {len(results)}")
    report.append("")

    # Summary statistics
    avg_score = sum(r.score for r in results) / len(results)
    perfect_scores = len([r for r in results if r.score == 10])
    needs_work = len([r for r in results if r.score < 7])

    report.append("## Summary")
    report.append("")
    report.append(f"- **Average Score:** {avg_score:.1f}/10")
    report.append(f"- **Perfect Scores (10/10):** {perfect_scores}")
    report.append(f"- **Needs Improvement (<7/10):** {needs_work}")
    report.append("")

    # Sort by score (lowest first to highlight issues)
    sorted_results = sorted(results, key=lambda r: (r.score, r.skill_name))

    report.append("## Validation Results")
    report.append("")

    for result in sorted_results:
        report.append(f"### {result.skill_name}")
        report.append("")
        report.append(f"**Score:** {result.score}/10")
        report.append("")

        if result.issues:
            report.append("**Issues Found:**")
            for issue in result.issues:
                report.append(f"- ❌ {issue}")
            report.append("")
        else:
            report.append("**Issues Found:** None ✅")
            report.append("")

        if result.recommendations:
            report.append("**Recommendations:**")
            for rec in result.recommendations:
                report.append(f"- 💡 {rec}")
            report.append("")

        report.append("---")
        report.append("")

    # Write report
    output_file.write_text('\n'.join(report))
    print(f"✅ Report generated: {output_file}")

def main():
    # Paths
    repo_root = Path("/Users/dawiddutoit/projects/claude/custom-claude")
    skills_dir = repo_root / "skills"
    output_file = repo_root / ".claude/artifacts/2026-01-22/validation/group-5-report.md"

    print("🔍 Validating Group 5 skills...")
    print(f"Skills directory: {skills_dir}")
    print(f"Output file: {output_file}")
    print("")

    results = []
    for skill_name in SKILLS_GROUP_5:
        print(f"Validating {skill_name}...", end=" ")
        result = validate_skill(skills_dir, skill_name)
        results.append(result)
        print(f"{result.score}/10")

    print("")
    print("📊 Generating report...")
    generate_report(results, output_file)
    print("")
    print("✅ Validation complete!")

if __name__ == "__main__":
    main()
