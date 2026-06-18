"""
tests/test_all.py
=================
Unit tests for the Nigeria DFS Market Analysis project.

All tests use tiny, clearly-labelled synthetic fixtures — NOT real data.
Real data is only used in notebooks and scripts.

Run:
    pytest tests/ -v
    pytest tests/ -v --cov=src --cov-report=term-missing

Tests are intentionally simple so a beginner can read and modify them.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

# Ensure src/ is on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ============================================================
#  TEST FIXTURES  (synthetic — labelled clearly)
# ============================================================

@pytest.fixture
def mock_wb_dataframe():
    """
    SYNTHETIC TEST FIXTURE — not real data.
    Mimics the shape and schema of a World Bank indicators DataFrame.
    """
    return pd.DataFrame({
        "country":   ["Nigeria", "Nigeria", "Kenya",   "Kenya"],
        "year":      [2020,       2021,       2020,      2021],
        "indicator": ["account_ownership", "account_ownership",
                      "account_ownership", "account_ownership"],
        "value":     [40.1, 41.5, 79.0, 82.0],
        "wb_code":   ["FX.OWN.TOTL.ZS"] * 4,
    })


@pytest.fixture
def mock_cbn_dataframe():
    """SYNTHETIC TEST FIXTURE — mimics CBN payment data shape."""
    return pd.DataFrame({
        "year":             [2020, 2021, 2022],
        "nip_volume_m":     [1823, 3093, 5286],
        "nip_value_bn_ngn": [218800, 358500, 516000],
        "pos_volume_m":     [773, 1000, 1294],
        "pos_value_bn_ngn": [15950, 20440, 25820],
        "mobile_vol_m":     [718, 1145, 1800],
        "mobile_val_bn_ngn":[47200, 79600, 120000],
        "inet_vol_m":       [134, 195, 275],
        "inet_val_bn_ngn":  [48900, 72100, 101000],
        "mobile_money_wallets_m": [8.4, 11.5, 14.2],
    })


@pytest.fixture
def mock_efina_dataframe():
    """SYNTHETIC TEST FIXTURE — mimics EFInA survey summary shape."""
    return pd.DataFrame({
        "year":             [2018, 2020, 2023],
        "banked_pct":       [39.5, 40.1, 45.0],
        "mobile_money_pct": [7.2,  12.4, 18.0],
        "excluded_pct":     [36.8, 35.9, 26.0],
        "adult_pop_m":      [96.8, 102.0, 106.0],
        "banked_m":         [38.2, 40.9, 47.7],
        "excluded_m":       [35.6, 36.6, 27.6],
    })


@pytest.fixture
def mock_competitors_dataframe():
    """SYNTHETIC TEST FIXTURE — mimics competitor dataset shape."""
    return pd.DataFrame({
        "company":           ["TestFintech_A", "TestFintech_B"],
        "founded":           [2018, 2020],
        "type":              ["Neobank", "Payments"],
        "reported_users_m":  [5.0, 2.0],
        "funding_usd_m":     [100.0, 30.0],
        "revenue_model":     ["Lend+Trans", "Trans"],
        "headquarters":      ["Lagos", "Lagos"],
        "cbsn_licensed":     [True, False],
        "agent_network_k":   [None, 50.0],
        "primary_market":    ["Consumer", "SME"],
        "monthly_txn_ngn_bn":[200.0, 80.0],
    })


# ============================================================
#  CONFIG TESTS
# ============================================================

class TestConfig:
    """Tests for src/config.py and configs/config.yaml."""

    def test_config_loads_without_error(self):
        """The config YAML must load cleanly."""
        from src.config import cfg
        assert isinstance(cfg, dict), "cfg must be a dict"

    def test_config_has_required_sections(self):
        """config.yaml must contain the required top-level sections."""
        from src.config import cfg
        required_sections = ["project", "paths", "world_bank", "market_sizing",
                             "financial_model", "risk_assessment", "viz"]
        for section in required_sections:
            assert section in cfg, f"Missing config section: {section}"

    def test_random_seed_is_integer(self):
        from src.config import RANDOM_SEED
        assert isinstance(RANDOM_SEED, int), "RANDOM_SEED must be int"
        assert 0 < RANDOM_SEED < 1_000_000

    def test_indicators_dict_is_populated(self):
        from src.config import INDICATORS
        assert len(INDICATORS) >= 5, "Must have at least 5 WB indicators"
        for name, code in INDICATORS.items():
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(code, str) and len(code) > 0

    def test_get_path_returns_existing_directory(self):
        from src.config import get_path
        for key in ["data_raw", "data_interim", "data_processed",
                    "reports_figures", "reports_tables"]:
            p = get_path(key)
            assert p.exists(), f"get_path('{key}') should create the directory"
            assert p.is_dir()

    def test_brand_colors_are_hex(self):
        from src.config import BRAND_COLORS
        import re
        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for name, color in BRAND_COLORS.items():
            assert hex_pattern.match(color), \
                f"Brand color '{name}' = '{color}' is not a valid hex color"

    def test_market_params_types(self):
        from src.config import MARKET_PARAMS
        assert MARKET_PARAMS["nigeria_adults_2023_m"] > 50
        assert 0 < MARKET_PARAMS["smartphone_penetration"] < 1
        assert MARKET_PARAMS["avg_annual_txn_value_usd"] > 0


# ============================================================
#  PREPROCESSING TESTS
# ============================================================

class TestPreprocessing:
    """Tests for src/preprocessing.py."""

    def test_validate_wb_schema_passes(self, mock_wb_dataframe):
        from src.preprocessing import validate_wb_schema
        validate_wb_schema(mock_wb_dataframe)   # Should not raise

    def test_validate_wb_schema_raises_on_missing_col(self, mock_wb_dataframe):
        from src.preprocessing import validate_wb_schema
        broken = mock_wb_dataframe.drop(columns=["indicator"])
        with pytest.raises(ValueError, match="missing required columns"):
            validate_wb_schema(broken)

    def test_validate_cbn_schema_passes(self, mock_cbn_dataframe):
        from src.preprocessing import validate_cbn_schema
        validate_cbn_schema(mock_cbn_dataframe)   # Should not raise

    def test_validate_cbn_schema_raises_on_missing(self, mock_cbn_dataframe):
        from src.preprocessing import validate_cbn_schema
        broken = mock_cbn_dataframe.drop(columns=["nip_volume_m"])
        with pytest.raises(ValueError, match="missing columns"):
            validate_cbn_schema(broken)

    def test_missing_value_report_returns_dataframe(self, mock_wb_dataframe):
        from src.preprocessing import missing_value_report
        report = missing_value_report(mock_wb_dataframe, label="test")
        assert isinstance(report, pd.DataFrame)
        assert "n_missing" in report.columns
        assert "pct_missing" in report.columns

    def test_add_yoy_growth_correct_values(self):
        """YoY growth should be correct for a simple doubling sequence."""
        from src.preprocessing import add_yoy_growth
        df = pd.DataFrame({"year": [2020, 2021, 2022], "val": [100, 200, 400]})
        df = add_yoy_growth(df, "val")
        # 2020→2021: +100%; 2021→2022: +100%
        assert df["val_yoy_pct"].iloc[0] != df["val_yoy_pct"].iloc[0]   # NaN for first
        assert abs(df["val_yoy_pct"].iloc[1] - 100.0) < 0.01
        assert abs(df["val_yoy_pct"].iloc[2] - 100.0) < 0.01

    def test_flag_outliers_iqr_identifies_extreme(self):
        """A value 10 standard deviations away should be flagged."""
        from src.preprocessing import flag_outliers_iqr
        df = pd.DataFrame({"val": list(range(100)) + [9999]})
        flags = flag_outliers_iqr(df, "val")
        assert flags.iloc[-1] == True, "9999 should be flagged as outlier"
        assert flags.sum() <= 3, "No more than 3 outliers expected"


# ============================================================
#  MARKET SIZING TESTS
# ============================================================

class TestMarketSizing:
    """Tests for src/market_sizing.py."""

    def test_compute_tam_sam_som_returns_four_results(self):
        from src.market_sizing import compute_tam_sam_som
        results = compute_tam_sam_som()
        assert set(results.keys()) == {"TAM", "SAM", "SOM_Y1", "SOM_Y3"}

    def test_tam_larger_than_sam(self):
        from src.market_sizing import compute_tam_sam_som
        r = compute_tam_sam_som()
        assert r["TAM"].market_size_usd_m > r["SAM"].market_size_usd_m

    def test_sam_larger_than_som_y1(self):
        from src.market_sizing import compute_tam_sam_som
        r = compute_tam_sam_som()
        assert r["SAM"].market_size_usd_m > r["SOM_Y1"].market_size_usd_m

    def test_som_y3_larger_than_som_y1(self):
        from src.market_sizing import compute_tam_sam_som
        r = compute_tam_sam_som()
        assert r["SOM_Y3"].market_size_usd_m > r["SOM_Y1"].market_size_usd_m

    def test_market_sizing_table_has_correct_columns(self):
        from src.market_sizing import compute_tam_sam_som, market_sizing_table
        r = compute_tam_sam_som()
        df = market_sizing_table(r)
        assert "Market" in df.columns
        assert "Market Size (USD M)" in df.columns
        assert len(df) == 4

    def test_all_population_values_positive(self):
        from src.market_sizing import compute_tam_sam_som
        r = compute_tam_sam_som()
        for key, result in r.items():
            assert result.population_m > 0, f"{key}: population must be > 0"
            assert result.market_size_usd_m > 0, f"{key}: market size must be > 0"

    def test_sensitivity_table_shape(self):
        from src.market_sizing import sensitivity_market_size
        arpu_vals  = [8, 12, 16]
        users_vals = [0.5, 1.0, 2.0]
        df = sensitivity_market_size(arpu_vals, users_vals)
        assert df.shape == (len(arpu_vals), len(users_vals))


# ============================================================
#  FINANCIAL MODEL TESTS
# ============================================================

class TestFinancialModel:
    """Tests for src/financial_model.py."""

    def test_project_users_returns_three_years(self):
        from src.financial_model import project_users
        df = project_users()
        assert len(df) == 3
        assert list(df["year"]) == [1, 2, 3]

    def test_user_base_grows_year_on_year(self):
        from src.financial_model import project_users
        df = project_users()
        assert df["active_users"].iloc[1] > df["active_users"].iloc[0]
        assert df["active_users"].iloc[2] > df["active_users"].iloc[1]

    def test_revenue_grows_year_on_year(self):
        from src.financial_model import project_users, project_revenue
        df_u = project_users()
        df_r = project_revenue(df_u)
        rev = df_r["total_revenue_usd_m"].values
        assert rev[1] > rev[0]
        assert rev[2] > rev[1]

    def test_revenue_streams_sum_to_total(self):
        """Transaction fees + float + lending + subscription ≈ total revenue."""
        from src.financial_model import project_users, project_revenue
        df_u = project_users()
        df_r = project_revenue(df_u)
        for _, row in df_r.iterrows():
            stream_sum = (
                row["txn_fees_usd_m"]
                + row["float_income_usd_m"]
                + row["lending_usd_m"]
                + row["subscription_usd_m"]
            )
            assert abs(stream_sum - row["total_revenue_usd_m"]) < 0.01, \
                f"Year {row['year']}: revenue streams don't sum to total"

    def test_income_statement_ebitda_margin_realistic(self):
        """EBITDA margin should be between -50% and +50% for a growth-stage fintech."""
        from src.financial_model import project_users, project_revenue, project_income_statement
        df_u = project_users()
        df_r = project_revenue(df_u)
        df_p = project_income_statement(df_r)
        for _, row in df_p.iterrows():
            assert -50 <= row["ebitda_margin_pct"] <= 50, \
                f"Year {row['year']}: EBITDA margin {row['ebitda_margin_pct']}% is unrealistic"

    def test_comparable_valuation_returns_dataframe(self):
        from src.financial_model import comparable_valuation
        df = comparable_valuation(y3_revenue_usd_m=10.0)
        assert isinstance(df, pd.DataFrame)
        assert "Comparable Company" in df.columns
        assert len(df) >= 3

    def test_sensitivity_revenue_shape(self):
        from src.financial_model import sensitivity_revenue
        arpu  = [8, 12, 16, 20]
        users = [500_000, 1_000_000, 2_000_000]
        df = sensitivity_revenue(arpu, users)
        assert df.shape[0] == len(arpu)
        assert df.shape[1] == len(users)


# ============================================================
#  RISK MODEL TESTS
# ============================================================

class TestRiskModel:
    """Tests for src/risk_model.py."""

    def test_risk_registry_not_empty(self):
        from src.risk_model import build_risk_registry
        df = build_risk_registry()
        assert len(df) >= 5, "Risk registry must have at least 5 risks"

    def test_risk_scores_in_valid_range(self):
        from src.risk_model import build_risk_registry
        df = build_risk_registry()
        assert df["Risk Score"].between(1, 25).all(), \
            "All risk scores must be between 1 and 25"

    def test_risk_tiers_valid_labels(self):
        from src.risk_model import build_risk_registry
        df = build_risk_registry()
        valid_tiers = {"Low", "Medium", "High", "Critical"}
        assert set(df["Risk Tier"].unique()).issubset(valid_tiers), \
            "All risk tiers must be Low / Medium / High / Critical"

    def test_risk_sorted_descending(self):
        from src.risk_model import build_risk_registry
        df = build_risk_registry()
        scores = df["Risk Score"].values
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), \
            "Risk registry must be sorted by score descending"

    def test_strategic_opportunities_not_empty(self):
        from src.risk_model import strategic_opportunities
        df = strategic_opportunities()
        assert len(df) >= 3
        assert "Priority Score" in df.columns

    def test_heatmap_matrix_shape(self):
        from src.risk_model import risk_heatmap_matrix
        df = risk_heatmap_matrix()
        assert df.shape == (5, 5), "Risk heatmap matrix must be 5×5"


# ============================================================
#  STATISTICS TESTS
# ============================================================

class TestStats:
    """Tests for src/stats.py."""

    def test_bootstrap_ci_mean_near_true_value(self):
        """Bootstrap mean CI should capture the true mean for a large sample."""
        from src.stats import bootstrap_ci
        rng  = np.random.default_rng(42)
        data = rng.normal(loc=10.0, scale=1.0, size=200)
        point, lo, hi = bootstrap_ci(data, np.mean)
        assert lo < 10.0 < hi, "95% CI should contain the true mean of 10.0"
        assert abs(point - 10.0) < 0.5

    def test_bootstrap_ci_lower_less_than_upper(self):
        from src.stats import bootstrap_ci
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        point, lo, hi = bootstrap_ci(data)
        assert lo < hi

    def test_cagr_correct_for_doubling(self):
        """A value that doubles over 1 year has CAGR = 100%."""
        from src.stats import cagr
        result = cagr(start_value=100, end_value=200, n_years=1)
        assert abs(result - 1.0) < 0.001   # 100%

    def test_cagr_correct_for_10pct_growth(self):
        from src.stats import cagr
        # 100 → 121 in 2 years → CAGR ≈ 10%
        result = cagr(100, 121, 2)
        assert abs(result - 0.1) < 0.001

    def test_cagr_raises_on_zero_start(self):
        from src.stats import cagr
        with pytest.raises(ValueError):
            cagr(start_value=0, end_value=100, n_years=5)

    def test_period_sensitivity_returns_dataframe(self):
        from src.stats import period_sensitivity_cagr
        df = pd.DataFrame({
            "year": [2015, 2016, 2017, 2018, 2019, 2020],
            "val":  [100,   120,   144,   173,   207,   249],
        })
        result = period_sensitivity_cagr(df, "year", "val",
                                         start_years=[2015, 2016, 2017],
                                         end_year=2020)
        assert len(result) == 3
        assert "CAGR (%)" in result.columns
        # All CAGRs should be positive (data is always growing)
        assert (result["CAGR (%)"] > 0).all()
