"""N8 — Risk synthesist.

Combines successful subagent returns, detects same-label contradictions, and
assigns conservative confidence values before scoring.
"""

import re
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from backend.constants import MIN_SOURCES_CONFIRMED
from backend.schemas import DataSource, FindingItem, SubAgentReturn, SynthesistFlag, SynthesistOutput


LOW_CONFIDENCE = "L"
FLAGGED_CONFIDENCE = "FLAGGED"

_NEGATIVE_RISK_PATTERNS = (
    r"\bno\s+(?:elevated|increased|higher|high)\s+risk\b",
    r"\bnot\s+(?:elevated|increased|higher|high)\b",
    r"\blow(?:er)?\s+risk\b",
    r"\breduced\s+risk\b",
    r"\bdecreased\s+risk\b",
    r"\bbelow\s+(?:baseline|expected|average)\b",
    r"\bnormal\b",
    r"\breassuring\b",
)

_POSITIVE_RISK_PATTERNS = (
    r"\belevated\s+risk\b",
    r"\bincreased\s+risk\b",
    r"\bhigher\s+risk\b",
    r"\bhigh\s+risk\b",
    r"\babove\s+(?:baseline|expected|average)\b",
    r"\bsevere\b",
    r"\burgent\b",
)


def _source_key(source: DataSource) -> Tuple[str, Optional[str]]:
    return (source.name.strip().lower(), source.url)


def _finding_key(finding: FindingItem) -> Tuple[str, str, Tuple[Tuple[str, Optional[str]], ...]]:
    return (
        finding.label.strip().lower(),
        finding.detail.strip(),
        tuple(sorted(_source_key(source) for source in finding.sources)),
    )


def _copy_finding(finding: FindingItem, confidence: str) -> FindingItem:
    return FindingItem(
        label=finding.label,
        detail=finding.detail,
        confidence=confidence,
        sources=list(finding.sources),
    )


def _risk_direction(detail: str) -> Optional[str]:
    normalized = detail.lower()
    has_negative = any(re.search(pattern, normalized) for pattern in _NEGATIVE_RISK_PATTERNS)
    has_positive = any(re.search(pattern, normalized) for pattern in _POSITIVE_RISK_PATTERNS)

    if has_negative and not has_positive:
        return "lower"
    if has_positive and not has_negative:
        return "higher"
    return None


def _has_contradiction(findings: Sequence[FindingItem]) -> bool:
    directions = {_risk_direction(finding.detail) for finding in findings}
    return "higher" in directions and "lower" in directions


def _source_names(findings: Sequence[FindingItem]) -> Set[str]:
    return {
        source.name.strip().lower()
        for finding in findings
        for source in finding.sources
        if source.name and source.name.strip()
    }


def _conflict_flag(label: str, findings: Sequence[FindingItem], agent_names: Sequence[str]) -> SynthesistFlag:
    details = " | ".join(f"{finding.confidence}: {finding.detail}" for finding in findings)
    return SynthesistFlag(
        flag_type="conflict",
        label=label,
        detail=f"Contradictory risk direction for '{label}': {details}",
        agents_involved=sorted(set(agent_names)),
    )


def synthesize_risk(
    subagent_results: Iterable[SubAgentReturn],
    fallback_flags: Optional[Iterable[SynthesistFlag]] = None,
) -> SynthesistOutput:
    """Return conflict-screened findings for downstream scoring.

    The synthesist preserves both sides of a contradiction by returning each
    conflicting data point with ``confidence='FLAGGED'`` and adding a conflict
    flag. Non-conflicting labels supported by fewer than two distinct source
    names are downgraded to low confidence.
    """
    flags = list(fallback_flags or [])
    grouped: Dict[str, List[Tuple[str, FindingItem]]] = {}
    seen = set()
    completed = 0
    partial_agents: List[str] = []

    for result in subagent_results:
        if result.status not in {"success", "partial"}:
            continue

        completed += 1
        if result.status == "partial":
            partial_agents.append(result.agent_name)
        for finding in result.findings:
            key = _finding_key(finding)
            if key in seen:
                continue
            seen.add(key)
            grouped.setdefault(finding.label, []).append((result.agent_name, finding))

    synthesized_findings: List[FindingItem] = []

    for label, agent_findings in grouped.items():
        agent_names = [agent_name for agent_name, _ in agent_findings]
        findings = [finding for _, finding in agent_findings]

        if _has_contradiction(findings):
            flags.append(_conflict_flag(label, findings, agent_names))
            synthesized_findings.extend(
                _copy_finding(finding, FLAGGED_CONFIDENCE)
                for finding in findings
            )
            continue

        confidence = LOW_CONFIDENCE if len(_source_names(findings)) < MIN_SOURCES_CONFIRMED else None
        synthesized_findings.extend(
            _copy_finding(finding, confidence or finding.confidence)
            for finding in findings
        )

    failed_agents = [
        agent
        for flag in flags
        if flag.flag_type == "gap"
        for agent in flag.agents_involved
    ]

    return SynthesistOutput(
        findings=synthesized_findings,
        conflicts=flags,
        subagents_completed=completed,
        subagents_failed=failed_agents,
        subagents_partial=partial_agents,
    )


__all__ = ["synthesize_risk"]
