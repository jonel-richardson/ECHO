# ECHO_BUILD_PLAN.md — Phase 1 Build Steps by Owner
**Version:** 2.2 | **Project:** ECHO — Early Care Handoff Observer
**Team:** Luba Kaper · Paula · Jonel

> Build in this exact sequence. Each step must be complete and tested before the next begins.
> Every function must have a unit test before handoff.

---

## Changes from v2.1

This version applies the data and licensing decisions captured in `data_summary.md`. Three things changed:

1. **AWHONN POST-BIRTH replaced by CDC Hear Her warning signs.** AWHONN POST-BIRTH is licensed and cannot be reproduced in a commercial tool. CDC Hear Her covers the same clinical ground and is public domain.
2. **AWHONN SBAR Library replaced by an original Communication Framing Library.** AWHONN's Terms of Use prohibit reproduction of SBAR content in a commercial environment. The framing library uses original copy grounded in public-domain sources (CDC, peer-reviewed literature). AWHONN is cited as a "see also" reference link only.
3. **ACOG excerpt cap added.** ACOG permits excerpts under approximately 100 words with attribution. Subagent 4 enforces this rule when constructing findings from ACOG Committee Opinion 736.

---

## Step 1 — Schemas
**Owner:** Luba | **Dependencies:** None

Build all dataclasses in `/backend/schemas/` first. Everything else depends on them.

| File | Class(es) |
|---|---|
| `patient_profile.py` | PatientProfile |
| `subagent_return.py` | SubAgentReturn, FindingItem, DataSource |
| `synthesist_output.py` | SynthesistOutput, SynthesistFlag |
| `scored_output.py` | ScoredOutput |
| `checklist_output.py` | ChecklistOutput, ChecklistItem, HospitalStatus |

**Done when:** Each class instantiates with valid data. Invalid data raises a clear validation error.

---

## Step 2 — Static Data Files
**Owner:** Jonel (CMS CSVs) + Luba (clinical static JSON)
**Dependencies:** None

Curate and validate all files in `/backend/data/` and `/backend/data/static/`.

| File | Content | License |
|---|---|---|
| `cms_birthing_friendly_geocoded.csv` | CMS Birthing-Friendly hospital designations (geocoded) | Public domain |
| `cms_hcahps_ny.csv` | NY HCAHPS discharge information scores | Public domain |
| `cms_core_set_ny_2023.xlsx` | NY Medicaid quality measures (sheet 52. PPC-AD is headline) | Public domain |
| `cms_core_set_tx_2023.xlsx` | TX Medicaid quality measures (sheet 52. PPC-AD is headline) | Public domain |
| `kff_postpartum_coverage.csv` | Medicaid 12-month extension status by state | Public domain |
| `nnpqc_funding.csv` | National Network of Perinatal Quality Collaboratives funding | Public domain |
| `nchs_maternal_mortality.csv` | Maternal mortality rates by race and age, transcribed from Health E-Stat 113 PDF table | Public domain |
| `cdc_hear_her_warning_signs.json` | CDC Hear Her urgent maternal warning signs | Public domain |
| `acog_4th_trimester.json` | Discrete excerpts from ACOG Committee Opinion 736, each under ~100 words, with inline attribution | Licensed (excerpt rule applies) |
| `cms_hrsn_domains.json` | 10 core + 8 supplemental SDOH domains from CMS AHC HRSN Screening Tool | Public domain |
| `framing_library.json` | Original communication framing copy keyed by patient identity dimensions, grounded in public-domain sources, with AWHONN cited as a "see also" reference link | Original work |

### Licensing rules for Step 2

- **CDC, NCHS, CMS, KFF, NNPQC, TCHMB content is public domain.** Use freely. No attribution requirement beyond standard citation.
- **ACOG Committee Opinion 736 excerpts must stay under ~100 words per finding** with inline attribution. Anything longer requires written permission from ACOG.
- **AWHONN content cannot be reproduced or paraphrased.** ECHO references AWHONN as a "see also" pointer with a URL (`awhonn.org/awhonn-sbars`). Original framing copy is grounded in public-domain sources and never paraphrases AWHONN material. Pursuing an AWHONN license is a v3 question.

**Done when:** All files load without error. CSVs have expected columns. JSON files validate against expected structure. No file contains AWHONN-sourced text.

---

## Step 3 — Subagents
**Owner:** Jonel (N3, N6, N7) + Luba (N4, N5)
**Dependencies:** Step 1 (schemas), Step 2 (data files)

Each subagent must:
1. Accept a PatientProfile as input
2. Query its assigned data sources
3. Return a SubAgentReturn object

| File | Node | Owner | Data Sources |
|---|---|---|---|
| `mortality.py` | N3 | Jonel | `nchs_maternal_mortality.csv`, NY MMRB, TX MMRB |
| `guideline.py` | N4 | Luba | `acog_4th_trimester.json`, `cdc_hear_her_warning_signs.json` |
| `sdoh.py` | N5 | Luba | `cms_hrsn_domains.json` |
| `bundle.py` | N6 | Jonel | `cms_birthing_friendly_geocoded.csv`, `cms_hcahps_ny.csv`, `cms_core_set_ny_2023.xlsx`, `cms_core_set_tx_2023.xlsx` |
| `state_context.py` | N7 | Jonel | `kff_postpartum_coverage.csv`, `nnpqc_funding.csv` |

**Subagent 4 (Guideline) excerpt rule:** When constructing findings from ACOG Committee Opinion 736, each excerpt stays under approximately 100 words and includes inline attribution to ACOG. CDC Hear Her content has no excerpt limit.

**Done when:** Each subagent tested individually against both demo fixtures (Maya and Janet) and returns a valid SubAgentReturn.

---

## Step 4 — Fallback Handler
**Owner:** Luba
**Dependencies:** Step 1 (schemas)
**File:** `backend/fallback.py`

- Receives list of SubAgentReturn objects after asyncio.gather completes
- Identifies any with status = "failed" or raised exception
- Creates SynthesistFlag with flag_type = "gap" for each failure
- Returns cleaned list + flags to Risk Synthesist
- Never raises — pipeline always continues

**Done when:** Unit test confirms failed subagent is removed from list, gap flag is created, and pipeline continues with remaining agents.

---

## Step 5 — Risk Synthesist
**Owner:** Luba
**Dependencies:** Step 3 (subagents), Step 4 (fallback)
**File:** `backend/risk_synthesist.py`

1. Receives 5 SubAgentReturn objects (or fewer after fallback)
2. Checks each finding label against all other findings for contradiction
3. Contradiction = same label AND opposite risk direction in detail strings
4. If contradiction: confidence = FLAGGED, create SynthesistFlag, preserve both data points
5. Sets confidence = LOW if fewer than 2 sources_confirmed per finding
6. Returns SynthesistOutput

**Done when:** Unit test confirms conflict detection fires on contradiction and passes on agreement.

---

## Step 6 — Scorer
**Owner:** Luba
**Dependencies:** Step 5 (Risk Synthesist)
**File:** `backend/scorer.py`

1. Receives SynthesistOutput
2. Calculates gap_score
3. Sets urgency_tier (HIGH / MED / LOW)
4. Sets disparity_flag (True if Black + NY or TX)
5. Sets lead_angle
6. Returns ScoredOutput

**Done when:** Maya scenario → disparity_flag = True, urgency = MED or HIGH. Janet (hypertensive) → urgency = HIGH.

**Scorer note:** Because Step 5 downgrades single-source findings to LOW, Janet's HIGH urgency path is based on complications plus a non-FLAGGED mortality signal, not only H/M mortality confidence. See `ECHO_SCHEMA.md` for the scorer contract.

---

## Step 7 — Output Generator
**Owner:** Paula
**Dependencies:** Step 6 (Scorer), Anthropic API key configured
**File:** `backend/output_generator.py`

1. Receives ScoredOutput
2. Loads matching framing copy from `framing_library.json` by patient identity dimensions
3. Builds prompt using the Prompt Template (see CLAUDE.md)
4. Calls Anthropic API: model = `claude-sonnet-4-20250514`, max_tokens = 8000, no streaming
5. Parses and validates ChecklistOutput from response
6. Every ChecklistItem must have: label, detail, action, source, confidence, priority_rank
7. Returns ChecklistOutput

**Output Generator licensing rule:** The system prompt instructs the model to write original framing copy grounded in cited public-domain sources, not to reproduce or paraphrase AWHONN content. AWHONN appears only as a "see also" reference at the bottom of the framing block.

**Done when:** Unit test against both fixtures returns valid ChecklistOutput with all fields populated and clinical disclaimer present.

---

## Step 8 — Orchestrator
**Owner:** Jonel
**Dependencies:** Steps 3–7 (all subagents, fallback, synthesist, scorer, output generator)
**File:** `backend/orchestrator.py`

1. Receives raw form data from frontend
2. Validates against PatientProfile — fail-loud with field-level error if missing
3. Dispatches N3–N7: `results = await asyncio.gather(mortality(p), guideline(p), sdoh(p), bundle(p), state_context(p), return_exceptions=True)`
4. Passes results to fallback (N9)
5. Passes cleaned results to Risk Synthesist (N8)
6. Passes SynthesistOutput to Scorer (N10)
7. Passes ScoredOutput to Output Generator (N11)
8. Returns ChecklistOutput

Timeout: `asyncio.wait_for(gather_call, timeout=25)` — returns: "ECHO is taking longer than expected. Please try again."

**Done when:** Full pipeline runs both fixtures end-to-end and returns ChecklistOutput in under 30 seconds.

---

## Step 9 — FastAPI Entry Point
**Owner:** Jonel
**Dependencies:** Step 8 (Orchestrator)
**File:** `backend/main.py`

Routes:
- `POST /generate-checklist` — accepts PatientProfile JSON, returns ChecklistOutput JSON
- `GET /health` — returns `{"status": "ok"}`

CORS: allow all origins for Demo Day.

**Done when:** Both routes respond correctly. `/health` returns 200. `/generate-checklist` runs full pipeline.

---

## Step 10 — Frontend
**Owner:** Paula
**Dependencies:** Step 9 (FastAPI running)

### index.html (N1)
- 8 required input fields matching PatientProfile
- Client-side validation before fetch
- POST to `/generate-checklist`
- Loading state during processing
- Error display for validation errors, timeout, API errors

### checklist.html (N13)
Display order:
1. Patient context header (no name or MRN)
2. Prioritized warning signs (CDC Hear Her, ordered by priority_rank)
3. SDOH screening flags (CMS AHC HRSN)
4. Hospital commitment status
5. Conflict flags (FLAGGED — show both data points)
6. Communication framing block (from `framing_library.json`, with AWHONN cited as "see also" reference link)
7. Data confidence summary
8. Clinical disclaimer (hardcoded, never modified)

**Done when:** Both demo fixtures render visibly different checklists in the browser. No console errors. Clinical disclaimer present.

---

## End-to-End Test Assertions
**Owner:** All — each owner tests their module before handoff
**File:** `tests/test_end_to_end.py`

- [ ] Pipeline completes in under 30 seconds (both fixtures)
- [ ] All 5 subagents return status = success on demo fixtures
- [ ] 100% of ChecklistItems have a non-empty source field
- [ ] Maya and Janet produce different priority_rank ordering and different disparity_flag values
- [ ] Clinical disclaimer is present in every ChecklistOutput
- [ ] No diagnostic language ("Patient has...", "Diagnose...") in any output string
- [ ] No AWHONN-sourced text appears in any static data file or generated output (AWHONN is cited as a "see also" reference link only)
- [ ] No ACOG excerpt exceeds approximately 100 words

Run: `pytest tests/`
