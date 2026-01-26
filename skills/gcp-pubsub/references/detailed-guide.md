# Google Cloud Pub/Sub - Detailed Reference

This document provides comprehensive implementation details, advanced patterns, and troubleshooting guidance for Google Cloud Pub/Sub.

## Detailed Setup Instructions

### Authentication Configuration

**Option A: Application Default Credentials (Development)**
```bash
gcloud auth application-default login
```

**Option B: Service Account (Production)**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

**Verify Setup:**
```python
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
print(f"Using project: {publisher.api.transport.credentials.project_id}")
```

## Advanced Topic and Subscription Configuration

### Create Topics and Subscriptions with Best Practices

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

## Production-Ready Publishing

### Message Publisher with Error Handling and Batching

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

## Production-Ready Subscribing

### Message Subscriber with Flow Control

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

## Dead Letter Queue Configuration

### Setup DLQ with Retry Policy

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

### Track Delivery Attempts

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

## Idempotency Patterns

### Idempotent Message Processing

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

## Local Development with Emulator

### Emulator Setup

```bash
# Install the Pub/Sub emulator
gcloud components install pubsub-emulator

# Start the emulator (runs on localhost:8085)
gcloud beta emulators pubsub start

# In another terminal, set environment variable
export PUBSUB_EMULATOR_HOST=localhost:8085
```

### Development Configuration

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

## Monitoring and Debugging

### Publisher with Monitoring

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

## IAM Permissions Reference

### Required Roles

- `roles/pubsub.publisher` - To publish messages
- `roles/pubsub.subscriber` - To subscribe to messages
- `roles/pubsub.admin` - To create/delete topics and subscriptions

### Custom IAM Policies

For production environments, create custom roles with minimal permissions:

```yaml
title: "Pub/Sub Publisher"
description: "Minimal permissions for publishing messages"
stage: "GA"
includedPermissions:
- pubsub.topics.publish
```

## Troubleshooting

### Common Issues

1. **PERMISSION_DENIED errors**: Verify IAM roles and service account permissions
2. **Timeout errors**: Increase `timeout` parameter in `future.result()`
3. **Memory issues**: Adjust `FlowControl` settings for subscribers
4. **Message duplicates**: Implement idempotency checks
5. **DLQ messages not moving**: Verify IAM permissions on dead letter topic

### Debugging Tips

- Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
- Use emulator for local testing
- Monitor Cloud Console for quota limits
- Check subscription backlog in Cloud Monitoring
