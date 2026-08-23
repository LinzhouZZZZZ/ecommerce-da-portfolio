"""Build the Power BI Executive Overview page from PBIR/TMDL source files.

Run from the repository root with Power BI Desktop CLOSED:
    python python/build_powerbi_dashboard.py

The script:
1. Backs up the current report definition and table TMDL.
2. Adds/updates measures needed by the dashboard.
3. Rebuilds the first PBIR page with:
   - Executive KPI card
   - Monthly revenue line chart
   - Top 5 countries by revenue
   - Top 5 merchandise products by revenue

Power BI Desktop validates PBIR files when the .pbip project is reopened.
"""

from __future__ import annotations

import json
import re
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
VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
    "visualContainer/2.12.0/schema.json"
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def literal(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def column_field(property_name: str) -> dict:
    return {
        "Column": {
            "Expression": {"SourceRef": {"Entity": ENTITY}},
            "Property": property_name,
        }
    }


def measure_field(property_name: str) -> dict:
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": ENTITY}},
            "Property": property_name,
        }
    }


def projection(field: dict, query_ref: str, label: str | None = None) -> dict:
    result = {"field": field, "queryRef": query_ref}
    if label:
        result["nativeQueryRef"] = label
        result["displayName"] = label
    result["active"] = True
    return result


def title_object(title: str) -> dict:
    return {
        "title": [
            {
                "properties": {
                    "show": literal("true"),
                    "text": literal(f"'{title}'"),
                    "fontSize": literal("15D"),
                    "bold": literal("true"),
                }
            }
        ]
    }


def make_card_visual() -> dict:
    measures = [
        ("Revenue KPI", "Revenue (£M)"),
        ("Orders KPI", "Orders (K)"),
        ("Customers KPI", "Customers (K)"),
        ("AOV KPI", "AOV (£)"),
    ]
    projections = [
        projection(
            measure_field(measure),
            f"{ENTITY}.{measure}",
            label,
        )
        for measure, label in measures
    ]

    return {
        "$schema": VISUAL_SCHEMA,
        "name": "executive_kpis",
        "position": {
            "x": 80,
            "y": 60,
            "z": 1000,
            "height": 185,
            "width": 1760,
            "tabOrder": 1000,
        },
        "visual": {
            "visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": projections}}},
            "visualContainerObjects": title_object("Executive KPIs"),
            "drillFilterOtherVisuals": True,
        },
    }


def make_line_chart() -> dict:
    month = column_field("month")
    revenue = measure_field("Total Revenue")

    return {
        "$schema": VISUAL_SCHEMA,
        "name": "monthly_revenue_trend",
        "position": {
            "x": 80,
            "y": 285,
            "z": 2000,
            "height": 350,
            "width": 1100,
            "tabOrder": 2000,
        },
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            projection(month, f"{ENTITY}.month", "Month")
                        ]
                    },
                    "Y": {
                        "projections": [
                            projection(
                                revenue,
                                f"{ENTITY}.Total Revenue",
                                "Revenue",
                            )
                        ]
                    },
                },
                "sortDefinition": {
                    "sort": [{"field": month, "direction": "Ascending"}],
                    "isDefaultSort": True,
                },
            },
            "visualContainerObjects": title_object("Monthly Revenue Trend"),
            "drillFilterOtherVisuals": True,
        },
    }


def top_n_filter(column: str, measure: str, count: int = 5) -> dict:
    alias = "r"
    return {
        "name": f"top_{count}_{column}",
        "field": column_field(column),
        "type": "TopN",
        "filter": {
            "Version": 2,
            "From": [{"Name": alias, "Entity": ENTITY, "Type": 0}],
            "Where": [
                {
                    "Condition": {
                        "VisualTopN": {
                            "Expression": {
                                "Column": {
                                    "Expression": {
                                        "SourceRef": {"Source": alias}
                                    },
                                    "Property": column,
                                }
                            },
                            "Count": {"Literal": {"Value": f"{count}L"}},
                            "OrderBy": measure_field(measure),
                            "IsAscending": False,
                        }
                    }
                }
            ],
        },
    }


def make_bar_chart(
    *,
    name: str,
    category: str,
    measure: str,
    title: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
) -> dict:
    category_field = column_field(category)
    measure_ref = measure_field(measure)

    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "height": height,
            "width": width,
            "tabOrder": z,
        },
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            projection(
                                category_field,
                                f"{ENTITY}.{category}",
                                category.replace("_", " ").title(),
                            )
                        ]
                    },
                    "Y": {
                        "projections": [
                            projection(
                                measure_ref,
                                f"{ENTITY}.{measure}",
                                "Revenue",
                            )
                        ]
                    },
                },
                "sortDefinition": {
                    "sort": [
                        {"field": measure_ref, "direction": "Descending"}
                    ],
                    "isDefaultSort": True,
                },
            },
            "visualContainerObjects": title_object(title),
            "drillFilterOtherVisuals": True,
        },
        "filterConfig": {
            "filters": [top_n_filter(category, measure, 5)]
        },
    }


def backup_files(page_dir: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_ROOT / stamp
    backup.mkdir(parents=True, exist_ok=True)

    shutil.copytree(REPORT_DEF, backup / "report_definition")
    shutil.copy2(MODEL_TABLE, backup / MODEL_TABLE.name)
    return backup


def measure_block_bounds(lines: list[str], measure_name: str) -> tuple[int, int] | None:
    start_pattern = re.compile(rf"^\tmeasure '{re.escape(measure_name)}' =")
    start = None
    for i, line in enumerate(lines):
        if start_pattern.match(line):
            start = i
            break
    if start is None:
        return None

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("\tmeasure '") or lines[j].startswith("\tcolumn "):
            end = j
            break
    return start, end


def set_measure_format(text: str, measure_name: str, format_string: str) -> str:
    lines = text.splitlines()
    bounds = measure_block_bounds(lines, measure_name)
    if not bounds:
        raise RuntimeError(f"Measure not found in TMDL: {measure_name}")

    start, end = bounds
    block = lines[start:end]

    for i, line in enumerate(block):
        if line.startswith("\t\tformatString:"):
            block[i] = f"\t\tformatString: {format_string}"
            return "\n".join(lines[:start] + block + lines[end:]) + "\n"

    insert_at = None
    for i, line in enumerate(block[1:], start=1):
        if line.startswith("\t\tlineageTag:") or line.startswith("\t\tannotation "):
            insert_at = i
            break

    if insert_at is None:
        insert_at = len(block)

    block.insert(insert_at, f"\t\tformatString: {format_string}")
    return "\n".join(lines[:start] + block + lines[end:]) + "\n"


def add_merchandise_measure(text: str) -> str:
    if "\tmeasure 'Merchandise Revenue'" in text:
        return text

    marker = "\n\tcolumn invoice_no\n"
    if marker not in text:
        raise RuntimeError("Could not locate first column in online_retail_clean.tmdl")

    lineage = str(uuid.uuid4())
    measure = f'''\n\tmeasure 'Merchandise Revenue' = ```\n\t\t\tCALCULATE(\n\t\t\t    [Total Revenue],\n\t\t\t    FILTER(\n\t\t\t        'online_retail_clean',\n\t\t\t        NOT (\n\t\t\t            UPPER('online_retail_clean'[stock_code]) IN {{\n\t\t\t                "POST", "DOT", "M", "BANK CHARGES", "C2",\n\t\t\t                "D", "CRUK", "AMAZONFEE", "S"\n\t\t\t            }}\n\t\t\t        )\n\t\t\t        && NOT (\n\t\t\t            CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "POSTAGE")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "CARRIAGE")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "BANK CHARGES")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "AMAZON FEE")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "MANUAL")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "DISCOUNT")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "DOTCOM POSTAGE")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "CRUK COMMISSION")\n\t\t\t            || CONTAINSSTRING(UPPER(COALESCE('online_retail_clean'[description], "")), "SAMPLES")\n\t\t\t        )\n\t\t\t    )\n\t\t\t)\n\t\t\t```\n\t\tformatString: "£"#,0.00;-"£"#,0.00;"£"#,0.00\n\t\tlineageTag: {lineage}\n\n\t\tannotation PBI_FormatHint = {{"currencyCulture":"en-GB"}}\n'''

    return text.replace(marker, measure + marker, 1)


def update_model() -> None:
    text = MODEL_TABLE.read_text(encoding="utf-8")
    text = set_measure_format(text, "Revenue KPI", "0.00")
    text = set_measure_format(text, "Orders KPI", "0.00")
    text = set_measure_format(text, "Customers KPI", "0.00")
    text = set_measure_format(text, "AOV KPI", '"£"#,0.00;-"£"#,0.00;"£"#,0.00')
    text = add_merchandise_measure(text)
    MODEL_TABLE.write_text(text, encoding="utf-8")


def rebuild_page(page_dir: Path) -> None:
    page_json_path = page_dir / "page.json"
    page = read_json(page_json_path)
    page["displayName"] = "Executive Overview"
    page["displayOption"] = "FitToPage"
    page["height"] = 1080
    page["width"] = 1920
    write_json(page_json_path, page)

    visuals_dir = page_dir / "visuals"
    if visuals_dir.exists():
        shutil.rmtree(visuals_dir)
    visuals_dir.mkdir(parents=True, exist_ok=True)

    visuals = [
        make_card_visual(),
        make_line_chart(),
        make_bar_chart(
            name="top_countries",
            category="country",
            measure="Total Revenue",
            title="Top 5 Countries by Revenue",
            x=1220,
            y=285,
            width=620,
            height=350,
            z=3000,
        ),
        make_bar_chart(
            name="top_products",
            category="description",
            measure="Merchandise Revenue",
            title="Top 5 Merchandise Products by Revenue",
            x=80,
            y=680,
            width=1760,
            height=320,
            z=4000,
        ),
    ]

    for visual in visuals:
        folder = visuals_dir / visual["name"]
        write_json(folder / "visual.json", visual)


def main() -> None:
    for required in (REPORT_DEF, MODEL_TABLE, PAGES_META):
        if not required.exists():
            raise SystemExit(f"Missing required Power BI project file: {required}")

    pages = read_json(PAGES_META)
    page_name = pages.get("activePageName") or pages["pageOrder"][0]
    page_dir = REPORT_DEF / "pages" / page_name
    if not page_dir.exists():
        raise SystemExit(f"Active page folder does not exist: {page_dir}")

    backup = backup_files(page_dir)
    update_model()
    rebuild_page(page_dir)

    print("Power BI dashboard source updated successfully.")
    print(f"Backup: {backup}")
    print(f"Page: {page_dir.name} -> Executive Overview")
    print("Visuals created: Executive KPIs, Monthly Revenue Trend, Top Countries, Top Products")
    print("\nNext: reopen powerbi/ecommerce_dashboard.pbip in Power BI Desktop.")


if __name__ == "__main__":
    main()
