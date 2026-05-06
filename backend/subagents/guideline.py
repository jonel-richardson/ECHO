"""N4 — Guideline subagent.

Loads CDC Hear Her warning signs and ACOG 4th trimester findings from static JSON
and returns all applicable findings for the patient profile.
"""

import json
import logging
from pathlib import Path
from typing import List

from backend.constants import (
    ACOG_CO_736_SOURCE_NAME,
    ACOG_CO_736_SOURCE_URL,
    CDC_HEAR_HER_SOURCE_NAME,
    CDC_HEAR_HER_SOURCE_URL,
)
from backend.schemas import DataSource, FindingItem, PatientProfile, SubAgentReturn

logger = logging.getLogger(__name__)

AGENT_NAME = "guideline"
ACOG_WORD_CAP = 100

_STATIC = Path(__file__).resolve().parents[1] / "data" / "static"
_CDC_DATA = json.loads((_STATIC / "cdc_hear_her_warning_signs.json").read_text())
_ACOG_DATA = json.loads((_STATIC / "acog_4th_trimester.json").read_text())


def _build_findings(profile: PatientProfile) -> List[FindingItem]:
    findings: List[FindingItem] = []
    cdc_source = DataSource(name=CDC_HEAR_HER_SOURCE_NAME, url=CDC_HEAR_HER_SOURCE_URL)
    acog_source = DataSource(name=ACOG_CO_736_SOURCE_NAME, url=ACOG_CO_736_SOURCE_URL)

    for entry in _CDC_DATA["warning_signs"]:
        findings.append(FindingItem(
            label=entry["label"],
            detail=entry["detail"],
            confidence=entry["confidence"],
            sources=[cdc_source],
        ))

    for entry in _ACOG_DATA["findings"]:
        if entry["word_count"] > ACOG_WORD_CAP:
            logger.warning(
                "Skipping ACOG entry '%s': word_count %d exceeds cap %d",
                entry["label"], entry["word_count"], ACOG_WORD_CAP,
            )
            continue
        findings.append(FindingItem(
            label=entry["label"],
            detail=entry["detail"],
            confidence=entry["confidence"],
            sources=[acog_source],
        ))

    return findings


async def run(profile: PatientProfile) -> SubAgentReturn:
    try:
        findings = _build_findings(profile)
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="success",
            findings=findings,
        )
    except Exception as exc:
        logger.exception("Guideline subagent failed")
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="failed",
            error_message=f"Guideline subagent error: {exc}",
        )
