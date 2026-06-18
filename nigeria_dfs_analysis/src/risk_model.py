"""
src/risk_model.py
=================
Risk assessment framework for Nigeria's DFS sector.

What it does
------------
- Defines a structured risk registry with probability and impact scores.
- Computes a risk priority score (P × I).
- Categorises risks by tier (Low / Medium / High / Critical).
- Returns DataFrames suitable for heatmap visualisation and report tables.

Risk categories scored on a 1–5 scale:
  Probability: 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost certain
  Impact:      1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Catastrophic

Risk score = Probability × Impact (max 25)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import cfg

_RISK_CFG = cfg["risk_assessment"]

# ── Risk registry ─────────────────────────────────────────────────────────────
# All risks are researched from public sources:
# - CBN regulatory announcements
# - IMF/World Bank Nigeria risk assessments
# - EFInA sector reports
# - GSMA cybersecurity reports

_RISK_REGISTRY = [
    # (category, risk_name, description, probability, impact, mitigation)
    (
        "Regulatory",
        "CBN Licensing Denial",
        "CBN may deny or delay Payment Service Bank / Fintech licence",
        3, 5,
        "Early pre-application engagement with CBN Innovation Lab; appoint CBN-experienced compliance officer",
    ),
    (
        "Regulatory",
        "Stricter Data Localisation",
        "NDPR or new CBN regulation mandating stricter Nigerian data residency",
        3, 3,
        "Build infrastructure on Nigerian cloud nodes (AWS Lagos, Azure West Africa) from day one",
    ),
    (
        "Macroeconomic",
        "NGN Devaluation / FX Volatility",
        "Continued naira devaluation erodes USD-equivalent revenue and investment return",
        5, 4,
        "Revenue in NGN; funding in USD with natural hedge strategy; FX risk disclosed to investors",
    ),
    (
        "Macroeconomic",
        "Inflation & Purchasing Power Erosion",
        "High inflation reduces consumer discretionary spend on financial products",
        4, 3,
        "Target essential payment services (utility bills, transport, remittances) which are less elastic",
    ),
    (
        "Competitive",
        "Incumbent Telco Dominance",
        "MTN MoMo or Airtel Money achieve network effect lock-in before entrant scales",
        3, 4,
        "Partner with Tier-2 telcos; focus on underserved segments not yet captured by telco wallets",
    ),
    (
        "Competitive",
        "Moniepoint / OPay Price War",
        "Established players cut transaction fees to zero to defend market share",
        3, 3,
        "Differentiate on product depth (lending, insurance, savings) rather than transaction fee price",
    ),
    (
        "Technology",
        "Cybersecurity / Fraud Incident",
        "Major data breach or fraud incident undermines user trust and triggers CBN sanctions",
        2, 5,
        "ISO 27001 certification; dedicated fraud team; mandatory MFA; bug bounty programme",
    ),
    (
        "Technology",
        "API / NIBSS Downtime",
        "Dependency on NIBSS or CBN payment infrastructure causes service outages",
        3, 3,
        "Multi-bank settlement redundancy; SLA agreements; in-app service status page",
    ),
    (
        "Operational",
        "Agent Network Quality Control",
        "Agent fraud or poor user experience damages brand in target communities",
        3, 4,
        "Tiered agent KYC; real-time monitoring dashboard; performance bonuses for compliant agents",
    ),
    (
        "Operational",
        "Customer Acquisition Cost Escalation",
        "Competitive market drives CAC above unit economics threshold",
        3, 3,
        "Referral programme; SME B2B2C channel; USSD fallback for feature-phone users",
    ),
    (
        "Credit",
        "Non-Performing Loan Spike",
        "Lending book NPL ratio exceeds 10% due to lack of credit bureau coverage",
        3, 4,
        "Conservative LTV ratios in Y1; leverage CBN Credit Risk Management System (CRMS); alternative data scoring",
    ),
    (
        "Geopolitical",
        "Insecurity in Target Regions",
        "Security incidents in North-East / North-West reduce addressable agent footprint",
        3, 2,
        "Initial focus on South-West, South-East, and FCT; phased North expansion with security assessment",
    ),
]


def build_risk_registry() -> pd.DataFrame:
    """
    Build the full risk registry DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: category, risk_name, description, probability, impact,
                 risk_score, risk_tier, mitigation
    """
    rows = []
    for cat, name, desc, prob, impact, mitigation in _RISK_REGISTRY:
        score = prob * impact
        tier  = _score_to_tier(score)
        rows.append({
            "Category":    cat,
            "Risk":        name,
            "Description": desc,
            "Probability": prob,
            "Impact":      impact,
            "Risk Score":  score,
            "Risk Tier":   tier,
            "Mitigation":  mitigation,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Risk Score", ascending=False).reset_index(drop=True)
    return df


def _score_to_tier(score: int) -> str:
    """Map a risk score (1–25) to a tier label."""
    thresholds = _RISK_CFG["risk_thresholds"]
    if score <= thresholds["low"][1]:
        return "Low"
    elif score <= thresholds["medium"][1]:
        return "Medium"
    elif score <= thresholds["high"][1]:
        return "High"
    else:
        return "Critical"


def risk_heatmap_matrix() -> pd.DataFrame:
    """
    Build a 5×5 risk heatmap matrix (Probability × Impact) for visualisation.

    Returns
    -------
    pd.DataFrame
        5×5 DataFrame where each cell = number of risks at that (P, I) coordinate.
    """
    df = build_risk_registry()

    matrix = np.zeros((5, 5), dtype=int)
    for _, row in df.iterrows():
        p = int(row["Probability"]) - 1
        i = int(row["Impact"]) - 1
        matrix[p][i] += 1

    df_matrix = pd.DataFrame(
        matrix,
        index=[f"P{i+1}" for i in range(5)],
        columns=[f"I{i+1}" for i in range(5)],
    )
    return df_matrix


def strategic_opportunities() -> pd.DataFrame:
    """
    Return the prioritised strategic opportunity set.

    Each opportunity is scored by Market Attractiveness (1–5) and
    Competitive Advantage Potential (1–5) to create a priority matrix.

    Returns
    -------
    pd.DataFrame
    """
    opportunities = [
        (
            "Rural Agent Network Expansion",
            "Deploy a localised agent banking network in under-served LGAs outside Lagos/Abuja",
            5, 3,
            "EFInA 2023: 26M adults remain financially excluded; most are rural",
            "Q1–Q4 Year 1",
        ),
        (
            "BNPL / Nano-lending for SMEs",
            "Short-term (14–30 day) credit products using alternative data scoring",
            4, 4,
            "CBN reports 60% of SME credit demand is unmet by commercial banks",
            "Q3 Year 1 – Q2 Year 2",
        ),
        (
            "Diaspora Remittance Corridor",
            "Lower-cost NGA/UK and NGA/US remittance product leveraging CBN IMTOs framework",
            4, 3,
            "World Bank: Nigeria received $20B in remittances in 2022 — 2nd largest in Africa",
            "Q2 Year 2",
        ),
        (
            "Embedded Insurance (Micro-products)",
            "Partner with AIICO or Leadway to offer airtime-billed micro-insurance at point of payment",
            3, 4,
            "NAICOM: insurance penetration <1% of GDP — one of lowest in Africa",
            "Q4 Year 2",
        ),
        (
            "USSD / Feature-Phone Access",
            "USSD-based wallet for users without smartphones — addresses 60% of Nigerians",
            5, 3,
            "GSMA 2023: only 40% smartphone penetration in Nigeria",
            "Q1 Year 1 (must-have at launch)",
        ),
    ]

    rows = []
    for name, desc, attractiveness, advantage, evidence, timeline in opportunities:
        priority = attractiveness * advantage
        rows.append({
            "Opportunity":             name,
            "Description":             desc,
            "Market Attractiveness":   attractiveness,
            "Comp. Advantage Pot.":   advantage,
            "Priority Score":          priority,
            "Supporting Evidence":     evidence,
            "Recommended Timeline":    timeline,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Priority Score", ascending=False).reset_index(drop=True)
    return df
