"""Regression checks for source lint; kernel checking remains separate."""

from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_companion import lean_code


FORBIDDEN = re.compile(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s", re.MULTILINE)


class SourceLintTests(unittest.TestCase):
    def test_nested_comments_are_not_proofs(self):
        source = "/- admit /- sorry -/ axiom -/\ntheorem ok : True := by trivial"
        self.assertIsNone(FORBIDDEN.search(lean_code(source)))
        self.assertEqual(lean_code(source).count("\n"), source.count("\n"))

    def test_line_comments_and_strings(self):
        source = '-- sorry\ndef label := "admit \\"sorry\\""\n'
        self.assertIsNone(FORBIDDEN.search(lean_code(source)))

    def test_actual_placeholders_remain_visible(self):
        for word in ("sorry", "admit"):
            with self.subTest(word=word):
                self.assertIsNotNone(FORBIDDEN.search(lean_code(f"theorem bad : True := by {word}")))

    def test_custom_axiom_remains_visible(self):
        self.assertIsNotNone(FORBIDDEN.search(lean_code("/- heading -/\naxiom bad : False")))

    def test_member_name_is_not_a_placeholder(self):
        self.assertIsNone(FORBIDDEN.search(lean_code("exact first.admit order")))


if __name__ == "__main__":
    unittest.main()
