"""
src/market_sizing.py
====================
TAM / SAM / SOM market sizing calculations for Nigeria's digital
financial services sector.

What it does
------------
- Computes Total Addressable Market (TAM) using bottom-up methodology.
- Computes Serviceable Addressable Market (SAM) based on smartphone-
  enabled, internet-connected adults.
- Computes Serviceable Obtainable Market (SOM) for a hypothetical new
  market entrant in Years 1–3.
- Returns clean DataFrames and dictionaries suitable for report tables.

Methodology (bottom-up)
-----------------------
TAM = Total Nigerian adults (15+) × estimated annual digital transaction
      value per adult (USD).
SAM = Smartphone-owning adults with mobile internet access ×
      annual transaction value.
SOM = Realistic share of SAM capturable by a single new entrant.

All key assumptions are documented and labelled as ASSUMPTION.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from src.config import MARKET_PARAMS, FIN_MODEL_PARAMS


@dataclass
class MarketSizeResult:
    """Container for one TAM/SAM/SOM calculation result."""
    label: str
    population_m: float
    pct_of_adults: float
    avg_txn_value_usd: float
    market_size_usd_m: float
    notes: str = ""


def compute_tam_sam_som(
    params: Optional[dict] = None,
    year: int = 2023,
) -> dict[str, MarketSizeResult]:
    """
    Compute TAM, SAM, and SOM for Nigeria's DFS market.

    Parameters
    ----------
    params : dict, optional
        Override config market_sizing parameters.
    year   : int
        Reference year for the calculation (for labelling).

    Returns
    -------
    dict
        Keys: 'TAM', 'SAM', 'SOM_Y1', 'SOM_Y3'
        Values: MarketSizeResult instances.

    Notes
    -----
    All figures are in USD millions.

    Assumptions (all documented in configs/config.yaml):
    - Nigeria adults (15+): 106 million — World Bank 2023 estimate
    - Mobile internet access rate: 40% — GSMA 2023 estimate
    - Financially excluded adults: 35 million — EFInA 2023 estimate
    - Average annual digital transaction value: $850 USD — ASSUMPTION
      (estimated from CBN total e-payment value ÷ estimated active users)
    - SOM Y1 capture: 2% of SAM — ASSUMPTION
    - SOM Y3 capture: 7% of SAM — ASSUMPTION
    """
    if params is None:
        params = MARKET_PARAMS

    total_adults_m         = params["nigeria_adults_2023_m"]        # 106M
    smartphone_pct         = params["smartphone_penetration"]       # 40%
    avg_txn_usd            = params["avg_annual_txn_value_usd"]     # $850
    mobile_money_rate      = params["mobile_money_rate_2023"]       # 35%
    som_y1_rate            = params["som_capture_rate_y1"]          # 2%
    som_y3_rate            = params["som_capture_rate_y3"]          # 7%

    # ── TAM: all Nigerian adults could potentially be served ─────────────────
    tam_pop_m = total_adults_m
    tam_size  = tam_pop_m * 1e6 * avg_txn_usd / 1e6   # USD millions

    tam = MarketSizeResult(
        label="TAM",
        population_m=round(tam_pop_m, 1),
        pct_of_adults=100.0,
        avg_txn_value_usd=avg_txn_usd,
        market_size_usd_m=round(tam_size, 0),
        notes=(
            "Total Nigerian adults (15+). ASSUMPTION: every adult participates "
            "in at least one digital financial transaction annually at $850/yr."
        ),
    )

    # ── SAM: smartphone-enabled, mobile internet-connected adults ─────────────
    # ASSUMPTION: smartphone penetration ≈ mobile internet access rate (GSMA)
    sam_pop_m = total_adults_m * smartphone_pct
    sam_size  = sam_pop_m * 1e6 * avg_txn_usd / 1e6

    sam = MarketSizeResult(
        label="SAM",
        population_m=round(sam_pop_m, 1),
        pct_of_adults=round(smartphone_pct * 100, 1),
        avg_txn_value_usd=avg_txn_usd,
        market_size_usd_m=round(sam_size, 0),
        notes=(
            f"Adults with smartphone/mobile internet access ({smartphone_pct*100:.0f}%). "
            "Source: GSMA State of Mobile Internet Connectivity 2023. "
            "ASSUMPTION: all smartphone users are reachable via mobile banking."
        ),
    )

    # ── SOM Year 1 (conservative new entrant capture) ────────────────────────
    som_y1_pop = sam_pop_m * som_y1_rate
    som_y1_size = som_y1_pop * 1e6 * avg_txn_usd / 1e6

    som_y1 = MarketSizeResult(
        label="SOM_Y1",
        population_m=round(som_y1_pop, 2),
        pct_of_adults=round(som_y1_rate * smartphone_pct * 100, 2),
        avg_txn_value_usd=avg_txn_usd,
        market_size_usd_m=round(som_y1_size, 0),
        notes=(
            f"Year 1 obtainable: {som_y1_rate*100:.0f}% of SAM. "
            "ASSUMPTION based on comparable fintech launches (Kuda, Carbon Y1 user counts). "
            "Conservative estimate."
        ),
    )

    # ── SOM Year 3 (growth after 3 years of operations) ──────────────────────
    som_y3_pop = sam_pop_m * som_y3_rate
    som_y3_size = som_y3_pop * 1e6 * avg_txn_usd / 1e6

    som_y3 = MarketSizeResult(
        label="SOM_Y3",
        population_m=round(som_y3_pop, 2),
        pct_of_adults=round(som_y3_rate * smartphone_pct * 100, 2),
        avg_txn_value_usd=avg_txn_usd,
        market_size_usd_m=round(som_y3_size, 0),
        notes=(
            f"Year 3 obtainable: {som_y3_rate*100:.0f}% of SAM. "
            "ASSUMPTION: strong growth with agent network + product-market fit."
        ),
    )

    return {
        "TAM":    tam,
        "SAM":    sam,
        "SOM_Y1": som_y1,
        "SOM_Y3": som_y3,
    }


def market_sizing_table(results: dict[str, MarketSizeResult]) -> pd.DataFrame:
    """
    Convert market sizing results into a publication-ready summary table.

    Parameters
    ----------
    results : dict
        Output of compute_tam_sam_som().

    Returns
    -------
    pd.DataFrame
        Columns: Market, Population (M), % Adults, Avg Txn/User (USD),
                 Market Size (USD M), Notes
    """
    rows = []
    for key, r in results.items():
        rows.append({
            "Market":                key,
            "Population (M)":        r.population_m,
            "% of Adults":           r.pct_of_adults,
            "Avg Txn/User (USD/yr)": r.avg_txn_value_usd,
            "Market Size (USD M)":   f"${r.market_size_usd_m:,.0f}M",
            "Notes":                 r.notes,
        })
    return pd.DataFrame(rows)


def sensitivity_market_size(
    arpu_range: list[float],
    users_m_range: list[float],
) -> pd.DataFrame:
    """
    Build a 2-way sensitivity table for market size.

    Parameters
    ----------
    arpu_range  : list[float]  — annual revenue per user (USD) values to test
    users_m_range : list[float] — user base (millions) values to test

    Returns
    -------
    pd.DataFrame
        Rows = ARPU values, Columns = user base values.
        Cell values = implied annual revenue (USD millions).
    """
    rows = {}
    for arpu in arpu_range:
        row = {}
        for users_m in users_m_range:
            revenue_usd_m = (users_m * 1e6 * arpu) / 1e6
            row[f"{users_m:.1f}M users"] = f"${revenue_usd_m:,.0f}M"
        rows[f"${arpu}/user ARPU"] = row

    return pd.DataFrame(rows).T
