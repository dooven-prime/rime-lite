#!/usr/bin/env python3
"""Symbolic and exact controls for the depth-three zero-route classification."""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

from core import content_digest, file_digest, modular_generators, permutation_orbits
from uniform_finite_field_route_profile import route_profile_at_depth


PACKAGE_PATH = "experiments/exploratory/carrier_realizations/fuchsian_schreier"
SCHEMA = "rime.exploratory.fuchsian-schreier.depth-three-zero-route-classification.v1"
LABELS = ("S", "R", "R_inv")
SHAPES = ("0101", "0110", "0111", "1010", "1011", "1101", "1110", "1111")

EXPECTED_HISTOGRAMS = {
    "F2": {
        "0101": 12,
        "0110": 22,
        "0111": 20,
        "1010": 12,
        "1011": 15,
        "1101": 15,
        "1110": 20,
        "1111": 19,
    },
    "F3": {
        "0101": 12,
        "0110": 23,
        "0111": 19,
        "1010": 12,
        "1011": 15,
        "1101": 15,
        "1110": 19,
        "1111": 1,
    },
    "CHARACTERISTIC_TWO_CARDINALITY_AT_LEAST_FOUR": {
        "0101": 12,
        "0110": 22,
        "0111": 20,
        "1010": 12,
        "1011": 15,
        "1101": 15,
        "1110": 20,
        "1111": 0,
    },
    "ODD_CARDINALITY_AT_LEAST_FIVE": {
        "0101": 12,
        "0110": 23,
        "0111": 19,
        "1010": 12,
        "1011": 15,
        "1101": 15,
        "1110": 19,
        "1111": 0,
    },
}


@dataclass(frozen=True)
class PolynomialField:
    """Small exact polynomial field used only for extension-field controls."""

    characteristic: int
    modulus: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.modulus) < 2 or self.modulus[-1] != 1:
            raise ValueError("modulus must be monic and have positive degree")

    @property
    def degree(self) -> int:
        return len(self.modulus) - 1

    @property
    def cardinality(self) -> int:
        return self.characteristic**self.degree

    @property
    def elements(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            itertools.product(range(self.characteristic), repeat=self.degree)
        )

    @property
    def zero(self) -> tuple[int, ...]:
        return (0,) * self.degree

    @property
    def one(self) -> tuple[int, ...]:
        return (1,) + (0,) * (self.degree - 1)

    def add(self, left, right):
        return tuple(
            (a + b) % self.characteristic for a, b in zip(left, right)
        )

    def neg(self, value):
        return tuple((-entry) % self.characteristic for entry in value)

    def mul(self, left, right):
        degree = self.degree
        values = [0] * (2 * degree - 1)
        for i, a in enumerate(left):
            for j, b in enumerate(right):
                values[i + j] = (values[i + j] + a * b) % self.characteristic
        for exponent in range(2 * degree - 2, degree - 1, -1):
            coefficient = values[exponent] % self.characteristic
            if not coefficient:
                continue
            for index in range(degree):
                values[exponent - degree + index] = (
                    values[exponent - degree + index]
                    - coefficient * self.modulus[index]
                ) % self.characteristic
        return tuple(values[:degree])

    def power(self, value, exponent: int):
        result = self.one
        factor = value
        while exponent:
            if exponent & 1:
                result = self.mul(result, factor)
            factor = self.mul(factor, factor)
            exponent //= 2
        return result

    def inverse(self, value):
        if value == self.zero:
            raise ZeroDivisionError("zero has no multiplicative inverse")
        inverse = self.power(value, self.cardinality - 2)
        if self.mul(value, inverse) != self.one:
            raise ArithmeticError("declared polynomial quotient is not a field")
        return inverse


def extension_field_histogram(field: PolynomialField) -> dict[str, int]:
    infinity = None
    zero = field.zero
    one = field.one
    minus_one = field.neg(one)

    def s(value):
        if value is infinity:
            return zero
        if value == zero:
            return infinity
        return field.neg(field.inverse(value))

    def r(value):
        if value is infinity:
            return zero
        shifted = field.add(value, one)
        if shifted == zero:
            return infinity
        return field.neg(field.inverse(shifted))

    def r_inv(value):
        if value is infinity:
            return minus_one
        if value == zero:
            return infinity
        return field.add(minus_one, field.neg(field.inverse(value)))

    generators = (s, r, r_inv)
    sectors = ({infinity}, set(field.elements))
    direct = [
        [
            [any(function(value) in sectors[target] for value in sectors[source])
             for source in range(2)]
            for target in range(2)
        ]
        for function in generators
    ]
    histogram = {shape: 0 for shape in SHAPES}
    for word in itertools.product(range(3), repeat=3):
        for path in itertools.product(range(2), repeat=4):
            if not all(
                direct[word[step]][path[step + 1]][path[step]]
                for step in range(3)
            ):
                continue
            states = set(sectors[path[0]])
            for step, generator in enumerate(word):
                target = sectors[path[step + 1]]
                states = {
                    generators[generator](value)
                    for value in states
                    if generators[generator](value) in target
                }
            if not states:
                histogram["".join(str(index) for index in path)] += 1
    return histogram


def prime_field_histogram(prime: int) -> dict[str, int]:
    generators = modular_generators(prime)
    named = tuple((label, generators[label]) for label in LABELS)
    sectors = permutation_orbits(generators["T"])
    profile = route_profile_at_depth(named, sectors, 3)
    return {
        shape: profile["zero_shape_counts"].get(shape, 0) for shape in SHAPES
    }


def verify_odd_prime_closed_form(prime: int) -> dict:
    """Replay the seven finite-table criteria against exact routed products."""

    if prime % 2 == 0 or prime < 3:
        raise ValueError("closed-form replay requires an odd prime")
    generators = modular_generators(prime)
    named = tuple((label, generators[label]) for label in LABELS)
    sectors = permutation_orbits(generators["T"])
    profile = route_profile_at_depth(named, sectors, 3)
    word_profiles = {
        tuple(row["word"]): row for row in profile["word_profiles"]
    }
    infinity = prime
    values_at_infinity = {
        name: permutation[infinity] for name, permutation in named
    }
    poles = {
        name: next(state for state in range(prime) if permutation[state] == infinity)
        for name, permutation in named
    }
    maps = {name: permutation for name, permutation in named}
    checked = 0
    for a, b, c in itertools.product(LABELS, repeat=3):
        v_a = values_at_infinity[a]
        v_b = values_at_infinity[b]
        e_ab = maps[b][v_a]
        predicted = {
            "0101": v_a == poles[b],
            "0110": v_a != poles[b] and e_ab == poles[c],
            "0111": v_a != poles[b] and e_ab != poles[c],
            "1010": v_b == poles[c],
            "1011": v_b != poles[c],
            "1101": v_a != poles[b],
            "1110": v_b != poles[c] and e_ab != poles[c],
            "1111": any(
                maps[a][state] != infinity
                and maps[b][maps[a][state]] != infinity
                and maps[c][maps[b][maps[a][state]]] != infinity
                for state in range(prime)
            ),
        }
        observed_zeros = word_profiles[(a, b, c)]["zero_shape_counts"]
        for shape, expected_nonzero in predicted.items():
            observed_nonzero = shape not in observed_zeros
            if observed_nonzero != expected_nonzero:
                raise AssertionError(
                    f"closed-form mismatch at p={prime}, word={(a, b, c)}, "
                    f"shape={shape}"
                )
            checked += 1
    return {"prime": prime, "checked_word_shape_pairs": checked, "status": "PASS"}


def build_payload() -> dict:
    controls = {
        "F2": prime_field_histogram(2),
        "F3": prime_field_histogram(3),
        "F5": prime_field_histogram(5),
        "F7": prime_field_histogram(7),
        "F4": extension_field_histogram(PolynomialField(2, (1, 1, 1))),
        "F8": extension_field_histogram(PolynomialField(2, (1, 1, 0, 1))),
        "F9": extension_field_histogram(PolynomialField(3, (1, 0, 1))),
    }
    expected_by_control = {
        "F2": "F2",
        "F3": "F3",
        "F4": "CHARACTERISTIC_TWO_CARDINALITY_AT_LEAST_FOUR",
        "F8": "CHARACTERISTIC_TWO_CARDINALITY_AT_LEAST_FOUR",
        "F5": "ODD_CARDINALITY_AT_LEAST_FIVE",
        "F7": "ODD_CARDINALITY_AT_LEAST_FIVE",
        "F9": "ODD_CARDINALITY_AT_LEAST_FIVE",
    }
    checks = {
        name: histogram == EXPECTED_HISTOGRAMS[expected_by_control[name]]
        for name, histogram in controls.items()
    }
    if not all(checks.values()):
        raise AssertionError("depth-three closed-form control failed")
    odd_prime_criterion_checks = [
        verify_odd_prime_closed_form(prime) for prime in (3, 5, 7)
    ]

    here = Path(__file__).resolve()
    files = {
        f"{PACKAGE_PATH}/core.py": file_digest(here.with_name("core.py")),
        f"{PACKAGE_PATH}/uniform_finite_field_route_profile.py": file_digest(
            here.with_name("uniform_finite_field_route_profile.py")
        ),
        f"{PACKAGE_PATH}/depth_three_zero_route_classification.py": file_digest(here),
    }
    totals = {
        regime: sum(histogram.values())
        for regime, histogram in EXPECTED_HISTOGRAMS.items()
    }
    return {
        "schema": SCHEMA,
        "bundle_id": "fuchsian-schreier.depth-three-zero-route-classification.v1",
        "artifact_role": "EXPLORATORY_SYMBOLIC_CLASSIFICATION_CERTIFICATE",
        "claim_status": "Symbolic Classification plus Computational Certificate",
        "paper_evidence_status": "NOT_PROMOTED",
        "contract": "(P^1(F), (S,R,R_inv), {infinity} disjoint union F, source-to-target depth-three route semantics)",
        "candidate_count": {
            "ordered_word_count": 27,
            "candidate_sector_shapes": list(SHAPES),
            "candidate_count": 216,
            "closed_form": "3^3 * F_6 = 27 * 8 = 216",
        },
        "closed_form_nonzero_criteria": {
            "notation": {
                "v_a": "a(infinity)",
                "pi_a": "a^(-1)(infinity), the pole of a",
                "e_ab": "b(v_a)",
            },
            "0101": "v_a = pi_b",
            "0110": "v_a != pi_b and e_ab = pi_c",
            "0111": "v_a != pi_b and e_ab != pi_c",
            "1010": "v_b = pi_c",
            "1011": "v_b != pi_c",
            "1101": "v_a != pi_b",
            "1110": "v_b != pi_c and e_ab != pi_c",
            "1111": "there exists finite x with x != pi_a, a(x) != pi_b, and b(a(x)) != pi_c",
        },
        "classification": {
            regime: {
                "zero_shape_histogram": histogram,
                "zero_route_count": totals[regime],
            }
            for regime, histogram in EXPECTED_HISTOGRAMS.items()
        },
        "zero_route_count_closed_form": {
            "formula": "|Z_3(F)| = 115 + 1_{char(F)=2} + 19*1_{|F|=2} + 1_{|F|=3}",
            "candidate_denominator": 216,
            "warning": "the scalar total does not determine the shape histogram",
        },
        "all_bulk_exception": {
            "F3_unique_zero_word": ["R_inv", "S", "R"],
            "sector_path": [1, 1, 1, 1],
            "reason": "the three forbidden finite preimages exhaust F3",
            "cardinality_at_least_four": "at most three finite inputs are forbidden, so at least one witness remains",
            "F2_nonzero_words": [
                ["S", "S", "S"],
                ["S", "S", "R_inv"],
                ["S", "R_inv", "R"],
                ["R", "S", "S"],
                ["R", "S", "R_inv"],
                ["R", "R_inv", "R"],
                ["R_inv", "R", "S"],
                ["R_inv", "R", "R_inv"],
            ],
        },
        "exact_controls": controls,
        "all_exact_controls_pass": all(checks.values()),
        "odd_prime_closed_form_replays": odd_prime_criterion_checks,
        "implementation": {
            "arithmetic": "exact prime and polynomial finite-field arithmetic; no floating point",
            "files": files,
            "implementation_sha256": content_digest(files),
        },
        "boundary": [
            "The classification is relative to the complete marked route contract.",
            "The result is not an abstract group-presentation invariant.",
            "No RG, Hecke, modular-form, or spectral zero-mode claim is made.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload()
    payload["content_sha256"] = content_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "bundle_id": payload["bundle_id"],
                "content_sha256": payload["content_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
