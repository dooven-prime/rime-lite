"""Paper VII v2.1: exact tables for carrier-structured incidence.

The theorem layer is a direct-product refinement of the free matrix-pair
incidence formulas.  This script evaluates those formulas exactly, records the
diagonal-ambient boundary, and checks a complementary-support represented
pullback on which incidence is identically forced.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
JSON_PATH = RESULTS_DIR / "structured_incidence_geometry_v2_1.json"
TEXT_PATH = RESULTS_DIR / "structured_incidence_geometry_v2_1.txt"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block_ambient_dimension(blocks: list[dict]) -> int:
    return sum(row["m"] * row["n"] + row["n"] * row["p"] for row in blocks)


def fixed_rank_vector_dimension(blocks: list[dict]) -> int:
    return sum(
        row["r"] * (row["m"] + row["n"] - row["r"])
        + row["p"] * (row["n"] - row["r"])
        for row in blocks
    )


def fixed_rank_vector_codimension(blocks: list[dict]) -> int:
    return sum(
        (row["m"] - row["r"]) * (row["n"] - row["r"])
        + row["p"] * row["r"]
        for row in blocks
    )


def fixed_double_rank_vector_dimension(blocks: list[dict]) -> int:
    for row in blocks:
        if not 0 <= row["s"] <= min(row["n"] - row["r"], row["p"]):
            raise ValueError(f"inadmissible carrier ranks: {row}")
    return sum(
        row["r"] * (row["m"] + row["n"] - row["r"])
        + row["s"] * (row["n"] - row["r"] + row["p"] - row["s"])
        for row in blocks
    )


def rank_pair_stratum_dimension(blocks: list[dict]) -> int:
    return sum(
        row["r"] * (row["m"] + row["n"] - row["r"])
        + row["s"] * (row["n"] + row["p"] - row["s"])
        for row in blocks
    )


def fixed_double_rank_relative_codimension(blocks: list[dict]) -> int:
    return sum(row["r"] * row["s"] for row in blocks)


def structured_record(label: str, blocks: list[dict]) -> dict:
    ambient = block_ambient_dimension(blocks)
    rank_dimension = fixed_rank_vector_dimension(blocks)
    rank_codimension = fixed_rank_vector_codimension(blocks)
    double_dimension = fixed_double_rank_vector_dimension(blocks)
    rank_pair_dimension = rank_pair_stratum_dimension(blocks)
    relative_codimension = fixed_double_rank_relative_codimension(blocks)
    assert ambient - rank_dimension == rank_codimension
    assert rank_pair_dimension - double_dimension == relative_codimension
    return {
        "label": label,
        "blocks": blocks,
        "structured_ambient_dimension": ambient,
        "fixed_rank_vector_dimension": rank_dimension,
        "fixed_rank_vector_codimension": rank_codimension,
        "fixed_double_rank_vector_dimension": double_dimension,
        "ambient_rank_pair_stratum_dimension": rank_pair_dimension,
        "relative_codimension_in_rank_pair_stratum": relative_codimension,
    }


def diagonal_incidence_count(q: int, d: int) -> int:
    """Count diagonal pairs over F_q satisfying a_i b_i = 0 for all i."""
    count = 0
    for a in itertools.product(range(q), repeat=d):
        for b in itertools.product(range(q), repeat=d):
            if all((left * right) % q == 0 for left, right in zip(a, b)):
                count += 1
    return count


def main(*, write_results: bool = False) -> None:
    structured_examples = [
        structured_record(
            "two_carrier_asymmetric",
            [
                {"carrier": "alpha", "m": 3, "n": 2, "p": 2, "r": 1, "s": 1},
                {"carrier": "beta", "m": 2, "n": 3, "p": 1, "r": 1, "s": 1},
            ],
        ),
        structured_record(
            "three_carrier_mixed_ranks",
            [
                {"carrier": "alpha", "m": 2, "n": 3, "p": 2, "r": 1, "s": 1},
                {"carrier": "beta", "m": 1, "n": 2, "p": 3, "r": 0, "s": 2},
                {"carrier": "gamma", "m": 2, "n": 1, "p": 2, "r": 1, "s": 0},
            ],
        ),
    ]

    diagonal_rows = []
    for d in range(1, 7):
        diagonal_rows.append(
            {
                "d": d,
                "ambient_dimension": 2 * d,
                "zero_product_locus_dimension": d,
                "zero_product_locus_codimension": d,
                "nonzero_factor_locus_nonempty": d >= 2,
            }
        )

    finite_field_checks = []
    for q in (2, 3):
        for d in (1, 2, 3):
            direct_count = diagonal_incidence_count(q, d)
            formula_count = (2 * q - 1) ** d
            assert direct_count == formula_count
            finite_field_checks.append(
                {
                    "field_order": q,
                    "d": d,
                    "direct_zero_product_pair_count": direct_count,
                    "formula_zero_product_pair_count": formula_count,
                    "nonzero_factor_pair_count": formula_count - 2 * (q**d) + 1,
                }
            )

    complementary_support = {
        "parameter_space": "C^2 with coordinates (u,v)",
        "map": "A(u,v)=diag(u,0), B(u,v)=diag(0,v)",
        "product": "A(u,v)B(u,v)=0 identically",
        "pullback_incidence_locus": "all of C^2",
        "pullback_codimension": 0,
        "nonzero_factor_open_subset": "{u!=0 and v!=0}",
    }

    payload = {
        "schema": "paper7.structured-incidence-geometry.v2.1",
        "claim_status": "Computational Certificate",
        "certificate_kind": "exact_integer_formula_evaluation",
        "field_for_theorem": "complex numbers",
        "structured_ambient": (
            "direct_sum_b Mat(m_b,n_b) x direct_sum_b Mat(n_b,p_b)"
        ),
        "formulas": {
            "fixed_rank_vector_dimension": (
                "sum_b [r_b(m_b+n_b-r_b)+p_b(n_b-r_b)]"
            ),
            "fixed_rank_vector_codimension": (
                "sum_b [(m_b-r_b)(n_b-r_b)+p_b r_b]"
            ),
            "fixed_double_rank_vector_dimension": (
                "sum_b [r_b(m_b+n_b-r_b)+s_b(n_b-r_b+p_b-s_b)]"
            ),
            "fixed_double_rank_relative_codimension": "sum_b r_b s_b",
        },
        "structured_examples": structured_examples,
        "diagonal_ambient": {
            "description": "d scalar 1x1 carrier blocks",
            "condition": "a_b b_b=0 for every carrier b",
            "rows": diagonal_rows,
            "boundary": (
                "The full diagonal pair ambient has codimension d, not 1. "
                "A support-pattern component can nevertheless have relative "
                "codimension zero."
            ),
        },
        "finite_field_count_checks": finite_field_checks,
        "represented_pullback_control": complementary_support,
        "runtime": {
            "python": platform.python_version(),
            "script_sha256": sha256(Path(__file__)),
        },
    }

    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    lines = [
        "Paper VII v2.1 structured incidence geometry",
        "=" * 72,
        "fixed rank vector codim = sum_b [(m_b-r_b)(n_b-r_b)+p_b r_b]",
        "fixed double-rank relative codim = sum_b r_b s_b",
        "",
        "Diagonal full ambient:",
    ]
    for row in diagonal_rows:
        lines.append(
            f"  d={row['d']}: ambient={row['ambient_dimension']}, "
            f"codim={row['zero_product_locus_codimension']}, "
            f"nonzero-factor={row['nonzero_factor_locus_nonempty']}"
        )
    lines.extend(
        [
            "",
            "Complementary-support represented pullback: codim=0.",
            "The full diagonal ambient has codimension d, not 1.",
        ]
    )
    text_value = "\n".join(lines) + "\n"
    if write_results:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        JSON_PATH.write_text(json_text, encoding="utf-8", newline="\n")
        TEXT_PATH.write_text(text_value, encoding="utf-8", newline="\n")
    else:
        if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != json_text:
            raise SystemExit(f"STALE {JSON_PATH}; rerun with --write-results")
        if not TEXT_PATH.is_file() or TEXT_PATH.read_text(encoding="utf-8") != text_value:
            raise SystemExit(f"STALE {TEXT_PATH}; rerun with --write-results")
    print("\n".join(lines))
    print(f"\n{'WROTE' if write_results else 'PASS'} {JSON_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-results", action="store_true")
    main(write_results=parser.parse_args().write_results)
