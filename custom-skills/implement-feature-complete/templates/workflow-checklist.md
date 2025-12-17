# Feature Implementation Workflow Checklist

**Feature:** [Feature Name Here]
**Date Started:** [YYYY-MM-DD]
**Estimated Time:** [X hours]

---

## Stage 1: Planning & Location (5-10 minutes)

### Identify Layer
- [ ] Determine which layer: Domain / Application / Infrastructure / Interface
- [ ] Identify pattern: Command / Query / Repository / Value Object
- [ ] List dependencies needed
- [ ] Check if dependencies exist in DI container

**Notes:**
```
Layer: _______________________
Pattern: _____________________
Dependencies:
  -
  -
```

---

## Stage 2: TDD - Red (Write Failing Test) (10-15 minutes)

### Review Current Tests
- [ ] Find similar test files: `ls tests/unit/<layer>/`
- [ ] Read test patterns from similar features
- [ ] Note common fixtures and setup patterns

### Create Test File
- [ ] Create test file: `tests/unit/<layer>/<feature>.py`
- [ ] Write constructor validation tests (fail-fast)
- [ ] Write business logic tests (mocked dependencies)
- [ ] Use pytest fixtures for setup
- [ ] Follow async patterns (if needed)

### Run Test
- [ ] Run: `uv run pytest tests/unit/<layer>/<feature>.py -v`
- [ ] Verify test FAILS with clear error message ✅ RED

**Test File Location:**
```
tests/unit/___________________________
```

---

## Stage 3: Consistent Naming (5 minutes)

### Search Existing Patterns
- [ ] Search queries: `search_code("class.*Query:", search_type="pattern")`
- [ ] Search handlers: `search_code("class.*Handler:", search_type="pattern")`
- [ ] Search repositories: `search_code("class.*Repository:", search_type="pattern")`

### Apply Conventions
- [ ] Class names follow project conventions
- [ ] Method names use snake_case
- [ ] File names match class names (snake_case)
- [ ] Names consistent with similar features

**Naming Decisions:**
```
Query Class: _______________________
Handler Class: _____________________
Repository Method: _________________
File Name: _________________________
```

---

## Stage 4: Extract Common (DRY Principle) (10 minutes)

### Search for Duplication
- [ ] Search for similar logic: `search_code("<pattern>", search_type="semantic")`
- [ ] Check if normalization/validation already exists
- [ ] Identify reusable patterns

### Create Reusable Components
- [ ] Create value object (if validation logic): `domain/values/<name>.py`
- [ ] Create utility function (if pure function): `application/utils/<name>.py`
- [ ] Write tests for reusable components
- [ ] Document with docstrings

**Reusable Components Created:**
```
Value Objects:
  -
Utilities:
  -
```

---

## Stage 5: Implementation - Green (Make Test Pass) (20-30 minutes)

### Create Classes
- [ ] Create query/command class (if CQRS)
- [ ] Create handler class with DI
- [ ] Add repository method to protocol
- [ ] Implement repository method
- [ ] Use value objects for validation
- [ ] Return ServiceResult (not bare None/exceptions)

### Wire to DI Container
- [ ] Register handler in container: `infrastructure/container.py`
- [ ] Inject dependencies via lambda
- [ ] Verify all dependencies resolved

### Run Tests
- [ ] Run: `uv run pytest tests/unit/<layer>/<feature>.py -v`
- [ ] Verify all tests PASS ✅ GREEN

**Implementation Files:**
```
Query/Command: ____________________
Handler: __________________________
Repository: _______________________
```

---

## Stage 6: Refactor - Clean (Quality Gates) (10-15 minutes)

### Run Quality Gates
- [ ] Run: `./scripts/check_all.sh`
- [ ] Fix type errors (pyright)
- [ ] Fix linting errors (ruff)
- [ ] Fix dead code (vulture)
- [ ] Ensure all tests still pass

### Code Quality
- [ ] Extract magic values to config/constants
- [ ] Add comprehensive docstrings
- [ ] Ensure constructor validation (fail-fast)
- [ ] Verify ServiceResult pattern usage
- [ ] Check for code duplication

### Re-run Quality Gates
- [ ] `./scripts/check_all.sh` - ALL PASS ✅

**Quality Gate Results:**
```
Pyright: _____ errors
Ruff: _______ errors
Vulture: _____ issues
Pytest: ______ passed / ______ failed
```

---

## Stage 7: Integration Testing (Real Dependencies) (15-20 minutes)

### Create Integration Test
- [ ] Create test file: `tests/integration/<layer>/<feature>_integration.py`
- [ ] Use real external dependencies (Neo4j, file system)
- [ ] Create test data fixtures
- [ ] Test with real database connections
- [ ] Mark with `@pytest.mark.integration`

### Run Integration Tests
- [ ] Ensure external dependencies running (Neo4j, etc.)
- [ ] Run: `uv run pytest tests/integration/<layer>/<feature>_integration.py -v -m integration`
- [ ] Verify tests PASS

### Verify Database State
- [ ] Manually verify data in Neo4j Browser (if applicable)
- [ ] Check file system state (if applicable)

**Integration Test File:**
```
tests/integration/___________________
```

---

## Stage 8: E2E Testing (MCP Interface) (15-20 minutes)

### Create MCP Tool (if needed)
- [ ] Create/update MCP tool: `interface/mcp_tools/<tool>.py`
- [ ] Handle ServiceResult → dict conversion
- [ ] Add error handling

### Create E2E Test
- [ ] Create test file: `tests/e2e/test_<feature>_e2e.py`
- [ ] Call MCP tool directly
- [ ] Test with initialized repository
- [ ] Mark with `@pytest.mark.e2e`

### Run E2E Tests
- [ ] Run: `uv run pytest tests/e2e/test_<feature>_e2e.py -v -m e2e`
- [ ] Verify tests PASS

### Verify Logs
- [ ] Check logs: `tail -f logs/project-watch-mcp.log`
- [ ] Verify tool invocation logged
- [ ] Verify query executed
- [ ] Verify results returned
- [ ] Verify no errors

**E2E Test File:**
```
tests/e2e/___________________________
```

---

## Stage 9: Real Usage Validation (Manual Testing) (10-15 minutes)

### Start MCP Server
- [ ] Run: `./run-mcp-server.sh`
- [ ] Verify server starts without errors

### Test in Claude Code
- [ ] Open Claude Code conversation
- [ ] Request feature naturally (e.g., "Search for Python files")
- [ ] Verify Claude invokes correct MCP tool
- [ ] Verify results are accurate
- [ ] Verify response time acceptable

### Monitor Logs
- [ ] Watch logs: `tail -f logs/project-watch-mcp.log`
- [ ] Verify no errors during execution
- [ ] Check query timing (<100ms preferred)

### Test Edge Cases
- [ ] Test with empty/null inputs
- [ ] Test with unusual inputs
- [ ] Test with non-existent data
- [ ] Verify fail-fast behavior

**Edge Cases Tested:**
```
1. _________________________________
2. _________________________________
3. _________________________________
```

---

## Stage 10: Production Monitoring (OTEL + Final Validation) (5-10 minutes)

### Analyze OTEL Traces
- [ ] Run: `python3 .claude/tools/utils/log_analyzer.py logs/project-watch-mcp.log`
- [ ] Verify no errors in traces
- [ ] Check performance metrics (query time)
- [ ] Verify trace context propagation

### Performance Validation
- [ ] Check query timing: < 100ms target
- [ ] Profile Neo4j queries (if applicable)
- [ ] Verify no full table scans
- [ ] Verify indexes used (if applicable)

### Final Quality Gates
- [ ] Run: `./scripts/check_all.sh` - ALL PASS ✅
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] No type errors
- [ ] No linting errors
- [ ] No dead code

### Documentation
- [ ] Docstrings complete
- [ ] API changes documented
- [ ] Breaking changes noted (if any)
- [ ] ADR created (if new pattern introduced)

**Production Readiness:**
```
OTEL Errors: ______________________
Query Time (avg): _________________
Quality Gates: ____________________
Documentation: ____________________
```

---

## Final Checklist

- [ ] All 10 stages completed
- [ ] All tests pass (unit + integration + E2E)
- [ ] All quality gates pass
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Feature validated in real usage
- [ ] Production monitoring verified

**Feature Status:** [ ] PRODUCTION READY ✅

---

## Notes

**Issues Encountered:**
```


```

**Learnings:**
```


```

**Future Improvements:**
```


```

---

**Completed By:** [Your Name]
**Date Completed:** [YYYY-MM-DD]
**Total Time:** [X hours]
