# ECHO_ARCHITECTURE.md — Node Map & Design Decisions
**Version:** 2.1 | **Project:** ECHO — Early Care Handoff Observer
**Team:** Luba Kaper · Paula · Jonel

---

## System Overview

ECHO is a linear pipeline with one parallel dispatch stage. The frontend sends a single POST request. The backend validates input, fans out to 5 subagents simultaneously, synthesizes results, scores output, and calls the Anthropic API once to generate the final checklist. Total pipeline target: under 30 seconds.

---

## Node Map

```
[Browser]
    |
    | POST /generate-checklist (PatientProfile JSON)
    v
[N1] CNM Input Form (index.html)
    |
    v
[N2] Orchestrator (orchestrator.py)
    - Validates PatientProfile schema
    - Fails loud on missing fields
    - Dispatches N3-N7 via asyncio.gather (25s timeout)
    |
    |---------------------------------------|
    v           v         v        v        v
  [N3]        [N4]      [N5]    [N6]      [N7]
Mortality  Guideline   SDOH    Bundle  State Context
(mortality.py)(guideline.py)(sdoh.py)(bundle.py)(state_context.py)
    |           |         |        |        |
    |---------------------------------------|
                    |
                    v
            [N9] Fallback Handler (fallback.py)
            - Catches failed subagents
            - Creates gap flags
            - Never raises — pipeline always continues
                    |
                    v
            [N8] Risk Synthesist (risk_synthesist.py)
            - Conflict detection across findings
            - Confidence rating
            - Returns SynthesistOutput
                    |
                    v
            [N10] Scorer (scorer.py)
            - gap_score, urgency_tier, disparity_flag
            - Returns ScoredOutput
                    |
                    v
            [N11] Output Generator (output_generator.py)
            - Loads AWHONN SBAR framing (N12)
            - Calls Anthropic API (claude-sonnet-4-20250514)
            - Returns ChecklistOutput
                    |
                    v
            [N13] Checklist Display (checklist.html)
            - Renders one-page provider checklist
            - Source citations on every item
            - Clinical disclaimer always at bottom
```

---

## Node Definitions

### N1 — CNM Input Form
**File:** `frontend/index.html`
**Owner:** Paula

- 8 required input fields matching PatientProfile schema
- Client-side validation before fetch
- POST to `/generate-checklist`
- Loading state during pipeline execution
- Error display for validation, timeout, or API errors

---

### N2 — Orchestrator
**File:** `backend/orchestrator.py`
**Owner:** Jonel

- Validates raw form data against PatientProfile dataclass
- Returns field-level error if any required field is missing
- Dispatches N3-N7 with `asyncio.gather(..., return_exceptions=True)`
- Wraps gather in `asyncio.wait_for` with 25-second timeout
- Timeout message: "ECHO is taking longer than expected. Please try again."

---

### N3 — Mortality Subagent
**File:** `backend/subagents/mortality.py`
**Owner:** Jonel
**Data:** `nchs_nvss_mortality.csv`, NY MMRB, TX MMRB

- Filters by race_ethnicity and state
- Returns top 3 leading causes of maternal mortality with MMR values
- confidence = H if 2+ sources confirm same cause, M if 1 source, L if extrapolated

---

### N4 — Guideline Subagent
**File:** `backend/subagents/guideline.py`
**Owner:** Luba
**Data:** `acog_4th_trimester.json`, `awhonn_post_birth.json`

- Loads ACOG timeline filtered by weeks_postpartum
- Loads full AWHONN POST-BIRTH 9-sign set — always returns all 9
- Elevates matching signs if complications_flagged is not empty
- Never filters out signs

---

### N5 — SDOH Subagent
**File:** `backend/subagents/sdoh.py`
**Owner:** Luba
**Data:** `cms_hrsn_domains.json`

- Returns all 10 core CMS AHC HRSN domains
- Adds Medicaid note if payer = "Medicaid"
- confidence = M for all SDOH flags

---

### N6 — Bundle Subagent
**File:** `backend/subagents/bundle.py`
**Owner:** Jonel
**Data:** `cms_birthing_friendly.csv`, `cms_hcahps.csv`

- Matches hospital_name + state against CMS Birthing-Friendly dataset
- Pulls HCAHPS discharge information score for matched hospital
- If hospital not found: status = partial, pipeline continues (not a failure)

---

### N7 — State Context Subagent
**File:** `backend/subagents/state_context.py`
**Owner:** Jonel
**Data:** `kff_medicaid_postpartum.csv`, static reference

- Returns Medicaid 12-month extension status for patient's state
- Returns state MMR ranking vs. national average
- NY: includes NNPQC perinatal QI context note
- TX: includes TCHMB maternal health data note

---

### N8 — Risk Synthesist
**File:** `backend/risk_synthesist.py`
**Owner:** Luba

- Receives 5 SubAgentReturn objects (or fewer after fallback)
- Detects contradictions: same finding label + opposite risk direction = FLAGGED
- Counts sources_confirmed per finding — fewer than 2 → confidence = LOW
- Never resolves conflicts silently — always preserves both data points

---

### N9 — Fallback Handler
**File:** `backend/fallback.py`
**Owner:** Luba

- Receives raw asyncio.gather results
- Identifies failed subagents (status = "failed" or raised exception)
- Creates SynthesistFlag with flag_type = "gap" for each failure
- Returns cleaned list + flags to Risk Synthesist
- Never raises — pipeline always continues

---

### N10 — Scorer
**File:** `backend/scorer.py`
**Owner:** Luba

- gap_score = (low/flagged findings + failed agents) ÷ expected total findings
- urgency_tier: HIGH / MED / LOW (see schema for logic)
- disparity_flag: True if race = "Black or African American" AND state IN (NY, TX)
- lead_angle: agent name of highest confidence + urgency finding

---

### N11 — Output Generator
**File:** `backend/output_generator.py`
**Owner:** Paula

- Receives ScoredOutput
- Loads AWHONN SBAR framing from `awhonn_sbar_library.json` by patient identity
- Builds prompt and calls Anthropic API
- Model: `claude-sonnet-4-20250514` | max_tokens: 2000 | no streaming
- Validates every ChecklistItem has all required fields
- Returns ChecklistOutput

---

### N12 — AWHONN SBAR Library
**File:** `backend/data/static/awhonn_sbar_library.json`
**Owner:** Luba

- 11 sourced SBAR framing documents keyed by patient identity dimensions
- Used by N11 to pull pre-sourced communication framing
- Do not generate SBAR framing from scratch — always pull from this library

---

### N13 — Checklist Display
**File:** `frontend/checklist.html`
**Owner:** Paula

Display order (always):
1. Patient context header (no name or MRN — age range, race/ethnicity, payer, state, weeks postpartum)
2. Prioritized warning signs (AWHONN POST-BIRTH 9 signs, ordered by priority_rank)
3. SDOH screening flags (CMS AHC HRSN domains)
4. Hospital commitment status (Birthing-Friendly + HCAHPS)
5. Conflict flags (FLAGGED findings — always show both data points)
6. Data confidence summary
7. Clinical disclaimer (hardcoded, always at bottom, never modified)

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Parallel subagent dispatch via asyncio.gather | Meet the 30-second pipeline target |
| No database writes | Zero PHI persistence — session-only |
| Fail-loud validation at N2 | Surface field errors before any API calls |
| Fallback handler never raises | Partial results are better than a full pipeline crash |
| Conflict detection by exact label matching | Avoids semantic similarity edge cases in Demo Day scope |
| Single Anthropic API call at N11 | One structured prompt → one ChecklistOutput JSON |
| AWHONN SBAR library (N12) | Sourced framing — never generate clinical communication from scratch |
| disparity_flag for Black patients in NY/TX | These states have documented elevated MMR for Black patients |

---

## Data Sources

| Source | Node | Data |
|---|---|---|
| NCHS NVSS | N3 | Maternal mortality rates by race and state |
| NY MMRB | N3 | New York Maternal Mortality Review Board data |
| TX MMRB | N3 | Texas Maternal Mortality Review Board data |
| AWHONN POST-BIRTH | N4 | 9 canonical postpartum warning signs |
| ACOG 4th Trimester | N4 | Postpartum care timeline by weeks |
| CMS AHC HRSN | N5 | 10 SDOH screening domains |
| CMS Birthing-Friendly | N6 | Hospital designation status |
| CMS HCAHPS | N6 | Hospital consumer experience scores |
| KFF | N7 | Medicaid postpartum coverage by state |
| NNPQC | N7 | New York perinatal quality context |
| TCHMB | N7 | Texas Child Health and Maternal Benefits data |
