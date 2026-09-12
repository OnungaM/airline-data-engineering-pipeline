{{ config(materialized='table') }}

select
    days_left,
    count(*) as total_flights,
    round(avg(price), 2) as average_price,
    min(price) as minimum_price,
    max(price) as maximum_price,
    round(avg(duration_hours), 2) as average_duration_hours
from {{ ref('stg_flights') }}
group by days_left
order by days_left