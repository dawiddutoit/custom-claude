# Quality Gates by Language

Complete quality gate reference for multi-file refactoring validation across different languages.

## Python

### Required Quality Gates

**1. Type Checking**
```bash
# Pyright (recommended)
uv run pyright src/

# Or Mypy
mypy src/ --strict
```

**What it validates:**
- Type annotations correct
- Return types match signatures
- No type mismatches after refactor
- Generic types properly used

**Common issues after refactor:**
- Changed return type not propagated to callers
- Optional types not handled
- Type annotations on renamed functions missing

---

**2. Linting**
```bash
# Ruff (fast, comprehensive)
uv run ruff check src/

# Or Pylint
pylint src/
```

**What it validates:**
- Code style consistent
- No unused imports after changes
- No undefined variables
- Proper naming conventions

**Common issues after refactor:**
- Unused imports from old module
- Star imports not updated
- Variables renamed but references missed

---

**3. Tests**
```bash
# Pytest
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=src --cov-report=term
```

**What it validates:**
- All functionality still works
- No regressions from refactor
- Edge cases handled
- Test coverage maintained

**Common issues after refactor:**
- Tests use old function names
- Mocks not updated for new signatures
- Assertions check old return types

---

**4. Dead Code Detection**
```bash
# Vulture
uv run vulture src/
```

**What it validates:**
- No unreachable code
- No unused functions after refactor
- Old code fully removed

**Common issues after refactor:**
- Old functions left behind
- Duplicate utilities not removed
- Commented code not cleaned up

---

**5. Import Validation**
```bash
# Check imports resolve
python -c "import sys; sys.path.insert(0, 'src'); import module_name"

# Or use isort to validate
isort src/ --check-only
```

**What it validates:**
- All imports resolve
- No circular imports
- Import order correct

**Common issues after refactor:**
- Circular imports introduced
- Relative imports broken
- Missing `__init__.py` files

---

### Unified Python Quality Gate

**Using check_all.sh:**
```bash
#!/bin/bash
# Run all quality gates in parallel

set -e

echo "Running quality gates..."

# Run in parallel for speed
uv run pyright src/ &
PID1=$!

uv run ruff check src/ &
PID2=$!

uv run vulture src/ &
PID3=$!

uv run pytest tests/ &
PID4=$!

# Wait for all
wait $PID1 || exit 1
wait $PID2 || exit 1
wait $PID3 || exit 1
wait $PID4 || exit 1

echo "✅ All quality gates passed"
```

---

## JavaScript/TypeScript

### Required Quality Gates

**1. Type Checking (TypeScript)**
```bash
# TypeScript compiler
npx tsc --noEmit

# With strict mode
npx tsc --noEmit --strict
```

**What it validates:**
- Type safety maintained
- Interface changes propagated
- Generic types correct
- No `any` leakage

**Common issues after refactor:**
- Type definitions not updated
- Interface changes not propagated
- Generic constraints violated

---

**2. Linting**
```bash
# ESLint
npx eslint src/ --ext .js,.jsx,.ts,.tsx

# With auto-fix (dry run)
npx eslint src/ --ext .js,.ts --fix-dry-run
```

**What it validates:**
- Code style consistent
- Best practices followed
- Potential bugs caught
- React hooks rules (if applicable)

**Common issues after refactor:**
- Unused variables after rename
- Import statements not updated
- React dependencies array outdated

---

**3. Tests**
```bash
# Jest
npx jest

# Vitest
npx vitest run

# With coverage
npx jest --coverage
```

**What it validates:**
- Functionality preserved
- No regressions
- Mocks updated
- Component tests pass (React)

**Common issues after refactor:**
- Snapshot tests fail
- Mock implementations outdated
- Component prop types changed

---

**4. Build Validation**
```bash
# Webpack
npm run build

# Vite
npx vite build

# Next.js
npx next build
```

**What it validates:**
- No build errors
- All imports resolve
- Production build succeeds

**Common issues after refactor:**
- Dynamic imports broken
- Code splitting issues
- Tree shaking assumptions violated

---

### Unified JS/TS Quality Gate

```bash
#!/bin/bash
set -e

echo "Running quality gates..."

# Type checking
echo "1/4 Type checking..."
npx tsc --noEmit

# Linting
echo "2/4 Linting..."
npx eslint src/ --ext .js,.jsx,.ts,.tsx

# Tests
echo "3/4 Running tests..."
npm test

# Build
echo "4/4 Building..."
npm run build

echo "✅ All quality gates passed"
```

---

## Go

### Required Quality Gates

**1. Build**
```bash
# Build all packages
go build ./...

# With race detector
go build -race ./...
```

**What it validates:**
- Code compiles
- No syntax errors
- Dependencies resolve

**Common issues after refactor:**
- Package names changed but not updated
- Import paths incorrect
- Circular dependencies introduced

---

**2. Vet (Static Analysis)**
```bash
# Go vet
go vet ./...
```

**What it validates:**
- Suspicious constructs
- Printf format strings
- Unreachable code
- Shadow variables

**Common issues after refactor:**
- Unused parameters after signature change
- Dead code not removed
- Printf args mismatched

---

**3. Linting**
```bash
# golangci-lint (comprehensive)
golangci-lint run

# With all linters
golangci-lint run --enable-all
```

**What it validates:**
- Code style
- Best practices
- Error handling
- Complexity

**Common issues after refactor:**
- Errors not checked
- Context not propagated
- defer missing for cleanup

---

**4. Tests**
```bash
# Run all tests
go test ./... -v

# With race detector
go test ./... -race

# With coverage
go test ./... -cover -coverprofile=coverage.out
```

**What it validates:**
- Functionality correct
- No race conditions
- Test coverage maintained

**Common issues after refactor:**
- Test helpers not updated
- Table tests missing cases
- Race conditions introduced

---

### Unified Go Quality Gate

```bash
#!/bin/bash
set -e

echo "Running quality gates..."

# Build
echo "1/4 Building..."
go build ./...

# Vet
echo "2/4 Vetting..."
go vet ./...

# Lint
echo "3/4 Linting..."
golangci-lint run

# Test
echo "4/4 Testing..."
go test ./... -race -cover

echo "✅ All quality gates passed"
```

---

## Rust

### Required Quality Gates

**1. Check**
```bash
# Fast compile check
cargo check

# All targets
cargo check --all-targets
```

**What it validates:**
- Code compiles
- Borrowing rules followed
- Lifetimes correct

**Common issues after refactor:**
- Lifetime annotations incorrect
- Ownership transferred incorrectly
- Trait bounds not satisfied

---

**2. Clippy (Linter)**
```bash
# Clippy with warnings as errors
cargo clippy -- -D warnings

# All features
cargo clippy --all-features -- -D warnings
```

**What it validates:**
- Idiomatic Rust
- Performance issues
- Common mistakes

**Common issues after refactor:**
- Unnecessary clones
- Inefficient patterns
- Unsafe usage unjustified

---

**3. Format Check**
```bash
# Check formatting
cargo fmt -- --check
```

**What it validates:**
- Consistent formatting
- Follows rustfmt rules

**Common issues after refactor:**
- Inconsistent formatting from edits
- Long lines from MultiEdit

---

**4. Tests**
```bash
# Run all tests
cargo test

# With doc tests
cargo test --doc

# All features
cargo test --all-features
```

**What it validates:**
- Functionality correct
- Doc examples work
- No panics

**Common issues after refactor:**
- Doc tests outdated
- Integration tests not updated
- Panic messages changed

---

**5. Build**
```bash
# Debug build
cargo build

# Release build
cargo build --release
```

**What it validates:**
- Production build succeeds
- Optimizations don't break code

---

### Unified Rust Quality Gate

```bash
#!/bin/bash
set -e

echo "Running quality gates..."

# Check
echo "1/5 Checking..."
cargo check --all-targets

# Clippy
echo "2/5 Linting..."
cargo clippy --all-features -- -D warnings

# Format
echo "3/5 Formatting..."
cargo fmt -- --check

# Test
echo "4/5 Testing..."
cargo test --all-features

# Build
echo "5/5 Building..."
cargo build --release

echo "✅ All quality gates passed"
```

---

## Cross-Language Best Practices

### Always Run Quality Gates After Refactor

**Why:**
- Catch issues immediately while context is fresh
- Verify refactor didn't break anything
- Ensure code quality maintained

**When:**
- After each refactor phase (definitions, usages, tests)
- Before declaring refactor complete
- Before committing changes

---

### Fail Fast on Quality Gate Failures

**Don't:**
- Continue refactoring if tests fail
- Skip quality gates because "almost done"
- Commit broken code with intent to "fix later"

**Do:**
- Stop immediately on first failure
- Fix the issue
- Re-run all gates
- Only proceed when all pass

---

### Use Project-Specific Gates

**Detect and use:**
```bash
# Project might have unified script
if [ -f ./scripts/check_all.sh ]; then
    ./scripts/check_all.sh
elif [ -f package.json ] && grep -q '"check"' package.json; then
    npm run check
elif [ -f Makefile ] && grep -q 'check:' Makefile; then
    make check
else
    # Fall back to language-specific gates
fi
```

---

### Parallel Execution for Speed

Run independent gates in parallel:
```bash
# Python example
pyright src/ &
PID1=$!
ruff check src/ &
PID2=$!
pytest tests/ &
PID3=$!

wait $PID1 && wait $PID2 && wait $PID3
```

Reduces total time by ~60% on multi-core systems.

---

## Quality Gate Integration with Refactoring

### Before Refactoring
- [ ] Baseline: Run quality gates to ensure starting from clean state
- [ ] All gates pass before starting refactor

### During Refactoring
- [ ] After each major phase (definitions, usages, tests)
- [ ] Run type checking after signature changes
- [ ] Run tests after logic changes

### After Refactoring
- [ ] All gates MUST pass before declaring complete
- [ ] No new warnings introduced
- [ ] Coverage maintained or improved

### Quality Gate Failure = Incomplete Refactor
Never consider a refactor "done" if quality gates fail.
