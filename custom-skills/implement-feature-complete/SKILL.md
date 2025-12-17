---
name: implement-feature-complete
description: |
  Complete feature implementation lifecycle with 10 stages: planning, TDD, naming,
  DRY, implementation, refactor, integration testing, E2E testing, real usage validation,
  and production monitoring. Use when implementing new features, significant changes,
  or onboarding to project workflow. Ensures Clean Architecture, fail-fast principles,
  ServiceResult pattern, and quality gates.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - MultiEdit
  - Write
---

# implement-feature-complete

## Purpose

Orchestrate the complete lifecycle of implementing a feature following project standards. This meta-skill ensures no step is forgotten, all quality gates pass, and the feature is production-ready with proper testing, monitoring, and documentation through a structured 10-stage workflow.

## Quick Start

Orchestrate the complete lifecycle of implementing a feature following project-watch-mcp standards. This meta-skill ensures no step is forgotten, all quality gates pass, and the feature is production-ready with proper testing, monitoring, and documentation.

**Most common use case:**
```
User: "Add ability to search code by file type"

→ Follow 10-stage workflow (TDD, naming, DRY, implementation, refactor, testing)
→ Use checklist template to track progress
→ Validate at each stage before proceeding
→ Feature is production-ready with unit/integration/E2E tests + monitoring

Result: Fully tested feature in ~2-3 hours
```

---

## Table of Contents

### Core Workflow Stages

- [10-Stage Workflow](#10-stage-workflow)
  - [Stage 1: Planning & Location](#stage-1-planning--location-5-10-minutes) - Determine layer placement and architectural patterns
  - [Stage 2: TDD - Red (Write Failing Test)](#stage-2-tdd---red-write-failing-test-10-15-minutes) - Create comprehensive failing tests first
  - [Stage 3: Consistent Naming](#stage-3-consistent-naming-5-minutes) - Follow project naming conventions
  - [Stage 4: Extract Common (DRY Principle)](#stage-4-extract-common-dry-principle-10-minutes) - Identify and centralize shared logic
  - [Stage 5: Implementation - Green (Make Test Pass)](#stage-5-implementation---green-make-test-pass-20-30-minutes) - Minimal implementation to pass tests
  - [Stage 6: Refactor - Clean (Quality Gates)](#stage-6-refactor---clean-quality-gates-10-15-minutes) - Clean code and enforce quality standards
  - [Stage 7: Integration Testing (Real Dependencies)](#stage-7-integration-testing-real-dependencies-15-20-minutes) - Test with real Neo4j and file system
  - [Stage 8: E2E Testing (MCP Interface)](#stage-8-e2e-testing-mcp-interface-15-20-minutes) - Test through actual MCP tool interface
  - [Stage 9: Real Usage Validation (Manual Testing + Monitoring)](#stage-9-real-usage-validation-manual-testing--monitoring-10-15-minutes) - Test in Claude Code and monitor logs
  - [Stage 10: Production Monitoring (OTEL Traces + Final Validation)](#stage-10-production-monitoring-otel-traces--final-validation-5-10-minutes) - Ensure production-ready with monitoring

### Supporting Resources

- [When to Use This Skill](#when-to-use-this-skill)
- [What This Skill Does](#what-this-skill-does)
- [Instructions (10-Stage Workflow)](#instructions)
- [Expected Outcomes](#expected-outcomes)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)
- [Red Flags to Avoid](#red-flags-to-avoid)

---

## When to Use This Skill

Use this skill when:
- **Implementing new features** - "Add ability to X"
- **Significant changes** - Multi-layer modifications affecting domain/application/infrastructure
- **Onboarding to project** - Learning the complete feature workflow
- **Quality-critical work** - Features requiring full test coverage and monitoring
- **Production deployments** - Changes that must be production-ready

**Trigger phrases:**
- "Implement feature X"
- "Add functionality for Y"
- "Complete workflow for Z"
- "End-to-end implementation of X"

---

## What This Skill Does

This skill orchestrates complete feature implementation through:

1. **Planning & Location** - Determine Clean Architecture layer placement
2. **TDD - Red** - Write comprehensive failing tests first
3. **Consistent Naming** - Follow project conventions
4. **Extract Common (DRY)** - Centralize shared logic
5. **Implementation - Green** - Minimum code to pass tests
6. **Refactor - Clean** - Quality gates enforcement
7. **Integration Testing** - Test with real dependencies (Neo4j, file system)
8. **E2E Testing** - Test through MCP interface
9. **Real Usage Validation** - Manual testing in Claude Code
10. **Production Monitoring** - OTEL traces and final validation

See Instructions section below for detailed stage-by-stage workflow.

---

## Instructions

## 10-Stage Workflow

### Stage 1: Planning & Location (5-10 minutes)

**Goal:** Determine where the feature belongs in Clean Architecture layers and which patterns to use.

**Actions:**
1. **Identify Layer:**
   - **Domain:** Business rules, value objects, entities → `src/project_watch_mcp/domain/`
   - **Application:** Use cases, CQRS handlers → `src/project_watch_mcp/application/`
   - **Infrastructure:** External dependencies (Neo4j, file system) → `src/project_watch_mcp/infrastructure/`
   - **Interface:** MCP tools, CLI → `src/project_watch_mcp/interface/`

2. **Determine Pattern:**
   - **CQRS:** Is it a read (Query) or write (Command)?
   - **Repository:** Does it access data? Add method to repository protocol
   - **Value Object:** Does it have validation logic? Create value object in domain

3. **Check Dependencies:**
   - What services/repositories are needed?
   - Are they already in the DI container?

**Validation:**
- [ ] Layer identified (Domain/Application/Infrastructure/Interface)
- [ ] Pattern determined (Command/Query/Repository/Value Object)
- [ ] Dependencies listed

**Skills Used:**
- Grep for existing patterns: `search_code("class.*Query", search_type="pattern")`
- Read ARCHITECTURE.md for layer guidelines
- Review similar features for patterns

---

### Stage 2: TDD - Red (Write Failing Test) (10-15 minutes)

**Goal:** Write comprehensive tests that fail because the feature doesn't exist yet.

**Actions:**
1. **Review Current Tests First:**
   ```bash
   # Find similar test files
   find tests/unit/application/queries -name "test_*.py"
   # Read test patterns
   cat tests/unit/application/queries/test_search_code_query.py
   ```

2. **Create Test File:**
   ```python
   # tests/unit/application/queries/test_search_by_file_type.py
   import pytest
   from project_watch_mcp.application.queries.search_by_file_type import (
       SearchByFileTypeQuery,
       SearchByFileTypeHandler
   )

   class TestSearchByFileTypeQuery:
       def test_constructor_requires_file_type(self):
           # Constructor validation (fail-fast)
           with pytest.raises(ValueError, match="file_type required"):
               SearchByFileTypeQuery(file_type=None)

       def test_constructor_normalizes_file_type(self):
           # Business logic test
           query = SearchByFileTypeQuery(file_type=".PY")
           assert query.file_type == "py"

   class TestSearchByFileTypeHandler:
       async def test_execute_calls_repository(self, mock_repository):
           # Mock repository behavior
           mock_repository.search_by_file_type.return_value = ServiceResult.success([])

           handler = SearchByFileTypeHandler(repository=mock_repository)
           result = await handler.execute(SearchByFileTypeQuery(file_type="py"))

           # Verify repository called correctly
           mock_repository.search_by_file_type.assert_called_once_with("py")
           assert result.success
   ```

3. **Run Test:**
   ```bash
   uv run pytest tests/unit/application/queries/test_search_by_file_type.py -v
   # Expected: FAIL (classes don't exist) ✅ RED
   ```

**Validation:**
- [ ] Test file created in correct location
- [ ] Constructor validation tests written (fail-fast)
- [ ] Business logic tests written (mocked dependencies)
- [ ] Tests FAIL with clear error messages
- [ ] Test follows project patterns (async, ServiceResult, pytest fixtures)

**Skills Used:**
- `setup-pytest-fixtures` - Create test fixtures
- `setup-async-testing` - Configure async test patterns
- `enforce-tdd-workflow` - Ensure RED → GREEN → REFACTOR

---

### Stage 3: Consistent Naming (5 minutes)

**Goal:** Follow project naming conventions by searching for existing patterns.

**Actions:**
1. **Search Existing Patterns:**
   ```python
   # Find similar classes
   search_code("class.*Query:", search_type="pattern")
   search_code("class.*Handler:", search_type="pattern")
   search_code("class.*Repository:", search_type="pattern")
   ```

2. **Apply Conventions:**
   - **Query:** `SearchByFileTypeQuery` (noun phrase + Query suffix)
   - **Handler:** `SearchByFileTypeHandler` (matches query name + Handler)
   - **Repository Method:** `search_by_file_type()` (verb + snake_case)
   - **File Names:** Match class names in snake_case

3. **Document Naming:**
   ```python
   # src/project_watch_mcp/application/queries/search_by_file_type.py
   """
   Search code by file type query and handler.

   Query: SearchByFileTypeQuery - Represents the search request
   Handler: SearchByFileTypeHandler - Executes the search via repository
   """
   ```

**Validation:**
- [ ] Names follow project conventions
- [ ] Names consistent with similar features
- [ ] File names match class names (snake_case)

**Skills Used:**
- `search_code()` - Find existing patterns
- `apply-code-template` - Use project templates

---

### Stage 4: Extract Common (DRY Principle) (10 minutes)

**Goal:** Identify and centralize shared logic to avoid duplication.

**Actions:**
1. **Search for Duplication:**
   ```python
   # Check if normalization already exists
   search_code("normalize.*file.*type", search_type="semantic")
   search_code("\.lower\(\).*\.strip\(\)", search_type="pattern")
   ```

2. **Create Value Object (if needed):**
   ```python
   # src/project_watch_mcp/domain/values/file_type.py
   from dataclasses import dataclass

   @dataclass(frozen=True)
   class FileType:
       """Normalized file type value object."""
       extension: str

       def __post_init__(self):
           if not self.extension:
               raise ValueError("File type extension required")

           # Normalize: remove leading dot, lowercase
           normalized = self.extension.lstrip('.').lower()
           object.__setattr__(self, 'extension', normalized)

       def __str__(self) -> str:
           return self.extension
   ```

3. **Centralize Utilities:**
   ```python
   # If it's a pure function, add to utilities
   # src/project_watch_mcp/application/utils/file_utils.py
   def normalize_file_extension(ext: str) -> str:
       """Normalize file extension to lowercase without leading dot."""
       if not ext:
           raise ValueError("Extension required")
       return ext.lstrip('.').lower()
   ```

**Validation:**
- [ ] No duplicated logic across files
- [ ] Common patterns extracted to value objects or utilities
- [ ] Reusable code documented with docstrings

**Skills Used:**
- `create-value-object` - Create domain value objects
- `search_code()` - Find existing duplication
- Read similar features to identify patterns

---

### Stage 5: Implementation - Green (Make Test Pass) (20-30 minutes)

**Goal:** Implement minimum code to make tests pass.

**Actions:**
1. **Create Classes:**
   ```python
   # src/project_watch_mcp/application/queries/search_by_file_type.py
   from dataclasses import dataclass
   from project_watch_mcp.domain.values.file_type import FileType
   from project_watch_mcp.application.utils.service_result import ServiceResult

   @dataclass(frozen=True)
   class SearchByFileTypeQuery:
       """Query to search code by file type."""
       file_type: str

       def __post_init__(self):
           if not self.file_type:
               raise ValueError("file_type required")
           # Normalize using value object
           file_type_vo = FileType(extension=self.file_type)
           object.__setattr__(self, 'file_type', str(file_type_vo))

   class SearchByFileTypeHandler:
       """Handler for searching code by file type."""

       def __init__(self, repository: CodeRepository):
           if not repository:
               raise ValueError("repository required")
           self._repository = repository

       async def execute(self, query: SearchByFileTypeQuery) -> ServiceResult[list]:
           """Execute file type search."""
           return await self._repository.search_by_file_type(query.file_type)
   ```

2. **Add Repository Method:**
   ```python
   # src/project_watch_mcp/domain/repositories/code_repository.py
   from typing import Protocol

   class CodeRepository(Protocol):
       async def search_by_file_type(self, file_type: str) -> ServiceResult[list]:
           """Search code by file type."""
           ...

   # src/project_watch_mcp/infrastructure/repositories/neo4j_code_repository.py
   async def search_by_file_type(self, file_type: str) -> ServiceResult[list]:
       """Search code by file type."""
       if not file_type:
           return ServiceResult.failure("file_type required")

       query = """
       MATCH (c:Code)
       WHERE c.file_path ENDS WITH $file_ext
       RETURN c
       """
       return await self._execute_query(query, {"file_ext": f".{file_type}"})
   ```

3. **Wire to DI Container:**
   ```python
   # src/project_watch_mcp/infrastructure/container.py
   def _register_query_handlers(self) -> None:
       self.register(
           SearchByFileTypeHandler,
           lambda: SearchByFileTypeHandler(
               repository=self.resolve(CodeRepository)
           )
       )
   ```

4. **Run Tests:**
   ```bash
   uv run pytest tests/unit/application/queries/test_search_by_file_type.py -v
   # Expected: PASS ✅ GREEN
   ```

**Validation:**
- [ ] All unit tests pass
- [ ] Minimum code written (no gold plating)
- [ ] Constructor validation enforced (fail-fast)
- [ ] ServiceResult pattern used
- [ ] Dependencies injected (no defaults)

**Skills Used:**
- `implement-cqrs-handler` - Create CQRS handlers
- `implement-dependency-injection` - Wire to container
- `implement-repository-pattern` - Add repository methods

---

### Stage 6: Refactor - Clean (Quality Gates) (10-15 minutes)

**Goal:** Clean up code while keeping tests passing, enforce quality standards.

**Actions:**
1. **Run Quality Gates:**
   ```bash
   ./scripts/check_all.sh
   # Must pass: pyright, ruff, vulture, pytest
   ```

2. **Fix Common Issues:**
   - **Type Errors:** Ensure all types annotated correctly
   - **Unused Imports:** Remove or use them
   - **Dead Code:** Delete if truly unused
   - **Linting:** Fix ruff warnings

3. **Extract Magic Values:**
   ```python
   # ❌ BEFORE (magic string)
   query = "MATCH (c:Code) WHERE c.file_path ENDS WITH '.py'"

   # ✅ AFTER (config injection)
   query = """
   MATCH (c:Code)
   WHERE c.file_path ENDS WITH $file_ext
   RETURN c
   """
   ```

4. **Add Docstrings:**
   ```python
   class SearchByFileTypeHandler:
       """
       Handler for searching code by file type.

       This handler accepts a file type (e.g., 'py', '.ts') and searches
       the code index for all files with that extension.

       Args:
           repository: Code repository for querying indexed code

       Returns:
           ServiceResult containing list of matching code nodes
       """
   ```

**Validation:**
- [ ] `./scripts/check_all.sh` passes completely
- [ ] No type errors (pyright)
- [ ] No linting errors (ruff)
- [ ] No dead code (vulture)
- [ ] All tests still pass
- [ ] Magic values extracted to config
- [ ] Docstrings added

**Skills Used:**
- `debug-type-errors` - Fix pyright errors
- `optimize-imports` - Clean up imports
- `resolve-serviceresult-errors` - Fix ServiceResult issues
- `run-quality-gates` - Enforce Definition of Done

---

### Stage 7: Integration Testing (Real Dependencies) (15-20 minutes)

**Goal:** Test feature with real external dependencies (Neo4j, file system).

**Actions:**
1. **Create Integration Test:**
   ```python
   # tests/integration/application/queries/test_search_by_file_type_integration.py
   import pytest
   from project_watch_mcp.application.queries.search_by_file_type import (
       SearchByFileTypeQuery,
       SearchByFileTypeHandler
   )

   @pytest.mark.integration
   class TestSearchByFileTypeIntegration:
       async def test_search_by_file_type_with_real_database(
           self,
           neo4j_repository,  # Real Neo4j connection
           sample_indexed_code  # Fixture that creates test data
       ):
           """Test searching by file type with real Neo4j."""
           handler = SearchByFileTypeHandler(repository=neo4j_repository)
           query = SearchByFileTypeQuery(file_type="py")

           result = await handler.execute(query)

           assert result.success
           assert len(result.value) > 0
           assert all(item.file_path.endswith('.py') for item in result.value)
   ```

2. **Run Integration Tests:**
   ```bash
   # Start Neo4j first
   # Run integration tests
   uv run pytest tests/integration/application/queries/test_search_by_file_type_integration.py -v -m integration
   ```

3. **Verify Database State:**
   ```cypher
   // Open Neo4j Browser
   MATCH (c:Code)
   WHERE c.file_path ENDS WITH '.py'
   RETURN count(c)
   ```

**Validation:**
- [ ] Integration test created
- [ ] Test uses real Neo4j database
- [ ] Test data fixtures created
- [ ] Integration tests pass
- [ ] Database state verified

**Skills Used:**
- `setup-async-testing` - Configure async integration tests
- `organize-test-layers` - Separate unit/integration tests

---

### Stage 8: E2E Testing (MCP Interface) (15-20 minutes)

**Goal:** Test feature through the MCP tool interface (how users will actually use it).

**Actions:**
1. **Create MCP Tool (if needed):**
   ```python
   # src/project_watch_mcp/interface/mcp_tools/search_tools.py
   @mcp.tool()
   async def search_code_by_file_type(file_type: str) -> dict:
       """Search code by file type."""
       handler = container.resolve(SearchByFileTypeHandler)
       query = SearchByFileTypeQuery(file_type=file_type)
       result = await handler.execute(query)

       if result.success:
           return {"success": True, "results": result.value}
       return {"success": False, "error": result.error}
   ```

2. **Create E2E Test:**
   ```python
   # tests/e2e/test_search_tools_e2e.py
   import pytest
   from project_watch_mcp.interface.mcp_tools import search_code_by_file_type

   @pytest.mark.e2e
   class TestSearchToolsE2E:
       async def test_search_by_file_type_via_mcp(
           self,
           initialized_repository  # Fixture with test data
       ):
           """Test search by file type through MCP tool interface."""
           result = await search_code_by_file_type(file_type="py")

           assert result["success"] is True
           assert len(result["results"]) > 0
   ```

3. **Run E2E Tests:**
   ```bash
   uv run pytest tests/e2e/test_search_tools_e2e.py -v -m e2e
   ```

4. **Verify Logs:**
   ```bash
   tail -f logs/project-watch-mcp.log
   # Check for:
   # - Tool invocation logged
   # - Query executed
   # - Results returned
   # - No errors
   ```

**Validation:**
- [ ] E2E test created
- [ ] Test calls MCP tool interface
- [ ] ServiceResult → dict conversion verified
- [ ] E2E tests pass
- [ ] Logs show successful execution

**Skills Used:**
- E2E testing patterns
- `analyze-logs` - Verify execution in logs

---

### Stage 9: Real Usage Validation (Manual Testing + Monitoring) (10-15 minutes)

**Goal:** Test feature in actual Claude Code usage and monitor for errors.

**Actions:**
1. **Start MCP Server:**
   ```bash
   ./run-mcp-server.sh
   ```

2. **Test in Claude Code:**
   ```
   # In Claude Code conversation:
   "Search for all Python files in the codebase"

   # Claude should invoke:
   search_code_by_file_type(file_type="py")
   ```

3. **Monitor Logs in Real-Time:**
   ```bash
   # Terminal 1: Run server
   ./run-mcp-server.sh

   # Terminal 2: Watch logs
   tail -f logs/project-watch-mcp.log | grep -i "search_by_file_type"
   ```

4. **Verify Results:**
   - Does Claude get results back?
   - Are results accurate?
   - Any error messages in logs?
   - Response time acceptable?

5. **Test Edge Cases:**
   ```
   # Test with different file types
   search_code_by_file_type(file_type=".ts")  # Leading dot
   search_code_by_file_type(file_type="PY")   # Uppercase
   search_code_by_file_type(file_type="xyz")  # Non-existent type
   ```

**Validation:**
- [ ] Feature works in Claude Code
- [ ] Results are accurate
- [ ] No errors in logs
- [ ] Edge cases handled correctly
- [ ] Performance acceptable

**Skills Used:**
- `analyze-logs` - Monitor execution logs

---

### Stage 10: Production Monitoring (OTEL Traces + Final Validation) (5-10 minutes)

**Goal:** Ensure feature is production-ready with monitoring and final quality gates.

**Actions:**
1. **Analyze OTEL Traces:**
   ```bash
   python3 .claude/tools/utils/log_analyzer.py logs/project-watch-mcp.log
   ```

2. **Check for:**
   - **Errors:** Any exceptions or failures?
   - **Performance:** Query execution time acceptable?
   - **Spans:** Proper trace context propagation?
   - **Attributes:** All relevant context logged?

3. **Final Quality Gates:**
   ```bash
   ./scripts/check_all.sh
   # Must pass all checks:
   # ✅ pyright (type checking)
   # ✅ ruff (linting)
   # ✅ vulture (dead code)
   # ✅ pytest (all tests)
   ```

4. **Performance Validation:**
   ```bash
   # Check query performance in Neo4j
   # Open Neo4j Browser, run:
   PROFILE MATCH (c:Code)
   WHERE c.file_path ENDS WITH '.py'
   RETURN c
   # Verify no full table scans, indexes used
   ```

5. **Documentation Check:**
   - [ ] Feature documented in relevant ADRs
   - [ ] API changes documented
   - [ ] Breaking changes noted

**Validation:**
- [ ] OTEL traces clean (no errors)
- [ ] Performance acceptable (<100ms for queries)
- [ ] All quality gates pass
- [ ] Documentation updated
- [ ] Feature ready for production

**Skills Used:**
- `instrument-with-otel` - Add OTEL instrumentation
- `run-quality-gates` - Final validation
- `analyze-logs` - Review traces

---

## Usage Examples

### Example 1: Implementing "Search by File Type" Feature

**Scenario:** User says "Add ability to search code by file type"

**Workflow:**

1. **Stage 1: Planning** - Query belongs in Application layer, CQRS pattern
2. **Stage 2: TDD - Red** - Write failing tests for SearchByFileTypeQuery and Handler
3. **Stage 3: Naming** - SearchByFileTypeQuery, SearchByFileTypeHandler (follows conventions)
4. **Stage 4: DRY** - Extract FileType value object for normalization
5. **Stage 5: Green** - Implement query, handler, repository method
6. **Stage 6: Refactor** - Run `./scripts/check_all.sh`, fix type errors, add docstrings
7. **Stage 7: Integration** - Test with real Neo4j database
8. **Stage 8: E2E** - Test through MCP tool interface
9. **Stage 9: Real Usage** - Test in Claude Code, monitor logs
10. **Stage 10: Monitoring** - Analyze OTEL traces, final quality gates

**Result:** Production-ready feature in ~2-3 hours with full test coverage

---

### Example 2: Adding New Repository Method

**Scenario:** Need to add `get_entities_by_type()` to CodeRepository

**Abbreviated Workflow:**

1. **Planning:** Infrastructure layer, repository pattern
2. **TDD:** Write test expecting ServiceResult[list[Entity]]
3. **Implementation:** Add method to Protocol and Neo4jCodeRepository
4. **Integration Test:** Test with real Neo4j
5. **Quality Gates:** Ensure pyright, ruff, pytest pass

**Time:** ~1 hour for simpler changes

---

## Expected Outcomes

### Successful Feature Implementation

```
✅ Feature Complete: search_by_file_type

Time: 2.5 hours
Stages completed: 10/10

Test Coverage:
  ✅ Unit tests (8 tests, 100% coverage)
  ✅ Integration tests (3 tests, real Neo4j)
  ✅ E2E tests (2 tests, MCP interface)

Quality Gates:
  ✅ pyright (0 errors)
  ✅ ruff (0 violations)
  ✅ vulture (no dead code)
  ✅ pytest (all tests pass)

Production Ready:
  ✅ OTEL traces clean
  ✅ Performance acceptable (<100ms queries)
  ✅ Real usage validated in Claude Code
  ✅ Documentation updated

Next Steps:
  1. Create PR with feature branch
  2. Request code review
  3. Deploy to staging
```

### Stage Failure - Quality Gates Not Passing

```
❌ Stage 6 Failed: Refactor - Clean

Quality gates status:
  ✅ pytest (15/15 tests pass)
  ❌ pyright (3 type errors)
  ✅ ruff (0 violations)
  ✅ vulture (0 dead code)

Type errors found:
  1. src/app/queries/search.py:42 - Argument type mismatch
  2. src/app/queries/search.py:58 - Missing return type annotation
  3. tests/unit/test_search.py:22 - Mock configuration incorrect

Action Required:
  1. Fix type errors before proceeding
  2. Re-run quality gates
  3. Do NOT proceed to Stage 7 until all gates pass

Use debug-type-errors skill for systematic fixes.
```

---

## Requirements

**Tools:**
- Read, Grep, Glob, Bash - File operations and code search
- Edit, MultiEdit, Write - Code modifications
- Skill invocations for specialized tasks

**Dependencies:**
- pytest>=7.0.0 - Testing framework
- pytest-asyncio - Async test support
- pyright - Type checking
- ruff - Linting
- vulture - Dead code detection
- Neo4j Desktop - Database for integration tests

**Environment:**
- Python 3.11+
- UV package manager configured
- Neo4j running on bolt://localhost:7687

**Knowledge:**
- Clean Architecture principles (Domain → Application → Infrastructure → Interface)
- CQRS pattern (Command/Query separation)
- ServiceResult pattern (monad for error handling)
- TDD workflow (Red → Green → Refactor)
- Project conventions (ARCHITECTURE.md, CLAUDE.md)

**Optional:**
- FastMCP framework (for MCP tool creation)
- OpenTelemetry instrumentation patterns

---

## Troubleshooting

### Issue: Quality gates failing at Stage 6

**Symptom:** `./scripts/check_all.sh` reports errors

**Solutions:**

1. **Pyright errors:**
   - Use `debug-type-errors` skill for systematic fixes
   - Check ServiceResult[T] type annotations
   - Verify all parameters have types

2. **Ruff violations:**
   - Run `uv run ruff check src/ --fix` for auto-fixes
   - Manual fixes for remaining violations

3. **Vulture dead code warnings:**
   - Verify code is actually unused (not just imported elsewhere)
   - Add `# noqa` comment if intentionally unused (e.g., Protocol methods)

4. **Pytest failures:**
   - Use `debug-test-failures` skill
   - Check mock configurations return ServiceResult
   - Verify async/await patterns

**Never skip quality gates - fix or explain why.**

---

### Issue: Integration tests failing at Stage 7

**Symptom:** Tests pass in unit layer, fail in integration layer

**Common causes:**

1. **Neo4j not running:**
   - Start Neo4j Desktop
   - Verify connection: `bolt://localhost:7687`

2. **Test data not created:**
   - Check fixture creates sample data
   - Verify database cleared before tests

3. **Cypher query syntax error:**
   - Test query in Neo4j Browser first
   - Check parameter placeholders ($param_name)

4. **ServiceResult wrapping missing:**
   - Repository must return ServiceResult[T]
   - Check mock configurations in tests

---

### Issue: E2E tests failing at Stage 8

**Symptom:** Integration tests pass, E2E tests fail

**Common causes:**

1. **MCP tool not registered:**
   - Check tool registered in FastMCP
   - Verify tool appears in MCP tools list

2. **ServiceResult → dict conversion missing:**
   - MCP tools must return dict, not ServiceResult
   - Use: `return {"success": result.success, "data": result.data}`

3. **Container resolution failing:**
   - Verify service registered in DI container
   - Check dependency injection chain

---

### Issue: Real usage failing at Stage 9

**Symptom:** E2E tests pass, but fails in Claude Code

**Debugging steps:**

1. **Check logs in real-time:**
   ```bash
   tail -f logs/project-watch-mcp.log | grep -i "feature_name"
   ```

2. **Look for errors:**
   - Import errors (missing dependencies)
   - Runtime errors (ServiceResult not handled)
   - Connection errors (Neo4j unreachable)

3. **Use analyze-logs skill:**
   ```bash
   python .claude/tools/utils/log_analyzer.py logs/project-watch-mcp.log
   ```

---

## Red Flags to Avoid

### Process Violations

1. **Skipping TDD** - Writing implementation before tests
2. **Skipping quality gates** - "I'll fix it later" (you won't)
3. **Not following naming conventions** - Creates inconsistency
4. **Duplicating logic** - Not extracting common patterns
5. **Magic values** - Hardcoding instead of config injection
6. **Optional config** - Violates fail-fast principle

### Testing Violations

7. **Only unit tests** - Integration/E2E tests are required
8. **Mock returns dict** - Must return ServiceResult
9. **No real usage validation** - Test in actual Claude Code
10. **Ignoring OTEL traces** - Monitoring is non-negotiable

### Quality Violations

11. **Type errors** - All code must be type-safe
12. **Dead code** - Delete or explain why unused
13. **No docstrings** - Public APIs must be documented
14. **Breaking changes without ADR** - Document architectural decisions

### Architecture Violations

15. **Wrong layer** - Domain importing from Infrastructure
16. **Dependency inversion violation** - Infrastructure importing concrete domain classes
17. **Missing Protocol** - Repository implementations without Protocol
18. **Direct database access** - Bypass repository pattern

**If you see any red flags, STOP and fix immediately.**

---

## Templates

Use the workflow checklist template:

```bash
cp .claude/skills/implement-feature-complete/templates/workflow-checklist.md ./feature-name-checklist.md
```

---

## Integration Points

### With Other Skills

**implement-feature-complete orchestrates these skills:**
- **setup-pytest-fixtures** - Stage 2 (test setup)
- **setup-async-testing** - Stage 2 (async patterns)
- **implement-cqrs-handler** - Stage 5 (CQRS implementation)
- **implement-repository-pattern** - Stage 5 (data access)
- **implement-dependency-injection** - Stage 5 (DI wiring)
- **debug-type-errors** - Stage 6 (refactor)
- **optimize-imports** - Stage 6 (cleanup)
- **run-quality-gates** - Stage 6, 10 (validation)
- **instrument-with-otel** - Stage 10 (monitoring)
- **analyze-logs** - Stage 9 (real usage)

### With Agent Workflows

**Agents should invoke this skill:**
- @implementer - Primary user for feature implementation
- @planner - To understand feature requirements and breakdown
- @unit-tester - For TDD workflow (Stage 2)

### With TodoWrite Tool

**Integration pattern:**
```python
# Create feature todo with 10-stage workflow
TodoWrite([
    {"content": "Stage 1: Planning", "status": "pending"},
    {"content": "Stage 2: TDD - Red", "status": "pending"},
    # ... 8 more stages
])

# Update as each stage completes
TodoWrite([
    {"content": "Stage 1: Planning", "status": "completed"},
    {"content": "Stage 2: TDD - Red", "status": "in_progress"},
])
```

## Expected Benefits

| Metric | Without Skill | With Skill | Improvement |
|--------|--------------|------------|-------------|
| **Feature Completion Time** | 4-6 hours | 2-3 hours | 50% faster |
| **Test Coverage** | 60% (ad-hoc) | 100% (TDD enforced) | 67% increase |
| **Quality Gate Pass Rate** | 70% (forgotten) | 100% (enforced) | 43% improvement |
| **Production Bugs** | 15% (testing gaps) | 3% (comprehensive) | 80% reduction |
| **Time to Production** | Days (missing steps) | Hours (complete workflow) | 90% faster |
| **Documentation Quality** | 40% (optional) | 100% (required) | 150% increase |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **All Stages Completed** | 10/10 | Checklist validation |
| **Test Coverage** | 100% | pytest --cov |
| **Quality Gates Pass** | 100% | check_all.sh |
| **OTEL Traces Clean** | Zero errors | log_analyzer.py |
| **Real Usage Validated** | Manual test passed | Claude Code testing |
| **Performance Acceptable** | <100ms queries | Neo4j profiling |

## Validation Process

### Stage Validation Checkpoints

Each stage has specific validation criteria:

**Stage 1: Planning**
```bash
✓ Layer identified
✓ Pattern determined
✓ Dependencies listed
```

**Stage 2: TDD - Red**
```bash
✓ Tests written
✓ Tests fail (RED)
✓ Error messages clear
```

**Stage 3-5: Implementation**
```bash
✓ Naming conventions followed
✓ Common patterns extracted
✓ Tests pass (GREEN)
```

**Stage 6: Refactor**
```bash
✓ Quality gates pass (MANDATORY)
✓ No type errors
✓ No dead code
```

**Stage 7-8: Testing**
```bash
✓ Integration tests pass
✓ E2E tests pass
✓ Real Neo4j validation
```

**Stage 9-10: Production Ready**
```bash
✓ Manual testing in Claude Code
✓ OTEL traces clean
✓ Performance validated
```

## See Also

- [templates/workflow-checklist.md](./templates/workflow-checklist.md) - Reusable checklist
- [references/stage-guide.md](./references/stage-guide.md) - Deep dive on each stage
- [ARCHITECTURE.md](../../../ARCHITECTURE.md) - Clean Architecture layers
- [CLAUDE.md](../../../CLAUDE.md) - Project standards and rules
