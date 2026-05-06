# CLAUDE.md — ECHO v2

## 1. Project Overview
- **Name:** ECHO — Early Care Handoff Observer
- **One-liner:** A clinical decision support tool that gives Certified Nurse-Midwives a patient-tailored postpartum screening checklist grounded in federal and professional-body sources.
- **Stack:** Python 3.11+, FastAPI, asyncio, Anthropic SDK (`claude-sonnet-4-20250514`), vanilla HTML/JS frontend (Tailwind via CDN for Demo Day), pytest
- **Deployment:** Local for Demo Day. Open access, no auth. No persistent storage.
- **Repo:** [add GitHub URL]
- **Branch strategy:** Feature branches only. Never merge to main until complete.
- **Branch naming:** `phase-N/short-description` (e.g., `phase-3/mortality-subagent`)

## 2. Confidence Rule
**Do not write or change any code until you reach 95% confidence in what needs to be built.**
- Ask follow-up questions until you hit that threshold.
- State your confidence level and what is unclear before proceeding.
- If a requirement is ambiguous, stop and ask. Never guess.
- Never mock data or fabricate endpoints. If you don't know, ask.
- For ECHO specifically: never invent a federal source citation. Every checklist item must trace to a real document in `/backend/data/`.

## 3. File Index

```
backend/
├── main.py                          — FastAPI entry point. Routes: POST /generate-checklist, GET /health
├── orchestrator.py                  — N2. Validates PatientProfile, dispatches subagents, runs full pipeline
├── fallback.py                      — N9. Catches failed subagents, creates gap flags, never raises
├── risk_synthesist.py               — N8. Conflict detection, confidence rating, dedup
├── scorer.py                        — N10. gap_score, urgency_tier, disparity_flag, lead_angle
├── output_generator.py              — N11. Calls Anthropic API, returns ChecklistOutput
├── subagents/
│   ├── mortality.py                 — N3. NCHS mortality data filtered by race + state
│   ├── guideline.py                 — N4. ACOG 4th trimester + CDC Hear Her warning signs
│   ├── sdoh.py                      — N5. CMS AHC HRSN 10 core domains
│   ├── bundle.py                    — N6. CMS Birthing-Friendly + HCAHPS
│   └── state_context.py             — N7. KFF Medicaid extension + state QI context
├── schemas/
│   ├── patient_profile.py           — PatientProfile (8 input fields)
│   ├── subagent_return.py           — SubAgentReturn, FindingItem, DataSource
│   ├── synthesist_output.py         — SynthesistOutput, SynthesistFlag
│   ├── scored_output.py             — ScoredOutput
│   └── checklist_output.py          — ChecklistOutput, ChecklistItem, HospitalStatus
└── data/
    ├── cms_birthing_friendly.csv    — Per-hospital Birthing-Friendly designation
    ├── cms_hcahps_ny.csv            — NY hospital experience scores
    ├── cms_core_set_ny_2023.xlsx    — NY Medicaid quality measures (sheet 52. PPC-AD is headline)
    ├── cms_core_set_tx_2023.xlsx    — TX Medicaid quality measures (sheet 52. PPC-AD is headline)
    ├── kff_postpartum_coverage.csv  — Medicaid 12-month extension status by state
    ├── nnpqc_funding.csv            — National Network of Perinatal Quality Collaboratives funding
    ├── nchs_maternal_mortality.csv  — Transcribed from hestat113.pdf table
    └── static/
        ├── cdc_hear_her_signs.json  — CDC Hear Her urgent warning signs (public domain)
        ├── acog_4th_trimester.json  — Short excerpts only, < 100 words each, with attribution
        ├── cms_hrsn_domains.json    — 10 core + 8 supplemental SDOH domains (public domain)
        └── framing_library.json     — ORIGINAL framing copy by patient identity, cites public-domain sources, never reproduces AWHONN

frontend/
├── index.html                       — N1. CNM input form (8 fields)
└── checklist.html                   — N13. One-page checklist render

tests/
├── fixtures/
│   ├── maya.json                    — 28y, Black, Medicaid, NY, 6wk pp, no complications
│   └── janet.json                   — 41y, White, Private, TX, 4wk pp, hypertensive disorder
├── test_subagents.py
├── test_synthesist.py
├── test_scorer.py
├── test_output_generator.py
└── test_end_to_end.py

ECHO_SCHEMA.md                       — Schema source of truth (Luba)
ECHO_BUILD_PLAN.md                   — Phased build steps (all)
ECHO_ARCHITECTURE.md                 — Node map and design decisions (all)
ECHO_v2_data_summary.md              — Data manifest (Jonel)
```

> Update this map when a new file or directory is added.

## 4. Build & Dev Commands

```bash
# Backend setup
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1          # Windows PowerShell
source venv/bin/activate              # Mac / Linux

# Install dependencies
pip install -r requirements.txt

# Run dev server (localhost:8000)
uvicorn backend.main:app --reload

# Tests
pytest tests/ -v
pytest tests/test_end_to_end.py       # Full pipeline against fixtures

# Frontend (Demo Day)
# Open frontend/index.html directly. CORS allowed for all origins on the backend.
```

## 5. Coding Conventions

### Architecture
- **Separation of concerns:** Orchestrator dispatches and validates. Subagents fetch and return findings. Synthesist screens. Scorer scores. Output Generator generates. No layer reaches around another.
- **No business logic in `main.py`:** FastAPI routes call the orchestrator and return its result. Nothing else.
- **Centralize constants:** All thresholds (timeout seconds, confidence cutoffs, model name) live in `backend/constants.py`. No magic numbers in functions.
- **Schemas are dataclasses, not dicts:** Every node-to-node handoff uses a typed schema from `/backend/schemas/`. No raw dict passing.

### Error Handling
- Every subagent function wrapped in try/except. On exception: return `SubAgentReturn(status="failed", error_message=...)`. Never raise out of a subagent.
- The fallback handler (N9) is the only layer that catches gather exceptions. Nothing downstream of N9 should ever see a raw exception.
- The orchestrator wraps the gather in `asyncio.wait_for(timeout=25)`. On timeout, return a clear error to the frontend, not a stack trace.
- Anthropic API calls in N11: catch `anthropic.APIError`, surface as a structured error to the frontend.

### Python
- Type hints on every function signature. Return types required.
- Dataclasses with `@dataclass(frozen=True)` for schemas where possible — these objects do not mutate after creation.
- f-strings for formatting. No `%` or `.format()`.
- `pathlib.Path` for file paths, never string concatenation.

### Styling (frontend)
- Tailwind via CDN for Demo Day. No build step.
- Mobile-first responsive. The CNM may view this on a tablet at the bedside.
- One CSS file: `frontend/styles.css` for any tokens that cannot be expressed in Tailwind utilities.

### Git
- Commit messages: `type(scope): description` (e.g., `feat(mortality): add NY MMRB filter`)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- **Never include Co-Authored-By trailers crediting Claude or any AI.** Single-author commits in the contributor's voice with first-person "I" statements.
- One logical change per commit. No "WIP" commits on main.

## 6. Phase Protocol

### Structure
Each phase is not complete until:
1. All acceptance criteria are met
2. All unit tests for that phase pass
3. The phase owner confirms it is done in writing

**Never start Phase N+1 until Phase N is confirmed complete.**

### Phases for ECHO v2

| Phase | Goal | Owner | Status |
|-------|------|-------|--------|
| 1 | Schemas built and tested | Luba | [ ] |
| 2 | Static data files curated and validated | Jonel + Luba | [ ] |
| 3 | All 5 subagents implemented and tested individually | Jonel + Luba | [ ] |
| 4 | Fallback handler complete | Luba | [ ] |
| 5 | Risk Synthesist complete | Luba | [ ] |
| 6 | Scorer complete | Luba | [ ] |
| 7 | Output Generator complete (Anthropic API integrated) | Paula | [ ] |
| 8 | Orchestrator wired end-to-end | Jonel | [ ] |
| 9 | FastAPI entry point exposed | Jonel | [ ] |
| 10 | Frontend form + checklist render | Paula | [ ] |
| 11 | End-to-end tests passing on both fixtures | All | [ ] |

## 7. Read Before Write

Before editing any file:
1. Read its current contents first.
2. After any successful edit, the previous view is stale. Re-read before making another edit to the same file.
3. Never assume file state from memory or earlier context.
4. For schema files specifically: a schema change is a contract change. Read every file that imports the schema before editing it.

## 8. Change Protocol

When a direction change is needed:
1. I describe the change.
2. You confirm understanding and list affected files (across schemas, subagents, tests, docs).
3. I approve the direction.
4. You update all affected files including ECHO_SCHEMA.md, ECHO_BUILD_PLAN.md, ECHO_ARCHITECTURE.md, and the data manifest if relevant.
5. You provide a summary of every change.
6. You provide a detailed commit message at the end of the summary.

**No commit happens without a summary first.**

## 9. Summary & Commit Format

```
### Summary
- What changed and why
- Files added/modified/deleted
- Any open questions or follow-ups

### Commit
git add [files]
git commit -m "type(scope): concise description

- Detail 1
- Detail 2
- Detail 3"
```

Reminder: no Co-Authored-By trailers.

## 10. Compaction Protocol (Token Optimization)

- **After 4 compactions:** Write a session summary capturing current phase, what was completed, what is in progress, blockers, decisions, and next step. Then alert me to `/clear`.
- **Where to store it:** Paste the session summary into the Session Log section of `claude.local.md`. On the next session, read that log first.
- **Session summary format:**
  ```
  ## Session Summary — [Date]
  **Phase:** N
  **Completed:** [list]
  **In progress:** [list]
  **Decisions:** [list]
  **Blockers:** [list]
  **Next step:** [specific next action]
  ```
- **Between tasks:** Use `/clear` to drop stale context.
- **Keep responses tight:** No preamble, no restating the question, no filler.
- **File index exists so you don't read everything.** Only read files relevant to the current task.

## 11. Quality Checklist (Pre-Merge)

Before any branch merges to main:
- [ ] All `pytest` tests pass for the touched modules
- [ ] No `print()` debug statements left in production code (use `logging` for real logs)
- [ ] No hardcoded values (everything in `backend/constants.py`)
- [ ] Type hints on every new function
- [ ] Error handling on all async operations and all subagent functions
- [ ] Every checklist item has a non-empty `source` field
- [ ] Clinical disclaimer present in every `ChecklistOutput` (exact text, never modified)
- [ ] No diagnostic language ("Patient has...", "Diagnose...") in any output string

## 12. Rules (Enforcement Layer)

Non-negotiable. If a rule conflicts with a request, flag it.

1. Never mock data or guess at endpoints.
2. Never merge to main until a branch is complete and confirmed.
3. Never skip error handling. Subagents return failed status; they do not raise.
4. Never use untyped function signatures.
5. Always separate concerns across orchestrator, subagents, synthesist, scorer, generator.
6. Always centralize constants in `backend/constants.py`.
7. Always ask before making changes you are not 95% confident about.
8. Always provide a summary and commit message after updates.
9. Always read a file before editing it.
10. Prefer targeted fixes over full rebuilds.
11. Schema changes require updating ECHO_SCHEMA.md before any code change.
12. **Never include Co-Authored-By trailers crediting Claude in commits.**
13. **Never reproduce or paraphrase licensed clinical content into static files.** AWHONN materials and ACOG content beyond ~100-word excerpts are copyrighted. ECHO cites these sources by reference, never embeds their text.

## 13. ECHO-Specific Constraints

These are project-specific rules that go beyond the general template.

### Clinical content discipline
- Every checklist item must trace to a real, named federal or professional-body source. No invented citations.
- Action language always begins with "Consider screening for..." Never "Patient has..." or "Diagnose..."
- The clinical disclaimer text is hardcoded and never modified. See `ECHO_SCHEMA.md` for the exact string.

### Licensing rules
- **AWHONN content (POST-BIRTH, SBARs, RMC framework) is licensed and cannot be reproduced in a commercial tool.** ECHO references AWHONN as a "see also" pointer with a URL. Original framing copy in `framing_library.json` is grounded in public-domain sources (CDC, peer-reviewed literature) and never paraphrases AWHONN content.
- **ACOG Committee Opinion 736 excerpts must stay under ~100 words per finding** with inline attribution. Subagent 4 (Guideline) enforces this in its output construction.
- CDC, NCHS, CMS, KFF, and TCHMB content is public domain and has no excerpt limit.

### Patient data discipline
- Nothing persists after a session ends. No database writes, no file logging of PatientProfile contents.
- The patient context header in the rendered checklist contains no name, no MRN. Age range, race/ethnicity, payer, state, weeks postpartum only.
- Open access for Demo Day. Revisit auth for production.

### Pipeline discipline
- The 25-second internal timeout (with 30-second user-facing budget) is non-negotiable. If a subagent is consistently slow, fix the subagent. Do not extend the timeout.
- The fallback handler (N9) is the only layer that catches gather exceptions. Other layers assume cleaned input.
- Conflict resolution is FLAGGED-and-preserve-both, never silent picking. The CNM decides.
