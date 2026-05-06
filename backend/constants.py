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
