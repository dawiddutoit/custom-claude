---
name: otel-logging-patterns
description: |
  Implement OpenTelemetry (OTEL) logging with trace context correlation and structured logging.
  Use when setting up production logging with OTEL exporters, structlog/loguru integration,
  trace context propagation, and comprehensive test patterns. Covers Python implementations
  for FastAPI, Kafka consumers, and background jobs. Includes OTLP, Jaeger, and console exporters.
allowed-tools: Read, Write, Edit, Bash, Grep
---

# OpenTelemetry Logging Patterns

## Table of Contents

- [Purpose](#purpose)
- [Quick Start](#quick-start)
- [Instructions](#instructions)
  - [Step 1: Configure OTEL Logging Provider](#step-1-configure-otel-logging-provider)
  - [Step 2: Integrate Structured Logging Library](#step-2-integrate-structured-logging-library)
  - [Step 3: Add Trace Context Propagation](#step-3-add-trace-context-propagation)
  - [Step 4: Set Up Log Exporters](#step-4-set-up-log-exporters)
  - [Step 5: Implement Instrumentation](#step-5-implement-instrumentation)
  - [Step 6: Add Error and Exception Logging](#step-6-add-error-and-exception-logging)
- [Requirements](#requirements)
- [Common Patterns](#common-patterns)
- [Testing OTEL Logging](#testing-otel-logging)
- [Troubleshooting](#troubleshooting)
- [Supporting Resources](#supporting-resources)

## Purpose

This skill provides production-grade OpenTelemetry logging patterns for Python applications. It covers:

- **OTEL Logging Architecture**: Provider and processor configuration
- **Trace Correlation**: Automatic trace context injection into logs
- **Structured Logging**: Integration with structlog for context preservation
- **Log Exporters**: OTLP, Jaeger, console, and file exporters
- **Error Handling**: Comprehensive exception and error logging
- **Testing Patterns**: Unit and integration tests for logging infrastructure
- **Performance**: Optimization tips to minimize logging overhead

This enables production observability where logs, traces, and metrics are correlated through trace IDs for efficient debugging and monitoring.

## Quick Start

**For this project**, use the authoritative OTEL logging module. Get started in 3 simple steps:

1. **Initialize OTEL at application startup** (once):

```python
from app.core.monitoring.otel_logger import initialize_otel_logger

# Call once at app startup
initialize_otel_logger(
    log_level="INFO",
    enable_console=True,
    enable_otlp=True,
    otlp_endpoint="localhost:4317"
)
```

2. **Get logger and tracer in each module**:

```python
from app.core.monitoring.otel_logger import logger, get_tracer

# Module-level initialization
logger = logger(__name__)
tracer = get_tracer(__name__)
```

3. **Use trace_span for operations**:

```python
from app.core.monitoring.otel_logger import trace_span, logger

logger = logger(__name__)

# Logs automatically include trace_id and span_id
with trace_span("process_order", order_id="12345") as span:
    logger.info("processing_order", order_id="12345")
    # Do work...
    logger.info("order_processed", result_count=5)
```

That's it! All logs automatically include trace context, and spans are created with attributes. For more advanced patterns, see the detailed instructions below.

**Key Benefits**:
- ✅ Single entry point: `app/core/monitoring/otel_logger.py`
- ✅ No direct imports of structlog or opentelemetry needed
- ✅ Automatic trace context propagation
- ✅ Automatic exception handling in spans
- ✅ Works with async and sync functions

## Instructions

### Step 1: Configure OTEL Logging Provider

Set up the core OpenTelemetry logging infrastructure:

```python
# app/shared/otel_config.py
from __future__ import annotations

from typing import Optional

from opentelemetry import logs, metrics, trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.logs.export import (
    BatchLogRecordExporter,
    SimpleLogRecordExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class OTELConfig:
    """Configure OpenTelemetry logging, tracing, and metrics.

    Provides centralized OTEL configuration with support for:
    - OTLP exporter (grpc to OTEL Collector)
    - Jaeger exporter (legacy, direct to Jaeger)
    - Console exporter (development/debugging)
    - Batch vs simple export strategies

    Attributes:
        service_name: Service identifier (required)
        service_version: Service version
        environment: Environment (dev, staging, prod)
        enable_metrics: Enable metrics export
        exporter_type: 'otlp', 'jaeger', or 'console'
    """

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "dev",
        enable_metrics: bool = True,
        exporter_type: str = "otlp",
        otlp_endpoint: str = "localhost:4317",
        jaeger_agent_host: str = "localhost",
        jaeger_agent_port: int = 6831,
    ) -> None:
        """Initialize OTEL configuration.

        Args:
            service_name: Service name for resource
            service_version: Service version
            environment: Environment name
            enable_metrics: Enable metrics export
            exporter_type: 'otlp', 'jaeger', or 'console'
            otlp_endpoint: OTLP Collector endpoint (grpc)
            jaeger_agent_host: Jaeger agent host
            jaeger_agent_port: Jaeger agent port
        """
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.enable_metrics = enable_metrics
        self.exporter_type = exporter_type
        self.otlp_endpoint = otlp_endpoint
        self.jaeger_agent_host = jaeger_agent_host
        self.jaeger_agent_port = jaeger_agent_port

    def create_resource(self) -> Resource:
        """Create OTEL Resource with service attributes.

        Returns:
            Resource with service.name, service.version, and environment
        """
        return Resource.create({
            "service.name": self.service_name,
            "service.version": self.service_version,
            "deployment.environment": self.environment,
        })

    def setup_logging(self) -> LoggerProvider:
        """Set up OpenTelemetry logging provider.

        Creates and configures logger provider with appropriate exporter.

        Returns:
            Configured LoggerProvider instance

        Raises:
            ValueError: If exporter_type is not recognized
        """
        resource = self.create_resource()
        logger_provider = LoggerProvider(resource=resource)

        # Configure exporter based on type
        if self.exporter_type == "otlp":
            exporter = OTLPLogExporter(
                endpoint=self.otlp_endpoint,
                insecure=True,  # Set to False in production with TLS
            )
            processor = BatchLogRecordExporter(exporter)
        elif self.exporter_type == "jaeger":
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.jaeger_agent_host,
                agent_port=self.jaeger_agent_port,
            )
            processor = BatchLogRecordExporter(jaeger_exporter)
        elif self.exporter_type == "console":
            # Simple console exporter for development
            from opentelemetry.sdk.logs.export import ConsoleLogExporter

            exporter = ConsoleLogExporter()
            processor = SimpleLogRecordExporter(exporter)
        else:
            raise ValueError(
                f"Unknown exporter type: {self.exporter_type}. "
                "Must be 'otlp', 'jaeger', or 'console'"
            )

        logger_provider.add_log_record_processor(processor)
        logs.set_logger_provider(logger_provider)

        return logger_provider

    def setup_tracing(self) -> TracerProvider:
        """Set up OpenTelemetry tracing provider.

        Creates tracer provider with span exporter.

        Returns:
            Configured TracerProvider instance
        """
        resource = self.create_resource()
        tracer_provider = TracerProvider(resource=resource)

        # Use same exporter as logging for consistency
        if self.exporter_type == "otlp":
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            span_exporter = OTLPSpanExporter(
                endpoint=self.otlp_endpoint,
                insecure=True,
            )
        elif self.exporter_type == "jaeger":
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.jaeger_agent_host,
                agent_port=self.jaeger_agent_port,
            )
            span_exporter = jaeger_exporter
        else:  # console
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            span_exporter = ConsoleSpanExporter()

        tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
        trace.set_tracer_provider(tracer_provider)

        return tracer_provider
```

### Step 2: Integrate Structured Logging Library

Set up structlog with OTEL trace context integration:

```python
# app/shared/logging_setup.py
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from opentelemetry.instrumentation.logging import LoggingInstrumentor


def setup_structlog() -> None:
    """Configure structlog with OTEL trace context integration.

    Enables:
    - Automatic trace_id and span_id injection
    - JSON output for structured logs
    - Context variables for request tracking
    - Integration with Python logging

    Call this once at application startup.
    """
    # Enable OTEL logging instrumentation
    LoggingInstrumentor().instrument()

    # Configure structlog
    structlog.configure(
        processors=[
            # Merge context variables (trace_id, request_id, etc.)
            structlog.contextvars.merge_contextvars,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add exception info if logging exception
            structlog.processors.ExceptionRenderer(),
            # Render as JSON for structured logging
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.logging.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure Python logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def get_logger(name: str) -> Any:
    """Get a type-safe logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        structlog logger with trace context support
    """
    return structlog.logger(name)
```

### Step 3: Add Trace Context Propagation

Ensure trace context flows through logs automatically:

```python
# app/shared/observability.py
from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Tracer

# Context variables for request tracking
request_id_var: ContextVar[str | None] = ContextVar(
    "request_id", default=None
)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)


class ObservabilityContext:
    """Manage observability context (trace IDs, request IDs, user IDs).

    Provides methods to set and retrieve context that's automatically
    included in logs and traces.

    Example:
        >>> ctx = ObservabilityContext()
        >>> ctx.set_request_id("req-12345")
        >>> ctx.set_user_id("user-456")
        >>> # All subsequent logs include request_id and user_id
    """

    @staticmethod
    def set_request_id(request_id: str) -> None:
        """Set request ID in context.

        Args:
            request_id: Unique request identifier
        """
        request_id_var.set(request_id)

    @staticmethod
    def get_request_id() -> str | None:
        """Get current request ID from context.

        Returns:
            Request ID or None if not set
        """
        return request_id_var.get()

    @staticmethod
    def set_user_id(user_id: str) -> None:
        """Set user ID in context.

        Args:
            user_id: User identifier
        """
        user_id_var.set(user_id)

    @staticmethod
    def get_user_id() -> str | None:
        """Get current user ID from context.

        Returns:
            User ID or None if not set
        """
        return user_id_var.get()

    @staticmethod
    def get_tracer(name: str) -> Tracer:
        """Get tracer instance.

        Args:
            name: Tracer name (typically __name__)

        Returns:
            OpenTelemetry tracer
        """
        return trace.get_tracer(name)

    @staticmethod
    def get_current_span() -> Any:
        """Get current active span.

        Returns:
            Current span from context
        """
        return trace.get_current_span()

    @staticmethod
    def set_span_attribute(key: str, value: Any) -> None:
        """Set attribute on current span.

        Args:
            key: Attribute name
            value: Attribute value
        """
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute(key, value)
```

### Step 4: Set Up Log Exporters

Configure different exporters for different environments:

```python
# app/extraction/infrastructure/config.py
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class ExtractorConfig(BaseSettings):
    """Configuration for data extraction service.

    Includes OTEL logging configuration for observability.
    """

    # Service
    service_name: str = Field(default="extractor", description="Service name")
    service_version: str = Field(default="1.0.0", description="Service version")

    # Shopify API
    shopify_url: str = Field(..., description="Shopify shop URL")
    shopify_token: str = Field(..., description="Shopify API token")

    # Kafka
    kafka_brokers: list[str] = Field(
        default=["localhost:9092"],
        description="Kafka broker addresses",
    )
    kafka_topic: str = Field(default="orders", description="Kafka topic")

    # Observability (OTEL)
    otel_enabled: bool = Field(default=True, description="Enable OTEL")
    otel_exporter_type: str = Field(
        default="console",
        description="OTEL exporter: 'otlp', 'jaeger', or 'console'",
    )
    otel_otlp_endpoint: str = Field(
        default="localhost:4317",
        description="OTLP Collector endpoint",
    )
    otel_jaeger_host: str = Field(
        default="localhost",
        description="Jaeger agent host",
    )
    otel_jaeger_port: int = Field(default=6831, description="Jaeger agent port")

    class Config:
        env_prefix = "EXTRACTOR_"
        env_file = ".env"
```

Then use config in main:

```python
# app/extraction/infrastructure/extractor_main.py
from __future__ import annotations

import asyncio

from app.extraction.infrastructure.config import ExtractorConfig
from app.shared.logging_setup import setup_structlog, get_logger
from app.shared.otel_config import OTELConfig


async def main() -> None:
    """Main entry point for extraction service."""
    # Load configuration
    config = ExtractorConfig()

    # Setup logging
    setup_structlog()

    # Setup OTEL
    if config.otel_enabled:
        otel_config = OTELConfig(
            service_name=config.service_name,
            service_version=config.service_version,
            exporter_type=config.otel_exporter_type,
            otlp_endpoint=config.otel_otlp_endpoint,
            jaeger_agent_host=config.otel_jaeger_host,
            jaeger_agent_port=config.otel_jaeger_port,
        )
        otel_config.setup_logging()
        otel_config.setup_tracing()

    logger = get_logger(__name__)
    logger.info("extraction_service_started", version=config.service_version)

    # ... rest of extraction logic ...


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 5: Implement Instrumentation

Add tracing and logging to key application flows:

```python
# app/extraction/application/use_cases/extract_orders.py
from __future__ import annotations

from opentelemetry import trace

from app.shared.logging_setup import get_logger


class ExtractOrdersUseCase:
    """Use case for extracting orders with observability.

    Automatically instruments extraction with traces and logs.
    """

    def __init__(self, shopify_gateway, kafka_publisher) -> None:
        self.shopify_gateway = shopify_gateway
        self.kafka_publisher = kafka_publisher
        self.logger = get_logger(__name__)
        self.tracer = trace.get_tracer(__name__)

    async def execute(self) -> int:
        """Execute order extraction with tracing.

        Returns:
            Number of orders extracted and published
        """
        with self.tracer.start_as_current_span("extract_orders") as span:
            self.logger.info("starting_order_extraction")

            try:
                # Fetch orders
                with self.tracer.start_as_current_span("fetch_orders"):
                    self.logger.info("fetching_orders_from_shopify")
                    orders = await self.shopify_gateway.fetch_all_orders()
                    self.logger.info(
                        "orders_fetched",
                        count=len(orders),
                    )

                # Publish orders
                with self.tracer.start_as_current_span("publish_orders"):
                    self.logger.info("publishing_orders_to_kafka")
                    for order in orders:
                        with self.tracer.start_as_current_span(
                            "publish_order"
                        ) as order_span:
                            order_span.set_attribute("order_id", order.order_id)
                            await self.kafka_publisher.publish(order)

                    self.logger.info(
                        "orders_published",
                        count=len(orders),
                    )

                span.set_attribute("orders_processed", len(orders))
                self.logger.info(
                    "order_extraction_completed",
                    total_orders=len(orders),
                )
                return len(orders)

            except Exception as e:
                self.logger.error(
                    "order_extraction_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                span.record_exception(e)
                raise
```

### Step 6: Add Error and Exception Logging

Implement comprehensive error logging with context:

```python
# app/reporting/adapters/api/error_handlers.py
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.shared.logging_setup import get_logger
from app.shared.observability import ObservabilityContext


logger = get_logger(__name__)


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Global exception handler with OTEL logging.

    Logs all unhandled exceptions with trace context,
    request details, and stack trace.

    Args:
        request: HTTP request
        exc: Exception to handle

    Returns:
        JSON error response with HTTP 500
    """
    request_id = ObservabilityContext.get_request_id()
    user_id = ObservabilityContext.get_user_id()

    # Log with full context
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        request_id=request_id,
        user_id=user_id,
        path=request.url.path,
        method=request.method,
        exc_info=True,  # Include full stack trace
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


async def data_not_available_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handler for data not available (503).

    Args:
        request: HTTP request
        exc: Exception to handle

    Returns:
        JSON error response with HTTP 503
    """
    request_id = ObservabilityContext.get_request_id()

    logger.warning(
        "data_not_available",
        request_id=request_id,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=503,
        content={
            "detail": "Data not yet available",
            "request_id": request_id,
        },
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Register error handlers with FastAPI app.

    Args:
        app: FastAPI application instance
    """
    from app.reporting.application.exceptions import DataNotAvailableException

    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(DataNotAvailableException, data_not_available_handler)


# FastAPI middleware for request tracking
async def logging_middleware(request: Request, call_next: Any) -> Any:
    """Middleware to add request tracking to logs.

    Extracts request ID from header and adds to context.

    Args:
        request: HTTP request
        call_next: Next middleware/handler

    Returns:
        Response from next handler
    """
    request_id = request.headers.get("x-request-id", "unknown")
    user_id = request.headers.get("x-user-id")

    # Set context for logging
    ObservabilityContext.set_request_id(request_id)
    if user_id:
        ObservabilityContext.set_user_id(user_id)

    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    try:
        response = await call_next(request)
        logger.info(
            "request_completed",
            request_id=request_id,
            status_code=response.status_code,
        )
        return response
    except Exception as e:
        logger.error(
            "request_failed",
            request_id=request_id,
            error=str(e),
        )
        raise
```

## Requirements

Production OTEL logging requires:

- `opentelemetry-api>=1.22.0` - OTEL API
- `opentelemetry-sdk>=1.22.0` - OTEL SDK with logging support
- `opentelemetry-exporter-otlp>=0.43b0` - OTLP exporter for gRPC
- `opentelemetry-exporter-jaeger-thrift>=1.22.0` - Jaeger exporter (optional)
- `opentelemetry-instrumentation-logging>=0.43b0` - Logging instrumentation
- `structlog>=23.2.0` - Structured logging library
- `pydantic>=2.5.0` - Configuration management
- `fastapi>=0.104.0` - Web framework (if using API)
- Python 3.11+ with type checking

## Common Patterns

### Logging in Different Contexts

See [`examples/examples.md`](./examples/examples.md) for detailed patterns:

1. **FastAPI Endpoints** - Request/response logging with trace context
2. **Kafka Consumers** - Message consumption with batch processing logs
3. **Background Jobs** - Long-running tasks with progress tracking
4. **Error Handling** - Exception logging with stack traces and context
5. **Performance Monitoring** - Timing spans and performance metrics

### Trace Context Propagation

Logs automatically include trace_id and span_id when logged within a span:

```python
from opentelemetry import trace
from app.shared.logging_setup import get_logger

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

# Logs within this span automatically include trace context
with tracer.start_as_current_span("process_payment"):
    logger.info("payment_started", customer_id="cust-123")
    # ... payment processing ...
    logger.info("payment_completed", amount=99.99)
    # All logs have same trace_id and span_id
```

### Context Variables

Use context variables for request-scoped data:

```python
from app.shared.observability import ObservabilityContext

# Set context
ObservabilityContext.set_request_id("req-12345")
ObservabilityContext.set_user_id("user-456")

logger.info("user_action", action="login")
# Log includes request_id and user_id automatically
```

## Testing OTEL Logging

See [`examples/examples.md`](./examples/examples.md) for comprehensive test patterns.

### Unit Testing

Test logging configuration without external dependencies:

```python
import pytest
from opentelemetry import logs
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.logs.export import SimpleLogRecordExporter
from unittest.mock import MagicMock

def test_logging_configuration():
    """Test OTEL logging provider setup."""
    # Create test provider
    test_exporter = MagicMock(spec=SimpleLogRecordExporter)
    logger_provider = LoggerProvider()

    # Verify provider created successfully
    assert logger_provider is not None
    logs.set_logger_provider(logger_provider)
    assert logs.get_logger_provider() == logger_provider
```

### Integration Testing

Test log export with real exporters:

```python
import pytest
from opentelemetry import logs, trace
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.logs.export import SimpleLogRecordExporter, LogRecord
from opentelemetry.sdk.trace import TracerProvider
from app.shared.logging_setup import get_logger


@pytest.fixture
def in_memory_log_exporter():
    """In-memory exporter for testing."""
    class InMemoryExporter(SimpleLogRecordExporter):
        def __init__(self):
            self.records = []

        def emit(self, log_records: list[LogRecord]) -> None:
            self.records.extend(log_records)

    return InMemoryExporter()


def test_trace_context_in_logs(in_memory_log_exporter):
    """Verify trace context is included in logs."""
    # Setup
    logger_provider = LoggerProvider()
    logger_provider.add_log_record_processor(
        SimpleLogRecordExporter(in_memory_log_exporter)
    )
    logs.set_logger_provider(logger_provider)

    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)

    # Log within span
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test_span") as span:
        logger = get_logger(__name__)
        logger.info("test_message")

    # Verify trace context in log
    records = in_memory_log_exporter.records
    assert len(records) > 0
    record = records[0]
    assert record.trace_id is not None
    assert record.span_id is not None
```

## Troubleshooting

### Common Issues and Solutions

**Issue: Trace IDs not appearing in logs**

- Ensure `LoggingInstrumentor().instrument()` is called before logging
- Verify logs are being created within a span context
- Check that OTEL trace provider is set before creating loggers

**Issue: OTLP exporter connection refused**

- Verify OTEL Collector is running on specified endpoint
- Check endpoint configuration (default: localhost:4317)
- Use console exporter in development
- Check firewall rules for gRPC port 4317

**Issue: High logging overhead**

- Use `BatchLogRecordExporter` instead of `SimpleLogRecordExporter`
- Increase batch size for fewer exports (e.g., 512 records)
- Use console exporter in development, OTLP in production
- Filter verbose DEBUG logs in production

**Issue: Logs not appearing in output**

- Verify logger is initialized with `setup_structlog()`
- Check Python logging level (INFO, WARNING, ERROR)
- Ensure logger name doesn't have filters applied
- Verify structlog configuration has JSONRenderer processor

**Issue: Memory leaks from logging**

- Call `logger_provider.force_flush()` on shutdown
- Ensure log processors are cleaned up
- Use context managers for resource management
- Monitor memory usage with profiling tools

## Supporting Resources

| Resource | Purpose |
|----------|---------|
| [`examples/examples.md`](./examples/examples.md) | 10+ complete examples covering FastAPI, Kafka, background jobs, testing |
| [`references/advanced-patterns.md`](./references/advanced-patterns.md) | Performance tuning, custom exporters, trace propagation details |
