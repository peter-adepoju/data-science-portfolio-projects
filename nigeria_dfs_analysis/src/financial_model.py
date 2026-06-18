"""
src/financial_model.py
======================
Three-year revenue projection, P&L model, sensitivity analysis,
and comparable-company valuation for a hypothetical DFS market entrant.

What it does
------------
1. Builds a 3-year user growth and revenue projection from first-principles
   assumptions documented in configs/config.yaml.
2. Constructs a simplified Income Statement (Revenue → EBITDA → Net Income).
3. Runs a 2-variable sensitivity analysis (ARPU × User Base).
4. Estimates an implied company valuation using EV/Revenue multiples
   from comparable listed/valued African fintechs.
5. Exports the model to Excel (data/processed/financial_model.xlsx).

All assumptions are documented.
No results are fabricated — this is a forward-looking model, not
a back-tested historical claim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.config import FIN_MODEL_PARAMS, VIZ_PARAMS


# ── User growth model ─────────────────────────────────────────────────────────

def project_users(params: Optional[dict] = None) -> pd.DataFrame:
    """
    Project active user base over 3 years.

    Parameters
    ----------
    params : dict, optional
        Override config financial_model parameters.

    Returns
    -------
    pd.DataFrame
        Columns: year, new_users, churned_users, active_users
    """
    if params is None:
        params = FIN_MODEL_PARAMS

    base_users = params["user_base_y1"]          # 500,000
    g2         = params["user_growth_rate_y2"]   # 80%
    g3         = params["user_growth_rate_y3"]   # 60%
    churn      = params["churn_rate"]            # 18%

    records = []
    active = base_users

    for year, growth in [(1, None), (2, g2), (3, g3)]:
        if year == 1:
            new_users = base_users
        else:
            # New users acquired this year (gross)
            new_users = int(active * growth)

        churned = int(active * churn)
        if year == 1:
            churned = int(base_users * churn)    # partial-year churn in Y1

        active = (active + new_users - churned) if year > 1 else base_users
        records.append({
            "year":         year,
            "new_users":    new_users,
            "churned_users": churned,
            "active_users": active,
        })
        if year > 1:
            active = records[-1]["active_users"]

    return pd.DataFrame(records)


def project_revenue(
    df_users: pd.DataFrame,
    params: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Project revenue by stream over 3 years.

    Parameters
    ----------
    df_users : pd.DataFrame  — output of project_users()
    params   : dict, optional

    Returns
    -------
    pd.DataFrame
        Columns: year, active_users, arpu_usd, total_revenue_usd_m,
                 txn_fees_usd_m, float_income_usd_m, lending_usd_m,
                 subscription_usd_m
    """
    if params is None:
        params = FIN_MODEL_PARAMS

    arpu_base   = params["arpu_usd_y1"]          # $12 ARPU in Year 1
    arpu_growth = params["arpu_growth_rate"]      # 15% per year
    mix         = params["revenue_mix"]

    records = []
    for _, row in df_users.iterrows():
        yr = int(row["year"])
        arpu = arpu_base * ((1 + arpu_growth) ** (yr - 1))
        total_rev = row["active_users"] * arpu / 1e6   # → USD millions

        records.append({
            "year":                  yr,
            "active_users":          int(row["active_users"]),
            "arpu_usd":              round(arpu, 2),
            "total_revenue_usd_m":   round(total_rev, 3),
            "txn_fees_usd_m":        round(total_rev * mix["transaction_fees_pct"], 3),
            "float_income_usd_m":    round(total_rev * mix["float_income_pct"], 3),
            "lending_usd_m":         round(total_rev * mix["lending_pct"], 3),
            "subscription_usd_m":    round(total_rev * mix["subscription_pct"], 3),
        })

    return pd.DataFrame(records)


def project_income_statement(
    df_revenue: pd.DataFrame,
    params: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Build a simplified 3-year Income Statement (P&L).

    Parameters
    ----------
    df_revenue : pd.DataFrame  — output of project_revenue()
    params     : dict, optional

    Returns
    -------
    pd.DataFrame
        Columns: year, revenue, cogs, gross_profit, personnel, tech_infra,
                 marketing, regulatory, other_opex, total_opex, ebitda,
                 ebitda_margin_pct, net_income (simplified, no D&A or tax)
    """
    if params is None:
        params = FIN_MODEL_PARAMS

    opex = params["opex"]

    records = []
    for _, row in df_revenue.iterrows():
        rev = row["total_revenue_usd_m"]

        cogs          = rev * opex["cost_of_revenue_pct"]
        gross_profit  = rev - cogs

        personnel     = rev * opex["personnel_pct"]
        tech_infra    = rev * opex["tech_infrastructure_pct"]
        marketing     = rev * opex["marketing_pct"]
        regulatory    = rev * opex["regulatory_compliance_pct"]
        other         = rev * opex["other_pct"]
        total_opex    = personnel + tech_infra + marketing + regulatory + other

        ebitda        = gross_profit - total_opex
        ebitda_margin = (ebitda / rev * 100) if rev > 0 else 0

        records.append({
            "year":               int(row["year"]),
            "revenue_usd_m":      round(rev, 3),
            "cogs_usd_m":         round(cogs, 3),
            "gross_profit_usd_m": round(gross_profit, 3),
            "personnel_usd_m":    round(personnel, 3),
            "tech_infra_usd_m":   round(tech_infra, 3),
            "marketing_usd_m":    round(marketing, 3),
            "regulatory_usd_m":   round(regulatory, 3),
            "other_opex_usd_m":   round(other, 3),
            "total_opex_usd_m":   round(total_opex, 3),
            "ebitda_usd_m":       round(ebitda, 3),
            "ebitda_margin_pct":  round(ebitda_margin, 1),
        })

    return pd.DataFrame(records)


# ── Sensitivity analysis ──────────────────────────────────────────────────────

def sensitivity_revenue(
    arpu_values: list[float],
    user_base_y3_values: list[float],
) -> pd.DataFrame:
    """
    2-variable sensitivity table: ARPU (rows) × Year-3 user base (columns).

    Parameters
    ----------
    arpu_values        : list[float]  — ARPU to test (USD)
    user_base_y3_values: list[float]  — Year-3 active user count to test

    Returns
    -------
    pd.DataFrame
        Rows = ARPU, Columns = user count.
        Cells = implied Year-3 revenue in USD millions.
    """
    rows = {}
    for arpu in arpu_values:
        row = {}
        for users in user_base_y3_values:
            rev_m = (users * arpu) / 1e6
            row[f"{users/1e6:.1f}M users"] = round(rev_m, 2)
        rows[f"${arpu:.0f} ARPU"] = row

    return pd.DataFrame(rows).T


def sensitivity_ebitda(
    arpu_values: list[float],
    cogs_pct_values: list[float],
    base_users_y3: int = 2_000_000,
) -> pd.DataFrame:
    """
    2-variable sensitivity: ARPU (rows) × COGS % (columns) → EBITDA margin.

    Parameters
    ----------
    arpu_values      : list[float]
    cogs_pct_values  : list[float]  — COGS as % of revenue
    base_users_y3    : int          — assumed Y3 active users

    Returns
    -------
    pd.DataFrame
        Rows = ARPU, Columns = COGS %, Cells = EBITDA margin (%).
    """
    params = FIN_MODEL_PARAMS.copy()
    opex   = params["opex"]
    fixed_opex_pct = (
        opex["personnel_pct"]
        + opex["tech_infrastructure_pct"]
        + opex["marketing_pct"]
        + opex["regulatory_compliance_pct"]
        + opex["other_pct"]
    )

    rows = {}
    for arpu in arpu_values:
        row = {}
        for cogs_pct in cogs_pct_values:
            rev = base_users_y3 * arpu / 1e6
            gross = rev * (1 - cogs_pct)
            ebitda = gross - rev * fixed_opex_pct
            margin = (ebitda / rev * 100) if rev > 0 else 0
            row[f"COGS {cogs_pct*100:.0f}%"] = round(margin, 1)
        rows[f"${arpu:.0f} ARPU"] = row

    return pd.DataFrame(rows).T


# ── Comparable company valuation ─────────────────────────────────────────────

def comparable_valuation(y3_revenue_usd_m: float) -> pd.DataFrame:
    """
    Estimate implied company value using EV/Revenue multiples from
    comparable African fintech companies.

    Sources for multiples:
    - MTN MoMo: ~5x revenue multiple (MTN Group annual report 2023)
    - Flutterwave: ~8x revenue (last funding round valuation vs disclosed ARR)
    - Interswitch: ~6x revenue (pre-IPO estimates, financial press)
    - PalmPay: ~4x (funding round vs disclosed GMV estimate)
    These are APPROXIMATIONS from public sources and analyst estimates.
    Use with significant caution.

    Parameters
    ----------
    y3_revenue_usd_m : float  — Year-3 projected revenue in USD millions

    Returns
    -------
    pd.DataFrame
        Columns: Company, EV/Rev Multiple, Implied EV (USD M),
                 Notes
    """
    comparables = [
        # (company, ev_rev_multiple, source_note)
        ("MTN MoMo (listed)",        5.0,
         "MTN Group Annual Report 2023 — mobile money segment"),
        ("Interswitch (pre-IPO est.)", 6.0,
         "Analyst estimates from financial press — APPROXIMATION"),
        ("Flutterwave (last round)",  8.0,
         "Last disclosed funding round vs estimated ARR — APPROXIMATION"),
        ("PalmPay (conservative)",    4.0,
         "Funding round valuation vs estimated GMV — APPROXIMATION"),
        ("Sector median",             5.5,
         "Median of above comparables"),
    ]

    records = []
    for company, multiple, note in comparables:
        implied_ev = y3_revenue_usd_m * multiple
        records.append({
            "Comparable Company":      company,
            "EV/Revenue Multiple":     f"{multiple:.1f}x",
            "Implied EV (USD M)":      f"${implied_ev:,.1f}M",
            "Implied EV (NGN B)":      f"₦{implied_ev * 1500 / 1000:.1f}B",  # approx FX
            "Source Notes":            note,
        })

    return pd.DataFrame(records)


# ── Excel export ──────────────────────────────────────────────────────────────

def export_to_excel(
    df_users: pd.DataFrame,
    df_revenue: pd.DataFrame,
    df_pnl: pd.DataFrame,
    df_sensitivity: pd.DataFrame,
    df_valuation: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Export the complete financial model to a formatted Excel workbook.

    Parameters
    ----------
    All DataFrames from the financial model functions above.
    output_path : Path  — e.g. data/processed/financial_model.xlsx
    """
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        wb = writer.book

        # Formats
        header_fmt = wb.add_format({
            "bold": True, "bg_color": "#003087", "font_color": "white",
            "border": 1,
        })
        num_fmt     = wb.add_format({"num_format": "#,##0", "border": 1})
        money_fmt   = wb.add_format({"num_format": "$#,##0.000", "border": 1})
        pct_fmt     = wb.add_format({"num_format": "0.0%", "border": 1})
        title_fmt   = wb.add_format({"bold": True, "font_size": 14})

        def write_df(df, sheet_name, title):
            df.to_excel(writer, sheet_name=sheet_name, startrow=3, index=False)
            ws = writer.sheets[sheet_name]
            ws.write(0, 0, title, title_fmt)
            ws.write(1, 0, "ASSUMPTION — All projections are forward-looking estimates.",
                     wb.add_format({"italic": True, "font_color": "#7F8C8D"}))
            ws.set_column(0, len(df.columns), 18)

        write_df(df_users,       "User_Growth",     "User Growth Projection (Years 1–3)")
        write_df(df_revenue,     "Revenue",          "Revenue Projection by Stream (USD M)")
        write_df(df_pnl,         "Income_Statement", "Simplified Income Statement (USD M)")
        write_df(df_sensitivity, "Sensitivity",      "Sensitivity Analysis: ARPU × Users")
        write_df(df_valuation,   "Valuation",        "Comparable Company Valuation")

        # Assumptions tab
        assumptions = pd.DataFrame([
            ("User base Y1",            "500,000",   "Management target"),
            ("User growth Y2",          "80%",       "ASSUMPTION — aggressive growth market"),
            ("User growth Y3",          "60%",       "ASSUMPTION"),
            ("Annual churn rate",       "18%",       "ASSUMPTION — comparable fintechs"),
            ("ARPU Y1 (USD)",           "$12",       "ASSUMPTION — see methodology note"),
            ("ARPU growth/yr",          "15%",       "ASSUMPTION"),
            ("Transaction fee split",   "55%",       "Revenue mix assumption"),
            ("Float income split",      "20%",       "Revenue mix assumption"),
            ("Lending split",           "15%",       "Revenue mix assumption"),
            ("Subscription split",      "10%",       "Revenue mix assumption"),
            ("COGS % of revenue",       "40%",       "ASSUMPTION — comparable fintechs"),
            ("Personnel % of revenue",  "25%",       "ASSUMPTION"),
            ("Tech infra %",            "10%",       "ASSUMPTION"),
            ("Marketing %",             "12%",       "ASSUMPTION"),
            ("Regulatory %",            "5%",        "CBN licensing and compliance"),
        ], columns=["Parameter", "Value", "Note"])

        assumptions.to_excel(writer, sheet_name="Assumptions", startrow=3, index=False)
        ws = writer.sheets["Assumptions"]
        ws.write(0, 0, "Financial Model Assumptions", title_fmt)
        ws.write(1, 0, "Review and validate all assumptions before client presentation.",
                 wb.add_format({"italic": True, "font_color": "#C0392B"}))
        ws.set_column(0, 2, 30)

    print(f"Financial model exported to {output_path}")
