"""Cross-check separately written log, forest, and abstract UFE transitions."""

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import forest
import log_consumer as log
import placed_ufe as ufe
from audit_scope import BOUNDARY, RESULT, cases
from contract import Environment, primitive, require

ROOT = Path(__file__).resolve().parents[2]


def encoded(value):
    return json.dumps(primitive(value), sort_keys=True, separators=(",", ":")).encode("ascii")


def all_blocks(size):
    return tuple(frozenset(i for i in range(size) if mask & (1 << i))
                 for mask in range(1, 1 << size))


def check_snapshot(env, history, state, adapter, counts):
    forest.check_wellformed(env, state)
    require(history.partition == forest.project(state) == ufe.project(adapter), "packet mismatch")
    require(state == ufe.to_forest(env, adapter), "full forest/marker correspondence failed")
    require(len(history.events) == len(adapter.unions) <= len(env.seed) - 1, "fusion budget failed")
    summaries = []
    for selected in all_blocks(len(env.seed)):
        expected = log.decode(history, selected)
        require(expected == forest.decode(state, selected) == ufe.decode(env, adapter, selected),
                "registration/read mismatch")
        counts["registration_queries"] += 1
        if expected is not None:
            counts["registered_invocations"] += 1
            summaries.append(expected)
            partners = frozenset()
            for record in expected.absorptions:
                require(partners.isdisjoint(record.partner) and selected.isdisjoint(record.partner),
                        "partners are not pairwise disjoint")
                partners |= record.partner
            require(expected.carrier[1] == selected | partners
                    and len(expected.absorptions) <= len(env.seed) - len(selected), "absorption bound failed")
            counts["max_absorptions"] = max(counts["max_absorptions"], len(expected.absorptions))
        for letter in ("p", "d"):
            for kind in ("Carry", "Absorb"):
                consumer_next = log.command(env, expected, kind, letter)
                forest_next = forest.command(env, state, selected, kind, letter)
                ufe_next = ufe.command(env, adapter, selected, kind, letter)
                require((consumer_next is None) == (forest_next is None) == (ufe_next is None),
                        "command domain reflection failed")
                counts["command_queries"] += 1
                if consumer_next is None:
                    continue
                counts["legal_commands"] += 1
                next_history = log.step(env, history, letter)
                require(consumer_next == log.decode(next_history, selected)
                        == forest.decode(forest_next, selected) == ufe.decode(env, ufe_next, selected),
                        "complete successor commutation failed")
                require(forest_next == ufe.to_forest(env, ufe_next), "next full forest mismatch")
                if kind == "Absorb":
                    counts["absorb_commands"] += 1
                elif len(next_history.events) > len(history.events):
                    counts["carry_with_unrelated_fusion"] += 1
    counts["histories"] += 1
    return summaries


def check_renaming(env, state, adapter):
    permutation = tuple(reversed(range(len(env.seed))))
    seed = [None] * len(env.seed)
    for old, new in enumerate(permutation):
        seed[new] = env.seed[old]
    renamed_env = Environment(env.defect, tuple(seed), tuple(permutation[x] for x in env.enumeration))
    renamed_state, renamed_adapter = forest.rename(state, permutation), ufe.rename(adapter, permutation)
    require(ufe.to_forest(renamed_env, renamed_adapter) == renamed_state, "renamed decoder mismatch")
    for letter in ("p", "d"):
        require(forest.step(renamed_env, renamed_state, letter)
                == forest.rename(forest.step(env, state, letter), permutation), "forest handoff failed")
        require(ufe.step(renamed_env, renamed_adapter, letter)
                == ufe.rename(ufe.step(env, adapter, letter), permutation), "ordered UFE handoff failed")
        for selected in all_blocks(len(env.seed)):
            target = frozenset(permutation[x] for x in selected)
            summary = log_summary = forest.decode(state, selected)
            if summary is not None:
                def block_map(block):
                    return frozenset(permutation[x] for x in block)
                origin = replace(summary.origin, parents=tuple((q, block_map(b)) for q, b in summary.origin.parents))
                records = tuple(replace(record, carrier=block_map(record.carrier),
                                        partner=block_map(record.partner), merged=block_map(record.merged))
                                for record in summary.absorptions)
                log_summary = replace(summary, partition=tuple((q, block_map(b)) for q, b in summary.partition),
                                      selected=target, origin=origin, absorptions=records)
            require(log_summary == forest.decode(renamed_state, target)
                    == ufe.decode(renamed_env, renamed_adapter, target), "renamed consumer reads failed")
            for kind in ("Carry", "Absorb"):
                before = forest.command(env, state, selected, kind, letter)
                after = forest.command(renamed_env, renamed_state, target, kind, letter)
                require((before is None and after is None)
                        or (before is not None and forest.rename(before, permutation) == after),
                        "renamed command failed")


def run_word(env, word):
    history, state, adapter = log.initial(env), forest.initial(env), ufe.initial(env)
    for letter in word:
        history, state, adapter = (log.step(env, history, letter), forest.step(env, state, letter),
                                   ufe.step(env, adapter, letter))
    return history, state, adapter


def worked_examples():
    three = Environment((0, 2, 0), (0, 1, 2), (0, 1, 2))
    selected = frozenset(range(3))
    h1, f1, _ = run_word(three, "dd")
    h2, f2, _ = run_word(three, "pdd")
    s1, s2 = log.decode(h1, selected), log.decode(h2, selected)
    require(h1.partition == h2.partition and s1.carrier == s2.carrier
            and s1.absorptions == s2.absorptions == () and s1.origin != s2.origin,
            "origin non-descent control failed")
    seven = Environment((0, 3, 2, 5, 1, 4, 0), tuple(range(7)), tuple(range(7)))
    chosen = frozenset({3, 5})
    rows = []
    for word in ("dppd", "dppdppd", "dppdppdpppppd"):
        history, state, adapter = run_word(seven, word)
        check_snapshot(seven, history, state, adapter, Counter())
        summary = forest.decode(state, chosen)
        rows.append({"word": word, "forest": primitive(state), "ufe": primitive(adapter),
                     "consumer": primitive(summary)})
    require(rows[1]["forest"]["marker"] == [1, 4]
            and rows[1]["consumer"]["selected"] == [3, 5]
            and not rows[1]["consumer"]["absorptions"], "unrelated Carry fusion failed")
    require(rows[2]["consumer"]["partition"] == [[0, [0, 3, 5, 6]], [4, [1, 4]], [5, [2]]],
            "seven-state endpoint mismatch")
    require(len(rows[2]["consumer"]["absorptions"]) == 1, "selected absorption missing")
    _, middle, mid_ufe = run_word(seven, "dppdppd")
    eta = (0, 2, 1, 3, 4, 5, 6)
    renamed_seed = tuple(eta.index(i) for i in range(7))
    renamed_env = Environment(seven.defect, renamed_seed, eta)
    left, left_ufe = forest.rename(middle, eta), ufe.rename(mid_ufe, eta)
    for letter in "pppppd":
        left = forest.step(renamed_env, left, letter)
        left_ufe = ufe.step(renamed_env, left_ufe, letter)
    _, final, _ = run_word(seven, "dppdppdpppppd")
    require(left == forest.rename(final, eta) == ufe.to_forest(renamed_env, left_ufe),
            "nonidentity same-invocation continuation failed")
    return {"origin_non_descent": {"words": ["dd", "pdd"], "first": primitive(s1), "second": primitive(s2),
                                   "forests_differ": f1 != f2},
            "seven_state": rows, "renamed_final": primitive(left)}


def audit_case(case):
    env, depth = case["environment"], case["max_word_length"]
    counts = Counter({key: 0 for key in (
        "histories", "registration_queries", "registered_invocations", "command_queries",
        "legal_commands", "max_absorptions", "absorb_commands", "carry_with_unrelated_fusion")})
    fingerprint = hashlib.sha256()

    def visit(word, history, state, adapter):
        summaries = check_snapshot(env, history, state, adapter, counts)
        fingerprint.update(encoded([word, history, state, adapter, summaries]) + b"\n")
        if len(word) < depth:
            for letter in ("p", "d"):
                visit(word + letter, log.step(env, history, letter), forest.step(env, state, letter),
                      ufe.step(env, adapter, letter))

    visit("", log.initial(env), forest.initial(env), ufe.initial(env))
    _, state, adapter = run_word(env, "d" * depth)
    check_renaming(env, state, adapter)
    require(counts["histories"] == 2 ** (depth + 1) - 1, "word range narrowed")
    return {"id": case["id"], "environment": primitive(env), "max_word_length": depth,
            "counts": dict(sorted(counts.items())), "full_trace_sha256": fingerprint.hexdigest(),
            "atom_renaming": "PASS"}


def build_report(progress=False):
    catalogue = list(cases())
    require(len(catalogue) == 464 and len({case["id"] for case in catalogue}) == 464, "fixed case scope drift")
    rows = []
    for i, case in enumerate(catalogue, 1):
        rows.append(audit_case(case))
        if progress and (i % 50 == 0 or i == len(catalogue)):
            print(f"replayed {i}/{len(catalogue)} fixed cases", flush=True)
    totals = Counter()
    for row in rows:
        for key, value in row["counts"].items():
            if key == "max_absorptions":
                totals[key] = max(totals[key], value)
            else:
                totals[key] += value
    return {"schema": "rime.paper39.consumer-audit.v1", "boundary": BOUNDARY,
            "cases": rows, "totals": dict(sorted(totals.items())), "examples": worked_examples()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / RESULT)
    args = parser.parse_args()
    report = build_report(progress=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii"))
    print("PASS: bounded three-model replay saved; no all-N or release certification")


if __name__ == "__main__":
    main()
