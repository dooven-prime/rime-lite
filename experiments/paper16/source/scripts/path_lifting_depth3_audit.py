#!/usr/bin/env python3
"""Fixed-depth-3 quotient/path-lifting audit for the MaleCNS carrier.

This is intentionally a *depth-3-only* audit.  It does not expose a generic
``--depth`` option: the project stop rule is to compute LP3/C3/h3 and then
move to sectorization comparison.  A concrete three-edge witness is

    a -> v -> w -> d

where ``v`` and ``w`` are the same concrete bodies used by the two adjacent
quotient edges.  ``Path_3^quot`` only records the three existential sector
edges and may use unrelated bodies at either relay.

All results are static support diagnostics.  ``weight`` is not used as a
physiological probability or capacity here; every positive release-native
body-pair row contributes one support edge.
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
UNANNOTATED = "<unannotated>"


def label(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "<missing>"
    text = str(value).strip()
    return text if text and text.lower() != "nan" else "<missing>"


def scan_batches(limit: int | None):
    """Yield (pre, post) numpy arrays from a deterministic row prefix."""
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
            yield pre, post
    finally:
        source.close()


def bit_values(mask: int, names: list[str]):
    """Return set-bit labels without constructing a dense mask array."""
    while mask:
        low = mask & -mask
        index = low.bit_length() - 1
        yield names[index]
        mask ^= low


def run(limit: int | None, sector_field: str = "superclass") -> dict:
    annotations = pd.read_feather(ANNOTATIONS, columns=["bodyId", sector_field])
    sectors = dict(zip(annotations["bodyId"].astype("int64"), annotations[sector_field].map(label)))
    annotated_ids = set(sectors)

    # A relay must have an outgoing concrete edge.  This first pass also gives
    # the exact body universe for the declared scan scope.
    pre_ids: set[int] = set()
    raw_rows = 0
    for pre, _post in scan_batches(limit):
        raw_rows += len(pre)
        pre_ids.update(int(x) for x in np.unique(pre).tolist())

    # Build concrete-body sector masks.  incoming[v] records source sectors
    # with an edge into v; outgoing[v] records target sectors reached from v.
    sector_names = sorted(set(sectors.values()) | {UNANNOTATED})
    if len(sector_names) > 64:
        raise ValueError(
            f"sector field {sector_field!r} has {len(sector_names)} labels; "
            "the fixed-depth-3 bit-packed audit is limited to 64 sectors. "
            "Use sectorization_field_audit.py and a separately declared restricted map."
        )
    sector_index = {name: bit for bit, name in enumerate(sector_names)}
    incoming: dict[int, int] = defaultdict(int)
    outgoing: dict[int, int] = defaultdict(int)
    macro_edges: set[tuple[str, str]] = set()
    scanned = 0
    for pre, post in scan_batches(limit):
        scanned += len(pre)
        for a, b in zip(pre.tolist(), post.tolist()):
            a_id, b_id = int(a), int(b)
            source_sector = sectors.get(a_id, UNANNOTATED)
            target_sector = sectors.get(b_id, UNANNOTATED)
            source_bit = 1 << sector_index[source_sector]
            target_bit = 1 << sector_index[target_sector]
            outgoing[a_id] |= target_bit
            # Only bodies with an observed outgoing edge can be concrete relays.
            if b_id in pre_ids:
                incoming[b_id] |= source_bit
            macro_edges.add((source_sector, target_sector))

    # Depth-2 witness multiplicities are reused for conditional survival.
    witness_counts: Counter[tuple[str, str, str]] = Counter()
    for middle, mask in incoming.items():
        middle_sector = sectors.get(middle, UNANNOTATED)
        for source_sector in bit_values(mask, sector_names):
            for target_sector in bit_values(outgoing.get(middle, 0), sector_names):
                witness_counts[(source_sector, middle_sector, target_sector)] += 1
    lifted2 = set(witness_counts)

    # Quotient words are three adjacent existential sector edges.  Carrier
    # rules are deliberately the same nested rules as the depth-2 audit.
    adjacency: dict[str, set[str]] = defaultdict(set)
    for source_sector, target_sector in macro_edges:
        adjacency[source_sector].add(target_sector)

    macro_words: dict[str, set[tuple[str, str, str, str]]] = {
        "typed_core": set(),
        "relay_strict": set(),
        "coverage_inclusive": set(),
    }
    for a, b in macro_edges:
        for c in adjacency.get(b, ()):
            for d in adjacency.get(c, ()):
                word = (a, b, c, d)
                if UNANNOTATED not in word:
                    macro_words["typed_core"].add(word)
                if b != UNANNOTATED and c != UNANNOTATED:
                    macro_words["relay_strict"].add(word)
                macro_words["coverage_inclusive"].add(word)

    # Scan concrete relay edges once.  Each edge v->w extends every incoming
    # sector of v and every outgoing sector of w.  We retain only a compact set
    # of sector words, never a body-level edge dump.
    lifted3: dict[str, set[tuple[str, str, str, str]]] = {
        key: set() for key in macro_words
    }
    extension_scanned = 0
    extension_candidates = 0
    # Many concrete edges share the same source-sector mask, relay labels, and
    # target-sector mask.  The projected support depends only on this pattern,
    # not on how many body edges realize it.  Deduplicating patterns preserves
    # Boolean Route_3 support while avoiding millions of repeated set inserts.
    seen_extension_patterns: set[int] = set()
    for pre, post in scan_batches(limit):
        extension_scanned += len(pre)
        for v, w in zip(pre.tolist(), post.tolist()):
            v_id, w_id = int(v), int(w)
            in_mask = incoming.get(v_id, 0)
            out_mask = outgoing.get(w_id, 0)
            if not in_mask or not out_mask:
                continue
            extension_candidates += 1
            b = sectors.get(v_id, UNANNOTATED)
            c = sectors.get(w_id, UNANNOTATED)
            # Packed integer key is materially smaller than a four-object
            # tuple for the large release-native scan.  Six bits suffice for
            # each sector index (the current universe has 29 labels).
            pattern = (in_mask << 76) | (sector_index[b] << 70) | (sector_index[c] << 64) | out_mask
            if pattern in seen_extension_patterns:
                continue
            seen_extension_patterns.add(pattern)
            for a in bit_values(in_mask, sector_names):
                for d in bit_values(out_mask, sector_names):
                    word = (a, b, c, d)
                    if word in macro_words["typed_core"]:
                        lifted3["typed_core"].add(word)
                    if word in macro_words["relay_strict"]:
                        lifted3["relay_strict"].add(word)
                    if word in macro_words["coverage_inclusive"]:
                        lifted3["coverage_inclusive"].add(word)

    def multiplicity_bin(value: int) -> str:
        if value == 1:
            return "1"
        if value <= 5:
            return "2-5"
        return ">5"

    def payload(rule: str) -> dict:
        words = macro_words[rule]
        realized = lifted3[rule] & words
        prefix_rule_words = {
            (a, b, c)
            for a, b, c, _d in words
        }
        # Prefixes must be admitted by the same carrier rule.  This is the
        # denominator for the newly-appended-step hazard h3.
        def prefix_allowed(prefix: tuple[str, str, str]) -> bool:
            a, b, c = prefix
            if rule == "typed_core":
                return UNANNOTATED not in prefix
            if rule == "relay_strict":
                return b != UNANNOTATED
            return True

        inherited_failures = 0
        new_step_failures = 0
        hazard_denominator = 0
        survival_by_bin: dict[str, dict[str, int | float | None]] = {}
        bin_counts: Counter[str] = Counter()
        bin_survived: Counter[str] = Counter()
        for word in words:
            prefix = word[:3]
            if prefix not in lifted2 or not prefix_allowed(prefix):
                inherited_failures += 1
                continue
            hazard_denominator += 1
            m = witness_counts[prefix]
            bucket = multiplicity_bin(m)
            bin_counts[bucket] += 1
            if word in realized:
                bin_survived[bucket] += 1
            else:
                new_step_failures += 1

        for bucket in ("1", "2-5", ">5"):
            denominator = bin_counts[bucket]
            survived = bin_survived[bucket]
            survival_by_bin[bucket] = {
                "prefix_route2_word_count": denominator,
                "survived_route3_word_count": survived,
                "conditional_survival": (survived / denominator if denominator else None),
            }

        lifted_prefix_words = sum(1 for word in words if word[:3] in lifted2 and prefix_allowed(word[:3]))
        return {
            "quotient_word_count": len(words),
            "lifted_word_count": len(realized),
            "LP3": (len(realized) / len(words) if words else None),
            "C3": (len(realized) / len(words) if words else None),
            "C3_equals_LP3_by_design": True,
            "depth2_prefix_route_word_count": lifted_prefix_words,
            "inherited_depth2_failure_count": inherited_failures,
            "newly_appended_step_failure_count": new_step_failures,
            "h3": (new_step_failures / hazard_denominator if hazard_denominator else None),
            "h3_denominator": hazard_denominator,
            "multiplicity_conditioned_survival": survival_by_bin,
            "route_semantics": "Route_3[Y_MaleCNS] support witnessed by one concrete v->w relay edge and concrete incoming/outgoing edges",
            "quotient_semantics": "Path_3^quot support from three adjacent existential sector edges",
        }

    result = {
        "schema": "rime.exploratory.male-cns-depth3-route-audit.v1",
        "scope": {
            "mode": "full" if limit is None else "deterministic_prefix",
            "rows_scanned": raw_rows,
            "extension_rows_scanned": extension_scanned,
            "extension_candidate_edges": extension_candidates,
            "unique_extension_patterns": len(seen_extension_patterns),
        },
        "universe": {
            "annotation_body_ids": len(annotated_ids),
            "candidate_relay_bodies": len(pre_ids),
            "sector_count": len(sector_names),
            "sector_labels": sector_names,
            "sector_field": sector_field,
        },
        "carrier_rules": {rule: payload(rule) for rule in macro_words},
        "semantics": {
            "depth": 3,
            "stop_rule": "fixed depth-3 audit only; do not extend to d=4+ unless a new structure is predeclared",
            "support": "all positive release-native body-pair rows; weight is not used as a physiological probability",
            "multiplicity": "depth-2 concrete middle-body witness count, not reliability or signal strength",
            "unreached_status": "not applicable to exact declared depth-3 word scan; no unresolved word is treated as infinity",
            "carrier_nesting": "typed_core excludes <unannotated> everywhere; relay_strict excludes it only as a relay; coverage_inclusive retains it",
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Fixed-depth-3 MaleCNS route-lifting audit")
    parser.add_argument("--max-rows", type=int, default=1_000_000)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--sector-field", default="superclass", choices=["superclass", "type", "flywireType", "somaSide", "itoleeHl", "trumanHl", "class", "subclass", "somaNeuromere", "entryNerve", "exitNerve", "rootSide"])
    args = parser.parse_args()
    if args.max_rows <= 0:
        raise ValueError("max-rows must be positive")
    result = run(None if args.full else args.max_rows, args.sector_field)
    RESULTS.mkdir(parents=True, exist_ok=True)
    suffix = "full" if args.full else f"prefix{result['scope']['rows_scanned']}"
    field_suffix = "" if args.sector_field == "superclass" else f"_{args.sector_field}"
    output = RESULTS / f"path_lifting_depth3_audit_{suffix}{field_suffix}_v1.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"scope": result["scope"], "carrier_rules": result["carrier_rules"]}, indent=2, ensure_ascii=False))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
