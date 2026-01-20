# Kafka Integration Testing - Reference Guide

This file contains detailed troubleshooting, configuration reference, and best practices for Kafka integration testing.

## Table of Contents

- [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
- [TestContainers Configuration](#testcontainers-configuration)
- [Kafka Configuration Reference](#kafka-configuration-reference)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)
- [Type Safety in Tests](#type-safety-in-tests)
- [Docker Integration](#docker-integration)

## Common Issues and Troubleshooting

### Issue: Container Fails to Start

**Symptoms:**
```
ERROR: Could not start KafkaContainer
Docker daemon not running or not accessible
```

**Solutions:**
1. Verify Docker is running:
   ```bash
   docker ps
   ```
2. Check Docker socket permissions:
   ```bash
   ls -la /var/run/docker.sock
   ```
3. Add current user to docker group (Linux):
   ```bash
   sudo usermod -aG docker $USER
   ```

### Issue: Test Hangs on consume()

**Symptoms:**
- Test never returns from `consumer.consume(timeout=5.0)`
- Consumer seems frozen

**Common Causes:**
1. **Topic doesn't exist**: Consumer waits for messages indefinitely if no messages exist
   - Solution: Always publish before consuming in tests

2. **Broker not responding**: Connection timeout
   - Solution: Verify kafka_brokers fixture returns correct bootstrap server
   - Check: `print(kafka_container.get_bootstrap_server())`

3. **Consumer group already consuming**: Only one consumer per group per topic
   - Solution: Use unique group_id per test
   - Use: `f"test-group-{id(object())}"` for guaranteed uniqueness

**Debug:**
```python
def test_with_debug(kafka_brokers: list[str]) -> None:
    """Test with debug output."""
    print(f"Brokers: {kafka_brokers}")
    print(f"Broker count: {len(kafka_brokers)}")

    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic="test-topic",
        group_id="debug-group"
    )
    print(f"Consumer created: {consumer}")

    # Add timeout buffer
    message = consumer.consume(timeout=10.0)  # Increase from 5.0
    print(f"Message received: {message}")
```

### Issue: Malformed Message Exceptions

**Symptoms:**
```
KafkaConsumerException: Failed to deserialize message
JSON decode error: ...
```

**Solutions:**
1. Verify message format matches schema:
   ```python
   # Schema expects these fields
   event = OrderEventMessage(
       order_id="...",           # Required
       created_at="...",         # Required - ISO 8601 format
       customer_name="...",      # Required
       line_items=[...],         # Required - must be non-empty
       total_price=99.99,        # Required
   )
   ```

2. Check raw message bytes:
   ```python
   from confluent_kafka import Consumer

   conf = {"bootstrap.servers": brokers[0], "group.id": "debug"}
   consumer = Consumer(conf)
   consumer.subscribe(["test-topic"])

   msg = consumer.poll(5.0)
   if msg:
       print(f"Raw value: {msg.value()}")  # See exact bytes
       print(f"Raw key: {msg.key()}")
   ```

### Issue: Port Already in Use

**Symptoms:**
```
ERROR: Could not bind to port 9092 - Address already in use
```

**Solutions:**
1. KafkaContainer uses random ports by default (should not happen)
2. If binding to fixed port, stop conflicting process:
   ```bash
   lsof -i :9092
   kill -9 <PID>
   ```

### Issue: Offset Commit Fails

**Symptoms:**
```
KafkaError: Broker: Request timed out (_TIMED_OUT)
```

**Solutions:**
1. Ensure consumer has consumed a message before committing:
   ```python
   message = consumer.consume(timeout=5.0)
   if message:  # Only commit if message exists
       consumer.commit()
   ```

2. Increase commit timeout:
   ```python
   consumer.commit()  # May take longer in slow environments
   ```

### Issue: Tests Fail Intermittently

**Symptoms:**
- Some test runs pass, others fail randomly
- Timing-dependent failures

**Common Causes:**
1. **Insufficient wait for container startup**:
   - Solution: `time.sleep(2)` after starting container

2. **Too-short consume timeouts**:
   - Solution: Use 5.0+ second timeouts
   - Increase for slower CI environments

3. **Concurrent consumer groups**:
   - Solution: Use unique group IDs
   - Avoid test parallelization with same group

**Prevention:**
```python
import time

@pytest.fixture
def kafka_container() -> KafkaContainer:
    """Fixture with proper initialization wait."""
    container = KafkaContainer()
    container.start()
    time.sleep(2)  # Critical: wait for broker readiness
    yield container
    container.stop()
```

## TestContainers Configuration

### Basic Container Setup

```python
from testcontainers.kafka import KafkaContainer

# Default configuration
container = KafkaContainer()
container.start()
brokers = [container.get_bootstrap_server()]
container.stop()
```

### Custom Image Version

```python
# Use specific Kafka version
container = KafkaContainer(image="confluentinc/cp-kafka:7.5.0")
container.start()
```

### Environment Variables

```python
container = KafkaContainer()
container.with_env("KAFKA_HEAP_OPTS", "-Xmx512M -Xms256M")
container.start()
```

### Port Binding

```python
# Get dynamically assigned port
container = KafkaContainer()
container.start()
bootstrap_server = container.get_bootstrap_server()  # e.g., "localhost:32769"
```

### Container Lifecycle

```python
# Context manager pattern (recommended)
from testcontainers.kafka import KafkaContainer

with KafkaContainer() as kafka:
    brokers = [kafka.get_bootstrap_server()]
    # Test code here
    # Auto cleanup on exit
```

## Kafka Configuration Reference

### Producer Configuration

```python
# Default confluent-kafka producer settings used by OrderEventPublisher
producer_config = {
    "bootstrap.servers": ",".join(brokers),  # Required
    "client.id": "order-producer",           # Optional
    "acks": "all",                           # Wait for all replicas
    "retries": 3,                            # Retry failed sends
    "max.in.flight.requests.per.connection": 1,  # Preserve order
    "compression.type": "gzip",              # Compress messages
    "linger.ms": 100,                        # Batch messages
    "batch.size": 32768,                     # Batch size in bytes
}
```

### Consumer Configuration

```python
# Default confluent-kafka consumer settings used by OrderEventConsumer
consumer_config = {
    "bootstrap.servers": ",".join(brokers),  # Required
    "group.id": group_id,                    # Required
    "auto.offset.reset": "earliest",         # Start from beginning
    "enable.auto.commit": False,              # Manual commit only
    "session.timeout.ms": 6000,              # Heartbeat timeout
    "max.poll.interval.ms": 300000,          # Poll interval
    "isolation.level": "read_committed",     # Only read committed
}
```

### Performance Tuning

```python
# For high-throughput scenarios
consumer_config = {
    # ... base config
    "fetch.min.bytes": 1024,                 # Min bytes per fetch
    "fetch.max.wait.ms": 500,                # Max wait time
    "max.partition.fetch.bytes": 1048576,    # 1MB per partition
}

producer_config = {
    # ... base config
    "batch.num.messages": 100,               # Messages per batch
    "queue.buffering.max.messages": 100000,  # Output buffer
}
```

## Performance Optimization

### Message Batching

```python
def test_batch_performance(kafka_brokers: list[str]) -> None:
    """Test publishing many messages efficiently."""
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic="orders")

    # Batch publish
    num_messages = 1000
    start_time = time.time()

    for i in range(num_messages):
        event = OrderEventMessage(
            order_id=f"order_{i}",
            created_at="2024-01-01T12:00:00Z",
            customer_name=f"Customer {i}",
            line_items=[
                LineItemMessage(
                    line_item_id="item_1",
                    product_id="prod_1",
                    product_title="Product",
                    quantity=1,
                    price=50.0,
                )
            ],
            total_price=50.0,
        )
        publisher.publish_order(event)

    publisher.flush()
    elapsed = time.time() - start_time

    print(f"Published {num_messages} messages in {elapsed:.2f}s")
    print(f"Throughput: {num_messages / elapsed:.0f} msg/s")
```

### Consumer Polling Efficiency

```python
def test_consume_efficiency(kafka_brokers: list[str]) -> None:
    """Test efficient message consumption."""
    topic = "orders"
    group_id = "perf-group"

    # Setup: publish messages
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)
    for i in range(100):
        event = OrderEventMessage(...)
        publisher.publish_order(event)
    publisher.flush()

    # Consume with metrics
    consumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic=topic,
        group_id=group_id
    )

    start_time = time.time()
    message_count = 0

    while True:
        message = consumer.consume(timeout=1.0)
        if not message:
            break
        message_count += 1
        consumer.commit()

    elapsed = time.time() - start_time
    print(f"Consumed {message_count} messages in {elapsed:.2f}s")
    print(f"Throughput: {message_count / elapsed:.0f} msg/s")

    consumer.close()
```

### Parallel Consumption

```python
from concurrent.futures import ThreadPoolExecutor

def consume_partition(brokers: list[str], topic: str, group_id: str) -> int:
    """Consume from single partition in thread."""
    consumer = OrderEventConsumer(
        brokers=brokers,
        topic=topic,
        group_id=group_id
    )

    count = 0
    while True:
        message = consumer.consume(timeout=1.0)
        if not message:
            break
        count += 1
        consumer.commit()

    consumer.close()
    return count

def test_parallel_consumption(kafka_brokers: list[str]) -> None:
    """Test parallel consumption across threads."""
    topic = "parallel-orders"
    group_id = "parallel-group"

    # Publish messages
    publisher = OrderEventPublisher(brokers=kafka_brokers, topic=topic)
    for i in range(100):
        event = OrderEventMessage(...)
        publisher.publish_order(event)
    publisher.flush()

    # Consume in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(consume_partition, kafka_brokers, topic, group_id)
            for _ in range(3)
        ]
        results = [f.result() for f in futures]

    total_consumed = sum(results)
    print(f"Total consumed: {total_consumed}")
```

## Best Practices

### 1. Use Unique Consumer Groups

```python
# BAD: May conflict between tests
def test_consumer_1(kafka_brokers):
    consumer = OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id="test-group")

def test_consumer_2(kafka_brokers):
    consumer = OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id="test-group")
    # May wait for consumer_1 to finish!

# GOOD: Unique groups
def test_consumer_1(kafka_brokers):
    consumer = OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id="test-1")

def test_consumer_2(kafka_brokers):
    consumer = OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id="test-2")

# BETTER: Generate unique IDs
def test_consumer_3(kafka_brokers):
    unique_group = f"test-{id(object())}"
    consumer = OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id=unique_group)
```

### 2. Always Flush Producers

```python
# BAD: No flush - messages may not be sent
publisher = OrderEventPublisher(brokers=kafka_brokers, topic="orders")
publisher.publish_order(event)
# Test immediately - message may not be sent yet!

# GOOD: Flush waits for acknowledgment
publisher = OrderEventPublisher(brokers=kafka_brokers, topic="orders")
publisher.publish_order(event)
publisher.flush()  # Wait for ack
# Now safe to test
```

### 3. Clean Up Resources

```python
# BAD: May leak resources
def test_consumer(kafka_brokers):
    consumer = OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id="test")
    message = consumer.consume(timeout=5.0)
    assert message is not None
    # Forgot to close!

# GOOD: Always close
def test_consumer(kafka_brokers):
    consumer = OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id="test")
    try:
        message = consumer.consume(timeout=5.0)
        assert message is not None
    finally:
        consumer.close()

# BETTER: Use context managers
class OrderEventConsumer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

def test_consumer(kafka_brokers):
    with OrderEventConsumer(brokers=kafka_brokers, topic="orders", group_id="test") as consumer:
        message = consumer.consume(timeout=5.0)
        assert message is not None
```

### 4. Timeout Considerations

```python
# BAD: Too short for integration tests
message = consumer.consume(timeout=0.5)  # Unreliable

# GOOD: Sufficient timeout for testcontainers
message = consumer.consume(timeout=5.0)  # Reliable

# BETTER: Configurable based on environment
CONSUME_TIMEOUT = float(os.getenv("KAFKA_TEST_TIMEOUT", "5.0"))
message = consumer.consume(timeout=CONSUME_TIMEOUT)
```

### 5. Error Handling

```python
# BAD: Swallowing errors
try:
    publisher.publish_order(event)
except Exception:
    pass  # Silently fail

# GOOD: Explicit error handling
from app.extraction.adapters.kafka.producer import KafkaProducerError

try:
    publisher.publish_order(event)
except KafkaProducerError as e:
    logger.error("Failed to publish order", error=str(e))
    raise

# BETTER: Type-safe error handling
def publish_order_safely(publisher: OrderEventPublisher, event: OrderEventMessage) -> bool:
    """Publish with type-safe error handling."""
    try:
        publisher.publish_order(event)
        return True
    except KafkaProducerError as e:
        logger.error("publish_failed", error=str(e), event_id=event.order_id)
        return False
```

## Type Safety in Tests

### Proper Type Annotations

```python
from typing import Optional, List
from app.extraction.adapters.kafka.schemas import OrderEventMessage

def test_with_types(kafka_brokers: List[str]) -> None:
    """Test with full type annotations."""
    consumer: OrderEventConsumer = OrderEventConsumer(
        brokers=kafka_brokers,
        topic="orders",
        group_id="typed-test"
    )

    message: Optional[OrderEventMessage] = consumer.consume(timeout=5.0)

    if message is not None:
        # Type checker knows message is OrderEventMessage
        assert isinstance(message.order_id, str)
        consumer.close()
```

### Type-Safe Fixtures

```python
from typing import Generator

@pytest.fixture
def kafka_brokers(kafka_container: KafkaContainer) -> Generator[List[str], None, None]:
    """Fixture with proper type annotation."""
    brokers: List[str] = [kafka_container.get_bootstrap_server()]
    yield brokers
```

### Mypy Type Checking

```bash
# Run mypy on test files
mypy tests/integration/test_kafka_producer_integration.py --strict

# Check entire test suite
mypy tests/integration/ --strict
```

## Docker Integration

### Docker Compose for Integration Tests

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
```

### Running Tests Against Docker Compose Kafka

```bash
# Start Kafka stack
docker-compose -f docker-compose.test.yml up -d

# Run tests against it
KAFKA_BROKERS=localhost:9092 pytest tests/integration/

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### TestContainers vs Docker Compose

| Aspect | TestContainers | Docker Compose |
|--------|---|---|
| **Isolation** | Per-test container | Shared containers |
| **Speed** | Slower (new container each test) | Faster (reused) |
| **Cleanup** | Automatic | Manual |
| **Parallelization** | Excellent | Poor |
| **CI/CD** | Excellent | Requires setup |
| **Local Dev** | Good | Better |

**Recommendation**: Use TestContainers for unit/integration tests (automatic cleanup, parallelizable). Use Docker Compose for local development and E2E tests (faster setup/teardown).
