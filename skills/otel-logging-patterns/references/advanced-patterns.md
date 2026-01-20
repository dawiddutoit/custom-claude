# Advanced OpenTelemetry Logging Patterns

Deep-dive into advanced OTEL logging patterns, performance optimization, and troubleshooting.

## Table of Contents

1. [Trace Propagation Across Services](#trace-propagation-across-services)
2. [Custom Log Exporters](#custom-log-exporters)
3. [Performance Optimization](#performance-optimization)
4. [Batch vs Simple Exporters](#batch-vs-simple-exporters)
5. [Structured Logging with Context](#structured-logging-with-context)
6. [Error Aggregation and Sampling](#error-aggregation-and-sampling)
7. [Resource Cleanup and Shutdown](#resource-cleanup-and-shutdown)
8. [Multi-Exporter Setup](#multi-exporter-setup)
9. [Custom Processors](#custom-processors)
10. [Debugging OTEL Configuration](#debugging-otel-configuration)

---

## Trace Propagation Across Services

How to propagate trace context between microservices.

### W3C Trace Context Header Format

The W3C Trace Context standard uses the `traceparent` header:

```
traceparent: version-trace_id-parent_id-trace_flags
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
            00  = version (1 byte, always 00 for now)
            4bf92f3577b34da6a3ce929d0e0e4736 = trace_id (32 hex chars)
            00f067aa0ba902b7 = span_id (16 hex chars)
            01 = trace_flags (2 hex chars, 01 = sampled)
```

### Propagating Context in HTTP Requests

Use the authoritative `app/core/monitoring/otel_logger.py` for trace context:

```python
from __future__ import annotations

import httpx

from app.core.monitoring.otel_logger import logger, trace_span


class ServiceClient:
    """HTTP client that propagates trace context."""


    def __init__(self) -> None:
        """Initialize client."""
        self.client = httpx.AsyncClient()
        self.logger = logger(__name__)


    async def call_service(self, url: str, data: dict) -> dict:
        """Call another service with trace context propagation.

        Args:
            url: Service URL
            data: Request data

        Returns:
            Response data
        """
        with trace_span("call_service", service_url=url) as span:
            # Trace context is automatically propagated through httpx
            # instrumentation (if enabled)

            self.logger.info(
                "calling_service",
                url=url,
            )

            try:
                response = await self.client.post(
                    url,
                    json=data,
                    # Trace context automatically injected by OTEL instrumentation
                )
                response.raise_for_status()

                self.logger.info(
                    "service_call_succeeded",
                    status_code=response.status_code,
                )

                return response.json()

            except httpx.HTTPError as e:
                self.logger.error(
                    "service_call_failed",
                    error=str(e),
                    exc_info=True,
                )
                span.record_exception(e)
                raise


# Usage in use case:
class OrderProcessingUseCase:
    """Use case that calls external service."""


    def __init__(self, service_client: ServiceClient) -> None:
        self.service_client = service_client
        self.logger = logger(__name__)
        self.tracer = trace.get_tracer(__name__)


    async def process_order(self, order_id: str) -> None:
        """Process order with external service call.

        Args:
            order_id: Order to process
        """
        with self.tracer.start_as_current_span("process_order"):
            self.logger.info("processing_order", order_id=order_id)

            # Call external service - trace context propagated automatically
            result = await self.service_client.call_service(
                "http://payment-service:8000/charge",
                {"order_id": order_id, "amount": 99.99},
            )

            self.logger.info(
                "order_processed",
                order_id=order_id,
                result=result,
            )
```

### Extracting Context on Receiving End

```python
from __future__ import annotations

from fastapi import FastAPI, Request
from opentelemetry.propagate import extract
from opentelemetry import trace, logs
from structlog import get_logger


def create_service_app() -> FastAPI:
    """Create service that receives trace context."""
    app = FastAPI()
    logger = get_logger(__name__)

    @app.middleware("http")
    async def extract_trace_context(request: Request, call_next):
        """Extract trace context from request headers.

        The extract() function reads traceparent and tracestate headers
        and sets them as the current trace context.
        """
        # Extract trace context from headers
        context = extract(request.headers)

        with trace.set_span_in_context(context):
            tracer = trace.get_tracer(__name__)

            with tracer.start_as_current_span("handle_request"):
                logger.info(
                    "request_received_with_context",
                    path=request.url.path,
                )

                response = await call_next(request)
                return response

    @app.post("/charge")
    async def charge_payment(data: dict) -> dict:
        """Charge payment (receives trace context from caller)."""
        tracer = trace.get_tracer(__name__)
        logger = get_logger(__name__)

        with tracer.start_as_current_span("charge_payment"):
            logger.info(
                "charging_payment",
                order_id=data.get("order_id"),
                amount=data.get("amount"),
            )
            # All logs have same trace_id as calling service
            return {"status": "charged", "transaction_id": "txn-123"}

    return app
```

---

## Custom Log Exporters

Create custom exporters for specialized needs.

### File-Based Exporter

```python
from __future__ import annotations

import json
from typing import Sequence

from opentelemetry.sdk.logs import LogRecord
from opentelemetry.sdk.logs.export import LogExporter, LogExportResult


class FileLogExporter(LogExporter):
    """Export logs to file in JSON Lines format.

    Each log record is written as a separate JSON line.
    Useful for local file storage and debugging.
    """

    def __init__(self, file_path: str) -> None:
        """Initialize exporter.

        Args:
            file_path: Path to log file
        """
        self.file_path = file_path
        self.file = open(file_path, "a")

    def emit(self, log_records: Sequence[LogRecord]) -> LogExportResult:
        """Export log records to file.

        Args:
            log_records: Records to export

        Returns:
            Export result (success/failure)
        """
        try:
            for record in log_records:
                # Convert record to JSON
                log_dict = {
                    "timestamp": record.timestamp,
                    "severity": record.severity_number,
                    "severity_text": record.severity_text,
                    "body": record.body,
                    "trace_id": record.trace_id,
                    "span_id": record.span_id,
                    "attributes": record.attributes or {},
                }

                # Write as JSON line
                json_line = json.dumps(log_dict)
                self.file.write(json_line + "\n")
                self.file.flush()

            return LogExportResult.SUCCESS

        except Exception as e:
            print(f"Failed to export logs: {e}")
            return LogExportResult.FAILURE

    def shutdown(self) -> None:
        """Shutdown and close file."""
        if self.file:
            self.file.close()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush (file is already flushed).

        Args:
            timeout_millis: Timeout in milliseconds

        Returns:
            Always True
        """
        if self.file:
            self.file.flush()
        return True


# Usage:
def setup_file_logging() -> None:
    """Setup file-based logging."""
    from opentelemetry import logs
    from opentelemetry.sdk.logs import LoggerProvider
    from opentelemetry.sdk.logs.export import SimpleLogRecordExporter

    exporter = FileLogExporter("app.jsonl")
    processor = SimpleLogRecordExporter(exporter)

    logger_provider = LoggerProvider()
    logger_provider.add_log_record_processor(processor)
    logs.set_logger_provider(logger_provider)
```

### Database Exporter

```python
from __future__ import annotations

from typing import Sequence

from opentelemetry.sdk.logs import LogRecord
from opentelemetry.sdk.logs.export import LogExporter, LogExportResult


class DatabaseLogExporter(LogExporter):
    """Export logs to database table.

    Stores logs in a database for querying and archival.
    """

    def __init__(self, db_connection_string: str) -> None:
        """Initialize exporter.

        Args:
            db_connection_string: Database connection string
        """
        import sqlite3

        self.conn = sqlite3.connect(db_connection_string)
        self._create_table()

    def _create_table(self) -> None:
        """Create logs table if not exists."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp BIGINT,
                severity_text TEXT,
                body TEXT,
                trace_id TEXT,
                span_id TEXT,
                attributes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def emit(self, log_records: Sequence[LogRecord]) -> LogExportResult:
        """Export logs to database.

        Args:
            log_records: Log records to export

        Returns:
            Export result
        """
        try:
            import json

            for record in log_records:
                self.conn.execute(
                    """
                    INSERT INTO logs
                    (timestamp, severity_text, body, trace_id, span_id, attributes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.timestamp,
                        record.severity_text,
                        record.body,
                        record.trace_id,
                        record.span_id,
                        json.dumps(record.attributes or {}),
                    ),
                )

            self.conn.commit()
            return LogExportResult.SUCCESS

        except Exception as e:
            print(f"Failed to export logs to database: {e}")
            return LogExportResult.FAILURE

    def shutdown(self) -> None:
        """Shutdown and close connection."""
        if self.conn:
            self.conn.close()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush (database is auto-committed).

        Args:
            timeout_millis: Timeout

        Returns:
            True if successful
        """
        return True
```

---

## Performance Optimization

Minimize logging overhead in production.

### Batch Configuration for High Throughput

```python
from __future__ import annotations

from opentelemetry import logs
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.logs.export import BatchLogRecordExporter
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource


def setup_high_throughput_logging() -> LoggerProvider:
    """Setup logging optimized for high throughput.

    Configuration for systems that produce many logs
    (e.g., data pipelines, high-traffic APIs).

    Returns:
        Configured LoggerProvider
    """
    resource = Resource.create({"service.name": "high-volume-service"})

    # OTLP exporter
    otlp_exporter = OTLPLogExporter(
        endpoint="localhost:4317",
        insecure=True,
    )

    # Batch processor with tuned configuration:
    # - Large batch size: Wait for many records before exporting
    # - Long schedule delay: Export less frequently
    # - Large queue size: Buffer many records in memory
    processor = BatchLogRecordExporter(
        otlp_exporter,
        max_queue_size=4096,  # Large queue (default: 2048)
        schedule_delay_millis=5000,  # 5 second batches (default: 5000)
        max_export_batch_size=1024,  # Large batches (default: 512)
        export_timeout_millis=30000,  # 30 second timeout
    )

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(processor)
    logs.set_logger_provider(logger_provider)

    return logger_provider
```

### Sampling to Reduce Volume

```python
from __future__ import annotations

from opentelemetry.sdk.logs import LogRecord
from opentelemetry.sdk.logs.export import LogRecordProcessor


class SamplingProcessor(LogRecordProcessor):
    """Sample logs to reduce volume.

    Only exports a percentage of logs (e.g., 10% of INFO logs,
    100% of ERROR logs).
    """

    def __init__(self, sample_rate: float = 0.1) -> None:
        """Initialize sampler.

        Args:
            sample_rate: Fraction of logs to keep (0.0-1.0)
        """
        import random

        self.sample_rate = sample_rate
        self.random = random

    def on_log_record(self, log_record: LogRecord) -> None:
        """Process log record (sampling).

        Args:
            log_record: Log record to process
        """
        # Always keep ERROR and above
        if log_record.severity_number >= 40:  # ERROR
            return

        # Sample INFO and DEBUG
        if self.random.random() > self.sample_rate:
            # Drop this log
            log_record.severity_number = 0

    def shutdown(self) -> None:
        """Shutdown processor."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush.

        Args:
            timeout_millis: Timeout

        Returns:
            Always True
        """
        return True


# Usage:
def setup_logging_with_sampling() -> None:
    """Setup logging with sampling."""
    from opentelemetry import logs
    from opentelemetry.sdk.logs import LoggerProvider

    logger_provider = LoggerProvider()

    # Sample 10% of logs
    sampler = SamplingProcessor(sample_rate=0.1)
    logger_provider.add_log_record_processor(sampler)

    logs.set_logger_provider(logger_provider)
```

---

## Batch vs Simple Exporters

Understand the tradeoffs.

### Simple Exporter (Immediate Export)

```python
from opentelemetry.sdk.logs.export import SimpleLogRecordExporter

# Characteristics:
# - Exports immediately when records are emitted
# - Lower latency (records available almost immediately)
# - Higher overhead (many small network requests)
# - Useful for: Development, debugging, low-volume logs

# Usage:
processor = SimpleLogRecordExporter(exporter)
```

### Batch Exporter (Buffered Export)

```python
from opentelemetry.sdk.logs.export import BatchLogRecordExporter

# Characteristics:
# - Buffers records and exports periodically
# - Higher throughput (batches reduce network overhead)
# - Higher latency (records delayed by batch time)
# - Useful for: Production, high-volume logs, cost-sensitive

# Configuration:
processor = BatchLogRecordExporter(
    exporter,
    max_queue_size=2048,        # Max buffered records
    schedule_delay_millis=5000,  # Export every 5 seconds
    max_export_batch_size=512,   # Records per batch
    export_timeout_millis=30000, # Timeout for export
)

# Performance characteristics:
# - If 100 logs/second: exports ~500 records every 5 seconds
# - If 10,000 logs/second: exports 512 records multiple times per second
# - Low overhead, high throughput
```

### Choosing the Right Exporter

```python
def setup_logger_for_environment(env: str) -> None:
    """Setup logger based on environment.

    Args:
        env: Environment name (dev, staging, prod)
    """
    from opentelemetry import logs
    from opentelemetry.sdk.logs import LoggerProvider
    from opentelemetry.sdk.logs.export import (
        SimpleLogRecordExporter,
        BatchLogRecordExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter

    exporter = OTLPLogExporter(endpoint="localhost:4317", insecure=True)
    logger_provider = LoggerProvider()

    if env == "dev":
        # Development: immediate export for debugging
        processor = SimpleLogRecordExporter(exporter)

    elif env == "staging":
        # Staging: balanced batching
        processor = BatchLogRecordExporter(
            exporter,
            max_queue_size=2048,
            schedule_delay_millis=5000,
            max_export_batch_size=512,
        )

    else:  # prod
        # Production: aggressive batching for throughput
        processor = BatchLogRecordExporter(
            exporter,
            max_queue_size=4096,
            schedule_delay_millis=10000,  # 10 second batches
            max_export_batch_size=1024,
        )

    logger_provider.add_log_record_processor(processor)
    logs.set_logger_provider(logger_provider)
```

---

## Structured Logging with Context

Using structlog's context vars for rich logs.

### Context Management

```python
from __future__ import annotations

import structlog
from typing import Any, Optional


class RequestContext:
    """Manage request-scoped context.

    Stores request metadata that should appear in all logs
    for that request.
    """

    @staticmethod
    def set_request_context(
        request_id: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Set request context that appears in all logs.

        Args:
            request_id: Unique request ID
            user_id: User making request
            tenant_id: Tenant ID (multi-tenant systems)
            **kwargs: Additional context
        """
        context = {
            "request_id": request_id,
        }

        if user_id:
            context["user_id"] = user_id

        if tenant_id:
            context["tenant_id"] = tenant_id

        # Add additional context
        context.update(kwargs)

        # Store in structlog context
        for key, value in context.items():
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(**context)

    @staticmethod
    def bind(**kwargs: Any) -> None:
        """Add context to current request.

        Args:
            **kwargs: Context key-value pairs
        """
        structlog.contextvars.bind_contextvars(**kwargs)

    @staticmethod
    def unbind(*keys: str) -> None:
        """Remove context from current request.

        Args:
            *keys: Context keys to remove
        """
        structlog.contextvars.unbind_contextvars(*keys)

    @staticmethod
    def clear() -> None:
        """Clear all context."""
        structlog.contextvars.clear_contextvars()


# Usage in middleware:
from fastapi import FastAPI, Request
import uuid


def create_app_with_context() -> FastAPI:
    """Create app with request context management."""
    app = FastAPI()

    @app.middleware("http")
    async def context_middleware(request: Request, call_next):
        """Setup context for request."""
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        user_id = request.headers.get("x-user-id")

        # Set request context
        RequestContext.set_request_context(
            request_id=request_id,
            user_id=user_id,
            path=request.url.path,
            method=request.method,
        )

        try:
            response = await call_next(request)
            return response
        finally:
            # Clear context after request
            RequestContext.clear()

    return app
```

---

## Error Aggregation and Sampling

Advanced error handling patterns.

### Error Deduplication

```python
from __future__ import annotations

from typing import Optional
from hashlib import md5


class ErrorDeduplicator:
    """Deduplicate errors to avoid log spam.

    Tracks recent errors and avoids logging duplicates.
    """


    def __init__(self, window_size: int = 100) -> None:
        """Initialize deduplicator.

        Args:
            window_size: Number of recent errors to track
        """
        self.recent_errors: dict[str, int] = {}
        self.window_size = window_size


    def should_log(self, error_type: str, error_msg: str) -> bool:
        """Check if error should be logged.

        Args:
            error_type: Type of error
            error_msg: Error message

        Returns:
            True if error should be logged (not duplicate)
        """
        # Create error signature
        signature = self._get_signature(error_type, error_msg)

        if signature in self.recent_errors:
            # Duplicate
            self.recent_errors[signature] += 1
            return False

        # New error
        self.recent_errors[signature] = 1

        # Trim window if too large
        if len(self.recent_errors) > self.window_size:
            # Remove oldest (could be more sophisticated)
            self.recent_errors.pop(next(iter(self.recent_errors)))

        return True


    def get_occurrence_count(self, error_type: str, error_msg: str) -> int:
        """Get occurrence count of error.

        Args:
            error_type: Type of error
            error_msg: Error message

        Returns:
            Number of times error occurred
        """
        signature = self._get_signature(error_type, error_msg)
        return self.recent_errors.get(signature, 0)


    @staticmethod
    def _get_signature(error_type: str, error_msg: str) -> str:
        """Create error signature.

        Args:
            error_type: Type of error
            error_msg: Error message

        Returns:
            Error signature
        """
        combined = f"{error_type}:{error_msg}"
        return md5(combined.encode()).hexdigest()


# Usage:
deduplicator = ErrorDeduplicator()
logger = structlog.logger(__name__)


def log_error_deduplicated(error: Exception) -> None:
    """Log error with deduplication.

    Args:
        error: Exception to log
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if deduplicator.should_log(error_type, error_msg):
        logger.error(
            "error_occurred",
            error_type=error_type,
            error=error_msg,
            exc_info=True,
        )
    else:
        count = deduplicator.get_occurrence_count(error_type, error_msg)
        logger.debug(
            "duplicate_error_suppressed",
            error_type=error_type,
            occurrence_count=count,
        )
```

---

## Resource Cleanup and Shutdown

Proper cleanup of OTEL resources.

### Graceful Shutdown

```python
from __future__ import annotations

import asyncio
import signal
from typing import Optional

from opentelemetry import logs, trace
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.trace import TracerProvider


class OTELResourceManager:
    """Manage OTEL resource lifecycle.

    Ensures proper cleanup and graceful shutdown.
    """


    def __init__(
            self,
            logger_provider: Optional[LoggerProvider] = None,
            tracer_provider: Optional[TracerProvider] = None,
    ) -> None:
        """Initialize manager.

        Args:
            logger_provider: LoggerProvider instance
            tracer_provider: TracerProvider instance
        """
        self.logger_provider = logger_provider
        self.tracer_provider = tracer_provider
        self.shutdown_event = asyncio.Event()


    def register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""


        def handle_signal(signum: int, frame) -> None:
            print(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()


        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)


    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self.shutdown_event.wait()


    def shutdown(self) -> None:
        """Shutdown OTEL providers and cleanup resources."""
        print("Shutting down OTEL resources...")

        # Shutdown logger provider
        if self.logger_provider:
            self.logger_provider.force_flush(timeout_millis=30000)
            self.logger_provider.shutdown()

        # Shutdown tracer provider
        if self.tracer_provider:
            self.tracer_provider.force_flush(timeout_millis=30000)
            self.tracer_provider.shutdown()

        print("OTEL resources shutdown complete")


# Usage in main:
async def main() -> None:
    """Main entry point with proper cleanup."""
    from app.shared.otel_config import OTELConfig
    from app.shared.logging_setup import setup_structlog

    # Setup OTEL
    setup_structlog()
    config = OTELConfig(
        service_name="my-service",
        exporter_type="console",
    )
    logger_provider = config.setup_logging()
    tracer_provider = config.setup_tracing()

    # Setup resource manager
    manager = OTELResourceManager(logger_provider, tracer_provider)
    manager.register_signal_handlers()

    try:
        # Run application
        logger = structlog.logger(__name__)
        logger.info("application_started")

        # Wait for shutdown signal
        await manager.wait_for_shutdown()

        logger.info("shutting_down")

    finally:
        # Cleanup
        manager.shutdown()
```

---

## Multi-Exporter Setup

Export logs to multiple destinations simultaneously.

```python
from __future__ import annotations

from opentelemetry import logs
from opentelemetry.sdk.logs import LoggerProvider
from opentelemetry.sdk.logs.export import (
    BatchLogRecordExporter,
    SimpleLogRecordExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource


def setup_multi_export_logging() -> LoggerProvider:
    """Setup logging that exports to multiple destinations.

    Sends logs to:
    1. OTLP Collector (primary)
    2. Local file (backup)
    3. Console (debugging)
    """
    resource = Resource.create({"service.name": "multi-export-service"})
    logger_provider = LoggerProvider(resource=resource)

    # Exporter 1: OTLP (batched)
    otlp_exporter = OTLPLogExporter(
        endpoint="localhost:4317",
        insecure=True,
    )
    otlp_processor = BatchLogRecordExporter(otlp_exporter)
    logger_provider.add_log_record_processor(otlp_processor)

    # Exporter 2: File (batched)
    from opentelemetry.sdk.logs.export import LogExporter, LogExportResult
    from opentelemetry.sdk.logs import LogRecord
    from typing import Sequence
    import json

    class FileExporter(LogExporter):
        def __init__(self, filepath: str):
            self.file = open(filepath, "a")

        def emit(self, records: Sequence[LogRecord]) -> LogExportResult:
            for record in records:
                json.dump(
                    {
                        "timestamp": record.timestamp,
                        "body": record.body,
                        "trace_id": record.trace_id,
                    },
                    self.file,
                )
                self.file.write("\n")
            self.file.flush()
            return LogExportResult.SUCCESS

        def shutdown(self) -> None:
            self.file.close()

        def force_flush(self, timeout_millis: int = 30000) -> bool:
            self.file.flush()
            return True

    file_exporter = FileExporter("logs.jsonl")
    file_processor = BatchLogRecordExporter(file_exporter)
    logger_provider.add_log_record_processor(file_processor)

    # Exporter 3: Console (immediate, for debugging)
    from opentelemetry.sdk.logs.export import ConsoleLogExporter

    console_exporter = ConsoleLogExporter()
    console_processor = SimpleLogRecordExporter(console_exporter)
    logger_provider.add_log_record_processor(console_processor)

    logs.set_logger_provider(logger_provider)
    return logger_provider


# Result:
# - Each log record sent to all 3 exporters
# - OTLP: Batched, for observability platform
# - File: Batched, for local archival
# - Console: Immediate, for real-time debugging
```

---

## Custom Processors

Create processors to transform or filter logs.

### Filtering Processor

```python
from __future__ import annotations

from opentelemetry.sdk.logs import LogRecord
from opentelemetry.sdk.logs.export import LogRecordProcessor


class FilteringProcessor(LogRecordProcessor):
    """Filter logs based on criteria.

    Can exclude verbose libraries, filter by severity, etc.
    """

    def __init__(self, exclude_loggers: list[str]) -> None:
        """Initialize filter.

        Args:
            exclude_loggers: Logger names to exclude
        """
        self.exclude_loggers = exclude_loggers

    def on_log_record(self, log_record: LogRecord) -> None:
        """Process log record (filtering).

        Args:
            log_record: Log record
        """
        # Check if logger should be excluded
        if log_record.name in self.exclude_loggers:
            # Mark as invalid so it's dropped
            log_record.severity_number = 0

    def shutdown(self) -> None:
        """Shutdown processor."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush.

        Args:
            timeout_millis: Timeout

        Returns:
            True
        """
        return True


# Usage:
processor = FilteringProcessor(exclude_loggers=[
    "urllib3.connectionpool",  # Quiet noisy libraries
    "asyncio",
])
logger_provider.add_log_record_processor(processor)
```

---

## Debugging OTEL Configuration

Tools and techniques for troubleshooting.

### Verify Configuration

```python
from __future__ import annotations

from opentelemetry import logs, trace


def verify_otel_configuration() -> dict[str, bool]:
    """Verify OTEL is properly configured.

    Returns:
        Dict with configuration status
    """
    results = {
        "logger_provider_set": logs.get_logger_provider() is not None,
        "tracer_provider_set": trace.get_tracer_provider() is not None,
        "default_logger": logs.logger(__name__) is not None,
        "default_tracer": trace.get_tracer(__name__) is not None,
    }

    # Check trace context
    span = trace.get_current_span()
    results["span_available"] = span is not None

    return results


# Usage:
config_status = verify_otel_configuration()
for key, value in config_status.items():
    status = "OK" if value else "NOT OK"
    print(f"{key}: {status}")

# Expected output:
# logger_provider_set: OK
# tracer_provider_set: OK
# default_logger: OK
# default_tracer: OK
# span_available: OK
```

### Debug Logging

```python
from __future__ import annotations

import logging

# Enable debug logging from OTEL libraries
logging.basicConfig(level=logging.DEBUG)

# Or for specific libraries:
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)
logging.getLogger("opentelemetry.exporter").setLevel(logging.DEBUG)

# Now OTEL debug messages will appear
```

### Common Configuration Issues

**Issue: No logs appearing**

```python
# Check provider is set
from opentelemetry import logs
provider = logs.get_logger_provider()
print(f"Logger provider: {provider}")
print(f"Provider type: {type(provider).__name__}")

# Check processor added
print(f"Processors: {provider._log_record_processors}")
```

**Issue: Trace context missing**

```python
# Check instrumentation is enabled
from opentelemetry.instrumentation.logging import LoggingInstrumentor
LoggingInstrumentor().instrument()

# Verify within span
from opentelemetry import trace
with trace.get_tracer(__name__).start_as_current_span("test"):
    span = trace.get_current_span()
    print(f"Current span recording: {span.is_recording()}")
    print(f"Trace ID: {span.get_span_context().trace_id}")
```

**Issue: Export failures**

```python
# Check endpoint reachability
import socket
endpoint = "localhost:4317"
hostname, port = endpoint.split(":")
try:
    socket.create_connection((hostname, int(port)), timeout=5)
    print(f"Endpoint {endpoint} is reachable")
except socket.error as e:
    print(f"Cannot reach endpoint {endpoint}: {e}")
```

---

## Summary

Advanced patterns for production OTEL logging:

1. **Trace Propagation**: W3C Trace Context across services
2. **Custom Exporters**: File and database exporters
3. **Performance**: Batching, sampling, throughput optimization
4. **Structured Context**: Request-scoped logging
5. **Error Handling**: Deduplication and aggregation
6. **Resource Management**: Graceful shutdown
7. **Multi-Export**: Multiple destinations simultaneously
8. **Custom Processors**: Filtering and transformation
9. **Debugging**: Verification and troubleshooting

Combine these patterns to build robust, observable production systems.
