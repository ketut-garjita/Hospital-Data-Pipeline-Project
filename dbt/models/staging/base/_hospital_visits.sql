{{
  config(
    materialized='view',
    schema='staging'
  )
}}

SELECT * FROM {{ source('hospital', 'visits') }}
