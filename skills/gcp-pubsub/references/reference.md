# Google Cloud Pub/Sub - Reference Guide

Complete API reference, configuration options, troubleshooting, and best practices.

## Table of Contents

1. [Core API Reference](#core-api-reference)
2. [Configuration Reference](#configuration-reference)
3. [Error Codes and Troubleshooting](#error-codes-and-troubleshooting)
4. [Best Practices Checklist](#best-practices-checklist)
5. [Performance Tuning](#performance-tuning)
6. [Debugging and Monitoring](#debugging-and-monitoring)

---

## Core API Reference

### Publisher Client

#### Class: `pubsub_v1.PublisherClient`

Main client for publishing messages.

##### Methods

**`topic_path(project_id: str, topic_id: str) -> str`**
- Formats topic resource name
- Returns: `projects/{project}/topics/{topic}`

**`create_topic(request: dict) -> Topic`**
- Creates a new topic
- Parameters:
  - `name`: Full topic path
  - `labels`: (optional) Dict of labels
  - `message_retention_duration`: (optional) Message retention time
  - `message_storage_policy`: (optional) Storage policy configuration
- Returns: Topic resource
- Raises: `google.api_core.exceptions.AlreadyExists` if topic exists

```python
topic = publisher.create_topic(
    request={
        "name": "projects/my-project/topics/my-topic",
        "labels": {
            "environment": "production",
            "team": "data-platform"
        }
    }
)
```

**`publish(topic: str, data: bytes, **attributes) -> Future`**
- Publishes a message to a topic
- Parameters:
  - `topic`: Topic path string
  - `data`: Message data as bytes
  - `**attributes`: Optional message attributes (dict)
- Returns: `concurrent.futures.Future` for message_id
- Attributes are limited to 100 per message, 1024 bytes per attribute

```python
future = publisher.publish(
    "projects/my-project/topics/my-topic",
    b"message content",
    source="api",
    version="1.0"
)
message_id = future.result(timeout=10)
```

**`get_topic(request: dict) -> Topic`**
- Retrieves topic metadata
- Parameters:
  - `topic`: Full topic path
- Returns: Topic resource with metadata

**`list_topics(request: dict) -> Iterable`**
- Lists all topics in project
- Returns: Paginated topic list

```python
for topic in publisher.list_topics(
    request={"project": "projects/my-project"}
):
    print(topic.name)
```

**`update_topic(request: dict) -> Topic`**
- Updates topic configuration
- Parameters:
  - `topic`: Topic resource with updated fields
  - `update_mask`: Which fields to update

**`delete_topic(request: dict)`**
- Deletes a topic
- Note: All subscriptions must be deleted first

---

### Subscriber Client

#### Class: `pubsub_v1.SubscriberClient`

Main client for subscribing to messages.

##### Methods

**`subscription_path(project_id: str, subscription_id: str) -> str`**
- Formats subscription resource name
- Returns: `projects/{project}/subscriptions/{subscription}`

**`create_subscription(request: dict) -> Subscription`**
- Creates a new subscription
- Parameters:
  - `name`: Full subscription path
  - `topic`: Topic to subscribe to
  - `ack_deadline_seconds`: Time window for acking (default 10)
  - `push_config`: (optional) Push delivery configuration
  - `dead_letter_policy`: (optional) DLQ configuration
  - `retry_policy`: (optional) Retry configuration
  - `enable_message_ordering`: (optional) Ordered delivery
  - `filter`: (optional) Message filter expression
- Returns: Subscription resource

```python
subscription = subscriber.create_subscription(
    request={
        "name": "projects/my-project/subscriptions/my-sub",
        "topic": "projects/my-project/topics/my-topic",
        "ack_deadline_seconds": 60,
        "dead_letter_policy": {
            "dead_letter_topic": "projects/my-project/topics/dlq-topic",
            "max_delivery_attempts": 5,
        },
        "enable_message_ordering": True,
    }
)
```

**`subscribe(subscription: str, callback: Callable) -> StreamingPullFuture`**
- Starts listening for messages
- Parameters:
  - `subscription`: Full subscription path
  - `callback`: Function called for each message
  - `flow_control`: FlowControl configuration
  - `scheduler`: (optional) Custom scheduler
- Returns: `StreamingPullFuture` to control subscriber
- Callback receives `Message` object with:
  - `data`: Message bytes
  - `attributes`: Message attributes dict
  - `message_id`: Unique message ID
  - `publish_time`: When published
  - `delivery_attempt`: Delivery attempt count (DLQ)

```python
def callback(message):
    print(f"Received: {message.data}")
    message.ack()

future = subscriber.subscribe(
    "projects/my-project/subscriptions/my-sub",
    callback=callback,
    flow_control=pubsub_v1.types.FlowControl(
        max_messages=100,
        max_bytes=100 * 1024 * 1024,
    )
)
```

**`pull(request: dict) -> PullResponse`**
- Synchronously pull messages (non-streaming)
- Parameters:
  - `subscription`: Full subscription path
  - `max_messages`: Max messages to return
  - `return_immediately`: (optional) Don't wait for messages
- Returns: Response with list of ReceivedMessage objects

```python
response = subscriber.pull(
    request={
        "subscription": "projects/my-project/subscriptions/my-sub",
        "max_messages": 100,
    },
    timeout=5.0,
)

for received_message in response.received_messages:
    message = received_message.message
    ack_id = received_message.ack_id
    print(f"Message: {message.data}")
```

**`acknowledge(request: dict)`**
- Acknowledges received messages
- Parameters:
  - `subscription`: Full subscription path
  - `ack_ids`: List of ack_id strings from pull response

```python
subscriber.acknowledge(
    request={
        "subscription": "projects/my-project/subscriptions/my-sub",
        "ack_ids": ["ack_id_1", "ack_id_2"],
    }
)
```

**`modify_ack_deadline(request: dict)`**
- Extends deadline for unacknowledged message
- Parameters:
  - `subscription`: Full subscription path
  - `ack_ids`: List of ack_ids
  - `ack_deadline_seconds`: New deadline

```python
# Give more time to process
subscriber.modify_ack_deadline(
    request={
        "subscription": "projects/my-project/subscriptions/my-sub",
        "ack_ids": ["ack_id_1"],
        "ack_deadline_seconds": 120,
    }
)
```

**`get_subscription(request: dict) -> Subscription`**
- Retrieves subscription metadata
- Parameters:
  - `subscription`: Full subscription path

**`list_subscriptions(request: dict) -> Iterable`**
- Lists all subscriptions in project

**`delete_subscription(request: dict)`**
- Deletes a subscription

---

### Message Objects

#### Class: `pubsub_v1.subscriber.message.Message` (streaming)

Represents a message in streaming pull.

**Attributes:**
- `message_id: str` - Unique message identifier
- `data: bytes` - Message payload
- `attributes: dict` - Message attributes
- `publish_time: google.protobuf.timestamp_pb2.Timestamp` - Publish time
- `delivery_attempt: int` - Delivery attempt number (requires DLQ enabled)

**Methods:**
- `ack()` - Acknowledge message (successfully processed)
- `nack()` - Negative acknowledge (redelivery)

#### ReceivedMessage (pull)

Represents message in pull response.

**Attributes:**
- `ack_id: str` - ID for acknowledging
- `message: Message` - The message object

---

### Types and Configuration

#### FlowControl

Controls message delivery rate.

```python
from google.cloud.pubsub_v1.types import FlowControl

flow_control = FlowControl(
    max_messages=100,        # Max unacked messages
    max_bytes=100*1024*1024, # Max total bytes of unacked messages
)
```

#### BatchSettings

Configures message batching for publishing.

```python
from google.cloud.pubsub_v1.types import BatchSettings

settings = BatchSettings(
    max_bytes=10 * 1024 * 1024,  # 10 MB
    max_latency=0.1,               # 100 ms
    max_messages=100,              # Messages
)

publisher = pubsub_v1.PublisherClient(batch_settings=settings)
```

#### RetryPolicy

Configures automatic retries.

```python
from google.cloud.pubsub_v1.types import RetryPolicy
from google.protobuf.duration_pb2 import Duration

retry_policy = RetryPolicy(
    minimum_backoff=Duration(seconds=10),
    maximum_backoff=Duration(seconds=600),
)
```

#### DeadLetterPolicy

Configures dead letter topic handling.

```python
from google.cloud.pubsub_v1.types import DeadLetterPolicy

dlq_policy = DeadLetterPolicy(
    dead_letter_topic="projects/my-project/topics/dlq",
    max_delivery_attempts=5,
)
```

---

## Configuration Reference

### Topic Configuration

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `labels` | dict | {} | Custom labels for organization |
| `message_retention_duration` | Duration | 7 days | How long to keep messages |
| `message_storage_policy` | Policy | region default | Where to store messages |

**Example:**

```python
publisher.create_topic(request={
    "name": "projects/my-project/topics/my-topic",
    "labels": {
        "team": "platform",
        "environment": "production"
    },
    "message_retention_duration": Duration(days=30),
    "message_storage_policy": MessageStoragePolicy(
        allowed_persistence_regions=["us-central1", "us-west1"]
    )
})
```

### Subscription Configuration

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `ack_deadline_seconds` | int | 10 | Time to process message |
| `message_retention_duration` | Duration | 7 days | Retain unacked messages |
| `enable_message_ordering` | bool | False | Process messages in order |
| `filter` | str | "" | CEL expression to filter messages |
| `dead_letter_policy` | Policy | None | Handle failed messages |
| `retry_policy` | Policy | Default | Retry configuration |
| `push_config` | Config | None | Push delivery configuration |

**Example with comprehensive settings:**

```python
subscriber.create_subscription(request={
    "name": "projects/my-project/subscriptions/my-sub",
    "topic": "projects/my-project/topics/my-topic",
    "ack_deadline_seconds": 60,
    "message_retention_duration": Duration(days=7),
    "enable_message_ordering": True,
    "filter": 'attributes.event_type = "critical"',
    "dead_letter_policy": {
        "dead_letter_topic": "projects/my-project/topics/dlq",
        "max_delivery_attempts": 5,
    },
    "retry_policy": {
        "minimum_backoff": Duration(seconds=10),
        "maximum_backoff": Duration(seconds=600),
    },
})
```

### Filter Expression Syntax

Filter messages using CEL (Common Expression Language):

```python
# Examples
"attributes.event_type = 'critical'"
"attributes.priority > 5"
"attributes.service IN ('api', 'worker')"
"has(attributes.user_id)"
"attributes.timestamp > '2024-01-01T00:00:00Z'"
"size(data) > 1024"  # Message size > 1KB
```

---

## Error Codes and Troubleshooting

### Common Exceptions

#### `google.api_core.exceptions.AlreadyExists`

Topic or subscription already exists.

```python
try:
    publisher.create_topic(request={"name": topic_path})
except AlreadyExists:
    print("Topic already exists")
```

#### `google.api_core.exceptions.NotFound`

Topic or subscription doesn't exist.

```python
try:
    subscription = subscriber.get_subscription(request={"subscription": sub_path})
except NotFound:
    print("Subscription not found")
```

#### `google.api_core.exceptions.DeadlineExceeded`

Operation timed out.

```python
try:
    message_id = future.result(timeout=5)
except DeadlineExceeded:
    print("Publish operation timed out")
```

#### `google.api_core.exceptions.PermissionDenied`

Insufficient IAM permissions.

**Solution:** Check service account has required roles:
- `roles/pubsub.publisher` - To publish
- `roles/pubsub.subscriber` - To subscribe
- `roles/pubsub.admin` - To create/delete resources

#### `google.api_core.exceptions.InvalidArgument`

Invalid argument in request.

Common causes:
- Malformed topic/subscription path
- Invalid configuration values
- Attributes exceed size limits

#### `google.api_core.exceptions.Unavailable`

Service temporarily unavailable.

**Solution:** Implement retry logic with exponential backoff.

### Troubleshooting Guide

#### Messages Not Being Received

**Possible Causes:**

1. **Subscription doesn't exist or is wrong topic**
   ```python
   sub = subscriber.get_subscription(request={"subscription": sub_path})
   print(f"Topic: {sub.topic}")
   ```

2. **Messages published before subscription created**
   - Pub/Sub doesn't deliver messages published before subscription exists
   - Solution: Create subscription first, then publish

3. **Flow control settings too restrictive**
   - Increase `max_messages` and `max_bytes`

4. **Message filter excluding messages**
   ```python
   # Check filter expression
   sub = subscriber.get_subscription(request={"subscription": sub_path})
   print(f"Filter: {sub.filter}")
   ```

5. **Subscription in dead letter queue**
   - Check if max_delivery_attempts exceeded

#### High Message Latency

**Possible Causes:**

1. **Ack deadline too low**
   - Increase `ack_deadline_seconds` if processing takes time
   - Min: 10 seconds, Max: 600 seconds

2. **Flow control limiting throughput**
   ```python
   # Increase for higher throughput
   flow_control = FlowControl(
       max_messages=1000,
       max_bytes=1024 * 1024 * 1024,  # 1 GB
   )
   ```

3. **Processing callback too slow**
   - Profile callback function
   - Move CPU-intensive work to thread/process pool
   - Batch operations

4. **Network latency to Pub/Sub**
   - Use same region as topic
   - Check network connectivity

#### High Publish Latency

**Possible Causes:**

1. **Batch settings creating delay**
   ```python
   # Reduce latency threshold
   settings = BatchSettings(
       max_latency=0.01,  # 10 ms instead of 100 ms
       max_messages=10,   # Smaller batches
   )
   ```

2. **Publishing too fast, hitting rate limits**
   - Implement backoff
   - Use batch publishing

3. **Attribute or message too large**
   - Attributes: max 1024 bytes each
   - Message: max 10 MB

#### Memory Issues in Subscriber

**Symptoms:** High memory usage, frequent GC pauses

**Solutions:**

1. **Reduce flow control limits**
   ```python
   flow_control = FlowControl(
       max_messages=10,
       max_bytes=10 * 1024 * 1024,  # 10 MB
   )
   ```

2. **Process messages faster**
   - Optimize callback function
   - Use async processing

3. **Monitor memory usage**
   ```python
   import psutil
   process = psutil.Process()
   memory_info = process.memory_info()
   print(f"Memory: {memory_info.rss / 1024 / 1024:.1f} MB")
   ```

#### Authentication Errors

**Error:** `google.auth.exceptions.DefaultCredentialsError`

**Solutions:**

1. **Use Application Default Credentials**
   ```bash
   gcloud auth application-default login
   ```

2. **Use service account key**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
   ```

3. **Verify credentials**
   ```python
   from google.auth import default
   credentials, project = default()
   print(f"Project: {project}")
   print(f"Credentials: {credentials}")
   ```

---

## Best Practices Checklist

### Before Going to Production

- [ ] **Idempotency**: Implement message deduplication
- [ ] **Error Handling**: Configure dead letter topics
- [ ] **Monitoring**: Add logging and metrics
- [ ] **Testing**: Test with emulator locally
- [ ] **Permissions**: Use least-privilege IAM roles
- [ ] **Retention**: Set appropriate message retention
- [ ] **Ordering**: Use ordering key if messages must be ordered
- [ ] **Timeouts**: Set appropriate ack deadlines
- [ ] **Flow Control**: Tune for your infrastructure
- [ ] **Retry Policy**: Configure appropriate backoff
- [ ] **Graceful Shutdown**: Handle termination signals

### Performance Optimization

- [ ] **Batch Publishing**: Use batch settings for high throughput
- [ ] **Flow Control**: Tune max_messages and max_bytes based on memory
- [ ] **Ack Deadline**: Set based on processing time
- [ ] **Message Size**: Keep messages under 10 MB
- [ ] **Attributes**: Use for routing, not large data
- [ ] **Regional**: Use same region as topic
- [ ] **Connection Pool**: Reuse client instances
- [ ] **Async Processing**: Use async/await patterns

### Security Best Practices

- [ ] **IAM Roles**: Use specific roles, not Editor/Owner
- [ ] **VPC-SC**: Use VPC Service Controls if required
- [ ] **Encryption**: Enable CMEK if required
- [ ] **Access Logs**: Enable audit logging
- [ ] **Secrets**: Don't include in message attributes
- [ ] **TLS**: Ensure TLS encryption in transit
- [ ] **Validation**: Validate message content

---

## Performance Tuning

### Publisher Tuning

```python
from google.cloud.pubsub_v1.types import BatchSettings

# High throughput settings
settings = BatchSettings(
    max_bytes=10 * 1024 * 1024,  # 10 MB
    max_latency=0.05,              # 50 ms
    max_messages=1000,             # 1000 messages
)

publisher = pubsub_v1.PublisherClient(batch_settings=settings)
```

**Trade-offs:**
- Higher `max_bytes` and `max_messages` = Higher throughput, higher latency
- Lower `max_latency` = Lower latency, less batching

### Subscriber Tuning

```python
# High throughput settings
flow_control = pubsub_v1.types.FlowControl(
    max_messages=1000,
    max_bytes=1024 * 1024 * 1024,  # 1 GB
)

streaming_pull_future = subscriber.subscribe(
    subscription_path,
    callback=callback,
    flow_control=flow_control,
)
```

**Trade-offs:**
- Higher limits = Better throughput, higher memory
- Lower limits = Lower memory, lower throughput

### Ack Deadline Tuning

**Rule of thumb:** `ack_deadline_seconds` >= 2 * 95th percentile processing time

```python
# For variable processing times
subscriber.create_subscription(request={
    "name": subscription_path,
    "topic": topic_path,
    "ack_deadline_seconds": 60,  # 60 seconds for ~30 second p95
})
```

---

## Debugging and Monitoring

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("google.api_core").setLevel(logging.DEBUG)

# Pub/Sub specific
logger = logging.getLogger("google.cloud.pubsub_v1")
logger.setLevel(logging.DEBUG)
```

### Monitoring Metrics

**Key Metrics:**

1. **Publish Metrics:**
   - Messages published per second
   - Publish latency (p50, p95, p99)
   - Publish errors

2. **Subscription Metrics:**
   - Messages delivered per second
   - Ack rate (acknowledged / delivered)
   - Message age (time in queue)
   - Processing latency
   - Redelivery rate

```python
# Example monitoring code
class MetricsCollector:
    def __init__(self):
        self.messages_published = 0
        self.messages_processed = 0
        self.errors = 0
        self.start_time = time.time()

    def record_publish(self, success: bool):
        if success:
            self.messages_published += 1
        else:
            self.errors += 1

    def record_process(self, success: bool):
        if success:
            self.messages_processed += 1
        else:
            self.errors += 1

    def get_stats(self):
        elapsed = time.time() - self.start_time
        return {
            "messages_published": self.messages_published,
            "messages_processed": self.messages_processed,
            "errors": self.errors,
            "pub_rate": self.messages_published / elapsed,
            "sub_rate": self.messages_processed / elapsed,
            "error_rate": self.errors / max(1, self.messages_published),
        }
```

### Health Checks

```python
def health_check(project_id: str, topic_id: str) -> bool:
    """Verify Pub/Sub is working."""
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)

        # Try to publish a test message
        future = publisher.publish(topic_path, b"health_check")
        future.result(timeout=5)
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
```

---

## Additional Resources

- [Google Cloud Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Python Client Library](https://cloud.google.com/python/docs/reference/pubsub/latest)
- [Pub/Sub Pricing](https://cloud.google.com/pubsub/pricing)
- [Quotas and Limits](https://cloud.google.com/pubsub/quotas)
