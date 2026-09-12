from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    trim,
    lower,
    when,
    lit,
    current_timestamp,
    row_number
)
from pyspark.sql.window import Window


# ---------------------------------------------------------
# 1. Start Spark
# ---------------------------------------------------------

spark = (
    SparkSession.builder
    .appName("airline-silver-transformation")
    .getOrCreate()
)


# ---------------------------------------------------------
# 2. Define paths
# ---------------------------------------------------------

bronze_path = "data/bronze/flights"
silver_path = "data/silver/flights"
rejected_path = "data/silver/rejected_flights"


print("Starting Silver transformation")


# ---------------------------------------------------------
# 3. Read Bronze data
# ---------------------------------------------------------

bronze = spark.read.parquet(bronze_path)

print(f"Bronze records received: {bronze.count()}")


# ---------------------------------------------------------
# 4. Standardize text columns
# ---------------------------------------------------------

cleaned = (
    bronze
    .withColumn("airline", trim(col("airline")))
    .withColumn("flight", trim(col("flight")))
    .withColumn("source_city", trim(col("source_city")))
    .withColumn("departure_time", trim(col("departure_time")))
    .withColumn("stops", trim(col("stops")))
    .withColumn("arrival_time", trim(col("arrival_time")))
    .withColumn("destination_city", trim(col("destination_city")))
    .withColumn("class", trim(col("class")))
)


# ---------------------------------------------------------
# 5. Convert columns to correct data types
# ---------------------------------------------------------

typed = (
    cleaned
    .withColumn("index", col("index").cast("long"))
    .withColumn("duration", col("duration").cast("double"))
    .withColumn("days_left", col("days_left").cast("integer"))
    .withColumn("price", col("price").cast("double"))
)


# ---------------------------------------------------------
# 6. Define data-quality rules
# ---------------------------------------------------------

validated = (
    typed
    .withColumn(
        "dq_reason",
        when(col("airline").isNull(), "Missing airline")
        .when(col("flight").isNull(), "Missing flight")
        .when(col("source_city").isNull(), "Missing source city")
        .when(col("destination_city").isNull(), "Missing destination city")
        .when(col("class").isNull(), "Missing class")
        .when(col("duration").isNull(), "Invalid duration")
        .when(col("duration") <= 0, "Duration must be greater than 0")
        .when(col("days_left").isNull(), "Invalid days_left")
        .when(col("days_left") < 0, "days_left cannot be negative")
        .when(col("price").isNull(), "Invalid price")
        .when(col("price") < 0, "Price cannot be negative")
        .when(
            ~col("class").isin("Economy", "Business"),
            "Invalid class"
        )
        .when(
            ~col("stops").isin("zero", "one", "two_or_more"),
            "Invalid stops"
        )
        .otherwise(None)
    )
)


# ---------------------------------------------------------
# 7. Separate valid and rejected records
# ---------------------------------------------------------

valid_records = (
    validated
    .filter(col("dq_reason").isNull())
    .drop("dq_reason")
)

rejected_records = (
    validated
    .filter(col("dq_reason").isNotNull())
)


# ---------------------------------------------------------
# 8. Remove duplicate records
# ---------------------------------------------------------

duplicate_window = Window.partitionBy(
    "airline",
    "flight",
    "source_city",
    "departure_time",
    "stops",
    "arrival_time",
    "destination_city",
    "class",
    "duration",
    "days_left",
    "price"
).orderBy(col("ingested_at").desc())


deduplicated = (
    valid_records
    .withColumn(
        "duplicate_number",
        row_number().over(duplicate_window)
    )
)


silver_flights = (
    deduplicated
    .filter(col("duplicate_number") == 1)
    .drop("duplicate_number")
)


# ---------------------------------------------------------
# 9. Write rejected records
# ---------------------------------------------------------

if rejected_records.count() > 0:

    (
        rejected_records
        .withColumn("rejected_at", current_timestamp())
        .write
        .mode("append")
        .parquet(rejected_path)
    )

    print(
        f"Rejected records written: "
        f"{rejected_records.count()}"
    )

else:

    print("No rejected records found.")


# ---------------------------------------------------------
# 10. Write Silver records
# ---------------------------------------------------------

(
    silver_flights
    .write
    .mode("overwrite")
    .parquet(silver_path)
)


# ---------------------------------------------------------
# 11. Print data-quality summary
# ---------------------------------------------------------

bronze_count = bronze.count()
valid_count = silver_flights.count()
rejected_count = rejected_records.count()

print("\nSilver transformation completed.")
print(f"Bronze records:   {bronze_count}")
print(f"Silver records:   {valid_count}")
print(f"Rejected records: {rejected_count}")


spark.stop()