"""Generic carrier-resolved support and routed-composition engine.

The engine deliberately works with actual matrix products. Boolean support is
used only for candidate paths; every active-depth result is backed by an
explicit routed product and a declared tolerance.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable

import numpy as np


def _boolean_matrix_product(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Compose relations over the Boolean semiring without integer counts."""
    left = np.asarray(left, dtype=bool)
    right = np.asarray(right, dtype=bool)
    if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
        raise ValueError("Boolean relation factors have incompatible shapes")
    result = np.zeros((left.shape[0], right.shape[1]), dtype=bool)
    for middle in range(left.shape[1]):
        result |= left[:, middle, None] & right[middle, None, :]
    return result


def _boolean_matrix_power(adjacency: np.ndarray, depth: int) -> np.ndarray:
    """Return exact-length reachability without fixed-width path-count overflow."""
    adjacency = np.asarray(adjacency, dtype=bool)
    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
        raise ValueError("adjacency must be square")
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    result = np.eye(adjacency.shape[0], dtype=bool)
    base = adjacency
    exponent = depth
    while exponent:
        if exponent & 1:
            result = _boolean_matrix_product(result, base)
        exponent >>= 1
        if exponent:
            base = _boolean_matrix_product(base, base)
    return result


@dataclass(frozen=True)
class CensusResult:
    carrier_profiles: list[dict]
    direct_support: list[list[float]]
    support_edge_count: int
    routed_counts: dict[int, int]
    active_route_counts: dict[int, int]
    support_path_pair_counts: dict[int, int]
    carrier_path_pair_counts: dict[int, int]
    composition_pair_counts: dict[int, int]
    obstructed_pair_counts: dict[int, int]
    obstructed_pairs: dict[int, list[list[int]]]
    cross_carrier_stitch_pair_counts: dict[int, int]
    cross_carrier_stitch_pairs: dict[int, list[list[int]]]
    within_carrier_obstructed_pair_counts: dict[int, int]
    within_carrier_obstructed_pairs: dict[int, list[list[int]]]
    carrier_disjoint_pair_count: int
    carrier_disjoint_pairs: list[list[int]]
    unresolved_overlapping_pair_count: int
    minimum_active_depth_within_bound: dict[str, int | None]


class CarrierAccessibility:
    """Analyze a finite transport/sector/carrier realization."""

    def __init__(
        self,
        transports: Iterable[np.ndarray],
        sector_projectors: Iterable[np.ndarray],
        carrier_projectors: Iterable[np.ndarray],
        *,
        tolerance: float = 1e-10,
        support_tolerance: float = 1e-10,
    ) -> None:
        self.transports = [np.asarray(x, dtype=np.complex128) for x in transports]
        self.sectors = [np.asarray(x, dtype=np.complex128) for x in sector_projectors]
        self.carriers = [np.asarray(x, dtype=np.complex128) for x in carrier_projectors]
        self.tolerance = tolerance
        self.support_tolerance = support_tolerance
        if not self.transports or not self.sectors or not self.carriers:
            raise ValueError("transports, sectors, and carriers must be nonempty")
        shape = self.transports[0].shape
        if shape[0] != shape[1]:
            raise ValueError("transport maps must be square")
        if any(x.shape != shape for x in self.transports + self.sectors + self.carriers):
            raise ValueError("all operators must have the same shape")
        self._validate_commutation()
        self._sector_bases = self._build_sector_bases()
        self._transport_blocks = self._build_transport_blocks()
        self._carrier_sector_blocks = self._build_carrier_sector_blocks()
        self._carrier_direct_support_cache: np.ndarray | None = None

    @property
    def dimension(self) -> int:
        return self.transports[0].shape[0]

    @property
    def sector_count(self) -> int:
        return len(self.sectors)

    def _validate_commutation(self) -> None:
        identity = np.eye(self.dimension, dtype=np.complex128)
        carrier_sum = sum(self.carriers, start=np.zeros_like(identity))
        if np.linalg.norm(carrier_sum - identity, "fro") > self.tolerance:
            raise ValueError("carrier projectors are not complete")
        sector_sum = sum(self.sectors, start=np.zeros_like(identity))
        if np.linalg.norm(sector_sum - identity, "fro") > self.tolerance:
            raise ValueError("sector projectors are not complete")
        for i, sector in enumerate(self.sectors):
            if np.linalg.norm(sector - sector.conj().T, "fro") > self.tolerance:
                raise ValueError("computational engine requires orthogonal sector projectors")
            if np.linalg.norm(sector @ sector - sector, "fro") > self.tolerance:
                raise ValueError("sector operator is not idempotent")
            for other in self.sectors[i + 1 :]:
                if np.linalg.norm(sector @ other, "fro") > self.tolerance:
                    raise ValueError("sector projectors are not pairwise orthogonal")
        for carrier in self.carriers:
            for operator in self.transports + self.sectors:
                if np.linalg.norm(operator @ carrier - carrier @ operator, "fro") > self.tolerance:
                    raise ValueError("transport/sector operator does not preserve carriers")

    def _build_sector_bases(self) -> list[np.ndarray]:
        bases = []
        for sector in self.sectors:
            eigenvalues, eigenvectors = np.linalg.eigh(sector)
            basis = eigenvectors[:, eigenvalues > 0.5]
            bases.append(basis)
        return bases

    def _build_transport_blocks(self) -> list[list[list[np.ndarray]]]:
        return [
            [
                [left.conj().T @ transport @ right for right in self._sector_bases]
                for left in self._sector_bases
            ]
            for transport in self.transports
        ]

    def _build_carrier_sector_blocks(self) -> list[list[np.ndarray]]:
        return [
            [basis.conj().T @ carrier @ basis for basis in self._sector_bases]
            for carrier in self.carriers
        ]

    def block_norm(self, sector_i: int, transport: np.ndarray, sector_j: int) -> float:
        return float(np.linalg.norm(self.sectors[sector_i] @ transport @ self.sectors[sector_j], "fro"))

    def direct_support(self) -> np.ndarray:
        values = np.zeros((self.sector_count, self.sector_count), dtype=float)
        for transport_index in range(len(self.transports)):
            for i in range(self.sector_count):
                for j in range(self.sector_count):
                    values[i, j] = max(
                        values[i, j],
                        float(np.linalg.norm(self._transport_blocks[transport_index][i][j], "fro")),
                    )
        return values

    def carrier_direct_support(self) -> np.ndarray:
        """Return per-carrier support in [carrier, target, source] order."""
        if self._carrier_direct_support_cache is not None:
            return self._carrier_direct_support_cache.copy()
        values = np.zeros(
            (len(self.carriers), self.sector_count, self.sector_count),
            dtype=float,
        )
        for carrier_index, sector_blocks in enumerate(self._carrier_sector_blocks):
            for transport_index in range(len(self.transports)):
                for target in range(self.sector_count):
                    left = sector_blocks[target]
                    for source in range(self.sector_count):
                        block = (
                            left
                            @ self._transport_blocks[transport_index][target][source]
                            @ sector_blocks[source]
                        )
                        values[carrier_index, target, source] = max(
                            values[carrier_index, target, source],
                            float(np.linalg.norm(block, "fro")),
                        )
        self._carrier_direct_support_cache = values
        return values.copy()

    def carrier_support(self, sector: int) -> list[int]:
        return [
            b
            for b, carrier in enumerate(self.carriers)
            if np.linalg.norm(carrier @ self.sectors[sector], "fro") > self.support_tolerance
        ]

    def carrier_profile(self, sector: int) -> dict:
        ranks = [
            int(np.linalg.matrix_rank(carrier @ self.sectors[sector], tol=self.tolerance))
            for carrier in self.carriers
        ]
        support = [b for b, rank in enumerate(ranks) if rank > 0]
        return {
            "sector": sector,
            "rank": int(np.linalg.matrix_rank(self.sectors[sector], tol=self.tolerance)),
            "carrier_ranks": ranks,
            "carrier_support": support,
            "profile_kind": "empty" if not support else ("pure" if len(support) == 1 else "hybrid"),
        }

    def route_product(
        self,
        endpoint_i: int,
        endpoint_j: int,
        transport_indices: tuple[int, ...],
        intermediate_sectors: tuple[int, ...] = (),
    ) -> np.ndarray:
        depth = len(transport_indices)
        if depth == 0:
            return self.sectors[endpoint_i] @ self.sectors[endpoint_j]
        if len(intermediate_sectors) != depth - 1:
            raise ValueError("one fewer intermediate sector is required")
        factors: list[np.ndarray] = [self.sectors[endpoint_j]]
        for step, transport_index in enumerate(transport_indices):
            factors.append(self.transports[transport_index])
            if step < depth - 1:
                factors.append(self.sectors[intermediate_sectors[step]])
        factors.append(self.sectors[endpoint_i])
        result = factors[0]
        for factor in factors[1:]:
            result = factor @ result
        return result

    def reduced_route_product(
        self,
        endpoint_i: int,
        endpoint_j: int,
        transport_indices: tuple[int, ...],
        intermediate_sectors: tuple[int, ...] = (),
    ) -> np.ndarray:
        """Represent the routed product between orthonormal sector bases."""
        depth = len(transport_indices)
        if depth == 0:
            return self._sector_bases[endpoint_i].conj().T @ self._sector_bases[endpoint_j]
        if len(intermediate_sectors) != depth - 1:
            raise ValueError("one fewer intermediate sector is required")
        chain = (endpoint_j,) + intermediate_sectors + (endpoint_i,)
        result = self._transport_blocks[transport_indices[0]][chain[1]][chain[0]]
        for step in range(1, depth):
            block = self._transport_blocks[transport_indices[step]][chain[step + 1]][chain[step]]
            result = block @ result
        return result

    def reduced_transport_block(
        self, transport_index: int, target_sector: int, source_sector: int
    ) -> np.ndarray:
        """Return one projected transport in orthonormal sector coordinates."""
        return self._transport_blocks[transport_index][target_sector][source_sector].copy()

    def carrier_reduced_transport_block(
        self,
        carrier_index: int,
        transport_index: int,
        target_sector: int,
        source_sector: int,
    ) -> np.ndarray:
        """Return one projected transport restricted to a declared carrier."""
        target_carrier = self._carrier_sector_blocks[carrier_index][target_sector]
        source_carrier = self._carrier_sector_blocks[carrier_index][source_sector]
        block = self._transport_blocks[transport_index][target_sector][source_sector]
        return target_carrier @ block @ source_carrier

    def route_factors(
        self,
        endpoint_i: int,
        endpoint_j: int,
        transport_indices: tuple[int, ...],
        intermediate_sectors: tuple[int, ...] = (),
    ) -> list[np.ndarray]:
        """Return factors in application order, from source to target."""
        depth = len(transport_indices)
        if len(intermediate_sectors) != max(0, depth - 1):
            raise ValueError("one fewer intermediate sector is required")
        factors = [self.sectors[endpoint_j]]
        for step, transport_index in enumerate(transport_indices):
            factors.append(self.transports[transport_index])
            if step < depth - 1:
                factors.append(self.sectors[intermediate_sectors[step]])
        factors.append(self.sectors[endpoint_i])
        return factors

    @staticmethod
    def _compose_application_order(factors: list[np.ndarray]) -> np.ndarray:
        result = factors[0]
        for factor in factors[1:]:
            result = factor @ result
        return result

    def image_kernel_obstruction(
        self,
        endpoint_i: int,
        endpoint_j: int,
        transport_indices: tuple[int, ...],
        intermediate_sectors: tuple[int, ...],
        *,
        cut_after_transport: int,
    ) -> dict:
        """Numerically certify the image-kernel condition at an internal cut.

        The cut is after transport r and its following intermediate projector,
        for 1 <= r < depth. The returned residual is ||A U_B||_F, where U_B
        is an orthonormal basis for im(B).
        """
        depth = len(transport_indices)
        if not 1 <= cut_after_transport < depth:
            raise ValueError("cut_after_transport must be internal")
        factors = self.route_factors(
            endpoint_i, endpoint_j, transport_indices, intermediate_sectors
        )
        cut_factor = 2 * cut_after_transport
        prefix = self._compose_application_order(factors[: cut_factor + 1])
        suffix = self._compose_application_order(
            [np.eye(self.dimension, dtype=np.complex128)] + factors[cut_factor + 1 :]
        )
        u, singular_values, _ = np.linalg.svd(prefix, full_matrices=False)
        rank = int(np.count_nonzero(singular_values > self.tolerance))
        image_basis = u[:, :rank]
        residual = float(np.linalg.norm(suffix @ image_basis, "fro")) if rank else 0.0
        product_matrix = suffix @ prefix
        return {
            "cut_after_transport": cut_after_transport,
            "prefix_rank": rank,
            "suffix_rank": int(np.linalg.matrix_rank(suffix, tol=self.tolerance)),
            "product_norm": float(np.linalg.norm(product_matrix, "fro")),
            "image_kernel_residual": residual,
            "obstructed": residual <= self.tolerance,
        }

    def enumerate_depth(self, depth: int) -> tuple[int, int]:
        """Return (candidate routes, nonzero routed products) at one depth."""
        if depth < 1:
            raise ValueError("depth must be positive")
        candidates = 0
        active = 0
        for i, j in product(range(self.sector_count), repeat=2):
            for transports in product(range(len(self.transports)), repeat=depth):
                for intermediates in product(range(self.sector_count), repeat=depth - 1):
                    candidates += 1
                    if np.linalg.norm(self.reduced_route_product(i, j, transports, intermediates), "fro") > self.tolerance:
                        active += 1
        return candidates, active

    def minimum_active_depth(self, max_depth: int = 2) -> dict[str, int | None]:
        """Find first active depth for each ordered sector pair by enumeration."""
        answer: dict[str, int | None] = {
            f"{j}->{i}": None for i, j in product(range(self.sector_count), repeat=2)
        }
        for depth in range(1, max_depth + 1):
            for i, j in product(range(self.sector_count), repeat=2):
                key = f"{j}->{i}"
                if answer[key] is not None:
                    continue
                for transports in product(range(len(self.transports)), repeat=depth):
                    for intermediates in product(range(self.sector_count), repeat=depth - 1):
                        if np.linalg.norm(self.reduced_route_product(i, j, transports, intermediates), "fro") > self.tolerance:
                            answer[key] = depth
                            break
                    if answer[key] is not None:
                        break
        return answer

    def reachability_at_depth(self, depth: int) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        """Return Boolean support-path pairs and actual routed-product pairs."""
        adjacency = self.direct_support() > self.support_tolerance
        support_paths = _boolean_matrix_power(adjacency, depth)
        candidate_pairs = {
            (j, i)
            for i, j in product(range(self.sector_count), repeat=2)
            if support_paths[i, j]
        }
        active_pairs: set[tuple[int, int]] = set()
        for j, i in candidate_pairs:
            for transports in product(range(len(self.transports)), repeat=depth):
                for intermediates in product(range(self.sector_count), repeat=depth - 1):
                    if np.linalg.norm(self.reduced_route_product(i, j, transports, intermediates), "fro") > self.tolerance:
                        active_pairs.add((j, i))
                        break
                if (j, i) in active_pairs:
                    break
        return candidate_pairs, active_pairs

    def carrier_path_pairs_at_depth(self, depth: int) -> set[tuple[int, int]]:
        """Return pairs joined at the given depth inside at least one carrier."""
        pairs: set[tuple[int, int]] = set()
        for support in self.carrier_direct_support():
            adjacency = support > self.support_tolerance
            paths = _boolean_matrix_power(adjacency, depth)
            pairs.update(
                (source, target)
                for target, source in product(range(self.sector_count), repeat=2)
                if paths[target, source]
            )
        return pairs

    def census(self, max_depth: int = 2) -> CensusResult:
        direct = self.direct_support()
        routed_counts: dict[int, int] = {}
        active_counts: dict[int, int] = {}
        support_path_counts: dict[int, int] = {}
        carrier_path_counts: dict[int, int] = {}
        composition_counts: dict[int, int] = {}
        obstruction_counts: dict[int, int] = {}
        obstruction_pairs: dict[int, list[list[int]]] = {}
        cross_carrier_counts: dict[int, int] = {}
        cross_carrier_pairs: dict[int, list[list[int]]] = {}
        within_carrier_counts: dict[int, int] = {}
        within_carrier_pairs: dict[int, list[list[int]]] = {}
        for depth in range(1, max_depth + 1):
            candidates, active = self.enumerate_depth(depth)
            routed_counts[depth] = candidates
            active_counts[depth] = active
            support_pairs, composition_pairs = self.reachability_at_depth(depth)
            carrier_pairs = self.carrier_path_pairs_at_depth(depth)
            if not composition_pairs <= carrier_pairs <= support_pairs:
                raise AssertionError("carrier reachability sandwich failed")
            obstructed = sorted(support_pairs - composition_pairs)
            cross_carrier = sorted(support_pairs - carrier_pairs)
            within_carrier = sorted(carrier_pairs - composition_pairs)
            support_path_counts[depth] = len(support_pairs)
            carrier_path_counts[depth] = len(carrier_pairs)
            composition_counts[depth] = len(composition_pairs)
            obstruction_counts[depth] = len(obstructed)
            obstruction_pairs[depth] = [list(pair) for pair in obstructed]
            cross_carrier_counts[depth] = len(cross_carrier)
            cross_carrier_pairs[depth] = [list(pair) for pair in cross_carrier]
            within_carrier_counts[depth] = len(within_carrier)
            within_carrier_pairs[depth] = [list(pair) for pair in within_carrier]
        profiles = [self.carrier_profile(i) for i in range(self.sector_count)]
        support_sets = {
            profile["sector"]: set(profile["carrier_support"]) for profile in profiles
        }
        carrier_disjoint = [
            [source, target]
            for source, target in product(range(self.sector_count), repeat=2)
            if not support_sets[source] & support_sets[target]
        ]
        minimum_depth = self.minimum_active_depth(max_depth)
        unresolved_overlapping = sum(
            1
            for key, value in minimum_depth.items()
            if value is None
            and support_sets[int(key.split("->")[0])] & support_sets[int(key.split("->")[1])]
        )
        return CensusResult(
            carrier_profiles=profiles,
            direct_support=direct.tolist(),
            support_edge_count=int(np.count_nonzero(direct > self.support_tolerance)),
            routed_counts=routed_counts,
            active_route_counts=active_counts,
            support_path_pair_counts=support_path_counts,
            carrier_path_pair_counts=carrier_path_counts,
            composition_pair_counts=composition_counts,
            obstructed_pair_counts=obstruction_counts,
            obstructed_pairs=obstruction_pairs,
            cross_carrier_stitch_pair_counts=cross_carrier_counts,
            cross_carrier_stitch_pairs=cross_carrier_pairs,
            within_carrier_obstructed_pair_counts=within_carrier_counts,
            within_carrier_obstructed_pairs=within_carrier_pairs,
            carrier_disjoint_pair_count=len(carrier_disjoint),
            carrier_disjoint_pairs=carrier_disjoint,
            unresolved_overlapping_pair_count=unresolved_overlapping,
            minimum_active_depth_within_bound=minimum_depth,
        )
