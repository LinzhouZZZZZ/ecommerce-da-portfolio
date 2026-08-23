from pathlib import Path
from urllib.request import urlretrieve

DATA_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"

raw_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

zip_path = raw_dir / "online_retail.zip"

print("Downloading UCI Online Retail dataset...")
urlretrieve(DATA_URL, zip_path)
print(f"Saved to: {zip_path}")
print("Next: unzip the file, or run the cleaning script after extracting Online Retail.xlsx.")
