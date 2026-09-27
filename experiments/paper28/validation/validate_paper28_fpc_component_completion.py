#!/usr/bin/env python3
"""Validate fixed-scope Fresh-Pair Carry component completion."""

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
SCRIPT = ROOT / "paper28_evaluate_fpc_component_completion.py"
DEFAULT_ARTIFACT = ROOT / "results" / "paper28_fpc_component_completion_v1.json.gz"
DEFAULT_RECEIPT = (
    ROOT / "results" / "paper28_fpc_component_completion_v1.receipt.json"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _load_module() -> Any:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("paper28_fpc_completion", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load FPC completion producer")
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
    artifact = _load(args.artifact)
    rebuilt = module.build_payload(
        declaration_path=module.DEFAULT_DECLARATION,
        projectability_path=module.DEFAULT_PROJECTABILITY,
        candidate_path=module.DEFAULT_CANDIDATE,
    )
    if artifact != rebuilt:
        raise AssertionError("FPC completion artifact differs from rebuild")
    if artifact["schema"] != module.SCHEMA:
        raise AssertionError("FPC completion schema drift")

    evaluation = artifact["evaluation"]
    expected = {
        "source_count": 48,
        "FPC_supported_source_count": 48,
        "completed_source_count": 48,
        "hostile_source_count": 0,
        "channel_count": 401,
        "returning_channel_count": 401,
        "nonreturning_channel_count": 0,
        "mixed_channel_count": 8,
        "mixed_source_count": 4,
        "exact_lift_count": 9600,
        "local_return_exact_lift_count": 9498,
        "nonreturning_exact_lift_count": 102,
        "certified_target_context_count": 1293,
    }
    for key, value in expected.items():
        if evaluation[key] != value:
            raise AssertionError(f"{key} drift: {evaluation[key]} != {value}")
    if len(evaluation["G_FPC_fs"]) != 48:
        raise AssertionError("fixed-scope good-provenance relation is incomplete")
    if not artifact["theorem"]["holds"]:
        raise AssertionError("FPC-FS-Completion does not hold")
    if artifact["scope"]["winner_selected"]:
        raise AssertionError("completion selected a winner")
    if artifact["scope"]["menu_or_lift_rebuilt"]:
        raise AssertionError("completion rebuilt the frozen relation")

    forbidden = artifact["definition"]["forbidden_success_refinements"]
    if forbidden != module.FORBIDDEN_SUCCESS_REFINEMENTS:
        raise AssertionError("success-semantics firewall drift")
    if "P_<=3^(7)" not in artifact["definition"]["LocalReturn_4_fs"]:
        raise AssertionError("generic low-rank LocalReturn semantics drift")

    receipt = json.loads(args.receipt.read_text(encoding="ascii"))
    if receipt["schema"] != module.RECEIPT_SCHEMA:
        raise AssertionError("receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(args.artifact):
        raise AssertionError("artifact receipt binding drift")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("content receipt binding drift")
    if receipt["artifact"]["frozen_completion_input_sha256"] != artifact[
        "frozen_completion_input_sha256"
    ]:
        raise AssertionError("completion-input receipt binding drift")
    input_paths = [
        module.DEFAULT_DECLARATION,
        module.DEFAULT_PROJECTABILITY,
        module.DEFAULT_CANDIDATE,
    ]
    expected_inputs = [
        {"name": path.name, "sha256": _sha256(path)} for path in input_paths
    ]
    if receipt["inputs"] != expected_inputs:
        raise AssertionError("input receipt binding drift")
    for row in receipt["source_closure"]:
        path = ROOT / row["name"]
        if row["sha256"] != _sha256(path):
            raise AssertionError(f"source closure drift: {row['name']}")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "frozen_completion_input_sha256": artifact[
                    "frozen_completion_input_sha256"
                ],
                "theorem_holds": True,
                **expected,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
