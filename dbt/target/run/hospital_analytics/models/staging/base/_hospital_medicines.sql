

  create or replace view `dataeng-2025-gar`.`hospital_staging`.`_hospital_medicines`
  OPTIONS()
  as 

SELECT 
  medicine_id,
  name,
  category,
  manufacturer,
  SAFE_CAST(price AS NUMERIC) AS price 
FROM `dataeng-2025-gar`.`hospital`.`medicines`;

