# Supplementary Material

## Nigeria DFS Market Analysis - Additional Data and Methodology Notes

---

## S1. World Bank Indicator Code Reference

| Friendly Name | WB Indicator Code | Description |
|--------------|------------------|-------------|
| account_ownership | FX.OWN.TOTL.ZS | Account at financial institution or mobile money (% 15+) |
| account_female | FX.OWN.TOTL.FE.ZS | Female account ownership (% female 15+) |
| account_male | FX.OWN.TOTL.MA.ZS | Male account ownership (% male 15+) |
| account_rural | FX.OWN.TOTL.RUR.ZS | Rural account ownership (%) |
| mobile_money | FX.OWN.TOTL.OT.ZS | Mobile money account (% 15+) |
| population_total | SP.POP.TOTL | Total population |
| mobile_subscriptions | IT.CEL.SETS.P2 | Mobile cellular subscriptions per 100 people |
| internet_users | IT.NET.USER.ZS | Individuals using the Internet (% of population) |
| gdp_usd | NY.GDP.MKTP.CD | GDP (current US$) |
| gdp_per_capita | NY.GDP.PCAP.CD | GDP per capita (current US$) |
| inflation | FP.CPI.TOTL.ZG | Inflation, consumer prices (annual %) |
| urban_population_pct | SP.URB.TOTL.IN.ZS | Urban population (% of total population) |

---

## S2. FX Rate Assumptions

Annual average USD/NGN rates used for currency conversion in this project.

| Year | USD/NGN Rate | Source Note |
|------|-------------|-------------|
| 2015 | 199 | CBN official rate |
| 2016 | 305 | Post-devaluation |
| 2017 | 360 | Approximate annual average |
| 2018 | 362 | Approximate annual average |
| 2019 | 363 | Approximate annual average |
| 2020 | 381 | Approximate annual average |
| 2021 | 413 | Approximate annual average |
| 2022 | 447 | Approximate annual average |
| 2023 | 900 | Post-unification devaluation |

---

## S3. Competitor Data Sources

| Company | User Figure Source | Funding Source |
|---------|-------------------|----------------|
| OPay | OPay press release, 2023 | Crunchbase |
| Moniepoint | Moniepoint press release, 2023 | Crunchbase |
| PalmPay | PalmPay press release, 2023 | Crunchbase |
| Kuda | Kuda press release, 2022 | Crunchbase |
| Carbon | Carbon blog post, 2023 | Crunchbase |
| FairMoney | FairMoney blog, 2023 | Crunchbase |
| ALAT | Wema Bank annual report | Bank subsidiary |
| GTCo Squad | GTCo investor presentation | Bank subsidiary |
| Access Closa | Access Bank press release | Bank subsidiary |
| MTN MoMo | MTN Group annual report | Telco subsidiary |

---

## S4. Financial Model Parameter Derivation

### ARPU Derivation

The $12/year ARPU estimate is derived from a simplified monetisation assumption
applied to average annual digital transaction value per user.

### Churn Rate

The 18% churn assumption is informed by fintech benchmarking and adjusted for the
Nigerian market context.

### User Growth Rates

The 80% and 60% growth assumptions for Years 2 and 3 are aggressive but within the
range of observed Nigerian fintech growth patterns.

---

## S5. Notebook Execution Checksums

After running all notebooks, the following files should be created:

| File | Location | Notes |
|------|----------|-------|
| wb_indicators_raw.csv | data/raw/ | World Bank data |
| cbn_payments.csv | data/external/ | CBN payment series |
| efina_summary.csv | data/external/ | EFInA summary |
| competitors.csv | data/external/ | Competitor benchmark |
| nigeria_combined.csv | data/processed/ | Master analysis dataset |
| financial_model.xlsx | data/processed/ | Excel workbook |
| fig01_*.png | reports/figures/ | Inclusion trend |
| fig02_*.png | reports/figures/ | NIP payment growth |
| fig03_*.png | reports/figures/ | Market sizing funnel |
| fig14_*.png | reports/figures/ | Risk matrix heatmap |
| TABLE_01_*.csv | paper_or_report/tables/ | Executive summary stats |
