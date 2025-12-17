"""Neo4j implementation of the {Name}Repository interface.

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {Name}: Repository name (e.g., User, Product)
- {name}: Lowercase name (e.g., user, product)
- {Entity}: Entity class name (e.g., User, Product)
- {entity}: Lowercase entity name (e.g., user, product)
- {entities}: Plural entity name (e.g., users, products)
- {purpose}: Purpose description (e.g., "user account", "product inventory")

This module provides the concrete implementation of the {Name}Repository port
for Neo4j database storage, following Clean Architecture principles.
"""

from typing import Any, LiteralString, cast

from neo4j import AsyncDriver, RoutingControl
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from {{PROJECT_NAME}}.config.settings import Settings
from {{PROJECT_NAME}}.core.monitoring import get_logger
from {{PROJECT_NAME}}.domain.common import ServiceResult
from {{PROJECT_NAME}}.domain.repositories.{name}_repository import {Name}Repository
from {{PROJECT_NAME}}.domain.services.resource_manager import ManagedResource
# Import domain models as needed
# from {{PROJECT_NAME}}.domain.models.{model} import {Model}
from {{PROJECT_NAME}}.infrastructure.neo4j.queries import CypherQueries
from {{PROJECT_NAME}}.infrastructure.neo4j.query_builder import validate_and_build_query

logger = get_logger(__name__)


class Neo4j{Name}Repository({Name}Repository, ManagedResource):
    """Neo4j adapter implementing the {Name}Repository interface.

    This adapter handles all {purpose} operations using Neo4j graph database,
    including connection pooling, retries, and explicit database specification.
    """

    def __init__(self, driver: AsyncDriver, settings: Settings):
        """Initialize the Neo4j {name} repository.

        Args:
            driver: Neo4j async driver instance
            settings: Application settings containing Neo4j configuration
        """
        if not driver:
            raise ValueError("Neo4j driver is required")
        if not settings:
            raise ValueError("Settings is required")

        self.driver = driver
        self.settings = settings
        self.database = settings.neo4j.database_name
        self.max_retries = settings.neo4j.max_retries
        self.initial_retry_delay = settings.neo4j.initial_retry_delay
        self.retry_delay_multiplier = settings.neo4j.retry_delay_multiplier
        self.max_retry_delay = settings.neo4j.max_retry_delay

    async def _execute_with_retry(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        routing: RoutingControl = RoutingControl.WRITE,
    ) -> ServiceResult[list[dict]]:
        """Execute a query with parameter validation and retry logic.

        Args:
            query: Cypher query to execute
            parameters: Query parameters
            routing: Routing control for read/write operations

        Returns:
            ServiceResult containing query results or validation error
        """
        # VALIDATE BEFORE EXECUTING
        validation_result = validate_and_build_query(query, parameters, strict=True)
        if validation_result.is_failure:
            logger.error(f"Query validation failed: {validation_result.error}")
            return ServiceResult.fail(f"Parameter validation failed: {validation_result.error}")

        validated_query = validation_result.data
        assert validated_query is not None

        # Log validation warnings even if query is valid
        if validated_query.validation_result.warnings:
            for warning in validated_query.validation_result.warnings:
                logger.warning(f"Query validation warning: {warning}")

        # Use driver.execute_query for automatic transaction management and retries
        try:
            # Driver.execute_query returns tuple (records, summary, keys)
            # Use validated parameters
            records, _, _ = await self.driver.execute_query(
                cast(LiteralString, validated_query.query),
                validated_query.parameters,
                database_=self.database,
                routing_=routing,
            )
            # Convert records to list of dicts
            data = [dict(record) for record in records]
            return ServiceResult.ok(data)
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            return ServiceResult.fail(f"Database unavailable: {str(e)}")
        except Neo4jError as e:
            logger.error(f"Neo4j error: {e}")
            return ServiceResult.fail(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return ServiceResult.fail(f"Unexpected error: {str(e)}")

    async def save_{entity}(self, {entity}: {Entity}) -> ServiceResult[None]:
        """Save or update {entity} in Neo4j.

        Args:
            {entity}: {Entity} entity to save

        Returns:
            ServiceResult[None]: Success if saved, Failure on database errors
        """
        query = CypherQueries.SAVE_{ENTITY}

        parameters = {
            "id": {entity}.id,
            "project_name": {entity}.project_name,
            # Add other properties
            # "property": {entity}.property,
        }

        result = await self._execute_with_retry(query, parameters)
        if not result.success:
            logger.error(f"Failed to save {entity}: {result.error}")
            return ServiceResult.fail(f"Failed to save {entity}: {result.error}")

        return ServiceResult.ok(None)

    async def get_{entity}(
        self, {entity}_id: str, project_name: str
    ) -> ServiceResult[{Entity} | None]:
        """Retrieve {entity} by ID.

        Args:
            {entity}_id: Unique identifier for the {entity}
            project_name: Name of the project

        Returns:
            ServiceResult[{Entity} | None]: Success with {Entity} if found,
                                            Success with None if not found,
                                            Failure on database errors
        """
        query = CypherQueries.GET_{ENTITY}

        parameters = {"id": {entity}_id, "project_name": project_name}

        result = await self._execute_with_retry(query, parameters, routing=RoutingControl.READ)
        if not result.success:
            logger.error(f"Failed to get {entity} {{{entity}_id}}: {result.error}")
            return ServiceResult.fail(f"Database error retrieving {entity}: {result.error}")

        data = result.data
        if not data:
            return ServiceResult.ok(None)  # {Entity} not found (expected)

        # Transform Neo4j record to domain model
        {entity}_data = data[0]["e"]
        {entity}_model = self._to_domain_model({entity}_data, project_name)

        return ServiceResult.ok({entity}_model)

    async def get_{entities}_by_project(
        self, project_name: str
    ) -> ServiceResult[list[{Entity}]]:
        """Retrieve all {entities} for a project.

        Args:
            project_name: Name of the project

        Returns:
            ServiceResult[list[{Entity}]]: Success with list of {Entity} entities,
                                           Failure on database errors
        """
        query = CypherQueries.GET_{ENTITIES}_BY_PROJECT

        parameters = {"project_name": project_name}

        result = await self._execute_with_retry(query, parameters, routing=RoutingControl.READ)
        if not result.success:
            logger.error(f"Failed to get {entities} for project {{project_name}}: {result.error}")
            return ServiceResult.fail(f"Database error retrieving {entities}: {result.error}")

        data = result.data
        {entities} = []
        for record in data:
            {entity}_data = record["e"]
            {entity}_model = self._to_domain_model({entity}_data, project_name)
            {entities}.append({entity}_model)

        return ServiceResult.ok({entities})

    async def delete_{entity}(
        self, {entity}_id: str, project_name: str
    ) -> ServiceResult[None]:
        """Delete {entity}.

        Args:
            {entity}_id: Unique identifier for the {entity}
            project_name: Name of the project

        Returns:
            ServiceResult indicating success or failure
        """
        query = CypherQueries.DELETE_{ENTITY}

        parameters = {"id": {entity}_id, "project_name": project_name}

        result = await self._execute_with_retry(query, parameters)
        if not result.success:
            return ServiceResult.fail(f"Failed to delete {entity}: {result.error}")

        return ServiceResult.ok(None)

    async def {entity}_exists(
        self, {entity}_id: str, project_name: str
    ) -> ServiceResult[bool]:
        """Check if {entity} exists.

        Args:
            {entity}_id: Unique identifier for the {entity}
            project_name: Name of the project

        Returns:
            ServiceResult containing True if exists, False otherwise
        """
        query = CypherQueries.{ENTITY}_EXISTS

        parameters = {"id": {entity}_id, "project_name": project_name}

        result = await self._execute_with_retry(query, parameters, routing=RoutingControl.READ)
        if not result.success:
            return ServiceResult.fail(f"Failed to check {entity} existence: {result.error}")

        data = result.data
        exists = data[0]["exists"] if (data and len(data) > 0) else False
        return ServiceResult.ok(exists)

    def _to_domain_model(self, data: dict, project_name: str) -> {Entity}:
        """Convert Neo4j record to {Entity} domain model.

        Args:
            data: Neo4j record data
            project_name: Name of the project

        Returns:
            {Entity} domain model
        """
        # TODO: Implement conversion logic
        # Example:
        # return {Entity}(
        #     identity=Identity(
        #         value=data["id"],
        #         entity_type="{entity}",
        #         project_name=project_name,
        #     ),
        #     # Add other properties
        # )
        raise NotImplementedError("Domain model conversion not implemented")

    async def close(self) -> None:
        """Close and cleanup Neo4j driver resources.

        Implements the ManagedResource protocol for proper resource cleanup.
        This method is idempotent and handles errors gracefully.

        Note: The driver itself is managed externally (by container),
        so we don't close it here. This is a placeholder for any
        repository-specific cleanup if needed in the future.
        """
        try:
            # Currently no repository-specific resources to clean up
            # The driver is managed by the container
            logger.debug(f"Neo4j{Name}Repository cleanup complete")
        except Exception as e:
            logger.error(f"Error during Neo4j{Name}Repository cleanup: {e}")
            # Don't raise - cleanup should be best-effort
