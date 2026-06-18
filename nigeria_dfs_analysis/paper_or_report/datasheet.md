# Datasheet for Datasets
## Nigeria DFS Market Analysis

This document follows the Datasheets for Datasets framework.

---

## Dataset 1: World Bank Development Indicators

Motivation: cross-country financial inclusion, demographic, and macroeconomic context.

Composition:
- Format: CSV
- Coverage: about 200 countries, 1960-present
- Used indicators: a small Nigeria and comparator-country subset
- File: `data/raw/wb_indicators_raw.csv`

Collection process:
- Downloaded programmatically via `scripts/download_data.py`
- Retrieved through the World Bank API

Preprocessing:
- Filtered to Nigeria and selected comparator countries
- Pivoted from long to wide format where needed
- Missing Findex years are left as missing

Uses:
- Financial inclusion benchmarking
- Macro context
- Cross-country comparison

Licence: CC BY 4.0

---

## Dataset 2: CBN Payment System Data

Motivation: Nigeria-specific payment statistics are not available in WDI.

Composition:
- Format: CSV
- Coverage: Nigeria, 2015-2023
- Variables: NIP volume and value, POS volume and value, mobile banking, mobile money wallets
- File: `data/external/cbn_payments.csv`

Collection process:
- Values transcribed from CBN annual report tables
- Cross-checked against secondary sources where possible

Known issues:
- Pre-2020 NIP figures may include settlement flows
- Post-2022 figures are affected by NGN devaluation

Licence: Public government publication

---

## Dataset 3: EFInA Access to Finance Survey Summary

Motivation: the most granular Nigeria-specific financial inclusion data available.

Composition:
- Format: CSV
- Coverage: survey years 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2023
- Variables: banked_pct, excluded_pct, mobile_money_pct, adult_pop_m, derived columns
- File: `data/external/efina_summary.csv`

Known issues:
- Biennial data means values between survey years are not directly observed
- 2020 was conducted remotely and may under-represent some populations
- Survey methodology changed between some rounds

Licence: Public download from EFInA

---

## Dataset 4: Competitor Benchmarking Data

Motivation: assemble the best publicly available information on Nigerian DFS players.

Composition:
- Format: CSV
- Coverage: 10 major Nigerian DFS players
- Variables: company, founded, type, reported_users_m, funding_usd_m, revenue_model,
  headquarters, agent_network_k, monthly_txn_ngn_bn
- File: `data/external/competitors.csv`

Known issues:
- User figures are self-reported or estimated from public sources
- Registered users are not the same as active users
- Figures should be treated as order-of-magnitude estimates

---

## Ethical Review

- No individual-level data is used.
- All datasets are country-level or company-level aggregates.
- Potential misuse is limited by the fact that the project clearly labels assumptions.
- The limitations document is included in the project and referenced from the report.
