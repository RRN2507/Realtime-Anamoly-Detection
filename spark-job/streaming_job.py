import os
# import torch
# import torch.nn as nn
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, pandas_udf, struct, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType, TimestampType
import pandas as pd
import numpy as np

# Global model instance for UDF
model = None

@pandas_udf(DoubleType())
def detect_anomaly_udf(amounts: pd.Series) -> pd.Series:
    # Simple threshold-based anomaly detection for this demo
    scores = amounts.apply(lambda x: 1.0 if x > 1000 else 0.0)
    return scores

def main():
    spark = SparkSession.builder \
        .appName("RealTimeAnomalyDetection") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    # Define schema
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("merchant_id", StringType(), True),
        StructField("timestamp", StringType(), True)
    ])

    # Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "financial_transactions") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON
    parsed_df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("timestamp", to_timestamp(col("timestamp")))

    # Apply Anomaly Detection UDF
    enriched_df = parsed_df.withColumn("anomaly_score", detect_anomaly_udf(col("amount"))) \
        .withColumn("is_anomaly", col("anomaly_score") > 0.5)

    # Write to TimescaleDB via JDBC
    def write_to_timescale(batch_df, batch_id):
        try:
            record_count = batch_df.count()
            print(f"DEBUG: Processing batch {batch_id} with {record_count} records")
            
            if record_count > 0:
                batch_df.write \
                    .format("jdbc") \
                    .option("url", "jdbc:postgresql://timescaledb:5432/pipeline_db") \
                    .option("dbtable", "transactions") \
                    .option("user", "postgres") \
                    .option("password", "postgres") \
                    .option("driver", "org.postgresql.Driver") \
                    .mode("append") \
                    .save()
                print(f"Batch {batch_id} successfully persisted to DB")
        except Exception as e:
            print(f"ERROR: Failed to process batch {batch_id}: {e}")

    query = enriched_df.writeStream \
        .foreachBatch(write_to_timescale) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
