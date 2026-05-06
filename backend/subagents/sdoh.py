"""N5 — SDOH subagent.

Loads CMS AHC HRSN screening domain definitions from static JSON and returns
all core and supplemental domains as screening flags for the patient profile.
"""

import json
import logging
from pathlib import Path
from typing import List

from backend.constants import CMS_HRSN_SOURCE_NAME, CMS_HRSN_SOURCE_URL
from backend.schemas import DataSource, FindingItem, PatientProfile, SubAgentReturn

logger = logging.getLogger(__name__)

AGENT_NAME = "sdoh"

_STATIC = Path(__file__).resolve().parents[1] / "data" / "static"
_HRSN_DATA = json.loads((_STATIC / "cms_hrsn_domains.json").read_text())


def _build_findings(profile: PatientProfile) -> List[FindingItem]:
    source = DataSource(name=CMS_HRSN_SOURCE_NAME, url=CMS_HRSN_SOURCE_URL)
    return [
        FindingItem(
            label=entry["label"],
            detail=entry["detail"],
            confidence=entry["confidence"],
            sources=[source],
        )
        for entry in _HRSN_DATA["core_domains"] + _HRSN_DATA["supplemental_domains"]
    ]


async def run(profile: PatientProfile) -> SubAgentReturn:
    try:
        findings = _build_findings(profile)
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="success",
            findings=findings,
        )
    except Exception as exc:
        logger.exception("SDOH subagent failed")
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="failed",
            error_message=f"SDOH subagent error: {exc}",
        )
