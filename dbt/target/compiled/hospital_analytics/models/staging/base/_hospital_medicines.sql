

SELECT 
  medicine_id,
  name,
  category,
  manufacturer,
  SAFE_CAST(price AS NUMERIC) AS price  # Pastikan numeric
FROM `de-zoomcamp-2025--id`.`hospital`.`medicines`