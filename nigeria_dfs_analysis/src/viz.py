"""
src/viz.py
==========
Publication-quality visualisation helpers for the Nigeria DFS project.

What it does
------------
- Sets a consistent matplotlib/seaborn style across all notebooks.
- Provides a save_figure() function that saves to both reports/figures/
  and paper_or_report/figures/.
- Provides reusable chart builders for key report figures.

Why this is a src/ module
--------------------------
The same style settings and save logic are needed in 6+ notebooks.
Centralising avoids duplicating 20 lines of style code in every notebook.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import VIZ_PARAMS, BRAND_COLORS, get_path

# ── Global style application ──────────────────────────────────────────────────

def apply_project_style() -> None:
    """
    Apply the project-wide matplotlib and seaborn style.

    Call this once at the top of each notebook (after imports).
    Settings are chosen for readability and to match a consulting report aesthetic.
    """
    plt.rcParams.update({
        "figure.dpi":        150,
        "savefig.dpi":       VIZ_PARAMS["dpi"],
        "figure.facecolor":  "white",
        "axes.facecolor":    VIZ_PARAMS["brand_colors"]["background"],
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         True,
        "grid.alpha":        0.4,
        "grid.color":        "#CCCCCC",
        "font.family":       "sans-serif",
        "font.size":         11,
        "axes.titlesize":    13,
        "axes.titleweight":  "bold",
        "axes.labelsize":    11,
        "xtick.labelsize":   10,
        "ytick.labelsize":   10,
        "legend.fontsize":   10,
        "legend.frameon":    False,
    })
    # Use a colorblind-safe palette by default
    sns.set_palette("colorblind")


# ── Figure saver ──────────────────────────────────────────────────────────────

def save_figure(
    fig: plt.Figure,
    filename: str,
    also_paper: bool = True,
) -> None:
    """
    Save a matplotlib figure to reports/figures/ and optionally paper_or_report/figures/.

    Parameters
    ----------
    fig         : plt.Figure  — the figure to save
    filename    : str         — e.g. 'fig01_inclusion_trend.png'
    also_paper  : bool        — also copy to paper_or_report/figures/

    Notes
    -----
    Both PNG (raster, high-resolution) and PDF (vector) are saved.
    """
    reports_dir = get_path("reports_figures")
    base = filename.rsplit(".", 1)[0]   # strip extension

    png_path = reports_dir / f"{base}.png"
    pdf_path = reports_dir / f"{base}.pdf"

    fig.savefig(png_path, bbox_inches="tight", dpi=VIZ_PARAMS["dpi"])
    fig.savefig(pdf_path, bbox_inches="tight")
    print(f"  Saved: {png_path}")
    print(f"  Saved: {pdf_path}")

    if also_paper:
        paper_dir = get_path("paper_figures")
        fig.savefig(paper_dir / f"{base}.png", bbox_inches="tight", dpi=VIZ_PARAMS["dpi"])
        fig.savefig(paper_dir / f"{base}.pdf", bbox_inches="tight")


# ── Reusable chart builders ───────────────────────────────────────────────────

def plot_inclusion_trend(df_efina: pd.DataFrame, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Line chart: financial inclusion trend from EFInA survey data.

    Parameters
    ----------
    df_efina : pd.DataFrame  — output of load_efina_summary()
    ax       : plt.Axes, optional

    Returns
    -------
    plt.Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=VIZ_PARAMS["figure_size"]["wide"])

    ax.plot(
        df_efina["year"], df_efina["banked_pct"],
        marker="o", linewidth=2.5, color=BRAND_COLORS["primary"],
        label="Formally Banked (%)"
    )
    ax.plot(
        df_efina["year"], df_efina["excluded_pct"],
        marker="s", linewidth=2.5, color=BRAND_COLORS["danger"],
        linestyle="--", label="Financially Excluded (%)"
    )
    if "mobile_money_pct" in df_efina.columns:
        ax.plot(
            df_efina["year"], df_efina["mobile_money_pct"],
            marker="^", linewidth=2.5, color=BRAND_COLORS["secondary"],
            label="Mobile Money (%)"
        )

    ax.set_title("Nigeria Financial Inclusion Trend (EFInA Survey Data)")
    ax.set_xlabel("Year")
    ax.set_ylabel("% of Adults (15+)")
    ax.set_ylim(0, 70)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend()
    ax.annotate(
        "Source: EFInA Access to Finance Surveys 2008–2023",
        xy=(0.01, -0.12), xycoords="axes fraction",
        fontsize=8, color="grey", style="italic"
    )
    return ax


def plot_payment_growth(df_cbn: pd.DataFrame, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Bar + line chart: NIP transaction volume and value growth from CBN data.

    Parameters
    ----------
    df_cbn : pd.DataFrame  — output of load_cbn_payments()
    ax     : plt.Axes, optional

    Returns
    -------
    plt.Axes
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=VIZ_PARAMS["figure_size"]["wide"])
    else:
        fig = ax.get_figure()

    ax2 = ax.twinx()

    bars = ax.bar(
        df_cbn["year"], df_cbn["nip_volume_m"],
        color=BRAND_COLORS["primary"], alpha=0.7, label="NIP Volume (M transactions)"
    )
    line, = ax2.plot(
        df_cbn["year"], df_cbn["nip_value_bn_ngn"] / 1e3,   # → NGN trillions
        marker="o", linewidth=2.5, color=BRAND_COLORS["accent"],
        label="NIP Value (₦ Trillions)"
    )

    ax.set_title("Nigeria NIBSS Instant Payment (NIP) Growth (CBN Annual Reports)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Transaction Volume (Millions)")
    ax2.set_ylabel("Transaction Value (₦ Trillions)")

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax.annotate(
        "Source: CBN Annual Reports 2015–2023 (cbn.gov.ng)",
        xy=(0.01, -0.12), xycoords="axes fraction",
        fontsize=8, color="grey", style="italic"
    )
    return ax


def plot_market_sizing_funnel(tam_m, sam_m, som_y1_m, som_y3_m) -> plt.Figure:
    """
    Horizontal bar chart showing TAM → SAM → SOM funnel.

    Parameters
    ----------
    *_m : float  — market size in USD millions

    Returns
    -------
    plt.Figure
    """
    labels = ["TAM", "SAM", "SOM (Year 1)", "SOM (Year 3)"]
    values = [tam_m, sam_m, som_y1_m, som_y3_m]
    colors = [
        BRAND_COLORS["primary"],
        BRAND_COLORS["secondary"],
        BRAND_COLORS["accent"],
        BRAND_COLORS["danger"],
    ]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.5)

    for bar, val in zip(bars, values[::-1]):
        ax.text(
            bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}M", va="center", ha="left", fontsize=11, fontweight="bold"
        )

    ax.set_xlabel("Market Size (USD Millions)")
    ax.set_title("Nigeria DFS Market Sizing: TAM → SAM → SOM (2023)")
    ax.set_xlim(0, max(values) * 1.25)

    ax.annotate(
        "ASSUMPTION: All figures are estimates. See configs/config.yaml for methodology.",
        xy=(0.01, -0.14), xycoords="axes fraction",
        fontsize=8, color=BRAND_COLORS["danger"], style="italic"
    )
    plt.tight_layout()
    return fig


def plot_risk_matrix(df_risks: pd.DataFrame) -> plt.Figure:
    """
    5×5 risk heatmap (Probability × Impact).

    Parameters
    ----------
    df_risks : pd.DataFrame  — output of build_risk_registry()

    Returns
    -------
    plt.Figure
    """
    # Build 5×5 count matrix
    matrix = np.zeros((5, 5), dtype=int)
    for _, row in df_risks.iterrows():
        p = int(row["Probability"]) - 1
        i = int(row["Impact"]) - 1
        matrix[p][i] += 1

    # Build a score matrix for colouring
    score_matrix = np.array([[i * j for j in range(1, 6)] for i in range(1, 6)])

    fig, ax = plt.subplots(figsize=(8, 7))

    # Color map: green → yellow → red
    im = ax.imshow(
        score_matrix, cmap="RdYlGn_r", vmin=1, vmax=25,
        aspect="auto", alpha=0.6
    )

    # Overlay risk counts
    for i in range(5):
        for j in range(5):
            count = matrix[i][j]
            score = (i + 1) * (j + 1)
            if count > 0:
                ax.text(
                    j, i, f"●×{count}",
                    ha="center", va="center",
                    fontsize=14, fontweight="bold", color="black"
                )
            ax.text(
                j, i + 0.35, f"score={score}",
                ha="center", va="center", fontsize=7, color="black", alpha=0.6
            )

    ax.set_xticks(range(5))
    ax.set_xticklabels(["Negligible\n(1)", "Minor\n(2)", "Moderate\n(3)",
                        "Major\n(4)", "Catastrophic\n(5)"])
    ax.set_yticks(range(5))
    ax.set_yticklabels(["Rare\n(1)", "Unlikely\n(2)", "Possible\n(3)",
                        "Likely\n(4)", "Almost Certain\n(5)"])
    ax.set_xlabel("Impact →")
    ax.set_ylabel("Probability →")
    ax.set_title("Nigeria DFS Market Entry — Risk Assessment Matrix")

    plt.colorbar(im, ax=ax, label="Risk Score (P × I)")
    plt.tight_layout()
    return fig
