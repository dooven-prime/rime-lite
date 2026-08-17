"""Incidence profiles for restricted Rubik generator families.

This module keeps two experiments distinct:

* ``fixed_full`` uses the canonical 18-generator sectors for every family.
* ``endogenous`` recomputes sectors from the selected family and emits an
  explicit overlap alignment back to the canonical sectors.

The code records finite numerical observations.  Exact certificates emitted
here are either combinatorial (cube rotations) or conditional algebraic
identities whose assumptions are serialized with the certificate.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent


def _find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "rime").is_dir():
            return candidate
    raise RuntimeError(f"cannot locate repository root above {start}")


REPO_ROOT = _find_repo_root(HERE)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rime.cubie import BLOCK_RANGES, CubieMove  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


MoveKey = tuple[int, int, int]
Family = tuple[MoveKey, ...]
PHYSICAL_CARRIERS = tuple(BLOCK_RANGES)


@dataclass(frozen=True)
class NumericalPolicy:
    support_atol: float = 1e-8
    rank_atol: float = 1e-12
    rank_rtol: float = 1e-9
    product_atol: float = 1e-12
    product_rtol: float = 1e-10
    alignment_atol: float = 1e-9


@dataclass
class Factor:
    matrix: np.ndarray
    norm: float
    rank: int
    rank_cutoff: float


def all_move_keys() -> Family:
    return tuple(sorted(tuple(map(int, key)) for key in CubieMove.prim_moves))


def normalize_family(keys: Iterable[MoveKey]) -> Family:
    family = tuple(sorted(set(tuple(map(int, key)) for key in keys)))
    unknown = set(family) - set(all_move_keys())
    if unknown:
        raise ValueError(f"unknown Rubik move keys: {sorted(unknown)}")
    if not family:
        raise ValueError("a generator family must not be empty")
    return family


def named_family(name: str) -> Family:
    keys = all_move_keys()
    selectors = {
        "full": lambda k: True,
        "drop_axis0_ht": lambda k: not (k[0] == 0 and k[2] == 2),
        "drop_axis2_ht": lambda k: not (k[0] == 2 and k[2] == 2),
        "quarter_turns": lambda k: k[2] != 2,
        "axes02_qt": lambda k: k[0] != 1 and k[2] != 2,
        "half_turns": lambda k: k[2] == 2,
    }
    try:
        selector = selectors[name]
    except KeyError as exc:
        raise ValueError(f"unknown family {name!r}; choose from {sorted(selectors)}") from exc
    return normalize_family(key for key in keys if selector(key))


def _permutation_sign(permutation: Sequence[int]) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def cube_rotations() -> tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]:
    """Return the 24 orientation-preserving signed axis permutations.

    A rotation is encoded by ``(axis_image, sign)`` with
    ``e_axis -> sign[axis] * e_axis_image[axis]``.
    """
    rotations = []
    for permutation in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            if _permutation_sign(permutation) * math.prod(signs) == 1:
                rotations.append((tuple(permutation), tuple(signs)))
    assert len(rotations) == 24
    return tuple(rotations)


def rotate_move(key: MoveKey, rotation) -> MoveKey:
    permutation, signs = rotation
    axis, side, direction = key
    return permutation[axis], side * signs[axis], direction


def rotate_family(keys: Iterable[MoveKey], rotation) -> Family:
    return normalize_family(rotate_move(key, rotation) for key in keys)


def canonical_family(keys: Iterable[MoveKey]) -> Family:
    family = normalize_family(keys)
    return min(rotate_family(family, rotation) for rotation in cube_rotations())


def rotation_witness(source: Iterable[MoveKey], target: Iterable[MoveKey]):
    source_family = normalize_family(source)
    target_family = normalize_family(target)
    for rotation in cube_rotations():
        if rotate_family(source_family, rotation) == target_family:
            return rotation
    return None


def axis_conjugacy_certificate(source: Iterable[MoveKey], target: Iterable[MoveKey]) -> dict:
    source_family = normalize_family(source)
    target_family = normalize_family(target)
    witness = rotation_witness(source_family, target_family)
    return {
        "claim_status": "Computational Certificate",
        "certificate_kind": "exact_combinatorial",
        "statement": "families lie in the same orientation-preserving cube-rotation orbit",
        "source_family": [list(key) for key in source_family],
        "target_family": [list(key) for key in target_family],
        "rotation": None
        if witness is None
        else {"axis_image": list(witness[0]), "sign": list(witness[1])},
        "verified": witness is not None,
        "profile_invariance_theorem": (
            "If rho is equivariant under the certified cube rotation and the sector "
            "projectors are transported by the same unitary, Frobenius norms, ranks, "
            "protection classes, and carrier-mechanism counts are identical."
        ),
    }


def axis_balanced_families(include_empty: bool = False) -> list[dict]:
    """Enumerate rotation-orbit representatives of axis-balanced families.

    Each axis independently retains neither class, its four quarter turns, its
    two half turns, or both.  This gives 4^3 labelled families before rotation
    quotienting.  Every returned family is inverse closed and treats the two
    opposite faces on an axis equally.
    """
    all_keys = all_move_keys()
    orbits: dict[Family, set[Family]] = {}
    for states in itertools.product(range(4), repeat=3):
        selected = []
        for key in all_keys:
            axis, _side, direction = key
            keep_qt = bool(states[axis] & 1) and direction != 2
            keep_ht = bool(states[axis] & 2) and direction == 2
            if keep_qt or keep_ht:
                selected.append(key)
        if not selected and not include_empty:
            continue
        family = tuple(sorted(selected))
        if not family:
            canonical = family
            images = {family}
        else:
            canonical = canonical_family(family)
            images = {rotate_family(family, rotation) for rotation in cube_rotations()}
        orbits.setdefault(canonical, set()).update(images)

    records = []
    for index, (canonical, images) in enumerate(sorted(orbits.items(), key=lambda x: (len(x[0]), x[0]))):
        records.append(
            {
                "orbit_id": f"axis-balanced-{index:02d}",
                "operator_count": len(canonical),
                "orbit_size": len(images),
                "generator_keys": [list(key) for key in canonical],
            }
        )
    return records


def _operator_for_family(family: Family) -> CubieSpectralOperator:
    moves = {key: CubieMove.prim_moves[key] for key in family}
    return CubieSpectralOperator.from_gens_dict(moves)


def _skew_operators(op: CubieSpectralOperator):
    keys = tuple(tuple(map(int, key)) for key in op.rho_moves)
    matrices = []
    for rho in op.rho_matrices():
        rho = np.asarray(rho, dtype=np.complex128)
        matrices.append((rho - rho.conj().T) / 2.0)
    return keys, matrices


def _sector_descriptors(decomposition: dict) -> list[dict]:
    descriptors = []
    for index, (sector, projector) in enumerate(
        zip(decomposition["sectors"], decomposition["projectors"])
    ):
        carrier_weights = {}
        for carrier, (start, stop) in BLOCK_RANGES.items():
            weight = float(np.trace(projector[start:stop, start:stop]).real)
            if weight > 1e-8:
                carrier_weights[carrier] = weight
        descriptors.append(
            {
                "sector_id": index,
                "dimension": int(round(np.trace(projector).real)),
                "joint_labels": {
                    "lambda_family_scaled": float(sector["lam_18"]),
                    "lambda_qt": float(sector["lam_QT"]),
                    "lambda_ht": float(sector["lam_HT"]),
                },
                "physical_carrier_weights": carrier_weights,
            }
        )
    return descriptors


def sector_alignment(reference: dict, target: dict, atol: float = 1e-9) -> dict:
    """Align two complete decompositions by basis-invariant projector overlap."""
    def near_extremizers(values, extremum):
        return [
            int(index)
            for index, value in enumerate(values)
            if abs(float(value) - float(extremum)) <= atol
        ]

    entries = []
    matrix = np.zeros((len(reference["sector_bases"]), len(target["sector_bases"])))
    for i, ref_basis in enumerate(reference["sector_bases"]):
        for j, target_basis in enumerate(target["sector_bases"]):
            overlap = float(np.linalg.norm(ref_basis.conj().T @ target_basis, "fro") ** 2)
            matrix[i, j] = overlap
            if overlap > atol:
                entries.append(
                    {
                        "reference_sector": i,
                        "target_sector": j,
                        "overlap_dimension": overlap,
                        "reference_fraction": overlap / ref_basis.shape[1],
                        "target_fraction": overlap / target_basis.shape[1],
                    }
                )
    ref_dims = np.array([basis.shape[1] for basis in reference["sector_bases"]], dtype=float)
    target_dims = np.array([basis.shape[1] for basis in target["sector_bases"]], dtype=float)
    target_containment = []
    for j, target_basis in enumerate(target["sector_bases"]):
        residuals = []
        for reference_basis in reference["sector_bases"]:
            projected = reference_basis @ (reference_basis.conj().T @ target_basis)
            residuals.append(float(np.linalg.norm(target_basis - projected, "fro")))
        minimum = min(residuals)
        target_containment.append(
            {
                "target_sector": j,
                "minimum_residual": minimum,
                "minimizing_reference_sectors": near_extremizers(residuals, minimum),
            }
        )
    reference_containment = []
    for i, reference_basis in enumerate(reference["sector_bases"]):
        residuals = []
        for target_basis in target["sector_bases"]:
            projected = target_basis @ (target_basis.conj().T @ reference_basis)
            residuals.append(float(np.linalg.norm(reference_basis - projected, "fro")))
        minimum = min(residuals)
        reference_containment.append(
            {
                "reference_sector": i,
                "minimum_residual": minimum,
                "minimizing_target_sectors": near_extremizers(residuals, minimum),
            }
        )
    target_refines = all(row["minimum_residual"] <= atol for row in target_containment)
    reference_refines = all(row["minimum_residual"] <= atol for row in reference_containment)
    if target_refines and reference_refines:
        relation = "equal_up_to_reindexing"
    elif target_refines:
        relation = "target_refines_reference"
    elif reference_refines:
        relation = "reference_refines_target"
    else:
        relation = "overlapping_non_refinement_frames"
    return {
        "semantics": "trace(P_reference P_target) = ||V_reference^* V_target||_F^2",
        "entries": entries,
        "reference_mass_residual": float(np.max(np.abs(matrix.sum(axis=1) - ref_dims))),
        "target_mass_residual": float(np.max(np.abs(matrix.sum(axis=0) - target_dims))),
        "maximizing_reference_sectors_for_target": [
            near_extremizers(matrix[:, j], np.max(matrix[:, j]))
            for j in range(matrix.shape[1])
        ],
        "maximizing_target_sectors_for_reference": [
            near_extremizers(matrix[i, :], np.max(matrix[i, :]))
            for i in range(matrix.shape[0])
        ],
        "selector_tolerance": atol,
        "containment_atol": atol,
        "relation": relation,
        "target_in_reference_containment": target_containment,
        "reference_in_target_containment": reference_containment,
    }


def _factor(matrix: np.ndarray, policy: NumericalPolicy) -> Factor:
    norm = float(np.linalg.norm(matrix, "fro"))
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    scale = float(singular_values[0]) if singular_values.size else 0.0
    cutoff = max(policy.rank_atol, policy.rank_rtol * scale)
    rank = int(np.count_nonzero(singular_values > cutoff))
    return Factor(matrix=matrix, norm=norm, rank=rank, rank_cutoff=cutoff)


def _build_factor_tables(bases, operators, policy: NumericalPolicy):
    factors = {}
    carrier_factors = {}
    for generator_index, operator in enumerate(operators):
        for i, left_basis in enumerate(bases):
            for j, right_basis in enumerate(bases):
                matrix = left_basis.conj().T @ operator @ right_basis
                factor = _factor(matrix, policy)
                factors[(generator_index, i, j)] = factor
                if factor.norm <= policy.support_atol:
                    continue
                for carrier, (start, stop) in BLOCK_RANGES.items():
                    piece = (
                        left_basis[start:stop].conj().T
                        @ operator[start:stop, start:stop]
                        @ right_basis[start:stop]
                    )
                    carrier_factors[(generator_index, i, j, carrier)] = piece
    return factors, carrier_factors


def _carrier_mechanism(
    left_key,
    right_key,
    carrier_factors,
    policy: NumericalPolicy,
):
    overlap = []
    product_norms = {}
    active_left = {}
    active_right = {}
    for carrier in PHYSICAL_CARRIERS:
        left = carrier_factors.get((*left_key, carrier))
        right = carrier_factors.get((*right_key, carrier))
        left_norm = 0.0 if left is None else float(np.linalg.norm(left, "fro"))
        right_norm = 0.0 if right is None else float(np.linalg.norm(right, "fro"))
        if left_norm > policy.support_atol:
            active_left[carrier] = left
        if right_norm > policy.support_atol:
            active_right[carrier] = right
        if left_norm > policy.support_atol and right_norm > policy.support_atol:
            overlap.append(carrier)
            carrier_product_norm = float(np.linalg.norm(left @ right, "fro"))
            threshold = policy.product_atol + policy.product_rtol * left_norm * right_norm
            product_norms[carrier] = {
                "norm": carrier_product_norm,
                "threshold": threshold,
            }
    cross_carrier_max = 0.0
    for left_carrier, left in active_left.items():
        for right_carrier, right in active_right.items():
            if left_carrier != right_carrier:
                cross_carrier_max = max(
                    cross_carrier_max, float(np.linalg.norm(left @ right, "fro"))
                )
    if not overlap:
        mechanism = "physical_carrier_forced"
    elif all(item["norm"] <= item["threshold"] for item in product_norms.values()):
        mechanism = "within_carrier_image_kernel"
    else:
        mechanism = "numerical_cancellation_or_threshold_conflict"
    return mechanism, overlap, product_norms, cross_carrier_max


def _carrier_commutator_residuals(projectors: Sequence[np.ndarray]) -> dict[str, float]:
    """Check that sector projectors reduce the exact physical carrier split."""
    residuals = {}
    ambient_dimension = projectors[0].shape[0] if projectors else 0
    for carrier, (start, stop) in BLOCK_RANGES.items():
        carrier_projector = np.zeros((ambient_dimension, ambient_dimension), dtype=complex)
        carrier_projector[start:stop, start:stop] = np.eye(stop - start)
        residuals[carrier] = max(
            (
                float(np.linalg.norm(projector @ carrier_projector - carrier_projector @ projector, "fro"))
                for projector in projectors
            ),
            default=0.0,
        )
    return residuals


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _source_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def source_artifact(path: Path) -> dict:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        relative = str(resolved)
    return {
        "path": relative,
        "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
    }


def incidence_census(
    family: Iterable[MoveKey],
    protocol: str,
    *,
    policy: NumericalPolicy | None = None,
    include_carrier_classification: bool = True,
    max_examples_per_class: int = 8,
) -> dict:
    """Compute one complete supported-route class census."""
    policy = policy or NumericalPolicy()
    family = normalize_family(family)
    if protocol not in {"fixed_full", "endogenous"}:
        raise ValueError("protocol must be 'fixed_full' or 'endogenous'")

    family_op = _operator_for_family(family)
    full_op = _operator_for_family(named_family("full"))
    full_decomposition = full_op.center_decomposition()
    decomposition = (
        full_decomposition if protocol == "fixed_full" else family_op.center_decomposition()
    )
    alignment = (
        {
            "semantics": "identity: canonical sectors are fixed",
            "reference_mass_residual": 0.0,
            "target_mass_residual": 0.0,
        }
        if protocol == "fixed_full"
        else sector_alignment(full_decomposition, decomposition, policy.alignment_atol)
    )
    carrier_commutator_residuals = _carrier_commutator_residuals(
        decomposition["projectors"]
    )

    generator_keys, operators = _skew_operators(family_op)
    operator_norms = [float(np.linalg.norm(operator, "fro")) for operator in operators]
    active_generators = [
        index for index, norm in enumerate(operator_norms) if norm > policy.support_atol
    ]
    bases = [np.asarray(basis, dtype=np.complex128) for basis in decomposition["sector_bases"]]
    factors, carrier_factors = _build_factor_tables(bases, operators, policy)

    class_counts = Counter()
    mechanism_counts = Counter()
    triple_counts = Counter()
    hub_counts = Counter()
    rank_signature_counts = Counter()
    examples: dict[str, list] = {}
    maximum_zero_norm = 0.0
    maximum_zero_relative_norm = 0.0
    maximum_cross_carrier_product_norm = 0.0

    for intermediate in range(len(bases)):
        for target in range(len(bases)):
            if target == intermediate:
                continue
            for source in range(len(bases)):
                if source == intermediate:
                    continue
                for g in active_generators:
                    left_key = (g, target, intermediate)
                    left = factors[left_key]
                    if left.norm <= policy.support_atol:
                        continue
                    for h in active_generators:
                        right_key = (h, intermediate, source)
                        right = factors[right_key]
                        if right.norm <= policy.support_atol:
                            continue

                        product_norm = float(np.linalg.norm(left.matrix @ right.matrix, "fro"))
                        product_threshold = (
                            policy.product_atol + policy.product_rtol * left.norm * right.norm
                        )
                        product_nonzero = product_norm > product_threshold
                        left_protected = left.rank == left.matrix.shape[1]
                        right_protected = right.rank == right.matrix.shape[0]
                        if left_protected and right_protected:
                            class_name = "both_protected"
                        elif left_protected:
                            class_name = "left_only"
                        elif right_protected:
                            class_name = "right_only"
                        elif product_nonzero:
                            class_name = "unprotected_nonzero"
                        else:
                            class_name = "unprotected_zero"
                        class_counts[class_name] += 1
                        rank_signature_counts[
                            (
                                left.matrix.shape[0],
                                left.matrix.shape[1],
                                right.matrix.shape[1],
                                left.rank,
                                right.rank,
                                class_name,
                            )
                        ] += 1

                        if class_name != "unprotected_zero":
                            continue
                        triple_counts[(target, intermediate, source)] += 1
                        hub_counts[intermediate] += 1
                        maximum_zero_norm = max(maximum_zero_norm, product_norm)
                        maximum_zero_relative_norm = max(
                            maximum_zero_relative_norm,
                            product_norm / (left.norm * right.norm),
                        )
                        mechanism = "not_computed"
                        overlap = []
                        carrier_products = {}
                        cross_carrier_max = 0.0
                        if include_carrier_classification:
                            mechanism, overlap, carrier_products, cross_carrier_max = _carrier_mechanism(
                                left_key, right_key, carrier_factors, policy
                            )
                            maximum_cross_carrier_product_norm = max(
                                maximum_cross_carrier_product_norm, cross_carrier_max
                            )
                        mechanism_counts[mechanism] += 1
                        bucket = examples.setdefault(mechanism, [])
                        if len(bucket) < max_examples_per_class:
                            bucket.append(
                                {
                                    "sector_triple": [target, intermediate, source],
                                    "generator_pair": [
                                        list(generator_keys[g]),
                                        list(generator_keys[h]),
                                    ],
                                    "dimensions": [
                                        left.matrix.shape[0],
                                        left.matrix.shape[1],
                                        right.matrix.shape[1],
                                    ],
                                    "ranks": [left.rank, right.rank],
                                    "product_norm": product_norm,
                                    "product_threshold": product_threshold,
                                    "overlapping_carriers": overlap,
                                    "carrier_products": carrier_products,
                                    "maximum_cross_carrier_product_norm": cross_carrier_max,
                                }
                            )

    total = sum(class_counts.values())
    unprotected = class_counts["unprotected_nonzero"] + class_counts["unprotected_zero"]
    protected = total - unprotected
    zero = class_counts["unprotected_zero"]
    hub = hub_counts.most_common(1)[0] if hub_counts else (None, 0)

    return {
        "schema": "rime.incidence-profile.v1",
        "claim_status": "Computational Observation",
        "protocol": protocol,
        "family": {
            "generator_keys": [list(key) for key in family],
            "generator_labels": [CubieMove.move_label(key) for key in family],
            "operator_count": len(family),
            "active_skew_operator_count": len(active_generators),
            "zero_skew_operator_keys": [
                list(generator_keys[index])
                for index, norm in enumerate(operator_norms)
                if norm <= policy.support_atol
            ],
            "rotation_canonical_key": [list(key) for key in canonical_family(family)],
        },
        "sector_frame": {
            "sector_count": len(bases),
            "sectors": _sector_descriptors(decomposition),
            "alignment_to_full": alignment,
            "physical_carrier_commutator_residuals": carrier_commutator_residuals,
        },
        "policy": policy.__dict__,
        "counts": {
            "class_counts": dict(sorted(class_counts.items())),
            "total_supported_routes": total,
            "protected_routes": protected,
            "unprotected_routes": unprotected,
            "unprotected_zero": zero,
            "zero_over_all_supported": zero / total if total else None,
            "zero_over_unprotected": zero / unprotected if unprotected else None,
            "protected_fraction": protected / total if total else None,
            "distinct_zero_triples": len(triple_counts),
            "zero_mechanism_counts": dict(sorted(mechanism_counts.items())),
        },
        "zero_profile": {
            "maximum_product_norm": maximum_zero_norm,
            "maximum_relative_product_norm": maximum_zero_relative_norm,
            "maximum_cross_carrier_product_norm": maximum_cross_carrier_product_norm,
            "top_hub": {
                "sector": hub[0],
                "count": hub[1],
                "share": hub[1] / zero if zero else None,
            },
            "triple_counts": [
                {"triple": list(triple), "count": count}
                for triple, count in sorted(triple_counts.items())
            ],
            "examples_by_mechanism": examples,
        },
        "rank_signature_counts": [
            {
                "di": signature[0],
                "dk": signature[1],
                "dj": signature[2],
                "rank_a": signature[3],
                "rank_b": signature[4],
                "class": signature[5],
                "count": count,
            }
            for signature, count in sorted(rank_signature_counts.items())
        ],
        "provenance": {
            "git_commit": _git_commit(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "source_sha256": _source_sha256(),
            "source_artifacts": [
                source_artifact(Path(__file__)),
                source_artifact(REPO_ROOT / "rime" / "base.py"),
                source_artifact(REPO_ROOT / "rime" / "cube.py"),
                source_artifact(REPO_ROOT / "rime" / "cubie.py"),
                source_artifact(REPO_ROOT / "rime" / "cubieoperator.py"),
                source_artifact(REPO_ROOT / "rime" / "helpers.py"),
                source_artifact(REPO_ROOT / "rime" / "spectral_utils.py"),
            ],
            "git_boundary": (
                "The commit identifies the repository baseline. The source-artifact "
                "digests bind the executed producer files, including uncommitted bytes."
            ),
        },
    }


def profile_invariant_signature(profile: dict) -> dict:
    """Return sector-label-independent data used for conjugacy comparisons."""
    sectors = profile["sector_frame"]["sectors"]
    return {
        "protocol": profile["protocol"],
        "sector_dimensions": sorted(sector["dimension"] for sector in sectors),
        "class_counts": profile["counts"]["class_counts"],
        "zero_mechanism_counts": profile["counts"]["zero_mechanism_counts"],
        "rank_signature_counts": sorted(
            (
                row["di"],
                row["dk"],
                row["dj"],
                row["rank_a"],
                row["rank_b"],
                row["class"],
                row["count"],
            )
            for row in profile["rank_signature_counts"]
        ),
    }


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


# ---- Exact Q(sqrt(5)) interpolation identities ---------------------------


@dataclass(frozen=True, order=True)
class Qsqrt5:
    rational: Fraction = Fraction(0)
    radical: Fraction = Fraction(0)

    def __add__(self, other):
        other = as_qsqrt5(other)
        return Qsqrt5(self.rational + other.rational, self.radical + other.radical)

    __radd__ = __add__

    def __neg__(self):
        return Qsqrt5(-self.rational, -self.radical)

    def __sub__(self, other):
        return self + (-as_qsqrt5(other))

    def __rsub__(self, other):
        return as_qsqrt5(other) - self

    def __mul__(self, other):
        other = as_qsqrt5(other)
        return Qsqrt5(
            self.rational * other.rational + 5 * self.radical * other.radical,
            self.rational * other.radical + self.radical * other.rational,
        )

    __rmul__ = __mul__

    def inverse(self):
        denominator = self.rational * self.rational - 5 * self.radical * self.radical
        if denominator == 0:
            raise ZeroDivisionError("zero divisor in Q(sqrt(5))")
        return Qsqrt5(self.rational / denominator, -self.radical / denominator)

    def __truediv__(self, other):
        return self * as_qsqrt5(other).inverse()

    def __float__(self):
        return float(self.rational) + float(self.radical) * math.sqrt(5.0)

    def to_json(self):
        return {
            "rational": str(self.rational),
            "sqrt5": str(self.radical),
            "expression": self.expression(),
        }

    def expression(self):
        if self.radical == 0:
            return str(self.rational)
        if self.rational == 0:
            return f"({self.radical})*sqrt(5)"
        return f"({self.rational}) + ({self.radical})*sqrt(5)"


def as_qsqrt5(value) -> Qsqrt5:
    if isinstance(value, Qsqrt5):
        return value
    return Qsqrt5(Fraction(value), Fraction(0))


def recognize_qsqrt5(value: float, max_denominator: int = 36, atol: float = 1e-8):
    candidates = []
    rational = Fraction(value).limit_denominator(max_denominator)
    candidates.append(Qsqrt5(rational, Fraction(0)))
    for denominator in range(1, max_denominator + 1):
        for numerator in range(-2 * denominator, 2 * denominator + 1):
            radical = Fraction(numerator, denominator)
            remaining = value - float(radical) * math.sqrt(5.0)
            rational = Fraction(remaining).limit_denominator(max_denominator)
            candidates.append(Qsqrt5(rational, radical))
    best = min(candidates, key=lambda candidate: abs(float(candidate) - value))
    return best if abs(float(best) - value) <= atol else None


def _poly_mul(left: list[Qsqrt5], right: list[Qsqrt5]) -> list[Qsqrt5]:
    result = [Qsqrt5() for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = result[i + j] + a * b
    return result


def _poly_eval(coefficients: list[Qsqrt5], value: Qsqrt5) -> Qsqrt5:
    result = Qsqrt5()
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def lagrange_projector_certificate(eigenvalues: Sequence[Qsqrt5]) -> dict:
    if len(set(eigenvalues)) != len(eigenvalues):
        raise ValueError("separating eigenvalues must be distinct")
    projectors = []
    verified = True
    for index, eigenvalue in enumerate(eigenvalues):
        coefficients = [as_qsqrt5(1)]
        denominator = as_qsqrt5(1)
        for other_index, other in enumerate(eigenvalues):
            if other_index == index:
                continue
            coefficients = _poly_mul(coefficients, [-other, as_qsqrt5(1)])
            denominator = denominator * (eigenvalue - other)
        coefficients = [coefficient / denominator for coefficient in coefficients]
        evaluations = [_poly_eval(coefficients, item) for item in eigenvalues]
        expected = [as_qsqrt5(int(j == index)) for j in range(len(eigenvalues))]
        verified = verified and evaluations == expected
        projectors.append(
            {
                "sector": index,
                "polynomial_coefficients_low_to_high": [item.to_json() for item in coefficients],
                "evaluations": [item.to_json() for item in evaluations],
            }
        )
    return {
        "claim_status": "Computational Certificate",
        "certificate_kind": "conditional_exact_algebraic",
        "field": "Q(sqrt(5))",
        "verified_interpolation_identity": verified,
        "separating_eigenvalues": [item.to_json() for item in eigenvalues],
        "projector_polynomials": projectors,
        "statement": "P_j = product_{l != j}(M-mu_l I)/(mu_j-mu_l)",
        "assumptions": [
            "M is diagonalizable over Q(sqrt(5), zeta_3)",
            "the supplied mu_j are the complete exact distinct spectrum of M",
            "the target sector is the mu_j eigenspace",
        ],
        "promotion_boundary": (
            "Exact interpolation is verified. Numerical recognition of the spectrum "
            "does not discharge the serialized exact-spectrum assumptions."
        ),
    }
