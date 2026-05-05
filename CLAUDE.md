# CLAUDE.md — ECHO
## Early Care Handoff Observer — Build Instructions for AI Assistants
**Team Female:** Luba Kaper · Paula · Jonel
**Program:** Pursuit AI-Native Cycle 3 | **Version:** 2.1 | **Date:** May 2026

> This is the HOW. The PRD (ECHO-PRD-v2.1.md) is the WHAT and WHY.
> Read the PRD before reading this file. Read this file before touching code.
> If the PRD and this file conflict, the PRD governs.

---

## What You Are Building

ECHO is a clinical decision support agent. A Certified Nurse Midwife (CNM) enters 8 patient parameters. ECHO dispatches 5 subagents in parallel, synthesizes their findings, and renders a one-page patient-specific postpartum screening checklist in the browser — in under 30 seconds.

You are not building a diagnostic engine. You are not building an EHR. You are not building a patient-facing tool. ECHO is a provider-facing decision support layer that surfaces federal data, clinical guidelines, SDOH risk, and hospital commitment status in a single, source-cited view at the point of care.

---

## Do Not Do These Things

- Do not store any patient parameter after the session ends. No database writes. No logging of PHI or routing inputs.
- Do not generate diagnostic language. No "Patient has..." or "Diagnose..." in any output string.
- Do not omit warning signs to simplify output. ECHO emphasizes — it never omits. Full set always present.
- Do not resolve clinical conflicts silently. If two subagents contradict each other, flag it and show both.
- Do not proceed if required fields are missing. Fail-loud at N2 with a specific field-level error message.
- Do not hardcode patient scenario values outside of the demo fixture files.
- Do not call subagents sequentially. Always use asyncio.gather for parallel dispatch.
- Do not use diagnostic framing in AWHONN SBAR copy. Pull from the sourced library (N12) — never generate framing from scratch.
- Do not add features outside Demo Day scope without a PRD update.

---

## Repository Structure

```
echo/
  README.md                    # project overview
  CLAUDE.md                    # this file
  ECHO-PRD-v2.1.md             # product requirements document
  ECHO_BUILD_PLAN.md           # phase 1 build steps by owner
  ECHO_SCHEMA.md               # data object definitions
  ECHO_ARCHITECTURE.md         # node map and design decisions

  /frontend
    index.html                 # CNM input form (N1)
    checklist.html             # checklist display (N13)
    styles.css                 # shared styles
    app.js                     # form submit handler, fetch to backend

  /backend
    main.py                    # FastAPI app entry point
    orchestrator.py            # N2: validates PatientProfile, dispatches subagents
    risk_synthesist.py         # N8: conflict detection, confidence rating
    scorer.py                  # N10: gap_score, urgency_tier, disparity_flag
    output_generator.py        # N11: Anthropic API call, checklist generation
    fallback.py                # N9: failed subagent handling

    /subagents
      mortality.py             # N3: NCHS NVSS, NY MMRB, TX MMRB
      guideline.py             # N4: AWHONN POST-BIRTH, ACOG 4th Trimester, AIM Bundle
      sdoh.py                  # N5: CMS AHC HRSN
      bundle.py                # N6: CMS Birthing-Friendly, HCAHPS
      state_context.py         # N7: KFF, NNPQC, TCHMB

    /data
      cms_birthing_friendly.csv
      cms_hcahps.csv
      kff_medicaid_postpartum.csv
      nchs_nvss_mortality.csv
      /static
        awhonn_post_birth.json
        acog_4th_trimester.json
        cms_hrsn_domains.json
        awhonn_sbar_library.json

    /schemas
      patient_profile.py
      subagent_return.py
      synthesist_output.py
      scored_output.py
      checklist_output.py

    /fixtures
      maya_scenario.json
      janet_scenario.json

  /tests
    test_orchestrator.py
    test_risk_synthesist.py
    test_scorer.py
    test_subagents.py
    test_output_generator.py
    test_end_to_end.py
```

---

## Phase 1 Build Order

Build in this exact sequence. Each step must be complete and tested before the next begins.

See ECHO_BUILD_PLAN.md for full step-by-step instructions per owner.

---

## Prompt Template (N11 — Output Generator)

```
You are ECHO's Output Generator. You receive structured clinical findings from a multi-agent postpartum screening pipeline and generate a patient-specific checklist for a Certified Nurse Midwife (CNM).

RULES — follow exactly:
1. Every checklist item must have: label, detail (1-2 sentences), action (begins with "Consider screening for..."), source (cite the federal source or professional body), confidence (H | M | L | FLAGGED), priority_rank (integer, 1 = highest urgency).
2. Never use diagnostic language. No "Patient has..." or "Diagnose..." anywhere in output.
3. Never omit warning signs. The full AWHONN POST-BIRTH 9-sign set is always present. Tailoring changes order (priority_rank), not inclusion.
4. Never resolve a FLAGGED conflict. If confidence = FLAGGED, show both data points in the detail field and note "CNM review required."
5. Use AWHONN SBAR framing provided in the input — do not generate communication framing from scratch.
6. Output valid JSON matching the ChecklistOutput schema. No prose. No markdown. No explanation outside the JSON object.

INPUT: {scored_output_json}
SBAR_FRAMING: {sbar_framing_json}

OUTPUT: ChecklistOutput JSON only.
```

---

## Environment Variables

```
ANTHROPIC_API_KEY=your_key_here
ECHO_ENV=demo
```

Do not commit API keys. Use a .env file locally and confirm .env is in .gitignore.

---

## Testing Requirements

Every function must have a unit test before the next build step begins.

End-to-end tests run both demo fixtures through the full pipeline and assert:
- Pipeline completes in under 30 seconds
- All 5 subagents return status = success on demo fixtures
- 100% of ChecklistItems have a non-empty source field
- Maya (NY) and Janet (TX) produce demonstrably different checklist outputs
- Clinical disclaimer is present in every ChecklistOutput
- No diagnostic language appears anywhere in output strings

Run tests: `pytest /tests/`

---

## Demo Day Checklist

- [ ] Both demo fixtures run end-to-end in under 30 seconds
- [ ] All 5 subagents return success on both scenarios
- [ ] Maya and Janet produce visibly different checklists
- [ ] Every checklist item has a source citation
- [ ] Clinical disclaimer is present on checklist display
- [ ] Hospital commitment status renders correctly
- [ ] FLAGGED conflict shows both data points
- [ ] No console errors in browser during demo flow
- [ ] /health endpoint returns 200
- [ ] No patient data persists after session ends

---

## Open Questions Blocking Phase 1

- [ ] AWHONN POST-BIRTH Warning Signs — license status for Demo Day use? (Paula)
- [ ] ACOG 4th Trimester content — license status for Demo Day use? (Paula)
- [ ] NCHS mortality CSV — clean download confirmed or PDF parsing required? (Jonel)
- [ ] NY and TX — all 5 subagents have sufficient real data coverage confirmed? (Jonel)
- [ ] Post Demo Day care team email layer — module owner decision? (Team)
