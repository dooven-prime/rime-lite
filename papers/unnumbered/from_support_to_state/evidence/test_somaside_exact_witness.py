"""Focused arithmetic and hostile controls; no full MaleCNS census."""

import copy
from fractions import Fraction
import json
import unittest

import somaside_exact_witness as witness


class WitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(witness.DEFAULT_RESULT.read_text(encoding="utf-8"))

    def test_exact_result(self):
        result = witness.check(self.data)
        self.assertEqual(result["cross_product"], -36355)
        self.assertEqual(result["exact_difference"], [-661, 84521472])
        self.assertEqual(result["rows"][0]["row_abs_mass"], 3369)
        self.assertEqual(result["rows"][1]["row_abs_mass"], 704)

    def test_bigint_not_machine_integer(self):
        data = copy.deepcopy(self.data)
        scale = 10**30
        for row in data["rows"]:
            for edge in row["edges"]:
                edge[3] *= scale
        result = witness.derive(data["rows"], data["sector_sizes"])
        self.assertEqual(result["cross_product"], -36355 * scale**2)
        self.assertEqual(result["exact_difference"], [-661, 84521472])

    def test_model_and_identity_tampering(self):
        for field, value in (
            ("action", "Y"), ("beta", [1, 2]), ("gain", 2),
            ("clipping", [0, 2]), ("external_input", 1),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["model"][field] = value
                with self.assertRaises(ValueError):
                    witness.check(data)
        data = copy.deepcopy(self.data)
        data["carrier_sha256"]["carrier_v0_edges.npz"] = "0" * 64
        with self.assertRaises(ValueError):
            witness.check(data)

    def test_row_and_result_tampering(self):
        changes = [
            lambda d: d["rows"][0].update(body_id=123),
            lambda d: d["rows"][0].update(sector="R"),
            lambda d: d["rows"][0].update(sign=-1),
            lambda d: d["rows"][0]["edges"][0].__setitem__(3, 123456),
            lambda d: d["rows"][0]["edges"].append(d["rows"][0]["edges"][0]),
            lambda d: d["rows"][0].update(edges=[]),
            lambda d: d["derived"].update(cross_product=0),
            lambda d: d["sector_sizes"].update(M=393),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                data = copy.deepcopy(self.data)
                change(data)
                with self.assertRaises(ValueError):
                    witness.check(data)

    def test_zero_difference_rejected(self):
        data = copy.deepcopy(self.data)
        data["rows"][1]["edges"] = copy.deepcopy(data["rows"][0]["edges"])
        with self.assertRaises(ValueError):
            witness.derive(data["rows"], data["sector_sizes"])

    def test_negative_source_clips_to_zero(self):
        data = copy.deepcopy(self.data)
        data["rows"][1].update(consensus_nt="gaba", sign=-1)
        result = witness.derive(data["rows"], data["sector_sizes"])
        self.assertEqual(result["successors"][1]["M"], [0, 1])
        self.assertEqual(Fraction(*result["exact_difference"]),
                         Fraction(1, 5 * 392 * 3369))


if __name__ == "__main__":
    unittest.main()
