-- 02_business_kpis.sql
-- Core business KPI queries for the cleaned Online Retail dataset

USE ecommerce_da;

-- Total revenue
SELECT ROUND(SUM(line_revenue), 2) AS total_revenue
FROM online_retail;

-- Number of unique orders
SELECT COUNT(DISTINCT invoice_no) AS total_orders
FROM online_retail;

-- Number of identified customers
SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM online_retail
WHERE customer_id IS NOT NULL
  AND customer_id <> '';

-- Average order value
WITH order_values AS (
    SELECT
        invoice_no,
        SUM(line_revenue) AS order_revenue
    FROM online_retail
    GROUP BY invoice_no
)
SELECT ROUND(AVG(order_revenue), 2) AS average_order_value
FROM order_values;

-- Monthly revenue trend
SELECT
    month,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM online_retail
GROUP BY month
ORDER BY month;

-- Revenue by country
SELECT
    country,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM online_retail
GROUP BY country
ORDER BY revenue DESC;

-- Top 10 products (raw ranking; advanced script contains merchandise-only ranking)
SELECT
    stock_code,
    description,
    SUM(quantity) AS units_sold,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM online_retail
GROUP BY stock_code, description
ORDER BY revenue DESC
LIMIT 10;
