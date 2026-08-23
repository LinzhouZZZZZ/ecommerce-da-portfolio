-- 01_create_table.sql
-- Example schema for MySQL 8+

CREATE TABLE online_retail (
    invoice_no VARCHAR(20),
    stock_code VARCHAR(50),
    description VARCHAR(255),
    quantity INT,
    invoice_date DATETIME,
    unit_price DECIMAL(12,2),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    line_revenue DECIMAL(14,2),
    year INT,
    month VARCHAR(7),
    order_date DATE
);
