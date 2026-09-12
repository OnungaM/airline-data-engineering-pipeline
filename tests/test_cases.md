# Data Quality Test Cases

## Purpose

This document describes the key data-quality scenarios that the pipeline is designed to detect and handle.

The actual automated data-quality tests are implemented in the dbt project under:

```text
airline_dbt/models/staging/schema.yml
```

## Test Cases

| Test case                           | Expected result                                   |
| ----------------------------------- | ------------------------------------------------- |
| Missing airline                     | Record rejected                                   |
| Missing flight number               | Record rejected                                   |
| Missing source city                 | Record rejected                                   |
| Missing destination city            | Record rejected                                   |
| Invalid duration                    | Record rejected                                   |
| Duration less than or equal to zero | Record rejected                                   |
| Negative `days_left`                | Record rejected                                   |
| Invalid price                       | Record rejected                                   |
| Negative price                      | Record rejected                                   |
| Invalid travel class                | Record rejected                                   |
| Invalid stops value                 | Record rejected                                   |
| Duplicate flight record             | Duplicate removed and most recent record retained |
| Null required staging field         | dbt `not_null` test fails                         |
| Duplicate `flight_record_id`        | dbt `unique` test fails                           |
| Invalid travel class in staging     | dbt `accepted_values` test fails                  |

## Current Test Results

For the provided dataset:

* 300,153 records were received
* 300,153 records reached Silver
* 0 records were rejected
* 10 dbt data-quality tests passed
* 0 dbt data-quality tests failed

The complete dbt pipeline was also validated using:

```powershell
dbt build
```

Result:

```text
15 PASS
0 WARN
0 ERROR
0 SKIP
```

## Test Philosophy

The pipeline separates data-quality validation from analytical modeling.

Invalid records should be identified before they reach the Gold analytical layer.

This makes data-quality failures visible and prevents known-invalid records from silently becoming part of business reporting.
