select product_id, max(unit_price) current_unit_price
from "warehouse"."main"."stg_orders" group by product_id