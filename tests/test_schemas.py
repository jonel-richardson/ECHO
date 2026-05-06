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


class TestChecklistOutput:
    def _item(self):
        return ChecklistItem(
            label="Severe Headache",
            detail="Sudden severe headache is a postpartum warning sign.",
            action="Consider screening for headache severity and blood pressure.",
            source="CDC Hear Her",
            confidence="H",
            priority_rank=1
        )

    def _hospital(self):
        return HospitalStatus(
            hospital_name="NYC Health + Hospitals/Lincoln",
            birthing_friendly="Meets criteria",
            status="success"
        )

    def _framing(self):
        return FramingBlock(
            framing_copy="Consider reviewing the following postpartum warning signs.",
            framing_sources=[DataSource(name="CDC Hear Her")],
            see_also=[]
        )

    def test_valid(self):
        output = ChecklistOutput(
            items=[self._item()],
            hospital_status=self._hospital(),
            framing_block=self._framing()
        )
        assert output.clinical_disclaimer == CLINICAL_DISCLAIMER
        assert output.framing_block.framing_copy == "Consider reviewing the following postpartum warning signs."

    def test_empty_items_raises(self):
        with pytest.raises(ValueError, match="items list cannot be empty"):
            ChecklistOutput(
                items=[],
                hospital_status=self._hospital(),
                framing_block=self._framing()
            )

    def test_modified_disclaimer_raises(self):
        with pytest.raises(ValueError, match="clinical_disclaimer must not be modified"):
            ChecklistOutput(
                items=[self._item()],
                hospital_status=self._hospital(),
                framing_block=self._framing(),
                clinical_disclaimer="Do not use this tool for diagnosis."
            )


class TestFindingItem:
    def test_empty_sources_raises(self):
        with pytest.raises(ValueError, match="sources must contain at least one DataSource"):
            FindingItem(
                label="Hypertensive Disorder Risk",
                detail="Elevated blood pressure at 6 weeks postpartum.",
                confidence="H",
                sources=[]
            )
