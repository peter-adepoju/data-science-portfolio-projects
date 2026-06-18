from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay

from .config import FIGURES_DIR, ensure_project_dirs


def save_figure(fig, filename: str, dpi: int = 160) -> Path:
    """Saving a matplotlib figure to reports/figures before displaying it."""
    ensure_project_dirs()
    path = FIGURES_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path


def plot_target_distribution(df: pd.DataFrame, target: str):
    """Plotting the target class distribution."""
    fig, ax = plt.subplots(figsize=(6, 4))
    df[target].value_counts(normalize=True).sort_index().plot(kind="bar", ax=ax)
    ax.set_title("Default target distribution")
    ax.set_xlabel("Default next month")
    ax.set_ylabel("Proportion")
    return fig


def plot_missingness(df: pd.DataFrame):
    """Plotting variables with non-zero missingness."""
    missing = df.isna().mean().sort_values(ascending=False)
    missing = missing[missing > 0]
    fig, ax = plt.subplots(figsize=(8, max(3, len(missing) * 0.25)))
    if missing.empty:
        ax.text(0.5, 0.5, "No missing values detected", ha="center", va="center")
        ax.set_axis_off()
    else:
        missing.plot(kind="barh", ax=ax)
        ax.set_title("Missingness by variable")
        ax.set_xlabel("Missing fraction")
    return fig


def plot_model_curves(y_true, y_proba, model_name: str):
    """Plotting ROC and precision-recall curves for a fitted model."""
    fig_roc, ax_roc = plt.subplots(figsize=(6, 5))
    RocCurveDisplay.from_predictions(y_true, y_proba, ax=ax_roc, name=model_name)
    ax_roc.set_title(f"ROC curve: {model_name}")

    fig_pr, ax_pr = plt.subplots(figsize=(6, 5))
    PrecisionRecallDisplay.from_predictions(y_true, y_proba, ax=ax_pr, name=model_name)
    ax_pr.set_title(f"Precision-recall curve: {model_name}")
    return fig_roc, fig_pr


def plot_confusion(y_true, y_proba, threshold: float, model_name: str):
    """Plotting a confusion matrix for a selected threshold."""
    y_pred = (y_proba >= threshold).astype(int)
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(y_true, y_pred, ax=ax, colorbar=False)
    ax.set_title(f"Confusion matrix: {model_name} at threshold={threshold:.2f}")
    return fig


def plot_calibration(y_true, y_proba, model_name: str, n_bins: int = 10):
    """Plotting calibration curve for predicted probabilities."""
    prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=n_bins, strategy="quantile")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(prob_pred, prob_true, marker="o", label=model_name)
    ax.plot([0, 1], [0, 1], linestyle="--", label="perfect calibration")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Observed default rate")
    ax.set_title(f"Calibration curve: {model_name}")
    ax.legend()
    return fig
