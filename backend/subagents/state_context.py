"""N7 — State Context subagent.

Loads three state-context data sources at module import (KFF Medicaid postpartum
coverage CSV, NNPQC funding CSV, and the curated state QI context JSON) and
returns up to 4 FindingItems describing the policy and quality-improvement
environment for the patient's state.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from backend.constants import (
    KFF_SOURCE_NAME,
    KFF_SOURCE_URL,
    NNPQC_SOURCE_NAME,
    NNPQC_SOURCE_URL,
    STATE_NAMES,
    SUPPORTED_STATES,
)
from backend.schemas import DataSource, FindingItem, PatientProfile, SubAgentReturn


logger = logging.getLogger(__name__)

AGENT_NAME = "state_context"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
KFF_CSV_PATH = DATA_DIR / "kff_postpartum_coverage.csv"
NNPQC_CSV_PATH = DATA_DIR / "nnpqc_funding.csv"
STATE_QI_JSON_PATH = DATA_DIR / "static" / "state_qi_context.json"

STATE_QI_FACTS_PER_STATE = 2
GENERAL_TAG = "general"

# Maps a complications_flagged string (lowercased) to the set of relevance_tags
# that should be considered a match for state-QI fact selection.
COMPLICATION_TAG_MAP: Dict[str, Set[str]] = {
    "hypertension": {"hypertension"},
    "preeclampsia": {"preeclampsia"},
    "hypertensive disorder": {"hypertension", "preeclampsia"},
    "mental health": {"mental_health"},
    "depression": {"mental_health"},
    "anxiety": {"mental_health"},
    "substance use": {"substance_use"},
    "oud": {"substance_use"},
}

# KFF CSV has 2 metadata rows above the header; trailing notes/footnotes have
# variable column counts so we skip malformed lines defensively.
_KFF_DF = pd.read_csv(KFF_CSV_PATH, skiprows=2, on_bad_lines="skip")
_NNPQC_DF = pd.read_csv(NNPQC_CSV_PATH)
with STATE_QI_JSON_PATH.open(encoding="utf-8") as fp:
    _STATE_QI_CONTEXT = json.load(fp)


def _kff_finding(state: str) -> Optional[FindingItem]:
    state_name = STATE_NAMES[state]
    rows = _KFF_DF[_KFF_DF["Location"] == state_name]
    if rows.empty:
        return None
    row = rows.iloc[0]
    extension_status = row["Status of State Action"]
    expansion_status = row["ACA Medicaid Expansion Status"]
    detail = (
        f"In {state_name}, the status of the 12-month postpartum Medicaid coverage extension is: "
        f"{extension_status}. The state's ACA Medicaid expansion status is: {expansion_status}. "
        f"Source: {KFF_SOURCE_NAME}."
    )
    return FindingItem(
        label=f"Medicaid Postpartum Coverage \u2014 {state_name}",
        detail=detail,
        confidence="M",
        sources=[DataSource(name=KFF_SOURCE_NAME, url=KFF_SOURCE_URL)],
    )


def _nnpqc_finding(state: str) -> Optional[FindingItem]:
    state_name = STATE_NAMES[state]
    rows = _NNPQC_DF[_NNPQC_DF["Location"] == state]
    if rows.empty:
        return None
    row = rows.iloc[0]
    funding_status = row["Funding"]
    website = row["Website"] if pd.notna(row["Website"]) else None
    detail = (
        f"The {state_name} Perinatal Quality Collaborative is currently {funding_status} "
        f"under the National Network of Perinatal Quality Collaboratives (NNPQC). "
    )
    if website:
        detail += f"State PQC website: {website}. "
    detail += f"Source: {NNPQC_SOURCE_NAME}."
    return FindingItem(
        label=f"State Perinatal QI Funding \u2014 {state_name}",
        detail=detail,
        confidence="M",
        sources=[DataSource(name=NNPQC_SOURCE_NAME, url=NNPQC_SOURCE_URL)],
    )


def _complications_to_tags(complications: List[str]) -> Set[str]:
    tags: Set[str] = set()
    for entry in complications:
        normalized = entry.strip().lower()
        if normalized in COMPLICATION_TAG_MAP:
            tags.update(COMPLICATION_TAG_MAP[normalized])
    return tags


def _select_state_qi_facts(facts: List[dict], complication_tags: Set[str]) -> List[dict]:
    """Pick exactly two distinct facts: one general-tagged + one complication match.

    Falls back to a second general-tagged fact (if no complication match) and
    finally to the first un-picked fact in JSON order. Returned facts preserve
    JSON order so downstream rendering is deterministic.
    """
    if len(facts) < 2:
        return facts

    general_idx: Optional[int] = None
    for i, fact in enumerate(facts):
        if GENERAL_TAG in fact.get("relevance_tags", []):
            general_idx = i
            break

    second_idx: Optional[int] = None
    if complication_tags:
        for i, fact in enumerate(facts):
            if i == general_idx:
                continue
            if set(fact.get("relevance_tags", [])) & complication_tags:
                second_idx = i
                break

    if second_idx is None:
        for i, fact in enumerate(facts):
            if i == general_idx:
                continue
            if GENERAL_TAG in fact.get("relevance_tags", []):
                second_idx = i
                break

    if second_idx is None:
        for i in range(len(facts)):
            if i != general_idx:
                second_idx = i
                break

    selected = sorted({idx for idx in (general_idx, second_idx) if idx is not None})
    return [facts[i] for i in selected]


def _state_qi_findings(state: str, complications_flagged: List[str]) -> List[FindingItem]:
    state_block = _STATE_QI_CONTEXT.get(state)
    if not state_block:
        return []
    facts = state_block.get("facts", [])
    complication_tags = _complications_to_tags(complications_flagged)
    selected = _select_state_qi_facts(facts, complication_tags)

    findings: List[FindingItem] = []
    for fact in selected:
        sources = [
            DataSource(name=src["name"], url=src.get("url"))
            for src in fact.get("sources", [])
        ]
        findings.append(FindingItem(
            label=fact["label"],
            detail=fact["detail"],
            confidence="M",
            sources=sources,
        ))
    return findings


def _build_findings(profile: PatientProfile) -> Tuple[str, List[FindingItem]]:
    state = profile.state
    if state not in SUPPORTED_STATES:
        limitation = FindingItem(
            label="State Coverage Limitation",
            detail=(
                f"ECHO v2 supports detailed state context only for New York and Texas. "
                f"Patient's state is '{state}'. State-specific Medicaid coverage and "
                f"quality-improvement context were not loaded for this state."
            ),
            confidence="M",
            sources=[DataSource(name="ECHO v2 scope", url=None)],
        )
        return "partial", [limitation]

    findings: List[FindingItem] = []
    kff = _kff_finding(state)
    if kff:
        findings.append(kff)
    nnpqc = _nnpqc_finding(state)
    if nnpqc:
        findings.append(nnpqc)
    findings.extend(_state_qi_findings(state, profile.complications_flagged))
    return "success", findings[:4]


async def run(profile: PatientProfile) -> SubAgentReturn:
    try:
        status, findings = _build_findings(profile)
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status=status,
            findings=findings,
        )
    except Exception as exc:
        logger.exception("State Context subagent failed")
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="failed",
            error_message=f"State Context subagent error: {exc}",
        )
