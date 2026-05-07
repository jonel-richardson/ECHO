"""Generate frontend/data/hospitals_ny_tx.json from the CMS Birthing-Friendly CSV.

Reads backend/data/cms_birthing_friendly_geocoded.csv, filters to NY and TX rows,
sorts each state's hospitals alphabetically by name, deduplicates by name (keeps
first occurrence), and writes the result to frontend/data/hospitals_ny_tx.json.

Output shape:
    {
      "NY": [{"name": "...", "birthing_friendly": true}, ...],
      "TX": [{"name": "...", "birthing_friendly": true}, ...]
    }

Every row in the source CSV is from the Birthing-Friendly designation list, so
birthing_friendly is always true here. The field is preserved for forward
compatibility if a future v3 cross-references a non-designated hospital list.

Run from repo root:
    python scripts/generate_hospitals_json.py
"""

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "backend" / "data" / "cms_birthing_friendly_geocoded.csv"
OUTPUT_PATH = REPO_ROOT / "frontend" / "data" / "hospitals_ny_tx.json"
SUPPORTED_STATES = ("NY", "TX")


def build_hospitals_by_state() -> Dict[str, List[Dict[str, object]]]:
    df = pd.read_csv(CSV_PATH)
    result: Dict[str, List[Dict[str, object]]] = {}
    for state in SUPPORTED_STATES:
        rows = df[df["state"] == state].copy()
        rows["name"] = rows["name"].astype(str).str.strip()
        rows = rows[rows["name"] != ""]
        rows = rows.drop_duplicates(subset=["name"], keep="first")
        rows = rows.sort_values("name", key=lambda s: s.str.lower(), kind="stable")
        result[state] = [
            {"name": name, "birthing_friendly": True}
            for name in rows["name"].tolist()
        ]
    return result


def main() -> None:
    hospitals_by_state = build_hospitals_by_state()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(hospitals_by_state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    counts = ", ".join(
        f"{state}={len(hospitals_by_state[state])}" for state in SUPPORTED_STATES
    )
    print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} ({counts})")


if __name__ == "__main__":
    main()
