#!/usr/bin/env python3
"""Replay exact raw-injection layers without importing producer algorithms."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/paper38"
sys.path.insert(0, str(PACKAGE))
from audit_scope import (  # noqa: E402
    BOUNDARY, MATCHED_G, MAX_RETURNS, PAIRS, RESULT_PATH, SCHEMA,
    branches, matched_branches, scope_record,
)


CASE_KEYS = {
    "input", "source_lane", "group_order", "group_sha256", "coset_budget",
    "aggregate_sha256", "initial_sha256", "first_cumulative_full_layer",
    "layers", "actual_terminal_witnesses",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def verify_shape(record):
    require(isinstance(record, dict) and set(record) == {
        "schema", "status", "claim_boundary", "scope", "cases", "matched_controls",
    }, "result top-level inventory drift")
    require(record["schema"] == SCHEMA and record["status"] == "BOUNDED_CONSISTENCY_CONTROL"
            and record["claim_boundary"] == BOUNDARY, "result evidence boundary drift")
    require(record["scope"] == scope_record(), "fixed budget/scope drift")
    expected = [(branch, source) for branch in branches() for source in range(1, branch.g)]
    require(isinstance(record["cases"], list) and len(record["cases"]) == len(expected),
            "source-case coverage drift")
    all_cases = list(zip(record["cases"], expected))
    controls = record["matched_controls"]
    require(isinstance(controls, list) and len(controls) == len(MATCHED_G), "matched coverage drift")
    for control, g in zip(controls, MATCHED_G):
        require(isinstance(control, dict) and set(control) == {
            "g", "cases", "consecutive_pair_controls",
        } and control["g"] == g, "matched input drift")
        require(isinstance(control["cases"], list) and len(control["cases"]) == 2,
                "matched branch coverage drift")
        all_cases.extend(zip(control["cases"], [(branch, 1) for branch in matched_branches(g)]))
        require(control["consecutive_pair_controls"] == expected_matched_maps(g),
                "matched survivor values drift")
    for case, (branch, source) in all_cases:
        require(isinstance(case, dict) and set(case) == CASE_KEYS, "case inventory drift")
        require(case["input"] == branch.record() and case["source_lane"] == source,
                "source/catalogue ordering drift")
        require(type(case["group_order"]) is int and 5 <= case["group_order"] <= 120
                and case["group_order"] % 5 == 0, "invalid group order")
        require(type(case["coset_budget"]) is int
                and case["coset_budget"] == case["group_order"] // 5, "coset budget drift")
        require(type(case["first_cumulative_full_layer"]) is int
                and 1 <= case["first_cumulative_full_layer"] <= case["coset_budget"],
                "cumulative saturation bound drift")
        require(isinstance(case["layers"], list) and len(case["layers"]) == MAX_RETURNS,
                "exact-layer range drift")
        for number, layer in enumerate(case["layers"], 1):
            require(isinstance(layer, dict) and set(layer) == {"returns", "exact", "cumulative"}
                    and type(layer["returns"]) is int and layer["returns"] == number,
                    "layer ordering drift")
            for name in ("exact", "cumulative"):
                row = layer[name]
                require(isinstance(row, dict) and set(row) == {
                    "terminal_count", "terminal_sha256", "survivor_counts", "survivor_sha256",
                }, "layer summary inventory drift")
                require(type(row["terminal_count"]) is int
                        and 0 < row["terminal_count"] <= case["group_order"], "terminal count drift")
                require(isinstance(row["survivor_counts"], list) and len(row["survivor_counts"]) == 10
                        and all(type(count) is int and 0 <= count <= 6
                                for count in row["survivor_counts"]), "survivor count drift")
                for key in ("terminal_sha256", "survivor_sha256"):
                    require(isinstance(row[key], str) and len(row[key]) == 64
                            and all(c in "0123456789abcdef" for c in row[key]), "invalid digest")
        witnesses = case["actual_terminal_witnesses"]
        require(isinstance(witnesses, list) and len(witnesses) == case["group_order"],
                "terminal witness coverage drift")
        previous = None
        for witness in witnesses:
            require(isinstance(witness, dict) and set(witness) == {"eta", "labels"},
                    "witness fields drift")
            eta, labels = witness["eta"], witness["labels"]
            require(isinstance(eta, list) and sorted(eta) == list(range(5))
                    and all(type(i) is int for i in eta), "invalid terminal permutation")
            require(previous is None or previous < eta, "duplicate/unordered terminal witness")
            previous = eta
            require(isinstance(labels, list) and 1 <= len(labels) <= case["coset_budget"]
                    and all(type(r) is int and 0 <= r < 5 * branch.g for r in labels),
                    "witness return-count/label drift")


def expected_matched_maps(g):
    return [{"pair_in_cyclic_order": [i, (i + 1) % 5],
             "survivor_label_order": [(i + j) % 5 for j in (2, 3, 4)],
             "at_most_one": {"reflection2": [[2 * g, 3 * g, 4 * g]],
                             "reflection1": [[4 * g, 3 * g, 2 * g]]},
             "at_most_two": [[2 * g, 3 * g, 4 * g], [4 * g, 3 * g, 2 * g]]}
            for i in range(5)]


def coordinate_table(branch):
    table = {}
    for lane, (destination, local) in enumerate(zip(branch.targets, branch.restrictions), 1):
        for index, image in enumerate(local):
            table[lane + index * branch.g] = destination + image * branch.g
    for index, image in enumerate(branch.punctured, 1):
        table[index * branch.g] = (image + 1) * branch.g
    require(set(table) == set(range(1, 5 * branch.g)) and set(table.values()) == set(table),
            "branch table is not a permutation on E")
    return table


def action(table, state, label, g):
    before = tuple((table[q] + label) % (5 * g) for q in state)
    after = tuple(g if q == 0 else q for q in before)
    return before, after


def generated_group(branch):
    identity = tuple(range(5))
    generators = [tuple((i + 1) % 5 for i in range(5)), *branch.restrictions]
    found, frontier = {identity}, {identity}
    while frontier:
        successor = {tuple(generator[q] for q in element)
                     for element in frontier for generator in generators} - found
        found |= successor
        frontier = successor
    return found


def summaries(elements, g):
    by_pair = []
    for pair in PAIRS:
        values = set()
        for eta in elements:
            if set(eta[i] for i in pair) == {0, 1}:
                values.add(tuple(g * eta[i] for i in range(5) if i not in pair))
        by_pair.append([list(pair), sorted(values)])
    return {"terminal_count": len(elements), "terminal_sha256": digest(sorted(elements)),
            "survivor_counts": [len(row[1]) for row in by_pair],
            "survivor_sha256": digest(by_pair)}


def raw_layers(branch, source):
    table = coordinate_table(branch)
    active = {tuple(source + i * branch.g for i in range(5))}
    cumulative, layers, cache = set(), [], {}
    for number in range(1, MAX_RETURNS + 1):
        exact, following = set(), set()
        for state in active:
            if state not in cache:
                internal, terminal = set(), set()
                for r in range(5 * branch.g):
                    before, after = action(table, state, r, branch.g)
                    if len(set(after)) == 5:
                        require(len({q % branch.g for q in after}) == 1
                                and after[0] % branch.g != 0, "ordinary confinement failed")
                        internal.add(after)
                    else:
                        require(len(set(after)) == 4
                                and set(before) == set(range(0, 5 * branch.g, branch.g)),
                                "strict event does not have the declared terminal support")
                        terminal.add(tuple(q // branch.g for q in before))
                cache[state] = internal, terminal
            internal, terminal = cache[state]
            following |= internal
            exact |= terminal
        cumulative |= exact
        layers.append({"returns": number, "exact": summaries(exact, branch.g),
                       "cumulative": summaries(cumulative, branch.g)})
        active = following
    return layers, cumulative, set(cache)


def replay_case(case, branch, source):
    group = generated_group(branch)
    raw, terminal, reachable = raw_layers(branch, source)
    require(terminal == group, "actual unbudgeted terminal/group mismatch")
    expected_reachable = {tuple(j + branch.g * eta[i] for i in range(5))
                          for j in range(1, branch.g) for eta in group}
    require(reachable == expected_reachable, "actual reachable injection/group mismatch")
    aggregate = {tuple((sigma[i] + k) % 5 for i in range(5))
                 for sigma in branch.restrictions for k in range(5)}
    initial = {tuple((branch.restrictions[source - 1][i] + k) % 5 for i in range(5))
               for k in range(5)}
    require(case["group_order"] == len(group) and case["group_sha256"] == digest(sorted(group))
            and case["aggregate_sha256"] == digest(sorted(aggregate))
            and case["initial_sha256"] == digest(sorted(initial)), "algebraic set summary drift")
    require(case["layers"] == raw, "exact/cumulative raw-injection layer mismatch")
    saturation = next(row["returns"] for row in raw if row["cumulative"]["terminal_count"] == len(group))
    require(case["first_cumulative_full_layer"] == saturation, "saturation-layer drift")
    table = coordinate_table(branch)
    witness_elements = set()
    for witness in case["actual_terminal_witnesses"]:
        state = tuple(source + i * branch.g for i in range(5))
        for index, label in enumerate(witness["labels"]):
            before, after = action(table, state, label, branch.g)
            if index + 1 == len(witness["labels"]):
                require(before == tuple(i * branch.g for i in witness["eta"])
                        and len(set(after)) == 4, "witness terminal placement mismatch")
            else:
                require(len(set(after)) == 5, "witness had an earlier strict event")
            state = after
        witness_elements.add(tuple(witness["eta"]))
    require(witness_elements == group, "actual witness coverage mismatch")
    return reachable


def replay(record):
    verify_shape(record)
    for case, (branch, source) in zip(record["cases"],
                                    [(b, s) for b in branches() for s in range(1, b.g)]):
        replay_case(case, branch, source)
    for control, g in zip(record["matched_controls"], MATCHED_G):
        states = [replay_case(case, branch, 1)
                  for case, branch in zip(control["cases"], matched_branches(g))]
        left, right = control["cases"]
        require(states[0] == states[1] and left["group_sha256"] == right["group_sha256"]
                and left["aggregate_sha256"] == right["aggregate_sha256"], "matched closure drift")
        require(left["layers"][0]["cumulative"]["survivor_sha256"]
                != right["layers"][0]["cumulative"]["survivor_sha256"], "first-layer separation lost")
        require(left["layers"][1]["cumulative"] == right["layers"][1]["cumulative"],
                "second-layer recovery lost")
        require(left["layers"][-1]["cumulative"] == right["layers"][-1]["cumulative"],
                "unbudgeted survivor equality lost")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="check fixed coverage only; skip raw replay")
    parser.add_argument("--result", type=Path, default=ROOT / RESULT_PATH)
    args = parser.parse_args()
    record = json.loads(args.result.read_text(encoding="utf-8"))
    if args.static:
        verify_shape(record)
        detail = "fixed coverage checked; finite replay skipped"
    else:
        replay(record)
        detail = "separately implemented bounded replay included"
    print(f"PASS: Paper XXXVIII return-budget control ({detail})")


if __name__ == "__main__":
    main()
