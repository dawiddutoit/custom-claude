# Template: Factory Fixture Template
# Usage: Replace {{FIXTURE_NAME}}, {{THING_TYPE}}, and {{PARAMETER_*}} placeholders

"""Reusable mock fixtures for {{THING_TYPE}} components.

This module provides centralized mock fixtures for {{THING_TYPE}} that can be
used across all tests. These mocks can be used directly or customized for
specific test needs.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


# Pattern A: Simple Mock Factory
@pytest.fixture
def mock_{{FIXTURE_NAME}}_factory():
    """Create a factory for custom mock {{THING_TYPE}}.

    Returns:
        callable: Function that creates {{THING_TYPE}} with custom parameters

    Example:
        def test_something(mock_{{FIXTURE_NAME}}_factory):
            thing = mock_{{FIXTURE_NAME}}_factory(param1=value1)
            # Use thing in test
    """

    def create_{{FIXTURE_NAME}}(
        {{PARAMETER_1}}={{DEFAULT_1}},
        {{PARAMETER_2}}={{DEFAULT_2}},
        success=True,
        error_message=None,
    ):
        """Create custom mock {{THING_TYPE}}.

        Args:
            {{PARAMETER_1}}: Description of parameter 1 (default: {{DEFAULT_1}})
            {{PARAMETER_2}}: Description of parameter 2 (default: {{DEFAULT_2}})
            success: Whether the mock should return success (default: True)
            error_message: Error message for failure cases (default: None)

        Returns:
            AsyncMock: Custom {{THING_TYPE}} instance
        """
        mock_thing = AsyncMock()

        if success:
            # Configure success behavior
            mock_thing.{{METHOD_NAME}} = AsyncMock(
                return_value=MagicMock(
                    success=True,
                    data={{SUCCESS_DATA}},
                )
            )
        else:
            # Configure failure behavior
            mock_thing.{{METHOD_NAME}} = AsyncMock(
                return_value=MagicMock(
                    success=False,
                    error=error_message or "{{DEFAULT_ERROR_MESSAGE}}",
                )
            )

        return mock_thing

    return create_{{FIXTURE_NAME}}


# Pattern B: Settings/Config Factory (Using **kwargs)
@pytest.fixture
def mock_{{FIXTURE_NAME}}_settings_factory():
    """Create a factory for custom mock settings.

    Returns:
        callable: Function that creates settings with custom attributes

    Example:
        def test_something(mock_{{FIXTURE_NAME}}_settings_factory):
            settings = mock_{{FIXTURE_NAME}}_settings_factory(
                attribute1=value1,
                attribute2=value2,
            )
            # Use settings in test
    """

    def create_settings(**kwargs):
        """Create custom mock settings with specified attributes.

        Args:
            **kwargs: Attributes to set on the settings object

        Returns:
            MagicMock: Custom settings object
        """
        settings = MagicMock()

        # Set default structure
        settings.{{CATEGORY_1}} = MagicMock()
        settings.{{CATEGORY_2}} = MagicMock()

        # Apply defaults with kwargs overrides
        settings.{{CATEGORY_1}}.{{ATTRIBUTE_1}} = kwargs.get(
            "{{ATTRIBUTE_1}}", {{DEFAULT_VALUE_1}}
        )
        settings.{{CATEGORY_1}}.{{ATTRIBUTE_2}} = kwargs.get(
            "{{ATTRIBUTE_2}}", {{DEFAULT_VALUE_2}}
        )
        settings.{{CATEGORY_2}}.{{ATTRIBUTE_3}} = kwargs.get(
            "{{ATTRIBUTE_3}}", {{DEFAULT_VALUE_3}}
        )

        return settings

    return create_settings


# Pattern C: Real Instance Factory (With Mock Dependencies)
@pytest.fixture
def mock_real_{{FIXTURE_NAME}}_factory(
    {{DEPENDENCY_1}}_fixture,
    {{DEPENDENCY_2}}_fixture,
):
    """Create a factory for real {{THING_TYPE}} instances with mock dependencies.

    Args:
        {{DEPENDENCY_1}}_fixture: Mock dependency 1
        {{DEPENDENCY_2}}_fixture: Mock dependency 2

    Returns:
        callable: Function that creates real {{THING_TYPE}} instances

    Example:
        def test_something(mock_real_{{FIXTURE_NAME}}_factory):
            instance = mock_real_{{FIXTURE_NAME}}_factory(
                param1=value1,
                param2=value2,
            )
            # Use real instance with mocked dependencies
    """

    def create_instance(**kwargs):
        """Create real {{THING_TYPE}} instance with custom settings.

        Args:
            **kwargs: Parameters to customize instance creation

        Returns:
            {{THING_TYPE}}: Real instance with mocked dependencies
        """
        from {{IMPORT_PATH}} import {{THING_TYPE}}

        # Extract parameters with defaults
        param1 = kwargs.get("param1", {{DEFAULT_PARAM_1}})
        param2 = kwargs.get("param2", {{DEFAULT_PARAM_2}})

        # Create real instance with injected mocks
        return {{THING_TYPE}}(
            {{DEPENDENCY_1}}={{DEPENDENCY_1}}_fixture,
            {{DEPENDENCY_2}}={{DEPENDENCY_2}}_fixture,
            param1=param1,
            param2=param2,
        )

    return create_instance


# Pattern D: Data/Result Factory
@pytest.fixture
def mock_{{FIXTURE_NAME}}_result():
    """Create a factory for mock {{THING_TYPE}} results.

    Returns:
        callable: Function that creates result mocks

    Example:
        def test_something(mock_{{FIXTURE_NAME}}_result):
            result = mock_{{FIXTURE_NAME}}_result(
                success=True,
                data={"key": "value"}
            )
            # Use result in test
    """

    def create_result(success=True, data=None, error=None):
        """Create mock result.

        Args:
            success: Whether the result is successful (default: True)
            data: Data for successful result (default: None)
            error: Error message for failed result (default: None)

        Returns:
            MagicMock: Mock result object
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

    return create_result
