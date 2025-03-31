{{
  config(
    materialized='table',
    description='Enhanced billing fact table with joined dimension data'
  )
}}

SELECT
  b.billing_id,
  b.billing_date,
  b.total_amount,
  b.payment_status,
  v.visit_id,
  v.visit_date,
  v.diagnosis,
  v.doctor_name,
  v.specialization,
  p.patient_id,
  p.full_name,
  p.age_group,
  p.insurance_id,
  -- Add some derived fields
  EXTRACT(MONTH FROM b.billing_date) AS billing_month,
  EXTRACT(YEAR FROM b.billing_date) AS billing_year,
  CASE
    WHEN b.payment_status = 'Paid' THEN 1
    ELSE 0
  END AS is_paid,
  -- Days between visit and billing
  DATE_DIFF(b.billing_date, v.visit_date, DAY) AS days_to_bill
FROM {{ source('hospital', 'billing_payments') }} b
LEFT JOIN {{ ref('visits_enhanced') }} v ON b.visit_id = v.visit_id
LEFT JOIN {{ ref('patients') }} p ON b.patient_id = p.patient_id

