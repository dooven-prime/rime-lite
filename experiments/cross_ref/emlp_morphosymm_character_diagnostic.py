# Cross-Reference Diagnostic: EMLP, MorphoSymm, and Character Methods
# =====================================================================
"""Clean support diagnostic for representation-software parallels.

Claim status:
  - S3 EMLP-style commutant constraint: exact small-scale sanity check.
  - S3 character central idempotents: exact character-table sanity check.
  - Rubik A_18 spectral basis: coarse spectral-coordinate diagnostic.
  - Rubik QT/HT sector basis Q and decompose_signal(): API diagnostic.
  - Rubik sector trace signatures: sampled diagnostic, not a theorem.

This script is intentionally kept in experiments/cross_ref rather than in a
single-paper support directory. It documents how standard equivariant-map,
isotypic-coordinate, and character methods relate to RIME's sectorized
representation objects without promoting them to new Paper I theorem inputs.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from rime.cubieoperator import CubieSpectralOperator  # noqa: E402
from rime.rep_utils import (  # noqa: E402
    conjugacy_class_key,
    regular_rep,
    symmetric_group,
)

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
)
LOG_PATH = os.path.join(OUT_DIR, "_cross_ref_emlp_morphosymm_character.txt")

TOL = 1e-10
RNG_SEED = 42


def log(msg: str = "") -> None:
    print(msg, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")


def section(title: str) -> None:
    log("=" * 72)
    log(f"  {title}")
    log("=" * 72)


def class_data(group: list[tuple[int, ...]]) -> list[tuple[tuple[int, ...], list[int]]]:
    """Return conjugacy classes as (cycle-key, element-index-list)."""
    buckets: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for idx, g in enumerate(group):
        buckets[conjugacy_class_key(g)].append(idx)
    return sorted(buckets.items(), key=lambda item: (sum(item[0]), item[0]))


def s3_character_table() -> dict[str, np.ndarray]:
    """S3 irreducible characters on classes [id, transposition, 3-cycle]."""
    return {
        "triv": np.array([1.0, 1.0, 1.0]),
        "sign": np.array([1.0, -1.0, 1.0]),
        "std": np.array([2.0, 0.0, -1.0]),
    }


def central_projector(
    rhos: list[np.ndarray],
    group: list[tuple[int, ...]],
    char_values: np.ndarray,
    dim_irrep: int,
    classes: list[tuple[tuple[int, ...], list[int]]],
) -> np.ndarray:
    """Central idempotent e_chi = d/|G| sum_g chi(g^-1) rho(g).

    For S3 all irreducible characters are real-valued class functions, so
    chi(g^-1)=chi(g).
    """
    n = rhos[0].shape[0]
    P = np.zeros((n, n), dtype=complex)
    for class_pos, (_, indices) in enumerate(classes):
        for idx in indices:
            P += char_values[class_pos] * rhos[idx]
    return (dim_irrep / len(group)) * P


def character_vector(
    P: np.ndarray,
    rhos: list[np.ndarray],
    classes: list[tuple[tuple[int, ...], list[int]]],
) -> np.ndarray:
    """Character trace Tr(P rho(g)) averaged over each conjugacy class."""
    values = []
    for _, indices in classes:
        traces = [np.trace(P @ rhos[idx]) for idx in indices]
        values.append(np.mean(traces).real)
    return np.array(values)


def character_inner_product(
    chi_a: np.ndarray,
    chi_b: np.ndarray,
    class_sizes: np.ndarray,
    group_order: int,
) -> float:
    return float(np.sum(class_sizes * chi_a * np.conj(chi_b)).real / group_order)


def cluster_hermitian_eigenspaces(
    A: np.ndarray,
    tol: float = 1e-6,
) -> tuple[list[float], list[np.ndarray]]:
    """Cluster Hermitian eigenspaces, returning eigenvalues and basis blocks."""
    evals, evecs = np.linalg.eigh(A)
    order = np.argsort(evals)[::-1]
    groups: list[list[int]] = []
    cur = [int(order[0])]
    cv = evals[order[0]]
    for idx in range(1, len(order)):
        oi = int(order[idx])
        if abs(evals[oi] - cv) < tol:
            cur.append(oi)
        else:
            groups.append(cur)
            cur = [oi]
            cv = evals[oi]
    groups.append(cur)

    values = [float(np.mean(evals[g]).real) for g in groups]
    bases = []
    for group in groups:
        V, _ = np.linalg.qr(evecs[:, group])
        bases.append(V)
    return values, bases


def emlp_s3_commutant() -> tuple[
    list[tuple[int, ...]],
    list[np.ndarray],
    list[tuple[tuple[int, ...], list[int]]],
]:
    section("Method 1: EMLP-Style Commutant Constraint on S3")

    group = symmetric_group(3)
    rhos = regular_rep(group)
    classes = class_data(group)

    gen_indices = [group.index((1, 0, 2)), group.index((0, 2, 1))]
    n = len(group)
    I = np.eye(n, dtype=complex)

    constraints = []
    for idx in gen_indices:
        rho = rhos[idx]
        constraints.append(np.kron(I, rho) - np.kron(rho.T, I))
    T = np.vstack(constraints)
    _, sing, vh = np.linalg.svd(T, full_matrices=True)
    comm_dim = int(np.sum(sing < TOL))
    null_basis = vh[-comm_dim:].conj().T

    max_err = 0.0
    for k in range(comm_dim):
        C = null_basis[:, k].reshape(n, n)
        for idx in gen_indices:
            err = np.linalg.norm(rhos[idx] @ C - C @ rhos[idx], "fro")
            max_err = max(max_err, err)

    log(f"S3 order: {n}")
    log(f"Generator indices: {gen_indices}")
    log(f"Constraint matrix: {T.shape[0]} x {T.shape[1]}")
    log(f"Nullity below tolerance: {comm_dim}")
    log(f"Expected regular-representation commutant dimension: {n}")
    log(f"Max commutator error over null-basis: {max_err:.2e}")
    assert comm_dim == n
    assert max_err < 1e-8
    return group, rhos, classes


def s3_character_projectors(
    group: list[tuple[int, ...]],
    rhos: list[np.ndarray],
    classes: list[tuple[tuple[int, ...], list[int]]],
) -> None:
    section("Method 2a: Exact S3 Character Central Idempotents")

    chars = s3_character_table()
    dims = {"triv": 1, "sign": 1, "std": 2}
    class_sizes = np.array([len(indices) for _, indices in classes], dtype=float)

    log(f"Conjugacy classes: {[key for key, _ in classes]}")
    log(f"Class sizes: {class_sizes.astype(int).tolist()}")

    projectors = {}
    for name, chi in chars.items():
        P = central_projector(rhos, group, chi, dims[name], classes)
        projectors[name] = P
        idem = np.linalg.norm(P @ P - P, "fro")
        rank = int(round(np.trace(P).real))
        chi_sector = character_vector(P, rhos, classes)
        multiplicities = {
            other: character_inner_product(chi_sector, other_chi, class_sizes, len(group))
            for other, other_chi in chars.items()
        }
        mult_text = ", ".join(f"{k}: {v:.1f}" for k, v in multiplicities.items())
        log(
            f"{name:>5s}: rank={rank}, idempotence={idem:.2e}, "
            f"chi_sector={np.round(chi_sector, 3).tolist()}, "
            f"multiplicities={{{mult_text}}}"
        )
        assert idem < 1e-8
        assert abs(multiplicities[name] - dims[name]) < 1e-8
        for other in chars:
            if other != name:
                assert abs(multiplicities[other]) < 1e-8

    completeness = np.linalg.norm(sum(projectors.values()) - np.eye(len(group)), "fro")
    log(f"Central-idempotent completeness error: {completeness:.2e}")
    assert completeness < 1e-8


def s3_morphosymm_style_basis(rhos: list[np.ndarray]) -> None:
    section("Method 3a: MorphoSymm-Style Basis from S3 Spectral Layers")

    A = sum(rhos) / len(rhos)
    A = (A + A.conj().T) / 2
    values, bases = cluster_hermitian_eigenspaces(A)
    dims = [V.shape[1] for V in bases]
    Q = np.hstack(bases)
    q_err = np.linalg.norm(Q.conj().T @ Q - np.eye(Q.shape[1]), "fro")
    log(f"A_S3 spectral values: {np.round(values, 6).tolist()}")
    log(f"A_S3 spectral layer dims: {dims}")
    log(f"Q shape: {Q.shape}, ||Q^*Q-I||_F={q_err:.2e}")
    log("Caveat: A_S3 gives [1,5], not the full [1,1,4] S3 isotypic split.")
    assert q_err < 1e-8

    rho_iso = Q.conj().T @ rhos[0] @ Q
    offset_i = 0
    for i, di in enumerate(dims):
        offset_j = 0
        for j, dj in enumerate(dims):
            block = rho_iso[offset_i : offset_i + di, offset_j : offset_j + dj]
            nrm = np.linalg.norm(block, "fro")
            if nrm > 1e-8:
                log(f"  rho block ({i},{j}) dims=({di},{dj}): ||B||_F={nrm:.3f}")
            offset_j += dj
        offset_i += di


def rubik_a18_spectral_basis(op: CubieSpectralOperator, rhos: list[np.ndarray]) -> None:
    section("Method 3b: Rubik A_18 Spectral Basis")

    A_18 = sum(rhos) / len(rhos)
    A_18 = (A_18 + A_18.conj().T) / 2
    values, bases = cluster_hermitian_eigenspaces(A_18)
    dims = [V.shape[1] for V in bases]
    Q = np.hstack(bases)
    q_err = np.linalg.norm(Q.conj().T @ Q - np.eye(Q.shape[1]), "fro")
    centralizer_dim = sum(d * d for d in dims)

    log(f"A_18 spectral values: {np.round(values, 6).tolist()}")
    log(f"A_18 layer dims: {dims}")
    log(f"A_18 spectral centralizer dimension sum dim(lambda)^2: {centralizer_dim}")
    log(f"A_18 layer-basis Q shape: {Q.shape}, ||Q^*Q-I||_F={q_err:.2e}")
    log("Caveat: these are spectral-layer coordinates, not the full Rubik")
    log("isotypic decomposition and not the QT/HT sector coordinates.")
    assert q_err < 1e-8

    rng = np.random.RandomState(RNG_SEED)
    signal = rng.randn(Q.shape[0]) + 1j * rng.randn(Q.shape[0])
    signal /= np.linalg.norm(signal)
    signal_iso = Q.conj().T @ signal
    components = []
    pos = 0
    for dim in dims:
        comp_iso = np.zeros_like(signal_iso)
        comp_iso[pos : pos + dim] = signal_iso[pos : pos + dim]
        components.append(Q @ comp_iso)
        pos += dim
    recon_err = np.linalg.norm(sum(components) - signal)
    log(f"A_18 signal reconstruction error: {recon_err:.2e}")
    assert recon_err < 1e-8

    decomp = op.center_decomposition()
    sector_dims = [s["dim"] for s in decomp["sectors"]]
    log(f"QT/HT sector dims from center_decomposition(): {sector_dims}")


def rubik_sector_basis_api(op: CubieSpectralOperator) -> None:
    section("Method 3c: Rubik QT/HT Sector Basis API")

    decomp = op.center_decomposition()
    Q = decomp["Q"]
    q_err = np.linalg.norm(Q.conj().T @ Q - np.eye(Q.shape[1]), "fro")
    projector_err = max(
        np.linalg.norm(V @ V.conj().T - P, "fro")
        for V, P in zip(decomp["sector_bases"], decomp["projectors"])
    )
    log(f"Q shape: {Q.shape}, ||Q^*Q-I||_F={q_err:.2e}")
    log(f"Max basis-projector reconstruction error: {projector_err:.2e}")

    rng = np.random.RandomState(RNG_SEED)
    vec = rng.randn(Q.shape[0]) + 1j * rng.randn(Q.shape[0])
    components = op.decompose_signal(vec)
    recon_err = np.linalg.norm(sum(components) - vec)
    component_dims = [V.shape[1] for V in decomp["sector_bases"]]
    log(f"Sector dims: {component_dims}")
    log(f"decompose_signal reconstruction error: {recon_err:.2e}")
    assert q_err < 1e-8
    assert projector_err < 1e-8
    assert recon_err < 1e-8


def rubik_sampled_sector_characters(op: CubieSpectralOperator, rhos: list[np.ndarray]) -> None:
    section("Method 2b: Rubik Sampled Sector Trace Signatures")

    decomp = op.center_decomposition()
    sectors = decomp["sectors"]
    projectors = decomp["projectors"]
    n_sec = len(sectors)

    n_samples = 200
    rng = np.random.RandomState(RNG_SEED)
    char_matrix = np.zeros((n_sec, n_samples), dtype=complex)
    for sample_idx in range(n_samples):
        if sample_idx < len(rhos):
            rho_g = rhos[sample_idx]
        else:
            rho_g = np.eye(rhos[0].shape[0], dtype=complex)
            for _ in range(rng.randint(1, 6)):
                rho_g = rho_g @ rhos[rng.randint(0, len(rhos))]
        for sec_idx, P in enumerate(projectors):
            char_matrix[sec_idx, sample_idx] = np.trace(P @ rho_g)

    log(f"Sectors: {n_sec}, dims={[s['dim'] for s in sectors]}")
    log(f"Samples: {n_samples} (18 generators + reproducible random words)")
    log("Sampled Gram data are diagnostics only; they are not class-weighted")
    log("group-character orthogonality relations. The normalized cosine values")
    log("below should be read as fingerprint overlap, not as irrep orthogonality.")

    gram = (char_matrix @ char_matrix.conj().T) / n_samples
    for i in range(n_sec):
        self_ip = gram[i, i].real
        max_cross = max(abs(gram[i, j]) for j in range(n_sec) if j != i)
        max_cosine = max(
            abs(gram[i, j]) / np.sqrt(abs(gram[i, i]) * abs(gram[j, j]))
            for j in range(n_sec)
            if j != i
        )
        log(
            f"S{i + 1:>2d}: dim={sectors[i]['dim']:>3d}, "
            f"sample-self={self_ip:>9.3f}, max-cross={max_cross:>9.3f}, "
            f"max-cos={max_cosine:>6.3f}"
        )

    distances = []
    for i in range(n_sec):
        for j in range(i + 1, n_sec):
            distances.append(np.linalg.norm(char_matrix[i] - char_matrix[j]))
    log(f"Minimum pairwise sampled fingerprint distance: {min(distances):.3f}")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("")

    section("Cross-Reference Diagnostic")
    log("Cleaned from old cross_ref prototypes for rime-lite.")
    log("Uses public APIs: rho_matrices(), center_decomposition(), decompose_signal().")
    log("")

    group, s3_rhos, s3_classes = emlp_s3_commutant()
    s3_character_projectors(group, s3_rhos, s3_classes)
    s3_morphosymm_style_basis(s3_rhos)

    op = CubieSpectralOperator()
    rubik_rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    rubik_a18_spectral_basis(op, rubik_rhos)
    rubik_sector_basis_api(op)
    rubik_sampled_sector_characters(op, rubik_rhos)

    section("Summary")
    log("S3 exact checks pass: EMLP-style commutant and character idempotents.")
    log("Rubik diagnostics pass: A_18 spectral basis, QT/HT sector Q, and sampled")
    log("sector trace signatures. These support related-work positioning only;")
    log("they are not new theorem-level inputs for Paper I.")
    log(f"Full log: {LOG_PATH}")
    log("Done.")


if __name__ == "__main__":
    main()
