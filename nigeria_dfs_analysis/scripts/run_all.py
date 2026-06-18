"""
scripts/run_all.py
==================
Execute the full project pipeline end-to-end.

Run:
    python scripts/run_all.py

What this does
--------------
1. Downloads all data (World Bank API + structured external datasets).
2. Executes all notebooks in order via nbconvert.
3. Reports success / failure per step.

Expected runtime: 15–40 minutes depending on internet speed and machine.
CPU only — no GPU required.

Notes
-----
- All notebooks must be run in order (00 → 13) because each saves
  processed files that the next notebook loads.
- If a notebook fails, execution stops and the error is printed.
- Re-running is idempotent: cached data is reused, figures overwritten.
"""

import subprocess
import sys
import time
from pathlib import Path

# Project root is one level up from scripts/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

NOTEBOOK_ORDER = [
    "00_project_overview_and_business_question.ipynb",
    "01_dataset_selection_and_access.ipynb",
    "02_data_loading_and_first_inspection.ipynb",
    "03_data_quality_checks.ipynb",
    "04_data_cleaning_and_feature_engineering.ipynb",
    "05_exploratory_analysis.ipynb",
    "06_market_sizing_tam_sam_som.ipynb",
    "07_competitive_landscape.ipynb",
    "08_financial_modelling_and_valuation.ipynb",
    "09_risk_assessment_framework.ipynb",
    "10_statistical_inference.ipynb",
    "11_robustness_checks.ipynb",
    "12_publication_figures_and_tables.ipynb",
    "13_limitations_and_next_steps.ipynb",
]


def run_step(label: str, cmd: list[str]) -> bool:
    """Run a shell command, print output, return True on success."""
    print(f"\n{'─'*60}")
    print(f"  STEP: {label}")
    print(f"{'─'*60}")
    start = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True, cwd=PROJECT_ROOT)
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"  ✓ Done in {elapsed:.1f}s")
        return True
    else:
        print(f"  ✗ FAILED (exit code {result.returncode})")
        return False


def main():
    print("=" * 60)
    print("Nigeria DFS Market Analysis — Full Pipeline")
    print("=" * 60)
    print(f"Project root: {PROJECT_ROOT}")

    results = {}

    # ── Step 0: Download data ────────────────────────────────────────────────
    ok = run_step(
        "Download all datasets",
        [sys.executable, str(PROJECT_ROOT / "scripts" / "download_data.py")],
    )
    results["data_download"] = ok

    # ── Steps 1–N: Execute notebooks in order ────────────────────────────────
    for nb_name in NOTEBOOK_ORDER:
        nb_path = NOTEBOOKS_DIR / nb_name
        if not nb_path.exists():
            print(f"\n  WARNING: Notebook not found — {nb_path}. Skipping.")
            results[nb_name] = None
            continue

        ok = run_step(
            nb_name,
            [
                sys.executable, "-m", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--inplace",
                "--ExecutePreprocessor.timeout=600",
                str(nb_path),
            ],
        )
        results[nb_name] = ok
        if not ok:
            print("\n  Pipeline stopped due to notebook failure.")
            print("  Fix the error above and re-run this script.")
            break

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    passed = sum(v for v in results.values() if v is True)
    failed = sum(v is False for v in results.values())
    skipped = sum(v is None for v in results.values())
    for name, ok in results.items():
        icon = "✓" if ok else ("✗" if ok is False else "–")
        print(f"  {icon}  {name}")
    print(f"\n  Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

    if failed == 0 and skipped == 0:
        print("\n  All steps completed successfully.")
        print("  Open reports/ for figures and tables.")
        print("  Run: streamlit run dashboard/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
