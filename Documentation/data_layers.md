# Bronze and Silver Layer Design

## Bronze Layer

The Bronze layer is the raw ingestion layer.

The source CSV is read using PySpark with schema inference disabled.

All source columns are initially preserved as strings.

This approach protects the original source representation and prevents incorrect type inference from changing source values during ingestion.

### Bronze metadata

The following metadata is added:

| Column | Purpose |
|---|---|
| `source_file` | Identifies the source file |
| `ingested_at` | Records when the data was ingested |
| `run_id` | Identifies the pipeline execution |
| `raw_payload` | Preserves the original row as JSON |

The raw payload provides an additional audit trail if downstream transformations need to be investigated.

### Bronze write strategy

Bronze data is written in append mode.

This allows the raw landing layer to retain previously ingested data and supports traceability across ingestion runs.

Because Bronze uses append mode, rerunning the same source file without file-level duplicate detection would create duplicate records. The incremental-processing strategy therefore requires source-file tracking before ingestion.

## Silver Layer

The Silver layer is the cleaned and analytics-ready data layer.

The transformation performs:

1. Whitespace trimming
2. Data type conversion
3. Business-rule validation
4. Rejection of invalid records
5. Duplicate detection
6. Deduplication

### Type standardization

The following fields are converted from strings:

| Field | Silver type |
|---|---|
| `index` | long |
| `duration` | double |
| `days_left` | integer |
| `price` | double |

Categorical and descriptive fields remain strings.

### Invalid records

Records that fail validation are assigned a `dq_reason`.

Examples include:

- Missing airline
- Missing flight
- Invalid duration
- Negative `days_left`
- Negative price
- Invalid travel class
- Invalid stops value

Rejected records are written separately so that invalid data is not silently discarded.

### Duplicate handling

Duplicates are identified using the flight's business attributes.

The most recently ingested record is retained.

This reduces the risk of duplicate business records reaching the analytical layer.

## Current processing result

For the current source file:

```text
Bronze records:    300,153
Silver records:    300,153
Rejected records:        0