-- 04_advanced_analysis.sql
-- MySQL 8+
-- Advanced portfolio queries demonstrating CTEs, CASE, window functions and ranking.

USE ecommerce_da;

-- 1. Monthly revenue with month-over-month growth
WITH monthly AS (
    SELECT
        month,
        ROUND(SUM(line_revenue), 2) AS revenue
    FROM online_retail
    GROUP BY month
),
with_previous AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue
    FROM monthly
)
SELECT
    month,
    revenue,
    previous_month_revenue,
    ROUND(
        (revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0) * 100,
        2
    ) AS mom_growth_pct
FROM with_previous
ORDER BY month;

-- 2. Customer revenue ranking
WITH customer_sales AS (
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS orders,
        ROUND(SUM(line_revenue), 2) AS revenue
    FROM online_retail
    WHERE customer_id IS NOT NULL
      AND customer_id <> ''
    GROUP BY customer_id
)
SELECT
    customer_id,
    orders,
    revenue,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM customer_sales
ORDER BY revenue_rank
LIMIT 50;

-- 3. Customer value segmentation using CASE
WITH customer_sales AS (
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS orders,
        ROUND(SUM(line_revenue), 2) AS revenue
    FROM online_retail
    WHERE customer_id IS NOT NULL
      AND customer_id <> ''
    GROUP BY customer_id
)
SELECT
    customer_id,
    orders,
    revenue,
    CASE
        WHEN revenue >= 5000 THEN 'High Value'
        WHEN revenue >= 2000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_segment
FROM customer_sales
ORDER BY revenue DESC;

-- 4. Revenue concentration by customer decile
WITH customer_sales AS (
    SELECT
        customer_id,
        SUM(line_revenue) AS revenue
    FROM online_retail
    WHERE customer_id IS NOT NULL
      AND customer_id <> ''
    GROUP BY customer_id
),
deciles AS (
    SELECT
        customer_id,
        revenue,
        NTILE(10) OVER (ORDER BY revenue DESC) AS customer_decile
    FROM customer_sales
)
SELECT
    customer_decile,
    COUNT(*) AS customers,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(
        SUM(revenue) / SUM(SUM(revenue)) OVER () * 100,
        2
    ) AS revenue_share_pct
FROM deciles
GROUP BY customer_decile
ORDER BY customer_decile;

-- 5. Country revenue share and cumulative share
WITH country_sales AS (
    SELECT
        country,
        SUM(line_revenue) AS revenue
    FROM online_retail
    GROUP BY country
),
ranked AS (
    SELECT
        country,
        revenue,
        SUM(revenue) OVER () AS total_revenue,
        SUM(revenue) OVER (
            ORDER BY revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue
    FROM country_sales
)
SELECT
    country,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue / total_revenue * 100, 2) AS revenue_share_pct,
    ROUND(cumulative_revenue / total_revenue * 100, 2) AS cumulative_share_pct
FROM ranked
ORDER BY revenue DESC;

-- 6. Repeat vs one-time customer profile
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS orders,
        SUM(line_revenue) AS revenue
    FROM online_retail
    WHERE customer_id IS NOT NULL
      AND customer_id <> ''
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN orders > 1 THEN 'Repeat Customer'
        ELSE 'One-Time Customer'
    END AS customer_type,
    COUNT(*) AS customers,
    ROUND(AVG(revenue), 2) AS avg_customer_revenue,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM customer_orders
GROUP BY customer_type
ORDER BY total_revenue DESC;

-- 7. Top merchandise products excluding service/adjustment rows
SELECT
    stock_code,
    description,
    SUM(quantity) AS units_sold,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM online_retail
WHERE UPPER(stock_code) NOT IN (
    'POST', 'DOT', 'M', 'BANK CHARGES', 'C2', 'D', 'CRUK', 'AMAZONFEE', 'S'
)
AND UPPER(COALESCE(description, '')) NOT REGEXP
    'POSTAGE|CARRIAGE|BANK CHARGES|AMAZON FEE|MANUAL|DISCOUNT|DOTCOM POSTAGE|CRUK COMMISSION|SAMPLES'
GROUP BY stock_code, description
ORDER BY revenue DESC
LIMIT 20;
