from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
raw_file = project_dir / "data" / "raw" / "Online Retail.xlsx"
output_dir = project_dir / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

if not raw_file.exists():
    raise FileNotFoundError(
        "Could not find data/raw/Online Retail.xlsx. Download/extract the UCI dataset first."
    )

df = pd.read_excel(raw_file)
print("Raw rows:", len(df))

df.columns = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
]

df = df.drop_duplicates()
df["invoice_no"] = df["invoice_no"].astype(str)
df["stock_code"] = df["stock_code"].astype(str)
df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
df["is_cancelled"] = df["invoice_no"].str.upper().str.startswith("C")
df["line_revenue"] = df["quantity"] * df["unit_price"]

returns = df[df["is_cancelled"]].copy()
returns.to_csv(output_dir / "online_retail_returns.csv", index=False)

sales = df[
    (~df["is_cancelled"])
    & (df["quantity"] > 0)
    & (df["unit_price"] > 0)
    & (df["invoice_date"].notna())
].copy()

sales["customer_id"] = sales["customer_id"].astype("Int64").astype("string")
sales["year"] = sales["invoice_date"].dt.year
sales["month"] = sales["invoice_date"].dt.to_period("M").astype(str)
sales["order_date"] = sales["invoice_date"].dt.date

sales.to_csv(output_dir / "online_retail_clean.csv", index=False)

print("Clean sales rows:", len(sales))
print("Cancellation rows:", len(returns))
print("Revenue:", round(sales["line_revenue"].sum(), 2))
print("Saved processed files to:", output_dir)
