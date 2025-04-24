
  
    

    create or replace table `dataeng-2025-gar`.`hospital_staging`.`patients`
      
    
    

    OPTIONS()
    as (
      

WITH cleaned_patients AS (
  SELECT
    patient_id,
    full_name,
    date_of_birth,
    gender,
    blood_type,
    contact_info,
    insurance_id
  FROM `dataeng-2025-gar`.`hospital_staging`.`_hospital_patients`
)

SELECT
  patient_id,
  full_name,
  date_of_birth,
  gender,
  blood_type,
  contact_info,
  insurance_id,
  -- Hitung usia
  CASE
    WHEN date_of_birth IS NOT NULL 
    THEN DATE_DIFF(CURRENT_DATE(), date_of_birth, YEAR)
    ELSE NULL
  END AS age,
  -- Kategori usia
  CASE
    WHEN date_of_birth IS NULL THEN 'Invalid Birth Date'
    WHEN DATE_DIFF(CURRENT_DATE(), date_of_birth, YEAR) < 18 THEN 'Child'
    WHEN DATE_DIFF(CURRENT_DATE(), date_of_birth, YEAR) BETWEEN 18 AND 40 THEN 'Adult'
    WHEN DATE_DIFF(CURRENT_DATE(), date_of_birth, YEAR) BETWEEN 41 AND 65 THEN 'Middle-aged'
    ELSE 'Senior'
  END AS age_group
FROM cleaned_patients
    );
  