import pandas as pd

from project_package.config import TARGET
from project_package.validation import validate_binary_target, validate_required_columns


def test_validate_binary_target_passes_for_binary_values():
    df = pd.DataFrame({TARGET: [0, 1, 0, 1]})
    result = validate_binary_target(df)
    assert result.passed


def test_validate_binary_target_fails_for_nonbinary_values():
    df = pd.DataFrame({TARGET: [0, 1, 2]})
    result = validate_binary_target(df)
    assert not result.passed


def test_validate_required_columns_reports_missing_columns():
    df = pd.DataFrame({TARGET: [0, 1]})
    result = validate_required_columns(df, required=[TARGET, "credit_limit"])
    assert not result.passed
    assert "credit_limit" in result.errors[0]
