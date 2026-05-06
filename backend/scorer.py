"""N10 — Scorer.

Converts synthesized findings into simple routing signals for output generation:
gap score, urgency tier, disparity flag, and lead angle.
"""

from typing import Iterable, Optional

from backend.constants import (
    ACOG_CO_736_SOURCE_NAME,
    CDC_HEAR_HER_SOURCE_NAME,
    CMS_HRSN_SOURCE_NAME,
    CONFIDENCE_GAP_VALUES,
    CONFIDENCE_FLAGGED,
    CONFIDENCE_RANK,
    DISPARITY_RACE_ETHNICITY,
    DISPARITY_STATES,
    KFF_SOURCE_NAME,
    MORTALITY_SOURCE_KEYWORD,
    NCHS_SOURCE_NAME,
    NNPQC_SOURCE_NAME,
    URGENCY_HIGH,
    URGENCY_LOW,
    URGENCY_MEDIUM,
)
from backend.schemas import FindingItem, PatientProfile, ScoredOutput, SynthesistOutput


def _calculate_gap_score(synthesist_output: SynthesistOutput) -> float:
    gap_count = sum(
        1
        for finding in synthesist_output.findings
        if finding.confidence in CONFIDENCE_GAP_VALUES
    ) + len(synthesist_output.subagents_failed)
    expected_total = len(synthesist_output.findings) + len(synthesist_output.subagents_failed)

    if expected_total == 0:
        return 0.0

    return min(gap_count / expected_total, 1.0)


def _has_mortality_signal(findings: Iterable[FindingItem]) -> bool:
    for finding in findings:
        if finding.confidence == CONFIDENCE_FLAGGED:
            continue

        label = finding.label.lower()
        source_names = " ".join(source.name.lower() for source in finding.sources)
        if MORTALITY_SOURCE_KEYWORD in label or MORTALITY_SOURCE_KEYWORD in source_names:
            return True

    return False


def _agent_for_finding(finding: FindingItem) -> str:
    source_names = {source.name for source in finding.sources}
    label = finding.label.lower()

    if NCHS_SOURCE_NAME in source_names or MORTALITY_SOURCE_KEYWORD in label:
        return "mortality"
    if source_names & {CDC_HEAR_HER_SOURCE_NAME, ACOG_CO_736_SOURCE_NAME}:
        return "guideline"
    if CMS_HRSN_SOURCE_NAME in source_names:
        return "sdoh"
    if source_names & {KFF_SOURCE_NAME, NNPQC_SOURCE_NAME}:
        return "state_context"
    if any("cms" in source_name.lower() for source_name in source_names):
        return "bundle"

    return "unknown"


def _is_disparity_flagged(profile: PatientProfile) -> bool:
    return (
        profile.race_ethnicity == DISPARITY_RACE_ETHNICITY
        and profile.state.strip().upper() in DISPARITY_STATES
    )


def _urgency_tier(
    profile: PatientProfile,
    synthesist_output: SynthesistOutput,
    disparity_flag: bool,
) -> str:
    if profile.complications_flagged and _has_mortality_signal(synthesist_output.findings):
        return URGENCY_HIGH

    if not profile.complications_flagged and (
        disparity_flag or bool(synthesist_output.subagents_partial)
    ):
        return URGENCY_MEDIUM

    return URGENCY_LOW


def _lead_angle(synthesist_output: SynthesistOutput) -> str:
    best: Optional[FindingItem] = None
    for finding in synthesist_output.findings:
        if best is None:
            best = finding
            continue

        if CONFIDENCE_RANK.get(finding.confidence, 0) > CONFIDENCE_RANK.get(best.confidence, 0):
            best = finding

    if best is None and synthesist_output.subagents_failed:
        return synthesist_output.subagents_failed[0]

    if best is None:
        return "none"

    return _agent_for_finding(best)


def score_output(
    synthesist_output: SynthesistOutput,
    patient_profile: PatientProfile,
) -> ScoredOutput:
    """Score synthesized findings for output generation."""
    disparity_flag = _is_disparity_flagged(patient_profile)
    return ScoredOutput(
        synthesist_output=synthesist_output,
        patient_profile=patient_profile,
        gap_score=_calculate_gap_score(synthesist_output),
        urgency_tier=_urgency_tier(patient_profile, synthesist_output, disparity_flag),
        disparity_flag=disparity_flag,
        lead_angle=_lead_angle(synthesist_output),
    )


__all__ = ["score_output"]
