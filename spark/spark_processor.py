from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, pandas_udf
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType
import pandas as pd
import joblib
import os

# Define schema for the incoming JSON from Kafka
schema = StructType([
    StructField("user_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("location", StringType()),
    StructField("timestamp", StringType())
])

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("RealTimeAnomalyDetection") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.2") \
    .getOrCreate()

# Model path inside the container (mounted volume)
model_path = "/opt/spark/work-dir/spark/isolation_forest_model.joblib"

# Load the model and broadcast it to executors
# In a real Spark cluster, you'd distribute the model file to all nodes
# Here, the volume mount makes it available everywhere
model = joblib.load(model_path)
sc = spark.sparkContext
broadcast_model = sc.broadcast(model)

# Define Pandas UDF for anomaly scoring
@pandas_udf(DoubleType())
def predict_anomaly_score(amounts: pd.Series) -> pd.Series:
    clf = broadcast_model.value
    X = amounts.values.reshape(-1, 1)
    # IsolationForest.decision_function returns the anomaly score
    scores = clf.decision_function(X)
    return pd.Series(scores)

# Define Pandas UDF for anomaly prediction (True/False)
@pandas_udf(BooleanType())
def is_anomaly_udf(amounts: pd.Series) -> pd.Series:
    clf = broadcast_model.value
    X = amounts.values.reshape(-1, 1)
    preds = clf.predict(X)
    return pd.Series(preds == -1)

# Read streaming data from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "transactions") \
    .option("startingOffsets", "latest") \
    .load()

# Parse the JSON value column
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Apply the anomaly detection UDFs
scored_df = parsed_df.withColumn("anomaly_score", predict_anomaly_score(col("amount"))) \
    .withColumn("is_anomaly", is_anomaly_udf(col("amount")))

# Write the results to PostgreSQL (TimescaleDB)
def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://timescaledb:5432/anomaly_db") \
        .option("dbtable", "transactions") \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

# Start the streaming query
query = scored_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("update") \
    .start()

print("Spark Streaming Processor started. Listening for transactions...")
query.awaitTermination()
