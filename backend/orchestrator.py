"""N2 — Orchestrator.

Validates a PatientProfile, dispatches the five subagents in parallel under a
single gather timeout, runs the cleaned results through fallback, synthesist,
and scorer, and returns a ChecklistOutput from the output generator.
"""

import asyncio
import logging
from typing import Any, List

import anthropic

from backend.constants import API_TIMEOUT_SECONDS, SUBAGENT_TIMEOUT_SECONDS
from backend.fallback import handle_subagent_results
from backend.output_generator import generate_checklist
from backend.risk_synthesist import synthesize_risk
from backend.scorer import score_output
from backend.schemas import ChecklistOutput, PatientProfile
from backend.subagents import bundle, guideline, mortality, sdoh, state_context


logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Raised for orchestrator-level failures: validation, timeout, API error."""


def _validate_profile(profile: PatientProfile) -> None:
    """Re-check that required fields are still populated.

    PatientProfile.__post_init__ owns value-validity at construction time. This
    re-check guards only against post-construction mutation that left a required
    field empty or None.
    """
    missing: List[str] = []

    if not isinstance(profile.age, int) or profile.age <= 0:
        missing.append("age")
    if not profile.race_ethnicity or not profile.race_ethnicity.strip():
        missing.append("race_ethnicity")
    if not profile.payer or not profile.payer.strip():
        missing.append("payer")
    if not profile.state or not profile.state.strip():
        missing.append("state")
    if not profile.hospital_name or not profile.hospital_name.strip():
        missing.append("hospital_name")
    if not isinstance(profile.weeks_postpartum, int) or profile.weeks_postpartum < 0:
        missing.append("weeks_postpartum")
    if not profile.primary_language or not profile.primary_language.strip():
        missing.append("primary_language")

    if missing:
        raise OrchestratorError(
            "PatientProfile validation failed: missing or invalid field(s): "
            + ", ".join(missing)
        )


async def _dispatch_subagents(profile: PatientProfile) -> List[Any]:
    return await asyncio.gather(
        mortality.run(profile),
        guideline.run(profile),
        sdoh.run(profile),
        bundle.run(profile),
        state_context.run(profile),
        return_exceptions=True,
    )


async def run_pipeline(profile: PatientProfile) -> ChecklistOutput:
    _validate_profile(profile)

    try:
        gather_results = await asyncio.wait_for(
            _dispatch_subagents(profile),
            timeout=SUBAGENT_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        logger.warning("Subagent gather exceeded %ss timeout", SUBAGENT_TIMEOUT_SECONDS)
        raise OrchestratorError(
            "ECHO is taking longer than expected. Please try again."
        ) from exc

    cleaned, gap_flags = handle_subagent_results(gather_results)
    synth = synthesize_risk(cleaned, fallback_flags=gap_flags)
    scored = score_output(synth, profile)

    # Defensive guard against output_generator.py issues flagged in the
    # pre-handoff audit: it reads os.environ["ANTHROPIC_API_KEY"] without
    # guarding for KeyError, and it does not catch anthropic.APIError.
    # Until those are fixed in output_generator.py, the orchestrator catches
    # them here so any caller of run_pipeline gets a clean OrchestratorError
    # instead of a raw KeyError or APIError.
    try:
        checklist = await asyncio.wait_for(
            generate_checklist(scored),
            timeout=API_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        logger.warning("Output generator exceeded %ss timeout", API_TIMEOUT_SECONDS)
        raise OrchestratorError(
            "Output generator timed out calling the Anthropic API."
        ) from exc
    except KeyError as exc:
        logger.error("Output generator missing required environment variable: %s", exc)
        raise OrchestratorError(
            f"Output generator missing required environment variable: {exc}"
        ) from exc
    except anthropic.APIError as exc:
        logger.exception("Anthropic API call failed")
        raise OrchestratorError(f"Anthropic API error: {exc}") from exc
    except ValueError as exc:
        logger.exception("Output generator validation failed")
        raise OrchestratorError(f"Output generator validation failed: {exc}") from exc

    return checklist


__all__ = ["OrchestratorError", "run_pipeline"]
