# Integration Task Requirements

**CRITICAL: Prevents "done but not integrated" failures**

## Background

ADR-013 was marked complete when code files existed but were never integrated into the system. To prevent this, ALWAYS create separate tasks for file creation and integration.

## The Creation-Connection-Verification (CCV) Principle

A feature is NOT complete until all three phases are done:

| Phase | What It Proves | Required Evidence |
|-------|----------------|-------------------|
| **CREATION** | Artifact exists | File, tests, types, linting |
| **CONNECTION** | Artifact is wired in | Import, registration, configuration |
| **VERIFICATION** | Artifact works at runtime | Logs, output, state changes |

**Missing any phase = Feature incomplete**

## The Four Questions Test

Before claiming "done", you MUST answer ALL FOUR:

1. **How do I trigger this?** (entry point - CLI, API, UI, scheduler)
2. **What connects it to the system?** (import, registration, wiring)
3. **What evidence proves it runs?** (logs, traces, debug output)
4. **What shows it works correctly?** (output, state change, behavior)

If you cannot answer ALL FOUR, the feature is NOT complete.

## Three-Phase Todo Pattern

For any integration feature, todos MUST include:

### Phase 1: CREATION (Artifacts)
- [ ] Create [file/module/class]
- [ ] Unit tests pass (isolated behavior)
- [ ] Types and linting pass

### Phase 2: CONNECTION (Integration)
- [ ] Import [artifact] in [consumer file]
- [ ] Register/instantiate in [system location]
- [ ] Wire to [other components] (edges, routes, etc.)
- [ ] Verify import exists: `grep -r "import.*[module]" src/`

### Phase 3: VERIFICATION (Runtime)
- [ ] **INTEGRATION TEST**: [Component] exists in compiled system
- [ ] **EXECUTION PROOF**: Trigger [entry point], attach logs showing execution
- [ ] **OUTCOME PROOF**: [Expected result] observed
- [ ] **FOUR QUESTIONS**: All four questions answered with evidence

## Enforcement Rules

1. **No "Create" Without "Connect"** — Every creation task MUST have corresponding connection tasks
2. **No "Connect" Without "Verify"** — Every connection task MUST have verification tasks
3. **No "Verify" Without Evidence** — Verification tasks MUST include evidence when checked
4. **Phase 3 Blocks Completion** — Feature CANNOT be complete without Phase 3 done with evidence

## Context-Specific Patterns

### LangGraph Nodes
```markdown
### Phase 2: CONNECTION
- [ ] Import in `builder.py`
- [ ] Add node with `graph.add_node()`
- [ ] Wire edges with `add_conditional_edges()`
- [ ] Verify: `grep "node_name" builder.py`

### Phase 3: VERIFICATION
- [ ] Integration test: node in `graph.nodes`
- [ ] Execution: logs show node triggered
- [ ] Outcome: state field populated
```

### CLI Commands
```markdown
### Phase 2: CONNECTION
- [ ] Import in `cli/app.py`
- [ ] Register with `add_command()`
- [ ] Verify: `uv run temet-run --help` shows command

### Phase 3: VERIFICATION
- [ ] Run command, capture output
- [ ] Verify expected behavior
```

### DI Services
```markdown
### Phase 2: CONNECTION
- [ ] Import in `container.py`
- [ ] Add provider definition
- [ ] Inject into consumer

### Phase 3: VERIFICATION
- [ ] Container resolves service
- [ ] Service methods called at runtime
```

## Using quality-verify-integration Skill

Before marking integration work complete, invoke:

```
Skill: quality-verify-integration
```

This runs:
1. Orphan detection (`verify_integration.sh`)
2. Import verification (grep checks)
3. Call-site verification
4. Four Questions audit

**If skill reports issues → BLOCK COMPLETION**
