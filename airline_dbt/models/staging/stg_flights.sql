{{ config(materialized='view') }}

select
    cast(index as bigint) as flight_record_id,
    trim(airline) as airline,
    trim(flight) as flight,
    trim(source_city) as source_city,
    trim(departure_time) as departure_time,
    trim(stops) as stops,
    trim(arrival_time) as arrival_time,
    trim(destination_city) as destination_city,
    trim(class) as travel_class,
    cast(duration as double) as duration_hours,
    cast(days_left as integer) as days_left,
    cast(price as double) as price,
    source_file,
    ingested_at,
    run_id
from read_parquet(
    '../data/silver/flights/*.parquet'
)