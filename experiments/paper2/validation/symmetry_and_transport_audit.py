"""Audit the symmetry/transport boundary for the canonical Rubik realization.

This script supports claim C0-G-COMMUTANT. It checks five independent facts:

1. A_18, QT_all, and HT_all are not in End_G(V).
2. Only the lambda=1 spectral layer is G-invariant.
3. The 24 orientation-preserving cube rotations act by external covariance and
   preserve A_18, QT_all, and HT_all.
4. The orientation-reversing symmetries have no complex-linear intertwiner on
   the CO block for the tested geometric automorphism.
5. The cubie-legality lifts contain a sector-preserving subgroup
   H isomorphic to A4 x C2. This H is not normal in G.

The script rebuilds rho in complex128 so that the CO root-of-unity arithmetic
is not limited by the complex64 dtype used by CubieMove.rho().
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from collections import Counter

import numpy as np
from scipy.linalg import block_diag

from rime.cube import CubeBase
from rime.cubie import CubieMove


TOL = 1e-10
OMEGA = np.exp(2j * np.pi / 3)
CORNER_POSITIONS = np.asarray(CubeBase.CORNER_POS_SIGNS, dtype=int)
EDGE_POSITIONS = np.asarray(CubeBase.EDGE_POS_SIGNS, dtype=int)


def permutation_matrix(perm: np.ndarray) -> np.ndarray:
    matrix = np.zeros((len(perm), len(perm)), dtype=np.complex128)
    matrix[perm, np.arange(len(perm))] = 1.0
    return matrix


def rho128(move: CubieMove) -> np.ndarray:
    cp = np.kron(permutation_matrix(move.corners_perm), np.eye(8))
    ep = np.kron(permutation_matrix(move.edges_perm), np.eye(12))

    co = np.zeros((8, 8), dtype=np.complex128)
    co[move.corners_perm, np.arange(8)] = OMEGA ** move.corners_ori_delta.astype(int)

    eo = np.zeros((12, 12), dtype=np.complex128)
    eo[move.edges_perm, np.arange(12)] = (-1.0) ** move.edges_ori_delta.astype(int)
    return block_diag(cp, ep, co, eo)


def move_key(move: CubieMove) -> tuple[tuple[int, ...], ...]:
    """Return a dtype-independent key.

    CubieMove.__hash__ includes ndarray bytes and therefore distinguishes equal
    integer arrays with different dtypes. Audit sets must not rely on that hash.
    """

    return (
        tuple(map(int, move.corners_perm)),
        tuple(map(int, move.edges_perm)),
        tuple(map(int, move.corners_ori_delta)),
        tuple(map(int, move.edges_ori_delta)),
    )


def permutation_parity(perm: np.ndarray) -> int:
    return sum(
        int(perm[i] > perm[j])
        for i in range(len(perm))
        for j in range(i + 1, len(perm))
    ) % 2


def position_permutation(rotation: np.ndarray, positions: np.ndarray) -> np.ndarray:
    lookup = {tuple(position): i for i, position in enumerate(positions)}
    return np.asarray(
        [lookup[tuple(rotation @ position)] for position in positions],
        dtype=np.int8,
    )


def rotation_key(rotation: np.ndarray) -> tuple[int, ...]:
    return tuple(map(int, rotation.reshape(-1)))


def mapped_generator(
    rotation: np.ndarray,
    generator: tuple[int, int, int],
    *,
    include_orientation_reversal: bool = False,
) -> tuple[int, int, int]:
    axis, side, direction = generator
    image = rotation[:, axis]
    image_axis = int(np.argmax(np.abs(image)))
    axis_sign = int(image[image_axis])
    determinant = int(round(np.linalg.det(rotation)))
    direction_sign = determinant if include_orientation_reversal else 1
    mapped_direction = 2 if direction == 2 else direction_sign * axis_sign * direction
    return image_axis, axis_sign * side, mapped_direction


def block_matrix(move: CubieMove, block: str) -> np.ndarray:
    if block == "co":
        matrix = np.zeros((8, 8), dtype=np.complex128)
        matrix[move.corners_perm, np.arange(8)] = (
            OMEGA ** move.corners_ori_delta.astype(int)
        )
        return matrix
    if block == "eo":
        matrix = np.zeros((12, 12), dtype=np.complex128)
        matrix[move.edges_perm, np.arange(12)] = (
            (-1.0) ** move.edges_ori_delta.astype(int)
        )
        return matrix
    raise ValueError(f"unsupported block: {block}")


def gauge_exponents(
    rotation: np.ndarray,
    moves: dict[tuple[int, int, int], CubieMove],
    block: str,
) -> np.ndarray:
    positions = CORNER_POSITIONS if block == "co" else EDGE_POSITIONS
    rotation_perm = position_permutation(rotation, positions)
    rows: list[np.ndarray] = []

    for generator, move in moves.items():
        mapped_move = moves[mapped_generator(rotation, generator)]
        if block == "co":
            perm = move.corners_perm
            mapped_perm = mapped_move.corners_perm
            phase = OMEGA ** move.corners_ori_delta.astype(int)
            mapped_phase = OMEGA ** mapped_move.corners_ori_delta.astype(int)
        else:
            perm = move.edges_perm
            mapped_perm = mapped_move.edges_perm
            phase = (-1.0) ** move.edges_ori_delta.astype(int)
            mapped_phase = (-1.0) ** mapped_move.edges_ori_delta.astype(int)

        assert np.array_equal(rotation_perm[perm], mapped_perm[rotation_perm])
        for i in range(len(positions)):
            row = np.zeros(len(positions), dtype=np.complex128)
            row[perm[i]] = phase[i]
            row[i] -= mapped_phase[rotation_perm[i]]
            rows.append(row)

    _, singular_values, vh = np.linalg.svd(np.vstack(rows))
    assert np.sum(singular_values < TOL) == 1
    gauge = vh.conj().T[:, -1]
    gauge /= gauge[0]
    roots = np.asarray([1, OMEGA, OMEGA**2]) if block == "co" else np.asarray([1, -1])
    return np.asarray([np.argmin(np.abs(roots - value)) for value in gauge], dtype=np.int8)


def rotation_intertwiner(
    rotation: np.ndarray,
    moves: dict[tuple[int, int, int], CubieMove],
) -> np.ndarray:
    corner_perm = position_permutation(rotation, CORNER_POSITIONS)
    edge_perm = position_permutation(rotation, EDGE_POSITIONS)
    cp = np.kron(permutation_matrix(corner_perm), np.eye(8))
    ep = np.kron(permutation_matrix(edge_perm), np.eye(12))

    co_exp = gauge_exponents(rotation, moves, "co")
    eo_exp = gauge_exponents(rotation, moves, "eo")
    co = permutation_matrix(corner_perm) @ np.diag(OMEGA**co_exp)
    eo = permutation_matrix(edge_perm) @ np.diag((-1.0) ** eo_exp)
    return block_diag(cp, ep, co, eo)


def solve_scalar_cocycle(
    rotations: list[np.ndarray],
    labels: list[int],
    modulus: int,
) -> np.ndarray:
    """Find scalar rephasings that remove a finite modular cocycle."""

    indices = {rotation_key(rotation): i for i, rotation in enumerate(rotations)}
    rows = []
    for i, left in enumerate(rotations):
        for j, right in enumerate(rotations):
            product_index = indices[rotation_key(left @ right)]
            row = np.zeros(len(rotations) + 1, dtype=int)
            row[i] += 1
            row[j] += 1
            row[product_index] -= 1
            row[-1] = -labels[i * len(rotations) + j]
            rows.append(row % modulus)

    identity_index = indices[rotation_key(np.eye(3, dtype=int))]
    identity_row = np.zeros(len(rotations) + 1, dtype=int)
    identity_row[identity_index] = 1
    rows.append(identity_row)

    augmented = np.asarray(rows, dtype=int) % modulus
    pivot_row = 0
    pivots = []
    for column in range(len(rotations)):
        selected = next(
            (
                row
                for row in range(pivot_row, len(augmented))
                if augmented[row, column] % modulus
            ),
            None,
        )
        if selected is None:
            continue
        augmented[[pivot_row, selected]] = augmented[[selected, pivot_row]]
        inverse = pow(int(augmented[pivot_row, column]), -1, modulus)
        augmented[pivot_row] = augmented[pivot_row] * inverse % modulus
        for row in range(len(augmented)):
            if row != pivot_row and augmented[row, column] % modulus:
                augmented[row] = (
                    augmented[row]
                    - augmented[row, column] * augmented[pivot_row]
                ) % modulus
        pivots.append(column)
        pivot_row += 1

    inconsistent = any(
        np.all(row[:-1] % modulus == 0) and row[-1] % modulus
        for row in augmented
    )
    assert not inconsistent

    solution = np.zeros(len(rotations), dtype=int)
    for row, column in enumerate(pivots):
        solution[column] = augmented[row, -1] % modulus
    return solution


def make_rotation_representation(
    rotations: list[np.ndarray],
    intertwiners: list[np.ndarray],
) -> tuple[list[np.ndarray], float, float]:
    """Rephase independently normalized intertwiners into an O-representation."""

    indices = {rotation_key(rotation): i for i, rotation in enumerate(rotations)}
    third_roots = np.asarray([1, OMEGA, OMEGA**2])
    labels_mod_3 = []
    labels_mod_2 = []
    cocycle_residuals = []

    for i, left in enumerate(rotations):
        for j, right in enumerate(rotations):
            product_index = indices[rotation_key(left @ right)]
            defect = (
                intertwiners[i]
                @ intertwiners[j]
                @ intertwiners[product_index].conj().T
            )
            co_scalar = np.trace(defect[208:216, 208:216]) / 8
            eo_scalar = np.trace(defect[216:228, 216:228]) / 12
            co_label = int(np.argmin(np.abs(third_roots - co_scalar)))
            eo_label = 0 if abs(eo_scalar - 1) < abs(eo_scalar + 1) else 1
            labels_mod_3.append(co_label)
            labels_mod_2.append(eo_label)

            model = np.eye(228, dtype=np.complex128)
            model[208:216, 208:216] *= third_roots[co_label]
            model[216:228, 216:228] *= (-1) ** eo_label
            cocycle_residuals.append(np.linalg.norm(defect - model, "fro"))

    phases_mod_3 = solve_scalar_cocycle(rotations, labels_mod_3, 3)
    phases_mod_2 = solve_scalar_cocycle(rotations, labels_mod_2, 2)
    representation = []
    for i, intertwiner in enumerate(intertwiners):
        rephasing = np.eye(228, dtype=np.complex128)
        rephasing[208:216, 208:216] *= third_roots[phases_mod_3[i]]
        rephasing[216:228, 216:228] *= (-1) ** phases_mod_2[i]
        representation.append(rephasing @ intertwiner)

    group_law_residuals = []
    for i, left in enumerate(rotations):
        for j, right in enumerate(rotations):
            product_index = indices[rotation_key(left @ right)]
            group_law_residuals.append(
                np.linalg.norm(
                    representation[i] @ representation[j]
                    - representation[product_index],
                    "fro",
                )
            )
    return representation, max(cocycle_residuals), max(group_law_residuals)


def co_intertwiner_nullity(
    symmetry: np.ndarray,
    moves: dict[tuple[int, int, int], CubieMove],
) -> tuple[int, float]:
    equations = []
    for generator, move in moves.items():
        source = block_matrix(move, "co")
        target = block_matrix(
            moves[
                mapped_generator(
                    symmetry,
                    generator,
                    include_orientation_reversal=True,
                )
            ],
            "co",
        )
        equations.append(
            np.kron(source.T, np.eye(8)) - np.kron(np.eye(8), target)
        )
    singular_values = np.linalg.svd(np.vstack(equations), compute_uv=False)
    return int(np.sum(singular_values < TOL)), float(singular_values[-1])


def build_sector_symmetry_group(
    moves: dict[tuple[int, int, int], CubieMove],
) -> dict[tuple[tuple[int, ...], ...], CubieMove]:
    group: dict[tuple[tuple[int, ...], ...], CubieMove] = {}
    for rotation in CubeBase.rotation_matrices:
        corner_perm = position_permutation(rotation, CORNER_POSITIONS)
        edge_perm = position_permutation(rotation, EDGE_POSITIONS)
        if permutation_parity(corner_perm) != permutation_parity(edge_perm):
            continue

        corner_base = gauge_exponents(rotation, moves, "co")
        edge_base = gauge_exponents(rotation, moves, "eo")
        for corner_shift in range(3):
            corner_delta = (corner_base + corner_shift) % 3
            if np.sum(corner_delta) % 3:
                continue
            for edge_shift in range(2):
                edge_delta = (edge_base + edge_shift) % 2
                if np.sum(edge_delta) % 2:
                    continue
                move = CubieMove(
                    corners_perm=corner_perm,
                    edges_perm=edge_perm,
                    corners_ori_delta=corner_delta,
                    edges_ori_delta=edge_delta,
                )
                group[move_key(move)] = move
    return group


def generated_subgroup(
    generators: list[CubieMove],
) -> dict[tuple[tuple[int, ...], ...], CubieMove]:
    identity = CubieMove.identity()
    group = {move_key(identity): identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            product = current @ generator
            key = move_key(product)
            if key not in group:
                group[key] = product
                frontier.append(product)
    return group


def move_order(move: CubieMove, cutoff: int = 30) -> int:
    identity_key = move_key(CubieMove.identity())
    power = CubieMove.identity()
    for order in range(1, cutoff + 1):
        power = power @ move
        if move_key(power) == identity_key:
            return order
    raise AssertionError(f"order exceeds cutoff {cutoff}")


def trace_rho(move: CubieMove) -> complex:
    fixed_corners = np.where(move.corners_perm == np.arange(8))[0]
    fixed_edges = np.where(move.edges_perm == np.arange(12))[0]
    return (
        8 * len(fixed_corners)
        + 12 * len(fixed_edges)
        + sum(OMEGA ** int(move.corners_ori_delta[i]) for i in fixed_corners)
        + sum((-1.0) ** int(move.edges_ori_delta[i]) for i in fixed_edges)
    )


def spectral_layer_audit(
    averaging_operator: np.ndarray,
    rhos: dict[tuple[int, int, int], np.ndarray],
) -> tuple[list[tuple[float, int, float, float]], float]:
    eigenvalues, eigenvectors = np.linalg.eigh(averaging_operator)
    rounded = np.round(eigenvalues, 10)
    results = []
    identity_residuals = []
    for eigenvalue in sorted(set(rounded), reverse=True):
        basis = eigenvectors[:, rounded == eigenvalue]
        projector = basis @ basis.conj().T
        commutators = [
            np.linalg.norm(projector @ rho - rho @ projector, "fro")
            for rho in rhos.values()
        ]
        leakages = [
            np.linalg.norm((np.eye(228) - projector) @ rho @ projector, "fro")
            for rho in rhos.values()
        ]
        for rho in rhos.values():
            outgoing_mass = np.linalg.norm(
                (np.eye(228) - projector) @ rho @ projector,
                "fro",
            ) ** 2
            commutator_mass = 0.5 * np.linalg.norm(
                rho @ projector - projector @ rho,
                "fro",
            ) ** 2
            identity_residuals.append(abs(outgoing_mass - commutator_mass))
        results.append(
            (
                float(eigenvalue),
                basis.shape[1],
                max(commutators),
                max(leakages),
            )
        )
    return results, max(identity_residuals)


def main() -> None:
    moves = CubieMove.prim_moves
    rhos = {generator: rho128(move) for generator, move in moves.items()}
    averaging_operator = sum(rhos.values()) / 18
    qt_all = sum(rho for key, rho in rhos.items() if key[2] != 2) / 12
    ht_all = sum(rho for key, rho in rhos.items() if key[2] == 2) / 6
    operators = {
        "A_18": averaging_operator,
        "QT_all": qt_all,
        "HT_all": ht_all,
    }

    pairwise_commutators = {
        "[A_18,QT_all]": np.linalg.norm(
            averaging_operator @ qt_all - qt_all @ averaging_operator,
            "fro",
        ),
        "[A_18,HT_all]": np.linalg.norm(
            averaging_operator @ ht_all - ht_all @ averaging_operator,
            "fro",
        ),
        "[QT_all,HT_all]": np.linalg.norm(qt_all @ ht_all - ht_all @ qt_all, "fro"),
    }
    print("0. Pairwise QH commutation")
    for name, residual in pairwise_commutators.items():
        print(f"  {name}: {residual:.3e}")
    assert max(pairwise_commutators.values()) < TOL

    print("\n1. Full-G commutant membership")
    for name, operator in operators.items():
        norms = [
            np.linalg.norm(operator @ rho - rho @ operator, "fro")
            for rho in rhos.values()
        ]
        print(
            f"  {name:7s}: min={min(norms):.6f} max={max(norms):.6f} "
            f"nonzero={sum(norm > TOL for norm in norms)}/18"
        )
        assert all(norm > TOL for norm in norms)

    print("\n2. Spectral-layer G-invariance")
    layer_results, transport_identity_residual = spectral_layer_audit(
        averaging_operator,
        rhos,
    )
    for eigenvalue, dimension, max_commutator, max_leakage in layer_results:
        print(
            f"  lambda={eigenvalue: .10f} dim={dimension:3d} "
            f"max_comm={max_commutator:.6e} max_leak={max_leakage:.6e}"
        )
    invariant_layers = [row for row in layer_results if row[2] < TOL]
    assert len(invariant_layers) == 1
    assert abs(invariant_layers[0][0] - 1.0) < TOL
    print(
        "  max_transport_invariance_identity_residual="
        f"{transport_identity_residual:.3e}"
    )
    assert transport_identity_residual < TOL

    print("\n3. Orientation-preserving rotational covariance")
    rotations = list(CubeBase.rotation_matrices)
    intertwiners = [rotation_intertwiner(rotation, moves) for rotation in rotations]
    covariance_residuals = []
    commutator_residuals = []
    for rotation, intertwiner in zip(rotations, intertwiners):
        covariance_residuals.append(
            max(
                np.linalg.norm(
                    intertwiner @ rhos[generator]
                    - rhos[mapped_generator(rotation, generator)] @ intertwiner,
                    "fro",
                )
                for generator in moves
            )
        )
        commutator_residuals.append(
            max(
                np.linalg.norm(intertwiner @ operator - operator @ intertwiner, "fro")
                for operator in operators.values()
            )
        )
    print(f"  rotations=24 max_covariance={max(covariance_residuals):.3e}")
    print(f"  max_operator_commutator={max(commutator_residuals):.3e}")
    _, cocycle_residual, group_law_residual = make_rotation_representation(
        rotations,
        intertwiners,
    )
    print(f"  scalar_cocycle_residual={cocycle_residual:.3e}")
    print(f"  rephased_group_law_residual={group_law_residual:.3e}")
    assert max(covariance_residuals) < TOL
    assert max(commutator_residuals) < TOL
    assert cocycle_residual < TOL
    assert group_law_residual < TOL

    print("\n4. Orientation-reversing complex-linear CO test")
    nullity_census: Counter[tuple[int, int]] = Counter()
    smallest_singular_values: dict[int, list[float]] = {1: [], -1: []}
    for symmetry in CubeBase.symmetry_matrices:
        determinant = int(round(np.linalg.det(symmetry)))
        nullity, smallest = co_intertwiner_nullity(symmetry, moves)
        nullity_census[(determinant, nullity)] += 1
        smallest_singular_values[determinant].append(smallest)
    for determinant in (1, -1):
        census = {
            nullity: count
            for (det, nullity), count in nullity_census.items()
            if det == determinant
        }
        values = smallest_singular_values[determinant]
        print(
            f"  det={determinant:+d}: nullity={census} "
            f"sigma_min=[{min(values):.3e}, {max(values):.3e}]"
        )
    assert nullity_census[(1, 1)] == 24
    assert nullity_census[(-1, 0)] == 24

    print("\n5. Sector-preserving cubie subgroup H")
    group = build_sector_symmetry_group(moves)
    identity_key = move_key(CubieMove.identity())
    assert len(group) == 24
    assert identity_key in group
    assert all(move_key(left @ right) in group for left in group.values() for right in group.values())
    assert all(move_key(move.inverse()) in group for move in group.values())

    order_census = Counter(move_order(move) for move in group.values())
    superflip_key = (
        tuple(range(8)),
        tuple(range(12)),
        (0,) * 8,
        (1,) * 12,
    )
    assert superflip_key in group
    superflip = group[superflip_key]
    assert move_order(superflip) == 2
    assert all(
        move_key(superflip @ move) == move_key(move @ superflip)
        for move in group.values()
    )

    # Find a split A4 complement of the central superflip factor.
    complement = None
    complement_generators = None
    order_three = [move for move in group.values() if move_order(move) == 3]
    order_two = [
        move
        for move in group.values()
        if move_order(move) == 2 and move_key(move) != superflip_key
    ]
    for first in order_three:
        for second in order_two:
            generated = generated_subgroup([first, second])
            if (
                len(generated) == 12
                and move_order(first @ second) == 3
                and superflip_key not in generated
            ):
                complement = generated
                complement_generators = (first, second)
                break
        if complement is not None:
            break
    assert complement is not None
    assert complement_generators is not None
    assert Counter(move_order(move) for move in complement.values()) == Counter({3: 8, 2: 3, 1: 1})
    generator_a, generator_b = complement_generators
    assert move_order(generator_a) == 3
    assert move_order(generator_b) == 2
    assert move_order(generator_a @ generator_b) == 3
    direct_product_keys = {
        move_key(element @ (superflip if exponent else CubieMove.identity()))
        for element in complement.values()
        for exponent in (0, 1)
    }
    assert direct_product_keys == set(group)

    h_commutators = {
        name: max(
            np.linalg.norm(rho128(move) @ operator - operator @ rho128(move), "fro")
            for move in group.values()
        )
        for name, operator in operators.items()
    }
    commutant_dimension = sum(abs(trace_rho(move)) ** 2 for move in group.values()) / len(group)

    normality_failures = []
    for generator, transport_move in moves.items():
        if any(
            move_key(transport_move.inverse() @ symmetry @ transport_move) not in group
            for symmetry in group.values()
        ):
            normality_failures.append(generator)

    print(f"  |H|={len(group)} order_census={dict(sorted(order_census.items()))}")
    print("  relations=a^3=b^2=(ab)^3=e, |<a,b>|=12")
    print("  split_structure=H=<a,b> x <z> = A4 x C2 (z is superflip)")
    for name, move in (("a", generator_a), ("b", generator_b), ("z", superflip)):
        print(
            f"  {name}: cp={tuple(map(int, move.corners_perm))} "
            f"ep={tuple(map(int, move.edges_perm))} "
            f"co={tuple(map(int, move.corners_ori_delta))} "
            f"eo={tuple(map(int, move.edges_ori_delta))}"
        )
    print(
        "  max_commutators="
        + ", ".join(f"{name}:{value:.3e}" for name, value in h_commutators.items())
    )
    print(f"  dim_End_H(V)={commutant_dimension.real:.0f}")
    print(f"  normal_in_G=False violating_generators={len(normality_failures)}/18")

    assert max(h_commutators.values()) < TOL
    assert abs(commutant_dimension - 4050) < TOL
    assert len(normality_failures) == 18

    print("\nAUDIT PASSED")


if __name__ == "__main__":
    main()
