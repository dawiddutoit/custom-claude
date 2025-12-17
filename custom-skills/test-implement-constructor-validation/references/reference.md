# Reference - Implement Constructor Validation Tests

## Python Example Scripts

The following utility scripts demonstrate practical usage patterns:

- [generate_constructor_tests.py](../examples/generate_constructor_tests.py) - Generates complete constructor validation test classes from service definitions using AST parsing
- [find_missing_validation.py](../examples/find_missing_validation.py) - Scans codebase to identify services missing constructor validation tests
- [validate_constructor_tests.py](../examples/validate_constructor_tests.py) - Validates existing constructor test implementations for correctness and completeness

---

## Pattern Analysis

### Core Pattern Components

Constructor validation tests follow a strict pattern with these components:

1. **Test Class Naming:** `Test{ServiceName}Constructor`
2. **Fixture Naming:** `mock_{parameter_name}` (exact match to constructor parameter)
3. **Success Test:** One test with all valid parameters
4. **Failure Tests:** One test per required parameter
5. **Type Ignores:** `# type: ignore` on every `None` assignment
6. **Error Assertions:** Validate exact error message text

### Fail-Fast Principle

This pattern enforces the project's fail-fast principle:

**From CLAUDE.md:**
> **Fail Fast** - No optional deps, no fallbacks, no try/except ImportError. All imports at top.

Applied to constructor parameters:
- All parameters are required (no Optional types)
- Constructor validates immediately (before any work)
- Raises ValueError with descriptive message
- Tests ensure validation happens correctly

### Error Message Format

**Standard Format:**
```python
"{ParameterType} is required for {ServiceName}"
```

**Examples:**
- `"Settings is required for IndexingOrchestrator"`
- `"ChunkingService is required for IndexingOrchestrator"`
- `"VoyageClient is required for EmbeddingService"`

**Pattern Rule:** Use the class/type name exactly as it appears in type annotations.

---

## Advanced Configuration

### Mocking Settings with Nested Configuration

Some services access nested settings attributes (e.g., `settings.indexing.max_concurrent_files`).

**When to Mock Nested Config:**
- Service methods (not constructor) use `settings.subsection.attribute`
- Other tests in same file need these values
- Maintaining consistency across test fixtures

**Example:**
```python
@pytest.fixture
def mock_settings(self):
    """Create mock Settings."""
    settings = MagicMock(spec=Settings)
    # Mock indexing configuration for batch processing
    settings.indexing = MagicMock()
    settings.indexing.max_concurrent_files = 5
    settings.indexing.batch_size = 100
    settings.indexing.timeout_seconds = 300
    return settings
```

**Constructor Test Doesn't Require This:**
Constructor validation tests only verify parameter is not None. Nested config is for functional tests.

---

### Async Service Dependencies

Services with async methods should use AsyncMock for async operations.

**When to Use AsyncMock:**
- Service has `async def` methods
- Dependencies (repositories, modules) have async methods
- Tests need to verify async method calls

**Example:**
```python
@pytest.fixture
def mock_indexing_module(self):
    """Create mock IndexingModule with async methods."""
    module = MagicMock(spec=IndexingModule)
    # Add AsyncMock for specific async methods
    module.phase1_create_all_nodes = AsyncMock()
    module.phase2_create_intra_file_relationships = AsyncMock()
    module.phase3_create_cross_file_relationships = AsyncMock()
    return module
```

**Constructor Test Doesn't Require This:**
Constructor validation tests are synchronous. AsyncMock is for functional tests that call async methods.

---

### Services That Create Objects in Constructor

Some services instantiate additional objects in their constructor (not injected).

**Example:**
```python
class IndexingOrchestrator:
    def __init__(self, settings: Settings, indexing_module: IndexingModule):
        if not settings:
            raise ValueError("Settings is required for IndexingOrchestrator")
        if not indexing_module:
            raise ValueError("IndexingModule is required for IndexingOrchestrator")

        self.settings = settings
        self.indexing_module = indexing_module

        # Created objects (not injected)
        self.file_categorizer = FileCategorizer()
        self.content_categorizer = ContentCategorizer()
```

**Test Assertions:**
```python
def test_constructor_initializes_with_valid_dependencies(
    self, mock_settings, mock_indexing_module
):
    """Test that constructor properly initializes with all valid dependencies."""
    orchestrator = IndexingOrchestrator(
        settings=mock_settings,
        indexing_module=mock_indexing_module,
    )

    # Assert injected dependencies (identity check)
    assert orchestrator.settings is mock_settings
    assert orchestrator.indexing_module is mock_indexing_module

    # Assert created objects (type check, not identity)
    assert isinstance(orchestrator.file_categorizer, FileCategorizer)
    assert isinstance(orchestrator.content_categorizer, ContentCategorizer)
```

**Key Difference:**
- **Injected:** Use `is` (identity check) - must be exact mock object
- **Created:** Use `isinstance` (type check) - new instance created

---

## Architecture Context

### Clean Architecture Layers

Constructor validation tests exist at all layers:

**Domain Layer:**
- Minimal dependencies (usually none)
- Entities validate their own invariants
- Value objects validate construction parameters

**Application Layer:**
- Services depend on repositories, other services
- Most constructor validation tests are here
- Orchestrators have many dependencies (5+)

**Infrastructure Layer:**
- Modules depend on external clients (Neo4j, Voyage AI)
- Database repositories depend on drivers
- Configuration validation

**Interface Layer:**
- MCP tools depend on application services
- Minimal constructor complexity

### Dependency Injection Pattern

All services follow constructor injection:

```python
class ApplicationService:
    def __init__(
        self,
        dependency1: Dependency1Type,
        dependency2: Dependency2Type,
    ):
        # Validate all dependencies
        if not dependency1:
            raise ValueError("...")
        if not dependency2:
            raise ValueError("...")

        # Assign dependencies
        self.dependency1 = dependency1
        self.dependency2 = dependency2
```

**Benefits:**
- Testable (can inject mocks)
- Explicit dependencies (no hidden coupling)
- Fail-fast (errors at construction, not runtime)
- Configuration precedence enforced

---

## Troubleshooting

### Common Issues

#### Issue 1: Pyright Error on `None` Assignment

**Error:**
```
Argument of type "None" cannot be assigned to parameter "settings" of type "Settings"
```

**Solution:**
Add `# type: ignore` comment:
```python
ServiceName(
    settings=None,  # type: ignore
    other_param=mock_other_param,
)
```

**Why:** We're intentionally passing wrong type to test validation. Type checker needs to be suppressed.

---

#### Issue 2: Test Fails - ValueError Not Raised

**Symptom:**
```
FAILED - DID NOT RAISE ValueError
```

**Root Cause:**
Service constructor missing validation for that parameter.

**Solution:**
Add validation to service constructor:
```python
def __init__(self, param: ParamType):
    if not param:
        raise ValueError("ParamType is required for ServiceName")
```

---

#### Issue 3: Wrong Error Message Assertion

**Symptom:**
```
AssertionError: assert 'Setting is required for IndexingOrchestrator' in 'Settings is required for IndexingOrchestrator'
```

**Root Cause:**
Typo in assertion - `Setting` vs `Settings`.

**Solution:**
1. Read actual error message from service constructor
2. Copy exact text for assertion
3. Or use partial match: `assert "required for" in str(exc_info.value)`

**Best Practice:** Use exact error message for precision.

---

#### Issue 4: Fixture Not Found

**Symptom:**
```
fixture 'mock_settings' not found
```

**Root Cause:**
- Fixture not defined
- Typo in fixture name
- Fixture defined in wrong test class

**Solution:**
Ensure fixture name exactly matches parameter name:
```python
# Constructor parameter: settings
@pytest.fixture
def mock_settings(self):  # Must be mock_settings
    return MagicMock(spec=Settings)
```

---

#### Issue 5: Too Many/Few Fixtures in Test Method

**Symptom:**
```
TypeError: test_constructor_fails_when_X_is_none() got multiple values for argument 'mock_Y'
```

**Root Cause:**
Fixture list doesn't match what test needs.

**Success Test Pattern:**
```python
def test_constructor_initializes_with_valid_dependencies(
    self,
    mock_param1,  # ALL fixtures included
    mock_param2,
    mock_param3,
):
```

**Validation Test Pattern:**
```python
def test_constructor_fails_when_param1_is_none(
    self,
    # mock_param1 EXCLUDED - this is what we're testing
    mock_param2,  # All OTHER fixtures included
    mock_param3,
):
```

---

## Automation Opportunities

### Why This Pattern is Highly Automatable

1. **Deterministic Generation:**
   - Input: Service class with typed constructor
   - Output: Test class with fixtures and validation tests
   - No subjective decisions required

2. **Extractable Rules:**
   - Parse `__init__` signature → Extract parameter names and types
   - Parse validation blocks → Extract error messages
   - Generate fixtures (1:1 mapping to parameters)
   - Generate tests (1 success + N failures for N parameters)

3. **Validation Possible:**
   - Run pyright to check generated code
   - Run pytest to verify tests pass
   - Check error messages match constructor

### AST Parsing Strategy

**Python AST can extract:**

```python
import ast

class ConstructorExtractor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        if node.name == "__init__":
            # Extract parameters
            params = []
            for arg in node.args.args[1:]:  # Skip 'self'
                param_name = arg.arg
                param_type = ast.unparse(arg.annotation)
                params.append((param_name, param_type))

            # Extract validation messages
            for stmt in node.body:
                if isinstance(stmt, ast.If):
                    # Parse 'if not X: raise ValueError("...")'
                    pass

            return params
```

**Generated Output:**
```python
[
    ("settings", "Settings"),
    ("indexing_module", "IndexingModule"),
    ("extractor_registry", "ExtractorRegistry"),
]
```

### Code Generation Template

**Jinja2 Template:**
```python
class Test{{ service_name }}Constructor:
    """Test {{ service_name }} constructor and initialization."""

    {% for param_name, param_type in parameters %}
    @pytest.fixture
    def mock_{{ param_name }}(self):
        """Create mock {{ param_type }}."""
        return MagicMock(spec={{ param_type }})

    {% endfor %}

    def test_constructor_initializes_with_valid_dependencies(
        self,
        {% for param_name, _ in parameters %}
        mock_{{ param_name }},
        {% endfor %}
    ):
        """Test that constructor properly initializes with all valid dependencies."""
        instance = {{ service_name }}(
            {% for param_name, _ in parameters %}
            {{ param_name }}=mock_{{ param_name }},
            {% endfor %}
        )

        {% for param_name, _ in parameters %}
        assert instance.{{ param_name }} is mock_{{ param_name }}
        {% endfor %}

    {% for param_name, param_type in parameters %}
    def test_constructor_fails_when_{{ param_name }}_is_none(
        self,
        {% for other_param, _ in parameters if other_param != param_name %}
        mock_{{ other_param }},
        {% endfor %}
    ):
        """Test that constructor raises ValueError when {{ param_type }} is None."""
        with pytest.raises(ValueError) as exc_info:
            {{ service_name }}(
                {% for other_param, _ in parameters %}
                {% if other_param == param_name %}
                {{ param_name }}=None,  # type: ignore
                {% else %}
                {{ other_param }}=mock_{{ other_param }},
                {% endif %}
                {% endfor %}
            )

        assert "{{ param_type }} is required for {{ service_name }}" in str(exc_info.value)

    {% endfor %}
```

### Script Skeleton

**Future Implementation:**
```bash
# Usage
python .claude/scripts/generate_constructor_tests.py \
    --service src/your_project/application/orchestration/indexing_orchestrator.py \
    --output tests/unit/application/orchestration/test_indexing_orchestrator.py \
    --append  # Add to existing file

# Features
# - Parse AST to extract constructor signature
# - Generate complete test class
# - Validate with pyright
# - Run generated tests
# - Report success/failure
```

---

## Project-Specific Patterns

### Import Organization

**Standard Import Order:**
```python
# Standard library
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Third party
import pytest

# Project imports - organize by layer
from your_project.config.settings import Settings
from your_project.domain.models.files.file import File
from your_project.application.services.chunking_service import ChunkingService
from your_project.infrastructure.neo4j.graphrag.indexing import IndexingModule
```

### Test File Location

**Mirror Source Structure:**
```
src/your_project/application/orchestration/indexing_orchestrator.py
tests/unit/application/orchestration/test_indexing_orchestrator.py
```

**Pattern:** `tests/{test_type}/{layer}/{module}/test_{filename}.py`

### Docstring Format

**Test Class:**
```python
class TestIndexingOrchestratorConstructor:
    """Test IndexingOrchestrator constructor and initialization."""
```

**Success Test:**
```python
def test_constructor_initializes_with_valid_dependencies(...):
    """Test that constructor properly initializes with all valid dependencies."""
```

**Validation Test:**
```python
def test_constructor_fails_when_settings_is_none(...):
    """Test that constructor raises ValueError when Settings is None."""
```

**Pattern Rules:**
- Class docstring: "Test {ServiceName} constructor and initialization."
- Success test: "Test that constructor properly initializes with all valid dependencies."
- Validation test: "Test that constructor raises ValueError when {Type} is None."

---

## Quality Gates Integration

### Running Constructor Validation Tests

**Individual Service:**
```bash
uv run pytest tests/unit/application/orchestration/test_indexing_orchestrator.py::TestIndexingOrchestratorConstructor -v
```

**All Constructor Tests:**
```bash
uv run pytest tests/ -k "Constructor" -v
```

**With Coverage:**
```bash
uv run pytest tests/unit/application/orchestration/test_indexing_orchestrator.py::TestIndexingOrchestratorConstructor --cov=src/your_project/application/orchestration/indexing_orchestrator --cov-report=term-missing
```

### Type Checking Generated Tests

**Individual File:**
```bash
uv run pyright tests/unit/application/orchestration/test_indexing_orchestrator.py
```

**All Tests:**
```bash
uv run pyright tests/
```

**Should Pass With:**
- 0 errors
- `# type: ignore` comments suppress intentional None assignments

### Quality Gate Command

**Project Standard:**
```bash
./scripts/check_all.sh
```

**Includes:**
- Pyright (type checking)
- Pytest (all tests)
- Ruff (linting)
- Vulture (dead code detection)

**Constructor tests are part of standard quality gates.**

---

## Related Documentation

- [CLAUDE.md](../../../../CLAUDE.md) - Fail-fast principle and quality gates
- [ARCHITECTURE.md](../../../../ARCHITECTURE.md) - Clean Architecture layers and dependency injection
- [../../apply-code-template/references/code-templates.md](../../../docs/code-templates.md) - Service constructor template
- [../../run-quality-gates/references/shared-quality-gates.md](../../../docs/shared-quality-gates.md) - Quality gate guidance
