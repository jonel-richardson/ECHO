# PRD — ECHO
## Early Care Handoff Observer — Clinical Decision Support

**Team Female:** Luba Kaper · Paula · Jonel
**Program:** Pursuit AI-Native Cycle 3 | **Version:** 2.1 | **Date:** May 2026

> Product Requirements Document — what and why. CLAUDE.md is the how. Write this BEFORE touching code.

---

## Problem Statement

**Who is affected:** Certified Nurse Midwives (CNMs) conducting postpartum follow-up visits at hospitals and health systems — primarily in high-disparity markets (New York, Texas). They carry 20–30 postpartum visits per day and are the last clinical touchpoint before a mother is discharged back into her community.

**What's broken:** CNMs do postpartum screening from memory and generic paper checklists. They have no fast, patient-tailored tool that pulls from federal mortality data, clinical guidelines, SDOH risk factors, and the specific hospital's care commitment record at the moment of the visit. The result is a checklist that doesn't reflect who is actually in the exam room.

**How we know it's real:**
- Black women die from pregnancy-related causes at 2–3x the rate of white women (CDC NCHS). Risk is not uniform — it is shaped by state, hospital, payer mix, and SDOH context.
- ACOG and AWHONN have published postpartum screening standards (4th trimester guidelines, POST-BIRTH Warning Signs) that are widely trained on but inconsistently applied at the bedside.
- CMS Birthing-Friendly Hospital designation and HCAHPS discharge data are public — but CNMs have no tool to surface whether their own hospital's commitments are reflected in the care a patient will receive post-discharge.
- Personal experience (Luba): postpartum maternal care systematically lags well-baby care. The system built for babies doesn't extend to the mother.

---

## Target User

**Primary user:** Certified Nurse Midwife (CNM) in a hospital or health system postpartum unit. She is seeing 20–30 patients per day. She cares about: not missing a warning sign, having the clinical data to support her assessment, and documenting efficiently. She is not a data analyst — she needs a tool that does the synthesis before the door opens.

**Secondary user:** Hospital administrator / VP of Women's Services (the buyer). They care about Joint Commission readiness, maternal mortality quality metrics, CMS designation status, liability, and staff retention. They approve the per-seat SaaS contract.

**How they solve this today:**
- Generic paper or EHR-embedded checklists (ACOG template, hospital policy document) — not patient-tailored.
- CNM experience and memory — inconsistent across providers, not data-informed.
- No tool currently synthesizes federal mortality data + clinical guidelines + SDOH + hospital commitment status into a single patient-specific view at point of care.

**User needs:**
- As a CNM, I need a patient-specific checklist generated in under 30 seconds so that I can start the visit without hunting across multiple sources.
- As a CNM, I need the checklist to reflect this patient's actual demographic risk profile (race, age, payer, postpartum week) because generic checklists miss high-risk presentations.
- As a CNM, I need to see whether my hospital delivered on its discharge commitments because a gap in handoff is a clinical risk I need to screen for.
- As a CNM, I need SDOH flags surfaced (housing instability, food insecurity, transportation) because social risk factors predict readmission and poor outcomes.
- As a hospital administrator, I need my CNMs using a documented, data-grounded screening tool so that I can demonstrate quality improvement to CMS and reduce liability exposure.

---

## Solution

**One-liner:** ECHO is a clinical decision support agent that takes a CNM's patient parameters and generates a real-time, patient-specific postpartum screening checklist grounded in federal mortality data, clinical guidelines, SDOH screening, and hospital commitment status.

**Core principle:** ECHO emphasizes, it does not omit. Every output contains the full warning sign set, the full SDOH set, and the full ACOG fourth trimester components. Tailoring changes what gets emphasized and in what order — not what gets included. Every adaptation traces to a federal source or a professional body. Hospital procurement and clinical committees can defend every tailoring decision by pointing at the citation.

**How tailoring works — three layers:**
- Risk Context section pulls different excerpts from the same federal sources based on race, age, and state.
- Warning sign priority reorders based on flagged complications. The full set is always present. Order changes.
- Communication framing pulls from the matching AWHONN SBAR for the patient's identity.

**Core user flow:**
1. CNM enters 6–8 routing inputs: age range, race/ethnicity, payer, state, hospital, weeks postpartum, pregnancy complications flagged, delivery type. These are intake-level fields, not patient records.
2. Agent orchestrator dispatches 5 subagents simultaneously — Mortality, Guideline, SDOH, Bundle, State Context — each returns structured findings.
3. Risk Synthesist layer intercepts all 5 returns — screens for conflicts and confidence gaps — sends cleaned, confidence-rated summary to orchestrator.
4. ECHO generates patient-specific checklist. CNM sees ranked warning signs, SDOH flags, hospital commitment status, and recommended screening actions.

> Demo Day scope ends here. No email send. CNM reviews checklist in the browser.

---

## Feature Scope

> P0 = must ship (MVP). P1 = important for a solid experience. P2 = nice to have.
> P0 features become CLAUDE.md Phase 1. P1 features become Phase 2. And so on.

### User Journey: CNM Generates a Patient Checklist

**Context:** The core Demo Day loop — a CNM opens ECHO, enters patient parameters, and receives a tailored screening checklist within 30 seconds. Demo Day shows 2 patient scenarios to demonstrate the system adapting in real time.

**Demo Day scenarios:**
- Maya, 28, Black, Medicaid, NY, 6 weeks postpartum, no complications
- Janet, 41, White, private insurance, TX, 4 weeks postpartum, hypertensive disorder

Same system, two runs, two meaningfully different outputs.

**Step 1: Patient Parameter Input**
- [P0] CNM can enter: age range, race/ethnicity, payer (Medicaid/private), weeks postpartum, hospital name, state, pregnancy complications flagged, delivery type
- [P0] System validates required fields before submitting
- [P1] Dropdowns pre-populated with CMS hospital list for selected state
- [P2] CNM can save a patient session to return to later

**Step 2: Agent Processing**
- [P0] Orchestrator dispatches all 5 subagents (Mortality, Guideline, SDOH, Bundle, State Context) in parallel
- [P0] Risk Synthesist intercepts returns, flags conflicts and confidence gaps
- [P0] Processing completes within 30 seconds for Demo Day
- [P1] Loading state shows which subagents are running
- [P2] CNM can see individual subagent outputs in an expandable detail panel

**Step 3: Checklist Output**
- [P0] ECHO displays prioritized warning signs (AWHONN POST-BIRTH 9 canonical signs, weighted by patient risk profile)
- [P0] ECHO displays SDOH screening flags (CMS AHC HRSN 10-question domains)
- [P0] ECHO displays hospital commitment status (Birthing-Friendly designation, HCAHPS discharge measure)
- [P0] Each checklist item is labeled with its source (e.g., "ACOG 4th Trimester", "CDC NVSS", "CMS HRSN")
- [P1] State policy context shown (Medicaid extension status, state MMR ranking)
- [P1] Data confidence rating displayed for each finding
- [P2] CNM can annotate or check off items during the visit

### Out of Scope (for now)
- **Email delivery to care team** — post Demo Day feature
- **EHR integration** — requires procurement and security review beyond Demo Day scope
- **Clinical recommendations (diagnoses, treatment plans)** — ECHO supports screening, not diagnosis
- **Patient-facing interface** — ECHO is a provider tool
- **Real-time EHR data pull** — uses public federal datasets and CNM-entered parameters
- **HIPAA-compliant data storage** — processes no persistent PII for Demo Day; BAA and infrastructure required before production

---

## Agent Architecture

| Subagent | Clinical Question Answered | Primary Sources |
|---|---|---|
| Mortality Subagent | What's killing women like this patient? | NCHS NVSS, NY MMRB, TX MMRB |
| Guideline Subagent | What should the CNM screen for at this postpartum week? | AWHONN POST-BIRTH, ACOG 4th Trimester |
| SDOH Subagent | What non-clinical risks apply to this patient? | CMS AHC HRSN Screening Tool |
| Bundle Subagent | Did the patient's hospital deliver on its commitments? | CMS Birthing-Friendly, AIM Bundle v2.0, HCAHPS |
| State Context Subagent | What's the policy/quality environment around this patient? | KFF, NY PQC, TX TCHMB |
| Risk Synthesist | What conflicts or confidence gaps exist across returns? | All 5 subagent outputs |

---

## Data Sources

| Data | Source | Format | Notes |
|---|---|---|---|
| Maternal mortality by race/cause | NCHS NVSS Vital Statistics Online | CSV / API | ICD-10 coded, demographic cross-tabs |
| State MMR Board reports | NY & TX Maternal Mortality Review Boards | PDF (parsed) | Leading causes by race, preventability assessments |
| Postpartum warning signs | AWHONN POST-BIRTH Warning Signs | Curated static | 9 canonical signs; confirm licensing for commercial use |
| 4th trimester guidelines | ACOG Postpartum Care Guidelines | Curated static | Timeline of postpartum risk windows |
| SDOH screening questions | CMS AHC HRSN Screening Tool | Curated static | 10 core domains: housing, food, transport, utilities, safety |
| Birthing-Friendly designation | CMS Hospital General Information | CSV (data.cms.gov) | Free/public; "Meets criteria" field = commitment flag |
| Discharge HCAHPS scores | CMS HCAHPS Hospital data | CSV (data.cms.gov) | Discharge information measures |
| Postpartum Medicaid coverage | KFF Postpartum Coverage Tracker | CSV / web | 12-month extension status by state |
| State perinatal QI context | NY Perinatal QC / TX TCHMB | PDF / web | State-level collaborative data and initiatives |
| Birthing-Friendly geocoded | CMS | CSV | Added per Jonel data manifest update |
| NNPQC funding context | NNPQC | Web / PDF | Added per Jonel data manifest update |

> All CMS files are free/public at data.cms.gov/provider-data — no login required.
> AWHONN and ACOG content is licensed clinical material — confirm reuse permissions before production.

---

## Success Metrics

| Goal | Signal | Metric | Target |
|---|---|---|---|
| Speed | CNM can run checklist in a single visit slot | Time from submit to checklist render | Under 30 seconds |
| Completeness | All 5 subagents return findings | Subagent completion rate per run | 100% on Demo Day scenarios |
| Accuracy | Checklist items are source-attributed | % of items with cited source | 100% |
| Trust | CNM can verify each recommendation | Data confidence label present | All items labeled high/low |
| Disparity signal | NY vs TX produce different checklists for same patient | Checklist diff across states | Demonstrably different for Maya vs Janet scenarios |

---

## ROI Snapshot

| Category | Without ECHO | With ECHO | Delta |
|---|---|---|---|
| **CNM prep time** | 15–20 min/patient: cross-referencing guidelines, EHR notes, state policy | 30 seconds: parameterized query → checklist | Save 15+ min/patient; ~5 hrs/week/CNM |
| **Screening consistency** | Varies by provider memory and shift fatigue | Standardized, data-grounded per visit | Risk of missed warning sign reduced |
| **Hospital liability** | Undocumented screening rationale | Source-cited checklist audit trail (post Demo Day) | CMS compliance readiness |
| **Build cost** | — | ~80 hrs team build (Demo Day scope) | vs. $30K+ for custom clinical tool |

**One-line pitch:** ECHO turns a 20-minute manual synthesis into a 30-second clinical decision support query — and extends the same rigor of well-baby screening to the mother.

---

## Stakeholder Concerns

**Sales:**
- Buyer is VP of Women's Services or CMO at the hospital — not the CNM. Buyer cares about CMS metrics, liability, and staff retention, not checklist UX.
- Sales cycle is multi-month. Hospital procurement requires security review, legal, IT, and clinical leadership sign-off. Path: Demo Day → pilot agreement → paid pilot → contract.
- Top buyer objections: (1) "We already have an EHR checklist" — ECHO is data-grounded and patient-tailored, not generic. (2) "Is this HIPAA compliant?" — Demo Day processes no PII; production requires BAA. (3) "How do we trust the clinical data?" — every item is source-cited to federal and professional-body data. Every tailoring decision can be defended by pointing at the citation.
- Proof point needed: one CNM pilot who can speak to checklist quality vs. her current workflow.

**Customer Success / Support:**
- Day-one question from CNMs: "Why did ECHO flag X — what's the source?" → Source citation on every item is the answer.
- Most common confusion: which patient parameters matter most and whether partial data degrades output quality.
- Tool is working if a CNM says: "I caught something I would have missed" or "This saved me 10 minutes today."

**Legal / Compliance:**
- HIPAA: Demo Day processes no persistent PII — CNM enters routing inputs but ECHO does not store them. Production requires Business Associate Agreement and infrastructure review.
- Clinical liability: ECHO is decision support, not a diagnostic engine. All output must be clearly labeled "for clinical review" — not a diagnosis or treatment recommendation. Action language on every item begins with "Consider screening for..." never "Patient has..." or "Diagnose."
- Data licensing: CMS and KFF data are public domain. AWHONN and ACOG content is licensed — confirm permissions before embedding in a commercial product.
- ECHO output could surface in quality review proceedings — source citation and audit trail are critical for defensibility.

**Operations / Engineering:**
- CMS datasets refresh quarterly — pipeline must handle new CSV releases without breaking the scoring logic.
- If a subagent fails (API timeout, data source unavailable), the Risk Synthesist must degrade gracefully and flag the gap rather than silently drop findings.
- Demo Day is stateless — no database, no auth, no persistent storage. Session ends, data is gone.

**Product / Strategy:**
- No direct competitor surfaces all five data layers (mortality + guidelines + SDOH + hospital commitment + state context) in a single patient-parameterized tool. EHR vendors have generic checklists but no real-time federal data synthesis.
- Moat: the curated, quality-reviewed data layer combining federal mortality microdata, clinical guidelines, and hospital commitment signals — this takes time to build and validate, and is the core IP.
- 6-month roadmap: Demo Day (checklist, no email) → care team email, NY + TX live data → EHR API pilot with one health system.
- 12-month: HIPAA-compliant hosted version, BAA-ready, pilot with 2–3 CNM departments.

**Finance:**
- Pricing hypothesis: per-seat SaaS, $200–500/CNM/month, billed to hospital. A 10-CNM department = $2,000–5,000/month ARR per hospital.
- Demo Day run cost: API calls (Anthropic) + hosting. Estimate under $0.50/checklist at current model pricing.
- Path: Pursuit Demo Day → 2–3 unpaid pilot CNMs → first paid pilot at $500/month → raise or bootstrap to production.

**End Users (CNMs):**
- Biggest reason to distrust: "This data doesn't match what I know about my patient." Mitigation: show source for every item; never hide data provenance.
- Ethical risk: over-reliance on the tool in place of clinical judgment. Mitigation: ECHO is framed as decision support, not decision-making. All language is "consider screening for" — not "diagnose."
- What would make a CNM recommend it: speed + specificity. If the checklist saves 15 minutes and catches one thing she would have missed, she will tell a colleague.

---

## Open Questions

- [ ] Is AWHONN POST-BIRTH Warning Signs content freely embeddable in a commercial tool, or does it require a license agreement? (Paula)
- [ ] Does a clean NCHS mortality CSV exist or must it be parsed manually from PDF? Document the plan either way. (Jonel)
- [x] How does the web app handle the case where a hospital is not in the CMS dataset? Bundle agent returns status = 'partial', Tool 6 displays "Hospital commitment status: Not found in CMS dataset" with no score applied. Pipeline continues.
- [x] What is the Risk Synthesist conflict resolution rule when two subagents return contradictory risk signals? When two sub-agents return directly contradictory signals for the same finding, the Risk Synthesist sets confidence to FLAGGED and creates a SynthesistFlag with flag_type = 'conflict'. Both data points are preserved. The orchestrator surfaces the conflict to the CNM with both values shown. ECHO never resolves a clinical contradiction silently.
- [x] Does Demo Day need a login/auth wall, or is it open access? Open access. No persistent PII is processed so there is nothing to protect at the session level. Revisit for production.
- [ ] NY and Texas — confirm all five subagents have sufficient real data coverage for both states. (Jonel)
- [x] Does anything persist after the browser session ends? Nothing. No database, no storage, no logging of patient parameters. Session ends, data is gone.
- [ ] Is ACOG 4th Trimester content freely embeddable or does it require a license? (Paula)
- [x] Dashboard: terminal display or HTML for Demo Day? HTML. Terminal display is hard to show on stage.
- [ ] Team module ownership for post Demo Day features: who owns the care team email layer?

> Resolve all open questions BEFORE starting Phase 1. They feed directly into CLAUDE.md.
