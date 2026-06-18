# Notebook Workflow

Run the notebooks in numerical order.

1. `00_project_overview_and_data_strategy.ipynb` — data-access position, problem framing, and project plan.
2. `01_download_and_validate_open_credit_data.ipynb` — downloading, cleaning, schema validation, and saving the base processed dataset.
3. `02_exploratory_data_analysis.ipynb` — default rates, repayment behavior, payment distributions, missingness, and class balance.
4. `03_feature_engineering_mobile_money_proxy.ipynb` — creating repayment, volatility, utilization, affordability, and mobile-money-style proxy features.
5. `04_modeling_baselines_and_xgboost.ipynb` — training logistic regression, random forest, and XGBoost models.
6. `05_deep_learning_credit_risk_model.ipynb` — training a PyTorch multilayer perceptron.
7. `06_model_evaluation_calibration_fairness.ipynb` — comparing models, calibration, threshold-cost analysis, and group error analysis.
8. `07_inference_reporting_and_streamlit_assets.ipynb` — saving final inference assets and report-ready tables.

Each notebook was written with markdown explanations and executable cells. Figures are saved to `reports/figures/` before being displayed. Tables are saved to `reports/tables/`.
