"""Hostile controls for the Paper XLIII commit-sourced candidate gate."""

from __future__ import annotations

import copy
import json
import subprocess
import unittest
from unittest import mock

from tools.release import validate_numbered_migration_commit_candidate as gate


EVIDENCE = json.loads(
    (gate.ROOT / "experiments/paper43/evidence-map.v1.json").read_text(encoding="utf-8")
)


class CandidateGateTests(unittest.TestCase):
    def test_declared_owner_surface(self) -> None:
        self.assertEqual(
            EVIDENCE["historical_submission"]["source_commit"],
            "5dd17636ba65060b0a84773fccacbf1505fa6a39",
        )
        self.assertNotIn("source_tag", EVIDENCE["historical_submission"])
        self.assertEqual(
            EVIDENCE["inherited_companions"][1]["source_tag"],
            {
                "name": "future-event-lean-companion-v1.0",
                "tag_object_sha": "1ef64bc0560ae5c04e915350f86046670f698b8c",
                "target_commit_sha": "547848ce2305daf54f0e2df049a9d5372ffdcbdc",
            },
        )
        self.assertEqual(
            [row["path"] for row in EVIDENCE["historical_submission"]["source_files"]],
            [
                "papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md",
                "papers/unnumbered/future_event_minimal_quotient/references.bib",
                "papers/unnumbered/future_event_minimal_quotient/hal-v1/Chen_Future_Event_Minimal_Quotients_HAL_preprint.pdf",
                "experiments/future_event_minimal_quotient/control-manifest.v1.json",
            ],
        )
        self.assertEqual(
            [row["argv"] for row in EVIDENCE["replay_commands"]],
            [
                ["python", "-B", "experiments/future_event_minimal_quotient/validation/validate.py"],
                ["python", "-B", "validate_companion.py", "--source-only", "--check-upstream-git"],
                ["python", "-B", "review/build_theorem_map.py", "--check-git"],
            ],
        )

    def test_baseline(self) -> None:
        self.assertGreater(gate.check_evidence(43, EVIDENCE), 0)
        gate.base.check_citations(43)
        self.assertGreater(gate.base.check_manifest(43)[0], 0)

    def test_unreachable_source_commit_rejected(self) -> None:
        altered = copy.deepcopy(EVIDENCE)
        altered["historical_submission"]["source_commit"] = "0" * 40
        with self.assertRaises(subprocess.CalledProcessError):
            gate.check_evidence(43, altered)

    def test_historical_byte_change_rejected(self) -> None:
        altered = copy.deepcopy(EVIDENCE)
        altered["historical_submission"]["source_files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "historical drift"):
            gate.check_evidence(43, altered)

    def test_lean_tag_move_rejected(self) -> None:
        altered = copy.deepcopy(EVIDENCE)
        altered["inherited_companions"][1]["source_tag"]["tag_object_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "tag object drift"):
            gate.check_evidence(43, altered)

    def test_lean_archive_doi_change_rejected(self) -> None:
        altered = copy.deepcopy(EVIDENCE)
        altered["inherited_companions"][1]["archive_doi"] = "10.5281/zenodo.0"
        with self.assertRaisesRegex(ValueError, "companion archive DOI mismatch"):
            gate.check_evidence(43, altered)

    def test_missing_citation_rejected(self) -> None:
        original = gate.base.payload

        def without_bibliography(path: str) -> bytes:
            if path == "papers/paper43/references-v1.bib":
                return b""
            return original(path)

        with mock.patch.object(gate.base, "payload", side_effect=without_bibliography):
            with self.assertRaisesRegex(ValueError, "unresolved citation"):
                gate.base.check_citations(43)

    def test_manuscript_byte_change_rejected(self) -> None:
        original = gate.base.payload

        def changed_manuscript(path: str) -> bytes:
            content = original(path)
            return content + b"\n" if path == "papers/paper43/Paper XLIII.md" else content

        with mock.patch.object(gate.base, "payload", side_effect=changed_manuscript):
            with self.assertRaisesRegex(ValueError, "manifest or artifact bytes drift"):
                gate.base.check_manifest(43)


if __name__ == "__main__":
    unittest.main()
