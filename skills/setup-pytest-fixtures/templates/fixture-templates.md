# Fixture Templates - Setup Pytest Fixtures

Copy-paste templates for common pytest fixture patterns. Replace placeholders with your specific values.

## Basic Fixture Templates

### Template 1: Simple Mock Fixture

```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_{{COMPONENT_NAME}}():
    """Create mock {{COMPONENT_NAME}} for testing.

    Returns:
        MagicMock: Mock {{COMPONENT_NAME}} with common attributes
    """
    mock = MagicMock()
    mock.{{ATTRIBUTE_1}} = {{DEFAULT_VALUE_1}}
    mock.{{ATTRIBUTE_2}} = {{DEFAULT_VALUE_2}}
    return mock
```

**Placeholders:**
- `{{COMPONENT_NAME}}`: Component being mocked (e.g., `settings`, `service`, `repository`)
- `{{ATTRIBUTE_1}}`, `{{ATTRIBUTE_2}}`: Attributes to configure
- `{{DEFAULT_VALUE_1}}`, `{{DEFAULT_VALUE_2}}`: Default values for attributes

**Example:**
```python
@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    mock = MagicMock()
    mock.project = MagicMock()
    mock.project.project_name = "test_project"
    mock.neo4j = MagicMock()
    mock.neo4j.database_name = "test_db"
    return mock
```

---

### Template 2: Fixture with Cleanup

```python
import pytest

@pytest.fixture
def {{FIXTURE_NAME}}():
    """{{FIXTURE_DESCRIPTION}}.

    Yields:
        {{RETURN_TYPE}}: {{RESOURCE_DESCRIPTION}}
    """
    # Setup
    resource = {{SETUP_FUNCTION}}()
    {{OPTIONAL_INITIALIZATION}}

    yield resource

    # Cleanup
    {{CLEANUP_FUNCTION}}(resource)
```

**Placeholders:**
- `{{FIXTURE_NAME}}`: Name of the fixture
- `{{FIXTURE_DESCRIPTION}}`: What the fixture provides
- `{{RETURN_TYPE}}`: Type of resource returned
- `{{RESOURCE_DESCRIPTION}}`: Description of the resource
- `{{SETUP_FUNCTION}}`: Function to create resource
- `{{OPTIONAL_INITIALIZATION}}`: Optional initialization code
- `{{CLEANUP_FUNCTION}}`: Function to cleanup resource

**Example:**
```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing.

    Yields:
        Path: Temporary directory path
    """
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
    # Cleanup happens automatically
```

---

## Factory Fixture Templates

### Template 3: Basic Factory Fixture

```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def {{FIXTURE_NAME}}_factory():
    """Factory for custom {{COMPONENT_NAME}}.

    Returns:
        callable: Function that creates {{COMPONENT_NAME}} with custom attributes

    Example:
        def test_something({{FIXTURE_NAME}}_factory):
            instance = {{FIXTURE_NAME}}_factory(
                {{PARAM_1}}={{VALUE_1}},
                {{PARAM_2}}={{VALUE_2}}
            )
    """
    def create_{{COMPONENT_NAME}}(**kwargs):
        """Create {{COMPONENT_NAME}} with custom attributes.

        Args:
            **kwargs: Attributes to customize

        Returns:
            {{RETURN_TYPE}}: Configured {{COMPONENT_NAME}}
        """
        instance = MagicMock()

        # Set defaults with override support
        instance.{{ATTRIBUTE_1}} = kwargs.get("{{PARAM_1}}", {{DEFAULT_1}})
        instance.{{ATTRIBUTE_2}} = kwargs.get("{{PARAM_2}}", {{DEFAULT_2}})

        return instance

    return create_{{COMPONENT_NAME}}
```

**Placeholders:**
- `{{FIXTURE_NAME}}`: Base fixture name
- `{{COMPONENT_NAME}}`: Component being created
- `{{RETURN_TYPE}}`: Type returned by factory
- `{{PARAM_1}}`, `{{PARAM_2}}`: Parameter names
- `{{VALUE_1}}`, `{{VALUE_2}}`: Example values
- `{{ATTRIBUTE_1}}`, `{{ATTRIBUTE_2}}`: Attributes to set
- `{{DEFAULT_1}}`, `{{DEFAULT_2}}`: Default values

**Example:**
```python
@pytest.fixture
def mock_settings_factory():
    """Factory for custom mock settings."""
    def create_settings(**kwargs):
        """Create settings with custom attributes."""
        settings = MagicMock()
        settings.project = MagicMock()
        settings.project.project_name = kwargs.get("project_name", "test_project")
        settings.chunking = MagicMock()
        settings.chunking.chunk_size = kwargs.get("chunk_size", 50)
        return settings
    return create_settings
```

---

### Template 4: Factory with Success/Failure States

```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def {{FIXTURE_NAME}}_factory():
    """Factory for {{COMPONENT_NAME}} with success/failure states.

    Returns:
        callable: Function that creates {{COMPONENT_NAME}} instances

    Example:
        success = {{FIXTURE_NAME}}_factory(success=True, data="result")
        failure = {{FIXTURE_NAME}}_factory(success=False, error="error msg")
    """
    def create_{{COMPONENT_NAME}}(success=True, data=None, error=None):
        """Create {{COMPONENT_NAME}} with specified state.

        Args:
            success: Whether operation succeeds
            data: Data for successful result
            error: Error message for failure

        Returns:
            MagicMock: Mock {{COMPONENT_NAME}}
        """
        result = MagicMock()
        result.is_success = success
        result.is_failure = not success

        if success:
            result.data = data
            result.unwrap = MagicMock(return_value=data)
            result.error = None
        else:
            result.data = None
            result.error = error or "Operation failed"
            result.unwrap = MagicMock(side_effect=ValueError(result.error))

        return result

    return create_{{COMPONENT_NAME}}
```

**Example:**
```python
@pytest.fixture
def mock_service_result():
    """Factory for ServiceResult mocks."""
    def create_result(success=True, data=None, error=None):
        result = MagicMock()
        result.is_success = success
        result.is_failure = not success
        if success:
            result.data = data
            result.unwrap = MagicMock(return_value=data)
        else:
            result.error = error or "Operation failed"
            result.unwrap = MagicMock(side_effect=ValueError(result.error))
        return result
    return create_result
```

---

## Async Fixture Templates

### Template 5: Basic Async Fixture

```python
import pytest_asyncio
from collections.abc import AsyncGenerator

@pytest_asyncio.fixture
async def {{FIXTURE_NAME}}() -> AsyncGenerator[{{RETURN_TYPE}}, None]:
    """{{FIXTURE_DESCRIPTION}}.

    Yields:
        {{RETURN_TYPE}}: {{RESOURCE_DESCRIPTION}}
    """
    # Async setup
    resource = await {{ASYNC_SETUP_FUNCTION}}()
    {{OPTIONAL_ASYNC_INITIALIZATION}}

    yield resource

    # Async cleanup
    await {{ASYNC_CLEANUP_FUNCTION}}(resource)
```

**Placeholders:**
- `{{FIXTURE_NAME}}`: Fixture name
- `{{RETURN_TYPE}}`: Type of async resource
- `{{FIXTURE_DESCRIPTION}}`: Description
- `{{RESOURCE_DESCRIPTION}}`: Resource description
- `{{ASYNC_SETUP_FUNCTION}}`: Async setup function
- `{{OPTIONAL_ASYNC_INITIALIZATION}}`: Optional async init
- `{{ASYNC_CLEANUP_FUNCTION}}`: Async cleanup function

**Example:**
```python
import pytest_asyncio
from collections.abc import AsyncGenerator
from neo4j import AsyncDriver, AsyncGraphDatabase

@pytest_asyncio.fixture
async def real_neo4j_driver() -> AsyncGenerator[AsyncDriver, None]:
    """Create a real Neo4j driver for testing.

    Yields:
        AsyncDriver: Connected Neo4j driver
    """
    # Async setup
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )

    yield driver

    # Async cleanup
    await driver.close()
```

---

### Template 6: Async Fixture with Database Cleanup

```python
import pytest_asyncio
from collections.abc import AsyncGenerator

@pytest_asyncio.fixture(scope="{{SCOPE}}")
async def {{FIXTURE_NAME}}() -> AsyncGenerator[{{RETURN_TYPE}}, None]:
    """{{FIXTURE_DESCRIPTION}}.

    Yields:
        {{RETURN_TYPE}}: {{RESOURCE_DESCRIPTION}}
    """
    # Create driver
    driver = {{CREATE_DRIVER}}()

    # Clear test data before test
    async with driver.session(database="{{DATABASE_NAME}}") as session:
        await session.run("""
            {{CLEANUP_QUERY}}
        """)

    yield driver

    # Close driver after test
    await driver.close()
```

**Placeholders:**
- `{{SCOPE}}`: Fixture scope (function, module, session)
- `{{FIXTURE_NAME}}`: Fixture name
- `{{RETURN_TYPE}}`: Return type
- `{{FIXTURE_DESCRIPTION}}`: Description
- `{{RESOURCE_DESCRIPTION}}`: Resource description
- `{{CREATE_DRIVER}}`: Driver creation code
- `{{DATABASE_NAME}}`: Database name
- `{{CLEANUP_QUERY}}`: Cypher cleanup query

**Example:**
```python
@pytest_asyncio.fixture(scope="function")
async def real_neo4j_driver() -> AsyncGenerator[AsyncDriver, None]:
    """Create Neo4j driver with clean database state."""
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )

    async with driver.session(database="test_db") as session:
        await session.run("""
            MATCH (n {project_name: 'test_project'})
            DETACH DELETE n
        """)

    yield driver

    await driver.close()
```

---

### Template 7: Async Mock Service

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def {{FIXTURE_NAME}}():
    """Create mock {{SERVICE_NAME}} for testing.

    Returns:
        AsyncMock: Mock {{SERVICE_NAME}} with common methods
    """
    service = AsyncMock()

    # Configure async methods
    service.{{ASYNC_METHOD_1}} = AsyncMock(
        return_value={{RETURN_VALUE_1}}
    )
    service.{{ASYNC_METHOD_2}} = AsyncMock(
        return_value={{RETURN_VALUE_2}}
    )

    return service
```

**Example:**
```python
@pytest.fixture
def mock_embedding_service():
    """Create mock embedding service."""
    service = AsyncMock()
    service.generate_embeddings = AsyncMock(
        return_value=MagicMock(
            success=True,
            data=[[0.1] * 384]
        )
    )
    service.get_embedding = AsyncMock(return_value=[0.1] * 384)
    return service
```

---

## Scoped Fixture Templates

### Template 8: Session-Scoped Fixture

```python
import pytest
from collections.abc import Generator

@pytest.fixture(scope="session")
def {{FIXTURE_NAME}}() -> Generator[{{RETURN_TYPE}}, None, None]:
    """{{FIXTURE_DESCRIPTION}} created once per test session.

    Yields:
        {{RETURN_TYPE}}: {{RESOURCE_DESCRIPTION}}
    """
    # Expensive setup (once per session)
    resource = {{EXPENSIVE_SETUP}}()
    {{OPTIONAL_INITIALIZATION}}

    yield resource

    # Cleanup after all tests
    {{CLEANUP_FUNCTION}}(resource)
```

**Example:**
```python
@pytest.fixture(scope="session")
def neo4j_container() -> Generator[Neo4jContainer, None, None]:
    """Create Neo4j container once per session."""
    from testcontainers.neo4j import Neo4jContainer

    container = Neo4jContainer(image="neo4j:5-enterprise")
    container.start()

    yield container

    container.stop()
```

---

### Template 9: Module-Scoped Fixture

```python
import pytest

@pytest.fixture(scope="module")
def {{FIXTURE_NAME}}():
    """{{FIXTURE_DESCRIPTION}} shared across module.

    Yields:
        {{RETURN_TYPE}}: {{RESOURCE_DESCRIPTION}}
    """
    # Setup once per module
    resource = {{SETUP_FUNCTION}}()

    yield resource

    # Cleanup after module
    {{CLEANUP_FUNCTION}}(resource)
```

---

## Parameterized Fixture Templates

### Template 10: Parameterized Fixture

```python
import pytest

@pytest.fixture(params=[{{PARAM_1}}, {{PARAM_2}}, {{PARAM_3}}])
def {{FIXTURE_NAME}}(request):
    """{{FIXTURE_DESCRIPTION}} with multiple parameter values.

    Yields:
        {{RETURN_TYPE}}: Parameterized value
    """
    return request.param
```

**Example:**
```python
@pytest.fixture(params=[384, 768, 1024])
def embedding_dimensions(request):
    """Parameterized embedding dimensions."""
    return request.param
```

---

### Template 11: Parameterized with IDs

```python
import pytest

@pytest.fixture(
    params=[
        ({{VALUE_1_A}}, {{VALUE_1_B}}),
        ({{VALUE_2_A}}, {{VALUE_2_B}}),
        ({{VALUE_3_A}}, {{VALUE_3_B}})
    ],
    ids=["{{ID_1}}", "{{ID_2}}", "{{ID_3}}"]
)
def {{FIXTURE_NAME}}(request):
    """{{FIXTURE_DESCRIPTION}} with labeled parameters.

    Yields:
        tuple: ({{COMPONENT_1}}, {{COMPONENT_2}})
    """
    {{COMPONENT_1}}, {{COMPONENT_2}} = request.param
    return {"{{KEY_1}}": {{COMPONENT_1}}, "{{KEY_2}}": {{COMPONENT_2}}}
```

**Example:**
```python
@pytest.fixture(
    params=[
        ("voyage", 1024),
        ("openai", 1536),
        ("local", 384)
    ],
    ids=["voyage-1024", "openai-1536", "local-384"]
)
def embedding_config(request):
    """Parameterized embedding configurations."""
    provider, dimensions = request.param
    return {"provider": provider, "dimensions": dimensions}
```

---

## Organization Templates

### Template 12: Utils Module Template

**File: `tests/utils/mock_{{COMPONENT}}.py`**

```python
"""Reusable mock fixtures for {{COMPONENT}} components.

This module provides centralized mock fixtures for {{COMPONENT}} that can be
used across all tests. These mocks can be used directly or customized for
specific test needs.
"""

from unittest.mock import MagicMock{{OPTIONAL_IMPORTS}}
import pytest


@pytest.fixture
def mock_{{COMPONENT}}_minimal():
    """Create minimal mock {{COMPONENT}} for basic testing.

    Returns:
        MagicMock: Mock {{COMPONENT}} with essential attributes
    """
    instance = MagicMock()
    instance.{{ATTRIBUTE_1}} = {{DEFAULT_1}}
    instance.{{ATTRIBUTE_2}} = {{DEFAULT_2}}
    return instance


@pytest.fixture
def mock_{{COMPONENT}}_factory():
    """Factory for custom mock {{COMPONENT}}.

    Returns:
        callable: Function that creates {{COMPONENT}} with custom attributes
    """
    def create_{{COMPONENT}}(**kwargs):
        """Create custom mock {{COMPONENT}}.

        Args:
            **kwargs: Attributes to customize

        Returns:
            MagicMock: Custom {{COMPONENT}}
        """
        instance = MagicMock()
        instance.{{ATTRIBUTE_1}} = kwargs.get("{{PARAM_1}}", {{DEFAULT_1}})
        instance.{{ATTRIBUTE_2}} = kwargs.get("{{PARAM_2}}", {{DEFAULT_2}})
        return instance

    return create_{{COMPONENT}}
```

---

### Template 13: Conftest Import Template

**File: `tests/conftest.py`**

```python
"""Main conftest file to make fixtures available to all tests."""

# Import fixtures from utils to make them available throughout test suite
from tests.utils.mock_{{COMPONENT_1}} import (
    {{FIXTURE_1}},
    {{FIXTURE_2}},
)
from tests.utils.mock_{{COMPONENT_2}} import (
    {{FIXTURE_3}},
    {{FIXTURE_4}},
)

__all__ = [
    # {{COMPONENT_1}} fixtures
    "{{FIXTURE_1}}",
    "{{FIXTURE_2}}",
    # {{COMPONENT_2}} fixtures
    "{{FIXTURE_3}}",
    "{{FIXTURE_4}}",
]
```

---

### Template 14: Layer-Specific Conftest

**File: `tests/{{LAYER}}/conftest.py`**

```python
"""{{LAYER}} test specific fixtures."""

import pytest
{{IMPORTS}}


@pytest.fixture
def {{LAYER}}_specific_fixture():
    """Fixture specific to {{LAYER}} tests.

    Returns:
        {{RETURN_TYPE}}: {{DESCRIPTION}}
    """
    {{IMPLEMENTATION}}
```

**Example for unit tests:**
```python
"""Unit test specific fixtures."""

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_repository():
    """Mock repository for unit tests only."""
    repo = MagicMock()
    repo.save = MagicMock(return_value=True)
    repo.find = MagicMock(return_value=None)
    return repo
```

---

## Special Pattern Templates

### Template 15: Autouse Fixture

```python
import pytest

@pytest.fixture(autouse=True)
def {{FIXTURE_NAME}}():
    """{{FIXTURE_DESCRIPTION}} - runs automatically for all tests.

    This fixture runs before/after every test without being explicitly
    included in test signatures.
    """
    # Setup before each test
    {{SETUP_CODE}}

    yield

    # Cleanup after each test
    {{CLEANUP_CODE}}
```

**Example:**
```python
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test."""
    SingletonClass.reset()
    yield
    SingletonClass.cleanup()
```

---

### Template 16: Conditional Fixture

```python
import pytest

@pytest.fixture
def {{FIXTURE_NAME}}(request):
    """{{FIXTURE_DESCRIPTION}} - behavior depends on test markers.

    Returns:
        {{RETURN_TYPE}}: Mock or real instance based on test marker
    """
    if request.node.get_closest_marker('{{MARKER_NAME}}'):
        # Return real implementation for marked tests
        return {{REAL_IMPLEMENTATION}}()
    else:
        # Return mock for unmarked tests
        from unittest.mock import MagicMock
        return MagicMock(spec={{REAL_IMPLEMENTATION}})
```

**Example:**
```python
@pytest.fixture
def service(request):
    """Return mock or real service based on marker."""
    if request.node.get_closest_marker('integration'):
        return RealService()
    else:
        return MagicMock(spec=RealService)
```

---

### Template 17: Fixture Composition

```python
import pytest

@pytest.fixture
def base_{{COMPONENT}}({{DEPENDENCY_FIXTURE}}):
    """Base {{COMPONENT}} fixture.

    Args:
        {{DEPENDENCY_FIXTURE}}: Dependency fixture

    Returns:
        {{RETURN_TYPE}}: Base {{COMPONENT}}
    """
    return {{CREATE_BASE}}({{DEPENDENCY_FIXTURE}})


@pytest.fixture
def extended_{{COMPONENT}}(base_{{COMPONENT}}):
    """Extended {{COMPONENT}} building on base.

    Args:
        base_{{COMPONENT}}: Base {{COMPONENT}} fixture

    Returns:
        {{RETURN_TYPE}}: Extended {{COMPONENT}}
    """
    base_{{COMPONENT}}.{{ADDITIONAL_ATTRIBUTE}} = {{VALUE}}
    return base_{{COMPONENT}}
```

---

### Template 18: Real Settings Factory

```python
import pytest

@pytest.fixture
def real_{{COMPONENT}}_factory(test_settings):
    """Factory for real {{COMPONENT}} with custom overrides.

    Args:
        test_settings: Base test settings

    Returns:
        callable: Function that creates real {{COMPONENT}} with overrides
    """
    def create_real_{{COMPONENT}}(**overrides):
        """Create real {{COMPONENT}} with overrides.

        Args:
            **overrides: Attributes to override

        Returns:
            {{COMPONENT}}: Real {{COMPONENT}} with overrides
        """
        from copy import deepcopy

        instance = deepcopy(test_settings)

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(instance.{{SECTION_1}}, key):
                setattr(instance.{{SECTION_1}}, key, value)
            elif hasattr(instance.{{SECTION_2}}, key):
                setattr(instance.{{SECTION_2}}, key, value)

        return instance

    return create_real_{{COMPONENT}}
```

---

## Usage Examples for Each Template

### Using Basic Mock Fixture (Template 1)
```python
def test_with_basic_mock(mock_component):
    """Test using basic mock fixture."""
    assert mock_component.attribute_1 == "default_value"
```

### Using Factory Fixture (Template 3)
```python
def test_with_factory(fixture_factory):
    """Test using factory fixture."""
    custom = fixture_factory(param_1="custom", param_2=100)
    assert custom.attribute_1 == "custom"
```

### Using Async Fixture (Template 5)
```python
@pytest.mark.asyncio
async def test_with_async(async_fixture):
    """Test using async fixture."""
    result = await async_fixture.operation()
    assert result is not None
```

### Using Session Fixture (Template 8)
```python
def test_with_session_fixture(session_fixture):
    """Test using session-scoped fixture."""
    # Fixture is shared across all tests
    assert session_fixture.is_initialized
```

### Using Parameterized Fixture (Template 10)
```python
def test_with_params(parameterized_fixture):
    """Test runs multiple times with different values."""
    # Test logic that works with any parameter value
    assert parameterized_fixture is not None
```

---

## Quick Reference

**Choose template based on need:**

1. **Basic mock** → Template 1
2. **Needs cleanup** → Template 2
3. **Needs customization** → Template 3
4. **Success/failure states** → Template 4
5. **Async operations** → Template 5
6. **Database with cleanup** → Template 6
7. **Async service mock** → Template 7
8. **Expensive setup** → Template 8
9. **Module-level sharing** → Template 9
10. **Multiple test variations** → Template 10
11. **Readable test names** → Template 11
12. **Reusable utilities** → Template 12
13. **Project-wide availability** → Template 13
14. **Layer-specific** → Template 14
15. **Auto-run for all tests** → Template 15
16. **Conditional behavior** → Template 16
17. **Build on existing fixture** → Template 17
18. **Real objects with overrides** → Template 18
