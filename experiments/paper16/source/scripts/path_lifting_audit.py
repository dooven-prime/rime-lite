#!/usr/bin/env python3
"""Audit whether superclass depth-2 routes lift to real body chains.

The sector graph only records existential edges. This audit compares those
macro triples with triples witnessed by a shared concrete middle body. The
``<unannotated>`` label is retained for coverage, but is never allowed to act
as a relay in the strict typed result.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.ipc as ipc

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
WEIGHTS = DATA / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
ANNOTATIONS = DATA / "body-annotations-male-cns-v1.0-minconf-0.5.feather"


def label(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "<missing>"
    text = str(value).strip()
    return text if text and text.lower() != "nan" else "<missing>"


def run(limit: int | None, sector_field: str = "superclass") -> dict:
    annotations = pd.read_feather(ANNOTATIONS, columns=["bodyId", sector_field])
    sectors = dict(zip(annotations["bodyId"].astype("int64"), annotations[sector_field].map(label)))
    annotated_ids = set(sectors)

    # First pass: body IDs that can serve as a concrete middle node (have an
    # outgoing edge). This avoids retaining the many terminal post IDs.
    source = pa.memory_map(str(WEIGHTS), "r")
    reader = ipc.open_file(source)
    pre_ids: set[int] = set()
    raw_rows = 0
    try:
        for index in range(reader.num_record_batches):
            if limit is not None and raw_rows >= limit:
                break
            batch = reader.get_batch(index)
            remaining = None if limit is None else limit - raw_rows
            pre = batch.column("body_pre").to_numpy(zero_copy_only=False)
            if remaining is not None:
                pre = pre[:remaining]
            raw_rows += len(pre)
            pre_ids.update(int(x) for x in np.unique(pre).tolist())
    finally:
        source.close()

    # For every middle body, retain bit masks of observed incoming/outgoing
    # superclass labels. A second pass is needed because post IDs can precede
    # their first outgoing row in the release ordering.
    incoming: dict[int, int] = defaultdict(int)
    outgoing: dict[int, int] = defaultdict(int)
    sector_names = sorted(set(sectors.values()) | {"<unannotated>"})
    sector_index = {name: bit for bit, name in enumerate(sector_names)}
    source = pa.memory_map(str(WEIGHTS), "r")
    reader = ipc.open_file(source)
    scanned = 0
    try:
        for index in range(reader.num_record_batches):
            if limit is not None and scanned >= limit:
                break
            batch = reader.get_batch(index)
            remaining = None if limit is None else limit - scanned
            pre = batch.column("body_pre").to_numpy(zero_copy_only=False)
            post = batch.column("body_post").to_numpy(zero_copy_only=False)
            if remaining is not None:
                pre, post = pre[:remaining], post[:remaining]
            scanned += len(pre)
            for a, b in zip(pre.tolist(), post.tolist()):
                a_id, b_id = int(a), int(b)
                middle_sector = sectors.get(b_id, "<unannotated>")
                source_sector = sectors.get(a_id, "<unannotated>")
                if b_id in pre_ids:
                    incoming[b_id] |= 1 << sector_index[source_sector]
                outgoing[a_id] |= 1 << sector_index[middle_sector]
    finally:
        source.close()

    # Count concrete middle-body witnesses, not just their Boolean support.
    # A body contributes once to a triple when it has at least one incoming
    # edge from the source sector and at least one outgoing edge to the target
    # sector. This is the multiplicity of projected-route witnesses, not a
    # synapse count or a reliability estimate.
    witness_counts: Counter[tuple[str, str, str]] = Counter()
    for middle, mask in incoming.items():
        middle_sector = sectors.get(middle, "<unannotated>")
        for source_sector, source_bit in sector_index.items():
            if mask & (1 << source_bit):
                for middle_target, target_bit in sector_index.items():
                    if outgoing.get(middle, 0) & (1 << target_bit):
                        witness_counts[(source_sector, middle_sector, middle_target)] += 1
    support = set(witness_counts)

    # M uses the same existential support semantics as the sector carrier.
    macro_edges = set()
    # Recover support directly from body rows to avoid dependence on a prior
    # aggregate scope; only rows in this audit scope are considered.
    source = pa.memory_map(str(WEIGHTS), "r")
    reader = ipc.open_file(source)
    scanned = 0
    try:
        for index in range(reader.num_record_batches):
            if limit is not None and scanned >= limit:
                break
            batch = reader.get_batch(index)
            remaining = None if limit is None else limit - scanned
            pre = batch.column("body_pre").to_numpy(zero_copy_only=False)
            post = batch.column("body_post").to_numpy(zero_copy_only=False)
            if remaining is not None:
                pre, post = pre[:remaining], post[:remaining]
            scanned += len(pre)
            macro_edges.update((sectors.get(int(a), "<unannotated>"), sectors.get(int(b), "<unannotated>")) for a, b in zip(pre.tolist(), post.tolist()))
    finally:
        source.close()

    macro_triples = {(a, b, c) for a, b in macro_edges for x, c in macro_edges if x == b}
    typed_core_macro = {triple for triple in macro_triples if "<unannotated>" not in triple}
    typed_core_lifted = {triple for triple in support if "<unannotated>" not in triple}
    relay_strict_macro = {triple for triple in macro_triples if triple[1] != "<unannotated>"}
    relay_strict_lifted = {triple for triple in support if triple[1] != "<unannotated>"}
    inclusive_lifted = set(support)

    def pair_depth_payload(macro_edges, macro, lifted):
        """Compare quotient and witnessed distances through depth two only."""
        adjacency: dict[str, set[str]] = defaultdict(set)
        sectors_seen: set[str] = set()
        for source_sector, target_sector in macro_edges:
            adjacency[source_sector].add(target_sector)
            sectors_seen.update((source_sector, target_sector))
        distances: dict[tuple[str, str], int] = {}
        for source_sector in sectors_seen:
            seen = {source_sector: 0}
            queue = [source_sector]
            for current in queue:
                for target in adjacency.get(current, ()):
                    if target not in seen:
                        seen[target] = seen[current] + 1
                        queue.append(target)
            distances.update({(source_sector, target): depth for target, depth in seen.items() if target != source_sector})

        direct = {(source_sector, target_sector) for source_sector, target_sector in macro_edges}
        witnessed_two = {(source_sector, target_sector) for source_sector, _, target_sector in lifted}
        eligible = {pair for pair, depth in distances.items() if depth <= 2}
        quotient_hist = Counter(distances[pair] for pair in eligible)
        route_at_cutoff: dict[tuple[str, str], int | str] = {}
        for pair in eligible:
            if pair in direct:
                route_at_cutoff[pair] = 1
            elif pair in witnessed_two:
                route_at_cutoff[pair] = 2
            else:
                route_at_cutoff[pair] = "UNREACHED_AT_CUTOFF"
        route_hist = Counter(str(value) for value in route_at_cutoff.values())
        deltas = Counter()
        for pair, quotient_depth in ((pair, distances[pair]) for pair in eligible):
            route_depth = route_at_cutoff[pair]
            if isinstance(route_depth, int):
                deltas[str(route_depth - quotient_depth)] += 1
        return {
            "cutoff_depth": 2,
            "eligible_quotient_pairs": len(eligible),
            "quotient_distance_histogram": dict(sorted((str(k), v) for k, v in quotient_hist.items())),
            "route_distance_at_cutoff_histogram": dict(sorted(route_hist.items())),
            "delta_histogram_for_resolved_pairs": dict(sorted(deltas.items())),
            "unreached_at_cutoff_pairs": sum(value == "UNREACHED_AT_CUTOFF" for value in route_at_cutoff.values()),
            "semantics": "direct body-level edges count as depth 1; depth 2 requires a shared concrete middle body; larger microscopic depths are not computed",
        }

    def payload(macro, lifted, rule):
        lifted_intersection = lifted & macro
        multiplicity_records = [
            {
                "source_sector": source_sector,
                "relay_sector": relay_sector,
                "target_sector": target_sector,
                "witness_multiplicity": witness_counts.get((source_sector, relay_sector, target_sector), 0),
            }
            for source_sector, relay_sector, target_sector in sorted(macro)
        ]
        multiplicities = [record["witness_multiplicity"] for record in multiplicity_records]
        return {
            "macro_triple_count": len(macro),
            "lifted_triple_count": len(lifted_intersection),
            "lift_precision_2": (len(lifted_intersection) / len(macro) if macro else None),
            "nonliftable_macro_triple_count": len(macro - lifted),
            "nonliftable_macro_fraction": (len(macro - lifted) / len(macro) if macro else None),
            "nonliftable_macro_examples": [list(x) for x in sorted(macro - lifted)[:100]],
            "universe_rule": rule,
            "witness_multiplicity": multiplicity_records,
            "witness_multiplicity_summary": {
                "triple_count": len(multiplicities),
                "positive_count": sum(value > 0 for value in multiplicities),
                "minimum": min(multiplicities) if multiplicities else None,
                "maximum": max(multiplicities) if multiplicities else None,
                "mean": (sum(multiplicities) / len(multiplicities)) if multiplicities else None,
            },
        }

    return {
        "scope": {"mode": "full" if limit is None else "deterministic_prefix", "rows_scanned": raw_rows},
        "universe": {"annotated_body_ids": len(annotated_ids), "candidate_middle_bodies": len(pre_ids), "sector_field": sector_field, "sector_count_including_missing": len(sector_names)},
        "typed_core": payload(typed_core_macro, typed_core_lifted, "exclude <unannotated> from source, relay, and target"),
        "relay_strict": payload(relay_strict_macro, relay_strict_lifted, "allow boundary <unannotated> endpoints but exclude <unannotated> as relay"),
        "coverage_inclusive": payload(macro_triples, inclusive_lifted, "retain every release-native label, including concrete bodies grouped as <unannotated>"),
        "pair_depth_discrepancy": {
            "typed_core": pair_depth_payload({(a, b) for a, b in macro_edges if "<unannotated>" not in (a, b)}, typed_core_macro, typed_core_lifted),
            "relay_strict": pair_depth_payload({(a, b) for a, b in macro_edges if b != "<unannotated>"}, relay_strict_macro, relay_strict_lifted),
            "coverage_inclusive": pair_depth_payload(macro_edges, macro_triples, inclusive_lifted),
        },
        "semantics": {
            "M_ijk": "A_ij > 0 and A_jk > 0 in the observed sector support",
            "L_ijk": "exists one concrete middle body with an incoming i edge and outgoing k edge",
            "Path_2_quotient": "Boolean support of the sector product A^2; existential edges may use different concrete middle bodies",
            "Route_2[Y_MaleCNS]": "support of the projected product Q_k Y_MaleCNS Q_j Y_MaleCNS Q_i; for the declared nonnegative node-basis carrier this is witnessed by one concrete middle body v",
            "D_quotient_support": "shortest directed-path distance on the sector support graph; this is the quantity formerly labelled D_route in the baseline aggregate",
            "D_route[Y_MaleCNS]": "only a depth-2 cutoff comparison is computed here; larger depths are UNREACHED_AT_CUTOFF rather than infinity",
            "descent_claim": "A sector path does not imply a liftable microscopic path without a shared-intermediate witness or an explicit lumpability theorem",
            "sector_field": sector_field,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rows", type=int, default=1_000_000)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--sector-field", default="superclass", choices=["superclass", "type", "flywireType", "somaSide", "itoleeHl", "trumanHl", "class", "subclass", "somaNeuromere", "entryNerve", "exitNerve", "rootSide"])
    args = parser.parse_args()
    result = run(None if args.full else args.max_rows, args.sector_field)
    field_suffix = "" if args.sector_field == "superclass" else f"_{args.sector_field}"
    output = RESULTS / (("path_lifting_audit_full_v3" if args.full else f"path_lifting_audit_prefix{result['scope']['rows_scanned']}_v3") + field_suffix + ".json")
    RESULTS.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema": "rime.exploratory.male-cns-path-lifting-audit.v3", **result}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"scope": result["scope"], "typed_core": result["typed_core"], "relay_strict": result["relay_strict"], "coverage_inclusive": result["coverage_inclusive"]}, indent=2, ensure_ascii=False))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
