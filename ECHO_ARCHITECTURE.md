# ECHO_ARCHITECTURE.md — Node Map & Design Decisions
**Version:** 2.2 | **Project:** ECHO — Early Care Handoff Observer
**Team:** Luba Kaper · Paula · Jonel

---

## Changes from v2.1

This version applies the data and licensing decisions captured in `ECHO_v2_data_summary.md`. Three things changed:

1. **N4 (Guideline) data source:** AWHONN POST-BIRTH replaced by CDC Hear Her urgent maternal warning signs. POST-BIRTH is licensed; Hear Her is public domain and covers the same clinical ground.
2. **N12 renamed and rescoped:** Was "AWHONN SBAR Library." Now "Communication Framing Library" containing original framing copy grounded in public-domain sources. AWHONN is cited as a "see also" reference link, never reproduced.
3. **Subagent 4 (Guideline) excerpt rule:** ACOG Committee Opinion 736 excerpts must stay under approximately 100 words per finding with inline attribution.

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
            - Loads Communication Framing Library (N12)
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
**Data:** `nchs_maternal_mortality.csv`, NY MMRB, TX MMRB

- Filters by race_ethnicity and state
- Returns top 3 leading causes of maternal mortality with MMR values
- confidence = H if 2+ sources confirm same cause, M if 1 source, L if extrapolated

---

### N4 — Guideline Subagent
**File:** `backend/subagents/guideline.py`
**Owner:** Luba
**Data:** `acog_4th_trimester.json`, `cdc_hear_her_signs.json`

- Loads ACOG postpartum care timeline filtered by weeks_postpartum
- Loads CDC Hear Her urgent warning signs — always returns the full set
- Elevates matching signs if complications_flagged is not empty
- Never filters out signs

**Excerpt rule:** ACOG Committee Opinion 736 excerpts must stay under approximately 100 words per finding with inline attribution. CDC Hear Her content has no excerpt limit. The subagent enforces the cap when constructing FindingItems.

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
**Data:** `cms_birthing_friendly.csv`, `cms_hcahps_ny.csv`, `cms_core_set_ny_2023.xlsx`, `cms_core_set_tx_2023.xlsx`

- Matches hospital_name + state against CMS Birthing-Friendly dataset (per-hospital signal)
- Pulls HCAHPS discharge information score for matched hospital (NY hospitals)
- Pulls state-level Core Set PPC-AD postpartum care visit rate from the matching state file
- If hospital not found: status = partial, pipeline continues (not a failure)

---

### N7 — State Context Subagent
**File:** `backend/subagents/state_context.py`
**Owner:** Jonel
**Data:** `kff_postpartum_coverage.csv`, `nnpqc_funding.csv`, static reference

- Returns Medicaid 12-month extension status for patient's state
- Returns state QI infrastructure context from NNPQC funding data
- NY: includes NYSPQC perinatal QI context note
- TX: includes TCHMB maternal health context note

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
- Loads matching framing copy from `framing_library.json` by patient identity dimensions (N12)
- Builds prompt and calls Anthropic API
- Model: `claude-sonnet-4-20250514` | max_tokens: 2000 | no streaming
- Validates every ChecklistItem has all required fields
- Returns ChecklistOutput

**Licensing rule:** The system prompt instructs the model to write original framing copy grounded in cited public-domain sources, not to reproduce or paraphrase AWHONN content. AWHONN appears only as a "see also" reference link at the bottom of the framing block.

---

### N12 — Communication Framing Library
**File:** `backend/data/static/framing_library.json`
**Owner:** Luba

- Original framing copy keyed by patient identity dimensions (race/ethnicity, payer, complications, language)
- Grounded in public-domain sources: CDC, peer-reviewed literature, federal guidance
- Never reproduces or paraphrases AWHONN content
- AWHONN appears as a "see also" reference link only (`awhonn.org/awhonn-sbars`)
- Used by N11 to fold patient-tailored communication guidance into the checklist

**Why this exists, not a 6th subagent:** A full 6th subagent would carry architectural cost (new contract, new Risk Synthesist screening rule, new failure modes, new tests). The framing value does not require that cost. It needs original copy in the output, sourced from public-domain materials and structured by patient identity. v3 is where this could be promoted to a full Respectful Care subagent if an AWHONN license is pursued.

---

### N13 — Checklist Display
**File:** `frontend/checklist.html`
**Owner:** Paula

Display order (always):
1. Patient context header (no name or MRN — age range, race/ethnicity, payer, state, weeks postpartum)
2. Prioritized warning signs (CDC Hear Her urgent signs, ordered by priority_rank)
3. SDOH screening flags (CMS AHC HRSN domains)
4. Hospital commitment status (Birthing-Friendly + HCAHPS + Core Set state-level)
5. Conflict flags (FLAGGED findings — always show both data points)
6. Communication framing block (from `framing_library.json`, with AWHONN cited as "see also" reference link)
7. Data confidence summary
8. Clinical disclaimer (hardcoded, always at bottom, never modified)

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
| Communication Framing Library (N12) is original work | AWHONN content cannot be reproduced commercially. Original copy grounded in public-domain sources is defensible and licensable for v3 if needed. |
| CDC Hear Her replaces AWHONN POST-BIRTH | Hear Her is public domain and covers the same clinical ground |
| ACOG excerpts capped at ~100 words per finding | ACOG permits short excerpts with attribution; longer reproductions require written permission |
| disparity_flag for Black patients in NY/TX | These states have documented elevated MMR for Black patients |

---

## Data Sources

| Source | Node | Data | License |
|---|---|---|---|
| NCHS Health E-Stat 113 | N3 | National maternal mortality rates by race and age | Public domain |
| NY MMRB | N3 | New York Maternal Mortality Review Board data | Public domain |
| TX MMRB / TCHMB | N3, N7 | Texas maternal mortality and QI context | Public domain |
| CDC Hear Her | N4 | Urgent maternal warning signs | Public domain |
| ACOG Committee Opinion 736 | N4 | Postpartum care timeline by weeks (excerpts under ~100 words) | Licensed; excerpt rule applies |
| AIM Postpartum Discharge Bundle v2.0 | N4 | Structured measures hospitals report on | Public domain |
| CMS AHC HRSN | N5 | 10 SDOH screening domains | Public domain |
| CMS Birthing-Friendly (geocoded) | N6 | Per-hospital designation status | Public domain |
| CMS HCAHPS (NY) | N6 | Hospital consumer experience scores | Public domain |
| CMS Core Set (NY, TX) | N6 | State-level Medicaid quality measures including PPC-AD | Public domain |
| KFF Postpartum Coverage Tracker | N7 | Medicaid 12-month extension status by state | Public domain |
| NNPQC Funding | N7 | National Network of Perinatal QI Collaboratives funding | Public domain |
| AWHONN | N12 | Cited as "see also" reference link only. Not reproduced or paraphrased. | Licensed; reference-only use |

---

## Out of Scope (v3 Considerations)

- **Autonomous care team email send.** Drawn dashed in early architecture diagrams as N14. Not built in v2. Provisional owner if pursued: Paula.
- **AWHONN license for embedded SBAR content.** If the demo lands and we want to embed AWHONN SBAR text directly in the framing block, contact `permissions@awhonn.org`. Facility license starts at $300 per facility for the full RMC framework.
- **Per-hospital AIM bundle adoption data.** Login-gated, not scrapeable at scale.
- **EHR integration.** Out of scope for v2. Pipeline is designed to be EHR-agnostic.
- **HIPAA-compliant persistent storage.** Not built. v2 is session-only with no PHI logging.
