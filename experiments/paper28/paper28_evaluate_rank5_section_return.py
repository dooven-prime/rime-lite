#!/usr/bin/env python3
"""Evaluate Good_5 on the frozen P28.5a candidate without rebuilding it."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

SCHEMA = "paper28-rank5-section-return-evaluation-v1"
RECEIPT_SCHEMA = "paper28-rank5-section-return-evaluation-receipt-v1"
CANDIDATE_SCHEMA = "paper28-rank5-section-return-candidate-v1"
LOWER_SECTION_SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_CHANNEL_COVER_V1"

HERE = Path(__file__).resolve().parent
DEFAULT_CANDIDATE = (
    HERE / "results" / "paper28_rank5_section_candidate_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_rank5_section_return_evaluation_v1.json.gz"
)
SOURCE_CLOSURE = (
    "paper28_evaluate_rank5_section_return.py",
    "validation/validate_paper28_rank5_section_return.py",
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


def _read(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("utf-8"))


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def default_receipt_path(output: Path) -> Path:
    name = output.name.removesuffix(".json.gz")
    return output.with_name(f"{name}.receipt.json")


def _construction_core(construction: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_contexts": construction["source_section"]["contexts"],
        "menu_contexts": construction["menus"]["contexts"],
        "exact_lifts": construction["exact_lifts"]["receipts"],
    }


def _validate_candidate(candidate: Mapping[str, Any]) -> None:
    if candidate.get("schema") != CANDIDATE_SCHEMA:
        raise AssertionError("unexpected P28.5a candidate schema")
    if candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("P28.5a candidate is not a pre-evaluation object")
    if candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("P28.5a candidate already contains an evaluator")
    if candidate["evaluator"]["evaluated_source_count"] != 0:
        raise AssertionError("P28.5a candidate evaluated source success")
    if candidate["evaluator"]["evaluated_channel_count"] != 0:
        raise AssertionError("P28.5a candidate evaluated channel success")
    if candidate["construction_payload_sha256"] != _digest(
        candidate["construction"]
    ):
        raise AssertionError("P28.5a construction digest mismatch")
    content = dict(candidate)
    observed_content_digest = content.pop("content_sha256")
    if observed_content_digest != _digest(content):
        raise AssertionError("P28.5a content digest mismatch")
    core_text = json.dumps(
        _construction_core(candidate["construction"]),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for forbidden in (
        "good_5",
        "lower_section_member",
        "target_in_lower_section",
        "successful_channel",
        "successful_exact_lift",
        "winning",
        "bellman",
        "reset_coaccessibility",
    ):
        if forbidden in core_text:
            raise AssertionError(
                f"candidate construction contains success field: {forbidden}"
            )


def _project_lower_section(
    path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = _read(path)
    if payload.get("schema") != LOWER_SECTION_SCHEMA:
        raise AssertionError("unexpected Paper XXVII lower-section schema")
    rows = []
    canonical_contexts: dict[str, dict[str, Any]] = {}
    role_order = {"F4": 0, "D1": 1, "D2": 2, "s": 3}
    for context in payload["contexts"]:
        geometry = context["source_geometry"]
        f4_coordinate = int(geometry["F4_coordinate"])
        mass_rows = [
            {
                "coordinate": int(row["coordinate"]),
                "mass": int(row["mass"]),
                "offset_from_distinguished": (
                    int(row["coordinate"]) - f4_coordinate
                )
                % 7,
                "is_distinguished": str(row["role"]).split("@", 1)[0]
                == "F4",
            }
            for row in geometry["packet_roles"]
        ]
        mass_rows.sort(key=lambda row: row["coordinate"])
        section_key = {
            "ambient_n": 7,
            "defect": [int(value) for value in geometry["defect_map"]],
            "rank": 4,
            "distinguished_coordinate": f4_coordinate,
            "distinguished_mass": 2,
            "mass_rows": mass_rows,
        }
        rows.append(
            {
                "authority": "Paper XXVII released Sec_4,ext^(7)",
                "defect": str(context["defect"]),
                "source_index": int(context["index"]),
                "section_boundary_key": section_key,
            }
        )

        role_rows = list(geometry["packet_roles"])
        role_rows.sort(
            key=lambda row: (
                role_order[str(row["role"]).split("@", 1)[0]],
                int(row["coordinate"]),
            )
        )
        canonical_packets = []
        canonical_distinguished: list[int] | None = None
        next_atom = 0
        for role_row in role_rows:
            size = int(role_row["mass"])
            packet = list(range(next_atom, next_atom + size))
            next_atom += size
            canonical_packets.append(
                {
                    "coordinate": int(role_row["coordinate"]),
                    "mass": size,
                    "packet": packet,
                    "role": str(role_row["role"]),
                }
            )
            if str(role_row["role"]).split("@", 1)[0] == "F4":
                canonical_distinguished = packet
        if next_atom != 7 or canonical_distinguished is None:
            raise AssertionError("released rank-four role carrier is malformed")
        canonical_packets.sort(key=lambda row: row["coordinate"])
        canonical_body = {
            "ambient_n": 7,
            "defect": [int(value) for value in geometry["defect_map"]],
            "packets": [
                {
                    "coordinate": row["coordinate"],
                    "mass": row["mass"],
                    "packet": row["packet"],
                }
                for row in canonical_packets
            ],
            "distinguished_packet": canonical_distinguished,
        }
        key_digest = _digest(section_key)
        canonical_contexts[key_digest] = {
            "context_id": f"ctx-{_digest(canonical_body)[:24]}",
            **canonical_body,
            "packet_roles": canonical_packets,
        }
    rows.sort(key=lambda row: (row["defect"], row["source_index"]))
    projection = {
        "name": "Sec_4,ext^(7)",
        "input_name": path.name,
        "input_schema": payload["schema"],
        "input_sha256": _sha256(path),
        "context_count": len(rows),
        "contexts": rows,
        "section_keys_sha256": _digest(
            [row["section_boundary_key"] for row in rows]
        ),
    }
    return projection, canonical_contexts


def _exact_role_handoff(
    receipt: Mapping[str, Any],
    canonical_context: Mapping[str, Any],
) -> dict[str, Any]:
    actual_context = receipt["exact"]["target_context"]
    if canonical_context["defect"] != actual_context["defect"]:
        raise AssertionError("section handoff changed the rooted action")
    canonical_by_coordinate = {
        int(row["coordinate"]): row for row in canonical_context["packet_roles"]
    }
    actual_by_coordinate = {
        int(row["coordinate"]): row for row in actual_context["packets"]
    }
    if set(canonical_by_coordinate) != set(actual_by_coordinate):
        raise AssertionError("section handoff changed occupied coordinates")

    atom_map: dict[int, int] = {}
    role_rows = []
    for coordinate in sorted(canonical_by_coordinate):
        canonical_row = canonical_by_coordinate[coordinate]
        actual_row = actual_by_coordinate[coordinate]
        canonical_packet = [int(value) for value in canonical_row["packet"]]
        actual_packet = [int(value) for value in actual_row["packet"]]
        if len(canonical_packet) != len(actual_packet):
            raise AssertionError("section handoff changed a packet mass")
        for canonical_atom, actual_atom in zip(
            sorted(canonical_packet), sorted(actual_packet), strict=True
        ):
            atom_map[canonical_atom] = actual_atom
        role_rows.append(
            {
                "role": str(canonical_row["role"]),
                "coordinate": coordinate,
                "canonical_packet": sorted(canonical_packet),
                "actual_packet": sorted(actual_packet),
            }
        )
    if set(atom_map) != set(range(7)) or set(atom_map.values()) != set(range(7)):
        raise AssertionError("section handoff is not an atom bijection")
    mapped_distinguished = sorted(
        atom_map[int(value)]
        for value in canonical_context["distinguished_packet"]
    )
    if mapped_distinguished != sorted(actual_context["distinguished_packet"]):
        raise AssertionError("section handoff does not preserve fresh ancestry")
    return {
        "canonical_source_context_id": str(canonical_context["context_id"]),
        "actual_target_context_id": str(actual_context["context_id"]),
        "canonical_to_actual_atom_bijection": [
            {"canonical_atom": source, "actual_atom": target}
            for source, target in sorted(atom_map.items())
        ],
        "role_packet_correspondence": role_rows,
        "distinguished_packet_preserved": True,
    }


def _lift_evaluation(
    receipt: Mapping[str, Any],
    target_by_key: Mapping[str, Mapping[str, Any]],
    canonical_contexts: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    key = receipt["exact"]["target_channel"]["section_boundary_key"]
    key_digest = _digest(key)
    target = target_by_key.get(key_digest)
    row: dict[str, Any] = {
        "receipt_id": str(receipt["receipt_id"]),
        "target_boundary_sha256": key_digest,
        "target_in_lower_section": target is not None,
    }
    if target is not None:
        row["target_section_refs"] = [
            {
                "defect": str(target["defect"]),
                "source_index": int(target["source_index"]),
            }
        ]
        row["target_section_key"] = key
        row["exact_ancestry_update"] = receipt["exact"]["ancestry_update"]
        row["exact_role_handoff"] = _exact_role_handoff(
            receipt,
            canonical_contexts[key_digest],
        )
    return row


def build_evaluation(
    candidate_path: Path,
    lower_section_path: Path,
) -> dict[str, Any]:
    candidate = _read(candidate_path)
    _validate_candidate(candidate)
    lower_section, canonical_contexts = _project_lower_section(
        lower_section_path
    )
    if lower_section != candidate["lower_section_target"]:
        raise AssertionError(
            "released lower-section authority differs from the frozen projection"
        )

    target_by_key: dict[str, Mapping[str, Any]] = {}
    for row in lower_section["contexts"]:
        key_digest = _digest(row["section_boundary_key"])
        if key_digest in target_by_key:
            raise AssertionError("lower-section boundary key is not unique")
        target_by_key[key_digest] = row

    receipts = {
        str(row["receipt_id"]): row
        for row in candidate["construction"]["exact_lifts"]["receipts"]
    }
    source_rows = []
    hostile_sources = []
    all_channel_rows = []
    for source_menu in candidate["construction"]["menus"]["contexts"]:
        channel_rows = []
        for channel in source_menu["channels"]:
            lift_rows = [
                _lift_evaluation(
                    receipts[receipt_id], target_by_key, canonical_contexts
                )
                for receipt_id in channel["exact_lift_ids"]
            ]
            successful = [
                row for row in lift_rows if row["target_in_lower_section"]
            ]
            unsuccessful = [
                row for row in lift_rows if not row["target_in_lower_section"]
            ]
            channel_row = {
                "channel_id": str(channel["channel_id"]),
                "good_5": bool(successful),
                "exact_lift_count": len(lift_rows),
                "successful_exact_lift_count": len(successful),
                "unsuccessful_exact_lift_count": len(unsuccessful),
                "successful_exact_lifts": successful,
                "unsuccessful_exact_lifts": unsuccessful,
            }
            channel_rows.append(channel_row)
            all_channel_rows.append(channel_row)
        good_channels = [
            row["channel_id"] for row in channel_rows if row["good_5"]
        ]
        source_row = {
            "source_context_id": str(source_menu["source_context_id"]),
            "menu_size": int(source_menu["menu_size"]),
            "good_channel_ids": good_channels,
            "good_channel_count": len(good_channels),
            "has_good_channel": bool(good_channels),
            "channels": channel_rows,
        }
        source_rows.append(source_row)
        if not good_channels:
            hostile_sources.append(
                {
                    "source_context_id": source_row["source_context_id"],
                    "complete_menu": source_menu,
                    "complete_exact_receipts": [
                        receipts[receipt_id]
                        for channel in source_menu["channels"]
                        for receipt_id in channel["exact_lift_ids"]
                    ],
                }
            )

    source_rows.sort(key=lambda row: row["source_context_id"])
    successful_channels = sum(row["good_5"] for row in all_channel_rows)
    successful_lifts = sum(
        row["successful_exact_lift_count"] for row in all_channel_rows
    )
    exact_lift_count = len(receipts)
    summary = {
        "source_context_count": len(source_rows),
        "successful_source_count": sum(
            row["has_good_channel"] for row in source_rows
        ),
        "hostile_source_count": len(hostile_sources),
        "channel_count": len(all_channel_rows),
        "successful_channel_count": successful_channels,
        "failed_channel_count": len(all_channel_rows) - successful_channels,
        "exact_lift_count": exact_lift_count,
        "successful_exact_lift_count": successful_lifts,
        "unsuccessful_exact_lift_count": exact_lift_count - successful_lifts,
        "good_channel_count_histogram": {
            str(key): value
            for key, value in sorted(
                Counter(row["good_channel_count"] for row in source_rows).items()
            )
        },
        "all_sources_have_good_channel": not hostile_sources,
        "winner_selected": False,
    }
    payload = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "source": "Sec_5,cand^(7) frozen by P28.5a",
            "target": "released Paper XXVII Sec_4,ext^(7)",
            "claim_boundary": (
                "fixed source-local candidate only; not the full 15120-context "
                "inherited universe and not a maximal rank-five section"
            ),
        },
        "quantifier_discipline": {
            "candidate_rebuilt": False,
            "menu_rebuilt": False,
            "exact_lifts_rebuilt": False,
            "best_channel_selected": False,
            "good_5_definition": (
                "exists exact lift in the frozen channel whose typed target "
                "boundary belongs to the independently released lower section"
            ),
        },
        "inputs": {
            "candidate": {
                "name": candidate_path.name,
                "schema": candidate["schema"],
                "sha256": _sha256(candidate_path),
                "content_sha256": candidate["content_sha256"],
                "construction_payload_sha256": candidate[
                    "construction_payload_sha256"
                ],
            },
            "lower_section": {
                "name": lower_section_path.name,
                "schema": lower_section["input_schema"],
                "sha256": lower_section["input_sha256"],
                "section_keys_sha256": lower_section[
                    "section_keys_sha256"
                ],
            },
        },
        "summary": summary,
        "sources": source_rows,
        "hostile_sources": hostile_sources,
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    output: Path,
    payload: Mapping[str, Any],
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
        "verification_mode": "LOCAL_REPLAY_FROM_FROZEN_CANDIDATE",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": payload["inputs"],
        "source_closure": closure,
    }


def _resolve_lower_section(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    release_root = os.environ.get("RIME_PAPER27_RELEASE_ROOT")
    if release_root:
        path = (
            Path(release_root)
            / "experiments"
            / "paper27"
            / "results"
            / "single_defect_n7_extremal_carrier_input_v1.json"
        )
        if path.exists():
            return path
    raise SystemExit(
        "Paper XXVII lower-section input not found; pass --n7-extremal-input "
        "or set RIME_PAPER27_RELEASE_ROOT"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--n7-extremal-input", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    lower_section_input = _resolve_lower_section(args.n7_extremal_input)
    payload = build_evaluation(args.candidate, lower_section_input)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(output=args.out, payload=payload),
    )
    print(
        json.dumps(
            {
                "artifact": args.out.as_posix(),
                "receipt": receipt_path.as_posix(),
                "status": "SECTION_TO_SECTION_RETURN_EVALUATED",
                **payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
