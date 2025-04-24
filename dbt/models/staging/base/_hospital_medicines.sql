{{
  config(
    materialized='view',
    schema='staging'
  )
}}

SELECT 
  medicine_id,
  name,
  category,
  manufacturer,
  SAFE_CAST(price AS NUMERIC) AS price 
FROM {{ source('hospital', 'medicines') }}
