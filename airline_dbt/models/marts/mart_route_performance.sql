{{ config(materialized='table') }}

select
    source_city,
    destination_city,
    count(*) as total_flights,
    round(avg(price), 2) as average_price,
    round(avg(duration_hours), 2) as average_duration_hours,
    min(price) as minimum_price,
    max(price) as maximum_price
from {{ ref('stg_flights') }}
group by
    source_city,
    destination_city
order by total_flights desc