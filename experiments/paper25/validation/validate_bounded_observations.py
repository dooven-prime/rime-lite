"""Validate the Paper XXV bounded float64 observation registry."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper25.generate_observations import RUBIK_RUNTIME_SOURCES  # noqa: E402
from experiments.paper25.markov_probability_alignment import (  # noqa: E402
    build_payload as build_markov_alignment,
)
from experiments.paper25.markov_stability import build_payload as build_markov  # noqa: E402
from experiments.paper25.perturbation_sweep import (  # noqa: E402
    build_payload as build_perturbation,
)
from experiments.paper25.register_bounded_observations import (  # noqa: E402
    RESULT,
    SOURCES,
    build_payload as build_registry_payload,
    content_digest,
    sha256,
)
from experiments.paper25.rubik_transport import build_payload as build_rubik  # noqa: E402
from experiments.paper25.transformation_laws import (  # noqa: E402
    build_payload as build_transformation,
)


RECEIPT = RESULT.with_name("bounded_observation_registry_v1.validation-receipt.json")
ALLOWED_SOURCE_STATUSES = {
    "BOUNDED_NUMERICAL_OBSERVATION",
    "EXACT_FINITE_CERTIFICATE_AND_BOUNDED_NUMERICAL_OBSERVATION",
}


def with_source_closure(payload: dict, sources: tuple[str, ...]) -> dict:
    payload["source_artifacts"] = [
        {"uri": source, "sha256": sha256(ROOT / source)} for source in sources
    ]
    return payload


def replay_sources() -> dict[str, dict]:
    markov = build_markov()
    return {
        "experiments/paper25/results/transformation_laws_v1.json": (
            with_source_closure(
                build_transformation(),
                ("experiments/paper25/transformation_laws.py",),
            )
        ),
        "experiments/paper25/results/rubik_qh_transport_v1.json": (
            with_source_closure(
                build_rubik(),
                ("experiments/paper25/rubik_transport.py", *RUBIK_RUNTIME_SOURCES),
            )
        ),
        "experiments/paper25/results/rubik_perturbation_sweep_v1.json": (
            with_source_closure(
                build_perturbation(),
                (
                    "experiments/paper25/perturbation_sweep.py",
                    "experiments/paper25/rubik_transport.py",
                    *RUBIK_RUNTIME_SOURCES,
                ),
            )
        ),
        "experiments/paper25/results/nonnormal_markov_stability_v1.json": (
            with_source_closure(
                markov,
                (
                    "experiments/paper25/markov_stability.py",
                    "experiments/paper25/markov_helpers.py",
                    "experiments/paper25/perturbation_sweep.py",
                ),
            )
        ),
        "experiments/paper25/results/markov_probability_alignment_v1.json": (
            with_source_closure(
                build_markov_alignment(markov),
                (
                    "experiments/paper25/markov_probability_alignment.py",
                    "experiments/paper25/markov_helpers.py",
                    "experiments/paper25/markov_stability.py",
                ),
            )
        ),
    }


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get("content_sha256") != content_digest(payload):
        errors.append("registry content digest mismatch")
    if payload.get("claim_status") != "BOUNDED_OBSERVATION_REGISTRY":
        errors.append("bounded-observation registry status mismatch")
    if payload.get("evidence_layer") != "BOUNDED_FLOAT64_OBSERVATION":
        errors.append("registry lost bounded float64 layer")

    expected_paths = [uri for uri, _, _ in SOURCES]
    expected_components = {uri: component for uri, _, component in SOURCES}
    rows = payload.get("artifacts", [])
    if [row.get("path") for row in rows] != expected_paths:
        errors.append("bounded artifact registry mismatch")

    replayed_sources = replay_sources()
    for row in rows:
        path = ROOT / row.get("path", "")
        if not path.is_file():
            errors.append(f"missing bounded source: {row.get('path')}")
            continue
        source = json.loads(path.read_text(encoding="utf-8"))
        if row.get("sha256") != sha256(path):
            errors.append(f"stale bounded source: {row.get('path')}")
        if row.get("source_claim_status") != source.get("claim_status"):
            errors.append(f"source status drift: {row.get('path')}")
        if source.get("claim_status") not in ALLOWED_SOURCE_STATUSES:
            errors.append(f"unsupported source status: {row.get('path')}")
        if source.get("paper_evidence_status") != "REGISTERED_SUPPORT_NOT_THEOREM_PROOF":
            errors.append(f"paper-owned evidence status drift: {row.get('path')}")
        if row.get("evidence_layer") != "BOUNDED_FLOAT64_OBSERVATION":
            errors.append(f"bounded evidence layer drift: {row.get('path')}")
        component = expected_components.get(row.get("path"))
        if row.get("registered_component") != component:
            errors.append(f"bounded component registry drift: {row.get('path')}")
        if component not in {None, "whole_artifact"} and component not in source:
            errors.append(f"missing bounded source component: {row.get('path')}")
        if row.get("registered_role") != "BOUNDED_SUPPORT_NOT_THEOREM_PROOF":
            errors.append(f"bounded role escaped support boundary: {row.get('path')}")
        if source != replayed_sources.get(row.get("path")):
            errors.append(f"bounded source differs from producer replay: {row.get('path')}")

    if payload != build_registry_payload():
        errors.append("bounded registry differs from semantic replay")
    return errors


def write_receipt(payload: dict) -> None:
    receipt = {
        "schema": "rime.paper25.bounded-observation-receipt.v1",
        "artifact_id": "PAPER25-BOUNDED-OBSERVATION-REGISTRY-V1-VALIDATED",
        "status": "PASS",
        "scope": "local hash/status validation of bounded support; not independent proof",
        "bounded_observation_registry": {
            "path": RESULT.relative_to(ROOT).as_posix(),
            "sha256": sha256(RESULT),
            "content_sha256": payload["content_sha256"],
        },
        "source_closure": {
            row["path"]: row["sha256"] for row in payload["artifacts"]
        },
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"WROTE {RECEIPT}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        print("FAIL bounded observation registry")
        for error in errors:
            print(f"  - {error}")
        return 1
    if args.write_receipt:
        write_receipt(payload)
    print(f"PASS {RESULT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
