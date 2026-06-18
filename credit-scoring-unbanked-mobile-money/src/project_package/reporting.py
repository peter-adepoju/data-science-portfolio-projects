from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import TABLES_DIR, ensure_project_dirs


def save_table(df: pd.DataFrame, filename: str, index: bool = False) -> Path:
    """Saving important tables to reports/tables for report writing."""
    ensure_project_dirs()
    path = TABLES_DIR / filename
    df.to_csv(path, index=index)
    return path


def markdown_summary_table(df: pd.DataFrame, max_rows: int = 10) -> str:
    """Creating a compact markdown version of a table for README/report drafting."""
    return df.head(max_rows).to_markdown(index=False)
