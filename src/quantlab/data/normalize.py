from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from quantlab.config import PROCESSED_DATA_DIR, ensure_directory

REQUIRED_COLUMNS = ["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]


def _normalize_aapl(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized = normalized.rename(columns={"Price": "Date"})
    normalized["Date"] = pd.to_datetime(normalized["Date"], errors="coerce")
    normalized["Symbol"] = "AAPL"
    normalized = normalized[["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]]
    return normalized


def normalize_dataset(name: str, df: pd.DataFrame) -> pd.DataFrame:
    if name == "AAPL_history":
        return _normalize_aapl(df)

    normalized = df.copy()
    normalized["Date"] = pd.to_datetime(normalized["Date"], errors="coerce")
    normalized["Symbol"] = name.replace("_history", "").upper()
    normalized = normalized[["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]]
    return normalized


def normalize_all_datasets(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    normalized = {}
    for name, df in datasets.items():
        normalized[name] = normalize_dataset(name, df)
    return normalized


def save_processed_data(normalized_datasets: Dict[str, pd.DataFrame], output_dir: Path | None = None) -> Dict[str, Path]:
    base_dir = Path(output_dir or PROCESSED_DATA_DIR)
    ensure_directory(base_dir)
    saved_paths: Dict[str, Path] = {}
    for name, df in normalized_datasets.items():
        output_path = base_dir / f"{name}.csv"
        df.to_csv(output_path, index=False)
        saved_paths[name] = output_path
    return saved_paths
