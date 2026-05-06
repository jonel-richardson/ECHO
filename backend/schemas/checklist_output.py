from dataclasses import dataclass, field
from typing import List, Optional

from .synthesist_output import SynthesistFlag
from .subagent_return import DataSource


VALID_CONFIDENCE = {"H", "M", "L", "FLAGGED"}
VALID_HOSPITAL_STATUSES = {"success", "partial"}

CLINICAL_DISCLAIMER = (
    "ECHO is clinical decision support, not a diagnostic engine. "
    "All items are for clinical review only. "
    "Action language reflects screening guidance — not a diagnosis or treatment recommendation. "
    "Source citations are provided for every item. "
    "CNM clinical judgment governs all care decisions."
)


@dataclass
class ChecklistItem:
    label: str
    detail: str
    action: str
    source: str
    confidence: str
    priority_rank: int

    def __post_init__(self):
        errors = []

        if not self.label or not self.label.strip():
            errors.append("label is required")

        if not self.detail or not self.detail.strip():
            errors.append("detail is required")

        if not self.action or not self.action.strip():
            errors.append("action is required")

        if not self.source or not self.source.strip():
            errors.append("source is required")

        if self.confidence not in VALID_CONFIDENCE:
            errors.append(f"confidence must be one of: {', '.join(VALID_CONFIDENCE)}")

        if not isinstance(self.priority_rank, int) or self.priority_rank < 1:
            errors.append("priority_rank must be a positive integer")

        if errors:
            raise ValueError(f"ChecklistItem validation failed: {'; '.join(errors)}")


@dataclass
class HospitalStatus:
    hospital_name: str
    birthing_friendly: str
    status: str
    hcahps_discharge_score: Optional[float] = None

    def __post_init__(self):
        errors = []

        valid_designations = {
            "Meets criteria",
            "Does not meet criteria",
            "Not found in CMS dataset"
        }

        if self.birthing_friendly not in valid_designations:
            errors.append(f"birthing_friendly must be one of: {', '.join(valid_designations)}")

        if self.status not in VALID_HOSPITAL_STATUSES:
            errors.append(f"status must be one of: {', '.join(VALID_HOSPITAL_STATUSES)}")

        if errors:
            raise ValueError(f"HospitalStatus validation failed: {'; '.join(errors)}")


@dataclass
class FramingBlock:
    framing_copy: str
    framing_sources: List[DataSource] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.framing_copy or not self.framing_copy.strip():
            raise ValueError("FramingBlock.framing_copy is required")


@dataclass
class ChecklistOutput:
    items: List[ChecklistItem]
    hospital_status: HospitalStatus
    framing_block: FramingBlock
    conflict_flags: List[SynthesistFlag] = field(default_factory=list)
    confidence_summary: str = ""
    clinical_disclaimer: str = CLINICAL_DISCLAIMER

    def __post_init__(self):
        errors = []

        if not self.items:
            errors.append("items list cannot be empty")

        if self.clinical_disclaimer != CLINICAL_DISCLAIMER:
            errors.append("clinical_disclaimer must not be modified")

        if errors:
            raise ValueError(f"ChecklistOutput validation failed: {'; '.join(errors)}")
