#!/usr/bin/env python3
"""Hostile tests for the compact drive-audit gate, not microscopic dynamics."""

from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

import validate_release_v2 as gate


class CompactDriveGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original = gate.read
        self.record = self.original(gate.REPO / gate.DRIVE)

    def check_record(self, record: dict) -> dict:
        def read(path):
            return record if path == gate.REPO / gate.DRIVE else self.original(path)

        with patch.object(gate, "read", side_effect=read):
            return gate.validate_drive()

    def test_retained_readout_passes_as_compact_only(self) -> None:
        result = self.check_record(self.record)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["source_payloads_replayed"])
        self.assertFalse(result["operator_action_recomputed"])

    def test_narrowed_saved_time_coverage_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["coverage"]["times"] = [2, 3]
        with self.assertRaises(ValueError):
            self.check_record(record)

    def test_duplicate_cohort_time_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["by_cohort_time"][-1] = copy.deepcopy(record["by_cohort_time"][0])
        with self.assertRaises(ValueError):
            self.check_record(record)

    def test_changed_parent_digest_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["inputs"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.check_record(record)

    def test_positive_drive_or_independent_validation_rejected(self) -> None:
        for field in ("drive", "independence"):
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                if field == "drive":
                    record["summary"]["nonzero_clipped_drive_source_times"] = 1
                else:
                    record["independent_validation"] = True
                with self.assertRaises(ValueError):
                    self.check_record(record)


if __name__ == "__main__":
    unittest.main()
