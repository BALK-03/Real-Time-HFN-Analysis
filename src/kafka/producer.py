import os, sys
import json
from typing import Dict, Tuple, Optional
from kafka import KafkaProducer
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.logger import get_logger


class Producer:
    def __init__(self, bootstrap_servers: str = 'kafka:19092', api_version: Tuple = (2, 6, 0)):
        self.logger = get_logger(__name__)
        self.bootstrap_servers = bootstrap_servers
        self.api_version = api_version
        self.kafka_producer = None
        # Kafka producer configuration
        self.setup_producer()

    def setup_producer(self):
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                api_version=self.api_version,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f"Kafka connection error: {e}")
            raise

    def publish_to_kafka(self, topic: str, data: Dict) -> bool:
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

    def close(self):
        """
        close Kafka producer.
        """
        try:
            self.kafka_producer.flush()
            self.kafka_producer.close()
        except AttributeError as e:
            self.logger.error(f"Error while closing producer: {e}")



if __name__ == "__main__":
    import os, sys
    from collections import defaultdict
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.reddit.reddit_scraper import RedditScraper
    from src.utils.get_config import get_config

    logger = get_logger(__name__ + "/file_main")
    BROKER = get_config('./config/kafka_config.yml', 'BROKER')
    TOPIC = get_config('./config/kafka_config.yml', 'TOPIC')
    API_VERSION = tuple(get_config('./config/kafka_config.yml', 'API_VERSION'))

    scraper = RedditScraper()

    subreddits = scraper.subreddits
    reddit_client = scraper.reddit_client
    producer = Producer(
        bootstrap_servers=BROKER,
        api_version=API_VERSION
        )
    
    last_post_info = defaultdict(lambda: None)
    idx = 0
    while True:
        try:
            subreddit_name = subreddits[idx]
            subreddit = reddit_client.subreddit(subreddit_name)

            post_data, after_post = scraper.fetch_posts(
                subreddit = subreddit,
                num_posts = 1,
                last_post = last_post_info[subreddit]
            )

            if not post_data:
                idx = (idx +1) % len(subreddits)
                continue
            else:                
                post = reddit_client.submission(post_data["post_id"])

                comments_data = scraper.fetch_comments(
                    post = post,
                    num_comments = 20
                )
                
                post_data["subreddit"] = subreddit_name                
                post_data["comments"] = comments_data

                is_produced = producer.publish_to_kafka(data=post_data, topic=TOPIC)
                if not is_produced:
                    logger.warning(f"Unpublished data, post: {post}. Check kafka setup!")

                last_post_info[subreddit] = after_post
                idx = (idx +1) % len(subreddits)
        except Exception as e:
            logger.warning(f"Problem occured while fetching or publishing data from subreddit {subreddit}: {e}")
            idx = (idx +1) % len(subreddits)
            continue