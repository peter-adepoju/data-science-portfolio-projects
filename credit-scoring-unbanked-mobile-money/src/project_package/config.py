from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Returning the repository root from the installed or local source tree."""
    return Path(__file__).resolve().parents[2]


ROOT = get_project_root()
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"
MODELS_DIR = ROOT / "models"

TARGET = "default_next_month"
RANDOM_STATE = 42


def ensure_project_dirs() -> None:
    """Creating the expected output directories before saving artifacts."""
    for path in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR, EXTERNAL_DIR, FIGURES_DIR, TABLES_DIR, MODELS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
