{{ config(materialized='table') }}

select
    airline,
    count(*) as total_flights,
    round(avg(price), 2) as average_price,
    round(avg(duration_hours), 2) as average_duration_hours,
    round(avg(days_left), 2) as average_days_left,
    min(price) as minimum_price,
    max(price) as maximum_price
from {{ ref('stg_flights') }}
group by airline
order by total_flights desc