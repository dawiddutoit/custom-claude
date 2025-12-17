---
name: quality-code-review
description: Perform systematic self-review of code changes before commits using structured
  checklist. Validates architecture boundaries, code quality, test coverage, documentation,
  and project-specific anti-patterns. Use before committing, creating PRs, or when
  user says "review my changes", "self-review", "check my code". Adapts to Python,
  JavaScript, TypeScript, Go, Rust projects.
allowed-tools:
- Read
- Bash
- Grep
- Glob
- Skill
tags:
- code-review
- pre-commit
- quality
- validation
- checklist
- --
---

# Self Code Review

## Table of Contents

### Core Sections
- [When to Use This Skill](#when-to-use-this-skill) - Mandatory situations and user trigger phrases
- [What This Skill Does](#what-this-skill-does) - 8-step comprehensive review process
- [Quick Start](#quick-start) - Immediate examples and usage patterns
  - [Example 1: Pre-Commit Review](#example-1-pre-commit-review) - Review with issues found
  - [Example 2: All Checks Pass](#example-2-all-checks-pass) - Ready to commit scenario
- [Review Process](#review-process) - Complete 8-step review workflow
  - [Step 1: Change Discovery](#step-1-change-discovery) - Detect and categorize modified files
  - [Step 2: Architectural Review](#step-2-architectural-review) - Layer boundaries, SRP, pattern compliance
  - [Step 3: Code Quality Review](#step-3-code-quality-review) - Style, logic, performance, security
  - [Step 4: Test Coverage Review](#step-4-test-coverage-review) - Test presence, quality, and coverage
  - [Step 5: Documentation Review](#step-5-documentation-review) - API docs, comments, high-level docs
  - [Step 6: Anti-Pattern Detection](#step-6-anti-pattern-detection) - Universal and project-specific violations
  - [Step 7: Quality Gates](#step-7-quality-gates) - Automated quality tool execution
  - [Step 8: Review Report Generation](#step-8-review-report-generation) - Actionable report with pass/fail status

### Integration & Adaptation
- [Integration with Other Skills](#integration-with-other-skills) - validate-layer-boundaries, run-quality-gates, detect-refactor-markers
- [Language-Specific Adaptations](#language-specific-adaptations) - Python, JavaScript/TypeScript, Go, Rust
- [Configuration](#configuration) - Custom checklists and quality gate configuration

### Output & Examples
- [Output Examples](#output-examples) - Success and failure report examples
  - [Success Example (All Pass)](#success-example-all-pass) - Clean commit ready
  - [Failure Example (Issues Found)](#failure-example-issues-found) - Detailed issue breakdown with fixes

### Best Practices & Guidance
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid) - Common review mistakes
- [Best Practices](#best-practices) - Workflow recommendations
- [Troubleshooting](#troubleshooting) - Common issues and solutions

### Supporting Resources
- [Supporting Files](#supporting-files) - References, anti-pattern catalog, language guides, scripts
- [Success Metrics](#success-metrics) - Target metrics and benefits
- [Examples](#examples) - Comprehensive example gallery
- [Requirements](#requirements) - Dependencies and optional components

## Purpose

Performs systematic self-review of code changes before commits to catch issues early and maintain high code quality. This skill executes an 8-step comprehensive review process covering architecture boundaries, code quality, test coverage, documentation, and project-specific anti-patterns. Adapts to Python, JavaScript, TypeScript, Go, and Rust projects. Essential for preventing bugs from reaching production and reducing PR review cycles.

## When to Use This Skill

**MANDATORY in these situations:**
- Before creating a commit
- Before opening a pull request
- Before marking feature as complete
- After implementing new functionality
- After refactoring code

**User trigger phrases:**
- "review my changes"
- "self-review"
- "check my code"
- "pre-commit check"
- "ready to commit?"
- "code quality check"
- "can I commit this?"

## What This Skill Does

Performs comprehensive code review covering:

1. **Change Discovery** - Identifies all modified files (staged and unstaged)
2. **Architectural Review** - Validates layer boundaries and design patterns
3. **Code Quality Review** - Checks style, logic, performance, security
4. **Test Coverage Review** - Ensures adequate testing
5. **Documentation Review** - Validates documentation completeness
6. **Anti-Pattern Detection** - Scans for project-specific violations
7. **Quality Gates** - Runs linting, type checking, tests
8. **Review Report** - Generates actionable report with pass/fail/warnings

**Result:** ✅ Ready to commit (all checks pass) or ❌ Not ready (issues found with fixes)

## Quick Start

### Example 1: Pre-Commit Review

```
User: "Review my changes before I commit"

Claude invokes skill:
→ Detects 5 modified files
→ Validates architecture boundaries
→ Checks code quality
→ Runs quality gates
→ Generates review report

Output:
✅ Architecture: Clean Architecture respected
✅ Code Quality: No style/logic issues
✅ Tests: All tests pass, coverage adequate
⚠️ Documentation: Missing docstring in new method
❌ Anti-Pattern: Optional config parameter found

❌ NOT READY TO COMMIT
Fix 1 critical issue and 1 warning before committing.
```

## Instructions

### Overview

Comprehensive code review follows an 8-step systematic process:

1. **Change Discovery** - Identify all modified files (staged and unstaged)
2. **Architectural Review** - Validate layer boundaries and design patterns
3. **Code Quality Review** - Check style, logic, performance, security
4. **Test Coverage Review** - Ensure adequate testing
5. **Documentation Review** - Validate documentation completeness
6. **Anti-Pattern Detection** - Scan for project-specific violations
7. **Quality Gates** - Run linting, type checking, tests
8. **Review Report** - Generate actionable report with pass/fail/warnings

See detailed steps in [Review Process](#review-process) section below.

### Example 2: All Checks Pass

```
User: "Am I ready to commit?"

Claude invokes skill:
→ Reviews changes
→ All checks pass

Output:
✅ All review checks passed (8/8)
✅ READY TO COMMIT

Summary:
- 3 files modified
- Architecture boundaries respected
- All quality gates pass
- Test coverage adequate
- Documentation complete
- No anti-patterns detected

You can safely commit these changes.
```

## Review Process

### Step 1: Change Discovery

**Detect changes:**
```bash
# Unstaged changes
git diff --name-only

# Staged changes
git diff --staged --name-only

# Combined view
git diff HEAD --name-only
```

**For each modified file:**
- Read file to understand changes
- Identify file type (Python, JS, TS, etc.)
- Determine which layer/module it belongs to
- Note scope of changes (lines added/removed)

### Step 2: Architectural Review

**Layer Boundary Validation** (if Clean Architecture):
- Invoke `validate-layer-boundaries` skill if available
- Check dependency directions (Domain ← Application ← Infrastructure ← Interface)
- Validate domain purity (no external dependencies)
- Ensure proper abstraction usage

**Single Responsibility Check:**
- Review method/class names for "and" (indicates multiple responsibilities)
- Check if methods do more than one thing
- Validate separation of concerns
- Ensure proper decomposition

**Pattern Compliance:**
- ServiceResult pattern used for error handling
- Repository interfaces implemented correctly
- Dependency injection properly used
- Configuration properly injected (not defaulted)

### Step 3: Code Quality Review

#### Style & Clarity Checklist

**Naming:**
- [ ] Variables descriptive (no `temp`, `data`, `x`)
- [ ] Functions describe behavior (verbs)
- [ ] Classes describe entities (nouns)
- [ ] Constants in UPPER_CASE
- [ ] Boolean variables start with `is_`, `has_`, `can_`

**Magic Numbers:**
- [ ] No hardcoded values (use constants or config)
- [ ] Configuration values in settings
- [ ] Clear reasoning if number appears essential

**Code Cleanliness:**
- [ ] No commented-out code
- [ ] No TODOs without issue references
- [ ] No dead/unused code
- [ ] Consistent formatting

#### Logic & Correctness Checklist

**Error Handling:**
- [ ] Fail fast (no silent failures)
- [ ] No bare `try/except` or `catch` blocks
- [ ] Specific exception types caught
- [ ] Error messages descriptive
- [ ] ServiceResult pattern used (Python projects)

**Null/None Safety:**
- [ ] No unchecked nullable values
- [ ] Optional types properly handled
- [ ] Guard clauses for None checks
- [ ] Type annotations accurate

**Edge Cases:**
- [ ] Empty collections handled
- [ ] Zero/negative values handled
- [ ] Boundary conditions tested
- [ ] Division by zero prevented

#### Performance Checklist

**Efficiency:**
- [ ] No N+1 query patterns
- [ ] Efficient algorithms (no unnecessary O(n²))
- [ ] Proper use of data structures
- [ ] No repeated expensive operations

**Resource Management:**
- [ ] Files/connections closed properly
- [ ] Context managers used (Python `with`, JS `try/finally`)
- [ ] Memory leaks prevented
- [ ] Database connections pooled

#### Security Checklist

**Sensitive Data:**
- [ ] No hardcoded secrets
- [ ] No credentials in code
- [ ] Sensitive data encrypted
- [ ] .env files in .gitignore

**Input Validation:**
- [ ] User input validated
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (escaped output)
- [ ] Path traversal prevented

**Authentication/Authorization:**
- [ ] Auth checks present where needed
- [ ] Proper permission validation
- [ ] Session management secure

### Step 4: Test Coverage Review

**Test Presence:**
- [ ] New code has tests (unit minimum)
- [ ] Modified code tests updated
- [ ] Edge cases covered
- [ ] Error paths tested

**Test Quality:**
- [ ] Tests independent (no interdependencies)
- [ ] Tests use proper mocking
- [ ] Test names describe behavior
- [ ] Tests are deterministic (no flakiness)
- [ ] No external dependencies in tests

**Run Tests:**
```bash
# Python projects
uv run pytest tests/ -v

# JavaScript/TypeScript
npm test

# Go
go test ./...

# Rust
cargo test
```

**Coverage Check:**
- New code should have >80% coverage
- Critical paths should have 100% coverage
- Acceptable if legacy code has lower coverage

### Step 5: Documentation Review

**Public API Documentation:**
- [ ] Functions/methods have docstrings/JSDoc
- [ ] Parameters documented
- [ ] Return values documented
- [ ] Exceptions documented

**Complex Logic:**
- [ ] WHY comments present (not WHAT)
- [ ] Non-obvious logic explained
- [ ] Algorithm choices justified

**High-Level Documentation:**
- [ ] README updated (if public API changed)
- [ ] CHANGELOG updated (for notable changes)
- [ ] ADR created (for architectural decisions)
- [ ] Migration guide updated (for breaking changes)

### Step 6: Anti-Pattern Detection

**Read project-specific anti-patterns from CLAUDE.md:**

#### Universal Anti-Patterns

**❌ Optional Config Parameters:**
```python
# ❌ WRONG
def __init__(self, config: Config | None = None):
    if not config:
        config = Config()

# ✅ CORRECT
def __init__(self, config: Config):
    if not config:
        raise ValueError("Config required")
```

**❌ try/except ImportError:**
```python
# ❌ WRONG
try:
    import optional_library
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

# ✅ CORRECT
import optional_library  # Fail fast at top
```

**❌ Methods with "and" in name:**
```python
# ❌ WRONG (violates SRP)
def process_and_save_data():
    data = process()
    save(data)

# ✅ CORRECT
def process_data(): ...
def save_data(): ...
```

**❌ Returning None on error:**
```python
# ❌ WRONG
def get_user(id: int) -> User | None:
    try:
        return fetch_user(id)
    except:
        return None  # Silent failure

# ✅ CORRECT (ServiceResult pattern)
def get_user(id: int) -> ServiceResult[User]:
    try:
        user = fetch_user(id)
        return ServiceResult.success(user)
    except Exception as e:
        return ServiceResult.failure(f"Failed to fetch user: {e}")
```

**❌ Sequential Edit operations:**
```python
# ❌ WRONG (30-50% more tokens)
Edit("file.py", old1, new1)
Edit("file.py", old2, new2)

# ✅ CORRECT (use MultiEdit)
MultiEdit("file.py", [
    {"old_string": old1, "new_string": new1},
    {"old_string": old2, "new_string": new2}
])
```

#### Project-Specific Anti-Patterns

**Scan CLAUDE.md for:**
- Red Flags section (anti-patterns)
- Common Fixes section (known issues)
- Anti-Pattern Enforcement section (validation rules)

**Detection patterns:**
```bash
# Optional config parameters
grep -rn "config.*Optional\|config.*None.*=" src/

# try/except ImportError
grep -rn "try:.*import\|except ImportError" src/

# Methods with "and"
grep -rn "def.*_and_.*\|function.*And.*" src/

# Returning None on error
grep -rn "return None.*#.*error\|except:.*return None" src/
```

### Step 7: Quality Gates

**Run quality gates using run-quality-gates skill:**
- Invoke `run-quality-gates` skill if available
- Otherwise run project-specific quality gates:

**Python projects:**
```bash
# Unified script (preferred)
./scripts/check_all.sh

# Individual tools
uv run pyright       # Type checking
uv run vulture src/  # Dead code
uv run pytest tests/ # Tests
uv run ruff check    # Linting
```

**JavaScript/TypeScript projects:**
```bash
npm run check        # Unified

# Individual
npx tsc --noEmit     # Type checking
npx eslint src/      # Linting
npm test             # Tests
```

**All gates must pass before declaring "ready to commit".**

### Step 8: Review Report Generation

**Report structure:**

```markdown
## 🔍 Code Review Report

**Changes:** X files modified, +Y lines, -Z lines

### ✅ Passed Checks (N/8)
- Architecture boundaries respected
- Code quality standards met
- All tests pass (X passed, 0 failed)
- Documentation complete
- No anti-patterns detected
- Quality gates pass

### ❌ Failed Checks (N/8)
1. **[CRITICAL] SRP Violation** - `src/services/user_service.py:45`
   - Issue: Method `validate_and_save_user()` does multiple things
   - Fix: Split into `validate_user()` and `save_user()`
   - Priority: HIGH

2. **[CRITICAL] Missing Tests** - `src/features/new_feature.py`
   - Issue: New functionality lacks test coverage
   - Fix: Add unit tests for `process_request()` method
   - Priority: HIGH

### ⚠️ Warnings (N)
1. **Magic Number** - `src/config.py:12`
   - Issue: Hardcoded value `42`
   - Fix: Move to settings or document reasoning
   - Priority: MEDIUM

2. **Missing Docstring** - `src/utils/helper.py:20`
   - Issue: Public function lacks documentation
   - Fix: Add docstring with parameters and return value
   - Priority: LOW

### 📊 Summary

❌ **NOT READY TO COMMIT**
- 2 critical issues must be fixed
- 2 warnings should be addressed
- Run self-review again after fixes

---

**Next Steps:**
1. Fix SRP violation in user_service.py (split method)
2. Add tests for new_feature.py (minimum 80% coverage)
3. Address magic number warning (move to config)
4. Add missing docstring (improves maintainability)
5. Re-run self-review to verify fixes
```

## Integration with Other Skills

### With validate-layer-boundaries

```python
# Invoke validate-layer-boundaries for architecture check
result = invoke_skill("validate-layer-boundaries")
if result.has_violations:
    report.add_failure("Architecture boundaries violated")
```

### With run-quality-gates

```python
# Invoke run-quality-gates for quality checks
result = invoke_skill("run-quality-gates")
if not result.all_pass:
    report.add_failure("Quality gates failing")
```

### With detect-refactor-markers

```python
# Check for active refactor markers
result = invoke_skill("detect-refactor-markers")
if result.has_stale_markers:
    report.add_warning("Stale refactor markers present")
```

## Language-Specific Adaptations

### Python Projects

**Detection:** `pyproject.toml`, `requirements.txt`, `setup.py`

**Quality Gates:**
- Type checking: `pyright` or `mypy`
- Linting: `ruff` or `pylint`
- Dead code: `vulture`
- Tests: `pytest`

**Anti-Patterns:**
- Optional config parameters
- ServiceResult pattern violations
- try/except ImportError

### JavaScript/TypeScript Projects

**Detection:** `package.json`, `tsconfig.json`

**Quality Gates:**
- Type checking: `tsc --noEmit`
- Linting: `eslint`
- Tests: `jest`, `vitest`, or `mocha`

**Anti-Patterns:**
- Bare `any` types
- Unhandled promise rejections
- Missing error boundaries

### Go Projects

**Detection:** `go.mod`

**Quality Gates:**
- Build: `go build ./...`
- Linting: `golangci-lint`
- Tests: `go test ./...`

**Anti-Patterns:**
- Ignoring errors
- Not using defer for cleanup
- Global mutable state

### Rust Projects

**Detection:** `Cargo.toml`

**Quality Gates:**
- Check: `cargo check`
- Linting: `cargo clippy`
- Tests: `cargo test`

**Anti-Patterns:**
- Unsafe code without justification
- Unwrap without error handling
- Clone instead of borrowing

## Output Examples

### Success Example (All Pass)

```
🔍 Code Review Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changes: 3 files modified, +147 lines, -23 lines

✅ Passed Checks (8/8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Architecture: Clean Architecture boundaries respected
✅ Single Responsibility: All methods have single purpose
✅ Code Quality: Style, logic, performance checks pass
✅ Security: No hardcoded secrets, input validated
✅ Tests: All tests pass (45 passed, 0 failed), 92% coverage
✅ Documentation: Docstrings complete, CHANGELOG updated
✅ Anti-Patterns: No violations detected
✅ Quality Gates: All gates pass (pyright, ruff, pytest, vulture)

📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ READY TO COMMIT

Your changes meet all quality standards and are ready to commit.

Modified files:
  - src/application/services/search_service.py (+89, -10)
  - src/domain/models/search_result.py (+42, -8)
  - tests/unit/application/test_search_service.py (+16, -5)

Next step: Create commit with descriptive message
```

### Failure Example (Issues Found)

```
🔍 Code Review Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changes: 5 files modified, +234 lines, -67 lines

✅ Passed Checks (4/8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Architecture: Clean Architecture boundaries respected
✅ Security: No hardcoded secrets, input validated
✅ Tests: All tests pass (52 passed, 0 failed)
✅ Documentation: Docstrings present

❌ Failed Checks (3/8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [CRITICAL] Single Responsibility Violation
   File: src/application/services/user_service.py:45
   Issue: Method `validate_and_save_user()` violates SRP
   Code:
   ```python
   def validate_and_save_user(self, user_data: dict):
       # Validation logic (responsibility 1)
       if not user_data.get("email"):
           raise ValueError("Email required")
       # Saving logic (responsibility 2)
       self.repository.save(user_data)
   ```
   Fix: Split into two methods
   ```python
   def validate_user(self, user_data: dict) -> bool:
       if not user_data.get("email"):
           return False
       return True

   def save_user(self, user_data: dict) -> ServiceResult[User]:
       if not self.validate_user(user_data):
           return ServiceResult.failure("Invalid user data")
       return self.repository.save(user_data)
   ```
   Priority: HIGH

2. [CRITICAL] Anti-Pattern: Optional Config Parameter
   File: src/infrastructure/cache/redis_cache.py:12
   Issue: Config parameter is optional with default creation
   Code:
   ```python
   def __init__(self, config: CacheConfig | None = None):
       if not config:
           config = CacheConfig()  # ❌ Creating default
   ```
   Fix: Make config required
   ```python
   def __init__(self, config: CacheConfig):
       if not config:
           raise ValueError("CacheConfig required")
       self.config = config
   ```
   Priority: HIGH

3. [CRITICAL] Quality Gate Failure: Type Checking
   Tool: pyright
   Errors:
   - src/application/services/search_service.py:78
     error: Type "None" cannot be assigned to type "str"
   - src/domain/models/search_result.py:23
     error: Argument of type "int" cannot be assigned to parameter "score: float"

   Fix: Update type annotations or handle None cases
   Priority: HIGH

⚠️ Warnings (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Magic Number
   File: src/application/services/search_service.py:45
   Issue: Hardcoded value `100` without explanation
   Code: `if score > 100:`
   Fix: Move to settings or add comment explaining threshold
   Priority: MEDIUM

2. Missing Test Coverage
   File: src/infrastructure/cache/redis_cache.py
   Issue: New `clear_cache()` method has no tests
   Fix: Add unit test for cache clearing behavior
   Priority: MEDIUM

📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ NOT READY TO COMMIT

3 critical issues must be fixed before committing
2 warnings should be addressed for better quality

Modified files:
  - src/application/services/user_service.py (+67, -12) ❌
  - src/application/services/search_service.py (+89, -23) ⚠️
  - src/infrastructure/cache/redis_cache.py (+45, -8) ❌
  - src/domain/models/search_result.py (+18, -15) ❌
  - tests/unit/application/test_user_service.py (+15, -9) ✅

Next Steps (in order):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Fix SRP violation in user_service.py (split method into validate + save)
2. Fix optional config in redis_cache.py (make required, add validation)
3. Fix type errors in search_service.py and search_result.py
4. Address magic number in search_service.py (move to settings)
5. Add tests for redis_cache.py clear_cache() method
6. Re-run self-review to verify all fixes
```

## Anti-Patterns to Avoid

**❌ DON'T: Skip review because "it's a small change"**
- Small changes can introduce big bugs
- Always run review, even for 1-line changes
- Fast review (10-30s) vs hours debugging

**❌ DON'T: Ignore warnings**
- Warnings become technical debt
- Address now (30s) vs refactor later (hours)
- Maintain high standards consistently

**❌ DON'T: Commit with failing quality gates**
- "Will fix later" rarely happens
- Broken main branch affects entire team
- Quality gates exist for a reason

**❌ DON'T: Skip test coverage check**
- Untested code = unverified code
- Tests document expected behavior
- Bugs found in review < bugs found in production

**❌ DON'T: Override critical failures without user approval**
- Agent cannot decide to ignore SRP violations
- Agent cannot decide to skip tests
- Must escalate to user for guidance

## Best Practices

**✅ DO: Run review before every commit**
- Make it part of workflow (like saving files)
- Automation prevents human error
- Consistency ensures quality

**✅ DO: Fix issues immediately**
- Context is fresh in your mind
- Fixes are faster now than later
- Prevents compounding technical debt

**✅ DO: Read project-specific guidelines**
- Every project has unique patterns
- Respect established conventions
- Align with team standards

**✅ DO: Provide specific, actionable fixes**
- File:line:column locations
- Code snippets showing before/after
- Clear explanation of why change needed

**✅ DO: Re-run review after fixes**
- Verify fixes actually work
- Catch any new issues introduced
- Confirm "ready to commit" status

## Configuration

### Custom Review Checklist

Projects can define custom review criteria in `.claude/code-review-checklist.md`:

```markdown
## Project-Specific Review Checklist

### Architecture
- [ ] All services use dependency injection
- [ ] No circular dependencies
- [ ] Repository pattern used for data access

### Testing
- [ ] Integration tests for all API endpoints
- [ ] Mocks used for external services
- [ ] Snapshot tests for UI components

### Security
- [ ] JWT tokens validated
- [ ] Rate limiting applied
- [ ] CORS configured correctly
```

Skill will merge project checklist with universal checklist.

### Quality Gate Configuration

Read quality gates from `CLAUDE.md` or `.claude/quality-gates.json`:

```json
{
  "required_gates": ["type_checking", "linting", "tests"],
  "optional_gates": ["dead_code", "coverage"],
  "coverage_threshold": 80,
  "fail_on_warnings": false
}
```

## Supporting Files

- [references/review-checklist.md](references/review-checklist.md) - Complete review checklist (copy-paste ready)
- [references/anti-patterns-catalog.md](references/anti-patterns-catalog.md) - Comprehensive anti-pattern database
- [references/language-specific-guides.md](references/language-specific-guides.md) - Python, JS, Go, Rust specifics

## Utility Scripts

- [Detect Project Type Script](./scripts/detect_project_type.sh) - Detect project language/framework

## Success Metrics

| Metric | Target | Benefit |
|--------|--------|---------|
| Review before commit | 100% | Zero unreviewed commits |
| Critical issues caught | >95% | Prevent bugs reaching main |
| Review time | <2 min | Fast enough to not block |
| False positives | <5% | High signal-to-noise ratio |
| Rework after PR review | -70% | Catch issues earlier |

## Troubleshooting

**Issue: Review too slow (>5 minutes)**
```bash
# Optimize by skipping some checks
# Review only staged files (not all modified)
git diff --staged --name-only | xargs review

# Run quality gates in parallel
./scripts/check_all.sh  # Already parallelized
```

**Issue: Too many false positives**
```bash
# Tune detection patterns in .claude/review-config.json
{
  "skip_patterns": ["test_*.py", "*.test.ts"],
  "ignore_rules": ["magic-number-in-tests"]
}
```

**Issue: Project type not detected**
```bash
# Manually specify project type
export PROJECT_TYPE="python"  # or "javascript", "go", "rust"

# Or create .claude/project-type file
echo "python" > .claude/project-type
```

## Usage Examples

### Example 1: Pre-Commit Review

```bash
# User: "Review my changes before commit"
# Skill invocation:
Skill(command: "code-review")

# Output: 8 checks performed
✅ Architecture boundaries respected
⚠️ Missing docstring warning
❌ Optional config anti-pattern detected
```

### Example 2: All Checks Pass

```bash
# User: "Am I ready to commit?"
# Skill invocation:
Skill(command: "code-review")

# Output: All green
✅ All review checks passed (8/8)
✅ READY TO COMMIT
```

## Expected Outcomes

### Success (Ready to Commit)

```
✅ Code Review: PASSED

All checks: 8/8
- Architecture boundaries validated
- Code quality standards met
- All tests passing
- Documentation complete
- No anti-patterns detected

You can safely commit these changes.
```

### Failure (Issues Found)

```
❌ Code Review: NOT READY

Checks: 4/8 passed
Critical issues: 3
Warnings: 2

Must fix before committing:
1. SRP violation in user_service.py
2. Optional config in redis_cache.py
3. Type errors in search_service.py
```

## Integration Points

### With Other Skills

**code-review integrates with:**
- **run-quality-gates** - Invoked as Step 7 of review process
- **validate-layer-boundaries** - For architecture validation
- **detect-refactor-markers** - Check for stale markers
- **git-commit-push** - Pre-commit validation

### With Agent Workflows

**Agents should invoke this skill:**
- @code-review-expert - Primary user of this skill
- @implementer - Before marking tasks complete
- @debugging-expert - After fixing bugs

### With TodoWrite Tool

**Integration pattern:**
```python
# Before marking todo as completed
run_code_review()  # Invoke skill
if review_passed:
    TodoWrite([{"content": "Task", "status": "completed"}])
```

## Examples

See [references/examples.md](references/examples.md) for comprehensive examples including:
- Python project with Clean Architecture
- JavaScript/React project
- Go microservice
- Rust CLI application
- Multi-language monorepo
- Legacy codebase (relaxed rules)

## Expected Benefits

| Metric | Without Code Review | With Code Review | Improvement |
|--------|-------------------|-----------------|-------------|
| Issues caught pre-commit | 30-40% | 95%+ | 158% increase |
| Time spent in PR review | 30-60 min | 10-20 min | 66% reduction |
| Bugs reaching production | 10-15 per release | 1-2 per release | 90% reduction |
| Architecture violations | 15-20 per quarter | 0-2 per quarter | 95% reduction |
| Code review time | 2-5 min | 30-90 sec | 75% faster |
| Rework after PR feedback | 40-50% | 5-10% | 85% reduction |

## Requirements

**No external dependencies** - Skill uses project's existing tools.

**Minimum requirements:**
- Git (for change detection)
- Project's quality gate tools (pyright, eslint, etc.)
- Bash shell (for script execution)

**Optional:**
- `CLAUDE.md` with project-specific anti-patterns
- `.claude/code-review-checklist.md` for custom checks
- Skills: `validate-layer-boundaries`, `run-quality-gates`, `detect-refactor-markers`

---

**Integration with Git Hooks:**

Create `.git/hooks/pre-commit` to auto-invoke this skill:
```bash
#!/bin/bash
# Auto-run code-review before every commit

echo "Running code-review..."
claude-skill code-review

if [ $? -ne 0 ]; then
    echo "❌ Code review failed. Fix issues before committing."
    exit 1
fi

echo "✅ Code review passed"
exit 0
```

**Last Updated:** 2025-10-17
**Version:** 1.0.0
