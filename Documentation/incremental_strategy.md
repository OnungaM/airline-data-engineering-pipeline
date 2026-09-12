# Incremental Processing Strategy

## Objective

The pipeline is designed to receive new flight-pricing files daily while avoiding duplicate processing and unnecessary full rebuilds.

The incremental design uses the Bronze layer as the durable ingestion layer and tracks file-level and record-level metadata.

## 1. New files

Each newly received source file is ingested into Bronze using append mode.

Bronze records include:

- `source_file`
- `ingested_at`
- `run_id`
- `raw_payload`

These fields provide traceability for each ingestion run.

## 2. Rerun of the same file

A rerun should not create another copy of the same source file.

Before processing a file, the pipeline checks whether its `source_file` has already been successfully processed.

If the file has already been processed, the pipeline skips it unless the file is identified as a changed version.

This prevents accidental double-counting caused by pipeline retries or manual reruns.

## 3. Duplicate records

Record-level duplicates are removed in the Silver layer.

The duplicate check uses the flight business attributes, including:

- airline
- flight
- source city
- departure time
- stops
- arrival time
- destination city
- class
- duration
- days left
- price

The most recent ingestion is retained when duplicate records are encountered.

## 4. Changed source files

A changed source file is treated as a new file version.

The pipeline should identify the changed file using file-level metadata such as a file name plus a file hash or other source version identifier.

The affected records are then reprocessed rather than blindly appended.

This prevents stale records from remaining in the analytical layer.

## 5. Late-arriving data

Late-arriving files are still accepted into Bronze.

Their records are validated and merged into Silver based on the same business-key and deduplication rules.

Gold aggregates are refreshed for the affected data so that late-arriving records are included in analytical results.

## 6. Failure and retry behaviour

Bronze ingestion should be treated as the durable landing point.

If a downstream Silver or Gold step fails, the source file does not need to be downloaded again.

The failed processing step can be retried from the Bronze data.

This makes retries safer and reduces the risk of duplicate ingestion.

## 7. Initial load versus daily processing

The initial project load processes the complete source dataset.

After the initial load, daily processing should operate only on newly detected or changed files.

This reduces unnecessary processing as the dataset grows.

## 8. Data reconciliation

Each incremental run should record:

- files received
- files processed
- files skipped
- files rejected
- Bronze record count
- Silver valid record count
- Silver rejected record count
- duplicate record count

These metrics can be compared between pipeline stages to identify unexpected record loss or duplication.

## Design summary

```text
New/changed files
       |
       v
File detection
       |
       +---- Already processed? ----> Skip
       |
       v
Bronze append
       |
       v
Validation + deduplication
       |
       v
Silver
       |
       v
Affected Gold aggregates