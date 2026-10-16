"""Adversarial controls against scope and consumer/representation confusions."""

from dataclasses import replace
import copy
import json
from itertools import permutations
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import forest
import log_consumer as log
import placed_ufe as ufe
from contract import Environment
from consumer_audit import run_word, worked_examples
from validate_consumer import check_record


class ConsumerControls(unittest.TestCase):
    def setUp(self):
        self.env = Environment((0, 3, 2, 5, 1, 4, 0), tuple(range(7)), tuple(range(7)))
        self.selected = frozenset({3, 5})

    def test_worked_examples(self):
        worked_examples()

    def test_reversed_two_point_seed_has_port_indexed_collision(self):
        env = Environment((0, 0), (0, 1), (0, 1))
        original = forest.initial(env)
        reversed_roots = replace(original, roots=tuple(reversed(original.roots)))
        forest.check_wellformed(env, reversed_roots)
        actual = forest.step(env, reversed_roots, "d")
        self.assertEqual(actual, forest.step(env, original, "d"))
        self.assertEqual(actual.roots[0][1].children,
                         ((0, forest.Tree(0)), (1, forest.Tree(1))))

    def test_root_storage_permutations_preserve_reads_and_successors(self):
        examples = ((Environment((0, 0, 1, 2), (0, 1, 2, 3), (0, 1, 2, 3)), "", frozenset({0, 1})),
                    (self.env, "dppd", self.selected),
                    (self.env, "dppdppd", self.selected))
        for env, word, selected in examples:
            _, original, _ = run_word(env, word)
            for reordered in permutations(original.roots):
                state = replace(original, roots=reordered)
                forest.check_wellformed(env, state)
                self.assertEqual(forest.project(state), forest.project(original))
                self.assertEqual(forest.decode(state, selected), forest.decode(original, selected))
                for letter in ("p", "d"):
                    actual = forest.step(env, state, letter)
                    forest.check_wellformed(env, actual)
                    self.assertEqual(actual, forest.step(env, original, letter))
                    for kind in ("Carry", "Absorb"):
                        self.assertEqual(forest.command(env, state, selected, kind, letter),
                                         forest.command(env, original, selected, kind, letter))

    def test_invalid_actions_and_seeds(self):
        for defect, seed, enumeration in (((0, 1), (0, 1), (0, 1)),
                                           ((0, 0, 0), (0, 1), (0, 1)),
                                           ((0, 0), (0, 0), (0, 1)),
                                           ((0, 0), (0, 1), (0, 0))):
            with self.assertRaises(ValueError):
                Environment(defect, seed, enumeration)

    def test_containment_is_not_registration(self):
        history, state, adapter = run_word(self.env, "dppdppdpppppd")
        unlogged = frozenset({0, 3})
        self.assertTrue(any(unlogged <= block for _, block in history.partition))
        for decoded in (log.decode(history, unlogged), forest.decode(state, unlogged),
                        ufe.decode(self.env, adapter, unlogged)):
            self.assertIsNone(decoded)
        for kind in ("Carry", "Absorb"):
            for letter in ("p", "d"):
                self.assertIsNone(forest.command(self.env, state, unlogged, kind, letter))
                self.assertIsNone(ufe.command(self.env, adapter, unlogged, kind, letter))

    def test_marker_is_not_the_selected_event(self):
        _, state, _ = run_word(self.env, "dppdppd")
        summary = forest.decode(state, self.selected)
        self.assertEqual(state.marker, frozenset({1, 4}))
        self.assertNotEqual(summary, forest.decode(state, state.marker))
        self.assertEqual(summary.selected, self.selected)
        self.assertEqual(summary.absorptions, ())

    def test_carry_updates_unrelated_packets(self):
        _, state, adapter = run_word(self.env, "dppdpp")
        before = forest.decode(state, self.selected)
        next_state = forest.command(self.env, state, self.selected, "Carry", "d")
        self.assertIsNotNone(next_state)
        after = forest.decode(next_state, self.selected)
        self.assertEqual(after.origin, before.origin)
        self.assertEqual(after.absorptions, before.absorptions)
        self.assertEqual(len(after.partition), len(before.partition) - 1)
        self.assertEqual(len(ufe.command(self.env, adapter, self.selected, "Carry", "d").unions),
                         len(adapter.unions) + 1)
        self.assertIsNone(forest.command(self.env, state, self.selected, "Absorb", "d"))

    def test_carrier_local_report_cannot_determine_guard(self):
        env = Environment((0, 0, 1, 2), (0, 1, 2, 3), (0, 1, 2, 3))
        first, _, _ = run_word(env, "dp")
        second, _, _ = run_word(env, "dppd")
        left, right = (log.decode(history, frozenset({0, 1})) for history in (first, second))
        self.assertEqual((left.origin, left.absorptions, left.carrier),
                         (right.origin, right.absorptions, right.carrier))
        self.assertNotEqual(left.partition, right.partition)
        self.assertIsNone(log.command(env, left, "Absorb", "d"))
        self.assertIsNotNone(log.command(env, right, "Absorb", "d"))

    def test_port_assignment_not_just_parent_mass(self):
        _, state, _ = run_word(self.env, "dppd")
        summary = forest.decode(state, self.selected)
        swapped = replace(summary.origin, parents=tuple((q, summary.origin.parents[1-i][1])
                                                        for i, (q, _) in enumerate(summary.origin.parents)))
        self.assertEqual(swapped.fresh, summary.origin.fresh)
        self.assertNotEqual(swapped, summary.origin)

    def test_ordered_union_inputs_matter(self):
        _, state, adapter = run_word(self.env, "dppd")
        altered = replace(adapter, unions=adapter.unions[:-1] + (tuple(reversed(adapter.unions[-1])),))
        self.assertEqual(ufe.project(altered), ufe.project(adapter))
        self.assertNotEqual(ufe.to_forest(self.env, altered), state)
        self.assertNotEqual(ufe.decode(self.env, altered, self.selected),
                            ufe.decode(self.env, adapter, self.selected))

    def test_complete_absorption_chain_not_only_current_carrier(self):
        env = Environment((0, 0, 1, 2, 3), tuple(range(5)), tuple(range(5)))
        _, state, _ = run_word(env, "dddd")
        summary = forest.decode(state, frozenset({0, 1}))
        self.assertEqual(len(summary.absorptions), 3)
        truncated = replace(summary, absorptions=summary.absorptions[1:])
        self.assertEqual(summary.carrier, truncated.carrier)
        self.assertNotEqual(summary, truncated)

    def test_marker_survives_plateau_and_becomes_internal(self):
        _, first, _ = run_word(self.env, "d")
        self.assertEqual(forest.step(self.env, first, "p").marker, first.marker)
        _, final, _ = run_word(self.env, "dppdppdpppppd")
        old = forest.decode(final, frozenset({0, 6}))
        self.assertIsNotNone(old)
        self.assertNotEqual(old.selected, old.carrier[1])

    def test_full_atom_handoff_not_partition_only(self):
        _, state, adapter = run_word(self.env, "dppdppdpppppd")
        eta = (0, 2, 1, 3, 4, 5, 6)
        env = Environment(self.env.defect, tuple(eta.index(i) for i in range(7)), eta)
        changed = forest.rename(state, eta)
        self.assertNotEqual(changed, state)
        self.assertEqual(changed, ufe.to_forest(env, ufe.rename(adapter, eta)))
        wrong_enum = replace(env, enumeration=tuple(range(7)))
        with self.assertRaises(ValueError):
            ufe.to_forest(wrong_enum, ufe.rename(adapter, eta))

    def test_long_plateau_not_unbounded_fusions(self):
        env = Environment((0, 0, 1, 2), (0, 1, 2, 3), (0, 1, 2, 3))
        short = run_word(env, "ddd")
        long = run_word(env, "ddd" + "p" * 4000)
        self.assertEqual(short, long)
        self.assertEqual(len(long[0].events), 3)

    def test_invalid_command_is_not_silently_carry(self):
        _, state, _ = run_word(self.env, "dppd")
        with self.assertRaises(ValueError):
            forest.command(self.env, state, self.selected, "Move", "p")


class RecordControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((PACKAGE / "results/consumer_audit_v1.json").read_text(encoding="utf-8"))

    def test_fixed_record(self):
        check_record(self.report)

    def test_coordinated_scope_shrink_fails(self):
        report = copy.deepcopy(self.report)
        report["cases"].pop()
        with self.assertRaises(ValueError):
            check_record(report)

    def test_changed_depth_fails(self):
        report = copy.deepcopy(self.report)
        report["cases"][0]["max_word_length"] = 4
        with self.assertRaises(ValueError):
            check_record(report)

    def test_changed_seed_fails(self):
        report = copy.deepcopy(self.report)
        report["cases"][0]["environment"]["seed"].reverse()
        with self.assertRaises(ValueError):
            check_record(report)

    def test_missing_worked_suffix_fails(self):
        report = copy.deepcopy(self.report)
        report["examples"]["seven_state"].pop()
        with self.assertRaises(ValueError):
            check_record(report)

    def test_optimization_environment_removed(self):
        from unittest.mock import patch
        from validate_package import child_environment
        with patch.dict("os.environ", {"PYTHONOPTIMIZE": "2"}):
            env = child_environment()
        self.assertNotIn("PYTHONOPTIMIZE", env)
        self.assertEqual(env["PYTHONDONTWRITEBYTECODE"], "1")

    def test_reader_rejects_main_branch_link(self):
        from validate_source import check_reader_surfaces
        paper = (ROOT / "papers/paper39/Paper XXXIX.md").read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            check_reader_surfaces(paper + "\n[broken](https://github.com/dooven-prime/rime-lite/blob/main/papers/paper39/README.md)\n")

    def test_reader_rejects_missing_formal_boundary(self):
        from validate_source import check_reader_surfaces
        paper = (ROOT / "papers/paper39/Paper XXXIX.md").read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            check_reader_surfaces(paper.replace("Neither the bounded replay nor the partial Lean spine is a machine proof",
                                                "These controls certify the complete theorems"))

    def test_formal_audit_rejects_missing_declaration(self):
        from validate_lean_formalization import DECLARATIONS, check_axioms
        output = "\n".join(f"'{name}' does not depend on any axioms" for name in DECLARATIONS[:-1])
        with self.assertRaises(ValueError):
            check_axioms(output)

    def test_formal_audit_rejects_unapproved_axiom(self):
        from validate_lean_formalization import DECLARATIONS, check_axioms
        output = "\n".join(f"'{name}' does not depend on any axioms" for name in DECLARATIONS[1:])
        output += f"\n'{DECLARATIONS[0]}' depends on axioms: [sorryAx]"
        with self.assertRaises(ValueError):
            check_axioms(output)

    def test_clean_selected_closure_and_tamper_rejection(self):
        from audit_scope import ARTIFACTS
        from validate_package import child_environment
        with tempfile.TemporaryDirectory(prefix="paper39-closure-") as directory:
            root = Path(directory)
            for relative in [*(path for _, path in ARTIFACTS),
                             "experiments/paper39/development-manifest.json"]:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            command = [sys.executable, "-B", str(root / "experiments/paper39/validation/validate_package.py"),
                       "--static"]
            env = child_environment()
            env.pop("PYTHONPATH", None)
            replay = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(replay.returncode, 0, replay.stdout + replay.stderr)
            target = root / "experiments/paper39/results/consumer_audit_v1.json"
            changed = target.read_bytes() + b" "
            target.write_bytes(changed)
            rejected = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("bound bytes drift", rejected.stderr)
            self.assertEqual(target.read_bytes(), changed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
