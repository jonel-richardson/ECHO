"""N11 — Output Generator.

Receives ScoredOutput, loads communication framing, calls the Anthropic API once,
parses and validates the response, and returns a ChecklistOutput.
"""

import dataclasses
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import anthropic

from backend.constants import ANTHROPIC_MAX_TOKENS, ANTHROPIC_MODEL
from backend.schemas import (
    ChecklistItem,
    ChecklistOutput,
    DataSource,
    FramingBlock,
    HospitalStatus,
    ScoredOutput,
    CLINICAL_DISCLAIMER,
)

logger = logging.getLogger(__name__)

_STATIC = Path(__file__).resolve().parent / "data" / "static"
_FRAMING_PATH = _STATIC / "framing_library.json"
_CDC_PATH = _STATIC / "cdc_hear_her_warning_signs.json"

with _FRAMING_PATH.open() as _f:
    _FRAMING_LIBRARY: Dict[str, Any] = json.load(_f)

with _CDC_PATH.open() as _f:
    _CDC_WARNING_SIGNS: List[Dict] = json.load(_f)["warning_signs"]


SYSTEM_PROMPT = """You are ECHO's Output Generator. You receive structured clinical findings from a multi-agent postpartum screening pipeline and generate a patient-specific checklist for a Certified Nurse Midwife (CNM).

RULES — follow exactly:
1. Every checklist item must have: label, detail (1-2 sentences), action (MUST begin with exactly "Consider screening for..."), source (federal source or professional body — NEVER cite AWHONN as a source), confidence (H | M | L | FLAGGED), priority_rank (integer, 1 = highest urgency).
2. Never use diagnostic language. No "Patient has..." or "Diagnose..." anywhere in output.
3. ALL CDC Hear Her warning signs in cdc_warning_signs_required MUST appear in items. Tailoring changes priority_rank, not inclusion.
4. Never resolve a FLAGGED conflict. If confidence = FLAGGED, keep both data points in the detail field and append "CNM review required."
5. hospital_status: derive from the bundle subagent findings in scored_output. birthing_friendly must be exactly one of: "Meets criteria" | "Does not meet criteria" | "Not found in CMS dataset". Set hcahps_discharge_score and state_postpartum_visit_rate as floats if found in findings, otherwise null.
6. confidence_summary: 1-2 sentences summarizing overall data confidence.
7. Output valid JSON ONLY. No prose, no markdown fences, no explanation. Root object keys: "items", "hospital_status", "confidence_summary".

Output schema:
{
  "items": [{"label":"","detail":"","action":"Consider screening for...","source":"","confidence":"H|M|L|FLAGGED","priority_rank":1}],
  "hospital_status": {"hospital_name":"","birthing_friendly":"Meets criteria|Does not meet criteria|Not found in CMS dataset","hcahps_discharge_score":null,"state_postpartum_visit_rate":null,"status":"success|partial"},
  "confidence_summary": ""
}"""


def _framing_block(race_ethnicity: str, payer: str) -> FramingBlock:
    key = f"{race_ethnicity}|{payer}"
    entry = _FRAMING_LIBRARY.get(key) or _FRAMING_LIBRARY["default"]
    return FramingBlock(
        framing_copy=entry["framing_copy"],
        framing_sources=[
            DataSource(name=s["name"], url=s.get("url"))
            for s in entry.get("framing_sources", [])
        ],
        see_also=entry.get("see_also", []),
    )


def _user_message(scored_output: ScoredOutput) -> str:
    return json.dumps({
        "scored_output": dataclasses.asdict(scored_output),
        "cdc_warning_signs_required": _CDC_WARNING_SIGNS,
    })


def _validate_items(raw_items: List[Dict]) -> List[ChecklistItem]:
    items = []
    for raw in raw_items:
        action = raw.get("action", "")
        source = raw.get("source", "")
        if not action.startswith("Consider screening for"):
            raise ValueError(f"Action must start with 'Consider screening for...': {action!r}")
        if not source or not source.strip():
            raise ValueError(f"Item missing source: {raw.get('label')!r}")
        if "awhonn" in source.lower():
            raise ValueError(f"AWHONN must not appear as a source: {source!r}")
        items.append(ChecklistItem(
            label=raw["label"],
            detail=raw["detail"],
            action=action,
            source=source,
            confidence=raw["confidence"],
            priority_rank=int(raw["priority_rank"]),
        ))
    return items


def _hospital_status(raw: Dict, hospital_name: str) -> HospitalStatus:
    return HospitalStatus(
        hospital_name=raw.get("hospital_name") or hospital_name,
        birthing_friendly=raw["birthing_friendly"],
        hcahps_discharge_score=raw.get("hcahps_discharge_score"),
        state_postpartum_visit_rate=raw.get("state_postpartum_visit_rate"),
        status=raw.get("status", "partial"),
    )


async def generate_checklist(scored_output: ScoredOutput) -> ChecklistOutput:
    profile = scored_output.patient_profile
    framing = _framing_block(profile.race_ethnicity, profile.payer)

    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = await client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=ANTHROPIC_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _user_message(scored_output)}],
    )

    if getattr(message, "stop_reason", None) == "max_tokens":
        raise ValueError(
            f"Output Generator: model response exceeded max_tokens={ANTHROPIC_MAX_TOKENS}"
        )

    raw_text = message.content[0].text.strip()
    # strip markdown fences if the model wraps output
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Output Generator: model returned invalid JSON: {exc}")

    items = _validate_items(parsed.get("items", []))
    if not items:
        raise ValueError("Output Generator: model returned no checklist items")

    hospital = _hospital_status(
        parsed.get("hospital_status", {}),
        profile.hospital_name,
    )

    return ChecklistOutput(
        items=sorted(items, key=lambda i: i.priority_rank),
        hospital_status=hospital,
        framing_block=framing,
        conflict_flags=scored_output.synthesist_output.conflicts,
        confidence_summary=parsed.get("confidence_summary", ""),
        clinical_disclaimer=CLINICAL_DISCLAIMER,
    )


__all__ = ["generate_checklist"]
