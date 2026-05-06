import asyncio

from backend.constants import (
    ACOG_CO_736_SOURCE_NAME,
    CDC_HEAR_HER_SOURCE_NAME,
    CMS_HRSN_SOURCE_NAME,
)
from backend.schemas import PatientProfile
from backend.subagents.guideline import AGENT_NAME as GUIDELINE_AGENT_NAME
from backend.subagents.guideline import run as guideline_run
from backend.subagents.sdoh import AGENT_NAME as SDOH_AGENT_NAME
from backend.subagents.sdoh import run as sdoh_run


def _maya() -> PatientProfile:
    return PatientProfile(
        age=28,
        race_ethnicity="Black or African American",
        payer="Medicaid",
        state="NY",
        hospital_name="NewYork-Presbyterian Hospital",
        weeks_postpartum=6,
        primary_language="English",
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


class TestGuidelineSubagent:
    def test_maya_returns_success(self):
        result = asyncio.run(guideline_run(_maya()))
        assert result.status == "success"
        assert result.agent_name == GUIDELINE_AGENT_NAME
        assert len(result.findings) > 0

    def test_janet_returns_success(self):
        result = asyncio.run(guideline_run(_janet()))
        assert result.status == "success"
        assert len(result.findings) > 0

    def test_findings_include_cdc_source(self):
        result = asyncio.run(guideline_run(_maya()))
        cdc_findings = [
            f for f in result.findings
            if any(s.name == CDC_HEAR_HER_SOURCE_NAME for s in f.sources)
        ]
        assert len(cdc_findings) >= 8

    def test_findings_include_acog_source(self):
        result = asyncio.run(guideline_run(_maya()))
        acog_findings = [
            f for f in result.findings
            if any(s.name == ACOG_CO_736_SOURCE_NAME for s in f.sources)
        ]
        assert len(acog_findings) >= 6

    def test_cdc_findings_are_high_confidence(self):
        result = asyncio.run(guideline_run(_maya()))
        cdc_findings = [
            f for f in result.findings
            if any(s.name == CDC_HEAR_HER_SOURCE_NAME for s in f.sources)
        ]
        for finding in cdc_findings:
            assert finding.confidence == "H", (
                f"Expected H, got {finding.confidence} for {finding.label}"
            )

    def test_no_acog_finding_exceeds_word_cap(self):
        result = asyncio.run(guideline_run(_maya()))
        acog_findings = [
            f for f in result.findings
            if any(s.name == ACOG_CO_736_SOURCE_NAME for s in f.sources)
        ]
        for finding in acog_findings:
            actual = len(finding.detail.split())
            assert actual <= 100, (
                f"{finding.label} detail has {actual} words — exceeds ACOG 100-word cap"
            )


class TestSdohSubagent:
    def test_maya_returns_success(self):
        result = asyncio.run(sdoh_run(_maya()))
        assert result.status == "success"
        assert result.agent_name == SDOH_AGENT_NAME

    def test_janet_returns_success(self):
        result = asyncio.run(sdoh_run(_janet()))
        assert result.status == "success"

    def test_returns_18_findings(self):
        result = asyncio.run(sdoh_run(_maya()))
        assert len(result.findings) == 18, (
            f"Expected 18 (10 core + 8 supplemental), got {len(result.findings)}"
        )

    def test_all_findings_medium_confidence(self):
        result = asyncio.run(sdoh_run(_maya()))
        for finding in result.findings:
            assert finding.confidence == "M", (
                f"Expected M for {finding.label}, got {finding.confidence}"
            )

    def test_source_is_cms_hrsn(self):
        result = asyncio.run(sdoh_run(_maya()))
        for finding in result.findings:
            assert any(s.name == CMS_HRSN_SOURCE_NAME for s in finding.sources)

    def test_maya_and_janet_return_same_findings(self):
        maya_result = asyncio.run(sdoh_run(_maya()))
        janet_result = asyncio.run(sdoh_run(_janet()))
        maya_labels = {f.label for f in maya_result.findings}
        janet_labels = {f.label for f in janet_result.findings}
        assert maya_labels == janet_labels
