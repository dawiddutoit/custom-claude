#!/usr/bin/env python3
"""
Quick validation script for Group 4 skills (124-164)
Validates against Anthropic's Official Best Practices (2026-01-21)
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

SKILLS_DIR = Path("/Users/dawiddutoit/projects/claude/custom-claude/skills")

SKILLS_GROUP_4 = [
    "pytest-test-data-factories",
    "pytest-type-safety",
    "python-best-practices-async-context-manager",
    "python-best-practices-fail-fast-imports",
    "python-best-practices-type-safety",
    "python-micrometer-business-metrics",
    "python-micrometer-cardinality-control",
    "python-micrometer-core",
    "python-micrometer-gcp-cloud-monitoring",
    "python-micrometer-metrics-setup",
    "python-micrometer-sli-slo-monitoring",
    "python-test-micrometer-testing-metrics",
    "quality-capture-baseline",
    "quality-code-review",
    "quality-detect-orphaned-code",
    "quality-detect-refactor-markers",
    "quality-detect-regressions",
    "quality-reflective-questions",
    "quality-run-linting-formatting",
    "quality-run-quality-gates",
    "quality-run-type-checking",
    "quality-verify-implementation-complete",
    "quality-verify-integration",
    "scad-load",
    "setup-pytest-fixtures",
    "skill-creator",
    "slack-gif-creator",
    "svelte-add-accessibility",
    "svelte-add-component",
    "svelte-components",
    "svelte-create-spa",
    "svelte-deployment",
    "svelte-extract-component",
    "svelte-migrate-html-to-spa",
    "svelte-runes",
    "svelte-setup-state-store",
    "svelte5-showcase-components",
    "sveltekit-data-flow",
    "sveltekit-remote-functions",
    "sveltekit-structure",
    "temet-run-tui-patterns",
]


def extract_frontmatter(content: str) -> Tuple[str, str]:
    """Extract YAML frontmatter and body content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return "", content


def validate_skill(skill_name: str) -> Dict:
    """Validate a single skill against all criteria."""
    skill_path = SKILLS_DIR / skill_name
    skill_md = skill_path / "SKILL.md"

    result = {
        "name": skill_name,
        "score": 0,
        "issues": [],
        "recommendations": [],
        "exists": False,
    }

    # Check if SKILL.md exists
    if not skill_md.exists():
        result["issues"].append("❌ SKILL.md not found")
        return result

    result["exists"] = True

    # Read content
    content = skill_md.read_text(encoding='utf-8')
    frontmatter_str, body = extract_frontmatter(content)

    # 1. YAML Valid
    yaml_valid = False
    frontmatter = {}
    try:
        frontmatter = yaml.safe_load(frontmatter_str) or {}
        yaml_valid = True
        result["score"] += 1
    except yaml.YAMLError as e:
        result["issues"].append(f"❌ YAML Invalid: {e}")
        return result  # Can't continue without valid YAML

    # Check required fields
    if "name" not in frontmatter:
        result["issues"].append("❌ Missing 'name' field in frontmatter")
    else:
        result["score"] += 0.5

    if "description" not in frontmatter:
        result["issues"].append("❌ Missing 'description' field in frontmatter")
    else:
        result["score"] += 0.5

    # 2. Description Complete (WHAT, WHEN, TERMS, CONTEXT)
    description = frontmatter.get("description", "")
    desc_score = 0

    # Check for WHAT (first sentence/paragraph)
    if description and len(description.strip()) > 20:
        desc_score += 0.25
    else:
        result["issues"].append("❌ Description too short or missing")

    # Check for WHEN (trigger phrases)
    trigger_patterns = [
        r'[Uu]se when',
        r'[Tt]rigger',
        r'asked to',
        r'need to',
        r'want to',
    ]
    has_triggers = any(re.search(pattern, description) for pattern in trigger_patterns)
    if has_triggers:
        desc_score += 0.25
    else:
        result["issues"].append("⚠️  Description missing explicit trigger phrases ('Use when', 'Triggers on')")

    # Check for TERMS (domain-specific keywords)
    if len(description.split()) > 30:
        desc_score += 0.25
    else:
        result["recommendations"].append("💡 Consider adding more domain-specific terms for semantic matching")

    # Check for CONTEXT (file types, technologies)
    context_patterns = [
        r'[Ww]orks? with',
        r'\.py\b',
        r'\.js\b',
        r'\.ts\b',
        r'Python',
        r'JavaScript',
        r'TypeScript',
        r'files?',
        r'projects?',
    ]
    has_context = any(re.search(pattern, description) for pattern in context_patterns)
    if has_context:
        desc_score += 0.25
    else:
        result["recommendations"].append("💡 Add context: file types, technologies, or packages")

    result["score"] += desc_score

    # 3. Progressive Disclosure (≤500 lines, lean content)
    line_count = len(content.split('\n'))
    if line_count <= 350:
        result["score"] += 1
    elif line_count <= 500:
        result["score"] += 0.5
        result["recommendations"].append(f"💡 Consider reducing from {line_count} to <350 lines (move to references/)")
    else:
        result["issues"].append(f"❌ SKILL.md too long ({line_count} lines, target ≤350, max 500)")

    # 4. Usage Section exists
    usage_patterns = [
        r'##\s+[Ww]hen [Tt]o [Uu]se',
        r'##\s+[Uu]sage',
        r'##\s+[Ww]hen [Tt]o [Ii]nvoke',
        r'##\s+[Tt]riggers?',
    ]
    has_usage = any(re.search(pattern, body, re.MULTILINE) for pattern in usage_patterns)
    if has_usage:
        result["score"] += 1
    else:
        result["issues"].append("❌ Missing 'When to Use' or 'Usage' section")

    # 5. Advanced Features justified (if present)
    has_allowed_tools = "allowed-tools" in frontmatter
    has_disable_invocation = frontmatter.get("disable-model-invocation", False)
    has_user_invocable = "user-invocable" in frontmatter

    if has_allowed_tools or has_disable_invocation or has_user_invocable:
        # Check for justification in body
        justification_patterns = [
            r'read-only',
            r'validation',
            r'side effects',
            r'explicit',
            r'background',
            r'context-only',
        ]
        has_justification = any(re.search(pattern, body, re.IGNORECASE) for pattern in justification_patterns)
        if has_justification:
            result["score"] += 1
        else:
            result["recommendations"].append("💡 Justify advanced features (allowed-tools, disable-model-invocation, user-invocable)")
    else:
        result["score"] += 1  # No advanced features to justify

    # 6-9. Check supporting structure
    examples_dir = skill_path / "examples"
    scripts_dir = skill_path / "scripts"
    templates_dir = skill_path / "templates"
    references_dir = skill_path / "references"

    # 6. Examples Structure
    if examples_dir.exists():
        examples_files = list(examples_dir.glob("*.md"))
        if examples_files:
            result["score"] += 0.5
        else:
            result["recommendations"].append("💡 examples/ directory exists but is empty")
    else:
        result["score"] += 0.5  # Optional, no penalty

    # 7. Scripts Structure
    if scripts_dir.exists():
        script_files = list(scripts_dir.glob("*"))
        if script_files:
            result["score"] += 0.5
        else:
            result["recommendations"].append("💡 scripts/ directory exists but is empty")
    else:
        result["score"] += 0.5  # Optional

    # 8. Templates Structure
    if templates_dir.exists():
        template_files = list(templates_dir.glob("*"))
        if template_files:
            result["score"] += 0.5
        else:
            result["recommendations"].append("💡 templates/ directory exists but is empty")
    else:
        result["score"] += 0.5  # Optional

    # 9. References Structure
    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        if ref_files:
            result["score"] += 0.5
        else:
            result["recommendations"].append("💡 references/ directory exists but is empty")
    else:
        result["score"] += 0.5  # Optional

    # 10. Cross-References Valid (basic check)
    # Look for broken references in body
    ref_links = re.findall(r'\[.*?\]\((.*?)\)', body)
    broken_refs = []
    for link in ref_links:
        if not link.startswith('http') and not link.startswith('#'):
            # Relative file reference
            ref_path = skill_path / link
            if not ref_path.exists():
                broken_refs.append(link)

    if broken_refs:
        result["issues"].append(f"❌ Broken cross-references: {', '.join(broken_refs[:3])}")
    else:
        result["score"] += 1

    # Cap score at 10
    result["score"] = min(10, result["score"])

    return result


def generate_report(results: List[Dict]) -> str:
    """Generate markdown report."""
    report = """# Group 4 Skill Validation Report

**Validation Date:** 2026-01-22
**Skills Validated:** 41 (Skills 124-164)
**Validation Criteria:** Anthropic's Official Best Practices (2026-01-21)

## Summary Statistics

"""

    total_skills = len(results)
    existing_skills = sum(1 for r in results if r["exists"])
    avg_score = sum(r["score"] for r in results if r["exists"]) / max(existing_skills, 1)
    excellent = sum(1 for r in results if r["score"] >= 9)
    good = sum(1 for r in results if 7 <= r["score"] < 9)
    needs_work = sum(1 for r in results if r["score"] < 7)

    report += f"""- **Total Skills:** {total_skills}
- **Existing Skills:** {existing_skills}
- **Average Score:** {avg_score:.1f}/10
- **Excellent (9-10):** {excellent}
- **Good (7-8.9):** {good}
- **Needs Work (<7):** {needs_work}

## Validation Criteria

1. **YAML Valid** - Frontmatter with name, description
2. **Description Complete** - WHAT, WHEN, TERMS, CONTEXT with trigger phrases
3. **Progressive Disclosure** - ≤500 lines (target ≤350)
4. **Usage Section** - "When to Use" or "Usage" section exists
5. **Advanced Features Justified** - allowed-tools, disable-model-invocation explained
6. **Examples Structure** - If /examples/ exists, contains .md files
7. **Scripts Structure** - If /scripts/ exists, contains files
8. **Templates Structure** - If /templates/ exists, contains files
9. **References Structure** - If /references/ exists, contains .md files
10. **Cross-References Valid** - All internal links work

## Detailed Results

"""

    # Sort by score (lowest first to highlight issues)
    sorted_results = sorted(results, key=lambda x: (x["score"], x["name"]))

    for r in sorted_results:
        if not r["exists"]:
            report += f"\n### ❌ {r['name']}\n\n"
            report += f"**Score:** N/A (SKILL.md not found)\n\n"
            continue

        emoji = "🟢" if r["score"] >= 9 else "🟡" if r["score"] >= 7 else "🔴"
        report += f"\n### {emoji} {r['name']}\n\n"
        report += f"**Score:** {r['score']:.1f}/10\n\n"

        if r["issues"]:
            report += "**Issues:**\n"
            for issue in r["issues"]:
                report += f"- {issue}\n"
            report += "\n"

        if r["recommendations"]:
            report += "**Recommendations:**\n"
            for rec in r["recommendations"]:
                report += f"- {rec}\n"
            report += "\n"

    # Priority Actions
    report += "\n## Priority Actions\n\n"

    high_priority = [r for r in sorted_results if r["exists"] and r["score"] < 7]
    if high_priority:
        report += "### High Priority (Score < 7)\n\n"
        for r in high_priority:
            report += f"- **{r['name']}** (Score: {r['score']:.1f})\n"
            if r["issues"]:
                report += f"  - {r['issues'][0]}\n"
        report += "\n"

    medium_priority = [r for r in sorted_results if r["exists"] and 7 <= r["score"] < 9]
    if medium_priority:
        report += "### Medium Priority (Score 7-8.9)\n\n"
        for r in medium_priority:
            report += f"- **{r['name']}** (Score: {r['score']:.1f})\n"
            if r["recommendations"]:
                report += f"  - {r['recommendations'][0]}\n"
        report += "\n"

    report += "\n## Notes\n\n"
    report += "- This is a quick validation focused on structure and completeness\n"
    report += "- Issues identified should be addressed by skill owners\n"
    report += "- Scores are relative to Anthropic's Official Best Practices (2026-01-21)\n"
    report += "- Progressive disclosure target: ≤350 lines, max 500 lines\n"

    return report


def main():
    print("Validating Group 4 Skills (124-164)...")
    print(f"Skills directory: {SKILLS_DIR}")
    print(f"Total skills to validate: {len(SKILLS_GROUP_4)}\n")

    results = []
    for skill_name in SKILLS_GROUP_4:
        print(f"Validating {skill_name}...", end=" ")
        result = validate_skill(skill_name)
        results.append(result)
        if result["exists"]:
            print(f"Score: {result['score']:.1f}/10")
        else:
            print("NOT FOUND")

    print("\nGenerating report...")
    report = generate_report(results)

    output_path = Path("/Users/dawiddutoit/projects/claude/custom-claude/.claude/artifacts/2026-01-22/validation/group-4-report.md")
    output_path.write_text(report, encoding='utf-8')

    print(f"\n✅ Report generated: {output_path}")
    print(f"\nSummary:")
    print(f"- Total: {len(results)}")
    print(f"- Existing: {sum(1 for r in results if r['exists'])}")
    print(f"- Average Score: {sum(r['score'] for r in results if r['exists']) / max(sum(1 for r in results if r['exists']), 1):.1f}/10")


if __name__ == "__main__":
    main()
