"""Project-wide constants. Centralized per CLAUDE.md Section 5."""

NCHS_SOURCE_NAME = "NCHS Health E-Stat 113"
NCHS_SOURCE_URL = "https://dx.doi.org/10.15620/cdc/174651"
NCHS_LATEST_YEAR = 2024

KFF_SOURCE_NAME = "KFF Medicaid Postpartum Coverage Extension Tracker"
KFF_SOURCE_URL = "https://www.kff.org/medicaid/state-indicator/medicaid-postpartum-coverage/"
NNPQC_SOURCE_NAME = "National Network of Perinatal Quality Collaboratives (NNPQC)"
NNPQC_SOURCE_URL = "https://nnpqc.org/"

SUPPORTED_STATES = {"NY", "TX"}
STATE_NAMES = {"NY": "New York", "TX": "Texas"}
CDC_HEAR_HER_SOURCE_NAME = "CDC Hear Her"
CDC_HEAR_HER_SOURCE_URL = "https://www.cdc.gov/hearher"
ACOG_CO_736_SOURCE_NAME = "ACOG Committee Opinion 736"
ACOG_CO_736_SOURCE_URL = "https://www.acog.org/clinical/clinical-guidance/committee-opinion/articles/2018/05/optimizing-postpartum-care"
CMS_HRSN_SOURCE_NAME = "CMS AHC HRSN Screening Tool"
CMS_HRSN_SOURCE_URL = "https://www.cms.gov/priorities/innovation/innovation-models/ahc"

CMS_BIRTHING_FRIENDLY_SOURCE_NAME = "CMS Birthing-Friendly Hospital Designation"
CMS_BIRTHING_FRIENDLY_SOURCE_URL = (
    "https://data.cms.gov/provider-data/birthing-friendly-hospitals-and-health-systems"
)
CMS_HCAHPS_SOURCE_NAME = "CMS HCAHPS Hospital Survey"
CMS_HCAHPS_SOURCE_URL = "https://www.hcahpsonline.org/"
CMS_CORE_SET_SOURCE_NAME = "CMS Medicaid Adult Core Set (PPC-AD)"
CMS_CORE_SET_SOURCE_URL = (
    "https://www.medicaid.gov/medicaid/quality-of-care/performance-measurement/"
    "adult-and-child-health-care-quality-measures"
)

HCAHPS_DISCHARGE_MEASURE_ID = "H_COMP_6_LINEAR_SCORE"
PPC_AD_SHEET_NAME = "52. PPC-AD"
PPC_AD_LATEST_YEAR = 2023

ACOG_WORD_CAP = 100

MIN_SOURCES_CONFIRMED = 2

CONFIDENCE_HIGH = "H"
CONFIDENCE_MEDIUM = "M"
CONFIDENCE_LOW = "L"
CONFIDENCE_FLAGGED = "FLAGGED"
CONFIDENCE_GAP_VALUES = {CONFIDENCE_LOW, CONFIDENCE_FLAGGED}
CONFIDENCE_RANK = {
    CONFIDENCE_HIGH: 3,
    CONFIDENCE_MEDIUM: 2,
    CONFIDENCE_LOW: 1,
    CONFIDENCE_FLAGGED: 0,
}

URGENCY_HIGH = "HIGH"
URGENCY_MEDIUM = "MED"
URGENCY_LOW = "LOW"

DISPARITY_RACE_ETHNICITY = "Black or African American"
DISPARITY_STATES = {"NY", "TX"}
MORTALITY_SOURCE_KEYWORD = "mortality"

SUBAGENT_TIMEOUT_SECONDS = 25
API_TIMEOUT_SECONDS = 90

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_MAX_TOKENS = 8000
