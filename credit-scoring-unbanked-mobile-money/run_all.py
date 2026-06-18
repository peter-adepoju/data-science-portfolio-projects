from __future__ import annotations

import subprocess
import sys
from pathlib import Path

NOTEBOOKS = [
    "00_project_overview_and_data_strategy.ipynb",
    "01_download_and_validate_open_credit_data.ipynb",
    "02_exploratory_data_analysis.ipynb",
    "03_feature_engineering_mobile_money_proxy.ipynb",
    "04_modeling_baselines_and_xgboost.ipynb",
    "05_deep_learning_credit_risk_model.ipynb",
    "06_model_evaluation_calibration_fairness.ipynb",
    "07_inference_reporting_and_streamlit_assets.ipynb",
]


def main() -> None:
    root = Path(__file__).resolve().parent
    notebooks_dir = root / "notebooks"
    for notebook in NOTEBOOKS:
        path = notebooks_dir / notebook
        print(f"\nExecuting {path}...", flush=True)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                str(path),
            ],
            check=True,
            cwd=root,
        )
    print("\nAll notebooks were executed successfully.")


if __name__ == "__main__":
    main()
