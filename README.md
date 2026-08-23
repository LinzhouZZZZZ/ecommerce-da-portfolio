# E-Commerce Customer & Revenue Analytics

End-to-end Data Analyst portfolio project using **Python, MySQL, SQL, DAX and Power BI** to analyse transactional e-commerce data, identify revenue drivers, evaluate customer behaviour and present business insights in an executive dashboard.

## Project Summary

The project uses the **UCI Online Retail** dataset and follows a complete analytics workflow:

**Raw data → Python cleaning → business analysis → MySQL/SQL validation → DAX measures → Power BI dashboard → business recommendations**

The final Power BI report is stored as a source-controlled **PBIP / PBIR / TMDL** project. Dashboard generation and styling are also automated with Python so the report layout can be reproduced from code.

## Key Results

| KPI | Result |
|---|---:|
| Total Revenue | **£10.64M** |
| Total Orders | **19,960** |
| Total Customers | **4,338** |
| Average Order Value | **£533.17** |
| Repeat Customer Rate | **65.58%** |
| Top 10% Customer Revenue Share | **61.41%** |
| UK Revenue Share | **84.59%** |
| Best Revenue Month | **Nov 2011 — £1.50M** |
| Top Merchandise Product | **REGENCY CAKESTAND 3 TIER — £174.16K** |

## Executive Dashboard

The Power BI **Executive Overview** page contains:

- Revenue, order, customer and AOV KPI cards
- Monthly revenue trend
- Top 5 countries by revenue
- Top 5 merchandise products by revenue
- Explicit £M / £K scaling for business-friendly interpretation
- Dark portfolio theme and source-controlled PBIR visual definitions

Power BI source files are available under [`powerbi/`](powerbi/).

## Business Insights

### 1. Revenue is highly concentrated in the United Kingdom

The UK contributes approximately **84.6% of total revenue**. This demonstrates strong performance in the core market, but it also creates geographic concentration risk.

**Business implication:** protect the UK customer base while testing targeted growth opportunities in markets such as the Netherlands, Ireland, Germany and France.

### 2. Customer value is concentrated

The highest-value **10% of customers generate approximately 61.4% of customer revenue**.

**Business implication:** retention campaigns, VIP treatment and churn monitoring should prioritise high-value customers because relatively small changes in this segment can materially affect revenue.

### 3. Repeat purchasing is an important revenue driver

Approximately **65.6% of identified customers place more than one order**.

**Business implication:** lifecycle marketing, replenishment reminders and personalised recommendations are likely to be more valuable than focusing only on first-time acquisition.

### 4. Revenue peaks late in the year

**November 2011** is the highest-revenue month at approximately **£1.50M**.

**Business implication:** inventory, marketing budget and fulfilment capacity should be prepared ahead of the Q4 demand peak.

### 5. Product revenue is concentrated in several high-performing items

The leading merchandise product is **REGENCY CAKESTAND 3 TIER**, generating approximately **£174K**. Product rankings exclude postage, manual adjustments, discounts and similar non-merchandise rows.

**Business implication:** maintain availability of proven high-performing products while using cross-sell and bundle strategies around them.

## Data Preparation

The cleaning pipeline in [`python/02_clean_data.py`](python/02_clean_data.py):

- Removes duplicate rows
- Standardises invoice, stock and customer identifiers
- Detects cancelled invoices
- Separates cancellation / return records
- Keeps valid positive-quantity, positive-price sales transactions
- Creates line revenue, year, month and order date fields
- Exports a clean sales dataset for Python, MySQL and Power BI analysis

Dataset scale:

- **541,909** raw transaction rows
- **524,878** cleaned sales rows
- **9,251** cancellation rows

Processed datasets are intentionally excluded from Git because they can be regenerated locally.

## SQL Analysis

The SQL layer uses **MySQL 8+** and demonstrates more than basic aggregation. Queries include:

- Revenue, orders, customers and AOV
- Monthly revenue and month-over-month growth using `LAG()`
- Customer revenue ranking using `DENSE_RANK()`
- Customer segmentation with `CASE`
- Revenue concentration using `NTILE()`
- Country revenue share and cumulative contribution
- Repeat vs one-time customer analysis
- Merchandise product ranking with service / adjustment exclusions

A compact executive KPI query is available in [`sql/05_quick_summary.sql`](sql/05_quick_summary.sql).

## Python Analysis

Python / pandas is used for:

- Data cleaning and validation
- KPI calculation
- Monthly revenue analysis
- Country and product performance analysis
- Customer-level metrics
- Repeat customer analysis
- Revenue concentration analysis
- Exporting lightweight summary outputs

The main business analysis script is [`python/04_business_analysis.py`](python/04_business_analysis.py).

## Power BI Automation

Instead of relying only on manual drag-and-drop editing, the Power BI report is stored in source-controlled project format and manipulated programmatically.

Key automation scripts:

- [`python/build_powerbi_dashboard.py`](python/build_powerbi_dashboard.py) — builds the Executive Overview page
- [`python/fix_powerbi_dashboard.py`](python/fix_powerbi_dashboard.py) — applies Top 5 logic and £M / £K measures
- [`python/style_powerbi_dashboard.py`](python/style_powerbi_dashboard.py) — applies the portfolio dashboard theme
- [`python/fix_kpi_cards.py`](python/fix_kpi_cards.py) — fixes KPI card contrast for the dark theme

This makes the dashboard structure reviewable through Git and demonstrates familiarity with **PBIP, PBIR and TMDL** in addition to normal Power BI development.

## Repository Structure

```text
.
├── python/
│   ├── 01_download_data.py
│   ├── 02_clean_data.py
│   ├── 03_eda.ipynb
│   ├── 04_business_analysis.py
│   ├── build_powerbi_dashboard.py
│   ├── fix_powerbi_dashboard.py
│   ├── style_powerbi_dashboard.py
│   └── fix_kpi_cards.py
├── sql/
│   ├── 00_create_database.sql
│   ├── 01_create_table.sql
│   ├── 02_business_kpis.sql
│   ├── 03_customer_rfm.sql
│   ├── 04_advanced_analysis.sql
│   └── 05_quick_summary.sql
├── powerbi/
│   ├── ecommerce_dashboard.pbip
│   ├── ecommerce_dashboard.Report/
│   └── ecommerce_dashboard.SemanticModel/
├── requirements.txt
└── README.md
```

## How to Reproduce

### 1. Create the Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Download and clean the dataset

```bash
python python/01_download_data.py
python python/02_clean_data.py
```

### 3. Run Python business analysis

```bash
python python/04_business_analysis.py
```

### 4. Load the clean dataset into MySQL

Run the SQL files in order from `sql/00_create_database.sql` through `sql/05_quick_summary.sql`.

### 5. Open the Power BI project

Open:

```text
powerbi/ecommerce_dashboard.pbip
```

The Power BI model expects the cleaned CSV at:

```text
data/processed/online_retail_clean.csv
```

## Skills Demonstrated

**Data Analysis:** KPI design, trend analysis, customer analytics, revenue concentration, product and geographic analysis  
**Python:** pandas, data cleaning, validation, automation  
**SQL:** MySQL, CTEs, window functions, ranking, segmentation, aggregation  
**Power BI:** DAX, dashboard design, PBIP, PBIR, TMDL  
**Engineering Practices:** reproducible workflow, Git version control, source-controlled BI assets

## Business Recommendation Summary

1. Prioritise retention and personalised engagement for high-value customers.
2. Reduce dependency on the UK by selectively expanding strong secondary markets.
3. Prepare inventory and operational capacity ahead of the Q4 revenue peak.
4. Protect availability of top merchandise products and build cross-sell opportunities around them.
5. Continue tracking repeat purchase behaviour and customer concentration as core management KPIs.

---

This project is designed to demonstrate an **end-to-end Data Analyst workflow**, not only dashboard creation: data quality, analytical SQL, Python validation, business interpretation and production-style Power BI reporting are all included.
