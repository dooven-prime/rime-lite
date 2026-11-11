"""Hostile controls for the Paper XLII candidate gate."""

from __future__ import annotations

import copy
import json
import unittest
from unittest import mock

from tools.release import validate_numbered_migration_candidate as gate


EVIDENCE = json.loads(
    (gate.ROOT / "experiments/paper42/evidence-map.v1.json").read_text(encoding="utf-8")
)


class CandidateGateTests(unittest.TestCase):
    def test_declared_owner_surface(self) -> None:
        self.assertEqual(
            EVIDENCE["historical_submission"]["source_tag"],
            {
                "name": "proper-arc-summaries-source-v1.0",
                "tag_object_sha": "a8d98e500b82dfeb88056f7d6167a82b10c270bb",
                "target_commit_sha": "2a30449b9dc37a36b25b277ebc006515c2addb59",
            },
        )
        self.assertEqual(
            EVIDENCE["inherited_companions"][1]["source_tag"],
            {
                "name": "proper-arc-lean-companion-v1.0",
                "tag_object_sha": "f20a4f1f32c3ebe1eba1c162e50a500c6d9ed327",
                "target_commit_sha": "b1aa5eb76cd29f1ff26dec14b350b5affeeb45f8",
            },
        )
        self.assertEqual(
            [row["path"] for row in EVIDENCE["historical_submission"]["source_files"]],
            [
                "papers/unnumbered/proper_arc_registered_summaries/MANUSCRIPT.md",
                "papers/unnumbered/proper_arc_registered_summaries/references.bib",
                "papers/unnumbered/proper_arc_registered_summaries/hal-v1/Chen_Registered_Proper_Arc_Summaries_HAL_preprint.pdf",
                "experiments/proper_arc_registered_summaries/control-manifest.v1.json",
            ],
        )
        self.assertEqual(
            [row["argv"] for row in EVIDENCE["replay_commands"]],
            [
                ["python", "-B", "experiments/proper_arc_registered_summaries/validate_controls.py"],
                ["python", "-B", "validate_companion.py", "--source-only", "--check-upstream-git"],
            ],
        )

    def test_baseline(self) -> None:
        self.assertGreater(gate.check_evidence(42, EVIDENCE), 0)
        gate.check_citations(42)
        self.assertGreater(gate.check_manifest(42)[0], 0)

    def test_tag_move_rejected(self) -> None:
        altered = copy.deepcopy(EVIDENCE)
        altered["historical_submission"]["source_tag"]["tag_object_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "tag object drift"):
            gate.check_evidence(42, altered)

    def test_historical_byte_change_rejected(self) -> None:
        altered = copy.deepcopy(EVIDENCE)
        altered["historical_submission"]["source_files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "historical drift"):
            gate.check_evidence(42, altered)

    def test_missing_citation_rejected(self) -> None:
        original = gate.payload

        def without_bibliography(path: str) -> bytes:
            if path == "papers/paper42/references-v1.bib":
                return b""
            return original(path)

        with mock.patch.object(gate, "payload", side_effect=without_bibliography):
            with self.assertRaisesRegex(ValueError, "unresolved citation"):
                gate.check_citations(42)

    def test_manuscript_byte_change_rejected(self) -> None:
        original = gate.payload

        def changed_manuscript(path: str) -> bytes:
            content = original(path)
            return content + b"\n" if path == "papers/paper42/Paper XLII.md" else content

        with mock.patch.object(gate, "payload", side_effect=changed_manuscript):
            with self.assertRaisesRegex(ValueError, "manifest or artifact bytes drift"):
                gate.check_manifest(42)


if __name__ == "__main__":
    unittest.main()
