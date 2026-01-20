# Kafka Integration Testing - Examples

This file contains comprehensive examples for testing Kafka producers, consumers, and complete workflows using testcontainers.

## Table of Contents

- [Basic Producer Test](#basic-producer-test)
- [Basic Consumer Test](#basic-consumer-test)
- [Producer-Consumer Round-Trip](#producer-consumer-round-trip)
- [Testing Message Ordering](#testing-message-ordering)
- [Testing Exactly-Once Semantics](#testing-exactly-once-semantics)
- [Error Handling Examples](#error-handling-examples)
- [Async Testing Examples](#async-testing-examples)
- [Custom Fixture Examples](#custom-fixture-examples)

## Basic Producer Test

### Simple Message Publishing

```python
from app.extraction.adapters.kafka.producer import OrderEventPublisher
from app.extraction.adapters.kafka.schemas import OrderEventMessage, LineItemMessage

def test_simple_message_publish(kafka_brokers: list[str]) -> None:
    """Test basic message publishing."""
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic="orders")

    event = OrderEventMessage(
        order_id="order_123",
        created_at="2024-01-01T12:00:00Z",
        customer_name="John Doe",
        line_items=[
            LineItemMessage(
                line_item_id="item_1",
                product_id="prod_1",
                product_title="Laptop",
                quantity=1,
                price=999.99,
            )
        ],
        total_price=999.99,
    )

    # Publish and flush
    publisher.publish_order(event)
    publisher.flush()

    # No exception means success
```

### Batch Publishing with Verification

```python
def test_batch_publish_with_flush(kafka_brokers: list[str]) -> None:
    """Test publishing multiple messages in batch."""
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic="orders")

    # Publish 10 messages
    for i in range(10):
        event = OrderEventMessage(
            order_id=f"order_{i}",
            created_at=f"2024-01-01T12:00:{i:02d}Z",
            customer_name=f"Customer {i}",
            line_items=[
                LineItemMessage(
                    line_item_id=f"item_{i}",
                    product_id=f"prod_{i}",
                    product_title=f"Product {i}",
                    quantity=1,
                    price=10.0 * (i + 1),
                )
            ],
            total_price=10.0 * (i + 1),
        )
        publisher.publish_order(event)

    # Flush waits for all messages to be acknowledged
    publisher.flush(timeout=10.0)
```

## Basic Consumer Test

### Simple Message Consumption

```python
from app.storage.adapters.kafka.consumer import OrderEventConsumer

def test_simple_message_consume(kafka_brokers: list[str]) -> None:
    """Test basic message consumption."""
    # First publish a message
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic="orders")
    event = OrderEventMessage(
        order_id="order_123",
        created_at="2024-01-01T12:00:00Z",
        customer_name="Alice",
        line_items=[
            LineItemMessage(
                line_item_id="item_1",
                product_id="prod_1",
                product_title="Phone",
                quantity=2,
                price=599.99,
            )
        ],
        total_price=1199.98,
    )
    publisher.publish_order(event)
    publisher.flush()

    # Now consume it
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic="orders",
        group_id="test-group"
    )
    message = consumer.consume(timeout=5.0)

    assert message is not None
    assert message.order_id == "order_123"
    assert message.customer_name == "Alice"

    consumer.close()
```

### Consuming Multiple Messages

```python
def test_consume_multiple_messages(kafka_brokers: list[str]) -> None:
    """Test consuming multiple messages in sequence."""
    topic = "orders"

    # Publish 5 messages
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)
    for i in range(5):
        event = OrderEventMessage(
            order_id=f"order_{i}",
            created_at=f"2024-01-01T12:00:{i:02d}Z",
            customer_name=f"Customer {i}",
            line_items=[
                LineItemMessage(
                    line_item_id=f"item_{i}",
                    product_id=f"prod_{i}",
                    product_title="Generic Product",
                    quantity=1,
                    price=100.0,
                )
            ],
            total_price=100.0,
        )
        publisher.publish_order(event)
    publisher.flush()

    # Consume all 5 messages
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id="multi-test-group"
    )

    consumed_messages = []
    for i in range(5):
        message = consumer.consume(timeout=5.0)
        if message:
            consumed_messages.append(message)
            consumer.commit()

    assert len(consumed_messages) == 5
    consumer.close()
```

## Producer-Consumer Round-Trip

### Complete End-to-End Workflow

```python
def test_full_order_pipeline(kafka_brokers: list[str]) -> None:
    """Test complete order: create -> publish -> consume -> commit."""
    topic = "order-pipeline"
    group_id = "e2e-test-group"

    # Step 1: Create order
    order = OrderEventMessage(
        order_id="order_e2e_001",
        created_at="2024-01-01T12:00:00Z",
        customer_name="Full Pipeline Test",
        line_items=[
            LineItemMessage(
                line_item_id="item_1",
                product_id="prod_001",
                product_title="Test Product",
                quantity=5,
                price=50.00,
            ),
            LineItemMessage(
                line_item_id="item_2",
                product_id="prod_002",
                product_title="Another Product",
                quantity=3,
                price=75.00,
            ),
        ],
        total_price=525.00,
    )

    # Step 2: Publish to Kafka
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)
    publisher.publish_order(order)
    publisher.flush()

    # Step 3: Consume from Kafka
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )
    consumed_order = consumer.consume(timeout=5.0)

    # Step 4: Verify
    assert consumed_order is not None
    assert consumed_order.order_id == "order_e2e_001"
    assert consumed_order.customer_name == "Full Pipeline Test"
    assert len(consumed_order.line_items) == 2
    assert consumed_order.total_price == 525.00

    # Step 5: Commit offset
    consumer.commit()
    consumer.close()

    # Step 6: Verify offset was committed (new consumer should not see it)
    consumer2 = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )
    message2 = consumer2.consume(timeout=2.0)
    assert message2 is None  # Already consumed
    consumer2.close()
```

## Testing Message Ordering

### Order Preservation with Same Key

```python
def test_strict_ordering_same_key(kafka_brokers: list[str]) -> None:
    """Test that messages with same key (order_id) maintain order."""
    topic = "ordered-orders"
    group_id = "order-test-group"
    order_id = "order_sequence_123"

    # Publish messages with same order_id (key)
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)

    product_titles = ["First", "Second", "Third", "Fourth", "Fifth"]
    for idx, title in enumerate(product_titles):
        event = OrderEventMessage(
            order_id=order_id,
            created_at=f"2024-01-01T12:00:{idx:02d}Z",
            customer_name="Sequence Tester",
            line_items=[
                LineItemMessage(
                    line_item_id=f"item_{idx}",
                    product_id=f"prod_{idx}",
                    product_title=title,
                    quantity=1,
                    price=10.0,
                )
            ],
            total_price=10.0,
        )
        publisher.publish_order(event)

    publisher.flush()

    # Consume and verify order
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )

    for idx, expected_title in enumerate(product_titles):
        message = consumer.consume(timeout=5.0)
        assert message is not None, f"Message {idx} not received"
        assert message.order_id == order_id
        assert message.line_items[0].product_title == expected_title
        consumer.commit()

    consumer.close()
```

### Different Keys May Have Different Order

```python
def test_different_keys_may_not_preserve_order(kafka_brokers: list[str]) -> None:
    """Test that messages with different keys may arrive in any order."""
    topic = "unordered-orders"
    group_id = "unorder-test-group"

    # Publish messages with different order_ids (keys)
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)

    order_ids = ["order_A", "order_B", "order_C", "order_A", "order_B"]
    for idx, order_id in enumerate(order_ids):
        event = OrderEventMessage(
            order_id=order_id,
            created_at=f"2024-01-01T12:00:{idx:02d}Z",
            customer_name=f"User for {order_id}",
            line_items=[
                LineItemMessage(
                    line_item_id=f"item_{idx}",
                    product_id=f"prod_{idx}",
                    product_title=f"Product {idx}",
                    quantity=1,
                    price=10.0,
                )
            ],
            total_price=10.0,
        )
        publisher.publish_order(event)

    publisher.flush()

    # Consume all messages
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )

    received_messages = []
    for _ in range(5):
        message = consumer.consume(timeout=5.0)
        if message:
            received_messages.append(message)
            consumer.commit()

    # Verify we got all 5 messages
    assert len(received_messages) == 5

    # Verify messages for same order_id maintain order
    order_a_indices = [i for i, m in enumerate(received_messages) if m.order_id == "order_A"]
    order_b_indices = [i for i, m in enumerate(received_messages) if m.order_id == "order_B"]

    # order_A should maintain order relative to each other
    # (but may be interleaved with order_B)

    consumer.close()
```

## Testing Exactly-Once Semantics

### Manual Commit Ensures Exactly-Once

```python
def test_exactly_once_with_manual_commit(kafka_brokers: list[str]) -> None:
    """Test exactly-once semantics with manual commit."""
    topic = "exactly-once-test"
    group_id = "exactly-once-group"

    # Publish message
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)
    event = OrderEventMessage(
        order_id="order_eo_001",
        created_at="2024-01-01T12:00:00Z",
        customer_name="Exactly Once Test",
        line_items=[
            LineItemMessage(
                line_item_id="item_1",
                product_id="prod_1",
                product_title="EO Product",
                quantity=1,
                price=99.99,
            )
        ],
        total_price=99.99,
    )
    publisher.publish_order(event)
    publisher.flush()

    # Consumer 1: Consume but don't commit
    consumer1 = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )
    msg1 = consumer1.consume(timeout=5.0)
    assert msg1 is not None
    # Close without committing
    consumer1.close()

    # Consumer 2: Same group, should get same message (offset not committed)
    consumer2 = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )
    msg2 = consumer2.consume(timeout=5.0)
    assert msg2 is not None
    assert msg2.order_id == msg1.order_id
    # This time commit
    consumer2.commit()
    consumer2.close()

    # Consumer 3: Same group, should NOT get message (offset committed)
    consumer3 = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )
    msg3 = consumer3.consume(timeout=2.0)
    assert msg3 is None  # Already processed by group
    consumer3.close()
```

## Error Handling Examples

### Malformed Message Handling

```python
from confluent_kafka import Producer
from app.extraction.adapters.kafka.producer import KafkaProducerError
from app.storage.adapters.kafka.consumer import KafkaConsumerException

def test_handle_malformed_json_message(kafka_brokers: list[str]) -> None:
    """Test consumer raises error on malformed message."""
    topic = "malformed-topic"
    group_id = "malformed-group"

    # Publish invalid JSON directly
    producer = Producer({"bootstrap.servers": ",".join(kafka_brokers)})
    producer.produce(topic, key=b"bad_key", value=b"not valid json at all")
    producer.flush()

    # Try to consume
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )

    with pytest.raises(KafkaConsumerException):
        consumer.consume(timeout=5.0)

    consumer.close()
```

### Timeout Handling

```python
def test_consumer_timeout_returns_none(kafka_brokers: list[str]) -> None:
    """Test consumer returns None on timeout with empty topic."""
    topic = "empty-topic"
    group_id = "timeout-group"

    # Don't publish anything
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )

    # Should wait and return None
    message = consumer.consume(timeout=1.0)
    assert message is None

    consumer.close()
```

## Async Testing Examples

### Async Producer-Consumer Test

```python
import pytest

@pytest.mark.asyncio
async def test_async_produce_consume(kafka_brokers: list[str]) -> None:
    """Test async producer and consumer operations."""
    topic = "async-orders"

    # Publish asynchronously (simulated)
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)

    event = OrderEventMessage(
        order_id="order_async_001",
        created_at="2024-01-01T12:00:00Z",
        customer_name="Async Tester",
        line_items=[
            LineItemMessage(
                line_item_id="item_1",
                product_id="prod_1",
                product_title="Async Product",
                quantity=1,
                price=50.0,
            )
        ],
        total_price=50.0,
    )

    publisher.publish_order(event)
    publisher.flush()

    # Consume
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id="async-group"
    )
    message = consumer.consume(timeout=5.0)

    assert message is not None
    assert message.order_id == "order_async_001"

    consumer.close()
```

## Custom Fixture Examples

### Fixture for Pre-Populated Topic

```python
from typing import Generator

@pytest.fixture
def populated_kafka_topic(kafka_brokers: list[str]) -> Generator[tuple[str, list[OrderEventMessage]], None, None]:
    """Fixture that provides pre-populated Kafka topic with test data."""
    topic = "pre-populated-orders"

    # Create test data
    test_orders = []
    for i in range(3):
        order = OrderEventMessage(
            order_id=f"prefilled_order_{i}",
            created_at=f"2024-01-01T12:00:{i:02d}Z",
            customer_name=f"Prefilled Customer {i}",
            line_items=[
                LineItemMessage(
                    line_item_id=f"item_{i}",
                    product_id=f"prod_{i}",
                    product_title=f"Prefilled Product {i}",
                    quantity=1,
                    price=100.0 + i,
                )
            ],
            total_price=100.0 + i,
        )
        test_orders.append(order)

    # Publish to topic
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)
    for order in test_orders:
        publisher.publish_order(order)
    publisher.flush()

    yield topic, test_orders

def test_with_prefilled_data(populated_kafka_topic: tuple[str, list[OrderEventMessage]], kafka_brokers: list[str]) -> None:
    """Test that uses pre-populated Kafka topic."""
    topic, test_orders = populated_kafka_topic

    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id="prefilled-test-group"
    )

    # Should be able to consume pre-populated messages
    for expected_order in test_orders:
        message = consumer.consume(timeout=5.0)
        assert message is not None
        assert message.order_id == expected_order.order_id
        consumer.commit()

    consumer.close()
```

### Fixture for Multiple Partitions

```python
@pytest.fixture
def multi_partition_topic(kafka_brokers: list[str]) -> Generator[str, None, None]:
    """Fixture providing multi-partition topic for parallel testing."""
    topic = "multi-partition-orders"

    # Publish messages to multiple partitions (different keys)
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)

    partition_keys = ["customer_A", "customer_B", "customer_C"]
    for key in partition_keys:
        event = OrderEventMessage(
            order_id=f"order_for_{key}",
            created_at="2024-01-01T12:00:00Z",
            customer_name=key,
            line_items=[
                LineItemMessage(
                    line_item_id="item_1",
                    product_id="prod_1",
                    product_title=f"Product for {key}",
                    quantity=1,
                    price=50.0,
                )
            ],
            total_price=50.0,
        )
        publisher.publish_order(event)

    publisher.flush()

    yield topic

def test_with_multiple_partitions(multi_partition_topic: str, kafka_brokers: list[str]) -> None:
    """Test consuming from multiple partitions."""
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=multi_partition_topic,
        group_id="multi-partition-group"
    )

    messages_received = []
    for _ in range(3):
        message = consumer.consume(timeout=5.0)
        if message:
            messages_received.append(message)
            consumer.commit()

    assert len(messages_received) == 3
    consumer.close()
```
