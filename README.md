# Real-Time Weather Streaming Pipeline

This project demonstrates a real-time data engineering pipeline using:

- **OpenWeather API** (data source)
- **Kafka** (message broker)
- **Spark Structured Streaming** (real-time ETL)
- (Optional) **S3/MinIO** (Data Lake) and **Redshift/Postgres** (Warehouse)

It mimics production pipelines: **collect → stream → process → persist → serve**.

---

## 📂 Project Structure

```
.
├─ docker-compose.yml
├─ producer/
│  └─ weather_producer.py
└─ spark_streaming/
   └─ stream_processor.py
```

---

## ⚙️ Prerequisites

- Python 3.10+ (with `venv`)
- Java 11+ (Spark requires JDK; 17/21 work fine)
- Docker & Docker Compose
- OpenWeather API key (free account works)

---

## 🔧 Setup

### 1) Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install requests kafka-python pyspark
```

### 2) Start Kafka & Zookeeper
```bash
docker compose up -d
docker compose ps
```

The `docker-compose.yml` runs:
- **Zookeeper** on `2181`
- **Kafka** on `9092`

### 3) Create the Kafka topic
```bash
docker exec -it kafka bash
/opt/kafka/bin/kafka-topics.sh \
  --create --topic weather_raw \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 --partitions 1
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

---

## 🛰️ Producer (Python → Kafka)

`producer/weather_producer.py` polls OpenWeather every 10s and sends JSON to Kafka.

Run it:
```bash
cd producer
python weather_producer.py
```

Sample output:
```
Sending: {'temp': 23.79, 'feels_like': 24.37, 'temp_min': 22.87, 'temp_max': 24.41, 'pressure': 1021, 'humidity': 82}
```

---

## 🔄 Spark Consumer (Kafka → Structured Streaming)

`spark_streaming/stream_processor.py` reads Kafka events, parses JSON, filters, and prints to console.

From the project root:
```bash
SPARK_VERSION=$(python -c "import pyspark; print(pyspark.__version__)")

spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:${SPARK_VERSION} \
  spark_streaming/stream_processor.py
```

Example console output:
```
-------------------------------------------
Batch: 1
-------------------------------------------
+-----+----------+--------+--------+--------+--------+
| temp|feels_like|temp_min|temp_max|pressure|humidity|
+-----+----------+--------+--------+--------+--------+
|23.79|     24.37|   22.87|   24.41|    1021|      82|
+-----+----------+--------+--------+--------+--------+
```

---

## 🛑 Stopping the Stream

- **Ctrl + C** in the Spark terminal (shows Py4J errors, harmless).
- To stop cleanly in code:
  ```python
  try:
      query.awaitTermination()
  except KeyboardInterrupt:
      query.stop()
      spark.stop()
  ```
- For testing: `query.awaitTermination(60)` runs for 60 seconds then exits.

---

## 📦 Extensions

### A) Persist to Data Lake (S3 or MinIO)
```python
(filtered_df.writeStream
   .format("parquet")
   .option("path", "s3a://weather-bucket/raw/")
   .option("checkpointLocation", "s3a://weather-bucket/checkpoints/")
   .outputMode("append")
   .start())
```

- Use AWS creds for S3
- Or run MinIO locally (`docker run minio/minio`), then configure endpoint

### B) Load into Warehouse
- **JDBC** sink (Postgres, Snowflake, Redshift)
- **Redshift COPY** from S3 parquet files (preferred for production)

---

## 📝 Notes

- OpenWeather “current weather” updates every ~10–60 minutes. Polling every 10s will often produce duplicate values.
- Use `forecast` or `onecall` endpoints for more frequent/different data.
- Always use **checkpoints** when writing streams → ensures recovery & exactly-once semantics.

---

## ✅ Skills Practiced

- Kafka setup & usage
- Python producer (requests + kafka-python)
- Spark Structured Streaming (Kafka source, JSON parsing, transformations)
- Real-time ETL design
- Cloud integration (S3/MinIO, Redshift/Snowflake)
