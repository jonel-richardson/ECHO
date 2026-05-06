import json
import pathlib
import pytest

STATIC = pathlib.Path("backend/data/static")


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
