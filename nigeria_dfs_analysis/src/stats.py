"""
src/stats.py
============
Statistical helper functions for the Nigeria DFS market analysis.

What it does
------------
- Bootstrap confidence intervals for trend estimates.
- Pearson and Spearman correlation with p-values.
- Simple linear regression with inference (via statsmodels).
- Robustness check: sensitivity of growth estimates to time-period choice.

Why this matters
----------------
A consulting report should not present point estimates alone.
Uncertainty ranges, significance tests, and robustness checks
make the analysis defensible and more honest about what the data
can and cannot tell us.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import pandas as pd
import scipy.stats as stats

try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    _STATSMODELS_AVAILABLE = True
except ImportError:
    _STATSMODELS_AVAILABLE = False
    sm = None
    smf = None

from src.config import RANDOM_SEED


# ── Bootstrap confidence intervals ────────────────────────────────────────────

def bootstrap_ci(
    data: np.ndarray,
    stat_fn=np.mean,
    n_boot: int = 2000,
    ci: float = 0.95,
    seed: int = RANDOM_SEED,
) -> Tuple[float, float, float]:
    """
    Non-parametric bootstrap confidence interval.

    Parameters
    ----------
    data    : array-like  — sample data
    stat_fn : callable    — statistic to compute (default: np.mean)
    n_boot  : int         — number of bootstrap resamples
    ci      : float       — confidence level (default: 0.95)
    seed    : int         — random seed for reproducibility

    Returns
    -------
    (point_estimate, lower_ci, upper_ci)

    Notes
    -----
    Uses the basic percentile method. For small samples the bootstrap
    CI should be interpreted cautiously.
    """
    rng   = np.random.default_rng(seed)
    data  = np.asarray(data, dtype=float)
    point = stat_fn(data)

    boot_stats = [
        stat_fn(rng.choice(data, size=len(data), replace=True))
        for _ in range(n_boot)
    ]

    alpha = 1 - ci
    lo = np.percentile(boot_stats, alpha / 2 * 100)
    hi = np.percentile(boot_stats, (1 - alpha / 2) * 100)

    return float(point), float(lo), float(hi)


# ── Correlation analysis ──────────────────────────────────────────────────────

def correlation_table(
    df: pd.DataFrame,
    cols: list[str],
    method: str = "pearson",
) -> pd.DataFrame:
    """
    Compute a correlation matrix with p-values.

    Parameters
    ----------
    df     : pd.DataFrame
    cols   : list[str]  — columns to include
    method : str        — 'pearson' or 'spearman'

    Returns
    -------
    pd.DataFrame
        Multi-level columns: (correlation, p_value) for each pair.
    """
    sub = df[cols].dropna()
    n   = len(sub)

    cor_matrix = pd.DataFrame(index=cols, columns=cols, dtype=float)
    pval_matrix = pd.DataFrame(index=cols, columns=cols, dtype=float)

    for c1 in cols:
        for c2 in cols:
            if c1 == c2:
                cor_matrix.loc[c1, c2]  = 1.0
                pval_matrix.loc[c1, c2] = 0.0
            else:
                if method == "pearson":
                    r, p = stats.pearsonr(sub[c1], sub[c2])
                else:
                    r, p = stats.spearmanr(sub[c1], sub[c2])
                cor_matrix.loc[c1, c2]  = round(r, 3)
                pval_matrix.loc[c1, c2] = round(p, 4)

    return cor_matrix, pval_matrix


# ── Linear regression with inference ─────────────────────────────────────────

def ols_regression(
    df: pd.DataFrame,
    formula: str,
    title: str = "",
) -> object:
    """
    Run OLS regression and print a formatted summary.

    Requires statsmodels. If not installed, prints a warning and returns None.

    Parameters
    ----------
    df      : pd.DataFrame
    formula : str  — statsmodels formula, e.g. 'banked_pct ~ year'
    title   : str  — printed above the summary

    Returns
    -------
    statsmodels RegressionResults object, or None if statsmodels unavailable.

    Notes
    -----
    Use conservative language when interpreting OLS results on time-series
    data — autocorrelation and small sample sizes limit inference.
    Install statsmodels with: pip install statsmodels
    """
    if not _STATSMODELS_AVAILABLE:
        print("WARNING: statsmodels is not installed.")
        print("Install with: pip install statsmodels")
        print("Falling back to scipy.stats.linregress for simple trend.")
        # Fallback: simple scipy linear regression
        parts = formula.replace(" ", "").split("~")
        if len(parts) == 2:
            y_col, x_col = parts[0], parts[1]
            sub = df[[x_col, y_col]].dropna()
            slope, intercept, r, p, se = stats.linregress(sub[x_col], sub[y_col])
            print(f"\n  scipy.stats.linregress({formula})")
            print(f"  Slope     : {slope:.4f}")
            print(f"  Intercept : {intercept:.4f}")
            print(f"  R²        : {r**2:.4f}")
            print(f"  p-value   : {p:.4f}")
        return None

    model  = smf.ols(formula, data=df.dropna())
    result = model.fit()

    if title:
        print(f"\n{'='*60}")
        print(f"OLS Regression: {title}")
        print(f"{'='*60}")
    print(result.summary())
    return result


# ── CAGR calculation ──────────────────────────────────────────────────────────

def cagr(start_value: float, end_value: float, n_years: int) -> float:
    """
    Compound Annual Growth Rate.

    Parameters
    ----------
    start_value : float
    end_value   : float
    n_years     : int

    Returns
    -------
    float
        CAGR as a decimal (e.g., 0.23 = 23% per year).
    """
    if start_value <= 0:
        raise ValueError("start_value must be > 0")
    return (end_value / start_value) ** (1 / n_years) - 1


# ── Robustness: time-period sensitivity ──────────────────────────────────────

def period_sensitivity_cagr(
    df: pd.DataFrame,
    year_col: str,
    value_col: str,
    start_years: list[int],
    end_year: int,
) -> pd.DataFrame:
    """
    Check how sensitive a CAGR estimate is to the choice of start year.

    Parameters
    ----------
    df          : pd.DataFrame
    year_col    : str
    value_col   : str
    start_years : list[int]  — alternative start years to test
    end_year    : int        — fixed end year

    Returns
    -------
    pd.DataFrame
        Columns: start_year, end_year, n_years, start_value,
                 end_value, cagr_pct
    """
    df = df.sort_values(year_col).copy()
    end_val = df.loc[df[year_col] == end_year, value_col].values

    if len(end_val) == 0:
        raise ValueError(f"end_year {end_year} not found in {year_col}")
    end_val = float(end_val[0])

    rows = []
    for sy in start_years:
        start_val = df.loc[df[year_col] == sy, value_col].values
        if len(start_val) == 0:
            continue
        sv = float(start_val[0])
        n  = end_year - sy
        if n <= 0 or sv <= 0:
            continue
        rate = cagr(sv, end_val, n) * 100
        rows.append({
            "Start Year": sy,
            "End Year":   end_year,
            "N Years":    n,
            "Start Value": round(sv, 2),
            "End Value":  round(end_val, 2),
            "CAGR (%)":   round(rate, 1),
        })

    result = pd.DataFrame(rows)
    print(f"\nCAGR Robustness Check — {value_col}:")
    print(result.to_string(index=False))
    return result
