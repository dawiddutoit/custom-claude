"""Template: Service with OTEL Instrumentation

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {{SERVICE_NAME}}: Name of your service class
- {{OPERATION_NAME}}: Name of the operation/method
- {{PARAM_NAME}}: Parameter names
- {{RETURN_TYPE}}: Return type (typically ServiceResult[T])

Usage: Copy this template and replace placeholders with the above variables.
"""

from {{PROJECT_NAME}}.core.monitoring import get_logger, traced, trace_span
from {{PROJECT_NAME}}.domain.common import ServiceResult

logger = get_logger(__name__)


class {{SERVICE_NAME}}:
    """Service description.

    Responsibilities:
    - Primary responsibility
    - Secondary responsibility
    """

    def __init__(self, dependency: DependencyType):
        """Initialize service with required dependencies.

        Args:
            dependency: Description of dependency

        Raises:
            ValueError: If dependency is None
        """
        if not dependency:
            raise ValueError("Dependency required")
        self.dependency = dependency

    @traced
    async def {{OPERATION_NAME}}(
        self, {{PARAM_NAME}}: ParamType
    ) -> {{RETURN_TYPE}}:
        """Execute operation with full OTEL instrumentation.

        Args:
            {{PARAM_NAME}}: Description of parameter

        Returns:
            ServiceResult with operation outcome
        """
        logger.info(f"Starting {{OPERATION_NAME}}: {{{PARAM_NAME}}}")

        try:
            # Step 1: Validation
            validation_result = self._validate({{PARAM_NAME}})
            if not validation_result.success:
                logger.warning(f"Validation failed: {validation_result.error}")
                return validation_result

            # Step 2: Execute with manual span for expensive operation
            with trace_span("expensive_operation", param={{PARAM_NAME}}) as span:
                logger.debug("Executing expensive operation")
                result = await self._execute({{PARAM_NAME}})
                span.set_attribute("operation_success", result.success)
                span.set_attribute("items_processed", len(result.data))

            # Step 3: Post-processing
            logger.info(f"{{OPERATION_NAME}} completed successfully")
            return ServiceResult.ok(result.data)

        except Exception as e:
            logger.error(f"{{OPERATION_NAME}} failed: {str(e)}")
            return ServiceResult.fail(f"Operation failed: {str(e)}")

    def _validate(self, {{PARAM_NAME}}: ParamType) -> ServiceResult[None]:
        """Validate input (private method, no tracing needed)."""
        if not {{PARAM_NAME}}:
            return ServiceResult.fail("Parameter required")
        return ServiceResult.ok(None)

    async def _execute(self, {{PARAM_NAME}}: ParamType) -> ServiceResult[Data]:
        """Execute core logic (private method, traced via parent)."""
        # Implementation
        pass


# =============================================================================
# Alternative Template: MCP Tool with OTEL
# =============================================================================

@traced
async def {{TOOL_NAME}}(
    {{PARAM_NAME}}: ParamType,
    optional_param: str | None = None,
) -> dict:
    """MCP tool description.

    Args:
        {{PARAM_NAME}}: Description
        optional_param: Optional parameter description

    Returns:
        Dictionary with operation results
    """
    logger.info(
        f"MCP {{TOOL_NAME}} called: {{PARAM_NAME}}={{{PARAM_NAME}}}, "
        f"optional={optional_param or 'none'}"
    )

    try:
        # Execute via handler
        result = await handler.handle(Command({{PARAM_NAME}}, optional_param))

        if result.success:
            logger.info(f"MCP {{TOOL_NAME}} completed successfully")
            return {
                "success": True,
                "data": result.data,
            }
        else:
            logger.error(f"MCP {{TOOL_NAME}} failed: {result.error}")
            return {
                "success": False,
                "error": result.error,
            }

    except Exception as e:
        logger.error(f"MCP {{TOOL_NAME}} exception: {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }


# =============================================================================
# Alternative Template: Repository with OTEL
# =============================================================================

class {{REPOSITORY_NAME}}:
    """Repository description."""

    @traced
    async def save(self, entity: Entity) -> ServiceResult[None]:
        """Save entity to persistence layer.

        Args:
            entity: Entity to save

        Returns:
            ServiceResult indicating success or failure
        """
        logger.info(f"Saving entity: {entity.id}")

        with trace_span("database_transaction", operation="CREATE") as span:
            try:
                await self.session.run(query, entity_data=entity.to_dict())
                span.set_attribute("transaction_success", True)
                logger.debug(f"Entity saved successfully: {entity.id}")
                return ServiceResult.ok(None)

            except DatabaseError as e:
                span.set_attribute("transaction_success", False)
                span.set_attribute("error", str(e))
                logger.error(f"Database error saving entity: {str(e)}")
                return ServiceResult.fail(f"Database error: {str(e)}")

    @traced
    async def find_by_id(self, entity_id: str) -> ServiceResult[Entity | None]:
        """Find entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            ServiceResult with entity or None if not found
        """
        logger.info(f"Finding entity by ID: {entity_id}")

        with trace_span("database_query", operation="SELECT", id=entity_id) as span:
            result = await self.session.run(query, entity_id=entity_id)
            records = [record async for record in result]

            span.set_attribute("records_found", len(records))

            if not records:
                logger.debug(f"Entity not found: {entity_id}")
                return ServiceResult.ok(None)

            logger.debug(f"Entity found: {entity_id}")
            return ServiceResult.ok(self._map_to_entity(records[0]))


# =============================================================================
# Alternative Template: Multi-Step Operation with Correlation Context
# =============================================================================

from {{PROJECT_NAME}}.core.monitoring import correlation_context

class {{ORCHESTRATOR_NAME}}:
    """Orchestrator for complex multi-step operations."""

    @traced
    async def orchestrate(
        self, items: list[Item]
    ) -> ServiceResult[list[Result]]:
        """Orchestrate multi-step operation with correlation tracking.

        Args:
            items: Items to process

        Returns:
            ServiceResult with processing results
        """
        # Create correlation context for entire operation
        with correlation_context() as cid:
            logger.info(
                f"Starting orchestration: {len(items)} items (correlation_id: {cid})"
            )

            results = []
            failed_count = 0

            for idx, item in enumerate(items):
                logger.debug(
                    f"Processing item {idx + 1}/{len(items)}: {item.id}"
                )

                # Each step includes same correlation_id
                result = await self._process_item(item)

                if result.success:
                    results.append(result.data)
                else:
                    failed_count += 1
                    logger.warning(f"Failed to process {item.id}: {result.error}")

            logger.info(
                f"Orchestration complete: {len(results)} succeeded, "
                f"{failed_count} failed (correlation_id: {cid})"
            )

            return ServiceResult.ok(
                results,
                metadata={
                    "total": len(items),
                    "succeeded": len(results),
                    "failed": failed_count,
                    "correlation_id": cid,
                },
            )

    @traced
    async def _process_item(self, item: Item) -> ServiceResult[Result]:
        """Process single item (automatically inherits correlation context)."""
        logger.debug(f"Processing item: {item.id}")

        with trace_span("item_processing", item_id=item.id) as span:
            # Step 1: Validate
            with trace_span("validate_item") as validation_span:
                validation = await self._validate(item)
                validation_span.set_attribute("valid", validation.success)

            if not validation.success:
                return validation

            # Step 2: Transform
            with trace_span("transform_item") as transform_span:
                transformed = await self._transform(item)
                transform_span.set_attribute("transformed", True)

            # Step 3: Store
            with trace_span("store_item") as store_span:
                store_result = await self._store(transformed)
                store_span.set_attribute("stored", store_result.success)

            span.set_attribute("processing_complete", True)
            return store_result
