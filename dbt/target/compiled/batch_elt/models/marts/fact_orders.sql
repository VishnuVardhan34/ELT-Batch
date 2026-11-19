
select * from "warehouse"."main"."stg_orders"

where updated_at > (select coalesce(max(updated_at), '1900-01-01') from "warehouse"."main"."fact_orders")
