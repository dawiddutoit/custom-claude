# Detailed Kafka Consumer Implementation Guide

## Consumer Configuration in Detail

Configure the consumer with appropriate offset and commit strategy:

```python
from __future__ import annotations

from confluent_kafka import Consumer, KafkaException
from structlog import get_logger


class ConsumerConfig:
    """Kafka consumer configuration for exactly-once processing.

    Strategy:
    - auto.offset.reset=earliest: Start from beginning if no offset
    - enable.auto.commit=False: Manual offset management for safety
    - session.timeout.ms=300000: 5-minute session timeout
    - max.poll.interval.ms=300000: Allow 5 minutes for processing

    This ensures no message loss even during failures.
    """

    @staticmethod
    def create_config(
        brokers: list[str],
        group_id: str,
        topic: str,
    ) -> dict[str, str]:
        """Create consumer configuration.

        Args:
            brokers: List of broker addresses
            group_id: Consumer group ID (e.g., "storage_loader")
            topic: Topic to consume

        Returns:
            Configuration dict for Consumer
        """
        return {
            "bootstrap.servers": ",".join(brokers),
            "group.id": group_id,
            "auto.offset.reset": "earliest",  # Start from beginning if new
            "enable.auto.commit": False,  # Manual offset management
            "session.timeout.ms": 300000,  # 5 minutes
            "max.poll.interval.ms": 300000,  # 5 minutes for processing
        }
```

## Complete Consumer Adapter Implementation

```python
from __future__ import annotations

from typing import Any

import msgspec
from confluent_kafka import Consumer, KafkaError, KafkaException
from opentelemetry import trace
from structlog import get_logger

from app.storage.adapters.kafka.schemas import OrderEventMessage


class KafkaConsumerException(Exception):
    """Kafka consumer operational error."""


class OrderEventConsumer:
    """Consumes order events from Kafka with high performance and reliability.

    Features:
    - msgspec deserialization (10-20x faster than Pydantic)
    - confluent-kafka with production-grade configuration
    - OpenTelemetry distributed tracing
    - Manual offset management for exactly-once semantics
    - Comprehensive error handling and logging
    - Graceful handling of rebalancing

    Configuration (for exactly-once-per-process):
    - enable.auto.commit=False: Manual offset management
    - auto.offset.reset=earliest: Start from beginning if no offset
    - session.timeout.ms=300000: 5-minute session timeout
    - max.poll.interval.ms=300000: Allow 5 minutes for processing

    Args:
        brokers: List of Kafka broker addresses (e.g. ["localhost:9092"])
        topic: Kafka topic to consume
        group_id: Consumer group ID (e.g., "storage_loader", "reporter_app")

    Example:
        >>> consumer = OrderEventConsumer(
        ...     brokers=["kafka:9092"],
        ...     topic="orders",
        ...     group_id="storage_loader"
        ... )
        >>> while True:
        ...     msg = consumer.consume(timeout=5.0)
        ...     if msg:
        ...         process_message(msg)
        ...         consumer.commit()
        >>> consumer.close()
    """

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        group_id: str = "default_group",
    ) -> None:
        """Initialize Kafka consumer with production configuration.

        Args:
            brokers: List of broker addresses
            topic: Topic to subscribe to
            group_id: Consumer group ID for offset management

        Raises:
            KafkaConsumerException: Initialization failed
        """
        self.topic = topic
        self.logger = get_logger(__name__)
        self.tracer = trace.get_tracer(__name__)
        self.decoder = msgspec.json.Decoder(OrderEventMessage)

        config = {
            "bootstrap.servers": ",".join(brokers),
            "group.id": group_id,
            "auto.offset.reset": "earliest",  # Start from beginning if new
            "enable.auto.commit": False,  # Manual offset management (exactly-once)
            "session.timeout.ms": 300000,  # 5 minute session timeout
            "max.poll.interval.ms": 300000,  # Allow 5 minutes for processing
        }

        try:
            self.consumer = Consumer(config)
            self.consumer.subscribe([topic])
            self.logger.info(
                "kafka_consumer_initialized",
                topic=topic,
                group_id=group_id,
                brokers=brokers,
            )
        except KafkaException as e:
            self.logger.error("kafka_consumer_init_failed", error=str(e))
            raise KafkaConsumerException(f"Failed to initialize Kafka consumer: {e}") from e

    def consume(self, timeout: float = 1.0) -> OrderEventMessage | None:
        """Consume single order event from Kafka.

        Polls the broker with given timeout and deserializes the message.
        Returns None if no message available within timeout.

        Handles:
        - Partition EOF (end of partition, not an error)
        - Deserialization errors with detailed logging
        - Network errors with exception wrapping

        Args:
            timeout: Poll timeout in seconds (default: 1s for low latency)

        Returns:
            OrderEventMessage if available, None if timeout

        Raises:
            KafkaConsumerException: Deserialization failed or Kafka error
        """
        with self.tracer.start_as_current_span("consume_order") as span:
            span.set_attribute("topic", self.topic)

            try:
                msg = self.consumer.poll(timeout=timeout)

                if msg is None:
                    return None

                # Check for errors
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition - not an error, just return None
                        return None
                    else:
                        error_msg = str(msg.error())
                        self.logger.error("kafka_poll_error", error=error_msg)
                        raise KafkaConsumerException(f"Kafka error: {error_msg}")

                # Deserialize with msgspec (10-20x faster than Pydantic)
                try:
                    order_message: OrderEventMessage = self.decoder.decode(msg.value())
                    span.set_attribute("order_id", order_message.order_id)
                    span.set_attribute("partition", msg.partition())
                    span.set_attribute("offset", msg.offset())

                    self.logger.debug(
                        "message_consumed",
                        order_id=order_message.order_id,
                        partition=msg.partition(),
                        offset=msg.offset(),
                    )

                    return order_message

                except msgspec.DecodeError as e:
                    self.logger.error(
                        "message_decode_failed",
                        error=str(e),
                        partition=msg.partition(),
                        offset=msg.offset(),
                        value=msg.value()[:100] if msg.value() else None,  # First 100 bytes
                    )
                    raise KafkaConsumerException(f"Failed to decode message: {e}") from e

            except KafkaException as e:
                self.logger.error("consume_failed", error=str(e))
                raise KafkaConsumerException(f"Failed to consume message: {e}") from e

    def commit(self) -> None:
        """Commit current offset.

        Persists the offset of the last consumed message.
        Should be called after successful message processing.

        Call this after:
        1. Message successfully deserialized
        2. Message successfully processed/stored
        3. All side effects complete

        This prevents reprocessing on restart.

        Raises:
            KafkaConsumerException: Commit failed
        """
        try:
            self.consumer.commit(asynchronous=False)
            self.logger.debug("offset_committed")
        except KafkaException as e:
            self.logger.error("commit_failed", error=str(e))
            raise KafkaConsumerException(f"Failed to commit offset: {e}") from e

    def close(self) -> None:
        """Close consumer and release resources.

        Safely closes connection to Kafka cluster.
        Unsubscribes from topics and revokes partitions.
        """
        try:
            self.consumer.close()
            self.logger.info("kafka_consumer_closed")
        except KafkaException as e:
            self.logger.warning("consumer_close_error", error=str(e))
```

## Anti-Corruption Layer Implementation

```python
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.storage.adapters.kafka.schemas import OrderEventMessage
from app.storage.domain.entities import Order
from app.storage.domain.value_objects import Money, OrderId


class OrderEventTranslator:
    """Translates message schema to domain Order.

    Anti-corruption layer that:
    - Converts message DTOs to domain entities
    - Validates data before domain construction
    - Handles type conversions (str -> OrderId, float -> Money)
    - Normalizes timestamp formats
    - Applies domain invariants

    This ensures domain layer never sees raw Kafka messages.
    """

    @staticmethod
    def to_domain_order(message: OrderEventMessage) -> Order:
        """Convert OrderEventMessage to domain Order.

        Args:
            message: Message from Kafka topic

        Returns:
            Domain Order entity ready for storage

        Raises:
            ValueError: Message data violates domain invariants
        """
        # Validate before constructing domain object
        if not message.order_id:
            raise ValueError("order_id is required")
        if not message.line_items:
            raise ValueError("Order must have at least one line item")

        try:
            # Convert ISO timestamp to datetime
            created_at = datetime.fromisoformat(message.created_at)

            # Convert string/float to domain value objects
            order_id = OrderId(message.order_id)
            total_price = Money(Decimal(str(message.total_price)))

            # Construct domain entity
            order = Order(
                order_id=order_id,
                created_at=created_at,
                customer_name=message.customer_name,
                total_price=total_price,
                line_items=[],  # Populated below
            )

            return order

        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to translate message to domain order: {e}") from e
```

## Processing Loop Implementation

```python
from __future__ import annotations

import asyncio
import signal
from typing import Any

from app.storage.adapters.kafka.consumer import OrderEventConsumer, KafkaConsumerException
from app.storage.adapters.kafka.translator import OrderEventTranslator
from app.storage.application.use_cases import LoadOrderUseCase
from structlog import get_logger


class OrderConsumerLoop:
    """Main processing loop for consuming and loading orders.

    Responsibilities:
    1. Poll Kafka for messages
    2. Deserialize messages
    3. Translate to domain orders
    4. Load into storage
    5. Commit offsets
    6. Handle errors and shutdown

    Guarantees:
    - Exactly-once-per-restart processing (manual commits)
    - Graceful shutdown on signals
    - Comprehensive error logging
    """

    def __init__(
        self,
        consumer: OrderEventConsumer,
        load_use_case: LoadOrderUseCase,
    ) -> None:
        self.consumer = consumer
        self.load_use_case = load_use_case
        self.translator = OrderEventTranslator()
        self.logger = get_logger(__name__)
        self.running = True

    def setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""

        def handle_shutdown(signum: int, frame: Any) -> None:
            self.logger.info("shutdown_signal_received", signal=signum)
            self.running = False

        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)

    async def run(self) -> None:
        """Main consumer loop.

        Runs until shutdown signal received:
        1. Poll for message (5 second timeout)
        2. Translate to domain order
        3. Load into storage
        4. Commit offset
        5. Repeat

        Handles errors gracefully without stopping loop.
        """
        self.setup_signal_handlers()
        self.logger.info("starting_consumer_loop")

        try:
            while self.running:
                try:
                    # Poll with 5 second timeout
                    message = self.consumer.consume(timeout=5.0)

                    if message is None:
                        continue

                    # Translate to domain order
                    try:
                        order = self.translator.to_domain_order(message)
                    except ValueError as e:
                        self.logger.error("order_translation_failed", error=str(e))
                        # Still commit offset to avoid reprocessing bad message
                        self.consumer.commit()
                        continue

                    # Load into storage
                    try:
                        await self.load_use_case.execute(order)
                        self.logger.info("order_loaded", order_id=str(order.order_id))
                    except Exception as e:
                        self.logger.error("order_load_failed", error=str(e))
                        # Don't commit on failure - will retry on restart
                        continue

                    # Commit only after successful processing
                    try:
                        self.consumer.commit()
                    except KafkaConsumerException as e:
                        self.logger.error("commit_failed", error=str(e))
                        # Don't raise - will retry on next message

                except KafkaConsumerException as e:
                    self.logger.error("consume_error", error=str(e))
                    # Continue loop even on errors
                    await asyncio.sleep(1)  # Brief backoff before retry

        finally:
            self.logger.info("closing_consumer_loop")
            self.consumer.close()
```

## Lifecycle Management

```python
import asyncio
from contextlib import asynccontextmanager

from app.storage.adapters.kafka.consumer import OrderEventConsumer


@asynccontextmanager
async def managed_consumer(brokers: list[str], topic: str, group_id: str):
    """Context manager for consumer lifecycle.

    Ensures proper cleanup even on errors.
    """
    consumer = OrderEventConsumer(brokers, topic, group_id)

    def handle_shutdown(signum: int, frame: Any) -> None:
        print(f"Received signal {signum}, shutting down...")
        consumer.close()

    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        yield consumer
    finally:
        consumer.close()


# In loader_main.py:
async def main() -> None:
    async with managed_consumer(
        brokers=["kafka:9092"],
        topic="orders",
        group_id="storage_loader"
    ) as consumer:
        loop = OrderConsumerLoop(
            consumer=consumer,
            load_use_case=LoadOrderUseCase(repository),
        )
        await loop.run()
```

## Consumer Groups and Offset Management

### Consumer Groups

Consumer groups enable parallel processing across multiple consumers. All consumers in a group:
- Share responsibility for topic partitions
- Coordinate via Kafka group coordination protocol
- Automatically rebalance when members join/leave

**Recommended Configuration**:
```python
config = {
    "group.id": "storage_loader",  # Unique per processing service
    "auto.offset.reset": "earliest",  # Start from beginning if new
}
```

### Offset Management

The skill implements **manual offset management** for exactly-once-per-restart semantics:

1. **Disable Auto-Commit**:
   ```python
   "enable.auto.commit": False  # Manual control for safety
   ```

2. **Commit After Processing**:
   ```python
   # Process successfully
   await load_use_case.execute(order)

   # Only then commit offset
   consumer.commit()
   ```

3. **Offset Reset Behavior**:
   - `earliest`: Start from first available message (default for new groups)
   - `latest`: Start from latest message (for tailing)
   - Invalid offset: Uses configured strategy
