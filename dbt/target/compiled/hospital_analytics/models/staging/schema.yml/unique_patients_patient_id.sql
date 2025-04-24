
    
    

with dbt_test__target as (

  select patient_id as unique_field
  from `dataeng-2025-gar`.`hospital_staging`.`patients`
  where patient_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


