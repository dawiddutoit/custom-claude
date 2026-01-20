# Error Handling Patterns for Kafka Consumers

This reference guide covers comprehensive error handling strategies for production Kafka consumers.

## Overview

Error handling in Kafka consumers must address:
1. **Deserialization failures** - Invalid message format
2. **Offset commit failures** - Transient vs permanent failures
3. **Message processing failures** - Application-level errors
4. **Network errors** - Broker unavailability
5. **Rebalancing scenarios** - Partition reassignment
6. **Poison pills** - Unprocessable messages

## Deserialization Failure Handling

When msgspec cannot deserialize a message:

```python
def consume(self, timeout: float = 1.0) -> OrderEventMessage | None:
    """Handle deserialization with comprehensive error logging."""
    try:
        msg = self.consumer.poll(timeout=timeout)
        if msg is None or msg.error():
            return None

        try:
            return self.decoder.decode(msg.value())
        except msgspec.DecodeError as e:
            # Log all context for debugging
            self.logger.error(
                "deserialization_failed",
                error=str(e),
                partition=msg.partition(),
                offset=msg.offset(),
                topic=msg.topic(),
                value_snippet=msg.value()[:200].decode('utf-8', errors='replace'),
                value_length=len(msg.value()),
            )
            # Option 1: Skip message and commit (poison pill handling)
            self.consumer.commit()
            return None
            # Option 2: Store to dead letter queue (if available)
            # await self.dlq_publisher.publish(DLQMessage(...))
            # self.consumer.commit()
            # Option 3: Fail fast (let caller handle)
            # raise KafkaConsumerException(...) from e

    except KafkaException as e:
        self.logger.error("consume_failed", error=str(e))
        raise
```

**Decision Logic**:
- **Poison Pills** (corrupted/invalid forever): Commit and skip
- **Transient Invalid Format**: Retry or DLQ
- **Unknown Schema**: Log and DLQ

## Offset Commit Failures

Offset commits can fail transiently or permanently:

```python
def commit(self, timeout_ms: int = 30000) -> bool:
    """Commit with failure detection and retry logic."""
    try:
        # Attempt synchronous commit (waits for acknowledgment)
        self.consumer.commit(asynchronous=False)
        self.logger.debug("offset_committed_successfully")
        return True

    except KafkaException as e:
        error_code = getattr(e, 'code', None)

        # Transient errors - retry eligible
        if error_code in [KafkaError.REQUEST_TIMED_OUT, KafkaError.NETWORK_EXCEPTION]:
            self.logger.warning(
                "commit_failed_transient",
                error=str(e),
                error_code=error_code,
                will_retry=True
            )
            return False  # Caller should retry

        # Permanent errors - don't retry
        elif error_code == KafkaError.UNKNOWN_MEMBER_ID:
            self.logger.error(
                "commit_failed_permanent",
                error=str(e),
                error_code=error_code,
                action="consumer_group_mismatch"
            )
            raise CommitFailedPermanentError(str(e)) from e

        # Unknown error
        else:
            self.logger.error("commit_failed_unknown", error=str(e))
            return False
```

## Message Processing Failure Handling

Processing errors require strategic decisions:

```python
async def process_message(
    self,
    message: OrderEventMessage,
) -> ProcessResult:
    """Process with comprehensive error handling."""
    try:
        # Translate message to domain model
        try:
            order = OrderEventTranslator.to_domain_order(message)
        except ValueError as e:
            self.logger.error(
                "translation_failed",
                error=str(e),
                order_id=message.order_id,
            )
            # Translation errors are permanent - skip
            return ProcessResult.SKIP

        # Load into storage
        try:
            await self.load_use_case.execute(order)
            self.logger.info("order_loaded_successfully", order_id=str(order.order_id))
            return ProcessResult.SUCCESS

        except DatabaseConstraintError as e:
            # Duplicate key or constraint violation - skip
            self.logger.warning(
                "constraint_violation",
                error=str(e),
                order_id=str(order.order_id),
            )
            return ProcessResult.SKIP

        except DatabaseConnectionError as e:
            # Network error - can retry
            self.logger.error("database_connection_error", error=str(e))
            return ProcessResult.RETRY

        except Exception as e:
            # Unknown error - log and skip
            self.logger.error(
                "processing_failed_unknown",
                error=str(e),
                order_id=str(order.order_id),
            )
            return ProcessResult.SKIP

    except Exception as e:
        self.logger.critical("unexpected_error", error=str(e))
        raise
```

## Consumer Loop Error Handling

Main loop must handle errors without stopping:

```python
async def run(self) -> None:
    """Main loop with comprehensive error handling."""
    self.setup_signal_handlers()

    try:
        while self.running:
            try:
                # Poll for message
                message = self.consumer.consume(timeout=5.0)
                if message is None:
                    continue

                # Process message
                result = await self.process_message(message)

                if result == ProcessResult.SUCCESS:
                    # Commit only after successful processing
                    try:
                        self.consumer.commit()
                    except Exception as e:
                        self.logger.error("commit_failed", error=str(e))
                        # Don't exit - commit will retry on next cycle

                elif result == ProcessResult.SKIP:
                    # Still commit to avoid reprocessing
                    try:
                        self.consumer.commit()
                    except Exception as e:
                        self.logger.error("commit_failed_after_skip", error=str(e))

                elif result == ProcessResult.RETRY:
                    # Don't commit - will reprocess on next poll
                    await asyncio.sleep(1)  # Brief backoff

            except KafkaConsumerException as e:
                # Consumer errors - brief backoff and continue
                self.logger.error("consume_error", error=str(e))
                await asyncio.sleep(1)

            except Exception as e:
                # Unexpected errors - log and continue
                self.logger.critical("unexpected_loop_error", error=str(e))
                await asyncio.sleep(5)

    except KeyboardInterrupt:
        self.logger.info("received_interrupt_signal")
    finally:
        self.consumer.close()
        self.logger.info("consumer_closed")
```

## Rebalancing Error Handling

Handle rebalancing during processing:

```python
def on_partitions_revoked(self, partitions: list[Any]) -> None:
    """Called when partitions are revoked (rebalancing)."""
    self.logger.info(
        "partitions_revoked",
        partitions=[f"{p.topic()}:{p.partition()}" for p in partitions],
    )
    # Commit current offset before losing partition
    try:
        self.consumer.commit(asynchronous=False)
    except Exception as e:
        self.logger.error("commit_failed_before_revoke", error=str(e))

def on_partitions_assigned(self, partitions: list[Any]) -> None:
    """Called when new partitions are assigned (rebalancing)."""
    self.logger.info(
        "partitions_assigned",
        partitions=[f"{p.topic()}:{p.partition()}" for p in partitions],
    )
    # Resume normal processing
    for partition in partitions:
        offset = self.consumer.committed(partition)
        self.logger.info(
            "resuming_from_offset",
            partition=partition.partition(),
            offset=offset,
        )
```

## Dead Letter Queue Implementation

For poison pill messages that cannot be processed:

```python
from typing import Protocol

class DLQPublisher(Protocol):
    """Publisher interface for dead letter queues."""
    async def publish(self, message: dict[str, Any]) -> None:
        """Publish message to DLQ topic."""
        ...

class ConsumerWithDLQ:
    """Consumer that publishes unprocessable messages to DLQ."""

    def __init__(
        self,
        brokers: list[str],
        topic: str,
        group_id: str,
        dlq_publisher: DLQPublisher,
    ) -> None:
        self.consumer = OrderEventConsumer(brokers, topic, group_id)
        self.dlq_publisher = dlq_publisher

    async def handle_poison_pill(self, raw_message: bytes) -> None:
        """Send unprocessable message to DLQ."""
        try:
            await self.dlq_publisher.publish({
                "reason": "deserialization_failed",
                "payload": raw_message.decode('utf-8', errors='replace'),
                "timestamp": datetime.utcnow().isoformat(),
            })
            self.logger.info("poison_pill_sent_to_dlq")
        except Exception as e:
            self.logger.error("dlq_publish_failed", error=str(e))
            raise
```

## Exception Hierarchy

Use a clear exception hierarchy:

```python
class KafkaConsumerException(Exception):
    """Base consumer exception."""
    pass

class DeserializationException(KafkaConsumerException):
    """Message deserialization failed."""
    pass

class CommitFailedError(KafkaConsumerException):
    """Offset commit failed."""
    pass

class CommitFailedPermanentError(CommitFailedError):
    """Offset commit failed permanently (not retryable)."""
    pass

class CommitFailedTransientError(CommitFailedError):
    """Offset commit failed transiently (retryable)."""
    pass

class ProcessingException(KafkaConsumerException):
    """Message processing failed."""
    pass

class RetryableProcessingException(ProcessingException):
    """Processing failed but can be retried."""
    pass

class SkippableProcessingException(ProcessingException):
    """Processing failed but message should be skipped."""
    pass
```

## Retry Strategies

Implement exponential backoff for transient failures:

```python
import asyncio
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for exponential backoff retry."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except RetryableProcessingException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, max_delay)

            if last_exception:
                raise last_exception

        return wrapper
    return decorator

# Usage
class OrderConsumer:
    @with_exponential_backoff(max_retries=3)
    async def load_order(self, order: Order) -> None:
        """Load order with automatic retry on transient errors."""
        await self.load_use_case.execute(order)
```

## Monitoring and Observability

Log errors with structured context for debugging:

```python
from typing import Any

class StructuredErrorLogger:
    """Structured error logging for consumers."""

    @staticmethod
    def log_deserialization_error(
        error: Exception,
        partition: int,
        offset: int,
        value_length: int,
    ) -> None:
        """Log deserialization error with context."""
        logger = get_logger(__name__)
        logger.error(
            "deserialization_error",
            error_type=type(error).__name__,
            error_message=str(error),
            partition=partition,
            offset=offset,
            value_length=value_length,
            error_stack=traceback.format_exc(),
        )

    @staticmethod
    def log_processing_error(
        error: Exception,
        order_id: str,
        action: str,
    ) -> None:
        """Log processing error with context."""
        logger = get_logger(__name__)
        logger.error(
            "processing_error",
            error_type=type(error).__name__,
            error_message=str(error),
            order_id=order_id,
            action=action,
            error_stack=traceback.format_exc(),
        )
```

## Best Practices Summary

1. **Always log with context** - Include partition, offset, order ID, etc.
2. **Distinguish transient vs permanent failures** - Use appropriate retry strategies
3. **Commit after successful processing** - Never skip offset commits after success
4. **Implement graceful degradation** - Skip poisoned messages, don't stop consumer
5. **Use structured logging** - JSON-formatted logs for easy parsing
6. **Monitor offset lag** - Track consumer lag to detect slowdowns
7. **Implement DLQ** - Store unprocessable messages for later analysis
8. **Test error scenarios** - Unit tests for each error type
