

SELECT 
  medicine_id,
  name,
  category,
  manufacturer,
  SAFE_CAST(price AS NUMERIC) AS price 
FROM `dataeng-2025-gar`.`hospital`.`medicines`