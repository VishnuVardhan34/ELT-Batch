
  
  create view "warehouse"."main"."dim_customers__dbt_tmp" as (
    select distinct customer_id from "warehouse"."main"."stg_orders"
  );
