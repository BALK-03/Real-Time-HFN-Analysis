from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, length
from pyspark.sql.types import StructType, StringType, ArrayType

# Using the Docker network alias for Kafka (i.e. service name "kafka")
KAFKA_BROKER = 'kafka:19092'
TOPIC = 'RedditData'

def start_spark():
    # Connect to Spark running in cluster mode (within Docker)
    spark = SparkSession.builder \
        .appName("KafkaSparkStreaming") \
        .master("spark://spark-master:7077") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1") \
        .getOrCreate()

    # Define the schema for our incoming JSON data
    schema = StructType() \
        .add("post_id", StringType()) \
        .add("post_title", StringType()) \
        .add("post_url", StringType()) \
        .add("created_utc", StringType()) \
        .add("post_body", StringType()) \
        .add("comments", ArrayType(StringType()))

    # Create a streaming DataFrame that reads from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    # Convert the binary 'value' column to string and parse JSON using the schema
    json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
                .select(from_json(col("json_str"), schema).alias("data")) \
                .select("data.*")

    # Perform a simple transformation: add a new column with the length of the post title
    processed_df = json_df.withColumn("title_length", length(col("post_title")))

    # Write the streaming output to the console so you can see the data
    query = processed_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    print("Spark streaming query started. Waiting for data from Kafka...")
    query.awaitTermination()

if __name__ == "__main__":
    start_spark()














# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col, from_json
# from pyspark.sql.types import StructType, StringType, ArrayType


# spark = SparkSession.builder \
#     .appName("RedditStreaming") \
#     .master("spark://localhost:7077") \
#     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1") \
#     .getOrCreate()

# df = spark \
#     .readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "kafka:9092") \
#     .option("subscribe", "RedditData") \
#     .option("startingOffsets", "latest") \
#     .load()

# schema = StructType() \
#     .add("post_id", StringType()) \
#     .add("post_title", StringType()) \
#     .add("post_url", StringType()) \
#     .add("created_utc", StringType()) \
#     .add("post_body", StringType()) \
#     .add("comments", ArrayType(StringType()))

# parsed_df = df.selectExpr("CAST(value AS STRING)") \
#     .select(from_json(col("value"), schema).alias("data")) \
#     .select("data.*")

# query = parsed_df.writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()

# query.awaitTermination()