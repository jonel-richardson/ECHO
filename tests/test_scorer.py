from backend.constants import CMS_HRSN_SOURCE_NAME, NCHS_SOURCE_NAME
from backend.scorer import score_output
from backend.schemas import DataSource, FindingItem, PatientProfile, SynthesistOutput


def _profile(
    race_ethnicity="White",
    state="TX",
    complications_flagged=None,
):
    return PatientProfile(
        age=41,
        race_ethnicity=race_ethnicity,
        payer="Private",
        state=state,
        hospital_name="Houston Methodist Hospital",
        weeks_postpartum=4,
        primary_language="English",
        complications_flagged=complications_flagged or [],
    )


def _finding(label, confidence, source_name, detail="Reference finding."):
    return FindingItem(
        label=label,
        detail=detail,
        confidence=confidence,
        sources=[DataSource(name=source_name)],
    )


class TestScorer:
    def test_maya_scenario_sets_disparity_and_medium_urgency(self):
        maya = _profile(
            race_ethnicity="Black or African American",
            state="NY",
            complications_flagged=[],
        )
        synthesist = SynthesistOutput(findings=[], subagents_completed=5)

        result = score_output(synthesist, maya)

        assert result.disparity_flag is True
        assert result.urgency_tier == "MED"

    def test_janet_hypertensive_scenario_sets_high_urgency(self):
        janet = _profile(complications_flagged=["hypertension"])
        mortality_finding = _finding(
            label="Maternal Mortality Rate - White",
            confidence="L",
            source_name=NCHS_SOURCE_NAME,
            detail="Mortality context is available for this patient profile.",
        )
        synthesist = SynthesistOutput(
            findings=[mortality_finding],
            subagents_completed=5,
        )

        result = score_output(synthesist, janet)

        assert result.disparity_flag is False
        assert result.urgency_tier == "HIGH"
        assert result.lead_angle == "mortality"

    def test_gap_score_counts_low_flagged_and_failed_agents(self):
        synthesist = SynthesistOutput(
            findings=[
                _finding("Food Security", "L", CMS_HRSN_SOURCE_NAME),
                _finding("Blood Pressure Risk", "FLAGGED", NCHS_SOURCE_NAME),
                _finding("Postpartum Warning Sign", "H", "CDC Hear Her"),
            ],
            subagents_completed=4,
            subagents_failed=["bundle"],
        )

        result = score_output(synthesist, _profile())

        assert result.gap_score == 0.75

    def test_partial_subagent_sets_medium_urgency_without_disparity(self):
        synthesist = SynthesistOutput(
            findings=[],
            subagents_completed=5,
            subagents_partial=["bundle"],
        )

        result = score_output(synthesist, _profile(complications_flagged=[]))

        assert result.disparity_flag is False
        assert result.urgency_tier == "MED"

    def test_low_urgency_when_no_complications_disparity_or_partial(self):
        synthesist = SynthesistOutput(
            findings=[
                _finding("Transportation Need", "M", CMS_HRSN_SOURCE_NAME),
            ],
            subagents_completed=5,
        )

        result = score_output(synthesist, _profile(complications_flagged=[]))

        assert result.urgency_tier == "LOW"
        assert result.lead_angle == "sdoh"

    def test_lead_angle_prefers_best_finding_over_failed_agent(self):
        synthesist = SynthesistOutput(
            findings=[
                _finding("Maternal Mortality Rate", "H", NCHS_SOURCE_NAME),
            ],
            subagents_completed=4,
            subagents_failed=["bundle"],
        )

        result = score_output(synthesist, _profile())

        assert result.lead_angle == "mortality"
