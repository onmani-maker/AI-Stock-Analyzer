"""Shared project utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"


def ensure_project_directories() -> None:
    """Create expected local data and report directories if they are missing."""
    for path in (DATA_DIR / "stocks", DATA_DIR / "options", REPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def save_dataframe(data: pd.DataFrame, path: Path) -> None:
    """Save a DataFrame to CSV, creating parent directories first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=True)


def format_percentage(value: float) -> str:
    """Format a decimal value as a percentage string."""
    return f"{value:.2%}"
