#!/usr/bin/env python3
"""Separately implemented bounded replay of the fixed catalogue without writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper37"
sys.path.insert(0, str(PACKAGE))

from audit_scope import (  # noqa: E402
    AFFINE2, CHECKS, CLAIM_BOUNDARY, CYCLE, DOMAIN_COUNTS, IDENTITY,
    MATCHED_G_VALUES, PAIRS, RESULT_RELATIVE, RESULT_SCHEMA, RESULT_STATUS,
    THREE_CYCLE, TRANSPOSITION, Branch, branches, scope_record,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_result() -> dict:
    raw = (ROOT / RESULT_RELATIVE).read_bytes()
    require(b"\r" not in raw, "result must have LF bytes")
    return json.loads(raw.decode("utf-8"))


def require_equal(actual: object, expected: object, message: str) -> None:
    # JSON distinguishes booleans from integer coordinates, unlike Python ==.
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            message)


def check_structure(record: dict) -> None:
    require(isinstance(record, dict), "result is not an object")
    require(set(record) == {
        "schema", "status", "scope", "checks", "claim_boundary",
        "domains", "cases", "matched_controls",
    }, "result field inventory drift")
    require(record["schema"] == RESULT_SCHEMA, "result schema drift")
    require(record["status"] == RESULT_STATUS, "result status drift")
    require_equal(record["scope"], scope_record(), "fixed scope drift")
    require(record["checks"] == list(CHECKS), "check inventory drift")
    require(record["claim_boundary"] == CLAIM_BOUNDARY, "claim boundary drift")
    require_equal(record["domains"], list(DOMAIN_COUNTS), "domain coverage drift")
    catalogue = [(branch, j) for branch in branches() for j in range(1, branch.g)]
    require(isinstance(record["cases"], list)
            and len(record["cases"]) == len(catalogue), "source-case coverage drift")
    for row, (branch, source) in zip(record["cases"], catalogue, strict=True):
        require(isinstance(row, dict), "case is not an object")
        expected_input = {**branch.record(), "source_lane": source}
        require_equal({key: row.get(key) for key in expected_input}, expected_input,
                      f"case input/order drift: {branch.identifier}, source {source}")
    controls = record["matched_controls"]
    require(isinstance(controls, list) and len(controls) == len(MATCHED_G_VALUES),
            "matched control coverage drift")
    require([row.get("g") for row in controls] == list(MATCHED_G_VALUES),
            "matched g-values drift")


# Only the declarative catalogue is shared with the producer. Coordinate
# actions, reachability, group closure, cosets, and projections are recomputed.
def branch_map(spec: Branch) -> dict[int, int]:
    g = spec.g
    table = {}
    star = tuple(t * g for t in range(1, 5))
    for index, coordinate in enumerate(star):
        table[coordinate] = star[spec.punctured[index]]
    for lane in range(1, g):
        domain = tuple(lane + g * i for i in range(5))
        image = tuple(spec.targets[lane - 1] + g * i for i in range(5))
        for index, coordinate in enumerate(domain):
            table[coordinate] = image[spec.restrictions[lane - 1][index]]
    require(set(table) == set(table.values()) == set(range(1, 5 * g)),
            "invalid finite branch")
    return table


def seed(g: int, lane: int) -> tuple[int, ...]:
    return tuple(lane + g * i for i in range(5))


def move(state: tuple[int, ...], table: dict[int, int],
         label: int, g: int) -> tuple[int, ...] | None:
    rotated = tuple((table[q] + label) % (5 * g) for q in state)
    if 0 in rotated and g in rotated:
        return None
    image = tuple(g if q == 0 else q for q in rotated)
    require(len(set(image)) == 5 and 0 not in image, "guard/action inconsistency")
    return image


def raw_closure(start: tuple[int, ...], table: dict[int, int], g: int) -> set[tuple[int, ...]]:
    found, pending = {start}, [start]
    while pending:
        state = pending.pop()
        lane = state[0] % g
        require(lane != 0 and set(state) == set(seed(g, lane)),
                "raw closure is not confined to a full ordinary lane")
        for label in range(5 * g):
            child = move(state, table, label, g)
            expected_guard = (table[state[0]] + label) % g != 0
            require((child is not None) == expected_guard, "uniform guard mismatch")
            if child is not None and child not in found:
                found.add(child)
                pending.append(child)
    return found


def subgroup(restrictions: tuple[tuple[int, ...], ...]) -> set[tuple[int, ...]]:
    members = {IDENTITY}
    while True:
        extended = members | {
            tuple(kappa[generator[i]] for i in range(5))
            for kappa in members for generator in (CYCLE,) + restrictions
        }
        if extended == members:
            return members
        members = extended


def phase_class(state: tuple[int, ...], g: int) -> tuple:
    lane = state[0] % g
    positions = tuple(q // g for q in state)
    rotated = [tuple((q + offset) % 5 for q in positions) for offset in range(5)]
    return lane, min(rotated)


def normalizer_condition(spec: Branch) -> bool:
    phases = {tuple((q + t) % 5 for q in range(5)) for t in range(5)}
    for sigma in spec.restrictions:
        inverse = tuple(sigma.index(i) for i in range(5))
        conjugate = tuple(sigma[(inverse[i] + 1) % 5] for i in range(5))
        if conjugate not in phases:
            return False
    return True


def check_words(spec: Branch, table: dict[int, int]) -> dict[str, int]:
    coordinates = tuple(sorted(table))
    power = tuple(table[q] for q in coordinates)
    order = 1
    while power != coordinates:
        power = tuple(table[q] for q in power)
        order += 1
    undo = [0] * (order - 1)

    def execute(initial: tuple[int, ...], labels: list[int]) -> tuple[int, ...]:
        current = initial
        for label in labels:
            successor = move(current, table, label, spec.g)
            require(successor is not None, "actual relocation loop is not guarded")
            current = successor
        return current

    words = []
    for j in range(1, spec.g):
        for h in range(1, spec.g):
            labels = undo + [(h - j) % (5 * spec.g)]
            require(execute(seed(spec.g, j), labels) == seed(spec.g, h),
                    "pure relocation mismatch")
            words.append(labels)
    for h in range(1, spec.g):
        labels = undo + [spec.g]
        require(execute(seed(spec.g, h), labels)
                == tuple(h + spec.g * CYCLE[i] for i in range(5)),
                "phase loop mismatch")
        words.append(labels)
        for j in range(1, spec.g):
            labels = (undo + [(j - h) % (5 * spec.g)] + [0]
                      + undo + [(h - spec.targets[j - 1]) % (5 * spec.g)])
            require(execute(seed(spec.g, h), labels)
                    == tuple(h + spec.g * spec.restrictions[j - 1][i] for i in range(5)),
                    "local-generator loop mismatch")
            words.append(labels)
    return {"branch_order": order, "executed_words": len(words),
            "maximum_word_length": max(len(word) for word in words)}


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def recompute(spec: Branch, source: int) -> tuple[dict, set, dict]:
    g, table = spec.g, branch_map(spec)
    members = subgroup(spec.restrictions)
    actual = raw_closure(seed(g, source), table, g)
    predicted = {
        tuple(lane + g * kappa[i] for i in range(5))
        for lane in range(1, g) for kappa in members
    }
    require(actual == predicted, "raw/group injection sets differ")
    terminals = set()
    actual_survivors = {pair: set() for pair in PAIRS}
    for state in actual:
        for label in range(5 * g):
            mu = tuple((table[q] + label) % (5 * g) for q in state)
            if 0 not in mu or g not in mu:
                continue
            require(set(mu) == {i * g for i in range(5)}, "terminal not on full kernel lane")
            terminals.add(mu)
            fused = tuple(sorted((mu.index(0), mu.index(g))))
            beta = tuple(g if q == 0 else q for q in mu)
            actual_survivors[fused].add(tuple(beta[i] for i in range(5) if i not in fused))
    require(terminals == {tuple(g * kappa[i] for i in range(5)) for kappa in members},
            "actual terminal placements differ from group prediction")
    swap_present = TRANSPOSITION in members
    for pair in PAIRS:
        fiber = [kappa for kappa in members if {kappa[i] for i in pair} == {0, 1}]
        expected_survivors = {
            tuple(g * kappa[i] for i in range(5) if i not in pair) for kappa in fiber
        }
        require(actual_survivors[pair] == expected_survivors,
                "full survivor set differs, even if counts might agree")
        require(len(fiber) == len(expected_survivors) * (2 if swap_present else 1),
                "kernel-swap restriction multiplicity differs")

    classes = {phase_class(state, g) for state in actual}
    require(len(classes) * 5 == len(actual), "phase-coset size differs")
    first_output = {}
    witness = None
    for state in sorted(actual):
        for label in range(5 * g):
            child = move(state, table, label, g)
            if child is None:
                continue
            key, image_class = (phase_class(state, g), label), phase_class(child, g)
            previous = first_output.get(key)
            if previous is not None and previous[1] != image_class and witness is None:
                witness = {
                    "label": label,
                    "source_representatives": [list(previous[0]), list(state)],
                    "output_phase_classes": [
                        [previous[1][0], list(previous[1][1])],
                        [image_class[0], list(image_class[1])],
                    ],
                }
            first_output.setdefault(key, (state, image_class))
    deterministic = normalizer_condition(spec)
    require(deterministic == (witness is None), "phase normalizer equivalence differs")
    survivors_payload = [
        {"pair": list(pair), "placements": [list(s) for s in sorted(actual_survivors[pair])]}
        for pair in PAIRS
    ]
    row = {
        **spec.record(), "source_lane": source,
        "group_order": len(members), "reachable_injections": len(actual),
        "phase_classes": len(classes), "terminal_placements": len(terminals),
        "deterministic_phase_descent": deterministic,
        "phase_non_descent_witness": witness, "kernel_swap_in_group": swap_present,
        "actual_word_controls": check_words(spec, table),
        "survivor_counts": [len(actual_survivors[pair]) for pair in PAIRS],
        "fused_pairs": [list(pair) for pair in PAIRS if actual_survivors[pair]],
        "digests": {
            "group": fingerprint([list(k) for k in sorted(members)]),
            "reachable_injections": fingerprint([list(s) for s in sorted(actual)]),
            "terminal_placements": fingerprint([list(mu) for mu in sorted(terminals)]),
            "survivor_spectra": fingerprint(survivors_payload),
        },
    }
    return row, actual, actual_survivors


def matched_control(g: int) -> dict:
    families = {}
    for name, sigma in (("F20", AFFINE2), ("A5", THREE_CYCLE), ("S5", TRANSPOSITION)):
        spec = Branch(f"matched-g{g}-{name}", g, tuple(range(1, g)),
                      (sigma,) + (IDENTITY,) * (g - 2), (0, 1, 2, 3))
        families[name] = (spec, *recompute(spec, 1))
    f_spec, f_row, _, f_spectra = families["F20"]
    _, a_row, a_states, a_spectra = families["A5"]
    s_spec, s_row, s_states, s_spectra = families["S5"]

    def graph(spec: Branch) -> list[tuple]:
        table = branch_map(spec)
        rows = []
        for lane in range(1, g):
            for label in range(5 * g):
                mu = {(table[q] + label) % (5 * g) for q in seed(g, lane)}
                rows.append((lane, label, frozenset(mu), 0 in mu and g in mu))
        return rows

    def parities(spec: Branch) -> list[int]:
        return [sum(sigma[i] > sigma[j] for i, j in PAIRS) % 2
                for sigma in spec.restrictions]

    require(graph(f_spec) == graph(s_spec), "full unsigned labelled graphs differ")
    require(parities(f_spec) == parities(s_spec), "local parity vectors differ")
    require(all(len(f_spectra[pair]) == 2 and len(s_spectra[pair]) == 6 for pair in PAIRS),
            "matched fused-pair/survivor distinction differs")
    require(a_states != s_states and a_spectra == s_spectra,
            "A5/S5 complete set comparison differs")
    require([f_row["group_order"], a_row["group_order"], s_row["group_order"]]
            == [20, 60, 120], "matched groups differ")
    return {
        "g": g,
        "F20_S5": {
            "unsigned_labelled_graph_equal": True, "local_parity_equal": True,
            "fused_pairs_equal": [list(pair) for pair in PAIRS],
            "survivor_counts": {"F20": [2] * 10, "S5": [6] * 10},
            "survivor_digests": {
                "F20": f_row["digests"]["survivor_spectra"],
                "S5": s_row["digests"]["survivor_spectra"],
            },
        },
        "A5_S5": {
            "reachable_counts": {"A5": len(a_states), "S5": len(s_states)},
            "complete_survivor_sets_equal": True, "survivors_per_pair": 6,
            "common_survivor_digest": a_row["digests"]["survivor_spectra"],
        },
    }


def validate(record: dict, *, replay: bool = True) -> None:
    check_structure(record)
    if not replay:
        return
    position = 0
    for spec in branches():
        for source in range(1, spec.g):
            actual = recompute(spec, source)[0]
            require_equal(record["cases"][position], actual,
                          f"finite replay drift: {spec.identifier}, source {source}")
            position += 1
    expected = [matched_control(g) for g in MATCHED_G_VALUES]
    require_equal(record["matched_controls"], expected, "matched control replay drift")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true",
                        help="check fixed input/coverage structure; do not claim finite replay")
    args = parser.parse_args()
    record = load_result()
    validate(record, replay=not args.static)
    mode = "structure only; replay skipped" if args.static else "separately implemented bounded replay"
    print(f"PASS: {mode}; 216 branches, 312 source cases, matched g=2,3,4")


if __name__ == "__main__":
    main()
