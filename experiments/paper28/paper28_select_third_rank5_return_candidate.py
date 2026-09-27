#!/usr/bin/env python3
"""Select the third P28.5 return candidate without downstream success data.

The selector implements the P28.5g preregistration on the existing 562-cell
future-free carrier.  It excludes 1+1 fusion, prefers 1+2, and minimizes the
declared source-local distance to the two closed realizations.  The primary
rule has a twelve-cell tie.  Before any success evaluator is opened, a frozen
source-local tie-break prefers nonzero surplus and then minimizes a refined
binary-kernel boundary distance.

No rank-four completion relation, Good_4/Good_5 predicate, lower-section
authority, or winning label is read or serialized by this producer.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from paper28_select_second_rank5_return_candidate import (
    CONTINUITY_FIELDS,
    EXPECTED_CANDIDATE_SIGNATURE as SECOND_CANDIDATE_SIGNATURE,
    FORBIDDEN_OUTPUT_FIELDS,
    INPUT_SCHEMA,
    KEY_FIELDS,
    N,
    REFERENCE_SIGNATURE,
    _context_projection,
    _future_free_signature,
    _hamming_distance,
)


SCHEMA = "paper28-third-rank5-return-candidate-selection-v1"
RECEIPT_SCHEMA = "paper28-third-rank5-return-candidate-selection-receipt-v1"
RULE_SCHEMA = "paper28-cross-realization-invariant-audit-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "results" / "single_defect_n7_inherited_section_pilot_complete_v1.json"
DEFAULT_RULE = HERE / "results" / "paper28_cross_realization_invariant_audit_v1.json"
DEFAULT_OUTPUT = HERE / "results" / "paper28_third_rank5_return_candidate_selection_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_select_third_rank5_return_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "section_return_core.py",
    "single_defect_transport.py",
    "validation/validate_paper28_third_rank5_return_candidate.py",
)

DISTANCE_FIELDS = (
    "fusion_contains_inherited_fresh",
    "sigma5_length",
    "sigma5_surplus",
    "binary_kernel_mass_multiset",
    "cyclic_offsets_F4_to_kernel",
)
PREFERRED_FUSION = [1, 2]
EXPECTED_CANDIDATE_SIGNATURE = {
    "family": "22111__12_TO_3211",
    "fusion_contains_inherited_fresh": False,
    "fusion_parent_sizes": [1, 2],
    "rank4_partition": [3, 2, 1, 1],
    "rank5_partition": [2, 2, 1, 1, 1],
    "sigma5_length": 3,
    "sigma5_surplus": 2,
    "binary_kernel_mass_multiset": [0, 3],
    "cyclic_offsets_F4_to_kernel": [0, 6],
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(output: Path) -> Path:
    name = output.name.removesuffix(".json.gz")
    return output.with_name(f"{name}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _signature_key(signature: Mapping[str, Any]) -> str:
    return json.dumps(signature, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _cyclic_distance(left: int, right: int) -> int:
    forward = (left - right) % N
    backward = (right - left) % N
    return min(forward, backward)


def _boundary_distance(left: Mapping[str, Any], right: Mapping[str, Any]) -> int:
    left_masses = [int(value) for value in left["binary_kernel_mass_multiset"]]
    right_masses = [int(value) for value in right["binary_kernel_mass_multiset"]]
    if len(left_masses) != len(right_masses):
        raise AssertionError("binary-kernel mass arity drift")
    mass_distance = sum(abs(a - b) for a, b in zip(left_masses, right_masses))

    left_offsets = [int(value) for value in left["cyclic_offsets_F4_to_kernel"]]
    right_offsets = [int(value) for value in right["cyclic_offsets_F4_to_kernel"]]
    if len(left_offsets) != len(right_offsets):
        raise AssertionError("binary-kernel offset arity drift")
    offset_distance = min(
        sum(_cyclic_distance(a, b) for a, b in zip(left_offsets, permutation))
        for permutation in itertools.permutations(right_offsets)
    )
    return mass_distance + offset_distance


def _candidate_row(
    signature: Mapping[str, Any],
    context_count: int,
    references: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "signature": dict(signature),
        "context_count": int(context_count),
        "primary_distance": min(
            _hamming_distance(signature, reference, DISTANCE_FIELDS)
            for reference in references
        ),
        "refined_boundary_distance": min(
            _boundary_distance(signature, reference) for reference in references
        ),
    }


def _assert_rule(rule: Mapping[str, Any]) -> None:
    if rule.get("schema") != RULE_SCHEMA:
        raise AssertionError("unexpected P28.5g audit schema")
    selection = rule["next_hostile_selection"]
    if selection["status"] != "PREREGISTERED_NOT_RUN":
        raise AssertionError("P28.5g third-selection status drift")
    if selection["hard_constraint"] != "fusion_parent_type != 1+1":
        raise AssertionError("P28.5g hard constraint drift")
    if selection["preferred_type"] != "1+2":
        raise AssertionError("P28.5g preferred fusion drift")
    if rule["derived_conclusions"]["fusion_1_plus_1_common_but_unproved"] is not True:
        raise AssertionError("P28.5g no longer preregisters the 1+1 hostile test")


def build_payload(input_path: Path, rule_path: Path) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected inherited pilot schema")
    if len(source["rows"]) != 15120:
        raise AssertionError("third selection requires the complete rooted scope")

    rule = json.loads(rule_path.read_text(encoding="ascii"))
    _assert_rule(rule)

    groups: dict[str, list[tuple[Mapping[str, Any], dict[str, Any]]]] = defaultdict(list)
    family_context_counts: Counter[str] = Counter()
    for row in source["rows"]:
        signature = _future_free_signature(row)
        groups[_signature_key(signature)].append((row, signature))
        family_context_counts[signature["family"]] += 1
    if len(groups) != 562:
        raise AssertionError("future-free carrier no longer has 562 cells")

    references = [REFERENCE_SIGNATURE, SECOND_CANDIDATE_SIGNATURE]
    if any(reference["fusion_parent_sizes"] != [1, 1] for reference in references):
        raise AssertionError("closed-reference fusion anatomy drift")

    non_11 = []
    for members in groups.values():
        signature = members[0][1]
        if signature["fusion_parent_sizes"] == [1, 1]:
            continue
        non_11.append(_candidate_row(signature, len(members), references))
    if not non_11:
        raise AssertionError("no carrier cell breaks 1+1 fusion")

    preferred = [
        row for row in non_11 if row["signature"]["fusion_parent_sizes"] == PREFERRED_FUSION
    ]
    selection_pool = preferred or non_11
    preferred_applied = bool(preferred)

    minimum_primary_distance = min(row["primary_distance"] for row in selection_pool)
    primary_minimizers = sorted(
        (row for row in selection_pool if row["primary_distance"] == minimum_primary_distance),
        key=lambda row: _signature_key(row["signature"]),
    )
    if len(primary_minimizers) != 12:
        raise AssertionError("P28.5g primary selector no longer has a twelve-cell tie")

    nonzero_surplus = [
        row for row in primary_minimizers if row["signature"]["sigma5_surplus"] != 0
    ]
    if not nonzero_surplus:
        raise AssertionError("no primary minimizer attacks zero surplus")

    minimum_boundary_distance = min(
        row["refined_boundary_distance"] for row in nonzero_surplus
    )
    finalists = [
        row
        for row in nonzero_surplus
        if row["refined_boundary_distance"] == minimum_boundary_distance
    ]
    if len(finalists) != 1:
        raise AssertionError("source-local tie-break did not select a unique cell")
    selected_signature = finalists[0]["signature"]
    if selected_signature != EXPECTED_CANDIDATE_SIGNATURE:
        raise AssertionError("third-realization candidate signature drift")

    selected_members = groups[_signature_key(selected_signature)]
    contexts = sorted(
        (_context_projection(row, signature) for row, signature in selected_members),
        key=lambda row: (row["defect"], row["index"]),
    )
    if len(contexts) != 36:
        raise AssertionError("third-realization candidate no longer has 36 contexts")

    sigma6_words = Counter(tuple(row["sigma6"]["selected_word"]) for row in contexts)
    sigma5_words = Counter(tuple(row["sigma5"]["selected_word"]) for row in contexts)
    source_placements = Counter(tuple(row["rank5_context"]["mass"]) for row in contexts)
    target_placements = Counter(tuple(row["rank4_context"]["mass"]) for row in contexts)

    candidate_projection = {
        "name": "C_4,cand3^(7) pre-section carrier",
        "recursive_authority": "NONE",
        "selection_rule": (
            "exclude 1+1 fusion, prefer 1+2, minimize the P28.5g source-local "
            "Hamming distance, retain the complete primary tie, then before any "
            "success evaluation prefer nonzero surplus and minimize refined "
            "binary-kernel mass/offset distance"
        ),
        "key_fields": list(KEY_FIELDS),
        "primary_distance_fields": list(DISTANCE_FIELDS),
        "closed_reference_signatures": references,
        "hard_constraint": "fusion_parent_sizes != [1,1]",
        "preferred_fusion": PREFERRED_FUSION,
        "preferred_fusion_applied": preferred_applied,
        "primary_minimum_distance": minimum_primary_distance,
        "primary_minimizer_count": len(primary_minimizers),
        "primary_minimizer_context_count": sum(
            row["context_count"] for row in primary_minimizers
        ),
        "primary_minimizers": primary_minimizers,
        "nonzero_surplus_minimizer_count": len(nonzero_surplus),
        "nonzero_surplus_context_count": sum(row["context_count"] for row in nonzero_surplus),
        "minimum_refined_boundary_distance": minimum_boundary_distance,
        "refined_finalist_count": len(finalists),
        "selected_signature": selected_signature,
        "context_count": len(contexts),
        "contexts": contexts,
    }
    encoded = json.dumps(
        candidate_projection,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_OUTPUT_FIELDS:
        if field in encoded:
            raise AssertionError(f"future-success field leaked into candidate: {field}")

    payload = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "purpose": "select a third source-local return model that breaks 1+1 fusion",
            "evaluation_status": "NOT_RUN",
            "section_authority_status": "NOT_GRANTED",
            "nonclaim": (
                "this artifact freezes a future-free pre-section carrier; it does "
                "not prove C_4,cand3 -> P_<=3 or C_5,cand3 -> C_4,cand3"
            ),
        },
        "phase_order": [
            "bind_P28_5g_preregistered_rule",
            "project_complete_inherited_rows_to_future_free_keys",
            "exclude_1_plus_1_fusion",
            "prefer_1_plus_2_fusion",
            "retain_all_primary_distance_minimizers",
            "apply_source_local_nonzero_surplus_boundary_tiebreak",
            "freeze_candidate_payload_and_digest",
            "downstream_completion_and_section_evaluators_absent",
        ],
        "inputs": {
            "inherited_pilot": {
                "name": input_path.name,
                "schema": source["schema"],
                "sha256": _sha256(input_path),
                "rows_digest": source["rows_digest"],
            },
            "preregistered_rule": {
                "name": rule_path.name,
                "schema": rule["schema"],
                "sha256": _sha256(rule_path),
                "content_sha256": rule["content_sha256"],
                "status": rule["next_hostile_selection"]["status"],
            },
        },
        "carrier_audit": {
            "signature_cell_count": len(groups),
            "context_count": sum(len(members) for members in groups.values()),
            "family_context_counts": dict(sorted(family_context_counts.items())),
            "non_1_plus_1_cell_count": len(non_11),
            "preferred_1_plus_2_cell_count": len(preferred),
            "primary_distance_distribution": {
                str(distance): count
                for distance, count in sorted(
                    Counter(row["primary_distance"] for row in selection_pool).items()
                )
            },
            "primary_tie_boundary_distance_distribution": {
                str(distance): count
                for distance, count in sorted(
                    Counter(
                        row["refined_boundary_distance"] for row in nonzero_surplus
                    ).items()
                )
            },
        },
        "candidate": candidate_projection,
        "candidate_anatomy": {
            "source_partition": selected_signature["rank5_partition"],
            "target_partition": selected_signature["rank4_partition"],
            "hostile_changes": [
                "Sigma_5 fusion masses 1+1 -> 1+2",
                "Sigma_5 surplus 0 -> 2",
                "binary-kernel mass multiset [0,2] -> [0,3]",
            ],
            "controlled_continuities": [
                "Sigma_5 length remains 3",
                "inherited fresh packet is not consumed by Sigma_5",
                "F4-relative kernel offsets remain [0,6]",
            ],
            "sigma6_word_distribution": {
                "".join(str(value) for value in word): count
                for word, count in sorted(sigma6_words.items())
            },
            "sigma5_word_distribution": {
                "".join(str(value) for value in word): count
                for word, count in sorted(sigma5_words.items())
            },
            "source_mass_placement_count": len(source_placements),
            "target_mass_placement_count": len(target_placements),
        },
        "next_phase_gate": {
            "allowed_next": (
                "construct and freeze future-free rank-four menus/exact lifts for "
                "the selected 36-context pre-section carrier"
            ),
            "evaluation_order": (
                "only after that construction is frozen may an independent Good_4 "
                "evaluator read the exact low-rank base"
            ),
            "forbidden_now": [
                "Good_4 or Good_5 evaluation",
                "lower-section membership",
                "winner-selected channel menus",
                "n=8 or full-15120 return evaluation",
            ],
        },
    }
    payload["candidate_payload_sha256"] = _digest(candidate_projection)
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, input_path: Path, rule_path: Path, output: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    closure = []
    for relative in SOURCE_CLOSURE:
        path = HERE / relative
        closure.append(
            {
                "path": path.relative_to(repo_root).as_posix(),
                "sha256": _sha256(path),
            }
        )
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "LOCAL_REPLAY_WITH_BOUND_HISTORICAL_INPUTS",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "candidate_payload_sha256": payload["candidate_payload_sha256"],
        },
        "inputs": {
            "inherited_pilot": {
                "name": input_path.name,
                "sha256": _sha256(input_path),
                "rows_digest": payload["inputs"]["inherited_pilot"]["rows_digest"],
            },
            "preregistered_rule": {
                "name": rule_path.name,
                "sha256": _sha256(rule_path),
                "content_sha256": payload["inputs"]["preregistered_rule"]["content_sha256"],
            },
        },
        "source_closure": closure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--rule", type=Path, default=DEFAULT_RULE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.input, args.rule)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            input_path=args.input,
            rule_path=args.rule,
            output=args.out,
            payload=payload,
        ),
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "candidate_payload_sha256": payload["candidate_payload_sha256"],
                "carrier_cells": payload["carrier_audit"]["signature_cell_count"],
                "primary_minimizers": payload["candidate"]["primary_minimizer_count"],
                "candidate_contexts": payload["candidate"]["context_count"],
                "candidate_family": payload["candidate"]["selected_signature"]["family"],
                "evaluation_status": payload["scope"]["evaluation_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
