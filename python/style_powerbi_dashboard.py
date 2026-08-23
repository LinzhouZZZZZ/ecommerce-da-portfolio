"""Apply a polished dark portfolio style to the Power BI Executive Overview page.

Run from the repository root with Power BI Desktop CLOSED:
    python python/style_powerbi_dashboard.py

This script only changes PBIR presentation settings. It does not change data,
DAX measures, filters, or ranking logic.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POWERBI_DIR = ROOT / "powerbi"
REPORT_DEF = POWERBI_DIR / "ecommerce_dashboard.Report" / "definition"
PAGES_META = REPORT_DEF / "pages" / "pages.json"
BACKUP_ROOT = POWERBI_DIR / ".pbir_backups"

# Portfolio palette
PAGE_BG = "#0B1220"
CARD_BG = "#111827"
KPI_TILE_BG = "#172033"
BORDER = "#243044"
GRID = "#263449"
TEXT = "#F8FAFC"
TEXT_SOFT = "#CBD5E1"
MUTED = "#94A3B8"
BLUE = "#38BDF8"
GREEN = "#34D399"
AMBER = "#FBBF24"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def lit_bool(value: bool) -> dict:
    return {"expr": {"Literal": {"Value": "true" if value else "false"}}}


def lit_num(value: float | int) -> dict:
    return {"expr": {"Literal": {"Value": f"{value}D"}}}


def lit_int(value: int) -> dict:
    return {"expr": {"Literal": {"Value": f"{value}L"}}}


def lit_str(value: str) -> dict:
    return {"expr": {"Literal": {"Value": f"'{value}'"}}}


def solid(hex_color: str) -> dict:
    return {
        "solid": {
            "color": {
                "expr": {
                    "Literal": {
                        "Value": f"'{hex_color}'"
                    }
                }
            }
        }
    }


def backup() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_style"
    target = BACKUP_ROOT / stamp
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPORT_DEF, target / "report_definition")
    return target


def common_vco(title: str, *, title_size: int = 16) -> dict:
    """Complete visual-container formatting block.

    Background, border, padding and visualHeader are deliberately all set
    together so Power BI does not fall back to mixed container defaults.
    """
    return {
        "title": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "text": lit_str(title),
                    "fontColor": solid(TEXT),
                    "fontSize": lit_num(title_size),
                    "fontFamily": lit_str("Segoe UI Semibold"),
                    "bold": lit_bool(True),
                    "alignment": lit_str("left"),
                }
            }
        ],
        "subTitle": [
            {
                "properties": {
                    "show": lit_bool(False)
                }
            }
        ],
        "background": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "color": solid(CARD_BG),
                    "transparency": lit_num(0),
                }
            }
        ],
        "border": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "color": solid(BORDER),
                    "width": lit_num(1),
                    "radius": lit_num(14),
                }
            }
        ],
        "padding": [
            {
                "properties": {
                    "top": lit_num(12),
                    "bottom": lit_num(12),
                    "left": lit_num(14),
                    "right": lit_num(14),
                }
            }
        ],
        "visualHeader": [
            {
                "properties": {
                    "show": lit_bool(False)
                }
            }
        ],
    }


def style_page(page_path: Path) -> None:
    page = read_json(page_path)
    page["displayName"] = "Executive Overview"
    page["displayOption"] = "FitToPage"
    page["objects"] = {
        "background": [
            {
                "properties": {
                    "color": solid(PAGE_BG),
                    "transparency": lit_num(0),
                }
            }
        ],
        "outspace": [
            {
                "properties": {
                    "color": solid(PAGE_BG),
                    "transparency": lit_num(0),
                }
            }
        ],
    }
    write_json(page_path, page)


def style_kpis(path: Path) -> None:
    data = read_json(path)
    data["position"].update({
        "x": 80,
        "y": 55,
        "width": 1760,
        "height": 210,
    })

    visual = data["visual"]
    visual["visualContainerObjects"] = common_vco(
        "E-Commerce Sales Overview  ·  Dec 2010 – Dec 2011",
        title_size=22,
    )
    visual["objects"] = {
        "value": [
            {
                "properties": {
                    "fontSize": lit_num(30),
                    "fontColor": solid(TEXT),
                    "bold": lit_bool(True),
                },
                "selector": {"id": "default"},
            }
        ],
        "label": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "fontSize": lit_num(11),
                    "fontColor": solid(MUTED),
                },
                "selector": {"id": "default"},
            }
        ],
        "cardCalloutArea": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "paddingUniform": lit_int(10),
                    "rectangleRoundedCurve": lit_int(10),
                    "backgroundFillColor": solid(KPI_TILE_BG),
                    "backgroundTransparency": lit_num(0),
                }
            }
        ],
        "outline": [
            {
                "properties": {
                    "show": lit_bool(False)
                },
                "selector": {"id": "default"},
            }
        ],
        "layout": [
            {
                "properties": {
                    "style": lit_str("Table"),
                    "customizeLines": lit_bool(True),
                    "gridlineWidth": lit_num(1),
                    "gridlineColor": solid(BORDER),
                    "gridlineTransparency": lit_num(15),
                    "gridlineStyle": lit_str("solid"),
                },
                "selector": {"id": "default"},
            }
        ],
        "spacing": [
            {
                "properties": {
                    "verticalSpacing": lit_num(-3)
                },
                "selector": {"id": "default"},
            }
        ],
    }
    write_json(path, data)


def chart_vco(title: str) -> dict:
    return common_vco(title, title_size=16)


def axis_object(*, show: bool, label_color: str = MUTED, gridlines: bool = False) -> list[dict]:
    props = {
        "show": lit_bool(show),
        "fontSize": lit_num(10),
        "labelColor": solid(label_color),
        "showAxisTitle": lit_bool(False),
        "gridlineShow": lit_bool(gridlines),
    }
    if gridlines:
        props["gridlineColor"] = solid(GRID)
        props["gridlineStyle"] = lit_str("dotted")
    return [{"properties": props}]


def style_line(path: Path) -> None:
    data = read_json(path)
    data["position"].update({
        "x": 80,
        "y": 305,
        "width": 1100,
        "height": 350,
    })
    visual = data["visual"]
    visual["visualContainerObjects"] = chart_vco("Monthly Revenue Trend (£M)")
    visual["objects"] = {
        "categoryAxis": axis_object(show=True, gridlines=False),
        "valueAxis": axis_object(show=True, gridlines=True),
        "legend": [
            {"properties": {"show": lit_bool(False)}}
        ],
        "labels": [
            {"properties": {"show": lit_bool(False)}}
        ],
        "dataPoint": [
            {
                "properties": {
                    "defaultColor": solid(BLUE),
                    "transparency": lit_num(0),
                }
            }
        ],
        "lineStyles": [
            {
                "properties": {
                    "strokeWidth": lit_num(3),
                    "interpolationSmooth": lit_bool(True),
                }
            }
        ],
    }
    write_json(path, data)


def style_bar(path: Path, *, title: str, color: str, position: dict) -> None:
    data = read_json(path)
    data["position"].update(position)
    visual = data["visual"]
    visual["visualContainerObjects"] = chart_vco(title)
    visual["objects"] = {
        "categoryAxis": axis_object(show=True, label_color=TEXT_SOFT, gridlines=False),
        "valueAxis": axis_object(show=False, gridlines=False),
        "legend": [
            {"properties": {"show": lit_bool(False)}}
        ],
        "labels": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "fontSize": lit_num(10),
                    "color": solid(TEXT_SOFT),
                }
            }
        ],
        "dataPoint": [
            {
                "properties": {
                    "defaultColor": solid(color),
                    "borderShow": lit_bool(False),
                }
            }
        ],
    }
    write_json(path, data)


def main() -> None:
    if not PAGES_META.exists():
        raise SystemExit(f"Missing Power BI pages metadata: {PAGES_META}")

    pages = read_json(PAGES_META)
    page_name = pages.get("activePageName") or pages["pageOrder"][0]
    page_dir = REPORT_DEF / "pages" / page_name
    page_path = page_dir / "page.json"
    visuals = page_dir / "visuals"

    expected = {
        "executive_kpis": visuals / "executive_kpis" / "visual.json",
        "monthly_revenue_trend": visuals / "monthly_revenue_trend" / "visual.json",
        "top_countries": visuals / "top_countries" / "visual.json",
        "top_products": visuals / "top_products" / "visual.json",
    }

    missing = [name for name, path in expected.items() if not path.exists()]
    if missing:
        raise SystemExit(
            "Dashboard visuals are missing: " + ", ".join(missing) +
            ". Run build_powerbi_dashboard.py and fix_powerbi_dashboard.py first."
        )

    backup_dir = backup()
    style_page(page_path)
    style_kpis(expected["executive_kpis"])
    style_line(expected["monthly_revenue_trend"])
    style_bar(
        expected["top_countries"],
        title="Top 5 Countries by Revenue (£M)",
        color=GREEN,
        position={"x": 1220, "y": 305, "width": 620, "height": 350},
    )
    style_bar(
        expected["top_products"],
        title="Top 5 Merchandise Products by Revenue (£K)",
        color=AMBER,
        position={"x": 80, "y": 695, "width": 1760, "height": 300},
    )

    print("Power BI dashboard styling applied successfully.")
    print(f"Backup: {backup_dir}")
    print("Theme: dark portfolio")
    print("KPI card: enlarged values and dark metric tiles")
    print("Charts: dark containers, explicit £M/£K titles, portfolio colors")
    print("Next: reopen powerbi/ecommerce_dashboard.pbip in Power BI Desktop.")


if __name__ == "__main__":
    main()
