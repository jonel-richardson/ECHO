"""N6 — Bundle subagent.

Loads three hospital-bundle data sources at module import (CMS Birthing-Friendly
designation list, CMS HCAHPS NY discharge-information scores, and the per-state
CMS Medicaid Adult Core Set PPC-AD workbook) and returns up to 4 FindingItems
describing the patient's hospital and state-level postpartum-care environment.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from backend.constants import (
    CMS_BIRTHING_FRIENDLY_SOURCE_NAME,
    CMS_BIRTHING_FRIENDLY_SOURCE_URL,
    CMS_CORE_SET_SOURCE_NAME,
    CMS_CORE_SET_SOURCE_URL,
    CMS_HCAHPS_SOURCE_NAME,
    CMS_HCAHPS_SOURCE_URL,
    HCAHPS_DISCHARGE_MEASURE_ID,
    PPC_AD_LATEST_YEAR,
    PPC_AD_SHEET_NAME,
    STATE_NAMES,
    SUPPORTED_STATES,
)
from backend.schemas import DataSource, FindingItem, PatientProfile, SubAgentReturn


logger = logging.getLogger(__name__)

AGENT_NAME = "bundle"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BF_CSV_PATH = DATA_DIR / "cms_birthing_friendly_geocoded.csv"
HCAHPS_CSV_PATH = DATA_DIR / "cms_hcahps_ny.csv"
CORE_SET_PATHS = {
    "NY": DATA_DIR / "cms_core_set_ny_2023.xlsx",
    "TX": DATA_DIR / "cms_core_set_tx_2023.xlsx",
}

# Suffixes stripped during hospital-name normalization (longest-first so
# "memorial hospital" wins over "hospital"). Lowercased; matched against the
# trailing portion of an already-lowercased candidate.
_NAME_SUFFIXES = (
    "hospital center",
    "memorial hospital",
    "general hospital",
    "medical center",
    "health system",
    "hospital",
    "medical",
    "health",
    "center",
)


def _load_hcahps_discharge() -> pd.DataFrame:
    df = pd.read_csv(HCAHPS_CSV_PATH)
    return df[df["HCAHPS Measure ID"] == HCAHPS_DISCHARGE_MEASURE_ID].copy()


def _load_core_set(state: str) -> dict:
    df = pd.read_excel(CORE_SET_PATHS[state], sheet_name=PPC_AD_SHEET_NAME, header=2)
    row = df[df["Data Period"] == PPC_AD_LATEST_YEAR].iloc[0]
    return {
        "value": float(row["Value"]),
        "median": float(row["Median"]),
        "first_quartile": float(row["First quartile"]),
        "third_quartile": float(row["Third quartile"]),
    }


_BF_DF = pd.read_csv(BF_CSV_PATH)
_HCAHPS_DF = _load_hcahps_discharge()
_PPC_AD = {state: _load_core_set(state) for state in SUPPORTED_STATES}


def _normalize_name(name: str) -> str:
    """Lowercase, drop a leading 'the ', strip one trailing common suffix."""
    if not isinstance(name, str):
        return ""
    n = " ".join(name.strip().lower().split())
    if n.startswith("the "):
        n = n[4:]
    for suffix in _NAME_SUFFIXES:
        if n.endswith(" " + suffix):
            n = n[: -(len(suffix) + 1)]
            break
    return n.strip()


def _match_hospital(target: str, candidates: pd.Series) -> Optional[int]:
    """Return the candidates label-index of the best name match, or None.

    First pass: exact match on normalized form. Second pass: substring contains
    in either direction. Both passes ignore case and whitespace via _normalize_name.
    """
    target_norm = _normalize_name(target)
    if not target_norm or candidates.empty:
        return None
    norms = candidates.apply(_normalize_name)
    exact = norms[norms == target_norm]
    if len(exact):
        return int(exact.index[0])
    contains = norms[norms.apply(
        lambda c: bool(c) and (target_norm in c or c in target_norm)
    )]
    if len(contains):
        return int(contains.index[0])
    return None


def _bf_finding(state: str, hospital_name: str) -> Tuple[FindingItem, bool]:
    state_pool = _BF_DF[_BF_DF["state"] == state]
    idx = (
        _match_hospital(hospital_name, state_pool["name"])
        if not state_pool.empty
        else None
    )
    if idx is not None:
        designated_name = state_pool.loc[idx, "name"]
        detail = (
            f"{hospital_name} (matched as '{designated_name}') is included in the CMS "
            f"Birthing-Friendly Hospital Designation list. The designation reflects "
            f"participation in a structured statewide or national perinatal "
            f"quality-improvement collaborative and adoption of evidence-based maternal "
            f"safety practices."
        )
        return FindingItem(
            label="CMS Birthing-Friendly Designation \u2014 Designated",
            detail=detail,
            confidence="M",
            sources=[DataSource(
                name=CMS_BIRTHING_FRIENDLY_SOURCE_NAME,
                url=CMS_BIRTHING_FRIENDLY_SOURCE_URL,
            )],
        ), True
    detail = (
        f"{hospital_name} was not located in the CMS Birthing-Friendly Hospital "
        f"Designation list for {STATE_NAMES[state]}. Hospitals without this designation "
        f"may still meet the criteria but have not been publicly listed by CMS at the "
        f"time of the latest data refresh."
    )
    return FindingItem(
        label="CMS Birthing-Friendly Designation \u2014 Not Designated",
        detail=detail,
        confidence="M",
        sources=[DataSource(
            name=CMS_BIRTHING_FRIENDLY_SOURCE_NAME,
            url=CMS_BIRTHING_FRIENDLY_SOURCE_URL,
        )],
    ), False


def _hcahps_finding(hospital_name: str) -> Optional[FindingItem]:
    idx = _match_hospital(hospital_name, _HCAHPS_DF["Facility Name"])
    if idx is None:
        return None
    row = _HCAHPS_DF.loc[idx]
    score = row["HCAHPS Linear Mean Value"]
    facility = row["Facility Name"]
    detail = (
        f"On the HCAHPS 'Care Transition / Discharge Information' linear-mean composite, "
        f"{hospital_name} (matched as '{facility}') scored {score}. This score reflects "
        f"how patients rated the clarity of discharge information, including written "
        f"instructions and understanding of post-hospital care. Reporting period: "
        f"04/01/2024\u201303/31/2025."
    )
    return FindingItem(
        label="HCAHPS Discharge Information Score",
        detail=detail,
        confidence="M",
        sources=[DataSource(name=CMS_HCAHPS_SOURCE_NAME, url=CMS_HCAHPS_SOURCE_URL)],
    )


def _state_ppc_ad_finding(state: str) -> FindingItem:
    info = _PPC_AD[state]
    state_name = STATE_NAMES[state]
    value_pct = round(info["value"] * 100, 1)
    median_pct = round(info["median"] * 100, 1)
    detail = (
        f"In the {PPC_AD_LATEST_YEAR} CMS Medicaid Adult Core Set, {state_name}'s "
        f"Postpartum Care (PPC-AD) rate \u2014 the percentage of Medicaid live-birth "
        f"deliveries with a postpartum visit between 7 and 84 days after delivery \u2014 "
        f"was {value_pct}%. The cross-state median for the same reporting cycle was "
        f"{median_pct}%."
    )
    return FindingItem(
        label=f"Medicaid PPC-AD Rate \u2014 {state_name} ({PPC_AD_LATEST_YEAR})",
        detail=detail,
        confidence="M",
        sources=[DataSource(name=CMS_CORE_SET_SOURCE_NAME, url=CMS_CORE_SET_SOURCE_URL)],
    )


def _disparity_finding(state: str) -> FindingItem:
    ny = _PPC_AD["NY"]
    tx = _PPC_AD["TX"]
    ny_pct = round(ny["value"] * 100, 1)
    tx_pct = round(tx["value"] * 100, 1)
    median_pct = round(ny["median"] * 100, 1)
    detail = (
        f"Cross-state Medicaid PPC-AD comparison for the {PPC_AD_LATEST_YEAR} reporting "
        f"cycle: New York {ny_pct}%, Texas {tx_pct}%. The cross-state median was "
        f"{median_pct}%. Patient is in {STATE_NAMES[state]}; differences in "
        f"postpartum-visit attendance between states reflect a mix of coverage policy, "
        f"access, and care-coordination factors and are commonly stratified by "
        f"race/ethnicity in state PRAMS reporting."
    )
    return FindingItem(
        label="Cross-State Postpartum Care Disparity Context",
        detail=detail,
        confidence="M",
        sources=[DataSource(name=CMS_CORE_SET_SOURCE_NAME, url=CMS_CORE_SET_SOURCE_URL)],
    )


def _build_findings(profile: PatientProfile) -> Tuple[str, List[FindingItem]]:
    state = profile.state
    if state not in SUPPORTED_STATES:
        limitation = FindingItem(
            label="State Hospital-Bundle Limitation",
            detail=(
                f"ECHO v2 supports detailed hospital-bundle context only for New York "
                f"and Texas. Patient's state is '{state}'. CMS Birthing-Friendly, HCAHPS, "
                f"and Medicaid Core Set findings were not loaded for this state."
            ),
            confidence="M",
            sources=[DataSource(name="ECHO v2 scope", url=None)],
        )
        return "partial", [limitation]

    findings: List[FindingItem] = []
    bf_finding, bf_matched = _bf_finding(state, profile.hospital_name)
    findings.append(bf_finding)

    hcahps_matched = False
    if state == "NY":
        hcahps = _hcahps_finding(profile.hospital_name)
        if hcahps is not None:
            findings.append(hcahps)
            hcahps_matched = True

    findings.append(_state_ppc_ad_finding(state))
    findings.append(_disparity_finding(state))

    hospital_found = bf_matched or (state == "NY" and hcahps_matched)
    status = "success" if hospital_found else "partial"
    return status, findings[:4]


async def run(profile: PatientProfile) -> SubAgentReturn:
    try:
        status, findings = _build_findings(profile)
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status=status,
            findings=findings,
        )
    except Exception as exc:
        logger.exception("Bundle subagent failed")
        return SubAgentReturn(
            agent_name=AGENT_NAME,
            status="failed",
            error_message=f"Bundle subagent error: {exc}",
        )
