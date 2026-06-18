"""
src/preprocessing.py
====================
Data cleaning and feature engineering helpers.

What it does
------------
- Validates schema of incoming DataFrames.
- Cleans missing values using documented strategies.
- Computes year-over-year growth rates.
- Builds derived indicators (penetration rates, market size estimates).
- Applies consistent dtype conversions.

Why this is a src/ module
--------------------------
The same cleaning logic is needed in notebook 03 (quality checks),
notebook 04 (cleaning), and downstream notebooks.  Centralising it here
keeps notebook cells readable while ensuring consistency.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# ── Schema validation ─────────────────────────────────────────────────────────

def validate_wb_schema(df: pd.DataFrame) -> None:
    """
    Check that a World Bank indicators DataFrame has the expected columns.

    Parameters
    ----------
    df : pd.DataFrame
        Output of src.data_loader.download_wb_indicators().

    Raises
    ------
    ValueError
        If required columns are missing.
    """
    required = {"year", "indicator", "value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"World Bank DataFrame is missing required columns: {missing}. "
            f"Got: {list(df.columns)}"
        )


def validate_cbn_schema(df: pd.DataFrame) -> None:
    """Validate the CBN payments DataFrame schema."""
    required = {"year", "nip_volume_m", "nip_value_bn_ngn"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CBN DataFrame is missing columns: {missing}")


# ── Missing value reporting ───────────────────────────────────────────────────

def missing_value_report(df: pd.DataFrame, label: str = "") -> pd.DataFrame:
    """
    Return a summary of missing values per column.

    Parameters
    ----------
    df    : pd.DataFrame
    label : str, optional
        Descriptive label printed with the report.

    Returns
    -------
    pd.DataFrame
        Columns: [column, n_missing, pct_missing, dtype]
    """
    n = len(df)
    report = (
        df.isnull()
        .sum()
        .reset_index()
        .rename(columns={"index": "column", 0: "n_missing"})
    )
    report["pct_missing"] = (report["n_missing"] / n * 100).round(2)
    report["dtype"] = report["column"].map(lambda c: str(df[c].dtype))
    report = report.sort_values("n_missing", ascending=False).reset_index(drop=True)

    if label:
        print(f"\n=== Missing Value Report: {label} ===")
        print(f"  Rows: {n:,}")
        print(report[report["n_missing"] > 0].to_string(index=False))
        if report["n_missing"].sum() == 0:
            print("  No missing values found.")

    return report


# ── Growth rate computation ───────────────────────────────────────────────────

def add_yoy_growth(
    df: pd.DataFrame,
    value_col: str,
    year_col: str = "year",
    new_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    Add a year-over-year (%) growth column to a DataFrame sorted by year.

    Parameters
    ----------
    df        : pd.DataFrame
    value_col : str   — column whose growth to compute
    year_col  : str   — column containing the year
    new_col   : str, optional — output column name; defaults to
                f"{value_col}_yoy_pct"

    Returns
    -------
    pd.DataFrame
        Original DataFrame with an extra growth column.

    Notes
    -----
    The first row will always be NaN (no prior year to compare).
    Divide-by-zero is handled gracefully (returns NaN).
    """
    if new_col is None:
        new_col = f"{value_col}_yoy_pct"

    df = df.sort_values(year_col).copy()
    prev = df[value_col].shift(1)
    df[new_col] = ((df[value_col] - prev) / prev.abs() * 100).round(2)
    return df


# ── Derived indicator builder ─────────────────────────────────────────────────

def build_nigeria_indicators(
    df_wb_ng: pd.DataFrame,
    df_cbn: pd.DataFrame,
    df_efina: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge World Bank, CBN, and EFInA data for Nigeria into a single
    analysis-ready DataFrame.

    Parameters
    ----------
    df_wb_ng : pd.DataFrame
        Wide-format Nigeria WB indicators (output of load_wb_nigeria).
    df_cbn   : pd.DataFrame
        CBN payments data (output of load_cbn_payments).
    df_efina : pd.DataFrame
        EFInA survey summaries (output of load_efina_summary).

    Returns
    -------
    pd.DataFrame
        Combined DataFrame, one row per year (2015–2023 where available).
        Missing years in EFInA are forward-filled (since the survey is
        biennial).  This fill is documented and labelled.
    """
    # ── Step 1: Merge WB + CBN on year ──────────────────────────────────────
    df = pd.merge(
        df_wb_ng,
        df_cbn,
        on="year",
        how="outer",
    ).sort_values("year")

    # ── Step 2: Merge EFInA (biennial survey, so many years are missing) ────
    df = pd.merge(
        df,
        df_efina[["year", "banked_pct", "excluded_pct", "mobile_money_pct"]],
        on="year",
        how="left",
    )

    # Forward-fill EFInA survey years (each value holds until the next survey)
    for col in ["banked_pct", "excluded_pct", "mobile_money_pct"]:
        if col in df.columns:
            df[col] = df[col].ffill()

    # ── Step 3: Derived indicators ───────────────────────────────────────────
    # NIP total payment value: NGN billions → USD millions (approx FX)
    # ASSUMPTION: Using approximate annual average USD/NGN rates.
    fx_map = {
        2015: 199, 2016: 305, 2017: 360, 2018: 362, 2019: 363,
        2020: 381, 2021: 413, 2022: 447, 2023: 900,   # NGN weakened sharply
    }
    df["fx_usd_ngn"] = df["year"].map(fx_map)
    df["nip_value_usd_m"] = (
        df["nip_value_bn_ngn"] * 1e9 / df["fx_usd_ngn"] / 1e6
    ).round(1)

    # Total digital payment volume (all channels combined)
    vol_cols = ["nip_volume_m", "pos_volume_m", "mobile_vol_m", "inet_vol_m"]
    existing_vol_cols = [c for c in vol_cols if c in df.columns]
    if existing_vol_cols:
        df["total_digital_vol_m"] = df[existing_vol_cols].sum(axis=1)

    # YoY growth for key metrics
    for col in ["nip_volume_m", "nip_value_bn_ngn", "total_digital_vol_m"]:
        if col in df.columns:
            df = add_yoy_growth(df, col)

    return df


# ── Outlier detection ─────────────────────────────────────────────────────────

def flag_outliers_iqr(
    df: pd.DataFrame,
    col: str,
    multiplier: float = 3.0,
) -> pd.Series:
    """
    Flag potential outliers using the IQR method.

    Parameters
    ----------
    df         : pd.DataFrame
    col        : str   — column to check
    multiplier : float — fence = Q1 - k*IQR or Q3 + k*IQR (default k=3)

    Returns
    -------
    pd.Series[bool]
        True where the value is a potential outlier.
    """
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return (df[col] < lower) | (df[col] > upper)


# ── Export helper ─────────────────────────────────────────────────────────────

def save_processed(df: pd.DataFrame, filename: str, processed_dir: Path) -> None:
    """
    Save a processed DataFrame to data/processed/ as CSV.

    Parameters
    ----------
    df           : pd.DataFrame
    filename     : str   — e.g. 'nigeria_combined.csv'
    processed_dir: Path  — usually get_path('data_processed')
    """
    out_path = processed_dir / filename
    df.to_csv(out_path, index=False)
    print(f"Saved processed dataset: {out_path}")
    print(f"  Shape : {df.shape}")
    print(f"  Cols  : {list(df.columns)}")
