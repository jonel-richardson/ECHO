import pytest
from backend.schemas.subagent_return import DataSource, FindingItem, SubAgentReturn
from backend.schemas.synthesist_output import SynthesistFlag, SynthesistOutput
from backend.schemas.patient_profile import PatientProfile
from backend.schemas.scored_output import ScoredOutput
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


class TestHospitalStatus:
    def test_valid_with_state_rate(self):
        hs = HospitalStatus(
            hospital_name="NYC Health + Hospitals/Lincoln",
            birthing_friendly="Meets criteria",
            status="success",
            state_postpartum_visit_rate=0.72
        )
        assert hs.state_postpartum_visit_rate == 0.72

    def test_valid_without_state_rate(self):
        hs = HospitalStatus(
            hospital_name="NYC Health + Hospitals/Lincoln",
            birthing_friendly="Meets criteria",
            status="success"
        )
        assert hs.state_postpartum_visit_rate is None

    def test_invalid_birthing_friendly_raises(self):
        with pytest.raises(ValueError, match="birthing_friendly must be one of"):
            HospitalStatus(
                hospital_name="NYC Health + Hospitals/Lincoln",
                birthing_friendly="Unknown",
                status="success"
            )


class TestDataSource:
    def test_valid(self):
        ds = DataSource(name="CDC Hear Her", url="https://www.cdc.gov/hearher")
        assert ds.name == "CDC Hear Her"
        assert ds.url == "https://www.cdc.gov/hearher"

    def test_valid_no_url(self):
        ds = DataSource(name="NCHS Health E-Stat 113")
        assert ds.url is None

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="DataSource.name is required"):
            DataSource(name="")

    def test_whitespace_name_raises(self):
        with pytest.raises(ValueError, match="DataSource.name is required"):
            DataSource(name="   ")


class TestFindingItem:
    def test_valid(self):
        fi = FindingItem(
            label="Hypertensive Disorder Risk",
            detail="Persistent headache may indicate hypertensive disorder of pregnancy.",
            confidence="H",
            sources=[DataSource(name="CDC Hear Her")]
        )
        assert fi.label == "Hypertensive Disorder Risk"
        assert fi.confidence == "H"
        assert len(fi.sources) == 1

    def test_empty_sources_raises(self):
        with pytest.raises(ValueError, match="sources must contain at least one DataSource"):
            FindingItem(
                label="Hypertensive Disorder Risk",
                detail="Elevated blood pressure at 6 weeks postpartum.",
                confidence="H",
                sources=[]
            )

    def test_invalid_confidence_raises(self):
        with pytest.raises(ValueError, match="confidence must be one of"):
            FindingItem(
                label="Test",
                detail="Test detail",
                confidence="X",
                sources=[DataSource(name="CDC Hear Her")]
            )

    def test_flagged_confidence_is_valid(self):
        fi = FindingItem(
            label="Blood Pressure Risk",
            detail="Conflicting subagent evidence requires CNM review.",
            confidence="FLAGGED",
            sources=[DataSource(name="CDC Hear Her")]
        )
        assert fi.confidence == "FLAGGED"

    def test_empty_label_raises(self):
        with pytest.raises(ValueError, match="label is required"):
            FindingItem(
                label="",
                detail="Test detail",
                confidence="H",
                sources=[DataSource(name="CDC Hear Her")]
            )


class TestSubAgentReturn:
    def test_valid_success(self):
        sar = SubAgentReturn(
            agent_name="mortality",
            status="success",
            findings=[
                FindingItem(
                    label="Mortality Risk",
                    detail="Black women in NY face elevated maternal mortality rates.",
                    confidence="H",
                    sources=[DataSource(name="NCHS Health E-Stat 113")]
                )
            ]
        )
        assert sar.status == "success"
        assert len(sar.findings) == 1

    def test_valid_failed_with_message(self):
        sar = SubAgentReturn(
            agent_name="bundle",
            status="failed",
            error_message="CMS data file not found"
        )
        assert sar.status == "failed"
        assert sar.error_message == "CMS data file not found"
        assert sar.findings == []

    def test_failed_without_message_raises(self):
        with pytest.raises(ValueError, match="error_message is required when status is 'failed'"):
            SubAgentReturn(agent_name="bundle", status="failed")

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="status must be one of"):
            SubAgentReturn(agent_name="mortality", status="unknown")


class TestSynthesistFlag:
    def test_valid_conflict(self):
        sf = SynthesistFlag(
            flag_type="conflict",
            label="Blood Pressure Risk",
            detail="Mortality subagent reports HIGH; bundle subagent reports LOW.",
            agents_involved=["mortality", "bundle"]
        )
        assert sf.flag_type == "conflict"

    def test_valid_gap(self):
        sf = SynthesistFlag(
            flag_type="gap",
            label="SDOH screening",
            detail="sdoh subagent failed — SDOH findings unavailable.",
            agents_involved=["sdoh"]
        )
        assert sf.flag_type == "gap"

    def test_invalid_flag_type_raises(self):
        with pytest.raises(ValueError, match="flag_type must be one of"):
            SynthesistFlag(
                flag_type="warning",
                label="Test",
                detail="Test detail"
            )

    def test_empty_label_raises(self):
        with pytest.raises(ValueError, match="label is required"):
            SynthesistFlag(flag_type="gap", label="", detail="Test detail")


class TestSynthesistOutput:
    def test_valid(self):
        so = SynthesistOutput(
            findings=[
                FindingItem(
                    label="Mortality Risk",
                    detail="Elevated risk in NY for Black women.",
                    confidence="H",
                    sources=[DataSource(name="NCHS Health E-Stat 113")]
                )
            ],
            subagents_completed=5
        )
        assert so.subagents_completed == 5
        assert so.subagents_failed == []

    def test_negative_subagents_completed_raises(self):
        with pytest.raises(ValueError, match="subagents_completed must be a non-negative integer"):
            SynthesistOutput(findings=[], subagents_completed=-1)


class TestPatientProfile:
    def test_valid(self):
        pp = PatientProfile(
            age=28,
            race_ethnicity="Black or African American",
            payer="Medicaid",
            state="NY",
            hospital_name="NYC Health + Hospitals/Lincoln",
            weeks_postpartum=6,
            primary_language="English"
        )
        assert pp.age == 28
        assert pp.complications_flagged == []

    def test_valid_with_complications(self):
        pp = PatientProfile(
            age=41,
            race_ethnicity="White",
            payer="Private",
            state="TX",
            hospital_name="Baylor Scott & White Medical Center",
            weeks_postpartum=4,
            primary_language="English",
            complications_flagged=["hypertension", "hemorrhage"]
        )
        assert pp.complications_flagged == ["hypertension", "hemorrhage"]

    def test_invalid_payer_raises(self):
        with pytest.raises(ValueError, match="payer must be one of"):
            PatientProfile(
                age=28,
                race_ethnicity="Black or African American",
                payer="Medicare",
                state="NY",
                hospital_name="NYC Health + Hospitals/Lincoln",
                weeks_postpartum=6,
                primary_language="English"
            )

    def test_state_not_two_chars_raises(self):
        with pytest.raises(ValueError, match="state must be a 2-letter state code"):
            PatientProfile(
                age=28,
                race_ethnicity="Black or African American",
                payer="Medicaid",
                state="New York",
                hospital_name="NYC Health + Hospitals/Lincoln",
                weeks_postpartum=6,
                primary_language="English"
            )

    def test_negative_age_raises(self):
        with pytest.raises(ValueError, match="age must be a positive integer"):
            PatientProfile(
                age=-1,
                race_ethnicity="Black or African American",
                payer="Medicaid",
                state="NY",
                hospital_name="NYC Health + Hospitals/Lincoln",
                weeks_postpartum=6,
                primary_language="English"
            )


class TestScoredOutput:
    def _synthesist(self):
        return SynthesistOutput(findings=[], subagents_completed=5)

    def _profile(self):
        return PatientProfile(
            age=28,
            race_ethnicity="Black or African American",
            payer="Medicaid",
            state="NY",
            hospital_name="NYC Health + Hospitals/Lincoln",
            weeks_postpartum=6,
            primary_language="English"
        )

    def test_valid(self):
        so = ScoredOutput(
            synthesist_output=self._synthesist(),
            patient_profile=self._profile(),
            gap_score=0.2,
            urgency_tier="MED",
            disparity_flag=True,
            lead_angle="mortality"
        )
        assert so.disparity_flag is True
        assert so.urgency_tier == "MED"

    def test_gap_score_out_of_range_raises(self):
        with pytest.raises(ValueError, match="gap_score must be between 0.0 and 1.0"):
            ScoredOutput(
                synthesist_output=self._synthesist(),
                patient_profile=self._profile(),
                gap_score=1.5,
                urgency_tier="MED",
                disparity_flag=False,
                lead_angle="mortality"
            )

    def test_invalid_urgency_tier_raises(self):
        with pytest.raises(ValueError, match="urgency_tier must be one of"):
            ScoredOutput(
                synthesist_output=self._synthesist(),
                patient_profile=self._profile(),
                gap_score=0.2,
                urgency_tier="CRITICAL",
                disparity_flag=False,
                lead_angle="mortality"
            )


class TestChecklistItem:
    def test_valid(self):
        item = ChecklistItem(
            label="Severe Headache",
            detail="Sudden severe headache can indicate postpartum preeclampsia.",
            action="Consider screening for headache severity and blood pressure elevation.",
            source="CDC Hear Her",
            confidence="H",
            priority_rank=1
        )
        assert item.priority_rank == 1

    def test_empty_source_raises(self):
        with pytest.raises(ValueError, match="source is required"):
            ChecklistItem(
                label="Severe Headache",
                detail="Test detail",
                action="Consider screening for headache.",
                source="",
                confidence="H",
                priority_rank=1
            )

    def test_invalid_confidence_raises(self):
        with pytest.raises(ValueError, match="confidence must be one of"):
            ChecklistItem(
                label="Severe Headache",
                detail="Test detail",
                action="Consider screening for headache.",
                source="CDC Hear Her",
                confidence="X",
                priority_rank=1
            )

    def test_priority_rank_zero_raises(self):
        with pytest.raises(ValueError, match="priority_rank must be a positive integer"):
            ChecklistItem(
                label="Severe Headache",
                detail="Test detail",
                action="Consider screening for headache.",
                source="CDC Hear Her",
                confidence="H",
                priority_rank=0
            )
