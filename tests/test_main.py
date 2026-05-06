from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.orchestrator import OrchestratorError
from backend.schemas import (
    ChecklistItem,
    ChecklistOutput,
    FramingBlock,
    HospitalStatus,
)


client = TestClient(app)


def _maya_dict() -> dict:
    return {
        "age": 28,
        "race_ethnicity": "Black or African American",
        "payer": "Medicaid",
        "state": "NY",
        "hospital_name": "Kaleida Health",
        "weeks_postpartum": 6,
        "primary_language": "English",
        "complications_flagged": [],
    }


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


def test_health_endpoint_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_generate_checklist_with_maya_returns_200():
    stub = _stub_checklist()
    with patch("backend.main.run_pipeline", new=AsyncMock(return_value=stub)):
        resp = client.post("/generate-checklist", json=_maya_dict())
    assert resp.status_code == 200
    body = resp.json()
    assert body["clinical_disclaimer"]
    assert body["items"][0]["label"] == "Stub finding"
    assert body["hospital_status"]["birthing_friendly"] == "Meets criteria"


def test_generate_checklist_with_missing_field_returns_400():
    payload = _maya_dict()
    del payload["hospital_name"]
    resp = client.post("/generate-checklist", json=payload)
    assert resp.status_code == 400
    body = resp.json()
    assert body["type"] == "validation"
    assert "hospital_name" in body["error"]


def test_generate_checklist_with_orchestrator_timeout_returns_504():
    async def raise_timeout(profile):
        raise OrchestratorError("ECHO is taking longer than expected. Please try again.")

    with patch("backend.main.run_pipeline", new=raise_timeout):
        resp = client.post("/generate-checklist", json=_maya_dict())
    assert resp.status_code == 504
    body = resp.json()
    assert body["type"] == "timeout"
    assert "longer than expected" in body["error"].lower()


def test_generate_checklist_with_api_error_returns_502():
    async def raise_api(profile):
        raise OrchestratorError("Anthropic API error: rate limited")

    with patch("backend.main.run_pipeline", new=raise_api):
        resp = client.post("/generate-checklist", json=_maya_dict())
    assert resp.status_code == 502
    body = resp.json()
    assert body["type"] == "upstream_error"
    assert "anthropic" in body["error"].lower()
