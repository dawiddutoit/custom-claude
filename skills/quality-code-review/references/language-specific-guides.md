# Language-Specific Code Review Guides

Detailed code review guidance for Python, JavaScript, TypeScript, Go, and Rust projects.

## Python Projects

### Detection

- `pyproject.toml`
- `requirements.txt`
- `setup.py`
- `*.py` files

### Quality Gates

```bash
# Type checking
pyright src/
# or
mypy src/

# Linting
ruff check src/
# or
pylint src/

# Dead code detection
vulture src/

# Tests
pytest tests/ -v

# Formatting check
ruff format --check src/
```

### Python-Specific Checklist

**Type Annotations:**
- [ ] All public functions have type hints
- [ ] Return types specified
- [ ] Optional types used correctly (`T | None` not bare `T`)
- [ ] No `Any` types without justification

**Error Handling:**
- [ ] No bare `except:` clauses
- [ ] Specific exception types caught
- [ ] ServiceResult pattern used (if project uses it)
- [ ] No silent failures

**Imports:**
- [ ] All imports at top of file
- [ ] No `try/except ImportError` patterns
- [ ] Absolute imports preferred over relative
- [ ] No circular import issues

**Code Style:**
- [ ] Follows PEP 8
- [ ] Docstrings use Google/NumPy style
- [ ] Max line length respected (88 chars for ruff)

### Python Anti-Patterns

**❌ Mutable Default Arguments:**
```python
# Wrong
def add_item(item, items=[]):
    items.append(item)
    return items

# Correct
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

**❌ Using `is` for Value Comparison:**
```python
# Wrong
if value is True:

# Correct
if value is True:  # Only for singletons
if value:  # For truthiness check
```

---

## JavaScript/TypeScript Projects

### Detection

- `package.json`
- `tsconfig.json`
- `*.js`, `*.ts`, `*.jsx`, `*.tsx` files

### Quality Gates

```bash
# Type checking (TypeScript)
npx tsc --noEmit

# Linting
npx eslint src/

# Tests
npm test
# or
npx jest
npx vitest run

# Formatting check
npx prettier --check src/
```

### JS/TS-Specific Checklist

**TypeScript:**
- [ ] No `any` types without `@ts-expect-error` justification
- [ ] Interfaces defined for public APIs
- [ ] Strict mode enabled
- [ ] No `@ts-ignore` without explanation

**Async/Await:**
- [ ] All promises properly awaited
- [ ] Error handling in async functions
- [ ] No unhandled promise rejections
- [ ] Proper use of `Promise.all()` for parallel ops

**React (if applicable):**
- [ ] Hooks rules followed
- [ ] No missing dependencies in `useEffect`
- [ ] Proper key props in lists
- [ ] Error boundaries for error handling

### JS/TS Anti-Patterns

**❌ Unhandled Promise Rejection:**
```javascript
// Wrong
async function fetchData() {
    const data = await fetch(url);
    // No error handling
}

// Correct
async function fetchData() {
    try {
        const data = await fetch(url);
        return data;
    } catch (error) {
        console.error("Failed to fetch:", error);
        throw error;
    }
}
```

**❌ Bare `any` Types:**
```typescript
// Wrong
function process(data: any) {
    return data.value;
}

// Correct
interface DataType {
    value: string;
}
function process(data: DataType) {
    return data.value;
}
```

---

## Go Projects

### Detection

- `go.mod`
- `*.go` files

### Quality Gates

```bash
# Build
go build ./...

# Tests
go test ./... -v

# Linting
golangci-lint run

# Vet (static analysis)
go vet ./...

# Formatting check
test -z $(gofmt -l .)
```

### Go-Specific Checklist

**Error Handling:**
- [ ] All errors checked (no ignored errors)
- [ ] Errors wrapped with context
- [ ] No panic in library code
- [ ] Proper error types defined

**Concurrency:**
- [ ] Goroutines have clear lifecycle
- [ ] Channels properly closed
- [ ] No race conditions
- [ ] WaitGroups used correctly

**Resource Management:**
- [ ] `defer` used for cleanup
- [ ] Files/connections closed
- [ ] Context cancellation handled
- [ ] No goroutine leaks

### Go Anti-Patterns

**❌ Ignoring Errors:**
```go
// Wrong
data, _ := os.ReadFile("file.txt")

// Correct
data, err := os.ReadFile("file.txt")
if err != nil {
    return fmt.Errorf("failed to read file: %w", err)
}
```

**❌ Not Using defer for Cleanup:**
```go
// Wrong
file, err := os.Open("file.txt")
// ... use file ...
file.Close()

// Correct
file, err := os.Open("file.txt")
if err != nil {
    return err
}
defer file.Close()
// ... use file ...
```

---

## Rust Projects

### Detection

- `Cargo.toml`
- `*.rs` files

### Quality Gates

```bash
# Check
cargo check

# Tests
cargo test

# Linting
cargo clippy -- -D warnings

# Formatting check
cargo fmt -- --check

# Build
cargo build --release
```

### Rust-Specific Checklist

**Ownership & Borrowing:**
- [ ] No unnecessary clones
- [ ] Proper lifetime annotations
- [ ] Borrowing rules followed
- [ ] No unsafe without justification

**Error Handling:**
- [ ] `Result` types used properly
- [ ] No `.unwrap()` without panic justification
- [ ] `?` operator used for propagation
- [ ] Custom error types defined

**Safety:**
- [ ] `unsafe` blocks minimal and documented
- [ ] FFI properly wrapped
- [ ] Raw pointers justified
- [ ] Memory safety guaranteed

### Rust Anti-Patterns

**❌ Unwrap Without Context:**
```rust
// Wrong
let value = some_option.unwrap();

// Correct
let value = some_option.expect("Value must exist at this point because X");
// or
let value = some_option.ok_or_else(|| Error::MissingValue)?;
```

**❌ Unnecessary Clone:**
```rust
// Wrong
fn process(data: &String) {
    let owned = data.clone();
    // ... use owned ...
}

// Correct
fn process(data: &str) {
    // ... use data directly ...
}
```

---

## Common Patterns Across Languages

### Magic Numbers
All languages: Extract to constants or config

### Code Duplication
All languages: DRY principle - extract common code

### Long Functions
All languages: Break down into smaller, focused functions

### Deep Nesting
All languages: Use early returns, guard clauses

### Commented Code
All languages: Remove (use version control)

### TODO Comments
All languages: Create issues, reference in comment

### Inconsistent Naming
All languages: Follow language conventions

### Missing Tests
All languages: Tests required for new code
