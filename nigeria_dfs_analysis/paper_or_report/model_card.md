# Model Card
## Nigeria DFS Market Analysis - Financial Model

This model card documents the financial projection model used in the project.

---

## Model Description

- Name: Nigeria DFS 3-Year Revenue Projection Model
- Version: 1.0
- Type: Deterministic financial projection model
- Primary use: Consulting engagement and portfolio demonstration

---

## Intended Use

Primary intended use:
- Illustrative 3-year financial projection for a hypothetical new DFS entrant
- Sensitivity analysis and scenario planning

Intended users:
- Consulting analysts
- Students and portfolio builders
- Educators demonstrating financial modelling concepts

Out-of-scope use cases:
- Actual investment decisions without replacing assumptions with primary data
- Regulatory filings or financial reporting

---

## Factors and Assumptions

Key assumptions are documented in `configs/config.yaml`.

| Parameter | Base Case Value | Assumption Source |
|-----------|----------------|------------------|
| Year 1 users | 500,000 | Management target |
| Year 2 user growth | 80%/yr | Assumption |
| Year 3 user growth | 60%/yr | Assumption |
| Annual churn | 18% | Assumption |
| ARPU Year 1 | $12/year | Assumption |
| ARPU growth | 15%/yr | Assumption |
| COGS | 40% of revenue | Assumption |
| Personnel | 25% of revenue | Assumption |

---

## Performance and Outputs

What the model produces:
- 3-year active user projections
- Revenue by stream
- Simplified income statement
- EBITDA margin trajectory
- Sensitivity tables
- Comparable company valuation range

What the model does not produce:
- DCF valuation
- LTV/CAC analysis
- Working capital or capex projections
- Cash flow statement
- Balance sheet

---

## Limitations

1. Entirely assumption-driven
2. No uncertainty quantification beyond sensitivity tables
3. Simplified cost structure
4. FX not modelled in a fully dynamic way
5. No regulatory cost modelling beyond a simplified allowance

---

## Ethical Considerations

- The model produces projections that can look precise but remain uncertain.
- All competitor data used in the broader project is from public sources.
- The model should not be used for investor or lender representations without validated operating data.

---

## Citation

If you use this model, cite the project repository and the financial model section of the report.
