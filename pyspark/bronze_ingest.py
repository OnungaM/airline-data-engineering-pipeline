from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    current_timestamp,
    input_file_name,
    lit,
    to_json,
    struct
)
from datetime import datetime
import uuid


# ---------------------------------------------------------
# 1. Start Spark
# ---------------------------------------------------------

spark = (
    SparkSession.builder
    .appName("airline-bronze-ingestion")
    .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    .getOrCreate()
)

# ---------------------------------------------------------
# 2. Define paths
# ---------------------------------------------------------

input_path = "data/landing/airlines_flights_data.csv"

bronze_path = "data/bronze/flights"


# ---------------------------------------------------------
# 3. Create a unique ID for this pipeline run
# ---------------------------------------------------------

run_id = str(uuid.uuid4())

print("Starting Bronze ingestion")
print(f"Run ID: {run_id}")
print(f"Input file: {input_path}")


# ---------------------------------------------------------
# 4. Read the raw CSV
# ---------------------------------------------------------

flights = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .csv(input_path)
)


# ---------------------------------------------------------
# 5. Add Bronze metadata
# ---------------------------------------------------------

bronze_flights = (
    flights
    .withColumn("source_file", input_file_name())
    .withColumn("ingested_at", current_timestamp())
    .withColumn("run_id", lit(run_id))
    .withColumn(
        "raw_payload",
        to_json(struct(*flights.columns))
    )
)


# ---------------------------------------------------------
# 6. Show what we received
# ---------------------------------------------------------

print("\nBronze data preview:")

bronze_flights.show(5, truncate=False)

print("\nNumber of records received:")
print(bronze_flights.count())


# ---------------------------------------------------------
# 7. Save Bronze data
# ---------------------------------------------------------

(
    bronze_flights.write
    .mode("append")
    .parquet(bronze_path)
)



print("\nBronze ingestion completed successfully.")
print(f"Bronze location: {bronze_path}")


# ---------------------------------------------------------
# 8. Stop Spark
# ---------------------------------------------------------

spark.stop()