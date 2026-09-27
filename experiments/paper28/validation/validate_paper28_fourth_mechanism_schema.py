#!/usr/bin/env python3
"""Validate the P28.6u-A3 Generalized Fresh-Pair Carry declaration."""

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

import paper28_declare_fourth_mechanism_schema as declaration

ARTIFACT = (
    PARENT / "results" / "paper28_fourth_mechanism_schema_declaration_v1.json.gz"
)
RECEIPT = declaration.default_receipt_path(ARTIFACT)


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
    rebuilt = declaration.build_payload()
    if artifact != rebuilt:
        raise AssertionError("artifact does not equal deterministic reconstruction")
    if receipt["schema"] != declaration.RECEIPT_SCHEMA:
        raise AssertionError("receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("receipt artifact hash mismatch")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("receipt content binding mismatch")
    if (
        receipt["artifact"]["anonymous_profile_payload_sha256"]
        != artifact["anonymous_role_analysis"][
            "anonymous_profile_payload_sha256"
        ]
    ):
        raise AssertionError("receipt anonymous-profile binding mismatch")
    if receipt["source_closure"]["script"]["sha256"] != _sha256(
        PARENT / "paper28_declare_fourth_mechanism_schema.py"
    ):
        raise AssertionError("receipt source closure mismatch")

    expected_input_paths = {
        "cand2_projectability": declaration.DEFAULT_CAND2_PROJECTABILITY,
        "ext_support": declaration.DEFAULT_EXT_SUPPORT,
        "fpc_declaration": declaration.DEFAULT_FPC_DECLARATION,
        "prior_family": declaration.DEFAULT_PRIOR_FAMILY,
    }
    for key, path in expected_input_paths.items():
        if receipt["inputs"][key]["sha256"] != _sha256(path):
            raise AssertionError(f"receipt input hash mismatch for {key}")

    summary = artifact["summary"]
    expected = {
        "pooled_provenances": 83,
        "GFPC_supported_provenances": 83,
        "by_pool": {
            "cand2_fpc": {
                "input_provenances": 48,
                "anonymous_role_equation_passes": 48,
            },
            "ext_unsupported": {
                "input_provenances": 35,
                "anonymous_role_equation_passes": 35,
            },
        },
        "source_partition_histogram": {
            "2,2,1,1,1": 35,
            "3,1,1,1,1": 48,
        },
        "current_partition_histogram": {
            "2,2,2,1": 35,
            "3,2,1,1": 48,
        },
        "background_mass_profile_histogram": {"2,2,1": 35, "3,1,1": 48},
        "incoming_distinguished_mass_histogram": {"2": 35, "3": 48},
        "handoff_type_histogram": {"ATOM_BIJECTION": 35, "IDENTITY": 48},
        "FPC_subsumed_rows": 48,
        "strict_ext_witnesses": 35,
        "result": "FOURTH_SCHEMA_DECLARED_WITH_FPC_SUBSUMPTION",
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(f"summary drift for {key}: {summary[key]!r}")
    if artifact["scope"]["success_evaluator_loaded"]:
        raise AssertionError("a success evaluator entered A3")
    if artifact["declaration"]["expanded_family"] != [
        "OW",
        "FPC",
        "PEC",
        "GFPC",
    ]:
        raise AssertionError("expanded family drift")
    if not all(
        row["supported"] for row in artifact["declaration"]["support_rows"]
    ):
        raise AssertionError("GFPC did not cover every pooled provenance")
    subsumption = artifact["schema_subsumption"]
    if subsumption["relation"] != "FPC <= GFPC":
        raise AssertionError("subsumption relation drift")
    if subsumption["completion_inheritance"]:
        raise AssertionError("completion was inherited across schema subsumption")
    if artifact["reduced_family_view"]["status"] != "NOT_DECLARED_MINIMAL":
        raise AssertionError("reduced family was promoted to a minimality theorem")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT.as_posix(),
                "artifact_sha256": _sha256(ARTIFACT),
                "anonymous_profile_payload_sha256": artifact[
                    "anonymous_role_analysis"
                ]["anonymous_profile_payload_sha256"],
                **expected,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
