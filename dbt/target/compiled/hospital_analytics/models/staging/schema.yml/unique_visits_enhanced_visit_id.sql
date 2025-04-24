
    
    

with dbt_test__target as (

  select visit_id as unique_field
  from `dataeng-2025-gar`.`hospital_intermediate`.`visits_enhanced`
  where visit_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


