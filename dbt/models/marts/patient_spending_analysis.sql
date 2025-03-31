{{
  config(
    materialized='table',
    description='Analysis of patient spending patterns'
  )
}}

SELECT
  p.patient_id,
  p.full_name,
  p.age_group,
  p.gender,
  p.blood_type,
  COUNT(DISTINCT v.visit_id) AS total_visits,
  SUM(v.total_cost) AS total_medical_spend,
  AVG(v.total_cost) AS avg_visit_cost,
  COUNT(DISTINCT pr.prescription_id) AS total_prescriptions,
  SUM(pr.estimated_total_cost) AS total_prescription_spend,
  COUNT(DISTINCT b.billing_id) AS total_bills,
  SUM(CASE WHEN b.payment_status = 'Paid' THEN b.total_amount ELSE 0 END) AS total_paid,
  SUM(CASE WHEN b.payment_status != 'Paid' THEN b.total_amount ELSE 0 END) AS total_outstanding
FROM {{ ref('patients') }} p
LEFT JOIN {{ ref('visits_enhanced') }} v ON p.patient_id = v.patient_id
LEFT JOIN {{ ref('prescriptions_enhanced') }} pr ON p.patient_id = pr.patient_id
LEFT JOIN {{ ref('billing_enhanced') }} b ON p.patient_id = b.patient_id
GROUP BY 1, 2, 3, 4, 5
ORDER BY total_medical_spend DESC
