# Limitations

## Nigeria DFS Market Analysis - Transparency Statement

This document provides a complete and honest account of the limitations of the
Nigeria Digital Financial Services Market Analysis. It is part of the project,
not an afterthought.

Rule: if a finding cannot be defended in a client meeting, it should not appear
in the report without a documented caveat.

---

## 1. Data Quality Limitations

### 1.1 Competitor User Figures

All user figures for OPay, PalmPay, Moniepoint, Kuda, and other players are
self-reported in company press releases. They have not been audited, independently
verified, or reported to a public regulatory body in a way that allows direct
comparison.

- "Registered users" may include inactive or duplicate accounts
- No consistent definition of "user" across companies
- Some reported figures have been disputed in Nigerian media

Consequence: all market concentration calculations must be treated as illustrative
estimates, not verified facts.

### 1.2 EFInA Survey Methodology Changes

The EFInA Access to Finance Survey changed its sampling methodology between rounds.
The 2020 survey was conducted remotely due to COVID-19 restrictions, which likely
under-sampled some populations.

- Comparisons between pre-2020 and post-2020 EFInA figures carry additional uncertainty
- The analysis flags this as an unresolved issue

### 1.3 CBN Pre-2020 NIP Data

NIP transaction figures before 2020 may include settlement flows alongside retail
payment flows. This can affect the apparent growth rate across the full series.

- The pre-2020 baseline may be overstated relative to later figures
- This can make CAGR appear lower than a pure retail-payment CAGR

### 1.4 FX Rate Assumptions

The NGN/USD exchange rate weakened sharply from end-2022 through 2024. All USD
market-size estimates are therefore sensitive to the chosen FX assumption.

- Approximate annual average FX rates are used
- These are not official CBN fixing rates
- USD market-size estimates have substantial uncertainty

### 1.5 World Bank Findex Gaps

The World Bank Global Findex is collected every three years. Between collection
years, the analysis uses the most recent available value, which means some annual
granularity is effectively interpolated.

---

## 2. Modelling Limitations

### 2.1 Financial Model Is Assumption-Driven

The three-year financial model is not based on actual operating data from any
company. Every input is an assumption documented in `configs/config.yaml`.

Parameters with the highest impact on model outputs:

- ARPU
- churn rate
- user growth rate

Recommendation: before using the model for an investment decision, replace the
assumption-based inputs with actual operating data from a comparable Nigerian fintech.

### 2.2 No Discounted Cash Flow Valuation

The project uses EV/Revenue multiple-based valuation only. A proper DCF would
require:

- a credible weighted average cost of capital
- long-term terminal growth assumptions
- detailed capex and working capital projections

These are beyond scope for the current market-entry assessment.

### 2.3 No Unit Economics Model

The analysis does not model Customer Acquisition Cost, Lifetime Value, or CAC
payback period. Those metrics would be essential in a private-equity or venture
capital setting.

---

## 3. Methodological Limitations

### 3.1 Correlation, Not Causation

All regression analyses are exploratory. They show relationships among trends
and financial inclusion metrics, but they do not establish causality.

### 3.2 Small Sample Sizes

- EFInA regression: small number of survey waves
- CBN time series: limited number of annual observations
- Hypothesis tests should be interpreted as exploratory

### 3.3 No Primary Research

This analysis relies entirely on secondary data sources.

- No consumer surveys were conducted
- No interviews with fintech operators, agents, or regulators were conducted
- No mystery shopping or field validation was conducted

### 3.4 No Geospatial Analysis

Financial exclusion is geographically uneven in Nigeria, but the current project
does not model state-level or LGA-level spatial variation.

---

## 4. Scope Limitations

### 4.1 No Regulatory Modelling

CBN licensing requirements, PSB guidelines, and NDPR compliance are assessed
qualitatively only. This report is not legal advice.

### 4.2 No Technology Assessment

The analysis assumes that the required payment technology can be built within
the cost assumptions used in the model.

### 4.3 Nigeria Only

The analysis covers Nigeria only. A Pan-African strategy would require separate
country-level work for Kenya, Ghana, South Africa, and others.

---

## 5. What Would Resolve These Limitations

| Limitation | Resolution | Estimated Effort |
|------------|------------|------------------|
| Unverified user counts | Confidential transaction data | Partnership/NDA |
| EFInA methodology changes | Primary survey | 3 months |
| Financial model assumptions | 12 months of operating data | Operational only |
| No LTV/CAC model | Agent network cost study | 4-6 weeks |
| No DCF valuation | Financial model specialist | 2 weeks |
| No geospatial analysis | LGA-level census data and GIS work | 6 weeks |
| No regulatory modelling | Specialist legal review | 2-4 weeks |

---

This limitations document was written as part of the project, not added
retrospectively.
