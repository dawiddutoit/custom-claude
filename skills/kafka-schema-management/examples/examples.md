# Kafka Schema Management Examples

This document provides comprehensive examples for designing, validating, and evolving Kafka message schemas.

## Table of Contents

- [Complete Order Event Schema](#complete-order-event-schema)
- [Event Envelope Pattern](#event-envelope-pattern)
- [Multiple Event Types](#multiple-event-types)
- [Schema Versioning](#schema-versioning)
- [Testing Multiple Schema Versions](#testing-multiple-schema-versions)
- [Schema Validation Edge Cases](#schema-validation-edge-cases)
- [Performance Considerations](#performance-considerations)

## Complete Order Event Schema

This example shows a production-grade order event schema with complete validation.

### Schema Definition

```python
from __future__ import annotations

import msgspec
from typing import Optional


class MoneyMessage(msgspec.Struct, frozen=True):
    """Money value object.

    Attributes:
        amount: Monetary amount as float
        currency: ISO 4217 currency code (default USD)
    """
    amount: float
    currency: str = "USD"


class LineItemMessage(msgspec.Struct, frozen=True):
    """Line item in an order.

    Attributes:
        line_item_id: Unique identifier for this line item
        product_id: Product catalog ID
        product_title: Human-readable product name
        quantity: Number of units (must be >= 1)
        price: Unit price per product
        discount: Optional discount on this item
    """
    line_item_id: str
    product_id: str
    product_title: str
    quantity: int
    price: float
    discount: float = 0.0


class AddressMessage(msgspec.Struct, frozen=True):
    """Shipping address for order.

    Attributes:
        street: Street address
        city: City name
        postal_code: Postal/ZIP code
        country: Country name or code
    """
    street: str
    city: str
    postal_code: str
    country: str


class OrderEventMessage(msgspec.Struct, frozen=True):
    """Complete order event.

    Immutable event representing a customer order with full details.

    Attributes:
        order_id: Unique order identifier
        created_at: ISO 8601 timestamp when order was created
        customer_name: Customer name for delivery
        customer_email: Customer email for notifications
        shipping_address: Delivery address
        line_items: List of products in order
        total_price: Total order value (validated in consumer)
        notes: Optional order notes

    Version History:
    - 1.0: Initial schema
    - 1.1: Added customer_email and notes (backward compatible)
    - 1.2: Added shipping_address (backward compatible)
    """
    order_id: str
    created_at: str  # ISO 8601: "2024-01-01T12:00:00Z"
    customer_name: str
    customer_email: str
    shipping_address: AddressMessage
    line_items: list[LineItemMessage]
    total_price: float
    notes: str = ""
```

### Validator with Complete Error Handling

```python
from __future__ import annotations

import msgspec
from structlog import get_logger
from typing import Final


class SchemaValidationError(Exception):
    """Schema validation or deserialization failed."""
    pass


class OrderMessageValidator:
    """Validates order event messages."""

    MAX_ORDER_ID_LENGTH: Final = 100
    MAX_CUSTOMER_NAME_LENGTH: Final = 255
    MAX_NOTES_LENGTH: Final = 1000
    PRICE_TOLERANCE: Final = 0.01  # 1 cent for rounding

    def __init__(self) -> None:
        """Initialize validator with pre-compiled codecs."""
        self.decoder = msgspec.json.Decoder(OrderEventMessage)
        self.encoder = msgspec.json.Encoder()
        self.logger = get_logger(__name__)

    def validate(self, data: bytes) -> OrderEventMessage:
        """Validate and deserialize message.

        Args:
            data: Raw JSON bytes from Kafka

        Returns:
            Validated OrderEventMessage

        Raises:
            SchemaValidationError: Deserialization or validation failed
        """
        try:
            message: OrderEventMessage = self.decoder.decode(data)
            self._validate_business_rules(message)
            return message
        except msgspec.DecodeError as e:
            self.logger.error(
                "decode_error",
                error=str(e),
                data_preview=data[:200].decode(errors='ignore')
            )
            raise SchemaValidationError(f"Failed to decode: {e}") from e

    def _validate_business_rules(self, msg: OrderEventMessage) -> None:
        """Validate business rules that msgspec can't check.

        Args:
            msg: Decoded message

        Raises:
            SchemaValidationError: Business rule violated
        """
        # Order ID validation
        if not msg.order_id or len(msg.order_id) > self.MAX_ORDER_ID_LENGTH:
            raise SchemaValidationError(
                f"Invalid order_id: must be 1-{self.MAX_ORDER_ID_LENGTH} chars"
            )

        # Customer name validation
        if not msg.customer_name or len(msg.customer_name) > self.MAX_CUSTOMER_NAME_LENGTH:
            raise SchemaValidationError(
                f"Invalid customer_name: must be 1-{self.MAX_CUSTOMER_NAME_LENGTH} chars"
            )

        # Email validation (basic)
        if "@" not in msg.customer_email or "." not in msg.customer_email:
            raise SchemaValidationError("Invalid email format")

        # Line items validation
        if not msg.line_items:
            raise SchemaValidationError("Order must have at least one line item")

        total_calculated = 0.0
        for i, item in enumerate(msg.line_items):
            if item.quantity <= 0:
                raise SchemaValidationError(f"Item {i}: quantity must be >= 1")
            if item.price < 0:
                raise SchemaValidationError(f"Item {i}: price must be >= 0")
            if item.discount < 0 or item.discount > item.price:
                raise SchemaValidationError(f"Item {i}: invalid discount")

            item_total = (item.price - item.discount) * item.quantity
            total_calculated += item_total

        # Validate total price
        if abs(total_calculated - msg.total_price) > self.PRICE_TOLERANCE:
            self.logger.warning(
                "price_mismatch",
                expected=total_calculated,
                actual=msg.total_price,
                difference=msg.total_price - total_calculated
            )

        # Notes length
        if len(msg.notes) > self.MAX_NOTES_LENGTH:
            raise SchemaValidationError(
                f"Notes too long: max {self.MAX_NOTES_LENGTH} chars"
            )

    def serialize(self, message: OrderEventMessage) -> bytes:
        """Serialize message to JSON bytes.

        Args:
            message: OrderEventMessage to serialize

        Returns:
            JSON bytes ready for Kafka

        Raises:
            SchemaValidationError: Serialization failed
        """
        try:
            return self.encoder.encode(message)
        except msgspec.EncodeError as e:
            self.logger.error("encode_error", error=str(e))
            raise SchemaValidationError(f"Failed to encode: {e}") from e
```

## Event Envelope Pattern

Use event envelopes when you have multiple event types and need explicit versioning.

### Envelope Schema

```python
from __future__ import annotations

import msgspec
from enum import Enum
from typing import Literal


class EventTypeEnum(str, Enum):
    """Known event types."""
    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    ORDER_CANCELLED = "order.cancelled"
    PAYMENT_PROCESSED = "payment.processed"


class EventEnvelopeMessage(msgspec.Struct, frozen=True):
    """Generic event envelope wrapping domain events.

    Allows evolution and multiple event types in same topic.

    Attributes:
        event_id: Unique event identifier (UUID)
        event_type: Type of event (use enum values)
        event_version: Schema version as semantic version "1.0"
        timestamp: ISO 8601 when event occurred
        correlation_id: Distributed tracing ID
        source: Origin service/context
        payload: Event-specific data as JSON
    """
    event_id: str
    event_type: str  # Use EventTypeEnum.value
    event_version: str  # "1.0", "2.0", etc.
    timestamp: str  # ISO 8601
    correlation_id: str
    source: str
    payload: dict[str, object]  # JSON-serializable dict


class EventEnvelopeValidator:
    """Validates event envelopes."""

    def __init__(self) -> None:
        self.decoder = msgspec.json.Decoder(EventEnvelopeMessage)
        self.encoder = msgspec.json.Encoder()
        self.logger = get_logger(__name__)

    def validate(self, data: bytes) -> EventEnvelopeMessage:
        """Validate event envelope."""
        try:
            envelope = self.decoder.decode(data)
            self._validate_rules(envelope)
            return envelope
        except msgspec.DecodeError as e:
            raise SchemaValidationError(f"Invalid envelope: {e}") from e

    def _validate_rules(self, envelope: EventEnvelopeMessage) -> None:
        """Check envelope business rules."""
        # Validate event type is known
        valid_types = {e.value for e in EventTypeEnum}
        if envelope.event_type not in valid_types:
            self.logger.warning(
                "unknown_event_type",
                event_type=envelope.event_type
            )

        # Version must be semantic
        if not self._is_valid_version(envelope.event_version):
            raise SchemaValidationError(
                f"Invalid event_version: {envelope.event_version}"
            )

        # IDs must be non-empty
        if not envelope.event_id or not envelope.correlation_id:
            raise SchemaValidationError("event_id and correlation_id required")

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version string is semantic."""
        parts = version.split(".")
        return (
            len(parts) == 2 and
            all(p.isdigit() for p in parts)
        )

    def serialize(self, envelope: EventEnvelopeMessage) -> bytes:
        """Serialize envelope to bytes."""
        try:
            return self.encoder.encode(envelope)
        except msgspec.EncodeError as e:
            raise SchemaValidationError(f"Failed to encode: {e}") from e
```

## Multiple Event Types

Example of handling different event types in the same message stream.

```python
from __future__ import annotations

import msgspec
from typing import Union


class OrderCreatedPayload(msgspec.Struct, frozen=True):
    """Payload for order.created event."""
    order_id: str
    customer_id: str
    items_count: int
    total_amount: float


class OrderUpdatedPayload(msgspec.Struct, frozen=True):
    """Payload for order.updated event."""
    order_id: str
    status: str
    updated_fields: list[str]  # ["status", "shipping_address", ...]


class PaymentProcessedPayload(msgspec.Struct, frozen=True):
    """Payload for payment.processed event."""
    payment_id: str
    order_id: str
    amount: float
    method: str


# Union type for all possible payloads
EventPayload = Union[
    OrderCreatedPayload,
    OrderUpdatedPayload,
    PaymentProcessedPayload
]


class TypedEventEnvelope(msgspec.Struct, frozen=True):
    """Event envelope with typed payload."""
    event_id: str
    event_type: str
    event_version: str
    timestamp: str
    correlation_id: str
    payload: dict[str, object]  # Store as dict, cast when needed


def decode_event_payload(
    envelope: TypedEventEnvelope,
) -> OrderCreatedPayload | OrderUpdatedPayload | PaymentProcessedPayload:
    """Decode payload based on event_type.

    Args:
        envelope: Envelope with payload dict

    Returns:
        Typed payload

    Raises:
        SchemaValidationError: Unknown event type
    """
    payload = envelope.payload
    event_type = envelope.event_type

    try:
        if event_type == "order.created":
            return msgspec.json.decode(
                msgspec.json.encode(payload),
                type=OrderCreatedPayload
            )
        elif event_type == "order.updated":
            return msgspec.json.decode(
                msgspec.json.encode(payload),
                type=OrderUpdatedPayload
            )
        elif event_type == "payment.processed":
            return msgspec.json.decode(
                msgspec.json.encode(payload),
                type=PaymentProcessedPayload
            )
        else:
            raise SchemaValidationError(f"Unknown event type: {event_type}")
    except msgspec.DecodeError as e:
        raise SchemaValidationError(
            f"Failed to decode {event_type} payload: {e}"
        ) from e
```

## Schema Versioning

Example of handling multiple schema versions in production.

```python
from __future__ import annotations

import msgspec


class OrderEventV1(msgspec.Struct, frozen=True):
    """Order schema version 1.0 (deprecated).

    This schema is deprecated. Use OrderEventV2 for new messages.
    Kept for backward compatibility with old messages.
    """
    order_id: str
    created_at: str
    customer_name: str
    line_items: list[LineItemMessage]
    total_price: float


class OrderEventV2(msgspec.Struct, frozen=True):
    """Order schema version 2.0 (current).

    Added customer_email and notes fields.
    Backward compatible with V1 messages.
    """
    order_id: str
    created_at: str
    customer_name: str
    customer_email: str  # New in V2
    line_items: list[LineItemMessage]
    total_price: float
    notes: str = ""  # New in V2


# Current version alias
OrderEvent = OrderEventV2


class VersionedOrderValidator:
    """Handles multiple order schema versions."""

    def __init__(self) -> None:
        self.decoder_v2 = msgspec.json.Decoder(OrderEventV2)
        self.decoder_v1 = msgspec.json.Decoder(OrderEventV1)
        self.encoder = msgspec.json.Encoder()
        self.logger = get_logger(__name__)

    def validate(self, data: bytes) -> OrderEventV2:
        """Validate message, supporting multiple versions.

        Strategy:
        1. Try current version (V2) first - fastest path
        2. Fall back to V1 - older messages
        3. Upgrade V1 to V2 format

        Args:
            data: Raw message bytes

        Returns:
            OrderEventV2 message

        Raises:
            SchemaValidationError: Neither version matched
        """
        # Try current version first
        try:
            return self.decoder_v2.decode(data)
        except msgspec.DecodeError:
            pass

        # Fall back to V1
        try:
            msg_v1 = self.decoder_v1.decode(data)
            upgraded = self._upgrade_v1_to_v2(msg_v1)
            self.logger.info(
                "message_upgraded",
                from_version="1.0",
                to_version="2.0",
                order_id=upgraded.order_id
            )
            return upgraded
        except msgspec.DecodeError as e:
            raise SchemaValidationError(
                f"Message matches neither V1 nor V2: {e}"
            ) from e

    @staticmethod
    def _upgrade_v1_to_v2(msg_v1: OrderEventV1) -> OrderEventV2:
        """Upgrade V1 message to V2.

        Args:
            msg_v1: Message in V1 schema

        Returns:
            Message in V2 schema with defaults for new fields
        """
        return OrderEventV2(
            order_id=msg_v1.order_id,
            created_at=msg_v1.created_at,
            customer_name=msg_v1.customer_name,
            customer_email="unknown@example.com",  # Default for old messages
            line_items=msg_v1.line_items,
            total_price=msg_v1.total_price,
            notes=""  # Default for old messages
        )

    def serialize(self, message: OrderEventV2) -> bytes:
        """Serialize V2 message to bytes."""
        return self.encoder.encode(message)
```

## Testing Multiple Schema Versions

```python
import pytest
from app.extraction.adapters.kafka.schemas import (
    OrderEventV1, OrderEventV2, VersionedOrderValidator,
    SchemaValidationError
)


class TestVersionedSchemas:
    """Test schema versioning and migration."""

    @pytest.fixture
    def validator(self) -> VersionedOrderValidator:
        return VersionedOrderValidator()

    def test_validate_v2_message(self, validator: VersionedOrderValidator) -> None:
        """Test validation of current V2 schema."""
        msg = OrderEventV2(
            order_id="order_123",
            created_at="2024-01-01T12:00:00Z",
            customer_name="John Doe",
            customer_email="john@example.com",
            line_items=[],
            total_price=0.0
        )

        bytes_data = validator.encoder.encode(msg)
        decoded = validator.validate(bytes_data)

        assert decoded.order_id == "order_123"
        assert decoded.customer_email == "john@example.com"

    def test_validate_v1_message_and_upgrade(
        self,
        validator: VersionedOrderValidator
    ) -> None:
        """Test validation and upgrade of V1 schema."""
        msg_v1 = OrderEventV1(
            order_id="order_456",
            created_at="2024-01-01T12:00:00Z",
            customer_name="Jane Doe",
            line_items=[],
            total_price=100.0
        )

        bytes_data = validator.decoder_v1.encode(msg_v1)
        decoded = validator.validate(bytes_data)

        # Should be upgraded to V2
        assert decoded.order_id == "order_456"
        assert decoded.customer_email == "unknown@example.com"  # Default
        assert decoded.notes == ""  # Default

    def test_invalid_message_raises_error(
        self,
        validator: VersionedOrderValidator
    ) -> None:
        """Test that invalid messages raise SchemaValidationError."""
        invalid_json = b'{"order_id": "123"}'  # Missing required fields

        with pytest.raises(SchemaValidationError):
            validator.validate(invalid_json)
```

## Schema Validation Edge Cases

```python
import pytest
from decimal import Decimal


class TestSchemaEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def validator(self) -> OrderMessageValidator:
        return OrderMessageValidator()

    def test_empty_order_id_fails(self, validator: OrderMessageValidator) -> None:
        """Empty order_id should fail validation."""
        # Create message with empty order_id
        invalid_msg = OrderEventMessage(
            order_id="",  # Empty!
            created_at="2024-01-01T12:00:00Z",
            customer_name="John",
            customer_email="john@example.com",
            shipping_address=AddressMessage(
                street="123 Main St",
                city="New York",
                postal_code="10001",
                country="USA"
            ),
            line_items=[],
            total_price=0.0
        )

        with pytest.raises(SchemaValidationError, match="Invalid order_id"):
            validator._validate_business_rules(invalid_msg)

    def test_zero_line_items_fails(self, validator: OrderMessageValidator) -> None:
        """Order with no items should fail."""
        invalid_msg = OrderEventMessage(
            order_id="order_123",
            created_at="2024-01-01T12:00:00Z",
            customer_name="John",
            customer_email="john@example.com",
            shipping_address=AddressMessage(
                street="123 Main St",
                city="New York",
                postal_code="10001",
                country="USA"
            ),
            line_items=[],  # No items!
            total_price=0.0
        )

        with pytest.raises(SchemaValidationError, match="at least one"):
            validator._validate_business_rules(invalid_msg)

    def test_negative_price_fails(self, validator: OrderMessageValidator) -> None:
        """Negative prices should fail."""
        item = LineItemMessage(
            line_item_id="item_1",
            product_id="prod_1",
            product_title="Laptop",
            quantity=1,
            price=-100.0  # Negative!
        )

        invalid_msg = OrderEventMessage(
            order_id="order_123",
            created_at="2024-01-01T12:00:00Z",
            customer_name="John",
            customer_email="john@example.com",
            shipping_address=AddressMessage(
                street="123 Main St",
                city="New York",
                postal_code="10001",
                country="USA"
            ),
            line_items=[item],
            total_price=0.0
        )

        with pytest.raises(SchemaValidationError, match="price must be"):
            validator._validate_business_rules(invalid_msg)

    def test_price_mismatch_warning(
        self,
        validator: OrderMessageValidator,
        caplog: pytest.LogCaptureFixture
    ) -> None:
        """Total price mismatch should log warning but not fail."""
        item = LineItemMessage(
            line_item_id="item_1",
            product_id="prod_1",
            product_title="Laptop",
            quantity=1,
            price=999.99
        )

        # Total price doesn't match (999.99 vs 500.00)
        msg = OrderEventMessage(
            order_id="order_123",
            created_at="2024-01-01T12:00:00Z",
            customer_name="John",
            customer_email="john@example.com",
            shipping_address=AddressMessage(
                street="123 Main St",
                city="New York",
                postal_code="10001",
                country="USA"
            ),
            line_items=[item],
            total_price=500.00  # Doesn't match!
        )

        # Should not raise, just log warning
        validator._validate_business_rules(msg)
        # Would be logged with structlog
```

## Performance Considerations

### Benchmarking Schema Operations

```python
import time
from typing import Final


class SchemaBenchmark:
    """Measure schema performance."""

    ITERATIONS: Final = 10_000

    @staticmethod
    def benchmark_serialization(validator: OrderMessageValidator) -> None:
        """Benchmark message serialization speed."""
        msg = OrderEventMessage(
            order_id="order_123",
            created_at="2024-01-01T12:00:00Z",
            customer_name="John Doe",
            customer_email="john@example.com",
            shipping_address=AddressMessage(
                street="123 Main St",
                city="New York",
                postal_code="10001",
                country="USA"
            ),
            line_items=[
                LineItemMessage(
                    line_item_id="item_1",
                    product_id="prod_1",
                    product_title="Product",
                    quantity=1,
                    price=99.99
                )
            ],
            total_price=99.99
        )

        start = time.perf_counter()
        for _ in range(SchemaBenchmark.ITERATIONS):
            validator.serialize(msg)
        elapsed = time.perf_counter() - start

        per_op = (elapsed / SchemaBenchmark.ITERATIONS) * 1_000_000  # microseconds
        print(f"Serialization: {per_op:.2f} microseconds per operation")
        print(f"Total: {elapsed:.2f} seconds for {SchemaBenchmark.ITERATIONS} operations")

    @staticmethod
    def benchmark_deserialization(
        validator: OrderMessageValidator,
        sample_bytes: bytes
    ) -> None:
        """Benchmark message deserialization speed."""
        start = time.perf_counter()
        for _ in range(SchemaBenchmark.ITERATIONS):
            validator.validate(sample_bytes)
        elapsed = time.perf_counter() - start

        per_op = (elapsed / SchemaBenchmark.ITERATIONS) * 1_000_000
        print(f"Deserialization: {per_op:.2f} microseconds per operation")
        print(f"Total: {elapsed:.2f} seconds for {SchemaBenchmark.ITERATIONS} operations")
```

### Key Performance Notes

1. **msgspec vs json module**: msgspec is 10-20x faster
2. **msgspec vs Pydantic**: msgspec is 5-10x faster for serialization
3. **Pre-compiled Decoders/Encoders**: Create once, reuse many times (singleton pattern)
4. **Frozen Structs**: Slightly faster than mutable structs (no mutation checks)
5. **Type Specificity**: `list[LineItemMessage]` faster than `list[dict]`

**Production Recommendation**: Use connection pools with validator instances:

```python
class ValidatorPool:
    """Reusable validator pool for concurrent environments."""

    def __init__(self, pool_size: int = 10) -> None:
        self._validators = [
            OrderMessageValidator() for _ in range(pool_size)
        ]
        self._current = 0

    def get_validator(self) -> OrderMessageValidator:
        """Get next validator in round-robin fashion."""
        validator = self._validators[self._current]
        self._current = (self._current + 1) % len(self._validators)
        return validator
```
