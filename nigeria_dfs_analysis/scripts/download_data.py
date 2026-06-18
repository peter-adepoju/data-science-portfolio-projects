"""
scripts/download_data.py
========================
Download and cache all public datasets used in this project.

Run:
    python scripts/download_data.py

What this script does
---------------------
1. Downloads World Bank Development Indicators via the wbdata API.
2. Creates the structured CBN payment dataset from hardcoded public values.
3. Creates the EFInA survey summary from hardcoded public values.
4. Creates the competitor benchmarking dataset from public sources.

All data is saved to data/raw/ and data/external/.

Notes
-----
- The World Bank API requires internet access.
- CBN, EFInA, and competitor data are pre-structured from public reports
  (no live API; the structured CSVs are created on first run).
- Expected runtime: 1–3 minutes (mostly network time for WB API).
"""

import sys
from pathlib import Path

# Make src/ importable from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import get_path
from src.data_loader import (
    download_wb_indicators,
    load_cbn_payments,
    load_efina_summary,
    load_competitors,
)


def main():
    print("=" * 60)
    print("Nigeria DFS Market Analysis — Data Download")
    print("=" * 60)

    # ── 1. World Bank indicators ─────────────────────────────────────────────
    print("\n[1/4] Downloading World Bank Development Indicators...")
    try:
        df_wb = download_wb_indicators(cache=True)
        print(f"  Downloaded: {len(df_wb):,} rows, {df_wb['indicator'].nunique()} indicators")
        print(f"  Countries : {sorted(df_wb['country'].unique()) if 'country' in df_wb.columns else 'see file'}")
    except Exception as exc:
        print(f"  ERROR downloading WB data: {exc}")
        print("  If wbdata is not installed: pip install wbdata")
        print("  Continuing — other datasets will still be created.")

    # ── 2. CBN payments dataset ──────────────────────────────────────────────
    print("\n[2/4] Creating CBN payment system dataset...")
    df_cbn = load_cbn_payments()
    print(f"  Created: {len(df_cbn)} rows")
    print(df_cbn[["year", "nip_volume_m", "nip_value_bn_ngn"]].to_string(index=False))

    # ── 3. EFInA summary ────────────────────────────────────────────────────
    print("\n[3/4] Creating EFInA financial inclusion summary...")
    df_efina = load_efina_summary()
    print(f"  Created: {len(df_efina)} rows")
    print(df_efina[["year", "banked_pct", "excluded_pct"]].to_string(index=False))

    # ── 4. Competitor dataset ────────────────────────────────────────────────
    print("\n[4/4] Creating competitor benchmarking dataset...")
    df_comp = load_competitors()
    print(f"  Created: {len(df_comp)} rows")
    print(df_comp[["company", "type", "reported_users_m", "funding_usd_m"]].to_string(index=False))

    print("\n" + "=" * 60)
    print("Data download complete.")
    print(f"Raw data saved to    : {get_path('data_raw')}")
    print(f"External data saved  : {get_path('data_external')}")
    print("\nNext step: open notebooks/02_data_loading_and_first_inspection.ipynb")
    print("=" * 60)


if __name__ == "__main__":
    main()
