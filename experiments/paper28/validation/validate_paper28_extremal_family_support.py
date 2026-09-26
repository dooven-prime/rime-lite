#!/usr/bin/env python3
"""Validate the P28.6u-B2 extremal-carrier support-separation artifact."""

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

import paper28_audit_extremal_carrier_support as audit


ARTIFACT = (
    PARENT / "results" / "paper28_extremal_carrier_support_separation_v1.json.gz"
)
RECEIPT = audit.default_receipt_path(ARTIFACT)


def _load_gzip(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    artifact = _load_gzip(ARTIFACT)
    receipt = _load_json(RECEIPT)
    rebuilt = audit.build_payload(
        rank4_authority_path=audit.DEFAULT_R4_AUTHORITY,
        rank5_candidate_path=audit.DEFAULT_R5_CANDIDATE,
        family_declaration_path=audit.DEFAULT_FAMILY_DECLARATION,
    )
    if artifact != rebuilt:
        raise AssertionError("artifact does not equal deterministic reconstruction")
    if receipt["schema"] != audit.RECEIPT_SCHEMA:
        raise AssertionError("receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("receipt artifact hash mismatch")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("receipt content binding mismatch")
    if (
        receipt["artifact"]["projectability_payload_sha256"]
        != artifact["projectability_payload_sha256"]
    ):
        raise AssertionError("receipt projectability binding mismatch")

    source_paths = {
        row["name"]: row["sha256"] for row in receipt["source_closure"]
    }
    expected_sources = {
        "paper28_audit_extremal_carrier_support.py": PARENT
        / "paper28_audit_extremal_carrier_support.py",
        "validation/validate_paper28_extremal_family_support.py": Path(__file__),
    }
    for name, path in expected_sources.items():
        if source_paths.get(name) != _sha256(path):
            raise AssertionError(f"source closure mismatch for {name}")

    expected = {
        "admitted_contexts": 35,
        "projectable_contexts": 35,
        "OW_supported_contexts": 0,
        "FPC_supported_contexts": 0,
        "PEC_supported_contexts": 0,
        "expanded_family_supported_contexts": 0,
        "projectable_but_unsupported_contexts": 35,
        "result": "OW_FPC_PEC_FAMILY_INCOMPLETE_ON_EXT",
    }
    for key, value in expected.items():
        if artifact["summary"][key] != value:
            raise AssertionError(f"summary drift for {key}")
    projectability = artifact["projectability"]
    if projectability["fiber_size_histogram"] != {"1": 35}:
        raise AssertionError("ext projectability fiber histogram drift")
    if projectability["handoff_type_histogram"] != {"ATOM_BIJECTION": 35}:
        raise AssertionError("ext handoff histogram drift")
    for row in projectability["rows"]:
        if not row["projectable"] or len(row["provenance_fiber"]) != 1:
            raise AssertionError("ext projectability row drift")
        eta = row["provenance_fiber"][0]["kappa_4_ISE"]["eta"]
        if eta["literal_atom_identity"]:
            raise AssertionError("ext handoff unexpectedly became identity")
    for row in artifact["support_audit"]["rows"]:
        if row["expanded_family_support_relation_nonempty"]:
            raise AssertionError("ext unexpectedly acquired family support")

    if artifact["scope"]["rank5_good_evaluator_loaded"]:
        raise AssertionError("rank-five Good evaluator entered the audit")
    forbidden_names = {
        name for name in artifact["forbidden_inputs"] if name.endswith(".json.gz")
    }
    receipt_names = {row["name"] for row in receipt["inputs"]}
    if forbidden_names & receipt_names:
        raise AssertionError("forbidden rank-five evaluator was loaded")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT.as_posix(),
                "artifact_sha256": _sha256(ARTIFACT),
                "projectability_payload_sha256": artifact[
                    "projectability_payload_sha256"
                ],
                **expected,
                "fiber_size_histogram": projectability["fiber_size_histogram"],
                "handoff_type_histogram": projectability[
                    "handoff_type_histogram"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
