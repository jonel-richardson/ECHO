import pytest
from backend.schemas.subagent_return import DataSource, FindingItem, SubAgentReturn
from backend.schemas.checklist_output import (
    ChecklistItem, HospitalStatus, FramingBlock, ChecklistOutput, CLINICAL_DISCLAIMER
)


class TestFramingBlock:
    def test_valid(self):
        fb = FramingBlock(
            framing_copy="Consider discussing postpartum warning signs at this visit.",
            framing_sources=[DataSource(name="CDC Hear Her", url="https://www.cdc.gov/hearher")],
            see_also=["https://www.awhonn.org/awhonn-sbars"]
        )
        assert fb.framing_copy == "Consider discussing postpartum warning signs at this visit."
        assert fb.see_also == ["https://www.awhonn.org/awhonn-sbars"]

    def test_empty_framing_copy_raises(self):
        with pytest.raises(ValueError, match="framing_copy is required"):
            FramingBlock(framing_copy="")

    def test_whitespace_framing_copy_raises(self):
        with pytest.raises(ValueError, match="framing_copy is required"):
            FramingBlock(framing_copy="   ")


class TestFindingItem:
    def test_empty_sources_raises(self):
        with pytest.raises(ValueError, match="sources must contain at least one DataSource"):
            FindingItem(
                label="Hypertensive Disorder Risk",
                detail="Elevated blood pressure at 6 weeks postpartum.",
                confidence="H",
                sources=[]
            )
