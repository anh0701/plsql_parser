SELECT c.customer_name, o.order_id, p.product_name, od.quantity  
FROM customers c  
INNER JOIN orders o ON c.customer_id = o.customer_id  
INNER JOIN order_details od ON o.order_id = od.order_id  
INNER JOIN products p ON od.product_id = p.product_id  
WHERE o.order_date >= '2024-01-01'  
GROUP BY c.customer_name, o.order_id, p.product_name, od.quantity  
ORDER BY c.customer_name;