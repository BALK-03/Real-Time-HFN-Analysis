import os, sys
import json
import logging
from typing import Dict, Optional
from kafka import KafkaProducer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.logger import get_logger



class Producer:
    def __init__(self, bootstrap_servers: Optional[str] = 'localhost:9092'):
        self.logger = get_logger(__name__)
        self.bootstrap_servers = bootstrap_servers
        self.kafka_producer = None
        # Kafka producer configuration
        self.setup_producer()

    def setup_producer(self) -> None:
        """
        Set up Kafka producer.
        """
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f"Kafka connection error: {e}")
            raise

    def publish_to_kafka(self, topic: str, data: Dict) -> bool:
        """
        Publish data to specified Kafka topic.
        
        :param topic: Kafka topic to publish to
        :param data: Data to publish
        """
        if not self.kafka_producer:
            self.logger.error("Kafka producer not initialized!")
            return False   
        try:
            future = self.kafka_producer.send(topic=topic, value=data)
            record_metadata = future.get(timeout=10)    # Wait 10s for acknowledgement
            self.logger.info(f"Published to {record_metadata.topic} partition {record_metadata.partition}")
            return True
        except Exception as e:
            self.logger.error(f"Kafka publish error: {e}")
            return False

    def close(self) -> None:
        """
        close Kafka producer.
        """
        try:
            self.kafka_producer.flush()
            self.kafka_producer.close()
        except AttributeError as e:
            self.logger.error(f"Error while closing producer: {e}")