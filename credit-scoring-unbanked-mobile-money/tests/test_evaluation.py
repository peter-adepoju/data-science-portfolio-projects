import numpy as np

from project_package.evaluation import classification_metrics, threshold_cost_curve


def test_classification_metrics_returns_core_metrics():
    y_true = np.array([0, 0, 1, 1])
    y_proba = np.array([0.1, 0.2, 0.7, 0.9])
    metrics = classification_metrics(y_true, y_proba, threshold=0.5)
    assert metrics["roc_auc"] == 1.0
    assert metrics["f1"] == 1.0


def test_threshold_cost_curve_has_expected_columns():
    y_true = np.array([0, 0, 1, 1])
    y_proba = np.array([0.1, 0.4, 0.6, 0.9])
    curve = threshold_cost_curve(y_true, y_proba, thresholds=np.array([0.3, 0.5]))
    assert {"threshold", "total_cost", "cost_per_applicant"}.issubset(curve.columns)
    assert len(curve) == 2
