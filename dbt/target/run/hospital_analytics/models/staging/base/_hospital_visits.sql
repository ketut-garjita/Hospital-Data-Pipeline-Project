

  create or replace view `dataeng-2025-gar`.`hospital_staging`.`_hospital_visits`
  OPTIONS()
  as 

SELECT * FROM `dataeng-2025-gar`.`hospital`.`visits`;

