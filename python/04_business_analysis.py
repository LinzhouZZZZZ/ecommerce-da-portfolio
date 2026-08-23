from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
input_file = project_dir / "data" / "processed" / "online_retail_clean.csv"
output_dir = project_dir / "outputs"
output_dir.mkdir(parents=True, exist_ok=True)

if not input_file.exists():
    raise FileNotFoundError(
        "Could not find data/processed/online_retail_clean.csv. "
        "Run python/02_clean_data.py first."
    )

# Load cleaned sales data
df = pd.read_csv(input_file, parse_dates=["invoice_date"])

# -----------------------------
# 1. Executive KPIs
# -----------------------------
total_revenue = df["line_revenue"].sum()
total_orders = df["invoice_no"].nunique()
total_customers = df["customer_id"].dropna().nunique()

order_values = (
    df.groupby("invoice_no", as_index=False)["line_revenue"]
    .sum()
    .rename(columns={"line_revenue": "order_revenue"})
)
average_order_value = order_values["order_revenue"].mean()

kpis = pd.DataFrame(
    {
        "metric": [
            "Total Revenue",
            "Total Orders",
            "Total Customers",
            "Average Order Value",
        ],
        "value": [
            round(total_revenue, 2),
            total_orders,
            total_customers,
            round(average_order_value, 2),
        ],
    }
)
kpis.to_csv(output_dir / "kpi_summary.csv", index=False)

# -----------------------------
# 2. Monthly Revenue Trend
# -----------------------------
df["month"] = df["invoice_date"].dt.to_period("M").astype(str)
monthly_revenue = (
    df.groupby("month", as_index=False)["line_revenue"]
    .sum()
    .rename(columns={"line_revenue": "revenue"})
    .sort_values("month")
)
monthly_revenue["revenue"] = monthly_revenue["revenue"].round(2)
monthly_revenue.to_csv(output_dir / "monthly_revenue.csv", index=False)

# -----------------------------
# 3. Revenue by Country
# -----------------------------
country_revenue = (
    df.groupby("country", as_index=False)["line_revenue"]
    .sum()
    .rename(columns={"line_revenue": "revenue"})
    .sort_values("revenue", ascending=False)
)
country_revenue["revenue"] = country_revenue["revenue"].round(2)
country_revenue["revenue_share_pct"] = (
    country_revenue["revenue"] / total_revenue * 100
).round(2)
country_revenue.head(15).to_csv(output_dir / "top_countries.csv", index=False)

uk_revenue = country_revenue.loc[
    country_revenue["country"].eq("United Kingdom"), "revenue"
].sum()
uk_revenue_share = uk_revenue / total_revenue if total_revenue else 0

# -----------------------------
# 4. Top Merchandise Products
# -----------------------------
# The UCI dataset includes service/adjustment rows such as postage,
# bank charges and manual adjustments. Exclude these from product rankings
# so that the ranking reflects merchandise rather than administrative items.
non_product_stock_codes = {
    "POST",
    "DOT",
    "M",
    "BANK CHARGES",
    "C2",
    "D",
    "CRUK",
    "AMAZONFEE",
    "S",
}
non_product_description_pattern = (
    r"POSTAGE|CARRIAGE|BANK CHARGES|AMAZON FEE|MANUAL|DISCOUNT|"
    r"DOTCOM POSTAGE|CRUK COMMISSION|SAMPLES"
)

product_df = df[
    ~df["stock_code"].astype(str).str.upper().isin(non_product_stock_codes)
].copy()
product_df = product_df[
    ~product_df["description"]
    .fillna("")
    .str.upper()
    .str.contains(non_product_description_pattern, regex=True)
].copy()

top_products = (
    product_df.groupby(["stock_code", "description"], as_index=False)
    .agg(
        units_sold=("quantity", "sum"),
        revenue=("line_revenue", "sum"),
    )
    .sort_values("revenue", ascending=False)
)
top_products["revenue"] = top_products["revenue"].round(2)
top_products.head(20).to_csv(output_dir / "top_products.csv", index=False)

# -----------------------------
# 5. Top Customers
# -----------------------------
customer_df = df[df["customer_id"].notna()].copy()
top_customers = (
    customer_df.groupby("customer_id", as_index=False)
    .agg(
        orders=("invoice_no", "nunique"),
        revenue=("line_revenue", "sum"),
        last_purchase=("invoice_date", "max"),
    )
    .sort_values("revenue", ascending=False)
)
top_customers["revenue"] = top_customers["revenue"].round(2)
top_customers.head(20).to_csv(output_dir / "top_customers.csv", index=False)

# -----------------------------
# 6. Repeat Customer Analysis
# -----------------------------
customer_orders = customer_df.groupby("customer_id")["invoice_no"].nunique()
repeat_customers = (customer_orders > 1).sum()
identified_customers = len(customer_orders)
repeat_customer_rate = (
    repeat_customers / identified_customers if identified_customers else 0
)

# -----------------------------
# 7. Revenue Concentration
# -----------------------------
customer_revenue = (
    customer_df.groupby("customer_id")["line_revenue"]
    .sum()
    .sort_values(ascending=False)
)
identified_customer_revenue = customer_revenue.sum()

top_10_count = max(1, int(len(customer_revenue) * 0.10))
top_10_revenue_share = (
    customer_revenue.head(top_10_count).sum() / identified_customer_revenue
    if identified_customer_revenue
    else 0
)

advanced_metrics = pd.DataFrame(
    {
        "metric": [
            "Repeat Customer Rate",
            "Top 10% Customer Revenue Share",
            "United Kingdom Revenue Share",
        ],
        "value": [
            round(repeat_customer_rate * 100, 2),
            round(top_10_revenue_share * 100, 2),
            round(uk_revenue_share * 100, 2),
        ],
        "unit": ["%", "%", "%"],
    }
)
advanced_metrics.to_csv(output_dir / "customer_metrics.csv", index=False)

# -----------------------------
# Console Summary
# -----------------------------
print("\n=== Executive KPIs ===")
print(f"Total Revenue: £{total_revenue:,.2f}")
print(f"Total Orders: {total_orders:,}")
print(f"Total Customers: {total_customers:,}")
print(f"Average Order Value: £{average_order_value:,.2f}")

print("\n=== Customer & Market Metrics ===")
print(f"Repeat Customer Rate: {repeat_customer_rate:.2%}")
print(f"Top 10% Customer Revenue Share: {top_10_revenue_share:.2%}")
print(f"United Kingdom Revenue Share: {uk_revenue_share:.2%}")

print("\n=== Top 5 Countries by Revenue ===")
print(country_revenue.head(5).to_string(index=False))

print("\n=== Top 5 Merchandise Products by Revenue ===")
print(
    top_products[["description", "units_sold", "revenue"]]
    .head(5)
    .to_string(index=False)
)

print(f"\nSaved summary outputs to: {output_dir}")
