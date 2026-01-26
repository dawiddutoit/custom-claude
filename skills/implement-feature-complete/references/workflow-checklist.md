# Complete Feature Implementation - Workflow Checklist

Use this checklist to track progress through the 10-stage feature implementation workflow.

## Stage 1: Planning & Location (5-10 min)

- [ ] Identify Clean Architecture layer (domain/application/infrastructure/interface)
- [ ] Locate existing similar features for consistency
- [ ] Plan dependencies and interfaces
- [ ] Identify required tests (unit, integration, E2E)
- [ ] Document architectural placement decisions
- [ ] Define clear exit criteria for this feature

**Exit Criteria:** Clear plan documented, layers identified, test strategy defined

## Stage 2: TDD - Red (Write Failing Test) (10-15 min)

- [ ] Write unit tests for business logic (domain/application)
- [ ] Add constructor validation tests
- [ ] Add edge case tests (empty inputs, invalid states)
- [ ] Add error handling tests (ServiceResult failures)
- [ ] Verify all tests are failing (red state)
- [ ] Coverage plan is complete

**Exit Criteria:** All tests written, all tests failing (red), coverage plan complete

## Stage 3: Consistent Naming (5 min)

- [ ] Review existing code for naming patterns
- [ ] Choose names matching project conventions
- [ ] Verify naming across layers is consistent
- [ ] Update tests with final names

**Exit Criteria:** All names follow project conventions, tests updated

## Stage 4: Extract Common (DRY) (10 min)

- [ ] Identify shared logic or utilities needed
- [ ] Check if similar functionality exists elsewhere
- [ ] Extract to appropriate shared location if needed
- [ ] Avoid premature extraction (wait for 2-3 uses)

**Exit Criteria:** Shared logic centralized, no duplication planned

## Stage 5: Implementation - Green (15-30 min)

- [ ] Write minimum code to make tests pass
- [ ] Use ServiceResult for error handling
- [ ] Inject dependencies (no hard dependencies)
- [ ] Run tests - verify all passing (green state)
- [ ] Verify test coverage is adequate

**Exit Criteria:** All tests passing (green), basic implementation complete

## Stage 6: Refactor - Clean (20-30 min)

- [ ] Run mypy type checking - fix all issues
- [ ] Run ruff linting - fix all issues
- [ ] Run ruff formatting - apply consistent style
- [ ] Review code for readability
- [ ] Run tests again - verify still passing
- [ ] Check test coverage - aim for >80%

**Quality Gate Commands:**
```bash
# Type checking
poetry run mypy src/

# Linting
poetry run ruff check src/

# Formatting
poetry run ruff format src/

# Test with coverage
poetry run pytest --cov=src/ --cov-report=term-missing
```

**Exit Criteria:** All quality gates pass, code is clean, tests passing

## Stage 7: Integration Testing (15-20 min)

- [ ] Write integration tests with real dependencies (Neo4j, file system)
- [ ] Test repository operations with real database
- [ ] Test file I/O with real file system
- [ ] Verify ServiceResult error handling in integration context
- [ ] Run integration tests - verify passing

**Integration Test Commands:**
```bash
# Run integration tests
poetry run pytest tests/integration/

# Run with coverage
poetry run pytest tests/integration/ --cov=src/ --cov-report=term-missing
```

**Exit Criteria:** Integration tests written and passing, real dependencies tested

## Stage 8: E2E Testing (15-20 min)

- [ ] Write E2E tests through MCP interface
- [ ] Test complete user workflows
- [ ] Verify MCP tool registration
- [ ] Test error scenarios through MCP
- [ ] Run E2E tests - verify passing

**E2E Test Commands:**
```bash
# Run E2E tests
poetry run pytest tests/e2e/

# Run specific E2E test
poetry run pytest tests/e2e/test_search_tools.py -v
```

**Exit Criteria:** E2E tests written and passing, user workflows validated

## Stage 9: Real Usage Validation (10-15 min)

- [ ] Start MCP server with changes
- [ ] Open Claude Code and connect to server
- [ ] Test feature manually in real conversation
- [ ] Verify expected behavior in practice
- [ ] Test error scenarios manually
- [ ] Document any issues found

**Manual Testing Commands:**
```bash
# Start MCP server in development mode
poetry run python -m project_watch_mcp

# In Claude Code
# Use /tools to verify tool is registered
# Test tool with real queries
```

**Exit Criteria:** Feature works correctly in Claude Code, manual testing complete

## Stage 10: Production Monitoring (10 min)

- [ ] Verify OTEL traces are generated
- [ ] Check trace includes relevant span attributes
- [ ] Verify errors are traced correctly
- [ ] Test trace visualization in Jaeger/Langfuse
- [ ] Document monitoring approach

**OTEL Validation Commands:**
```bash
# Check for OTEL spans in logs
poetry run python -m project_watch_mcp | grep -i "span"

# View traces in Jaeger
open http://localhost:16686

# Or view in Langfuse
open http://localhost:3000
```

**Exit Criteria:** OTEL traces verified, monitoring in place, feature is production-ready

## Final Production Readiness Checklist

- [ ] All 10 stages completed with exit criteria met
- [ ] All quality gates passing (mypy, ruff, tests)
- [ ] Unit tests passing with >80% coverage
- [ ] Integration tests passing with real dependencies
- [ ] E2E tests passing through MCP interface
- [ ] Manual testing in Claude Code successful
- [ ] OTEL traces verified and working
- [ ] Documentation updated (if needed)
- [ ] Code reviewed (if team process requires)
- [ ] Ready for production deployment

## Common Issues and Resolutions

### Tests Failing After Refactor
- Rerun tests after each change
- Check if types or interfaces changed
- Verify imports are correct

### Integration Tests Failing
- Verify database is running and accessible
- Check connection strings and credentials
- Ensure test data is properly set up

### E2E Tests Failing
- Verify MCP server is running
- Check tool registration in server
- Ensure Claude Code is connected properly

### Manual Testing Issues
- Clear Claude Code cache if behavior is unexpected
- Restart MCP server with latest changes
- Check server logs for errors

### Missing OTEL Traces
- Verify OTEL configuration is correct
- Check that instrumentation is enabled
- Ensure trace collector is running

## Time Estimates

| Stage | Estimated Time |
|-------|----------------|
| Stage 1: Planning | 5-10 min |
| Stage 2: TDD - Red | 10-15 min |
| Stage 3: Naming | 5 min |
| Stage 4: Extract Common | 10 min |
| Stage 5: Implementation | 15-30 min |
| Stage 6: Refactor | 20-30 min |
| Stage 7: Integration Testing | 15-20 min |
| Stage 8: E2E Testing | 15-20 min |
| Stage 9: Real Usage | 10-15 min |
| Stage 10: Production Monitoring | 10 min |
| **Total** | **2-3 hours** |

## Notes

- Don't skip stages - each builds on the previous
- If a stage takes significantly longer, consider breaking the feature into smaller pieces
- Quality gates in Stage 6 are critical - don't bypass them
- Manual testing in Stage 9 often reveals UX issues automated tests miss
- OTEL traces in Stage 10 are essential for production debugging
