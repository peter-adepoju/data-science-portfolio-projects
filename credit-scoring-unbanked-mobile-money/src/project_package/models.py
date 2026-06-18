from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import MODELS_DIR, RANDOM_STATE, ensure_project_dirs
from .features import get_feature_columns

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover
    XGBClassifier = None


@dataclass
class TrainedModel:
    name: str
    pipeline: Pipeline


def build_preprocessor(X: pd.DataFrame, scale_numeric: bool = False) -> ColumnTransformer:
    """Building a reusable preprocessing object for mixed tabular credit data."""
    numeric_cols, categorical_cols = get_feature_columns(X.assign(default_next_month=0))
    numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipe = Pipeline(numeric_steps)
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric_pipe, numeric_cols),
        ("cat", categorical_pipe, categorical_cols),
    ])


def build_logistic_model(X: pd.DataFrame) -> Pipeline:
    """Building the regularized logistic-regression baseline."""
    return Pipeline([
        ("preprocess", build_preprocessor(X, scale_numeric=True)),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)),
    ])


def build_random_forest_model(X: pd.DataFrame) -> Pipeline:
    """Building the random-forest nonlinear baseline."""
    return Pipeline([
        ("preprocess", build_preprocessor(X, scale_numeric=False)),
        ("model", RandomForestClassifier(
            n_estimators=350,
            max_depth=10,
            min_samples_leaf=20,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])


def build_xgboost_model(X: pd.DataFrame, y: pd.Series | None = None) -> Pipeline:
    """Building an XGBoost credit-risk model with imbalance-aware weighting."""
    if XGBClassifier is None:
        raise ImportError("xgboost was not installed. Install requirements.txt before training this model.")
    scale_pos_weight = 1.0
    if y is not None and y.sum() > 0:
        scale_pos_weight = float((len(y) - y.sum()) / y.sum())
    return Pipeline([
        ("preprocess", build_preprocessor(X, scale_numeric=False)),
        ("model", XGBClassifier(
            n_estimators=500,
            max_depth=3,
            learning_rate=0.035,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_lambda=5.0,
            min_child_weight=5,
            objective="binary:logistic",
            eval_metric="aucpr",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            scale_pos_weight=scale_pos_weight,
        )),
    ])


def train_standard_models(X_train: pd.DataFrame, y_train: pd.Series) -> list[TrainedModel]:
    """Training the baseline and boosted-tree models used in the comparison notebook."""
    builders = {
        "logistic_regression": build_logistic_model(X_train),
        "random_forest": build_random_forest_model(X_train),
        "xgboost": build_xgboost_model(X_train, y_train),
    }
    trained = []
    for name, pipeline in builders.items():
        pipeline.fit(X_train, y_train)
        trained.append(TrainedModel(name=name, pipeline=pipeline))
    return trained


def predict_proba_positive(model: Pipeline, X: pd.DataFrame) -> np.ndarray:
    """Returning positive-class probabilities from a fitted scikit-learn pipeline."""
    proba = model.predict_proba(X)
    if proba.ndim != 2 or proba.shape[1] < 2:
        raise ValueError("Model did not return a two-column probability matrix.")
    return proba[:, 1]


def save_model(model: Any, filename: str) -> str:
    """Persisting a trained model or preprocessor into the models directory."""
    ensure_project_dirs()
    path = MODELS_DIR / filename
    joblib.dump(model, path)
    return str(path)


def load_model(filename: str) -> Any:
    """Loading a persisted model from the models directory."""
    path = MODELS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Model artifact was not found at {path}.")
    return joblib.load(path)
