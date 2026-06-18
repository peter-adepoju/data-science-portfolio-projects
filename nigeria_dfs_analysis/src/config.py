"""
src/config.py
=============
Load and validate the project configuration from configs/config.yaml.

What it does
------------
- Finds the project root by locating the Makefile.
- Loads configs/config.yaml as a plain Python dict.
- Provides a helper to resolve any relative path from the config to an
  absolute Path object.
- Exposes the random seed and indicator codebook for notebooks.

What inputs it expects
----------------------
- configs/config.yaml must exist at the project root.

What it returns
---------------
- cfg : dict  — the full configuration dictionary.
- get_path(key) : Path — absolute path for any path key in cfg["paths"].
- INDICATORS : dict — World Bank indicator codes keyed by friendly name.

Why this is useful
------------------
Every notebook can do `from src.config import cfg, get_path, INDICATORS`
to access configuration without repeating YAML loading logic.
"""

import os
from pathlib import Path
from typing import Optional

import yaml


# ── Locate the project root ───────────────────────────────────────────────────
def _find_project_root(start: Path) -> Path:
    """Walk up the directory tree until we find the Makefile."""
    for parent in [start] + list(start.parents):
        if (parent / "Makefile").exists():
            return parent
    # Fallback: assume we are already at the root
    return start


PROJECT_ROOT: Path = _find_project_root(Path(__file__).resolve().parent)


# ── Load configuration ────────────────────────────────────────────────────────
def load_config(config_path: Optional[Path] = None) -> dict:
    """
    Load the project config YAML.

    Parameters
    ----------
    config_path : Path, optional
        Custom path to a YAML config file.  Defaults to
        PROJECT_ROOT / configs / config.yaml.

    Returns
    -------
    dict
        Parsed configuration as a nested dict.
    """
    if config_path is None:
        config_path = PROJECT_ROOT / "configs" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}. "
            "Run this from the project root or set config_path explicitly."
        )

    with open(config_path, "r") as fh:
        cfg = yaml.safe_load(fh)

    return cfg


# ── Singleton config object used across notebooks ─────────────────────────────
cfg: dict = load_config()


# ── Path resolver ─────────────────────────────────────────────────────────────
def get_path(key: str) -> Path:
    """
    Resolve a named path from cfg['paths'] to an absolute Path.

    Parameters
    ----------
    key : str
        Key from the paths section of config.yaml, e.g. 'data_raw',
        'reports_figures', 'models'.

    Returns
    -------
    Path
        Absolute path; the directory is created if it does not yet exist.

    Example
    -------
    >>> from src.config import get_path
    >>> raw = get_path("data_raw")   # → /absolute/path/to/data/raw
    """
    relative = cfg["paths"][key]
    absolute = PROJECT_ROOT / relative
    absolute.mkdir(parents=True, exist_ok=True)
    return absolute


# ── Convenience exports ───────────────────────────────────────────────────────
RANDOM_SEED: int = cfg.get("random_seed", 42)

# World Bank indicator codes, keyed by readable name
INDICATORS: dict[str, str] = cfg["world_bank"]["indicators"]

# Countries to include in comparative analysis
COMPARATOR_COUNTRIES: list[str] = cfg["world_bank"]["comparators"]

# Date range for World Bank pulls
DATE_RANGE: tuple[int, int] = tuple(cfg["world_bank"]["date_range"])  # (start, end)

# Market sizing parameters
MARKET_PARAMS: dict = cfg["market_sizing"]

# Financial model parameters
FIN_MODEL_PARAMS: dict = cfg["financial_model"]

# Visualisation settings
VIZ_PARAMS: dict = cfg["viz"]

BRAND_COLORS: dict[str, str] = VIZ_PARAMS["brand_colors"]
