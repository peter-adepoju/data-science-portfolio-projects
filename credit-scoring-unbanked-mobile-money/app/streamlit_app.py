from __future__ import annotations

from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Credit Scoring for the Unbanked",
    layout="wide",
)

st.title("Credit Scoring for the Unbanked")

st.markdown(
    """
    This Streamlit app is the deployable companion to the report-style README.
    It is intentionally self-contained so it can open on Streamlit Cloud with Python 3.11
    even when the trained artifacts are not bundled in the repository.
    """
)

st.subheader("Project framing")
st.markdown(
    """
    The project is a credit-risk scoring prototype for a financial-inclusion setting.
    It uses public proxy data and mobile-money-style feature abstractions rather than
    private transaction records.
    """
)

expected_paths = {
    "Raw dataset": ROOT / "data" / "raw" / "default_of_credit_card_clients.xls",
    "Trained model": ROOT / "models" / "best_credit_scoring_pipeline.joblib",
    "Inference sample": ROOT / "data" / "processed" / "inference_sample.csv",
    "Reports folder": ROOT / "reports",
}

st.subheader("Deployment checks")
for label, path in expected_paths.items():
    if path.exists():
        st.success(f"{label} found: {path.relative_to(ROOT)}")
    else:
        st.warning(
            f"{label} not found at {path.relative_to(ROOT)}. "
            "This app still opens, but the full notebook-generated workflow is not yet available in this checkout."
        )

st.subheader("How to use this app")
st.markdown(
    """
    1. If the notebook outputs are present, run the full scoring workflow and review the model outputs.
    2. Use the README and reports folder to inspect figures, tables, and calibration artifacts.
    3. If the trained artifacts are not present, this page still provides a working deployment shell for Streamlit Cloud.
    """
)

st.subheader("What the report covers")
st.markdown(
    """
    - public proxy data and ethical framing
    - repayment-behavior feature engineering
    - model comparison across logistic regression, random forest, XGBoost, and an MLP
    - calibration, thresholding, and subgroup diagnostics
    - report-ready figures and tables
    """
)

st.caption("Python 3.11 compatible Streamlit entrypoint.")
