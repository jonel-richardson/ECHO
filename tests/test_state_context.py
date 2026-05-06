import asyncio

from backend.constants import KFF_SOURCE_NAME, NNPQC_SOURCE_NAME
from backend.schemas import PatientProfile
from backend.subagents.state_context import AGENT_NAME, _STATE_QI_CONTEXT, run


def _general_labels_for_state(state: str) -> set:
    facts = _STATE_QI_CONTEXT[state]["facts"]
    return {f["label"] for f in facts if "general" in f.get("relevance_tags", [])}


def _labels_with_tag(state: str, tag: str) -> set:
    facts = _STATE_QI_CONTEXT[state]["facts"]
    return {f["label"] for f in facts if tag in f.get("relevance_tags", [])}


def _ny_profile() -> PatientProfile:
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


def _tx_profile() -> PatientProfile:
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


def _ca_profile() -> PatientProfile:
    return PatientProfile(
        age=30,
        race_ethnicity="Hispanic or Latino",
        payer="Medicaid",
        state="CA",
        hospital_name="UCSF Medical Center",
        weeks_postpartum=6,
        primary_language="Spanish",
        complications_flagged=[],
    )


def test_ny_patient_returns_4_findings():
    result = asyncio.run(run(_ny_profile()))

    assert result.status == "success"
    assert result.agent_name == AGENT_NAME
    assert len(result.findings) == 4

    source_names = [s.name for f in result.findings for s in f.sources]
    assert KFF_SOURCE_NAME in source_names
    assert NNPQC_SOURCE_NAME in source_names

    kff_finding = result.findings[0]
    assert "New York" in kff_finding.detail
    assert "12-month extension implemented" in kff_finding.detail


def test_tx_patient_returns_4_findings():
    result = asyncio.run(run(_tx_profile()))

    assert result.status == "success"
    assert len(result.findings) == 4

    kff_finding = result.findings[0]
    assert "Texas" in kff_finding.detail
    assert "Not Adopted" in kff_finding.detail

    nnpqc_finding = result.findings[1]
    assert "tchmb.org" in nnpqc_finding.detail


def test_unsupported_state_returns_partial():
    result = asyncio.run(run(_ca_profile()))

    assert result.status == "partial"
    assert len(result.findings) == 1
    assert result.findings[0].label == "State Coverage Limitation"
    assert "CA" in result.findings[0].detail


def test_findings_carry_sources():
    for profile in [_ny_profile(), _tx_profile(), _ca_profile()]:
        result = asyncio.run(run(profile))
        for finding in result.findings:
            assert len(finding.sources) >= 1
            for source in finding.sources:
                assert source.name and source.name.strip()


def test_ny_patient_with_mental_health_complication_surfaces_mental_health_fact():
    profile = PatientProfile(
        age=32,
        race_ethnicity="Hispanic or Latino",
        payer="Medicaid",
        state="NY",
        hospital_name="Mount Sinai",
        weeks_postpartum=10,
        primary_language="English",
        complications_flagged=["mental health"],
    )
    result = asyncio.run(run(profile))

    assert result.status == "success"
    assert len(result.findings) == 4

    state_qi_labels = {f.label for f in result.findings[2:4]}
    mental_health_labels = _labels_with_tag("NY", "mental_health")
    assert state_qi_labels & mental_health_labels


def test_tx_patient_with_hypertensive_disorder_surfaces_preeclampsia_fact():
    profile = PatientProfile(
        age=39,
        race_ethnicity="Black or African American",
        payer="Medicaid",
        state="TX",
        hospital_name="Memorial Hermann",
        weeks_postpartum=3,
        primary_language="English",
        complications_flagged=["hypertensive disorder"],
    )
    result = asyncio.run(run(profile))

    assert result.status == "success"
    assert len(result.findings) == 4

    state_qi_labels = {f.label for f in result.findings[2:4]}
    preeclampsia_labels = _labels_with_tag("TX", "preeclampsia")
    hypertension_labels = _labels_with_tag("TX", "hypertension")
    assert state_qi_labels & (preeclampsia_labels | hypertension_labels)


def test_patient_with_no_complications_returns_general_facts():
    result = asyncio.run(run(_ny_profile()))

    assert result.status == "success"
    assert len(result.findings) == 4

    general_labels = _general_labels_for_state("NY")
    state_qi_labels = {f.label for f in result.findings[2:4]}
    assert state_qi_labels.issubset(general_labels)
