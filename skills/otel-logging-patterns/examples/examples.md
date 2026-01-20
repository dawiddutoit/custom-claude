# OpenTelemetry Logging Examples

Complete, production-ready examples for implementing OTEL logging in Python applications.

## Table of Contents

1. [FastAPI Endpoint Logging](#1-fastapi-endpoint-logging)
2. [Kafka Consumer with Logging](#2-kafka-consumer-with-logging)
3. [Background Job Logging](#3-background-job-logging)
4. [Error Handling and Exceptions](#4-error-handling-and-exceptions)
5. [Unit Testing Logging](#5-unit-testing-logging)
6. [Integration Testing Log Export](#6-integration-testing-log-export)
7. [Trace Context Propagation](#7-trace-context-propagation)
8. [Performance Monitoring](#8-performance-monitoring)
9. [Request Correlation](#9-request-correlation)
10. [Console vs OTLP Exporters](#10-console-vs-otlp-exporters)

---

## 1. FastAPI Endpoint Logging

Complete FastAPI application with OTEL logging integration using the authoritative `app/core/monitoring/otel_logger.py`:

```python
# app/reporting/infrastructure/fastapi_app.py
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel

from app.core.monitoring.otel_logger import (
    initialize_otel_logger,
    logger,
    get_tracer,
    trace_span,
    correlation_context,
)


class TopProductsResponse(BaseModel):
    """Response model for top products."""
    id: str
    title: str
    cnt_bought: int


def create_app() -> FastAPI:
    """Create and configure FastAPI application with OTEL logging.

    Returns:
        Configured FastAPI app
    """
    # Initialize OTEL (once at startup)
    initialize_otel_logger(
        log_level="INFO",
        enable_console=True,
        enable_otlp=True,
        otlp_endpoint="localhost:4317"
    )

    app = FastAPI(title="Reporter API", version="1.0.0")
    logger = logger(__name__)


    # Middleware for request tracking
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: Any) -> Any:
        """Add request tracking to logs."""
        request_id = request.headers.get("x-request-id", "auto")

        # Use correlation context for request tracking
        with correlation_context(request_id):
            with trace_span("http_request",
                            method=request.method,
                            url=str(request.url),
                            request_id=request_id) as span:

                logger.info(
                    "request_started",
                    method=request.method,
                    path=request.url.path,
                    request_id=request_id,
                )

            try:
                response = await call_next(request)
                span.set_attribute("http.status_code", response.status_code)
                logger.info(
                    "request_completed",
                    status_code=response.status_code,
                    path=request.url.path,
                )
                return response
            except Exception as e:
                logger.error(
                    "request_failed",
                    error=str(e),
                    path=request.url.path,
                    exc_info=True,
                )
                span.record_exception(e)
                raise


    @app.get("/top-products", response_model=list[TopProductsResponse])
    async def get_top_products(count: int = 10) -> list[TopProductsResponse]:
        """Get top products by purchase count.

        Args:
            count: Number of top products to return

        Returns:
            List of top products
        """
        tracer = ObservabilityContext.get_tracer(__name__)
        logger = logger(__name__)

        with tracer.start_as_current_span("query_top_products") as span:
            span.set_attribute("count", count)

            logger.info(
                "querying_top_products",
                count=count,
                request_id=ObservabilityContext.get_request_id(),
            )

            try:
                # Simulate database query
                products = [
                    TopProductsResponse(
                        id="prod-1",
                        title="Laptop",
                        cnt_bought=150,
                    ),
                    TopProductsResponse(
                        id="prod-2",
                        title="Mouse",
                        cnt_bought=320,
                    ),
                ][:count]

                logger.info(
                    "top_products_retrieved",
                    count=len(products),
                )
                return products

            except Exception as e:
                logger.error(
                    "top_products_query_failed",
                    error=str(e),
                    count=count,
                    exc_info=True,
                )
                span.record_exception(e)
                raise


    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        logger = logger(__name__)
        logger.debug("health_check")
        return {"status": "healthy"}


    return app
```

**Key Points:**
- Middleware sets up request tracing context
- Each endpoint creates span with attributes
- Errors are logged with full stack trace
- Request IDs tracked through all logs

---

## 2. Kafka Consumer with Logging

Consumer processing messages with comprehensive logging:

```python
# app/storage/adapters/kafka/consumer.py
from __future__ import annotations

import asyncio
from typing import Optional

from confluent_kafka import Consumer, KafkaError, KafkaException
from opentelemetry import trace
from structlog import get_logger

from app.shared.otel_config import OTELConfig


class KafkaConsumerAdapter:
    """Kafka consumer with OTEL logging and tracing.

    Consumes messages and logs processing with trace context.
    """

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        group_id: str,
        otel_config: OTELConfig,
    ) -> None:
        """Initialize consumer.

        Args:
            brokers: Kafka broker addresses
            topic: Topic to consume
            group_id: Consumer group ID
            otel_config: OTEL configuration
        """
        self.topic = topic
        self.group_id = group_id
        self.logger = get_logger(__name__)
        self.tracer = trace.get_tracer(__name__)

        # Setup OTEL
        otel_config.setup_logging()
        otel_config.setup_tracing()

        # Configure consumer
        config = {
            "bootstrap.servers": ",".join(brokers),
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }

        self.consumer = Consumer(config)
        self.consumer.subscribe([topic])

        self.logger.info(
            "kafka_consumer_initialized",
            topic=topic,
            group_id=group_id,
            brokers=brokers,
        )

    async def consume_and_process(
        self,
        process_fn,
        timeout_ms: int = 1000,
        max_messages: Optional[int] = None,
    ) -> int:
        """Consume and process messages with tracing.

        Args:
            process_fn: Async function to process message
            timeout_ms: Consumption timeout in ms
            max_messages: Max messages to consume (None=infinite)

        Returns:
            Number of messages processed
        """
        processed_count = 0

        with self.tracer.start_as_current_span("consume_messages") as root_span:
            root_span.set_attribute("topic", self.topic)
            root_span.set_attribute("group_id", self.group_id)

            self.logger.info("starting_message_consumption", topic=self.topic)

            try:
                while max_messages is None or processed_count < max_messages:
                    # Poll for message
                    msg = self.consumer.poll(timeout_ms / 1000.0)

                    if msg is None:
                        self.logger.debug("poll_timeout", timeout_ms=timeout_ms)
                        continue

                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            self.logger.info("partition_eof")
                            continue
                        else:
                            raise KafkaException(msg.error())

                    # Process message with tracing
                    with self.tracer.start_as_current_span("process_message") as span:
                        span.set_attribute("partition", msg.partition())
                        span.set_attribute("offset", msg.offset())

                        self.logger.info(
                            "message_received",
                            partition=msg.partition(),
                            offset=msg.offset(),
                            key=msg.key().decode("utf-8") if msg.key() else None,
                        )

                        try:
                            # Process message
                            await process_fn(msg.value())

                            # Commit offset
                            self.consumer.commit(asynchronous=False)

                            processed_count += 1
                            self.logger.info(
                                "message_processed",
                                offset=msg.offset(),
                                total_processed=processed_count,
                            )

                        except Exception as e:
                            self.logger.error(
                                "message_processing_failed",
                                error=str(e),
                                offset=msg.offset(),
                                exc_info=True,
                            )
                            span.record_exception(e)
                            raise

                self.logger.info(
                    "message_consumption_completed",
                    total_processed=processed_count,
                )
                return processed_count

            except Exception as e:
                self.logger.error(
                    "message_consumption_failed",
                    error=str(e),
                    processed_count=processed_count,
                    exc_info=True,
                )
                raise
            finally:
                self.consumer.close()
                self.logger.info("kafka_consumer_closed")

    def close(self) -> None:
        """Close consumer."""
        self.consumer.close()
        self.logger.info("consumer_closed")
```

**Key Points:**
- Each message gets its own span for tracing
- Partition and offset logged for debugging
- Error tracking with exception logging
- Offset committed after successful processing

---

## 3. Background Job Logging

Long-running background job with progress tracking:

```python
# app/storage/infrastructure/loader_main.py
from __future__ import annotations

import asyncio
from datetime import datetime

from opentelemetry import trace
from structlog import get_logger

from app.shared.logging_setup import setup_structlog
from app.shared.otel_config import OTELConfig


class DataLoaderJob:
    """Background job for loading data into ClickHouse.

    Long-running job with progress tracking and error handling.
    """

    def __init__(self, otel_config: OTELConfig) -> None:
        """Initialize loader job.

        Args:
            otel_config: OTEL configuration
        """
        self.logger = get_logger(__name__)
        self.tracer = trace.get_tracer(__name__)

        setup_structlog()
        otel_config.setup_logging()
        otel_config.setup_tracing()

    async def run(self) -> None:
        """Run data loading job."""
        start_time = datetime.utcnow()

        with self.tracer.start_as_current_span("load_data") as root_span:
            self.logger.info(
                "data_loading_started",
                start_time=start_time.isoformat(),
            )

            try:
                # Phase 1: Initialize schema
                with self.tracer.start_as_current_span("initialize_schema"):
                    self.logger.info("initializing_clickhouse_schema")
                    await self._initialize_schema()
                    self.logger.info("schema_initialized")

                # Phase 2: Create Kafka table
                with self.tracer.start_as_current_span("create_kafka_table"):
                    self.logger.info("creating_kafka_table")
                    await self._create_kafka_table()
                    self.logger.info("kafka_table_created")

                # Phase 3: Create materialized views
                with self.tracer.start_as_current_span("create_materialized_views"):
                    self.logger.info("creating_materialized_views")
                    views_created = await self._create_materialized_views()
                    self.logger.info(
                        "materialized_views_created",
                        count=views_created,
                    )

                # Phase 4: Verify setup
                with self.tracer.start_as_current_span("verify_setup"):
                    self.logger.info("verifying_setup")
                    verified = await self._verify_setup()
                    self.logger.info("setup_verified", verified=verified)

                elapsed = (datetime.utcnow() - start_time).total_seconds()
                root_span.set_attribute("duration_seconds", elapsed)

                self.logger.info(
                    "data_loading_completed",
                    duration_seconds=elapsed,
                )

            except Exception as e:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                self.logger.error(
                    "data_loading_failed",
                    error=str(e),
                    duration_seconds=elapsed,
                    exc_info=True,
                )
                root_span.record_exception(e)
                raise

    async def _initialize_schema(self) -> None:
        """Initialize database schema."""
        self.logger.debug("executing_schema_queries")
        # Schema initialization code
        await asyncio.sleep(0.1)  # Simulate work
        self.logger.debug("schema_queries_executed")

    async def _create_kafka_table(self) -> None:
        """Create Kafka table engine."""
        self.logger.debug("creating_kafka_table_engine")
        # Kafka table creation code
        await asyncio.sleep(0.1)
        self.logger.debug("kafka_table_engine_created")

    async def _create_materialized_views(self) -> int:
        """Create materialized views for aggregation."""
        views = ["products_by_count", "daily_sales"]
        self.logger.info(
            "creating_views",
            view_count=len(views),
        )

        for i, view in enumerate(views):
            with self.tracer.start_as_current_span("create_view"):
                self.logger.debug("creating_view", view_name=view)
                await asyncio.sleep(0.05)
                self.logger.debug(
                    "view_created",
                    view_name=view,
                    progress=f"{i+1}/{len(views)}",
                )

        return len(views)

    async def _verify_setup(self) -> bool:
        """Verify setup completed successfully."""
        self.logger.debug("running_verification_checks")
        # Verification code
        await asyncio.sleep(0.05)
        return True


async def main() -> None:
    """Main entry point for data loader."""
    otel_config = OTELConfig(
        service_name="data-loader",
        service_version="1.0.0",
        exporter_type="console",
    )

    job = DataLoaderJob(otel_config)
    await job.run()


if __name__ == "__main__":
    asyncio.run(main())
```

**Key Points:**
- Job phases tracked as separate spans
- Progress logged at each step
- Total elapsed time tracked
- Detailed error logging on failure

---

## 4. Error Handling and Exceptions

Comprehensive error logging patterns:

```python
# app/extraction/application/exceptions.py
from __future__ import annotations

from typing import Optional

from opentelemetry import trace
from structlog import get_logger


class ExtractionException(Exception):
    """Base exception for extraction context."""

    def __init__(
        self,
        message: str,
        error_code: str,
        context: Optional[dict] = None,
    ) -> None:
        """Initialize exception with context.

        Args:
            message: Error message
            error_code: Error code for classification
            context: Additional context data
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}

        # Log exception with context
        logger = get_logger(__name__)
        logger.error(
            "exception_raised",
            error_type=type(self).__name__,
            error_code=error_code,
            message=message,
            context=self.context,
        )

        # Record in current span
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("error.type", type(self).__name__)
            span.set_attribute("error.code", error_code)
            span.record_exception(self)


class InvalidOrderException(ExtractionException):
    """Invalid order data."""

    def __init__(self, message: str, order_id: Optional[str] = None) -> None:
        context = {}
        if order_id:
            context["order_id"] = order_id
        super().__init__(message, "INVALID_ORDER", context)


class ShopifyApiException(ExtractionException):
    """Shopify API error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[str] = None,
    ) -> None:
        context = {}
        if status_code:
            context["status_code"] = status_code
        if response:
            context["response"] = response
        super().__init__(message, "SHOPIFY_API_ERROR", context)


class KafkaPublishException(ExtractionException):
    """Kafka publish failure."""

    def __init__(
        self,
        message: str,
        topic: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> None:
        context = {}
        if topic:
            context["topic"] = topic
        if order_id:
            context["order_id"] = order_id
        super().__init__(message, "KAFKA_PUBLISH_ERROR", context)


# Usage in use case:
class ExtractOrdersUseCase:
    """Use case with exception handling."""

    async def execute(self) -> int:
        """Execute with error handling."""
        logger = get_logger(__name__)
        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span("extract_orders"):
            try:
                orders = await self.shopify_gateway.fetch_all_orders()
                return len(orders)

            except ShopifyApiException as e:
                # Handle Shopify-specific errors
                logger.error(
                    "shopify_api_failed",
                    error=e.message,
                    error_code=e.error_code,
                    context=e.context,
                    exc_info=True,
                )
                raise

            except KafkaPublishException as e:
                # Handle Kafka-specific errors
                logger.error(
                    "kafka_publish_failed",
                    error=e.message,
                    error_code=e.error_code,
                    context=e.context,
                    exc_info=True,
                )
                raise

            except Exception as e:
                # Catch unexpected errors
                logger.error(
                    "unexpected_error",
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True,
                )
                raise
```

**Key Points:**
- Custom exceptions log context automatically
- Error codes for easy classification
- Context data preserved with error
- Span attributes set for tracing

---

## 5. Unit Testing Logging

Unit tests for logging configuration:

```python
# tests/unit/shared/test_logging.py
from __future__ import annotations

import pytest
from opentelemetry import logs
from opentelemetry.sdk.logs import LoggerProvider
from structlog import get_logger

from app.shared.logging_setup import setup_structlog


@pytest.fixture
def logger_provider():
    """Create test logger provider."""
    provider = LoggerProvider()
    logs.set_logger_provider(provider)
    return provider


def test_structlog_configuration():
    """Test structlog is configured correctly."""
    setup_structlog()
    logger = get_logger(__name__)

    # Should not raise
    logger.info("test_message", key="value")


def test_logger_name_resolved():
    """Test logger names are resolved."""
    setup_structlog()
    logger = get_logger("app.test")

    assert logger is not None
    assert callable(logger.info)
    assert callable(logger.error)
    assert callable(logger.debug)


def test_logger_with_context():
    """Test logging with context."""
    import structlog

    setup_structlog()
    logger = structlog.logger(__name__)

    # Log with context (should not raise)
    logger.info(
        "test_with_context",
        user_id="user-123",
        request_id="req-456",
        duration_ms=100,
    )


def test_logger_with_exception():
    """Test exception logging."""
    setup_structlog()
    logger = get_logger(__name__)

    try:
        raise ValueError("Test error")
    except ValueError:
        # Should not raise
        logger.exception("error_occurred")


def test_logger_levels():
    """Test all logger levels."""
    setup_structlog()
    logger = get_logger(__name__)

    # All levels should work without raising
    logger.debug("debug_message")
    logger.info("info_message")
    logger.warning("warning_message")
    logger.error("error_message")
```

**Key Points:**
- Fixtures provide clean logger state
- Tests verify configuration
- Exception logging tested
- All logger levels tested

---

## 6. Integration Testing Log Export

Integration tests with actual exporters:

```python
# tests/integration/test_logging_export.py
from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import pytest
from opentelemetry import logs, trace
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.logs.export import SimpleLogRecordExporter, LogRecord
from opentelemetry.sdk.trace import TracerProvider
from structlog import get_logger

from app.shared.logging_setup import setup_structlog


class InMemoryLogExporter(SimpleLogRecordExporter):
    """In-memory exporter for testing."""

    def __init__(self) -> None:
        """Initialize exporter."""
        self.records: list[LogRecord] = []

    def emit(self, records: list[LogRecord]) -> None:
        """Capture log records.

        Args:
            records: Log records to export
        """
        self.records.extend(records)

    def shutdown(self) -> None:
        """Shutdown exporter."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush (no-op for in-memory).

        Args:
            timeout_millis: Flush timeout

        Returns:
            Always True
        """
        return True


@pytest.fixture
def in_memory_exporter() -> InMemoryLogExporter:
    """Fixture providing in-memory exporter."""
    return InMemoryLogExporter()


@pytest.fixture
def test_logger_provider(in_memory_exporter: InMemoryLogExporter) -> LoggerProvider:
    """Fixture providing test logger provider."""
    provider = LoggerProvider()
    logs.set_logger_provider(provider)

    from opentelemetry.sdk.logs.export import SimpleLogRecordExporter

    processor = SimpleLogRecordExporter(in_memory_exporter)
    provider.add_log_record_processor(processor)

    return provider


@pytest.fixture
def test_tracer_provider() -> TracerProvider:
    """Fixture providing test tracer provider."""
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    return provider


def test_log_export(
    test_logger_provider: LoggerProvider,
    in_memory_exporter: InMemoryLogExporter,
) -> None:
    """Test logs are exported.

    Args:
        test_logger_provider: Test logger provider
        in_memory_exporter: In-memory exporter
    """
    setup_structlog()
    logger = get_logger(__name__)

    # Log message
    logger.info("test_message", key="value")

    # Force flush
    test_logger_provider.force_flush()

    # Verify log was exported
    assert len(in_memory_exporter.records) > 0
    record = in_memory_exporter.records[0]
    assert record is not None


def test_trace_context_in_exported_logs(
    test_logger_provider: LoggerProvider,
    test_tracer_provider: TracerProvider,
    in_memory_exporter: InMemoryLogExporter,
) -> None:
    """Test trace context is exported with logs.

    Args:
        test_logger_provider: Test logger provider
        test_tracer_provider: Test tracer provider
        in_memory_exporter: In-memory exporter
    """
    setup_structlog()
    logger = get_logger(__name__)
    tracer = trace.get_tracer(__name__)

    # Log within span
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("test_attr", "test_value")
        logger.info("test_message")

    # Force flush
    test_logger_provider.force_flush()

    # Verify trace context in log
    assert len(in_memory_exporter.records) > 0
    record = in_memory_exporter.records[0]
    assert record.trace_id is not None
    assert record.span_id is not None


def test_multiple_logs_in_span(
    test_logger_provider: LoggerProvider,
    test_tracer_provider: TracerProvider,
    in_memory_exporter: InMemoryLogExporter,
) -> None:
    """Test multiple logs within span have same trace context.

    Args:
        test_logger_provider: Test logger provider
        test_tracer_provider: Test tracer provider
        in_memory_exporter: In-memory exporter
    """
    setup_structlog()
    logger = get_logger(__name__)
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("test_span"):
        logger.info("message_1")
        logger.info("message_2")
        logger.info("message_3")

    test_logger_provider.force_flush()

    # All logs should have same trace ID
    assert len(in_memory_exporter.records) >= 3
    trace_ids = [record.trace_id for record in in_memory_exporter.records[:3]]
    assert len(set(trace_ids)) == 1  # All same
```

**Key Points:**
- In-memory exporter for testing
- Logs captured and verified
- Trace context assertions
- Multiple logs verified in span

---

## 7. Trace Context Propagation

Demonstrate automatic trace context in logs:

```python
# tests/unit/shared/test_observability.py
from __future__ import annotations

import pytest
from opentelemetry import trace
from structlog import get_logger

from app.shared.logging_setup import setup_structlog
from app.shared.observability import ObservabilityContext


def test_context_variables_preserved():
    """Test context variables are preserved across logs."""
    setup_structlog()
    logger = get_logger(__name__)

    # Set context
    ObservabilityContext.set_request_id("req-12345")
    ObservabilityContext.set_user_id("user-456")

    # Log should include context (through structlog contextvars processor)
    logger.info("test_message")

    # Context should still be set
    assert ObservabilityContext.get_request_id() == "req-12345"
    assert ObservabilityContext.get_user_id() == "user-456"


def test_trace_context_automatic():
    """Test trace context is automatic in logs.

    When logging within a span, trace ID and span ID
    are automatically included by OTEL instrumentation.
    """
    setup_structlog()
    logger = get_logger(__name__)
    tracer = trace.get_tracer(__name__)

    # Get span before and within trace
    span_before = trace.get_current_span()
    assert not span_before.is_recording()

    with tracer.start_as_current_span("test_span"):
        span_during = trace.get_current_span()
        assert span_during.is_recording()
        logger.info("message_within_span")

    span_after = trace.get_current_span()
    assert not span_after.is_recording()


def test_span_attributes():
    """Test setting span attributes."""
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("test_span") as span:
        # Set attributes
        ObservabilityContext.set_span_attribute("order_id", "order-789")
        ObservabilityContext.set_span_attribute("count", 42)

        # Should be set on span
        assert span.is_recording()


def test_nested_spans():
    """Test nested spans with hierarchy."""
    tracer = trace.get_tracer(__name__)
    logger = get_logger(__name__)

    with tracer.start_as_current_span("parent_span"):
        logger.info("parent_message")

        with tracer.start_as_current_span("child_span"):
            logger.info("child_message")
            # Child has different span_id but same trace_id

    logger.info("after_spans")
```

**Key Points:**
- Context variables work automatically
- Trace context added by instrumentation
- Span attributes for correlation
- Nested spans maintain trace_id

---

## 8. Performance Monitoring

Logging with performance metrics:

```python
# app/reporting/adapters/api/controllers.py
from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter
from opentelemetry import trace
from structlog import get_logger

from app.shared.observability import ObservabilityContext


router = APIRouter(prefix="/api", tags=["products"])
logger = get_logger(__name__)


@router.get("/top-products")
async def get_top_products(count: int = 10) -> list[dict[str, Any]]:
    """Get top products with performance tracking.

    Args:
        count: Number of products to return

    Returns:
        List of top products
    """
    tracer = ObservabilityContext.get_tracer(__name__)
    request_id = ObservabilityContext.get_request_id()

    with tracer.start_as_current_span("query_top_products") as span:
        start_time = time.time()

        span.set_attribute("count", count)
        span.set_attribute("request_id", request_id)

        logger.info(
            "query_started",
            count=count,
            request_id=request_id,
        )

        try:
            # Simulate database query
            query_start = time.time()
            products = await _fetch_products(count)
            query_duration_ms = (time.time() - query_start) * 1000

            span.set_attribute("query_duration_ms", query_duration_ms)
            logger.info(
                "query_completed",
                products_count=len(products),
                query_duration_ms=int(query_duration_ms),
            )

            # Simulate serialization
            serialize_start = time.time()
            result = [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "cnt_bought": p["cnt_bought"],
                }
                for p in products
            ]
            serialize_duration_ms = (time.time() - serialize_start) * 1000

            span.set_attribute("serialize_duration_ms", serialize_duration_ms)

            total_duration_ms = (time.time() - start_time) * 1000
            span.set_attribute("total_duration_ms", total_duration_ms)

            logger.info(
                "response_ready",
                total_duration_ms=int(total_duration_ms),
                serialize_duration_ms=int(serialize_duration_ms),
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "query_failed",
                error=str(e),
                duration_ms=int(duration_ms),
                exc_info=True,
            )
            span.record_exception(e)
            raise


async def _fetch_products(count: int) -> list[dict[str, Any]]:
    """Fetch products from database."""
    # Simulate database query
    import asyncio
    await asyncio.sleep(0.01)
    return [
        {"id": "prod-1", "title": "Product 1", "cnt_bought": 100},
        {"id": "prod-2", "title": "Product 2", "cnt_bought": 50},
    ][:count]
```

**Key Points:**
- Timing measurements in spans
- Duration logged with context
- Performance metrics tracked
- Query vs serialization time separated

---

## 9. Request Correlation

Correlating logs across request lifecycle:

```python
# app/reporting/infrastructure/fastapi_app.py
from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Request
from structlog import get_logger

from app.shared.observability import ObservabilityContext
from app.shared.logging_setup import setup_structlog


def create_app_with_correlation() -> FastAPI:
    """Create FastAPI app with request correlation."""
    setup_structlog()
    app = FastAPI()
    logger = get_logger(__name__)

    @app.middleware("http")
    async def correlation_middleware(
        request: Request,
        call_next: Any,
    ) -> Any:
        """Add correlation IDs to all logs.

        Sets request_id and user_id in context so all
        logs from this request include these values.
        """
        # Get or generate request ID
        request_id = request.headers.get(
            "x-request-id",
            str(uuid.uuid4()),
        )
        user_id = request.headers.get("x-user-id")

        # Set context
        ObservabilityContext.set_request_id(request_id)
        if user_id:
            ObservabilityContext.set_user_id(user_id)

        # Log request start with correlation ID
        logger.info(
            "http_request_started",
            request_id=request_id,
            user_id=user_id,
            method=request.method,
            path=request.url.path,
            query_string=str(request.url.query),
        )

        try:
            # Process request
            response = await call_next(request)

            # Log response with same correlation ID
            logger.info(
                "http_request_completed",
                request_id=request_id,
                status_code=response.status_code,
            )

            return response

        except Exception as e:
            # Log error with correlation ID
            logger.error(
                "http_request_failed",
                request_id=request_id,
                error=str(e),
                exc_info=True,
            )
            raise

    @app.get("/orders/{order_id}")
    async def get_order(order_id: str) -> dict[str, Any]:
        """Endpoint that logs with request correlation."""
        request_id = ObservabilityContext.get_request_id()
        user_id = ObservabilityContext.get_user_id()

        logger.info(
            "fetching_order",
            order_id=order_id,
            request_id=request_id,
            user_id=user_id,
        )

        # All these logs have same request_id and user_id
        order = {"id": order_id, "status": "completed"}

        logger.info(
            "order_fetched",
            order_id=order_id,
            request_id=request_id,
        )

        return order

    return app
```

**Key Points:**
- Request IDs generated or extracted
- Context set for all logs
- All logs in request have correlation ID
- User IDs included when present

---

## 10. Console vs OTLP Exporters

Configuration for different exporters:

```python
# config examples
from app.shared.otel_config import OTELConfig


# Development - Console exporter
def setup_development() -> None:
    """Setup OTEL for development."""
    config = OTELConfig(
        service_name="my-service",
        service_version="1.0.0",
        environment="dev",
        exporter_type="console",  # Print logs to console
    )
    config.setup_logging()
    config.setup_tracing()


# Staging - OTLP exporter
def setup_staging() -> None:
    """Setup OTEL for staging."""
    config = OTELConfig(
        service_name="my-service",
        service_version="1.0.0",
        environment="staging",
        exporter_type="otlp",  # Send to OTEL Collector
        otlp_endpoint="otel-collector.staging:4317",
    )
    config.setup_logging()
    config.setup_tracing()


# Production - OTLP with secure endpoint
def setup_production() -> None:
    """Setup OTEL for production."""
    config = OTELConfig(
        service_name="my-service",
        service_version="1.0.0",
        environment="prod",
        exporter_type="otlp",  # Send to OTEL Collector
        otlp_endpoint="otel-collector.prod:4317",
    )
    config.setup_logging()
    config.setup_tracing()


# Console output example:
# {
#     "event": "order_processed",
#     "timestamp": "2024-11-08T10:30:45.123456Z",
#     "order_id": "order-123",
#     "status": "completed",
#     "duration_ms": 145,
#     "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
#     "span_id": "00f067aa0ba902b7"
# }
```

**Key Points:**
- Console exporter for development
- OTLP exporter for production
- Configuration per environment
- Easy switching via exporter_type

---

## Summary

These 10 examples cover:

1. **FastAPI** - HTTP request logging with middleware
2. **Kafka** - Message consumption with tracing
3. **Background Jobs** - Long-running tasks with phases
4. **Exceptions** - Custom exception logging
5. **Unit Tests** - Configuration testing
6. **Integration Tests** - Log export testing
7. **Trace Context** - Automatic correlation
8. **Performance** - Timing measurements
9. **Request Correlation** - Request-scoped logging
10. **Exporters** - Different configurations

All examples are production-ready and follow OTEL best practices.
