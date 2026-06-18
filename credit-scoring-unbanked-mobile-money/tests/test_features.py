import pandas as pd

from project_package.config import TARGET
from project_package.features import add_repayment_proxy_features, chronological_customer_split, create_modeling_split


def _toy_credit_frame():
    return pd.DataFrame({
        "credit_limit": [1000, 2000, 1500, 3000, 2500, 1100],
        "sex": ["male", "female", "female", "male", "female", "male"],
        "education": ["university"] * 6,
        "marriage": ["single"] * 6,
        "age": [25, 35, 45, 28, 39, 41],
        "pay_status_apr": [0, 1, 0, 2, -1, 0],
        "pay_status_may": [0, 1, 0, 2, -1, 0],
        "pay_status_jun": [0, 0, 0, 2, -1, 0],
        "pay_status_jul": [0, 0, 0, 1, -1, 0],
        "pay_status_aug": [0, 0, 0, 1, -1, 0],
        "pay_status_sep": [0, 0, 1, 1, -1, 0],
        "bill_amt_apr": [100, 300, 200, 800, 0, 120],
        "bill_amt_may": [100, 400, 180, 900, 0, 120],
        "bill_amt_jun": [100, 350, 180, 850, 0, 120],
        "bill_amt_jul": [100, 330, 180, 830, 0, 120],
        "bill_amt_aug": [100, 300, 180, 810, 0, 120],
        "bill_amt_sep": [100, 300, 180, 800, 0, 120],
        "pay_amt_apr": [100, 50, 200, 20, 0, 120],
        "pay_amt_may": [100, 50, 180, 20, 0, 120],
        "pay_amt_jun": [100, 50, 180, 20, 0, 120],
        "pay_amt_jul": [100, 50, 180, 20, 0, 120],
        "pay_amt_aug": [100, 50, 180, 20, 0, 120],
        "pay_amt_sep": [100, 50, 180, 20, 0, 120],
        TARGET: [0, 1, 0, 1, 0, 1],
    })


def test_add_repayment_proxy_features_creates_expected_columns():
    df = add_repayment_proxy_features(_toy_credit_frame())
    assert "proxy_delinquency_count_6m" in df.columns
    assert "proxy_total_payment_to_bill_6m" in df.columns
    assert df["proxy_total_payment_to_bill_6m"].notna().all()


def test_create_modeling_split_preserves_shape():
    df = add_repayment_proxy_features(_toy_credit_frame())
    X_train, X_test, y_train, y_test = create_modeling_split(df, test_size=0.33, random_state=7)
    assert len(X_train) + len(X_test) == len(df)
    assert len(y_train) + len(y_test) == len(df)


def test_chronological_split_orders_dates():
    df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=10), TARGET: [0, 1] * 5})
    train, test = chronological_customer_split(df, date_col="date", test_fraction=0.2)
    assert train["date"].max() < test["date"].min()
