---
name: gcp-pubsub
description: |
  Work with Google Cloud Pub/Sub in Python: setup, topics, subscriptions, publishing,
  subscribing, dead letter queues, and emulator. Use when building event-driven
  architectures, implementing message queuing, or managing high-throughput systems.
  Includes reliability, idempotency, and testing patterns.
---

# Google Cloud Pub/Sub

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Quick Start](#quick-start)
- [Instructions](#instructions)
- [Examples](#examples)
- [Requirements](#requirements)
- [See Also](#see-also)

## Purpose

This skill provides comprehensive guidance for building robust, production-ready event-driven systems using Google Cloud Pub/Sub with Python. It covers the full lifecycle from initial setup through deployment, including advanced patterns for reliability, error handling, and performance optimization.

## When to Use

Use this skill when you need to:
- Build event-driven architectures with message-based communication
- Implement reliable message queuing between services
- Set up asynchronous communication patterns
- Handle at-least-once message delivery guarantees
- Manage high-throughput message systems (1000+ msgs/sec)
- Configure local development with Pub/Sub emulator
- Implement dead letter queues for failed message handling
- Monitor and debug Pub/Sub operations

## Quick Start

Install the google-cloud-pubsub library and authenticate:

```bash
# Install dependency
pip install google-cloud-pubsub

# Set up authentication (if not already configured)
gcloud auth application-default login

# Verify installation
python -c "from google.cloud import pubsub_v1; print('Ready')"
```

Create a topic and publish a message:

```python
from google.cloud import pubsub_v1

# Create publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("my-project", "my-topic")

# Create topic if it doesn't exist
try:
    publisher.create_topic(request={"name": topic_path})
except Exception as e:
    if "ALREADY_EXISTS" not in str(e):
        raise

# Publish a message
future = publisher.publish(topic_path, b"Hello, World!")
message_id = future.result()
print(f"Published message: {message_id}")
```

Subscribe and receive messages:

```python
from google.cloud import pubsub_v1

# Create subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("my-project", "my-subscription")

# Define message handler
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received: {message.data.decode()}")
    message.ack()

# Subscribe and listen
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

# Keep the subscriber running for at least 30 seconds
import time
try:
    streaming_pull_future.result(timeout=30)
except Exception as e:
    streaming_pull_future.cancel()
```

## Instructions

### Step 1: Set Up Your Development Environment

1. **Install dependencies:**
   ```bash
   pip install google-cloud-pubsub google-cloud-storage
   ```

2. **Configure authentication:**
   - Option A (Development): Use Application Default Credentials
     ```bash
     gcloud auth application-default login
     ```
   - Option B (Production): Use service account key
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
     ```

3. **Verify the setup:**
   ```python
   from google.cloud import pubsub_v1

   publisher = pubsub_v1.PublisherClient()
   print(f"Using project: {publisher.api.transport.credentials.project_id}")
   ```

### Step 2: Create Topics and Subscriptions

Create topics and subscriptions with appropriate configurations:

```python
from google.cloud import pubsub_v1

def create_topic_and_subscription(project_id: str, topic_id: str, subscription_id: str):
    """Create a topic and subscription with best practice settings."""
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    # Create topic
    topic_path = publisher.topic_path(project_id, topic_id)
    try:
        topic = publisher.create_topic(request={"name": topic_path})
        print(f"Topic created: {topic.name}")
    except Exception as e:
        if "ALREADY_EXISTS" not in str(e):
            raise
        print(f"Topic already exists: {topic_path}")

    # Create subscription with retry and flow control settings
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    subscription_config = {
        "name": subscription_path,
        "topic": topic_path,
        # Acknowledge deadline: time window for message processing
        "ack_deadline_seconds": 60,
        # Flow control settings
        "push_config": None,  # Use pull model
        # Retry policy (optional, uses defaults if not specified)
    }

    try:
        subscription = subscriber.create_subscription(request=subscription_config)
        print(f"Subscription created: {subscription.name}")
    except Exception as e:
        if "ALREADY_EXISTS" not in str(e):
            raise
        print(f"Subscription already exists: {subscription_path}")

    return topic_path, subscription_path
```

For detailed configuration examples and advanced setup, see `examples/examples.md`.

### Step 3: Publish Messages

Implement robust message publishing with proper error handling and batching:

```python
from google.cloud import pubsub_v1
import json
from typing import Optional, Dict, Any

class MessagePublisher:
    """Production-ready message publisher with error handling."""

    def __init__(self, project_id: str, topic_id: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)

    def publish_single(
        self,
        data: bytes,
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """Publish a single message and wait for result."""
        try:
            future = self.publisher.publish(
                self.topic_path,
                data,
                **(attributes or {})
            )
            message_id = future.result(timeout=5)
            return message_id
        except Exception as e:
            raise Exception(f"Failed to publish message: {e}")

    def publish_json(
        self,
        message_dict: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """Publish a JSON message."""
        data = json.dumps(message_dict).encode("utf-8")
        attributes = attributes or {}
        attributes["content-type"] = "application/json"
        return self.publish_single(data, attributes)

    def publish_batch(self, messages: list) -> list:
        """Publish multiple messages. Returns list of message IDs."""
        futures = []
        for msg in messages:
            future = self.publisher.publish(
                self.topic_path,
                msg.get("data", b""),
                **(msg.get("attributes", {}))
            )
            futures.append(future)

        message_ids = []
        for future in futures:
            try:
                message_ids.append(future.result(timeout=5))
            except Exception as e:
                message_ids.append(None)
                print(f"Batch publish error: {e}")

        return message_ids
```

### Step 4: Subscribe to Messages

Implement message subscribers with proper acknowledgment and error handling:

```python
from google.cloud import pubsub_v1
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageSubscriber:
    """Production-ready message subscriber with error handling."""

    def __init__(self, project_id: str, subscription_id: str):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_id
        )
        self.streaming_pull_future = None

    def process_message(self, message: pubsub_v1.subscriber.message.Message):
        """Override this method in subclasses to process messages."""
        raise NotImplementedError

    def callback(self, message: pubsub_v1.subscriber.message.Message):
        """Handle incoming message with error handling."""
        try:
            # Process message
            self.process_message(message)
            # Only acknowledge after successful processing
            message.ack()
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Don't ack - message will be redelivered
            message.nack()

    def subscribe(self, timeout: int = 30):
        """Start listening for messages."""
        self.streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.callback,
            flow_control=pubsub_v1.types.FlowControl(
                max_messages=100,  # Adjust based on memory
                max_bytes=100 * 1024 * 1024,  # 100 MB
            ),
        )

        try:
            self.streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            logger.error(f"Subscriber error: {e}")
            self.streaming_pull_future.cancel()

    def close(self):
        """Gracefully shutdown subscriber."""
        if self.streaming_pull_future:
            self.streaming_pull_future.cancel()
            self.streaming_pull_future.result()
```

### Step 5: Handle Acknowledgments, Retries, and Dead Letter Queues

Configure proper error handling and dead letter topic setup:

```python
from google.cloud import pubsub_v1
from google.protobuf.duration_pb2 import Duration

def setup_dead_letter_subscription(
    project_id: str,
    topic_id: str,
    subscription_id: str,
    dead_letter_topic_id: str,
    dead_letter_subscription_id: str,
    max_delivery_attempts: int = 5
):
    """Set up a subscription with dead letter topic."""
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    # Create main topic and subscription
    topic_path = publisher.topic_path(project_id, topic_id)
    dead_letter_topic_path = publisher.topic_path(project_id, dead_letter_topic_id)

    try:
        publisher.create_topic(request={"name": topic_path})
    except Exception as e:
        if "ALREADY_EXISTS" not in str(e):
            raise

    try:
        publisher.create_topic(request={"name": dead_letter_topic_path})
    except Exception as e:
        if "ALREADY_EXISTS" not in str(e):
            raise

    # Create main subscription with dead letter policy
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    subscription = pubsub_v1.types.Subscription(
        name=subscription_path,
        topic=topic_path,
        ack_deadline_seconds=60,
        # Dead letter policy configuration
        dead_letter_policy=pubsub_v1.types.DeadLetterPolicy(
            dead_letter_topic=dead_letter_topic_path,
            max_delivery_attempts=max_delivery_attempts,
        ),
        # Retry policy
        retry_policy=pubsub_v1.types.RetryPolicy(
            minimum_backoff=Duration(seconds=10),
            maximum_backoff=Duration(seconds=600),  # 10 minutes
        ),
    )

    try:
        subscriber.create_subscription(request=subscription)
        print(f"Subscription with DLQ created: {subscription_path}")
    except Exception as e:
        if "ALREADY_EXISTS" not in str(e):
            raise

    # Create dead letter subscription
    dlq_subscription_path = subscriber.subscription_path(
        project_id, dead_letter_subscription_id
    )
    dlq_subscription = pubsub_v1.types.Subscription(
        name=dlq_subscription_path,
        topic=dead_letter_topic_path,
        ack_deadline_seconds=60,
    )

    try:
        subscriber.create_subscription(request=dlq_subscription)
        print(f"Dead letter subscription created: {dlq_subscription_path}")
    except Exception as e:
        if "ALREADY_EXISTS" not in str(e):
            raise
```

Access delivery attempt count in your message handler:

```python
def callback_with_delivery_tracking(message: pubsub_v1.subscriber.message.Message):
    """Process message and track delivery attempts."""
    delivery_attempt = message.delivery_attempt or 0
    print(f"Message delivered {delivery_attempt} time(s)")

    try:
        # Process message
        print(f"Processing: {message.data.decode()}")
        message.ack()
    except Exception as e:
        if delivery_attempt >= 4:  # max_delivery_attempts is 5
            print(f"Max retries reached, moving to DLQ: {e}")
            message.ack()  # Acknowledge to remove from queue
        else:
            print(f"Retrying (attempt {delivery_attempt}): {e}")
            message.nack()  # Will be retried
```

### Step 6: Implement Best Practices for Reliability and Idempotency

Ensure idempotent message processing:

```python
import hashlib
import json
from typing import Dict, Any

class IdempotentMessageProcessor:
    """Process messages idempotently using message ID deduplication."""

    def __init__(self, backend=None):
        # backend could be Redis, Memcached, or any state store
        self.backend = backend or {}
        self.processed_ids = set()

    def get_message_key(self, message_data: bytes, attributes: Dict[str, str]) -> str:
        """Generate idempotency key from message content and attributes."""
        # Use message ID if available
        if "message_id" in attributes:
            return attributes["message_id"]

        # Otherwise generate from content
        content = message_data + json.dumps(attributes, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()

    def process_with_idempotency(
        self,
        message: pubsub_v1.subscriber.message.Message,
        process_fn
    ) -> bool:
        """Process message only once per unique ID."""
        key = self.get_message_key(message.data, dict(message.attributes))

        if key in self.processed_ids:
            print(f"Message already processed: {key}")
            message.ack()  # Still acknowledge
            return False

        try:
            # Process the message
            process_fn(message)
            # Mark as processed
            self.processed_ids.add(key)
            message.ack()
            return True
        except Exception as e:
            print(f"Processing failed: {e}")
            message.nack()
            return False
```

### Step 7: Set Up Local Development with Pub/Sub Emulator

Configure local development environment:

```bash
# Install the Pub/Sub emulator
gcloud components install pubsub-emulator

# Start the emulator (runs on localhost:8085)
gcloud beta emulators pubsub start

# In another terminal, set environment variable
export PUBSUB_EMULATOR_HOST=localhost:8085
```

Create a development configuration:

```python
import os
from google.cloud import pubsub_v1

def get_publisher(project_id: str):
    """Get publisher configured for dev or production."""
    if os.getenv("PUBSUB_EMULATOR_HOST"):
        # Local development
        return pubsub_v1.PublisherClient(
            transport=pubsub_v1.services.publisher.transports.GrpcTransport(
                channel=pubsub_v1.gapic_v1.client_info.ClientInfo(
                    api_core={"api_core": "emulator"}
                )
            )
        )
    else:
        # Production
        return pubsub_v1.PublisherClient()

# Usage
publisher = get_publisher("my-project-id")
# Works with both emulator and production service
```

### Step 8: Monitor and Debug Pub/Sub Operations

Implement logging and monitoring:

```python
import logging
from google.cloud import pubsub_v1
from functools import wraps
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoredPublisher:
    """Publisher with operation monitoring."""

    def __init__(self, project_id: str, topic_id: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)
        self.publish_count = 0
        self.publish_errors = 0

    def publish(self, data: bytes, attributes: dict = None):
        """Publish with timing and error tracking."""
        start = time.time()
        try:
            future = self.publisher.publish(
                self.topic_path,
                data,
                **(attributes or {})
            )
            message_id = future.result(timeout=5)
            duration = time.time() - start
            self.publish_count += 1
            logger.info(
                f"Message published: {message_id} (duration: {duration:.3f}s)"
            )
            return message_id
        except Exception as e:
            self.publish_errors += 1
            logger.error(f"Publish failed: {e}", exc_info=True)
            raise

    def get_stats(self) -> dict:
        """Get publisher statistics."""
        return {
            "published": self.publish_count,
            "errors": self.publish_errors,
            "error_rate": self.publish_errors / max(1, self.publish_count)
        }

# Query subscription stats
def get_subscription_stats(project_id: str, subscription_id: str) -> dict:
    """Get subscription metrics."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    subscription = subscriber.get_subscription(request={"subscription": subscription_path})

    return {
        "subscription": subscription.name,
        "topic": subscription.topic,
        "ack_deadline": subscription.ack_deadline_seconds,
        "push_endpoint": subscription.push_config.push_endpoint if subscription.push_config else None,
    }
```

## Examples

### Example 1: Simple Publisher

```python
from google.cloud import pubsub_v1

def publish_message(project_id: str, topic_id: str, message: str):
    """Simple one-time message publish."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    future = publisher.publish(topic_path, message.encode("utf-8"))
    print(f"Published: {future.result()}")

# Usage
publish_message("my-project", "my-topic", "Hello, World!")
```

### Example 2: Streaming Subscriber

```python
from google.cloud import pubsub_v1
import signal
import sys

def listen_for_messages(project_id: str, subscription_id: str):
    """Continuously listen for messages."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message):
        print(f"Received: {message.data.decode()}")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("Shutting down...")
        streaming_pull_future.cancel()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        streaming_pull_future.result()
    except Exception as e:
        print(f"Streaming error: {e}")
        streaming_pull_future.cancel()

# Usage
listen_for_messages("my-project", "my-subscription")
```

### Example 3: Message With Attributes

```python
from google.cloud import pubsub_v1
import json

def publish_event(project_id: str, topic_id: str, event: dict):
    """Publish event with attributes for routing."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    future = publisher.publish(
        topic_path,
        json.dumps(event).encode("utf-8"),
        event_type=event.get("type", "unknown"),
        timestamp=str(event.get("timestamp")),
        source=event.get("source", "unknown"),
    )

    return future.result()

# Usage
event = {
    "type": "user.created",
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "auth-service",
    "user_id": "user-123",
    "email": "user@example.com"
}
publish_event("my-project", "events-topic", event)
```

For more comprehensive examples including async patterns, testing, and integration scenarios, see `examples/examples.md`.

## Requirements

- **Python:** 3.7+ (tested on 3.13+)
- **Dependencies:**
  ```bash
  pip install google-cloud-pubsub>=2.18.0
  ```
- **Google Cloud Project:** Active GCP project with Pub/Sub API enabled
- **Authentication:** One of the following:
  - Application Default Credentials (ADC)
  - Service account key file
  - Cloud SDK authenticated account (via `gcloud auth`)
- **IAM Permissions:** Required roles depend on use case:
  - `roles/pubsub.publisher` - To publish messages
  - `roles/pubsub.subscriber` - To subscribe to messages
  - `roles/pubsub.admin` - To create/delete topics and subscriptions
- **For Local Development:**
  ```bash
  gcloud components install pubsub-emulator
  ```

## See Also

- [examples/examples.md](./examples/examples.md) - Comprehensive code examples including async patterns, testing, and advanced scenarios
- [references/reference.md](./references/reference.md) - API reference, configuration options, and troubleshooting guide
- [scripts/setup_emulator.sh](./scripts/setup_emulator.sh) - Emulator setup utility
- [scripts/pubsub_utils.py](./scripts/pubsub_utils.py) - Helper utilities for common operations
