{{
  config(
    materialized='table',
    description='Enhanced visits fact table with joined dimension data'
  )
}}

SELECT
  v.visit_id,
  v.visit_date,
  v.diagnosis,
  v.total_cost,
  p.patient_id,
  p.full_name,
  p.age,
  p.age_group,
  p.gender,
  p.blood_type,
  d.doctor_id,
  d.doctor_name,
  d.specialization,
  d.experience_level,
  -- Add some derived metrics
  CASE
    WHEN v.total_cost > 500 THEN 'High-cost visit'
    WHEN v.total_cost > 200 THEN 'Medium-cost visit'
    ELSE 'Low-cost visit'
  END AS cost_category,
  EXTRACT(MONTH FROM v.visit_date) AS visit_month,
  EXTRACT(YEAR FROM v.visit_date) AS visit_year
FROM {{ source('hospital', 'visits') }} v
LEFT JOIN {{ ref('patients') }} p ON v.patient_id = p.patient_id
LEFT JOIN {{ ref('doctors') }} d ON v.doctor_id = d.doctor_id

