import asyncio

from backend.constants import (
    CMS_BIRTHING_FRIENDLY_SOURCE_NAME,
    CMS_CORE_SET_SOURCE_NAME,
    CMS_HCAHPS_SOURCE_NAME,
)
from backend.schemas import PatientProfile
from backend.subagents.bundle import AGENT_NAME, run


def _ny_known_profile() -> PatientProfile:
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


def _tx_known_profile() -> PatientProfile:
    return PatientProfile(
        age=41,
        race_ethnicity="White",
        payer="Private",
        state="TX",
        hospital_name="Houston Methodist Hospital",
        weeks_postpartum=4,
        primary_language="English",
        complications_flagged=["hypertension"],
    )


def _ny_unknown_profile() -> PatientProfile:
    return PatientProfile(
        age=30,
        race_ethnicity="Hispanic or Latino",
        payer="Medicaid",
        state="NY",
        hospital_name="Nonexistent Birthing Pavilion of Atlantis",
        weeks_postpartum=6,
        primary_language="English",
        complications_flagged=[],
    )


def test_ny_patient_with_known_hospital_returns_4_findings():
    result = asyncio.run(run(_ny_known_profile()))

    assert result.status == "success"
    assert result.agent_name == AGENT_NAME
    assert len(result.findings) == 4

    source_names = [s.name for f in result.findings for s in f.sources]
    assert CMS_BIRTHING_FRIENDLY_SOURCE_NAME in source_names
    assert CMS_HCAHPS_SOURCE_NAME in source_names
    assert CMS_CORE_SET_SOURCE_NAME in source_names

    bf_finding = result.findings[0]
    assert "Birthing-Friendly" in bf_finding.label
    assert "Designated" in bf_finding.label

    hcahps_finding = result.findings[1]
    assert "HCAHPS" in hcahps_finding.label
    assert "86" in hcahps_finding.detail


def test_tx_patient_with_known_hospital_returns_3_findings():
    result = asyncio.run(run(_tx_known_profile()))

    assert result.status == "success"
    assert len(result.findings) == 3

    bf_finding = result.findings[0]
    assert "Birthing-Friendly" in bf_finding.label
    assert "Designated" in bf_finding.label

    state_finding = result.findings[1]
    assert "Texas" in state_finding.label
    assert "77.4" in state_finding.detail


def test_unknown_hospital_returns_partial_status_with_state_finding_intact():
    result = asyncio.run(run(_ny_unknown_profile()))

    assert result.status == "partial"
    assert len(result.findings) >= 2

    bf_finding = result.findings[0]
    assert "Not Designated" in bf_finding.label

    labels = {f.label for f in result.findings}
    assert any("Medicaid PPC-AD Rate" in label for label in labels)
    assert any("Cross-State Postpartum Care Disparity" in label for label in labels)


def test_disparity_context_finding_includes_headline_numbers():
    for profile in [_ny_known_profile(), _tx_known_profile()]:
        result = asyncio.run(run(profile))
        disparity = next(
            f for f in result.findings
            if "Cross-State Postpartum Care Disparity" in f.label
        )
        assert "82.4" in disparity.detail
        assert "77.4" in disparity.detail


def test_findings_carry_sources():
    for profile in [_ny_known_profile(), _tx_known_profile(), _ny_unknown_profile()]:
        result = asyncio.run(run(profile))
        for finding in result.findings:
            assert len(finding.sources) >= 1
            for source in finding.sources:
                assert source.name and source.name.strip()
