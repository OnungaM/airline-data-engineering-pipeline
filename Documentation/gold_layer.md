# Gold Layer Design

## Purpose

The Gold layer contains business-focused analytical datasets designed for reporting and analysis.

The Gold models are built with dbt and materialized as tables.

## Gold Model 1: Airline Performance

### Model

`mart_airline_performance`

### Grain

One row per airline.

### Business question

Which airlines have the most flights, and how do their prices and durations compare?

### Measures

- Total flights
- Average price
- Average flight duration
- Average days left
- Minimum price
- Maximum price

### Business value

This dataset allows analysts to compare airline activity, pricing, and typical flight duration.

---

## Gold Model 2: Route Performance

### Model

`mart_route_performance`

### Grain

One row per source-city and destination-city combination.

### Business question

Which routes have the most flights, and how do prices and durations differ between routes?

### Dimensions

- Source city
- Destination city

### Measures

- Total flights
- Average price
- Average flight duration
- Minimum price
- Maximum price

### Business value

This dataset supports route-level analysis and helps identify high-volume routes and differences in pricing and duration.

---

## Gold Model 3: Pricing by Lead Time

### Model

`mart_pricing_lead_time`

### Grain

One row per number of days remaining before departure.

### Business question

How does flight pricing vary depending on how many days remain before departure?

### Dimension

- Days left

### Measures

- Total flights
- Average price
- Minimum price
- Maximum price
- Average flight duration

### Business value

This dataset can be used to analyze pricing patterns based on booking lead time.

---

## dbt materialization strategy

The Gold models are materialized as tables because they are analytical datasets that may be queried repeatedly.

Staging and intermediate models are views because they primarily support transformation logic and do not need to persist separate physical copies of the data.

This keeps the transformation structure simple while providing persisted tables for downstream analytical workloads.

## Local development and production target

The dbt project is executed locally using DuckDB for development and validation.

Amazon Redshift is the intended warehouse target for production deployment.

The Redshift DDL in the `redshift/` directory represents the proposed production warehouse design.