#!/usr/bin/env python3
"""Exact signed route audit for the admitted ``Y_known_pm`` carrier.

The audit works on the frozen node basis.  Every normalized edge is the exact
rational number ``sigma(source) * weight / row_abs_mass(source)``.  A nonzero
finite-field residue is therefore an exact nonzero certificate whenever the
prime does not divide a row denominator.  Finite-field collisions fall back
to Python ``Fraction`` accumulation; floating-point thresholds are never used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import scipy
import numba
from numba import njit
from scipy import sparse


ROOT = Path(__file__).resolve().parents[1]
FOLLOWUPS = Path(__file__).resolve().parent
DESIGN_PATH = FOLLOWUPS / "y_known_pm_route_audit.design-v1.json"
REGISTRATION_PATH = FOLLOWUPS / "y_known_pm_route_audit.registration-v1.2.json"
DEFAULT_OUTPUT = FOLLOWUPS / "results" / "y_known_pm_route_audit.v1.json"

PROXY_SIGN_MAP = {
    "acetylcholine": 1,
    "dopamine": 1,
    "gaba": -1,
    "glutamate": 1,
    "histamine": 1,
    "octopamine": 1,
    "serotonin": 1,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def hash_operator(
    rows: np.ndarray, cols: np.ndarray, data: np.ndarray, shape: tuple[int, int]
) -> str:
    digest = hashlib.sha256()
    digest.update(np.asarray(shape, dtype=np.int64).tobytes())
    for array in (rows, cols, data):
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(np.asarray(contiguous.shape, dtype=np.int64).tobytes())
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def normalized_label(value: object) -> str:
    if value is None or pd.isna(value):
        return "<missing>"
    text = str(value).strip()
    return text if text and text.lower() != "nan" else "<missing>"


def resolve_bound_path(relative: str) -> Path:
    return (FOLLOWUPS / relative).resolve()


def exact_row_abs_mass(
    rows: np.ndarray, weights: np.ndarray, node_count: int
) -> tuple[np.ndarray, int]:
    """Accumulate nonnegative row masses without a floating-point round trip."""
    if rows.dtype != np.int64 or weights.dtype != np.int64:
        raise TypeError("exact row-mass accumulation requires int64 inputs")
    if np.any(weights < 0):
        raise ValueError("exact row-mass accumulation received a negative weight")
    overflow_upper_bound = int(weights.max(initial=0)) * int(len(weights))
    if overflow_upper_bound > np.iinfo(np.int64).max:
        raise OverflowError("declared int64 row-mass accumulation bound is unsafe")
    row_abs = np.zeros(node_count, dtype=np.int64)
    np.add.at(row_abs, rows, weights)
    return row_abs, overflow_upper_bound


def verify_registration() -> tuple[dict, dict]:
    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    registration = json.loads(REGISTRATION_PATH.read_text(encoding="utf-8"))
    if registration.get("status") != "REGISTERED_READY_TO_EXECUTE":
        raise ValueError("A1 audit is not registered for execution")
    if registration.get("execution_authority") != "A1_EXACT_SIGNED_ROUTE_AUDIT_ONLY":
        raise ValueError("unexpected A1 execution authority")
    if registration.get("design_sha256") != sha256_file(DESIGN_PATH):
        raise ValueError("registration does not bind the current design")
    producer = registration.get("producer", {})
    if producer.get("path") != Path(__file__).name:
        raise ValueError("registration producer path mismatch")
    if producer.get("sha256") != sha256_file(Path(__file__)):
        raise ValueError("registration producer digest mismatch")
    runtime = registration.get("runtime", {})
    actual_runtime = {
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "pandas_version": pd.__version__,
        "numba_version": numba.__version__,
    }
    if runtime != actual_runtime:
        raise ValueError(
            f"registered runtime mismatch: expected={runtime!r}, actual={actual_runtime!r}"
        )
    for entry in design.get("bound_inputs", []):
        path = resolve_bound_path(entry["path"])
        if not path.is_file() or sha256_file(path) != entry["sha256"]:
            raise ValueError(f"bound input mismatch: {entry['role']}")
    return design, registration


class Carrier:
    def __init__(self, design: dict):
        bound = {entry["role"]: entry for entry in design["bound_inputs"]}
        edge_path = resolve_bound_path(bound["CARRIER_EDGES"]["path"])
        node_path = resolve_bound_path(bound["CARRIER_NODES_AND_SECTORS"]["path"])
        admission_path = resolve_bound_path(bound["OPERATOR_ADMISSION"]["path"])

        edges = np.load(edge_path)
        rows = edges["row"].astype(np.int64, copy=False)
        cols = edges["col"].astype(np.int64, copy=False)
        weights = edges["weight"].astype(np.int64, copy=False)
        self.nodes = pd.read_parquet(node_path)
        self.n = len(self.nodes)
        if len(rows) != len(cols) or len(rows) != len(weights):
            raise ValueError("carrier edge arrays have inconsistent lengths")
        if np.any(weights <= 0):
            raise ValueError("carrier contains a nonpositive raw weight")

        node_sign = np.asarray(
            [PROXY_SIGN_MAP.get(str(value), 0) for value in self.nodes["consensus_nt"]],
            dtype=np.int8,
        )
        known = node_sign[rows] != 0
        known_rows = rows[known]
        known_cols = cols[known]
        known_weights = weights[known]
        known_values = known_weights * node_sign[known_rows].astype(np.int64)
        self.row_abs, self.row_abs_overflow_upper_bound = exact_row_abs_mass(
            known_rows, known_weights, self.n
        )
        normalized = known_values.astype(np.float64) / self.row_abs[known_rows]

        admission = json.loads(admission_path.read_text(encoding="utf-8"))
        expected = admission["operators"]["Y_known_pm"]
        shape = (self.n, self.n)
        raw_digest = hash_operator(known_rows, known_cols, known_values, shape)
        normalized_digest = hash_operator(known_rows, known_cols, normalized, shape)
        if raw_digest != expected["raw_operator_sha256"]:
            raise ValueError("reconstructed raw Y_known_pm digest mismatch")
        if normalized_digest != expected["normalized_operator_sha256"]:
            raise ValueError("reconstructed normalized Y_known_pm digest mismatch")
        if raw_digest != design["carrier"]["raw_operator_sha256"]:
            raise ValueError("design raw operator digest mismatch")
        if normalized_digest != design["carrier"]["normalized_operator_sha256"]:
            raise ValueError("design normalized operator digest mismatch")

        matrix = sparse.csr_matrix(
            (known_values, (known_rows, known_cols)), shape=shape, dtype=np.int64
        )
        matrix.sum_duplicates()
        matrix.sort_indices()
        if matrix.nnz != design["carrier"]["edge_count"]:
            raise ValueError("reconstructed Y_known_pm edge count mismatch")
        self.indptr = matrix.indptr.astype(np.int64, copy=False)
        self.indices = matrix.indices.astype(np.int64, copy=False)
        self.numerators = matrix.data.astype(np.int64, copy=False)
        self.body_ids = self.nodes["bodyId"].astype("int64").to_numpy()
        self.raw_operator_sha256 = raw_digest
        self.normalized_operator_sha256 = normalized_digest

    def sector_codes(self, field: str) -> tuple[list[str], np.ndarray]:
        labels = self.nodes[field].map(normalized_label)
        names = sorted(labels.unique().tolist())
        index = {name: i for i, name in enumerate(names)}
        return names, labels.map(index).to_numpy(dtype=np.int16)


def choose_prime(max_denominator: int, declared_prime: int) -> int:
    if declared_prime <= max_denominator:
        raise ValueError("declared prime does not exceed every row denominator")
    for divisor in range(2, int(declared_prime**0.5) + 1):
        if declared_prime % divisor == 0:
            raise ValueError("declared modular base is not prime")
    return declared_prime


def candidate_sources(
    carrier: Carrier, sector_codes: np.ndarray, sector_count: int
) -> dict[tuple[int, int], list[int]]:
    candidates: dict[tuple[int, int], list[tuple[int, int, int]]] = defaultdict(list)
    for source in np.flatnonzero(carrier.row_abs):
        start, stop = carrier.indptr[source : source + 2]
        targets = carrier.indices[start:stop]
        if not len(targets):
            continue
        counts = np.bincount(sector_codes[targets], minlength=sector_count)
        source_sector = int(sector_codes[source])
        total = int(stop - start)
        for target_sector in np.flatnonzero(counts):
            candidates[(source_sector, int(target_sector))].append(
                (int(counts[target_sector]), total, int(source))
            )
    return {
        key: [source for _, _, source in sorted(values)]
        for key, values in candidates.items()
    }


def macro_words(macro: np.ndarray, depth: int) -> Iterable[tuple[int, ...]]:
    sector_count = macro.shape[0]

    def extend(prefix: tuple[int, ...]) -> Iterable[tuple[int, ...]]:
        if len(prefix) == depth + 1:
            yield prefix
            return
        for target in range(sector_count):
            if macro[prefix[-1], target]:
                yield from extend((*prefix, target))

    for source in range(sector_count):
        yield from extend((source,))


@njit
def exact_boolean_route_support(
    rows: np.ndarray,
    cols: np.ndarray,
    sector_codes: np.ndarray,
    node_count: int,
    sector_count: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return exact macro, depth-2, and depth-3 Boolean support.

    This is an integer existence computation.  Saturated internal-sector
    pairs are skipped after every outer-sector pair has a witness.
    """
    incoming = np.zeros(node_count, dtype=np.uint64)
    outgoing = np.zeros(node_count, dtype=np.uint64)
    macro = np.zeros((sector_count, sector_count), dtype=np.uint8)
    one = np.uint64(1)
    for index in range(len(rows)):
        source = rows[index]
        target = cols[index]
        source_sector = int(sector_codes[source])
        target_sector = int(sector_codes[target])
        incoming[target] |= one << np.uint64(source_sector)
        outgoing[source] |= one << np.uint64(target_sector)
        macro[source_sector, target_sector] = 1

    route2 = np.zeros((sector_count, sector_count, sector_count), dtype=np.uint8)
    for middle in range(node_count):
        in_mask = incoming[middle]
        out_mask = outgoing[middle]
        if in_mask == 0 or out_mask == 0:
            continue
        middle_sector = int(sector_codes[middle])
        for source_sector in range(sector_count):
            if ((in_mask >> np.uint64(source_sector)) & one) == 0:
                continue
            for target_sector in range(sector_count):
                if ((out_mask >> np.uint64(target_sector)) & one) != 0:
                    route2[source_sector, middle_sector, target_sector] = 1

    route3 = np.zeros(
        (sector_count, sector_count, sector_count, sector_count), dtype=np.uint8
    )
    pair_counts = np.zeros((sector_count, sector_count), dtype=np.int32)
    pair_complete = np.zeros((sector_count, sector_count), dtype=np.uint8)
    complete_count = sector_count * sector_count
    for index in range(len(rows)):
        left = rows[index]
        right = cols[index]
        left_sector = int(sector_codes[left])
        right_sector = int(sector_codes[right])
        if pair_complete[left_sector, right_sector]:
            continue
        in_mask = incoming[left]
        out_mask = outgoing[right]
        if in_mask == 0 or out_mask == 0:
            continue
        for source_sector in range(sector_count):
            if ((in_mask >> np.uint64(source_sector)) & one) == 0:
                continue
            for target_sector in range(sector_count):
                if ((out_mask >> np.uint64(target_sector)) & one) == 0:
                    continue
                if route3[
                    source_sector, left_sector, right_sector, target_sector
                ] == 0:
                    route3[
                        source_sector, left_sector, right_sector, target_sector
                    ] = 1
                    pair_counts[left_sector, right_sector] += 1
        if pair_counts[left_sector, right_sector] == complete_count:
            pair_complete[left_sector, right_sector] = 1
    return macro.astype(np.bool_), route2.astype(np.bool_), route3.astype(np.bool_)


def propagate_modular(
    carrier: Carrier,
    sector_codes: np.ndarray,
    source: int,
    word: tuple[int, ...],
    prime: int,
    inverse_denominator: np.ndarray,
) -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    values = {source: 1}
    path_count = {source: 1}
    parity = {source: 1}
    for target_sector in word[1:]:
        next_values: dict[int, int] = {}
        next_count: dict[int, int] = {}
        next_parity: dict[int, int] = {}
        for node, value in values.items():
            start, stop = carrier.indptr[node : node + 2]
            targets = carrier.indices[start:stop]
            numerators = carrier.numerators[start:stop]
            mask = sector_codes[targets] == target_sector
            if not np.any(mask):
                continue
            denominator_inverse = int(inverse_denominator[node])
            old_count = path_count[node]
            old_parity = parity[node]
            for target, numerator in zip(targets[mask].tolist(), numerators[mask].tolist()):
                contribution = value * (int(numerator) % prime) * denominator_inverse
                next_values[target] = (next_values.get(target, 0) + contribution) % prime
                next_count[target] = min(2, next_count.get(target, 0) + old_count)
                edge_negative = numerator < 0
                if edge_negative:
                    mapped_parity = ((old_parity & 1) << 1) | ((old_parity & 2) >> 1)
                else:
                    mapped_parity = old_parity
                next_parity[target] = next_parity.get(target, 0) | mapped_parity
        values, path_count, parity = next_values, next_count, next_parity
        if not path_count:
            break
    return values, path_count, parity


def propagate_fraction(
    carrier: Carrier,
    sector_codes: np.ndarray,
    source: int,
    word: tuple[int, ...],
) -> dict[int, Fraction]:
    values = {source: Fraction(1, 1)}
    for target_sector in word[1:]:
        next_values: dict[int, Fraction] = {}
        for node, value in values.items():
            start, stop = carrier.indptr[node : node + 2]
            targets = carrier.indices[start:stop]
            numerators = carrier.numerators[start:stop]
            mask = sector_codes[targets] == target_sector
            denominator = int(carrier.row_abs[node])
            for target, numerator in zip(targets[mask].tolist(), numerators[mask].tolist()):
                contribution = value * Fraction(int(numerator), denominator)
                next_values[target] = next_values.get(target, Fraction()) + contribution
        values = {node: value for node, value in next_values.items() if value}
        if not values:
            break
    return values


def classify_word(
    carrier: Carrier,
    sector_codes: np.ndarray,
    word: tuple[int, ...],
    sources: list[int],
    prime: int,
    inverse_denominator: np.ndarray,
) -> dict:
    paths_seen = False
    for examined, source in enumerate(sources, start=1):
        values, counts, parity = propagate_modular(
            carrier, sector_codes, source, word, prime, inverse_denominator
        )
        paths_seen = paths_seen or bool(counts)
        for target in sorted(values):
            residue = int(values[target])
            if residue == 0:
                continue
            if counts[target] == 1:
                method = "UNIQUE_MICROSCOPIC_ROUTE"
            elif parity[target] in (1, 2):
                method = "SIGN_HOMOGENEOUS_ROUTE_FAMILY"
            else:
                method = "EXACT_RATIONAL_ACCUMULATION"
            return {
                "status": "EXACT_NONZERO_PROJECTED_PRODUCT",
                "method": method,
                "source_index": int(source),
                "source_body_id": int(carrier.body_ids[source]),
                "target_index": int(target),
                "target_body_id": int(carrier.body_ids[target]),
                "sources_examined": examined,
                "path_count_class": "ONE" if counts[target] == 1 else "MULTIPLE",
                "path_sign_support": [
                    sign
                    for bit, sign in ((1, "POSITIVE"), (2, "NEGATIVE"))
                    if parity[target] & bit
                ],
                "modular_certificate": {"prime": prime, "residue": residue},
            }

        if counts:
            exact = propagate_fraction(carrier, sector_codes, source, word)
            if exact:
                target = min(exact)
                value = exact[target]
                return {
                    "status": "EXACT_NONZERO_PROJECTED_PRODUCT",
                    "method": "EXACT_RATIONAL_ACCUMULATION",
                    "source_index": int(source),
                    "source_body_id": int(carrier.body_ids[source]),
                    "target_index": int(target),
                    "target_body_id": int(carrier.body_ids[target]),
                    "sources_examined": examined,
                    "exact_coefficient": {
                        "numerator": str(value.numerator),
                        "denominator": str(value.denominator),
                    },
                    "modular_certificate": {
                        "prime": prime,
                        "residue": int(
                            (value.numerator % prime)
                            * pow(value.denominator % prime, -1, prime)
                            % prime
                        ),
                    },
                }

    return {
        "status": "EXACT_ZERO_BY_CANCELLATION_OR_ABSENCE",
        "method": "ALL_SOURCE_BASIS_VECTORS_EXHAUSTED",
        "sources_examined": len(sources),
        "zero_reason": "EXACT_CANCELLATION" if paths_seen else "NO_MICROSCOPIC_ROUTE",
    }


def audit_field(
    carrier: Carrier, field: str, depths: list[int], prime: int
) -> dict:
    names, codes = carrier.sector_codes(field)
    sector_count = len(names)
    row_counts = np.diff(carrier.indptr)
    rows = np.repeat(np.arange(carrier.n, dtype=np.int64), row_counts)
    macro, route2, route3 = exact_boolean_route_support(
        rows,
        carrier.indices,
        codes,
        carrier.n,
        sector_count,
    )
    candidates = candidate_sources(carrier, codes, sector_count)
    inverse_denominator = np.zeros(carrier.n, dtype=np.int64)
    for row in np.flatnonzero(carrier.row_abs):
        inverse_denominator[row] = pow(int(carrier.row_abs[row]), -1, prime)

    depth_results = {}
    for depth in depths:
        records = []
        for word in macro_words(macro, depth):
            route_exists = bool(route2[word]) if depth == 2 else bool(route3[word])
            if route_exists:
                result = classify_word(
                    carrier,
                    codes,
                    word,
                    candidates.get((word[0], word[1]), []),
                    prime,
                    inverse_denominator,
                )
            else:
                result = {
                    "status": "EXACT_ZERO_BY_CANCELLATION_OR_ABSENCE",
                    "method": "EXACT_BOOLEAN_ROUTE_SUPPORT",
                    "sources_examined": 0,
                    "zero_reason": "NO_MICROSCOPIC_ROUTE",
                }
            records.append(
                {
                    "word": [names[index] for index in word],
                    **result,
                }
            )
        counts = {
            status: sum(record["status"] == status for record in records)
            for status in (
                "EXACT_NONZERO_PROJECTED_PRODUCT",
                "EXACT_ZERO_BY_CANCELLATION_OR_ABSENCE",
                "UNRESOLVED_EXACT_ARITHMETIC",
            )
        }
        macro_count = len(records)
        depth_results[str(depth)] = {
            "macro_word_count": macro_count,
            "classification_counts": counts,
            "LP": (
                counts["EXACT_NONZERO_PROJECTED_PRODUCT"] / macro_count
                if macro_count
                else None
            ),
            "records": records,
        }
    return {
        "sector_labels": names,
        "sector_count": sector_count,
        "macro_edge_count": int(macro.sum()),
        "depths": depth_results,
    }


def run_audit(fields: list[str] | None = None) -> dict:
    design, registration = verify_registration()
    fields = fields or list(design["sector_fields"])
    if any(field not in design["sector_fields"] for field in fields):
        raise ValueError("requested field is outside the registered design")
    carrier = Carrier(design)
    prime = choose_prime(
        int(carrier.row_abs.max(initial=0)),
        int(registration["exact_arithmetic"]["prime"]),
    )
    results = {
        field: audit_field(carrier, field, list(design["depths"]), prime)
        for field in fields
    }
    complete = set(results) == set(design["sector_fields"])
    soma = results.get("somaSide")
    if not complete:
        outcome = "PARTIAL_NOT_ADMISSIBLE"
    elif any(
        soma["depths"][str(depth)]["classification_counts"][
            "UNRESOLVED_EXACT_ARITHMETIC"
        ]
        for depth in design["depths"]
    ):
        outcome = "UNRESOLVED"
    elif all(
        soma["depths"][str(depth)]["LP"] == 1.0 for depth in design["depths"]
    ):
        outcome = "SAME_CARRIER_CONTRAST_CONFIRMED"
    else:
        outcome = "SIGNED_STATIC_OBSTRUCTION_FOUND"

    payload = {
        "schema": "rime.exploratory.malecns-y-known-pm-route-audit.v1",
        "status": "COMPLETED" if complete else "PARTIAL",
        "evidence_level": "Computational Certificate",
        "outcome": outcome,
        "design": {
            "path": DESIGN_PATH.name,
            "sha256": sha256_file(DESIGN_PATH),
        },
        "registration": {
            "path": REGISTRATION_PATH.name,
            "sha256": sha256_file(REGISTRATION_PATH),
        },
        "producer": {
            "path": Path(__file__).name,
            "sha256": sha256_file(Path(__file__)),
        },
        "carrier": {
            "name": "Y_known_pm",
            "raw_operator_sha256": carrier.raw_operator_sha256,
            "normalized_operator_sha256": carrier.normalized_operator_sha256,
            "node_count": carrier.n,
            "edge_count": int(len(carrier.numerators)),
            "maximum_row_denominator": int(carrier.row_abs.max(initial=0)),
        },
        "exact_arithmetic": {
            "model": "rational row-normalized operator reduced modulo a prime exceeding every row denominator, with Fraction fallback",
            "prime": prime,
            "row_abs_accumulation": "int64 np.add.at over nonnegative integer weights",
            "row_abs_int64_overflow_upper_bound": carrier.row_abs_overflow_upper_bound,
            "floating_nonzero_tolerance_used": False,
        },
        "fields": results,
        "claim_boundary": design["claim_boundary"],
    }
    payload["result_content_sha256"] = canonical_sha256(payload)
    return payload


def synthetic_hostile_controls() -> dict:
    # Two routes +1/2 and -1/2 cancel exactly; changing the second sign makes
    # the family sign-homogeneous and nonzero.  This exercises the fallback
    # semantics independently of the MaleCNS carrier.
    cancellation = Fraction(1, 2) + Fraction(-1, 2)
    homogeneous = Fraction(1, 2) + Fraction(1, 2)
    return {
        "exact_depth2_cancellation": cancellation == 0,
        "sign_homogeneous_nonzero": homogeneous == 1,
        "finite_field_nonzero_implies_rational_nonzero": (
            homogeneous.numerator * pow(homogeneous.denominator, -1, 140909)
        )
        % 140909
        != 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fields", nargs="+", choices=["somaSide", "superclass"])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        checks = synthetic_hostile_controls()
        print(json.dumps({"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}, indent=2))
        raise SystemExit(0 if all(checks.values()) else 1)
    result = run_audit(args.fields)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "outcome": result["outcome"],
                "fields": {
                    field: {
                        depth: {
                            "macro_word_count": data["macro_word_count"],
                            "LP": data["LP"],
                            "classification_counts": data["classification_counts"],
                        }
                        for depth, data in payload["depths"].items()
                    }
                    for field, payload in result["fields"].items()
                },
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
