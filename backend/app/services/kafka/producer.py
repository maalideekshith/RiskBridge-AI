import json
import logging
from typing import Any

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self._producer = None

    def _get_producer(self) -> KafkaProducer:
        if self._producer is None:
            self._producer = KafkaProducer(
    bootstrap_servers=self.bootstrap_servers,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)

        return self._producer

    def _validate_event(
        self,
        topic: str,
        event: dict[str, Any],
    ) -> None:
        """
        Validate the basic schema of a Kafka event before publishing.
        """

        if not isinstance(event, dict):
            raise ValueError("Kafka event must be a dictionary")

        event_type = event.get("event_type")

        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError(
                "Kafka event must contain a non-empty 'event_type'"
            )

        expected_event_prefix = {
            "payment-events": "payment.",
            "refund-events": "refund.",
            "dispute-events": "dispute.",
            "merchant-events": "merchant.",
            "risk-events": "risk.",
        }

        expected_prefix = expected_event_prefix.get(topic)

        if expected_prefix and not event_type.startswith(expected_prefix):
            raise ValueError(
                f"Invalid event_type '{event_type}' for topic '{topic}'. "
                f"Expected prefix '{expected_prefix}'"
            )

        identifier_fields = (
            "payment_id",
            "refund_id",
            "dispute_id",
            "merchant_id",
            "risk_assessment_id",
        )

        if not any(field in event for field in identifier_fields):
            raise ValueError(
                "Kafka event must contain at least one entity identifier"
            )

        if "created_at" not in event:
            raise ValueError(
                "Kafka event must contain 'created_at'"
            )

    def publish(
        self,
        topic: str,
        event: dict[str, Any],
    ) -> bool:
        """
        Publish an event to Kafka.

        Returns:
            True  -> event published successfully
            False -> Kafka unavailable / publish failed

        Kafka failure does not propagate to the API request.
        """

        try:
            self._validate_event(topic, event)

            producer = self._get_producer()

            future = producer.send(
                topic,
                value=event,
            )

            record_metadata = future.get(timeout=5)

            logger.info(
                "Kafka event published: "
                "topic=%s partition=%s offset=%s",
                record_metadata.topic,
                record_metadata.partition,
                record_metadata.offset,
            )

            return True

        except Exception:
            logger.exception(
                "Kafka publish failed for topic '%s'. "
                "The database operation will remain successful.",
                topic,
            )

            # Reset the producer so the next request gets a fresh client.
            self._reset_producer()

            return False

    def _reset_producer(self) -> None:
        if self._producer is not None:
            try:
                self._producer.close(timeout=2)
            except Exception:
                logger.exception("Error while closing Kafka producer")

            finally:
                self._producer = None

    def close(self) -> None:
        if self._producer is not None:
            try:
                self._producer.flush(timeout=5)
            except Exception:
                logger.exception("Kafka producer flush failed")

            try:
                self._producer.close(timeout=5)
            except Exception:
                logger.exception("Kafka producer close failed")

            finally:
                self._producer = None


kafka_producer = KafkaEventProducer()