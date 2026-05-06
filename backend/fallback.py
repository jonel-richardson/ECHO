"""Fallback handling for subagent results.

N9 receives the raw output from ``asyncio.gather(..., return_exceptions=True)``
and converts subagent failures into synthesist gap flags so the pipeline can
continue with the remaining successful results.
"""

from typing import Iterable, List, Tuple, Union

from backend.schemas import SubAgentReturn, SynthesistFlag


GatherResult = Union[SubAgentReturn, BaseException]


def _failure_flag(agent_name: str, detail: str) -> SynthesistFlag:
    safe_agent_name = agent_name.strip() if agent_name and agent_name.strip() else "unknown_subagent"
    safe_detail = detail.strip() if detail and detail.strip() else "Subagent failed without details."
    return SynthesistFlag(
        flag_type="gap",
        label=f"{safe_agent_name} unavailable",
        detail=safe_detail,
        agents_involved=[safe_agent_name],
    )


def handle_subagent_results(
    results: Iterable[GatherResult],
) -> Tuple[List[SubAgentReturn], List[SynthesistFlag]]:
    """Return successful subagent results and gap flags for failures.

    This function is intentionally defensive: it never raises for bad subagent
    output, because fallback is the pipeline boundary that keeps downstream
    synthesis running with whatever evidence remains available.
    """
    cleaned_results: List[SubAgentReturn] = []
    gap_flags: List[SynthesistFlag] = []

    try:
        raw_results = list(results)
    except Exception as exc:
        return [], [
            _failure_flag(
                "subagent_collection",
                f"Subagent result collection could not be read: {exc}",
            )
        ]

    for index, result in enumerate(raw_results):
        try:
            if isinstance(result, BaseException):
                gap_flags.append(
                    _failure_flag(
                        f"subagent_{index}",
                        f"Subagent raised {type(result).__name__}: {result}",
                    )
                )
                continue

            if not isinstance(result, SubAgentReturn):
                gap_flags.append(
                    _failure_flag(
                        f"subagent_{index}",
                        f"Unexpected subagent result type: {type(result).__name__}",
                    )
                )
                continue

            if result.status == "failed":
                detail = result.error_message or f"{result.agent_name} subagent failed."
                gap_flags.append(_failure_flag(result.agent_name, detail))
                continue

            cleaned_results.append(result)
        except Exception as exc:
            gap_flags.append(
                _failure_flag(
                    f"subagent_{index}",
                    f"Fallback could not process subagent result: {exc}",
                )
            )

    return cleaned_results, gap_flags


__all__ = ["handle_subagent_results"]
