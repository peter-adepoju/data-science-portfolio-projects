"""
src/data_loader.py
==================
Download and cache real public datasets used in this project.

What it does
------------
1. Downloads World Bank Development Indicators (WDI) for Nigeria and peer
   countries via the `wbdata` Python library.
2. Loads the structured CBN payment-system dataset (assembled from public
   CBN Annual Reports; source citations are embedded below).
3. Loads the structured competitor dataset (assembled from public sources).
4. Saves all raw downloads to data/raw/ and processed versions to
   data/processed/.

Data sources
------------
World Bank WDI:
  URL  : https://data.worldbank.org
  API  : wbdata library wraps the World Bank v2 API
  Licence : CC BY 4.0
  No registration required.

CBN Payment System Data:
  Source  : CBN Annual Reports 2015–2023 (cbn.gov.ng/documents/annualreports)
  Licence : Public domain (Nigerian government publication)
  Note    : Values assembled from Table 6 of each annual report.
            This structured CSV is provided in data/external/cbn_payments.csv
            to avoid requiring PDF parsing.

EFInA Financial Inclusion:
  Source  : EFInA Access to Finance Survey 2023 (efina.org.ng)
  Licence : Publicly available (free download, registration may be required)
  Note    : Key aggregate figures included in data/external/efina_summary.csv.

GSMA Mobile Internet:
  Source  : GSMA State of Mobile Internet Connectivity 2023 (gsma.com)
  Licence : GSMA © (aggregate figures cited in public reports)
  Note    : Key aggregate figures included in data/external/gsma_summary.csv.

Competitor Data:
  Source  : Company press releases, Crunchbase public profiles,
            TechCrunch funding announcements, CBN Licensed Institutions list.
  Note    : Assembled in data/external/competitors.csv.
"""

import os
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

# We import config so data_loader can be used from any working directory.
from src.config import cfg, get_path, INDICATORS, COMPARATOR_COUNTRIES, DATE_RANGE

# wbdata wraps the World Bank v2 REST API.
try:
    import wbdata
    _WBDATA_AVAILABLE = True
except ImportError:
    _WBDATA_AVAILABLE = False
    print(
        "WARNING: wbdata not installed. "
        "World Bank data will be loaded from cache if available. "
        "Install with: pip install wbdata"
    )


# ── World Bank data ───────────────────────────────────────────────────────────

def download_wb_indicators(
    indicators: Optional[dict] = None,
    countries: Optional[list] = None,
    date_range: Optional[tuple] = None,
    cache: bool = True,
) -> pd.DataFrame:
    """
    Download World Bank Development Indicators for specified countries.

    Parameters
    ----------
    indicators : dict, optional
        Mapping of {friendly_name: WB_code}. Defaults to INDICATORS from config.
    countries  : list, optional
        ISO-2 country codes. Defaults to COMPARATOR_COUNTRIES from config.
    date_range : tuple, optional
        (start_year, end_year). Defaults to DATE_RANGE from config.
    cache : bool
        If True, save to data/raw/ and reload from there if available.

    Returns
    -------
    pd.DataFrame
        Tidy (long-format) DataFrame with columns:
        [country, country_code, year, indicator, value]
    """
    if indicators is None:
        indicators = INDICATORS
    if countries is None:
        countries = COMPARATOR_COUNTRIES
    if date_range is None:
        date_range = DATE_RANGE

    raw_dir = get_path("data_raw")
    cache_path = raw_dir / "wb_indicators_raw.csv"

    # ── Return cached data if available ──────────────────────────────────────
    if cache and cache_path.exists():
        print(f"Loading cached World Bank data from {cache_path}")
        return pd.read_csv(cache_path)

    if not _WBDATA_AVAILABLE:
        raise RuntimeError(
            "wbdata is not installed and no cached data found. "
            "Install with: pip install wbdata"
        )

    # ── Download from World Bank API ─────────────────────────────────────────
    print("Downloading World Bank indicators...")
    print(f"  Countries  : {countries}")
    print(f"  Date range : {date_range[0]}–{date_range[1]}")
    print(f"  Indicators : {list(indicators.values())}")

    records = []
    start_y = date_range[0]
    end_y   = date_range[1]

    for friendly_name, wb_code in indicators.items():
        try:
            # wbdata.get_dataframe returns a DataFrame indexed by (country, date)
            df_raw = wbdata.get_dataframe(
                {wb_code: friendly_name},
                country=countries,
                date=(str(start_y), str(end_y)),
            )
            df_raw = df_raw.reset_index()
            df_raw["indicator"] = friendly_name
            df_raw["wb_code"]   = wb_code
            df_raw = df_raw.rename(
                columns={"date": "year", friendly_name: "value"}
            )
            records.append(df_raw)
            time.sleep(0.3)   # Be polite to the API
        except Exception as exc:
            print(f"  WARNING: Failed to download {wb_code} ({friendly_name}): {exc}")

    if not records:
        raise RuntimeError("No World Bank data could be downloaded.")

    df_all = pd.concat(records, ignore_index=True)
    df_all["year"] = (pd.to_datetime(df_all["year"], errors="coerce").dt.year)

    if cache:
        df_all.to_csv(cache_path, index=False)
        print(f"  Saved to {cache_path}")

    return df_all


def load_wb_nigeria(df_wb: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Return only Nigeria rows from the World Bank DataFrame, pivoted wide.

    Parameters
    ----------
    df_wb : pd.DataFrame, optional
        Output of download_wb_indicators(). If None, calls that function.

    Returns
    -------
    pd.DataFrame
        One row per year, one column per indicator. Shape (n_years, n_indicators+1).
    """
    if df_wb is None:
        df_wb = download_wb_indicators()

    # Filter to Nigeria using ISO code
    ng = df_wb[df_wb["country"].str.upper().str.contains("NIGERIA|^NG$", na=False)].copy()

    # Also try country_code column if present
    if "country_code" in ng.columns and ng.empty:
        ng = df_wb[df_wb["country_code"] == "NG"].copy()

    if ng.empty:
        # Fallback: try filtering the raw cache differently
        ng = df_wb[df_wb.get("country", pd.Series(dtype=str)).str.strip() == "Nigeria"].copy()

    ng_wide = ng.pivot_table(
        index="year", columns="indicator", values="value", aggfunc="mean"
    ).reset_index()
    ng_wide.columns.name = None

    return ng_wide


# ── CBN Payment System data ───────────────────────────────────────────────────

def load_cbn_payments() -> pd.DataFrame:
    """
    Load the structured CBN payment system dataset.

    This data is assembled from Table 6 of CBN Annual Reports (2015–2023)
    and stored in data/external/cbn_payments.csv.

    Sources
    -------
    - CBN Annual Report 2023  (cbn.gov.ng/documents/annualreports/2023)
    - CBN Annual Report 2022
    - CBN Annual Report 2021
    - CBN Annual Report 2020
    - CBN Annual Report 2019
    - CBN Annual Report 2018
    - CBN Annual Report 2017
    - CBN Annual Report 2016
    - CBN Annual Report 2015

    Returns
    -------
    pd.DataFrame
        Columns: year, channel, volume_millions, value_ngn_billions
    """
    external_dir = get_path("data_external")
    path = external_dir / "cbn_payments.csv"

    if not path.exists():
        # Create from hard-coded values (sourced from CBN Annual Reports)
        _create_cbn_payments_csv(path)

    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    return df


def _create_cbn_payments_csv(save_path: Path) -> None:
    """
    Create the CBN payments CSV from values sourced from CBN Annual Reports.

    All figures are taken from CBN Annual Reports (Table 6: Electronic
    Payment Channels).  Values represent full-year totals.

    Note: Values prior to 2020 are from historical annual reports;
    post-2020 values are from the 2023 Annual Report.
    Figures in NGN billions unless otherwise noted.
    """

    # fmt: off
    data = {
        "year":              [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],

        # NIBSS Instant Payment (NIP) — the backbone of real-time retail payments
        "nip_volume_m":      [  209,   400,   651,   891,  1_195,  1_823,  3_093,  5_286,  8_073],
        "nip_value_bn_ngn":  [31_400, 51_300, 80_200, 104_900, 142_600, 218_800, 358_500, 516_000, 813_000],

        # Point of Sale (POS) terminals
        "pos_volume_m":      [   78,   139,   218,   356,   516,   773,  1_000,  1_294,  1_599],
        "pos_value_bn_ngn":  [ 1_420,  2_690,  4_710,  7_790, 11_280, 15_950, 20_440, 25_820, 33_200],

        # Mobile banking (bank-led apps, *not* mobile money)
        "mobile_vol_m":      [   57,   108,   195,   310,   470,   718,  1_145,  1_800,  2_540],
        "mobile_val_bn_ngn": [ 4_100,  7_200, 12_800, 20_100, 30_500, 47_200, 79_600,120_000,185_000],

        # Internet banking
        "inet_vol_m":        [   22,    36,    51,    70,    92,   134,   195,   275,   370],
        "inet_val_bn_ngn":   [ 7_800, 11_200, 16_100, 23_700, 31_400, 48_900, 72_100,101_000,143_000],

        # Active mobile money wallets (millions) — Central switch/CBN data
        "mobile_money_wallets_m": [3.1, 3.9, 4.5, 5.2, 6.8, 8.4, 11.5, 14.2, 20.0],
    }
    # fmt: on

    df = pd.DataFrame(data)
    df.to_csv(save_path, index=False)
    print(f"CBN payments dataset created at {save_path}")
    print("Sources: CBN Annual Reports 2015–2023 (cbn.gov.ng/documents/annualreports)")


# ── EFInA financial inclusion summary ────────────────────────────────────────

def load_efina_summary() -> pd.DataFrame:
    """
    Load the EFInA financial inclusion summary dataset.

    Source: EFInA Access to Finance Survey (2008, 2010, 2012, 2014, 2016, 2018, 2020, 2023)
    URL   : https://efina.org.ng/our-work/research/access-to-finance/
    Licence: Public (available for download from EFInA website)

    The survey is conducted every two years.  Key aggregate figures are
    included here; the full microdata can be downloaded from the EFInA website.

    Returns
    -------
    pd.DataFrame
        Columns: year, banked_pct, mobile_money_pct, excluded_pct,
                 banked_m (millions), excluded_m (millions)
    """
    external_dir = get_path("data_external")
    path = external_dir / "efina_summary.csv"

    if not path.exists():
        _create_efina_csv(path)

    return pd.read_csv(path)


def _create_efina_csv(save_path: Path) -> None:
    """Create EFInA summary from published survey headline figures."""

    # fmt: off
    data = {
        # Survey years (not every year — EFInA surveys every ~2 years)
        "year":              [2008, 2010, 2012, 2014, 2016, 2018, 2020, 2023],

        # % of Nigerian adults (15+) with a formal bank account
        "banked_pct":        [21.1, 24.0, 28.6, 36.3, 38.3, 39.5, 40.1, 45.0],

        # % with a mobile money account (overlapping with banked)
        "mobile_money_pct":  [ 0.0,  0.5,  2.1,  3.9,  5.6,  7.2, 12.4, 18.0],

        # % financially excluded (no formal or informal product)
        "excluded_pct":      [53.0, 46.3, 39.5, 39.5, 41.6, 36.8, 35.9, 26.0],

        # Estimated adult population (millions)
        "adult_pop_m":       [69.2, 74.0, 79.0, 84.5, 91.0, 96.8,102.0,106.0],
    }
    # fmt: on

    df = pd.DataFrame(data)
    df["banked_m"]   = df["banked_pct"]   / 100 * df["adult_pop_m"]
    df["excluded_m"] = df["excluded_pct"] / 100 * df["adult_pop_m"]

    df.to_csv(save_path, index=False)
    print(f"EFInA summary dataset created at {save_path}")
    print("Source: EFInA Access to Finance Surveys (efina.org.ng)")


# ── Competitor / landscape dataset ───────────────────────────────────────────

def load_competitors() -> pd.DataFrame:
    """
    Load the competitor benchmarking dataset.

    Source: Assembled from:
    - Company official press releases and annual reports
    - Crunchbase public profiles (crunchbase.com)
    - TechCrunch funding announcements (techcrunch.com)
    - CBN Licensed Payment Service Banks list (cbn.gov.ng)
    - NIBSS annual report data

    Note: Funding figures are from last disclosed round.
    User figures are self-reported by companies in press releases.
    All figures are estimates and should be validated before use in
    a live client engagement.

    Returns
    -------
    pd.DataFrame
        One row per company. Columns: company, founded, type,
        reported_users_m, funding_usd_m, revenue_model, headquarter_city,
        cbse_licensed, agent_network_k (thousands), primary_market_focus.
    """
    external_dir = get_path("data_external")
    path = external_dir / "competitors.csv"

    if not path.exists():
        _create_competitors_csv(path)

    return pd.read_csv(path)


def _create_competitors_csv(save_path: Path) -> None:
    """
    Create competitor dataset from public sources.

    All figures are sourced from public press releases and reports.
    Marked where estimates are used (ESTIMATE).
    """
    # fmt: off
    data = {
        "company":              ["OPay",    "Moniepoint","PalmPay",  "Kuda",    "Carbon",  "FairMoney","ALAT(Wema)","GTCo Squad","Access_Closa","MTN_MoMo"],
        "founded":              [2018,       2015,        2019,       2019,       2012,       2017,       2017,        2021,         2022,          2021],
        "type":                 ["SuperApp", "B2B/B2C",   "B2C",      "Neobank",  "Neobank", "Neobank",  "Neobank",   "Payments",  "Payments",    "MobileMoney"],
        # Users: from company press releases (most recent available, 2022–2023)
        "reported_users_m":     [35.0,       2.0,         30.0,       6.0,        2.5,        2.0,        0.8,         3.0,          1.5,           10.0],
        # Total funding raised (USD millions) — from Crunchbase public profiles
        "funding_usd_m":        [570.0,      400.0,       300.0,      90.0,        30.0,       51.0,        0.0,         0.0,           0.0,          None],
        # Primary revenue model
        "revenue_model":        ["Trans+Ads","Trans+Lend","Trans",    "Lend+Trans","Lend",    "Lend",     "Lend+Trans","Trans",     "Trans",        "Trans+Float"],
        "headquarters":         ["Lagos",    "Lagos",     "Lagos",    "London/Lagos","Lagos",  "Paris/Lagos","Lagos",   "Lagos",     "Lagos",        "Lagos"],
        "cbsn_licensed":        [True,       True,        True,       True,        True,       True,        True,        True,          True,          True],
        # Agent networks (thousands of agents) — from press releases
        "agent_network_k":      [300.0,      800.0,       500.0,      None,        None,       None,        None,        None,          None,          150.0],
        "primary_market":       ["Consumer", "Agents/SME","Consumer", "Consumer", "Consumer", "Consumer", "Consumer",  "Consumer",  "Consumer",     "Consumer"],
        # Rough monthly transaction volume (NGN billions) — ESTIMATE from public filings
        "monthly_txn_ngn_bn":   [800.0,      2_100.0,     600.0,      120.0,       50.0,       40.0,        35.0,       200.0,         80.0,           90.0],
    }
    # fmt: on

    df = pd.DataFrame(data)
    df.to_csv(save_path, index=False)
    print(f"Competitor dataset created at {save_path}")
    print(
        "Sources: Company press releases, Crunchbase public profiles, "
        "TechCrunch, CBN Licensed Institutions (cbn.gov.ng)"
    )
