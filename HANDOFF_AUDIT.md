# HANDOFF_AUDIT.md — ECHO v2 Pre-Handoff State

**Audited from:** `audit/pre-handoff-state` (off `main`, commit `d129ee7`)
**Audit date:** 2026-05-06
**Auditor:** Jonel
**Read-only audit. No production files modified.**

---

## Section 1: What is built and on main

### Pytest output (verbatim, full suite)

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\Jonel Richardson\ECHO\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Jonel Richardson\ECHO
plugins: anyio-4.13.0
collecting ... collected 114 items

tests/test_bundle.py::test_ny_patient_with_known_hospital_returns_4_findings PASSED [  0%]
tests/test_bundle.py::test_tx_patient_with_known_hospital_returns_3_findings PASSED [  1%]
tests/test_bundle.py::test_unknown_hospital_returns_partial_status_with_state_finding_intact PASSED [  2%]
tests/test_bundle.py::test_disparity_context_finding_includes_headline_numbers PASSED [  3%]
tests/test_bundle.py::test_findings_carry_sources PASSED                 [  4%]
tests/test_fallback.py::TestFallbackHandler::test_failed_subagent_is_removed_and_gap_flag_created PASSED [  5%]
tests/test_fallback.py::TestFallbackHandler::test_exception_result_becomes_gap_flag PASSED [  6%]
tests/test_fallback.py::TestFallbackHandler::test_partial_results_continue_through_pipeline PASSED [  7%]
tests/test_fallback.py::TestFallbackHandler::test_unexpected_result_type_does_not_raise PASSED [  7%]
tests/test_mortality.py::test_maya_returns_3_findings PASSED             [  8%]
tests/test_mortality.py::test_janet_returns_findings_with_age_cohort_jump PASSED [  9%]
tests/test_mortality.py::test_unknown_race_returns_failed_status PASSED  [ 10%]
tests/test_mortality.py::test_suppressed_cell_falls_back_to_all_ages PASSED [ 11%]
tests/test_risk_synthesist.py::TestRiskSynthesist::test_conflict_detection_flags_opposite_risk_direction PASSED [ 12%]
tests/test_risk_synthesist.py::TestRiskSynthesist::test_agreement_does_not_create_conflict PASSED [ 13%]
tests/test_risk_synthesist.py::TestRiskSynthesist::test_single_source_label_is_downgraded_to_low_confidence PASSED [ 14%]
tests/test_risk_synthesist.py::TestRiskSynthesist::test_fallback_gap_flags_are_preserved PASSED [ 14%]
tests/test_risk_synthesist.py::TestRiskSynthesist::test_partial_agents_are_preserved_for_scorer PASSED [ 15%]
tests/test_risk_synthesist.py::TestRiskSynthesist::test_exact_duplicate_findings_are_deduplicated PASSED [ 16%]
tests/test_schemas.py::TestFramingBlock::test_valid PASSED               [ 17%]
tests/test_schemas.py::TestFramingBlock::test_empty_framing_copy_raises PASSED [ 18%]
tests/test_schemas.py::TestFramingBlock::test_whitespace_framing_copy_raises PASSED [ 19%]
tests/test_schemas.py::TestChecklistOutput::test_valid PASSED            [ 20%]
tests/test_schemas.py::TestChecklistOutput::test_empty_items_raises PASSED [ 21%]
tests/test_schemas.py::TestChecklistOutput::test_modified_disclaimer_raises PASSED [ 21%]
tests/test_schemas.py::TestHospitalStatus::test_valid_with_state_rate PASSED [ 22%]
tests/test_schemas.py::TestHospitalStatus::test_valid_without_state_rate PASSED [ 23%]
tests/test_schemas.py::TestHospitalStatus::test_invalid_birthing_friendly_raises PASSED [ 24%]
tests/test_schemas.py::TestDataSource::test_valid PASSED                 [ 25%]
tests/test_schemas.py::TestDataSource::test_valid_no_url PASSED          [ 26%]
tests/test_schemas.py::TestDataSource::test_empty_name_raises PASSED     [ 27%]
tests/test_schemas.py::TestDataSource::test_whitespace_name_raises PASSED [ 28%]
tests/test_schemas.py::TestFindingItem::test_valid PASSED                [ 28%]
tests/test_schemas.py::TestFindingItem::test_empty_sources_raises PASSED [ 29%]
tests/test_schemas.py::TestFindingItem::test_invalid_confidence_raises PASSED [ 30%]
tests/test_schemas.py::TestFindingItem::test_flagged_confidence_is_valid PASSED [ 31%]
tests/test_schemas.py::TestFindingItem::test_empty_label_raises PASSED   [ 32%]
tests/test_schemas.py::TestSubAgentReturn::test_valid_success PASSED     [ 33%]
tests/test_schemas.py::TestSubAgentReturn::test_valid_failed_with_message PASSED [ 34%]
tests/test_schemas.py::TestSubAgentReturn::test_failed_without_message_raises PASSED [ 35%]
tests/test_schemas.py::TestSubAgentReturn::test_invalid_status_raises PASSED [ 35%]
tests/test_schemas.py::TestSynthesistFlag::test_valid_conflict PASSED    [ 36%]
tests/test_schemas.py::TestSynthesistFlag::test_valid_gap PASSED         [ 37%]
tests/test_schemas.py::TestSynthesistFlag::test_invalid_flag_type_raises PASSED [ 38%]
tests/test_schemas.py::TestSynthesistFlag::test_empty_label_raises PASSED [ 39%]
tests/test_schemas.py::TestSynthesistOutput::test_valid PASSED           [ 40%]
tests/test_schemas.py::TestSynthesistOutput::test_negative_subagents_completed_raises PASSED [ 41%]
tests/test_schemas.py::TestPatientProfile::test_valid PASSED             [ 42%]
tests/test_schemas.py::TestPatientProfile::test_valid_with_complications PASSED [ 42%]
tests/test_schemas.py::TestPatientProfile::test_invalid_payer_raises PASSED [ 43%]
tests/test_schemas.py::TestPatientProfile::test_state_not_two_chars_raises PASSED [ 44%]
tests/test_schemas.py::TestPatientProfile::test_negative_age_raises PASSED [ 45%]
tests/test_schemas.py::TestScoredOutput::test_valid PASSED               [ 46%]
tests/test_schemas.py::TestScoredOutput::test_gap_score_out_of_range_raises PASSED [ 47%]
tests/test_schemas.py::TestScoredOutput::test_invalid_urgency_tier_raises PASSED [ 48%]
tests/test_schemas.py::TestChecklistItem::test_valid PASSED              [ 49%]
tests/test_schemas.py::TestChecklistItem::test_empty_source_raises PASSED [ 50%]
tests/test_schemas.py::TestChecklistItem::test_invalid_confidence_raises PASSED [ 50%]
tests/test_schemas.py::TestChecklistItem::test_priority_rank_zero_raises PASSED [ 51%]
tests/test_scorer.py::TestScorer::test_maya_scenario_sets_disparity_and_medium_urgency PASSED [ 52%]
tests/test_scorer.py::TestScorer::test_janet_hypertensive_scenario_sets_high_urgency PASSED [ 53%]
tests/test_scorer.py::TestScorer::test_gap_score_counts_low_flagged_and_failed_agents PASSED [ 54%]
tests/test_scorer.py::TestScorer::test_partial_subagent_sets_medium_urgency_without_disparity PASSED [ 55%]
tests/test_scorer.py::TestScorer::test_low_urgency_when_no_complications_disparity_or_partial PASSED [ 56%]
tests/test_scorer.py::TestScorer::test_lead_angle_prefers_best_finding_over_failed_agent PASSED [ 57%]
tests/test_state_context.py::test_ny_patient_returns_4_findings PASSED   [ 57%]
tests/test_state_context.py::test_tx_patient_returns_4_findings PASSED   [ 58%]
tests/test_state_context.py::test_unsupported_state_returns_partial PASSED [ 59%]
tests/test_state_context.py::test_findings_carry_sources PASSED          [ 60%]
tests/test_state_context.py::test_ny_patient_with_mental_health_complication_surfaces_mental_health_fact PASSED [ 61%]
tests/test_state_context.py::test_tx_patient_with_hypertensive_disorder_surfaces_preeclampsia_fact PASSED [ 62%]
tests/test_state_context.py::test_patient_with_no_complications_returns_general_facts PASSED [ 63%]
tests/test_static_data.py::TestCdcHearHer::test_file_exists PASSED       [ 64%]
tests/test_static_data.py::TestCdcHearHer::test_top_level_key PASSED     [ 64%]
tests/test_static_data.py::TestCdcHearHer::test_all_entries_have_required_fields PASSED [ 65%]
tests/test_static_data.py::TestCdcHearHer::test_all_confidence_high PASSED [ 66%]
tests/test_static_data.py::TestCdcHearHer::test_source_is_cdc PASSED     [ 67%]
tests/test_static_data.py::TestCdcHearHer::test_minimum_entry_count PASSED [ 68%]
tests/test_static_data.py::TestAcogFindingItem::test_file_exists PASSED  [ 69%]
tests/test_static_data.py::TestAcogFindingItem::test_top_level_key PASSED [ 70%]
tests/test_static_data.py::TestAcogFindingItem::test_all_entries_have_required_fields PASSED [ 71%]
tests/test_static_data.py::TestAcogFindingItem::test_all_word_counts_under_100 PASSED [ 71%]
tests/test_static_data.py::TestAcogFindingItem::test_all_details_contain_attribution PASSED [ 72%]
tests/test_static_data.py::TestAcogFindingItem::test_source_is_acog PASSED [ 73%]
tests/test_static_data.py::TestAcogFindingItem::test_minimum_entry_count PASSED [ 74%]
tests/test_static_data.py::TestAcogFindingItem::test_actual_detail_word_count_under_100 PASSED [ 75%]
tests/test_static_data.py::TestCmsHrsnDomains::test_file_exists PASSED   [ 76%]
tests/test_static_data.py::TestCmsHrsnDomains::test_top_level_keys PASSED [ 77%]
tests/test_static_data.py::TestCmsHrsnDomains::test_exactly_10_core_domains PASSED [ 78%]
tests/test_static_data.py::TestCmsHrsnDomains::test_exactly_8_supplemental_domains PASSED [ 78%]
tests/test_static_data.py::TestCmsHrsnDomains::test_all_entries_have_required_fields PASSED [ 79%]
tests/test_static_data.py::TestCmsHrsnDomains::test_all_confidence_medium PASSED [ 80%]
tests/test_static_data.py::TestCmsHrsnDomains::test_domain_codes_unique PASSED [ 81%]
tests/test_static_data.py::TestFramingLibrary::test_file_exists PASSED   [ 82%]
tests/test_static_data.py::TestFramingLibrary::test_default_key_present PASSED [ 83%]
tests/test_static_data.py::TestFramingLibrary::test_maya_fixture_key_present PASSED [ 84%]
tests/test_static_data.py::TestFramingLibrary::test_janet_fixture_key_present PASSED [ 85%]
tests/test_static_data.py::TestFramingLibrary::test_all_blocks_have_required_fields PASSED [ 85%]
tests/test_static_data.py::TestFramingLibrary::test_no_awhonn_text_in_framing_copy PASSED [ 86%]
tests/test_static_data.py::TestFramingLibrary::test_awhonn_reference_in_see_also PASSED [ 87%]
tests/test_static_data.py::TestFramingLibrary::test_all_framing_copies_nonempty PASSED [ 88%]
tests/test_static_data.py::TestFramingLibrary::test_all_blocks_have_at_least_one_source PASSED [ 89%]
tests/test_subagents.py::TestGuidelineSubagent::test_maya_returns_success PASSED [ 90%]
tests/test_subagents.py::TestGuidelineSubagent::test_janet_returns_success PASSED [ 91%]
tests/test_subagents.py::TestGuidelineSubagent::test_findings_include_cdc_source PASSED [ 92%]
tests/test_subagents.py::TestGuidelineSubagent::test_findings_include_acog_source PASSED [ 92%]
tests/test_subagents.py::TestGuidelineSubagent::test_cdc_findings_are_high_confidence PASSED [ 93%]
tests/test_subagents.py::TestGuidelineSubagent::test_no_acog_finding_exceeds_word_cap PASSED [ 94%]
tests/test_subagents.py::TestSdohSubagent::test_maya_returns_success PASSED [ 95%]
tests/test_subagents.py::TestSdohSubagent::test_janet_returns_success PASSED [ 96%]
tests/test_subagents.py::TestSdohSubagent::test_returns_18_findings PASSED [ 97%]
tests/test_subagents.py::TestSdohSubagent::test_all_findings_medium_confidence PASSED [ 98%]
tests/test_subagents.py::TestSdohSubagent::test_source_is_cms_hrsn PASSED [ 99%]
tests/test_subagents.py::TestSdohSubagent::test_maya_and_janet_return_same_findings PASSED [100%]

============================= 114 passed in 3.83s =============================
```

### Phase status

| Step | Name | Owner (per build plan) | Status | Files that prove it | Test coverage |
|---|---|---|---|---|---|
| 1 | Schemas built and tested | Luba | **COMPLETE** | `backend/schemas/patient_profile.py`, `subagent_return.py`, `synthesist_output.py`, `scored_output.py`, `checklist_output.py`, `__init__.py` | `tests/test_schemas.py` — 40 tests |
| 2 | Static data files curated and validated | Jonel + Luba | **COMPLETE** | `backend/data/*.csv`, `backend/data/*.xlsx`, `backend/data/static/*.json` (CSVs/Excels by Jonel; JSONs by Luba) | `tests/test_static_data.py` — 30 tests |
| 3 | All 5 subagents implemented and tested individually | Jonel + Luba | **COMPLETE** | `backend/subagents/mortality.py` (N3, Jonel), `guideline.py` (N4, Luba), `sdoh.py` (N5, Luba), `bundle.py` (N6, Jonel), `state_context.py` (N7, Jonel) | `tests/test_mortality.py` — 4; `tests/test_subagents.py` — 12 (Guideline + SDOH); `tests/test_bundle.py` — 5; `tests/test_state_context.py` — 7 |
| 4 | Fallback handler complete | Luba | **COMPLETE** | `backend/fallback.py` (86 lines) | `tests/test_fallback.py` — 4 tests |
| 5 | Risk Synthesist complete | Luba | **COMPLETE** | `backend/risk_synthesist.py` (163 lines) | `tests/test_risk_synthesist.py` — 6 tests |
| 6 | Scorer complete | Luba | **COMPLETE** | `backend/scorer.py` (132 lines) | `tests/test_scorer.py` — 6 tests |
| 7 | Output Generator complete | Paula | **NOT STARTED** | `backend/output_generator.py` exists but is **empty (0 bytes)** | `tests/test_output_generator.py` — empty (0 bytes) |
| 8 | Orchestrator wired end-to-end | Jonel | **NOT STARTED** | `backend/orchestrator.py` exists but is **empty (0 bytes)** | `tests/test_orchestrator.py` — empty (0 bytes) |
| 9 | FastAPI entry point exposed | Jonel | **NOT STARTED** | `backend/main.py` exists but is **empty (0 bytes)** | (none yet) |
| 10 | Frontend form + checklist render | Paula | **NOT STARTED** | `frontend/index.html`, `frontend/checklist.html`, `frontend/app.js`, `frontend/styles.css` all **empty (0 bytes)** | `tests/test_end_to_end.py` — empty (0 bytes) |

**Headline:** Steps 1–6 are complete on `main`. 114 tests pass. Steps 7–10 are unstarted — every file in those scopes exists as a 0-byte placeholder.

---

## Section 2: Subagent inventory

### N3 — Mortality
- **Owner:** Jonel
- **File:** `backend/subagents/mortality.py`
- **Data sources read:** `backend/data/nchs_maternal_mortality.csv` (loaded once at module import)
- **Findings returned:**
  - Maya (28y, Black, NY): 3 findings — all-ages MMR + age-cohort + racial disparity
  - Janet (41y, White, TX, hypertension): 2 findings — all-ages + age-cohort with "≈4× baseline" jump text (no disparity finding because race == comparison race)
  - Suppressed-cell case (Asian, age 22): 2+ findings — all-ages + age-cohort with NCHS-suppression fallback text
  - Unknown race (Native Hawaiian or Pacific Islander, no rows): `status="failed"` with descriptive `error_message`
- **Test file:** `tests/test_mortality.py` — 4 tests
- **Constraints for downstream:**
  - All findings carry `confidence="M"` (no H/L tiering implemented).
  - `agent_name="mortality"` and the NCHS source name contains "mortality"-keyword strings the scorer pattern-matches on (`scorer._has_mortality_signal` keys off the substring `"mortality"` in label/source).
  - Returns `failed` for any race not present in the CSV — orchestrator should expect mortality may fail.

### N4 — Guideline
- **Owner:** Luba
- **File:** `backend/subagents/guideline.py`
- **Data sources read:** `backend/data/static/cdc_hear_her_warning_signs.json`, `backend/data/static/acog_4th_trimester.json`
- **Findings returned:** Returns the full CDC Hear Her warning-sign set + every ACOG 4th-trimester entry whose `word_count` ≤ `ACOG_WORD_CAP` (100). Same set returned for Maya and Janet — no patient-specific filtering.
- **Test file:** `tests/test_subagents.py::TestGuidelineSubagent` — 6 tests
- **Constraints for downstream:**
  - CDC findings are `confidence="H"`; ACOG findings inherit confidence from the JSON entry.
  - The ACOG word-cap filter is logged (warning) but does not raise.
  - **Behavior mismatch flagged in Section 5:** the architecture doc describes weeks-postpartum filtering and complication-based elevation that are not implemented; the implementation returns the full set always.

### N5 — SDOH
- **Owner:** Luba
- **File:** `backend/subagents/sdoh.py`
- **Data sources read:** `backend/data/static/cms_hrsn_domains.json`
- **Findings returned:** **18** findings every time — 10 core CMS AHC HRSN domains + 8 supplemental domains. Identical output for Maya and Janet (no patient gating).
- **Test file:** `tests/test_subagents.py::TestSdohSubagent` — 6 tests (one explicitly asserts 18)
- **Constraints for downstream:**
  - All 18 findings are `confidence="M"`.
  - SDOH always returns `status="success"` unless an unexpected exception occurs.
  - **Behavior mismatch flagged in Section 5:** the architecture doc says "10 core domains" + "Medicaid note if payer=='Medicaid'"; implementation returns 18 with no Medicaid-conditional logic.

### N6 — Bundle
- **Owner:** Jonel
- **File:** `backend/subagents/bundle.py`
- **Data sources read:** `backend/data/cms_birthing_friendly_geocoded.csv`, `backend/data/cms_hcahps_ny.csv` (filtered to `H_COMP_6_LINEAR_SCORE` at load), `backend/data/cms_core_set_ny_2023.xlsx` and `cms_core_set_tx_2023.xlsx` (sheet `52. PPC-AD`, latest year 2023)
- **Findings returned:**
  - NY known hospital (Kaleida Health): 4 findings — BF + HCAHPS + state PPC-AD (NY 82.4%) + cross-state disparity
  - TX known hospital (Houston Methodist Hospital): 3 findings — BF + state PPC-AD (TX 77.4%) + cross-state disparity (HCAHPS is NY-only by design)
  - Unknown hospital: `status="partial"`, BF finding becomes "Not Designated", state + disparity findings still present
  - Unsupported state: `status="partial"`, single "State Hospital-Bundle Limitation" finding
- **Test file:** `tests/test_bundle.py` — 5 tests
- **Constraints for downstream:**
  - Hospital-name matching is stdlib-only (lowercase + strip + suffix-strip + exact-then-substring); will substring-match aggressively. Substring direction goes both ways.
  - Disparity finding always carries both NY 82.4% and TX 77.4% headline rates regardless of patient state — the synthesist should expect the same disparity label across both fixtures.

### N7 — State Context
- **Owner:** Jonel
- **File:** `backend/subagents/state_context.py`
- **Data sources read:** `backend/data/kff_postpartum_coverage.csv`, `backend/data/nnpqc_funding.csv`, `backend/data/static/state_qi_context.json`
- **Findings returned:**
  - NY/TX patient: 4 findings — KFF Medicaid extension + NNPQC funding + 2 state-QI facts (one general-tagged, one matched to `complications_flagged` via `COMPLICATION_TAG_MAP`; falls back to a second general-tagged fact when no complication match)
  - Unsupported state (e.g. CA): `status="partial"`, single "State Coverage Limitation" finding
- **Test file:** `tests/test_state_context.py` — 7 tests
- **Constraints for downstream:**
  - Complication-tag vocabulary is closed: `{hypertension, preeclampsia, hypertensive disorder, mental health, depression, anxiety, substance use, oud}`. Anything else falls back to general-only selection.
  - State-QI facts come from `state_qi_context.json`, which has its own `sources` field with custom names (e.g., NYSDOH, TCHMB) — the synthesist should expect more than just KFF/NNPQC source names from this agent.

---

## Section 3: Schema contracts

All dataclasses live in `backend/schemas/` and are re-exported from `backend/schemas/__init__.py`. Field lists below are pulled from the actual code; the **Doc check** column reports whether `ECHO_SCHEMA.md` matches.

### `PatientProfile` — `backend/schemas/patient_profile.py`
| Field | Type | Doc check |
|---|---|---|
| age | int | MATCHES |
| race_ethnicity | str | MATCHES |
| payer | str (must be in {Medicaid, Private, Other}) | MATCHES |
| state | str (2 chars) | MATCHES |
| hospital_name | str | MATCHES |
| weeks_postpartum | int (≥0) | MATCHES |
| primary_language | str | MATCHES |
| complications_flagged | list[str] (default `[]`) | MATCHES |

**Producer:** Frontend form (N1) → Orchestrator (N2). **Consumers:** every subagent (N3–N7), Scorer (N10).

### `DataSource` — `backend/schemas/subagent_return.py`
| Field | Type | Doc check |
|---|---|---|
| name | str (required, non-blank) | MATCHES |
| url | Optional[str] | MATCHES |

**Producer:** Subagents. **Consumer:** every layer that walks findings.

### `FindingItem` — `backend/schemas/subagent_return.py`
| Field | Type | Doc check |
|---|---|---|
| label | str (required) | MATCHES |
| detail | str (required) | MATCHES |
| confidence | str — must be in `{H, M, L, FLAGGED}` | MATCHES |
| sources | list[DataSource] (must contain ≥1) | MATCHES |

**Producer:** Subagents (and the synthesist when re-emitting with adjusted confidence). **Consumers:** Risk Synthesist, Scorer, Output Generator.

### `SubAgentReturn` — `backend/schemas/subagent_return.py`
| Field | Type | Doc check |
|---|---|---|
| agent_name | str (required) | MATCHES |
| status | str — `{success, partial, failed}` | MATCHES |
| findings | list[FindingItem] (default `[]`) | MATCHES |
| error_message | Optional[str] (required when status==failed) | MATCHES |

**Producer:** N3–N7. **Consumer:** Fallback (N9), then Risk Synthesist (N8).

### `SynthesistFlag` — `backend/schemas/synthesist_output.py`
| Field | Type | Doc check |
|---|---|---|
| flag_type | str — `{conflict, gap}` | MATCHES |
| label | str (required) | MATCHES |
| detail | str (required) | MATCHES |
| agents_involved | list[str] (default `[]`) | MATCHES |

**Producer:** Fallback (gap flags) and Risk Synthesist (conflict flags). **Consumer:** ChecklistOutput.

### `SynthesistOutput` — `backend/schemas/synthesist_output.py`
| Field | Type | Doc check |
|---|---|---|
| findings | list[FindingItem] | MATCHES |
| conflicts | list[SynthesistFlag] | MATCHES |
| subagents_completed | int (≥0) | MATCHES |
| subagents_failed | list[str] | MATCHES |
| subagents_partial | list[str] | MATCHES |

**Producer:** N8. **Consumer:** N10.

### `ScoredOutput` — `backend/schemas/scored_output.py`
| Field | Type | Doc check |
|---|---|---|
| synthesist_output | SynthesistOutput | MATCHES |
| patient_profile | PatientProfile | MATCHES |
| gap_score | float (0.0–1.0) | MATCHES |
| urgency_tier | str — `{HIGH, MED, LOW}` | MATCHES |
| disparity_flag | bool | MATCHES |
| lead_angle | str | MATCHES |

**Producer:** N10. **Consumer:** N11.

### `HospitalStatus` — `backend/schemas/checklist_output.py`
| Field | Type | Doc check |
|---|---|---|
| hospital_name | str | MATCHES |
| birthing_friendly | str — `{Meets criteria, Does not meet criteria, Not found in CMS dataset}` | MATCHES |
| status | str — `{success, partial}` | MATCHES |
| hcahps_discharge_score | Optional[float] | MATCHES |
| state_postpartum_visit_rate | Optional[float] | MATCHES |

**Producer:** N11 (built from N6 findings). **Consumer:** N13.

### `FramingBlock` — `backend/schemas/checklist_output.py`
| Field | Type | Doc check |
|---|---|---|
| framing_copy | str (required, non-blank) | MATCHES |
| framing_sources | list[DataSource] | MATCHES |
| see_also | list[str] | MATCHES |

**Producer:** N11 (loads from `framing_library.json`, N12). **Consumer:** N13.

### `ChecklistItem` — `backend/schemas/checklist_output.py`
| Field | Type | Doc check |
|---|---|---|
| label | str (required) | MATCHES |
| detail | str (required) | MATCHES |
| action | str (required) | MATCHES |
| source | str (required, non-blank) | MATCHES |
| confidence | str — `{H, M, L, FLAGGED}` | MATCHES |
| priority_rank | int (≥1) | MATCHES |

### `ChecklistOutput` — `backend/schemas/checklist_output.py`
| Field | Type | Doc check |
|---|---|---|
| items | list[ChecklistItem] (non-empty) | MATCHES |
| hospital_status | HospitalStatus | MATCHES |
| framing_block | FramingBlock | MATCHES |
| conflict_flags | list[SynthesistFlag] | MATCHES |
| confidence_summary | str (default `""`) | MATCHES |
| clinical_disclaimer | str — exact, never modified | MATCHES |

**Producer:** N11. **Consumer:** N13.

**Net schema verdict:** every dataclass in `ECHO_SCHEMA.md` matches the actual code field-for-field. No extra fields exist that are undocumented; no documented fields are missing.

---

## Section 4: Data file inventory

### `backend/data/` (loaded at runtime)
| File | Type | Used by | Size / rows |
|---|---|---|---|
| `cms_birthing_friendly_geocoded.csv` | CSV | N6 Bundle | 211,118 bytes / 2,265 rows |
| `cms_core_set_ny_2023.xlsx` | XLSX | N6 Bundle (sheet `52. PPC-AD`) | 133,482 bytes / 64 sheets |
| `cms_core_set_tx_2023.xlsx` | XLSX | N6 Bundle (sheet `52. PPC-AD`) | 160,509 bytes / 64 sheets |
| `cms_core_set_postpartum_cross_state.csv` | CSV | none — backup/sanity check (per `data_summary.md`) | 19,231 bytes / 59 rows (after metadata header) |
| `cms_hcahps_ny.csv` | CSV | N6 Bundle (filtered to `H_COMP_6_LINEAR_SCORE`) | 3,495,047 bytes / 10,948 rows |
| `cms_quality_measures_2021.csv` | CSV | none — baseline reference (per `data_summary.md`) | 2,821,890 bytes / 3,830 rows |
| `kff_postpartum_coverage.csv` | CSV | N7 State Context | 10,841 bytes / 113 rows (after 2 metadata rows) |
| `nchs_maternal_mortality.csv` | CSV | N3 Mortality | 6,256 bytes / 140 rows |
| `nnpqc_funding.csv` | CSV | N7 State Context | 1,885 bytes / 51 rows |
| `us_maternal_mortality_2019_2023.csv` | CSV | none yet — listed in `data_summary.md` for trend lines, not currently read by N3 | 73 bytes / 5 rows |

### `backend/data/static/`
| File | Type | Used by | Size / top-level keys |
|---|---|---|---|
| `acog_4th_trimester.json` | JSON | N4 Guideline | 6,093 bytes / `findings` |
| `cdc_hear_her_warning_signs.json` | JSON | N4 Guideline | 4,773 bytes / `warning_signs` |
| `cms_hrsn_domains.json` | JSON | N5 SDOH | 8,883 bytes / `core_domains`, `supplemental_domains` |
| `framing_library.json` | JSON | N11 Output Generator (not yet built) | 6,183 bytes / 7 identity keys + `default` |
| `state_qi_context.json` | JSON | N7 State Context | 5,731 bytes / `NY`, `TX` |

### `backend/data/sources/` (source material, not loaded at runtime)
| File | Type | Used by | Size |
|---|---|---|---|
| `acog_committee_opinion_736.pdf` | PDF | source for `acog_4th_trimester.json` | 414,035 bytes |
| `aim_postpartum_discharge_bundle_v2.pdf` | PDF | source material, not loaded at runtime | 169,811 bytes |
| `cdc_hear_her_warning_signs.pdf` | PDF | source for `cdc_hear_her_warning_signs.json` | 523,545 bytes |
| `cms_ahc_hrsn_screening_tool.pdf` | PDF | source for `cms_hrsn_domains.json` | 336,062 bytes |
| `cms_iqr_fy28_measures_directory.pdf` | PDF | source material, not loaded at runtime | 278,712 bytes |
| `cureus_racial_disparity_2025.pdf` | PDF | source material (PRMR figures), not loaded at runtime | 729,337 bytes |
| `nchs_maternal_mortality_2024.pdf` | PDF | source for `nchs_maternal_mortality.csv` | 297,515 bytes |
| `nysdoh_mental_health_pregnancy_deaths_2018_2021.pdf` | PDF | source for NY entries in `state_qi_context.json` | 237,659 bytes |
| `tchmb_pped_report_2024.pdf` | PDF | source for TX entries in `state_qi_context.json` | 1,019,955 bytes |

---

## Section 5: Drift between docs and code

Each item below explicitly states **MATCHES** or **DRIFT**. Findings are not fixed (read-only audit).

### CLAUDE.md File Index — file existence

- **DRIFT** — `tests/fixtures/maya.json` and `tests/fixtures/janet.json`. The CLAUDE.md File Index lists these under `tests/fixtures/`. Actual: the `tests/fixtures/` directory does **not exist**. Empty 0-byte files named `maya_scenario.json` and `janet_scenario.json` exist at `backend/fixtures/` instead, and the `backend/fixtures/` directory itself is not listed in the CLAUDE.md File Index.

- **DRIFT** — Test file roster. CLAUDE.md File Index lists `tests/test_subagents.py`, `test_synthesist.py`, `test_scorer.py`, `test_output_generator.py`, `test_end_to_end.py`. Actual `tests/` directory contains 12 test files: `test_bundle.py`, `test_end_to_end.py` (empty), `test_fallback.py`, `test_mortality.py`, `test_orchestrator.py` (empty), `test_output_generator.py` (empty), `test_risk_synthesist.py` (note: index says `test_synthesist.py`), `test_schemas.py`, `test_scorer.py`, `test_state_context.py`, `test_static_data.py`, `test_subagents.py`. Several real test files are not indexed; one indexed name (`test_synthesist.py`) is misspelled vs reality.

- **DRIFT** — `backend/data/static/` contents. CLAUDE.md File Index lists 4 JSONs (`cdc_hear_her_warning_signs.json`, `acog_4th_trimester.json`, `cms_hrsn_domains.json`, `framing_library.json`). Actual has 5: those 4 + `state_qi_context.json` (added during N7 build). The new file is not in the File Index.

- **DRIFT** — `frontend/` contents. CLAUDE.md File Index lists 2 files (`index.html`, `checklist.html`). Actual has 4 (`index.html`, `checklist.html`, `app.js`, `styles.css`) — all empty 0-byte stubs. Section 5 of CLAUDE.md does mention `styles.css` as a target, but the File Index does not list `styles.css` or `app.js`.

- **MATCHES** — every other file listed in the CLAUDE.md File Index for `backend/` (top-level Python files, `subagents/`, `schemas/`, `data/` CSVs/Excels, `data/sources/` PDFs) exists at the listed path with the listed name.

### ECHO_SCHEMA.md class definitions vs. code

- **MATCHES** — every dataclass in `backend/schemas/` has the exact field set described in `ECHO_SCHEMA.md` (see Section 3 above for field-by-field check). No undocumented extra fields. No documented field is missing in code.

### ECHO_BUILD_PLAN.md ownership vs. git authorship

Authorship from `git log --pretty=format:"%h %an %s"`:

- **MATCHES** — Step 1 Schemas. Doc owner: Luba. Git: every schema file is authored by Luba Kaper.
- **MATCHES** — Step 2 Static Data. Doc owners: Jonel + Luba. Git: NCHS CSV transcription by JoneL; clinical JSONs (`acog_4th_trimester.json`, `cdc_hear_her_warning_signs.json`, `cms_hrsn_domains.json`, `framing_library.json`) by Luba Kaper.
- **MATCHES** — Step 3 N3 Mortality. Doc owner: Jonel. Git: feat by JoneL (`6325edf`).
- **MATCHES** — Step 3 N4 Guideline. Doc owner: Luba. Git: feat by Luba Kaper (`4b713ff`).
- **MATCHES** — Step 3 N5 SDOH. Doc owner: Luba. Git: feat by Luba Kaper (`4b713ff`, same commit as N4).
- **MATCHES** — Step 3 N6 Bundle. Doc owner: Jonel. Git: feat by JoneL (`fa985f3`).
- **MATCHES** — Step 3 N7 State Context. Doc owner: Jonel. Git: feat by JoneL (`4103722`).
- **MATCHES** — Step 4 Fallback. Doc owner: Luba. Git: by Luba Kaper (`c67dff4`).
- **MATCHES** — Step 5 Risk Synthesist. Doc owner: Luba. Git: by Luba Kaper (`c67dff4`, bundled with fallback).
- **MATCHES** — Step 6 Scorer. Doc owner: Luba. Git: by Luba Kaper (`aab496d`).

### ECHO_ARCHITECTURE.md node behavior vs. built subagents

- **DRIFT** — N3 Mortality. Architecture doc says "Filters by race_ethnicity and state. Returns top 3 leading causes of maternal mortality with MMR values. confidence = H if 2+ sources confirm same cause, M if 1 source, L if extrapolated." Actual `mortality.py` filters by `race_ethnicity` and `age_group` (not state); returns up to 3 *structural* findings (all-ages MMR, age-cohort MMR, racial-disparity ratio) — not "top 3 leading causes"; all findings hardcoded `confidence="M"` (no H/L tiering). Note also `data_summary.md` and the build plan list NY MMRB / TX MMRB as sources for N3, but only the NCHS CSV is loaded.

- **DRIFT** — N4 Guideline. Architecture doc says "Loads ACOG postpartum care timeline filtered by `weeks_postpartum`. … Elevates matching signs if `complications_flagged` is not empty." Actual `guideline.py` does **not** filter ACOG by `weeks_postpartum` and does **not** elevate any sign by `complications_flagged`. It returns the full CDC Hear Her set + every ACOG entry under the word cap, identical for all patients. The build plan does say "Done when: each subagent tested individually against both demo fixtures and returns a valid SubAgentReturn" — that test passes — so this is a doc/code drift, not a test failure.

- **DRIFT** — N5 SDOH. Architecture doc says "Returns all 10 core CMS AHC HRSN domains. Adds Medicaid note if payer = 'Medicaid'." Actual `sdoh.py` returns **18** findings (10 core + 8 supplemental), with no Medicaid-conditional logic. `tests/test_subagents.py::TestSdohSubagent::test_returns_18_findings` explicitly asserts the 18-finding count, so the code and tests are internally consistent — only the architecture doc is out of date.

- **MATCHES** — N6 Bundle. Architecture doc behaviors (BF match, NY-only HCAHPS, state Core Set PPC-AD, partial when hospital not found) all match `bundle.py`.

- **MATCHES** (with a caveat) — N7 State Context. Architecture doc behaviors (KFF extension status, NNPQC funding context, NY/TX context notes) all show up in output. The build plan lists only `kff_postpartum_coverage.csv` and `nnpqc_funding.csv`; the architecture doc adds "static reference" without naming it. The actual subagent additionally loads `backend/data/static/state_qi_context.json` to source NY/TX context facts. The data source list in the build plan is therefore incomplete — flagging here so Paula and downstream consumers know to expect NYSDOH and TCHMB source names from this agent, not just KFF/NNPQC.

### data_summary.md filenames vs. filesystem

- **MATCHES** — every CSV/XLSX referenced in `data_summary.md` (`us_maternal_mortality_2019_2023.csv`, `cms_birthing_friendly_geocoded.csv`, `cms_hcahps_ny.csv`, `cms_core_set_ny_2023.xlsx`, `cms_core_set_tx_2023.xlsx`, `cms_core_set_postpartum_cross_state.csv`, `cms_quality_measures_2021.csv`, `kff_postpartum_coverage.csv`, `nnpqc_funding.csv`, `nchs_maternal_mortality.csv`) exists at `backend/data/`.
- **MATCHES** — every PDF referenced in `data_summary.md` (`nchs_maternal_mortality_2024.pdf`, `cureus_racial_disparity_2025.pdf`, `nysdoh_mental_health_pregnancy_deaths_2018_2021.pdf`, `cdc_hear_her_warning_signs.pdf`, `acog_committee_opinion_736.pdf`, `aim_postpartum_discharge_bundle_v2.pdf`, `cms_ahc_hrsn_screening_tool.pdf`, `tchmb_pped_report_2024.pdf`, `cms_iqr_fy28_measures_directory.pdf`) exists at `backend/data/sources/`.

---

## Section 6: What is left for Paula

### Luba's remaining Phase 3 work
- **None.** Luba has completed N4 Guideline, N5 SDOH, Fallback (N9), Risk Synthesist (N8), and Scorer (N10). All five subagents are built and merged. **However**, Section 5 above flags two doc-vs-code drifts in Luba's subagents that someone should resolve before demo:
  1. N4 Guideline does not filter by `weeks_postpartum` and does not elevate by `complications_flagged` (architecture says it should).
  2. N5 SDOH returns 18 findings with no Medicaid-conditional note (architecture says 10 + Medicaid note). Tests assert 18, so code and tests are aligned — the doc is the part out of step.

  These are not blockers; they need a decision: either update the docs to match shipping behavior, or refine the subagents.

### Paula's frontend and orchestrator work
- **Step 7 — Output Generator (`backend/output_generator.py`).** Paula. **0 bytes today.** Spec lives in `ECHO_BUILD_PLAN.md` Step 7 and `ECHO_ARCHITECTURE.md` N11. Must call the Anthropic API once with `claude-sonnet-4-20250514`, max_tokens 2000, no streaming; load identity-keyed copy from `framing_library.json`; emit a validated `ChecklistOutput` with the exact clinical disclaimer.
- **Step 10 — Frontend (`frontend/index.html`, `checklist.html`, `app.js`, `styles.css`).** Paula. **All 0 bytes today.** N1 form spec in build plan + architecture; N13 render order in build plan + architecture. Tailwind via CDN, no build step. Mobile-first. Display order is fixed (8 sections ending with the clinical disclaimer).

Paula does **not** own N2/N9 — Jonel owns the Orchestrator (`backend/orchestrator.py`, also 0 bytes today) and the FastAPI entry point (`backend/main.py`, 0 bytes today).

### Open follow-ups not yet addressed
- **Doc updates from Section 5 drift** (CLAUDE.md File Index, ECHO_ARCHITECTURE.md N3/N4/N5 behavior). Owner: whoever lands the next data-or-code change should refresh.
- **`tests/fixtures/`** does not exist; `backend/fixtures/maya_scenario.json` and `backend/fixtures/janet_scenario.json` are 0-byte placeholders. Step 11 end-to-end tests will need real fixture content — every subagent test currently uses inline `PatientProfile(...)` construction.
- **`tests/test_end_to_end.py`** is 0 bytes. Step 11 acceptance criteria are spelled out at the bottom of `ECHO_BUILD_PLAN.md` but no harness yet exists to run them.
- **Mortality "MMRB" data sources** (NY MMRB, TX MMRB) called out in `ECHO_BUILD_PLAN.md` Step 3 are not loaded by N3 today. If demo storyline depends on MMRB attribution, this needs a decision before demo.
