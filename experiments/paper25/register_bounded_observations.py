"""Register bounded float64 observations on the Paper XXV claim surface."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = HERE / "results" / "bounded_observation_registry_v1.json"
SOURCES = (
    (
        "experiments/paper25/results/transformation_laws_v1.json",
        ["Theorem 2.1"],
        "bounded_numerical_observation",
    ),
    (
        "experiments/paper25/results/rubik_qh_transport_v1.json",
        ["Theorem 2.1", "Boundary 2.3"],
        "whole_artifact",
    ),
    (
        "experiments/paper25/results/rubik_perturbation_sweep_v1.json",
        ["Theorem 3.1", "Corollaries 4.1 and 4.3"],
        "whole_artifact",
    ),
    (
        "experiments/paper25/results/nonnormal_markov_stability_v1.json",
        ["Corollary 5.1"],
        "whole_artifact",
    ),
    (
        "experiments/paper25/results/markov_probability_alignment_v1.json",
        ["Corollary 5.1"],
        "whole_artifact",
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_digest(payload: dict) -> str:
    unsigned = deepcopy(payload)
    unsigned.pop("content_sha256", None)
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_payload() -> dict:
    artifacts = []
    for uri, surfaces, component in SOURCES:
        path = ROOT / uri
        source = json.loads(path.read_text(encoding="utf-8"))
        artifacts.append(
            {
                "path": uri,
                "sha256": sha256(path),
                "evidence_layer": "BOUNDED_FLOAT64_OBSERVATION",
                "registered_component": component,
                "source_claim_status": source.get("claim_status"),
                "registered_role": "BOUNDED_SUPPORT_NOT_THEOREM_PROOF",
                "supports": surfaces,
            }
        )
    payload = {
        "schema": "rime.paper25.bounded-observation-registry.v1",
        "artifact_id": "PAPER25-BOUNDED-OBSERVATION-REGISTRY-V1",
        "evidence_layer": "BOUNDED_FLOAT64_OBSERVATION",
        "claim_status": "BOUNDED_OBSERVATION_REGISTRY",
        "scope": (
            "Registers selected float64 observations on the Paper XXV claim "
            "surface without changing their source status or treating them as "
            "theorem proofs."
        ),
        "artifacts": artifacts,
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"WROTE {RESULT}")


if __name__ == "__main__":
    main()
