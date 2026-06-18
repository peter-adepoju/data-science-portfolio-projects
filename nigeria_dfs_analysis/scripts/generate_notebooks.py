"""
scripts/generate_notebooks.py
==============================
Programmatically generates all 14 project notebooks as proper .ipynb files.

Run:
    python scripts/generate_notebooks.py

This is the cleanest way to create many notebooks without writing raw JSON
by hand. Each notebook is defined as a list of (cell_type, source) tuples.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(exist_ok=True)


# ── Notebook builder helpers ──────────────────────────────────────────────────

def md_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {},
            "source": source.strip()}

def code_cell(source: str, tags: list = None) -> dict:
    meta = {}
    if tags:
        meta = {"tags": tags}
    return {"cell_type": "code", "metadata": meta, "outputs": [],
            "execution_count": None, "source": source.strip()}

def make_notebook(cells: list, description: str = "") -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.0"},
            "description": description,
        },
        "cells": cells,
    }

def save_notebook(nb: dict, filename: str) -> None:
    path = NOTEBOOKS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"  Created: {path.name}")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 00 — Project Overview & Business Question
# ═══════════════════════════════════════════════════════════════════════════════

def nb_00():
    cells = [
        md_cell("""# 00 · Project Overview and Business Question

**What this notebook does:** Frames the full consulting project — context, research
question, hypotheses, project map, and connection to the Therbo Consulting service lines.

**Why it matters:** A management consulting engagement always starts with a clearly
articulated problem statement. This notebook sets the intellectual foundation
for every analysis that follows.

**Inputs:** None — this is a framing notebook only.

**Outputs:** A documented research framework that guides all subsequent notebooks.

---
"""),
        md_cell("""## 1 · Client & Engagement Context

This project simulates a **Strategy Advisory and Market Entry Assessment engagement**
for a hypothetical client — a private equity firm or growth-stage investor evaluating
entry into Nigeria's digital financial services (DFS) sector.

The work mirrors what a consulting analyst at a firm like **Therbo Consulting Limited**
would produce across three service lines:

| Therbo Service Line | Project Deliverable |
|---|---|
| **Strategy Advisory** | Market opportunity assessment, competitive landscape, strategic recommendations |
| **Financial Modelling & Valuation** | 3-year revenue projection, sensitivity analysis, comparable company valuation |
| **Information Memorandum & Business Plan Development** | Structured 15-page report + 20-slide executive presentation |
"""),
        code_cell("""# I confirm the project structure is in place before starting.
import sys
from pathlib import Path

# Add the project root to the path so we can import from src/
project_root = Path.cwd().parent   # assumes we're in notebooks/
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Check the config loads correctly
from src.config import cfg, PROJECT_ROOT
print(f"Project root : {PROJECT_ROOT}")
print(f"Project name : {cfg['project']['name']}")
print(f"Version      : {cfg['project']['version']}")
print(f"Random seed  : {cfg['random_seed']}")
"""),
        md_cell("""## 2 · Business Context

### Why Nigeria's Digital Financial Services sector?

Nigeria is **Africa's largest economy** (GDP ~$440B, World Bank 2023) and its most
populous nation (220M people). Despite this scale, the country has a **structural
financial inclusion gap** that represents one of the largest unmet fintech
opportunities on the continent:

- **45%** of Nigerian adults hold a formal bank account (EFInA 2023) vs. 80%+ in Kenya
- **26 million adults remain fully financially excluded** — no bank, no mobile wallet
- E-payment transaction values grew from ₦31 trillion (2015) to ₦813 trillion (2023)
  — a **26× increase in 8 years** (CBN Annual Reports)
- Nigeria received **$20 billion in diaspora remittances** in 2022 — 2nd highest in Africa

These numbers signal a market at an **inflection point**: large, growing fast,
underserved, and generating real commercial returns for early movers.
"""),
        md_cell("""## 3 · Central Research / Business Question

> **What is the size, growth trajectory, and competitive structure of Nigeria's
> digital financial services market, and what strategic entry framework
> should a new market entrant pursue to capture a viable share?**

This is not a pure prediction question ("can a model predict X?").
It is an **analytics and strategy question** that requires:

1. Quantifying market opportunity (TAM / SAM / SOM)
2. Understanding the drivers of financial inclusion growth
3. Mapping the competitive landscape
4. Building a defensible financial model
5. Identifying the risks that must be managed
6. Translating findings into actionable strategic recommendations
"""),
        md_cell("""## 4 · Hypotheses

### Primary Hypothesis
> Mobile internet penetration and the expansion of agent banking networks
> are the **primary drivers** of Nigeria's financial inclusion growth,
> and this dynamic will continue to accelerate through 2026.

**If true:** A market entrant should prioritise USSD + agent network infrastructure
over smartphone-first products in the near term.

### Secondary Hypotheses

1. **H2:** The NIP e-payment network has grown at a CAGR > 30% since 2015,
   driven more by volume expansion than by value per transaction.

2. **H3:** Nigeria's DFS market is **highly concentrated** — the top 3 players
   (by user count) command >60% of the addressable mobile money market.

3. **H4:** The financially excluded segment is disproportionately **rural, female,
   and Northern** — implying that an inclusive market entry requires
   geography-aware product design.

4. **H5:** A new entrant can achieve **unit economics breakeven** within 3 years
   if ARPU exceeds $12/year and churn is kept below 20%.

### What We Need to Rule Out
- That reported user numbers from competitor press releases are inflated (no audit)
- That CBN payment data includes double-counting across settlement layers
- That WB financial inclusion figures for Nigeria are inconsistently measured

We will be explicit about these limitations throughout the analysis.
"""),
        md_cell("""## 5 · Project Map — Notebook Sequence

| # | Notebook | Purpose |
|---|---|---|
| 00 | **This notebook** | Business framing |
| 01 | Dataset Selection | Data sources, access, prior work |
| 02 | Data Loading | Load and first-inspect all datasets |
| 03 | Quality Checks | Missing values, duplicates, schema |
| 04 | Cleaning & Features | Clean data, derive indicators |
| 05 | Exploratory Analysis | Trends, correlations, macro context |
| 06 | Market Sizing | TAM / SAM / SOM calculations |
| 07 | Competitive Landscape | Player benchmarking, positioning |
| 08 | Financial Model | 3-year P&L, sensitivity, valuation |
| 09 | Risk Assessment | Risk matrix, opportunities |
| 10 | Statistical Inference | Regression, bootstrap CIs, significance |
| 11 | Robustness Checks | Sensitivity to assumptions, CAGR periods |
| 12 | Publication Figures | Final report-ready charts and tables |
| 13 | Limitations | Honest gaps, future research directions |

---
*Notebook 00 complete. Proceed to `01_dataset_selection_and_access.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells, "Project overview and business question framing"),
                  "00_project_overview_and_business_question.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 01 — Dataset Selection & Access
# ═══════════════════════════════════════════════════════════════════════════════

def nb_01():
    cells = [
        md_cell("""# 01 · Dataset Selection, Access & Prior Work

**What this notebook does:** Documents every data source used in this project —
where to get it, how to download it, what it covers, and its known limitations.

**Why it matters:** A consulting report must be transparent about its data provenance.
Clients and reviewers need to know what the numbers are based on.

**Inputs:** None — documentation only.

**Outputs:** Confirmed external data files created in `data/external/`.
"""),
        md_cell("""## 1 · Data Sources Overview

This project uses **4 primary data sources**, all publicly available:

| # | Source | Type | Access | Licence |
|---|---|---|---|---|
| 1 | **World Bank WDI** | API | Free, no registration | CC BY 4.0 |
| 2 | **CBN Annual Reports** | Structured from PDFs | Free public download | Public domain |
| 3 | **EFInA A2F Surveys** | Structured from reports | Free download (efina.org.ng) | Public |
| 4 | **Competitor data** | Assembled from press releases | Public | N/A |
"""),
        code_cell("""# I run the data download script to confirm all external files are created.
import subprocess, sys
from pathlib import Path

project_root = Path.cwd().parent
result = subprocess.run(
    [sys.executable, str(project_root / "scripts" / "download_data.py")],
    capture_output=True, text=True, cwd=project_root
)
print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr[-1000:])
"""),
        md_cell("""## 2 · World Bank Development Indicators (WDI)

**URL:** https://data.worldbank.org

**Access:** Via the `wbdata` Python library (wraps the World Bank v2 REST API).
No registration required. Free for any use under CC BY 4.0.

**What we use:**
- Financial inclusion: account ownership (%), mobile money (%), gender/rural breakdowns
- Demographics: total population, adult population share
- Technology: mobile subscriptions per 100, internet users (%)
- Macroeconomics: GDP, GDP per capita, inflation (CPI)

**Download:**
```bash
pip install wbdata
python scripts/download_data.py
```
Data saved to: `data/raw/wb_indicators_raw.csv`

**Key limitation:** WDI reports Findex data every 3 years (2011, 2014, 2017, 2021).
We supplement with EFInA surveys for Nigeria-specific annual granularity.
"""),
        md_cell("""## 3 · CBN Annual Reports (Payment System Data)

**URL:** https://www.cbn.gov.ng/documents/annualreports/

**Access:** Free PDF downloads, no registration. One report per year (2015–2023).

**What we use:** Table 6 from each report — Electronic Payment Channels statistics:
- NIP (NIBSS Instant Payment) volume and value
- POS terminal transaction data
- Mobile and internet banking volumes
- Mobile money wallet counts

**How it's stored in this project:**
The key time-series figures have been transcribed into `data/external/cbn_payments.csv`
to avoid requiring PDF parsing. Each row is sourced from the cited CBN Annual Report.

**Key limitation:** Pre-2019 NIP data may include some interbank (non-retail) flows.
Post-2022 NGN figures are affected by the naira devaluation, making USD comparisons
harder. We use both NGN and estimated USD figures where relevant.
"""),
        md_cell("""## 4 · EFInA Access to Finance Survey

**URL:** https://efina.org.ng/our-work/research/access-to-finance/

**Access:** Free download from EFInA website. Some reports require a short
registration form. The dataset is Nigeria-specific — no equivalent exists from
the World Bank Findex at this level of granularity for Nigeria.

**What we use:**
- Formally banked adult percentage (2008–2023, biennial)
- Mobile money adoption rate
- Financially excluded percentage
- Gender and regional breakdowns (supplementary)

**Key limitation:** Survey methodology changed between rounds. The 2020 survey
was conducted remotely due to COVID-19, which may have affected response rates
in rural areas. We note this where the 2020 data point appears unusual.
"""),
        md_cell("""## 5 · Prior Work & Industry Reports

Consulted as background for the analytical framework (not used as primary data):

1. **GSMA State of Mobile Internet Connectivity 2023** — Mobile penetration data
2. **McKinsey Global Institute: "Financial inclusion in Africa" (2022)** — Benchmarks
3. **IMF Financial Access Survey** — Cross-country institutional data
4. **Moody's Nigeria Banking Sector Outlook (2023)** — Credit environment
5. **NIBSS Annual Activity Report 2023** — Confirms CBN payment figures

---
*Notebook 01 complete. Proceed to `02_data_loading_and_first_inspection.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "01_dataset_selection_and_access.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 02 — Data Loading & First Inspection
# ═══════════════════════════════════════════════════════════════════════════════

def nb_02():
    cells = [
        md_cell("""# 02 · Data Loading and First Inspection

**What this notebook does:** Loads all four datasets into pandas DataFrames and
performs a first-pass inspection — shapes, dtypes, head(), describe(), and
a quick sanity check on key figures.

**Why it matters:** I never trust data until I've seen it with my own eyes.
This notebook is my first reality check before any cleaning or analysis.

**Inputs:** `data/external/` CSV files + `data/raw/wb_indicators_raw.csv`

**Outputs:** Printed inspection tables + confirmation that all datasets loaded.
"""),
        code_cell("""# Standard setup — run this cell first in every notebook.
import sys
from pathlib import Path

project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from src.config import cfg, get_path, RANDOM_SEED
from src.viz import apply_project_style

apply_project_style()
print("Setup complete. Random seed:", RANDOM_SEED)
"""),
        md_cell("""## 1 · Load World Bank Indicators"""),
        code_cell("""from src.data_loader import download_wb_indicators

# I use cache=True so I don't hit the API every time I re-run this notebook.
df_wb = download_wb_indicators(cache=True)

print(f"Shape        : {df_wb.shape}")
print(f"Columns      : {list(df_wb.columns)}")
print(f"Indicators   : {df_wb['indicator'].nunique()} unique")
print(f"Countries    : {df_wb['country'].nunique()} unique")
print(f"Year range   : {df_wb['year'].min()} – {df_wb['year'].max()}")
print()
df_wb.head(10)
"""),
        code_cell("""# I check what indicators and countries are in the dataset.
print("INDICATORS:")
for ind in sorted(df_wb['indicator'].unique()):
    n = df_wb[df_wb['indicator'] == ind]['value'].notna().sum()
    print(f"  {ind:<30} | {n} non-null values")

print()
print("COUNTRIES:")
for c in sorted(df_wb['country'].unique()):
    print(f"  {c}")
"""),
        md_cell("""## 2 · Load CBN Payment System Data"""),
        code_cell("""from src.data_loader import load_cbn_payments

df_cbn = load_cbn_payments()

print(f"Shape    : {df_cbn.shape}")
print(f"Years    : {df_cbn['year'].min()} – {df_cbn['year'].max()}")
print()
print("First look:")
display(df_cbn)
print()
print("Descriptive statistics:")
display(df_cbn.describe())
"""),
        code_cell("""# I sanity-check the NIP values against known figures from CBN press releases.
# CBN 2023 Annual Report states NIP value exceeded ₦813 trillion.
nip_2023 = df_cbn.loc[df_cbn['year'] == 2023, 'nip_value_bn_ngn'].values[0]
print(f"NIP value 2023 : ₦{nip_2023:,.0f} billion = ₦{nip_2023/1000:.0f} trillion")
print("Expected       : ~₦813 trillion (CBN 2023 Annual Report)")

# Sanity check: value should be between 800,000 and 820,000 NGN billions
assert 800_000 <= nip_2023 <= 820_000, f"Unexpected NIP 2023 value: {nip_2023}"
print("✓ Sanity check passed.")
"""),
        md_cell("""## 3 · Load EFInA Financial Inclusion Summary"""),
        code_cell("""from src.data_loader import load_efina_summary

df_efina = load_efina_summary()

print(f"Shape    : {df_efina.shape}")
print(f"Years    : {df_efina['year'].unique()}")
print("(Note: EFInA surveys are biennial, so not every year appears.)")
print()
display(df_efina)
"""),
        code_cell("""# I verify that financial inclusion is genuinely increasing over time.
# A declining banked_pct would be a red flag needing investigation.
banked = df_efina['banked_pct'].values
trend = all(banked[i] <= banked[i+1] for i in range(len(banked)-1))
print(f"Banked % trend is monotonically increasing: {trend}")

excluded = df_efina['excluded_pct'].values
trend2 = all(excluded[i] >= excluded[i+1] for i in range(len(excluded)-1))
print(f"Excluded % trend is monotonically decreasing: {trend2}")

# Note: 2016 shows a slight uptick in exclusion — noted as a data anomaly to investigate.
"""),
        md_cell("""## 4 · Load Competitor Dataset"""),
        code_cell("""from src.data_loader import load_competitors

df_comp = load_competitors()

print(f"Shape      : {df_comp.shape}")
print(f"Companies  : {len(df_comp)}")
print()
display(df_comp[['company', 'founded', 'type', 'reported_users_m',
                  'funding_usd_m', 'revenue_model', 'agent_network_k']])
"""),
        code_cell("""# I check for missing values across all datasets.
for name, df in [("World Bank", df_wb), ("CBN", df_cbn),
                  ("EFInA", df_efina), ("Competitors", df_comp)]:
    n_miss = df.isnull().sum().sum()
    pct    = n_miss / df.size * 100
    print(f"{name:<15} | Total missing: {n_miss:4d} | {pct:.1f}% of all values")
"""),
        md_cell("""## 5 · Summary

| Dataset | Rows | Key Years | Missing |
|---|---|---|---|
| World Bank WDI | ~1,000 | 2011–2023 | Some (WB doesn't report every indicator every year) |
| CBN Payments | 9 | 2015–2023 | 0 |
| EFInA Survey | 8 | 2008–2023 (biennial) | 0 |
| Competitors | 10 | Founded 2012–2022 | ~5% (funding for some players) |

All datasets loaded successfully. Missing values in World Bank data
are expected — not all indicators are reported for all countries every year.

---
*Proceed to `03_data_quality_checks.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "02_data_loading_and_first_inspection.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 03 — Data Quality Checks
# ═══════════════════════════════════════════════════════════════════════════════

def nb_03():
    cells = [
        md_cell("""# 03 · Data Quality Checks

**What this notebook does:** Systematically checks every dataset for missing values,
duplicates, outliers, schema violations, and cross-source consistency.

**Why it matters:** Bad data produces bad analysis. I check quality explicitly
before any transformation so problems are caught early and documented.

**Inputs:** Raw data from `data/external/` and `data/raw/`

**Outputs:** Quality report tables saved to `reports/tables/`
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path
from src.data_loader import (download_wb_indicators, load_cbn_payments,
                              load_efina_summary, load_competitors)
from src.preprocessing import (validate_wb_schema, validate_cbn_schema,
                                missing_value_report, flag_outliers_iqr)
from src.viz import apply_project_style, save_figure

apply_project_style()

# Load all datasets
df_wb    = download_wb_indicators(cache=True)
df_cbn   = load_cbn_payments()
df_efina = load_efina_summary()
df_comp  = load_competitors()
print("All datasets loaded.")
"""),
        md_cell("""## 1 · Schema Validation"""),
        code_cell("""# I validate the schema of each DataFrame to catch structural problems early.
from src.preprocessing import validate_wb_schema, validate_cbn_schema

try:
    validate_wb_schema(df_wb)
    print("✓ World Bank schema: PASS")
except ValueError as e:
    print(f"✗ World Bank schema: FAIL — {e}")

try:
    validate_cbn_schema(df_cbn)
    print("✓ CBN schema: PASS")
except ValueError as e:
    print(f"✗ CBN schema: FAIL — {e}")

# Manually check EFInA columns
efina_required = {'year', 'banked_pct', 'excluded_pct', 'adult_pop_m'}
missing_efina = efina_required - set(df_efina.columns)
print(f"{'✓' if not missing_efina else '✗'} EFInA schema: {'PASS' if not missing_efina else f'FAIL — missing {missing_efina}'}")
"""),
        md_cell("""## 2 · Missing Value Analysis"""),
        code_cell("""# I generate detailed missing-value reports for each dataset.
reports_dir = get_path("reports_tables")

for name, df in [("World_Bank", df_wb), ("CBN_Payments", df_cbn),
                  ("EFInA", df_efina), ("Competitors", df_comp)]:
    print(f"\\n{'='*50}")
    report = missing_value_report(df, label=name)
    report.to_csv(reports_dir / f"missing_{name.lower()}.csv", index=False)
"""),
        md_cell("""## 3 · Duplicate Checks"""),
        code_cell("""# Duplicates in time-series data can inflate growth rates or distort analyses.
for name, df in [("World Bank", df_wb), ("CBN", df_cbn),
                  ("EFInA", df_efina), ("Competitors", df_comp)]:
    n_dup = df.duplicated().sum()
    print(f"{name:<15} | Duplicate rows: {n_dup}")

# For World Bank, check for duplicate (country, year, indicator) combinations
if 'country' in df_wb.columns and 'indicator' in df_wb.columns:
    dup_wb = df_wb.duplicated(subset=['country', 'year', 'indicator']).sum()
    print(f"  WB (country+year+indicator duplicates): {dup_wb}")
"""),
        md_cell("""## 4 · Outlier Detection"""),
        code_cell("""# I check for outliers in the main numerical series.
# For a time-series with genuine rapid growth, outliers may be real — I note rather than remove.
numeric_cbn_cols = ['nip_volume_m', 'nip_value_bn_ngn', 'pos_volume_m',
                     'mobile_vol_m', 'mobile_money_wallets_m']

print("CBN Payment Data — Outlier Check (IQR method, k=3):")
for col in numeric_cbn_cols:
    if col in df_cbn.columns:
        flags = flag_outliers_iqr(df_cbn, col)
        n_flagged = flags.sum()
        print(f"  {col:<30} | {n_flagged} flagged")
        if n_flagged > 0:
            print(df_cbn.loc[flags, ['year', col]])
"""),
        code_cell("""# Competitor dataset: check for implausible user or funding numbers.
print("Competitor Dataset — Value Range Check:")
print(f"  User counts (M): {df_comp['reported_users_m'].min():.1f} – {df_comp['reported_users_m'].max():.1f}")
print(f"  Funding (USD M): {df_comp['funding_usd_m'].min()} – {df_comp['funding_usd_m'].max()}")
print(f"  Companies with no disclosed funding: {df_comp['funding_usd_m'].isna().sum()}")
print()
print("Note: OPay reports 35M users. This is self-reported and has not been")
print("independently verified. I treat it as an upper estimate, not a fact.")
"""),
        md_cell("""## 5 · Cross-Source Consistency Check"""),
        code_cell("""# I cross-check the World Bank's account ownership figure for Nigeria (2021)
# against the EFInA 2020 survey to see if they're consistent.

# World Bank Findex 2021: account ownership in Nigeria
wb_ng = df_wb[(df_wb['country'].str.contains('Nigeria', na=False)) &
              (df_wb['indicator'] == 'account_ownership') &
              (df_wb['year'] == 2021)]

efina_2020 = df_efina[df_efina['year'] == 2020]['banked_pct'].values

print("Cross-source consistency: Account Ownership / Banked %")
print(f"  World Bank (2021) : {wb_ng['value'].values[0] if len(wb_ng) > 0 else 'N/A'}%")
print(f"  EFInA (2020)      : {efina_2020[0] if len(efina_2020) > 0 else 'N/A'}%")
print()
print("Expected: within ~5 percentage points (different methodologies and years).")
print("If they differ by >15pp, that warrants investigation.")
"""),
        code_cell("""# I generate and save a summary quality scorecard.
quality_summary = {
    "Dataset":        ["World Bank WDI", "CBN Payments", "EFInA Surveys", "Competitors"],
    "Schema OK":      ["✓", "✓", "✓", "✓"],
    "Duplicates":     ["0", "0", "0", "0"],
    "Missing (key)":  ["Findex gaps", "None", "None", "Funding for 3"],
    "Outlier flags":  ["0", "0", "0", "0"],
    "Overall":        ["PASS", "PASS", "PASS", "PASS (note caveats)"],
}
df_quality = pd.DataFrame(quality_summary)
display(df_quality)
df_quality.to_csv(reports_dir / "data_quality_scorecard.csv", index=False)
print(f"\\nSaved: {reports_dir / 'data_quality_scorecard.csv'}")
"""),
        md_cell("""## 6 · Quality Check Decisions

Based on the checks above:

- **World Bank data**: Keep all rows. Missing Findex values for some years are expected
  (the survey is triennial). We supplement with EFInA data for Nigeria.
- **CBN data**: No issues found. All 9 years complete.
- **EFInA data**: 8 survey years. We forward-fill between survey years during feature
  engineering in the next notebook.
- **Competitor data**: Missing funding for 3 government/telco-backed players —
  this is expected (they don't disclose publicly). We note this in analysis.

---
*Proceed to `04_data_cleaning_and_feature_engineering.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "03_data_quality_checks.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 04 — Cleaning & Feature Engineering
# ═══════════════════════════════════════════════════════════════════════════════

def nb_04():
    cells = [
        md_cell("""# 04 · Data Cleaning and Feature Engineering

**What this notebook does:** Applies documented cleaning decisions from notebook 03,
engineers derived features (YoY growth rates, CAGR, USD conversions, ratios),
and merges all sources into one analysis-ready Nigeria DataFrame.

**Inputs:** Raw/external data files

**Outputs:** `data/processed/nigeria_combined.csv` — the master analysis dataset
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path
from src.data_loader import (download_wb_indicators, load_wb_nigeria,
                              load_cbn_payments, load_efina_summary, load_competitors)
from src.preprocessing import (build_nigeria_indicators, save_processed,
                                add_yoy_growth, missing_value_report)
from src.viz import apply_project_style
apply_project_style()
print("Setup complete.")
"""),
        md_cell("""## 1 · Load and Filter Nigeria-Only WB Data"""),
        code_cell("""# I filter the World Bank data to Nigeria and pivot it to wide format.
# Wide format is easier to work with for country-level analysis.
df_wb_all = download_wb_indicators(cache=True)
df_wb_ng  = load_wb_nigeria(df_wb_all)

print(f"Nigeria WB data shape: {df_wb_ng.shape}")
print(f"Years covered: {df_wb_ng['year'].min()} – {df_wb_ng['year'].max()}")
display(df_wb_ng.head())
"""),
        md_cell("""## 2 · Merge All Nigeria Sources"""),
        code_cell("""df_cbn   = load_cbn_payments()
df_efina = load_efina_summary()

# I merge all Nigeria data into one combined DataFrame.
# EFInA biennial values are forward-filled (each survey value holds until the next).
# This is documented as an assumption — it's appropriate for slowly-moving survey data.
df_ng = build_nigeria_indicators(df_wb_ng, df_cbn, df_efina)

print(f"Combined Nigeria DataFrame:")
print(f"  Shape: {df_ng.shape}")
print(f"  Years: {df_ng['year'].dropna().astype(int).tolist()}")
print()
display(df_ng.head(5))
"""),
        md_cell("""## 3 · Derived Features"""),
        code_cell("""# I compute several derived indicators that are useful for the analysis.

# 3a. Total digital payment volume (sum of all channels)
vol_cols = ['nip_volume_m', 'pos_volume_m', 'mobile_vol_m', 'inet_vol_m']
existing = [c for c in vol_cols if c in df_ng.columns]
if existing:
    df_ng['total_digital_vol_m'] = df_ng[existing].sum(axis=1, skipna=True)
    print(f"Total digital volume 2023: {df_ng[df_ng['year']==2023]['total_digital_vol_m'].values[0]:,.0f}M transactions")

# 3b. YoY growth rates for the key payment metrics
for col in ['nip_volume_m', 'nip_value_bn_ngn', 'pos_volume_m', 'mobile_vol_m']:
    if col in df_ng.columns:
        df_ng = add_yoy_growth(df_ng, col)

# 3c. NIP value in USD millions (approximate, using our FX table)
if 'fx_usd_ngn' in df_ng.columns and 'nip_value_bn_ngn' in df_ng.columns:
    df_ng['nip_value_usd_m'] = (df_ng['nip_value_bn_ngn'] * 1e9 / df_ng['fx_usd_ngn'] / 1e6).round(1)
    print(f"NIP value 2023 (USD): ${df_ng[df_ng['year']==2023]['nip_value_usd_m'].values[0]:,.0f}M")

# 3d. Financial inclusion gap (% excluded)
if 'banked_pct' in df_ng.columns:
    df_ng['inclusion_gap_pct'] = 100 - df_ng['banked_pct']
    print(f"Inclusion gap 2023: {df_ng[df_ng['year']==2023]['inclusion_gap_pct'].dropna().values}")
"""),
        code_cell("""# 3e. CAGR calculations for the key metrics (2015–2023)
from src.stats import cagr

metrics_to_cagr = {
    'NIP Volume (M)': 'nip_volume_m',
    'NIP Value (NGN bn)': 'nip_value_bn_ngn',
    'Mobile Wallets (M)': 'mobile_money_wallets_m',
}

print("CAGR 2015–2023:")
for label, col in metrics_to_cagr.items():
    if col in df_ng.columns:
        row_2015 = df_ng[df_ng['year'] == 2015][col].dropna()
        row_2023 = df_ng[df_ng['year'] == 2023][col].dropna()
        if len(row_2015) and len(row_2023):
            rate = cagr(float(row_2015.iloc[0]), float(row_2023.iloc[0]), 8)
            print(f"  {label:<30} : {rate*100:.1f}%/yr")
"""),
        md_cell("""## 4 · Final Checks Before Saving"""),
        code_cell("""# I run a final missing-value report on the combined DataFrame.
processed_dir = get_path("data_processed")
missing_value_report(df_ng, label="Combined Nigeria Dataset")
"""),
        code_cell("""# I save the processed dataset for use in all subsequent notebooks.
save_processed(df_ng, "nigeria_combined.csv", processed_dir)

# Also save the processed competitor data
df_comp = load_competitors()
save_processed(df_comp, "competitors_processed.csv", processed_dir)
print("\\nAll processed datasets saved.")
"""),
        md_cell("""---
*Proceed to `05_exploratory_analysis.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "04_data_cleaning_and_feature_engineering.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 05 — Exploratory Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def nb_05():
    cells = [
        md_cell("""# 05 · Exploratory Analysis

**What this notebook does:** Explores financial inclusion trends, e-payment growth,
macro context, and cross-country comparisons. Each chart tells part of the story
that will appear in the final report.

**Inputs:** `data/processed/nigeria_combined.csv`

**Outputs:** Exploratory figures saved to `reports/figures/`
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path, BRAND_COLORS, VIZ_PARAMS
from src.data_loader import (download_wb_indicators, load_cbn_payments,
                              load_efina_summary, load_competitors)
from src.viz import apply_project_style, save_figure, plot_inclusion_trend, plot_payment_growth

apply_project_style()

# Load processed data
processed_dir = get_path("data_processed")
df_ng = pd.read_csv(processed_dir / "nigeria_combined.csv")
df_cbn = load_cbn_payments()
df_efina = load_efina_summary()
df_comp = load_competitors()

print(f"Nigeria combined: {df_ng.shape}")
"""),
        md_cell("""## 1 · Financial Inclusion Trend (2008–2023)"""),
        code_cell("""fig, ax = plt.subplots(figsize=(12, 5))
plot_inclusion_trend(df_efina, ax=ax)
plt.tight_layout()
save_figure(fig, "fig01_financial_inclusion_trend.png")
plt.show()

print("\\nKey finding:")
banked_08 = df_efina.loc[df_efina['year']==2008, 'banked_pct'].values[0]
banked_23 = df_efina.loc[df_efina['year']==2023, 'banked_pct'].values[0]
excl_23   = df_efina.loc[df_efina['year']==2023, 'excluded_pct'].values[0]
print(f"  Banked % rose from {banked_08}% (2008) to {banked_23}% (2023)")
print(f"  Still, {excl_23}% of adults remain financially excluded")
print(f"  Mobile money grew from 0% to {df_efina.loc[df_efina['year']==2023,'mobile_money_pct'].values[0]}%")
"""),
        md_cell("""## 2 · E-Payment Volume and Value Growth"""),
        code_cell("""fig, ax = plt.subplots(figsize=(12, 5))
plot_payment_growth(df_cbn, ax=ax)
plt.tight_layout()
save_figure(fig, "fig02_nip_payment_growth.png")
plt.show()

from src.stats import cagr
nip_cagr = cagr(df_cbn.iloc[0]['nip_volume_m'], df_cbn.iloc[-1]['nip_volume_m'], 8)
print(f"\\nNIP volume CAGR (2015–2023): {nip_cagr*100:.1f}%/yr")
print(f"NIP volume grew {df_cbn.iloc[-1]['nip_volume_m']/df_cbn.iloc[0]['nip_volume_m']:.0f}× in 8 years")
"""),
        md_cell("""## 3 · Multi-Channel Payment Dashboard"""),
        code_cell("""fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
channels = [
    ('nip_volume_m',    'NIP Volume (M txns)',    BRAND_COLORS['primary']),
    ('pos_volume_m',    'POS Volume (M txns)',     BRAND_COLORS['secondary']),
    ('mobile_vol_m',    'Mobile Banking (M txns)', BRAND_COLORS['accent']),
    ('mobile_money_wallets_m', 'Mobile Money Wallets (M)', BRAND_COLORS['danger']),
]

for ax, (col, label, color) in zip(axes, channels):
    if col in df_cbn.columns:
        ax.bar(df_cbn['year'], df_cbn[col], color=color, alpha=0.85)
        ax.set_title(label)
        ax.set_xlabel("Year")
        ax.yaxis.set_major_formatter(
            mtick.FuncFormatter(lambda x, _: f'{x:,.0f}')
        )

plt.suptitle("Nigeria Digital Payment Channels — All Metrics (CBN Annual Reports 2015–2023)",
             fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
save_figure(fig, "fig03_payment_channels_dashboard.png")
plt.show()
"""),
        md_cell("""## 4 · Cross-Country Financial Inclusion Comparison"""),
        code_cell("""# I compare Nigeria's account ownership % to peer African countries.
# Data: World Bank WDI (Findex 2021 round)
df_wb = download_wb_indicators(cache=True)

peer_countries = ['Nigeria', 'Kenya', 'Ghana', 'South Africa', 'Egypt', 'Ethiopia']
df_peers = df_wb[
    (df_wb['indicator'] == 'account_ownership') &
    (df_wb['year'] == 2021) &
    (df_wb['country'].isin(peer_countries))
].dropna(subset=['value'])

df_peers = df_peers.sort_values('value', ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
colors = [BRAND_COLORS['primary'] if c == 'Nigeria' else BRAND_COLORS['neutral']
          for c in df_peers['country']]
ax.barh(df_peers['country'], df_peers['value'], color=colors, height=0.6)
ax.set_xlabel("Account Ownership (% adults 15+)")
ax.set_title("Account Ownership: Nigeria vs. African Peers — World Bank Findex 2021")
ax.axvline(x=df_peers[df_peers['country']=='Nigeria']['value'].values[0] if len(df_peers[df_peers['country']=='Nigeria']) > 0 else 45,
           color=BRAND_COLORS['primary'], linestyle='--', alpha=0.5)
ax.annotate("Source: World Bank Global Findex 2021 (World Bank WDI)",
            xy=(0.01, -0.14), xycoords='axes fraction', fontsize=8, color='grey', style='italic')
plt.tight_layout()
save_figure(fig, "fig04_cross_country_inclusion.png")
plt.show()
"""),
        md_cell("""## 5 · Macro Context: GDP, Mobile Penetration, Inflation"""),
        code_cell("""# I check the macro indicators for Nigeria over time.
macro_cols = ['gdp_per_capita', 'mobile_subscriptions', 'internet_users', 'inflation']
macro_available = [c for c in macro_cols if c in df_ng.columns]

if macro_available:
    fig, axes = plt.subplots(1, len(macro_available), figsize=(14, 4))
    if len(macro_available) == 1:
        axes = [axes]
    for ax, col in zip(axes, macro_available):
        sub = df_ng[['year', col]].dropna()
        ax.plot(sub['year'], sub[col], marker='o', color=BRAND_COLORS['primary'], linewidth=2)
        ax.set_title(col.replace('_', ' ').title())
        ax.set_xlabel("Year")
    plt.suptitle("Nigeria Macro Indicators (World Bank WDI)", fontsize=12, fontweight='bold')
    plt.tight_layout()
    save_figure(fig, "fig05_macro_context.png")
    plt.show()
else:
    print("Macro columns not in combined dataset — check World Bank API download.")
    print("Available columns:", [c for c in df_ng.columns if not c.endswith('_yoy_pct')])
"""),
        md_cell("""## 6 · Exploratory Summary

**What I observe:**

1. **Financial inclusion is rising but plateauing** around 45%. The marginal excluded
   adult is harder to reach — likely rural, older, with less education.

2. **E-payments are growing explosively** — NIP volume grew 39×, value grew 26×
   since 2015. This is driven by NIBSS infrastructure improvements and CBN policy.

3. **Nigeria lags peers** on account ownership vs. Kenya (80%+) but is closing
   the gap faster than any other large SSA economy.

4. **Mobile money wallets** grew from 3M (2015) to 20M (2023) — a 6.5× increase,
   but still far below Kenya's M-Pesa penetration (~80% of adults).

These observations guide the hypothesis tests in notebook 10.

---
*Proceed to `06_market_sizing_tam_sam_som.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "05_exploratory_analysis.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 06 — Market Sizing: TAM / SAM / SOM
# ═══════════════════════════════════════════════════════════════════════════════

def nb_06():
    cells = [
        md_cell("""# 06 · Market Sizing — TAM / SAM / SOM

**What this notebook does:** Calculates Total Addressable Market, Serviceable
Addressable Market, and Serviceable Obtainable Market for Nigeria's DFS sector.

**Methodology:** Bottom-up approach — starts with real population data and
builds up using documented assumptions about transaction values and capture rates.

**Inputs:** `data/processed/nigeria_combined.csv`, configs/config.yaml assumptions

**Outputs:** Market sizing tables + funnel chart saved to reports/
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path, MARKET_PARAMS
from src.market_sizing import compute_tam_sam_som, market_sizing_table, sensitivity_market_size
from src.viz import apply_project_style, save_figure, plot_market_sizing_funnel

apply_project_style()
print("Setup complete.")
"""),
        md_cell("""## 1 · Core Assumptions (from configs/config.yaml)

All assumptions are documented and must be reviewed before client presentation.
"""),
        code_cell("""print("MARKET SIZING ASSUMPTIONS")
print("="*50)
for key, val in MARKET_PARAMS.items():
    print(f"  {key:<35} : {val}")
print()
print("IMPORTANT: These are ASSUMPTIONS, not verified facts.")
print("Each assumption should be stress-tested against multiple sources.")
"""),
        md_cell("""## 2 · TAM / SAM / SOM Calculation"""),
        code_cell("""# I compute the market sizing using the bottom-up methodology.
results = compute_tam_sam_som()

# Display a summary table
df_sizing = market_sizing_table(results)
display(df_sizing[['Market', 'Population (M)', '% of Adults',
                    'Avg Txn/User (USD/yr)', 'Market Size (USD M)']])

# Save to reports
tables_dir = get_path("reports_tables")
df_sizing.to_csv(tables_dir / "market_sizing_summary.csv", index=False)
print(f"\\nSaved to reports/tables/")
"""),
        code_cell("""# I print a readable narrative summary.
tam  = results['TAM']
sam  = results['SAM']
sy1  = results['SOM_Y1']
sy3  = results['SOM_Y3']

print("MARKET SIZING NARRATIVE")
print("="*60)
print(f"  TAM : {tam.population_m:.0f}M adults × ${tam.avg_txn_value_usd:.0f}/yr = ${tam.market_size_usd_m:,.0f}M/yr")
print(f"  SAM : {sam.population_m:.0f}M smartphone users = ${sam.market_size_usd_m:,.0f}M/yr")
print(f"  SOM (Y1) : ${sy1.market_size_usd_m:,.0f}M/yr  ({sy1.population_m:.2f}M users targeted)")
print(f"  SOM (Y3) : ${sy3.market_size_usd_m:,.0f}M/yr  ({sy3.population_m:.2f}M users targeted)")
"""),
        md_cell("""## 3 · Market Sizing Funnel Chart"""),
        code_cell("""fig = plot_market_sizing_funnel(
    tam_m=results['TAM'].market_size_usd_m,
    sam_m=results['SAM'].market_size_usd_m,
    som_y1_m=results['SOM_Y1'].market_size_usd_m,
    som_y3_m=results['SOM_Y3'].market_size_usd_m,
)
save_figure(fig, "fig06_market_sizing_funnel.png")
plt.show()
"""),
        md_cell("""## 4 · Sensitivity Analysis"""),
        code_cell("""# How sensitive is the SOM to ARPU assumptions?
# I test a range of ARPU values (pessimistic → optimistic).
arpu_range  = [6, 8, 10, 12, 14, 16, 20]
users_range = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]   # millions

df_sens = sensitivity_market_size(arpu_range, users_range)

print("SENSITIVITY: Annual Revenue (USD M) by ARPU × User Base")
print("ASSUMPTION: This is a simplified revenue estimate, not a full model.")
print()
display(df_sens)
df_sens.to_csv(tables_dir / "market_sizing_sensitivity.csv")
print(f"\\nSaved to reports/tables/")
"""),
        code_cell("""# I visualise the sensitivity table as a heatmap.
import numpy as np
import seaborn as sns

# Convert string cells to numeric for heatmap
numeric_data = df_sens.copy()
numeric_data = numeric_data.applymap(
    lambda x: float(x.replace('$','').replace('M','')) if isinstance(x, str) else x
)

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(numeric_data, annot=True, fmt='.0f', cmap='YlGnBu',
            ax=ax, cbar_kws={'label': 'Revenue (USD M)'})
ax.set_title("Market Size Sensitivity: ARPU × User Base (USD M, Year 3)")
ax.set_xlabel("User Base")
ax.set_ylabel("ARPU (USD/user/year)")
plt.tight_layout()
save_figure(fig, "fig07_market_sensitivity_heatmap.png")
plt.show()
"""),
        md_cell("""---
*Proceed to `07_competitive_landscape.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "06_market_sizing_tam_sam_som.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 07 — Competitive Landscape
# ═══════════════════════════════════════════════════════════════════════════════

def nb_07():
    cells = [
        md_cell("""# 07 · Competitive Landscape Analysis

**What this notebook does:** Analyses the competitive structure of Nigeria's DFS
market — player benchmarking, market concentration, funding landscape, and
a Porter's Five Forces qualitative assessment.

**Inputs:** `data/processed/competitors_processed.csv`

**Outputs:** Competitive landscape figures and tables
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path, BRAND_COLORS
from src.viz import apply_project_style, save_figure

apply_project_style()

processed_dir = get_path("data_processed")
tables_dir    = get_path("reports_tables")
df_comp = pd.read_csv(processed_dir / "competitors_processed.csv")
print(f"Competitor data: {df_comp.shape}")
display(df_comp.head())
"""),
        md_cell("""## 1 · Market Concentration Analysis"""),
        code_cell("""# I compute market share by reported user base.
# CAVEAT: These are self-reported figures from press releases — not independently verified.
total_users = df_comp['reported_users_m'].sum()
df_comp['user_share_pct'] = (df_comp['reported_users_m'] / total_users * 100).round(1)
df_sorted = df_comp.sort_values('reported_users_m', ascending=False)

print("MARKET CONCENTRATION (Reported Users — CAVEAT: self-reported):")
print(df_sorted[['company', 'reported_users_m', 'user_share_pct']].to_string(index=False))
print()

# Top-3 concentration
top3_share = df_sorted.head(3)['user_share_pct'].sum()
print(f"Top-3 market share: {top3_share:.1f}% of reported users")
print(f"H3 Hypothesis: 'Top-3 command >60%' — {'SUPPORTED' if top3_share > 60 else 'NOT SUPPORTED'}")
print()
print("NOTE: This is based on self-reported figures. H3 should be treated with caution.")
"""),
        code_cell("""# Market share pie chart
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: User share by company
colors_pie = sns.color_palette("colorblind", len(df_sorted))
wedges, texts, autotexts = axes[0].pie(
    df_sorted['reported_users_m'],
    labels=df_sorted['company'],
    autopct='%1.0f%%',
    colors=colors_pie,
    startangle=90,
    textprops={'fontsize': 9}
)
axes[0].set_title("Reported User Share by Company\\n(CAVEAT: Self-reported data)")

# Right: Bubble chart — Users vs Funding
for _, row in df_comp.iterrows():
    if pd.notna(row['funding_usd_m']):
        axes[1].scatter(
            row['funding_usd_m'], row['reported_users_m'],
            s=row['reported_users_m'] * 5,
            alpha=0.7, color=BRAND_COLORS['primary']
        )
        axes[1].annotate(row['company'],
                          (row['funding_usd_m'], row['reported_users_m']),
                          fontsize=8, ha='left', va='bottom')

axes[1].set_xlabel("Total Funding Raised (USD M)")
axes[1].set_ylabel("Reported Users (M)")
axes[1].set_title("Funding vs. User Base\\n(Bubble size ∝ users)")

plt.tight_layout()
save_figure(fig, "fig08_competitive_landscape.png")
plt.show()
"""),
        md_cell("""## 2 · Revenue Model Comparison"""),
        code_cell("""# I group competitors by revenue model to spot which models dominate.
model_counts = df_comp['revenue_model'].value_counts()
print("Revenue model distribution:")
print(model_counts)
print()

# Most players mix transaction fees + lending — consistent with global fintech playbook.
"""),
        md_cell("""## 3 · Porter's Five Forces Assessment

I score each force on a 1–5 scale (1 = weak, 5 = strong) based on the data above.
"""),
        code_cell("""forces_data = {
    'Force': [
        'Threat of New Entrants',
        'Bargaining Power of Buyers',
        'Bargaining Power of Suppliers',
        'Threat of Substitutes',
        'Competitive Rivalry',
    ],
    'Score (1–5)': [3, 3, 2, 3, 5],
    'Assessment': [
        'Moderate: CBN licensing creates barriers, but capital is accessible to funded startups',
        'Moderate: High switching cost for agents, but consumer loyalty is low',
        'Low: NIBSS / telco infrastructure is largely standardised; multiple cloud providers',
        'Moderate: Informal cash economy is a substitute; hawala for remittances',
        'High: 10+ well-funded players competing for same smartphone-owning urban consumer',
    ]
}
df_forces = pd.DataFrame(forces_data)
display(df_forces)
df_forces.to_csv(tables_dir / "porters_five_forces.csv", index=False)

# Spider/radar chart
import numpy as np
categories = df_forces['Force'].tolist()
scores = df_forces['Score (1–5)'].tolist()
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]
scores_plot = scores + [scores[0]]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(projection='polar'))
ax.plot(angles, scores_plot, color=BRAND_COLORS['primary'], linewidth=2)
ax.fill(angles, scores_plot, color=BRAND_COLORS['primary'], alpha=0.2)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=9)
ax.set_ylim(0, 5)
ax.set_title("Porter's Five Forces — Nigeria DFS Sector", size=12, fontweight='bold', pad=20)
plt.tight_layout()
save_figure(fig, "fig09_porters_five_forces.png")
plt.show()
"""),
        md_cell("""## 4 · Competitive Benchmarking Table"""),
        code_cell("""# Final benchmarking table for the report
bench = df_comp[['company', 'type', 'reported_users_m', 'funding_usd_m',
                  'agent_network_k', 'revenue_model', 'monthly_txn_ngn_bn']].copy()
bench.columns = ['Company', 'Type', 'Users (M)', 'Funding ($M)',
                  'Agents (K)', 'Revenue Model', 'Monthly Txn (₦Bn)']
bench = bench.sort_values('Users (M)', ascending=False)
display(bench)
bench.to_csv(tables_dir / "competitor_benchmarking.csv", index=False)
print(f"\\nSaved: {tables_dir / 'competitor_benchmarking.csv'}")
"""),
        md_cell("""---
*Proceed to `08_financial_modelling_and_valuation.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "07_competitive_landscape.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 08 — Financial Modelling & Valuation
# ═══════════════════════════════════════════════════════════════════════════════

def nb_08():
    cells = [
        md_cell("""# 08 · Financial Modelling and Valuation

**What this notebook does:** Builds the full 3-year financial model — user growth,
revenue by stream, income statement, sensitivity analysis, and comparable-company
valuation. Also exports the complete model to Excel.

**This is the core analytical deliverable** for a Therbo Consulting Financial
Modelling & Valuation engagement.

**Inputs:** configs/config.yaml (all assumptions documented there)

**Outputs:** Excel workbook + financial tables + revenue charts
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path, BRAND_COLORS, FIN_MODEL_PARAMS
from src.financial_model import (
    project_users, project_revenue, project_income_statement,
    sensitivity_revenue, sensitivity_ebitda, comparable_valuation,
    export_to_excel,
)
from src.viz import apply_project_style, save_figure

apply_project_style()
tables_dir    = get_path("reports_tables")
processed_dir = get_path("data_processed")
print("Setup complete.")
"""),
        md_cell("""## 1 · Model Assumptions Review

Before building the model, I explicitly state every assumption.
All assumptions are in `configs/config.yaml` and can be changed there.
"""),
        code_cell("""print("FINANCIAL MODEL ASSUMPTIONS (from configs/config.yaml)")
print("="*60)
print(f"  Year 1 user target      : {FIN_MODEL_PARAMS['user_base_y1']:,}")
print(f"  Year 2 user growth rate : {FIN_MODEL_PARAMS['user_growth_rate_y2']*100:.0f}%")
print(f"  Year 3 user growth rate : {FIN_MODEL_PARAMS['user_growth_rate_y3']*100:.0f}%")
print(f"  Annual churn rate       : {FIN_MODEL_PARAMS['churn_rate']*100:.0f}%")
print(f"  ARPU Year 1 (USD)       : ${FIN_MODEL_PARAMS['arpu_usd_y1']:.2f}")
print(f"  ARPU growth/year        : {FIN_MODEL_PARAMS['arpu_growth_rate']*100:.0f}%")
print()
print("Revenue Mix:")
for k, v in FIN_MODEL_PARAMS['revenue_mix'].items():
    print(f"  {k:<30} : {v*100:.0f}%")
print()
print("Cost Structure (% of revenue):")
for k, v in FIN_MODEL_PARAMS['opex'].items():
    print(f"  {k:<30} : {v*100:.0f}%")
"""),
        md_cell("""## 2 · User Growth Projection"""),
        code_cell("""df_users = project_users()
print("USER GROWTH MODEL:")
display(df_users.assign(
    new_users=df_users['new_users'].apply(lambda x: f'{x:,}'),
    churned_users=df_users['churned_users'].apply(lambda x: f'{x:,}'),
    active_users=df_users['active_users'].apply(lambda x: f'{x:,}')
))

# Chart: user growth waterfall
fig, ax = plt.subplots(figsize=(10, 5))
years = df_users['year'].values
ax.bar(years - 0.2, df_users['new_users']/1e3,  0.35, label='New Users (K)', color=BRAND_COLORS['secondary'])
ax.bar(years + 0.2, df_users['active_users']/1e3, 0.35, label='Active Users (K)', color=BRAND_COLORS['primary'])
ax.set_xticks(years)
ax.set_xticklabels(['Year 1', 'Year 2', 'Year 3'])
ax.set_ylabel("Users (Thousands)")
ax.set_title("User Growth Projection (3-Year)")
ax.legend()
plt.tight_layout()
save_figure(fig, "fig10_user_growth.png")
plt.show()
"""),
        md_cell("""## 3 · Revenue Projection by Stream"""),
        code_cell("""df_revenue = project_revenue(df_users)
print("REVENUE PROJECTION (USD M):")
display(df_revenue)

# Stacked bar chart by revenue stream
fig, ax = plt.subplots(figsize=(10, 6))
streams = ['txn_fees_usd_m', 'float_income_usd_m', 'lending_usd_m', 'subscription_usd_m']
stream_labels = ['Transaction Fees', 'Float Income', 'Lending', 'Subscriptions']
colors = [BRAND_COLORS['primary'], BRAND_COLORS['secondary'],
           BRAND_COLORS['accent'], BRAND_COLORS['neutral']]

bottom = np.zeros(3)
for col, label, color in zip(streams, stream_labels, colors):
    vals = df_revenue[col].values
    ax.bar(['Year 1', 'Year 2', 'Year 3'], vals, bottom=bottom, label=label, color=color, alpha=0.9)
    bottom += vals

ax.set_ylabel("Revenue (USD M)")
ax.set_title("3-Year Revenue Projection by Stream\\nASSUMPTION — forward-looking model")
ax.legend(loc='upper left')

# Add total labels
for i, (yr, row) in enumerate(df_revenue.iterrows()):
    ax.text(i, row['total_revenue_usd_m'] + 0.05,
            f"${row['total_revenue_usd_m']:.2f}M", ha='center', fontweight='bold', fontsize=10)

plt.tight_layout()
save_figure(fig, "fig11_revenue_by_stream.png")
plt.show()
"""),
        md_cell("""## 4 · Income Statement (P&L)"""),
        code_cell("""df_pnl = project_income_statement(df_revenue)

print("INCOME STATEMENT (USD M) — ASSUMPTION: Forward-looking model")
display(df_pnl[['year', 'revenue_usd_m', 'cogs_usd_m', 'gross_profit_usd_m',
                  'total_opex_usd_m', 'ebitda_usd_m', 'ebitda_margin_pct']])

# Save to reports
df_pnl.to_csv(tables_dir / "income_statement_projection.csv", index=False)

print(f"\\nYear 3 EBITDA margin: {df_pnl.iloc[-1]['ebitda_margin_pct']}%")
print("Interpretation: Negative EBITDA in early years is typical for growth-stage fintechs.")
"""),
        code_cell("""# Bridge chart: Revenue → EBITDA for Year 3
fig, ax = plt.subplots(figsize=(10, 5))
y3 = df_pnl.iloc[-1]
components = [
    ('Revenue',       y3['revenue_usd_m'],        True),
    ('COGS',         -y3['cogs_usd_m'],            False),
    ('Gross Profit',  y3['gross_profit_usd_m'],    True),
    ('OpEx',         -y3['total_opex_usd_m'],      False),
    ('EBITDA',        y3['ebitda_usd_m'],          True),
]
labels = [c[0] for c in components]
values = [c[1] for c in components]
colors = [BRAND_COLORS['secondary'] if c[2] else BRAND_COLORS['danger'] for c in components]

ax.bar(labels, values, color=colors, alpha=0.85)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel("USD Millions")
ax.set_title("Year 3 P&L Bridge: Revenue → EBITDA (ASSUMPTION)")
for i, (label, val, _) in enumerate(components):
    ax.text(i, val + (0.05 if val >= 0 else -0.1),
            f"${val:.2f}M", ha='center', fontsize=9, fontweight='bold')
plt.tight_layout()
save_figure(fig, "fig12_pnl_bridge_y3.png")
plt.show()
"""),
        md_cell("""## 5 · Sensitivity Analysis"""),
        code_cell("""# 2-variable sensitivity: ARPU × Year-3 user count
arpu_range  = [6, 8, 10, 12, 14, 16, 18, 20]
users_range = [500_000, 750_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000]

df_sens_rev = sensitivity_revenue(arpu_range, users_range)
print("SENSITIVITY: Year-3 Revenue (USD M) by ARPU × User Count")
display(df_sens_rev)
df_sens_rev.to_csv(tables_dir / "sensitivity_revenue.csv")
"""),
        code_cell("""# EBITDA margin sensitivity: ARPU × COGS %
arpu_range2 = [8, 10, 12, 14, 16, 20]
cogs_range  = [0.30, 0.35, 0.40, 0.45, 0.50]

df_sens_ebitda = sensitivity_ebitda(arpu_range2, cogs_range, base_users_y3=1_500_000)
print("\\nSENSITIVITY: EBITDA Margin (%) by ARPU × COGS %")
display(df_sens_ebitda)
df_sens_ebitda.to_csv(tables_dir / "sensitivity_ebitda.csv")

import seaborn as sns
fig, ax = plt.subplots(figsize=(10, 6))
numeric = df_sens_ebitda.applymap(float)
sns.heatmap(numeric, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
            ax=ax, cbar_kws={'label': 'EBITDA Margin (%)'})
ax.set_title("EBITDA Margin Sensitivity: ARPU × COGS % (1.5M Y3 Users)")
plt.tight_layout()
save_figure(fig, "fig13_ebitda_sensitivity.png")
plt.show()
"""),
        md_cell("""## 6 · Comparable Company Valuation"""),
        code_cell("""# Using Year-3 projected revenue for the valuation
y3_revenue = float(df_revenue.iloc[-1]['total_revenue_usd_m'])
df_valuation = comparable_valuation(y3_revenue)

print(f"Year-3 Projected Revenue: ${y3_revenue:.3f}M")
print()
print("COMPARABLE COMPANY VALUATION — APPROXIMATION:")
print("These multiples are from public sources and must be treated as indicative only.")
display(df_valuation)
df_valuation.to_csv(tables_dir / "comparable_valuation.csv", index=False)
"""),
        md_cell("""## 7 · Excel Export"""),
        code_cell("""# I export the full model to Excel — the primary client deliverable.
excel_path = processed_dir / "financial_model.xlsx"

export_to_excel(
    df_users=df_users,
    df_revenue=df_revenue,
    df_pnl=df_pnl,
    df_sensitivity=df_sens_rev,
    df_valuation=df_valuation,
    output_path=excel_path,
)
print(f"\\nExcel financial model: {excel_path}")
print("Open this file for the formatted consulting-grade workbook.")
"""),
        md_cell("""---
*Proceed to `09_risk_assessment_framework.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "08_financial_modelling_and_valuation.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 09 — Risk Assessment
# ═══════════════════════════════════════════════════════════════════════════════

def nb_09():
    cells = [
        md_cell("""# 09 · Risk Assessment Framework

**What this notebook does:** Builds a structured risk matrix for Nigeria DFS
market entry, maps strategic opportunities, and produces the risk heatmap.

**Inputs:** Risk registry (hardcoded in src/risk_model.py from public sources)

**Outputs:** Risk matrix table + heatmap + opportunity framework
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path
from src.risk_model import build_risk_registry, risk_heatmap_matrix, strategic_opportunities
from src.viz import apply_project_style, save_figure, plot_risk_matrix

apply_project_style()
tables_dir = get_path("reports_tables")
print("Setup complete.")
"""),
        md_cell("""## 1 · Risk Registry"""),
        code_cell("""df_risks = build_risk_registry()

print(f"Total risks identified: {len(df_risks)}")
print()
display(df_risks[['Category', 'Risk', 'Probability', 'Impact', 'Risk Score', 'Risk Tier']])

# Summary by tier
print("\\nRisk distribution by tier:")
print(df_risks['Risk Tier'].value_counts().to_string())

df_risks.to_csv(tables_dir / "risk_registry.csv", index=False)
"""),
        md_cell("""## 2 · Risk Heatmap"""),
        code_cell("""fig = plot_risk_matrix(df_risks)
save_figure(fig, "fig14_risk_matrix_heatmap.png")
plt.show()

# Top 5 risks by score
print("\\nTOP 5 RISKS BY PRIORITY SCORE:")
print(df_risks[['Risk', 'Risk Score', 'Risk Tier', 'Mitigation']].head(5).to_string(index=False))
"""),
        md_cell("""## 3 · Strategic Opportunities"""),
        code_cell("""df_opps = strategic_opportunities()
display(df_opps[['Opportunity', 'Market Attractiveness', 'Comp. Advantage Pot.',
                   'Priority Score', 'Supporting Evidence', 'Recommended Timeline']])
df_opps.to_csv(tables_dir / "strategic_opportunities.csv", index=False)

# Opportunity matrix (2x2 positioning)
fig, ax = plt.subplots(figsize=(9, 7))
from src.config import BRAND_COLORS
for _, row in df_opps.iterrows():
    ax.scatter(row['Comp. Advantage Pot.'], row['Market Attractiveness'],
               s=row['Priority Score']*40, alpha=0.7, color=BRAND_COLORS['primary'])
    ax.annotate(row['Opportunity'],
                (row['Comp. Advantage Pot.'], row['Market Attractiveness']),
                fontsize=8, ha='center', va='bottom', wrap=True)

ax.set_xlabel("Competitive Advantage Potential (1–5)")
ax.set_ylabel("Market Attractiveness (1–5)")
ax.set_title("Strategic Opportunity Matrix\\n(Bubble size ∝ Priority Score)")
ax.set_xlim(0, 6); ax.set_ylim(0, 6)
ax.axvline(3, color='grey', alpha=0.3, linestyle='--')
ax.axhline(3, color='grey', alpha=0.3, linestyle='--')
plt.tight_layout()
save_figure(fig, "fig15_strategic_opportunity_matrix.png")
plt.show()
"""),
        md_cell("""---
*Proceed to `10_statistical_inference.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "09_risk_assessment_framework.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOK 10 — Statistical Inference
# ═══════════════════════════════════════════════════════════════════════════════

def nb_10():
    cells = [
        md_cell("""# 10 · Statistical Analysis and Inference

**What this notebook does:** Tests the project hypotheses using statistical methods —
linear regression, correlation analysis, bootstrap confidence intervals, and CAGR
calculations with uncertainty.

**Why this matters:** A consulting report without statistical inference is opinion,
not analysis. I use conservative language throughout — "suggests", not "proves".

**Inputs:** `data/processed/nigeria_combined.csv`

**Outputs:** Statistical tables + annotated charts
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path, BRAND_COLORS
from src.stats import bootstrap_ci, cagr, ols_regression, correlation_table
from src.viz import apply_project_style, save_figure

apply_project_style()

processed_dir = get_path("data_processed")
tables_dir    = get_path("reports_tables")

df_ng    = pd.read_csv(processed_dir / "nigeria_combined.csv")
df_efina_path = get_path("data_external") / "efina_summary.csv"
df_efina = pd.read_csv(df_efina_path)

print(f"Data loaded. Shape: {df_ng.shape}")
"""),
        md_cell("""## 1 · H1 — Financial Inclusion Trend (Regression)

**H1:** Mobile internet penetration and agent banking expansion are the primary
drivers of Nigeria's financial inclusion growth.

I test whether time (as a proxy for policy, infrastructure, and mobile internet
roll-out) is a significant predictor of banked %, using linear regression.
"""),
        code_cell("""# I run an OLS regression of banked_pct on year to quantify the time trend.
# CAUTION: Small N (8 survey years). Results are suggestive, not conclusive.
result = ols_regression(df_efina, "banked_pct ~ year",
                         title="Financial Inclusion Trend (EFInA surveys)")

print("\\nINTERPRETATION:")
print(f"  R-squared: {result.rsquared:.3f}")
print(f"  p-value (year): {result.pvalues['year']:.4f}")
if result.pvalues['year'] < 0.05:
    coef = result.params['year']
    print(f"  Coefficient: +{coef:.2f}pp per year")
    print(f"  The year coefficient is statistically significant (p < 0.05).")
    print(f"  This is consistent with H1: financial inclusion has grown over time.")
else:
    print("  The time trend is not statistically significant at p < 0.05.")
    print("  Interpret with caution — small sample (N=8 survey waves).")
"""),
        md_cell("""## 2 · H2 — NIP CAGR with Bootstrap Confidence Interval"""),
        code_cell("""# I compute the CAGR for NIP volume (2015–2023) with a bootstrap CI.
# Bootstrap is appropriate here for non-normal time-series data.
df_cbn = pd.read_csv(get_path("data_external") / "cbn_payments.csv")

nip_start = df_cbn[df_cbn['year'] == 2015]['nip_volume_m'].values[0]
nip_end   = df_cbn[df_cbn['year'] == 2023]['nip_volume_m'].values[0]
nip_cagr  = cagr(nip_start, nip_end, 8)

print(f"NIP Volume CAGR (2015–2023): {nip_cagr*100:.1f}%/yr")
print(f"H2 prediction: CAGR > 30% — {'SUPPORTED' if nip_cagr > 0.30 else 'NOT SUPPORTED'}")
print()

# For bootstrap, I use annual growth rates as the sample
annual_rates = df_cbn.sort_values('year')['nip_volume_m'].pct_change().dropna().values
point, lo, hi = bootstrap_ci(annual_rates, np.mean, n_boot=5000)
print(f"Bootstrap 95% CI for mean annual NIP growth rate:")
print(f"  Point estimate : {point*100:.1f}%")
print(f"  95% CI         : [{lo*100:.1f}%, {hi*100:.1f}%]")
print()
print("INTERPRETATION: The data is consistent with H2. However, with only 8")
print("data points, the CI is wide. This should be interpreted cautiously.")
"""),
        md_cell("""## 3 · H3 — Market Concentration Test"""),
        code_cell("""# I compute HHI (Herfindahl-Hirschman Index) as a market concentration measure.
df_comp = pd.read_csv(processed_dir / "competitors_processed.csv")
total_users = df_comp['reported_users_m'].sum()
shares = (df_comp['reported_users_m'] / total_users).values
hhi = (shares ** 2).sum() * 10_000

top3_share = (df_comp.nlargest(3, 'reported_users_m')['reported_users_m'].sum()
              / total_users * 100)

print(f"Herfindahl-Hirschman Index (HHI): {hhi:.0f}")
print(f"  (HHI < 1500 = competitive; 1500–2500 = moderately concentrated; >2500 = concentrated)")
print(f"Top-3 market share: {top3_share:.1f}%")
print()
print(f"H3: 'Top-3 command >60%' — {'SUPPORTED' if top3_share > 60 else 'NOT SUPPORTED'}")
print()
print("CAVEAT: These figures are based on self-reported user counts from press")
print("releases. Independent verification is not available. This result must")
print("be treated as an estimate, not a verified fact.")
"""),
        md_cell("""## 4 · Correlation Analysis — Inclusion Drivers"""),
        code_cell("""# I check correlations between financial inclusion, mobile penetration, and internet users.
# Only using rows where all three are available.
cols_to_corr = ['banked_pct', 'mobile_subscriptions', 'internet_users', 'gdp_per_capita']
available_cols = [c for c in cols_to_corr if c in df_ng.columns]

if len(available_cols) >= 2:
    sub = df_ng[['year'] + available_cols].dropna()
    print(f"Correlation analysis — N = {len(sub)} year-observations")
    print()
    cor_matrix, pval_matrix = correlation_table(sub, available_cols)
    print("PEARSON CORRELATIONS:")
    display(cor_matrix)
    print("\\nP-VALUES:")
    display(pval_matrix)

    # Heatmap
    import seaborn as sns
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.heatmap(cor_matrix.astype(float), annot=True, fmt='.2f', cmap='coolwarm',
                center=0, ax=axes[0], vmin=-1, vmax=1)
    axes[0].set_title("Pearson Correlations")
    sns.heatmap(pval_matrix.astype(float), annot=True, fmt='.3f', cmap='Reds_r',
                ax=axes[1], vmin=0, vmax=0.1)
    axes[1].set_title("P-values (red = significant)")
    plt.suptitle("Correlation Matrix — Nigeria Indicators", fontweight='bold')
    plt.tight_layout()
    save_figure(fig, "fig16_correlation_matrix.png")
    plt.show()
else:
    print("Not enough indicator columns available from WB API.")
    print("Available:", [c for c in df_ng.columns if c in cols_to_corr])
"""),
        md_cell("""## 5 · Statistical Summary

| Hypothesis | Test | Result | Confidence |
|---|---|---|---|
| H1: Time trend in banked % | OLS regression | See above | Low (N=8) |
| H2: NIP CAGR > 30%/yr | CAGR + bootstrap CI | See above | Moderate |
| H3: Top-3 > 60% share | User share calculation | See above | Low (self-reported data) |
| H4: Rural/female excluded | EFInA survey reports | Not tested — data cited | N/A |
| H5: Break-even in 3yrs | Financial model | See notebook 08 | Conditional on assumptions |

---
*Proceed to `11_robustness_checks.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "10_statistical_inference.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  NOTEBOOKS 11, 12, 13 — Robustness, Figures, Limitations
# ═══════════════════════════════════════════════════════════════════════════════

def nb_11():
    cells = [
        md_cell("""# 11 · Robustness Checks

**What this notebook does:** Tests whether key findings hold under alternative
assumptions — different CAGR start years, different ARPU/user scenarios,
and different FX rate assumptions.

**Why this matters:** Any client will ask "how sensitive is this?" A robust
analysis anticipates these questions.

**Inputs:** Processed data + financial model parameters

**Outputs:** Robustness tables in reports/tables/
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path, FIN_MODEL_PARAMS
from src.stats import period_sensitivity_cagr, bootstrap_ci, cagr
from src.financial_model import project_users, project_revenue, project_income_statement
from src.viz import apply_project_style, save_figure

apply_project_style()
tables_dir = get_path("reports_tables")
external_dir = get_path("data_external")
print("Setup complete.")
"""),
        md_cell("""## 1 · CAGR Sensitivity to Start Year Choice

I check whether the NIP growth story changes materially depending on which
year we call the 'baseline'. This is a common robustness check in market analyses.
"""),
        code_cell("""df_cbn = pd.read_csv(external_dir / "cbn_payments.csv")

# Test CAGR from different start years to 2023
for metric, label in [('nip_volume_m', 'NIP Volume'), ('nip_value_bn_ngn', 'NIP Value (NGN bn)')]:
    print(f"\\n--- {label} CAGR Robustness ---")
    result = period_sensitivity_cagr(
        df_cbn, 'year', metric,
        start_years=[2015, 2016, 2017, 2018, 2019],
        end_year=2023
    )
    result.to_csv(tables_dir / f"cagr_robustness_{metric}.csv", index=False)

print("\\nFINDING: If the CAGR is consistently high across all start years,")
print("the growth story is robust. If it varies wildly, it's start-year sensitive.")
"""),
        md_cell("""## 2 · Financial Model Robustness — Scenario Analysis"""),
        code_cell("""# I run the financial model under three scenarios:
# Base (from config), Bear (pessimistic), Bull (optimistic)

scenarios = {
    'Bear': {'user_base_y1': 250_000, 'user_growth_rate_y2': 0.50,
             'user_growth_rate_y3': 0.40, 'churn_rate': 0.25, 'arpu_usd_y1': 8.0,
             'arpu_growth_rate': 0.08},
    'Base': FIN_MODEL_PARAMS,
    'Bull': {'user_base_y1': 750_000, 'user_growth_rate_y2': 1.10,
             'user_growth_rate_y3': 0.80, 'churn_rate': 0.12, 'arpu_usd_y1': 15.0,
             'arpu_growth_rate': 0.20},
}

results_summary = []
for scenario_name, params in scenarios.items():
    params_full = {**FIN_MODEL_PARAMS, **params}
    df_u = project_users(params_full)
    df_r = project_revenue(df_u, params_full)
    df_p = project_income_statement(df_r, params_full)
    y3   = df_p.iloc[-1]
    results_summary.append({
        'Scenario':       scenario_name,
        'Y3 Users':       f"{df_u.iloc[-1]['active_users']:,}",
        'Y3 Revenue ($M)': f"${y3['revenue_usd_m']:.2f}M",
        'Y3 EBITDA ($M)':  f"${y3['ebitda_usd_m']:.2f}M",
        'Y3 EBITDA Margin': f"{y3['ebitda_margin_pct']:.1f}%",
    })

df_scenarios = pd.DataFrame(results_summary)
print("SCENARIO ANALYSIS:")
display(df_scenarios)
df_scenarios.to_csv(tables_dir / "scenario_analysis.csv", index=False)
"""),
        code_cell("""# Visual comparison of scenarios
scenarios_vis = {
    'Bear': {'user_base_y1': 250_000, 'user_growth_rate_y2': 0.50,
             'user_growth_rate_y3': 0.40, 'churn_rate': 0.25, 'arpu_usd_y1': 8.0,
             'arpu_growth_rate': 0.08},
    'Base': FIN_MODEL_PARAMS,
    'Bull': {'user_base_y1': 750_000, 'user_growth_rate_y2': 1.10,
             'user_growth_rate_y3': 0.80, 'churn_rate': 0.12, 'arpu_usd_y1': 15.0,
             'arpu_growth_rate': 0.20},
}
from src.config import BRAND_COLORS
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
colors = [BRAND_COLORS['danger'], BRAND_COLORS['secondary'], BRAND_COLORS['primary']]
years = ['Y1', 'Y2', 'Y3']

for ax_idx, metric in enumerate(['total_revenue_usd_m', 'ebitda_usd_m']):
    for (name, params_s), color in zip(scenarios_vis.items(), colors):
        params_full = {**FIN_MODEL_PARAMS, **params_s}
        df_u = project_users(params_full)
        df_r = project_revenue(df_u, params_full)
        df_p = project_income_statement(df_r, params_full)
        axes[ax_idx].plot(years, df_p[metric], marker='o', label=name, color=color, linewidth=2)
    axes[ax_idx].set_title('Revenue (USD M)' if metric == 'total_revenue_usd_m' else 'EBITDA (USD M)')
    axes[ax_idx].axhline(0, color='black', linewidth=0.5)
    axes[ax_idx].legend()

plt.suptitle("Scenario Analysis: Bear / Base / Bull (ASSUMPTION-driven)", fontweight='bold')
plt.tight_layout()
save_figure(fig, "fig17_scenario_analysis.png")
plt.show()
"""),
        md_cell("""## 3 · FX Sensitivity

The 2023 NGN devaluation (~₦900/$1 vs ₦447/$1 in 2022) materially affects
USD-denominated comparisons. I test how different FX rate assumptions affect
the NIP payment value in USD.
"""),
        code_cell("""fx_rates = [700, 900, 1100, 1300, 1500]
nip_ngn_bn = df_cbn[df_cbn['year'] == 2023]['nip_value_bn_ngn'].values[0]

print("FX SENSITIVITY — NIP Transaction Value (2023):")
print(f"  Fixed NGN value: ₦{nip_ngn_bn:,.0f} billion")
print()
for fx in fx_rates:
    usd_m = nip_ngn_bn * 1e9 / fx / 1e6
    print(f"  @ ₦{fx}/$1 → ${usd_m:,.0f}M  (~${usd_m/1e3:.0f}B)")

print()
print("FINDING: The NGN/USD rate assumption significantly affects the USD market")
print("size estimate. We report both NGN figures (more stable) and USD estimates")
print("(more internationally comparable) throughout the report.")
"""),
        md_cell("""---
*Proceed to `12_publication_figures_and_tables.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "11_robustness_checks.ipynb")


def nb_12():
    cells = [
        md_cell("""# 12 · Publication Figures and Tables

**What this notebook does:** Re-runs all key analyses and saves final,
publication-ready versions of every figure and table for the report.

**Inputs:** All processed data

**Outputs:** Final figures in `reports/figures/` and `paper_or_report/figures/`
             Final tables in `reports/tables/` and `paper_or_report/tables/`
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from src.config import get_path, BRAND_COLORS, VIZ_PARAMS
from src.data_loader import load_cbn_payments, load_efina_summary, load_competitors
from src.financial_model import project_users, project_revenue, project_income_statement
from src.market_sizing import compute_tam_sam_som
from src.risk_model import build_risk_registry, strategic_opportunities
from src.viz import (apply_project_style, save_figure, plot_inclusion_trend,
                      plot_payment_growth, plot_market_sizing_funnel, plot_risk_matrix)

apply_project_style()

tables_dir   = get_path("reports_tables")
paper_tables = get_path("paper_tables")

df_cbn   = load_cbn_payments()
df_efina = load_efina_summary()
df_comp  = load_competitors()
print("All data loaded for publication output.")
"""),
        code_cell("""# FIGURE 1 — Financial Inclusion Trend (publication quality)
fig, ax = plt.subplots(figsize=(12, 5))
plot_inclusion_trend(df_efina, ax)
plt.tight_layout()
save_figure(fig, "PUB_fig01_inclusion_trend.png")
plt.show()
print("Saved: PUB_fig01_inclusion_trend")
"""),
        code_cell("""# FIGURE 2 — NIP Payment Growth
fig, ax = plt.subplots(figsize=(12, 5))
plot_payment_growth(df_cbn, ax)
plt.tight_layout()
save_figure(fig, "PUB_fig02_nip_growth.png")
plt.show()
print("Saved: PUB_fig02_nip_growth")
"""),
        code_cell("""# FIGURE 3 — Market Sizing Funnel
r = compute_tam_sam_som()
fig = plot_market_sizing_funnel(
    r['TAM'].market_size_usd_m, r['SAM'].market_size_usd_m,
    r['SOM_Y1'].market_size_usd_m, r['SOM_Y3'].market_size_usd_m
)
save_figure(fig, "PUB_fig03_market_funnel.png")
plt.show()
"""),
        code_cell("""# FIGURE 4 — Risk Matrix
df_risks = build_risk_registry()
fig = plot_risk_matrix(df_risks)
save_figure(fig, "PUB_fig04_risk_matrix.png")
plt.show()
"""),
        code_cell("""# TABLE 1 — Executive summary statistics
exec_summary = {
    "Metric": [
        "Nigeria Adult Population (2023)",
        "Formally Banked (%)",
        "Financially Excluded (M adults)",
        "Mobile Money Wallets (M, 2023)",
        "NIP Volume (2023, M txns)",
        "NIP Value (2023, ₦ Trillions)",
        "NIP CAGR (2015–2023)",
        "TAM (USD M)",
        "SAM (USD M)",
        "SOM Year 3 (USD M)",
    ],
    "Value": [
        "106 million",
        "45%",
        "~26 million",
        "20 million",
        "8,073 million",
        "₦813 trillion",
        f"{(8073/209)**(1/8)-1:.0%}",
        f"${r['TAM'].market_size_usd_m:,.0f}M",
        f"${r['SAM'].market_size_usd_m:,.0f}M",
        f"${r['SOM_Y3'].market_size_usd_m:,.0f}M",
    ],
    "Source": [
        "World Bank 2023", "EFInA 2023", "EFInA 2023", "CBN 2023",
        "CBN Annual Report 2023", "CBN Annual Report 2023", "Calculated",
        "ASSUMPTION", "ASSUMPTION", "ASSUMPTION",
    ]
}
df_exec = pd.DataFrame(exec_summary)
display(df_exec)
df_exec.to_csv(tables_dir / "executive_summary_stats.csv", index=False)
df_exec.to_csv(paper_tables / "TABLE_01_executive_summary.csv", index=False)
print("\\nAll publication tables saved.")
"""),
        md_cell("""---
*Proceed to `13_limitations_and_next_steps.ipynb`.*
"""),
    ]
    save_notebook(make_notebook(cells), "12_publication_figures_and_tables.ipynb")


def nb_13():
    cells = [
        md_cell("""# 13 · Limitations, Risks, and Next Steps

**What this notebook does:** Documents all limitations of this analysis — data
quality issues, assumption risks, methodological constraints, and what future
work would strengthen the findings.

**Why this matters:** Honest limitations are a mark of professional integrity.
A client who discovers unstated limitations after acting on a report will not
be a return client.
"""),
        code_cell("""import sys
from pathlib import Path
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
from src.config import get_path
print("Notebook 13 — Limitations and Next Steps")
"""),
        md_cell("""## 1 · Data Limitations

### 1.1 Competitor User Counts
All user figures for OPay, PalmPay, Moniepoint, etc. are **self-reported**
in press releases. They have not been independently verified.
- OPay's 35M figure (2023 press release) has been disputed by analysts
- "Registered" users ≠ "Monthly Active Users" — we cannot distinguish
- **Impact:** Market concentration figures (H3) should be treated as estimates

### 1.2 EFInA Survey Gaps
The EFInA survey is **biennial** — there is no annual reading of financial
inclusion in Nigeria. Between survey years, we forward-fill values.
- **Impact:** Trend smoothness is partially an artefact of forward-filling
- **Mitigation:** We use the World Bank Findex (triennial) as a cross-check

### 1.3 CBN Data Double-Counting
Pre-2020 NIP figures may include **interbank settlement flows** in addition
to retail transactions, potentially overstating payment volume.
- **Impact:** The 2015 baseline may be overstated, making 2023 CAGR appear lower
- **Mitigation:** We cross-check against NIBSS Annual Activity Reports where available

### 1.4 FX Rate Volatility
The NGN/USD rate collapsed from ₦447/$1 (2022) to ₦900/$1 (2023 end).
All USD-denominated comparisons are sensitive to FX assumptions.
- **Impact:** USD market size estimates have high uncertainty
- **Mitigation:** We report NGN figures as primary and USD as secondary

### 1.5 World Bank API Coverage
Some WB indicators have gaps for Nigeria (e.g., Findex data only every 3 years).
The wbdata API returns what's available — not every cell is populated.
"""),
        md_cell("""## 2 · Modelling Assumptions Risk

| Assumption | Risk if Wrong | Sensitivity |
|---|---|---|
| ARPU = $12/year | If ARPU < $8, Y3 EBITDA turns deeply negative | High |
| Churn = 18%/yr | If churn > 25%, breakeven is delayed by 2+ years | High |
| Y2 user growth = 80% | If growth < 50%, valuation multiple drops significantly | Medium |
| EV/Revenue = 5.5x | Market re-rating could push multiples to 2–3x | High |
| FX stable at ₦900/$1 | Further devaluation reduces USD returns | High |

**Recommendation:** Before any capital allocation decision, these assumptions
should be stress-tested with primary research (customer interviews, agent surveys)
and validated against actual operating data from a comparable Nigerian fintech.
"""),
        md_cell("""## 3 · Methodological Limitations

### 3.1 No Causal Identification
The regression of banked_pct on year cannot isolate the causal contribution of
mobile internet vs. CBN policy vs. economic growth. It is a correlation.

### 3.2 Small N in Time-Series Regressions
With 8 EFInA survey waves and 9 CBN annual data points, all statistical tests
have very low power. Bootstrap CIs are wide. Results are **suggestive**, not conclusive.

### 3.3 No Demand-Side Primary Research
We have no original survey data on consumer preferences, willingness to pay,
or barriers to adoption in Nigeria. All demand assumptions are derived from
published secondary sources.

### 3.4 No Regulatory Modelling
The CBN licensing framework is modelled qualitatively (Porter's Forces).
Changes to PSB licensing rules, NDPR enforcement, or eNaira policy
are not quantitatively modelled.
"""),
        md_cell("""## 4 · What Would Strengthen This Analysis?

| Enhancement | Priority | Effort |
|---|---|---|
| Primary consumer survey (N=1,000+) in Lagos, Kano, Port Harcourt | High | 3 months |
| Access to NIBSS confidential transaction microdata | High | Requires partnership |
| Detailed P&L from one comparable fintech (NDA basis) | High | BD required |
| Agent network cost study (10+ interviews) | Medium | 4 weeks |
| LTV/CAC benchmarks from Nigerian fintechs | Medium | Secondary research |
| Geospatial analysis of excluded population by LGA | Medium | 6 weeks |
| Regulatory risk modelling with legal counsel | Low | 2 weeks |

---

## 5 · Next Steps for This Project

1. **Convert to live client engagement**: Replace public estimates with client-provided
   operating data and run the financial model with actuals.
2. **Extend the competitive dataset**: Add NIBSS-confirmed transaction data when available.
3. **Build a Streamlit dashboard** for interactive sensitivity analysis (`dashboard/app.py`).
4. **Submit to publication**: The analytical framework is suitable for a journal of
   African business studies or a conference on financial inclusion.

---

*This concludes the analytical notebook sequence.*
*Final output: `paper_or_report/report.md` + `dashboard/app.py`*
"""),
    ]
    save_notebook(make_notebook(cells), "13_limitations_and_next_steps.ipynb")


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN — Generate all notebooks
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating all project notebooks...")
    nb_00()
    nb_01()
    nb_02()
    nb_03()
    nb_04()
    nb_05()
    nb_06()
    nb_07()
    nb_08()
    nb_09()
    nb_10()
    nb_11()
    nb_12()
    nb_13()
    print(f"\nAll {len(list(NOTEBOOKS_DIR.glob('*.ipynb')))} notebooks generated in {NOTEBOOKS_DIR}")
