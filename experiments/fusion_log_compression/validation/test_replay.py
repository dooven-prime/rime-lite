"""Regression checks for the replay gate, not tests of the Lean theorem."""

import hashlib
from pathlib import Path
import tempfile
import unittest

import replay


class ReplayGateTests(unittest.TestCase):
    def test_current_inputs(self):
        manifest = replay.verify_inputs()
        self.assertEqual(len(manifest["axiom_targets"]), 18)

    def test_file_drift_and_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "input.lean"
            path.write_bytes(b"original\n")
            expected = {"input.lean": hashlib.sha256(path.read_bytes()).hexdigest()}
            replay.checked_files(root, expected, {"input.lean"})
            with self.assertRaisesRegex(RuntimeError, "inventory mismatch"):
                replay.checked_files(root, expected, {"input.lean", "extra.lean"})
            path.write_bytes(b"changed\n")
            with self.assertRaisesRegex(RuntimeError, "byte drift"):
                replay.checked_files(root, expected, {"input.lean"})
            with self.assertRaisesRegex(RuntimeError, "escapes its root"):
                replay.checked_files(root, {"../outside.lean": "unused"}, {"../outside.lean"})

    def test_standard_and_empty_axioms(self):
        output = ("'T.a' depends on axioms: [propext, Classical.choice, Quot.sound]\n"
                  "'T.b' does not depend on any axioms\n")
        self.assertEqual(replay.parse_axiom_audit(output, ["T.a", "T.b"])["T.b"], [])

    def test_missing_duplicate_and_unsafe_axioms(self):
        row = "'T.a' depends on axioms: [propext]\n"
        for output, targets in [(row, ["T.a", "T.b"]), (row + row, ["T.a"]),
                                ("'T.a' depends on axioms: [sorryAx]", ["T.a"]),
                                ("'T.a' depends on axioms: [Custom.assumption]", ["T.a"])]:
            with self.subTest(output=output), self.assertRaises(RuntimeError):
                replay.parse_axiom_audit(output, targets)


if __name__ == "__main__":
    unittest.main()
