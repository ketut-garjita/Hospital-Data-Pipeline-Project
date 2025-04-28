{{
  config(
    materialized='table',
    schema='staging'
  )
}}

SELECT
  medicine_id,
  name AS medicine_name,
  category,
  manufacturer,
  -- convert to numeric
  SAFE_CAST(price AS NUMERIC) AS price,
  -- Fixed price category with correct data type
  CASE
    WHEN SAFE_CAST(price AS NUMERIC) < 10 THEN 'Low-cost'
    WHEN SAFE_CAST(price AS NUMERIC) BETWEEN 10 AND 50 THEN 'Medium-cost'
    ELSE 'High-cost'
  END AS price_category
FROM {{ ref('_hospital_medicines') }}
