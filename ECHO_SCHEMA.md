# ECHO_SCHEMA.md — Data Object Definitions
**Version:** 2.2 | **Project:** ECHO — Early Care Handoff Observer
**Owner:** Luba (schema files in `/backend/schemas/`)

> All schema files live at `/backend/schemas/`. These are Python dataclasses.
> Build these first — everything else depends on them.
>
> A schema change is a contract change. Read every file that imports the schema before editing it. Update this document before changing the code.

---

## Changes from v2.1

- Data flow summary updated to reference N12 by its new name (Communication Framing Library).
- Added licensing notes on `DataSource` and `ChecklistItem.source` so the constraint is visible to anyone reading the schema.
- No structural changes to any class. Existing code that uses these schemas does not need to change.

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
| `detail` | str | 1-2 sentence clinical detail. ACOG-sourced details stay under approximately 100 words with inline attribution. |
| `confidence` | str | "H" \| "M" \| "L" |
| `sources` | list[DataSource] | One or more data sources supporting this finding. Every finding must have at least one source. |

---

## DataSource
**File:** `/backend/schemas/subagent_return.py` (nested in FindingItem)

| Field | Type | Values / Notes |
|---|---|---|
| `name` | str | Source name, e.g. "NCHS Health E-Stat 113", "CDC Hear Her", "ACOG Committee Opinion 736" |
| `url` | str \| None | Link to source if publicly available |

**Licensing note:** `name` must reference the actual source the finding traces to. Subagents cite public-domain sources directly (CDC, NCHS, CMS, KFF, NNPQC). ACOG content appears as a citation with the corresponding excerpt held to under approximately 100 words in the parent FindingItem.detail. AWHONN is never cited as a `DataSource` in v2 because no AWHONN content is reproduced in the pipeline. AWHONN appears only as a "see also" reference link in the rendered output (N13), not as a finding source.

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
| `framing_block` | FramingBlock | Communication framing copy for this patient identity |
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
| `action` | str | Begins with "Consider screening for..." Never "Patient has..." or "Diagnose..." |
| `source` | str | Federal source or professional body name. Must trace to a real document in `/backend/data/`. |
| `confidence` | str | "H" \| "M" \| "L" \| "FLAGGED" |
| `priority_rank` | int | 1 = highest urgency. Set by Output Generator based on patient profile |

**Licensing note:** `source` is non-empty for every ChecklistItem. No invented citations. AWHONN never appears as a `source`. If the model attempts to cite AWHONN as a finding source, the Output Generator's validation rejects the output.

---

## FramingBlock
**File:** `/backend/schemas/checklist_output.py` (nested in ChecklistOutput)
**Sourced from:** N12 (Communication Framing Library)

| Field | Type | Values / Notes |
|---|---|---|
| `framing_copy` | str | Original communication framing for the CNM. Grounded in public-domain sources. |
| `framing_sources` | list[DataSource] | Public-domain sources the framing is grounded in (CDC, peer-reviewed literature) |
| `see_also` | list[str] | "See also" reference links. AWHONN URL appears here, never reproduced inline. |

**Licensing note:** `framing_copy` is original work. Never reproduces or paraphrases AWHONN content. The Output Generator's system prompt enforces this.

---

## HospitalStatus
**File:** `/backend/schemas/checklist_output.py` (nested in ChecklistOutput)

| Field | Type | Values / Notes |
|---|---|---|
| `hospital_name` | str | Name matched from PatientProfile |
| `birthing_friendly` | str | "Meets criteria" \| "Does not meet criteria" \| "Not found in CMS dataset" |
| `hcahps_discharge_score` | float \| None | Discharge information measure score. None if hospital not found. |
| `state_postpartum_visit_rate` | float \| None | State-level PPC-AD rate from CMS Core Set. None if state not in scope. |
| `status` | str | "success" \| "partial" |

---

## Data Flow Summary

```
PatientProfile (N1 form input)
  → Orchestrator N2 (validates)
  → [N3, N4, N5, N6, N7] parallel dispatch
  → each returns SubAgentReturn
  → Fallback N9 (handles failures, creates gap flags)
  → Risk Synthesist N8 → SynthesistOutput
  → Scorer N10 → ScoredOutput
  → Output Generator N11 → loads framing from N12 → ChecklistOutput
  → Frontend N13 (renders checklist)
```

---

## Validation Rules Summary

These rules are enforced by the schema or by the layer that produces the schema. If any rule is violated, the layer raises or returns a failure status.

| Rule | Where enforced |
|---|---|
| All 8 PatientProfile fields are required | N2 (Orchestrator validation) |
| Subagents never raise; on error, return `status: "failed"` with error_message | Each subagent (N3-N7) |
| Every FindingItem has at least one DataSource | Each subagent before return |
| ACOG-sourced FindingItem.detail stays under approximately 100 words | N4 (Guideline subagent) |
| Conflicting findings get confidence = "FLAGGED" with both data points preserved | N8 (Risk Synthesist) |
| Every ChecklistItem has a non-empty `source` field | N11 (Output Generator validation) |
| AWHONN never appears as a `DataSource.name` or `ChecklistItem.source` | N11 (Output Generator validation) |
| Action language begins with "Consider screening for..." | N11 system prompt + validation |
| Clinical disclaimer text is exact and never modified | Hardcoded in ChecklistOutput construction |
