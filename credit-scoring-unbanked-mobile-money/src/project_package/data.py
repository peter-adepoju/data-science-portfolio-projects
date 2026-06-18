from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

import numpy as np
import pandas as pd

from .config import RAW_DIR, PROCESSED_DIR, TARGET, ensure_project_dirs

UCI_DEFAULT_ZIP_URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"

COLUMN_RENAME = {
    "default payment next month": TARGET,
    "LIMIT_BAL": "credit_limit",
    "SEX": "sex",
    "EDUCATION": "education",
    "MARRIAGE": "marriage",
    "AGE": "age",
    "PAY_0": "pay_status_sep",
    "PAY_2": "pay_status_aug",
    "PAY_3": "pay_status_jul",
    "PAY_4": "pay_status_jun",
    "PAY_5": "pay_status_may",
    "PAY_6": "pay_status_apr",
    "BILL_AMT1": "bill_amt_sep",
    "BILL_AMT2": "bill_amt_aug",
    "BILL_AMT3": "bill_amt_jul",
    "BILL_AMT4": "bill_amt_jun",
    "BILL_AMT5": "bill_amt_may",
    "BILL_AMT6": "bill_amt_apr",
    "PAY_AMT1": "pay_amt_sep",
    "PAY_AMT2": "pay_amt_aug",
    "PAY_AMT3": "pay_amt_jul",
    "PAY_AMT4": "pay_amt_jun",
    "PAY_AMT5": "pay_amt_may",
    "PAY_AMT6": "pay_amt_apr",
}

PAY_STATUS_COLS = [
    "pay_status_apr", "pay_status_may", "pay_status_jun", "pay_status_jul", "pay_status_aug", "pay_status_sep"
]
BILL_COLS = ["bill_amt_apr", "bill_amt_may", "bill_amt_jun", "bill_amt_jul", "bill_amt_aug", "bill_amt_sep"]
PAY_AMT_COLS = ["pay_amt_apr", "pay_amt_may", "pay_amt_jun", "pay_amt_jul", "pay_amt_aug", "pay_amt_sep"]


def download_uci_default_dataset(force: bool = False) -> Path:
    """Downloading the UCI Default of Credit Card Clients spreadsheet into data/raw.

    The function first used the stable UCI static zip URL. The raw file was not
    committed to the repository, so running Notebook 01 recreated it locally.
    """
    ensure_project_dirs()
    output_path = RAW_DIR / "default_of_credit_card_clients.xls"
    if output_path.exists() and not force:
        return output_path

    with urlopen(UCI_DEFAULT_ZIP_URL, timeout=60) as response:
        payload = response.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        excel_members = [m for m in zf.namelist() if m.lower().endswith(('.xls', '.xlsx'))]
        if not excel_members:
            raise FileNotFoundError("No Excel file was found inside the UCI zip archive.")
        member = excel_members[0]
        output_path.write_bytes(zf.read(member))
    return output_path


def load_raw_uci_default(path: Optional[Path] = None) -> pd.DataFrame:
    """Loading the raw UCI spreadsheet and standardizing the original column names."""
    if path is None:
        path = download_uci_default_dataset(force=False)
    raw = pd.read_excel(path, header=1)
    raw = raw.rename(columns=COLUMN_RENAME)
    raw.columns = [str(c).strip() for c in raw.columns]
    return raw


def clean_credit_default_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleaning the public credit-default dataset for modeling.

    Category values outside documented ranges were grouped into explicit
    'other/unknown' levels rather than being silently removed.
    """
    clean = df.copy()
    clean = clean.drop(columns=[c for c in ["ID"] if c in clean.columns])
    clean[TARGET] = clean[TARGET].astype(int)

    # Harmonizing categorical values based on the UCI codebook.
    clean["sex"] = clean["sex"].map({1: "male", 2: "female"}).fillna("unknown")
    clean["education"] = clean["education"].replace({0: 4, 5: 4, 6: 4})
    clean["education"] = clean["education"].map({1: "graduate_school", 2: "university", 3: "high_school", 4: "other"}).fillna("other")
    clean["marriage"] = clean["marriage"].replace({0: 3})
    clean["marriage"] = clean["marriage"].map({1: "married", 2: "single", 3: "other"}).fillna("other")

    numeric_cols = [c for c in clean.columns if c not in ["sex", "education", "marriage"]]
    for col in numeric_cols:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")

    return clean


def save_processed_base(df: pd.DataFrame, filename: str = "credit_default_base.csv") -> Path:
    """Saving the cleaned base dataset for downstream notebooks."""
    ensure_project_dirs()
    path = PROCESSED_DIR / filename
    df.to_csv(path, index=False)
    return path


def load_processed_base(filename: str = "credit_default_base.csv") -> pd.DataFrame:
    """Loading the cleaned base dataset created by Notebook 01."""
    path = PROCESSED_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Processed dataset was not found at {path}. Run Notebook 01 first.")
    return pd.read_csv(path)


def create_sample_mobile_money_events(n_customers: int = 500, random_state: int = 42) -> pd.DataFrame:
    """Creating a clearly synthetic mobile-money event table for interface testing only.

    This data was not real customer data. It supported tests and app scaffolding
    when a legitimate mobile-money dataset was unavailable.
    """
    rng = np.random.default_rng(random_state)
    rows = []
    event_types = ["airtime_topup", "cash_in", "cash_out", "p2p_send", "p2p_receive", "bill_pay", "ussd_session"]
    for customer_id in range(1, n_customers + 1):
        n_events = int(rng.poisson(15) + 3)
        for _ in range(n_events):
            event_type = rng.choice(event_types, p=[0.30, 0.12, 0.12, 0.14, 0.14, 0.10, 0.08])
            amount = 0.0 if event_type == "ussd_session" else float(rng.gamma(shape=2.0, scale=900.0))
            days_ago = int(rng.integers(0, 180))
            rows.append({
                "customer_id": customer_id,
                "days_ago": days_ago,
                "event_type": event_type,
                "amount": round(amount, 2),
                "is_synthetic_demo": True,
            })
    return pd.DataFrame(rows)
