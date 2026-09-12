-- ============================================================
-- Amazon Redshift target schema
--
-- Purpose:
-- Defines the warehouse target for the Gold analytical layer.
--
-- The local project uses DuckDB to validate dbt transformations.
-- These tables represent the intended Amazon Redshift target.
--
-- Distribution:
-- DISTSTYLE AUTO allows Redshift to automatically select an
-- appropriate distribution strategy.
--
-- Sorting:
-- SORTKEY columns support common filtering and aggregation
-- patterns for the analytical workloads.
--
-- Note:
-- Redshift execution is not required for this take-home project.
-- ============================================================


-- ============================================================
-- Gold analytical table: airline performance
-- Grain: one row per airline
-- ============================================================

create table if not exists gold_airline_performance (
    airline varchar(50) not null,
    total_flights bigint not null,
    average_price decimal(12,2),
    average_duration_hours decimal(10,2),
    average_days_left decimal(10,2),
    minimum_price decimal(12,2),
    maximum_price decimal(12,2)
)
diststyle auto
sortkey (airline);


-- ============================================================
-- Gold analytical table: route performance
-- Grain: one row per source/destination route
-- ============================================================

create table if not exists gold_route_performance (
    source_city varchar(50) not null,
    destination_city varchar(50) not null,
    total_flights bigint not null,
    average_price decimal(12,2),
    average_duration_hours decimal(10,2),
    minimum_price decimal(12,2),
    maximum_price decimal(12,2)
)
diststyle auto
sortkey (source_city, destination_city);
-- ============================================================
-- Gold analytical table: pricing by booking lead time
-- Grain: one row per number of days left before departure
-- ============================================================

create table if not exists gold_pricing_lead_time (
    days_left integer not null,
    total_flights bigint not null,
    average_price decimal(12,2),
    minimum_price decimal(12,2),
    maximum_price decimal(12,2),
    average_duration_hours decimal(10,2)
)
diststyle auto
sortkey (days_left);
