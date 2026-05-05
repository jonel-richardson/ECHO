# ECHO v2 Data Summary

Owner: Jonel
Status: Ready to build
Last updated: May 2026

This is the data inventory for ECHO v2. One row per subagent. Each row tells you what file feeds it, what we pull from that file, and what the fallback is if the source breaks.

---

## Subagent 1: Mortality

**Question it answers:** What is killing women like this patient?

| Source | Filename | What we pull |
|---|---|---|
| NCHS Health E-Stat 113 | `nchs_maternal_mortality_2024.pdf` | Maternal Mortality Ratio (MMR): deaths within 42 days of pregnancy end. National Black MMR 44.8 vs White 14.2 per 100K (2024). |
| Cureus Racial Disparity Paper | `cureus_racial_disparity_2025.pdf` | Pregnancy-Related Mortality Ratio (PRMR): broader window, deaths up to 1 year postpartum. Black PRMR 68.0 vs White 26.3 per 100K. Post-pandemic gap widened, not closed. |
| NY Mental Health Factsheet | `nysdoh_mental_health_pregnancy_deaths_2018_2021.pdf` | 1 in 3 NY pregnancy-associated deaths are mental health. 2 of 3 occur 6 weeks to 1 year postpartum. |
| US Mortality CSV | `us_maternal_mortality_2019_2023.csv` | Year-over-year national figures for trend lines. |

**Important methodology note for the PRD and pitch:** NCHS MMR (44.8 Black, 14.2 White) and Cureus PRMR (68.0 Black, 26.3 White) are different measures. MMR counts deaths within 42 days of pregnancy end. PRMR counts deaths up to 1 year postpartum. Both are valid. They are not interchangeable.

**Recommendation:** Lead the pitch with NCHS MMR (44.8 vs 14.2) as the headline because it is the federal standard and easier to defend in a clinical setting. Use Cureus PRMR as supporting context to show the disparity gets worse, not better, when you look at the full year postpartum window. If we mix the two without a footnote, a clinical judge will catch it.

**Fallback:** None needed. Multiple independent sources confirm the disparity.

---

## Subagent 2: Guideline

**Question it answers:** What should the CNM screen this patient for at six weeks?

| Source | Filename | What we pull |
|---|---|---|
| CDC Hear Her | `cdc_hear_her_warning_signs.pdf` | Urgent maternal warning signs (severe headache, vision changes, swelling, fever, chest pain, etc.) and conversation starter language. |
| ACOG Committee Opinion 736 | `acog_committee_opinion_736.pdf` | Fourth trimester framework. Box 1 components (mood, infant care, contraception, sleep, physical recovery, chronic disease, health maintenance). Table 1 care plan template. |
| AIM Postpartum Discharge Bundle v2.0 | `aim_postpartum_discharge_bundle_v2.pdf` | Structured measures: state surveillance, process, and structure measures hospitals are expected to track. |

**Fallback:** None needed. Three federal and professional sources align.

**Licensing constraint (ACOG):** ACOG's permissions policy allows excerpts under approximately 100 words with attribution, without requiring written permission. Reproducing whole sections or "most of a publication" is explicitly prohibited. Subagent 2 must enforce a per-finding excerpt cap on ACOG-sourced content and include inline attribution. CDC Hear Her and AIM materials are public domain and have no excerpt limit.

---

## Subagent 3: SDOH

**Question it answers:** What non-clinical risks should the care team flag?

| Source | Filename | What we pull |
|---|---|---|
| CMS AHC HRSN Screening Tool | `cms_ahc_hrsn_screening_tool.pdf` | 10 core domains (housing, food, transportation, utilities, safety) + 8 supplemental (financial, employment, family support, education, physical activity, substance use, mental health, disabilities). Full question text and scoring rules included. |

**Fallback:** None needed. Single CMS source is comprehensive.

---

## Subagent 4: Bundle and Hospital Commitment

**Question it answers:** How is the patient's state delivering on hospital-level postpartum care commitments? Does the patient's specific hospital hold a federal commitment badge?

**Scope note:** Most of these sources answer the question at the state aggregate level. The Birthing-Friendly file is the one per-hospital signal: it gives a yes/no on whether the patient's hospital holds the CMS Birthing-Friendly designation.

| Source | Filename | What we pull |
|---|---|---|
| CMS Birthing-Friendly Hospitals (geocoded) | `birthing_friendly_hospitals_geocoded.csv` | Per-hospital yes/no on CMS Birthing-Friendly designation. The only per-hospital signal in v2. |
| NY HCAHPS | `cms_hcahps_ny.csv` | Hospital-level patient experience scores for NY facilities, aggregated to state-level signals. |
| CMS Core Set NY (full) | `cms_core_set_ny_2023.xlsx` | State-level NY Medicaid quality measures. Sheet `52. PPC-AD` is the headline: postpartum care visit rates 2021-2023. |
| CMS Core Set TX (full) | `cms_core_set_tx_2023.xlsx` | State-level TX Medicaid quality measures. Sheet `52. PPC-AD` gives directly comparable postpartum care visit rates 2021-2023. |
| CMS Core Set Prenatal/Postpartum (selected) | `cms_core_set_postpartum_cross_state.csv` | Cross-state baseline. Use as backup or sanity check against the full state files. |
| 2021 Quality Measures | `cms_quality_measures_2021.csv` | Baseline state quality measure reporting. |

**Headline numbers for the demo (PPC-AD, postpartum care visit 7-84 days after delivery, Medicaid):**

| Year | NY | TX | Gap |
|------|-----|------|------|
| 2021 | 75.9% | 68.0% | -7.9 pts |
| 2022 | 76.5% | 75.5% | -1.0 pts |
| 2023 | 82.4% | 77.4% | -5.0 pts |

NY consistently outperforms TX on postpartum care visit rates. This pairs with the Subagent 5 state context signal that both states have 12-month Medicaid extension, but NY has stronger QI infrastructure to back it up.

---

## Subagent 5: State Context

**Question it answers:** What is the policy and quality improvement environment in this state?

| Source | Filename | What we pull |
|---|---|---|
| KFF Postpartum Coverage Tracker | `kff_postpartum_coverage.csv` | State-by-state status of 12-month postpartum Medicaid coverage extension. Both NY and TX have it active. This is the policy floor signal. |
| NNPQC Funding | `nnpqc_funding.csv` | State-level National Network of Perinatal Quality Collaboratives funding. Proxy for QI infrastructure investment. |
| TCHMB PPED Report | `tchmb_pped_report_2024.pdf` | Full Texas postpartum preeclampsia QI initiative. Hospital coverage map (15 of 22 RACs). Race and ethnicity disparities cited. Process and structure measure outcomes. |
| CMS IQR FY28 Measures Directory | `cms_iqr_fy28_measures_directory.pdf` | What hospitals are required to report under CMS Inpatient Quality Reporting. Includes Maternal Morbidity Structural Measure and PC-07 Severe Obstetric Complications. |
| NY Mental Health Factsheet | `nysdoh_mental_health_pregnancy_deaths_2018_2021.pdf` | NY-specific recommendations and state action items (NYSPQC Opioid Use Disorder Project, Project TEACH expansion, Maternal Mental Health Workgroup). |

**Fallback:** None needed.

---

## What I am skipping and why

| Source | Reason |
|---|---|
| Per-hospital AIM bundle adoption | Login required, not scrapeable at scale |
| Joint Commission Perinatal Care certification | Not scrapeable |
| AWHONN POST-BIRTH Warning Signs | CDC Hear Her covers the same clinical ground and is public domain |
| PRAPARE | CMS AHC HRSN is more comprehensive and CMS-endorsed |
| AIM Postpartum Discharge Transition submission template | Blank form, not data. Measures already documented in `aim_postpartum_discharge_bundle_v2.pdf`. |

---

## Resolved: 5 subagents vs 6, and how AWHONN fits

**Decision:** Ship 5 subagents. AWHONN SBARs are referenced, not embedded.

**Background:** Earlier we discussed Option A — fold AWHONN respectful care SBAR text into the Output Generator as framing copy. That plan does not survive contact with AWHONN's licensing terms.

**AWHONN licensing finding:** AWHONN SBAR PDFs carry "© Copyright 2023 by the Association of Women's Health, Obstetric and Neonatal Nurses." Their Terms of Use prohibit reproduction, copying, or republication of materials in any commercial environment without written permission. Individually purchased downloads are explicitly for "personal, informational, and non-commercial use only." A facility license starts at $300 per facility for the full Respectful Maternity Care framework. ECHO is a commercial tool. We cannot embed AWHONN SBAR text directly, even with attribution.

**What we are doing instead:**

1. **Cite AWHONN SBARs as a reference** in the output. Example output line: "Communication framing aligned to AWHONN Respectful Patient Care SBARs. See awhonn.org/awhonn-sbars for full guidance." This is a citation, not reproduction. It is allowed.

2. **Write our own original framing copy** in the Output Generator, grounded in publicly available evidence about respectful maternity care for specific populations. Sources: peer-reviewed literature (Cureus paper already in hand), CDC guidance (Hear Her), and other public-domain materials. Every piece of framing copy traces to a public-domain source, not to an AWHONN document.

3. **Pursue an AWHONN license for v3** if the demo lands and we want to embed SBAR content directly. Contact: `permissions@awhonn.org`.

**What this changes for the build:**
- No `data/awhonn-sbars/` folder in the repo. The PDFs stay out of version control to avoid any implication of redistribution.
- Output Generator system prompt instructs the model to write original framing copy grounded in cited public-domain sources, not to reproduce or paraphrase AWHONN content.
- Every framing line in the output carries a citation to a public-domain source. AWHONN appears only as a "see also" reference at the bottom of the framing block.

**What this does not change:**
- The clinical value of patient-tailored communication framing is preserved. The CNM still gets identity-aware guidance.
- The pitch story stays intact: ECHO points the CNM to authoritative resources (including AWHONN) for full guidance, while delivering original, sourced framing in the moment of care.
- Architecture and contracts do not change. This is a content-generation rule, not a schema change.

**Path to v3:** If the demo lands and we pursue an AWHONN license, the framing-copy module becomes a thin wrapper over licensed SBAR text. The same Output Generator slot fills with licensed content. No architectural rework.

---

## Locked decisions (resolved questions)

| # | Question | Decision |
|---|---|---|
| 1 | AWHONN POST-BIRTH licensing | Skipped for v2. Replaced by CDC Hear Her (public domain). |
| 2 | NCHS clean CSV vs PDF | Public domain. Health E-Stat 113 PDF table is the source. CDC WONDER available for queryable downloads if needed. Manual transcription from PDF table is acceptable for v2. |
| 3 | Hospital not in CMS dataset | Bundle agent returns `status: 'partial'`. Display reads "Hospital commitment status: Not found in CMS dataset." Pipeline continues. |
| 4 | Risk Synthesist conflict resolution | Confidence set to FLAGGED. SynthesistFlag created with `flag_type: 'conflict'`. Both data points preserved. CNM sees both. ECHO never resolves a clinical contradiction silently. |
| 5 | Demo Day login wall | Open access. No persistent PII. Revisit for production. |
| 6 | NY and TX subagent data coverage | Confirmed. All five subagents have audited, current data for both states. |
| 7 | Session persistence | Nothing persists. No database, no storage, no logging of patient parameters. |
| 8 | ACOG 4th Trimester licensing | Excerpts under approximately 100 words with attribution allowed without permission. Subagent 2 enforces per-finding excerpt cap. |
| 9 | Dashboard format | HTML for Demo Day. |
| 10 | Care team email layer ownership | Parked. v3 feature, out of scope for Demo Day. Provisional owner: Paula. Revisit after Demo Day. |
