#!/usr/bin/env python3
"""Validate the P28.6u-A1 second mechanism-schema declaration."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_ARTIFACT = (
    ROOT / "results" / "paper28_second_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_RECEIPT = (
    ROOT / "results" / "paper28_second_mechanism_schema_declaration_v1.receipt.json"
)
SCRIPT = ROOT / "paper28_declare_second_mechanism_schema.py"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_gzip(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("paper28_second_schema", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load declaration producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    module = _load_module()
    artifact = _load_gzip(args.artifact)
    rebuilt = module.build_payload(input_path=module.DEFAULT_INPUT)
    if artifact != rebuilt:
        raise AssertionError("artifact differs from deterministic rebuild")
    if artifact["schema"] != module.SCHEMA:
        raise AssertionError("artifact schema drift")

    summary = artifact["summary"]
    expected = {
        "unsupported_projectable_provenances": 48,
        "FPC_supported_provenances": 48,
        "expanded_family_supported_contexts": 48,
        "selected_word_histogram": {"001": 24, "011": 24},
        "source_placement_profile_count": 2,
        "target_offset_profile_count": 21,
        "result": "SECOND_SCHEMA_DECLARED_AND_CAND2_SUPPORT_GAP_CLOSED",
    }
    if summary != expected:
        raise AssertionError(f"summary drift: {summary}")

    declaration = artifact["declaration"]
    if declaration["prior_family"] != ["OW"]:
        raise AssertionError("prior family drift")
    if declaration["schema_id"] != "FPC":
        raise AssertionError("second schema identifier drift")
    if declaration["expanded_family"] != ["OW", "FPC"]:
        raise AssertionError("expanded family drift")
    if not all(row["supported"] for row in declaration["support_rows"]):
        raise AssertionError("an unsupported cand2 provenance remains")

    clause_text = json.dumps(
        artifact["declaration"]["branch_formula"]["clauses"], sort_keys=True
    ).lower()
    for token in ("good_4", "good_5", "localreturn", "successful endpoint"):
        if token in clause_text:
            raise AssertionError(f"forbidden branch-clause token: {token}")
    firewall_text = json.dumps(
        artifact["declaration"]["branch_formula"]["explicitly_not_read"],
        sort_keys=True,
    ).lower()
    if "good or localreturn" not in firewall_text:
        raise AssertionError("branch formula does not state the success firewall")

    receipt = json.loads(args.receipt.read_text(encoding="ascii"))
    if receipt["schema"] != module.RECEIPT_SCHEMA:
        raise AssertionError("receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(args.artifact):
        raise AssertionError("artifact receipt binding drift")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("content receipt binding drift")
    if receipt["artifact"]["common_profile_payload_sha256"] != artifact[
        "unsupported_provenance_analysis"
    ]["common_profile_payload_sha256"]:
        raise AssertionError("common-profile receipt binding drift")
    if receipt["input"]["sha256"] != _sha256(module.DEFAULT_INPUT):
        raise AssertionError("input receipt binding drift")
    if receipt["source_closure"]["script"]["sha256"] != _sha256(SCRIPT):
        raise AssertionError("source-closure binding drift")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "common_profile_payload_sha256": artifact[
                    "unsupported_provenance_analysis"
                ]["common_profile_payload_sha256"],
                **summary,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
