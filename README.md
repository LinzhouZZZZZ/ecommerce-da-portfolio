# E-Commerce Customer & Revenue Analytics

## Project Overview

This portfolio project analyzes transactional data from the UCI Online Retail dataset.

The goal is to answer practical business questions using:

- SQL
- Python / pandas
- Power BI
- Data cleaning
- Customer segmentation (RFM)
- Business recommendations

## Business Questions

1. How is revenue changing over time?
2. Which countries and products generate the most revenue?
3. What is the average order value?
4. How much revenue is associated with cancellations / returns?
5. Who are the highest-value customers?
6. Which customers are at risk of becoming inactive?
7. How concentrated is revenue among the top customers?
8. What actions should the business take based on the findings?

## Dataset

Source: UCI Machine Learning Repository — Online Retail

Main fields:

- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

## Planned Workflow

1. Download the dataset with `python/01_download_data.py`
2. Clean the data with `python/02_clean_data.py`
3. Run SQL analysis from the `sql/` folder
4. Perform exploratory analysis in Python
5. Build a Power BI dashboard
6. Add business insights and recommendations

## Suggested Dashboard Pages

### Executive Overview
- Total Revenue
- Total Orders
- Total Customers
- Average Order Value
- Monthly Revenue Trend
- Revenue by Country
- Top Products

### Customer Analysis
- RFM segments
- Top customers
- Revenue concentration
- Repeat customers

### Returns / Cancellations
- Cancelled orders
- Cancelled value
- Products with high cancellation activity

## Portfolio Goal

This project demonstrates an end-to-end Data Analyst workflow rather than only visualization.
