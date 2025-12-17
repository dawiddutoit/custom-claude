"""Template for creating services with dependency injection.

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)

This template demonstrates proper patterns for:
- Required dependency injection (no Optional parameters)
- Settings validation
- Clean Architecture layer positioning
- Type safety
- Container integration
"""

from {{PROJECT_NAME}}.config.settings import Settings
from {{PROJECT_NAME}}.domain.common.service_result import ServiceResult

# Example: Infrastructure Layer Repository
# Location: src/{{PROJECT_NAME}}/infrastructure/mymodule/my_repository.py


class MyRepository:
    """Repository for [describe purpose].

    Follows Clean Architecture - Infrastructure Layer.
    Manages data access for [domain concept].
    """

    def __init__(self, driver, settings: Settings):
        """Initialize repository with required dependencies.

        Args:
            driver: Neo4j async driver instance
            settings: Application settings (required, never None)

        Raises:
            ValueError: If driver or settings is None
        """
        if not driver:
            raise ValueError("Neo4j driver required")
        if not settings:
            raise ValueError("Settings required")

        self.driver = driver
        self.settings = settings

    async def get_data(self, query: str) -> ServiceResult[dict]:
        """Retrieve data using dependency-injected driver.

        Args:
            query: Query parameter

        Returns:
            ServiceResult containing data or error
        """
        try:
            # Use injected dependencies
            result = await self.driver.execute_query(query)
            return ServiceResult.ok(result)
        except Exception as e:
            return ServiceResult.failure(f"Query failed: {e}")


# Example: Application Layer Service
# Location: src/{{PROJECT_NAME}}/application/services/my_service.py


class MyService:
    """Service for [describe business logic].

    Follows Clean Architecture - Application Layer.
    Coordinates business operations using repositories.
    """

    def __init__(self, repository: MyRepository, settings: Settings):
        """Initialize service with required dependencies.

        Args:
            repository: Data access repository (required, never None)
            settings: Application settings (required, never None)

        Raises:
            ValueError: If repository or settings is None
        """
        if not repository:
            raise ValueError("Repository required")
        if not settings:
            raise ValueError("Settings required")

        self.repository = repository
        self.settings = settings

    async def perform_operation(self, input_data: str) -> ServiceResult[str]:
        """Execute business operation.

        Args:
            input_data: Input for operation

        Returns:
            ServiceResult containing result or error
        """
        # Validate with settings
        if len(input_data) > self.settings.project.max_input_length:
            return ServiceResult.failure("Input exceeds max length")

        # Use injected repository
        result = await self.repository.get_data(input_data)

        if not result.success:
            return ServiceResult.failure(f"Repository error: {result.error}")

        return ServiceResult.ok(f"Processed: {result.data}")


# Example: Command Handler
# Location: src/{{PROJECT_NAME}}/application/commands/my_command.py


class MyCommandHandler:
    """Handler for MyCommand.

    Follows Clean Architecture - Application Layer.
    Orchestrates services to fulfill command.
    """

    def __init__(
        self,
        service: MyService,
        auxiliary_service: "AuxiliaryService",
        settings: Settings,
    ):
        """Initialize handler with required dependencies.

        Args:
            service: Primary service for operation
            auxiliary_service: Supporting service
            settings: Application settings

        Raises:
            ValueError: If any dependency is None
        """
        if not service:
            raise ValueError("Service required")
        if not auxiliary_service:
            raise ValueError("Auxiliary service required")
        if not settings:
            raise ValueError("Settings required")

        self.service = service
        self.auxiliary_service = auxiliary_service
        self.settings = settings

    async def handle(self, command: "MyCommand") -> ServiceResult[str]:
        """Handle command execution.

        Args:
            command: Command to execute

        Returns:
            ServiceResult containing result or error
        """
        # Orchestrate multiple services
        primary_result = await self.service.perform_operation(command.data)

        if not primary_result.success:
            return primary_result

        auxiliary_result = await self.auxiliary_service.validate(primary_result.data)

        if not auxiliary_result.success:
            return ServiceResult.failure(f"Validation failed: {auxiliary_result.error}")

        return ServiceResult.ok(auxiliary_result.data)


# Container Integration
# Location: src/{{PROJECT_NAME}}/interfaces/mcp/container.py
"""
Add to Container class:

# Infrastructure Layer - Repositories
my_repository = providers.Singleton(
    MyRepository,
    driver=neo4j_driver,
    settings=settings,
)

# Application Layer - Services
my_service = providers.Singleton(
    MyService,
    repository=my_repository,
    settings=settings,
)

auxiliary_service = providers.Singleton(
    AuxiliaryService,
    settings=settings,
)

# Application Layer - Command Handlers
my_command_handler = providers.Factory(
    MyCommandHandler,
    service=my_service,
    auxiliary_service=auxiliary_service,
    settings=settings,
)
"""

# Test Integration
# Location: tests/integration/{{PROJECT_NAME}}_module/conftest.py
"""
@pytest.fixture
def container(real_settings):
    '''Create container with test overrides.'''
    container = Container()

    # Override dependencies
    container.settings.override(real_settings)

    # Mock external dependencies
    mock_driver = AsyncMock()
    container.neo4j_driver.override(mock_driver)

    return container

def test_service_receives_dependencies(container):
    '''Test dependency injection.'''
    service = container.my_service()

    # Verify dependencies injected
    assert service.repository is not None
    assert service.settings is not None
    assert isinstance(service.settings, Settings)

def test_handler_orchestrates_services(container):
    '''Test handler uses multiple services.'''
    handler = container.my_command_handler()

    # Verify all dependencies injected
    assert handler.service is not None
    assert handler.auxiliary_service is not None
    assert handler.settings is not None
"""

# Anti-Patterns to Avoid

# ❌ WRONG - Optional settings
"""
class BadService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or self._create_default()  # NEVER DO THIS
"""

# ❌ WRONG - Creating dependencies internally
"""
class BadService:
    def __init__(self):
        self.settings = Settings()  # NEVER create your own
        self.repository = MyRepository(driver, self.settings)  # NEVER instantiate
"""

# ❌ WRONG - No validation
"""
class BadService:
    def __init__(self, settings: Settings):
        self.settings = settings  # Missing validation - fails late
"""

# ✅ CORRECT - Required with validation
"""
class GoodService:
    def __init__(self, settings: Settings):
        if not settings:
            raise ValueError("Settings required")  # Fail fast
        self.settings = settings
"""

# Usage Pattern

"""
# In application code:
container = Container()
container.settings.override(actual_settings)
container.neo4j_driver.override(actual_driver)

# Get service from container - dependencies injected automatically
service = container.my_service()

# Service ready to use - all dependencies present
result = await service.perform_operation("input")
"""

# Provider Selection Guide

"""
Choose provider type based on lifecycle:

1. providers.Singleton:
   - Repositories (MyRepository)
   - Services (MyService, AuxiliaryService)
   - Expensive initialization (embeddings, ML models)
   - Shared state needed

2. providers.Factory:
   - Handlers (MyCommandHandler)
   - Request-scoped objects
   - Stateless operations
   - New instance per invocation

3. providers.Dependency:
   - Settings (configuration)
   - External connections (driver)
   - Runtime-provided dependencies
"""

# Quality Checklist

"""
Before committing:

- [ ] Constructor requires all dependencies (no Optional)
- [ ] Constructor validates all dependencies (raises ValueError if None)
- [ ] Added to Container in correct layer section
- [ ] Correct provider type (Singleton/Factory/Dependency)
- [ ] Dependencies defined before service in container.py
- [ ] Test fixture overrides dependencies
- [ ] Type annotations present
- [ ] Pyright passes: uv run pyright src/
- [ ] Tests pass: uv run pytest tests/
"""
