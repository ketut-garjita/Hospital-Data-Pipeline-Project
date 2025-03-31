
    
    

with dbt_test__target as (

  select doctor_id as unique_field
  from `de-zoomcamp-2025--id`.`hospital_staging`.`doctors`
  where doctor_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


