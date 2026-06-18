from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project_package.config import MODELS_DIR, PROCESSED_DIR, REPORTS_DIR
from project_package.inference import create_adverse_action_reasons, score_applications

st.set_page_config(page_title="Credit Scoring for the Unbanked", layout="wide")
st.title("Credit Scoring for the Unbanked")

st.markdown(
    """
    This dashboard is the deployable companion to the report-style README.
    It uses public proxy data and mobile-money-style feature abstractions to demonstrate a
    credit-risk workflow from model comparison to thresholding and explanation.
    """
)


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_sample() -> pd.DataFrame | None:
    path = PROCESSED_DIR / "inference_sample.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


metrics_path = REPORTS_DIR / "tables" / "06_final_model_comparison.csv"
metrics = load_csv(metrics_path)
sample = load_sample()
model_path = MODELS_DIR / "best_credit_scoring_pipeline.joblib"

st.subheader("Project framing")
st.markdown(
    """
    The repository is intentionally explicit about scope. It is a reproducible prototype for
    alternative-data credit scoring, not a production lending system and not a claim that
    private mobile-money records are bundled here.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("Raw dataset", "available" if (ROOT / "data" / "raw" / "default_of_credit_card_clients.xls").exists() else "missing")
col2.metric("Trained model", "available" if model_path.exists() else "missing")
col3.metric("Inference sample", "available" if sample is not None else "missing")

st.subheader("How to read the dashboard")
st.markdown(
    """
    The left sidebar lets you choose how many applications to score and where the high-risk
    threshold should sit. The table and charts show the resulting decisions, while the reason
    helper illustrates how a model output could be translated into a plain-language review
    note.
    """
)

if metrics is not None and not metrics.empty:
    st.subheader("Final model comparison")
    display_metrics = metrics[["model", "roc_auc", "pr_auc", "brier_score", "log_loss", "f1", "precision", "recall", "balanced_accuracy"]].copy()
    st.dataframe(display_metrics, use_container_width=True)
else:
    st.info("The final comparison table was not found in reports/tables/06_final_model_comparison.csv.")

if sample is None:
    st.warning(
        "The inference sample was not found. Run Notebook 07 or regenerate the processed artifacts before using the scoring controls."
    )
    st.stop()

st.sidebar.header("Scoring controls")
n_rows = st.sidebar.slider(
    "Number of applications to score",
    min_value=5,
    max_value=min(200, len(sample)),
    value=min(25, len(sample)),
)
threshold = st.sidebar.slider("High-risk threshold", min_value=0.05, max_value=0.80, value=0.25, step=0.01)

if not model_path.exists():
    st.error("The trained model artifact was not found in `models/`. Re-run the notebook pipeline first.")
    st.stop()

scored = score_applications("best_credit_scoring_pipeline.joblib", sample.head(n_rows))
scored["decision"] = scored["predicted_default_probability"].apply(
    lambda p: "review_or_reject" if p >= threshold else "approve"
)

st.subheader("Scored applications")
st.dataframe(
    scored[
        ["predicted_default_probability", "risk_band", "decision"]
        + [c for c in scored.columns if c not in ["predicted_default_probability", "risk_band", "decision"]]
    ],
    use_container_width=True,
)

col1, col2, col3 = st.columns(3)
col1.metric("Applications scored", len(scored))
col2.metric("Mean default probability", f"{scored['predicted_default_probability'].mean():.3f}")
col3.metric("Review/reject rate", f"{(scored['decision'] == 'review_or_reject').mean():.1%}")

st.subheader("Risk-band distribution")
st.bar_chart(scored["risk_band"].value_counts().sort_index())

st.subheader("Threshold sensitivity")
threshold_summary = (
    scored.assign(review_or_reject=scored["predicted_default_probability"] >= threshold)
    .groupby("decision")
    .size()
    .reset_index(name="count")
)
st.dataframe(threshold_summary, use_container_width=True)

st.subheader("Illustrative adverse-action reason helper")
st.markdown(
    """
    This section shows how the model output could be translated into a brief explanation.
    The logic is heuristic and is not a substitute for a formal adverse-action notice.
    """
)
selected_idx = st.number_input("Application row", min_value=0, max_value=len(scored) - 1, value=0, step=1)
reasons = create_adverse_action_reasons(scored.iloc[int(selected_idx)])
if reasons:
    for reason in reasons:
        st.write(f"- {reason}")
else:
    st.write("No simple heuristic reason was triggered for this row.")

st.caption("Python 3.11 compatible Streamlit entrypoint for the deployed demo.")
