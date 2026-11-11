import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve().parent
gate = load("c1_rgt_gate_tests", HERE / "replay.py")
runtime = load("c1_rgt_runtime_tests", gate.ROOT / "formal-cases/rgt-bounded-history/v1/replay.py")


class CompanionGates(unittest.TestCase):
    def test_current_inputs_and_audit_counts(self):
        manifest = gate.verify_inputs()
        self.assertEqual({k: len(v) for k, v in manifest["axiom_targets"].items()},
                         {"paper40": 68, "rgt": 25, "c1": 29})

    def test_source_byte_drift_is_rejected(self):
        original = gate.sha
        target = gate.LEAN / "PaperXL/C1QuadraticRGT.lean"
        with patch.object(gate, "sha", side_effect=lambda p: "0" * 64 if p == target else original(p)):
            with self.assertRaisesRegex(ValueError, "source byte drift"):
                gate.verify_inputs()

    def test_extra_or_missing_source_is_rejected(self):
        with patch.object(gate, "inventory", return_value=gate.inventory() | {"extra.lean"}):
            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                gate.verify_inputs()

    def test_wrong_tag_object_is_rejected(self):
        original = gate.git
        def changed(*args):
            if args == ("rev-parse", "refs/tags/paper40-v1.0"):
                return b"0000000000000000000000000000000000000000\n"
            return original(*args)
        with patch.object(gate, "git", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "source tag drift"):
                gate.verify_inputs()

    def test_duplicate_audit_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Audit.lean"
            path.write_text("#print axioms A\n#print axioms A\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                gate.targets(path)

    def test_unknown_or_duplicate_audit_output_is_rejected(self):
        for raw in ("'A' depends on axioms: [sorryAx]", "'A' does not depend on any axioms\n" * 2):
            with self.assertRaises(ValueError):
                gate.audit(raw, ["A"])

    def test_missing_audit_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "inventory"):
            gate.audit("'A' depends on axioms: [propext]", ["A", "B"])

    def test_bool_and_nat_cannot_compare_equal(self):
        with self.assertRaisesRegex(ValueError, "mismatch"):
            runtime.compare_vectors([{"q": True}], [{"q": 1}])

    def test_missing_lean_response_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "count mismatch"):
            runtime.compare_vectors([], [{}])

    def test_corrupt_frozen_runtime_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.zip"
            path.write_bytes(b"not the released archive")
            with patch.object(runtime, "ARCHIVE", path):
                with self.assertRaisesRegex(ValueError, "ZIP drift"):
                    with runtime.frozen_runtime():
                        pass

    def test_frozen_runtime_extracts_exact_implementation(self):
        with runtime.frozen_runtime() as modules:
            self.assertEqual(modules["model"].parse_environment({"defect": [0, 0, 2], "seed": [0, 1, 2]}).n, 3)

    def test_manifest_excludes_receipts_and_itself(self):
        inventory = gate.inventory()
        self.assertNotIn(gate.MANIFEST.relative_to(gate.ROOT).as_posix(), inventory)
        self.assertTrue(all("/results/" not in name and "/.lake/" not in name for name in inventory))


if __name__ == "__main__":
    unittest.main()
