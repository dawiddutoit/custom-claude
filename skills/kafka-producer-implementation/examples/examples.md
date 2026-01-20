# Kafka Producer Implementation Examples

## Example 1: Basic Order Publisher

Simple single-topic producer with error handling:

```python
# app/extraction/adapters/kafka/producer.py
from __future__ import annotations

import msgspec
from confluent_kafka import Producer, KafkaException
from structlog import get_logger

from app.extraction.adapters.kafka.schemas import OrderEventMessage


class OrderEventPublisher:
    """Basic Kafka producer for order events."""

    def __init__(self, brokers: list[str], topic: str) -> None:
        self.topic = topic
        self.encoder = msgspec.json.Encoder()
        self.logger = get_logger(__name__)

        config = {
            "bootstrap.servers": ",".join(brokers),
            "acks": "all",
            "enable.idempotence": True,
            "compression.type": "snappy",
        }

        try:
            self.producer = Producer(config)
        except KafkaException as e:
            self.logger.error("producer_init_failed", error=str(e))
            raise

    def publish_order(self, event: OrderEventMessage) -> None:
        """Publish single order event."""
        payload = self.encoder.encode(event)
        self.producer.produce(
            topic=self.topic,
            key=event.order_id.encode("utf-8"),
            value=payload,
        )
        self.producer.poll(0)

    def flush(self) -> None:
        """Wait for all messages to be published."""
        self.producer.flush(timeout=10.0)

    def close(self) -> None:
        """Close producer."""
        self.flush()
        self.logger.info("producer_closed")
```

## Example 2: Multi-Topic Producer with Topic Routing

Route different event types to different topics:

```python
from app.extraction.adapters.kafka.schemas import OrderEventMessage, OrderCancelledMessage


class MultiTopicEventPublisher:
    """Publisher that routes events to different topics based on type.

    Use when publishing multiple event types from single producer.
    """

    def __init__(self, brokers: list[str]) -> None:
        self.brokers = brokers
        self.producers: dict[str, OrderEventPublisher] = {}
        self.logger = get_logger(__name__)

    def get_producer(self, topic: str) -> OrderEventPublisher:
        """Get or create producer for topic."""
        if topic not in self.producers:
            self.producers[topic] = OrderEventPublisher(self.brokers, topic)
            self.logger.info("created_producer_for_topic", topic=topic)

        return self.producers[topic]

    def publish_order_created(self, event: OrderEventMessage) -> None:
        """Publish order created event."""
        publisher = self.get_producer("orders.created")
        publisher.publish_order(event)

    def publish_order_cancelled(self, event: OrderCancelledMessage) -> None:
        """Publish order cancelled event."""
        publisher = self.get_producer("orders.cancelled")
        # Would adapt event to schema if needed
        payload = msgspec.json.Encoder().encode(event)
        publisher.producer.produce(
            topic="orders.cancelled",
            key=event.order_id.encode("utf-8"),
            value=payload,
        )

    def close_all(self) -> None:
        """Close all producers."""
        for topic, publisher in self.producers.items():
            publisher.close()
            self.logger.info("closed_producer_for_topic", topic=topic)
```

## Example 3: Async Batch Publisher with Backpressure

Buffer messages and publish in batches:

```python
import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable


@dataclass
class BatchPublishConfig:
    max_batch_size: int = 100
    max_wait_ms: int = 1000  # 1 second


class AsyncBatchPublisher:
    """Publishes messages in batches for efficiency.

    Batches messages and publishes when:
    - Batch reaches max_batch_size, OR
    - max_wait_ms time elapses

    Reduces producer poll overhead by batching.
    """

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        config: BatchPublishConfig = BatchPublishConfig(),
    ) -> None:
        self.publisher = OrderEventPublisher(brokers, topic)
        self.config = config
        self.batch: list[OrderEventMessage] = []
        self.lock = asyncio.Lock()
        self.logger = get_logger(__name__)

    async def add_to_batch(self, event: OrderEventMessage) -> None:
        """Add event to batch, publish when full.

        Args:
            event: Event to add to batch
        """
        async with self.lock:
            self.batch.append(event)

            if len(self.batch) >= self.config.max_batch_size:
                await self._flush_batch()

    async def _flush_batch(self) -> None:
        """Publish all batched messages."""
        if not self.batch:
            return

        batch_to_publish = self.batch.copy()
        self.batch.clear()

        self.logger.info("publishing_batch", size=len(batch_to_publish))

        for event in batch_to_publish:
            try:
                self.publisher.publish_order(event)
            except Exception as e:
                self.logger.error("batch_publish_error", error=str(e))
                raise

        self.publisher.flush()

    async def flush_async(self) -> None:
        """Async flush remaining messages."""
        async with self.lock:
            await self._flush_batch()

    def close(self) -> None:
        """Close publisher."""
        self.publisher.close()


# Usage:
async def main():
    batch_publisher = AsyncBatchPublisher(
        ["localhost:9092"],
        "orders",
        config=BatchPublishConfig(max_batch_size=50, max_wait_ms=500),
    )

    # Simulate publishing many orders
    for i in range(150):
        event = OrderEventMessage(...)
        await batch_publisher.add_to_batch(event)

    # Flush remaining
    await batch_publisher.flush_async()
    batch_publisher.close()
```

## Example 4: Producer with Monitoring and Metrics

Publish with comprehensive metrics collection:

```python
import time
from dataclasses import dataclass, field


@dataclass
class PublisherMetrics:
    """Metrics for monitoring producer performance."""

    messages_published: int = 0
    messages_failed: int = 0
    total_latency_ms: float = 0.0
    failed_messages: list[str] = field(default_factory=list)

    @property
    def average_latency_ms(self) -> float:
        """Average publish latency."""
        if self.messages_published == 0:
            return 0.0
        return self.total_latency_ms / self.messages_published

    @property
    def error_rate(self) -> float:
        """Error rate as percentage."""
        total = self.messages_published + self.messages_failed
        if total == 0:
            return 0.0
        return (self.messages_failed / total) * 100


class MonitoredOrderPublisher:
    """Publisher that collects performance metrics."""

    def __init__(self, brokers: list[str], topic: str) -> None:
        self.publisher = OrderEventPublisher(brokers, topic)
        self.metrics = PublisherMetrics()
        self.logger = get_logger(__name__)

    def publish_order(self, event: OrderEventMessage) -> None:
        """Publish with metrics collection."""
        start_time = time.time()

        try:
            self.publisher.publish_order(event)
            latency_ms = (time.time() - start_time) * 1000

            self.metrics.messages_published += 1
            self.metrics.total_latency_ms += latency_ms

            if latency_ms > 100:  # Warn on slow publishes
                self.logger.warning(
                    "slow_publish",
                    order_id=event.order_id,
                    latency_ms=latency_ms,
                )

        except Exception as e:
            self.metrics.messages_failed += 1
            self.metrics.failed_messages.append(event.order_id)
            self.logger.error("publish_failed", order_id=event.order_id, error=str(e))
            raise

    def get_metrics(self) -> PublisherMetrics:
        """Get current metrics."""
        return self.metrics

    def log_metrics(self) -> None:
        """Log metrics summary."""
        m = self.metrics
        self.logger.info(
            "publisher_metrics",
            messages_published=m.messages_published,
            messages_failed=m.messages_failed,
            error_rate_pct=f"{m.error_rate:.2f}%",
            average_latency_ms=f"{m.average_latency_ms:.2f}",
        )

    def close(self) -> None:
        """Close publisher."""
        self.publisher.close()
        self.log_metrics()
```

## Example 5: Context Manager for Resource Management

Ensure proper cleanup with context manager:

```python
from contextlib import contextmanager
from typing import Generator
import signal


@contextmanager
def managed_publisher(
    brokers: list[str],
    topic: str,
) -> Generator[OrderEventPublisher, None, None]:
    """Context manager for publisher lifecycle.

    Ensures proper cleanup even on error.
    Handles graceful shutdown on signals.

    Example:
        >>> with managed_publisher(["localhost:9092"], "orders") as pub:
        ...     pub.publish_order(event)
        ...     pub.flush()
        # Publisher automatically closed
    """
    publisher = OrderEventPublisher(brokers, topic)
    logger = get_logger(__name__)

    def handle_signal(signum: int, frame: object) -> None:
        logger.info("shutdown_signal", signal=signum)
        publisher.close()
        exit(0)

    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        yield publisher
    finally:
        publisher.close()
        logger.info("publisher_context_closed")


# Usage in extractor_main.py:
def main() -> None:
    with managed_publisher(["kafka:9092"], "orders") as publisher:
        use_case = ExtractOrdersUseCase(shopify_gateway, publisher)
        count = asyncio.run(use_case.execute())
        print(f"Published {count} orders")
```

## Example 6: Testing with Mocks

Unit test producer without Kafka:

```python
from unittest.mock import MagicMock, patch, call
import pytest


@patch("app.extraction.adapters.kafka.producer.Producer")
def test_publisher_serializes_correctly(mock_producer_class: MagicMock) -> None:
    """Test publisher correctly serializes events."""
    mock_producer = MagicMock()
    mock_producer_class.return_value = mock_producer

    publisher = OrderEventPublisher(["localhost:9092"], "test-topic")

    event = OrderEventMessage(
        order_id="order_123",
        created_at="2024-01-01T12:00:00Z",
        customer_name="Test",
        line_items=[...],
        total_price=99.99,
    )

    publisher.publish_order(event)

    # Verify producer.produce was called with correct args
    mock_producer.produce.assert_called_once()
    call_kwargs = mock_producer.produce.call_args[1]

    assert call_kwargs["topic"] == "test-topic"
    assert call_kwargs["key"] == b"order_123"
    assert isinstance(call_kwargs["value"], bytes)  # msgspec produces bytes


@patch("app.extraction.adapters.kafka.producer.Producer")
def test_publisher_flushes_on_close(mock_producer_class: MagicMock) -> None:
    """Test publisher flushes messages on close."""
    mock_producer = MagicMock()
    mock_producer_class.return_value = mock_producer

    publisher = OrderEventPublisher(["localhost:9092"], "test-topic")
    publisher.close()

    # Verify flush was called
    mock_producer.flush.assert_called_once()
```

## Example 7: Integration with Use Case

Use producer in extraction use case:

```python
from app.extraction.application.use_cases import ExtractOrdersUseCase
from app.extraction.domain.value_objects import OrderId


class ExtractOrdersUseCase:
    """Extract orders and publish to Kafka."""

    def __init__(
        self,
        shopify_gateway: ShopifyGateway,
        publisher: OrderEventPublisher,
    ) -> None:
        self.shopify_gateway = shopify_gateway
        self.publisher = publisher
        self.logger = get_logger(__name__)

    async def execute(self) -> int:
        """Extract orders from Shopify and publish to Kafka.

        Returns:
            Number of orders published
        """
        self.logger.info("starting_order_extraction")

        try:
            # Fetch all orders from Shopify
            orders = await self.shopify_gateway.fetch_all_orders()
            self.logger.info("orders_fetched", count=len(orders))

            published_count = 0
            for order in orders:
                try:
                    # Build event message
                    event = self._to_event_message(order)

                    # Publish to Kafka
                    self.publisher.publish_order(event)
                    published_count += 1

                    self.logger.debug("order_published", order_id=str(order.order_id))

                except Exception as e:
                    self.logger.error(
                        "order_publish_error",
                        order_id=str(order.order_id),
                        error=str(e),
                    )
                    # Continue with next order (transactional per-message)

            # Ensure all messages are sent
            self.publisher.flush()

            self.logger.info(
                "extraction_complete",
                fetched=len(orders),
                published=published_count,
            )

            return published_count

        except Exception as e:
            self.logger.error("extraction_failed", error=str(e))
            raise

    def _to_event_message(self, order: Order) -> OrderEventMessage:
        """Convert domain Order to event message."""
        # Implementation from OrderEventTranslator
        ...
```

## Example 8: Performance Tuning

Optimize producer for throughput:

```python
class HighThroughputPublisher:
    """Publisher configured for maximum throughput.

    Configuration:
    - Large batch size (32KB) for better CPU utilization
    - Longer linger time (100ms) to fill batches
    - Compression enabled to reduce network traffic
    - Multiple in-flight requests for parallelism

    Trade-off: Higher latency (up to 100ms) for better throughput.
    """

    def __init__(self, brokers: list[str], topic: str) -> None:
        config = {
            "bootstrap.servers": ",".join(brokers),
            "acks": "all",
            "enable.idempotence": True,
            "compression.type": "snappy",
            "batch.size": 32768,  # 32KB batches
            "linger.ms": 100,  # Wait up to 100ms to fill batch
            "max.in.flight.requests.per.connection": 5,  # More parallelism (still ordered per partition key)
            "buffer.memory": 67108864,  # 64MB producer buffer
        }

        self.producer = Producer(config)
        self.topic = topic
        self.logger = get_logger(__name__)

    def publish_order(self, event: OrderEventMessage) -> None:
        """Publish with high throughput settings."""
        encoder = msgspec.json.Encoder()
        payload = encoder.encode(event)

        self.producer.produce(
            topic=self.topic,
            key=event.order_id.encode("utf-8"),
            value=payload,
        )

        # Don't poll on every message - batch the polls
        # This is handled by producer's background thread

    def close(self) -> None:
        """Close producer."""
        self.producer.flush(timeout=30.0)
        self.logger.info("high_throughput_publisher_closed")
```

## Example 9: Low-Latency Configuration

Optimize producer for low latency:

```python
class LowLatencyPublisher:
    """Publisher configured for minimum latency.

    Configuration:
    - Small batch size (1KB) to send quickly
    - No linger time (0ms) to send immediately
    - No compression overhead
    - Fewer in-flight requests for predictability

    Trade-off: Lower throughput but faster delivery.
    """

    def __init__(self, brokers: list[str], topic: str) -> None:
        config = {
            "bootstrap.servers": ",".join(brokers),
            "acks": "all",
            "enable.idempotence": True,
            "compression.type": "none",  # No compression overhead
            "batch.size": 1024,  # Small batches
            "linger.ms": 0,  # Send immediately
            "max.in.flight.requests.per.connection": 1,  # Sequential
        }

        self.producer = Producer(config)
        self.topic = topic
        self.logger = get_logger(__name__)

    def publish_order(self, event: OrderEventMessage) -> None:
        """Publish with low latency."""
        encoder = msgspec.json.Encoder()
        payload = encoder.encode(event)

        self.producer.produce(
            topic=self.topic,
            key=event.order_id.encode("utf-8"),
            value=payload,
        )

        # Poll immediately to flush batch
        self.producer.poll(0)

    def close(self) -> None:
        """Close producer."""
        self.producer.flush(timeout=10.0)
```

## Example 10: Graceful Shutdown with Signal Handling

Handle SIGTERM and SIGINT for clean shutdown:

```python
import signal
import sys


class ExtractorService:
    """Service that extracts orders and publishes to Kafka."""

    def __init__(self, brokers: list[str], topic: str) -> None:
        self.publisher = OrderEventPublisher(brokers, topic)
        self.running = True
        self.logger = get_logger(__name__)

    def setup_signals(self) -> None:
        """Register signal handlers for graceful shutdown."""

        def handle_sigterm(signum: int, frame: object) -> None:
            self.logger.info("sigterm_received")
            self.running = False

        def handle_sigint(signum: int, frame: object) -> None:
            self.logger.info("sigint_received")
            self.running = False

        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigint)

    async def run(self) -> None:
        """Main service loop."""
        self.setup_signals()
        self.logger.info("extractor_service_started")

        try:
            use_case = ExtractOrdersUseCase(
                shopify_gateway=ShopifyGateway(...),
                publisher=self.publisher,
            )

            while self.running:
                count = await use_case.execute()
                self.logger.info("extraction_cycle_complete", orders_published=count)

                # Wait before next extraction
                await asyncio.sleep(3600)  # 1 hour

        except Exception as e:
            self.logger.error("extractor_error", error=str(e))
            raise

        finally:
            self.logger.info("extractor_shutting_down")
            self.publisher.close()
            self.logger.info("extractor_shutdown_complete")


# In extractor_main.py:
async def main() -> None:
    service = ExtractorService(["kafka:9092"], "orders")
    await service.run()


if __name__ == "__main__":
    asyncio.run(main())
```
