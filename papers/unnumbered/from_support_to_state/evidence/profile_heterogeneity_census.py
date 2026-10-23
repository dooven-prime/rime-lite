"""Exact unit-source profile census on the two retained annotation partitions.

--build creates a new result (refuses overwrite). The default replays it.
No trajectories, floating-point grouping, or learned predictors are used.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import sys

import numpy as np
import pandas as pd

import somaside_exact_witness as source


HERE = Path(__file__).resolve().parent
DEFAULT_RESULT = HERE / "profile_heterogeneity_census.v1.json"
D22 = source.SOURCE / "digital_fly_v0_2/results/d2_2_memory_closure_v0_2.json"
PARTITIONS = ("somaSide", "superclass")


def choose_two(n: int) -> int:
    return n * (n - 1) // 2


def accumulate(rows, cols, weights, signs, codes, node_count, coordinate_count):
    """Use int64 only after proving an upper bound on every partial sum."""
    rows, cols, weights = (np.asarray(a) for a in (rows, cols, weights))
    source.require(all(np.issubdtype(a.dtype, np.integer) for a in (rows, cols, weights)),
                   "carrier arrays must be integers")
    source.require(len(rows) == len(cols) == len(weights), "edge lengths")
    source.require(not len(rows) or
                   (int(rows.min()) >= 0 and int(rows.max()) < node_count and
                    int(cols.min()) >= 0 and int(cols.max()) < node_count and
                    int(weights.min()) > 0), "edge bounds/counts")
    bound = int(weights.max(initial=0)) * int(len(weights))
    source.require(bound <= np.iinfo(np.int64).max, "unsafe int64 accumulation")
    known = signs[rows] != 0
    positive = signs[rows] > 0
    mass = np.zeros(node_count, dtype=np.int64)
    numerators = np.zeros((node_count, coordinate_count), dtype=np.int64)
    np.add.at(mass, rows[known], weights[known])
    np.add.at(numerators, (rows[positive], codes[cols[positive]]), weights[positive])
    return mass, numerators, {
        "accumulator": "int64",
        "arithmetic_bound": "edge_count_times_max_positive_weight",
        "edge_count": int(len(weights)),
        "max_weight": int(weights.max(initial=0)),
        "partial_sum_upper_bound": bound,
        "int64_max": int(np.iinfo(np.int64).max),
        "later_pair_counts_and_cross_products": "Python_bigint",
    }


def raw_operator_digest(rows, cols, weights, signs, node_count):
    """Reproduce the published raw operator identity in bounded chunks."""
    known_count = int(np.count_nonzero(signs[rows]))
    digest = hashlib.sha256()
    digest.update(np.asarray((node_count, node_count), dtype=np.int64).tobytes())
    for name in ("row", "col", "value"):
        digest.update(b"int64")
        digest.update(np.asarray((known_count,), dtype=np.int64).tobytes())
        for start in range(0, len(rows), 1_000_000):
            stop = start + 1_000_000
            r = rows[start:stop]
            keep = signs[r] != 0
            if name == "row":
                values = r[keep].astype(np.int64)
            elif name == "col":
                values = cols[start:stop][keep].astype(np.int64)
            else:
                values = weights[start:stop][keep].astype(np.int64)
                values *= signs[r[keep]].astype(np.int64)
            digest.update(np.ascontiguousarray(values).tobytes())
    return digest.hexdigest(), known_count


def unique_count(keys, coordinates):
    columns = [0] + [j + 1 for j in coordinates]
    return int(len(np.unique(keys[:, columns], axis=0)))


def separation_scope(keys, representatives, eligible, body_ids, labels):
    """Separate pairwise witnesses from a dataset-wide coordinate selection."""
    m, target = len(labels), len(keys)
    mandatory, witnesses = [], []
    for j in range(m):
        columns = [0] + [k + 1 for k in range(m) if k != j]
        _, inverse, counts = np.unique(keys[:, columns], axis=0,
                                       return_inverse=True, return_counts=True)
        duplicates = np.flatnonzero(counts > 1)
        if len(duplicates):
            mandatory.append(j)
            pair = np.flatnonzero(inverse == duplicates[0])[:2]
            sources = [int(eligible[int(representatives[k])]) for k in pair]
            witnesses.append({
                "coordinate": labels[j],
                "source_sector": labels[int(keys[int(pair[0]), 0])],
                "source_indices": sources,
                "body_ids": [int(body_ids[a]) for a in sources],
                "all_other_coordinates_equal": True,
            })
    lower = max(len(mandatory), int(target > len(np.unique(keys[:, 0]))))
    if m <= 8:
        minima = []
        for size in range(m + 1):
            for selection in combinations(range(m), size):
                if unique_count(keys, selection) == target:
                    minima.append([labels[j] for j in selection])
            if minima:
                break
        return {
            "status": "EXACT_BY_EXHAUSTIVE_SUBSETS",
            "minimum_coordinate_count": size,
            "minimum_coordinate_sets": minima,
            "mandatory_coordinates": [labels[j] for j in mandatory],
            "mandatory_witnesses": witnesses,
            "lower_bound": size, "upper_bound": size,
            "scope": "all_profile_classes_within_each_observed_source_sector",
        }
    selection = list(range(m))
    for j in range(m):
        if j not in mandatory:
            trial = [k for k in selection if k != j]
            if unique_count(keys, trial) == target:
                selection = trial
    exact = len(selection) == lower
    return {
        "status": "EXACT_BY_MATCHING_BOUNDS" if exact else "BOUNDED_NOT_SOLVED",
        "minimum_coordinate_count": len(selection) if exact else None,
        "mandatory_coordinates": [labels[j] for j in mandatory],
        "mandatory_witnesses": witnesses,
        "lower_bound": lower, "upper_bound": len(selection),
        "sufficient_coordinate_set": [labels[j] for j in selection],
        "selection_rule": "delete_nonmandatory_coordinates_in_declared_label_order",
        "scope": "all_profile_classes_within_each_observed_source_sector",
    }


def census(mass, numerators, source_codes, labels, body_ids):
    eligible = np.flatnonzero(mass > 0)
    s, p, sectors = mass[eligible], numerators[eligible], source_codes[eligible]
    source.require(len(eligible) > 0, "empty eligible domain")
    common = np.gcd(s, np.gcd.reduce(p, axis=1))
    canonical = np.column_stack((eligible, sectors, s // common, p // common[:, None]))
    canonical = np.ascontiguousarray(canonical, dtype="<i8")
    digest = hashlib.sha256()
    digest.update(b"source_index,source_sector,reduced_denominator,reduced_numerators;<i8")
    digest.update(np.asarray(canonical.shape, dtype="<i8").tobytes())
    digest.update(canonical.tobytes())
    coordinate_ids = np.empty_like(p, dtype=np.int64)
    for j in range(len(labels)):
        g = np.gcd(p[:, j], s)
        exact_values = np.column_stack((p[:, j] // g, s // g))
        _, coordinate_ids[:, j] = np.unique(exact_values, axis=0, return_inverse=True)
    full_keys, representative, class_counts = np.unique(
        np.column_stack((sectors, coordinate_ids)), axis=0,
        return_index=True, return_counts=True)
    by_sector = []
    totals = [0] * len(labels)
    split_sectors = [0] * len(labels)
    all_pairs, unequal_profile_pairs = 0, 0
    for i, label in enumerate(labels):
        local = np.flatnonzero(sectors == i)
        n = int(len(local))
        counts = class_counts[full_keys[:, 0] == i]
        pair_count = choose_two(n)
        profile_pairs = pair_count - sum(choose_two(int(c)) for c in counts)
        all_pairs += pair_count
        unequal_profile_pairs += profile_pairs
        columns = []
        for j, target_label in enumerate(labels):
            _, value_counts = np.unique(coordinate_ids[local, j], return_counts=True)
            different = pair_count - sum(choose_two(int(c)) for c in value_counts)
            totals[j] += different
            split_sectors[j] += int(len(value_counts) > 1)
            columns.append({
                "target_sector": target_label,
                "distinct_exact_coordinate_values": int(len(value_counts)),
                "separated_unordered_source_pairs": different,
            })
        by_sector.append({
            "source_sector": label,
            "eligible_sources": n,
            "exact_profile_classes": int(len(counts)),
            "largest_profile_class_sources": int(max(counts, default=0)),
            "singleton_profile_classes": int(np.count_nonzero(counts == 1)),
            "collision_profile_classes": int(np.count_nonzero(counts > 1)),
            "sources_in_collision_profile_classes": sum(int(c) for c in counts if c > 1),
            "zero_profile_sources": int(np.count_nonzero(~np.any(p[local], axis=1))),
            "unordered_same_observation_source_pairs": pair_count,
            "unequal_profile_source_pairs": profile_pairs,
            "coordinates": columns,
        })
    output = {
        "labels": labels,
        "eligible_sources": int(len(eligible)),
        "profile_classes_with_source_sector_retained": int(len(full_keys)),
        "collision_profile_classes": int(np.count_nonzero(class_counts > 1)),
        "sources_in_collision_profile_classes": sum(int(c) for c in class_counts if c > 1),
        "canonical_profile_assignment_sha256": digest.hexdigest(),
        "profile_key": "(source_sector,s/g,p_1/g,...,p_m/g); g=gcd(s,p_1,...,p_m)",
        "by_source_sector": by_sector,
        "largest_observation_fiber": max(by_sector, key=lambda x: x["eligible_sources"])["source_sector"],
        "all_unordered_same_observation_source_pairs": all_pairs,
        "all_unequal_profile_source_pairs": unequal_profile_pairs,
        "target_coordinate_splits": [{
            "target_sector": label,
            "source_sectors_split": split_sectors[j],
            "separated_unordered_source_pairs": totals[j],
            "denominator_all_same_observation_source_pairs": all_pairs,
        } for j, label in enumerate(labels)],
        "coordinate_separation": separation_scope(
            full_keys, representative, eligible, body_ids, labels),
    }
    source.require(all(n <= unequal_profile_pairs for n in totals), "coordinate/pair scope")
    source.require(sum(totals) >= unequal_profile_pairs, "missing profile difference")
    source.require(sum(r["eligible_sources"] for r in by_sector) == len(eligible),
                   "source coverage")
    return output


def compute(carrier_dir):
    for name, expected in source.PINNED_FILES.items():
        source.require(source.digest(carrier_dir / name) == expected, f"carrier digest: {name}")
    d22 = json.loads(D22.read_text(encoding="utf-8"))
    nodes = pd.read_parquet(carrier_dir / "carrier_v0_nodes.parquet")
    n = len(nodes)
    body_ids = nodes["bodyId"].to_numpy()
    signs = np.asarray([source.SIGN_MAP.get(str(label), 0)
                        for label in nodes["consensus_nt"]], dtype=np.int8)
    results = {}
    with np.load(carrier_dir / "carrier_v0_edges.npz", allow_pickle=False) as edges:
        rows, cols, weights = (edges[name] for name in ("row", "col", "weight"))
        raw_digest, edge_count = raw_operator_digest(rows, cols, weights, signs, n)
        source.require(raw_digest == d22["operator_hashes"]["Y_known_pm"]["raw"],
                       "published signed raw-operator digest")
        for field in PARTITIONS:
            print(f"Computing exact {field} profiles", file=sys.stderr, flush=True)
            values = nodes[field].astype("string").fillna("<missing>").astype(str)
            labels = sorted(values.unique().tolist())
            lookup = {label: i for i, label in enumerate(labels)}
            codes = np.asarray([lookup[value] for value in values], dtype=np.int64)
            mass, numerators, bound = accumulate(rows, cols, weights, signs, codes, n, len(labels))
            results[field] = census(mass, numerators, codes, labels, body_ids)
            results[field]["full_observation_sector_sizes"] = dict(sorted(Counter(values).items()))
            results[field]["arithmetic_bound"] = bound
    old = d22["candidate_surface"]
    current = results["superclass"]
    checks = {
        "eligible_sources": (current["eligible_sources"], old["nonzero_outgoing_rows"]),
        "profile_classes": (current["profile_classes_with_source_sector_retained"],
                            old["exact_history_signature_groups"]),
        "collision_classes": (current["collision_profile_classes"],
                              old["collision_groups_with_at_least_two_states"]),
        "collision_sources": (current["sources_in_collision_profile_classes"],
                              old["states_in_collision_groups"]),
    }
    source.require(all(a == b for a, b in checks.values()), "old D2.2 consistency")
    return {
        "format": "from-support-to-state.profile-heterogeneity.v1",
        "model": source.MODEL,
        "domain": "all_eligible_unit_sources_of_Y_known_pm",
        "source_nodes": n,
        "known_sign_edges": edge_count,
        "carrier_sha256": source.PINNED_FILES,
        "signed_raw_operator_sha256": raw_digest,
        "source_metadata": {"path": D22.relative_to(source.REPO).as_posix(),
                            "checkout_sha256": source.digest(D22)},
        "implementation_sha256": {
            Path(__file__).name: source.digest(Path(__file__)),
            "somaside_exact_witness.py": source.digest(Path(source.__file__)),
        },
        "prior_total_consistency": {k: {"current": a, "published": b, "equal": a == b}
                                   for k, (a, b) in checks.items()},
        "novel_slice": "per_source_sector_multiplicity_and_target_coordinate_separation",
        "boundaries": [
            "Counts are finite-domain class/pair counts, not bits or population estimates.",
            "A pairwise mismatch needs one differing coordinate; separating all classes is a different task.",
            "Source-weighted pair counts overlap across target coordinates.",
            "Replay uses the same implementation and is not independent replication.",
            "No trajectories or later-time closure are computed.",
        ],
        "partitions": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--carrier-dir", type=Path, default=source.DEFAULT_CARRIER)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    if args.build:
        source.require(not args.result.exists(), "refusing to overwrite an existing result")
    result = compute(args.carrier_dir)
    if args.build:
        with args.result.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=True)
            handle.write("\n")
    else:
        recorded = json.loads(args.result.read_text(encoding="utf-8"))
        source.require(json.dumps(recorded, sort_keys=True) == json.dumps(result, sort_keys=True),
                       "source replay differs from saved census")
    print(json.dumps({
        "status": "PASS",
        "mode": "BUILD" if args.build else "FULL_CENSUS_SOURCE_REPLAY",
        "eligible_sources": result["partitions"]["somaSide"]["eligible_sources"],
        "profile_classes": {k: v["profile_classes_with_source_sector_retained"]
                            for k, v in result["partitions"].items()},
    }))


if __name__ == "__main__":
    main()
