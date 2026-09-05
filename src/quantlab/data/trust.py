from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class DataTrustState(str, Enum):
    """Machine-readable trust states for QuantLab data."""

    TRUSTED = "trusted"
    CONDITIONALLY_TRUSTED = "conditionally_trusted"
    DEGRADED = "degraded"
    QUESTIONABLE = "questionable"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class DataTrustAssessment:
    """Immutable assessment of data trust for a specific capability."""

    state: DataTrustState
    capability: str
    suitable: bool
    reasons: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.capability.strip():
            raise ValueError("Capability must not be empty")


def assess_data_trust(
    *,
    capability: str,
    validation_passed: bool,
    source_quality: DataTrustState = DataTrustState.TRUSTED,
    reasons: Iterable[str] = (),
    evidence: Iterable[str] = (),
) -> DataTrustAssessment:
    """
    Assess Data Trust independently from raw dataset validation.

    Validation failure can never produce a trusted assessment.
    Source-quality uncertainty remains explicitly represented.
    Capability suitability is evaluated separately from the trust state.
    """

    if not capability.strip():
        raise ValueError("Capability must not be empty")

    reasons_tuple = tuple(str(reason) for reason in reasons)
    evidence_tuple = tuple(str(item) for item in evidence)

    if not validation_passed:
        state = DataTrustState.UNRESOLVED
        final_reasons = (
            *reasons_tuple,
            "Canonical data validation did not pass",
        )
        return DataTrustAssessment(
            state=state,
            capability=capability,
            suitable=False,
            reasons=final_reasons,
            evidence=evidence_tuple,
        )

    state = DataTrustState(source_quality)

    # Trust state alone does not imply capability suitability.
    suitable = state in {
        DataTrustState.TRUSTED,
        DataTrustState.CONDITIONALLY_TRUSTED,
    }

    if state in {
        DataTrustState.QUESTIONABLE,
        DataTrustState.UNRESOLVED,
    }:
        suitable = False

    return DataTrustAssessment(
        state=state,
        capability=capability,
        suitable=suitable,
        reasons=reasons_tuple,
        evidence=evidence_tuple,
    )


def require_data_trust(
    assessment: DataTrustAssessment,
    *,
    allowed_states: Iterable[DataTrustState],
) -> DataTrustAssessment:
    """
    Enforce a capability-specific Data Trust gate.

    This function only evaluates data suitability. It never grants,
    implies, or represents execution authority.
    """

    allowed = frozenset(
        DataTrustState(state)
        for state in allowed_states
    )

    if assessment.state not in allowed:
        raise ValueError(
            "Data Trust requirement failed: "
            f"state '{assessment.state.value}' is not permitted "
            f"for capability '{assessment.capability}'"
        )

    if not assessment.suitable:
        raise ValueError(
            "Data Trust requirement failed: "
            f"data is not suitable for capability "
            f"'{assessment.capability}'"
        )

    return assessment
