from dataclasses import dataclass, field
from typing import List, Optional


VALID_STATUSES = {"success", "partial", "failed"}
VALID_CONFIDENCE = {"H", "M", "L"}


@dataclass
class DataSource:
    name: str
    url: Optional[str] = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("DataSource.name is required")


@dataclass
class FindingItem:
    label: str
    detail: str
    confidence: str
    sources: List[DataSource] = field(default_factory=list)

    def __post_init__(self):
        errors = []

        if not self.label or not self.label.strip():
            errors.append("label is required")

        if not self.detail or not self.detail.strip():
            errors.append("detail is required")

        if self.confidence not in VALID_CONFIDENCE:
            errors.append(f"confidence must be one of: {', '.join(VALID_CONFIDENCE)}")

        if not self.sources:
            errors.append("sources must contain at least one DataSource")

        if errors:
            raise ValueError(f"FindingItem validation failed: {'; '.join(errors)}")


@dataclass
class SubAgentReturn:
    agent_name: str
    status: str
    findings: List[FindingItem] = field(default_factory=list)
    error_message: Optional[str] = None

    def __post_init__(self):
        errors = []

        if not self.agent_name or not self.agent_name.strip():
            errors.append("agent_name is required")

        if self.status not in VALID_STATUSES:
            errors.append(f"status must be one of: {', '.join(VALID_STATUSES)}")

        if self.status == "failed" and not self.error_message:
            errors.append("error_message is required when status is 'failed'")

        if errors:
            raise ValueError(f"SubAgentReturn validation failed: {'; '.join(errors)}")
