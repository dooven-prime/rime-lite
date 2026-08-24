"""Exact depth-two census for a strict shared-carrier obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_OUTPUT = HERE / "results" / "within_carrier_obstruction_v1.json"
SCHEMA = "rime.carrier-accessibility.within-carrier-obstruction.v1"
ARTIFACT_ID = "PAPER20-EXACT-WITHIN-CARRIER-OBSTRUCTION-V1"

Matrix = tuple[tuple[int, ...], ...]


def diagonal(entries: tuple[int, ...]) -> Matrix:
    return tuple(
        tuple(value if row == column else 0 for column, value in enumerate(entries))
        for row in range(len(entries))
    )


def permutation(image: tuple[int, ...]) -> Matrix:
    size = len(image)
    return tuple(
        tuple(1 if row == image[column] else 0 for column in range(size))
        for row in range(size)
    )


def multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return tuple(
        tuple(
            sum(left[row][mid] * right[mid][column] for mid in range(size))
            for column in range(size)
        )
        for row in range(size)
    )


def is_nonzero(matrix: Matrix) -> bool:
    return any(value != 0 for row in matrix for value in row)


def rank_integer(matrix: Matrix) -> int:
    work = [[value for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    rank = 0
    pivot_column = 0
    while rank < rows and pivot_column < columns:
        pivot = next(
            (row for row in range(rank, rows) if work[row][pivot_column] != 0),
            None,
        )
        if pivot is None:
            pivot_column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][pivot_column]
        for row in range(rows):
            if row == rank or work[row][pivot_column] == 0:
                continue
            row_value = work[row][pivot_column]
            work[row] = [
                pivot_value * work[row][column] - row_value * work[rank][column]
                for column in range(columns)
            ]
        rank += 1
        pivot_column += 1
    return rank


def block(projectors: tuple[Matrix, ...], transports: dict[str, Matrix], target: int, label: str, source: int) -> Matrix:
    return multiply(projectors[target], multiply(transports[label], projectors[source]))


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_digest(payload: dict) -> str:
    unsigned = deepcopy(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def source_reference(path: Path) -> dict:
    return {
        "uri": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def build_payload() -> dict:
    projectors = (
        diagonal((1, 0, 0, 0)),
        diagonal((0, 1, 1, 0)),
        diagonal((0, 0, 0, 1)),
    )
    transports = {
        "g01": permutation((1, 0, 2, 3)),
        "h23": permutation((0, 1, 3, 2)),
    }

    candidate_count = 0
    active_count = 0
    obstructions = []
    for source in range(3):
        for middle in range(3):
            for target in range(3):
                for first_label in sorted(transports):
                    for second_label in sorted(transports):
                        incoming = block(
                            projectors, transports, middle, first_label, source
                        )
                        outgoing = block(
                            projectors, transports, target, second_label, middle
                        )
                        product = multiply(outgoing, incoming)
                        candidate = is_nonzero(incoming) and is_nonzero(outgoing)
                        if not candidate:
                            continue
                        candidate_count += 1
                        if is_nonzero(product):
                            active_count += 1
                            continue
                        obstructions.append(
                            {
                                "route": {
                                    "source": source,
                                    "middle": middle,
                                    "target": target,
                                    "first_label": first_label,
                                    "second_label": second_label,
                                },
                                "endpoint_carrier_intersection": ["b"],
                                "incoming_rank": rank_integer(incoming),
                                "outgoing_rank": rank_integer(outgoing),
                                "product_rank": rank_integer(product),
                                "mechanism": "STRICT_WITHIN_CARRIER_IMAGE_KERNEL_CONTAINMENT",
                            }
                        )

    payload = {
        "schema": SCHEMA,
        "artifact_id": ARTIFACT_ID,
        "claim_status": "Computational Certificate",
        "arithmetic": "exact_integer_permutation_and_projector_matrices",
        "model": {
            "field": "Z interpreted in every field without coefficient collapse",
            "dimension": 4,
            "carrier_count": 1,
            "carrier_labels": ["b"],
            "sector_dimensions": [1, 2, 1],
            "sector_carrier_supports": [["b"], ["b"], ["b"]],
            "transport_labels": sorted(transports),
            "transport_semantics": {
                "g01": "coordinate transposition (0 1)",
                "h23": "coordinate transposition (2 3)",
            },
        },
        "enumeration": {
            "depth": 2,
            "route_policy": "all source/middle/target sectors and all ordered transport-label pairs",
            "total_labelled_route_count": 3**3 * len(transports) ** 2,
            "support_candidate_count": candidate_count,
            "active_product_count": active_count,
            "strict_within_carrier_obstruction_count": len(obstructions),
            "disjoint_endpoint_carrier_obstruction_count": 0,
            "obstructions": obstructions,
        },
        "strongest_claim": (
            "Complete exact depth-two census for the declared one-carrier model; "
            "every recorded obstruction has nonzero adjacent factors, shared "
            "endpoint carrier support, and exactly zero routed product."
        ),
        "known_nonclaims": [
            "No frequency or genericity claim beyond the declared finite model.",
            "No all-depth classification is inferred from the depth-two census.",
            "No Rubik or finite-field route claim is certified by this artifact.",
        ],
        "source_artifacts": [source_reference(Path(__file__).resolve())],
    }
    payload["content_sha256"] = content_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    target = args.out if args.out.is_absolute() else ROOT / args.out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(canonical_json({
        "artifact_id": payload["artifact_id"],
        "candidate_count": payload["enumeration"]["support_candidate_count"],
        "obstruction_count": payload["enumeration"]["strict_within_carrier_obstruction_count"],
    }))


if __name__ == "__main__":
    main()
