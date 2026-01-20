# Kafka Producer Error Handling

## Error Classification

### Transient Errors (Retry)

**Definition**: Temporary failures that may succeed on retry.

**Examples:**
- Broker temporarily unavailable
- Network timeout
- Metadata refresh needed
- Temporary buffer full

**Strategy:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
def publish_with_retry(publisher: OrderEventPublisher, event: OrderEventMessage) -> None:
    """Publish with automatic exponential backoff retry."""
    publisher.publish_order(event)
```

### Permanent Errors (Don't Retry)

**Definition**: Failures that won't recover with retries.

**Examples:**
- Invalid message schema (DeserializationError)
- Message too large for broker
- Topic does not exist (if create-on-produce disabled)
- Authentication failure
- Invalid configuration

**Strategy:**
```python
def publish_with_early_exit(publisher: OrderEventPublisher, event: OrderEventMessage) -> None:
    """Publish with early exit on permanent errors."""
    try:
        publisher.publish_order(event)
    except SchemaValidationError:
        # Permanent: don't retry
        logger.error("schema_invalid", event_id=event.order_id)
        raise
    except KafkaProducerError as e:
        if "MessageSizeTooLarge" in str(e):
            # Permanent: don't retry
            logger.error("message_too_large", event_id=event.order_id)
            raise
        else:
            # Transient: retry
            logger.warning("kafka_error", error=str(e))
            raise
```

## Error Handling Patterns

### Pattern 1: Retry with Exponential Backoff

Use for transient failures that may recover:

```python
import asyncio
from typing import TypeVar, Callable, Any

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., T],
    args: tuple[Any, ...],
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
) -> T:
    """Execute function with exponential backoff retry.

    Args:
        func: Function to execute
        args: Function arguments
        max_retries: Maximum retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)

    Returns:
        Function result

    Raises:
        Last exception if all retries exhausted
    """
    delay = initial_delay
    last_exception: Exception | None = None

    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            last_exception = e

            if attempt == max_retries - 1:
                # Last attempt - raise
                break

            # Calculate next delay with exponential backoff and jitter
            logger.warning(
                "retry_attempt",
                attempt=attempt + 1,
                max_retries=max_retries,
                delay=delay,
                error=str(e),
            )

            await asyncio.sleep(delay)

            # Exponential backoff: delay *= 2, capped at max_delay
            delay = min(delay * 2, max_delay)

    # All retries exhausted
    logger.error("all_retries_exhausted", max_retries=max_retries, last_error=str(last_exception))
    raise last_exception or RuntimeError("Unknown error")


# Usage:
async def main():
    publisher = OrderEventPublisher(["localhost:9092"], "orders")
    event = OrderEventMessage(...)

    try:
        await retry_with_backoff(
            publisher.publish_order,
            (event,),
            max_retries=5,
            initial_delay=1.0,
            max_delay=30.0,
        )
    except KafkaProducerError as e:
        logger.error("publish_failed_after_retries", error=str(e))
        raise
```

### Pattern 2: Dead Letter Queue (DLQ)

Send unrecoverable messages to DLQ:

```python
class DeadLetterQueue:
    """Stores unrecoverable messages for later analysis.

    Messages that fail validation or exceed retry limits
    are sent here for manual inspection.
    """

    def __init__(self, dlq_topic: str = "orders-dlq"):
        self.dlq_topic = dlq_topic
        self.logger = get_logger(__name__)

    def send_to_dlq(
        self,
        event: OrderEventMessage,
        error: str,
        attempt_count: int,
    ) -> None:
        """Send event to DLQ with error metadata.

        Args:
            event: Event that failed
            error: Error message
            attempt_count: Number of retry attempts
        """
        dlq_message = {
            "original_event": event,
            "error": error,
            "attempts": attempt_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Serialize and publish to DLQ topic
        encoder = msgspec.json.Encoder()
        payload = encoder.encode(dlq_message)

        # Use DLQ producer (usually separate, low-priority producer)
        self.logger.error(
            "sending_to_dlq",
            order_id=event.order_id,
            error=error,
            topic=self.dlq_topic,
        )


class OrderPublisherWithDLQ:
    """Publisher with DLQ fallback for unrecoverable messages."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        dlq_topic: str = "orders-dlq",
    ) -> None:
        self.publisher = OrderEventPublisher(brokers, topic)
        self.dlq = DeadLetterQueue(dlq_topic)
        self.logger = get_logger(__name__)

    async def publish_with_dlq_fallback(self, event: OrderEventMessage) -> None:
        """Publish with DLQ fallback for unrecoverable errors.

        1. Try to publish with retries
        2. If all retries fail, send to DLQ
        3. Log error for monitoring
        """
        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                self.publisher.publish_order(event)
                return  # Success

            except SchemaValidationError as e:
                # Permanent error - don't retry
                self.dlq.send_to_dlq(
                    event=event,
                    error=f"Schema validation failed: {e}",
                    attempt_count=1,
                )
                self.logger.error("permanent_error_sent_to_dlq", order_id=event.order_id)
                return

            except KafkaProducerError as e:
                attempt += 1
                if attempt == max_retries:
                    # All retries exhausted - send to DLQ
                    self.dlq.send_to_dlq(
                        event=event,
                        error=f"Kafka producer error: {e}",
                        attempt_count=attempt,
                    )
                    self.logger.error("max_retries_exceeded_sent_to_dlq", order_id=event.order_id)
                    return
                else:
                    # Retry with backoff
                    delay = 2 ** attempt
                    self.logger.warning(
                        "publish_retry",
                        order_id=event.order_id,
                        attempt=attempt,
                        max_attempts=max_retries,
                        delay=delay,
                        error=str(e),
                    )
                    await asyncio.sleep(delay)
```

### Pattern 3: Circuit Breaker

Stop publishing if broker is persistently unavailable:

```python
from enum import Enum
from datetime import datetime, timedelta


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """Prevents cascading failures when broker is down.

    States:
    - CLOSED: Normal, requests pass through
    - OPEN: Broker down, reject requests immediately
    - HALF_OPEN: Testing if broker recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.logger = get_logger(__name__)

    def record_success(self) -> None:
        """Record successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.logger.info("circuit_breaker_closed")

    def record_failure(self) -> None:
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.error(
                "circuit_breaker_opened",
                failures=self.failure_count,
                threshold=self.failure_threshold,
            )

    def call(self, func: Callable[[], T]) -> T:
        """Execute function if circuit allows."""
        # Check if should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            elapsed = datetime.utcnow() - (self.last_failure_time or datetime.utcnow())
            if elapsed > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                self.logger.info("circuit_breaker_half_open")

        # Reject if OPEN
        if self.state == CircuitState.OPEN:
            raise RuntimeError("Circuit breaker OPEN - broker unavailable")

        # Execute
        try:
            result = func()
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class OrderPublisherWithCircuitBreaker:
    """Publisher with circuit breaker for fault tolerance."""

    def __init__(self, brokers: list[str], topic: str) -> None:
        self.publisher = OrderEventPublisher(brokers, topic)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)
        self.logger = get_logger(__name__)

    def publish_order(self, event: OrderEventMessage) -> None:
        """Publish with circuit breaker protection."""
        try:
            self.circuit_breaker.call(lambda: self.publisher.publish_order(event))
        except RuntimeError as e:
            # Circuit is OPEN - fail fast
            self.logger.error("publish_rejected_circuit_open", order_id=event.order_id)
            raise KafkaProducerError(str(e)) from e
        except KafkaProducerError as e:
            # Let circuit breaker handle failure counting
            raise
```

### Pattern 4: Idempotent Publishing with Deduplication

Ensure exactly-once publishing despite retries:

```python
import hashlib
from datetime import datetime


class IdempotentPublisher:
    """Publisher that deduplicates messages across retries.

    Even if message is published multiple times due to retries,
    downstream ensures it's only processed once.

    Kafka provides this natively with:
    - enable.idempotence=True
    - acks=all
    - max.in.flight.requests.per.connection=1
    """

    def __init__(self, brokers: list[str], topic: str) -> None:
        self.publisher = OrderEventPublisher(brokers, topic)
        self.logger = get_logger(__name__)

    def publish_idempotent(self, event: OrderEventMessage) -> None:
        """Publish with idempotence guarantee.

        Kafka's idempotence=True ensures exactly-one-delivery
        even if producer retries.

        Idempotence guarantees:
        - No duplicate messages
        - Order preserved within partition
        - Even across producer restarts
        """
        # Kafka handles deduplication automatically
        # Order ID becomes the idempotency key (partition key)
        self.publisher.publish_order(event)

        self.logger.info(
            "order_published_idempotent",
            order_id=event.order_id,
            idempotence_key=f"{event.order_id}:{event.created_at}",
        )
```

## Monitoring and Alerting

### Key Metrics

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProducerMetrics:
    """Metrics for monitoring producer health."""

    messages_published: int = 0
    messages_failed: int = 0
    messages_retried: int = 0
    total_publish_time_ms: float = 0.0
    last_error: str | None = None
    circuit_breaker_state: str = "closed"


class MetricsCollector(Protocol):
    """Protocol for metrics collection."""

    def record_publish_success(self, duration_ms: float) -> None:
        """Record successful publish."""
        ...

    def record_publish_failure(self, error: str) -> None:
        """Record failed publish."""
        ...

    def get_metrics(self) -> ProducerMetrics:
        """Get current metrics."""
        ...
```

### Health Check

```python
def is_producer_healthy(publisher: OrderEventPublisher, metrics: ProducerMetrics) -> bool:
    """Check if producer is healthy.

    Criteria:
    - Circuit breaker not OPEN
    - Recent errors < threshold
    - Messages successfully published
    """
    error_rate = metrics.messages_failed / max(metrics.messages_published, 1)
    return error_rate < 0.1 and metrics.circuit_breaker_state != "open"
```

## Summary

| Error Type | Strategy | Example |
|-----------|----------|---------|
| Transient | Retry with backoff | Network timeout |
| Permanent | Fail fast, log, DLQ | Invalid schema |
| Unknown | Circuit breaker | Broker offline |
| Transient Long | DLQ + alert ops | Broker down >10min |
