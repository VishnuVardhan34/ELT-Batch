
        
            delete from "warehouse"."main"."fact_orders"
            where (
                order_id) in (
                select (order_id)
                from "fact_orders__dbt_tmp20261120181725825150"
            );

        
    

    insert into "warehouse"."main"."fact_orders" ("order_id", "customer_id", "product_id", "order_date", "updated_at", "quantity", "unit_price", "gross_amount", "status")
    (
        select "order_id", "customer_id", "product_id", "order_date", "updated_at", "quantity", "unit_price", "gross_amount", "status"
        from "fact_orders__dbt_tmp20261120181725825150"
    )
  