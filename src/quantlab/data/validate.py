from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

from .trust import (
    DataTrustAssessment,
    DataTrustState,
    assess_data_trust,
)



REQUIRED_COLUMNS = [
    "Date",
    "Symbol",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]

PRICE_COLUMNS = ["Open", "High", "Low", "Close"]

KEY_COLUMNS = ["Date", "Symbol"]

# OHLC comparisons must tolerate microscopic floating-point representation
# noise while continuing to reject economically meaningful inconsistencies.
OHLC_COMPARISON_RTOL = 1e-12
OHLC_COMPARISON_ATOL = 1e-12


def _less_than(left: pd.Series, right: pd.Series) -> pd.Series:
    """Return left < right while tolerating floating-point rounding noise."""
    return ~np.isclose(
        left.astype(float),
        right.astype(float),
        rtol=OHLC_COMPARISON_RTOL,
        atol=OHLC_COMPARISON_ATOL,
    ) & (left.astype(float) < right.astype(float))


def _greater_than(left: pd.Series, right: pd.Series) -> pd.Series:
    """Return left > right while tolerating floating-point rounding noise."""
    return ~np.isclose(
        left.astype(float),
        right.astype(float),
        rtol=OHLC_COMPARISON_RTOL,
        atol=OHLC_COMPARISON_ATOL,
    ) & (left.astype(float) > right.astype(float))


def validate_dataset(df: pd.DataFrame) -> Dict[str, object]:
    """
    Validate the canonical QuantLab market-data contract.

    This function is intentionally non-mutating. It reports all detected
    contract violations so callers can reject untrusted market data before
    it reaches strategies, backtests, or portfolio calculations.
    """

    issues: List[str] = []

    if not isinstance(df, pd.DataFrame):
        return {
            "is_valid": False,
            "issues": ["Dataset must be a pandas DataFrame"],
        }

    if df.empty:
        issues.append("Dataset is empty")
        return {
            "is_valid": False,
            "issues": issues,
        }

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        issues.append(
            f"Missing required columns: {missing_columns}"
        )

    if missing_columns:
        return {
            "is_valid": False,
            "issues": issues,
        }

    # ------------------------------------------------------------------
    # Date contract
    # ------------------------------------------------------------------

    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        issues.append(
            "Date column must have a datetime dtype"
        )
    else:
        if df["Date"].isna().any():
            issues.append(
                "Date column contains missing values"
            )

        if not df["Date"].is_monotonic_increasing:
            issues.append(
                "Date column must be sorted ascending"
            )

    # ------------------------------------------------------------------
    # Symbol contract
    # ------------------------------------------------------------------

    if df["Symbol"].isna().any():
        issues.append(
            "Symbol column contains missing values"
        )

    if (
        df["Symbol"].astype(str).str.strip() == ""
    ).any():
        issues.append(
            "Symbol column contains empty values"
        )

    # ------------------------------------------------------------------
    # Numeric contract
    # ------------------------------------------------------------------

    for column in PRICE_COLUMNS + ["Volume"]:
        if not pd.api.types.is_numeric_dtype(df[column]):
            issues.append(
                f"{column} column must be numeric"
            )
            continue

        values = df[column].astype(float)

        if not np.isfinite(values.to_numpy()).all():
            issues.append(
                f"{column} column must contain only finite values"
            )

    # ------------------------------------------------------------------
    # Price domain contract
    # ------------------------------------------------------------------

    for column in PRICE_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[column]):
            continue

        values = df[column].astype(float)

        if (values <= 0).any():
            issues.append(
                f"{column} column must contain only positive values"
            )

    # ------------------------------------------------------------------
    # Volume domain contract
    # ------------------------------------------------------------------

    if pd.api.types.is_numeric_dtype(df["Volume"]):
        volume = df["Volume"].astype(float)

        if (volume < 0).any():
            issues.append(
                "Volume column must contain only non-negative values"
            )

    # ------------------------------------------------------------------
    # OHLC consistency contract
    # ------------------------------------------------------------------

    if all(
        pd.api.types.is_numeric_dtype(df[column])
        for column in PRICE_COLUMNS
    ):
        open_values = df["Open"].astype(float)
        high_values = df["High"].astype(float)
        low_values = df["Low"].astype(float)
        close_values = df["Close"].astype(float)

        if _less_than(high_values, open_values).any():
            issues.append(
                "High column must be greater than or equal to Open"
            )

        if _less_than(high_values, close_values).any():
            issues.append(
                "High column must be greater than or equal to Close"
            )

        if _less_than(high_values, low_values).any():
            issues.append(
                "High column must be greater than or equal to Low"
            )

        if _greater_than(low_values, open_values).any():
            issues.append(
                "Low column must be less than or equal to Open"
            )

        if _greater_than(low_values, close_values).any():
            issues.append(
                "Low column must be less than or equal to Close"
            )

    # ------------------------------------------------------------------
    # Identity / uniqueness contract
    # ------------------------------------------------------------------

    if df.duplicated(KEY_COLUMNS).any():
        issues.append(
            "Dataset must not contain duplicate Date and Symbol pairs"
        )

    return {
        "is_valid": not issues,
        "issues": issues,
    }


def validate_datasets(
    datasets: Dict[str, pd.DataFrame],
) -> Dict[str, Dict[str, object]]:
    """
    Validate multiple datasets using the canonical market-data contract.
    """

    return {
        name: validate_dataset(df)
        for name, df in datasets.items()
    }

def assess_dataset_trust(
    df: pd.DataFrame,
    *,
    capability: str,
    source_quality: DataTrustState = DataTrustState.TRUSTED,
    evidence: Iterable[str] = (),
) -> DataTrustAssessment:
    """
    Compose canonical dataset validation with the Data Trust boundary.

    This function does not change the behavior or return contract of
    validate_dataset(). It converts the canonical validation result into
    a machine-readable DataTrustAssessment for a specific capability.
    """

    validation_result = validate_dataset(df)

    validation_passed = bool(validation_result["is_valid"])
    validation_issues = tuple(
        str(issue)
        for issue in validation_result["issues"]
    )

    return assess_data_trust(
        capability=capability,
        validation_passed=validation_passed,
        source_quality=source_quality,
        reasons=validation_issues,
        evidence=evidence,
    )

