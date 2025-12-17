---
name: anyio-memory-streams
description: |
  Implements async producer/consumer channels and pub/sub message routing using anyio.create_memory_object_stream with backpressure control. Use when building async message queues, event routing systems, or coroutine communication channels. Triggers on "anyio streams", "memory object stream", "backpressure handling", "async message queue", "producer consumer async", "pub/sub anyio", or when implementing async communication between tasks. Works with anyio library for structured concurrency patterns.
---

# anyio Memory Object Streams

## Quick Start

```python
from anyio import create_memory_object_stream
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

# Create buffered channel with backpressure control
send_stream, receive_stream = create_memory_object_stream[dict[str, Any]](
    max_buffer_size=100
)

# Producer task
async def producer():
    await send_stream.send({"type": "event", "data": "value"})
    await send_stream.aclose()  # Signal completion

# Consumer task
async def consumer():
    async for message in receive_stream:
        print(f"Received: {message}")
    # Loop exits when sender closes
```

## Table of Contents

1. When to Use This Skill
2. What This Skill Does
3. Core Patterns
   3.1. Basic Producer/Consumer
   3.2. Pub/Sub Message Router
   3.3. Backpressure Handling
   3.4. Stream Cleanup
4. API Reference
   4.1. Stream Creation
   4.2. Sending Messages
   4.3. Receiving Messages
   4.4. Stream Statistics
5. Exception Handling
6. Best Practices
7. Integration Examples
8. Expected Outcomes
9. Requirements
10. Red Flags to Avoid

## 1. When to Use This Skill

**Explicit Triggers:**
- "How do I handle backpressure in async code?"
- "I need a message queue between async tasks"
- "Implement pub/sub with anyio"
- "Create producer/consumer pattern"
- "Route messages to multiple subscribers"

**Implicit Triggers:**
- Building event routing systems
- Implementing async communication between coroutines
- Managing message flow with buffer limits
- Creating fan-out message distribution
- Handling async data streams with bounded memory

**Debugging/Analysis Triggers:**
- "Why is my async task blocking?"
- "How do I prevent unbounded memory growth in async queues?"
- "Stream closed error in anyio"
- "Tasks waiting on send/receive"

## 2. What This Skill Does

This skill provides:
- **Producer/Consumer Channels**: Type-safe, buffered message passing between async tasks
- **Backpressure Control**: Automatic blocking when buffers are full to prevent memory overflow
- **Pub/Sub Routing**: Fan-out message distribution to multiple subscribers
- **Stream Statistics**: Real-time monitoring of buffer usage and waiting tasks
- **Graceful Cleanup**: Proper stream closure and resource management

## 3. Core Patterns

### 3.1. Basic Producer/Consumer

**Single Producer, Single Consumer:**

```python
from anyio import create_memory_object_stream, create_task_group
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

async def producer(send_stream: MemoryObjectSendStream[str]) -> None:
    """Produce messages and close stream when done."""
    try:
        for i in range(10):
            await send_stream.send(f"message-{i}")
            # Blocks if buffer is full (backpressure!)
    finally:
        await send_stream.aclose()  # Signal completion

async def consumer(receive_stream: MemoryObjectReceiveStream[str]) -> None:
    """Consume messages until stream closes."""
    async for message in receive_stream:
        print(f"Processing: {message}")
    # Loop exits when all senders close

async def main() -> None:
    send_stream, receive_stream = create_memory_object_stream[str](
        max_buffer_size=5  # Buffer holds 5 messages
    )

    async with create_task_group() as tg:
        tg.start_soon(producer, send_stream)
        tg.start_soon(consumer, receive_stream)
```

**Multiple Producers, Single Consumer:**

```python
async def run_multi_producer() -> None:
    send_stream, receive_stream = create_memory_object_stream[dict[str, Any]](
        max_buffer_size=100
    )

    async def producer(name: str, stream: MemoryObjectSendStream[dict[str, Any]]) -> None:
        try:
            for i in range(5):
                await stream.send({"producer": name, "seq": i})
        finally:
            await stream.aclose()  # Each producer closes independently

    async def consumer(stream: MemoryObjectReceiveStream[dict[str, Any]]) -> None:
        async for msg in stream:
            print(f"Got: {msg}")

    async with create_task_group() as tg:
        # Start multiple producers
        for i in range(3):
            tg.start_soon(producer, f"prod-{i}", send_stream.clone())

        # Close original send stream (each clone is independent)
        await send_stream.aclose()

        # Start consumer
        tg.start_soon(consumer, receive_stream)
```

### 3.2. Pub/Sub Message Router

**Full Implementation:**

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Generic, TypeVar
import anyio
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

T = TypeVar("T")

class MessageRouter(Generic[T]):
    """Thread-safe pub/sub message router with backpressure control."""

    def __init__(self, buffer_size: int = 100) -> None:
        """
        Initialize message router.

        Args:
            buffer_size: Max messages buffered per subscriber before backpressure.
        """
        self._buffer_size = buffer_size
        self._subscribers: list[MemoryObjectSendStream[T]] = []
        self._lock = anyio.Lock()

    async def publish(self, message: T) -> int:
        """
        Publish message to all active subscribers.

        Args:
            message: Message to distribute.

        Returns:
            Number of subscribers that received the message.

        Note:
            Uses send_nowait() to avoid blocking on slow consumers.
            Drops messages for subscribers with full buffers.
        """
        delivered = 0
        async with self._lock:
            for send_stream in self._subscribers[:]:  # Copy to allow removal
                try:
                    send_stream.send_nowait(message)
                    delivered += 1
                except anyio.WouldBlock:
                    # Subscriber buffer full - drop message or log warning
                    print(f"Warning: Subscriber buffer full, dropping message")
                except anyio.ClosedResourceError:
                    # Subscriber disconnected - remove from list
                    self._subscribers.remove(send_stream)
        return delivered

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[MemoryObjectReceiveStream[T]]:
        """
        Subscribe to messages.

        Yields:
            Receive stream for consuming published messages.

        Example:
            async with router.subscribe() as stream:
                async for message in stream:
                    process(message)
        """
        send_stream, receive_stream = create_memory_object_stream[T](
            max_buffer_size=self._buffer_size
        )

        async with self._lock:
            self._subscribers.append(send_stream)

        try:
            yield receive_stream
        finally:
            async with self._lock:
                if send_stream in self._subscribers:
                    self._subscribers.remove(send_stream)
            await send_stream.aclose()
            await receive_stream.aclose()

# Usage example
async def use_router() -> None:
    router: MessageRouter[dict[str, Any]] = MessageRouter(buffer_size=50)

    # Publisher task
    async def publisher() -> None:
        for i in range(100):
            count = await router.publish({"event": "update", "seq": i})
            print(f"Delivered to {count} subscribers")
            await anyio.sleep(0.1)

    # Subscriber task
    async def subscriber(name: str) -> None:
        async with router.subscribe() as stream:
            async for message in stream:
                print(f"{name} received: {message}")
                await anyio.sleep(0.2)  # Slow consumer

    async with create_task_group() as tg:
        tg.start_soon(publisher)
        tg.start_soon(subscriber, "sub-1")
        tg.start_soon(subscriber, "sub-2")
```

### 3.3. Backpressure Handling

**Blocking vs Non-Blocking Send:**

```python
async def demonstrate_backpressure() -> None:
    send_stream, receive_stream = create_memory_object_stream[int](
        max_buffer_size=3  # Very small buffer
    )

    # Blocking send - waits for space in buffer
    async def blocking_producer() -> None:
        for i in range(10):
            print(f"Sending {i}...")
            await send_stream.send(i)  # Blocks when buffer full!
            print(f"Sent {i}")

    # Non-blocking send - raises WouldBlock if buffer full
    async def nonblocking_producer() -> None:
        for i in range(10):
            try:
                send_stream.send_nowait(i)
                print(f"Sent {i}")
            except anyio.WouldBlock:
                print(f"Buffer full, dropping {i}")
            except anyio.ClosedResourceError:
                print("Stream closed, stopping")
                break

    # Slow consumer creates backpressure
    async def slow_consumer() -> None:
        async for value in receive_stream:
            print(f"Processing {value}...")
            await anyio.sleep(1)  # Slow!
```

**Monitoring Buffer State:**

```python
async def monitor_stream_health(
    stream: MemoryObjectSendStream[Any] | MemoryObjectReceiveStream[Any]
) -> None:
    """Monitor stream statistics for debugging."""
    stats = stream.statistics()

    print(f"Current buffer: {stats.current_buffer_used}/{stats.max_buffer_size}")
    print(f"Open streams: send={stats.open_send_streams}, recv={stats.open_receive_streams}")
    print(f"Waiting tasks: send={stats.tasks_waiting_send}, recv={stats.tasks_waiting_receive}")

    # Check for backpressure
    if stats.current_buffer_used == stats.max_buffer_size:
        print("⚠️  Buffer full - backpressure active!")

    # Check for blocked tasks
    if stats.tasks_waiting_send > 0:
        print(f"⚠️  {stats.tasks_waiting_send} tasks blocked on send")
    if stats.tasks_waiting_receive > 0:
        print(f"⚠️  {stats.tasks_waiting_receive} tasks blocked on receive")
```

### 3.4. Stream Cleanup

**Proper Cleanup Pattern:**

```python
async def proper_cleanup_example() -> None:
    send_stream, receive_stream = create_memory_object_stream[str](100)

    try:
        # Use streams
        await send_stream.send("message")
        msg = await receive_stream.receive()
    finally:
        # Always close both streams
        await send_stream.aclose()
        await receive_stream.aclose()

# Better: Use context managers when possible
@asynccontextmanager
async def create_channel[T](
    buffer_size: int = 100
) -> AsyncIterator[tuple[MemoryObjectSendStream[T], MemoryObjectReceiveStream[T]]]:
    """Create channel with automatic cleanup."""
    send_stream, receive_stream = create_memory_object_stream[T](buffer_size)
    try:
        yield send_stream, receive_stream
    finally:
        await send_stream.aclose()
        await receive_stream.aclose()

async def use_channel() -> None:
    async with create_channel[str](100) as (send, recv):
        await send.send("message")
        msg = await recv.receive()
    # Automatic cleanup!
```

## 4. API Reference

### 4.1. Stream Creation

```python
# Generic type signature
create_memory_object_stream[T](
    max_buffer_size: int = 0  # 0 = unbounded (dangerous!)
) -> tuple[MemoryObjectSendStream[T], MemoryObjectReceiveStream[T]]

# Examples
send, recv = create_memory_object_stream[str](100)
send, recv = create_memory_object_stream[dict[str, Any]](50)
send, recv = create_memory_object_stream[int](0)  # Unbounded - use with caution!
```

### 4.2. Sending Messages

```python
# Blocking send (waits for space in buffer)
await send_stream.send(message)

# Non-blocking send (raises WouldBlock if buffer full)
send_stream.send_nowait(message)

# Clone stream (for multiple producers)
new_send_stream = send_stream.clone()

# Close stream (signals no more messages)
await send_stream.aclose()
```

### 4.3. Receiving Messages

```python
# Blocking receive (waits for message)
message = await receive_stream.receive()

# Non-blocking receive (raises WouldBlock if empty)
message = receive_stream.receive_nowait()

# Iterate until stream closes
async for message in receive_stream:
    process(message)

# Clone stream (for multiple consumers - rare)
new_receive_stream = receive_stream.clone()

# Close stream
await receive_stream.aclose()
```

### 4.4. Stream Statistics

```python
from anyio.streams.memory import MemoryObjectStreamStatistics

stats: MemoryObjectStreamStatistics = stream.statistics()

# Available fields:
stats.current_buffer_used      # int: Messages currently in buffer
stats.max_buffer_size          # int: Maximum buffer capacity
stats.open_send_streams        # int: Number of active senders
stats.open_receive_streams     # int: Number of active receivers
stats.tasks_waiting_send       # int: Tasks blocked on send()
stats.tasks_waiting_receive    # int: Tasks blocked on receive()
```

## 5. Exception Handling

```python
import anyio

try:
    send_stream.send_nowait(message)
except anyio.WouldBlock:
    # Buffer is full - backpressure active
    # Options: drop message, log warning, use blocking send(), or queue for retry
    pass

except anyio.ClosedResourceError:
    # Stream was closed (aclose() was called)
    # Producer should stop sending
    break

except anyio.EndOfStream:
    # All senders closed - no more data coming
    # Consumer should finish processing and exit
    break

except anyio.BrokenResourceError:
    # All receivers closed - no point sending
    # Producer should stop
    break
```

**Exception Decision Tree:**

| Exception | When It Occurs | Producer Action | Consumer Action |
|-----------|---------------|-----------------|-----------------|
| `WouldBlock` | Buffer full (send_nowait) | Drop/retry/block | N/A |
| `ClosedResourceError` | Stream closed | Stop sending | Stop receiving |
| `EndOfStream` | All senders closed | N/A | Exit gracefully |
| `BrokenResourceError` | All receivers closed | Stop sending | N/A |

## 6. Best Practices

### Resource Management
```python
# ✅ GOOD: Always close streams
async def good_cleanup() -> None:
    send, recv = create_memory_object_stream[str](100)
    try:
        await send.send("msg")
    finally:
        await send.aclose()
        await recv.aclose()

# ❌ BAD: Leaking streams
async def bad_cleanup() -> None:
    send, recv = create_memory_object_stream[str](100)
    await send.send("msg")
    # Forgot to close - resource leak!
```

### Buffer Sizing
```python
# ✅ GOOD: Bounded buffers prevent memory overflow
send, recv = create_memory_object_stream[dict](100)

# ❌ BAD: Unbounded buffers can cause OOM
send, recv = create_memory_object_stream[dict](0)  # Dangerous!
```

### Backpressure Strategy
```python
# ✅ GOOD: Handle backpressure explicitly
try:
    send_stream.send_nowait(msg)
except anyio.WouldBlock:
    # Explicit strategy: drop, log, retry, or block
    logger.warning("Buffer full, dropping message")

# ❌ BAD: Ignoring backpressure
send_stream.send_nowait(msg)  # Raises exception, crashes task
```

### Type Safety
```python
# ✅ GOOD: Explicit generic types
send, recv = create_memory_object_stream[dict[str, Any]](100)

# ❌ BAD: Untyped streams
send, recv = create_memory_object_stream(100)  # Type checker can't help
```

## 7. Integration Examples

### With Claude Agent SDK (Query Streaming)

```python
from anyio import create_memory_object_stream
from anthropic.types import Message

async def stream_agent_responses() -> None:
    """Stream agent responses through memory object stream."""
    send_stream, receive_stream = create_memory_object_stream[Message](
        max_buffer_size=10
    )

    async def producer() -> None:
        async with ClaudeAgentClient(config) as client:
            try:
                async for msg in client.query("Analyze code"):
                    await send_stream.send(msg)
            finally:
                await send_stream.aclose()

    async def consumer() -> None:
        async for msg in receive_stream:
            print(f"Agent: {msg.content}")

    async with create_task_group() as tg:
        tg.start_soon(producer)
        tg.start_soon(consumer)
```

### With temet-run IPC

```python
from temet_run.ipc.protocol import IPCMessage

class IPCMessageRouter:
    """Route IPC messages to multiple handlers."""

    def __init__(self) -> None:
        self.router: MessageRouter[IPCMessage] = MessageRouter(buffer_size=50)

    async def handle_message(self, message: IPCMessage) -> None:
        """Publish message to all subscribers."""
        count = await self.router.publish(message)
        if count == 0:
            logger.warning("No subscribers for message")

    @asynccontextmanager
    async def subscribe_to_messages(
        self
    ) -> AsyncIterator[MemoryObjectReceiveStream[IPCMessage]]:
        """Subscribe to IPC messages."""
        async with self.router.subscribe() as stream:
            yield stream
```

## 8. Expected Outcomes

### Successful Implementation

```
✅ Producer/Consumer Working

Buffer: 45/100 messages
Throughput: 1000 msg/sec
Backpressure events: 0
Dropped messages: 0

Subscribers: 3 active
Messages delivered: 10,000
Average latency: 2ms

All streams closed gracefully
No resource leaks detected
```

### Backpressure Detection

```
⚠️  Backpressure Active

Current buffer: 100/100 (FULL)
Tasks waiting on send: 5
Subscriber processing rate: 50 msg/sec
Producer rate: 200 msg/sec

Recommendation: Increase buffer_size or slow down producer
```

## 9. Requirements

**Dependencies:**
```bash
# anyio is the only requirement
uv add anyio
```

**Python Version:**
- Python 3.11+ (for generic type syntax)
- Python 3.9+ (with `typing.TypeVar` alternative)

**Knowledge:**
- Async/await fundamentals
- Structured concurrency concepts (task groups)
- Backpressure control principles
- Context manager patterns

## 10. Red Flags to Avoid

❌ **Unbounded Buffers**
```python
# Dangerous - can cause OOM
send, recv = create_memory_object_stream[dict](0)
```

❌ **Ignoring WouldBlock**
```python
# Will crash when buffer full
send_stream.send_nowait(msg)  # No exception handling
```

❌ **Not Closing Streams**
```python
# Resource leak
send, recv = create_memory_object_stream[str](100)
await send.send("msg")
# Forgot to close!
```

❌ **Using send() in publish()**
```python
# Blocks entire router if one subscriber is slow
async def bad_publish(self, msg: T) -> None:
    for stream in self._subscribers:
        await stream.send(msg)  # Blocking!
```

❌ **No Type Annotations**
```python
# Type checker can't help
send, recv = create_memory_object_stream(100)
```

❌ **Swallowing ClosedResourceError**
```python
# Producer keeps trying to send to closed stream
try:
    await send_stream.send(msg)
except anyio.ClosedResourceError:
    pass  # Should break/return instead
```

✅ **Correct Patterns**
```python
# Bounded buffer
send, recv = create_memory_object_stream[dict[str, Any]](100)

# Handle backpressure
try:
    send_stream.send_nowait(msg)
except anyio.WouldBlock:
    logger.warning("Buffer full")

# Always close
try:
    await send.send(msg)
finally:
    await send.aclose()
    await recv.aclose()

# Non-blocking publish
async def publish(self, msg: T) -> None:
    for stream in self._subscribers:
        try:
            stream.send_nowait(msg)  # Non-blocking!
        except anyio.WouldBlock:
            logger.warning("Subscriber slow")
```

## Notes

- **Backpressure is automatic**: Blocking send() waits for buffer space
- **EndOfStream signals completion**: Consumer loop exits when all senders close
- **Clone for multiple producers/consumers**: Each clone is independent
- **Statistics for monitoring**: Use `statistics()` to detect bottlenecks
- **Type safety matters**: Always use generic type parameters
- **Cleanup is critical**: Unclosed streams leak resources
- **send_nowait() for pub/sub**: Avoids blocking on slow subscribers
