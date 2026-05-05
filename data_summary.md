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

## Open question for the team

5 subagents vs 6 (adding AWHONN Respectful Care Framework as agent 6).

**My recommendation:** Ship 5 subagents. Fold AWHONN respectful care principles into the Output Generator as framing copy alongside the clinical checklist. Keep the 11 AWHONN SBAR documents in the repo under `data/awhonn-sbars/` so the framing copy is sourced from the documents and traceable, not invented.

**Reasoning:** A 6th subagent carries real architectural cost (new contract, new Risk Synthesist screening rule, new failure modes, new tests). The AWHONN value does not require that cost. It requires two or three sentences of patient-tailored communication guidance in the output, sourced from the matching SBAR for the patient's identity. For the demo patient (Black woman, Medicaid), that means pulling framing language from the AWHONN Black women SBAR.

**Why this matters for the demo:** Without any AWHONN integration, the output is a clinically correct but generic-looking checklist. A judge or buyer will reasonably ask how it differs from a paper handout from ACOG. With the framing copy in place, the answer is clear: same evidence base every CNM uses, framing calibrated to the patient in front of you.

**Sourcing rule (carry into PRD):** Every piece of framing copy must trace back to a specific AWHONN SBAR document, the same way every checklist item traces to a federal source. No paraphrasing without citation. This keeps ECHO defensible.

**Path to v3:** If the framing-copy approach lands well in the demo, v3 is where we promote it to a full Respectful Care subagent with Risk Synthesist integration.
