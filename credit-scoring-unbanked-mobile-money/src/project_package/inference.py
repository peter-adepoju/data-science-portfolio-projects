from __future__ import annotations

import pandas as pd

from .models import load_model, predict_proba_positive


def score_applications(model_filename: str, applications: pd.DataFrame) -> pd.DataFrame:
    """Scoring new applications with a saved model artifact."""
    model = load_model(model_filename)
    scores = predict_proba_positive(model, applications)
    output = applications.copy()
    output["predicted_default_probability"] = scores
    output["risk_band"] = pd.cut(
        output["predicted_default_probability"],
        bins=[-0.001, 0.10, 0.25, 0.50, 1.0],
        labels=["very_low", "low", "medium", "high"],
    )
    return output


def create_adverse_action_reasons(scored_row: pd.Series, top_features: list[str] | None = None) -> list[str]:
    """Creating simple report text for model-governance demonstrations.

    These reasons were heuristic and were not a substitute for a legally compliant
    adverse-action notice.
    """
    reasons: list[str] = []
    if scored_row.get("proxy_delinquency_count_6m", 0) >= 2:
        reasons.append("recent repayment delays were frequent")
    if scored_row.get("proxy_total_payment_to_bill_6m", 1) < 0.3:
        reasons.append("recent payments were low relative to outstanding balances")
    if scored_row.get("proxy_utilization_mean_6m", 0) > 0.8:
        reasons.append("average balance utilization was high")
    if scored_row.get("proxy_payment_consistency_6m", 1) < 0.5:
        reasons.append("payments were not consistently observed across recent months")
    if not reasons and top_features:
        reasons.extend([f"model sensitivity was high for {f}" for f in top_features[:3]])
    return reasons[:3]
