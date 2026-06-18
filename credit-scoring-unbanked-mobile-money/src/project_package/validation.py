from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from .config import TARGET


@dataclass
class ValidationResult:
    passed: bool
    errors: list[str]
    warnings: list[str]


REQUIRED_BASE_COLUMNS = {
    "credit_limit", "sex", "education", "marriage", "age",
    "pay_status_sep", "pay_status_aug", "pay_status_jul", "pay_status_jun", "pay_status_may", "pay_status_apr",
    "bill_amt_sep", "bill_amt_aug", "bill_amt_jul", "bill_amt_jun", "bill_amt_may", "bill_amt_apr",
    "pay_amt_sep", "pay_amt_aug", "pay_amt_jul", "pay_amt_jun", "pay_amt_may", "pay_amt_apr",
    TARGET,
}


def validate_required_columns(df: pd.DataFrame, required: Iterable[str] = REQUIRED_BASE_COLUMNS) -> ValidationResult:
    """Checking whether the expected modeling columns had been created."""
    required = set(required)
    missing = sorted(required - set(df.columns))
    errors = [f"Missing required column: {col}" for col in missing]
    return ValidationResult(passed=len(errors) == 0, errors=errors, warnings=[])


def validate_binary_target(df: pd.DataFrame, target: str = TARGET) -> ValidationResult:
    """Validating that the default target was binary and non-missing."""
    errors: list[str] = []
    warnings: list[str] = []
    if target not in df.columns:
        errors.append(f"Target column {target!r} was missing.")
        return ValidationResult(False, errors, warnings)
    if df[target].isna().any():
        errors.append(f"Target column {target!r} contained missing values.")
    unique_values = set(pd.Series(df[target]).dropna().unique().tolist())
    if not unique_values.issubset({0, 1}):
        errors.append(f"Target column {target!r} was not binary: {sorted(unique_values)}")
    positive_rate = float(df[target].mean()) if len(df) else 0.0
    if positive_rate < 0.05 or positive_rate > 0.95:
        warnings.append(f"Target prevalence was extreme: {positive_rate:.3f}")
    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_no_duplicate_rows(df: pd.DataFrame) -> ValidationResult:
    """Checking duplicated full records after cleaning."""
    duplicates = int(df.duplicated().sum())
    warnings = []
    if duplicates:
        warnings.append(f"Found {duplicates} duplicated rows.")
    return ValidationResult(True, [], warnings)


def run_base_validations(df: pd.DataFrame) -> dict[str, ValidationResult]:
    """Running all base dataset validations and returning reportable results."""
    return {
        "required_columns": validate_required_columns(df),
        "binary_target": validate_binary_target(df),
        "duplicate_rows": validate_no_duplicate_rows(df),
    }


def validations_to_frame(results: dict[str, ValidationResult]) -> pd.DataFrame:
    """Converting validation outputs into a table saved by notebooks."""
    rows = []
    for name, result in results.items():
        rows.append({
            "check": name,
            "passed": result.passed,
            "errors": " | ".join(result.errors),
            "warnings": " | ".join(result.warnings),
        })
    return pd.DataFrame(rows)
