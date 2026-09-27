#!/usr/bin/env python3
"""Validate P28.6v canonical return-certificate alignment."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import paper28_audit_canonical_return_certificate_alignment as producer

ARTIFACT = producer.DEFAULT_OUTPUT
RECEIPT = producer.default_receipt_path(ARTIFACT)
EXPECTED = {
    "ext": (35, 35, 4182, 2329),
    "cand2": (48, 48, 9600, 9498),
    "cand3": (36, 36, 5239, 4208),
    "cand4": (36, 36, 6498, 5937),
    "cand5": (10, 10, 1476, 1205),
}


def _load(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    artifact = _load(ARTIFACT)
    rebuilt = producer.build_payload()
    if artifact != rebuilt:
        raise AssertionError("canonical alignment artifact differs from replay")
    if artifact["schema"] != producer.SCHEMA:
        raise AssertionError("canonical alignment schema drift")
    if (
        producer._digest(artifact["alignment_core"])
        != artifact["frozen_alignment_core_sha256"]
    ):
        raise AssertionError("frozen alignment core digest mismatch")

    scope = artifact["scope"]
    if scope["all_n_claim"] or scope["all_rank_claim"]:
        raise AssertionError("fixed-scope audit crossed its scope boundary")
    if scope["all_Sec_4_origin_coverage_claim"]:
        raise AssertionError("inherited origin coverage became universal")
    if scope["success_evaluator_rerun"]:
        raise AssertionError("canonical alignment reran a success evaluator")

    core = artifact["alignment_core"]
    inherited = core["inherited_section_domain"]
    projection = core["projection_existence"]
    if inherited["context_count"] != 165 or not inherited["origin_coverage_holds"]:
        raise AssertionError("fixed-scope origin coverage failed")
    if projection["transfer_record_count"] != 165:
        raise AssertionError("frozen transfer-record domain drift")
    if projection["projected_provenance_count"] != 165:
        raise AssertionError("projected provenance count drift")
    if not projection["every_transfer_has_projection"]:
        raise AssertionError("projection existence failed")

    summaries = {row["carrier_id"]: row for row in core["carrier_summaries"]}
    if set(summaries) != set(EXPECTED):
        raise AssertionError("canonical alignment carrier domain drift")
    for carrier_id, (sources, transfers, exact_rows, _) in EXPECTED.items():
        row = summaries[carrier_id]
        if row["inherited_context_count"] != sources:
            raise AssertionError(f"{carrier_id} inherited source count drift")
        if row["transfer_record_count"] != transfers:
            raise AssertionError(f"{carrier_id} transfer count drift")
        if row["fs_exact_lift_count"] != exact_rows:
            raise AssertionError(f"{carrier_id} fs relation count drift")
        if row["lambda4_complete_exact_row_count"] <= 0:
            raise AssertionError(f"{carrier_id} canonical Lambda_4 is empty")
        if row["canonical_macro_path_count"] != exact_rows:
            raise AssertionError(f"{carrier_id} canonical path count drift")
        if row["type_I_path_count"] + row["type_II_path_count"] != exact_rows:
            raise AssertionError(f"{carrier_id} canonical path type count drift")
        if not row["A0_holds"] or not row["A1_holds"]:
            raise AssertionError(f"{carrier_id} semantic alignment failed")
        if row["A2_adapter_equals_Lambda4_claimed"]:
            raise AssertionError(f"{carrier_id} overclaims adapter equality")

    alignment_rows = core["rows"]
    if len(alignment_rows) != 165:
        raise AssertionError("alignment row count drift")
    fs_keys = set()
    canonical_keys = set()
    correspondence_count = 0
    for row in alignment_rows:
        strength = row["alignment_strength"]
        if not all(
            strength[key]
            for key in (
                "A0_every_fs_lift_has_canonical_first_exit_path",
                "A1_typed_observables_and_provenance_transport",
            )
        ):
            raise AssertionError("an alignment row is weaker than declared")
        if strength["A2_adapter_equals_Lambda_4_complete"]:
            raise AssertionError("macro adapter was equated to first-exit Lambda_4")
        if strength["A2_status"] != "NOT_CLAIMED_DIFFERENT_RELATION_TYPES":
            raise AssertionError("A2 relation-type firewall drift")
        if strength["raw_serialization_identity_required"]:
            raise AssertionError("raw serialization identity became a premise")
        correspondence = row["row_correspondence"]
        if len(correspondence) != row["fs_exact_lift_count"]:
            raise AssertionError("A0 correspondence is not total on fs lifts")
        if len(correspondence) != row["canonical_macro_path_count"]:
            raise AssertionError("canonical macro-path image count drift")
        if producer._digest(correspondence) != row["row_correspondence_sha256"]:
            raise AssertionError("row correspondence digest drift")
        for item in correspondence:
            fs_key = (row["carrier_id"], item["fs_receipt_id"])
            canonical_key = (row["carrier_id"], item["canonical_path_id"])
            if fs_key in fs_keys or canonical_key in canonical_keys:
                raise AssertionError("macro-path correspondence is not bijective")
            if item["canonical_segment_count"] not in (1, 2):
                raise AssertionError("canonical path has unsupported length")
            if len(item["canonical_segment_ids"]) != item["canonical_segment_count"]:
                raise AssertionError("canonical path segment ids are incomplete")
            fs_keys.add(fs_key)
            canonical_keys.add(canonical_key)
        correspondence_count += len(correspondence)
    if correspondence_count != 26995:
        raise AssertionError("total exact-row correspondence count drift")

    encoded_core = json.dumps(core, sort_keys=True).lower()
    for forbidden in (
        "localreturn",
        "successful_exact_lift",
        "target_in_exact_p_le3",
        '"good_4"',
        '"good_5"',
    ):
        if forbidden in encoded_core:
            raise AssertionError(
                f"success field leaked into alignment core: {forbidden}"
            )

    transport = artifact["canonical_mechanism_transport"]
    if not transport["loaded_after_alignment_freeze"]:
        raise AssertionError("component inputs were opened before alignment freeze")
    if transport["component_evaluator_rerun"]:
        raise AssertionError("component evaluator was rerun")
    if transport["source_count"] != 165:
        raise AssertionError("canonical transport source count drift")
    if transport["canonically_completed_source_count"] != 165:
        raise AssertionError("canonical component transport is incomplete")
    transport_summaries = {
        row["carrier_id"]: row for row in transport["carrier_summaries"]
    }
    for carrier_id, (sources, _, _, returns) in EXPECTED.items():
        row = transport_summaries[carrier_id]
        if row["source_count"] != sources:
            raise AssertionError(f"{carrier_id} transported source count drift")
        if row["canonically_completed_source_count"] != sources:
            raise AssertionError(f"{carrier_id} canonical completion failed")
        if row["canonical_local_return_path_count"] != returns:
            raise AssertionError(f"{carrier_id} canonical return count drift")

    theorems = artifact["theorems"]
    for key in (
        "fixed_scope_origin_coverage",
        "fixed_scope_projection_existence",
        "A0_alignment",
        "A1_alignment",
        "adapter_macro_equals_canonical_path_replay",
        "canonical_fixed_scope_mechanism_cover",
    ):
        if not theorems[key]:
            raise AssertionError(f"declared theorem failed: {key}")
    if theorems["A2_adapter_equals_Lambda4_complete"]:
        raise AssertionError("adapter equality with Lambda_4 was overclaimed")
    if theorems["raw_adapter_serialization_equality"]:
        raise AssertionError("raw serialization equality was overclaimed")

    receipt = json.loads(RECEIPT.read_text(encoding="ascii"))
    if receipt["schema"] != producer.RECEIPT_SCHEMA:
        raise AssertionError("canonical alignment receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("canonical alignment receipt hash mismatch")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("canonical alignment receipt content mismatch")
    if (
        receipt["artifact"]["frozen_alignment_core_sha256"]
        != artifact["frozen_alignment_core_sha256"]
    ):
        raise AssertionError("canonical alignment receipt core binding drift")

    input_paths = [
        producer.DEFAULT_CAND2_PROJECTABILITY,
        producer.DEFAULT_EXPANDED_PROJECTABILITY,
        producer.DEFAULT_EXT_PROJECTABILITY,
        *(Path(spec["candidate"]) for spec in producer.CARRIER_SPECS),
        *(Path(spec["rank5_candidate"]) for spec in producer.CARRIER_SPECS),
        producer.DEFAULT_GFPC,
        producer.DEFAULT_PEC,
    ]
    expected_receipt = producer.build_receipt(
        output=ARTIFACT,
        payload=artifact,
        input_paths=input_paths,
    )
    if receipt != expected_receipt:
        raise AssertionError("canonical alignment receipt closure drift")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT.as_posix(),
                "artifact_sha256": _sha256(ARTIFACT),
                "frozen_alignment_core_sha256": artifact[
                    "frozen_alignment_core_sha256"
                ],
                "inherited_sources": 165,
                "transfer_records": 165,
                "lambda4_complete_exact_rows": sum(
                    row["lambda4_complete_exact_row_count"]
                    for row in summaries.values()
                ),
                "canonical_macro_paths": 26995,
                "canonical_local_return_paths": 23177,
                "canonically_completed_sources": 165,
                "A0": True,
                "A1": True,
                "A2_adapter_equals_Lambda4": False,
                "raw_serialization_equality": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
