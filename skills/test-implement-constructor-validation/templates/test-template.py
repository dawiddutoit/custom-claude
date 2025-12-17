"""
Template: Constructor Validation Tests

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {{SERVICE_NAME}}: Service class name (e.g., UserService, FileProcessor)
- {{PARAM_1}}: First parameter name (e.g., repository)
- {{PARAM_TYPE_1}}: First parameter type (e.g., UserRepository)
- {{PARAM_2}}: Second parameter name (e.g., settings)
- {{PARAM_TYPE_2}}: Second parameter type (e.g., Settings)

Usage: Replace all {{PLACEHOLDERS}} with your actual values

Pattern:
- One fixture per constructor parameter
- One success test (all valid parameters)
- One failure test per parameter (parameter set to None)
- Each failure test excludes the fixture for parameter being tested
"""

import pytest
from unittest.mock import MagicMock

from {{PROJECT_NAME}}.path.to.service import {{SERVICE_NAME}}
from {{PROJECT_NAME}}.path.to.dependency1 import {{PARAM_TYPE_1}}
from {{PROJECT_NAME}}.path.to.dependency2 import {{PARAM_TYPE_2}}
# Add imports for all parameter types


class Test{{SERVICE_NAME}}Constructor:
    """Test {{SERVICE_NAME}} constructor and initialization."""

    # ===== FIXTURES =====
    # Create one fixture per constructor parameter

    @pytest.fixture
    def mock_{{PARAM_1}}(self):
        """Create mock {{PARAM_TYPE_1}}."""
        return MagicMock(spec={{PARAM_TYPE_1}})

    @pytest.fixture
    def mock_{{PARAM_2}}(self):
        """Create mock {{PARAM_TYPE_2}}."""
        return MagicMock(spec={{PARAM_TYPE_2}})

    # Add fixtures for all parameters...
    # For Settings with nested config:
    # @pytest.fixture
    # def mock_settings(self):
    #     """Create mock Settings."""
    #     settings = MagicMock(spec=Settings)
    #     settings.subsection = MagicMock()
    #     settings.subsection.attribute = value
    #     return settings

    # ===== SUCCESS CASE =====
    # Test that constructor works with all valid parameters

    def test_constructor_initializes_with_valid_dependencies(
        self,
        mock_{{PARAM_1}},
        mock_{{PARAM_2}},
        # ... all fixtures
    ):
        """Test that constructor properly initializes with all valid dependencies."""
        instance = {{SERVICE_NAME}}(
            {{PARAM_1}}=mock_{{PARAM_1}},
            {{PARAM_2}}=mock_{{PARAM_2}},
            # ... all parameters
        )

        # Assert all dependencies are assigned
        assert instance.{{PARAM_1}} is mock_{{PARAM_1}}
        assert instance.{{PARAM_2}} is mock_{{PARAM_2}}
        # ... assert all parameters

        # If service creates additional objects in constructor:
        # assert isinstance(instance.created_object, ExpectedType)

    # ===== VALIDATION TESTS =====
    # One test per parameter - each tests that parameter=None raises ValueError

    def test_constructor_fails_when_{{PARAM_1}}_is_none(
        self,
        # EXCLUDE: mock_{{PARAM_1}}  <- This fixture is excluded
        mock_{{PARAM_2}},
        # ... all OTHER fixtures
    ):
        """Test that constructor raises ValueError when {{PARAM_TYPE_1}} is None."""
        with pytest.raises(ValueError) as exc_info:
            {{SERVICE_NAME}}(
                {{PARAM_1}}=None,  # type: ignore
                {{PARAM_2}}=mock_{{PARAM_2}},
                # ... all other parameters with valid values
            )

        # Assert specific error message from service constructor
        assert "{{PARAM_TYPE_1}} is required for {{SERVICE_NAME}}" in str(exc_info.value)

    def test_constructor_fails_when_{{PARAM_2}}_is_none(
        self,
        mock_{{PARAM_1}},
        # EXCLUDE: mock_{{PARAM_2}}  <- This fixture is excluded
        # ... all OTHER fixtures
    ):
        """Test that constructor raises ValueError when {{PARAM_TYPE_2}} is None."""
        with pytest.raises(ValueError) as exc_info:
            {{SERVICE_NAME}}(
                {{PARAM_1}}=mock_{{PARAM_1}},
                {{PARAM_2}}=None,  # type: ignore
                # ... all other parameters with valid values
            )

        # Assert specific error message from service constructor
        assert "{{PARAM_TYPE_2}} is required for {{SERVICE_NAME}}" in str(exc_info.value)

    # Add one test method per parameter following same pattern...


# ===== USAGE INSTRUCTIONS =====

"""
STEP 1: Find and Replace
- {{SERVICE_NAME}} -> Actual service class name (e.g., IndexingOrchestrator)
- {{PARAM_1}}, {{PARAM_2}}, ... -> Constructor parameter names (e.g., settings, indexing_module)
- {{PARAM_TYPE_1}}, {{PARAM_TYPE_2}}, ... -> Parameter type names (e.g., Settings, IndexingModule)

STEP 2: Adjust Fixture Count
- Add/remove fixtures to match number of constructor parameters
- Each parameter needs exactly one fixture

STEP 3: Update Success Test
- Include all fixtures as parameters
- Pass all mocks to constructor
- Assert all dependencies are assigned

STEP 4: Create Validation Tests
- One test per parameter
- Each test excludes its own fixture
- Each test passes None for one parameter
- Each test asserts specific error message

STEP 5: Verify Error Messages
- Read service constructor to find exact error message text
- Update assertion to match: "{{Type}} is required for {{Service}}"

STEP 6: Run Tests
```bash
uv run pytest path/to/test_file.py::Test{{SERVICE_NAME}}Constructor -v
```

STEP 7: Run Type Checking
```bash
uv run pyright path/to/test_file.py
```
Should pass with no errors (# type: ignore suppresses intentional None assignments)
"""
