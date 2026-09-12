# Data Quality Strategy

## Objective

The pipeline validates flight records before they are made available for analytical use.

Data quality checks are performed primarily during the Silver transformation, with additional automated tests in dbt.

## Silver-layer validation rules

The following validation rules are applied:

| Rule | Action |
|---|---|
| Airline is missing | Reject record |
| Flight is missing | Reject record |
| Source city is missing | Reject record |
| Destination city is missing | Reject record |
| Travel class is missing | Reject record |
| Duration is missing or invalid | Reject record |
| Duration is less than or equal to 0 | Reject record |
| `days_left` is missing or invalid | Reject record |
| `days_left` is negative | Reject record |
| Price is missing or invalid | Reject record |
| Price is negative | Reject record |
| Travel class is not Economy or Business | Reject record |
| Stops contains an unexpected value | Reject record |

Rejected records are written to a separate Silver rejected-records location with the reason for rejection.

## Duplicate handling

Duplicate flight records are identified using the flight business attributes.

When duplicates are found, the most recently ingested record is retained using `ingested_at`.

This prevents duplicate records from being propagated into analytical models.

## dbt automated tests

The dbt staging model has automated tests covering:

- Required fields are not null
- `flight_record_id` is unique
- `travel_class` contains only accepted values

## Current dataset results

The source dataset contains:

- 300,153 records received
- 300,153 records written to Silver
- 0 rejected records
- 0 duplicate records identified during the current Silver processing
- 10 dbt tests executed
- 10 dbt tests passed
- 0 dbt test failures

## Why zero rejected records is acceptable

A data-quality process does not need to reject records in every run.

The important requirement is that invalid records would be detected and handled if they appeared.

The current source data satisfies the validation rules, so no records were rejected during this run.

## Reconciliation

The pipeline compares record counts between stages.

For the current dataset:

```text
Source records:    300,153
Bronze records:    300,153
Silver valid:      300,153
Silver rejected:         0