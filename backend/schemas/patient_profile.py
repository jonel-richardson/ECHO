from dataclasses import dataclass, field
from typing import List


REQUIRED_FIELDS = [
    "age", "race_ethnicity", "payer", "state",
    "hospital_name", "weeks_postpartum", "primary_language"
]

VALID_PAYERS = {"Medicaid", "Private", "Other"}


@dataclass
class PatientProfile:
    age: int
    race_ethnicity: str
    payer: str
    state: str
    hospital_name: str
    weeks_postpartum: int
    primary_language: str
    complications_flagged: List[str] = field(default_factory=list)

    def __post_init__(self):
        errors = []

        if not isinstance(self.age, int) or self.age <= 0:
            errors.append("age must be a positive integer")

        if not self.race_ethnicity or not self.race_ethnicity.strip():
            errors.append("race_ethnicity is required")

        if self.payer not in VALID_PAYERS:
            errors.append(f"payer must be one of: {', '.join(VALID_PAYERS)}")

        if not self.state or len(self.state.strip()) != 2:
            errors.append("state must be a 2-letter state code")

        if not self.hospital_name or not self.hospital_name.strip():
            errors.append("hospital_name is required")

        if not isinstance(self.weeks_postpartum, int) or self.weeks_postpartum < 0:
            errors.append("weeks_postpartum must be a non-negative integer")

        if not self.primary_language or not self.primary_language.strip():
            errors.append("primary_language is required")

        if errors:
            raise ValueError(f"PatientProfile validation failed: {'; '.join(errors)}")
