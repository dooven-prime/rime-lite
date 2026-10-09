#!/usr/bin/env python3
"""Produce algebraic layers and check constructed same-representative words."""

import argparse
import hashlib
import json
from pathlib import Path

from audit_scope import (
    BOUNDARY, IDENTITY, MATCHED_G, MAX_RETURNS, PAIRS, RESULT_PATH,
    SCHEMA, branches, matched_branches, scope_record,
)


ROOT = Path(__file__).resolve().parents[2]
PHASES = tuple(tuple((i + k) % 5 for i in range(5)) for k in range(5))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    return tuple(left[right[i]] for i in range(5))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"),
                                    sort_keys=True).encode("ascii")).hexdigest()


def closure(generators):
    known, queue = {IDENTITY}, [IDENTITY]
    for word in queue:
        for generator in generators:
            successor = multiply(generator, word)
            if successor not in known:
                known.add(successor)
                queue.append(successor)
    return known


def survivor_sets(elements, g):
    result = []
    for pair in PAIRS:
        survivors = [i for i in range(5) if i not in pair]
        maps = {tuple(eta[i] * g for i in survivors) for eta in elements
                if {eta[i] for i in pair} == {0, 1}}
        result.append([list(pair), sorted(maps)])
    return result


def layer_record(number, exact, cumulative, g):
    result = {"returns": number}
    for name, elements in (("exact", exact), ("cumulative", cumulative)):
        survivors = survivor_sets(elements, g)
        result[name] = {
            "terminal_count": len(elements), "terminal_sha256": fingerprint(sorted(elements)),
            "survivor_counts": [len(row[1]) for row in survivors],
            "survivor_sha256": fingerprint(survivors),
        }
    return result


def branch_image(branch, coordinate):
    lane, index = coordinate % branch.g, coordinate // branch.g
    if lane:
        return branch.targets[lane - 1] + branch.g * branch.restrictions[lane - 1][index]
    return branch.g * (1 + branch.punctured[index - 1])


def realize(branch, source, factors, eta):
    state = tuple(source + i * branch.g for i in range(5))
    labels = []
    for step, (lane, phase) in enumerate(factors):
        require(all(q % branch.g == lane for q in state), "factor uses the wrong actual lane")
        target = factors[step + 1][0] if step + 1 < len(factors) else 0
        label = (target - branch.targets[lane - 1] + phase * branch.g) % (5 * branch.g)
        before = tuple((branch_image(branch, q) + label) % (5 * branch.g) for q in state)
        after = tuple(branch.g if q == 0 else q for q in before)
        if step + 1 < len(factors):
            require(len(set(after)) == 5 and all(q % branch.g == target for q in after),
                    "constructed internal return is not guarded")
        else:
            require(before == tuple(branch.g * i for i in eta), "terminal placement drift")
            require(len(set(after)) == 4, "last return is not strict")
        state = after
        labels.append(label)
    return labels


def audit_case(branch, source):
    group = closure((PHASES[1], *branch.restrictions))
    factors = {}
    for j, sigma in enumerate(branch.restrictions, 1):
        for k, phase in enumerate(PHASES):
            factors.setdefault(multiply(phase, sigma), (j, k))
    exact = {multiply(phase, branch.restrictions[source - 1]): [(source, k)]
             for k, phase in enumerate(PHASES)}
    initial = set(exact)
    cumulative, witnesses, layers = set(), {}, []
    for number in range(1, MAX_RETURNS + 1):
        cumulative.update(exact)
        for eta, word in exact.items():
            if eta not in witnesses:
                labels = realize(branch, source, word, eta)
                witnesses[eta] = {"eta": list(eta), "labels": labels}
        layers.append(layer_record(number, set(exact), cumulative, branch.g))
        exact = {multiply(factor, eta): word + [choice]
                 for factor, choice in factors.items() for eta, word in exact.items()}
    q = len(group) // 5
    require(cumulative == group and len(witnesses) == len(group), "product saturation drift")
    require(all(len(w["labels"]) <= q for w in witnesses.values()), "at-most coset bound failed")
    saturation = next(row["returns"] for row in layers
                      if row["cumulative"]["terminal_count"] == len(group))
    for first, second in zip(layers, layers[1:]):
        size = first["cumulative"]["terminal_count"]
        require(size == len(group) or second["cumulative"]["terminal_count"] >= size + 5,
                "proper cumulative layer stalled")
    if all(sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5)) % 2
           for p in branch.restrictions):
        require(all(row["exact"]["terminal_count"] < len(group) for row in layers),
                "exact odd layers incorrectly treated as cumulative")
    return {
        "input": branch.record(), "source_lane": source, "group_order": len(group),
        "group_sha256": fingerprint(sorted(group)), "coset_budget": q,
        "aggregate_sha256": fingerprint(sorted(factors)),
        "initial_sha256": fingerprint(sorted(initial)),
        "first_cumulative_full_layer": saturation, "layers": layers,
        "actual_terminal_witnesses": [witnesses[eta] for eta in sorted(witnesses)],
    }


def matched_control(g):
    second, first = matched_branches(g)
    cases = [audit_case(branch, 1) for branch in (second, first)]
    h = set(PHASES)
    ht = {multiply(phase, first.restrictions[0]) for phase in PHASES}
    require(cases[0]["group_sha256"] == cases[1]["group_sha256"]
            and cases[0]["aggregate_sha256"] == cases[1]["aggregate_sha256"],
            "matched unbudgeted group/aggregate drift")
    expected = []
    for i in range(5):
        pair = {i, (i + 1) % 5}
        order = [(i + j) % 5 for j in (2, 3, 4)]
        plus = {tuple(g * eta[q] for q in order) for eta in h if {eta[q] for q in pair} == {0, 1}}
        minus = {tuple(g * eta[q] for q in order) for eta in ht if {eta[q] for q in pair} == {0, 1}}
        require(plus == {(2 * g, 3 * g, 4 * g)} and minus == {(4 * g, 3 * g, 2 * g)},
                "matched source-addressed maps drift")
        expected.append({"pair_in_cyclic_order": [i, (i + 1) % 5],
                         "survivor_label_order": order,
                         "at_most_one": {"reflection2": sorted(plus), "reflection1": sorted(minus)},
                         "at_most_two": sorted(plus | minus)})
    require(cases[0]["layers"][1]["cumulative"] == cases[1]["layers"][1]["cumulative"],
            "second-layer recovery failed")
    return {"g": g, "cases": cases, "consecutive_pair_controls": expected}


def produce():
    return {
        "schema": SCHEMA, "status": "BOUNDED_CONSISTENCY_CONTROL",
        "claim_boundary": BOUNDARY, "scope": scope_record(),
        "cases": [audit_case(branch, source) for branch in branches() for source in range(1, branch.g)],
        "matched_controls": [matched_control(g) for g in MATCHED_G],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / RESULT_PATH)
    args = parser.parse_args()
    record = produce()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n",
                           encoding="utf-8", newline="\n")
    print(f"PASS: produced {len(record['cases'])} bounded source cases and 3 matched controls")


if __name__ == "__main__":
    main()
