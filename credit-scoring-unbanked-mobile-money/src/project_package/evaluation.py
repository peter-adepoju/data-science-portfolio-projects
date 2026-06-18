from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)


def classification_metrics(y_true, y_proba, threshold: float = 0.5) -> dict[str, float]:
    """Calculating discrimination, calibration, and threshold-based metrics."""
    y_true = np.asarray(y_true).astype(int)
    y_proba = np.asarray(y_proba, dtype=float)
    y_pred = (y_proba >= threshold).astype(int)
    return {
        "roc_auc": roc_auc_score(y_true, y_proba),
        "pr_auc": average_precision_score(y_true, y_proba),
        "brier_score": brier_score_loss(y_true, y_proba),
        "log_loss": log_loss(y_true, np.clip(y_proba, 1e-6, 1 - 1e-6)),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "threshold": threshold,
    }


def metrics_frame(results: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Converting model metric dictionaries into a sorted comparison table."""
    rows = []
    for model_name, metrics in results.items():
        rows.append({"model": model_name, **metrics})
    frame = pd.DataFrame(rows)
    if "pr_auc" in frame.columns:
        frame = frame.sort_values("pr_auc", ascending=False).reset_index(drop=True)
    return frame


def threshold_cost_curve(
    y_true,
    y_proba,
    false_approval_cost: float = 5.0,
    false_rejection_cost: float = 1.0,
    thresholds: np.ndarray | None = None,
) -> pd.DataFrame:
    """Computing expected business cost across decision thresholds.

    In this framing, a false approval meant predicting low risk for a borrower who
    defaulted. A false rejection meant declining a borrower who would not default.
    """
    y_true = np.asarray(y_true).astype(int)
    y_proba = np.asarray(y_proba, dtype=float)
    if thresholds is None:
        thresholds = np.linspace(0.01, 0.99, 99)
    rows = []
    for threshold in thresholds:
        # High probability meant high risk, so prediction 1 meant reject/high-risk.
        y_pred = (y_proba >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        false_approvals = fn
        false_rejections = fp
        cost = false_approval_cost * false_approvals + false_rejection_cost * false_rejections
        rows.append({
            "threshold": threshold,
            "false_approvals": false_approvals,
            "false_rejections": false_rejections,
            "total_cost": cost,
            "cost_per_applicant": cost / len(y_true),
        })
    return pd.DataFrame(rows)


def lift_table(y_true, y_proba, n_bins: int = 10) -> pd.DataFrame:
    """Creating a decile lift table for credit-risk ranking."""
    frame = pd.DataFrame({"y_true": y_true, "y_proba": y_proba}).sort_values("y_proba", ascending=False)
    frame["risk_decile"] = pd.qcut(np.arange(len(frame)), q=n_bins, labels=False) + 1
    base_rate = frame["y_true"].mean()
    grouped = frame.groupby("risk_decile", observed=True).agg(
        applicants=("y_true", "size"),
        default_rate=("y_true", "mean"),
        mean_score=("y_proba", "mean"),
    ).reset_index()
    grouped["lift"] = grouped["default_rate"] / base_rate
    return grouped


def group_error_summary(df: pd.DataFrame, y_true, y_proba, group_col: str, threshold: float = 0.5) -> pd.DataFrame:
    """Summarizing errors by a selected group for basic fairness diagnostics."""
    if group_col not in df.columns:
        raise ValueError(f"{group_col!r} was not found in the dataframe.")
    working = pd.DataFrame({"group": df[group_col].values, "y_true": y_true, "y_proba": y_proba})
    working["y_pred"] = (working["y_proba"] >= threshold).astype(int)
    rows = []
    for group, g in working.groupby("group", dropna=False):
        tn, fp, fn, tp = confusion_matrix(g["y_true"], g["y_pred"], labels=[0, 1]).ravel()
        rows.append({
            "group": group,
            "n": len(g),
            "default_rate": g["y_true"].mean(),
            "mean_score": g["y_proba"].mean(),
            "false_positive_rate": fp / max(fp + tn, 1),
            "false_negative_rate": fn / max(fn + tp, 1),
            "approval_rate_at_threshold": (g["y_pred"] == 0).mean(),
        })
    return pd.DataFrame(rows)
