from __future__ import annotations

import pytest

from quantlab.data.trust import (
    DataTrustAssessment,
    DataTrustState,
    assess_data_trust,
    require_data_trust,
)


def test_trust_states_are_machine_readable() -> None:
    assert DataTrustState.TRUSTED.value == "trusted"
    assert (
        DataTrustState.CONDITIONALLY_TRUSTED.value
        == "conditionally_trusted"
    )
    assert DataTrustState.DEGRADED.value == "degraded"
    assert DataTrustState.QUESTIONABLE.value == "questionable"
    assert DataTrustState.UNRESOLVED.value == "unresolved"


def test_trusted_valid_data_produces_trusted_assessment() -> None:
    assessment = assess_data_trust(
        capability="research",
        validation_passed=True,
        source_quality=DataTrustState.TRUSTED,
        reasons=["Source verified"],
        evidence=["source-check-001"],
    )

    assert isinstance(assessment, DataTrustAssessment)
    assert assessment.state is DataTrustState.TRUSTED
    assert assessment.capability == "research"
    assert assessment.suitable is True
    assert assessment.reasons == ("Source verified",)
    assert assessment.evidence == ("source-check-001",)


def test_failed_validation_can_never_become_trusted() -> None:
    assessment = assess_data_trust(
        capability="backtest",
        validation_passed=False,
        source_quality=DataTrustState.TRUSTED,
    )

    assert assessment.state is DataTrustState.UNRESOLVED
    assert assessment.suitable is False
    assert "Canonical data validation did not pass" in assessment.reasons


def test_unresolved_source_quality_remains_unresolved() -> None:
    assessment = assess_data_trust(
        capability="research",
        validation_passed=True,
        source_quality=DataTrustState.UNRESOLVED,
        reasons=["Gold source-quality investigation unresolved"],
        evidence=["gold-source-review-pending"],
    )

    assert assessment.state is DataTrustState.UNRESOLVED
    assert assessment.suitable is False
    assert (
        "Gold source-quality investigation unresolved"
        in assessment.reasons
    )
    assert "gold-source-review-pending" in assessment.evidence


def test_questionable_data_is_not_suitable() -> None:
    assessment = assess_data_trust(
        capability="risk",
        validation_passed=True,
        source_quality=DataTrustState.QUESTIONABLE,
    )

    assert assessment.state is DataTrustState.QUESTIONABLE
    assert assessment.suitable is False


def test_conditional_trust_can_be_suitable() -> None:
    assessment = assess_data_trust(
        capability="research",
        validation_passed=True,
        source_quality=DataTrustState.CONDITIONALLY_TRUSTED,
    )

    assert assessment.state is DataTrustState.CONDITIONALLY_TRUSTED
    assert assessment.suitable is True


def test_capability_specific_gate_accepts_allowed_state() -> None:
    assessment = assess_data_trust(
        capability="research",
        validation_passed=True,
        source_quality=DataTrustState.TRUSTED,
    )

    result = require_data_trust(
        assessment,
        allowed_states={
            DataTrustState.TRUSTED,
            DataTrustState.CONDITIONALLY_TRUSTED,
        },
    )

    assert result == assessment


def test_capability_specific_gate_rejects_unresolved_state() -> None:
    assessment = assess_data_trust(
        capability="backtest",
        validation_passed=True,
        source_quality=DataTrustState.UNRESOLVED,
    )

    with pytest.raises(ValueError, match="Data Trust requirement failed"):
        require_data_trust(
            assessment,
            allowed_states={DataTrustState.TRUSTED},
        )


def test_capability_specific_gate_rejects_unsuitable_data() -> None:
    assessment = assess_data_trust(
        capability="risk",
        validation_passed=True,
        source_quality=DataTrustState.QUESTIONABLE,
    )

    with pytest.raises(ValueError, match="Data Trust requirement failed"):
        require_data_trust(
            assessment,
            allowed_states={
                DataTrustState.QUESTIONABLE,
                DataTrustState.UNRESOLVED,
            },
        )


def test_assessment_is_immutable() -> None:
    assessment = assess_data_trust(
        capability="research",
        validation_passed=True,
    )

    with pytest.raises(AttributeError):
        assessment.state = DataTrustState.UNRESOLVED  # type: ignore[misc]


def test_empty_capability_is_rejected() -> None:
    with pytest.raises(ValueError, match="Capability must not be empty"):
        assess_data_trust(
            capability=" ",
            validation_passed=True,
        )


def test_execution_authority_is_not_part_of_the_contract() -> None:
    assessment = assess_data_trust(
        capability="trading",
        validation_passed=True,
        source_quality=DataTrustState.TRUSTED,
    )

    assert not hasattr(assessment, "execution_authorized")
    assert not hasattr(assessment, "authorization")
    assert not hasattr(assessment, "execute")
