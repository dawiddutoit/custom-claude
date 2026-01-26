# Group 5 Skills Validation Report

**Validation Date:** 2026-01-22
**Skills Validated:** 41

## Summary

- **Average Score:** 7.6/10
- **Perfect Scores (10/10):** 4
- **Needs Improvement (<7/10):** 9

## Validation Results

### util-resolve-serviceresult-errors

**Score:** 4.0/10

**Issues Found:**
- ❌ SKILL.md too long: 600 lines (target ≤500)
- ❌ Broken cross-reference: [scripts/README.md](./scripts/README.md)
- ❌ Broken cross-reference: [find_serviceresult_chains.py](./scripts/find_serviceresult_chains.py)
- ❌ Broken cross-reference: [fix_serviceresult_mocks.py](./scripts/fix_serviceresult_mocks.py)
- ❌ Broken cross-reference: [validate_serviceresult_usage.py](./scripts/validate_serviceresult_usage.py)
- ❌ Broken cross-reference: [scripts/README.md](./scripts/README.md)
- ❌ Broken cross-reference: [scripts/EXAMPLES.md](./scripts/EXAMPLES.md)
- ❌ Broken cross-reference: [scripts/SCRIPT_SUMMARY.md](./scripts/SCRIPT_SUMMARY.md)
- ❌ Broken cross-reference: [templates/serviceresult-patterns.md](./templates/serviceresult-patterns.md)
- ❌ Broken cross-reference: [references/monad-pattern.md](./references/monad-pattern.md)
- ❌ Broken cross-reference: [scripts/examples.md](./scripts/examples.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Move 100 lines to references/ or examples/
- 💡 Document scripts/ utilities in SKILL.md

---

### validating-clickhouse-kafka-pipelines

**Score:** 4.0/10

**Issues Found:**
- ❌ Name mismatch: 'clickhouse-kafka-validation' != 'validating-clickhouse-kafka-pipelines'
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ references/ directory exists but is empty
- ❌ Broken cross-reference: [references/clickhouse-schema.sql](./references/clickhouse-schema.sql)
- ❌ Broken cross-reference: [references/producer-patterns.py](./references/producer-patterns.py)
- ❌ Broken cross-reference: [references/consumer-patterns.py](./references/consumer-patterns.py)
- ❌ Broken cross-reference: [references/monitoring-queries.sql](./references/monitoring-queries.sql)
- ❌ Broken cross-reference: [examples/examples.md](./examples/examples.md)
- ❌ Broken cross-reference: [Full ADR](../../artifacts/2025-11-09/analysis/adr-clickhouse-kafka-validation-patterns.md)
- ❌ Broken cross-reference: [Quick Reference](../../artifacts/2025-11-09/analysis/quickref-validation-patterns.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### test-setup-async

**Score:** 5.0/10

**Issues Found:**
- ❌ SKILL.md too long: 536 lines (target ≤500)
- ❌ Broken cross-reference: [references/SCRIPTS-REFERENCE.md](./references/SCRIPTS-REFERENCE.md)
- ❌ Broken cross-reference: [convert_to_async.py](./scripts/convert_to_async.py)
- ❌ Broken cross-reference: [generate_async_fixture.py](./scripts/generate_async_fixture.py)
- ❌ Broken cross-reference: [validate_async_tests.py](./scripts/validate_async_tests.py)
- ❌ Broken cross-reference: [templates/async-test-template.py](./templates/async-test-template.py)
- ❌ Broken cross-reference: [references/SCRIPTS-REFERENCE.md](./references/SCRIPTS-REFERENCE.md)
- ❌ Broken cross-reference: [references/QUICK-REFERENCE.md](./references/QUICK-REFERENCE.md)
- ❌ Broken cross-reference: [references/IMPLEMENTATION-SUMMARY.md](./references/IMPLEMENTATION-SUMMARY.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Move 36 lines to references/ or examples/
- 💡 Document scripts/ utilities in SKILL.md

---

### uv-ci-cd-integration

**Score:** 5.0/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ examples/ directory exists but is empty
- ❌ Broken cross-reference: [examples/github-actions-complete.yml](./examples/github-actions-complete.yml)
- ❌ Broken cross-reference: [examples/dockerfile-development](./examples/dockerfile-development)
- ❌ Broken cross-reference: [examples/gitlab-ci-complete.yml](./examples/gitlab-ci-complete.yml)
- ❌ Broken cross-reference: [examples/pypi-publishing-workflow.yml](./examples/pypi-publishing-workflow.yml)
- ❌ Broken cross-reference: [references/cache-optimization.md](./references/cache-optimization.md)
- ❌ Broken cross-reference: [references/docker-patterns.md](./references/docker-patterns.md)
- ❌ Broken cross-reference: [references/troubleshooting.md](./references/troubleshooting.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### test-implement-constructor-validation

**Score:** 5.5/10

**Issues Found:**
- ❌ Broken cross-reference: [templates/test-template.py](./templates/test-template.py)
- ❌ Broken cross-reference: [references/reference.md](./references/reference.md)
- ❌ Broken cross-reference: [Find Missing Validation Tests](./scripts/find_missing_validation.py)
- ❌ Broken cross-reference: [Generate Constructor Tests](./scripts/generate_constructor_tests.py)
- ❌ Broken cross-reference: [Validate Test Coverage](./scripts/validate_constructor_tests.py)
- ❌ Broken cross-reference: [references/reference.md](./references/reference.md)
- ❌ Broken cross-reference: [templates/test-template.py](./templates/test-template.py)
- ❌ Broken cross-reference: [references/reference.md](./references/reference.md)
- ❌ Broken cross-reference: [CLAUDE.md](../../../../CLAUDE.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### test-organize-layers

**Score:** 5.5/10

**Issues Found:**
- ❌ Broken cross-reference: [references/reference.md](./references/reference.md)
- ❌ Broken cross-reference: [Analyze Test Pyramid](./scripts/analyze_test_pyramid.py)
- ❌ Broken cross-reference: [Move Test](./scripts/move_test.py)
- ❌ Broken cross-reference: [Validate Test Placement](./scripts/validate_test_placement.py)
- ❌ Broken cross-reference: [Organize Tests](./scripts/organize_tests.py)
- ❌ Broken cross-reference: [tests/unit/conftest.py](../../../tests/unit/conftest.py)
- ❌ Broken cross-reference: [tests/integration/conftest.py](../../../tests/integration/conftest.py)
- ❌ Broken cross-reference: [tests/e2e/conftest.py](../../../tests/e2e/conftest.py)
- ❌ Broken cross-reference: [references/reference.md](./references/reference.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### test-implement-factory-fixtures

**Score:** 6.5/10

**Issues Found:**
- ❌ SKILL.md too long: 558 lines (target ≤500)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [Convert Fixture to Factory](./scripts/convert_fixture_to_factory.py)
- ❌ Broken cross-reference: [Generate Factory Fixture](./scripts/generate_factory_fixture.py)
- ❌ Broken cross-reference: [Validate Fixtures](./scripts/validate_fixtures.py)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Move 58 lines to references/ or examples/
- 💡 Document scripts/ utilities in SKILL.md

---

### uv-project-migration

**Score:** 6.5/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [uv-project-setup](../uv-project-setup/SKILL.md)
- ❌ Broken cross-reference: [uv-dependency-management](../uv-dependency-management/SKILL.md)
- ❌ Broken cross-reference: [uv-ci-cd-integration](../uv-ci-cd-integration/SKILL.md)
- ❌ Broken cross-reference: [uv-troubleshooting](../uv-troubleshooting/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### uv-troubleshooting

**Score:** 6.5/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [uv-dependency-management](../uv-dependency-management/SKILL.md)
- ❌ Broken cross-reference: [uv-python-version-management](../uv-python-version-management/SKILL.md)
- ❌ Broken cross-reference: [uv-project-migration](../uv-project-migration/SKILL.md)
- ❌ Broken cross-reference: [uv-ci-cd-integration](../uv-ci-cd-integration/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### textual-layout-styling

**Score:** 7.0/10

**Issues Found:**
- ❌ SKILL.md too long: 582 lines (target ≤500)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-widget-development.md](../textual-widget-development)
- ❌ Broken cross-reference: [textual-app-lifecycle.md](../textual-app-lifecycle)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Move 82 lines to references/ or examples/

---

### textual-test-patterns

**Score:** 7.0/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-testing](../textual-testing)
- ❌ Broken cross-reference: [textual-test-fixtures](../textual-test-fixtures)
- ❌ Broken cross-reference: [textual-snapshot-testing](../textual-snapshot-testing)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### util-research-library

**Score:** 7.0/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ SKILL.md too long: 589 lines (target ≤500)
- ❌ Broken cross-reference: [references/date-aware-search.md](./references/date-aware-search.md)
- ❌ Broken cross-reference: [references/research-checklist.md](./references/research-checklist.md)
- ❌ Broken cross-reference: [templates/decision-matrix-template.md](./templates/decision-matrix-template.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Move 89 lines to references/ or examples/

---

### uv-dependency-management

**Score:** 7.0/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [uv-project-setup](../uv-project-setup/SKILL.md)
- ❌ Broken cross-reference: [uv-python-version-management](../uv-python-version-management/SKILL.md)
- ❌ Broken cross-reference: [uv-troubleshooting](../uv-troubleshooting/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### uv-project-setup

**Score:** 7.0/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [uv-dependency-management](../uv-dependency-management/SKILL.md)
- ❌ Broken cross-reference: [uv-python-version-management](../uv-python-version-management/SKILL.md)
- ❌ Broken cross-reference: [uv-ci-cd-integration](../uv-ci-cd-integration/SKILL.md)
- ❌ Broken cross-reference: [uv-tool-management](../uv-tool-management/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Document why allowed-tools is restricted

---

### uv-python-version-management

**Score:** 7.0/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [uv-project-setup](../uv-project-setup/SKILL.md)
- ❌ Broken cross-reference: [uv-ci-cd-integration](../uv-ci-cd-integration/SKILL.md)
- ❌ Broken cross-reference: [uv-troubleshooting](../uv-troubleshooting/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### uv-tool-management

**Score:** 7.0/10

**Issues Found:**
- ❌ Missing trigger phrases (WHEN component)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [references/tool-comparison.md](./references/tool-comparison.md)
- ❌ Broken cross-reference: [references/common-workflows.md](./references/common-workflows.md)
- ❌ Broken cross-reference: [examples/tool-scenarios.md](./examples/tool-scenarios.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### test-debug-failures

**Score:** 7.5/10

**Issues Found:**
- ❌ SKILL.md too long: 556 lines (target ≤500)
- ❌ Broken cross-reference: [examples.md](./references/examples.md)
- ❌ Broken cross-reference: [Test Skill Script](./scripts/test_skill.sh)
- ❌ Broken cross-reference: [../run-quality-gates/references/shared-quality-gates.md](../run-quality-gates/references/shared-quality-gates.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Move 56 lines to references/ or examples/
- 💡 Document scripts/ utilities in SKILL.md
- 💡 Cross-reference reference.md in SKILL.md

---

### textual-app-lifecycle

**Score:** 7.5/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-event-messages.md](../textual-event-messages)
- ❌ Broken cross-reference: [textual-widget-development.md](../textual-widget-development)
- ❌ Broken cross-reference: [textual-reactive-programming.md](../textual-reactive-programming)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### textual-data-display

**Score:** 7.5/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-widget-development.md](../textual-widget-development)
- ❌ Broken cross-reference: [textual-event-messages.md](../textual-event-messages)
- ❌ Broken cross-reference: [textual-layout-styling.md](../textual-layout-styling)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Consider moving content to references/ (482 lines, approaching limit)

---

### textual-test-fixtures

**Score:** 7.5/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-testing](../textual-testing)
- ❌ Broken cross-reference: [textual-snapshot-testing](../textual-snapshot-testing)
- ❌ Broken cross-reference: [textual-test-patterns](../textual-test-patterns)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### textual-testing

**Score:** 7.5/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-snapshot-testing](../textual-snapshot-testing)
- ❌ Broken cross-reference: [textual-test-fixtures](../textual-test-fixtures)
- ❌ Broken cross-reference: [textual-test-patterns](../textual-test-patterns)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### textual-widget-development

**Score:** 7.5/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-app-lifecycle.md](../textual-app-lifecycle)
- ❌ Broken cross-reference: [textual-event-messages.md](../textual-event-messages)
- ❌ Broken cross-reference: [textual-layout-styling.md](../textual-layout-styling)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Consider moving content to references/ (469 lines, approaching limit)

---

### textual-snapshot-testing

**Score:** 8.0/10

**Issues Found:**
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ Broken cross-reference: [textual-testing](../textual-testing)
- ❌ Broken cross-reference: [textual-test-fixtures](../textual-test-fixtures)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### web-artifacts-builder

**Score:** 8.0/10

**Issues Found:**
- ❌ Missing trigger phrases (WHEN component)
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Document scripts/ utilities in SKILL.md

---

### webapp-testing

**Score:** 8.0/10

**Issues Found:**
- ❌ Missing trigger phrases (WHEN component)
- ❌ Missing 'When to Use' or 'Usage' section
- ❌ examples/ directory exists but is empty

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Document scripts/ utilities in SKILL.md

---

### xlsx

**Score:** 8.0/10

**Issues Found:**
- ❌ Missing trigger phrases (WHEN component)
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### terraform-gcp-integration

**Score:** 8.5/10

**Issues Found:**
- ❌ Broken cross-reference: [terraform skill](../terraform/SKILL.md)
- ❌ Broken cross-reference: [terraform-state-management](../terraform-state-management/SKILL.md)
- ❌ Broken cross-reference: [terraform-troubleshooting](../terraform-troubleshooting/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Consider moving content to references/ (456 lines, approaching limit)

---

### terraform-module-design

**Score:** 8.5/10

**Issues Found:**
- ❌ Broken cross-reference: [terraform skill](../terraform/SKILL.md)
- ❌ Broken cross-reference: [terraform-gcp-integration](../terraform-gcp-integration/SKILL.md)
- ❌ Broken cross-reference: [terraform-state-management](../terraform-state-management/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Consider moving content to references/ (500 lines, approaching limit)

---

### terraform-secrets-management

**Score:** 8.5/10

**Issues Found:**
- ❌ Broken cross-reference: [terraform skill](../terraform/SKILL.md)
- ❌ Broken cross-reference: [terraform-gcp-integration](../terraform-gcp-integration/SKILL.md)
- ❌ Broken cross-reference: [terraform-troubleshooting](../terraform-troubleshooting/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Consider moving content to references/ (498 lines, approaching limit)

---

### terraform-state-management

**Score:** 8.5/10

**Issues Found:**
- ❌ Broken cross-reference: [terraform skill](../terraform/SKILL.md)
- ❌ Broken cross-reference: [terraform-troubleshooting](../terraform-troubleshooting/SKILL.md)
- ❌ Broken cross-reference: [terraform-gcp-integration](../terraform-gcp-integration/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### terraform-troubleshooting

**Score:** 8.5/10

**Issues Found:**
- ❌ Broken cross-reference: [terraform skill](../terraform/SKILL.md)
- ❌ Broken cross-reference: [terraform-state-management](../terraform-state-management/SKILL.md)
- ❌ Broken cross-reference: [terraform-gcp-integration](../terraform-gcp-integration/SKILL.md)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### work-with-adf

**Score:** 8.5/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)
- ❌ Missing 'When to Use' or 'Usage' section

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Document scripts/ utilities in SKILL.md

---

### test-property-based

**Score:** 9/10

**Issues Found:**
- ❌ SKILL.md too long: 651 lines (target ≤500)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Move 151 lines to references/ or examples/

---

### textual-event-messages

**Score:** 9.0/10

**Issues Found:**
- ❌ Broken cross-reference: [textual-app-lifecycle.md](../textual-app-lifecycle)
- ❌ Broken cross-reference: [textual-widget-development.md](../textual-widget-development)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Consider moving content to references/ (432 lines, approaching limit)

---

### textual-reactive-programming

**Score:** 9.0/10

**Issues Found:**
- ❌ Broken cross-reference: [textual-widget-development.md](../textual-widget-development)
- ❌ Broken cross-reference: [textual-event-messages.md](../textual-event-messages)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Consider moving content to references/ (475 lines, approaching limit)

---

### theme-factory

**Score:** 9.0/10

**Issues Found:**
- ❌ Missing trigger phrases (WHEN component)
- ❌ Missing context (CONTEXT component - file types/technologies)

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### util-multi-file-refactor

**Score:** 9.5/10

**Issues Found:**
- ❌ Missing context (CONTEXT component - file types/technologies)

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Document why allowed-tools is restricted
- 💡 Cross-reference quality-gates.md in SKILL.md
- 💡 Cross-reference troubleshooting.md in SKILL.md
- 💡 Cross-reference refactoring-patterns.md in SKILL.md
- 💡 Cross-reference language-guides.md in SKILL.md

---

### terraform-basics

**Score:** 10/10

**Issues Found:** None ✅

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### test-first-thinking

**Score:** 10/10

**Issues Found:** None ✅

**Recommendations:**
- 💡 Add 'version' field to frontmatter

---

### util-manage-todo

**Score:** 10/10

**Issues Found:** None ✅

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Document why allowed-tools is restricted
- 💡 Document scripts/ utilities in SKILL.md

---

### write-atomic-tasks

**Score:** 10/10

**Issues Found:** None ✅

**Recommendations:**
- 💡 Add 'version' field to frontmatter
- 💡 Document scripts/ utilities in SKILL.md

---
