---
name: architecture-single-responsibility-principle
description: |
  Automated SRP validation using multi-dimensional detection. Use when reviewing code for SRP compliance, checking "is this doing too much", validating architectural boundaries, before commits, or during refactoring. Detects God classes, method naming violations, complexity issues.
allowed-tools:
- Read
- Grep
- Glob
- Bash
- mcp__ast-grep__find_code
- mcp__ast-grep__find_code_by_rule
- mcp__project-watch-mcp__search_code
---

# Single Responsibility Principle Validation

## Table of Contents

**Quick Start** → [When to Use](#when-to-use-this-skill) | [What It Does](#purpose) | [Simple Example](#quick-start)

**How to Implement** → [Detection Process](#instructions) | [Validation Levels](#step-1-determine-validation-level) | [Expected Output](#step-5-output-report)

**Patterns** → [Detection Patterns](#detection-patterns) | [Project Patterns](./references/project-patterns.md)

**Help** → [Troubleshooting](#troubleshooting) | [Requirements](#requirements) | [Integration](#integration-points)

**Reference** → [SRP Principles](./references/srp-principles.md) | [Detection Patterns](./references/detection-patterns.md) | [Quick Reference](./references/quick-reference.md)

---

## When to Use This Skill

**MANDATORY in these situations:**
- Before declaring architectural refactoring complete
- During code reviews for SRP compliance
- Before commits that modify class structure
- When user says "check SRP", "validate single responsibility"
- After implementing new services or handlers

**User trigger phrases:**
- "check SRP"
- "single responsibility"
- "is this doing too much?"
- "validate SRP"
- "god class check"
- "class too large"
- "method doing too much"

## Purpose

Automatically detect Single Responsibility Principle violations using multi-dimensional analysis: naming patterns, class metrics, method complexity, and project-specific architectural patterns. Provides actionable fix guidance with confidence scoring.

## Quick Start

```bash
# Validate entire codebase (thorough level)
Skill(command: "single-responsibility-principle")

# Validate specific directory
Skill(command: "single-responsibility-principle --path=src/services/")

# Fast validation (pre-commit)
Skill(command: "single-responsibility-principle --level=fast")

# Full validation with JSON output
Skill(command: "single-responsibility-principle --level=full --format=json")
```

## Instructions

### Step 1: Determine Validation Level

Choose based on context:
- **fast**: Naming patterns + basic size metrics (5-10s, pre-commit)
- **thorough**: + Complexity metrics + project patterns (30s, default)
- **full**: + Actor analysis + cohesion metrics (1-2min, comprehensive)

### Step 2: Run Detection

Execute multi-dimensional detection:

1. **Naming Analysis** (ast-grep):
   - Methods with "and" in name → 40% confidence violation
   - Files named "manager", "handler", "utils" → review needed

2. **Size Metrics** (AST or line count):
   - Classes >300 lines → review needed
   - Files >500 lines → review needed
   - Methods >50 lines → 60% confidence violation
   - Classes >15 methods → review needed

3. **Dependency Analysis** (constructor params):
   - 5-8 params → warning (75% confidence)
   - >8 params → critical (90% confidence)

4. **Complexity Metrics** (radon if available):
   - Cyclomatic complexity >10 → 60% confidence violation
   - God class detection (ATFD >5 AND WMC >47 AND TCC <0.33) → 80% confidence

5. **Project-Specific Patterns**:
   - Optional config parameters → critical violation
   - Domain entities doing I/O → critical violation
   - Application services with business logic → violation
   - Repositories with orchestration → violation

### Step 3: Categorize Violations

Assign confidence levels:
- **CRITICAL (80%+)**: God classes, optional config, architecture violations
- **WARNING (60-80%)**: Long methods, many dependencies, complexity
- **REVIEW (40-60%)**: Naming patterns, size thresholds

### Step 4: Generate Fix Guidance

For each violation:
1. Identify specific issue (line, pattern, metric)
2. Suggest split strategy (actor-based)
3. Provide example (from references/project-patterns.md)
4. Estimate refactoring time

### Step 5: Output Report

Format results:
```
Single Responsibility Principle Validation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scope: path/to/code
Level: thorough
Files Analyzed: X
Classes Analyzed: Y

✅ Passed: Z/Y classes (P%)

❌ Violations Found: N

[CRITICAL] God Class: ClassName (path/file.py:45)
  - Lines: 450 (threshold: 300)
  - Methods: 23 (threshold: 15)
  - Constructor params: 9 (threshold: 4)
  - Complexity metrics: ATFD=8, WMC=52, TCC=0.28
  - Actors identified: 3 (persistence, validation, coordination)
  - Fix: Split into:
    * ClassNamePersistence (handles database operations)
    * ClassNameValidator (handles validation logic)
    * ClassNameCoordinator (orchestrates workflow)
  - Estimated effort: 4-6 hours

[WARNING] Method Name Violation: validate_and_save_user (path/file.py:120)
  - Method name contains 'and' (40% confidence)
  - Fix: Split into:
    * validate_user() -> ServiceResult[User]
    * save_user(user: User) -> ServiceResult[None]
  - Estimated effort: 30 minutes

[WARNING] Long Method: process_data (path/file.py:200)
  - Lines: 75 (threshold: 50)
  - Cyclomatic complexity: 14 (threshold: 10)
  - Fix: Extract helper methods for each logical section
  - Estimated effort: 1-2 hours

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical: X violations
Warnings: Y violations
Reviews needed: Z items

Total estimated refactoring time: A-B hours

Next Steps:
1. Address critical violations first (God classes, architecture)
2. Refactor method name violations
3. Break down long methods
4. Review class sizes for potential splits
```

## Examples

### Example 1: Validate Entire Codebase

```python
# Default: thorough validation of src/
Skill(command: "single-responsibility-principle")
```

**Expected Output**: Full report with all violation types, confidence scores, fix guidance.

### Example 2: Fast Pre-Commit Check

```python
# Quick validation before commit
Skill(command: "single-responsibility-principle --level=fast")
```

**Expected Output**: Naming patterns + basic size metrics only (5-10s).

### Example 3: Validate Specific Service

```python
# Deep analysis of specific file
Skill(command: "single-responsibility-principle --path=src/application/services/indexing_service.py --level=full")
```

**Expected Output**: Comprehensive analysis including actor identification, cohesion metrics.

### Example 4: JSON Output for CI/CD

```python
# Machine-readable output
Skill(command: "single-responsibility-principle --level=thorough --format=json")
```

**Expected Output**:
```json
{
  "summary": {
    "files_analyzed": 45,
    "classes_analyzed": 78,
    "violations": 12,
    "passed": 66,
    "pass_rate": 0.846
  },
  "violations": [
    {
      "level": "critical",
      "type": "god_class",
      "file": "src/services/user_service.py",
      "line": 45,
      "class": "UserService",
      "metrics": {
        "lines": 450,
        "methods": 23,
        "params": 9,
        "atfd": 8,
        "wmc": 52,
        "tcc": 0.28
      },
      "confidence": 0.85,
      "fix": "Split into UserServicePersistence, UserServiceValidator, UserServiceCoordinator",
      "effort_hours": [4, 6]
    }
  ]
}
```

## Requirements

### Required Tools
- `mcp__ast-grep__find_code`: AST-based pattern detection
- `Read`: File analysis
- `Bash`: Metrics calculation (radon if available)
- `Grep`: Quick pattern matching
- `Glob`: File discovery

### Optional Dependencies
- `radon`: Python complexity metrics (`pip install radon`)
  - If unavailable: Use basic AST metrics (line counts, method counts)
- `pylint`: Additional metrics (`pip install pylint`)
  - If unavailable: Skip cohesion metrics (TCC, ATFD)

### Installation
```bash
# Install optional metrics tools
uv pip install radon pylint

# Verify installation
radon --version
pylint --version
```

## Detection Patterns

### Pattern 1: Method Names with "and"
```yaml
id: method-name-and
language: python
rule:
  pattern: "def $NAME_and_$REST"
```

### Pattern 2: God Classes
```yaml
id: god-class
language: python
rule:
  pattern: |
    class $NAME:
      $$$BODY
  has:
    stopBy: end
    kind: function_definition
    count: { min: 15 }
```

### Pattern 3: Constructor with Many Parameters
```yaml
id: constructor-params
language: python
rule:
  pattern: |
    def __init__(self, $$$PARAMS):
      $$$BODY
  constraints:
    PARAMS:
      count: { min: 5 }
```

### Pattern 4: Optional Config Anti-Pattern
```yaml
id: optional-config
language: python
rule:
  pattern: "$NAME: $TYPE | None = None"
  inside:
    kind: function_definition
    pattern: "def __init__"
```

## Integration Points

### With code-review Skill
Add SRP validation as Step 2 sub-check:
```markdown
## Step 2: Single Responsibility Review
- [ ] Run `single-responsibility-principle --level=fast`
- [ ] Address critical violations
- [ ] Document acceptable warnings
```

### With validate-architecture Skill
Include SRP at layer level:
```python
# Check domain entities don't do I/O
# Check application services don't contain business logic
# Check repositories only do data access
```

### With run-quality-gates Skill
Add as quality gate:
```bash
# In check_all.sh or quality gate hook
Skill(command: "single-responsibility-principle --level=fast")
# Block commit if critical violations found
```

### With multi-file-refactor Skill
Coordinate SRP refactoring across files:
```python
# Identify all God classes
# Plan extraction strategy
# Use MultiEdit for atomic refactoring
```

## Troubleshooting

### "radon not found"
**Solution**: Install with `uv pip install radon` or skip complexity metrics (use --level=fast)

### "Too many false positives"
**Solution**: Adjust thresholds in detection patterns or focus on critical violations only

### "Analysis too slow"
**Solution**: Use `--level=fast` or `--path=specific/directory` to narrow scope

### "Missing violations"
**Solution**: Use `--level=full` for comprehensive analysis including actor identification

## See Also

- [srp-principles.md](./references/srp-principles.md) - Core SRP concepts and misconceptions
- [detection-patterns.md](./references/detection-patterns.md) - AST patterns and metrics thresholds
- [project-patterns.md](./references/project-patterns.md) - project-watch-mcp specific patterns
- [quick-reference.md](./references/quick-reference.md) - One-page SRP checklist
