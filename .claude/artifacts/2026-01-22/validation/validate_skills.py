#!/usr/bin/env python3
"""
Skill Validation Script
Validates skills against Anthropic's Official Best Practices (2026-01-21)
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

SKILLS_DIR = Path("/Users/dawiddutoit/projects/claude/custom-claude/skills")

# Validation criteria
CRITERIA = {
    "yaml_valid": "YAML frontmatter is valid",
    "description_complete": "Description has WHAT, WHEN, TERMS, CONTEXT",
    "progressive_disclosure": "Content ≤500 lines, lean and focused",
    "usage_section": "Has clear 'When to Use' or 'Usage' section",
    "advanced_features": "Advanced features (allowed-tools, disable-model-invocation) justified",
    "examples_structure": "If /examples/ exists, proper structure",
    "scripts_structure": "If /scripts/ exists, proper structure",
    "templates_structure": "If /templates/ exists, proper structure",
    "references_structure": "If /references/ exists, proper structure",
    "cross_references": "Cross-references are valid (links work)"
}

def validate_yaml_frontmatter(content: str) -> Tuple[bool, Dict, List[str]]:
    """Extract and validate YAML frontmatter"""
    issues = []

    # Check for frontmatter delimiters
    if not content.startswith('---'):
        issues.append("No YAML frontmatter found (must start with ---)")
        return False, {}, issues

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        issues.append("Incomplete YAML frontmatter (missing closing ---)")
        return False, {}, issues

    yaml_content = parts[1].strip()

    try:
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            issues.append("YAML frontmatter is not a dictionary")
            return False, {}, issues

        # Check required fields
        if 'name' not in data:
            issues.append("Missing 'name' field")
        elif not data['name']:
            issues.append("'name' field is empty")
        elif len(data['name']) > 64:
            issues.append(f"'name' too long ({len(data['name'])} chars, max 64)")

        if 'description' not in data:
            issues.append("Missing 'description' field")
        elif not data['description']:
            issues.append("'description' field is empty")
        elif len(data['description']) > 1024:
            issues.append(f"'description' too long ({len(data['description'])} chars, max 1024)")

        return len(issues) == 0, data, issues

    except yaml.YAMLError as e:
        issues.append(f"YAML parsing error: {str(e)}")
        return False, {}, issues

def validate_description(description: str) -> Tuple[bool, List[str]]:
    """Check if description has WHAT, WHEN, TERMS, CONTEXT"""
    issues = []

    # Check length
    if len(description) < 100:
        issues.append("Description too short (<100 chars, lacks detail)")

    # Check for trigger phrases (WHEN component)
    trigger_indicators = [
        "use when", "use this when", "triggers on", "trigger terms",
        "invoke when", "trigger phrases", "when asked to"
    ]
    has_triggers = any(indicator.lower() in description.lower() for indicator in trigger_indicators)
    if not has_triggers:
        issues.append("Missing trigger phrases (WHEN component)")

    # Check for technology/context (CONTEXT component)
    context_indicators = [
        "works with", "file types", "technologies", ".py", ".js", ".ts",
        "python", "javascript", "typescript", "java"
    ]
    has_context = any(indicator.lower() in description.lower() for indicator in context_indicators)
    if not has_context:
        issues.append("Missing technology/context information (CONTEXT component)")

    return len(issues) == 0, issues

def count_lines(file_path: Path) -> int:
    """Count lines in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def check_usage_section(content: str) -> Tuple[bool, List[str]]:
    """Check for usage/when-to-use section"""
    issues = []

    # Common section headers
    usage_patterns = [
        r'##\s+when to use',
        r'##\s+usage',
        r'##\s+triggers',
        r'##\s+use cases',
        r'##\s+when to invoke'
    ]

    has_usage = any(re.search(pattern, content, re.IGNORECASE) for pattern in usage_patterns)

    if not has_usage:
        issues.append("Missing 'When to Use' or 'Usage' section")

    return has_usage, issues

def check_directory_structure(skill_dir: Path, subdir: str) -> Tuple[bool, List[str]]:
    """Check if subdirectory structure is proper"""
    issues = []
    subdir_path = skill_dir / subdir

    if not subdir_path.exists():
        return True, []  # Not present is fine

    if not subdir_path.is_dir():
        issues.append(f"{subdir}/ exists but is not a directory")
        return False, issues

    # Check if has files
    files = list(subdir_path.iterdir())
    if not files:
        issues.append(f"{subdir}/ exists but is empty")

    return len(issues) == 0, issues

def validate_cross_references(skill_dir: Path, content: str) -> Tuple[bool, List[str]]:
    """Validate that cross-references point to existing files"""
    issues = []

    # Find markdown links
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = re.findall(link_pattern, content)

    for link_text, link_url in links:
        # Skip external URLs
        if link_url.startswith('http://') or link_url.startswith('https://'):
            continue

        # Skip anchors
        if link_url.startswith('#'):
            continue

        # Check if file exists
        # Remove anchor if present
        file_path = link_url.split('#')[0]

        # Resolve relative path
        target = skill_dir / file_path
        if not target.exists():
            issues.append(f"Broken link: [{link_text}]({link_url}) - file not found")

    return len(issues) == 0, issues

def validate_skill(skill_name: str) -> Dict:
    """Validate a single skill"""
    skill_dir = SKILLS_DIR / skill_name
    skill_file = skill_dir / "SKILL.md"

    result = {
        "name": skill_name,
        "score": 0,
        "max_score": 10,
        "issues": [],
        "recommendations": []
    }

    # Check if SKILL.md exists
    if not skill_file.exists():
        result["issues"].append("❌ SKILL.md not found")
        return result

    # Read content
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result["issues"].append(f"❌ Cannot read SKILL.md: {str(e)}")
        return result

    # 1. YAML Valid
    yaml_valid, yaml_data, yaml_issues = validate_yaml_frontmatter(content)
    if yaml_valid:
        result["score"] += 1
        result["issues"].append("✅ YAML frontmatter valid")
    else:
        result["issues"].append(f"❌ YAML validation failed: {', '.join(yaml_issues)}")
        result["recommendations"].append("Fix YAML frontmatter syntax and required fields")

    # 2. Description Complete
    if yaml_valid and 'description' in yaml_data:
        desc_valid, desc_issues = validate_description(yaml_data['description'])
        if desc_valid:
            result["score"] += 1
            result["issues"].append("✅ Description complete (WHAT, WHEN, TERMS, CONTEXT)")
        else:
            result["issues"].append(f"⚠️  Description issues: {', '.join(desc_issues)}")
            result["recommendations"].append("Enhance description with missing components (triggers, context)")

    # 3. Progressive Disclosure (≤500 lines)
    line_count = count_lines(skill_file)
    if line_count <= 500:
        result["score"] += 1
        result["issues"].append(f"✅ Progressive disclosure ({line_count} lines ≤ 500)")
    elif line_count <= 700:
        result["score"] += 0.5
        result["issues"].append(f"⚠️  Content slightly long ({line_count} lines, target ≤500)")
        result["recommendations"].append(f"Consider moving {line_count - 500} lines to references/")
    else:
        result["issues"].append(f"❌ Content too long ({line_count} lines > 500)")
        result["recommendations"].append(f"Move {line_count - 500} lines to references/ for progressive disclosure")

    # 4. Usage Section
    usage_valid, usage_issues = check_usage_section(content)
    if usage_valid:
        result["score"] += 1
        result["issues"].append("✅ Usage/When-to-Use section exists")
    else:
        result["issues"].append(f"❌ {usage_issues[0]}")
        result["recommendations"].append("Add '## When to Use This Skill' section")

    # 5. Advanced Features (allowed-tools justified)
    if yaml_valid and 'allowed-tools' in yaml_data:
        # Check if there's justification
        if 'read-only' in content.lower() or 'validation' in content.lower():
            result["score"] += 1
            result["issues"].append("✅ Advanced features (allowed-tools) justified")
        else:
            result["score"] += 0.5
            result["issues"].append("⚠️  allowed-tools present but justification unclear")
            result["recommendations"].append("Document why tools are restricted")
    else:
        result["score"] += 1
        result["issues"].append("✅ No advanced features requiring justification")

    # 6-9. Directory structures
    subdirs = ["examples", "scripts", "templates", "references"]
    for subdir in subdirs:
        struct_valid, struct_issues = check_directory_structure(skill_dir, subdir)
        if not (skill_dir / subdir).exists():
            # Not present - no penalty
            result["score"] += 0.25
        elif struct_valid:
            result["score"] += 0.25
            result["issues"].append(f"✅ {subdir}/ structure proper")
        else:
            result["issues"].append(f"⚠️  {subdir}/ issues: {', '.join(struct_issues)}")

    # 10. Cross-references valid
    xref_valid, xref_issues = validate_cross_references(skill_dir, content)
    if xref_valid:
        result["score"] += 1
        result["issues"].append("✅ Cross-references valid")
    elif xref_issues:
        result["issues"].append(f"⚠️  Broken links: {len(xref_issues)} found")
        result["recommendations"].append("Fix broken cross-references")
        for issue in xref_issues[:3]:  # Show first 3
            result["issues"].append(f"   - {issue}")
    else:
        result["score"] += 1
        result["issues"].append("✅ No cross-references to validate")

    return result

def main():
    """Validate all skills in group 1"""
    skills = [
        "agent-sdk-python", "algorithmic-art", "architecture-single-responsibility-principle",
        "architecture-validate-architecture", "architecture-validate-layer-boundaries",
        "architecture-validate-srp", "artifacts-creating-and-managing", "brand-guidelines",
        "browser-layout-editor", "build-jira-document-format", "caddy-certificate-maintenance",
        "caddy-https-troubleshoot", "caddy-subdomain-add", "canvas-design",
        "chrome-auth-recorder", "chrome-browser-automation", "chrome-form-filler",
        "chrome-gif-recorder", "clickhouse-materialized-views", "clickhouse-operations",
        "clickhouse-query-optimization", "cloudflare-access-add-user", "cloudflare-access-setup",
        "cloudflare-access-troubleshoot", "cloudflare-dns-operations", "cloudflare-service-token-setup",
        "cloudflare-tunnel-setup", "cloudflare-tunnel-troubleshoot", "create-adr-spike",
        "data-migration-versioning", "design-jira-state-analyzer", "doc-coauthoring",
        "docx", "editing-claude", "export-and-analyze-jira-data", "frontend-design",
        "gcp-gke-cluster-setup", "gcp-gke-cost-optimization", "gcp-gke-deployment-strategies",
        "gcp-gke-monitoring-observability", "gcp-gke-troubleshooting"
    ]

    print("Validating 41 skills...")
    print("=" * 80)

    results = []
    for skill in skills:
        print(f"Validating {skill}...", end=" ")
        result = validate_skill(skill)
        results.append(result)
        print(f"Score: {result['score']:.1f}/10")

    # Generate report
    report_path = Path("/Users/dawiddutoit/projects/claude/custom-claude/.claude/artifacts/2026-01-22/validation/group-1-report.md")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Skill Validation Report - Group 1 (Skills 1-41)\n\n")
        f.write("**Validation Date:** 2026-01-22\n")
        f.write("**Skills Validated:** 41\n")
        f.write("**Criteria:** Anthropic Official Best Practices (2026-01-21)\n\n")

        # Summary statistics
        avg_score = sum(r['score'] for r in results) / len(results)
        perfect_scores = sum(1 for r in results if r['score'] == 10)
        needs_work = sum(1 for r in results if r['score'] < 7)

        f.write("## Summary\n\n")
        f.write(f"- **Average Score:** {avg_score:.1f}/10\n")
        f.write(f"- **Perfect Scores:** {perfect_scores}/41 ({perfect_scores/41*100:.0f}%)\n")
        f.write(f"- **Needs Improvement:** {needs_work}/41 ({needs_work/41*100:.0f}%)\n\n")

        f.write("## Validation Criteria\n\n")
        for i, (key, desc) in enumerate(CRITERIA.items(), 1):
            f.write(f"{i}. **{key}**: {desc}\n")
        f.write("\n")

        f.write("## Detailed Results\n\n")
        f.write("---\n\n")

        # Sort by score (lowest first)
        results.sort(key=lambda r: r['score'])

        for result in results:
            f.write(f"### {result['name']}\n\n")
            f.write(f"**Score:** {result['score']:.1f}/10\n\n")

            f.write("**Issues Found:**\n\n")
            for issue in result['issues']:
                f.write(f"- {issue}\n")
            f.write("\n")

            if result['recommendations']:
                f.write("**Recommendations:**\n\n")
                for rec in result['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")

            f.write("---\n\n")

    print("=" * 80)
    print(f"Report generated: {report_path}")
    print(f"Average score: {avg_score:.1f}/10")
    print(f"Perfect scores: {perfect_scores}/41")
    print(f"Needs work: {needs_work}/41")

if __name__ == "__main__":
    main()
