# Google Cloud Pub/Sub - Comprehensive Examples

This file contains detailed, production-ready code examples for various Pub/Sub patterns and scenarios.

## Table of Contents

1. [Async Publishing Patterns](#async-publishing-patterns)
2. [Advanced Subscription Patterns](#advanced-subscription-patterns)
3. [Testing with Emulator](#testing-with-emulator)
4. [Error Handling Strategies](#error-handling-strategies)
5. [Integration Examples](#integration-examples)
6. [Performance Optimization](#performance-optimization)

---

## Async Publishing Patterns

### Using asyncio for Concurrent Publishing

```python
import asyncio
from google.cloud import pubsub_v1
import json
from typing import List, Dict, Any

class AsyncPublisher:
    """Async message publisher for high-throughput scenarios."""

    def __init__(self, project_id: str, topic_id: str, batch_size: int = 100):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)
        self.batch_size = batch_size
        self.batch_queue: asyncio.Queue = asyncio.Queue(maxsize=batch_size)

    async def publish_async(
        self,
        data: bytes,
        attributes: Dict[str, str] = None
    ) -> str:
        """Publish message asynchronously."""
        loop = asyncio.get_event_loop()

        def publish_sync():
            future = self.publisher.publish(
                self.topic_path,
                data,
                **(attributes or {})
            )
            return future.result(timeout=5)

        message_id = await loop.run_in_executor(None, publish_sync)
        return message_id

    async def publish_batch_async(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Publish multiple messages concurrently."""
        tasks = [
            self.publish_async(
                msg.get("data", b""),
                msg.get("attributes", {})
            )
            for msg in messages
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Usage
async def main():
    publisher = AsyncPublisher("my-project", "my-topic")

    messages = [
        {
            "data": json.dumps({"event": f"event-{i}"}).encode(),
            "attributes": {"index": str(i)}
        }
        for i in range(100)
    ]

    results = await publisher.publish_batch_async(messages)
    success_count = sum(1 for r in results if isinstance(r, str))
    print(f"Published {success_count}/{len(messages)} messages")

# Run
asyncio.run(main())
```

### Publishing with Futures and Callback Handlers

```python
from google.cloud import pubsub_v1
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

class PublisherWithCallbacks:
    """Publisher with future-based callback handling."""

    def __init__(self, project_id: str, topic_id: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)

    def publish_with_callback(
        self,
        data: bytes,
        on_success: Callable[[str], None] = None,
        on_error: Callable[[Exception], None] = None,
        attributes: dict = None
    ):
        """Publish with success and error callbacks."""
        future = self.publisher.publish(
            self.topic_path,
            data,
            **(attributes or {})
        )

        def success_callback(message_id):
            if on_success:
                on_success(message_id)

        def error_callback(exc):
            if on_error:
                on_error(exc)

        future.add_done_callback(
            lambda f: success_callback(f.result()) if f.exception() is None
            else error_callback(f.exception())
        )

        return future

# Usage
def on_publish_success(message_id: str):
    print(f"Message published successfully: {message_id}")

def on_publish_error(exc: Exception):
    print(f"Failed to publish: {exc}")

publisher = PublisherWithCallbacks("my-project", "my-topic")
publisher.publish_with_callback(
    b"test message",
    on_success=on_publish_success,
    on_error=on_publish_error,
    attributes={"type": "test"}
)
```

---

## Advanced Subscription Patterns

### Ordered Message Processing

```python
from google.cloud import pubsub_v1
import json
from collections import defaultdict
from typing import Dict, Any

class OrderedMessageProcessor:
    """Process messages in order per ordering key."""

    def __init__(self, project_id: str, subscription_id: str):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_id
        )
        self.pending_messages: Dict[str, list] = defaultdict()

    def process_message(self, message: pubsub_v1.subscriber.message.Message):
        """Override to process ordered messages."""
        raise NotImplementedError

    def callback(self, message: pubsub_v1.subscriber.message.Message):
        """Handle message in order per key."""
        ordering_key = message.attributes.get("ordering_key", "default")

        try:
            # Process message - framework guarantees ordering per key
            self.process_message(message)
            message.ack()
        except Exception as e:
            print(f"Error processing ordered message: {e}")
            message.nack()

    def subscribe(self, timeout: int = 30):
        """Subscribe with ordering enabled."""
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.callback,
            flow_control=pubsub_v1.types.FlowControl(
                max_messages=100,
                max_bytes=100 * 1024 * 1024,
            ),
        )

        try:
            streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            print(f"Subscriber error: {e}")
            streaming_pull_future.cancel()
```

### Subscription with Dynamic Flow Control

```python
from google.cloud import pubsub_v1
import time
import psutil

class AdaptiveFlowControlSubscriber:
    """Adjust flow control based on system resources."""

    def __init__(self, project_id: str, subscription_id: str):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_id
        )
        self.memory_threshold = 80  # percent
        self.last_flow_adjustment = time.time()

    def get_flow_control(self) -> pubsub_v1.types.FlowControl:
        """Calculate flow control based on system resources."""
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)

        if memory_percent > self.memory_threshold or cpu_percent > 80:
            # Reduce message throughput
            max_messages = 10
            max_bytes = 10 * 1024 * 1024  # 10 MB
            print(f"Flow control reduced: Memory {memory_percent}%, CPU {cpu_percent}%")
        else:
            # Normal throughput
            max_messages = 100
            max_bytes = 100 * 1024 * 1024  # 100 MB

        return pubsub_v1.types.FlowControl(
            max_messages=max_messages,
            max_bytes=max_bytes,
        )

    def callback(self, message: pubsub_v1.subscriber.message.Message):
        """Process message."""
        try:
            print(f"Processing: {message.data.decode()}")
            message.ack()
        except Exception as e:
            print(f"Error: {e}")
            message.nack()

    def subscribe(self, timeout: int = 30):
        """Subscribe with adaptive flow control."""
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.callback,
            flow_control=self.get_flow_control(),
        )

        try:
            streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            print(f"Subscriber error: {e}")
            streaming_pull_future.cancel()
```

### Pull-Based Subscription

```python
from google.cloud import pubsub_v1
import time

def pull_messages(project_id: str, subscription_id: str, max_messages: int = 10):
    """Pull messages synchronously."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # Pull messages
    response = subscriber.pull(
        request={
            "subscription": subscription_path,
            "max_messages": max_messages,
        },
        timeout=5.0,
    )

    ack_ids = []
    for message in response.received_messages:
        print(f"Received: {message.message.data.decode()}")
        ack_ids.append(message.ack_id)

    # Acknowledge all at once
    if ack_ids:
        subscriber.acknowledge(
            request={
                "subscription": subscription_path,
                "ack_ids": ack_ids,
            }
        )
        print(f"Acknowledged {len(ack_ids)} messages")

# Usage
pull_messages("my-project", "my-subscription", max_messages=100)
```

---

## Testing with Emulator

### Pytest Integration Test

```python
import pytest
import os
from google.cloud import pubsub_v1
import json

@pytest.fixture(scope="module")
def pubsub_project_id():
    """Use test project ID."""
    return "test-project"

@pytest.fixture
def publisher(pubsub_project_id):
    """Create publisher client."""
    if os.getenv("PUBSUB_EMULATOR_HOST"):
        return pubsub_v1.PublisherClient()
    pytest.skip("Emulator not running")

@pytest.fixture
def subscriber(pubsub_project_id):
    """Create subscriber client."""
    if os.getenv("PUBSUB_EMULATOR_HOST"):
        return pubsub_v1.SubscriberClient()
    pytest.skip("Emulator not running")

@pytest.fixture
def topic_and_subscription(publisher, subscriber, pubsub_project_id):
    """Create test topic and subscription."""
    topic_id = "test-topic"
    subscription_id = "test-subscription"

    topic_path = publisher.topic_path(pubsub_project_id, topic_id)
    subscription_path = subscriber.subscription_path(pubsub_project_id, subscription_id)

    # Create topic
    try:
        publisher.create_topic(request={"name": topic_path})
    except:
        pass

    # Create subscription
    try:
        subscriber.create_subscription(request={
            "name": subscription_path,
            "topic": topic_path,
        })
    except:
        pass

    yield topic_path, subscription_path

    # Cleanup
    try:
        subscriber.delete_subscription(request={"subscription": subscription_path})
        publisher.delete_topic(request={"topic": topic_path})
    except:
        pass

def test_publish_and_receive(publisher, subscriber, topic_and_subscription):
    """Test basic publish and receive."""
    topic_path, subscription_path = topic_and_subscription

    # Publish message
    future = publisher.publish(topic_path, b"test message")
    message_id = future.result(timeout=5)
    assert message_id

    # Receive message
    import time
    time.sleep(1)  # Give it a moment to be delivered

    response = subscriber.pull(
        request={
            "subscription": subscription_path,
            "max_messages": 1,
        }
    )

    assert len(response.received_messages) == 1
    message = response.received_messages[0].message
    assert message.data == b"test message"

def test_publish_json_message(publisher, subscriber, topic_and_subscription):
    """Test JSON message publishing and receiving."""
    topic_path, subscription_path = topic_and_subscription

    # Publish JSON
    payload = {"event": "test", "value": 123}
    future = publisher.publish(
        topic_path,
        json.dumps(payload).encode(),
        content_type="application/json"
    )
    message_id = future.result(timeout=5)
    assert message_id

    # Receive and parse
    import time
    time.sleep(1)

    response = subscriber.pull(
        request={"subscription": subscription_path, "max_messages": 1}
    )

    assert len(response.received_messages) == 1
    message = response.received_messages[0].message
    received_payload = json.loads(message.data)
    assert received_payload == payload
```

### Manual Integration Test

```python
import os
import time
from google.cloud import pubsub_v1

def test_with_emulator():
    """Manual test using emulator."""
    # Start emulator first:
    # gcloud beta emulators pubsub start

    if not os.getenv("PUBSUB_EMULATOR_HOST"):
        print("Set PUBSUB_EMULATOR_HOST=localhost:8085")
        return

    project_id = "test-project"
    topic_id = "test-topic"
    subscription_id = "test-sub"

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    # Create resources
    topic_path = publisher.topic_path(project_id, topic_id)
    sub_path = subscriber.subscription_path(project_id, subscription_id)

    publisher.create_topic(request={"name": topic_path})
    subscriber.create_subscription(request={
        "name": sub_path,
        "topic": topic_path,
    })

    # Publish
    future = publisher.publish(topic_path, b"Hello Emulator!")
    print(f"Published: {future.result()}")

    # Receive
    time.sleep(0.5)
    response = subscriber.pull(
        request={"subscription": sub_path, "max_messages": 10}
    )

    for msg in response.received_messages:
        print(f"Received: {msg.message.data.decode()}")
        subscriber.acknowledge(request={
            "subscription": sub_path,
            "ack_ids": [msg.ack_id]
        })

    print("Test passed!")

if __name__ == "__main__":
    test_with_emulator()
```

---

## Error Handling Strategies

### Exponential Backoff with Retries

```python
from google.cloud import pubsub_v1
import time
import random

class ResilientPublisher:
    """Publisher with exponential backoff retry strategy."""

    def __init__(self, project_id: str, topic_id: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)
        self.max_retries = 5
        self.base_wait = 1  # seconds

    def publish_with_retry(self, data: bytes, attributes: dict = None) -> str:
        """Publish with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                future = self.publisher.publish(
                    self.topic_path,
                    data,
                    **(attributes or {})
                )
                message_id = future.result(timeout=5)
                return message_id
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise

                wait_time = self.base_wait * (2 ** attempt)
                jitter = random.uniform(0, wait_time * 0.1)
                total_wait = wait_time + jitter

                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {total_wait:.2f} seconds...")
                time.sleep(total_wait)

# Usage
publisher = ResilientPublisher("my-project", "my-topic")
try:
    message_id = publisher.publish_with_retry(b"Resilient message")
    print(f"Published: {message_id}")
except Exception as e:
    print(f"Final failure: {e}")
```

### Circuit Breaker Pattern

```python
from google.cloud import pubsub_v1
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Operating normally
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreakerPublisher:
    """Publisher with circuit breaker for failure handling."""

    def __init__(self, project_id: str, topic_id: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = 5
        self.recovery_timeout = 60  # seconds
        self.last_failure_time = None

    def is_available(self) -> bool:
        """Check if circuit allows requests."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if enough time has passed for recovery attempt
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
                return True
            return False

        # HALF_OPEN: allow one attempt
        return True

    def publish(self, data: bytes, attributes: dict = None) -> str:
        """Publish with circuit breaker protection."""
        if not self.is_available():
            raise Exception(f"Circuit breaker is OPEN, service unavailable")

        try:
            future = self.publisher.publish(
                self.topic_path,
                data,
                **(attributes or {})
            )
            message_id = future.result(timeout=5)

            # Success - reset failure count
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                print("Circuit breaker CLOSED - service recovered")

            return message_id
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"Circuit breaker OPEN after {self.failure_count} failures")

            raise

# Usage
publisher = CircuitBreakerPublisher("my-project", "my-topic")
try:
    message_id = publisher.publish(b"test")
except Exception as e:
    print(f"Publish failed: {e}")
```

---

## Integration Examples

### Message Processing with Logging

```python
from google.cloud import pubsub_v1
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoggingSubscriber:
    """Subscriber with detailed logging."""

    def __init__(self, project_id: str, subscription_id: str):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_id
        )

    def callback(self, message: pubsub_v1.subscriber.message.Message):
        """Process message with logging."""
        message_log = {
            "message_id": message.message_id,
            "publish_time": str(message.publish_time),
            "attributes": dict(message.attributes),
            "size_bytes": len(message.data),
            "processing_started": datetime.utcnow().isoformat(),
        }

        try:
            logger.info(f"Received message: {message_log}")

            # Try to parse as JSON
            try:
                payload = json.loads(message.data.decode())
                message_log["payload"] = payload
            except:
                message_log["raw_data"] = message.data.decode()

            # Process
            logger.info(f"Processing: {message_log}")
            message.ack()

            message_log["status"] = "acked"
            logger.info(f"Message processed: {message_log}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            message.nack()
            message_log["status"] = "nacked"
            message_log["error"] = str(e)

    def subscribe(self, timeout: int = 30):
        """Subscribe with logging."""
        logger.info(f"Subscribing to: {self.subscription_path}")
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.callback,
            flow_control=pubsub_v1.types.FlowControl(
                max_messages=100,
                max_bytes=100 * 1024 * 1024,
            ),
        )

        try:
            streaming_pull_future.result(timeout=timeout)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            streaming_pull_future.cancel()
        except Exception as e:
            logger.error(f"Subscriber error: {e}", exc_info=True)
            streaming_pull_future.cancel()
```

### Request-Reply Pattern

```python
from google.cloud import pubsub_v1
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import time

class RequestReplyPublisher:
    """Implement request-reply pattern using Pub/Sub."""

    def __init__(self, project_id: str, request_topic: str, reply_topic: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.request_topic_path = self.publisher.topic_path(project_id, request_topic)
        self.reply_topic_path = self.publisher.topic_path(project_id, reply_topic)
        self.pending_requests = {}

    def send_request(self, request_data: dict, timeout: int = 10) -> dict:
        """Send request and wait for reply."""
        request_id = str(uuid.uuid4())
        self.pending_requests[request_id] = None

        # Publish request
        self.publisher.publish(
            self.request_topic_path,
            json.dumps(request_data).encode(),
            reply_to=f"reply-{request_id}",
        )

        # Wait for reply
        start = time.time()
        while time.time() - start < timeout:
            if self.pending_requests.get(request_id) is not None:
                reply = self.pending_requests[request_id]
                del self.pending_requests[request_id]
                return reply
            time.sleep(0.1)

        raise TimeoutError(f"No reply received for request {request_id}")

    def register_reply_handler(self, handler_fn):
        """Register handler for replies."""
        def callback(message: pubsub_v1.subscriber.message.Message):
            reply_data = json.loads(message.data.decode())
            request_id = message.attributes.get("request_id")

            if request_id in self.pending_requests:
                self.pending_requests[request_id] = reply_data

            message.ack()

        subscriber = pubsub_v1.SubscriberClient()
        # Create reply subscription and register callback
```

---

## Performance Optimization

### Batch Publishing Configuration

```python
from google.cloud import pubsub_v1
import json

def publish_with_batching(project_id: str, topic_id: str, messages: list):
    """Publish with optimized batch settings."""
    settings = pubsub_v1.types.BatchSettings(
        max_bytes=10 * 1024 * 1024,  # 10 MB
        max_latency=0.1,  # 100 ms
        max_messages=100,
    )

    publisher = pubsub_v1.PublisherClient(batch_settings=settings)
    topic_path = publisher.topic_path(project_id, topic_id)

    futures = []
    for msg in messages:
        future = publisher.publish(
            topic_path,
            json.dumps(msg).encode(),
            content_type="application/json",
        )
        futures.append(future)

    # Wait for all messages
    results = [f.result(timeout=10) for f in futures]
    return results

# Usage
messages = [{"id": i, "value": f"message-{i}"} for i in range(1000)]
message_ids = publish_with_batching("my-project", "my-topic", messages)
print(f"Published {len(message_ids)} messages")
```

### Subscriber Performance Tuning

```python
from google.cloud import pubsub_v1

def subscribe_with_tuned_flow_control(
    project_id: str,
    subscription_id: str,
    max_messages: int = 1000,
    max_bytes: int = 1024 * 1024 * 1024,  # 1 GB
):
    """Subscribe with high-performance settings."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message):
        # Process message
        print(f"Processing: {message.data.decode()}")
        message.ack()

    streaming_pull_future = subscriber.subscribe(
        subscription_path,
        callback=callback,
        flow_control=pubsub_v1.types.FlowControl(
            max_messages=max_messages,
            max_bytes=max_bytes,
            # These settings allow maximum throughput
            # Adjust based on your message processing latency
        ),
    )

    try:
        streaming_pull_future.result()
    except Exception as e:
        print(f"Error: {e}")
        streaming_pull_future.cancel()
```

---

## Additional Resources

- See main SKILL.md for core concepts and setup
- See reference.md for API reference and troubleshooting
- Run scripts/setup_emulator.sh for automated emulator setup
