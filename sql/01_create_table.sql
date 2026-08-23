-- 01_create_table.sql
-- MySQL 8.4+ schema matching data/processed/online_retail_clean.csv

USE ecommerce_da;

DROP TABLE IF EXISTS online_retail;

CREATE TABLE online_retail (
    invoice_no VARCHAR(20),
    stock_code VARCHAR(50),
    description VARCHAR(255),
    quantity INT,
    invoice_date DATETIME,
    unit_price DECIMAL(12,2),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    is_cancelled BOOLEAN,
    line_revenue DECIMAL(14,2),
    year INT,
    month VARCHAR(7),
    order_date DATE
);

CREATE INDEX idx_invoice_no ON online_retail(invoice_no);
CREATE INDEX idx_customer_id ON online_retail(customer_id);
CREATE INDEX idx_invoice_date ON online_retail(invoice_date);
CREATE INDEX idx_country ON online_retail(country);
