"""Independently recompute the finite GridWorld F4 audit coordinates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

import gridworld_reference_sof as source  # noqa: E402


LEGACY_AUDIT = PAPER_DIR / "archive" / "results" / "gridworld_f4.sofaudit"
V2_AUDIT = PAPER_DIR / "results" / "audits" / "gridworld_f4.sofaudit.json"
NATIVE_ROOT = PAPER_DIR / "results" / "native" / "gridworld-f4"
REFERENCE_SOURCE = NATIVE_ROOT / "sources" / "gridworld-reference.source.json"
TARGET_SOURCE = NATIVE_ROOT / "sources" / "gridworld-f4-target.source.json"
NATIVE_RESULT = NATIVE_ROOT / "evidence" / "gridworld-f4.audit-result.json"
RESULT = (
    PAPER_DIR
    / "results"
    / "object-certificates"
    / "gridworld_f4.object-certificate.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, Any]:
    return {
        "uri": path.relative_to(ROOT).as_posix(),
        "digest": {"algorithm": "sha256", "value": sha256(path)},
    }


def matrices_from_snapshot(path: Path) -> tuple[dict[str, np.ndarray], float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    dimension = payload["dimension"]
    matrices: dict[str, np.ndarray] = {}
    for name in payload["observable_labels"]:
        matrix = np.zeros((dimension, dimension), dtype=float)
        for entry in payload["action_matrices"][name]:
            matrix[entry["row"], entry["column"]] = entry["value"]
        matrices[name] = matrix
    return matrices, float(payload["threshold"])


def support_from_matrices(matrices: list[np.ndarray], tol: float) -> np.ndarray:
    support = np.zeros(matrices[0].shape, dtype=bool)
    for matrix in matrices:
        support |= np.abs(matrix) > tol
    np.fill_diagonal(support, False)
    return support


def ordered_word_support(generators: list[np.ndarray], tol: float) -> np.ndarray:
    products = [left @ right for left in generators for right in generators]
    return support_from_matrices(products, tol)


def simple_commutator_support(
    generators: list[np.ndarray], tol: float
) -> np.ndarray:
    commutators = [
        generators[left] @ generators[right]
        - generators[right] @ generators[left]
        for left in range(len(generators))
        for right in range(left + 1, len(generators))
    ]
    return support_from_matrices(commutators, tol)


def graph_direct_support(
    transition_matrices: dict[str, np.ndarray], tol: float
) -> np.ndarray:
    """Graph baseline for the declared skew(T) generator convention."""

    support = np.zeros(next(iter(transition_matrices.values())).shape, dtype=bool)
    for matrix in transition_matrices.values():
        support |= np.abs(matrix - matrix.T) > 2 * tol
    np.fill_diagonal(support, False)
    return support


def pair_delta(reference: np.ndarray, target: np.ndarray) -> dict[str, Any]:
    missing = np.argwhere(reference & ~target).tolist()
    extra = np.argwhere(~reference & target).tolist()
    return {
        "missing_pairs": missing,
        "extra_pairs": extra,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "total_mismatch": len(missing) + len(extra),
    }


def normalized_released_delta(value: dict[str, Any]) -> dict[str, Any]:
    missing = value.get("missing_support", value.get("missing_bridge", []))
    extra = value.get("extra_support", value.get("extra_bridge", []))
    return {
        "missing_pairs": missing,
        "extra_pairs": extra,
        "missing_count": value["missing_count"],
        "extra_count": value["extra_count"],
        "total_mismatch": value["total_mismatch"],
    }


def build_certificate() -> dict[str, Any]:
    reference_raw, reference_tol = matrices_from_snapshot(REFERENCE_SOURCE)
    target_raw, target_tol = matrices_from_snapshot(TARGET_SOURCE)
    if reference_tol != target_tol:
        raise ValueError("native source thresholds differ")
    tol = reference_tol
    action_names = list(reference_raw)
    if action_names != list(target_raw):
        raise ValueError("native source observable labels differ")
    reference_generators = [
        (reference_raw[name] - reference_raw[name].T) / 2 for name in action_names
    ]
    target_generators = [
        (target_raw[name] - target_raw[name].T) / 2 for name in action_names
    ]

    reference_support = support_from_matrices(reference_generators, tol)
    target_support = support_from_matrices(target_generators, tol)
    graph_reference = graph_direct_support(reference_raw, tol)
    graph_target = graph_direct_support(target_raw, tol)
    if not np.array_equal(reference_support, graph_reference):
        raise ValueError("reference matrix support differs from graph baseline")
    if not np.array_equal(target_support, graph_target):
        raise ValueError("target matrix support differs from graph baseline")

    recomputed = {
        "support": pair_delta(reference_support, target_support),
        "word_bridge": pair_delta(
            ordered_word_support(reference_generators, tol),
            ordered_word_support(target_generators, tol),
        ),
        "lie_bridge": pair_delta(
            simple_commutator_support(reference_generators, tol),
            simple_commutator_support(target_generators, tol),
        ),
    }

    producer_result = json.loads(NATIVE_RESULT.read_text(encoding="utf-8"))
    producer_keys = {
        "support": "operator_support",
        "word_bridge": "word_length_two_support",
        "lie_bridge": "lie_simple_commutator_support",
    }
    for certificate_key, producer_key in producer_keys.items():
        producer_coordinate = producer_result["coordinates"][producer_key]
        producer_delta = {
            "missing_pairs": producer_coordinate["missing_pairs"],
            "extra_pairs": producer_coordinate["extra_pairs"],
            "missing_count": len(producer_coordinate["missing_pairs"]),
            "extra_count": len(producer_coordinate["extra_pairs"]),
            "total_mismatch": producer_coordinate["total_mismatch"],
        }
        if producer_delta != recomputed[certificate_key]:
            raise ValueError(
                f"native producer {producer_key} differs from independent recomputation"
            )

    legacy = json.loads(LEGACY_AUDIT.read_text(encoding="utf-8"))
    legacy_values = {
        "support": legacy["signature"]["support_mismatch"],
        "word_bridge": legacy["signature"]["bridge_word_mismatch"],
        "lie_bridge": legacy["signature"]["bridge_lie_mismatch"],
    }
    v2 = json.loads(V2_AUDIT.read_text(encoding="utf-8"))
    for coordinate_id, expected in recomputed.items():
        if normalized_released_delta(legacy_values[coordinate_id]) != expected:
            raise ValueError(f"legacy {coordinate_id} differs from recomputation")
        migrated_coordinate = v2["coordinates"][coordinate_id]
        if (
            migrated_coordinate["comparison_state"] != "UNRESOLVED"
            or migrated_coordinate["value"] is not None
            or migrated_coordinate["claim_status"] is not None
        ):
            raise ValueError(
                f"v2 {coordinate_id} must retain the legacy result only by source digest"
            )

    return {
        "certificate_version": "1.0",
        "certificate_id": "paper13.gridworld-f4.object-certificate.v1",
        "certificate_class": "object",
        "claim_target": "external_mathematical_object",
        "claim_status": "Computational Certificate",
        "result_state": "CERTIFIED",
        "scope": (
            "GridWorld F4 source-level direct support, ordered length-two word "
            "support, and simple-commutator support under tol=1e-8 and "
            "skew(T)=(T-T^T)/2; the migrated SOFAUDIT coordinates remain unresolved."
        ),
        "source_artifacts": [
            artifact(Path(source.__file__).resolve()),
            artifact(REFERENCE_SOURCE),
            artifact(TARGET_SOURCE),
            artifact(NATIVE_RESULT),
            artifact(LEGACY_AUDIT),
            artifact(V2_AUDIT),
            artifact(Path(__file__).resolve()),
        ],
        "validator_independence": {
            "implementation_relation": "separate_algorithm",
            "language_relation": "same_language",
            "runtime_relation": "same_process",
            "input_source": "declared_gridworld_source_construction",
            "producer_cache_used": False,
        },
        "external_baseline": {
            "method": "direct graph incidence for the declared skew-generator convention",
            "reference_pair_count": int(graph_reference.sum()),
            "target_pair_count": int(graph_target.sum()),
            "agrees_with_matrix_support": True,
        },
        "native_v2_control": {
            "raw_sources": [artifact(REFERENCE_SOURCE), artifact(TARGET_SOURCE)],
            "producer_result": artifact(NATIVE_RESULT),
            "comparison": (
                "The producer result and independent recomputation agree on all "
                "three native factual coordinates."
            ),
        },
        "recomputed": recomputed,
        "status": "PASS",
        "migration_boundary": {
            "active_audit_coordinates": "UNRESOLVED",
            "reason": (
                "The migrated SOFRS v2 reports do not bind the sector alignment "
                "and item-level report mappings needed for a comparison claim."
            ),
        },
        "negative_boundaries": [
            "This finite certificate does not establish GridWorld model adequacy, causal interpretation, or a cross-realization sensitivity ordering.",
            "Schema validation and migration consistency are checked separately and are not object-level evidence.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    certificate = build_certificate()
    rendered = json.dumps(certificate, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(rendered, encoding="utf-8")
    elif not RESULT.is_file():
        raise SystemExit(f"missing object certificate: {RESULT}")
    elif RESULT.read_text(encoding="utf-8") != rendered:
        raise SystemExit("released object certificate differs from recomputation")
    print(
        "PASS GridWorld F4 Object Certificate: "
        f"support={certificate['recomputed']['support']['total_mismatch']}, "
        f"word={certificate['recomputed']['word_bridge']['total_mismatch']}, "
        f"lie={certificate['recomputed']['lie_bridge']['total_mismatch']}"
    )


if __name__ == "__main__":
    main()
