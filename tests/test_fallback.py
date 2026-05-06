from backend.fallback import handle_subagent_results
from backend.schemas import DataSource, FindingItem, SubAgentReturn


def _success(agent_name="mortality"):
    return SubAgentReturn(
        agent_name=agent_name,
        status="success",
        findings=[
            FindingItem(
                label="Mortality risk",
                detail="Reference finding for downstream synthesis.",
                confidence="H",
                sources=[DataSource(name="NCHS Health E-Stat 113")],
            )
        ],
    )


class TestFallbackHandler:
    def test_failed_subagent_is_removed_and_gap_flag_created(self):
        failed = SubAgentReturn(
            agent_name="bundle",
            status="failed",
            error_message="CMS hospital data unavailable",
        )

        cleaned, flags = handle_subagent_results([_success(), failed])

        assert [result.agent_name for result in cleaned] == ["mortality"]
        assert len(flags) == 1
        assert flags[0].flag_type == "gap"
        assert flags[0].label == "bundle unavailable"
        assert flags[0].detail == "CMS hospital data unavailable"
        assert flags[0].agents_involved == ["bundle"]

    def test_exception_result_becomes_gap_flag(self):
        cleaned, flags = handle_subagent_results([_success(), RuntimeError("timeout")])

        assert len(cleaned) == 1
        assert len(flags) == 1
        assert flags[0].flag_type == "gap"
        assert flags[0].agents_involved == ["subagent_1"]
        assert "RuntimeError" in flags[0].detail
        assert "timeout" in flags[0].detail

    def test_partial_results_continue_through_pipeline(self):
        partial = SubAgentReturn(
            agent_name="state_context",
            status="partial",
            findings=[],
            error_message="Funding file missing; coverage data loaded.",
        )

        cleaned, flags = handle_subagent_results([partial])

        assert cleaned == [partial]
        assert flags == []

    def test_unexpected_result_type_does_not_raise(self):
        cleaned, flags = handle_subagent_results([_success(), {"status": "failed"}])

        assert [result.agent_name for result in cleaned] == ["mortality"]
        assert len(flags) == 1
        assert flags[0].flag_type == "gap"
        assert "Unexpected subagent result type" in flags[0].detail
