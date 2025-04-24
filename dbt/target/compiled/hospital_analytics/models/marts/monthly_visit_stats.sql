

SELECT
  visit_year,
  visit_month,
  COUNT(DISTINCT visit_id) AS total_visits,
  COUNT(DISTINCT patient_id) AS unique_patients,
  COUNT(DISTINCT doctor_id) AS unique_doctors,
  SUM(total_cost) AS total_revenue,
  AVG(total_cost) AS avg_visit_cost,
  -- Calculate percentage of high-cost visits
  SAFE_DIVIDE(
    COUNT(CASE WHEN cost_category = 'High-cost visit' THEN 1 END),
    COUNT(*)
  ) * 100 AS pct_high_cost_visits
FROM `dataeng-2025-gar`.`hospital_intermediate`.`visits_enhanced`
GROUP BY visit_year, visit_month
ORDER BY visit_year, visit_month