#!/usr/bin/env python3
"""Select the second P28.5 rank-five return candidate without success data.

The selector projects the inherited n=7 pilot to the frozen 562-cell
future-free carrier.  It then excludes the released extremal family and
chooses the unique cell that preserves every declared continuity field of the
extremal reference while changing its source/target partition family.

No rank-four completion relation, Good_4/Good_5 predicate, or lower-section
authority is read or serialized by this producer.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from section_return_core import deserialize_packet_state
from single_defect_transport import kernel_blocks


SCHEMA = "paper28-second-rank5-return-candidate-selection-v1"
RECEIPT_SCHEMA = "paper28-second-rank5-return-candidate-selection-receipt-v1"
INPUT_SCHEMA = "SINGLE_DEFECT_N7_INHERITED_SECTION_PILOT_V1"

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "results" / "single_defect_n7_inherited_section_pilot_complete_v1.json"
DEFAULT_OUTPUT = HERE / "results" / "paper28_second_rank5_return_candidate_selection_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_select_second_rank5_return_candidate.py",
    "section_return_core.py",
    "single_defect_transport.py",
    "validation/validate_paper28_second_rank5_return_candidate.py",
)

N = 7
KEY_FIELDS = (
    "family",
    "fusion_contains_inherited_fresh",
    "fusion_parent_sizes",
    "rank4_partition",
    "rank5_partition",
    "sigma5_length",
    "sigma5_surplus",
    "binary_kernel_mass_multiset",
    "cyclic_offsets_F4_to_kernel",
)
CONTINUITY_FIELDS = (
    "fusion_parent_sizes",
    "fusion_contains_inherited_fresh",
    "sigma5_length",
    "sigma5_surplus",
    "binary_kernel_mass_multiset",
    "cyclic_offsets_F4_to_kernel",
)
REFERENCE_SIGNATURE = {
    "family": "22111__11_TO_2221",
    "fusion_contains_inherited_fresh": False,
    "fusion_parent_sizes": [1, 1],
    "rank4_partition": [2, 2, 2, 1],
    "rank5_partition": [2, 2, 1, 1, 1],
    "sigma5_length": 3,
    "sigma5_surplus": 0,
    "binary_kernel_mass_multiset": [0, 2],
    "cyclic_offsets_F4_to_kernel": [0, 6],
}
EXPECTED_CANDIDATE_SIGNATURE = {
    "family": "31111__11_TO_3211",
    "fusion_contains_inherited_fresh": False,
    "fusion_parent_sizes": [1, 1],
    "rank4_partition": [3, 2, 1, 1],
    "rank5_partition": [3, 1, 1, 1, 1],
    "sigma5_length": 3,
    "sigma5_surplus": 0,
    "binary_kernel_mass_multiset": [0, 2],
    "cyclic_offsets_F4_to_kernel": [0, 6],
}
FORBIDDEN_OUTPUT_FIELDS = (
    "rank4_evaluator",
    "good_4",
    "good_5",
    "successful_channel",
    "successful_exact_lift",
    "lower_section_member",
    "target_in_exact_p_le3",
    "winning",
    "bellman",
    "reset_coaccessibility",
)


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


def _family_name(
    source_partition: Sequence[int],
    parent_sizes: Sequence[int],
    target_partition: Sequence[int],
) -> str:
    source = "".join(str(int(value)) for value in source_partition)
    fusion = "".join(str(int(value)) for value in sorted(parent_sizes))
    target = "".join(str(int(value)) for value in target_partition)
    return f"{source}__{fusion}_TO_{target}"


def _future_free_signature(row: Mapping[str, Any]) -> dict[str, Any]:
    """Project one pilot row without reading its rank-four evaluator."""

    defect = tuple(int(value) for value in str(row["defect"]))
    rank5 = row["rank5_context"]
    rank4 = row["rank4_context"]
    selected = row["sigma5"]["selected_block"]
    fusion = selected["first_fusion"]

    inherited_fresh = frozenset(int(value) for value in rank5["activation"]["fresh_packet"])
    fusion_parents = [
        frozenset(int(value) for value in packet)
        for packet in fusion["parent_packets"]
    ]
    parent_sizes = sorted(int(value) for value in fusion["parent_sizes"])

    packets = deserialize_packet_state(rank4["packets"])
    f4 = frozenset(int(value) for value in rank4["activation"]["fresh_packet"])
    f4_locations = [coordinate for coordinate, packet in packets.items() if packet == f4]
    if len(f4_locations) != 1:
        raise AssertionError("rank-four fresh packet has no unique coordinate")
    f4_coordinate = int(f4_locations[0])

    binary_blocks = [block for block in kernel_blocks(defect, N) if len(block) == 2]
    if len(binary_blocks) != 1:
        raise AssertionError("rooted defect lost its unique binary kernel")
    binary_block = tuple(sorted(int(value) for value in binary_blocks[0]))
    mass = tuple(int(value) for value in rank4["mass"])
    block_masses = [mass[coordinate] for coordinate in binary_block]

    signature = {
        "family": _family_name(rank5["partition"], parent_sizes, rank4["partition"]),
        "fusion_contains_inherited_fresh": inherited_fresh in fusion_parents,
        "fusion_parent_sizes": parent_sizes,
        "rank4_partition": [int(value) for value in rank4["partition"]],
        "rank5_partition": [int(value) for value in rank5["partition"]],
        "sigma5_length": int(selected["total_length"]),
        "sigma5_surplus": int(selected["total_surplus"]),
        "binary_kernel_mass_multiset": sorted(block_masses),
        "cyclic_offsets_F4_to_kernel": [
            (coordinate - f4_coordinate) % N for coordinate in binary_block
        ],
    }
    return signature


def _context_projection(row: Mapping[str, Any], signature: Mapping[str, Any]) -> dict[str, Any]:
    rank5 = row["rank5_context"]
    rank4 = row["rank4_context"]
    sigma6 = row["sigma6"]["selected_block"]
    sigma5 = row["sigma5"]["selected_block"]
    return {
        "index": int(row["index"]),
        "defect": str(row["defect"]),
        "carrier_signature": dict(signature),
        "sigma6": {
            "selection_reason": str(row["sigma6"]["selection_reason"]),
            "selected_word": [int(value) for value in sigma6["first_word"]],
            "fusion_parent_sizes": sorted(
                int(value) for value in sigma6["first_fusion"]["parent_sizes"]
            ),
        },
        "rank5_context": {
            "mass": [int(value) for value in rank5["mass"]],
            "partition": [int(value) for value in rank5["partition"]],
            "packets": rank5["packets"],
            "activation": rank5["activation"],
        },
        "sigma5": {
            "selected_word": [int(value) for value in sigma5["first_word"]],
            "fusion_parent_sizes": sorted(
                int(value) for value in sigma5["first_fusion"]["parent_sizes"]
            ),
            "total_length": int(sigma5["total_length"]),
            "total_surplus": int(sigma5["total_surplus"]),
            "first_fusion": sigma5["first_fusion"],
        },
        "rank4_context": {
            "mass": [int(value) for value in rank4["mass"]],
            "partition": [int(value) for value in rank4["partition"]],
            "packets": rank4["packets"],
            "activation": rank4["activation"],
        },
    }


def _hamming_distance(
    left: Mapping[str, Any], right: Mapping[str, Any], fields: Sequence[str]
) -> int:
    return sum(left[field] != right[field] for field in fields)


def build_payload(input_path: Path) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected inherited pilot schema")
    if len(source["rows"]) != 15120:
        raise AssertionError("candidate selection requires the complete rooted scope")

    groups: dict[str, list[tuple[Mapping[str, Any], dict[str, Any]]]] = defaultdict(list)
    family_context_counts: Counter[str] = Counter()
    for row in source["rows"]:
        signature = _future_free_signature(row)
        key = json.dumps(signature, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        groups[key].append((row, signature))
        family_context_counts[signature["family"]] += 1
    if len(groups) != 562:
        raise AssertionError("future-free carrier no longer has 562 cells")

    reference_key = json.dumps(
        REFERENCE_SIGNATURE, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )
    if reference_key not in groups or len(groups[reference_key]) != 35:
        raise AssertionError("released extremal reference cell drift")

    candidates = []
    for key, members in sorted(groups.items()):
        signature = members[0][1]
        if signature["family"] == REFERENCE_SIGNATURE["family"]:
            continue
        distance = _hamming_distance(signature, REFERENCE_SIGNATURE, CONTINUITY_FIELDS)
        candidates.append(
            {
                "signature": signature,
                "continuity_distance": distance,
                "context_count": len(members),
            }
        )
    minimum_distance = min(row["continuity_distance"] for row in candidates)
    minimizers = [row for row in candidates if row["continuity_distance"] == minimum_distance]
    if minimum_distance != 0 or len(minimizers) != 1:
        raise AssertionError("second-realization selector lost its unique minimizer")
    selected_signature = minimizers[0]["signature"]
    if selected_signature != EXPECTED_CANDIDATE_SIGNATURE:
        raise AssertionError("second-realization candidate signature drift")

    selected_key = json.dumps(
        selected_signature, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )
    selected_members = groups[selected_key]
    contexts = sorted(
        (_context_projection(row, signature) for row, signature in selected_members),
        key=lambda row: (row["defect"], row["index"]),
    )
    if len(contexts) != 48:
        raise AssertionError("second-realization candidate no longer has 48 contexts")

    sigma6_words = Counter(tuple(row["sigma6"]["selected_word"]) for row in contexts)
    sigma5_words = Counter(tuple(row["sigma5"]["selected_word"]) for row in contexts)
    source_placements = Counter(tuple(row["rank5_context"]["mass"]) for row in contexts)
    target_placements = Counter(tuple(row["rank4_context"]["mass"]) for row in contexts)

    candidate_projection = {
        "name": "C_4,cand2^(7) pre-section carrier",
        "recursive_authority": "NONE",
        "selection_rule": (
            "among non-extremal cells of the future-free 562-cell carrier, "
            "preserve all declared continuity fields of the released extremal "
            "reference; the minimizer is unique and changes the source/target "
            "partition family"
        ),
        "key_fields": list(KEY_FIELDS),
        "continuity_fields": list(CONTINUITY_FIELDS),
        "reference_signature": REFERENCE_SIGNATURE,
        "selected_signature": selected_signature,
        "minimum_continuity_distance": minimum_distance,
        "minimizer_count": len(minimizers),
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
            "purpose": "select the second minimal independent rank-five return model",
            "evaluation_status": "NOT_RUN",
            "section_authority_status": "NOT_GRANTED",
            "nonclaim": (
                "this artifact selects a future-free pre-section carrier; it does "
                "not prove C_4,cand2 -> P_<=3 or C_5,cand2 -> C_4,cand2"
            ),
        },
        "phase_order": [
            "project_complete_inherited_rows_to_future_free_keys",
            "exclude_released_extremal_family",
            "select_unique_continuity_minimizer",
            "freeze_candidate_payload_and_digest",
            "downstream_completion_and_section_evaluators_absent",
        ],
        "input": {
            "name": input_path.name,
            "schema": source["schema"],
            "sha256": _sha256(input_path),
            "rows_digest": source["rows_digest"],
        },
        "carrier_audit": {
            "signature_cell_count": len(groups),
            "context_count": sum(len(members) for members in groups.values()),
            "family_context_counts": dict(sorted(family_context_counts.items())),
            "non_extremal_candidate_cell_count": len(candidates),
            "continuity_distance_distribution": {
                str(distance): count
                for distance, count in sorted(
                    Counter(row["continuity_distance"] for row in candidates).items()
                )
            },
        },
        "candidate": candidate_projection,
        "candidate_anatomy": {
            "source_partition": selected_signature["rank5_partition"],
            "target_partition": selected_signature["rank4_partition"],
            "changed_reference_facts": [
                "rank-five source partition 22111 -> 31111",
                "rank-four target partition 2221 -> 3211",
                "Sigma_6 selected word p^2 d -> d",
            ],
            "preserved_reference_facts": [
                "Sigma_5 fusion masses 1+1",
                "Sigma_5 length 3 and surplus 0",
                "inherited fresh packet is not consumed by Sigma_5",
                "binary-kernel mass multiset [0,2]",
                "F4-relative kernel offsets [0,6]",
            ],
            "sigma6_word_distribution": {
                "".join(str(value) for value in word): count
                for word, count in sorted(sigma6_words.items())
            },
            "sigma5_word_distribution": {
                "".join(str(value) for value in word): count
                for word, count in sorted(sigma5_words.items())
            },
            "source_mass_placement_distribution": [
                {"mass": list(mass), "count": count}
                for mass, count in sorted(source_placements.items())
            ],
            "target_mass_placement_count": len(target_placements),
        },
        "preregistered_hostile_questions": {
            "H1": "does section return again require a non-identity typed handoff?",
            "H2": "does the normalized action-relative boundary still support liftability?",
            "H3": "do TRANSPORT/RETURN/FUSION still cover every exact lift?",
            "H4": "does the future-free forall-C exists-m exists-x return shape still hold?",
        },
        "next_phase_gate": {
            "first": (
                "construct menus/lifts for the frozen 48-context rank-four carrier, "
                "digest them, and only then evaluate Good_4 against P_<=3"
            ),
            "second": (
                "only if lower authority is independently certified, construct the "
                "matching rank-five source and evaluate Good_5 after its own freeze"
            ),
            "forbidden_now": [
                "completion-success-derived source membership",
                "winner-selected channel menus",
                "promotion of typed handoff to F1-F5 before the second realization",
                "n=8 or full-15120 expansion",
            ],
        },
    }
    payload["candidate_payload_sha256"] = _digest(candidate_projection)
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, input_path: Path, output: Path, payload: Mapping[str, Any]
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
        "verification_mode": "LOCAL_REPLAY_WITH_BOUND_HISTORICAL_INPUT",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "candidate_payload_sha256": payload["candidate_payload_sha256"],
        },
        "input": {
            "name": input_path.name,
            "schema": payload["input"]["schema"],
            "sha256": payload["input"]["sha256"],
            "rows_digest": payload["input"]["rows_digest"],
        },
        "source_closure": closure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.input)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(input_path=args.input, output=args.out, payload=payload),
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "candidate_payload_sha256": payload["candidate_payload_sha256"],
                "carrier_cells": payload["carrier_audit"]["signature_cell_count"],
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
