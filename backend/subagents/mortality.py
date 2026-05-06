"""N3 — Mortality subagent.

Loads NCHS Health E-Stat 113 mortality data once at module load and returns
up to 3 FindingItems describing maternal mortality risk for the patient profile.
"""

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

from backend.constants import NCHS_LATEST_YEAR, NCHS_SOURCE_NAME, NCHS_SOURCE_URL
from backend.schemas import DataSource, FindingItem, PatientProfile, SubAgentReturn


logger = logging.getLogger(__name__)

AGENT_NAME = "mortality"
COMPARISON_RACE = "White"
CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "nchs_maternal_mortality.csv"
COHORT_JUMP_THRESHOLD = 2.0

_DF = pd.read_csv(CSV_PATH)


def _age_to_group(age: int) -> str:
    if age < 25:
        return "under_25"
    if age < 40:
        return "25_to_39"
    return "40_and_older"


def _get_rate(race: str, age_group: str, year: int = NCHS_LATEST_YEAR) -> Optional[float]:
    rows = _DF[
        (_DF["year"] == year)
        & (_DF["race_ethnicity"] == race)
        & (_DF["age_group"] == age_group)
    ]
    if rows.empty:
        return None
    rate = rows.iloc[0]["mortality_rate"]
    return float(rate) if pd.notna(rate) else None


def _approx_multiplier(numerator: float, denominator: float) -> int:
    return int(round(numerator / denominator))


def _build_findings(profile: PatientProfile) -> List[FindingItem]:
    race = profile.race_ethnicity
    age_group = _age_to_group(profile.age)
    cohort_label_human = age_group.replace("_", " ")
    nchs = DataSource(name=NCHS_SOURCE_NAME, url=NCHS_SOURCE_URL)

    findings: List[FindingItem] = []

    all_ages_rate = _get_rate(race, "all_ages")
    if all_ages_rate is None:
        return findings

    findings.append(FindingItem(
        label=f"Maternal Mortality Rate \u2014 {race}",
        detail=(
            f"In {NCHS_LATEST_YEAR}, the maternal mortality rate for {race} women "
            f"in the United States was {all_ages_rate} deaths per 100,000 live births. "
            f"Source: {NCHS_SOURCE_NAME}."
        ),
        confidence="M",
        sources=[nchs],
    ))

    cohort_rate = _get_rate(race, age_group)
    if cohort_rate is not None:
        ratio = cohort_rate / all_ages_rate if all_ages_rate > 0 else 0.0
        jump_text = ""
        if ratio >= COHORT_JUMP_THRESHOLD:
            multiplier = _approx_multiplier(cohort_rate, all_ages_rate)
            jump_text = (
                f" The {race} {cohort_label_human} MMR ({cohort_rate} per 100K) is approximately "
                f"{multiplier} times the {race} all-ages baseline "
                f"({all_ages_rate} per 100K), reflecting age-cohort risk."
            )
        findings.append(FindingItem(
            label=f"Age-Cohort Mortality Risk \u2014 {race}, {cohort_label_human}",
            detail=(
                f"For {race} women in the {cohort_label_human} cohort, "
                f"the {NCHS_LATEST_YEAR} mortality rate was {cohort_rate} deaths per 100,000 live births."
                f"{jump_text} Source: {NCHS_SOURCE_NAME}."
            ),
            confidence="M",
            sources=[nchs],
        ))
    else:
        findings.append(FindingItem(
            label=f"Age-Cohort Mortality Risk \u2014 {race}, {cohort_label_human}",
            detail=(
                f"Cohort-specific rate for {race} women in the {cohort_label_human} cohort "
                f"is suppressed in NCHS data due to small case counts (NCHS reliability standard); "
                f"using the {race} all-ages rate of {all_ages_rate} per 100,000 live births as a baseline. "
                f"Source: {NCHS_SOURCE_NAME}."
            ),
            confidence="M",
            sources=[nchs],
        ))

    if race != COMPARISON_RACE:
        comparison_rate = _get_rate(COMPARISON_RACE, "all_ages")
        if comparison_rate is not None and comparison_rate > 0:
            multiplier = _approx_multiplier(all_ages_rate, comparison_rate)
            findings.append(FindingItem(
                label=f"Racial Disparity \u2014 {race} vs {COMPARISON_RACE}",
                detail=(
                    f"In {NCHS_LATEST_YEAR}, the all-ages maternal mortality rate for {race} women "
                    f"({all_ages_rate} per 100K) is approximately {multiplier} times the rate "
                    f"for {COMPARISON_RACE} women ({comparison_rate} per 100K). "
                    f"Source: {NCHS_SOURCE_NAME}."
                ),
                confidence="M",
                sources=[nchs],
            ))

    return findings[:3]


async def run(profile: PatientProfile) -> SubAgentReturn:
    try:
        findings = _build_findings(profile)
        if not findings:
            return SubAgentReturn(
                agent_name=AGENT_NAME,
                status="failed",
                error_message=(
                    f"No NCHS mortality data for race_ethnicity '{profile.race_ethnicity}' "
                    f"in year {NCHS_LATEST_YEAR}"
                ),
            )
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="success",
            findings=findings,
        )
    except Exception as exc:
        logger.exception("Mortality subagent failed")
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="failed",
            error_message=f"Mortality subagent error: {exc}",
        )
