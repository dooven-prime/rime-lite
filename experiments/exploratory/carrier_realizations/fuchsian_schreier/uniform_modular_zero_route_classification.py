#!/usr/bin/env python3
"""Uniform modular zero-route classification and exact replay.

The proof object is the pole/value classification in
UNIFORM_MODULAR_ZERO_ROUTE_CLASSIFICATION.md. This script independently replays the listed
finite-field conditions for a declared odd-prime sample and checks that the
resulting zero signature agrees with the core route evaluator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import content_digest, file_digest, route_length_two_profile


INF = None
PACKAGE_PATH = "experiments/exploratory/carrier_realizations/fuchsian_schreier"
SCHEMA = "rime.exploratory.fuchsian-schreier.uniform-modular-zero-route-classification.v1"


def S(x, p):
    if x is INF:
        return 0
    if x == 0:
        return INF
    return (-pow(x, -1, p)) % p


def R(x, p):
    if x is INF:
        return 0
    if x == p - 1:
        return INF
    return (-pow(x + 1, -1, p)) % p


def R_inv(x, p):
    if x is INF:
        return p - 1
    if x == 0:
        return INF
    return (-1 - pow(x, -1, p)) % p


GENERATOR_FUNCTIONS = {"S": S, "R": R, "R_inv": R_inv}


def permutation(function, p):
    values = [function(x, p) for x in range(p)]
    values.append(function(INF, p))
    return tuple(p if value is INF else value for value in values)


def symbolic_zero_route_table() -> list[dict]:
    """Return the fourteen zero routes grouped by finite-field obstruction."""

    rows = []
    rows.extend(
        [
            {
                "word": ["S", "R"],
                "route": [0, 1, 0],
                "condition": "R(S(infinity)) = R(0) = -1 in F_p; target infinity is missed",
            },
            {
                "word": ["R", "R"],
                "route": [0, 1, 0],
                "condition": "R(R(infinity)) = R(0) = -1 in F_p; target infinity is missed",
            },
            {
                "word": ["R_inv", "S"],
                "route": [0, 1, 0],
                "condition": "S(R_inv(infinity)) = S(-1) = 1 in F_p; target infinity is missed",
            },
            {
                "word": ["R_inv", "R_inv"],
                "route": [0, 1, 0],
                "condition": "R_inv(R_inv(infinity)) = R_inv(-1) = 0 in F_p; target infinity is missed",
            },
            {
                "word": ["S", "S"],
                "route": [1, 1, 0],
                "condition": "S(S(infinity)) = S(0) = infinity; finite target is missed",
            },
            {
                "word": ["S", "R_inv"],
                "route": [1, 1, 0],
                "condition": "R_inv(S(infinity)) = R_inv(0) = infinity; finite target is missed",
            },
            {
                "word": ["R", "S"],
                "route": [1, 1, 0],
                "condition": "S(R(infinity)) = S(0) = infinity; finite target is missed",
            },
            {
                "word": ["R", "R_inv"],
                "route": [1, 1, 0],
                "condition": "R_inv(R(infinity)) = R_inv(0) = infinity; finite target is missed",
            },
            {
                "word": ["R_inv", "R"],
                "route": [1, 1, 0],
                "condition": "R(R_inv(infinity)) = R(-1) = infinity; finite target is missed",
            },
            {
                "word": ["S", "S"],
                "route": [0, 1, 1],
                "condition": "S(x) = pole(S) = 0 has no x in F_p minus {0}",
            },
            {
                "word": ["S", "R_inv"],
                "route": [0, 1, 1],
                "condition": "S(x) = pole(R_inv) = 0 has no x in F_p minus {0}",
            },
            {
                "word": ["R", "S"],
                "route": [0, 1, 1],
                "condition": "R(x) = pole(S) = 0 has no x in F_p minus {-1}",
            },
            {
                "word": ["R", "R_inv"],
                "route": [0, 1, 1],
                "condition": "R(x) = pole(R_inv) = 0 has no x in F_p minus {-1}",
            },
            {
                "word": ["R_inv", "R"],
                "route": [0, 1, 1],
                "condition": "R_inv(x) = pole(R) = -1 reduces to 1/x = 0; no finite solution",
            },
        ]
    )
    return rows


def exact_signature(p: int) -> list[dict]:
    named = tuple(
        (name, permutation(GENERATOR_FUNCTIONS[name], p))
        for name in GENERATOR_FUNCTIONS
    )
    sectors = ((p,), tuple(range(p)))
    profile = route_length_two_profile(named, sectors)
    rows = []
    for pair in profile["ordered_letter_pair_profiles"]:
        for route in pair["zero_routes_target_middle_source"]:
            rows.append(
                {
                    "word": pair["word_left_to_right"],
                    "route": route,
                }
            )
    return sorted(rows, key=lambda row: (row["word"], row["route"]))


def build_payload(primes: list[int]) -> dict:
    symbolic = symbolic_zero_route_table()
    expected = sorted(
        [{"word": row["word"], "route": row["route"]} for row in symbolic],
        key=lambda row: (row["word"], row["route"]),
    )
    checks = []
    for p in primes:
        actual = exact_signature(p)
        checks.append(
            {
                "prime": p,
                "zero_count": len(actual),
                "signature_matches_symbolic_table": actual == expected,
            }
        )
    here = Path(__file__).resolve()
    files = {
        f"{PACKAGE_PATH}/core.py": file_digest(here.with_name("core.py")),
        f"{PACKAGE_PATH}/uniform_modular_zero_route_classification.py": file_digest(here),
    }
    return {
        "schema": SCHEMA,
        "bundle_id": "fuchsian-schreier.uniform-modular-zero-route-classification.v1",
        "artifact_role": "EXPLORATORY_SYMBOLIC_FINITE_FIELD_CERTIFICATE",
        "claim_status": "Computational Certificate plus symbolic proof record",
        "paper_evidence_status": "NOT_PROMOTED",
        "scope": {
            "typed_contract": "(P^1(F_p), {S,R,R_inv}, {C0,C1}, label order (S,R,R_inv), two-step route semantics)",
            "domain": "all odd primes, with exact replay sample",
            "carrier": "P^1(F_p)",
            "partition": "{infinity} disjoint union F_p, induced by T-orbits",
            "alphabet": ["S", "R", "R_inv"],
            "metric": "length-two zero routed products among Boolean-supported routes",
        },
        "shape_exhaustion": {
            "ordered_letter_pair_count": 9,
            "candidate_shapes": [
                [1, 0, 1],
                [0, 1, 0],
                [1, 1, 0],
                [0, 1, 1],
                [1, 1, 1],
            ],
            "candidate_count_factorization": "9 * 5 = 45",
            "nonzero_shapes": [[1, 0, 1], [1, 1, 1]],
            "potentially_zero_shapes": [[0, 1, 0], [1, 1, 0], [0, 1, 1]],
            "zero_shape_contributions": {
                "(0,1,0)": 4,
                "(1,1,0)": 5,
                "(0,1,1)": 5,
            },
            "zero_count_decomposition": "4 + 5 + 5 = 14",
        },
        "modular_formulas": {
            "S": {
                "infinity": "0",
                "finite": "S(x)=-x^{-1} for x != 0; S(0)=infinity",
            },
            "R": {
                "infinity": "0",
                "finite": "R(x)=-(x+1)^{-1} for x != -1; R(-1)=infinity",
            },
            "R_inv": {
                "infinity": "-1",
                "finite": "R_inv(x)=-1-x^{-1} for x != 0; R_inv(0)=infinity",
            },
            "poles": {"S": "0", "R": "-1", "R_inv": "0"},
        },
        "symbolic_zero_route_table": symbolic,
        "exact_replay_checks": checks,
        "all_replay_checks_pass": all(
            item["signature_matches_symbolic_table"] for item in checks
        ),
        "proof_boundary": [
            "The symbolic classification proves p-independence for this declared carrier, partition, alphabet, and route semantics.",
            "It does not prove p-independence for another representation or marked partition.",
            "It does not identify an RG fixed point or an asymptotic limit.",
        ],
        "implementation": {
            "files": files,
            "implementation_sha256": content_digest(files),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--primes",
        type=int,
        nargs="+",
        default=[3, 5, 7, 11, 13, 17, 19, 23, 29],
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.primes)
    if not payload["all_replay_checks_pass"]:
        raise AssertionError("symbolic zero-route table did not replay exactly")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "bundle_id": payload["bundle_id"],
                "content_sha256": content_digest(payload),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
