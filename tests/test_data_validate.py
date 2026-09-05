from __future__ import annotations

import pandas as pd
import pytest

from quantlab.data.trust import DataTrustState
from quantlab.data.validate import (
    assess_dataset_trust,
    validate_dataset,
    validate_datasets,
)


def make_valid_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "Symbol": ["AAPL", "AAPL", "AAPL"],
            "Open": [100.0, 102.0, 104.0],
            "High": [101.0, 103.0, 105.0],
            "Low": [99.0, 101.0, 103.0],
            "Close": [100.5, 102.5, 104.5],
            "Volume": [1000.0, 1100.0, 1200.0],
        }
    )


def assert_invalid(
    dataset: pd.DataFrame,
    expected_issue: str,
) -> None:
    result = validate_dataset(dataset)

    assert result["is_valid"] is False
    assert expected_issue in result["issues"]


def test_valid_dataset_passes_canonical_contract() -> None:
    result = validate_dataset(make_valid_dataset())

    assert result["is_valid"] is True
    assert result["issues"] == []


def test_non_dataframe_is_rejected() -> None:
    result = validate_dataset([1, 2, 3])

    assert result["is_valid"] is False
    assert "Dataset must be a pandas DataFrame" in result["issues"]


def test_empty_dataset_is_rejected() -> None:
    result = validate_dataset(pd.DataFrame())

    assert result["is_valid"] is False
    assert "Dataset is empty" in result["issues"]


@pytest.mark.parametrize(
    "column",
    [
        "Date",
        "Symbol",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ],
)
def test_missing_required_column_is_rejected(column: str) -> None:
    dataset = make_valid_dataset().drop(columns=[column])

    result = validate_dataset(dataset)

    assert result["is_valid"] is False
    assert f"Missing required columns: ['{column}']" in result["issues"]


def test_date_must_be_datetime() -> None:
    dataset = make_valid_dataset()
    dataset["Date"] = dataset["Date"].astype(str)

    assert_invalid(
        dataset,
        "Date column must have a datetime dtype",
    )


def test_date_missing_values_are_rejected() -> None:
    dataset = make_valid_dataset()
    dataset.loc[1, "Date"] = pd.NaT

    assert_invalid(
        dataset,
        "Date column contains missing values",
    )


def test_dates_must_be_sorted_ascending() -> None:
    dataset = make_valid_dataset()
    dataset = dataset.iloc[[1, 0, 2]].reset_index(drop=True)

    assert_invalid(
        dataset,
        "Date column must be sorted ascending",
    )


def test_missing_symbol_is_rejected() -> None:
    dataset = make_valid_dataset()
    dataset.loc[1, "Symbol"] = None

    assert_invalid(
        dataset,
        "Symbol column contains missing values",
    )


def test_empty_symbol_is_rejected() -> None:
    dataset = make_valid_dataset()
    dataset.loc[1, "Symbol"] = "   "

    assert_invalid(
        dataset,
        "Symbol column contains empty values",
    )


@pytest.mark.parametrize(
    "column",
    ["Open", "High", "Low", "Close", "Volume"],
)
def test_market_numeric_columns_must_be_numeric(column: str) -> None:
    dataset = make_valid_dataset()
    dataset[column] = "invalid"

    assert_invalid(
        dataset,
        f"{column} column must be numeric",
    )


@pytest.mark.parametrize(
    "column",
    ["Open", "High", "Low", "Close", "Volume"],
)
def test_market_numeric_columns_must_be_finite(column: str) -> None:
    dataset = make_valid_dataset()
    dataset.loc[1, column] = float("inf")

    assert_invalid(
        dataset,
        f"{column} column must contain only finite values",
    )


@pytest.mark.parametrize(
    "column",
    ["Open", "High", "Low", "Close"],
)
def test_prices_must_be_positive(column: str) -> None:
    dataset = make_valid_dataset()
    dataset.loc[1, column] = 0.0

    assert_invalid(
        dataset,
        f"{column} column must contain only positive values",
    )


def test_volume_must_be_non_negative() -> None:
    dataset = make_valid_dataset()
    dataset.loc[1, "Volume"] = -1.0

    assert_invalid(
        dataset,
        "Volume column must contain only non-negative values",
    )


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("High", 99.0),
        ("High", 100.0),
        ("High", 98.0),
    ],
)
def test_high_must_not_be_below_open(column: str, value: float) -> None:
    dataset = make_valid_dataset()
    dataset.loc[0, column] = value

    if value < dataset.loc[0, "Open"]:
        assert_invalid(
            dataset,
            "High column must be greater than or equal to Open",
        )


def test_high_must_not_be_below_close() -> None:
    dataset = make_valid_dataset()
    dataset.loc[0, "High"] = 100.0
    dataset.loc[0, "Close"] = 101.0

    assert_invalid(
        dataset,
        "High column must be greater than or equal to Close",
    )


def test_high_must_not_be_below_low() -> None:
    dataset = make_valid_dataset()
    dataset.loc[0, "High"] = 98.0

    assert_invalid(
        dataset,
        "High column must be greater than or equal to Low",
    )


def test_low_must_not_be_above_open() -> None:
    dataset = make_valid_dataset()
    dataset.loc[0, "Low"] = 101.0

    assert_invalid(
        dataset,
        "Low column must be less than or equal to Open",
    )


def test_low_must_not_be_above_close() -> None:
    dataset = make_valid_dataset()
    dataset.loc[0, "Low"] = 101.0

    assert_invalid(
        dataset,
        "Low column must be less than or equal to Close",
    )


def test_duplicate_date_symbol_pairs_are_rejected() -> None:
    dataset = make_valid_dataset()
    duplicate = dataset.iloc[[0]].copy()

    dataset = pd.concat(
        [dataset, duplicate],
        ignore_index=True,
    )

    assert_invalid(
        dataset,
        "Dataset must not contain duplicate Date and Symbol pairs",
    )


def test_validate_dataset_does_not_mutate_input() -> None:
    dataset = make_valid_dataset()
    original = dataset.copy(deep=True)

    validate_dataset(dataset)

    pd.testing.assert_frame_equal(
        dataset,
        original,
    )


def test_validate_datasets_validates_each_dataset() -> None:
    valid = make_valid_dataset()

    invalid = valid.copy()
    invalid.loc[0, "Close"] = -1.0

    results = validate_datasets(
        {
            "valid": valid,
            "invalid": invalid,
        }
    )

    assert results["valid"]["is_valid"] is True
    assert results["invalid"]["is_valid"] is False
    assert (
        "Close column must contain only positive values"
        in results["invalid"]["issues"]
    )

def test_ohlc_validation_tolerates_floating_point_rounding_noise() -> None:
    dataset = make_valid_dataset()

    # Create OHLC boundaries that differ only by microscopic
    # floating-point representation noise.
    dataset.loc[0, "Open"] = 100.0
    dataset.loc[0, "High"] = 100.0
    dataset.loc[0, "Low"] = 100.0
    dataset.loc[0, "Close"] = 100.0 + 1e-16

    dataset.loc[1, "Open"] = 102.5
    dataset.loc[1, "High"] = 102.5 - 1e-16
    dataset.loc[1, "Low"] = 102.5
    dataset.loc[1, "Close"] = 102.5

    result = validate_dataset(dataset)

    assert result["is_valid"] is True
    assert result["issues"] == []


def test_ohlc_validation_rejects_meaningful_price_inconsistency() -> None:
    dataset = make_valid_dataset()

    dataset.loc[0, "High"] = dataset.loc[0, "Close"] - 1.0

    result = validate_dataset(dataset)

    assert result["is_valid"] is False
    assert (
        "High column must be greater than or equal to Close"
        in result["issues"]
    )

# ---------------------------------------------------------------------------
# S1.1-B Data Trust integration tests
# ---------------------------------------------------------------------------

def test_assess_dataset_trust_returns_trusted_for_valid_trusted_data() -> None:
    dataset = make_valid_dataset()

    assessment = assess_dataset_trust(
        dataset,
        capability="research",
        source_quality=DataTrustState.TRUSTED,
    )

    assert assessment.state is DataTrustState.TRUSTED
    assert assessment.suitable is True
    assert assessment.capability == "research"


def test_assess_dataset_trust_rejects_invalid_dataset_even_when_source_is_trusted() -> None:
    dataset = make_valid_dataset().drop(columns=["Close"])

    assessment = assess_dataset_trust(
        dataset,
        capability="research",
        source_quality=DataTrustState.TRUSTED,
    )

    assert assessment.state is DataTrustState.UNRESOLVED
    assert assessment.suitable is False
    assert "Missing required columns: ['Close']" in assessment.reasons
    assert "Canonical data validation did not pass" in assessment.reasons


def test_assess_dataset_trust_preserves_unresolved_source_quality() -> None:
    dataset = make_valid_dataset()

    assessment = assess_dataset_trust(
        dataset,
        capability="research",
        source_quality=DataTrustState.UNRESOLVED,
        evidence=["gold-source-review-pending"],
    )

    assert assessment.state is DataTrustState.UNRESOLVED
    assert assessment.suitable is False
    assert "gold-source-review-pending" in assessment.evidence


def test_assess_dataset_trust_preserves_questionable_source_quality() -> None:
    dataset = make_valid_dataset()

    assessment = assess_dataset_trust(
        dataset,
        capability="risk",
        source_quality=DataTrustState.QUESTIONABLE,
    )

    assert assessment.state is DataTrustState.QUESTIONABLE
    assert assessment.suitable is False


def test_assess_dataset_trust_allows_conditionally_trusted_data() -> None:
    dataset = make_valid_dataset()

    assessment = assess_dataset_trust(
        dataset,
        capability="research",
        source_quality=DataTrustState.CONDITIONALLY_TRUSTED,
    )

    assert assessment.state is DataTrustState.CONDITIONALLY_TRUSTED
    assert assessment.suitable is True


def test_assess_dataset_trust_preserves_evidence() -> None:
    dataset = make_valid_dataset()

    assessment = assess_dataset_trust(
        dataset,
        capability="research",
        evidence=["source-check-001", "provenance-check-002"],
    )

    assert assessment.evidence == (
        "source-check-001",
        "provenance-check-002",
    )


def test_assess_dataset_trust_preserves_capability() -> None:
    dataset = make_valid_dataset()

    assessment = assess_dataset_trust(
        dataset,
        capability="risk",
    )

    assert assessment.capability == "risk"


def test_assess_dataset_trust_does_not_change_validate_dataset_contract() -> None:
    dataset = make_valid_dataset()

    original_result = validate_dataset(dataset)

    assess_dataset_trust(
        dataset,
        capability="research",
    )

    result_after = validate_dataset(dataset)

    assert result_after == original_result
    assert result_after == {
        "is_valid": True,
        "issues": [],
    }


def test_assess_dataset_trust_preserves_validation_issues() -> None:
    dataset = make_valid_dataset()
    dataset.loc[0, "High"] = 90.0

    assessment = assess_dataset_trust(
        dataset,
        capability="backtest",
    )

    assert assessment.state is DataTrustState.UNRESOLVED
    assert assessment.suitable is False
    assert (
        "High column must be greater than or equal to Open"
        in assessment.reasons
    )


def test_assess_dataset_trust_does_not_grant_execution_authority() -> None:
    dataset = make_valid_dataset()

    assessment = assess_dataset_trust(
        dataset,
        capability="trading",
        source_quality=DataTrustState.TRUSTED,
    )

    assert not hasattr(assessment, "execution_authorized")
    assert not hasattr(assessment, "authorization")
    assert not hasattr(assessment, "execute")

