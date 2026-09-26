#!/usr/bin/env python3
"""Close the tagged 165-context fixed-n=7 reduced mechanism cover.

This is theorem composition only.  It combines the already frozen GFPC and
PEC component completions as a tagged disjoint union; it opens no oracle,
reruns no lift evaluator, and makes no minimal-family claim.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

SCHEMA = "paper28-fixed-scope-mechanism-cover-closure-v1"
RECEIPT_SCHEMA = "paper28-fixed-scope-mechanism-cover-closure-receipt-v1"
GFPC_SCHEMA = "paper28-gfpc-component-completion-v1"
PEC_SCHEMA = "paper28-pec-component-completion-v1"

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_GFPC = RESULTS / "paper28_gfpc_component_completion_v1.json.gz"
DEFAULT_PEC = RESULTS / "paper28_pec_component_completion_v1.json.gz"
DEFAULT_OUTPUT = (
    RESULTS / "paper28_fixed_scope_mechanism_cover_closure_v1.json.gz"
)

ASSIGNMENT = {
    "ext": "GFPC",
    "cand2": "GFPC",
    "cand3": "PEC",
    "cand4": "PEC",
    "cand5": "PEC",
}
SECTIONS = {
    "ext": "Sec_4,ext^(7)",
    "cand2": "Sec_4,cand2^(7)",
    "cand3": "Sec_4,cand3^(7)",
    "cand4": "Sec_4,cand4^(7)",
    "cand5": "Sec_4,cand5^(7)",
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(path: Path) -> Path:
    return path.with_name(
        f"{path.name.removesuffix('.json.gz')}.receipt.json"
    )


def _verify_content_digest(payload: Mapping[str, Any], label: str) -> None:
    candidate = dict(payload)
    stored = str(candidate.pop("content_sha256"))
    if _digest(candidate) != stored:
        raise AssertionError(f"{label} content digest mismatch")


def _input_record(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload["content_sha256"],
        "frozen_completion_input_sha256": payload[
            "frozen_completion_input_sha256"
        ],
    }


def _carrier_map(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(row["carrier_id"]): row
        for row in payload["evaluation"]["carriers"]
    }


def build_payload(*, gfpc_path: Path, pec_path: Path) -> dict[str, Any]:
    gfpc = _load(gfpc_path)
    pec = _load(pec_path)
    if gfpc.get("schema") != GFPC_SCHEMA:
        raise AssertionError("unexpected GFPC completion schema")
    if pec.get("schema") != PEC_SCHEMA:
        raise AssertionError("unexpected PEC completion schema")
    _verify_content_digest(gfpc, "GFPC completion")
    _verify_content_digest(pec, "PEC completion")
    if not gfpc["theorem"]["holds"] or not pec["theorem"]["holds"]:
        raise AssertionError("a component completion theorem is not closed")

    gfpc_carriers = _carrier_map(gfpc)
    pec_carriers = _carrier_map(pec)
    if set(gfpc_carriers) != {"cand2", "ext"}:
        raise AssertionError("GFPC carrier domain drift")
    if set(pec_carriers) != {"cand3", "cand4", "cand5"}:
        raise AssertionError("PEC carrier domain drift")
    if set(gfpc_carriers) & set(pec_carriers):
        raise AssertionError("component carrier tags are not disjoint")

    component_rows = {
        **{carrier: ("GFPC", row) for carrier, row in gfpc_carriers.items()},
        **{carrier: ("PEC", row) for carrier, row in pec_carriers.items()},
    }
    if set(component_rows) != set(ASSIGNMENT):
        raise AssertionError("declared five-carrier universe drift")

    reduced_rows = []
    carrier_rows = []
    for carrier_id in ("ext", "cand2", "cand3", "cand4", "cand5"):
        mechanism, row = component_rows[carrier_id]
        if mechanism != ASSIGNMENT[carrier_id]:
            raise AssertionError("reduced mechanism assignment drift")
        if row["section"] != SECTIONS[carrier_id]:
            raise AssertionError(f"{carrier_id} section tag drift")
        if not row["theorem_holds"]:
            raise AssertionError(f"{carrier_id} component theorem failed")
        if row["completed_source_count"] != row["source_count"]:
            raise AssertionError(f"{carrier_id} has an uncompleted source")
        good_key = (
            "G_GFPC_j_fs" if mechanism == "GFPC" else "G_PEC_j_fs"
        )
        good_rows = row[good_key]
        if len(good_rows) != row["source_count"]:
            raise AssertionError(f"{carrier_id} good-provenance relation drift")
        for good in good_rows:
            reduced_rows.append(
                {
                    "carrier_id": carrier_id,
                    "section": SECTIONS[carrier_id],
                    "mechanism": mechanism,
                    "context_id": str(good["context_id"]),
                    "return_certificate_id": str(good["return_certificate_id"]),
                    "kappa_4_ISE_id": str(good["kappa_4_ISE_id"]),
                }
            )
        carrier_rows.append(
            {
                "carrier_id": carrier_id,
                "section": SECTIONS[carrier_id],
                "completed_mechanism": mechanism,
                **{
                    key: row[key]
                    for key in (
                        "source_count",
                        "completed_source_count",
                        "channel_count",
                        "returning_channel_count",
                        "nonreturning_channel_count",
                        "mixed_channel_count",
                        "mixed_source_count",
                        "exact_lift_count",
                        "local_return_exact_lift_count",
                        "nonreturning_exact_lift_count",
                        "certified_target_context_count",
                    )
                },
            }
        )

    reduced_rows.sort(
        key=lambda row: (
            row["carrier_id"],
            row["context_id"],
            row["kappa_4_ISE_id"],
        )
    )
    tagged_keys = {
        (row["carrier_id"], row["context_id"], row["kappa_4_ISE_id"])
        for row in reduced_rows
    }
    if len(reduced_rows) != 165 or len(tagged_keys) != 165:
        raise AssertionError("reduced tagged good-provenance domain is not 165")

    closure_input = {
        "GFPC_content_sha256": gfpc["content_sha256"],
        "GFPC_frozen_completion_input_sha256": gfpc[
            "frozen_completion_input_sha256"
        ],
        "PEC_content_sha256": pec["content_sha256"],
        "PEC_frozen_completion_input_sha256": pec[
            "frozen_completion_input_sha256"
        ],
        "assignment": ASSIGNMENT,
        "tagged_good_relation_sha256": _digest(reduced_rows),
    }

    aggregate_keys = (
        "source_count",
        "completed_source_count",
        "channel_count",
        "returning_channel_count",
        "nonreturning_channel_count",
        "mixed_channel_count",
        "mixed_source_count",
        "exact_lift_count",
        "local_return_exact_lift_count",
        "nonreturning_exact_lift_count",
        "certified_target_context_count",
    )
    aggregate = {
        key: sum(int(row[key]) for row in carrier_rows)
        for key in aggregate_keys
    }

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "tagged_admitted_context_count": 165,
            "component_evaluator_rerun": False,
            "new_oracle_opened": False,
            "winner_selected": False,
            "all_n_claim": False,
        },
        "phase_order": [
            "load_and_verify_frozen_GFPC_and_PEC_component_theorems",
            "freeze_reduced_carrier_to_mechanism_assignment",
            "form_tagged_disjoint_union_of_good_provenance_relations",
            "verify_every_tagged_admitted_context_is_covered",
            "aggregate_failure_controls_without_rerunning_evaluators",
        ],
        "inputs": {
            "GFPC_completion": _input_record(gfpc_path, gfpc),
            "PEC_completion": _input_record(pec_path, pec),
        },
        "frozen_closure_input": closure_input,
        "frozen_closure_input_sha256": _digest(closure_input),
        "declared_universe": {
            "name": "D_4^(7)",
            "construction": "tagged disjoint union of five admitted sections",
            "sections": [SECTIONS[key] for key in ("ext", "cand2", "cand3", "cand4", "cand5")],
            "context_count": len(reduced_rows),
        },
        "reduced_sufficient_cover": {
            "schemas": ["GFPC", "PEC"],
            "assignment": ASSIGNMENT,
            "minimality_claimed": False,
            "historical_declared_family_preserved": [
                "OW",
                "FPC",
                "PEC",
                "GFPC",
            ],
            "G_red_fs": reduced_rows,
            "G_red_fs_sha256": _digest(reduced_rows),
        },
        "evaluation_summary": {
            "carriers": carrier_rows,
            "aggregate": aggregate,
        },
        "theorem": {
            "name": "Fixed-n7-Tagged-Multi-Carrier-Mechanism-Cover",
            "statement": (
                "for every tagged (j,C) in D_4^(7), the reduced tagged "
                "good-provenance relation G_red^fs(j,C) is nonempty"
            ),
            "derivation": [
                "projectability and GFPC support/completion on ext and cand2",
                "projectability and PEC support/completion on cand3, cand4, and cand5",
                "tagged disjoint-union introduction",
            ],
            "holds": aggregate["completed_source_count"] == 165,
        },
        "quantifier_audit": {
            "source_quantifier": "universal over the 165 tagged admitted contexts",
            "mechanism_quantifier": "existential sufficient cover, not unique classification",
            "provenance_quantifier": "existential inside each complete frozen fiber",
            "failed_channels_retained": aggregate["nonreturning_channel_count"],
            "failed_exact_lifts_retained": aggregate[
                "nonreturning_exact_lift_count"
            ],
            "winner_selected": False,
        },
        "claim_boundary": {
            "proved": [
                "fixed-n=7 tagged mechanism cover on all five declared rank-four carriers",
                "a reduced sufficient cover using GFPC and PEC",
                "finite multi-carrier F5 on D_4^(7) by component-theorem composition",
            ],
            "not_proved": [
                "minimality of {GFPC,PEC}",
                "one schema subsuming both GFPC and PEC",
                "all-n projectability, support cover, or component completion",
                "alignment with Lambda_4^complete(C)",
                "all-rank F5",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, output: Path, payload: Mapping[str, Any], input_paths: Sequence[Path]
) -> dict[str, Any]:
    source_paths = [
        Path(__file__).resolve(),
        HERE / "validation" / "validate_paper28_fixed_scope_mechanism_cover.py",
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "DETERMINISTIC_TAGGED_THEOREM_COMPOSITION",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "frozen_closure_input_sha256": payload[
                "frozen_closure_input_sha256"
            ],
        },
        "inputs": [
            {"name": path.name, "sha256": _sha256(path)}
            for path in input_paths
        ],
        "source_closure": [
            {
                "name": path.relative_to(HERE).as_posix(),
                "sha256": _sha256(path),
            }
            for path in source_paths
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gfpc", type=Path, default=DEFAULT_GFPC)
    parser.add_argument("--pec", type=Path, default=DEFAULT_PEC)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(gfpc_path=args.gfpc, pec_path=args.pec)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    receipt = build_receipt(
        output=args.out,
        payload=payload,
        input_paths=[args.gfpc, args.pec],
    )
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="ascii",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "frozen_closure_input_sha256": payload[
                    "frozen_closure_input_sha256"
                ],
                "theorem_holds": payload["theorem"]["holds"],
                "reduced_sufficient_cover": ["GFPC", "PEC"],
                "minimality_claimed": False,
                **payload["evaluation_summary"]["aggregate"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
