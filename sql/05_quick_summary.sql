USE ecommerce_da;

-- 1. Executive KPI snapshot
WITH order_values AS (
    SELECT invoice_no, SUM(line_revenue) AS order_revenue
    FROM online_retail
    GROUP BY invoice_no
)
SELECT
    ROUND((SELECT SUM(line_revenue) FROM online_retail), 2) AS total_revenue,
    (SELECT COUNT(DISTINCT invoice_no) FROM online_retail) AS total_orders,
    (SELECT COUNT(DISTINCT customer_id) FROM online_retail WHERE customer_id IS NOT NULL AND customer_id <> '') AS total_customers,
    ROUND(AVG(order_revenue), 2) AS average_order_value
FROM order_values;

-- 2. Monthly revenue trend
SELECT
    month,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM online_retail
GROUP BY month
ORDER BY month;

-- 3. Top 5 countries by revenue
SELECT
    country,
    ROUND(SUM(line_revenue), 2) AS revenue,
    ROUND(SUM(line_revenue) / (SELECT SUM(line_revenue) FROM online_retail) * 100, 2) AS revenue_share_pct
FROM online_retail
GROUP BY country
ORDER BY revenue DESC
LIMIT 5;

-- 4. Top 5 merchandise products by revenue
SELECT
    description,
    SUM(quantity) AS units_sold,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM online_retail
WHERE UPPER(stock_code) NOT IN ('POST','DOT','M','BANK CHARGES','C2','D','CRUK','AMAZONFEE','S')
  AND UPPER(COALESCE(description, '')) NOT REGEXP 'POSTAGE|CARRIAGE|BANK CHARGES|AMAZON FEE|MANUAL|DISCOUNT|DOTCOM POSTAGE|CRUK COMMISSION|SAMPLES'
GROUP BY stock_code, description
ORDER BY revenue DESC
LIMIT 5;
