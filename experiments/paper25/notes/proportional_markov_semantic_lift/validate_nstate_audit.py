#!/usr/bin/env python3
"""Validate the bounded audit retained by the Paper XXV companion note."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


RESULT = Path(__file__).resolve().parent / "markov_nstate_lift_v2.json"


def parse_matrix(rows: list[list[str]]) -> list[list[Fraction]]:
    matrix = [[Fraction(value) for value in row] for row in rows]
    assert len(matrix) == 3
    assert all(len(row) == 3 for row in matrix)
    assert all(value >= 0 for row in matrix for value in row)
    assert all(sum(row) == 1 for row in matrix)
    return matrix


def hitting_time_0_to_1(matrix: list[list[Fraction]]) -> Fraction:
    # Solve (I-Q)h=1 on transient states {0,2} by Cramer's rule.
    a = 1 - matrix[0][0]
    b = -matrix[0][2]
    c = -matrix[2][0]
    d = 1 - matrix[2][2]
    determinant = a * d - b * c
    assert determinant != 0
    return (d - b) / determinant


def main() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["schema"] == "rime-lite.deterministic-stochastic-bridge-nstate.v2"
    assert payload["A1"]["non_monotone"] is True
    a2 = payload["A2"]
    assert a2["both_directions"] is True
    shortcut = parse_matrix(a2["below_example"]["matrix"])
    trap = parse_matrix(a2["above_example"]["matrix"])
    assert shortcut[0] == trap[0]
    assert shortcut[0][1] == Fraction(3, 20)
    shortcut_time = hitting_time_0_to_1(shortcut)
    trap_time = hitting_time_0_to_1(trap)
    assert shortcut_time == Fraction(a2["below_example"]["E_exact"]) == Fraction(180, 67)
    assert trap_time == Fraction(a2["above_example"]["E_exact"]) == Fraction(100, 7)
    geometric_guess = 1 / shortcut[0][1]
    assert shortcut_time < geometric_guess < trap_time
    assert abs(float(shortcut_time) - a2["below_example"]["E"]) < 1e-12
    assert abs(float(trap_time) - a2["above_example"]["E"]) < 1e-12
    assert payload["A3"]["holds"] is True
    assert payload["A4"]["monotone"] is True
    assert payload["A4"]["violations"] == 0
    assert payload["A5"]["monotone"] is True
    assert payload["A5"]["violations"] == 0
    gap = payload["absolute_spectral_gap"]
    assert gap["status"] == "EXPLICIT_NEGATIVE_BOUNDARY"
    assert gap["nonmonotone"] is True
    assert len(gap["points"]) == 3
    print("PASS PAPER25-COMPANION-NSTATE-AUDIT")


if __name__ == "__main__":
    main()
