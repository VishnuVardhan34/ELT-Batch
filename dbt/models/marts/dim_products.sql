select product_id, max(unit_price) current_unit_price
from {{ ref('stg_orders') }} group by product_id
