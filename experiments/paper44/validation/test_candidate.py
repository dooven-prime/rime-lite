"""Mutation controls for the Paper XLIV first-numbered candidate gate."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import validate_candidate as gate


class CandidateTests(unittest.TestCase):
    def check_mutated_manifest(self, mutation) -> None:
        manifest = json.loads(gate.MANIFEST.read_text(encoding="utf-8"))
        mutation(manifest)
        with tempfile.TemporaryDirectory() as directory:
            replacement = Path(directory) / "manifest.json"
            replacement.write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(gate, "MANIFEST", replacement):
                with self.assertRaises(ValueError):
                    gate.check_manifest()

    def test_current_candidate_passes(self) -> None:
        gate.check_review()
        gate.check_citations()
        gate.check_lean_source()
        self.assertEqual(gate.check_manifest(), len(gate.ARTIFACTS))

    def test_rejects_publication_promotion(self) -> None:
        self.check_mutated_manifest(lambda value: value.__setitem__("external_anchor_claimed", True))

    def test_rejects_artifact_digest_change(self) -> None:
        self.check_mutated_manifest(
            lambda value: value["artifacts"][0].__setitem__("sha256", "0" * 64)
        )

    def test_rejects_duplicate_artifact(self) -> None:
        self.check_mutated_manifest(
            lambda value: value["artifacts"][1].__setitem__(
                "role", value["artifacts"][0]["role"]
            )
        )

    def test_rejects_historical_hal_identity(self) -> None:
        original = gate.data

        def changed(path: str) -> bytes:
            payload = original(path)
            if path == "papers/paper44/Paper XLIV.md":
                return payload + b"\nhal-00000000v1\n"
            return payload

        with patch.object(gate, "data", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "historical HAL"):
                gate.check_citations()

    def test_rejects_unresolved_citation(self) -> None:
        original = gate.data

        def changed(path: str) -> bytes:
            if path == "papers/paper44/references-v1.bib":
                return b""
            return original(path)

        with patch.object(gate, "data", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "unresolved citations"):
                gate.check_citations()

    def test_rejects_wrong_doi_in_cited_entry(self) -> None:
        original = gate.data

        def changed(path: str) -> bytes:
            payload = original(path)
            if path == "papers/paper44/references-v1.bib":
                return payload.replace(b"doi = {10.5281/zenodo.24148747}",
                                       b"doi = {10.5281/zenodo.00000000}")
            return payload

        with patch.object(gate, "data", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "published input DOI mismatch"):
                gate.check_citations()

    def test_rejects_stale_review_digest(self) -> None:
        original = gate.data

        def changed(path: str) -> bytes:
            payload = original(path)
            if path == "experiments/paper44/review/CRITICAL_WINDOW_REVIEW.md":
                return payload.replace(gate.digest(original("papers/paper44/Paper XLIV.md")).encode(),
                                       b"0" * 64)
            return payload

        with patch.object(gate, "data", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "review binding drift"):
                gate.check_review()

    def test_rejects_lean_source_drift(self) -> None:
        with patch.object(gate, "source_inventory", return_value={"drift": "0" * 64}):
            with self.assertRaisesRegex(ValueError, "Lean source closure drift"):
                gate.check_lean_source()

    def test_rejects_path_escape(self) -> None:
        with self.assertRaisesRegex(ValueError, "noncanonical path"):
            gate.path_for("../paper43/Paper XLIII.md")


if __name__ == "__main__":
    unittest.main()
