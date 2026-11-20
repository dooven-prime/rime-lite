import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

import replay
from build_reader import numbered_reader_layout


class ReplayTests(unittest.TestCase):
    def test_numbered_reader_layout_has_one_geometry_setting(self):
        original = r"\usepackage[a4paper,margin=1in]{geometry}"
        self.assertEqual(numbered_reader_layout(original, 22),
                         r"\usepackage[a4paper,margin=22mm]{geometry}")
        with self.assertRaisesRegex(ValueError, "geometry setting changed"):
            numbered_reader_layout("", 22)

    def test_exact_selected_menus(self):
        groups = replay.menus()
        self.assertEqual([len(g[3]) for g in groups], [25, 57, 34, 25])

    def test_default_build_covers_audit_only_imports(self):
        def imports(path):
            return [m for line in path.read_text(encoding="utf-8-sig").splitlines()
                    if line.startswith("import ")
                    for m in line.split("--", 1)[0].split()[1:]
                    if m.split(".")[0] in replay.LIBRARIES]
        pending, built = ["Paper47"], set()
        while pending:
            module = pending.pop()
            if module in built:
                continue
            built.add(module)
            pending.extend(imports(replay.LEAN / (module.replace(".", "/") + ".lean")))
        for _, audit, signatures, _ in replay.MENUS:
            for filename in (audit, signatures):
                self.assertTrue(set(imports(replay.LEAN / filename)) <= built, filename)

    def test_standard_axioms(self):
        rows = replay.parse_axioms("'x' depends on axioms: [propext, Classical.choice, Quot.sound]", ["x"])
        self.assertEqual(set(rows[0]["axioms"]), replay.ALLOWED)

    def test_axiom_free(self):
        self.assertEqual(replay.parse_axioms("'x' does not depend on any axioms", ["x"])[0]["axioms"], [])

    def test_sorry_and_custom_axioms_rejected(self):
        for axiom in ("sorryAx", "budgetPremise", "axiomFromRuntime"):
            with self.subTest(axiom=axiom), self.assertRaisesRegex(ValueError, "unapproved"):
                replay.parse_axioms(f"'x' depends on axioms: [{axiom}]", ["x"])

    def test_missing_duplicate_and_wrong_targets_rejected(self):
        for text in ("Unknown constant x", "'x' does not depend on any axioms\n" * 2,
                     "'y' does not depend on any axioms"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "exactly"):
                replay.parse_axioms(text, ["x"])

    def test_preserved_ancestor_and_local_imports(self):
        summary = replay.check_structure()
        self.assertEqual(summary["mirrored_lean_sources"], 195)
        self.assertEqual(summary["local_lean_sources"], 196)
        self.assertEqual(summary["preserved_ancestor_lean_sources"], 149)

    def test_no_external_local_lake_dependencies(self):
        lock = json.loads((replay.LEAN / "lake-manifest.json").read_text())
        self.assertTrue(all(p["type"] == "git" for p in lock["packages"]))
        self.assertNotIn("path =", (replay.LEAN / "lakefile.toml").read_text())

    def test_local_document_links(self):
        paths = [replay.PACKAGE / name for name in ("README.md", "THEOREM_MAP.md", "SCOPE.md")]
        paths += [replay.ROOT / "papers/paper47/README.md"]
        for path in paths:
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / unquote(link.split("#")[0])).exists(), (path, link))

    def test_caches_excluded_from_inventory(self):
        self.assertTrue(all(".lake" not in p.parts and "__pycache__" not in p.parts for p in replay.inputs()))


if __name__ == "__main__":
    unittest.main()
