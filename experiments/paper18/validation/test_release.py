"""Hostile checks for Paper XVIII's release binding."""

from __future__ import annotations

import copy
import unittest

import validate_release as release


class ReleaseBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = release.manifest_payload()

    def test_historical_commit_and_inventory_are_fixed(self) -> None:
        self.assertEqual(self.manifest["historical_evidence"]["commit"], release.HISTORICAL_COMMIT)
        self.assertEqual(len(self.manifest["historical_evidence"]["artifacts"]), 33)
        self.assertTrue(release.REQUIRED_HISTORICAL.issubset(
            {row["path"] for row in self.manifest["historical_evidence"]["artifacts"]}
        ))

    def test_changed_historical_digest_is_rejected(self) -> None:
        altered = copy.deepcopy(self.manifest)
        altered["historical_evidence"]["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale or noncanonical"):
            release.validate_manifest(altered)

    def test_dropped_historical_file_is_rejected(self) -> None:
        altered = copy.deepcopy(self.manifest)
        altered["historical_evidence"]["artifacts"].pop()
        with self.assertRaisesRegex(ValueError, "stale or noncanonical"):
            release.validate_manifest(altered)

    def test_archive_identities_and_replay_claims_are_fixed(self) -> None:
        altered = copy.deepcopy(self.manifest)
        altered["external_packages"]["compact_witness"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale or noncanonical"):
            release.validate_manifest(altered)
        self.assertFalse(release.REPLAY["dataset_carrier_replayed"])
        self.assertFalse(release.REPLAY["paper18_publication_identity_claimed"])

    def test_unsafe_paths_are_rejected(self) -> None:
        for value in ("../escape", "C:/escape", "a\\b", "/absolute"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                release.checked_path(value)

    def test_headline_claims_match_retained_results(self) -> None:
        release.validate_claim_values()


if __name__ == "__main__":
    unittest.main()
