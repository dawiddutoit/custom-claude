---
name: util-multi-file-refactor
description: Optimizes multi-file refactoring workflows by enforcing token-efficient MultiEdit usage (30-50% savings), coordinating changes across files, validating imports/references, and running quality gates. Use when refactoring patterns across codebase, renaming functions/classes/variables, extracting common code, moving functionality, or updating patterns in multiple files. Prevents sequential Edit anti-patterns.
allowed-tools:
  - Read
  - Edit
  - MultiEdit
  - Grep
  - Glob
  - Bash
---

# Multi-File Refactor

## Purpose
Provides systematic, token-efficient multi-file refactoring with safety checks. Enforces MultiEdit for 2+ changes per file (30-50% token savings vs sequential Edit), coordinates cross-file changes, validates imports/references, and ensures quality gates pass. Prevents anti-patterns like blind editing or incomplete refactoring.

## Table of Contents

### Core Sections

- [When to Use This Skill](#when-to-use-this-skill)
  - [Primary Triggers (User Requests)](#primary-triggers-user-requests)
  - [Contextual Triggers (Agent Detection)](#contextual-triggers-agent-detection)
  - [When NOT to Use](#when-not-to-use)

- [What This Skill Does](#what-this-skill-does)
  - [Core Capabilities](#core-capabilities)

- [Quick Start](#quick-start)

- [Refactoring Workflow](#refactoring-workflow)
  - [Phase 1: Discovery & Analysis](#phase-1-discovery--analysis)
  - [Phase 2: Change Planning](#phase-2-change-planning)
  - [Phase 3: Execution](#phase-3-execution)
  - [Phase 4: Import & Reference Updates](#phase-4-import--reference-updates)
  - [Phase 5: Validation](#phase-5-validation)
  - [Phase 6: Reporting](#phase-6-reporting)

- [Token Optimization Rules](#token-optimization-rules)
  - [Rule 1: ALWAYS Use MultiEdit for 2+ Edits](#rule-1-always-use-multiedit-for-2-edits)
  - [Rule 2: Group Changes by File](#rule-2-group-changes-by-file)
  - [Rule 3: Read Before Modifying](#rule-3-read-before-modifying)
  - [Rule 4: Batch Independent Operations](#rule-4-batch-independent-operations)

- [Common Refactoring Patterns](#common-refactoring-patterns)
  - [Pattern 1: Function/Method Rename](#pattern-1-functionmethod-rename)
  - [Pattern 2: Class Rename](#pattern-2-class-rename)
  - [Pattern 3: Module/File Move](#pattern-3-modulefile-move)
  - [Pattern 4: Extract Common Code](#pattern-4-extract-common-code)
  - [Pattern 5: API Signature Change](#pattern-5-api-signature-change)
  - [Pattern 6: Configuration Migration](#pattern-6-configuration-migration)

- [Language-Specific Guidance](#language-specific-guidance)
  - [Python](#python)
  - [JavaScript/TypeScript](#javascripttypescript)
  - [Java](#java)
  - [Go](#go)

### Advanced Topics

- [Edge Cases & Troubleshooting](#edge-cases--troubleshooting)
  - [Edge Case 1: Pattern in Strings/Comments](#edge-case-1-pattern-in-stringscomments)
  - [Edge Case 2: Partial Matches](#edge-case-2-partial-matches)
  - [Edge Case 3: Generated/Vendored Code](#edge-case-3-generatedvendored-code)
  - [Edge Case 4: Circular Dependencies](#edge-case-4-circular-dependencies)
  - [Edge Case 5: Tests Failing After Refactor](#edge-case-5-tests-failing-after-refactor)
  - [Edge Case 6: MultiEdit Conflicts](#edge-case-6-multiedit-conflicts)

- [Validation Checklist](#validation-checklist)

- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
  - [❌ Anti-Pattern 1: Sequential Edit on Same File](#-anti-pattern-1-sequential-edit-on-same-file)
  - [❌ Anti-Pattern 2: Blind Editing Without Reading](#-anti-pattern-2-blind-editing-without-reading)
  - [❌ Anti-Pattern 3: Skipping Tests](#-anti-pattern-3-skipping-tests)
  - [❌ Anti-Pattern 4: Ignoring Quality Gates](#-anti-pattern-4-ignoring-quality-gates)
  - [❌ Anti-Pattern 5: Forgetting Imports](#-anti-pattern-5-forgetting-imports)
  - [❌ Anti-Pattern 6: Incomplete Refactoring](#-anti-pattern-6-incomplete-refactoring)
  - [❌ Anti-Pattern 7: Wrong Dependency Order](#-anti-pattern-7-wrong-dependency-order)

- [Success Metrics](#success-metrics)

- [Expected Benefits](#expected-benefits)

### Supporting Resources

- [Supporting Files](#supporting-files)
  - [refactoring-patterns.md](./references/refactoring-patterns.md) - Detailed pattern recipes
  - [language-guides.md](./references/language-guides.md) - Language-specific refactoring guides
  - [quality-gates.md](./references/quality-gates.md) - Quality gate reference by language
  - [troubleshooting.md](./references/troubleshooting.md) - Common issues and solutions

- [Usage Examples](#usage-examples)
  - [Example 1: Function Rename (Python)](#example-1-function-rename-python)
  - [Example 2: Class Rename (JavaScript)](#example-2-class-rename-javascript)
  - [Example 3: Extract Common Utility (Python)](#example-3-extract-common-utility-python)

- [Integration Points](#integration-points)
  - [With Quality Gate Systems](#with-quality-gate-systems)
  - [With CI/CD Pipelines](#with-cicd-pipelines)
  - [With Version Control](#with-version-control)
  - [With Agent Orchestration](#with-agent-orchestration)

- [Requirements](#requirements)
  - [File System Access](#file-system-access)
  - [Tool Access](#tool-access)
  - [Language/Framework Tools](#languageframework-tools)
  - [Project Structure](#project-structure)

- [Invocation Triggers](#invocation-triggers)

## When to Use This Skill

### Primary Triggers (User Requests)

Use this skill when user asks to:
- "Refactor X across the codebase"
- "Rename function/class/variable throughout project"
- "Update pattern in multiple files"
- "Extract common code/functionality"
- "Move functionality to another module"
- "Replace pattern A with pattern B"
- "Consolidate duplicate code"
- "Update all usages of X"

### Contextual Triggers (Agent Detection)

Invoke this skill when:
- Grep/Glob reveals 2+ files need the same change
- Pattern appears in multiple locations (detected via search)
- Refactoring requires coordinated changes across modules
- Import statements need updating across files
- Function/class signatures changing with multiple callers

### When NOT to Use

Skip this skill when:
- Single file needs changes (use Edit/MultiEdit directly)
- Changes are unrelated (not a refactoring pattern)
- Trivial find-replace with no context needed
- Experimental changes (not ready for systematic refactor)

## What This Skill Does

Provides systematic, token-efficient multi-file refactoring with safety checks:

### Core Capabilities

1. **Pattern Discovery**
   - Find all files matching refactor criteria
   - Identify related code (imports, usages, tests)
   - Map dependencies between files
   - Detect test files requiring updates

2. **Token-Efficient Editing**
   - Enforce MultiEdit for files with 2+ changes (30-50% token savings)
   - NEVER use sequential Edit operations on same file
   - Group related changes by file
   - Batch operations when possible

3. **Cross-File Coordination**
   - Update imports in dependent files
   - Fix broken references
   - Maintain consistency across modules
   - Handle cascading changes

4. **Quality Validation**
   - Run tests after changes
   - Run quality gates (linting, type checking)
   - Verify no broken imports/references
   - Ensure all changes are consistent

5. **Safety Checks**
   - Read files before modifying
   - Validate patterns before applying
   - Check for edge cases
   - Report issues before committing

## Quick Start

**User:** "Rename the `process_data` function to `transform_data` across the codebase"

**Skill execution:**
1. Find all files with `process_data` (Grep)
2. Read affected files to understand context
3. Group changes by file (identify files needing 2+ edits)
4. Use MultiEdit for each file (never sequential Edit)
5. Update imports and references
6. Run tests to validate
7. Run quality gates
8. Report results

**Result:** All occurrences updated, tests pass, quality gates pass, 35% token savings vs sequential edits.

## Refactoring Workflow

### Phase 1: Discovery & Analysis

**Objective:** Understand the full scope of changes needed

```bash
# 1. Find all files matching the pattern
Glob: "**/*.{py,js,ts,java,go}" (adjust for language)
Grep: "pattern_to_refactor" (find all occurrences)

# 2. Identify related files
# - Files with direct usage
# - Files importing the target
# - Test files exercising the target
# - Documentation mentioning the target

# 3. Read all affected files
Read: file1.py, file2.py, file3.py, ...

# 4. Map dependencies
# - Which files import from which
# - Which tests cover which modules
# - Which changes depend on others
```

**Output:** Complete list of affected files, dependency graph, change plan

### Phase 2: Change Planning

**Objective:** Group changes efficiently by file

```
For each affected file:
  Count number of required edits

If file needs 1 edit:
  → Plan single Edit operation

If file needs 2+ edits:
  → Plan MultiEdit operation with all edits
  → NEVER use sequential Edit operations

Order files by dependencies:
  → Core definitions first
  → Usages second
  → Tests third
```

**Output:** Ordered list of file operations, each using optimal tool

### Phase 3: Execution

**Objective:** Apply changes systematically

```
For each file in dependency order:

  If single edit:
    Edit(
      file_path=file_path,
      old_string=exact_old_string,
      new_string=exact_new_string
    )

  If multiple edits:
    MultiEdit(
      file_path=file_path,
      edits=[
        {old_string: old1, new_string: new1},
        {old_string: old2, new_string: new2},
        ...
      ]
    )

  Log: "Updated {file_path} with {N} changes"
```

**Output:** All files modified using token-efficient operations

### Phase 4: Import & Reference Updates

**Objective:** Fix cascading changes

```
# 1. Check for broken imports
Grep: "from old_module import" or "import old_module"

# 2. Update import statements
For each file with old imports:
  Use MultiEdit if 2+ imports need updating

# 3. Verify cross-references
Check: All references still resolve correctly

# 4. Update documentation
If code docs/comments reference old names:
  Update to match new names
```

**Output:** All imports and references updated

### Phase 5: Validation

**Objective:** Ensure refactoring is correct and complete

```bash
# 1. Run tests (required)
bash: "pytest tests/ -v" (Python example)
# Adjust command for language/framework

# 2. Run quality gates (required)
bash: "./scripts/check_all.sh" (if exists)
# Or run linting/type checking individually

# 3. Check for missed occurrences
Grep: "old_pattern_name" (should return no results)

# 4. Verify imports
bash: Language-specific import validation
# Python: pyright, mypy
# JavaScript: eslint
# Java: javac, etc.
```

**Output:** All tests pass, quality gates pass, no missed occurrences

### Phase 6: Reporting

**Objective:** Communicate results clearly

```
Report format:

Refactoring Complete: [Pattern Description]

Files Modified: 12
  - Core modules: 4
  - Usage sites: 5
  - Tests: 3

Changes Applied:
  - Renamed: process_data → transform_data
  - Updated: 23 function calls
  - Fixed: 12 imports
  - Updated: 3 test files

Token Efficiency:
  - MultiEdit used: 8 files
  - Token savings: ~40% (vs sequential Edit)

Validation:
  ✅ All tests pass (15/15)
  ✅ Quality gates pass
  ✅ No broken imports
  ✅ No missed occurrences

Next Steps:
  - Review changes if needed
  - Update documentation
  - Consider updating changelog
```

## Token Optimization Rules

### Rule 1: ALWAYS Use MultiEdit for 2+ Edits

**❌ ANTI-PATTERN - Sequential Edit (wasteful)**
```
Edit(file="module.py", old_string=old1, new_string=new1)
Edit(file="module.py", old_string=old2, new_string=new2)
Edit(file="module.py", old_string=old3, new_string=new3)

Result: 3 tool calls, 3x file reads, excessive tokens
```

**✅ CORRECT - MultiEdit (efficient)**
```
MultiEdit(
  file_path="module.py",
  edits=[
    {old_string: old1, new_string: new1},
    {old_string: old2, new_string: new2},
    {old_string: old3, new_string: new3}
  ]
)

Result: 1 tool call, 1 file read, 30-50% token savings
```

### Rule 2: Group Changes by File

**Before executing:**
```
Changes needed:
  file1.py: 3 edits
  file2.py: 1 edit
  file3.py: 5 edits
  file4.py: 2 edits

Execution plan:
  MultiEdit(file1.py, [edit1, edit2, edit3])  ← 3 edits = MultiEdit
  Edit(file2.py, edit1)                        ← 1 edit = Edit
  MultiEdit(file3.py, [edit1...edit5])         ← 5 edits = MultiEdit
  MultiEdit(file4.py, [edit1, edit2])          ← 2 edits = MultiEdit
```

### Rule 3: Read Before Modifying

**Always read files first to:**
- Understand context
- Validate patterns exist
- Catch edge cases
- Plan exact old_string/new_string

**NEVER:**
- Make blind edits without reading
- Assume patterns without verification
- Edit files you haven't examined

### Rule 4: Batch Independent Operations

**If files have no dependencies:**
```
Can execute in parallel:
  - MultiEdit(file1.py, ...)
  - MultiEdit(file2.py, ...)
  - MultiEdit(file3.py, ...)

Reduces latency (operations don't wait on each other)
```

**If files have dependencies:**
```
Execute in order:
  1. Core definitions first
  2. Dependent usages second
  3. Tests third

Ensures each step sees correct state
```

## Common Refactoring Patterns

### Pattern 1: Function/Method Rename

**Scenario:** Rename `old_name()` to `new_name()` across codebase

**Steps:**
1. Find all definitions: `Grep: "def old_name("`
2. Find all usages: `Grep: "old_name("`
3. Find imports: `Grep: "from .* import.*old_name"`
4. Read affected files
5. Group changes by file (use MultiEdit if 2+ changes)
6. Update in order: definitions → usages → imports → tests
7. Validate: tests pass, no grep results for `old_name`

### Pattern 2: Class Rename

**Scenario:** Rename `OldClass` to `NewClass`

**Steps:**
1. Find class definition
2. Find all instantiations: `Grep: "OldClass("`
3. Find inheritance: `Grep: "class.*OldClass"`
4. Find imports: `Grep: "import.*OldClass"`
5. Find type hints: `Grep: "OldClass]" or ": OldClass"`
6. Read affected files
7. Use MultiEdit for files with multiple occurrences
8. Update tests (test class names often match)
9. Validate

### Pattern 3: Module/File Move

**Scenario:** Move functionality from `old/module.py` to `new/module.py`

**Steps:**
1. Find all imports: `Grep: "from old.module import"`
2. Read target file and destination
3. Move code (Edit or MultiEdit as needed)
4. Update all import statements (MultiEdit if 2+ in file)
5. Update `__init__.py` if needed
6. Run tests
7. Delete old file if empty
8. Validate imports resolve

### Pattern 4: Extract Common Code

**Scenario:** Extract duplicate code to shared utility

**Steps:**
1. Identify duplicated pattern across files
2. Create new utility module/function
3. Read all files with duplicates
4. Replace duplicates with utility calls (MultiEdit per file)
5. Add utility import to each file (combine with replacements in MultiEdit)
6. Run tests
7. Validate: no duplicates remain

### Pattern 5: API Signature Change

**Scenario:** Change function signature (add/remove/rename parameters)

**Steps:**
1. Find function definition
2. Find all call sites: `Grep: "function_name("`
3. Read affected files to understand current usage
4. Update definition (Edit)
5. Update all call sites (MultiEdit if multiple in same file)
6. Update tests to match new signature
7. Validate: tests pass with new signature

### Pattern 6: Configuration Migration

**Scenario:** Update config parameter names/structure

**Steps:**
1. Find all config usages: `Grep: "config.old_name"`
2. Read config definition
3. Update config definition (Edit or MultiEdit)
4. Update all usages (MultiEdit per file)
5. Update tests and fixtures
6. Update documentation
7. Validate: no old parameter references remain

## Language-Specific Guidance

### Python

**Discovery:**
```bash
Glob: "**/*.py"
Grep: "def function_name|class ClassName|import module_name"
```

**Quality Gates:**
```bash
bash: "pyright src/"          # Type checking
bash: "pytest tests/ -v"      # Tests
bash: "ruff check src/"       # Linting
```

**Import Patterns:**
```python
# Absolute imports
from package.module import function_name

# Relative imports
from .module import function_name
from ..parent import function_name
```

### JavaScript/TypeScript

**Discovery:**
```bash
Glob: "**/*.{js,ts,jsx,tsx}"
Grep: "function functionName|class ClassName|import.*from"
```

**Quality Gates:**
```bash
bash: "npm run test"          # Tests
bash: "npm run lint"          # ESLint
bash: "npm run typecheck"     # TypeScript
```

**Import Patterns:**
```javascript
// ES6 imports
import { functionName } from './module';
import ClassName from './module';

// CommonJS (if used)
const { functionName } = require('./module');
```

### Java

**Discovery:**
```bash
Glob: "**/*.java"
Grep: "public class ClassName|public.*methodName|import.*ClassName"
```

**Quality Gates:**
```bash
bash: "./gradlew test"        # Tests (Gradle)
bash: "mvn test"              # Tests (Maven)
bash: "./gradlew check"       # Checkstyle/PMD
```

**Import Patterns:**
```java
import com.package.ClassName;
import static com.package.ClassName.methodName;
```

### Go

**Discovery:**
```bash
Glob: "**/*.go"
Grep: "func FunctionName|type TypeName|import"
```

**Quality Gates:**
```bash
bash: "go test ./..."         # Tests
bash: "go vet ./..."          # Static analysis
bash: "golangci-lint run"     # Linting
```

**Import Patterns:**
```go
import "package/module"
import alias "package/module"
```

## Edge Cases & Troubleshooting

### Edge Case 1: Pattern in Strings/Comments

**Problem:** Grep finds pattern in string literals or comments

**Solution:**
```
1. Read file to see context
2. Only replace actual code references
3. Use specific old_string with surrounding context
4. Manually review string/comment occurrences
5. Update if semantically meaningful (e.g., error messages)
```

### Edge Case 2: Partial Matches

**Problem:** `Grep: "data"` matches `process_data`, `data_handler`, `metadata`

**Solution:**
```
1. Use more specific Grep patterns:
   Grep: "\\bdata\\b" (word boundaries)
   Grep: "def data\\(|class data\\(" (definition context)
2. Read results to filter false positives
3. Use precise old_string in edits
```

### Edge Case 3: Generated/Vendored Code

**Problem:** Refactor pattern appears in generated/vendored files

**Solution:**
```
1. Exclude from Glob:
   Glob: "src/**/*.py" (not "**/*.py")
   Skip: node_modules/, vendor/, .venv/, dist/
2. If must change: regenerate instead of manual edit
3. Document why generated code differs
```

### Edge Case 4: Circular Dependencies

**Problem:** File A imports from B, B imports from A

**Solution:**
```
1. Detect circular import (Grep import statements)
2. Refactor to break cycle first (extract interface/base)
3. Then proceed with original refactor
4. Validate with import checker
```

### Edge Case 5: Tests Failing After Refactor

**Problem:** Refactor complete but tests fail

**Solution:**
```
1. Read test failure messages carefully
2. Check if tests use old names (mocks, fixtures)
3. Update test helpers/utilities (often missed)
4. Check test data/fixtures for hardcoded references
5. Re-run after fixing
```

### Edge Case 6: MultiEdit Conflicts

**Problem:** MultiEdit edits overlap or conflict

**Solution:**
```
1. Ensure old_strings are unique within file
2. Use surrounding context if needed:
   Old: "def process():\n    return data"
   Not: "return data" (too vague)
3. If overlapping, split into sequential MultiEdit calls
4. Read file after first edit to plan second
```

## Validation Checklist

Before reporting refactor complete, verify:

- [ ] **Pattern Discovery Complete**
  - All files identified via Glob/Grep
  - Related files (imports, tests) found
  - Dependencies mapped

- [ ] **Token Efficiency Achieved**
  - All files with 2+ edits used MultiEdit
  - No sequential Edit operations on same file
  - Changes grouped optimally

- [ ] **Changes Applied Correctly**
  - All target occurrences updated
  - No false positives modified
  - Context preserved (not broken)

- [ ] **Imports & References Updated**
  - Import statements fixed
  - Cross-references updated
  - No dangling references

- [ ] **Tests Pass**
  - All existing tests pass
  - Test names/fixtures updated if needed
  - No new test failures introduced

- [ ] **Quality Gates Pass**
  - Linting passes
  - Type checking passes (if applicable)
  - Code formatting correct
  - No new warnings

- [ ] **No Missed Occurrences**
  - Grep for old pattern returns empty
  - Manual spot check of key files
  - Edge cases handled

- [ ] **Documentation Updated**
  - Code comments updated
  - API docs reflect changes (if applicable)
  - README/CHANGELOG noted (if significant)

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Sequential Edit on Same File

```
Edit(file.py, old1, new1)
Edit(file.py, old2, new2)  ← Wasteful!

Why bad: 2x tool calls, 2x file reads, excessive tokens
Fix: Use MultiEdit([edit1, edit2])
```

### ❌ Anti-Pattern 2: Blind Editing Without Reading

```
Grep finds pattern in 10 files
→ Immediately Edit all 10 files

Why bad: May edit wrong contexts, miss edge cases
Fix: Read files first to understand context
```

### ❌ Anti-Pattern 3: Skipping Tests

```
Apply refactor changes
Report "done" without running tests

Why bad: May have broken code, false success
Fix: Always run tests, required for completion
```

### ❌ Anti-Pattern 4: Ignoring Quality Gates

```
Tests pass, but linting/type checking fails
Report success anyway

Why bad: Violates code quality standards
Fix: Run full quality gate suite, fix all issues
```

### ❌ Anti-Pattern 5: Forgetting Imports

```
Rename function in module
Update all call sites
Forget to update import statements

Why bad: Code won't run, import errors
Fix: Explicitly check and update imports
```

### ❌ Anti-Pattern 6: Incomplete Refactoring

```
Update 8/10 occurrences
Stop because "most are done"

Why bad: Inconsistent codebase, bugs
Fix: Update ALL occurrences, validate with Grep
```

### ❌ Anti-Pattern 7: Wrong Dependency Order

```
Update test files first
Then update source code
Tests fail because source not updated yet

Why bad: Unnecessary test failures, confusion
Fix: Update in order: source → usages → tests
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Token Efficiency** | 30-50% savings vs sequential Edit | Token usage logs |
| **MultiEdit Usage** | 100% for files with 2+ edits | Operation audit |
| **Test Pass Rate** | 100% after refactor | Test runner output |
| **Quality Gate Pass** | 100% (all gates pass) | Quality scripts |
| **Missed Occurrences** | 0 (all updated) | Post-refactor Grep |
| **Import Errors** | 0 (all fixed) | Import validation |
| **Refactor Completion Time** | <10min for typical refactor | Duration tracking |

## Expected Benefits

| Benefit | Impact | Evidence |
|---------|--------|----------|
| **Token Savings** | High (30-50%) | Reduced tool calls, single file reads |
| **Consistency** | High | Systematic approach ensures all updated |
| **Quality** | High | Mandatory tests + quality gates |
| **Safety** | High | Read-before-edit prevents blind changes |
| **Completeness** | High | Validation checklist ensures nothing missed |
| **Speed** | Medium | Batching and MultiEdit reduce latency |

## Supporting Files

- [refactoring-patterns.md](./references/refactoring-patterns.md) - Detailed pattern recipes
- [language-guides.md](./references/language-guides.md) - Language-specific refactoring guides
- [quality-gates.md](./references/quality-gates.md) - Quality gate reference by language
- [troubleshooting.md](./references/troubleshooting.md) - Common issues and solutions

## Usage Examples

### Example 1: Function Rename (Python)

**User:** "Rename `calculate_sum` to `compute_total` across the codebase"

**Skill execution:**
```
1. Discovery
   Glob: "**/*.py"
   Grep: "calculate_sum" → finds 15 occurrences in 6 files

2. Analysis
   Read: file1.py (definition + 2 usages)
   Read: file2.py (3 usages)
   Read: file3.py (1 usage)
   Read: test_file1.py (5 usages in tests)
   Read: file4.py (2 import statements)
   Read: file5.py (1 import + 1 usage)

3. Execution Plan
   file1.py: 3 edits → MultiEdit
   file2.py: 3 edits → MultiEdit
   file3.py: 1 edit → Edit
   test_file1.py: 5 edits → MultiEdit
   file4.py: 2 edits → MultiEdit
   file5.py: 2 edits → MultiEdit

4. Apply Changes (in dependency order)
   MultiEdit(file1.py, [def_edit, usage1_edit, usage2_edit])
   MultiEdit(file2.py, [usage1, usage2, usage3])
   Edit(file3.py, usage1)
   MultiEdit(file4.py, [import1, import2])
   MultiEdit(file5.py, [import1, usage1])
   MultiEdit(test_file1.py, [test1...test5])

5. Validation
   bash: "pytest tests/ -v" → ✅ 45/45 pass
   bash: "pyright src/" → ✅ 0 errors
   Grep: "calculate_sum" → 0 results ✅

6. Report
   Files Modified: 6
   Occurrences Updated: 15
   Token Efficiency: 40% savings (MultiEdit used 5/6 files)
   Tests: ✅ All pass
   Quality: ✅ Type check pass
   Completeness: ✅ No missed occurrences
```

### Example 2: Class Rename (JavaScript)

**User:** "Rename `DataProcessor` class to `DataTransformer`"

**Skill execution:**
```
1. Discovery
   Glob: "**/*.{js,ts}"
   Grep: "DataProcessor" → 8 files

2. Read & Plan
   src/processor.js: class definition + export
   src/index.js: import + usage
   src/handlers/*.js: 3 files with imports + usages
   test/*.spec.js: 3 test files

3. Apply Changes
   Edit(src/processor.js, "class DataProcessor", "class DataTransformer")
   MultiEdit(src/index.js, [import_edit, usage_edit])
   MultiEdit for each handler file
   MultiEdit for each test file

4. Validation
   bash: "npm run test" → ✅ pass
   bash: "npm run lint" → ✅ pass
   Grep: "DataProcessor" → 0 results ✅

5. Report
   Refactor complete, 8 files updated, tests pass
```

### Example 3: Extract Common Utility (Python)

**User:** "Extract duplicate validation logic to shared utility"

**Skill execution:**
```
1. Identify Duplicates
   Grep: "def validate_email" → 4 identical functions in 4 files

2. Create Utility
   Write: src/utils/validators.py with centralized validate_email()

3. Update Files (each has 2 changes: remove duplicate + add import)
   MultiEdit(file1.py, [remove_function, add_import])
   MultiEdit(file2.py, [remove_function, add_import])
   MultiEdit(file3.py, [remove_function, add_import])
   MultiEdit(file4.py, [remove_function, add_import])

4. Validation
   bash: "pytest tests/" → ✅ pass
   bash: "pyright src/" → ✅ pass

5. Report
   Extracted validation to utils/validators.py
   Removed 4 duplicate functions
   Added imports in 4 files
   Token efficiency: 50% savings (4 MultiEdit vs 8 Edit)
```

## Integration Points

### With Quality Gate Systems

If project has quality gate scripts:
```bash
# Use project-specific validation
bash: "./scripts/check_all.sh"

# Or individual gates
bash: "./scripts/lint.sh"
bash: "./scripts/test.sh"
bash: "./scripts/typecheck.sh"
```

### With CI/CD Pipelines

Skill ensures changes will pass CI:
- Run same checks locally that CI runs
- Fix issues before committing
- Reduces failed CI builds

### With Version Control

After successful refactor:
- Changes ready to commit
- All tests pass
- Quality gates pass
- Safe to create PR

### With Agent Orchestration

Other agents can use this skill:
- @implementer: Delegate multi-file refactors
- @code-review-expert: Suggest refactors, invoke skill
- @architecture-guardian: Enforce patterns, use skill

## Requirements

### File System Access
- Read permissions for source files
- Write permissions for editing files
- Execute permissions for test/quality scripts

### Tool Access
- **Read**: Read files before editing
- **MultiEdit**: Token-efficient multi-edit operations
- **Grep**: Pattern discovery
- **Glob**: File discovery
- **Bash**: Run tests and quality gates

### Language/Framework Tools
- Test runner (pytest, npm test, mvn test, etc.)
- Linter (ruff, eslint, golangci-lint, etc.)
- Type checker (pyright, tsc, javac, etc.)

### Project Structure
- Identifiable test directory (tests/, __tests__, etc.)
- Quality gate scripts (optional but recommended)
- Standard project layout for language

## Invocation Triggers

**Direct user commands:**
- "Refactor [pattern] across [scope]"
- "Rename [old] to [new] everywhere"
- "Update all usages of [X]"
- "Extract common code from [files]"
- "Move [functionality] to [location]"

**Contextual detection:**
- Search returns 2+ files with same pattern → Suggest refactor
- Code review identifies duplication → Invoke skill
- Architecture change requires multi-file updates → Use skill

**Agent delegation:**
- @implementer encounters multi-file work → Delegate to skill
- @code-review-expert suggests refactor → Invoke skill
- @architecture-guardian enforces pattern → Use skill

---

**Skill Version:** 1.0.0
**Last Updated:** 2025-10-16
**Compatibility:** Language-agnostic (Python, JavaScript, Java, Go, etc.)
**Maintenance:** Review quarterly for new patterns and optimizations
