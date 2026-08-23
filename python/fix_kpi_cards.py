"""Fix KPI card contrast after applying the dark Power BI portfolio style.

Run from the repository root with Power BI Desktop CLOSED:
    python python/fix_kpi_cards.py

This only patches the Executive KPI card's internal fill and text colors.
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

KPI_TILE_BG = "#172033"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lit_bool(value: bool) -> dict:
    return {"expr": {"Literal": {"Value": "true" if value else "false"}}}


def lit_num(value: float | int) -> dict:
    return {"expr": {"Literal": {"Value": f"{value}D"}}}


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


def main() -> None:
    if not PAGES_META.exists():
        raise SystemExit(f"Missing Power BI pages metadata: {PAGES_META}")

    pages = read_json(PAGES_META)
    page_name = pages.get("activePageName") or pages["pageOrder"][0]
    visual_path = (
        REPORT_DEF
        / "pages"
        / page_name
        / "visuals"
        / "executive_kpis"
        / "visual.json"
    )

    if not visual_path.exists():
        raise SystemExit(
            "Executive KPI visual not found. Run build/fix/style scripts first."
        )

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_kpi_fix"
    backup_dir = BACKUP_ROOT / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(visual_path, backup_dir / "executive_kpis.visual.json")

    data = read_json(visual_path)
    visual = data["visual"]
    objects = visual.setdefault("objects", {})

    # The modern card visual needs fillCustom with the default instance selector
    # to prevent the internal cards from inheriting the light-theme white fill.
    objects["fillCustom"] = [
        {
            "properties": {
                "show": lit_bool(True),
                "fillColor": solid(KPI_TILE_BG),
            },
            "selector": {"id": "default"},
        }
    ]

    # Keep explicit high-contrast typography on the dark KPI tiles.
    objects["value"] = [
        {
            "properties": {
                "fontSize": lit_num(30),
                "fontColor": solid(TEXT),
                "bold": lit_bool(True),
            },
            "selector": {"id": "default"},
        }
    ]
    objects["label"] = [
        {
            "properties": {
                "show": lit_bool(True),
                "fontSize": lit_num(11),
                "fontColor": solid(MUTED),
            },
            "selector": {"id": "default"},
        }
    ]

    write_json(visual_path, data)

    print("KPI card contrast fix applied successfully.")
    print(f"Backup: {backup_dir}")
    print("KPI tiles: dark fill via fillCustom")
    print("KPI values: high-contrast light text")
    print("Next: reopen powerbi/ecommerce_dashboard.pbip in Power BI Desktop.")


if __name__ == "__main__":
    main()
