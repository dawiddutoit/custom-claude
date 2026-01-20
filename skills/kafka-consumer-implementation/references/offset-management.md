# Consumer Group and Offset Management

This reference guide covers best practices for managing consumer groups, offsets, and rebalancing in production Kafka consumers.

## Table of Contents

- [Consumer Groups](#consumer-groups)
- [Offset Commit Strategies](#offset-commit-strategies)
- [Offset Tracking and Lag](#offset-tracking-and-lag)
- [Rebalancing Behavior](#rebalancing-behavior)
- [Offset Reset Scenarios](#offset-reset-scenarios)
- [Consumer Group Lifecycle](#consumer-group-lifecycle)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)

## Consumer Groups

### Group Coordination

Consumer groups coordinate via the Kafka group coordinator:

```python
from confluent_kafka import Consumer

class ConsumerGroupCoordinator:
    """Manages consumer group lifecycle and coordination."""

    def __init__(self, brokers: list[str], group_id: str, topic: str) -> None:
        """Initialize consumer with group coordination.

        Args:
            brokers: Bootstrap servers (e.g., ["kafka:9092"])
            group_id: Consumer group identifier (e.g., "storage_loader")
            topic: Topic to consume
        """
        self.config = {
            "bootstrap.servers": ",".join(brokers),
            "group.id": group_id,  # Group membership
            "client.id": f"{group_id}-consumer-1",  # Instance identifier
            "group.instance.id": f"{group_id}-consumer-1",  # Static membership (optional)
            "session.timeout.ms": 300000,  # 5 minutes
            "heartbeat.interval.ms": 10000,  # 10 seconds
        }
        self.consumer = Consumer(self.config)
        self.consumer.subscribe([topic])

    def get_group_metadata(self) -> dict[str, str]:
        """Get current group membership metadata."""
        return {
            "group_id": self.config["group.id"],
            "client_id": self.config.get("client.id", "unknown"),
            "generation_id": str(self.consumer.memberid()),
        }
```

### Group Membership

A consumer is a member of its group once it joins:

- **Membership Duration**: From subscription until close
- **Heartbeats**: Sent periodically to prove liveness
- **Session Timeout**: If no heartbeat, removed from group
- **Max Poll Interval**: Max time allowed for processing before removal

**Configuration**:
```python
config = {
    "session.timeout.ms": 300000,      # 5 min - heartbeat timeout
    "heartbeat.interval.ms": 10000,     # 10 sec - heartbeat frequency
    "max.poll.interval.ms": 300000,     # 5 min - max processing time
}
```

## Offset Commit Strategies

### Manual Offset Commits (Recommended)

Commit only after successful processing:

```python
async def process_message_with_manual_commit(
    self,
    message: OrderEventMessage,
) -> None:
    """Process message and commit only on success."""
    try:
        # 1. Deserialize and validate
        order = OrderEventTranslator.to_domain_order(message)

        # 2. Process (most critical step)
        await self.load_use_case.execute(order)
        self.logger.info("order_loaded", order_id=str(order.order_id))

        # 3. Commit ONLY after processing succeeds
        try:
            self.consumer.commit(asynchronous=False)
            self.logger.debug("offset_committed")
        except Exception as e:
            self.logger.error("commit_failed", error=str(e))
            # Don't raise - message will reprocess on restart

    except Exception as e:
        self.logger.error("processing_failed", error=str(e))
        # Don't commit - message will reprocess
        raise
```

**Guarantees**:
- Exactly-once-per-restart: Reprocessing only on crash
- No data loss: Failed messages never committed
- No duplication in storage: Same logic can run twice

### Automatic Offset Commits (Use with Caution)

Commits at regular intervals:

```python
config = {
    "enable.auto.commit": True,          # Enable auto-commit
    "auto.commit.interval.ms": 5000,     # Commit every 5 seconds
    "auto.offset.reset": "earliest",
}

consumer = Consumer(config)
consumer.subscribe(["orders"])

# Messages are auto-committed in background
# Risk: Failure between consume() and commit
while True:
    message = consumer.poll(timeout=1.0)
    if message is None:
        continue

    # If processing fails here, offset still commits
    process_message(message)  # Could fail
    # Auto-commit happens in background - message might be lost
```

**Risks**:
- Data loss if processing fails after auto-commit
- Timing window between consume and commit
- No control over commit timing

**Only use when**:
- Reprocessing is acceptable
- Processing is very fast
- Exactly-once semantics not required

### Asynchronous Manual Commits

For high-throughput scenarios:

```python
def commit_async(self) -> None:
    """Commit asynchronously (for high throughput)."""
    try:
        # Don't wait for broker acknowledgment
        self.consumer.commit(asynchronous=True)
    except Exception as e:
        self.logger.error("async_commit_failed", error=str(e))

# Usage: Batch processing multiple messages
messages = []
for _ in range(100):
    msg = self.consumer.poll(timeout=1.0)
    if msg:
        messages.append(msg)

# Process batch
for msg in messages:
    process_message(msg)

# Commit after batch completes
self.commit_async()
```

**Trade-off**:
- Higher throughput
- Lower latency commitment
- Less safety on immediate failure
- Faster offset progression

## Offset Tracking and Lag

### Consumer Lag Monitoring

Track how far consumer lags behind producer:

```python
from datetime import datetime
from typing import NamedTuple

class ConsumerLagMetrics(NamedTuple):
    """Consumer lag metrics per partition."""
    partition: int
    committed_offset: int | None
    high_watermark: int
    lag: int
    lag_percent: float

class LagMonitor:
    """Monitor and report consumer lag."""

    def get_lag_metrics(self) -> list[ConsumerLagMetrics]:
        """Get lag metrics for all partitions."""
        metrics = []

        # Get assigned partitions
        partitions = self.consumer.assignment()

        for partition in partitions:
            # Get committed offset
            committed = self.consumer.committed([partition])
            committed_offset = committed[0].offset() if committed else None

            # Query high watermark
            low, high = self.consumer.query_watermark_offsets(
                partition.topic(),
                partition.partition(),
                timeout=5
            )

            lag = high - (committed_offset or 0)
            lag_percent = (lag / high * 100) if high > 0 else 0

            metrics.append(ConsumerLagMetrics(
                partition=partition.partition(),
                committed_offset=committed_offset,
                high_watermark=high,
                lag=lag,
                lag_percent=lag_percent,
            ))

        return metrics

    def log_lag_metrics(self) -> None:
        """Log lag metrics to structured logger."""
        metrics = self.get_lag_metrics()
        for m in metrics:
            logger = get_logger(__name__)
            logger.info(
                "consumer_lag",
                partition=m.partition,
                committed_offset=m.committed_offset,
                high_watermark=m.high_watermark,
                lag=m.lag,
                lag_percent=f"{m.lag_percent:.1f}%",
            )
```

### Offset Position Tracking

Track current consumer position:

```python
def get_consumer_positions(self) -> dict[int, int]:
    """Get current position for each partition."""
    positions = {}

    for partition in self.consumer.assignment():
        tp = partition.topic(), partition.partition()
        pos = self.consumer.position([partition])
        if pos:
            positions[partition.partition()] = pos[0].offset()

    return positions

def get_committed_offsets(self) -> dict[int, int | None]:
    """Get last committed offset per partition."""
    offsets = {}

    for partition in self.consumer.assignment():
        committed = self.consumer.committed([partition])
        offset = committed[0].offset() if committed else None
        offsets[partition.partition()] = offset

    return offsets
```

## Rebalancing Behavior

### Rebalancing Scenarios

Rebalancing occurs when:

1. **Consumer joins** - New consumer added to group
2. **Consumer leaves** - Consumer shuts down or crashes
3. **Partition count changes** - Topic scaled up/down
4. **Group initialization** - First consumer subscribes

### Safe Rebalancing Pattern

Implement rebalancing callbacks:

```python
def on_assign(self, partitions: list[Any]) -> None:
    """Called when partitions are assigned (after rebalancing)."""
    self.logger.info(
        "partitions_assigned",
        count=len(partitions),
        partitions=[f"{p.topic()}:{p.partition()}" for p in partitions],
    )

def on_revoke(self, partitions: list[Any]) -> None:
    """Called when partitions are revoked (before rebalancing)."""
    self.logger.info(
        "partitions_revoked",
        count=len(partitions),
        partitions=[f"{p.topic()}:{p.partition()}" for p in partitions],
    )

    # Commit current offset before losing partition
    try:
        self.consumer.commit(asynchronous=False)
        self.logger.info("offset_committed_before_revoke")
    except Exception as e:
        self.logger.error("commit_failed_on_revoke", error=str(e))

# Register callbacks
consumer.subscribe(["orders"], on_assign=self.on_assign, on_revoke=self.on_revoke)
```

### Rebalancing Pause/Resume

Pause processing during rebalancing:

```python
def pause_consumption(self) -> None:
    """Pause message consumption (during rebalancing)."""
    partitions = self.consumer.assignment()
    self.consumer.pause(partitions)
    self.logger.info("consumption_paused")

def resume_consumption(self) -> None:
    """Resume message consumption."""
    partitions = self.consumer.assignment()
    self.consumer.resume(partitions)
    self.logger.info("consumption_resumed")
```

## Offset Reset Scenarios

### Offset Reset Strategies

When a consumer has no committed offset:

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `earliest` | Start from beginning of topic | New consumer, catch-up |
| `latest` | Start from end of topic | Real-time tailing, skip backlog |
| `none` | Throw exception | Fail-fast validation |

### Configuration

```python
config = {
    "auto.offset.reset": "earliest",  # Default for new groups
}

# Can be overridden per scenario
consumer.seek(TopicPartition("orders", 0, 0))  # Manual seek to offset 0
```

### Handling No Offset Found

When no offset exists:

```python
def consume_with_fallback(self, timeout: float = 1.0) -> Message | None:
    """Consume with fallback strategy."""
    try:
        msg = self.consumer.poll(timeout=timeout)

        if msg is None:
            return None

        if msg.error():
            error_code = msg.error().code()

            if error_code == KafkaError.NO_OFFSET:
                # No committed offset - use reset strategy
                self.logger.warning("no_committed_offset_using_reset_strategy")
                # Consumer will use auto.offset.reset setting
                return None

            elif error_code == KafkaError._PARTITION_EOF:
                # End of partition - normal
                return None

            else:
                raise KafkaException(msg.error())

        return msg

    except Exception as e:
        self.logger.error("consume_error", error=str(e))
        raise
```

## Consumer Group Lifecycle

### Initialization

When consumer starts:

```python
1. **Subscribe to Topic**
   - Sends join request to broker
   - Consumer becomes group member

2. **Partition Assignment**
   - Coordinator assigns partitions
   - Partitions distributed among group members
   - on_assign callback triggered

3. **Offset Lookup**
   - Consumer queries committed offset
   - If no offset: uses auto.offset.reset strategy
   - Seeks to starting position

4. **Message Consumption**
   - Starts consuming from assigned position
   - Sends heartbeats to maintain membership
```

### Shutdown

Safe consumer shutdown:

```python
async def shutdown(self) -> None:
    """Gracefully shutdown consumer."""
    self.logger.info("shutting_down_consumer")

    try:
        # Commit any pending offsets
        self.consumer.commit(asynchronous=False)
        self.logger.info("final_offset_committed")
    except Exception as e:
        self.logger.error("final_commit_failed", error=str(e))

    # Close and revoke partitions
    self.consumer.close()
    self.logger.info("consumer_closed")
```

## Monitoring and Troubleshooting

### Key Metrics to Monitor

```python
class ConsumerMetrics:
    """Track consumer health metrics."""

    def __init__(self) -> None:
        self.messages_consumed = 0
        self.messages_processed = 0
        self.messages_failed = 0
        self.offsets_committed = 0
        self.offsets_failed = 0

    def record_consume(self) -> None:
        """Record message consumed."""
        self.messages_consumed += 1

    def record_success(self) -> None:
        """Record successful processing."""
        self.messages_processed += 1
        self.offsets_committed += 1

    def record_failure(self) -> None:
        """Record processing failure."""
        self.messages_failed += 1

    def get_summary(self) -> dict[str, int]:
        """Get metrics summary."""
        return {
            "consumed": self.messages_consumed,
            "processed": self.messages_processed,
            "failed": self.messages_failed,
            "success_rate": (
                self.messages_processed / self.messages_consumed * 100
                if self.messages_consumed > 0 else 0
            ),
        }
```

### Common Troubleshooting

**Consumer stuck/not consuming**:
1. Check group coordination: `consumer.memberid()`
2. Verify heartbeats: Check logs for rebalancing
3. Check lag: Consumer may be at end of topic
4. Verify permissions: Topic access rights

**Slow consumption**:
1. Monitor lag: High lag = falling behind
2. Check processing time: Increase `max.poll.interval.ms`
3. Add consumers: Scale to more partitions
4. Optimize deserializer: Use msgspec instead of Pydantic

**Rebalancing storms**:
1. Check heartbeat settings: May be too aggressive
2. Verify processing time: Not exceeding `max.poll.interval.ms`
3. Monitor broker logs: Check for group coordination issues

### Health Check

```python
def health_check(self) -> bool:
    """Check if consumer is healthy."""
    try:
        # Check group membership
        if not self.consumer.memberid():
            self.logger.warning("health_check_no_member_id")
            return False

        # Check assignments
        assignments = self.consumer.assignment()
        if not assignments:
            self.logger.warning("health_check_no_assignments")
            return False

        # Check lag
        metrics = self.get_lag_metrics()
        if any(m.lag > 10000 for m in metrics):
            self.logger.warning("health_check_high_lag", metrics=metrics)

        return True

    except Exception as e:
        self.logger.error("health_check_failed", error=str(e))
        return False
```
