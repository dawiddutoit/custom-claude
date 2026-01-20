# Kafka Schema Management References

Advanced topics, best practices, and integration patterns for production Kafka schema management.

## Table of Contents

- [Performance Optimization](#performance-optimization)
- [Integration with Pydantic Models](#integration-with-pydantic-models)
- [Schema Documentation Standards](#schema-documentation-standards)
- [Monitoring Schema Usage](#monitoring-schema-usage)
- [ClickHouse Table Schema Alignment](#clickhouse-table-schema-alignment)
- [Distributed Tracing with Correlation IDs](#distributed-tracing-with-correlation-ids)
- [Schema Registry Pattern](#schema-registry-pattern)
- [Troubleshooting](#troubleshooting)

## Performance Optimization

### msgspec Performance Characteristics

msgspec is the fastest Python serialization library for JSON:

- **Serialization**: 10-20x faster than json.dumps() + Pydantic
- **Deserialization**: 5-10x faster than json.loads() + Pydantic
- **Memory**: Lower memory overhead than Pydantic validation
- **CPU**: Optimized Rust backend with minimal Python overhead

### Optimization Strategies

#### 1. Pre-compile Decoders and Encoders

Always create decoders/encoders once and reuse them:

```python
class OptimizedValidator:
    """Validator with pre-compiled codec instances."""

    def __init__(self) -> None:
        # These are created once and reused for all messages
        self._decoder = msgspec.json.Decoder(OrderEventMessage)
        self._encoder = msgspec.json.Encoder()

    def validate(self, data: bytes) -> OrderEventMessage:
        """Uses pre-compiled decoder."""
        return self._decoder.decode(data)

    def serialize(self, msg: OrderEventMessage) -> bytes:
        """Uses pre-compiled encoder."""
        return self._encoder.encode(msg)


# Bad: Creates new decoder/encoder for each message!
def slow_validate(data: bytes) -> OrderEventMessage:
    decoder = msgspec.json.Decoder(OrderEventMessage)  # Slow!
    return decoder.decode(data)
```

#### 2. Use Immutable Structs (frozen=True)

Frozen structs are slightly faster and prevent mutation:

```python
# Good: Immutable
class OrderEventMessage(msgspec.Struct, frozen=True):
    order_id: str

# Avoid: Mutable (has overhead)
class OrderEventMessage(msgspec.Struct):
    order_id: str
```

#### 3. Type Specificity Matters

More specific types enable better optimizations:

```python
# Good: Type-specific
line_items: list[LineItemMessage]
metadata: dict[str, str]

# Slower: Less specific
line_items: list[object]
metadata: dict[str, object]

# Very slow: No type info
line_items: Any
```

#### 4. Connection Pooling for High Throughput

For high-throughput scenarios (>10K messages/sec):

```python
from concurrent.futures import ThreadPoolExecutor
from typing import Final
import threading


class ValidatorPool:
    """Thread-safe pool of pre-configured validators."""

    def __init__(self, pool_size: int = 10) -> None:
        self._validators: list[OrderMessageValidator] = [
            OrderMessageValidator() for _ in range(pool_size)
        ]
        self._lock = threading.Lock()
        self._current = 0

    def get_validator(self) -> OrderMessageValidator:
        """Get next validator in round-robin fashion."""
        with self._lock:
            validator = self._validators[self._current]
            self._current = (self._current + 1) % len(self._validators)
        return validator

    def validate(self, data: bytes) -> OrderEventMessage:
        """Validate using a pooled validator."""
        validator = self.get_validator()
        return validator.validate(data)


# Usage
pool = ValidatorPool(pool_size=20)
order = pool.validate(kafka_message_bytes)
```

#### 5. Batch Processing

For bulk operations, batch serialization:

```python
class BatchValidator:
    """Batch validation for improved throughput."""

    def __init__(self) -> None:
        self.validator = OrderMessageValidator()

    def validate_batch(
        self,
        messages: list[bytes]
    ) -> list[tuple[OrderEventMessage, Exception | None]]:
        """Validate multiple messages.

        Returns:
            List of (decoded_message, error) tuples
        """
        results: list[tuple[OrderEventMessage, Exception | None]] = []

        for msg_bytes in messages:
            try:
                decoded = self.validator.validate(msg_bytes)
                results.append((decoded, None))
            except SchemaValidationError as e:
                results.append((None, e))  # type: ignore

        return results

    def serialize_batch(
        self,
        messages: list[OrderEventMessage]
    ) -> list[bytes]:
        """Serialize multiple messages."""
        return [self.validator.serialize(msg) for msg in messages]
```

## Integration with Pydantic Models

Use Pydantic for configuration and API validation, msgspec for Kafka schemas.

### Pydantic Config Model

```python
from pydantic import BaseModel, Field, validator
from typing import Optional


class SchemaRegistryConfig(BaseModel):
    """Configuration for schema registry integration."""

    registry_url: str = Field(
        ...,
        description="Schema registry server URL"
    )
    schema_subject: str = Field(
        ...,
        description="Schema subject in registry"
    )
    cache_schemas: bool = Field(
        default=True,
        description="Cache schemas locally"
    )
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache TTL in seconds"
    )

    @validator('registry_url')
    def validate_url(cls, v: str) -> str:
        if not v.startswith('http'):
            raise ValueError("URL must start with http/https")
        return v

    class Config:
        env_prefix = "SCHEMA_"
        env_file = ".env"
```

### Converting Pydantic to msgspec

When you have Pydantic models but want msgspec performance:

```python
from typing import TypeVar

T = TypeVar('T')


class PydanticToMsgspec:
    """Convert between Pydantic and msgspec models."""

    @staticmethod
    def pydantic_to_msgspec(
        pydantic_obj: BaseModel,
        msgspec_class: type[T]
    ) -> T:
        """Convert Pydantic model to msgspec Struct.

        Args:
            pydantic_obj: Pydantic model instance
            msgspec_class: Target msgspec Struct class

        Returns:
            msgspec Struct instance
        """
        # Use dict() to convert Pydantic model
        data = pydantic_obj.model_dump()
        return msgspec_class(**data)

    @staticmethod
    def msgspec_to_pydantic(
        msgspec_obj: msgspec.Struct,
        pydantic_class: type[T]
    ) -> T:
        """Convert msgspec Struct to Pydantic model.

        Args:
            msgspec_obj: msgspec Struct instance
            pydantic_class: Target Pydantic model class

        Returns:
            Pydantic model instance
        """
        data = msgspec.json.decode(
            msgspec.json.encode(msgspec_obj),
            type=dict
        )
        return pydantic_class(**data)
```

## Schema Documentation Standards

### Comprehensive Schema Docstring Format

```python
from __future__ import annotations

import msgspec


class OrderEventMessage(msgspec.Struct, frozen=True):
    """Complete order event for Kafka publication.

    This is the primary event emitted when orders are created or updated.
    Consumers subscribe to this event to:
    - Update order database (storage context)
    - Generate shipping labels
    - Send customer confirmations
    - Update analytics/reporting

    Schema Characteristics:
    - Immutable: frozen=True prevents accidental mutation
    - Type-safe: All fields have explicit types
    - Versioned: Includes version history for evolution tracking
    - Serializable: Uses JSON-compatible types only

    Version History:
    - 1.0 (2024-01-01): Initial schema
      * Fields: order_id, created_at, customer_name, line_items, total_price
      * Breaking change: None
      * Notes: Original schema from project kickoff

    - 1.1 (2024-02-15): Added customer_email field
      * Fields: Added customer_email
      * Backward compatible: Yes (old messages have empty email)
      * Forward compatible: Yes (new consumers ignore field)
      * Migration: Producers updated first (2024-02-10)
      * Rollout: Completed 2024-02-20

    - 1.2 (2024-03-01): Added shipping_address
      * Fields: Added shipping_address (AddressMessage)
      * Backward compatible: Yes
      * Forward compatible: Yes
      * Consumers: Updated to handle address (2024-02-28)
      * Rollout: Completed 2024-03-05

    Backward Compatibility:
    - Consumers reading V1.0 messages: Use default email, unknown address
    - Producers still sending V1.0: Consumers handle missing fields

    Forward Compatibility:
    - Old consumers (V1.0) reading V1.2 messages: Ignore extra fields

    Known Issues:
    - None current

    Future Changes:
    - Consider: Shipping method field (estimated 2024-04-01)
    - Deprecation: customer_name field may be removed in V2.0

    Related Contexts:
    - Storage Context: Consumes this event, stores in orders table
    - Reporting Context: Aggregates order data for analytics
    - Notification Context: Sends customer emails on order creation

    Attributes:
        order_id: Unique order identifier (UUID format preferred)
        created_at: ISO 8601 timestamp "2024-01-01T12:00:00Z"
        customer_name: Customer name (1-255 characters)
        customer_email: Customer email (1-254 characters, valid email)
        shipping_address: Full shipping address (AddressMessage)
        line_items: List of products (minimum 1)
        total_price: Total order value (sum of line items - discount)
        notes: Optional order notes (max 1000 characters)
    """

    order_id: str
    created_at: str
    customer_name: str
    customer_email: str
    shipping_address: AddressMessage
    line_items: list[LineItemMessage]
    total_price: float
    notes: str = ""
```

## Monitoring Schema Usage

### Schema Metrics Collector

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Final
import threading


@dataclass
class SchemaMetrics:
    """Metrics for schema validation and serialization."""

    messages_validated: int = 0
    messages_serialized: int = 0
    validation_errors: int = 0
    serialization_errors: int = 0
    total_validation_time_ms: float = 0.0
    total_serialization_time_ms: float = 0.0
    schema_versions_seen: dict[str, int] = field(default_factory=dict)

    @property
    def avg_validation_time_ms(self) -> float:
        """Average validation time per message."""
        if self.messages_validated == 0:
            return 0.0
        return self.total_validation_time_ms / self.messages_validated

    @property
    def avg_serialization_time_ms(self) -> float:
        """Average serialization time per message."""
        if self.messages_serialized == 0:
            return 0.0
        return self.total_serialization_time_ms / self.messages_serialized

    @property
    def validation_error_rate(self) -> float:
        """Percentage of validation failures."""
        total = self.messages_validated + self.validation_errors
        if total == 0:
            return 0.0
        return (self.validation_errors / total) * 100


class MetricsCollector:
    """Thread-safe metrics collection."""

    def __init__(self) -> None:
        self._metrics = SchemaMetrics()
        self._lock = threading.Lock()

    def record_validation(
        self,
        duration_ms: float,
        success: bool,
        schema_version: str = "1.0"
    ) -> None:
        """Record validation metrics."""
        with self._lock:
            if success:
                self._metrics.messages_validated += 1
                self._metrics.total_validation_time_ms += duration_ms
            else:
                self._metrics.validation_errors += 1

            # Track schema versions
            if schema_version not in self._metrics.schema_versions_seen:
                self._metrics.schema_versions_seen[schema_version] = 0
            self._metrics.schema_versions_seen[schema_version] += 1

    def record_serialization(
        self,
        duration_ms: float,
        success: bool
    ) -> None:
        """Record serialization metrics."""
        with self._lock:
            if success:
                self._metrics.messages_serialized += 1
                self._metrics.total_serialization_time_ms += duration_ms
            else:
                self._metrics.serialization_errors += 1

    def get_metrics(self) -> SchemaMetrics:
        """Get current metrics snapshot."""
        with self._lock:
            # Return copy to prevent external mutation
            return SchemaMetrics(**self._metrics.__dict__)

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics = SchemaMetrics()
```

### Integration with Structured Logging

```python
import time
from structlog import get_logger


class MonitoredValidator:
    """Validator with metrics collection."""

    def __init__(self, metrics: MetricsCollector) -> None:
        self.validator = OrderMessageValidator()
        self.metrics = metrics
        self.logger = get_logger(__name__)

    def validate(self, data: bytes) -> OrderEventMessage:
        """Validate with metrics."""
        start = time.perf_counter()
        try:
            message = self.validator.validate(data)
            elapsed_ms = (time.perf_counter() - start) * 1000

            self.metrics.record_validation(elapsed_ms, success=True)
            self.logger.info(
                "message_validated",
                order_id=message.order_id,
                duration_ms=elapsed_ms
            )
            return message
        except SchemaValidationError as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.metrics.record_validation(elapsed_ms, success=False)
            self.logger.warning(
                "validation_failed",
                error=str(e),
                duration_ms=elapsed_ms
            )
            raise

    def serialize(self, message: OrderEventMessage) -> bytes:
        """Serialize with metrics."""
        start = time.perf_counter()
        try:
            result = self.validator.serialize(message)
            elapsed_ms = (time.perf_counter() - start) * 1000

            self.metrics.record_serialization(elapsed_ms, success=True)
            return result
        except SchemaValidationError as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.metrics.record_serialization(elapsed_ms, success=False)
            self.logger.error(
                "serialization_failed",
                error=str(e),
                duration_ms=elapsed_ms
            )
            raise
```

## ClickHouse Table Schema Alignment

### Mapping msgspec Schemas to ClickHouse

```python
from typing import Final


class ClickHouseSchemaMapper:
    """Map msgspec schemas to ClickHouse table definitions."""

    TYPE_MAPPING: Final = {
        str: "String",
        int: "Int64",
        float: "Float64",
        bool: "UInt8",
    }

    @staticmethod
    def msgspec_to_clickhouse(schema_class: type) -> str:
        """Generate ClickHouse CREATE TABLE statement.

        Args:
            schema_class: msgspec.Struct class

        Returns:
            ClickHouse SQL CREATE TABLE statement
        """
        # Example for OrderEventMessage
        return """
        CREATE TABLE IF NOT EXISTS orders (
            order_id String,
            created_at DateTime,
            customer_name String,
            customer_email String,
            shipping_address_street String,
            shipping_address_city String,
            shipping_address_postal_code String,
            shipping_address_country String,
            line_items Array(
                Tuple(
                    line_item_id String,
                    product_id String,
                    product_title String,
                    quantity Int64,
                    price Float64,
                    discount Float64
                )
            ),
            total_price Float64,
            notes String
        ) ENGINE = MergeTree()
        ORDER BY (created_at, order_id)
        SETTINGS index_granularity = 8192
        """


# Better: Use Kafka table engine to consume directly
class KafkaTableSchema:
    """ClickHouse table consuming from Kafka."""

    @staticmethod
    def create_kafka_table() -> str:
        """Create table that consumes from Kafka topic."""
        return """
        CREATE TABLE IF NOT EXISTS orders_kafka (
            order_id String,
            created_at DateTime,
            customer_name String,
            customer_email String,
            line_items String,  -- JSON string from Kafka
            total_price Float64
        ) ENGINE = Kafka()
        SETTINGS
            kafka_broker_list = 'redpanda:9092',
            kafka_topic_list = 'orders',
            kafka_group_id = 'clickhouse_loader',
            kafka_format = 'JSONEachRow'
        """

    @staticmethod
    def create_materialized_view() -> str:
        """Create materialized view for aggregation."""
        return """
        CREATE MATERIALIZED VIEW orders_mv
        TO orders_final AS
        SELECT
            order_id,
            toDateTime(created_at) as created_at,
            customer_name,
            customer_email,
            arrayJoin(JSONExtractArrayRaw(line_items, '')) as line_item_json,
            JSONExtractString(line_item_json, 'product_id') as product_id,
            JSONExtractString(line_item_json, 'product_title') as product_title,
            JSONExtractInt(line_item_json, 'quantity') as quantity,
            JSONExtractFloat(line_item_json, 'price') as price,
            total_price
        FROM orders_kafka
        """
```

## Distributed Tracing with Correlation IDs

### Adding Tracing to Schemas

```python
from __future__ import annotations

import msgspec
import uuid


class TracedOrderEventMessage(msgspec.Struct, frozen=True):
    """Order event with tracing support.

    Includes correlation_id for distributed tracing across services:
    1. Extractor generates correlation_id (UUID)
    2. Includes in Kafka message
    3. Loader reads correlation_id
    4. Includes in ClickHouse insert
    5. Reporter includes in API response headers

    This allows tracing a single order through entire pipeline.
    """

    # Standard fields
    order_id: str
    created_at: str
    customer_name: str

    # Tracing fields
    correlation_id: str  # UUID for distributed tracing
    trace_id: str  # Optional: OpenTelemetry trace ID
    span_id: str  # Optional: OpenTelemetry span ID


class TracingHelper:
    """Utilities for tracing support."""

    @staticmethod
    def generate_correlation_id() -> str:
        """Generate unique correlation ID."""
        return str(uuid.uuid4())

    @staticmethod
    def add_tracing(
        message: OrderEventMessage,
        correlation_id: str = ""
    ) -> TracedOrderEventMessage:
        """Add tracing fields to message."""
        if not correlation_id:
            correlation_id = TracingHelper.generate_correlation_id()

        return TracedOrderEventMessage(
            order_id=message.order_id,
            created_at=message.created_at,
            customer_name=message.customer_name,
            correlation_id=correlation_id,
            trace_id="",  # Set by OpenTelemetry if enabled
            span_id=""  # Set by OpenTelemetry if enabled
        )
```

## Schema Registry Pattern

### Local Schema Registry

```python
from __future__ import annotations

from typing import Final
from datetime import datetime
import json


class LocalSchemaRegistry:
    """Simple in-memory schema registry.

    Use when you don't have Confluent Schema Registry available.
    For production with multiple services, use real Schema Registry.
    """

    CURRENT_VERSION: Final = "1.2"

    def __init__(self) -> None:
        self._schemas: dict[str, dict[str, object]] = {}
        self._versions: dict[str, list[str]] = {}

    def register_schema(
        self,
        subject: str,
        version: str,
        schema_def: dict[str, object]
    ) -> int:
        """Register a schema version.

        Args:
            subject: Schema subject (e.g., "order-events-value")
            version: Semantic version (e.g., "1.2")
            schema_def: Schema definition (JSON Schema)

        Returns:
            Schema ID
        """
        key = f"{subject}:{version}"
        self._schemas[key] = schema_def

        if subject not in self._versions:
            self._versions[subject] = []
        self._versions[subject].append(version)

        return hash(key) % 2**31  # Simple ID generation

    def get_schema(self, subject: str, version: str) -> dict[str, object]:
        """Get schema by subject and version."""
        key = f"{subject}:{version}"
        if key not in self._schemas:
            raise ValueError(f"Schema not found: {key}")
        return self._schemas[key]

    def get_latest_schema(self, subject: str) -> tuple[str, dict[str, object]]:
        """Get latest schema for subject."""
        if subject not in self._versions:
            raise ValueError(f"Subject not found: {subject}")

        versions = self._versions[subject]
        latest = sorted(versions, key=lambda x: [int(p) for p in x.split(".")])[-1]
        return latest, self.get_schema(subject, latest)

    def list_schemas(self) -> dict[str, list[str]]:
        """List all registered schemas."""
        return self._versions.copy()
```

## Troubleshooting

### Common Schema Issues

#### Issue 1: "DecodeError: unexpected extra bytes"

```python
# Problem: Extra bytes after JSON in Kafka message
invalid_data = b'{"order_id":"123",...} extra bytes'

# Solution: Use proper JSON parsing
try:
    message = validator.validate(data)
except msgspec.DecodeError as e:
    if "unexpected extra bytes" in str(e):
        # Check for protocol wrapper (e.g., Avro/Protobuf header)
        # Remove any non-JSON prefix
        pass
```

#### Issue 2: "Missing required field"

```python
# Problem: Old producer sends V1 schema, new consumer expects V2
# Solution: Implement schema upgrading

class FlexibleValidator:
    """Handles missing required fields gracefully."""

    def validate_with_defaults(
        self,
        data: bytes,
        defaults: dict[str, object]
    ) -> OrderEventMessage:
        """Validate with default values for missing fields."""
        try:
            return self.decoder.decode(data)
        except msgspec.DecodeError:
            # Parse as dict and add defaults
            raw_dict = json.loads(data)
            for field, default in defaults.items():
                if field not in raw_dict:
                    raw_dict[field] = default
            return msgspec.json.decode(
                msgspec.json.encode(raw_dict),
                type=OrderEventMessage
            )
```

#### Issue 3: Performance Degradation

```python
# Problem: Slow message processing
# Root cause: Creating new decoder/encoder for each message

# Bad:
for msg_bytes in messages:
    decoder = msgspec.json.Decoder(OrderEventMessage)  # New each time!
    order = decoder.decode(msg_bytes)

# Good: Reuse pre-compiled decoder
decoder = msgspec.json.Decoder(OrderEventMessage)  # Create once
for msg_bytes in messages:
    order = decoder.decode(msg_bytes)  # Reuse many times
```

#### Issue 4: Type Checking Failures

```python
# Problem: mypy reports type errors in msgspec usage
# Solution: Use proper type annotations

from typing import Final

class ValidValidator:
    """Type-safe validator."""

    def __init__(self) -> None:
        self.decoder: Final = msgspec.json.Decoder(OrderEventMessage)
        self.encoder: Final = msgspec.json.Encoder()

    def validate(self, data: bytes) -> OrderEventMessage:
        """mypy understands return type."""
        return self.decoder.decode(data)
```
