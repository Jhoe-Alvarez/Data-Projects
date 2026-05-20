--CREACION DE BASE DE DATOS
CREATE DATABASE OlistEcommerceDB;
USE OlistEcommerceDB;

--SELECCION DE TABLAS

--TABLA CLIENTES
SELECT * FROM customers;

--TABLA ITEMS DE ORDENES
SELECT * FROM order_items;

--TABLA DE PAGOS
SELECT * FROM payments;

--TABLA DE PRODUCTOS
SELECT * FROM products

--TABLA DE ORDENES
SELECT * FROM orders

--TABLA DE CATEGORIAS
SELECT * FROM category_translation

--CANTIDAD DE REGISTROS DE CADA TABLA 
SELECT 'customers' AS tabla, COUNT(*) AS total_registros FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'payments', COUNT(*) FROM payments
UNION ALL
SELECT 'category_translation', COUNT(*) FROM category_translation;

--PRIMEROS REGISTROS DE CADA TABLA 
SELECT TOP 10 * FROM customers;
SELECT TOP 10 * FROM orders;
SELECT TOP 10 * FROM order_items;
SELECT TOP 10 * FROM products;
SELECT TOP 10 * FROM payments;
SELECT TOP 10 * FROM category_translation;

--ESTADO DE PEDIDOS 
SELECT 
    order_status,
    COUNT(*) AS cantidad
FROM orders
GROUP BY order_status
ORDER BY cantidad DESC;

--RANGO DE FECHA DE ORDENES 
SELECT 
    MIN(order_purchase_timestamp) AS primera_fecha,
    MAX(order_purchase_timestamp) AS ultima_fecha
FROM orders;

--CREACION DE VISTA DE VENTAS 

CREATE VIEW vw_sales_analysis AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    o.order_status,
    CAST(o.order_purchase_timestamp AS DATE) AS order_date,
    YEAR(o.order_purchase_timestamp) AS order_year,
    MONTH(o.order_purchase_timestamp) AS order_month,

    oi.order_item_id,
    oi.product_id,
    p.product_category_name,
    ISNULL(ct.product_category_name_english, 'unknown') AS product_category_name_english,

    oi.seller_id,
    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value AS total_value

FROM orders o
INNER JOIN customers c
    ON o.customer_id = c.customer_id
INNER JOIN order_items oi
    ON o.order_id = oi.order_id
LEFT JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered';

--VER VISTA 
SELECT TOP 20 *
FROM vw_sales_analysis;

--NUMERO DE TOTALES DE REGISTROS
SELECT 
    COUNT(*) AS total_filas,
    SUM(total_value) AS ventas_totales,
    SUM(price) AS ingresos_productos,
    SUM(freight_value) AS ingresos_flete
FROM vw_sales_analysis;

--CONSULTAS

--VENTAS TOTALES 

SELECT 
    SUM(total_value) AS ventas_totales
FROM vw_sales_analysis;

--CANTIDAD DE PEDIDOS
SELECT 
      COUNT(DISTINCT order_id) as cantidad_pedidos
FROM vw_sales_analysis;

--TICKET PROMEDIO
SELECT 
     SUM(total_value) /COUNT(DISTINCT order_id) AS ticket_promedio
FROM vw_sales_analysis;

--VENTAS POR MES 
SELECT 
    order_year,
    order_month,
    SUM(total_value) AS ventas_totales,
    COUNT(DISTINCT order_id) AS cantidad_pedidos
FROM vw_sales_analysis
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

--CATEGORIAS CON MAYOR VENTA
SELECT TOP 10
    product_category_name_english AS categoria,
    SUM(total_value) AS ventas_totales,
    COUNT(DISTINCT order_id) AS pedidos,
    SUM(price) AS ingresos_producto,
    SUM(freight_value) AS ingresos_flete
FROM vw_sales_analysis
GROUP BY product_category_name_english
ORDER BY ventas_totales DESC;

--ESTADOS CON MAYOR VENTA
SELECT TOP 10
    customer_state,
    SUM(total_value) AS ventas_totales,
    COUNT(DISTINCT order_id) AS pedidos,
    COUNT(DISTINCT customer_unique_id) AS clientes_unicos
FROM vw_sales_analysis
GROUP BY customer_state
ORDER BY ventas_totales DESC;

--CLIENTE CON MAYOR GASTO 
SELECT TOP 10
    customer_unique_id,
    customer_state,
    SUM(total_value) AS gasto_total,
    COUNT(DISTINCT order_id) AS cantidad_pedidos
FROM vw_sales_analysis
GROUP BY customer_unique_id, customer_state
ORDER BY gasto_total DESC;


--VISTAS PARA PAGOS 
CREATE VIEW vw_payments_analysis AS
SELECT
    o.order_id,
    CAST(o.order_purchase_timestamp AS DATE) AS order_date,
    YEAR(o.order_purchase_timestamp) AS order_year,
    MONTH(o.order_purchase_timestamp) AS order_month,
    p.payment_type,
    p.payment_installments,
    p.payment_value
FROM orders o
INNER JOIN payments p
    ON o.order_id = p.order_id
WHERE o.order_status = 'delivered';

--VER VISTAS 
SELECT TOP 20 *
FROM vw_payments_analysis;

--METODOS DE PAGO

SELECT
    payment_type,
    COUNT(*) AS cantidad_pagos,
    SUM(payment_value) AS total_pagado
FROM vw_payments_analysis
GROUP BY payment_type
ORDER BY total_pagado DESC;


SELECT 
    SUM(total_value) AS ventas_totales,
    COUNT(DISTINCT order_id) AS cantidad_pedidos,
    SUM(total_value) / COUNT(DISTINCT order_id) AS ticket_promedio,
    COUNT(DISTINCT customer_unique_id) AS clientes_unicos,
    COUNT(order_item_id) AS unidades_vendidas
FROM vw_sales_analysis;