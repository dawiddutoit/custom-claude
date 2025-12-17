#!/bin/bash
# Test script to validate the debug-test-failures skill is properly installed

set -e

SKILL_DIR="/Users/dawiddutoit/projects/play/project-watch-mcp/.claude/skills/debug-test-failures"

echo "=== Testing debug-test-failures Skill Installation ==="
echo ""

# Check if skill directory exists
if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ FAIL: Skill directory not found at $SKILL_DIR"
    exit 1
fi
echo "✅ Skill directory exists"

# Check if SKILL.md exists
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "❌ FAIL: SKILL.md not found"
    exit 1
fi
echo "✅ SKILL.md exists"

# Validate YAML frontmatter
echo ""
echo "=== Validating YAML Frontmatter ==="
if head -n 10 "$SKILL_DIR/SKILL.md" | grep -q "^name:"; then
    echo "✅ 'name' field found"
else
    echo "❌ FAIL: 'name' field missing"
    exit 1
fi

if head -n 10 "$SKILL_DIR/SKILL.md" | grep -q "^description:"; then
    echo "✅ 'description' field found"
else
    echo "❌ FAIL: 'description' field missing"
    exit 1
fi

if head -n 10 "$SKILL_DIR/SKILL.md" | grep -q "^allowed-tools:"; then
    echo "✅ 'allowed-tools' field found"
else
    echo "⚠️  WARNING: 'allowed-tools' field not specified (skill will ask for permission)"
fi

# Check YAML syntax (basic check for tabs)
if head -n 10 "$SKILL_DIR/SKILL.md" | grep -q $'\t'; then
    echo "❌ FAIL: YAML frontmatter contains tabs (must use spaces)"
    exit 1
fi
echo "✅ No tabs in YAML frontmatter"

# Check for supporting files
echo ""
echo "=== Checking Supporting Files ==="
if [ -f "$SKILL_DIR/examples.md" ]; then
    echo "✅ examples.md exists"
else
    echo "⚠️  WARNING: examples.md not found (recommended)"
fi

if [ -f "$SKILL_DIR/reference.md" ]; then
    echo "✅ reference.md exists"
else
    echo "⚠️  WARNING: reference.md not found (recommended)"
fi

# Check description quality
echo ""
echo "=== Checking Description Quality ==="
DESCRIPTION=$(grep "^description:" "$SKILL_DIR/SKILL.md" | cut -d: -f2-)

if echo "$DESCRIPTION" | grep -qi "test"; then
    echo "✅ Description mentions 'test' (good for discovery)"
else
    echo "⚠️  WARNING: Description doesn't mention 'test'"
fi

if echo "$DESCRIPTION" | grep -qi "fail\|error\|debug"; then
    echo "✅ Description mentions failure/error/debug (good for discovery)"
else
    echo "⚠️  WARNING: Description doesn't mention failure/error/debug"
fi

if echo "$DESCRIPTION" | grep -qi "pytest\|jest\|vitest"; then
    echo "✅ Description mentions test frameworks (good for discovery)"
else
    echo "⚠️  WARNING: Description doesn't mention test frameworks"
fi

# Check if skill follows best practices
echo ""
echo "=== Checking Best Practices ==="

if grep -q "## Quick Start" "$SKILL_DIR/SKILL.md"; then
    echo "✅ Has 'Quick Start' section"
else
    echo "⚠️  WARNING: Missing 'Quick Start' section"
fi

if grep -q "## Examples" "$SKILL_DIR/SKILL.md"; then
    echo "✅ Has 'Examples' section"
else
    echo "⚠️  WARNING: Missing 'Examples' section"
fi

# Test if skill can be read by Claude
echo ""
echo "=== Testing Readability ==="
WORD_COUNT=$(wc -w < "$SKILL_DIR/SKILL.md")
echo "   SKILL.md word count: $WORD_COUNT"

if [ "$WORD_COUNT" -lt 100 ]; then
    echo "⚠️  WARNING: SKILL.md is very short (< 100 words)"
elif [ "$WORD_COUNT" -gt 5000 ]; then
    echo "⚠️  WARNING: SKILL.md is very long (> 5000 words) - consider moving content to reference.md"
else
    echo "✅ SKILL.md length is reasonable"
fi

# Test for common anti-patterns
echo ""
echo "=== Checking for Anti-Patterns ==="

if grep -qi "example\|demo\|sample" "$SKILL_DIR/SKILL.md" | grep -qi "file\|code"; then
    echo "⚠️  WARNING: Skill mentions 'example files' - avoid creating temp files"
else
    echo "✅ No mention of creating example files"
fi

if grep -q "emoji" "$SKILL_DIR/SKILL.md"; then
    echo "⚠️  INFO: Skill mentions emojis (use sparingly)"
fi

# Final summary
echo ""
echo "=== Skill Validation Summary ==="
echo "✅ All critical checks passed!"
echo ""
echo "To use this skill, Claude will automatically discover it when you mention:"
grep "^description:" "$SKILL_DIR/SKILL.md" | cut -d: -f2- | sed 's/^/  - /'
echo ""
echo "Skill location: $SKILL_DIR"
echo "Skill type: Project (shared with team)"
echo ""
echo "Next steps:"
echo "1. Commit skill to git: git add .claude/skills/debug-test-failures"
echo "2. Test discovery: Ask Claude 'can you help debug my failing tests?'"
echo "3. Validate behavior: Ensure Claude follows the systematic approach"
