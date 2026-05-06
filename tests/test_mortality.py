import asyncio

from backend.constants import NCHS_SOURCE_NAME
from backend.schemas import PatientProfile
from backend.subagents.mortality import AGENT_NAME, run


def _maya() -> PatientProfile:
    return PatientProfile(
        age=28,
        race_ethnicity="Black or African American",
        payer="Medicaid",
        state="NY",
        hospital_name="NewYork-Presbyterian Hospital",
        weeks_postpartum=6,
        primary_language="English",
        complications_flagged=[],
    )


def _janet() -> PatientProfile:
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


def test_maya_returns_3_findings():
    result = asyncio.run(run(_maya()))

    assert result.status == "success"
    assert result.agent_name == AGENT_NAME
    assert len(result.findings) == 3

    for finding in result.findings:
        assert finding.confidence == "M"
        assert len(finding.sources) >= 1
        assert finding.sources[0].name == NCHS_SOURCE_NAME

    disparity = result.findings[2]
    assert "Black or African American" in disparity.detail
    assert "44.8" in disparity.detail
    assert "14.2" in disparity.detail


def test_janet_returns_findings_with_age_cohort_jump():
    result = asyncio.run(run(_janet()))

    assert result.status == "success"
    assert len(result.findings) == 2

    cohort_finding = result.findings[1]
    assert "58.8" in cohort_finding.detail
    assert "14.2" in cohort_finding.detail
    assert "4 times" in cohort_finding.detail
    assert "age-cohort risk" in cohort_finding.detail


def test_unknown_race_returns_failed_status():
    profile = PatientProfile(
        age=30,
        race_ethnicity="Native Hawaiian or Pacific Islander",
        payer="Medicaid",
        state="NY",
        hospital_name="Test Hospital",
        weeks_postpartum=6,
        primary_language="English",
    )

    result = asyncio.run(run(profile))

    assert result.status == "failed"
    assert result.error_message
    assert "Native Hawaiian" in result.error_message
    assert result.findings == []


def test_suppressed_cell_falls_back_to_all_ages():
    profile = PatientProfile(
        age=22,
        race_ethnicity="Asian",
        payer="Private",
        state="NY",
        hospital_name="Test Hospital",
        weeks_postpartum=6,
        primary_language="English",
    )

    result = asyncio.run(run(profile))

    assert result.status == "success"
    assert len(result.findings) >= 2

    cohort_finding = result.findings[1]
    assert "suppressed" in cohort_finding.detail.lower()
    assert "all-ages" in cohort_finding.detail.lower()
    assert "NCHS reliability standard" in cohort_finding.detail
