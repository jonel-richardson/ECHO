from dataclasses import dataclass, field
from typing import List

from .subagent_return import FindingItem


VALID_FLAG_TYPES = {"conflict", "gap"}


@dataclass
class SynthesistFlag:
    flag_type: str
    label: str
    detail: str
    agents_involved: List[str] = field(default_factory=list)

    def __post_init__(self):
        errors = []

        if self.flag_type not in VALID_FLAG_TYPES:
            errors.append(f"flag_type must be one of: {', '.join(VALID_FLAG_TYPES)}")

        if not self.label or not self.label.strip():
            errors.append("label is required")

        if not self.detail or not self.detail.strip():
            errors.append("detail is required")

        if errors:
            raise ValueError(f"SynthesistFlag validation failed: {'; '.join(errors)}")


@dataclass
class SynthesistOutput:
    findings: List[FindingItem]
    conflicts: List[SynthesistFlag] = field(default_factory=list)
    subagents_completed: int = 0
    subagents_failed: List[str] = field(default_factory=list)
    subagents_partial: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.subagents_completed < 0:
            raise ValueError("subagents_completed must be a non-negative integer")
