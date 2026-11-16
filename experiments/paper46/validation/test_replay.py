import unittest

from replay import check_axioms


class AxiomOutputTests(unittest.TestCase):
    def test_allowed_axioms(self):
        result = check_axioms("'RSR2.Parametric.target' depends on axioms: "
                              "[propext, Classical.choice, Quot.sound]\n", ["Parametric.target"])
        self.assertEqual(result["target_count"], 1)

    def test_empty_axiom_set(self):
        self.assertEqual(check_axioms("'RSR2.target' does not depend on any axioms\n",
                                      ["target"])["axioms"], [])

    def test_missing_output_rejected(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            check_axioms("", ["target"])

    def test_unknown_axiom_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unexpected axioms"):
            check_axioms("'RSR2.target' depends on axioms: [sorryAx]\n", ["target"])

    def test_wrong_name_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unexpected or duplicate"):
            check_axioms("'RSR2.other' depends on axioms: []\n", ["target"])

    def test_duplicate_output_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unexpected or duplicate"):
            check_axioms("'RSR2.a' depends on axioms: []\n" * 2, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
