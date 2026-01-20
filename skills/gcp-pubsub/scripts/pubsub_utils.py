#!/usr/bin/env python
"""
Utility script for common Google Cloud Pub/Sub operations.

Usage:
  python pubsub_utils.py --help
  python pubsub_utils.py --create-topic my-project my-topic
  python pubsub_utils.py --create-subscription my-project my-sub my-topic
  python pubsub_utils.py --publish my-project my-topic "message content"
  python pubsub_utils.py --list-topics my-project
"""

import argparse
import json
import os
import sys
from typing import Optional

from google.cloud import pubsub_v1
from google.api_core import exceptions


class PubSubManager:
    """Utility class for Pub/Sub operations."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()

    def create_topic(self, topic_id: str) -> str:
        """Create a topic."""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        try:
            topic = self.publisher.create_topic(request={"name": topic_path})
            print(f"✓ Topic created: {topic.name}")
            return topic_path
        except exceptions.AlreadyExists:
            print(f"✓ Topic already exists: {topic_path}")
            return topic_path
        except Exception as e:
            print(f"✗ Error creating topic: {e}")
            raise

    def create_subscription(
        self,
        subscription_id: str,
        topic_id: str,
        ack_deadline: int = 60,
    ) -> str:
        """Create a subscription."""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_id
        )

        try:
            subscription = self.subscriber.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": topic_path,
                    "ack_deadline_seconds": ack_deadline,
                }
            )
            print(f"✓ Subscription created: {subscription.name}")
            return subscription_path
        except exceptions.AlreadyExists:
            print(f"✓ Subscription already exists: {subscription_path}")
            return subscription_path
        except Exception as e:
            print(f"✗ Error creating subscription: {e}")
            raise

    def publish_message(
        self,
        topic_id: str,
        message: str,
        attributes: Optional[dict] = None,
    ) -> str:
        """Publish a message to a topic."""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)

        try:
            future = self.publisher.publish(
                topic_path,
                message.encode("utf-8"),
                **(attributes or {})
            )
            message_id = future.result(timeout=5)
            print(f"✓ Message published: {message_id}")
            return message_id
        except Exception as e:
            print(f"✗ Error publishing message: {e}")
            raise

    def publish_json(
        self,
        topic_id: str,
        data: dict,
        attributes: Optional[dict] = None,
    ) -> str:
        """Publish a JSON message to a topic."""
        message = json.dumps(data)
        attrs = attributes or {}
        attrs["content-type"] = "application/json"
        return self.publish_message(topic_id, message, attrs)

    def list_topics(self) -> list:
        """List all topics in the project."""
        try:
            topics = list(
                self.publisher.list_topics(request={"project": f"projects/{self.project_id}"})
            )
            if not topics:
                print("No topics found")
                return []

            print(f"Topics ({len(topics)}):")
            for topic in topics:
                print(f"  - {topic.name}")
            return topics
        except Exception as e:
            print(f"✗ Error listing topics: {e}")
            raise

    def list_subscriptions(self) -> list:
        """List all subscriptions in the project."""
        try:
            subscriptions = list(
                self.subscriber.list_subscriptions(
                    request={"project": f"projects/{self.project_id}"}
                )
            )
            if not subscriptions:
                print("No subscriptions found")
                return []

            print(f"Subscriptions ({len(subscriptions)}):")
            for sub in subscriptions:
                print(f"  - {sub.name}")
                print(f"    Topic: {sub.topic}")
                print(f"    Ack deadline: {sub.ack_deadline_seconds}s")
            return subscriptions
        except Exception as e:
            print(f"✗ Error listing subscriptions: {e}")
            raise

    def delete_topic(self, topic_id: str) -> None:
        """Delete a topic."""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)

        try:
            self.publisher.delete_topic(request={"topic": topic_path})
            print(f"✓ Topic deleted: {topic_path}")
        except exceptions.NotFound:
            print(f"✗ Topic not found: {topic_path}")
        except Exception as e:
            print(f"✗ Error deleting topic: {e}")
            raise

    def delete_subscription(self, subscription_id: str) -> None:
        """Delete a subscription."""
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_id
        )

        try:
            self.subscriber.delete_subscription(
                request={"subscription": subscription_path}
            )
            print(f"✓ Subscription deleted: {subscription_path}")
        except exceptions.NotFound:
            print(f"✗ Subscription not found: {subscription_path}")
        except Exception as e:
            print(f"✗ Error deleting subscription: {e}")
            raise

    def get_topic_info(self, topic_id: str) -> dict:
        """Get topic information."""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)

        try:
            topic = self.publisher.get_topic(request={"topic": topic_path})
            info = {
                "name": topic.name,
                "labels": dict(topic.labels),
                "message_retention_duration": topic.message_retention_duration,
            }
            print(f"Topic: {topic.name}")
            print(f"  Labels: {info['labels']}")
            print(f"  Retention: {info['message_retention_duration']}")
            return info
        except Exception as e:
            print(f"✗ Error getting topic info: {e}")
            raise

    def get_subscription_info(self, subscription_id: str) -> dict:
        """Get subscription information."""
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_id
        )

        try:
            sub = self.subscriber.get_subscription(
                request={"subscription": subscription_path}
            )
            info = {
                "name": sub.name,
                "topic": sub.topic,
                "ack_deadline": sub.ack_deadline_seconds,
                "labels": dict(sub.labels),
                "enable_message_ordering": sub.enable_message_ordering,
                "filter": sub.filter,
            }
            print(f"Subscription: {sub.name}")
            print(f"  Topic: {sub.topic}")
            print(f"  Ack deadline: {sub.ack_deadline_seconds}s")
            print(f"  Labels: {info['labels']}")
            print(f"  Message ordering: {sub.enable_message_ordering}")
            if sub.filter:
                print(f"  Filter: {sub.filter}")
            return info
        except Exception as e:
            print(f"✗ Error getting subscription info: {e}")
            raise

    def pull_messages(self, subscription_id: str, max_messages: int = 10) -> list:
        """Pull messages from a subscription."""
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_id
        )

        try:
            response = self.subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": max_messages,
                },
                timeout=5.0,
            )

            if not response.received_messages:
                print("No messages available")
                return []

            messages = []
            ack_ids = []

            for received_message in response.received_messages:
                msg = received_message.message
                ack_id = received_message.ack_id

                print(f"\nMessage ID: {msg.message_id}")
                print(f"Data: {msg.data.decode('utf-8')}")
                print(f"Attributes: {dict(msg.attributes)}")
                print(f"Publish time: {msg.publish_time}")

                messages.append({
                    "id": msg.message_id,
                    "data": msg.data.decode("utf-8"),
                    "attributes": dict(msg.attributes),
                    "publish_time": str(msg.publish_time),
                })
                ack_ids.append(ack_id)

            # Acknowledge messages
            if ack_ids:
                self.subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": ack_ids,
                    }
                )
                print(f"\n✓ Acknowledged {len(ack_ids)} messages")

            return messages
        except Exception as e:
            print(f"✗ Error pulling messages: {e}")
            raise


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Google Cloud Pub/Sub utility tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List topics
  python pubsub_utils.py my-project --list-topics

  # Create topic and subscription
  python pubsub_utils.py my-project --create-topic my-topic
  python pubsub_utils.py my-project --create-subscription my-sub my-topic

  # Publish message
  python pubsub_utils.py my-project --publish my-topic "Hello World"

  # Pull messages
  python pubsub_utils.py my-project --pull my-subscription 10

  # Get topic info
  python pubsub_utils.py my-project --topic-info my-topic

  # Delete resources
  python pubsub_utils.py my-project --delete-topic my-topic
  python pubsub_utils.py my-project --delete-subscription my-subscription
        """,
    )

    parser.add_argument("project_id", help="Google Cloud project ID")
    parser.add_argument("--list-topics", action="store_true", help="List all topics")
    parser.add_argument("--list-subscriptions", action="store_true", help="List all subscriptions")
    parser.add_argument("--create-topic", metavar="TOPIC_ID", help="Create a topic")
    parser.add_argument(
        "--create-subscription",
        nargs=2,
        metavar=("SUBSCRIPTION_ID", "TOPIC_ID"),
        help="Create a subscription",
    )
    parser.add_argument(
        "--publish",
        nargs=2,
        metavar=("TOPIC_ID", "MESSAGE"),
        help="Publish a message",
    )
    parser.add_argument(
        "--pull",
        nargs=2,
        metavar=("SUBSCRIPTION_ID", "MAX_MESSAGES"),
        help="Pull messages from subscription",
    )
    parser.add_argument("--topic-info", metavar="TOPIC_ID", help="Get topic information")
    parser.add_argument(
        "--subscription-info",
        metavar="SUBSCRIPTION_ID",
        help="Get subscription information",
    )
    parser.add_argument("--delete-topic", metavar="TOPIC_ID", help="Delete a topic")
    parser.add_argument(
        "--delete-subscription",
        metavar="SUBSCRIPTION_ID",
        help="Delete a subscription",
    )

    args = parser.parse_args()

    manager = PubSubManager(args.project_id)

    try:
        if args.list_topics:
            manager.list_topics()
        elif args.list_subscriptions:
            manager.list_subscriptions()
        elif args.create_topic:
            manager.create_topic(args.create_topic)
        elif args.create_subscription:
            sub_id, topic_id = args.create_subscription
            manager.create_subscription(sub_id, topic_id)
        elif args.publish:
            topic_id, message = args.publish
            manager.publish_message(topic_id, message)
        elif args.pull:
            subscription_id, max_messages = args.pull
            manager.pull_messages(subscription_id, int(max_messages))
        elif args.topic_info:
            manager.get_topic_info(args.topic_info)
        elif args.subscription_info:
            manager.get_subscription_info(args.subscription_info)
        elif args.delete_topic:
            manager.delete_topic(args.delete_topic)
        elif args.delete_subscription:
            manager.delete_subscription(args.delete_subscription)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
