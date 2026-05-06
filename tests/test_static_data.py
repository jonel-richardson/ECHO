import json
import pathlib
import pytest

STATIC = pathlib.Path(__file__).parent.parent / "backend/data/static"


class TestCdcHearHer:
    def _load(self):
        return json.loads((STATIC / "cdc_hear_her_warning_signs.json").read_text())

    def test_file_exists(self):
        assert (STATIC / "cdc_hear_her_warning_signs.json").exists()

    def test_top_level_key(self):
        data = self._load()
        assert "warning_signs" in data

    def test_all_entries_have_required_fields(self):
        data = self._load()
        required = {"label", "detail", "confidence", "source_name", "source_url"}
        for entry in data["warning_signs"]:
            assert required.issubset(entry.keys()), f"Missing fields in: {entry}"

    def test_all_confidence_high(self):
        data = self._load()
        for entry in data["warning_signs"]:
            assert entry["confidence"] == "H", f"Expected H, got {entry['confidence']} for {entry['label']}"

    def test_source_is_cdc(self):
        data = self._load()
        for entry in data["warning_signs"]:
            assert entry["source_name"] == "CDC Hear Her"

    def test_minimum_entry_count(self):
        data = self._load()
        assert len(data["warning_signs"]) >= 8


class TestAcogFindingItem:
    def _load(self):
        return json.loads((STATIC / "acog_4th_trimester.json").read_text())

    def test_file_exists(self):
        assert (STATIC / "acog_4th_trimester.json").exists()

    def test_top_level_key(self):
        data = self._load()
        assert "findings" in data

    def test_all_entries_have_required_fields(self):
        data = self._load()
        required = {"label", "detail", "confidence", "source_name", "source_url", "word_count"}
        for entry in data["findings"]:
            assert required.issubset(entry.keys()), f"Missing fields in: {entry}"

    def test_all_word_counts_under_100(self):
        data = self._load()
        for entry in data["findings"]:
            assert entry["word_count"] <= 100, (
                f"{entry['label']} has word_count {entry['word_count']} — exceeds 100 word ACOG excerpt cap"
            )

    def test_all_details_contain_attribution(self):
        data = self._load()
        for entry in data["findings"]:
            assert "ACOG" in entry["detail"], (
                f"{entry['label']} detail missing ACOG attribution"
            )

    def test_source_is_acog(self):
        data = self._load()
        for entry in data["findings"]:
            assert entry["source_name"] == "ACOG Committee Opinion 736"

    def test_minimum_entry_count(self):
        data = self._load()
        assert len(data["findings"]) >= 6

    def test_actual_detail_word_count_under_100(self):
        data = self._load()
        for entry in data["findings"]:
            actual = len(entry["detail"].split())
            assert actual <= 100, (
                f"{entry['label']} detail has {actual} words — exceeds 100 word ACOG excerpt cap"
            )


class TestCmsHrsnDomains:
    def _load(self):
        return json.loads((STATIC / "cms_hrsn_domains.json").read_text())

    def test_file_exists(self):
        assert (STATIC / "cms_hrsn_domains.json").exists()

    def test_top_level_keys(self):
        data = self._load()
        assert "core_domains" in data
        assert "supplemental_domains" in data

    def test_exactly_10_core_domains(self):
        data = self._load()
        assert len(data["core_domains"]) == 10, (
            f"Expected 10 core domains, got {len(data['core_domains'])}"
        )

    def test_exactly_8_supplemental_domains(self):
        data = self._load()
        assert len(data["supplemental_domains"]) == 8, (
            f"Expected 8 supplemental domains, got {len(data['supplemental_domains'])}"
        )

    def test_all_entries_have_required_fields(self):
        data = self._load()
        required = {"label", "detail", "confidence", "source_name", "source_url", "domain_code"}
        for entry in data["core_domains"] + data["supplemental_domains"]:
            assert required.issubset(entry.keys()), f"Missing fields in: {entry}"

    def test_all_confidence_medium(self):
        data = self._load()
        for entry in data["core_domains"] + data["supplemental_domains"]:
            assert entry["confidence"] == "M", (
                f"Expected M confidence for SDOH domain {entry['label']}, got {entry['confidence']}"
            )

    def test_domain_codes_unique(self):
        data = self._load()
        codes = [e["domain_code"] for e in data["core_domains"] + data["supplemental_domains"]]
        assert len(codes) == len(set(codes)), "Duplicate domain_code found"
