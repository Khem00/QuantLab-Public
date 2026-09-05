from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import pandas as pd

from quantlab.config import RAW_DATA_DIR

SUPPORTED_DATASETS = [
    "AAPL_history.csv",
    "BTC_history.csv",
    "Gold_history.csv",
    "SP500_history.csv",
    "VIX_history.csv",
]


def list_raw_datasets(data_dir: Path | None = None) -> List[Path]:
    base_dir = Path(data_dir or RAW_DATA_DIR)
    if not base_dir.exists():
        raise FileNotFoundError(f"Raw data directory not found: {base_dir}")

    datasets = [base_dir / name for name in SUPPORTED_DATASETS if (base_dir / name).exists()]
    if not datasets:
        raise FileNotFoundError(f"No supported datasets found in {base_dir}")
    return datasets


def load_dataset(path: str | os.PathLike[str]) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    if file_path.name == "AAPL_history.csv":
        return pd.read_csv(file_path, skiprows=[1, 2])

    return pd.read_csv(file_path)


def load_all_datasets(data_dir: Path | None = None) -> Dict[str, pd.DataFrame]:
    datasets = {}
    for file_path in list_raw_datasets(data_dir):
        datasets[file_path.stem] = load_dataset(file_path)
    return datasets
