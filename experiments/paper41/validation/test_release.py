"""Mutation controls for the Paper XLI candidate validator."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_release as release


class CandidateValidationTests(unittest.TestCase):
    def check_rejected_manifest(self, mutate) -> None:
        manifest = json.loads(release.MANIFEST.read_text(encoding="utf-8"))
        mutate(manifest)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(release, "MANIFEST", path):
                with self.assertRaises(ValueError):
                    release.check_manifest()

    def check_rejected_evidence(self, mutate) -> None:
        evidence = json.loads(release.EVIDENCE_MAP.read_text(encoding="utf-8"))
        mutate(evidence)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            with patch.object(release, "EVIDENCE_MAP", path):
                with self.assertRaises(ValueError):
                    release.check_historical()

    def test_current_candidate_passes(self) -> None:
        release.check_historical()
        release.check_citations()
        self.assertEqual(release.check_manifest()[0], len(release.ARTIFACTS))

    def test_rejects_publication_promotion(self) -> None:
        self.check_rejected_manifest(
            lambda m: m.__setitem__("release_identity_claimed", True)
        )

    def test_rejects_digest_drift(self) -> None:
        self.check_rejected_manifest(
            lambda m: m["artifacts"][0].__setitem__("sha256", "0" * 64)
        )

    def test_rejects_duplicate_role(self) -> None:
        self.check_rejected_manifest(
            lambda m: m["artifacts"][1].__setitem__(
                "role", m["artifacts"][0]["role"]
            )
        )

    def test_rejects_hal_acceptance_claim(self) -> None:
        self.check_rejected_evidence(
            lambda e: e["historical_submission"].__setitem__(
                "status", "PUBLISHED"
            )
        )

    def test_rejects_historical_digest_rebinding(self) -> None:
        self.check_rejected_evidence(
            lambda e: e["historical_submission"]["source_files"][0].__setitem__(
                "sha256", "0" * 64
            )
        )


if __name__ == "__main__":
    unittest.main()
