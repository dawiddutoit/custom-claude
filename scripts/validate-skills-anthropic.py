#!/usr/bin/env python3
"""
Skill Validation Script - Anthropic Best Practices Aligned
===========================================================

Validates 190+ skills against Anthropic's official best practices.

Usage:
    python validate-skills-anthropic.py [skill-path]
    python validate-skills-anthropic.py --all
    python validate-skills-anthropic.py --update-inventory

Based on: Anthropic Skill Best Practices (2026-01-21)
Source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
"""

import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Results from validating a single skill"""
    skill_name: str
    checks: Dict[str, bool] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: int = 0
    total_checks: int = 10

    def add_pass(self, check_name: str):
        """Mark a check as passed"""
        self.checks[check_name] = True
        self.score += 1

    def add_fail(self, check_name: str, issue: str):
        """Mark a check as failed with issue description"""
        self.checks[check_name] = False
        self.issues.append(f"[{check_name}] {issue}")

    def add_warning(self, check_name: str, warning: str):
        """Add a warning without failing the check"""
        self.warnings.append(f"[{check_name}] {warning}")


class SkillValidator:
    """Validates skills against Anthropic best practices"""

    # Anthropic constraints
    MAX_NAME_LENGTH = 64
    MAX_DESC_LENGTH = 1024
    RESERVED_WORDS = ["anthropic", "claude"]
    MAX_SKILL_LINES = 500
    TARGET_SKILL_LINES = 350

    # Gerund naming patterns (preferred)
    GERUND_PATTERN = re.compile(r'^[a-z]+-[a-z]+-[a-z]+ing$|^[a-z]+-[a-z]+ing$|^[a-z]+ing$')

    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.skill_name = skill_path.name
        self.skill_md_path = skill_path / "SKILL.md"
        self.result = ValidationResult(skill_name=self.skill_name)

    def validate(self) -> ValidationResult:
        """Run all validation checks"""

        # Check 1: YAML Valid with Constraints
        yaml_data = self._validate_yaml_constraints()

        if yaml_data:
            # Check 2: Description Complete (4 elements)
            self._validate_description_complete(yaml_data.get('description', ''))

            # Check 5: Advanced Features Justified
            self._validate_advanced_features(yaml_data)

        # Check 3: Progressive Disclosure
        self._validate_progressive_disclosure()

        # Check 4: Usage Section
        self._validate_usage_section()

        # Check 6-9: Directory Structure
        self._validate_examples_structure()
        self._validate_scripts_structure()
        self._validate_templates_structure()
        self._validate_references_structure()

        # Check 10: Cross-References
        self._validate_cross_references()

        return self.result

    def _validate_yaml_constraints(self) -> Optional[Dict]:
        """
        Check 1: YAML Valid with Anthropic Constraints
        - name: max 64 chars, kebab-case, no reserved words
        - description: max 1024 chars, third-person, non-empty
        - Naming: preferred gerund form
        """
        if not self.skill_md_path.exists():
            self.result.add_fail("YAML", "SKILL.md not found")
            return None

        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            self.result.add_fail("YAML", "No YAML frontmatter found")
            return None

        try:
            yaml_data = yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError as e:
            self.result.add_fail("YAML", f"YAML parse error: {e}")
            return None

        # Validate name field
        name = yaml_data.get('name', '')
        if not name:
            self.result.add_fail("YAML", "Missing 'name' field")
        elif len(name) > self.MAX_NAME_LENGTH:
            self.result.add_fail("YAML", f"Name exceeds {self.MAX_NAME_LENGTH} chars (got {len(name)})")
        elif not re.match(r'^[a-z0-9-]+$', name):
            self.result.add_fail("YAML", "Name must be lowercase letters, numbers, hyphens only")
        elif any(word in name for word in self.RESERVED_WORDS):
            self.result.add_fail("YAML", f"Name contains reserved word: {self.RESERVED_WORDS}")
        elif name != self.skill_name:
            self.result.add_fail("YAML", f"Name '{name}' doesn't match directory '{self.skill_name}'")
        else:
            # Check naming convention (warning only)
            if not self.GERUND_PATTERN.match(name):
                self.result.add_warning("YAML", f"Consider gerund form naming (e.g., 'processing-pdfs' not 'pdf-processor')")
            self.result.add_pass("YAML")

        # Validate description field
        description = yaml_data.get('description', '')
        if not description:
            self.result.add_fail("YAML", "Missing 'description' field")
        elif len(description) > self.MAX_DESC_LENGTH:
            self.result.add_fail("YAML", f"Description exceeds {self.MAX_DESC_LENGTH} chars (got {len(description)})")
        elif '<' in description or '>' in description:
            self.result.add_fail("YAML", "Description should not contain XML tags")

        # Check third-person voice (heuristic: shouldn't start with "You")
        if description.strip().startswith("You "):
            self.result.add_warning("YAML", "Description should be in third person, not 'You...'")

        return yaml_data

    def _validate_description_complete(self, description: str):
        """
        Check 2: Description Complete (3 required elements per Anthropic)
        - [WHAT] - What the skill does (action verbs)
        - [WHEN] - Use when... with trigger phrases
        - [TERMS] - Key terms for semantic matching (implicit)

        Based on: https://code.claude.com/docs/en/skills#extend-claude-with-skills
        """
        if not description:
            self.result.add_fail("Desc", "Empty description")
            return

        issues = []

        # Check for WHAT (capability statement) - heuristic: contains action verbs
        action_verbs = ['creates', 'manages', 'validates', 'analyzes', 'implements', 'configures',
                       'provides', 'enables', 'supports', 'handles', 'processes', 'generates',
                       'evaluates', 'parses', 'adds', 'identifies', 'detects', 'monitors']
        if not any(verb in description.lower() for verb in action_verbs):
            issues.append("Missing WHAT (capability statement with action verbs)")

        # Check for WHEN (trigger phrases) - should contain "use when" or "trigger"
        if not any(phrase in description.lower() for phrase in ['use when', 'triggers on', 'trigger with']):
            issues.append("Missing WHEN (trigger phrases with 'use when' or 'trigger')")

        # TERMS are implicit if the description is detailed enough with domain keywords

        if issues:
            self.result.add_fail("Desc", " | ".join(issues))
        else:
            self.result.add_pass("Desc")

    def _validate_progressive_disclosure(self):
        """
        Check 3: Progressive Disclosure
        - SKILL.md <500 lines (warn if >350)
        - Contains 1-2 inline examples (code blocks allowed)
        - References heavy content appropriately
        """
        if not self.skill_md_path.exists():
            return

        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        line_count = len(lines)
        content = ''.join(lines)

        # Check line count
        if line_count > self.MAX_SKILL_LINES:
            self.result.add_fail("Prog", f"SKILL.md has {line_count} lines (max {self.MAX_SKILL_LINES}). Move content to references/")
        elif line_count > self.TARGET_SKILL_LINES:
            self.result.add_warning("Prog", f"SKILL.md has {line_count} lines (target <{self.TARGET_SKILL_LINES}). Consider moving content to references/")
            self.result.add_pass("Prog")
        else:
            self.result.add_pass("Prog")

        # Check for inline examples (code blocks)
        code_blocks = re.findall(r'```[^`]*```', content, re.DOTALL)
        if len(code_blocks) == 0:
            self.result.add_warning("Prog", "No inline code examples. Anthropic recommends 1-2 copy-paste-ready examples.")
        elif len(code_blocks) > 5:
            self.result.add_warning("Prog", f"Many code blocks ({len(code_blocks)}). Consider moving some to examples/")

    def _validate_usage_section(self):
        """Check 4: Usage Section exists"""
        if not self.skill_md_path.exists():
            return

        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        usage_patterns = [r'##\s+Usage', r'##\s+Instructions', r'##\s+How to Use']
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in usage_patterns):
            self.result.add_pass("Usage")
        else:
            self.result.add_fail("Usage", "No Usage/Instructions/How to Use section found")

    def _validate_advanced_features(self, yaml_data: Dict):
        """
        Check 5: Advanced Features Justified
        - allowed-tools: for read-only/validation skills
        - disable-model-invocation: for side-effect operations
        - user-invocable: for background knowledge
        """
        allowed_tools = yaml_data.get('allowed-tools')
        disable_invocation = yaml_data.get('disable-model-invocation')
        user_invocable = yaml_data.get('user-invocable')

        # This is a basic check - manual review needed for proper justification
        if allowed_tools or disable_invocation or user_invocable is not None:
            # At least one advanced feature used
            self.result.add_pass("Adv")

            # Add informational warnings
            if allowed_tools:
                self.result.add_warning("Adv", "Uses allowed-tools - ensure justified for read-only/validation")
            if disable_invocation:
                self.result.add_warning("Adv", "Uses disable-model-invocation - ensure justified for side-effects")
            if user_invocable is False:
                self.result.add_warning("Adv", "Uses user-invocable:false - ensure justified for background knowledge")
        else:
            # No advanced features - that's fine
            self.result.add_pass("Adv")

    def _validate_examples_structure(self):
        """Check 6: Examples structure"""
        examples_dir = self.skill_path / "examples"
        if examples_dir.exists() and examples_dir.is_dir():
            example_files = list(examples_dir.glob("*.md"))
            if example_files:
                self.result.add_pass("Examples")
            else:
                self.result.add_fail("Examples", "examples/ exists but contains no .md files")
        else:
            # No examples/ is OK
            self.result.add_pass("Examples")

    def _validate_scripts_structure(self):
        """Check 7: Scripts structure"""
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists() and scripts_dir.is_dir():
            script_files = list(scripts_dir.glob("*"))
            script_files = [f for f in script_files if f.is_file() and not f.name.startswith('.')]
            if script_files:
                self.result.add_pass("Scripts")
            else:
                self.result.add_fail("Scripts", "scripts/ exists but contains no files")
        else:
            # No scripts/ is OK
            self.result.add_pass("Scripts")

    def _validate_templates_structure(self):
        """Check 8: Templates structure"""
        templates_dir = self.skill_path / "templates"
        if templates_dir.exists() and templates_dir.is_dir():
            template_files = list(templates_dir.glob("*"))
            template_files = [f for f in template_files if f.is_file()]
            if template_files:
                self.result.add_pass("Templates")
            else:
                self.result.add_fail("Templates", "templates/ exists but contains no files")
        else:
            # No templates/ is OK
            self.result.add_pass("Templates")

    def _validate_references_structure(self):
        """Check 9: References structure"""
        references_dir = self.skill_path / "references"
        if references_dir.exists() and references_dir.is_dir():
            ref_files = list(references_dir.glob("*.md"))
            if ref_files:
                self.result.add_pass("Refs")
                # Check for large files with ToC
                for ref_file in ref_files:
                    with open(ref_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    if len(lines) > 100:
                        # Check for ToC
                        content = ''.join(lines[:50])  # Check first 50 lines
                        if 'table of contents' not in content.lower():
                            self.result.add_warning("Refs", f"{ref_file.name} is {len(lines)} lines but missing ToC")
            else:
                self.result.add_fail("Refs", "references/ exists but contains no .md files")
        else:
            # No references/ is OK
            self.result.add_pass("Refs")

    def _validate_cross_references(self):
        """Check 10: Cross-references are valid"""
        if not self.skill_md_path.exists():
            return

        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        broken_links = []

        for link_text, link_path in links:
            # Skip external URLs
            if link_path.startswith('http://') or link_path.startswith('https://'):
                continue

            # Skip anchors
            if link_path.startswith('#'):
                continue

            # Resolve relative path
            full_path = self.skill_path / link_path
            if not full_path.exists():
                broken_links.append(f"{link_text} -> {link_path}")

        if broken_links:
            self.result.add_fail("Links", f"Broken links: {', '.join(broken_links)}")
        else:
            self.result.add_pass("Links")


def validate_skill(skill_path: Path, verbose: bool = False) -> ValidationResult:
    """Validate a single skill"""
    validator = SkillValidator(skill_path)
    result = validator.validate()

    if verbose:
        print(f"\n{'='*70}")
        print(f"Skill: {result.skill_name}")
        print(f"Score: {result.score}/{result.total_checks}")
        print(f"{'='*70}")

        if result.checks:
            print("\nChecks:")
            for check, passed in result.checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")

        if result.issues:
            print("\nIssues:")
            for issue in result.issues:
                print(f"  ❌ {issue}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")

    return result


def validate_all_skills(skills_dir: Path, verbose: bool = False) -> List[ValidationResult]:
    """Validate all skills in a directory"""
    results = []

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    skill_dirs.sort()

    print(f"Validating {len(skill_dirs)} skills...")

    for i, skill_dir in enumerate(skill_dirs, 1):
        if verbose:
            print(f"\n[{i}/{len(skill_dirs)}] Validating {skill_dir.name}...")
        else:
            # Progress indicator
            if i % 10 == 0:
                print(f"  {i}/{len(skill_dirs)}...", end='', flush=True)

        result = validate_skill(skill_dir, verbose=verbose)
        results.append(result)

    if not verbose:
        print()  # Newline after progress

    return results


def print_summary(results: List[ValidationResult]):
    """Print summary statistics"""
    total_skills = len(results)
    perfect_skills = len([r for r in results if r.score == r.total_checks])
    avg_score = sum(r.score for r in results) / total_skills if total_skills > 0 else 0

    print(f"\n{'='*70}")
    print("VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total Skills:        {total_skills}")
    print(f"Perfect (10/10):     {perfect_skills} ({perfect_skills/total_skills*100:.1f}%)")
    print(f"Average Score:       {avg_score:.1f}/10")
    print(f"{'='*70}\n")

    # Show failing skills
    failing_skills = [r for r in results if r.score < r.total_checks]
    if failing_skills:
        print(f"\nSkills needing attention ({len(failing_skills)}):\n")
        for result in sorted(failing_skills, key=lambda r: r.score):
            print(f"  [{result.score:2d}/10] {result.skill_name}")
            if result.issues:
                for issue in result.issues[:2]:  # Show first 2 issues
                    print(f"          - {issue}")
                if len(result.issues) > 2:
                    print(f"          ... and {len(result.issues)-2} more issues")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate skills against Anthropic best practices")
    parser.add_argument('skill_path', nargs='?', help='Path to skill directory')
    parser.add_argument('--all', action='store_true', help='Validate all skills in ~/.claude/skills/')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--skills-dir', default='~/.claude/skills', help='Skills directory to validate')

    args = parser.parse_args()

    if args.all:
        skills_dir = Path(args.skills_dir).expanduser()
        if not skills_dir.exists():
            print(f"Error: Skills directory not found: {skills_dir}")
            sys.exit(1)

        results = validate_all_skills(skills_dir, verbose=args.verbose)
        print_summary(results)

    elif args.skill_path:
        skill_path = Path(args.skill_path)
        if not skill_path.exists():
            print(f"Error: Skill not found: {skill_path}")
            sys.exit(1)

        result = validate_skill(skill_path, verbose=True)
        print(f"\nFinal Score: {result.score}/{result.total_checks}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
