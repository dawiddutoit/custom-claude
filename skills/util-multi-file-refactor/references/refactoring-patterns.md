# Refactoring Patterns

Detailed recipes for common refactoring patterns with multi-file coordination.

## Pattern 1: Function/Method Rename

**Scenario:** Rename a function/method consistently across all usage sites.

### Discovery Phase
```bash
# Find definition
Grep: "def old_function_name\(|function old_function_name"

# Find all usages
Grep: "old_function_name\("

# Find imports
Grep: "from .* import.*old_function_name|import.*old_function_name"
```

### Execution Pattern
1. **Read all affected files** to understand context
2. **Update definition** (Edit if one change)
3. **Update call sites** (MultiEdit if 2+ in same file)
4. **Update imports** (MultiEdit if 2+ in same file)
5. **Update tests** (MultiEdit for test methods and assertions)
6. **Validate** with Grep (should return no results)

### Example
```python
# Before:
def calculate_sum(numbers):
    return sum(numbers)

# After:
def compute_total(numbers):
    return sum(numbers)

# Changes needed:
# - Definition in utils.py (1 edit)
# - 5 call sites in service.py (MultiEdit with 5 edits)
# - 2 imports in handlers.py (MultiEdit with 2 edits)
# - 3 test calls in test_utils.py (MultiEdit with 3 edits)
```

### Token Efficiency
- Sequential Edit: 11 tool calls
- With MultiEdit: 4 tool calls (64% savings)

---

## Pattern 2: Class Rename

**Scenario:** Rename a class and update all instantiations, inheritance, and type hints.

### Discovery Phase
```bash
# Find class definition
Grep: "class OldClassName"

# Find instantiations
Grep: "OldClassName\("

# Find inheritance
Grep: "class.*\(.*OldClassName"

# Find imports
Grep: "from .* import.*OldClassName|import.*OldClassName"

# Find type hints
Grep: ": OldClassName|-> OldClassName|\[OldClassName\]"
```

### Execution Pattern
1. **Read all affected files**
2. **Update class definition** (Edit)
3. **Update instantiations** (MultiEdit per file)
4. **Update inheritance** (MultiEdit if multiple in file)
5. **Update imports** (MultiEdit if multiple)
6. **Update type hints** (MultiEdit if multiple)
7. **Update tests** (MultiEdit for test class name and usages)
8. **Validate** (Grep for old name, run tests)

### Example
```python
# Before:
class DataProcessor:
    def process(self, data):
        ...

# After:
class DataTransformer:
    def process(self, data):
        ...

# Changes across files:
# processor.py: class definition (1 edit)
# service.py: instantiation + type hint (MultiEdit 2)
# handlers.py: 3 instantiations (MultiEdit 3)
# test_processor.py: class name + 5 usages (MultiEdit 6)
```

### Token Efficiency
- Sequential Edit: 13 tool calls
- With MultiEdit: 5 tool calls (62% savings)

---

## Pattern 3: Extract Common Code to Utility

**Scenario:** Remove duplicated code by extracting to shared utility function.

### Discovery Phase
```bash
# Find duplicate pattern
Grep: "def validate_email"  # Example duplicated function

# Count occurrences
# Identify which files have the duplicate
```

### Execution Pattern
1. **Create utility module** (Write new file)
2. **Read all files with duplicates**
3. **For each file:**
   - Remove duplicate function (edit 1)
   - Add import for utility (edit 2)
   - Use MultiEdit to combine both
4. **Update tests** to use new utility
5. **Validate** (tests pass, no duplicates remain)

### Example
```python
# Before (in 4 files):
def validate_email(email):
    return "@" in email and "." in email

# After:
# utils/validators.py (new file):
def validate_email(email):
    return "@" in email and "." in email

# Each file (4 total):
# - Remove duplicate function
# - Add: from utils.validators import validate_email
# Use MultiEdit for both changes per file
```

### Token Efficiency
- Sequential Edit: 9 tool calls (1 Write + 4×2 Edit)
- With MultiEdit: 5 tool calls (1 Write + 4 MultiEdit) (44% savings)

---

## Pattern 4: Module/File Move

**Scenario:** Move functionality from one module to another, updating all imports.

### Discovery Phase
```bash
# Find all imports of old module
Grep: "from old.module import|import old.module"

# Count affected files
```

### Execution Pattern
1. **Read source and destination files**
2. **Move code** (Edit old file to remove, Edit new file to add)
3. **Update all import statements:**
   - For each file with imports (MultiEdit if 2+ imports)
4. **Update `__init__.py`** if needed (Edit or MultiEdit)
5. **Delete old file** if empty (Bash)
6. **Run tests** to validate imports work
7. **Run quality gates** (type checking validates imports)

### Example
```python
# Before:
# old/helpers.py
def helper_a():
    ...
def helper_b():
    ...

# After:
# new/utils.py (moved)
def helper_a():
    ...
def helper_b():
    ...

# Changes:
# 5 files import from old.helpers → update to new.utils
# Each file might have 1-3 import statements
# Use MultiEdit for files with 2+ imports
```

### Token Efficiency
- If 5 files, 2 with multiple imports:
  - Sequential Edit: 7 tool calls
  - With MultiEdit: 5 tool calls (29% savings)

---

## Pattern 5: API Signature Change

**Scenario:** Change function signature (add/remove/rename parameters) across all call sites.

### Discovery Phase
```bash
# Find function definition
Grep: "def function_name\("

# Find all call sites
Grep: "function_name\("

# Read files to understand current usage
```

### Execution Pattern
1. **Update function definition** (Edit)
2. **Read all files with call sites**
3. **Update each call site:**
   - If file has 1 call → Edit
   - If file has 2+ calls → MultiEdit
4. **Update tests:**
   - Test calls (MultiEdit if multiple)
   - Test assertions (MultiEdit if multiple)
5. **Run tests** to validate new signature
6. **Run quality gates** (type checking validates signatures)

### Example
```python
# Before:
def create_user(name, email):
    ...

# After:
def create_user(name, email, role="user"):
    ...

# Changes:
# Definition: 1 edit
# service.py: 3 calls (MultiEdit 3)
# handlers.py: 2 calls (MultiEdit 2)
# admin.py: 1 call (Edit 1)
# test_user.py: 5 test calls (MultiEdit 5)
```

### Token Efficiency
- Sequential Edit: 12 tool calls
- With MultiEdit: 5 tool calls (58% savings)

---

## Pattern 6: Configuration Migration

**Scenario:** Update configuration parameter names/structure throughout codebase.

### Discovery Phase
```bash
# Find all config usages
Grep: "config\.old_param_name|config\[\"old_param_name\"\]"

# Find config definition
```

### Execution Pattern
1. **Update config definition** (Edit or MultiEdit)
2. **Read all files using config**
3. **Update each usage:**
   - Single usage → Edit
   - Multiple usages → MultiEdit
4. **Update tests and fixtures:**
   - Test config objects (MultiEdit)
   - Mock config (MultiEdit)
5. **Update documentation** (Edit)
6. **Run tests** to validate
7. **Grep for old param name** (should be 0 results)

### Example
```python
# Before:
class Config:
    max_retries = 3

# After:
class Config:
    retry_limit = 3

# Changes:
# config.py: definition (1 edit)
# service.py: 4 usages (MultiEdit 4)
# handlers.py: 2 usages (MultiEdit 2)
# test_config.py: 6 test usages (MultiEdit 6)
# docs/config.md: documentation (Edit 1)
```

### Token Efficiency
- Sequential Edit: 14 tool calls
- With MultiEdit: 5 tool calls (64% savings)

---

## Pattern 7: Pattern Adoption (e.g., ServiceResult Migration)

**Scenario:** Migrate from one error handling pattern to another (e.g., None returns → ServiceResult).

### Discovery Phase
```bash
# Find functions returning None on error
Grep: "return None.*#.*error|except.*return None"

# Find all methods in target classes
Grep: "class TargetService"
```

### Execution Pattern
1. **Create ADR** if not exists (architectural decision)
2. **Add REFACTOR markers** to files
3. **For each method:**
   - Update return type annotation (edit 1)
   - Update return statements (edit 2, 3, ...)
   - Use MultiEdit to combine all edits in method
4. **Update call sites:**
   - Check `.success` instead of `is not None`
   - Handle `.failure()` cases
   - MultiEdit if multiple calls in file
5. **Update tests:**
   - Assert on ServiceResult properties
   - MultiEdit for multiple test methods
6. **Remove REFACTOR markers** when complete
7. **Run quality gates** (type checking validates patterns)

### Example
```python
# Before:
def get_user(id: int) -> User | None:
    try:
        return fetch_user(id)
    except:
        return None

# After:
def get_user(id: int) -> ServiceResult[User]:
    try:
        user = fetch_user(id)
        return ServiceResult.success(user)
    except Exception as e:
        return ServiceResult.failure(f"Failed: {e}")

# Changes per method:
# - Return type annotation (1)
# - Success return (1)
# - Failure return (1)
# = MultiEdit with 3 edits per method

# Call sites per file:
# - Change None checks to .success checks
# - MultiEdit if 2+ calls in file
```

### Token Efficiency
- For 5 methods, 10 call sites across 4 files:
  - Sequential Edit: 20 tool calls
  - With MultiEdit: 9 tool calls (55% savings)

---

## General Refactoring Best Practices

### Always Read First
Before any edit, read the file to understand context and plan exact old_string/new_string values.

### Group by File
Count edits needed per file. If 2+, use MultiEdit. If 1, use Edit.

### Validate Immediately
After each phase, use Grep to verify changes or find missed occurrences.

### Run Tests Between Phases
For large refactors, run tests after each major phase (definitions, usages, tests).

### Use Dependency Order
Update core definitions before usages, usages before tests.

### Document with Markers
For multi-session refactors, use REFACTOR markers to track progress.

### Verify Completeness
Final Grep for old pattern should return 0 results.
