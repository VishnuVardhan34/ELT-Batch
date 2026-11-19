
  
  create view "warehouse"."main"."stg_orders__dbt_tmp" as (
    select order_id, customer_id, product_id, cast(order_date as date) order_date,
       cast(updated_at as timestamp) updated_at, quantity, unit_price,
       quantity * unit_price gross_amount, status
from "warehouse"."main"."raw_orders"
qualify row_number() over (partition by order_id order by updated_at desc) = 1
  );
