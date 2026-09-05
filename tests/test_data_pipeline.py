from __future__ import annotations

from pathlib import Path

import pandas as pd

from quantlab.data.loading import load_all_datasets, list_raw_datasets
from quantlab.data.normalize import normalize_all_datasets
from quantlab.data.validate import validate_datasets


def test_list_raw_datasets_returns_supported_files():
    datasets = list_raw_datasets()
    names = [path.name for path in datasets]
    assert len(names) == 5
    assert "AAPL_history.csv" in names
    assert "BTC_history.csv" in names


def test_load_all_datasets_returns_frames():
    datasets = load_all_datasets()
    assert isinstance(datasets, dict)
    assert "AAPL_history" in datasets
    assert "BTC_history" in datasets


def test_normalize_all_datasets_returns_common_schema():
    raw = load_all_datasets()
    normalized = normalize_all_datasets(raw)

    for df in normalized.values():
        assert {"Date", "Symbol", "Open", "High", "Low", "Close", "Volume"}.issubset(df.columns)


def test_validate_datasets_detects_invalid_inputs():
    invalid_df = pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-01"],
            "Symbol": ["TEST", "TEST"],
            "Open": [10.0, -1.0],
            "High": [11.0, 12.0],
            "Low": [9.0, 8.0],
            "Close": [10.5, 11.5],
            "Volume": [100, 200],
        }
    )
    result = validate_datasets({"test": invalid_df})
    assert result["test"]["is_valid"] is False
    assert result["test"]["issues"]
