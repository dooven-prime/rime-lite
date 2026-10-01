#!/usr/bin/env python3
"""Exact labelled-lineage discovery audit for Paper XXXIV.

The audit fixes one normalized source injection, follows complete guarded
lineage paths, and records terminal incidences from the same (lambda, u)
witness. It searches for branches with the same fused-pair reachability
signature but different survivor spectra.

The output is a bounded theorem-discovery control, not evidence for an all-n
survivor theorem or for any typed transfer statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from itertools import combinations, permutations
from math import factorial
from pathlib import Path
from typing import Iterable, TypeAlias


Injection: TypeAlias = tuple[int, int, int, int, int]
Pair: TypeAlias = tuple[int, int]
Perm: TypeAlias = tuple[int, ...]
Survivor: TypeAlias = tuple[int, int, int]

SCHEMA = "rime.paper34.survivor-incidence-audit.v2"
STATUS = "FINITE_THEOREM_DISCOVERY_CONTROL"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def epsilon(delta: int, q: int) -> int:
    return delta if q == 0 else q


def branch_perm(n: int, values: tuple[int, ...]) -> Perm:
    carrier = tuple(range(1, n))
    require(tuple(sorted(values)) == carrier, "branch is not a permutation of E")
    return (0, *values)


def identity_branch(n: int) -> Perm:
    return tuple(range(n))


def cycle_reflection_branch(n: int) -> Perm:
    """Reflection fixing lane coordinate 1 in the delta=1 punctured cycle."""

    values = (1, *range(n - 1, 1, -1))
    return branch_perm(n, values)


def dihedral_branch(n: int, shift: int, orientation: int) -> Perm:
    """Return psi^shift for +1 and psi^shift rho for -1 on E."""

    require(orientation in (-1, 1), "orientation character must be +1 or -1")
    lane_length = n - 1
    values = tuple(
        1 + ((orientation * (q - 1) + shift) % lane_length)
        for q in range(1, n)
    )
    return branch_perm(n, values)


def phi_injection(
    n: int, delta: int, branch: Perm, label: int, state: Injection
) -> Injection | None:
    pre = tuple((branch[q] + label) % n for q in state)
    if {0, delta} <= set(pre):
        return None
    output = tuple(epsilon(delta, q) for q in pre)
    require(len(set(output)) == 5, "guarded return lost lineage injectivity")
    require(all(1 <= q < n for q in output), "return left normalized carrier")
    return output  # type: ignore[return-value]


def reachable_injections(
    n: int, delta: int, branch: Perm, source: Injection
) -> frozenset[Injection]:
    reached = {source}
    queue = deque([source])
    while queue:
        state = queue.popleft()
        for label in range(n):
            output = phi_injection(n, delta, branch, label, state)
            if output is not None and output not in reached:
                reached.add(output)
                queue.append(output)
    return frozenset(reached)


def terminal_incidence(
    n: int,
    delta: int,
    branch: Perm,
    state: Injection,
    fused: Pair,
    terminal_label: int,
) -> Injection | None:
    pre = tuple((branch[q] + terminal_label) % n for q in state)
    if {pre[fused[0]], pre[fused[1]]} != {0, delta}:
        return None
    output = tuple(epsilon(delta, q) for q in pre)
    require(output[fused[0]] == delta, "first fused lineage missed collision root")
    require(output[fused[1]] == delta, "second fused lineage missed collision root")
    survivors = tuple(index for index in range(5) if index not in fused)
    survivor_values = tuple(output[index] for index in survivors)
    require(len(set(survivor_values)) == 3, "survivor restriction is not injective")
    require(delta not in survivor_values, "survivor occupied the collision root")
    return output  # type: ignore[return-value]


def survivor_spectra(
    n: int, delta: int, branch: Perm, source: Injection
) -> tuple[
    dict[Pair, frozenset[Survivor]],
    dict[Pair, frozenset[Injection]],
    int,
]:
    reachable = reachable_injections(n, delta, branch, source)
    survivor_rows: dict[Pair, set[Survivor]] = {
        pair: set() for pair in combinations(range(5), 2)
    }
    boundary_rows: dict[Pair, set[Injection]] = {
        pair: set() for pair in combinations(range(5), 2)
    }
    witness_count = 0
    for state in reachable:
        for fused in survivor_rows:
            survivor_labels = tuple(index for index in range(5) if index not in fused)
            for terminal_label in range(n):
                incidence = terminal_incidence(
                    n,
                    delta,
                    branch,
                    state,
                    fused,
                    terminal_label,
                )
                if incidence is None:
                    continue
                witness_count += 1
                boundary_rows[fused].add(incidence)
                survivor_rows[fused].add(
                    tuple(incidence[index] for index in survivor_labels)  # type: ignore[arg-type]
                )
    return (
        {pair: frozenset(rows) for pair, rows in survivor_rows.items()},
        {pair: frozenset(rows) for pair, rows in boundary_rows.items()},
        witness_count,
    )


def pair_signature(spectra: dict[Pair, frozenset[Survivor]]) -> tuple[Pair, ...]:
    return tuple(pair for pair, rows in sorted(spectra.items()) if rows)


def oriented_pair_data(pair: Pair) -> tuple[int, int, tuple[int, int, int]]:
    """Orient a consecutive source pair in the positive five-cycle."""

    left, right = pair
    if (left + 1) % 5 == right:
        first, second = left, right
    else:
        require((right + 1) % 5 == left, "pair is not consecutive")
        first, second = right, left
    survivors = tuple((second + offset) % 5 for offset in range(1, 4))
    return first, second, survivors  # type: ignore[return-value]


def expected_orientation_spectrum(
    n: int,
    pair: Pair,
    orientation: int,
) -> frozenset[Survivor]:
    """Exact increasing/decreasing survivor family for one fused pair."""

    require(orientation in (-1, 1), "terminal orientation must be +1 or -1")
    _first, _second, survivor_order = oriented_pair_data(pair)
    sorted_survivors = tuple(sorted(survivor_order))
    rows: set[Survivor] = set()
    for coordinates in combinations(range(2, n), 3):
        placed = coordinates if orientation == 1 else tuple(reversed(coordinates))
        placement = dict(zip(survivor_order, placed, strict=True))
        rows.add(tuple(placement[index] for index in sorted_survivors))  # type: ignore[arg-type]
    return frozenset(rows)


def spectrum_digest(spectra: dict[Pair, frozenset[Survivor]]) -> str:
    payload = [
        [list(pair), [list(row) for row in sorted(rows)]]
        for pair, rows in sorted(spectra.items())
    ]
    encoded = json.dumps(payload, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def branch_row(
    branch: Perm,
    reachable: int,
    witnesses: int,
    spectra: dict[Pair, frozenset[Survivor]],
    boundary: dict[Pair, frozenset[Injection]],
) -> dict[str, object]:
    return {
        "branch": list(branch[1:]),
        "reachable_lineage_states": reachable,
        "terminal_witnesses": witnesses,
        "hittable_pairs": [list(pair) for pair in pair_signature(spectra)],
        "survivor_spectrum_sizes": {
            f"{pair[0]}-{pair[1]}": len(rows)
            for pair, rows in sorted(spectra.items())
        },
        "boundary_spectrum_sizes": {
            f"{pair[0]}-{pair[1]}": len(rows)
            for pair, rows in sorted(boundary.items())
        },
        "survivor_digest": spectrum_digest(spectra),
    }


def canonical_control(
    n: int,
    delta: int,
    source: Injection,
    spectra: dict[Pair, frozenset[Survivor]],
    boundary: dict[Pair, frozenset[Injection]],
) -> dict[str, object]:
    require(delta == 1, "canonical recovery control currently uses delta=1")
    consecutive = {
        tuple(sorted((index, (index + 1) % 5)))
        for index in range(5)
    }
    actual = set(pair_signature(spectra))
    require(actual == consecutive, "canonical fused-pair set mismatch")
    expected_per_pair = len(tuple(combinations(range(1, n - 1), 3)))
    require(
        all(len(spectra[pair]) == expected_per_pair for pair in consecutive),
        "canonical survivor count mismatch",
    )
    require(
        all(len(boundary[pair]) == expected_per_pair for pair in consecutive),
        "canonical boundary count mismatch",
    )
    return {
        "source": list(source),
        "consecutive_pairs": [list(pair) for pair in sorted(consecutive)],
        "survivors_per_pair": expected_per_pair,
        "total_boundary_incidences": sum(len(rows) for rows in boundary.values()),
        "paper29_expected_total": 5 * expected_per_pair,
        "status": "MATCHED_CANONICAL_RECOVERY_CONTROL",
    }


def find_pair_summary_non_descent(
    rows: list[
        tuple[
            Perm,
            dict[Pair, frozenset[Survivor]],
            dict[Pair, frozenset[Injection]],
            int,
            int,
        ]
    ],
) -> dict[str, object] | None:
    groups: defaultdict[
        tuple[Pair, ...],
        dict[str, tuple[Perm, dict[Pair, frozenset[Survivor]]]],
    ] = defaultdict(dict)
    for branch, spectra, _boundary, _reachable, _witnesses in rows:
        groups[pair_signature(spectra)].setdefault(
            spectrum_digest(spectra),
            (branch, spectra),
        )
    for signature, variants in groups.items():
        if len(variants) < 2:
            continue
        left, right = list(variants.values())[:2]
        left_branch, left_spectra = left
        right_branch, right_spectra = right
        differing = next(
            pair
            for pair in sorted(left_spectra)
            if left_spectra[pair] != right_spectra[pair]
        )
        only_left = sorted(left_spectra[differing] - right_spectra[differing])
        only_right = sorted(right_spectra[differing] - left_spectra[differing])
        return {
            "same_hittable_pairs": [list(pair) for pair in signature],
            "left_branch": list(left_branch[1:]),
            "right_branch": list(right_branch[1:]),
            "differing_pair": list(differing),
            "left_spectrum_size": len(left_spectra[differing]),
            "right_spectrum_size": len(right_spectra[differing]),
            "first_only_left": list(only_left[0]) if only_left else None,
            "first_only_right": list(only_right[0]) if only_right else None,
            "status": "FINITE_MATCHED_NON_DESCENT_WITNESS",
        }
    return None


def compare_branches(
    n: int,
    delta: int,
    source: Injection,
    left: Perm,
    right: Perm,
) -> dict[str, object]:
    left_spectra, _left_boundary, _left_witnesses = survivor_spectra(
        n, delta, left, source
    )
    right_spectra, _right_boundary, _right_witnesses = survivor_spectra(
        n, delta, right, source
    )
    left_pairs = pair_signature(left_spectra)
    right_pairs = pair_signature(right_spectra)
    differing_pairs = [
        pair
        for pair in sorted(left_spectra)
        if left_spectra[pair] != right_spectra[pair]
    ]
    return {
        "left_branch": list(left[1:]),
        "right_branch": list(right[1:]),
        "same_hittable_pairs": left_pairs == right_pairs,
        "hittable_pairs": [list(pair) for pair in left_pairs]
        if left_pairs == right_pairs
        else None,
        "different_survivor_spectra": bool(differing_pairs),
        "differing_pairs": [list(pair) for pair in differing_pairs],
        "left_spectrum_sizes": {
            f"{pair[0]}-{pair[1]}": len(left_spectra[pair])
            for pair in differing_pairs
        },
        "right_spectrum_sizes": {
            f"{pair[0]}-{pair[1]}": len(right_spectra[pair])
            for pair in differing_pairs
        },
        "status": "BOUNDED_MATCHED_DIHEDRAL_CONTROL",
    }


def identity_reflection_family_control(max_n: int = 9) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for n in range(6, max_n + 1):
        source: Injection = tuple(range(1, 6))  # type: ignore[assignment]
        comparison = compare_branches(
            n,
            1,
            source,
            identity_branch(n),
            cycle_reflection_branch(n),
        )
        expected = len(tuple(combinations(range(2, n), 3)))
        require(comparison["same_hittable_pairs"] is True, "family pair drift")
        require(
            comparison["different_survivor_spectra"] is True,
            "family survivor spectra unexpectedly agree",
        )
        left_sizes = comparison["left_spectrum_sizes"]
        right_sizes = comparison["right_spectrum_sizes"]
        require(isinstance(left_sizes, dict), "left family sizes missing")
        require(isinstance(right_sizes, dict), "right family sizes missing")
        require(
            set(left_sizes.values()) == {expected},
            "identity family survivor count mismatch",
        )
        require(
            set(right_sizes.values()) == {2 * expected},
            "reflection family survivor count mismatch",
        )
        rows.append(
            {
                "n": n,
                "delta": 1,
                "hittable_pairs": len(comparison["hittable_pairs"]),  # type: ignore[arg-type]
                "identity_survivors_per_pair": expected,
                "reflection_survivors_per_pair": 2 * expected,
            }
        )
    return {
        "min_n": 6,
        "max_n": max_n,
        "rows": rows,
        "status": "BOUNDED_CONTROL_OF_SYMBOLIC_NONDESCENT_NOT_PROOF",
    }


def dihedral_family_control(max_n: int = 9) -> dict[str, object]:
    """Check the exact orientation classification for every dihedral branch."""

    rows: list[dict[str, object]] = []
    consecutive = {
        tuple(sorted((index, (index + 1) % 5)))
        for index in range(5)
    }
    for n in range(6, max_n + 1):
        source: Injection = tuple(range(1, 6))  # type: ignore[assignment]
        expected_positive = {
            pair: expected_orientation_spectrum(n, pair, 1)
            for pair in consecutive
        }
        expected_negative = {
            pair: expected_orientation_spectrum(n, pair, -1)
            for pair in consecutive
        }
        checked = 0
        rotations = 0
        reflections = 0
        for orientation in (1, -1):
            for shift in range(n - 1):
                branch = dihedral_branch(n, shift, orientation)
                spectra, _boundary, _witnesses = survivor_spectra(
                    n, 1, branch, source
                )
                require(
                    set(pair_signature(spectra)) == consecutive,
                    "dihedral fused-pair classification drift",
                )
                for pair in consecutive:
                    expected = expected_positive[pair]
                    if orientation == -1:
                        expected = expected | expected_negative[pair]
                    require(
                        spectra[pair] == expected,
                        "dihedral orientation spectrum mismatch",
                    )
                checked += 1
                rotations += orientation == 1
                reflections += orientation == -1
        rows.append(
            {
                "n": n,
                "delta": 1,
                "dihedral_branches_checked": checked,
                "rotations_checked": rotations,
                "reflections_checked": reflections,
                "hittable_pairs": 5,
                "positive_survivors_per_pair": len(next(iter(expected_positive.values()))),
                "reflection_survivors_per_pair": 2
                * len(next(iter(expected_positive.values()))),
                "exact_orientation_spectra_matched": True,
            }
        )
    return {
        "min_n": 6,
        "max_n": max_n,
        "orientation_character": {
            "rotation": "+1",
            "reflection": "-1",
        },
        "rows": rows,
        "status": "BOUNDED_CONTROL_OF_DIHEDRAL_CLASSIFICATION_NOT_PROOF",
    }


def build_result(n: int, delta: int, branch_limit: int | None) -> dict[str, object]:
    if n < 6:
        raise ValueError("n must be at least 6")
    if not 1 <= delta < n:
        raise ValueError("delta must lie in 1..n-1")
    carrier = tuple(range(1, n))
    source: Injection = tuple(carrier[:5])  # type: ignore[assignment]
    branch_total = factorial(n - 1)
    limit = branch_total if branch_limit is None else min(branch_limit, branch_total)
    rows: list[
        tuple[
            Perm,
            dict[Pair, frozenset[Survivor]],
            dict[Pair, frozenset[Injection]],
            int,
            int,
        ]
    ] = []

    for values in permutations(carrier):
        if len(rows) >= limit:
            break
        branch = branch_perm(n, values)
        reachable = reachable_injections(n, delta, branch, source)
        spectra, boundary, witnesses = survivor_spectra(
            n, delta, branch, source
        )
        rows.append((branch, spectra, boundary, len(reachable), witnesses))

    identity_row = next(row for row in rows if row[0] == identity_branch(n))
    identity, identity_spectra, identity_boundary, identity_reachable, identity_witnesses = (
        identity_row
    )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "n": n,
            "delta": delta,
            "source": list(source),
            "branches_checked": len(rows),
            "branch_fiber_size": branch_total,
            "branch_scan_complete": len(rows) == branch_total,
        },
        "normalized_incidence_identity": {
            "formula": "beta = epsilon_delta o p^u o a o lambda",
            "same_witness_required": True,
        },
        "identity_branch": branch_row(
            identity,
            identity_reachable,
            identity_witnesses,
            identity_spectra,
            identity_boundary,
        ),
        "canonical_recovery": canonical_control(
            n,
            delta,
            source,
            identity_spectra,
            identity_boundary,
        ),
        "identity_reflection_control": compare_branches(
            n,
            delta,
            source,
            identity_branch(n),
            cycle_reflection_branch(n),
        ),
        "identity_reflection_family_control": identity_reflection_family_control(),
        "one_lane_dihedral_family_control": dihedral_family_control(),
        "pair_summary_non_descent": find_pair_summary_non_descent(rows),
        "claim_boundary": [
            "the normalized incidence identity is algebraic; finite replay is only a control",
            "a finite matched pair proves non-descent only on the declared branch domain",
            "absence of a matched pair is OPEN, not a descent theorem",
            "raw survivor incidence does not establish typed transfer membership",
        ],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--delta", type=int, default=1)
    parser.add_argument("--branch-limit", type=int)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_result(args.n, args.delta, args.branch_limit)
    payload = json.dumps(result, indent=2, sort_keys=False) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
