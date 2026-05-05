from dataclasses import dataclass

from .synthesist_output import SynthesistOutput
from .patient_profile import PatientProfile


VALID_URGENCY_TIERS = {"HIGH", "MED", "LOW"}


@dataclass
class ScoredOutput:
    synthesist_output: SynthesistOutput
    patient_profile: PatientProfile
    gap_score: float
    urgency_tier: str
    disparity_flag: bool
    lead_angle: str

    def __post_init__(self):
        errors = []

        if not (0.0 <= self.gap_score <= 1.0):
            errors.append("gap_score must be between 0.0 and 1.0")

        if self.urgency_tier not in VALID_URGENCY_TIERS:
            errors.append(f"urgency_tier must be one of: {', '.join(VALID_URGENCY_TIERS)}")

        if not self.lead_angle or not self.lead_angle.strip():
            errors.append("lead_angle is required")

        if errors:
            raise ValueError(f"ScoredOutput validation failed: {'; '.join(errors)}")
