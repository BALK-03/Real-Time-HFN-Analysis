import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, ArrayType
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.logger import get_logger
from src.utils.get_config import get_config
from src.cassandra.cassandra_manager import CassandraManager

logger = get_logger(__name__)

KAFKA_CONFIG = "./config/kafka_config.yml"
BERT_CONFIG = "./config/bert_config.yml"
CASSANDRA_CONFIG = "./config/cassandra_config.yml"


KAFKA_BROKER = get_config(config_file=KAFKA_CONFIG, target_config="BROKER")
TOPIC = get_config(config_file=KAFKA_CONFIG, target_config="TOPIC")

BERT_URL = get_config(config_file=BERT_CONFIG, target_config="URL")

CASSANDRA_HOST = get_config(config_file=CASSANDRA_CONFIG, target_config="HOST")
CASSANDRA_KEYSPACE = get_config(config_file=CASSANDRA_CONFIG, target_config="KEYSPACE")


cassandra = CassandraManager(CASSANDRA_HOST, CASSANDRA_KEYSPACE)
cassandra.connect()

def bert_predict(text: str, URL: str = "http://bert:8000/predict") -> str:
    data = {"text": text}
    response = requests.post(url=URL, json=data)
    response.raise_for_status()
    return response.json()["prediction"]

def process_batch(df, batch_id):
    try:
        rows = df.collect()
        for row in rows:
            post_text = row.post_body
            subreddit = row.subreddit
            if post_text:
                try:
                    post_pred = bert_predict(post_text, URL=BERT_URL)
                    cassandra.insert_prediction(post_text, post_pred, subreddit)
                except Exception as e:
                    logger.warning(f"Error processing post text: {e}")

            if row.comments:
                for comment in row.comments:
                    if comment:
                        try:
                            comment_pred = bert_predict(comment, URL=BERT_URL)
                            cassandra.insert_prediction(comment, comment_pred, subreddit)
                        except Exception as e:
                            logger.warning(f"Error processing comment: {e}")
                            continue
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {e}")

def start_spark():
    """Start Spark Streaming to consume data from Kafka."""
    spark = SparkSession.builder \
        .appName("KafkaSparkStreaming") \
        .master("spark://spark-master:7077") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1") \
        .getOrCreate()

    schema = StructType() \
        .add("post_id", StringType()) \
        .add("post_title", StringType()) \
        .add("post_url", StringType()) \
        .add("created_utc", StringType()) \
        .add("post_body", StringType()) \
        .add("subreddit", StringType()) \
        .add("comments", ArrayType(StringType()))

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
                .select(from_json(col("json_str"), schema).alias("data")) \
                .select("data.*")

    query = json_df.writeStream \
        .foreachBatch(process_batch) \
        .start()

    logger.info("Spark streaming query started. Waiting for data from Kafka...")
    query.awaitTermination()



if __name__ == "__main__":
    start_spark()
    cassandra.close()