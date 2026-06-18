from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .config import RANDOM_STATE, TARGET
from .data import BILL_COLS, PAY_AMT_COLS, PAY_STATUS_COLS

CATEGORICAL_COLS = ["sex", "education", "marriage"]


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Dividing while avoiding infinities from zero denominators."""
    out = numerator / denominator.replace(0, np.nan)
    return out.replace([np.inf, -np.inf], np.nan)


def add_repayment_proxy_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineering repayment-history features inspired by mobile-money lending behavior."""
    out = df.copy()
    pay_status = out[PAY_STATUS_COLS]
    bills = out[BILL_COLS]
    payments = out[PAY_AMT_COLS]

    out["proxy_recent_repayment_status"] = out["pay_status_sep"]
    out["proxy_max_delinquency_6m"] = pay_status.max(axis=1)
    out["proxy_mean_delinquency_6m"] = pay_status.mean(axis=1)
    out["proxy_delinquency_count_6m"] = (pay_status > 0).sum(axis=1)
    out["proxy_severe_delinquency_count_6m"] = (pay_status >= 2).sum(axis=1)
    out["proxy_on_time_count_6m"] = (pay_status <= 0).sum(axis=1)

    total_bill = bills.clip(lower=0).sum(axis=1)
    total_payment = payments.clip(lower=0).sum(axis=1)
    out["proxy_total_bill_6m"] = total_bill
    out["proxy_total_payment_6m"] = total_payment
    out["proxy_total_payment_to_bill_6m"] = _safe_divide(total_payment, total_bill).fillna(0).clip(0, 5)

    ratio_cols = []
    for bill_col, pay_col in zip(BILL_COLS, PAY_AMT_COLS):
        ratio_col = f"ratio_{pay_col}_to_{bill_col}"
        out[ratio_col] = _safe_divide(out[pay_col].clip(lower=0), out[bill_col].clip(lower=0)).fillna(0).clip(0, 5)
        ratio_cols.append(ratio_col)

    out["proxy_payment_ratio_mean_6m"] = out[ratio_cols].mean(axis=1)
    out["proxy_payment_ratio_volatility_6m"] = out[ratio_cols].std(axis=1).fillna(0)
    out["proxy_payment_consistency_6m"] = (payments > 0).sum(axis=1) / len(PAY_AMT_COLS)
    out["proxy_bill_volatility_6m"] = bills.std(axis=1).fillna(0)
    out["proxy_payment_volatility_6m"] = payments.std(axis=1).fillna(0)
    out["proxy_utilization_mean_6m"] = _safe_divide(bills.clip(lower=0).mean(axis=1), out["credit_limit"]).fillna(0).clip(0, 5)
    out["proxy_utilization_max_6m"] = _safe_divide(bills.clip(lower=0).max(axis=1), out["credit_limit"]).fillna(0).clip(0, 5)
    out["proxy_recent_payment_to_limit"] = _safe_divide(out["pay_amt_sep"].clip(lower=0), out["credit_limit"]).fillna(0).clip(0, 5)
    out["proxy_recent_bill_to_limit"] = _safe_divide(out["bill_amt_sep"].clip(lower=0), out["credit_limit"]).fillna(0).clip(0, 5)
    out["proxy_age_to_credit_limit"] = _safe_divide(out["age"], out["credit_limit"]).fillna(0)
    return out


def add_synthetic_mobile_money_aggregates(events: pd.DataFrame) -> pd.DataFrame:
    """Aggregating clearly synthetic mobile-money events for tests or demo interfaces."""
    if events.empty:
        return pd.DataFrame()
    events = events.copy()
    events["amount"] = pd.to_numeric(events["amount"], errors="coerce").fillna(0)
    recent_30 = events[events["days_ago"] <= 30]
    recent_90 = events[events["days_ago"] <= 90]

    def sum_by_event(frame: pd.DataFrame, event_type: str, name: str) -> pd.Series:
        return frame[frame["event_type"] == event_type].groupby("customer_id")["amount"].sum().rename(name)

    def count_by_event(frame: pd.DataFrame, event_type: str, name: str) -> pd.Series:
        return frame[frame["event_type"] == event_type].groupby("customer_id").size().rename(name)

    base = pd.DataFrame(index=events["customer_id"].drop_duplicates().sort_values())
    features = [
        count_by_event(recent_30, "airtime_topup", "mm_topup_count_30d"),
        sum_by_event(recent_30, "airtime_topup", "mm_topup_amount_sum_30d"),
        count_by_event(recent_30, "cash_in", "mm_cash_in_count_30d"),
        count_by_event(recent_30, "cash_out", "mm_cash_out_count_30d"),
        sum_by_event(recent_90, "p2p_receive", "mm_p2p_received_sum_90d"),
        sum_by_event(recent_90, "p2p_send", "mm_p2p_sent_sum_90d"),
        count_by_event(recent_90, "bill_pay", "mm_billpay_count_90d"),
        count_by_event(recent_30, "ussd_session", "mm_ussd_sessions_30d"),
    ]
    for series in features:
        base = base.join(series, how="left")
    base = base.fillna(0).reset_index().rename(columns={"index": "customer_id"})
    return base


def get_feature_columns(df: pd.DataFrame, target: str = TARGET) -> tuple[list[str], list[str]]:
    """Returning numeric and categorical feature columns for preprocessing."""
    categorical = [c for c in CATEGORICAL_COLS if c in df.columns]
    excluded = {target}
    numeric = [c for c in df.columns if c not in excluded and c not in categorical and pd.api.types.is_numeric_dtype(df[c])]
    return numeric, categorical


def create_modeling_split(
    df: pd.DataFrame,
    target: str = TARGET,
    test_size: float = 0.20,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Creating a stratified holdout split for default-risk classification.

    The UCI data was cross-sectional with six ordered repayment-history months,
    not true loan-origination timestamps. A stratified holdout was therefore used
    for the public proxy dataset, while the codebase still isolates split logic
    so that a real chronological split could replace it when dated mobile-money
    loan records become available.
    """
    X = df.drop(columns=[target])
    y = df[target].astype(int)
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def chronological_customer_split(
    df: pd.DataFrame,
    date_col: str,
    target: str = TARGET,
    test_fraction: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splitting dated records chronologically for future real mobile-money data."""
    if date_col not in df.columns:
        raise ValueError(f"date_col={date_col!r} was not in the dataframe.")
    ordered = df.sort_values(date_col).reset_index(drop=True)
    cutoff = int(len(ordered) * (1 - test_fraction))
    return ordered.iloc[:cutoff].copy(), ordered.iloc[cutoff:].copy()
