{{
  config(
    materialized='view',
    schema='staging'
  )
}}

SELECT 
  patient_id,
  full_name,
  date_of_birth,
  gender,
  blood_type,
  contact_info,
  insurance_id,
  -- Hitung usia
  DATE_DIFF(CURRENT_DATE(), PARSE_DATE('%Y%m%d', CAST(date_of_birth AS STRING)), YEAR) AS age,
  
  -- Age group calculation
  CASE
    WHEN DATE_DIFF(CURRENT_DATE(), PARSE_DATE('%Y%m%d', CAST(date_of_birth AS STRING)), YEAR) < 18 THEN 'Child'
    WHEN DATE_DIFF(CURRENT_DATE(), PARSE_DATE('%Y%m%d', CAST(date_of_birth AS STRING)), YEAR) BETWEEN 18 AND 40 THEN 'Adult'
    WHEN DATE_DIFF(CURRENT_DATE(), PARSE_DATE('%Y%m%d', CAST(date_of_birth AS STRING)), YEAR) BETWEEN 41 AND 65 THEN 'Middle-aged'
    ELSE 'Senior'
  END AS age_group
FROM {{ source('hospital', 'patients') }}
