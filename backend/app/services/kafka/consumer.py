import json
import logging
from typing import Any

from kafka import KafkaConsumer


logger = logging.getLogger(__name__)


class KafkaEventConsumer:
    def __init__(
        self,
        topics: list[str],
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "riskbridge-risk-consumer",
    ):
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self._consumer = None

    def _get_consumer(self) -> KafkaConsumer:
        if self._consumer is None:
            self._consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda value: json.loads(
                    value.decode("utf-8")
                ),
            )

        return self._consumer

    def consume(self):
        consumer = self._get_consumer()

        logger.info(
            "Kafka consumer started: topics=%s group_id=%s",
            self.topics,
            self.group_id,
        )

        for message in consumer:
            event: dict[str, Any] = message.value

            logger.info(
                "Kafka event received: topic=%s partition=%s offset=%s",
                message.topic,
                message.partition,
                message.offset,
            )

            yield event

    def close(self) -> None:
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None