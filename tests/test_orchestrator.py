import asyncio
from unittest.mock import AsyncMock, patch

import anthropic
import pytest

from backend.orchestrator import OrchestratorError, run_pipeline
from backend.schemas import (
    ChecklistItem,
    ChecklistOutput,
    FramingBlock,
    HospitalStatus,
    PatientProfile,
)


def _maya_profile() -> PatientProfile:
    return PatientProfile(
        age=28,
        race_ethnicity="Black or African American",
        payer="Medicaid",
        state="NY",
        hospital_name="Kaleida Health",
        weeks_postpartum=6,
        primary_language="English",
        complications_flagged=[],
    )


def _janet_profile() -> PatientProfile:
    return PatientProfile(
        age=41,
        race_ethnicity="White",
        payer="Private",
        state="TX",
        hospital_name="Houston Methodist Hospital",
        weeks_postpartum=4,
        primary_language="English",
        complications_flagged=["hypertensive disorder"],
    )


def _stub_checklist() -> ChecklistOutput:
    return ChecklistOutput(
        items=[ChecklistItem(
            label="Stub finding",
            detail="Stub detail.",
            action="Consider screening for stub.",
            source="Test source",
            confidence="M",
            priority_rank=1,
        )],
        hospital_status=HospitalStatus(
            hospital_name="Test Hospital",
            birthing_friendly="Meets criteria",
            status="success",
        ),
        framing_block=FramingBlock(framing_copy="Test framing copy."),
        confidence_summary="Test summary.",
    )


def test_full_pipeline_with_maya_returns_checklist_output():
    stub = _stub_checklist()
    with patch(
        "backend.orchestrator.generate_checklist",
        new=AsyncMock(return_value=stub),
    ):
        result = asyncio.run(run_pipeline(_maya_profile()))
    assert isinstance(result, ChecklistOutput)
    assert result is stub


def test_full_pipeline_with_janet_returns_checklist_output():
    stub = _stub_checklist()
    with patch(
        "backend.orchestrator.generate_checklist",
        new=AsyncMock(return_value=stub),
    ):
        result = asyncio.run(run_pipeline(_janet_profile()))
    assert isinstance(result, ChecklistOutput)
    assert result is stub


def test_missing_patient_field_raises_validation_error():
    profile = _maya_profile()
    profile.hospital_name = ""
    with pytest.raises(OrchestratorError) as exc_info:
        asyncio.run(run_pipeline(profile))
    assert "hospital_name" in str(exc_info.value)


def test_subagent_timeout_raises_orchestrator_error():
    async def hang_forever(profile):
        await asyncio.sleep(100)

    with patch("backend.orchestrator.mortality.run", new=hang_forever), \
         patch("backend.orchestrator.SUBAGENT_TIMEOUT_SECONDS", 0.1):
        with pytest.raises(OrchestratorError) as exc_info:
            asyncio.run(run_pipeline(_maya_profile()))
    assert "longer than expected" in str(exc_info.value).lower()


def test_output_generator_failure_is_caught():
    class _StubAPIError(anthropic.APIError):
        def __init__(self):
            pass

        def __str__(self):
            return "simulated rate limit"

    async def raise_api_error(scored):
        raise _StubAPIError()

    with patch("backend.orchestrator.generate_checklist", new=raise_api_error):
        with pytest.raises(OrchestratorError) as exc_info:
            asyncio.run(run_pipeline(_maya_profile()))
    assert "Anthropic API" in str(exc_info.value)
