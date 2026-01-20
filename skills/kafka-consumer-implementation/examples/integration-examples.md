# Kafka Consumer Integration Examples

This file contains real-world integration patterns and complete working examples for Kafka consumers.

## Table of Contents

- [Standalone Consumer with Async Loop](#standalone-consumer-with-async-loop)
- [Consumer with Pydantic Validation](#consumer-with-pydantic-validation)
- [Consumer with Retry Policies](#consumer-with-retry-policies)
- [Consumer with Custom Metrics](#consumer-with-custom-metrics)
- [Full Pipeline: Producer → Consumer → Storage](#full-pipeline-producer--consumer--storage)
- [Multi-Partition Consumer with Load Balancing](#multi-partition-consumer-with-load-balancing)

## Standalone Consumer with Async Loop

Minimal consumer that processes messages:

```python
# app/storage/infrastructure/loader_main.py
from __future__ import annotations

import asyncio
import signal
from typing import Any

from app.storage.adapters.kafka.consumer import OrderEventConsumer, KafkaConsumerException
from app.storage.adapters.kafka.translator import OrderEventTranslator
from app.storage.application.use_cases import LoadOrderUseCase
from app.storage.adapters.clickhouse.schema_manager import ClickHouseSchemaManager
from structlog import get_logger


class LoaderApplication:
    """Main loader application with event consumer."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        clickhouse_host: str,
        clickhouse_port: int,
    ) -> None:
        self.logger = get_logger(__name__)
        self.brokers = brokers
        self.topic = topic
        self.running = True

        # Initialize components
        self.schema_manager = ClickHouseSchemaManager(clickhouse_host, clickhouse_port)
        self.consumer = OrderEventConsumer(brokers, topic, group_id="storage_loader")
        self.translator = OrderEventTranslator()
        self.load_use_case = LoadOrderUseCase(self.schema_manager)

    def setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""

        def handle_shutdown(signum: int, frame: Any) -> None:
            self.logger.info("shutdown_signal_received", signal=signum)
            self.running = False

        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)

    async def run(self) -> None:
        """Main application loop."""
        self.setup_signal_handlers()
        self.logger.info("loader_application_started")

        try:
            # Initialize schema
            await self.schema_manager.initialize_schema()

            # Main consumer loop
            while self.running:
                try:
                    message = self.consumer.consume(timeout=5.0)

                    if message is None:
                        continue

                    # Translate to domain model
                    try:
                        order = self.translator.to_domain_order(message)
                    except ValueError as e:
                        self.logger.error("translation_failed", error=str(e))
                        self.consumer.commit()
                        continue

                    # Load into storage
                    try:
                        await self.load_use_case.execute(order)
                        self.logger.info("order_loaded", order_id=str(order.order_id))
                    except Exception as e:
                        self.logger.error("load_failed", error=str(e))
                        continue

                    # Commit offset
                    self.consumer.commit()

                except KafkaConsumerException as e:
                    self.logger.error("consume_error", error=str(e))
                    await asyncio.sleep(1)

        finally:
            self.consumer.close()
            self.logger.info("loader_application_stopped")


async def main() -> None:
    """Entry point."""
    app = LoaderApplication(
        brokers=["kafka:9092"],
        topic="orders",
        clickhouse_host="clickhouse",
        clickhouse_port=9000,
    )
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
```

## Consumer with Pydantic Validation

Add validation layer for message schemas:

```python
# app/storage/adapters/kafka/validated_consumer.py
from __future__ import annotations

from typing import Generic, TypeVar, Type

import msgspec
from pydantic import BaseModel, ValidationError
from confluent_kafka import Consumer, KafkaError, KafkaException
from structlog import get_logger


T = TypeVar('T', bound=BaseModel)


class ValidatedMessageConsumer(Generic[T]):
    """Consumer with Pydantic validation."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        group_id: str,
        model_class: Type[T],
    ) -> None:
        self.logger = get_logger(__name__)
        self.topic = topic
        self.model_class = model_class

        config = {
            "bootstrap.servers": ",".join(brokers),
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }

        self.consumer = Consumer(config)
        self.consumer.subscribe([topic])
        self.decoder = msgspec.json.Decoder(dict)

    def consume(self, timeout: float = 1.0) -> T | None:
        """Consume and validate message."""
        msg = self.consumer.poll(timeout=timeout)

        if msg is None or msg.error():
            return None

        try:
            # Deserialize with msgspec
            data = self.decoder.decode(msg.value())

            # Validate with Pydantic
            message = self.model_class(**data)

            self.logger.debug("message_consumed_and_validated")
            return message

        except msgspec.DecodeError as e:
            self.logger.error("deserialization_failed", error=str(e))
            raise

        except ValidationError as e:
            self.logger.error("validation_failed", errors=e.errors())
            raise

    def commit(self) -> None:
        """Commit current offset."""
        self.consumer.commit(asynchronous=False)

    def close(self) -> None:
        """Close consumer."""
        self.consumer.close()


# Usage
from pydantic import BaseModel, Field

class OrderEventDTO(BaseModel):
    """Validated order event schema."""
    order_id: str = Field(..., min_length=1)
    customer_name: str = Field(..., min_length=1)
    total_price: float = Field(..., gt=0)
    line_items: list[dict] = Field(default=[])


consumer = ValidatedMessageConsumer(
    brokers=["localhost:9092"],
    topic="orders",
    group_id="storage_loader",
    model_class=OrderEventDTO,
)

message = consumer.consume()
if message:
    print(f"Order {message.order_id} by {message.customer_name}")
    consumer.commit()
```

## Consumer with Retry Policies

Implement robust retry strategies:

```python
# app/storage/adapters/kafka/resilient_consumer.py
from __future__ import annotations

import asyncio
from typing import Callable, TypeVar, Any
from functools import wraps

from app.storage.adapters.kafka.consumer import OrderEventConsumer, KafkaConsumerException
from structlog import get_logger


T = TypeVar('T')


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_multiplier: float = 2.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for exponential backoff retry."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None
            logger = get_logger(__name__)

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except KafkaConsumerException as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        logger.warning(
                            "operation_failed_retrying",
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            delay=delay,
                            error=str(e),
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_multiplier, max_delay)
                    else:
                        logger.error(
                            "operation_failed_max_retries",
                            max_retries=max_retries,
                            error=str(e),
                        )

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class ResilientConsumer:
    """Consumer with built-in retry logic."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        group_id: str,
        max_retries: int = 3,
    ) -> None:
        self.consumer = OrderEventConsumer(brokers, topic, group_id)
        self.max_retries = max_retries
        self.logger = get_logger(__name__)

    @with_retry(max_retries=3, initial_delay=1.0, max_delay=10.0)
    async def consume_with_retry(self, timeout: float = 1.0) -> Any:
        """Consume with automatic retry on transient failures."""
        return self.consumer.consume(timeout=timeout)

    @with_retry(max_retries=3, initial_delay=1.0, max_delay=10.0)
    async def commit_with_retry(self) -> None:
        """Commit with automatic retry on transient failures."""
        self.consumer.commit()

    def close(self) -> None:
        """Close consumer."""
        self.consumer.close()


# Usage in application
async def resilient_load_order(
    consumer: ResilientConsumer,
    load_use_case: Any,
) -> None:
    """Load order with retry protection."""
    try:
        message = await consumer.consume_with_retry(timeout=5.0)

        if message is None:
            return

        order = translate_to_domain(message)
        await load_use_case.execute(order)

        # Commit with retries
        await consumer.commit_with_retry()

    except Exception as e:
        logger = get_logger(__name__)
        logger.error("load_order_failed", error=str(e))
```

## Consumer with Custom Metrics

Track performance metrics:

```python
# app/storage/adapters/kafka/metrics_consumer.py
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from app.storage.adapters.kafka.consumer import OrderEventConsumer
from structlog import get_logger


@dataclass
class ConsumerMetrics:
    """Track consumer performance metrics."""

    messages_consumed: int = 0
    messages_processed: int = 0
    messages_failed: int = 0
    bytes_consumed: int = 0
    total_processing_time_ms: int = 0
    total_commit_time_ms: int = 0
    errors: dict[str, int] = field(default_factory=dict)

    def record_consume(self, bytes_read: int) -> None:
        """Record message consumed."""
        self.messages_consumed += 1
        self.bytes_consumed += bytes_read

    def record_success(self, processing_time_ms: int, commit_time_ms: int) -> None:
        """Record successful processing."""
        self.messages_processed += 1
        self.total_processing_time_ms += processing_time_ms
        self.total_commit_time_ms += commit_time_ms

    def record_failure(self, error_type: str) -> None:
        """Record processing failure."""
        self.messages_failed += 1
        self.errors[error_type] = self.errors.get(error_type, 0) + 1

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary."""
        total = self.messages_consumed
        processed = self.messages_processed

        return {
            "messages_consumed": total,
            "messages_processed": processed,
            "messages_failed": self.messages_failed,
            "success_rate": (processed / total * 100) if total > 0 else 0,
            "avg_processing_time_ms": (
                self.total_processing_time_ms / processed if processed > 0 else 0
            ),
            "avg_commit_time_ms": (
                self.total_commit_time_ms / processed if processed > 0 else 0
            ),
            "bytes_consumed": self.bytes_consumed,
            "errors_by_type": self.errors,
            "throughput_msgs_per_sec": (
                total / (self.total_processing_time_ms / 1000)
                if self.total_processing_time_ms > 0
                else 0
            ),
        }


class MetricsConsumer:
    """Consumer that tracks metrics."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        group_id: str,
    ) -> None:
        self.consumer = OrderEventConsumer(brokers, topic, group_id)
        self.metrics = ConsumerMetrics()
        self.logger = get_logger(__name__)

    def consume(self, timeout: float = 1.0) -> Any:
        """Consume and track metrics."""
        msg = self.consumer.consume(timeout=timeout)

        if msg:
            self.metrics.record_consume(len(msg.value()) if msg.value() else 0)

        return msg

    def commit_with_metrics(self) -> None:
        """Commit and track metrics."""
        start = time.time()
        self.consumer.commit()
        elapsed_ms = (time.time() - start) * 1000
        self.metrics.total_commit_time_ms += int(elapsed_ms)

    def record_processing(self, processing_time_ms: int, success: bool, error_type: str | None = None) -> None:
        """Record processing metrics."""
        if success:
            self.metrics.record_success(processing_time_ms, 0)
        else:
            self.metrics.record_failure(error_type or "unknown")

    def log_metrics(self) -> None:
        """Log current metrics."""
        summary = self.metrics.get_summary()
        self.logger.info("metrics_summary", **summary)

    def close(self) -> None:
        """Close consumer and log final metrics."""
        self.log_metrics()
        self.consumer.close()


# Usage
async def process_with_metrics(metrics_consumer: MetricsConsumer) -> None:
    """Process messages and track metrics."""
    while True:
        start = time.time()

        try:
            message = metrics_consumer.consume(timeout=5.0)

            if message is None:
                continue

            # Process
            order = translate_to_domain(message)
            await load_use_case.execute(order)

            elapsed_ms = (time.time() - start) * 1000
            metrics_consumer.record_processing(int(elapsed_ms), success=True)

            # Commit
            metrics_consumer.commit_with_metrics()

            # Log periodically
            if metrics_consumer.metrics.messages_processed % 100 == 0:
                metrics_consumer.log_metrics()

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            metrics_consumer.record_processing(int(elapsed_ms), success=False, error_type=type(e).__name__)
```

## Full Pipeline: Producer → Consumer → Storage

Complete end-to-end example:

```python
# tests/integration/test_complete_pipeline.py
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator

import pytest
from testcontainers.kafka import KafkaContainer
from testcontainers.clickhouse import ClickHouseContainer

from app.extraction.adapters.kafka.producer import OrderEventProducer
from app.storage.adapters.kafka.consumer import OrderEventConsumer
from app.storage.adapters.kafka.translator import OrderEventTranslator
from app.storage.adapters.clickhouse.schema_manager import ClickHouseSchemaManager


@pytest.fixture
async def kafka_container() -> AsyncGenerator[KafkaContainer, None]:
    """Kafka container for testing."""
    with KafkaContainer() as container:
        yield container


@pytest.fixture
async def clickhouse_container() -> AsyncGenerator[ClickHouseContainer, None]:
    """ClickHouse container for testing."""
    with ClickHouseContainer() as container:
        yield container


@pytest.mark.asyncio
async def test_complete_pipeline(
    kafka_container: KafkaContainer,
    clickhouse_container: ClickHouseContainer,
) -> None:
    """Test complete pipeline: produce → consume → store."""

    # Get containers
    kafka_brokers = [kafka_container.get_bootstrap_server()]
    clickhouse_url = clickhouse_container.get_connection_url()

    # Initialize producer
    producer = OrderEventProducer(kafka_brokers, "orders")

    # Produce test orders
    test_orders = [
        {
            "order_id": "order-1",
            "customer_name": "Alice",
            "total_price": 100.0,
            "created_at": datetime.utcnow().isoformat(),
            "line_items": [
                {"product_id": "prod-1", "title": "Widget", "quantity": 1, "price": 100.0}
            ],
        },
        {
            "order_id": "order-2",
            "customer_name": "Bob",
            "total_price": 200.0,
            "created_at": datetime.utcnow().isoformat(),
            "line_items": [
                {"product_id": "prod-2", "title": "Gadget", "quantity": 2, "price": 100.0}
            ],
        },
    ]

    for order in test_orders:
        producer.publish(json.dumps(order))

    # Initialize consumer
    consumer = OrderEventConsumer(kafka_brokers, "orders", "test_group")
    translator = OrderEventTranslator()

    # Consume and translate
    consumed_orders = []
    for _ in range(len(test_orders)):
        message = consumer.consume(timeout=5.0)
        if message:
            order = translator.to_domain_order(message)
            consumed_orders.append(order)
            consumer.commit()

    # Verify all orders consumed
    assert len(consumed_orders) == 2
    assert consumed_orders[0].order_id.value == "order-1"
    assert consumed_orders[1].order_id.value == "order-2"

    # Cleanup
    producer.close()
    consumer.close()
```

## Multi-Partition Consumer with Load Balancing

Handle multiple partitions efficiently:

```python
# app/storage/adapters/kafka/partitioned_consumer.py
from __future__ import annotations

from typing import Any
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Consumer
from structlog import get_logger


class PartitionedConsumer:
    """Consumer that handles multiple partitions efficiently."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        group_id: str,
        num_workers: int = 4,
    ) -> None:
        self.consumer = Consumer({
            "bootstrap.servers": ",".join(brokers),
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        self.consumer.subscribe([topic])
        self.topic = topic
        self.num_workers = num_workers
        self.logger = get_logger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

    def consume_batch(self, batch_size: int = 100, timeout: float = 5.0) -> list[Any]:
        """Consume batch of messages across partitions."""
        messages = []

        while len(messages) < batch_size:
            msg = self.consumer.poll(timeout=timeout / (batch_size - len(messages)))

            if msg is None:
                break

            if not msg.error():
                messages.append(msg)
                self.logger.debug(
                    "message_batched",
                    partition=msg.partition(),
                    offset=msg.offset(),
                )

        self.logger.info("batch_consumed", batch_size=len(messages))
        return messages

    def process_batch_parallel(
        self,
        messages: list[Any],
        processor: Any,
    ) -> tuple[int, int]:
        """Process batch messages in parallel."""
        processed = 0
        failed = 0

        futures = [
            self.executor.submit(self._process_message, msg, processor)
            for msg in messages
        ]

        for future in futures:
            try:
                result = future.result(timeout=30.0)
                if result:
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                self.logger.error("parallel_processing_failed", error=str(e))
                failed += 1

        return processed, failed

    def _process_message(self, msg: Any, processor: Any) -> bool:
        """Process single message."""
        try:
            processor(msg)
            return True
        except Exception as e:
            self.logger.error("message_processing_failed", error=str(e))
            return False

    def commit(self) -> None:
        """Commit current offsets."""
        self.consumer.commit(asynchronous=False)

    def close(self) -> None:
        """Close consumer and executor."""
        self.executor.shutdown(wait=True)
        self.consumer.close()


# Usage
async def process_batch_pipeline(consumer: PartitionedConsumer) -> None:
    """Process messages in batches with parallel workers."""
    while True:
        # Consume batch
        messages = consumer.consume_batch(batch_size=100)

        if not messages:
            continue

        # Process in parallel
        processed, failed = consumer.process_batch_parallel(
            messages,
            processor=process_order,
        )

        # Commit after batch
        consumer.commit()

        logger = get_logger(__name__)
        logger.info(
            "batch_processed",
            total=len(messages),
            processed=processed,
            failed=failed,
        )
```

---

These examples demonstrate production-ready patterns for consuming Kafka messages with reliability, performance, and observability.
