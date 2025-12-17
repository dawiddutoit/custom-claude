"""Template for Query Handler implementation.

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {{QUERY_NAME}}: Your query name (e.g., SearchCode)
- {{query_name}}: Lowercase query name (e.g., search_code)
- {{RESULT_TYPE}}: Return type (e.g., list[SearchResultDTO])
- {{OPERATION}}: What the query does (e.g., "search code")

USAGE:
1. Copy this template to application/queries/your_handler.py
2. Replace {{QUERY_NAME}} with your query name (e.g., SearchCode)
3. Replace {{query_name}} with lowercase version (e.g., search_code)
4. Replace {{RESULT_TYPE}} with return type (e.g., list[SearchResultDTO])
5. Replace {{OPERATION}} with what the query does (e.g., "search code")
6. Replace {{PROJECT_NAME}} with your project's base package name
7. Add your dependencies to __init__
8. Implement data retrieval in handle()
9. Create DTO in application/dto/ if needed
"""

from {{PROJECT_NAME}}.application.queries.base import QueryHandler
from {{PROJECT_NAME}}.application.queries.{{query_name}} import {{QUERY_NAME}}Query

# Import your DTO
# from {{PROJECT_NAME}}.application.dto.{{query_name}}_dto import {{QUERY_NAME}}DTO

from {{PROJECT_NAME}}.core.monitoring import get_logger, traced
from {{PROJECT_NAME}}.domain.common import ServiceResult

# Add your repository imports here
# from {{PROJECT_NAME}}.domain.repositories.your_repository import YourRepository

logger = get_logger(__name__)


class {{QUERY_NAME}}Handler(QueryHandler[{{QUERY_NAME}}Query, {{RESULT_TYPE}}]):
    """Handler for {{QUERY_NAME}}Query.

    Retrieves data without modifying system state.
    Queries return ServiceResult[TResult] with the requested data.
    """

    def __init__(
        self,
        # Add your dependencies here
        # repository: YourRepository,
    ):
        """Initialize the handler with required services.

        Args:
            Add your dependency documentation here
        """
        # Validate all dependencies (fail-fast principle)
        # if not repository:
        #     raise ValueError("Repository required")

        # Store dependencies
        # self.repository = repository

    @traced
    async def handle(self, query: {{QUERY_NAME}}Query) -> ServiceResult[{{RESULT_TYPE}}]:
        """Execute the {{OPERATION}} query.

        Args:
            query: The query to execute

        Returns:
            ServiceResult containing the requested data or error.
            Queries return ServiceResult[TResult], not ServiceResult[None].
        """
        try:
            # Step 1: Validate query parameters
            logger.info(f"Executing {{OPERATION}}: {query}")
            if not self._validate_query(query):
                return ServiceResult.fail("Invalid query parameters")

            # Step 2: Fetch data from repository
            # Replace with your implementation
            # result = await self.repository.find_by_criteria(
            #     filter=query.filter,
            #     limit=query.limit
            # )
            # if not result.success:
            #     logger.error(f"Query failed: {result.error}")
            #     return ServiceResult.fail(result.error)

            # Step 3: Convert to DTOs
            # Replace with your implementation
            # dtos = [
            #     {{QUERY_NAME}}DTO.from_entity(entity)
            #     for entity in result.data
            # ]

            # Placeholder return - replace with actual DTOs
            dtos = []

            # Step 4: Return results with metadata
            logger.info(f"{{OPERATION}} returned {len(dtos)} results")
            return ServiceResult.ok(
                dtos,
                metadata={
                    "total_results": len(dtos),
                    # Add any other relevant metadata
                    # "query": query.filter,
                    # "execution_time_ms": 100,
                },
            )

        except ValueError as e:
            # Expected validation errors
            logger.warning(f"Validation error: {str(e)}")
            return ServiceResult.fail(f"Invalid query: {str(e)}")

        except Exception as e:
            # Unexpected errors - log with full stacktrace
            logger.exception(f"Unexpected error in {{OPERATION}}: {str(e)}")
            return ServiceResult.fail(f"System error: {str(e)}")

    def _validate_query(self, query: {{QUERY_NAME}}Query) -> bool:
        """Validate query parameters.

        Args:
            query: The query to validate

        Returns:
            True if valid, False otherwise
        """
        # Add your validation logic here
        # if query.limit < 1:
        #     logger.warning("Limit must be at least 1")
        #     return False
        # if not query.filter:
        #     logger.warning("Filter is required")
        #     return False

        return True
