
  
    

    create or replace table `dataeng-2025-gar`.`hospital_analytics`.`patient_journey`
      
    
    

    OPTIONS()
    as (
      

WITH patient_data AS (
  SELECT 
    patient_id,
    full_name,
    gender,
    age
  FROM `dataeng-2025-gar`.`hospital_staging`.`patients`
),

visit_details AS (
  SELECT
    v.visit_id,
    v.visit_date,
    v.patient_id,
    COALESCE(p.full_name, 'Unknown Patient') AS patient_full_name,
    v.doctor_id,
    v.doctor_name,
    v.specialization,
    v.diagnosis,
    v.total_cost AS visit_cost,
    v.cost_category,
    p.gender,
    p.age
  FROM `dataeng-2025-gar`.`hospital_intermediate`.`visits_enhanced` v
  LEFT JOIN patient_data p ON v.patient_id = p.patient_id
),

prescription_details AS (
  SELECT
    p.prescription_id,
    p.patient_id,
    p.doctor_id,
    p.medicine_name,
    p.dosage,
    p.duration,
    p.estimated_total_cost AS prescription_cost,
    -- Using visit_date as proxy since prescription_date doesn't exist
    (SELECT MIN(v.visit_date) 
    FROM `dataeng-2025-gar`.`hospital_intermediate`.`visits_enhanced` v
    WHERE v.patient_id = p.patient_id
      AND v.doctor_id = p.doctor_id
    ) AS approximate_prescription_date
  FROM `dataeng-2025-gar`.`hospital_intermediate`.`prescriptions_enhanced` p
),

billing_details AS (
  SELECT
    b.billing_id,
    b.visit_id,
    b.patient_id,
    b.billing_date,
    b.total_amount,
    b.payment_status,
    b.days_to_bill
  FROM `dataeng-2025-gar`.`hospital_intermediate`.`billing_enhanced` b
)

SELECT
  vd.visit_id,
  vd.visit_date,
  vd.patient_id,
  vd.patient_full_name AS patient_name,
  vd.gender,
  vd.age,
  vd.doctor_id,
  COALESCE(vd.doctor_name, 'Unknown Doctor') AS doctor_name,
  COALESCE(vd.specialization, 'Not Specified') AS specialization,
  COALESCE(vd.diagnosis, 'No Diagnosis Recorded') AS diagnosis,
  vd.visit_cost,
  vd.cost_category,
  
  pd.prescription_id,
  COALESCE(pd.medicine_name, 'No Prescription') AS medicine_name,
  pd.dosage,
  pd.duration,
  COALESCE(pd.prescription_cost, 0) AS prescription_cost,
  
  bd.billing_id,
  bd.billing_date,
  bd.total_amount AS billed_amount,
  COALESCE(bd.payment_status, 'Not Billed') AS payment_status,
  bd.days_to_bill,
  
  -- Financial calculations
  vd.visit_cost + COALESCE(pd.prescription_cost, 0) AS total_episode_cost,
  CASE
    WHEN bd.payment_status = 'Paid' THEN 0
    ELSE COALESCE(bd.total_amount, vd.visit_cost)
  END AS outstanding_balance,
  
  -- Enhanced analytics
  CASE
    WHEN pd.prescription_id IS NOT NULL THEN 1
    ELSE 0
  END AS has_prescription,
  
  COUNT(pd.prescription_id) OVER (
    PARTITION BY vd.patient_id
  ) AS total_prescriptions_for_patient,
  
  AVG(vd.visit_cost) OVER (
    PARTITION BY vd.patient_id
  ) AS avg_visit_cost_per_patient,
  
  -- Visit analytics
  COUNT(vd.visit_id) OVER (
    PARTITION BY vd.patient_id
  ) AS total_visits_for_patient

FROM visit_details vd
LEFT JOIN prescription_details pd ON 
  vd.patient_id = pd.patient_id AND
  vd.doctor_id = pd.doctor_id
LEFT JOIN billing_details bd ON 
  vd.visit_id = bd.visit_id
ORDER BY 
  vd.patient_full_name,
  vd.visit_date
    );
  