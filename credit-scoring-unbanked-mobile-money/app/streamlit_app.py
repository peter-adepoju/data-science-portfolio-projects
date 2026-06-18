from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project_package.config import PROCESSED_DIR, MODELS_DIR
from project_package.inference import score_applications, create_adverse_action_reasons

st.set_page_config(page_title="Credit Scoring for the Unbanked", layout="wide")
st.title("Credit Scoring for the Unbanked")

st.markdown(
    """
    This dashboard mirrors the report narrative in an interactive form.
    It uses a public proxy dataset rather than real mobile-money records, and it shows how a
    credit-risk workflow can move from exploratory analysis to scoring, thresholding, and
    adverse-action style explanations.
    """
)

st.subheader("Project framing")
st.markdown(
    """
    The project is intentionally honest about scope. It is a reproducible prototype for
    alternative-data credit scoring, not a production lending system and not a claim that
    private mobile-money records are included in the repository.
    """
)

model_path = MODELS_DIR / "best_credit_scoring_pipeline.joblib"
sample_path = PROCESSED_DIR / "inference_sample.csv"

if not model_path.exists() or not sample_path.exists():
    st.warning("Run the notebooks through Notebook 07 first. The trained model and inference sample were not found.")
    st.stop()

sample = pd.read_csv(sample_path)

st.subheader("How to read the dashboard")
st.markdown(
    """
    Adjust the scoring controls on the left to see how the model behaves under different
    thresholds. The table, risk-band chart, and reason helper are designed to show how a
    decision-support workflow can be explained to a reviewer or analyst.
    """
)

st.sidebar.header("Scoring controls")
n_rows = st.sidebar.slider("Number of applications to score", min_value=5, max_value=min(200, len(sample)), value=min(25, len(sample)))
threshold = st.sidebar.slider("High-risk threshold", min_value=0.05, max_value=0.80, value=0.25, step=0.01)

scored = score_applications("best_credit_scoring_pipeline.joblib", sample.head(n_rows))
scored["decision"] = scored["predicted_default_probability"].apply(lambda p: "review_or_reject" if p >= threshold else "approve")

col1, col2, col3 = st.columns(3)
col1.metric("Applications scored", len(scored))
col2.metric("Mean default probability", f"{scored['predicted_default_probability'].mean():.3f}")
col3.metric("Review/reject rate", f"{(scored['decision'] == 'review_or_reject').mean():.1%}")

st.subheader("Scored applications")
st.dataframe(scored[["predicted_default_probability", "risk_band", "decision"] + [c for c in scored.columns if c not in ["predicted_default_probability", "risk_band", "decision"]]].head(n_rows))

st.subheader("Risk-band distribution")
st.bar_chart(scored["risk_band"].value_counts().sort_index())

st.subheader("Illustrative adverse-action reason helper")
st.markdown(
    """
    This section is meant to illustrate how model outputs could be translated into plain
    language reasons. The rules are heuristic and should not be treated as formal underwriting
    policy.
    """
)
selected_idx = st.number_input("Application row", min_value=0, max_value=len(scored) - 1, value=0, step=1)
reasons = create_adverse_action_reasons(scored.iloc[int(selected_idx)])
if reasons:
    for reason in reasons:
        st.write(f"- {reason}")
else:
    st.write("No simple heuristic reason was triggered for this row.")

st.caption(
    "This prototype is for portfolio and research demonstration only. It is not a production lending system."
)
