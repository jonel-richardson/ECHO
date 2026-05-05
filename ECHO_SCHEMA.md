# ECHO_SCHEMA.md — Data Object Definitions
**Version:** 2.1 | **Project:** ECHO — Early Care Handoff Observer
**Owner:** Luba (schema files in /backend/schemas/)

> All schema files live at `/backend/schemas/`. These are Python dataclasses.
> Build these first — everything else depends on them.

---

## PatientProfile
**File:** `/backend/schemas/patient_profile.py`
**Node:** N2 (input to Orchestrator)

The 8 fields a CNM enters into the form. All fields are required. The orchestrator fails-loud with a field-level error if any are missing.

| Field | Type | Values / Notes |
|---|---|---|
| `age` | int | Patient age in years |
| `race_ethnicity` | str | e.g. "Black or African American", "White", "Hispanic or Latino" |
| `payer` | str | "Medicaid" \| "Private" \| "Other" |
| `state` | str | 2-letter state code, e.g. "NY", "TX" |
| `hospital_name` | str | Full hospital name as it appears in CMS dataset |
| `weeks_postpartum` | int | Weeks since delivery |
| `complications_flagged` | list[str] | e.g. ["hypertension", "hemorrhage"] — empty list if none |
| `primary_language` | str | e.g. "English", "Spanish" |

---

## SubAgentReturn
**File:** `/backend/schemas/subagent_return.py`
**Returned by:** N3, N4, N5, N6, N7

Every subagent returns this object. The pipeline never raises — a failed subagent returns status = "failed" with an error_message.

| Field | Type | Values / Notes |
|---|---|---|
| `agent_name` | str | "mortality" \| "guideline" \| "sdoh" \| "bundle" \| "state_context" |
| `status` | str | "success" \| "partial" \| "failed" |
| `findings` | list[FindingItem] | Empty list if status = "failed" |
| `error_message` | str \| None | Populated only if status = "failed" |

---

## FindingItem
**File:** `/backend/schemas/subagent_return.py` (nested in SubAgentReturn)

| Field | Type | Values / Notes |
|---|---|---|
| `label` | str | Short finding label, e.g. "Hypertensive Disorder Risk" |
| `detail` | str | 1-2 sentence clinical detail |
| `confidence` | str | "H" \| "M" \| "L" |
| `sources` | list[DataSource] | One or more data sources supporting this finding |

---

## DataSource
**File:** `/backend/schemas/subagent_return.py` (nested in FindingItem)

| Field | Type | Values / Notes |
|---|---|---|
| `name` | str | Source name, e.g. "NCHS NVSS 2021" |
| `url` | str \| None | Link to source if publicly available |

---

## SynthesistOutput
**File:** `/backend/schemas/synthesist_output.py`
**Node:** N8 (Risk Synthesist output)

| Field | Type | Values / Notes |
|---|---|---|
| `findings` | list[FindingItem] | Conflict-screened, deduplicated findings |
| `conflicts` | list[SynthesistFlag] | Flagged contradictions between subagents |
| `subagents_completed` | int | Count of subagents that returned success or partial |
| `subagents_failed` | list[str] | Names of subagents that returned status = "failed" |

---

## SynthesistFlag
**File:** `/backend/schemas/synthesist_output.py` (nested in SynthesistOutput)

| Field | Type | Values / Notes |
|---|---|---|
| `flag_type` | str | "conflict" \| "gap" |
| `label` | str | Finding label that triggered the flag |
| `detail` | str | Description of the conflict or gap |
| `agents_involved` | list[str] | Agent names involved in the conflict |

---

## ScoredOutput
**File:** `/backend/schemas/scored_output.py`
**Node:** N10 (Scorer output)

| Field | Type | Values / Notes |
|---|---|---|
| `synthesist_output` | SynthesistOutput | Full synthesist output passed through |
| `gap_score` | float | 0.0–1.0. Count of low/flagged findings + failed agents ÷ expected total |
| `urgency_tier` | str | "HIGH" \| "MED" \| "LOW" |
| `disparity_flag` | bool | True if race_ethnicity = "Black or African American" AND state IN (NY, TX) |
| `lead_angle` | str | Agent name of the highest-confidence, highest-urgency finding |
| `patient_profile` | PatientProfile | Original patient input passed through |

**urgency_tier logic:**
- HIGH: complications_flagged is not empty AND Mortality returned H or M confidence
- MED: no complications AND (disparity_flag = True OR any subagent returned partial)
- LOW: no complications, no elevated disparity signal, all subagents success

---

## ChecklistOutput
**File:** `/backend/schemas/checklist_output.py`
**Node:** N11 (Output Generator output) → N13 (Frontend display)

| Field | Type | Values / Notes |
|---|---|---|
| `items` | list[ChecklistItem] | Full checklist, ordered by priority_rank |
| `hospital_status` | HospitalStatus | CMS Birthing-Friendly + HCAHPS result |
| `conflict_flags` | list[SynthesistFlag] | FLAGGED items from synthesist — always shown |
| `confidence_summary` | str | 1-2 sentence summary of data confidence |
| `clinical_disclaimer` | str | Hardcoded — see below. Never modify. |

**Clinical disclaimer (exact, do not modify):**
> "ECHO is clinical decision support, not a diagnostic engine. All items are for clinical review only. Action language reflects screening guidance — not a diagnosis or treatment recommendation. Source citations are provided for every item. CNM clinical judgment governs all care decisions."

---

## ChecklistItem
**File:** `/backend/schemas/checklist_output.py` (nested in ChecklistOutput)

| Field | Type | Values / Notes |
|---|---|---|
| `label` | str | Warning sign or screening item label |
| `detail` | str | 1-2 sentence clinical detail |
| `action` | str | Begins with "Consider screening for..." |
| `source` | str | Federal source or professional body name |
| `confidence` | str | "H" \| "M" \| "L" \| "FLAGGED" |
| `priority_rank` | int | 1 = highest urgency. Set by Output Generator based on patient profile |

---

## HospitalStatus
**File:** `/backend/schemas/checklist_output.py` (nested in ChecklistOutput)

| Field | Type | Values / Notes |
|---|---|---|
| `hospital_name` | str | Name matched from PatientProfile |
| `birthing_friendly` | str | "Meets criteria" \| "Does not meet criteria" \| "Not found in CMS dataset" |
| `hcahps_discharge_score` | float \| None | Discharge information measure score. None if hospital not found |
| `status` | str | "success" \| "partial" |

---

## Data Flow Summary

```
PatientProfile (N1 form input)
  → Orchestrator N2 (validates)
  → [N3, N4, N5, N6, N7] parallel dispatch
  → each returns SubAgentReturn
  → Fallback N9 (handles failures)
  → Risk Synthesist N8 → SynthesistOutput
  → Scorer N10 → ScoredOutput
  → Output Generator N11 → ChecklistOutput
  → Frontend N13 (renders checklist)
```
