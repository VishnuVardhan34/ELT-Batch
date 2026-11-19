select order_date, sum(gross_amount) revenue, count(*) orders
from fact_orders where status <> 'cancelled' group by order_date order by order_date;
select product_id, sum(gross_amount) revenue from fact_orders group by product_id order by revenue desc;
