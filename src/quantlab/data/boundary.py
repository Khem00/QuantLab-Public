from __future__ import annotations

from pathlib import Path

import pandas as pd

from .loading import load_dataset
from .normalize import normalize_dataset
from .trust import DataTrustAssessment, DataTrustState
from .validate import assess_dataset_trust


def load_validated_dataset(
    path: str | Path,
    *,
    capability: str,
    source_quality: DataTrustState = DataTrustState.TRUSTED,
) -> tuple[pd.DataFrame, DataTrustAssessment]:
    """
    Load, normalize, validate, and assess trust for one dataset.

    This is the single canonical boundary for obtaining a dataset
    suitable for a named capability.

    File-loading failures remain ordinary exceptions. Dataset contract
    failures are represented through the returned DataTrustAssessment.
    """

    file_path = Path(path)

    raw = load_dataset(file_path)
    normalized = normalize_dataset(file_path.stem, raw)

    trust = assess_dataset_trust(
        normalized,
        capability=capability,
        source_quality=source_quality,
        evidence=(str(file_path),),
    )

    return normalized, trust
