from __future__ import annotations

import pandas as pd
import pytest

from quantlab.data import boundary
from quantlab.data.trust import DataTrustAssessment, DataTrustState


def test_load_validated_dataset_composes_load_normalize_and_trust(
    monkeypatch,
) -> None:
    raw = pd.DataFrame({"raw": [1, 2]})
    normalized = pd.DataFrame({"normalized": [1, 2]})
    expected_assessment = DataTrustAssessment(
        state=DataTrustState.TRUSTED,
        capability="research",
        suitable=True,
        evidence=("data/BTC_history.csv",),
    )

    calls: list[tuple[str, object]] = []

    def fake_load(path):
        calls.append(("load", path))
        return raw

    def fake_normalize(name, dataset):
        calls.append(("normalize", (name, dataset)))
        return normalized

    def fake_assess(dataset, *, capability, source_quality, evidence):
        calls.append(
            (
                "trust",
                (dataset, capability, source_quality, evidence),
            )
        )
        return expected_assessment

    monkeypatch.setattr(boundary, "load_dataset", fake_load)
    monkeypatch.setattr(boundary, "normalize_dataset", fake_normalize)
    monkeypatch.setattr(boundary, "assess_dataset_trust", fake_assess)

    result_dataset, result_assessment = boundary.load_validated_dataset(
        "data/BTC_history.csv",
        capability="research",
    )

    assert result_dataset is normalized
    assert result_assessment is expected_assessment

    assert calls[0] == ("load", boundary.Path("data/BTC_history.csv"))
    assert calls[1] == ("normalize", ("BTC_history", raw))
    assert calls[2] == (
        "trust",
        (
            normalized,
            "research",
            DataTrustState.TRUSTED,
            (str(boundary.Path("data/BTC_history.csv")),),
        ),
    )


def test_load_validated_dataset_passes_capability_to_trust(
    monkeypatch,
) -> None:
    captured = {}

    monkeypatch.setattr(
        boundary,
        "load_dataset",
        lambda path: pd.DataFrame({"raw": [1]}),
    )
    monkeypatch.setattr(
        boundary,
        "normalize_dataset",
        lambda name, dataset: pd.DataFrame({"normalized": [1]}),
    )

    def fake_assess(dataset, *, capability, source_quality, evidence):
        captured["capability"] = capability
        return DataTrustAssessment(
            state=DataTrustState.TRUSTED,
            capability=capability,
            suitable=True,
            evidence=evidence,
        )

    monkeypatch.setattr(boundary, "assess_dataset_trust", fake_assess)

    _, assessment = boundary.load_validated_dataset(
        "data/BTC_history.csv",
        capability="risk",
    )

    assert captured["capability"] == "risk"
    assert assessment.capability == "risk"


def test_load_validated_dataset_passes_source_quality_to_trust(
    monkeypatch,
) -> None:
    captured = {}

    monkeypatch.setattr(
        boundary,
        "load_dataset",
        lambda path: pd.DataFrame({"raw": [1]}),
    )
    monkeypatch.setattr(
        boundary,
        "normalize_dataset",
        lambda name, dataset: pd.DataFrame({"normalized": [1]}),
    )

    def fake_assess(dataset, *, capability, source_quality, evidence):
        captured["source_quality"] = source_quality
        return DataTrustAssessment(
            state=source_quality,
            capability=capability,
            suitable=source_quality
            in {
                DataTrustState.TRUSTED,
                DataTrustState.CONDITIONALLY_TRUSTED,
            },
            evidence=evidence,
        )

    monkeypatch.setattr(boundary, "assess_dataset_trust", fake_assess)

    _, assessment = boundary.load_validated_dataset(
        "data/BTC_history.csv",
        capability="research",
        source_quality=DataTrustState.CONDITIONALLY_TRUSTED,
    )

    assert (
        captured["source_quality"]
        is DataTrustState.CONDITIONALLY_TRUSTED
    )
    assert assessment.state is DataTrustState.CONDITIONALLY_TRUSTED


def test_load_validated_dataset_propagates_loading_failure(
    monkeypatch,
) -> None:
    error = OSError("dataset could not be loaded")

    def fake_load(path):
        raise error

    monkeypatch.setattr(boundary, "load_dataset", fake_load)

    with pytest.raises(OSError, match="dataset could not be loaded"):
        boundary.load_validated_dataset(
            "data/BTC_history.csv",
            capability="research",
        )
