"""
Template for implementing retry logic with exponential backoff.

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {{SERVICE_NAME}}: Service class name (e.g., DatabaseService, APIClient)
- {{SERVICE_DESCRIPTION}}: Description of what the service does
- {{SERVICE_SECTION}}: Settings section for this service (e.g., neo4j, embedding)
- {{METHOD_NAME}}: Public method name (e.g., create_database, generate_embeddings)
- {{METHOD_PARAMS}}: Method parameters (e.g., database_name: str)
- {{RETURN_TYPE}}: Return type (e.g., str, list[list[float]])
- {{RETRIABLE_EXCEPTION_1}}: Exception type (e.g., ConnectionError)
- {{PERMANENT_EXCEPTION}}: Exception type (e.g., ValueError)
- {{OPERATION_METHOD}}: Internal operation method (e.g., _create_database)

Replace {{PLACEHOLDERS}} with actual values for your use case.

Usage:
    1. Copy this template to your service file
    2. Replace all {{PLACEHOLDERS}}
    3. Add to config/settings.py: max_retries and retry_delay
    4. Import required dependencies
    5. Test with mock failures
"""

import asyncio
import time
from typing import TypeVar

from {{PROJECT_NAME}}.config.settings import Settings
from {{PROJECT_NAME}}.domain.models.result import ServiceResult
from {{PROJECT_NAME}}.core.monitoring import get_logger

logger = get_logger(__name__)
T = TypeVar("T")


class {{SERVICE_NAME}}:
    """{{SERVICE_DESCRIPTION}}."""

    def __init__(self, settings: Settings):
        """Initialize service with required settings.

        Args:
            settings: Application settings (must not be None)

        Raises:
            ValueError: If settings is None
        """
        if not settings:
            raise ValueError("Settings required")

        self.settings = settings
        self.max_retries = settings.{{SERVICE_SECTION}}.max_retries
        self.retry_delay = settings.{{SERVICE_SECTION}}.retry_delay

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds with jitter
        """
        # Exponential backoff: base * 2^attempt, capped at 30s
        delay = min(self.retry_delay * (2**attempt), 30.0)

        # Add jitter to avoid thundering herd (±20%)
        jitter = delay * 0.2 * (2 * (time.time() % 1) - 1)

        return max(0.1, delay + jitter)

    def _is_retriable_error(self, error: Exception, status_code: int | None = None) -> bool:
        """Determine if error should be retried.

        Args:
            error: Exception that occurred
            status_code: HTTP status code if applicable

        Returns:
            True if error is retriable
        """
        # HTTP status codes
        if status_code:
            # 429 Rate Limited - retriable
            if status_code == 429:
                return True

            # 5xx Server errors - retriable
            if 500 <= status_code < 600:
                return True

            # 408 Request Timeout - retriable
            if status_code == 408:
                return True

            # 4xx Client errors (except above) - NOT retriable
            if 400 <= status_code < 500:
                return False

        # {{ADD_YOUR_RETRIABLE_EXCEPTIONS}}
        # Example: Network/connection errors - retriable
        if isinstance(
            error,
            (
                # {{REPLACE_WITH_YOUR_RETRIABLE_EXCEPTIONS}}
                ConnectionError,
                TimeoutError,
                # aiohttp.ClientConnectionError,
                # aiohttp.ServerDisconnectedError,
            ),
        ):
            return True

        # {{ADD_YOUR_PERMANENT_EXCEPTIONS}}
        # Example: Validation errors - NOT retriable
        if isinstance(
            error,
            (
                # {{REPLACE_WITH_YOUR_PERMANENT_EXCEPTIONS}}
                ValueError,
                TypeError,
                KeyError,
            ),
        ):
            return False

        # Default: fail fast (not retriable)
        return False

    async def {{METHOD_NAME}}_with_retry(
        self, {{METHOD_PARAMS}}
    ) -> ServiceResult[{{RETURN_TYPE}}]:
        """{{METHOD_DESCRIPTION}} with retry logic.

        Args:
            {{METHOD_PARAMS_DESCRIPTION}}

        Returns:
            ServiceResult with {{RETURN_TYPE}} or error
        """
        last_error: str = ""

        for attempt in range(self.max_retries):
            try:
                # {{PERFORM_OPERATION}}
                # Example:
                # result = await self._perform_operation({{METHOD_PARAMS}})
                # return ServiceResult.ok(result)
                result = await self._{{OPERATION_METHOD}}({{METHOD_PARAMS}})
                return ServiceResult.ok(result)

            except {{RETRIABLE_EXCEPTION_1}} as e:
                # {{RETRIABLE_EXCEPTION_1_DESCRIPTION}}
                last_error = f"{{ERROR_CATEGORY_1}}: {e}"

                if attempt < self.max_retries - 1:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        f"{last_error}. Retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)

            except {{RETRIABLE_EXCEPTION_2}} as e:
                # {{RETRIABLE_EXCEPTION_2_DESCRIPTION}}
                last_error = f"{{ERROR_CATEGORY_2}}: {e}"

                if attempt < self.max_retries - 1:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        f"{last_error}. Retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)

            except {{PERMANENT_EXCEPTION}} as e:
                # {{PERMANENT_EXCEPTION_DESCRIPTION}}
                # Do NOT retry - fail immediately
                logger.error(f"{{ERROR_CATEGORY_PERMANENT}} (non-retriable): {e}")
                return ServiceResult.fail(
                    f"{{ERROR_CATEGORY_PERMANENT}}: {e}",
                    error_type="{{ERROR_TYPE}}",
                    recoverable=False,
                )

            except Exception as e:
                # Unexpected error - fail fast
                logger.error(f"Unexpected error in {{METHOD_NAME}}: {e}")
                return ServiceResult.fail(f"Unexpected error: {e}")

        # All retries exhausted
        return ServiceResult.fail(f"Failed after {self.max_retries} retries: {last_error}")


# ==============================================================================
# CONFIGURATION TEMPLATE
# ==============================================================================

"""
Add to config/settings.py:

@dataclass
class {{SERVICE_NAME}}Settings:
    \"\"\"{{SERVICE_NAME}} configuration.\"\"\"

    # {{SERVICE_SPECIFIC_SETTINGS}}
    {{SERVICE_SETTING_1}}: {{TYPE_1}}
    {{SERVICE_SETTING_2}}: {{TYPE_2}}

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0

    @classmethod
    def from_env(cls) -> "{{SERVICE_NAME}}Settings":
        return cls(
            {{SERVICE_SETTING_1}}={{ENV_VAR_1}},
            {{SERVICE_SETTING_2}}={{ENV_VAR_2}},
            max_retries=int(os.getenv("{{SERVICE_NAME_UPPER}}_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("{{SERVICE_NAME_UPPER}}_RETRY_DELAY", "1.0")),
        )
"""


# ==============================================================================
# TEST TEMPLATE
# ==============================================================================

"""
Add to tests/unit/{{MODULE}}/test_{{SERVICE_NAME}}_retry.py:

import pytest
from unittest.mock import AsyncMock, patch

class Test{{SERVICE_NAME}}Retry:
    @pytest.fixture
    def service(self, settings):
        return {{SERVICE_NAME}}(settings)

    async def test_success_on_first_attempt(self, service):
        \"\"\"Test that successful operation doesn't retry.\"\"\"
        with patch.object(service, "_{{OPERATION_METHOD}}") as mock_op:
            mock_op.return_value = {{SUCCESS_VALUE}}

            result = await service.{{METHOD_NAME}}_with_retry({{TEST_PARAMS}})

            assert result.is_success
            assert mock_op.call_count == 1  # No retry needed

    async def test_retry_on_transient_error(self, service):
        \"\"\"Test retry on retriable errors.\"\"\"
        with patch.object(service, "_{{OPERATION_METHOD}}") as mock_op:
            # Fail twice, then succeed
            mock_op.side_effect = [
                {{RETRIABLE_EXCEPTION_1}}("{{ERROR_MESSAGE_1}}"),
                {{RETRIABLE_EXCEPTION_2}}("{{ERROR_MESSAGE_2}}"),
                {{SUCCESS_VALUE}}
            ]

            result = await service.{{METHOD_NAME}}_with_retry({{TEST_PARAMS}})

            assert result.is_success
            assert mock_op.call_count == 3  # 2 failures + 1 success

    async def test_no_retry_on_permanent_error(self, service):
        \"\"\"Test that permanent errors fail immediately.\"\"\"
        with patch.object(service, "_{{OPERATION_METHOD}}") as mock_op:
            mock_op.side_effect = {{PERMANENT_EXCEPTION}}("{{PERMANENT_ERROR_MESSAGE}}")

            result = await service.{{METHOD_NAME}}_with_retry({{TEST_PARAMS}})

            assert result.is_failure
            assert mock_op.call_count == 1  # No retry
            assert "{{ERROR_CATEGORY_PERMANENT}}" in result.error

    async def test_max_retries_exhausted(self, service):
        \"\"\"Test behavior when all retries fail.\"\"\"
        with patch.object(service, "_{{OPERATION_METHOD}}") as mock_op:
            mock_op.side_effect = {{RETRIABLE_EXCEPTION_1}}("{{ERROR_MESSAGE_1}}")

            result = await service.{{METHOD_NAME}}_with_retry({{TEST_PARAMS}})

            assert result.is_failure
            assert mock_op.call_count == service.max_retries
            assert "Failed after 3 retries" in result.error

    async def test_exponential_backoff(self, service):
        \"\"\"Test that delays increase exponentially.\"\"\"
        delays: list[float] = []

        async def mock_sleep(delay: float):
            delays.append(delay)

        with patch.object(service, "_{{OPERATION_METHOD}}") as mock_op:
            with patch("asyncio.sleep", side_effect=mock_sleep):
                mock_op.side_effect = {{RETRIABLE_EXCEPTION_1}}("{{ERROR_MESSAGE_1}}")

                await service.{{METHOD_NAME}}_with_retry({{TEST_PARAMS}})

                # Verify exponential increase (accounting for jitter)
                assert len(delays) == service.max_retries - 1
                assert delays[0] < delays[1]  # Second delay > first delay
"""


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

"""
Example 1: Database Operation

Replace:
    {{SERVICE_NAME}} = DatabaseService
    {{SERVICE_DESCRIPTION}} = Neo4j database operations
    {{SERVICE_SECTION}} = neo4j
    {{METHOD_NAME}} = create_database
    {{METHOD_PARAMS}} = database_name: str
    {{RETURN_TYPE}} = str
    {{RETRIABLE_EXCEPTION_1}} = ConnectionError
    {{RETRIABLE_EXCEPTION_2}} = TimeoutError
    {{PERMANENT_EXCEPTION}} = ValueError

Example 2: API Call

Replace:
    {{SERVICE_NAME}} = EmbeddingService
    {{SERVICE_DESCRIPTION}} = External embedding API client
    {{SERVICE_SECTION}} = embedding
    {{METHOD_NAME}} = generate_embeddings
    {{METHOD_PARAMS}} = texts: list[str]
    {{RETURN_TYPE}} = list[list[float]]
    {{RETRIABLE_EXCEPTION_1}} = aiohttp.ClientConnectionError
    {{RETRIABLE_EXCEPTION_2}} = TimeoutError
    {{PERMANENT_EXCEPTION}} = ValueError
"""
