"""Post-process the generated PBIR dashboard.

Run from the repository root with Power BI Desktop CLOSED:
    python python/fix_powerbi_dashboard.py

Fixes:
- Top 5 country chart to render only the five highest-revenue countries.
- Top 5 merchandise chart to render only the five highest-revenue products.
- Revenue chart axes to use explicit £M / £K-scaled measures instead of localized 万/千 units.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POWERBI_DIR = ROOT / "powerbi"
REPORT_DEF = POWERBI_DIR / "ecommerce_dashboard.Report" / "definition"
MODEL_TABLE = (
    POWERBI_DIR
    / "ecommerce_dashboard.SemanticModel"
    / "definition"
    / "tables"
    / "online_retail_clean.tmdl"
)
PAGES_META = REPORT_DEF / "pages" / "pages.json"
BACKUP_ROOT = POWERBI_DIR / ".pbir_backups"
ENTITY = "online_retail_clean"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def backup() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_fix"
    target = BACKUP_ROOT / stamp
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPORT_DEF, target / "report_definition")
    shutil.copy2(MODEL_TABLE, target / MODEL_TABLE.name)
    return target


def add_measure_if_missing(text: str, name: str, expression: str, format_string: str = "0.00") -> str:
    if f"\tmeasure '{name}'" in text:
        return text

    marker = "\n\tcolumn invoice_no\n"
    if marker not in text:
        raise RuntimeError("Could not find insertion point in online_retail_clean.tmdl")

    lineage = str(uuid.uuid4())
    if "\n" in expression:
        body = f"\n\tmeasure '{name}' = ```\n"
        for line in expression.splitlines():
            body += f"\t\t\t{line}\n"
        body += "\t\t\t```\n"
    else:
        body = f"\n\tmeasure '{name}' = {expression}\n"

    body += f"\t\tformatString: {format_string}\n"
    body += f"\t\tlineageTag: {lineage}\n\n"
    body += "\t\tannotation PBI_FormatHint = {\"isGeneralNumber\":true}\n"
    return text.replace(marker, body + marker, 1)


def update_model() -> None:
    text = MODEL_TABLE.read_text(encoding="utf-8")

    text = add_measure_if_missing(
        text,
        "Revenue Millions",
        "DIVIDE([Total Revenue], 1000000)",
    )

    country_expr = """VAR CurrentRank =
    RANKX(
        ALL('online_retail_clean'[country]),
        CALCULATE([Total Revenue]),
        ,
        DESC,
        DENSE
    )
RETURN
    IF(CurrentRank <= 5, DIVIDE([Total Revenue], 1000000))"""
    text = add_measure_if_missing(text, "Country Revenue Top 5", country_expr)

    product_expr = """VAR CurrentRank =
    RANKX(
        ALL('online_retail_clean'[description]),
        CALCULATE([Merchandise Revenue]),
        ,
        DESC,
        DENSE
    )
RETURN
    IF(CurrentRank <= 5, DIVIDE([Merchandise Revenue], 1000))"""
    text = add_measure_if_missing(text, "Product Revenue Top 5", product_expr)

    MODEL_TABLE.write_text(text, encoding="utf-8")


def replace_measure_refs(value, old: str, new: str):
    if isinstance(value, dict):
        for key, item in list(value.items()):
            if key == "Property" and item == old:
                value[key] = new
            elif isinstance(item, str):
                value[key] = item.replace(f"{ENTITY}.{old}", f"{ENTITY}.{new}")
            else:
                replace_measure_refs(item, old, new)
    elif isinstance(value, list):
        for item in value:
            replace_measure_refs(item, old, new)


def patch_visual(path: Path, old_measure: str, new_measure: str) -> None:
    data = read_json(path)
    replace_measure_refs(data, old_measure, new_measure)
    data.pop("filterConfig", None)
    write_json(path, data)


def main() -> None:
    for required in (MODEL_TABLE, PAGES_META):
        if not required.exists():
            raise SystemExit(f"Missing required Power BI file: {required}")

    pages = read_json(PAGES_META)
    page_name = pages.get("activePageName") or pages["pageOrder"][0]
    visuals = REPORT_DEF / "pages" / page_name / "visuals"

    expected = {
        "monthly_revenue_trend": ("Total Revenue", "Revenue Millions"),
        "top_countries": ("Total Revenue", "Country Revenue Top 5"),
        "top_products": ("Merchandise Revenue", "Product Revenue Top 5"),
    }

    missing = [name for name in expected if not (visuals / name / "visual.json").exists()]
    if missing:
        raise SystemExit(
            "Generated dashboard visuals are missing: " + ", ".join(missing) +
            ". Run build_powerbi_dashboard.py first."
        )

    backup_dir = backup()
    update_model()

    for name, (old_measure, new_measure) in expected.items():
        patch_visual(visuals / name / "visual.json", old_measure, new_measure)

    print("Power BI dashboard fixes applied successfully.")
    print(f"Backup: {backup_dir}")
    print("Monthly revenue: scaled to £M")
    print("Countries: true Top 5, scaled to £M")
    print("Products: true Top 5, scaled to £K")
    print("Next: reopen powerbi/ecommerce_dashboard.pbip in Power BI Desktop.")


if __name__ == "__main__":
    main()
