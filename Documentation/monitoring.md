# Monitoring and Observability

## Objective

The production pipeline should provide enough visibility to detect ingestion failures, data-quality problems, unexpected volume changes, and downstream transformation failures.

Actual monitoring infrastructure is outside the scope of this take-home project.

## Pipeline Events

The following events should be recorded for every pipeline run:

* Pipeline start
* Pipeline completion
* Pipeline failure
* Source file detected
* Source file processed
* Source file skipped
* Source file rejected
* Silver transformation completed
* dbt transformation completed
* dbt test completed

## Key Metrics

### Ingestion Metrics

* Number of files received
* Number of files processed
* Number of files skipped
* Number of files rejected
* Bronze record count
* Ingestion duration

### Data-Quality Metrics

* Number of valid Silver records
* Number of rejected records
* Number of duplicate records
* Rejection rate
* Number of dbt test failures

### Reconciliation Metrics

Record counts should be compared between pipeline stages.

Example:

```text
Source → Bronze → Silver → Gold
```

Unexpected differences should be investigated.

For example, if 300,000 records enter Bronze but only 250,000 valid records reach Silver, the 50,000-record difference should be explainable by validation or deduplication.

### Performance Metrics

The following should be monitored:

* Pipeline runtime
* Spark processing duration
* dbt model runtime
* Number of records processed per run

## Alerts

Alerts should be triggered for conditions such as:

| Condition                    | Example response                      |
| ---------------------------- | ------------------------------------- |
| Pipeline failure             | Alert engineering team                |
| Source file missing          | Alert ingestion owner                 |
| Unexpected schema change     | Stop or quarantine ingestion          |
| High rejection rate          | Investigate source quality            |
| Duplicate spike              | Investigate source or ingestion issue |
| dbt test failure             | Prevent downstream release            |
| Source-target count mismatch | Investigate reconciliation            |
| Significant runtime increase | Investigate performance               |

## Operational Approach

The pipeline should produce structured run metadata that can be stored in a monitoring table or observability system.

A production run record could contain:

```text
run_id
pipeline_name
start_time
end_time
status
files_received
files_processed
files_skipped
bronze_count
silver_valid_count
silver_rejected_count
duplicate_count
dbt_test_failures
error_message
```

This provides an audit trail for investigating failed or unexpected pipeline runs.

## Current Project Scope

The take-home project demonstrates the monitoring design but does not deploy an external monitoring or alerting platform.

The design can later be implemented using cloud-native logging, metrics, scheduling, and alerting services.
