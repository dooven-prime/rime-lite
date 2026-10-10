#!/usr/bin/env python3
"""Read-only exact drive audit for the five frozen persistent-safe cohorts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import gmpy2

MECHANISM = Path(__file__).resolve().parents[1]
PAPER = MECHANISM.parent
RESULT = MECHANISM / "results" / "mts1-v1"
OUTPUT = MECHANISM / "post_result_audits" / "persistent_safe_effective_drive.v1.json"
sys.path.insert(0, str(MECHANISM))

from exact_state_payload_v1 import decode_microstate_payload_v1
from exact_transition_payloads_v1 import (
    decode_clipped_drive_payload_v1,
    decode_raw_drive_payload_v1,
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def input_ref(path: Path) -> dict:
    data = path.read_bytes()
    return {"path": path.relative_to(PAPER).as_posix(), "bytes": len(data), "sha256": digest(data)}


def canonical_coarse(value: dict) -> tuple[tuple[int, int, int], ...]:
    if value["dimension"] != 28:
        raise ValueError("coarse dimension drift")
    entries = []
    last = -1
    for entry in value["entries"]:
        coordinate = entry["coordinate"]
        numerator = int(entry["numerator"])
        denominator = int(entry["denominator"])
        if not (last < coordinate < 28) or not numerator or denominator <= 0:
            raise ValueError("noncanonical coarse coordinate or rational")
        if gmpy2.gcd(abs(numerator), denominator) != 1:
            raise ValueError("nonreduced coarse rational")
        entries.append((coordinate, numerator, denominator))
        last = coordinate
    return tuple(entries)


def checked_file(relative: str, expected: dict, inventory: dict[str, dict]) -> bytes:
    if relative not in inventory or inventory[relative] != expected:
        raise ValueError(f"artifact not bound by frozen inventory: {relative}")
    path = (RESULT / relative).resolve()
    if not path.is_relative_to(RESULT.resolve()) or not path.is_file():
        raise ValueError(f"artifact outside result root: {relative}")
    data = path.read_bytes()
    if len(data) != expected["bytes"] or digest(data) != expected["sha256"]:
        raise ValueError(f"artifact differs from frozen inventory: {relative}")
    return data


def checked_payload(ref: dict, inventory: dict[str, dict]) -> bytes:
    relative = ref["path"]
    expected = {key: ref[key] for key in ("path", "bytes", "sha256", "role")}
    return checked_file(relative, expected, inventory)


def build_audit() -> dict:
    fiber_path = PAPER / "results" / "finite_history_transient_fiber_audit.v1.json"
    common_path = PAPER / "results" / "finite_history_common_support_audit.v1.json"
    registry_path = MECHANISM / "results" / "mechanism_cohort_registry.v1.json"
    freeze_path = MECHANISM / "results" / "mts1-v1.freeze-manifest.json"
    inventory_path = RESULT / "inventory.json"
    receipt_path = RESULT / "validation" / "mechanism_validation.v1.receipt.json"
    fiber, common, registry, freeze, inventory, receipt = map(
        read_json,
        (fiber_path, common_path, registry_path, freeze_path, inventory_path, receipt_path),
    )
    common_profile = common["common_support_audit"]["profiles"][0]
    if (
        fiber["status"] != "PASS"
        or common["status"] != "PASS"
        or common["common_support_audit"]["source_count"] != 711
        or common["common_support_audit"]["times"] != [2, 3]
        or common_profile["h"] != 0
        or common_profile["N_h"] != 1422
        or common_profile["K_h"] != 1228
        or common_profile["non_singleton_fiber_count"] != 10
        or common_profile["redundancy_N_minus_K"] != 194
        or not fiber["persistent_safe_forgetting"]["same_cohort_collection_at_t2_and_t3"]
        or fiber["persistent_safe_forgetting"]["total_redundancy_across_t2_t3"] != 194
        or freeze["status"] != "POST_EXECUTION_FROZEN"
        or receipt["status"] != "PASS"
        or receipt["validation_mode"] != "LOCAL_EXHAUSTIVE_EXACT_REDERIVATION"
    ):
        raise ValueError("parent exact certificate is not in the frozen passing state")
    closure = {item["role"]: item for item in freeze["artifact_closure"]}
    for role, path in (
        ("EXACT_SIDECAR_INVENTORY", inventory_path),
        ("EXHAUSTIVE_VALIDATION_RECEIPT", receipt_path),
    ):
        ref = closure[role]
        data = path.read_bytes()
        if ref["bytes"] != len(data) or ref["sha256"] != digest(data):
            raise ValueError(f"frozen {role} binding differs")
    refs = inventory["ordered_artifacts"]
    by_path = {ref["path"]: ref for ref in refs}
    if len(by_path) != len(refs):
        raise ValueError("duplicate path in frozen inventory")

    paper_cohorts = fiber["persistent_safe_forgetting"]["cohorts"]
    registered_cohorts = registry["persistent_safe"]["cohorts"]
    if len(paper_cohorts) != 5 or len(registered_cohorts) != 5:
        raise ValueError("persistent cohort count drift")
    if fiber["persistent_safe_forgetting"]["cohort_sizes"] != [51, 25, 19, 4, 3]:
        raise ValueError("persistent cohort sizes drift")

    total_sources = set()
    total_times = Counter()
    total_raw_signs = Counter()
    total_clip_nonzero = 0
    total_pairs = 0
    summaries = []
    for paper_cohort, registered in zip(paper_cohorts, registered_cohorts, strict=True):
        source_ids = paper_cohort["source_ids"]
        cohort_id = registered["cohort_id"]
        if (
            source_ids != registered["source_ids"]
            or len(source_ids) != paper_cohort["size"]
            or len(source_ids) != registered["source_count"]
            or not paper_cohort["same_source_membership_at_t3"]
            or total_sources.intersection(source_ids)
        ):
            raise ValueError(f"persistent membership mismatch: {cohort_id}")
        total_sources.update(source_ids)
        for current_time in (1, 2, 3):
            clipped_by_source = {}
            coarse_x = set()
            coarse_clip = set()
            raw_signs = Counter()
            for source_id in source_ids:
                relative = f"source-cache/{source_id}/{current_time}.json"
                record = json.loads(checked_file(relative, by_path[relative], by_path))
                if (
                    record["source_id"] != source_id
                    or record["current_time"] != current_time
                    or record["cohort_id"] != cohort_id
                    or record["source_role"] != "PERSISTENT_SAFE"
                    or record["replay_gates"]["observation_bytes_equal"] is not True
                    or record["replay_gates"]["legacy_state_hash_equal"] is not True
                ):
                    raise ValueError(f"source cache binding drift: {relative}")
                payloads = record["payloads"]
                state = decode_microstate_payload_v1(checked_payload(payloads["x_t"], by_path))
                raw = decode_raw_drive_payload_v1(checked_payload(payloads["u_t"], by_path))
                clipped = decode_clipped_drive_payload_v1(
                    checked_payload(payloads["clip_u_t"], by_path)
                )
                if not state:
                    raise ValueError(f"empty microscopic state: {relative}")
                expected_clip = {
                    coordinate: min(gmpy2.mpq(1), value)
                    for coordinate, value in raw.items()
                    if value > 0
                }
                if clipped != expected_clip:
                    raise ValueError(f"clipped payload differs from exact raw drive: {relative}")
                for name, values in (("x_t", state), ("u_t", raw), ("clip_u_t", clipped)):
                    if len(values) != payloads[name]["entry_count"]:
                        raise ValueError(f"payload entry count mismatch: {relative}/{name}")
                coarse_x.add(canonical_coarse(record["observations"]["O_x_t"]))
                coarse_clip.add(canonical_coarse(record["observations"]["O_clip_u_t"]))
                clipped_by_source[source_id] = clipped
                sign = "HAS_POSITIVE" if any(value > 0 for value in raw.values()) else (
                    "NONZERO_NONPOSITIVE" if raw else "ZERO"
                )
                raw_signs[sign] += 1
                total_raw_signs[sign] += 1
                total_clip_nonzero += bool(clipped)
                total_times[str(current_time)] += 1
                if not clipped and record["observations"]["O_clip_u_t"]["entries"]:
                    raise ValueError(f"zero clipped drive has nonzero coarse record: {relative}")
            if len(coarse_x) != 1 or len(coarse_clip) != 1:
                raise ValueError(f"cohort not successor-compatible in cached observations: {cohort_id}")
            pair_modes = Counter()
            for left, right in combinations(source_ids, 2):
                left_drive, right_drive = clipped_by_source[left], clipped_by_source[right]
                pair_modes[
                    "BOTH_DRIVES_ZERO" if not left_drive and not right_drive else
                    "COMMON_NONZERO_MICRO_DRIVE" if left_drive == right_drive else
                    "DIFFERENT_MICRO_DRIVES_WITH_COMMON_COARSE_OUTPUT"
                ] += 1
            if sum(pair_modes.values()) != registered["unordered_pair_count"]:
                raise ValueError(f"pair universe mismatch: {cohort_id}")
            total_pairs += sum(pair_modes.values())
            summaries.append({
                "cohort_id": cohort_id,
                "time": current_time,
                "source_count": len(source_ids),
                "pair_count": sum(pair_modes.values()),
                "raw_drive_sign_counts": dict(sorted(raw_signs.items())),
                "nonzero_clipped_drive_sources": sum(bool(x) for x in clipped_by_source.values()),
                "pair_modes": dict(sorted(pair_modes.items())),
            })
    if (
        len(total_sources) != 102
        or total_times != {"1": 102, "2": 102, "3": 102}
        or total_pairs != 5265
    ):
        raise ValueError("incomplete persistent source-time or pair universe")

    return {
        "schema": "rime.paper17.post-result-persistent-safe-effective-drive-audit.v1",
        "status": "PASS",
        "evidence_role": "POST_RESULT_READ_ONLY_EXACT_CACHE_AUDIT",
        "validation_mode": "LOCAL_BOUND_PAYLOAD_REPLAY_NO_OPERATOR_TRAVERSAL",
        "independent_validation": False,
        "microscopic_producer_replayed": False,
        "inputs": [
            input_ref(path)
            for path in (fiber_path, common_path, registry_path, freeze_path, inventory_path, receipt_path)
        ],
        "coverage": {
            "cohorts": 5,
            "distinct_sources": len(total_sources),
            "source_time_records": sum(total_times.values()),
            "times": [1, 2, 3],
            "paper17_common_support_times": [2, 3],
            "within_cohort_pairs_across_cached_times": total_pairs,
        },
        "summary": {
            "raw_drive_sign_counts": dict(sorted(total_raw_signs.items())),
            "nonzero_clipped_drive_source_times": total_clip_nonzero,
            "nonzero_clipped_drive_fiber_exists": total_clip_nonzero > 0,
            "all_selected_updates_are_pure_leak": total_clip_nonzero == 0,
        },
        "by_cohort_time": summaries,
        "boundary": (
            "The five non-singleton successor-compatible cohorts on times 2,3 are inherited "
            "from the frozen Paper XVII exact audit. This read-only audit verifies MTS-1 cached "
            "raw/clipped payloads and their inventory bindings at times 1,2,3. The time-1 "
            "cohort readout does not enlarge Paper XVII's common-support factorization. The "
            "audit does not recompute Y^T x, extend cached time, validate independently, or "
            "alter a frozen outcome."
        ),
        "audit_script": input_ref(Path(__file__).resolve()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write a separate post-result audit")
    parser.add_argument("--check", action="store_true", help="compare against the saved audit bytes")
    args = parser.parse_args()
    if args.write and args.check:
        parser.error("--write and --check are mutually exclusive")
    result = build_audit()
    data = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.write:
        OUTPUT.write_bytes(data)
    if args.check and OUTPUT.read_bytes() != data:
        raise ValueError("saved post-result audit differs from exact cache replay")
    print(json.dumps({"status": result["status"], **result["coverage"], **result["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
