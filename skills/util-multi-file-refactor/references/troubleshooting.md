# Multi-File Refactor Troubleshooting Guide

Common issues and solutions when performing multi-file refactoring.

---

## Issue 1: MultiEdit Reports "old_string Not Found"

### Symptoms
```
Error: old_string not found in file.py
```

### Root Causes

1. **Whitespace mismatch** - Tabs vs spaces, trailing spaces
2. **Line ending differences** - CRLF vs LF
3. **String doesn't exist** - Typo in old_string or file changed
4. **String not unique** - Identical strings elsewhere confuse matching

### Solutions

#### Solution 1: Read File First to Get Exact String
```bash
# ALWAYS read file before editing
Read: "src/module.py"

# Copy exact string including whitespace, line breaks
old_string = """    def process(self):
        return data"""

# Use exact copy in MultiEdit
```

#### Solution 2: Include More Context to Make Unique
```python
# ❌ Too vague (may not be unique)
old_string = "return data"

# ✅ Include surrounding context
old_string = """    def process(self):
        return data
"""
```

#### Solution 3: Check Whitespace with Hex View
```bash
# If still failing, check exact whitespace
bash: "cat -A file.py | grep -A2 'process'"
# Shows: ^I for tabs, $ for line ends, spaces as-is
```

#### Solution 4: Use replace_all for Identical Strings
```python
# If string appears multiple times and all should change
MultiEdit(
  file_path="file.py",
  edits=[
    {
      old_string: "return data",
      new_string: "return processed_data",
      replace_all: true  # Replace all occurrences
    }
  ]
)
```

---

## Issue 2: Tests Fail After Refactor

### Symptoms
```
FAILED tests/test_module.py::test_function
AssertionError: Function 'old_name' not found
```

### Root Causes

1. **Test uses old names** - Test code not updated
2. **Mock uses old import path** - Mock target incorrect
3. **Test fixtures hardcode old values** - Data files not updated
4. **Test helpers not updated** - Utility functions in tests/
5. **Doctest failures** - Doctests in docstrings reference old names

### Solutions

#### Solution 1: Update Test Imports and Usage
```python
# Before
from module import old_function

def test_old_function():
    result = old_function()
    assert result

# After
from module import new_function

def test_new_function():  # ← Update test name too!
    result = new_function()
    assert result
```

#### Solution 2: Fix Mock Paths
```python
# Before
@patch('module.old_function')
def test_something(mock_old):
    ...

# After
@patch('module.new_function')  # ← Update mock target
def test_something(mock_new):  # ← Update parameter name
    ...
```

#### Solution 3: Update Test Fixtures
```yaml
# tests/fixtures/data.yml
# Before
function_name: old_function

# After
function_name: new_function
```

#### Solution 4: Search for Old Names in Test Directory
```bash
# Find all test references to old name
Grep: "old_function" in tests/
→ Update each occurrence

# Don't forget test helpers
Grep: "old_function" in tests/helpers/
Grep: "old_function" in tests/fixtures/
```

#### Solution 5: Check Doctests
```python
def new_function():
    """Process data.

    >>> old_function()  # ← Update doctest!
    'result'
    """
    return "result"

# Should be:
    """Process data.

    >>> new_function()
    'result'
    """
```

---

## Issue 3: Import Errors After Refactor

### Symptoms
```
ImportError: cannot import name 'OldClass' from 'module'
ModuleNotFoundError: No module named 'old_module'
```

### Root Causes

1. **Missed import statement** - Some imports not updated
2. **Circular import created** - Refactor introduced cycle
3. **Module not moved** - File still in old location
4. **`__init__.py` not updated** - Re-exports broken
5. **Dynamic imports not updated** - `importlib`, `__import__`

### Solutions

#### Solution 1: Find All Import Statements
```bash
# Search for ALL import patterns
Grep: "from.*old_module|import.*old_module"
Grep: "from.*import.*OldClass"

# Include dynamic imports
Grep: "importlib.import_module|__import__"

# Check string references
Grep: "\"old_module\"|'old_module'"
```

#### Solution 2: Update `__init__.py` Re-exports
```python
# package/__init__.py
# Before
from .old_module import OldClass
__all__ = ['OldClass']

# After
from .new_module import NewClass
__all__ = ['NewClass']
```

#### Solution 3: Check for Circular Imports
```bash
# If you get circular import error, find the cycle
# Use import graph tool or manually trace imports

# Solution: Extract common interface/base to break cycle
# Create: shared/interface.py
# Both modules import from interface, not each other
```

#### Solution 4: Update Dynamic Imports
```python
# Before
module = importlib.import_module('old.module.path')
OldClass = module.OldClass

# After
module = importlib.import_module('new.module.path')
NewClass = module.NewClass
```

#### Solution 5: Check Python Path and Relative Imports
```python
# If using relative imports, check import level
# Before
from ..old_package import OldClass

# After (if package structure changed)
from ..new_package import NewClass
# Or
from ...parent.new_package import NewClass
```

---

## Issue 4: Type Checking Fails (Python/TypeScript)

### Symptoms
```
error: Name "OldType" is not defined
error: Cannot find name 'OldInterface'
```

### Root Causes

1. **Type annotations not updated** - Function signatures still reference old types
2. **Generic types not updated** - `List[OldType]`, `Promise<OldType>`
3. **Type imports not updated** - `from typing import ...`
4. **Type aliases not updated** - `MyType = OldType`
5. **Protocol/Interface references** - Abstract definitions not updated

### Solutions

#### Solution 1: Find All Type References (Python)
```bash
Grep: "OldType" in src/
→ Check each occurrence:
  - Function signatures: def foo() -> OldType:
  - Type hints: data: OldType
  - Generic types: List[OldType], Optional[OldType]
  - Type aliases: NewAlias = OldType
  - isinstance checks: isinstance(obj, OldType)
```

#### Solution 2: Update Generic Types (Python)
```python
# Before
from typing import List, Optional
def process(data: List[OldType]) -> Optional[OldType]:
    ...

# After
from typing import List, Optional
def process(data: List[NewType]) -> Optional[NewType]:
    ...
```

#### Solution 3: Update Type Imports (TypeScript)
```typescript
// Before
import type { OldType } from './old-module';
import { OldInterface } from './old-module';

// After
import type { NewType } from './new-module';
import { NewInterface } from './new-module';
```

#### Solution 4: Update Generic Types (TypeScript)
```typescript
// Before
Promise<OldType>
Array<OldType>
Record<string, OldType>
Map<string, OldType>

// After
Promise<NewType>
Array<NewType>
Record<string, NewType>
Map<string, NewType>
```

---

## Issue 5: Linting Errors After Refactor

### Symptoms
```
error: Line too long (E501)
error: Unused import (F401)
error: Import order violation (I001)
```

### Root Causes

1. **Import order changed** - New imports in wrong position
2. **Unused imports left behind** - Old imports not removed
3. **Line length exceeded** - New names longer than old
4. **Formatting inconsistent** - Refactor changed whitespace

### Solutions

#### Solution 1: Run Auto-Formatter
```bash
# Python
bash: "black src/"
bash: "isort src/"

# JavaScript/TypeScript
bash: "prettier --write src/"

# Go
bash: "gofmt -w ."
```

#### Solution 2: Remove Unused Imports
```bash
# Python - find unused imports
bash: "vulture src/"
bash: "autoflake --remove-unused-variables --in-place src/**/*.py"

# JavaScript - ESLint fix
bash: "eslint --fix src/"
```

#### Solution 3: Fix Import Order
```bash
# Python
bash: "isort src/ --check-diff"
bash: "isort src/"  # Fix

# Import order convention:
# 1. Standard library
# 2. Third-party packages
# 3. Local application imports
```

#### Solution 4: Fix Line Length
```python
# Before (too long after rename)
result = some_service.very_long_new_function_name_that_exceeds_limit(param1, param2, param3)

# After (break into multiple lines)
result = some_service.very_long_new_function_name_that_exceeds_limit(
    param1, param2, param3
)
```

---

## Issue 6: Git Merge Conflicts (If Refactoring in Branch)

### Symptoms
```
CONFLICT (content): Merge conflict in src/module.py
```

### Root Causes

1. **Main branch modified same files** - Simultaneous changes
2. **Imports in different order** - Both branches added imports
3. **Function moved in main** - Refactor target changed location

### Solutions

#### Solution 1: Rebase Before Refactoring
```bash
# Update your branch with latest main first
bash: "git checkout main && git pull"
bash: "git checkout feature-branch"
bash: "git rebase main"

# Then perform refactor on up-to-date code
```

#### Solution 2: Refactor in Small PRs
```
Instead of one massive refactor PR:
1. PR 1: Move files, update imports
2. PR 2: Rename classes/functions
3. PR 3: Extract common code

Smaller PRs = less conflict risk
```

#### Solution 3: Communicate Refactoring to Team
```
Before starting major refactor:
1. Announce in team chat/channel
2. Request code freeze on affected files
3. Complete refactor quickly
4. Merge ASAP to minimize drift
```

---

## Issue 7: Refactor Incomplete - Missed Occurrences

### Symptoms
```
# Some files still reference old names
Grep: "old_name" → returns results
```

### Root Causes

1. **Grep pattern too narrow** - Missed some usage patterns
2. **Generated code not updated** - Auto-generated files skipped
3. **Comments/docstrings** - Not considered "real" code
4. **Configuration files** - `.json`, `.yaml`, `.xml` not searched
5. **Documentation** - README, docs/ not updated

### Solutions

#### Solution 1: Use Comprehensive Grep Patterns
```bash
# Don't just search for exact name
Grep: "old_name"  # ❌ Too narrow

# Include variations
Grep: "old_name|oldName|OldName|OLD_NAME"

# Include word boundaries
Grep: "\\bold_name\\b"

# Check all file types
Glob: "**/*" (not just code files)
Grep: "old_name" in all files
```

#### Solution 2: Check Configuration Files
```bash
# Search config files explicitly
Grep: "old_name" in "**/*.{json,yaml,yml,toml,ini,xml,cfg}"

# Examples of config that might reference code:
# - package.json (entry points)
# - pyproject.toml (module names)
# - tsconfig.json (paths)
# - .env files (variable names)
```

#### Solution 3: Update Comments and Docstrings
```python
# Before
def new_function():
    """Process data using old_function logic."""  # ← Update!
    # TODO: Refactor old_function call  # ← Update!
    ...

# After
def new_function():
    """Process data using new_function logic."""
    # Logic extracted from previous implementation
    ...
```

#### Solution 4: Update Documentation
```bash
# Search documentation
Grep: "old_name" in "docs/**/*.md"
Grep: "old_name" in "README.md"
Grep: "old_name" in "*.md"

# Update examples in docs
```

#### Solution 5: Check Generated Code
```bash
# If code is generated, regenerate instead of editing
bash: "npm run generate"  # Regenerate code
bash: "make codegen"      # Or whatever your tool is

# Then check if generated code updated
```

---

## Issue 8: Performance Issues with Large Refactors

### Symptoms
```
Refactoring is taking a very long time
Tool timeouts
Out of memory errors
```

### Root Causes

1. **Too many files at once** - Processing 100+ files
2. **Large files** - Individual files with 10k+ lines
3. **Too many edits per file** - 50+ edits in one MultiEdit
4. **Reading files repeatedly** - Not batching reads

### Solutions

#### Solution 1: Batch by Directory
```bash
# Instead of all at once
Refactor: "**/*.py"  # ❌ All 1000 files

# Do by module
Refactor: "src/services/**/*.py"  # First
Refactor: "src/handlers/**/*.py"  # Second
Refactor: "src/models/**/*.py"    # Third
...
```

#### Solution 2: Split Large Files First
```bash
# If file has 10k+ lines, consider splitting before refactor
# Use smaller, focused modules
# Then refactor the smaller files
```

#### Solution 3: Limit Edits per MultiEdit
```python
# If 50+ edits needed in one file
# Split into multiple MultiEdit calls

# First MultiEdit (edits 1-20)
MultiEdit(file, edits[0:20])

# Second MultiEdit (edits 21-40)
MultiEdit(file, edits[21:40])

# Third MultiEdit (edits 41-60)
MultiEdit(file, edits[41:60])
```

#### Solution 4: Batch File Reads
```bash
# Read all files first, plan all edits
Read: file1.py
Read: file2.py
Read: file3.py
...

# Then execute all edits (don't re-read)
MultiEdit: file1.py
MultiEdit: file2.py
MultiEdit: file3.py
```

---

## Issue 9: Refactor Breaks Production Code

### Symptoms
```
Code works locally but fails in production
Integration tests fail
External systems can't connect
```

### Root Causes

1. **API contract changed** - External consumers broken
2. **Database schema mismatch** - ORM model renamed but DB not migrated
3. **Environment-specific config** - Production uses different imports/paths
4. **Serialization format changed** - JSON keys, pickle, etc.

### Solutions

#### Solution 1: Maintain API Compatibility
```python
# Don't break external APIs immediately
# Provide deprecated alias

# new_module.py
def new_function():
    """New implementation."""
    ...

# Keep old function as deprecated wrapper
@deprecated("Use new_function instead")
def old_function():
    """Deprecated. Use new_function."""
    return new_function()
```

#### Solution 2: Database Migrations
```python
# If renaming ORM model
# Step 1: Create migration to rename table
# Step 2: Update model name in code
# Step 3: Deploy both together

# Example (Django)
python manage.py makemigrations --name rename_old_to_new
python manage.py migrate
```

#### Solution 3: Feature Flags
```python
# Use feature flag for gradual rollout
if feature_flag('use_new_function'):
    result = new_function()
else:
    result = old_function()  # Fallback

# Roll out gradually, monitor errors
```

---

## Issue 10: Refactor Causes Security Issues

### Symptoms
```
Authentication broken
Authorization bypassed
Secrets exposed
```

### Root Causes

1. **Decorator removed** - `@login_required`, `@admin_only` lost
2. **Validation skipped** - Input validation function not called
3. **Access control changed** - Method visibility changed (public/private)
4. **Secrets in new location** - Config path changed, secrets not found

### Solutions

#### Solution 1: Check Decorators
```python
# Before
@login_required
@admin_only
def old_function():
    ...

# After - DON'T FORGET DECORATORS!
@login_required
@admin_only
def new_function():
    ...
```

#### Solution 2: Verify Security Tests Pass
```bash
# Run security-specific tests
bash: "pytest tests/security/ -v"
bash: "pytest -m security"  # If using pytest marks

# Check authentication tests
# Check authorization tests
# Check input validation tests
```

#### Solution 3: Review Access Modifiers
```python
# Before
class Service:
    def _private_method(self):  # Private (convention)
        ...

# After - maintain privacy!
class Service:
    def _private_method_new_name(self):  # Still private
        ...
```

---

## Debugging Checklist

When refactor goes wrong, check:

- [ ] **Read files before editing** - Understand context
- [ ] **Exact string matching** - Whitespace, line endings
- [ ] **All import statements** - Including dynamic imports
- [ ] **All file types** - Code, tests, configs, docs
- [ ] **Test files and fixtures** - Often forgotten
- [ ] **Type annotations** - Signatures, generics, aliases
- [ ] **Comments and docstrings** - May reference old names
- [ ] **Configuration files** - JSON, YAML, ENV, etc.
- [ ] **Generated code** - Regenerate, don't edit manually
- [ ] **Security decorators/attributes** - Don't lose these!
- [ ] **Run ALL quality gates** - Tests, linting, type checking
- [ ] **Grep for old names** - Should return 0 results
- [ ] **Check git diff** - Review all changes manually

---

## Prevention Best Practices

1. **Plan before executing** - Map all affected files first
2. **Read all files before editing** - Understand context fully
3. **Use MultiEdit for 2+ changes** - Atomic, efficient
4. **Update tests immediately** - Don't defer test updates
5. **Run tests frequently** - After each file or small batch
6. **Use version control** - Commit working state, easy rollback
7. **Refactor in small steps** - Easier to debug if issues arise
8. **Communicate with team** - Avoid merge conflicts
9. **Use automated tools when available** - IDE refactor tools
10. **Validate completeness** - Grep, type check, test, build

---

## When to Stop and Reconsider

Stop the refactor if:

1. **Tests failing for unclear reasons** - May have broken more than intended
2. **Too many unexpected side effects** - Refactor scope too large
3. **Circular dependencies detected** - Architectural issue
4. **More than 100 files affected** - Consider automated tool or split into phases
5. **Production issues anticipated** - Need feature flag or gradual rollout strategy

Consider:
- Breaking into smaller refactors
- Using automated refactoring tools (IDE features)
- Creating detailed migration plan with rollback strategy
- Pairing with another developer for complex refactors

---

## Getting Help

If stuck:

1. **Run diagnostic commands**
   ```bash
   # Python
   bash: "pyright src/ --verbose"
   bash: "pytest tests/ -v --tb=short"

   # JavaScript
   bash: "tsc --noEmit --verbose"
   bash: "npm test -- --verbose"
   ```

2. **Check logs and error messages** - Read carefully, don't skip
3. **Review git diff** - See exactly what changed
4. **Ask for code review** - Fresh eyes catch issues
5. **Use language-specific refactoring tools** - IDE built-ins
6. **Rollback and try smaller steps** - If totally stuck

Remember: Refactoring should improve code. If it's making things worse, stop and reassess!
