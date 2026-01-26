#!/bin/bash
#
# Add "When to Use This Skill" sections to skills
# Usage: ./add_when_to_use_sections.sh

set -e

SKILLS_DIR="/Users/dawiddutoit/projects/claude/custom-claude/skills"

# Function to add section after Purpose
add_when_to_use() {
    local skill_path="$1"
    local use_case="$2"
    local do_not_use="$3"

    # Check if section already exists
    if grep -q "## When to Use This Skill" "$skill_path"; then
        echo "  ✓ Already has 'When to Use This Skill' section"
        return 0
    fi

    # Create temp file with new section
    awk -v use="$use_case" -v dont="$do_not_use" '
    /^## Purpose/ {
        in_purpose=1
    }
    in_purpose && /^## / && !/^## Purpose/ {
        # Found next section after Purpose
        print ""
        print "## When to Use This Skill"
        print ""
        print use
        print ""
        print dont
        in_purpose=0
    }
    { print }
    ' "$skill_path" > "$skill_path.tmp"

    mv "$skill_path.tmp" "$skill_path"
    echo "  ✓ Added 'When to Use This Skill' section"
}

echo "Adding 'When to Use This Skill' sections..."
echo

# Kafka skills
echo "kafka-integration-testing..."
add_when_to_use \
    "$SKILLS_DIR/kafka-integration-testing/SKILL.md" \
    "Use when testing Kafka producer/consumer workflows end-to-end with \"test Kafka integration\", \"verify message ordering\", \"test Kafka roundtrip\", or \"validate exactly-once semantics\"." \
    "Do NOT use for unit testing with mocked Kafka (use \`pytest-adapter-integration-testing\`), implementing producers/consumers (use respective \`kafka-*-implementation\` skills), or schema validation (use \`kafka-schema-management\`)."

echo "kafka-producer-implementation..."
add_when_to_use \
    "$SKILLS_DIR/kafka-producer-implementation/SKILL.md" \
    "Use when building event publishers that send domain events to Kafka topics with \"implement Kafka producer\", \"publish events to Kafka\", \"send order events\", or \"create event publisher\"." \
    "Do NOT use for consuming events (use \`kafka-consumer-implementation\`), testing with testcontainers (use \`kafka-integration-testing\`), or designing schemas (use \`kafka-schema-management\`)."

echo "kafka-schema-management..."
add_when_to_use \
    "$SKILLS_DIR/kafka-schema-management/SKILL.md" \
    "Use when defining message formats for Kafka with \"design Kafka schema\", \"create message schema\", \"manage schema versions\", or \"handle schema evolution\"." \
    "Do NOT use for implementing producers/consumers (use \`kafka-*-implementation\` skills) or testing (use \`kafka-integration-testing\`)."

# Playwright skills (already have "When to Use" sections in most - skip for now)

# Pytest skills
echo "pytest-adapter-integration-testing..."
add_when_to_use \
    "$SKILLS_DIR/pytest-adapter-integration-testing/SKILL.md" \
    "Use when testing adapters and gateways with \"test Shopify gateway\", \"mock HTTP responses\", \"test Kafka adapter\", or \"decide between mocks and containers\"." \
    "Do NOT use for domain testing (use \`pytest-domain-model-testing\`), application layer (use \`pytest-application-layer-testing\`), or general mocking patterns (use \`pytest-mocking-strategy\`)."

echo "pytest-application-layer-testing..."
add_when_to_use \
    "$SKILLS_DIR/pytest-application-layer-testing/SKILL.md" \
    "Use when testing use cases and application services with \"test use case\", \"mock gateways\", \"test orchestration\", or \"test DTOs\"." \
    "Do NOT use for domain testing (use \`pytest-domain-model-testing\`), adapter testing (use \`pytest-adapter-integration-testing\`), or pytest configuration (use \`pytest-configuration\`)."

echo "pytest-configuration..."
add_when_to_use \
    "$SKILLS_DIR/pytest-configuration/SKILL.md" \
    "Use when setting up pytest in a project with \"configure pytest\", \"setup test discovery\", \"create conftest\", or \"configure coverage\"." \
    "Do NOT use for writing tests themselves (use layer-specific testing skills), debugging failures (use \`test-debug-failures\`), or mocking strategies (use \`pytest-mocking-strategy\`)."

echo "pytest-coverage-measurement..."
add_when_to_use \
    "$SKILLS_DIR/pytest-coverage-measurement/SKILL.md" \
    "Use when measuring test coverage with \"measure coverage\", \"track coverage\", \"identify untested code\", or \"set coverage thresholds\"." \
    "Do NOT use for writing tests (use layer-specific testing skills), pytest configuration (use \`pytest-configuration\`), or fixing low coverage (identify gaps first, then use appropriate testing skill)."

echo "pytest-domain-model-testing..."
add_when_to_use \
    "$SKILLS_DIR/pytest-domain-model-testing/SKILL.md" \
    "Use when testing domain models with \"test value objects\", \"test entities\", \"test domain logic\", or \"achieve 95% domain coverage\"." \
    "Do NOT use for application layer (use \`pytest-application-layer-testing\`), adapters (use \`pytest-adapter-integration-testing\`), or mocking (domain tests should use real objects)."

echo "pytest-mocking-strategy..."
add_when_to_use \
    "$SKILLS_DIR/pytest-mocking-strategy/SKILL.md" \
    "Use when deciding what to mock in tests with \"create mock\", \"mock external service\", \"AsyncMock pattern\", or \"what should I mock\"." \
    "Do NOT use for domain testing (never mock domain objects), pytest configuration (use \`pytest-configuration\`), or test factories (use \`pytest-test-data-factories\`)."

# Python best practices
echo "python-best-practices-async-context-manager..."
add_when_to_use \
    "$SKILLS_DIR/python-best-practices-async-context-manager/SKILL.md" \
    "Use when managing async resources with \"create context manager\", \"manage database session\", \"async with pattern\", or \"resource cleanup\"." \
    "Do NOT use for synchronous resources (use regular context managers), simple try/finally (overkill), or testing (use pytest fixtures)."

echo "python-best-practices-fail-fast-imports..."
add_when_to_use \
    "$SKILLS_DIR/python-best-practices-fail-fast-imports/SKILL.md" \
    "Use when validating imports with \"check imports\", \"validate fail-fast\", \"detect optional imports\", or as part of pre-commit hooks." \
    "Do NOT use for fixing individual import errors (use manually), type errors (use \`python-best-practices-type-safety\`), or general code quality (use \`quality-run-quality-gates\`)."

echo "python-best-practices-type-safety..."
add_when_to_use \
    "$SKILLS_DIR/python-best-practices-type-safety/SKILL.md" \
    "Use when fixing type errors with \"fix pyright errors\", \"resolve type mismatch\", \"add type annotations\", or \"handle Optional types\"." \
    "Do NOT use for pytest configuration (use \`pytest-configuration\`), import validation (use \`python-best-practices-fail-fast-imports\`), or runtime errors (type checking is static)."

echo
echo "✅ Done! Added 'When to Use This Skill' sections to all applicable skills."
