-- 03_customer_rfm.sql
-- MySQL 8+ RFM customer segmentation

USE ecommerce_da;

WITH customer_metrics AS (
    SELECT
        customer_id,
        DATEDIFF(
            (SELECT DATE_ADD(MAX(order_date), INTERVAL 1 DAY) FROM online_retail),
            MAX(order_date)
        ) AS recency,
        COUNT(DISTINCT invoice_no) AS frequency,
        ROUND(SUM(line_revenue), 2) AS monetary
    FROM online_retail
    WHERE customer_id IS NOT NULL
      AND customer_id <> ''
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_metrics
)
SELECT
    *,
    CONCAT(r_score, f_score, m_score) AS rfm_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score = 1 AND f_score <= 2 THEN 'Lost'
        ELSE 'Needs Attention'
    END AS customer_segment
FROM rfm_scores
ORDER BY monetary DESC;
