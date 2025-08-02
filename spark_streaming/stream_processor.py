# spark_streaming/stream_processor.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType

# 1. Create Spark session
spark = SparkSession.builder \
    .appName("WeatherKafkaConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Define schema for the weather 'main' object
weather_schema = StructType() \
    .add("temp", DoubleType()) \
    .add("feels_like", DoubleType()) \
    .add("temp_min", DoubleType()) \
    .add("temp_max", DoubleType()) \
    .add("pressure", IntegerType()) \
    .add("humidity", IntegerType())

# 3. Read from Kafka topic
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "weather_raw") \
    .load()

# 4. Convert binary 'value' column to string, parse JSON
json_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), StructType().add("main", weather_schema)).alias("data")) \
    .select("data.main.*")

# 5. Filter example: temp > 35°C
filtered_df = json_df.filter(col("temp") > 10)

# 6. Write to console
query = filtered_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
