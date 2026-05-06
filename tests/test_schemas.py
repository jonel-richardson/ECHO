import pytest
from backend.schemas.subagent_return import DataSource, FindingItem, SubAgentReturn


class TestFindingItem:
    def test_empty_sources_raises(self):
        with pytest.raises(ValueError, match="sources must contain at least one DataSource"):
            FindingItem(
                label="Hypertensive Disorder Risk",
                detail="Elevated blood pressure at 6 weeks postpartum.",
                confidence="H",
                sources=[]
            )
