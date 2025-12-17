"""Template for Command Handler implementation.

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {{COMMAND_NAME}}: Your command name (e.g., IndexFile)
- {{command_name}}: Lowercase command name (e.g., index_file)
- {{OPERATION}}: What the command does (e.g., "index file")

USAGE:
1. Copy this template to application/commands/your_handler.py
2. Replace {{COMMAND_NAME}} with your command name (e.g., IndexFile)
3. Replace {{command_name}} with lowercase version (e.g., index_file)
4. Replace {{OPERATION}} with what the command does (e.g., "index file")
5. Replace {{PROJECT_NAME}} with your project's base package name
6. Add your dependencies to __init__
7. Implement business logic in handle()
8. Add validation in _validate()
"""

from {{PROJECT_NAME}}.application.commands.base import CommandHandler
from {{PROJECT_NAME}}.application.commands.{{command_name}}_command import (
    {{COMMAND_NAME}}Command,
)
from {{PROJECT_NAME}}.core.monitoring import get_logger, traced
from {{PROJECT_NAME}}.domain.common import ServiceResult

# Add your repository/service imports here
# from {{PROJECT_NAME}}.domain.repositories.your_repository import YourRepository

logger = get_logger(__name__)


class {{COMMAND_NAME}}Handler(CommandHandler[{{COMMAND_NAME}}Command]):
    """Handler for {{COMMAND_NAME}}Command.

    Orchestrates the {{OPERATION}} operation using domain services.
    Commands modify system state and return ServiceResult[None].
    """

    def __init__(
        self,
        # Add your dependencies here
        # repository: YourRepository,
        # service: YourService,
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
    async def handle(self, command: {{COMMAND_NAME}}Command) -> ServiceResult[None]:
        """Execute the {{OPERATION}} command.

        Args:
            command: The command to execute

        Returns:
            ServiceResult indicating success or failure.
            Commands always return ServiceResult[None].
        """
        try:
            # Step 1: Validate command parameters
            logger.info(f"Executing {{OPERATION}}: {command}")
            validation = self._validate(command)
            if not validation.success:
                logger.warning(f"Validation failed: {validation.error}")
                return validation

            # Step 2: Execute business logic
            # Replace with your implementation
            # result = await self.service.do_work(command.param1)
            # if not result.success:
            #     logger.error(f"Business logic failed: {result.error}")
            #     return ServiceResult.fail(result.error)

            # Step 3: Persist changes
            # Replace with your implementation
            # save_result = await self.repository.save(result.data)
            # if not save_result.success:
            #     logger.error(f"Save failed: {save_result.error}")
            #     return ServiceResult.fail(f"Failed to save: {save_result.error}")

            # Step 4: Return success with metadata
            logger.info(f"{{OPERATION}} completed successfully")
            return ServiceResult.ok(
                None,
                # Add metadata about what was done
                # items_processed=1,
                # operation="{{command_name}}",
            )

        except ValueError as e:
            # Expected validation errors
            logger.warning(f"Validation error: {str(e)}")
            return ServiceResult.fail(f"Invalid input: {str(e)}")

        except Exception as e:
            # Unexpected errors - log with full stacktrace
            logger.exception(f"Unexpected error in {{OPERATION}}: {str(e)}")
            return ServiceResult.fail(f"System error: {str(e)}")

    def _validate(self, command: {{COMMAND_NAME}}Command) -> ServiceResult[None]:
        """Validate command parameters.

        Args:
            command: The command to validate

        Returns:
            ServiceResult indicating validation success or failure
        """
        # Add your validation logic here
        # if not command.param1:
        #     return ServiceResult.fail("param1 is required")
        # if command.param2 < 0:
        #     return ServiceResult.fail("param2 must be non-negative")

        return ServiceResult.ok(None)
