"""
nigeria_dfs_analysis — source package
======================================
Helper utilities for the Nigeria Digital Financial Services Market Analysis.

These modules are imported inside notebooks to keep notebook cells clean
and to avoid repeating the same boilerplate code across notebooks.

Modules
-------
config      : Load and validate the project configuration (configs/config.yaml).
paths       : Resolve all project file paths from the config.
data_loader : Download and cache real public datasets (World Bank, CBN).
preprocessing : Clean and transform raw data into analysis-ready form.
market_sizing : TAM / SAM / SOM calculations.
financial_model : 3-year revenue projection and sensitivity analysis.
risk_model  : Risk matrix scoring and visualisation helpers.
stats       : Statistical helper functions (bootstrap, permutation tests).
viz         : Publication-quality figure saving and style helpers.
"""
