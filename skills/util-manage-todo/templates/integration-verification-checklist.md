# Integration Verification Checklist

**COPY-PASTE THIS FOR ANY FEATURE WORK**

---

## Quick Template (Minimal)

```markdown
## Feature: [Your Feature Name]

### Phase 1: CREATION
- [ ] Create [file/module/class]
- [ ] Unit tests pass
- [ ] Types check (mypy passes)
- [ ] Linting passes (ruff passes)

### Phase 2: CONNECTION
- [ ] Import in [target file]
- [ ] Register/wire in [system location]
- [ ] Verify: `grep -r "import.*[module]" src/`

### Phase 3: VERIFICATION
- [ ] **INTEGRATION TEST**: [Test passes]
- [ ] **EXECUTION PROOF**: [Logs attached]
- [ ] **OUTCOME PROOF**: [Result observed]
- [ ] **FOUR QUESTIONS**: All answered
```

---

## Full Template (Comprehensive)

```markdown
## Feature: [Your Feature Name]

**Date:** YYYY-MM-DD
**ADR:** [ADR-XXX if applicable]
**Memory:** [memory-key if applicable]

### The Four Questions Test

Before marking this complete, I MUST answer:

1. **How do I trigger this?** ___________
2. **What connects it to the system?** ___________
3. **What evidence proves it runs?** ___________
4. **What shows it works correctly?** ___________

### Phase 1: CREATION (Artifacts)

- [ ] Create [file/module/class/function]
  - Location: `[path/to/file.py]`
  - Lines of code: ~[estimated]
- [ ] Unit tests pass (isolated behavior)
  - Test file: `[path/to/test_file.py]`
  - Tests added: [number]
- [ ] Types check: `uv run mypy [path]` passes
- [ ] Linting passes: `uv run ruff check [path]` passes

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Phase 2: CONNECTION (Integration)

- [ ] Import [artifact] in [consumer file]
  - File: `[path/to/consumer.py]`
  - Line: ~[line number]
  - Import statement: `from [module] import [artifact]`
- [ ] Register/instantiate in [system location]
  - Location: `[where it's wired]`
  - Method: [how it's registered/called]
- [ ] Wire to [other components]
  - [Component 1]: [connection details]
  - [Component 2]: [connection details]
- [ ] Verify import exists:
  ```bash
  grep -r "import.*[module]" src/
  # Expected output: [paste actual output when done]
  ```

**Connection Evidence:**
```
[Paste code snippet showing import/registration]
```

### Phase 3: VERIFICATION (Runtime)

- [ ] **INTEGRATION TEST**: [Component] exists in compiled system
  - Test file: `[path/to/integration_test.py]`
  - Test name: `test_[component]_integrated`
  - Command: `uv run pytest [path/to/test.py] -v`
  - Expected: [what the test verifies]

- [ ] **EXECUTION PROOF**: Trigger [entry point], attach logs showing execution
  - Trigger command: `[command to run]`
  - Expected log output:
    ```
    [Paste actual log output showing execution]
    ```

- [ ] **OUTCOME PROOF**: [Expected result] observed
  - Expected behavior: [what should happen]
  - Actual result:
    ```
    [Paste actual output/state/result]
    ```

- [ ] **FOUR QUESTIONS**: All four questions answered with evidence
  - Q1 Answer: [paste answer]
  - Q2 Answer: [paste answer]
  - Q3 Answer: [paste answer]
  - Q4 Answer: [paste answer]

**Verification Summary:**
```
✓ Integration test passes
✓ Runtime execution confirmed
✓ Expected outcome observed
✓ All four questions answered
```

### Final Checklist

Before marking this feature COMPLETE:

- [ ] All Phase 1 tasks checked
- [ ] All Phase 2 tasks checked
- [ ] All Phase 3 tasks checked
- [ ] Evidence pasted for all verification tasks
- [ ] Four questions answered with specific details
- [ ] No "TODO" or "placeholder" code remains
- [ ] Quality gates pass: `uv run pytest && uv run mypy src/ && uv run ruff check .`
```

---

## Specialized Templates

### LangGraph Node Integration

```markdown
## Feature: Add [NodeName] Node to LangGraph

### Phase 1: CREATION
- [ ] Create `coordination/graph/[name]_nodes.py`
- [ ] Implement `create_[name]_node()` factory
- [ ] Implement routing function (if conditional edge)
- [ ] Unit tests pass ([number] tests with mocks)
- [ ] Types check passes
- [ ] Linting passes

### Phase 2: CONNECTION
- [ ] Import in `builder.py` line ~[X]
- [ ] Call factory in builder: `create_[name]_node(agent)`
- [ ] Add to graph: `graph.add_node("[name]", node)`
- [ ] Add edges (conditional or direct)
- [ ] Verify: `grep "[name]_nodes" src/temet_run/coordination/graph/builder.py`

### Phase 3: VERIFICATION
- [ ] **INTEGRATION TEST**: Added "[name]" to `test_graph_completeness.py` EXPECTED_NODES
- [ ] **EXECUTION PROOF**: Coordinator logs show node triggered
- [ ] **OUTCOME PROOF**: `state.[field]` populated correctly
- [ ] **FOUR QUESTIONS**: Answered with coordinator run evidence
```

### CLI Command Addition

```markdown
## Feature: Add `temet-run [command]` Command

### Phase 1: CREATION
- [ ] Create `cli/commands/[command].py`
- [ ] Implement `[command]_command()` function
- [ ] Unit tests for command logic pass
- [ ] Types check passes
- [ ] Linting passes

### Phase 2: CONNECTION
- [ ] Import in `cli/app.py`
- [ ] Register with `@app.command()` or CLI group
- [ ] Verify: `grep "[command]" src/temet_run/cli/app.py`

### Phase 3: VERIFICATION
- [ ] **INTEGRATION TEST**: `uv run temet-run --help | grep [command]` shows command
- [ ] **EXECUTION PROOF**: `uv run temet-run [command] [args]` output attached
- [ ] **OUTCOME PROOF**: Command produces expected result
- [ ] **FOUR QUESTIONS**: CLI help, registration, execution, behavior verified
```

### Service with Dependency Injection

```markdown
## Feature: Add [ServiceName]Service

### Phase 1: CREATION
- [ ] Create `services/[name].py` with [ServiceName]Service class
- [ ] Unit tests with mocks pass
- [ ] Types check passes
- [ ] Linting passes

### Phase 2: CONNECTION
- [ ] Add to DI container in `config/container.py`
- [ ] Inject in consumer classes
- [ ] Verify: `grep "[ServiceName]Service" src/temet_run/config/container.py`

### Phase 3: VERIFICATION
- [ ] **INTEGRATION TEST**: `container.resolve([ServiceName]Service)` succeeds
- [ ] **EXECUTION PROOF**: Daemon logs show service instantiated/called
- [ ] **OUTCOME PROOF**: Service methods execute correctly
- [ ] **FOUR QUESTIONS**: DI resolution, consumer injection, logs, behavior verified
```

### API Endpoint

```markdown
## Feature: Add /api/[endpoint] Endpoint

### Phase 1: CREATION
- [ ] Create `api/routes/[endpoint].py`
- [ ] Implement route handler
- [ ] Request/response models defined
- [ ] Unit tests pass
- [ ] Types check passes
- [ ] Linting passes

### Phase 2: CONNECTION
- [ ] Import in API router
- [ ] Add route: `router.add_route("/[endpoint]", handler)`
- [ ] Verify: `grep "[endpoint]" src/temet_run/api/`

### Phase 3: VERIFICATION
- [ ] **INTEGRATION TEST**: Route registered in OpenAPI schema
- [ ] **EXECUTION PROOF**: `curl http://localhost:8000/api/[endpoint]` response attached
- [ ] **OUTCOME PROOF**: Response matches expected schema
- [ ] **FOUR QUESTIONS**: curl command, router registration, response, schema verified
```

---

## Enforcement Rules

1. **No "Create" Without "Connect"** — Every creation task MUST have corresponding connection tasks
2. **No "Connect" Without "Verify"** — Every connection task MUST have verification tasks
3. **No "Verify" Without Evidence** — Verification tasks MUST include evidence when checked
4. **Phase 3 Blocks Completion** — Feature CANNOT be complete without Phase 3 done with evidence

---

## The Four Questions (Memorize These)

1. **How do I trigger this?** → Entry point
2. **What connects it to the system?** → Import/registration
3. **What evidence proves it runs?** → Logs/traces
4. **What shows it works correctly?** → Output/behavior

**All four MUST be answered before claiming "done"**
