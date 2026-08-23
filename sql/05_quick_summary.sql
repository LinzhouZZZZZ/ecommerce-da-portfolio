USE ecommerce_da;

-- Compact one-screen summary for quick review.
WITH
order_values AS (
    SELECT invoice_no, SUM(line_revenue) AS order_revenue
    FROM online_retail
    GROUP BY invoice_no
),
monthly AS (
    SELECT month, SUM(line_revenue) AS revenue
    FROM online_retail
    GROUP BY month
),
top_month AS (
    SELECT month, revenue
    FROM monthly
    ORDER BY revenue DESC
    LIMIT 1
),
country_sales AS (
    SELECT country, SUM(line_revenue) AS revenue
    FROM online_retail
    GROUP BY country
),
top_country AS (
    SELECT country, revenue
    FROM country_sales
    ORDER BY revenue DESC
    LIMIT 1
),
product_sales AS (
    SELECT description, SUM(line_revenue) AS revenue
    FROM online_retail
    WHERE UPPER(stock_code) NOT IN ('POST','DOT','M','BANK CHARGES','C2','D','CRUK','AMAZONFEE','S')
      AND UPPER(COALESCE(description, '')) NOT REGEXP
          'POSTAGE|CARRIAGE|BANK CHARGES|AMAZON FEE|MANUAL|DISCOUNT|DOTCOM POSTAGE|CRUK COMMISSION|SAMPLES'
    GROUP BY stock_code, description
),
top_product AS (
    SELECT description, revenue
    FROM product_sales
    ORDER BY revenue DESC
    LIMIT 1
)
SELECT 'Total Revenue' AS metric,
       CONCAT('£', FORMAT((SELECT SUM(line_revenue) FROM online_retail), 2)) AS value
UNION ALL
SELECT 'Total Orders',
       FORMAT((SELECT COUNT(DISTINCT invoice_no) FROM online_retail), 0)
UNION ALL
SELECT 'Total Customers',
       FORMAT((SELECT COUNT(DISTINCT customer_id) FROM online_retail WHERE customer_id IS NOT NULL AND customer_id <> ''), 0)
UNION ALL
SELECT 'Average Order Value',
       CONCAT('£', FORMAT((SELECT AVG(order_revenue) FROM order_values), 2))
UNION ALL
SELECT 'Best Revenue Month',
       CONCAT((SELECT month FROM top_month), ' (£', FORMAT((SELECT revenue FROM top_month), 2), ')')
UNION ALL
SELECT 'Top Country',
       CONCAT(
           (SELECT country FROM top_country),
           ' (£', FORMAT((SELECT revenue FROM top_country), 2), ', ',
           ROUND((SELECT revenue FROM top_country) / (SELECT SUM(line_revenue) FROM online_retail) * 100, 2), '%)'
       )
UNION ALL
SELECT 'Top Merchandise Product',
       CONCAT((SELECT description FROM top_product), ' (£', FORMAT((SELECT revenue FROM top_product), 2), ')');
