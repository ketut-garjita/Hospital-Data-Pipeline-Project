{{
  config(
    materialized='table',
    description='Cleaned and enhanced doctors dimension table'
  )
}}

SELECT
  doctor_id,
  doctor_name,
  specialization,
  experience_years,
  contact_info,
  -- Add some derived fields
  CASE
    WHEN experience_years < 5 THEN 'Junior'
    WHEN experience_years BETWEEN 5 AND 15 THEN 'Experienced'
    ELSE 'Senior'
  END AS experience_level
FROM {{ source('hospital', 'doctors') }}
