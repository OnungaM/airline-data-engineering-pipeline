# Airline Flight Data Engineering Pipeline

## Project Overview

This project implements a reliable data engineering pipeline for airline flight and pricing data using a Medallion Architecture.

The pipeline transforms raw flight-pricing data into cleaned, validated, and analytics-ready datasets.

The project demonstrates:

- PySpark for data ingestion and transformation
- Bronze, Silver, and Gold data layers
- dbt for analytical transformations and testing
- Amazon Redshift warehouse design
- Data quality validation and rejected-record handling
- Incremental processing design
- Reconciliation and observability
- Business-focused analytical marts

## Architecture

```text
Raw CSV
   |
   v
+------------------+
| Bronze           |
| PySpark          |
| Raw + metadata   |
+------------------+
   |
   v
+------------------+
| Silver           |
| PySpark          |
| Clean + validate |
| Deduplicate      |
+------------------+
   |
   v
+------------------+
| dbt Staging      |
| stg_flights      |
+------------------+
   |
   +-------------------------+
   |                         |
   v                         v
+------------------+    +----------------------+
| dbt Intermediate |    | Gold Analytical      |
| int_flight_      |    | Marts                |
| metrics          |    |                      |
+------------------+    | Airline Performance  |
                        | Route Performance    |
                        | Pricing / Lead Time  |
                        +----------------------+
                                  |
                                  v
                        Amazon Redshift
                        (proposed target)






## Project Structure

```text
JUNIOR DATA ENGINEER/
├── README.md
│
├── architecture/
│   └── architecture.md
│
├── data/
│   ├── landing/
│   │   └── airlines_flights_data.csv
│   ├── bronze/
│   │   └── flights/
│   └── silver/
│       ├── flights/
│       └── rejected_flights/
│
├── Documentation/
│   ├── data_layers.md
│   ├── data_quality.md
│   ├── gold_layer.md
│   ├── incremental_strategy.md
│   └── monitoring.md
│
├── pyspark/
│   ├── bronze ingestion script
│   └── silver transformation script
│
├── airline_dbt/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── ...
│
├── redshift/
│   └── schema.sql
│
├── tests/
│
├── requirements.txt
│
└── ...



## Technologies

| Technology      | Purpose                               
| Python          -- Pipeline scripting                                             
| PySpark         -- Bronze ingestion and Silver transformation                     
| Parquet         -- Bronze and Silver storage format                               
| dbt             -- SQL transformations, analytical models, and data quality tests
| DuckDB          -- Local development and dbt validation                           
| Amazon Redshift -- Proposed production warehouse target                           
| SQL             -- Analytical transformations                                     
| Git             -- Versioncontrol                                                  

## Setup

### Prerequisites

The project requires:

* Python
* Java 17
* PySpark
* dbt Core
* dbt-duckdb
* Git

### PySpark on Windows

PySpark requires Java.

The project was developed using Java 17.

For local Windows execution, the Hadoop Windows native utilities are also configured for Spark compatibility.

Before running the PySpark scripts, configure the required environment variables:

```powershell
$env:JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

$env:HADOOP_HOME="C:\hadoop"

$env:Path="$env:HADOOP_HOME\bin;$env:Path"
```

### dbt

The dbt project is located in:

```text
airline_dbt/
```

DuckDB is used as the local development warehouse so that the transformations can be developed and tested without requiring an active Amazon Redshift cluster.

The intended production warehouse is Amazon Redshift.

### Install Python dependencies

From the project root:

```powershell
py -m pip install -r requirements.txt
```


## Pipeline Execution

The pipeline follows the Medallion Architecture:

```text
Landing → Bronze → Silver → dbt Staging → dbt Intermediate → Gold
```

### Step 1: Bronze ingestion

The PySpark Bronze process reads the raw CSV from:

```text
data/landing/airlines_flights_data.csv
```

It preserves the source values and adds ingestion metadata before writing Parquet files to:

```text
data/bronze/flights/
```

Run the Bronze ingestion script from the project root:

```powershell
py pyspark/bronze_ingest.py
```

### Step 2: Silver transformation

The Silver process reads the Bronze Parquet data and performs:

* Data type conversion
* Whitespace standardization
* Business-rule validation
* Invalid-record rejection
* Duplicate detection
* Deduplication

Valid records are written to:

```text
data/silver/flights/
```

Rejected records are written separately to:

```text
data/silver/rejected_flights/
```

Run the Silver transformation:

```powershell
py pyspark/silver_transform.py
```

### Step 3: Run dbt

Move into the dbt project:

```powershell
cd airline_dbt
```

Run all dbt models:

```powershell
dbt run
```

Run the automated data-quality tests:

```powershell
dbt test
```

The dbt project contains:

* Staging models
* Intermediate models
* Gold analytical marts

### Step 4: Validate the complete dbt pipeline

The complete dbt workflow can also be executed using:

```powershell
dbt build
```

This builds the models and executes the associated tests.

### Important execution note

The Bronze ingestion uses append mode to preserve ingestion history.

Therefore, the same source file should **not** be manually ingested repeatedly without the file-level duplicate detection described in the incremental processing design.

For the current take-home dataset, the initial Bronze load has already been completed successfully.





## Data Quality

Data quality checks are performed primarily in the Silver layer using PySpark, with additional automated tests implemented in dbt.

### Validation

The Silver transformation checks for:

* Missing required fields
* Invalid numeric values
* Duration less than or equal to zero
* Negative `days_left`
* Negative prices
* Invalid travel classes
* Unexpected stops values

Records that fail validation are not included in the clean Silver dataset.

Instead, rejected records are written to a separate location:

```text
data/silver/rejected_flights/
```

Each rejected record contains a `dq_reason` explaining why it failed validation.

### Duplicate handling

Duplicate flight records are identified using the flight's business attributes.

When duplicate records are encountered, the most recently ingested record is retained.

### dbt tests

The dbt staging model includes automated tests for:

* Required fields not being null
* Unique flight record identifiers
* Accepted travel-class values

The current dataset passed all implemented dbt tests:

```text
10 tests passed
0 tests failed
```

### Current data-quality results

For the current source dataset:

| Metric               |  Result |
| -------------------- | ------: |
| Source records       | 300,153 |
| Bronze records       | 300,153 |
| Silver valid records | 300,153 |
| Rejected records     |       0 |
| dbt tests passed     |      10 |
| dbt tests failed     |       0 |

The current dataset contains no records that violate the implemented validation rules.

A zero rejection count is still considered a successful data-quality result because the validation rules are designed to detect and isolate invalid records when they occur.



## Gold Analytical Layer

The Gold layer contains business-focused datasets created with dbt. These models are materialized as tables because they are intended for repeated analytical queries.

### 1. Airline Performance

**Model:** `mart_airline_performance`

**Grain:** One row per airline.

**Business question:**

> Which airlines have the most flights, and how do their prices and durations compare?

**Measures:**

* Total flights
* Average price
* Average flight duration
* Average days left
* Minimum price
* Maximum price

**Business value:**

This dataset allows analysts to compare airline activity, pricing, and typical flight duration.

---

### 2. Route Performance

**Model:** `mart_route_performance`

**Grain:** One row per source-city and destination-city combination.

**Business question:**

> Which routes have the most flights, and how do prices and durations differ between routes?

**Dimensions:**

* Source city
* Destination city

**Measures:**

* Total flights
* Average price
* Average flight duration
* Minimum price
* Maximum price

**Business value:**

This dataset supports route-level analysis and helps identify high-volume routes and differences in pricing and duration.

---

### 3. Pricing by Lead Time

**Model:** `mart_pricing_lead_time`

**Grain:** One row per number of days remaining before departure.

**Business question:**

> How does flight pricing vary depending on how many days remain before departure?

**Dimension:**

* Days left

**Measures:**

* Total flights
* Average price
* Minimum price
* Maximum price
* Average flight duration

**Business value:**

This dataset can be used to analyze pricing patterns based on booking lead time.

### Gold Model Summary

| Gold dataset         | Grain                       | Main business use        |
| -------------------- | --------------------------- | ------------------------ |
| Airline Performance  | One row per airline         | Compare airlines         |
| Route Performance    | One row per route           | Analyze routes           |
| Pricing by Lead Time | One row per days-left value | Analyze pricing patterns |



## Incremental Processing

The pipeline is designed to support daily flight-pricing files without unnecessarily rebuilding the entire dataset.

### New files

New source files are detected before ingestion and appended to the Bronze layer.

Bronze records contain:

* `source_file`
* `ingested_at`
* `run_id`
* `raw_payload`

This metadata provides traceability for each ingestion run.

### Rerunning the same file

A previously processed file should not be ingested again.

The production design uses file-level tracking, such as a file name combined with a file hash or source version identifier.

If the file has already been successfully processed, it is skipped.

This prevents accidental double-counting during pipeline retries or manual reruns.

### Changed files

If a previously received file changes, it is treated as a new file version.

The changed version is identified using file-level metadata such as a file hash.

Affected records are then reprocessed so that stale data does not remain in the analytical layer.

### Duplicate records

Record-level duplicates are handled in the Silver layer using the flight's business attributes.

The most recently ingested record is retained.

### Late-arriving data

Late-arriving files are accepted into Bronze and processed through the same validation and deduplication logic.

Affected analytical results are refreshed so that the late-arriving records are included.

### Failure and retry

Bronze acts as the durable ingestion layer.

If a downstream Silver or dbt transformation fails, processing can be retried from Bronze without downloading the source file again.

This reduces the risk of duplicate ingestion and makes pipeline recovery safer.

### Initial load versus daily processing

The current project performs an initial full load of the provided dataset.

For production, subsequent daily runs should process only newly detected or changed files rather than rebuilding the complete dataset unnecessarily.

### Current implementation note

The current take-home implementation demonstrates the incremental processing **design**, while the provided Silver transformation currently writes the Silver dataset using overwrite mode.

A production implementation would replace this batch-style Silver write with an incremental merge/upsert strategy based on the appropriate business key and file/version metadata.

The incremental design is documented in:

```text
Documentation/incremental_strategy.md
```





## Monitoring and Observability

The production pipeline should provide visibility into ingestion, transformation, data quality, and reconciliation.

The monitoring design tracks:

* Pipeline start and completion
* Pipeline failures
* Files received and processed
* Files skipped or rejected
* Bronze and Silver record counts
* Duplicate records
* Data-quality rejection rates
* dbt test failures
* Pipeline and model runtime
* Source-to-target reconciliation

### Alerts

The production design should alert when important conditions occur, including:

* Pipeline failure
* Missing source files
* Unexpected schema changes
* High data-quality rejection rates
* Duplicate spikes
* dbt test failures
* Source-to-target count mismatches
* Significant increases in processing time

The detailed monitoring design is documented in:

```text
Documentation/monitoring.md
```

Actual cloud monitoring and alerting infrastructure is outside the scope of this take-home project.







## Amazon Redshift

Amazon Redshift is the proposed production data warehouse for the Gold analytical layer.

The project includes the target warehouse DDL in:

```text
redshift/schema.sql
```

### Target analytical tables

The proposed Redshift schema contains three Gold tables:

| Table                      | Grain                                |
| -------------------------- | ------------------------------------ |
| `gold_airline_performance` | One row per airline                  |
| `gold_route_performance`   | One row per source/destination route |
| `gold_pricing_lead_time`   | One row per days-left value          |

### Design decisions

The Redshift tables use:

* Appropriate `varchar` types for descriptive fields
* `bigint` for record counts
* `decimal` types for monetary and calculated numeric values
* `NOT NULL` constraints for required dimensions and measures
* `DISTSTYLE AUTO` to allow Redshift to choose an appropriate distribution strategy
* Sort keys aligned with common analytical filtering and grouping patterns

### Distribution and sorting

`DISTSTYLE AUTO` is used because the dataset and workload are relatively small for this take-home project.

Sort keys are defined according to the analytical grain:

* Airline performance → `airline`
* Route performance → `source_city, destination_city`
* Pricing by lead time → `days_left`

These choices provide a reasonable starting point for a production warehouse while avoiding premature optimization.

### Production deployment

An actual Amazon Redshift cluster is not required for this take-home project.

The dbt transformations are validated locally using DuckDB, while `redshift/schema.sql` documents the intended production warehouse structure.

This separation allows the transformation logic to be tested locally while still demonstrating how the analytical data would be stored in Redshift.



## Assumptions and Limitations

### Assumptions

The following assumptions were made during implementation:

* The provided CSV represents the initial source dataset.
* `index` is treated as the source record identifier.
* Flight business attributes are used to identify duplicate records.
* `Economy` and `Business` are the expected travel-class values.
* `zero`, `one`, and `two_or_more` are the expected stops values.
* `duration` represents flight duration in hours.
* `days_left` represents the number of days remaining before departure.
* `price` represents the flight ticket price.
* DuckDB is used for local dbt development and validation.
* Amazon Redshift is the intended production warehouse.

### Limitations

This take-home implementation has several intentional limitations:

1. **No live Redshift deployment**

   The Redshift schema is provided as DDL, but no live Amazon Redshift cluster is required.

2. **Local dbt execution**

   dbt transformations are validated locally using DuckDB rather than a cloud warehouse.

3. **Incremental processing design**

   The project documents a production incremental-processing strategy, but the current Silver implementation uses overwrite mode for the initial batch processing.

4. **No production scheduler**

   Scheduling and orchestration are described conceptually but are not deployed.

5. **No external monitoring platform**

   Monitoring and alerting are documented as a production design but are not deployed.

6. **Single provided source file**

   The current dataset represents the initial project load. Daily file-arrival scenarios are addressed through the documented incremental design.

These limitations were kept intentional to focus the implementation on data engineering fundamentals, correctness, data quality, analytical modeling, and clear engineering decisions.






## Validation Results

The complete dbt pipeline was validated successfully using `dbt build`.

The final validation produced:

```text
Models:       5
Data tests:   10
Total tasks:  15

PASS:         15
WARN:          0
ERROR:        0
SKIP:          0
```

The five dbt models were successfully built:

* `stg_flights`
* `int_flight_metrics`
* `mart_airline_performance`
* `mart_pricing_lead_time`
* `mart_route_performance`

All ten configured data-quality tests passed.

The initial PySpark processing also successfully produced:

```text
Source records:    300,153
Bronze records:    300,153
Silver records:    300,153
Rejected records:        0
```

This demonstrates that the current dataset successfully passed the implemented ingestion, transformation, data-quality, and analytical modeling stages.
