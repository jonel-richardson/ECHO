from backend.risk_synthesist import synthesize_risk
from backend.schemas import DataSource, FindingItem, SubAgentReturn, SynthesistFlag


def _finding(label, detail, source_name, confidence="M"):
    return FindingItem(
        label=label,
        detail=detail,
        confidence=confidence,
        sources=[DataSource(name=source_name)],
    )


def _result(agent_name, findings):
    return SubAgentReturn(
        agent_name=agent_name,
        status="success",
        findings=findings,
    )


class TestRiskSynthesist:
    def test_conflict_detection_flags_opposite_risk_direction(self):
        high = _finding(
            "Blood Pressure Risk",
            "Postpartum symptoms indicate elevated risk requiring follow-up.",
            "CDC Hear Her",
            "H",
        )
        low = _finding(
            "Blood Pressure Risk",
            "Blood pressure pattern is normal with low risk signal.",
            "CMS Quality Measures",
            "M",
        )

        output = synthesize_risk([
            _result("guideline", [high]),
            _result("bundle", [low]),
        ])

        assert len(output.conflicts) == 1
        assert output.conflicts[0].flag_type == "conflict"
        assert output.conflicts[0].label == "Blood Pressure Risk"
        assert output.conflicts[0].agents_involved == ["bundle", "guideline"]
        assert [finding.confidence for finding in output.findings] == ["FLAGGED", "FLAGGED"]
        assert {finding.detail for finding in output.findings} == {high.detail, low.detail}

    def test_agreement_does_not_create_conflict(self):
        first = _finding(
            "Postpartum Warning Sign",
            "Severe headache is an elevated risk warning sign.",
            "CDC Hear Her",
            "H",
        )
        second = _finding(
            "Postpartum Warning Sign",
            "Persistent headache indicates increased risk and needs review.",
            "ACOG Committee Opinion 736",
            "M",
        )

        output = synthesize_risk([
            _result("guideline", [first]),
            _result("mortality", [second]),
        ])

        assert output.conflicts == []
        assert [finding.confidence for finding in output.findings] == ["H", "M"]

    def test_single_source_label_is_downgraded_to_low_confidence(self):
        finding = _finding(
            "Transportation Need",
            "Screen for transportation access before discharge.",
            "CMS AHC HRSN Screening Tool",
            "M",
        )

        output = synthesize_risk([_result("sdoh", [finding])])

        assert len(output.findings) == 1
        assert output.findings[0].confidence == "L"

    def test_fallback_gap_flags_are_preserved(self):
        gap = SynthesistFlag(
            flag_type="gap",
            label="bundle unavailable",
            detail="CMS hospital data unavailable",
            agents_involved=["bundle"],
        )

        output = synthesize_risk([], fallback_flags=[gap])

        assert output.conflicts == [gap]
        assert output.subagents_completed == 0
        assert output.subagents_failed == ["bundle"]

    def test_partial_agents_are_preserved_for_scorer(self):
        partial = SubAgentReturn(
            agent_name="bundle",
            status="partial",
            findings=[],
            error_message="Hospital not found in CMS dataset.",
        )

        output = synthesize_risk([partial])

        assert output.subagents_completed == 1
        assert output.subagents_partial == ["bundle"]

    def test_exact_duplicate_findings_are_deduplicated(self):
        finding = _finding(
            "Coverage Context",
            "State has extended postpartum Medicaid coverage.",
            "KFF Medicaid Postpartum Coverage Tracker",
            "M",
        )

        output = synthesize_risk([
            _result("state_context", [finding]),
            _result("state_context", [finding]),
        ])

        assert len(output.findings) == 1
