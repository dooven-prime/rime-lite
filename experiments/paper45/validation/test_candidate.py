"""Hostile checks for the Paper XLV candidate inventory."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_candidate as candidate


class CandidateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(candidate.MANIFEST.read_bytes())
        cls.manuscript = candidate.data("papers/paper45/Paper XLV.md").decode("utf-8")
        cls.bibliography = candidate.data("papers/paper45/references-v1.bib").decode("utf-8")

    def test_retained_candidate_passes(self) -> None:
        candidate.check_inputs()
        self.assertGreater(candidate.check_manifest(self.manifest), 30)

    def test_unresolved_citation_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unresolved citations"):
            candidate.check_citations(self.manuscript + " [@missingKey]", self.bibliography)

    def test_numbered_identity_rejected(self) -> None:
        bad = self.manuscript.replace("Paper XLV (version 1.0)",
                                      "Paper XLV (version 2.0)")
        with self.assertRaisesRegex(ValueError, "numbered identity missing"):
            candidate.check_citations(bad, self.bibliography)

    def test_statement_title_style_rejected(self) -> None:
        bad = self.manuscript.replace("**Theorem 4.1 (log and endpoint realization).**",
                                      "### Theorem 4.1. Log and Endpoint Realization")
        with self.assertRaisesRegex(ValueError, "descriptive statement titles missing"):
            candidate.check_citations(bad, self.bibliography)

    def test_unreleased_hal_reference_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unreleased HAL"):
            candidate.check_citations(self.manuscript, self.bibliography + "\nhal-05852797v1")

    def test_published_input_doi_rejected(self) -> None:
        bad = self.bibliography.replace("10.5281/zenodo.24138941", "10.5281/zenodo.0")
        with self.assertRaisesRegex(ValueError, "DOI drift"):
            candidate.check_citations(self.manuscript, bad)

    def test_manifest_digest_rejected(self) -> None:
        bad = copy.deepcopy(self.manifest)
        bad["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact digest drift"):
            candidate.check_manifest(bad)

    def test_extra_lean_source_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            all_r = root / "experiments/fusion_log_compression/lean_all_r"
            for _, relative in candidate.artifact_paths():
                if not relative.startswith("experiments/fusion_log_compression/lean_all_r/") or not relative.endswith(".lean"):
                    continue
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            (all_r / "Unexpected.lean").write_text("def unexpected := True\n", encoding="utf-8")
            with patch.object(candidate, "ROOT", root), patch.object(candidate, "ALL_R", all_r):
                with self.assertRaisesRegex(ValueError, "inventory drift"):
                    candidate.check_manifest(self.manifest)


if __name__ == "__main__":
    unittest.main()
