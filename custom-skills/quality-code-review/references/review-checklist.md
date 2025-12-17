# Complete Code Review Checklist

**Quick reference for systematic code review. Copy-paste sections as needed.**

---

## 🏗️ Architecture Review

### Layer Boundaries (Clean Architecture)
- [ ] Domain has no external dependencies
- [ ] Application doesn't import from interfaces
- [ ] Infrastructure implements repository interfaces
- [ ] Interfaces depend only on application layer
- [ ] Dependencies flow inward (Domain ← Application ← Infrastructure ← Interface)

### Single Responsibility Principle
- [ ] Each method does ONE thing
- [ ] No methods with "and" in name
- [ ] Classes have single, well-defined purpose
- [ ] Separation of concerns maintained
- [ ] Proper decomposition of complex logic

### Design Patterns
- [ ] ServiceResult pattern used for error handling (if applicable)
- [ ] Repository pattern used for data access
- [ ] Dependency injection used throughout
- [ ] Configuration injected (never defaulted)
- [ ] Factory pattern for complex object creation

### Dependencies
- [ ] No circular dependencies
- [ ] Minimal coupling between modules
- [ ] Clear abstraction boundaries
- [ ] Proper use of interfaces/protocols

---

## 📝 Code Quality Review

### Style & Clarity

**Naming:**
- [ ] Variables are descriptive (no `temp`, `data`, `x`, `foo`)
- [ ] Functions describe behavior (verbs: `calculate`, `validate`, `process`)
- [ ] Classes describe entities (nouns: `User`, `Repository`, `Service`)
- [ ] Constants use UPPER_SNAKE_CASE
- [ ] Boolean variables start with `is_`, `has_`, `can_`, `should_`
- [ ] Private members prefixed appropriately (`_private` in Python)

**Magic Numbers:**
- [ ] No hardcoded values without explanation
- [ ] Configuration values in settings/config
- [ ] Clear constants for threshold values
- [ ] Documented reasoning for unavoidable literals

**Code Cleanliness:**
- [ ] No commented-out code
- [ ] No TODOs without issue references (JIRA, GitHub)
- [ ] No dead/unused code
- [ ] Consistent formatting (use formatter)
- [ ] No trailing whitespace
- [ ] Proper line length (<88 Python, <80 others)

### Logic & Correctness

**Error Handling:**
- [ ] Fail fast principle followed
- [ ] No silent failures (`except: pass`)
- [ ] No bare `try/except` or `catch` blocks
- [ ] Specific exception types caught
- [ ] Error messages descriptive and actionable
- [ ] ServiceResult pattern used (Python projects)
- [ ] Errors logged with context (trace IDs, request IDs)

**Null/None Safety:**
- [ ] No unchecked nullable values
- [ ] Optional types properly handled
- [ ] Guard clauses for None checks
- [ ] Type annotations accurate
- [ ] Default values appropriate (or absent)

**Edge Cases:**
- [ ] Empty collections handled (`[]`, `{}`, `null`)
- [ ] Zero values handled
- [ ] Negative values handled
- [ ] Boundary conditions tested (min, max, off-by-one)
- [ ] Division by zero prevented
- [ ] Overflow/underflow considered

**Control Flow:**
- [ ] No deeply nested conditionals (>3 levels)
- [ ] Early returns used to reduce nesting
- [ ] Switch/match statements exhaustive
- [ ] Loop exit conditions clear
- [ ] No infinite loops without break conditions

### Performance

**Efficiency:**
- [ ] No N+1 query patterns
- [ ] Efficient algorithms (avoid O(n²) when O(n log n) possible)
- [ ] Proper use of data structures (hash maps vs arrays)
- [ ] No repeated expensive operations in loops
- [ ] Caching used for expensive computations
- [ ] Pagination used for large datasets

**Resource Management:**
- [ ] Files closed properly (use context managers)
- [ ] Database connections closed/returned to pool
- [ ] Network connections cleaned up
- [ ] Memory leaks prevented (no circular references)
- [ ] Large objects released when done
- [ ] Streams properly consumed/closed

**Concurrency:**
- [ ] Thread safety considered
- [ ] Race conditions prevented
- [ ] Deadlocks prevented
- [ ] Locks released in finally blocks
- [ ] Async operations awaited properly

### Security

**Sensitive Data:**
- [ ] No hardcoded secrets (API keys, passwords)
- [ ] No credentials in code
- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit (HTTPS/TLS)
- [ ] .env files in .gitignore
- [ ] Secrets loaded from environment/vault

**Input Validation:**
- [ ] All user input validated
- [ ] Input sanitized before use
- [ ] Type checking on inputs
- [ ] Range checking (min/max values)
- [ ] Format validation (email, phone, etc.)

**Injection Prevention:**
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (escaped output)
- [ ] Command injection prevented (no shell=True)
- [ ] Path traversal prevented (validated paths)
- [ ] LDAP injection prevented

**Authentication/Authorization:**
- [ ] Auth checks present where needed
- [ ] Proper permission validation
- [ ] Session management secure
- [ ] JWT tokens validated
- [ ] CSRF protection enabled
- [ ] Rate limiting applied

---

## 🧪 Test Coverage Review

### Test Presence
- [ ] New functionality has tests
- [ ] Modified code has updated tests
- [ ] Bug fixes have regression tests
- [ ] Edge cases covered in tests
- [ ] Error paths tested
- [ ] Integration tests for workflows

### Test Quality
- [ ] Tests are independent (no shared state)
- [ ] Tests use proper mocking (no external dependencies)
- [ ] Test names describe behavior (`test_returns_error_when_user_not_found`)
- [ ] Tests are deterministic (no flakiness)
- [ ] Tests run fast (<1s per test ideally)
- [ ] Setup/teardown properly isolated

### Test Coverage
- [ ] New code has >80% coverage
- [ ] Critical paths have 100% coverage
- [ ] Happy paths tested
- [ ] Sad paths tested (errors, exceptions)
- [ ] Boundary conditions tested

### Test Execution
- [ ] All tests pass
- [ ] No skipped tests without reason
- [ ] No disabled tests without issue references
- [ ] Tests run in CI/CD pipeline
- [ ] Test failures block deployment

---

## 📚 Documentation Review

### Code Documentation

**Public APIs:**
- [ ] Functions/methods have docstrings/JSDoc
- [ ] Parameters documented with types
- [ ] Return values documented
- [ ] Exceptions/errors documented
- [ ] Examples provided for complex APIs

**Complex Logic:**
- [ ] WHY comments present (explain reasoning)
- [ ] Algorithm choices justified
- [ ] Non-obvious behavior explained
- [ ] Performance trade-offs documented
- [ ] No WHAT comments (code should be self-documenting)

**Types:**
- [ ] Type annotations complete (Python, TypeScript)
- [ ] Generic types properly constrained
- [ ] Union types explained
- [ ] Optional types justified

### High-Level Documentation

**README:**
- [ ] Updated if public API changed
- [ ] Installation instructions current
- [ ] Usage examples accurate
- [ ] Dependencies listed

**CHANGELOG:**
- [ ] Notable changes documented
- [ ] Breaking changes highlighted
- [ ] Migration guide for breaking changes

**ADR (Architecture Decision Records):**
- [ ] Created for architectural decisions
- [ ] Context explained (why decision needed)
- [ ] Alternatives considered
- [ ] Consequences documented

---

## 🚫 Anti-Pattern Detection

### Universal Anti-Patterns

**Optional Config Parameters:**
```python
# ❌ WRONG
def __init__(self, config: Config | None = None):
    if not config:
        config = Config()  # Creating default

# ✅ CORRECT
def __init__(self, config: Config):
    if not config:
        raise ValueError("Config required")
    self.config = config
```

**try/except ImportError:**
```python
# ❌ WRONG (optional dependencies)
try:
    import optional_library
    AVAILABLE = True
except ImportError:
    AVAILABLE = False
    optional_library = None

# ✅ CORRECT (fail fast)
import optional_library  # Fails immediately if missing
```

**Single Responsibility Violations:**
```python
# ❌ WRONG (does multiple things)
def validate_and_save_user(user_data: dict):
    # Validation
    if not user_data.get("email"):
        raise ValueError("Email required")
    # Saving
    db.save(user_data)

# ✅ CORRECT (split responsibilities)
def validate_user(user_data: dict) -> bool:
    return bool(user_data.get("email"))

def save_user(user_data: dict) -> ServiceResult[User]:
    if not validate_user(user_data):
        return ServiceResult.failure("Invalid user")
    return db.save(user_data)
```

**Returning None on Error:**
```python
# ❌ WRONG (silent failure)
def get_user(id: int) -> User | None:
    try:
        return fetch_user(id)
    except:
        return None  # Lost error context

# ✅ CORRECT (ServiceResult pattern)
def get_user(id: int) -> ServiceResult[User]:
    try:
        user = fetch_user(id)
        return ServiceResult.success(user)
    except Exception as e:
        return ServiceResult.failure(f"Failed to fetch user: {e}")
```

**Sequential Edit Operations:**
```python
# ❌ WRONG (30-50% more tokens)
Edit("file.py", old1, new1)
Edit("file.py", old2, new2)
Edit("file.py", old3, new3)

# ✅ CORRECT (use MultiEdit)
MultiEdit("file.py", [
    {"old_string": old1, "new_string": new1},
    {"old_string": old2, "new_string": new2},
    {"old_string": old3, "new_string": new3}
])
```

### Project-Specific Anti-Patterns

**Read from CLAUDE.md:**
- Red Flags section
- Common Fixes section
- Anti-Pattern Enforcement section

**Detection commands:**
```bash
# Optional config parameters
grep -rn "def.*config.*Optional\|config.*None.*=" src/

# try/except ImportError
grep -rn "try:.*import" src/ -A 3 | grep "except ImportError"

# Methods with "and" (SRP violation)
grep -rn "def.*_and_.*\|function.*And" src/

# Returning None on error
grep -rn "except.*:.*return None" src/
```

---

## ✅ Quality Gates

### Python Projects
- [ ] `pyright` - Type checking passes
- [ ] `ruff check` - Linting passes
- [ ] `vulture` - No dead code detected
- [ ] `pytest` - All tests pass
- [ ] `ruff format --check` - Formatting correct
- [ ] Coverage >80% on new code

### JavaScript/TypeScript Projects
- [ ] `tsc --noEmit` - Type checking passes
- [ ] `eslint` - Linting passes
- [ ] `npm test` - All tests pass
- [ ] `prettier --check` - Formatting correct
- [ ] Coverage >80% on new code

### Go Projects
- [ ] `go build ./...` - Compilation succeeds
- [ ] `golangci-lint run` - Linting passes
- [ ] `go test ./...` - All tests pass
- [ ] `go fmt` - Formatting correct
- [ ] `go vet` - Static analysis passes

### Rust Projects
- [ ] `cargo check` - Compilation succeeds
- [ ] `cargo clippy` - Linting passes
- [ ] `cargo test` - All tests pass
- [ ] `cargo fmt --check` - Formatting correct

---

## 📊 Final Checklist

### Before Declaring "Ready to Commit"
- [ ] All architecture checks pass
- [ ] All code quality checks pass
- [ ] All tests pass (100% pass rate)
- [ ] All quality gates pass
- [ ] Documentation complete
- [ ] No anti-patterns detected
- [ ] Security review complete
- [ ] Performance acceptable

### Commit Message Quality
- [ ] Descriptive commit message
- [ ] Follows conventional commits format
- [ ] References issue/ticket if applicable
- [ ] Explains WHY (not just WHAT)

### Pull Request Readiness (if applicable)
- [ ] PR description complete
- [ ] Screenshots/demos added (UI changes)
- [ ] Breaking changes documented
- [ ] Migration guide included
- [ ] Reviewers assigned

---

## 🎯 Checklist Usage Guide

**How to use this checklist:**

1. **Copy relevant sections** - Not all sections apply to every change
2. **Focus on modified code** - Don't review unchanged files
3. **Prioritize critical checks** - Architecture, security, tests first
4. **Document skipped checks** - Explain why if checklist item doesn't apply
5. **Iterate until clean** - Fix issues, re-check, repeat

**Prioritization:**

- **CRITICAL (must fix):** Architecture violations, security issues, failing tests
- **HIGH (should fix):** Anti-patterns, missing tests, type errors
- **MEDIUM (recommended):** Documentation gaps, performance issues, warnings
- **LOW (nice to have):** Style consistency, minor refactoring

**Time estimates:**

- Small change (1-2 files): 2-5 minutes
- Medium change (3-10 files): 10-20 minutes
- Large change (10+ files): 30-60 minutes

**Red flags (stop and escalate):**

- Cannot understand code logic
- Tests failing with unclear reasons
- Security concerns unclear
- Performance implications unknown
- Breaking changes without migration plan

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0
