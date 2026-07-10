"""Isotypic decomposition and transport from combinatorial commutant (F1/F2/F3/F4).

Uses CubieSpectralOperator.full_commutant_combinatorial() for exact 228-dim
commutant (610 basis matrices, ~2s), then projects to each eigenspace layer,
finds central idempotents (12 isotypic components total), and computes
isotypic-level transport tensor (12×12×18).

Key findings (260514):
- 12 isotypic components (not ~99 as previously estimated)
- 12 isotypic ≠ 12 observable-algebra sectors — different objects
- Σm² = comm self-consistent for every layer
- 28/144 nonzero transport connections (block-preserving)
- Sum of per-layer comm_dim (966) > full comm_dim (610) — overcompleteness
- V₁ has M₂×4 ⊕ M₁×4 structure (8 components, matches A_EP AW decomposition)
- F2 "no new topology" is the positive result: sector decomposition already
  captures all transport-relevant structure; isotypic is finer but adds nothing

Usage:
    python experiments/paper1/isotypic_decomposition.py
"""
import numpy as np
from collections import defaultdict
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove


# ═══════════════════════════════════════════════════════════════════════════════
# Standalone helpers (extracted from CubieSpectralOperator, 260514)
#
# _center_idempotents lives in CubieSpectralOperator (kept there for demonstration);
# imported here for the isotypic decomposition pipeline.
# ═══════════════════════════════════════════════════════════════════════════════

# _center_idempotents is CubieSpectralOperator._center_idempotents —
# called via op._center_idempotents() in the pipeline below.


# ═══════════════════════════════════════════════════════════════════════════════
# Isotypic decomposition pipeline
# ═══════════════════════════════════════════════════════════════════════════════

def project_commutant_to_layer(op, full_basis, lam, tol=1e-12):
    """Project full-space commutant basis to an eigenspace layer."""
    V = op.eigenspace_basis(lam)
    d = V.shape[1]
    gs_tol = tol * d * 10
    projected_basis = []
    for B in full_basis:
        B_proj = V.T.conj() @ B @ V
        for existing in projected_basis:
            B_proj -= np.tensordot(existing.conj(), B_proj) * existing
        nrm = np.linalg.norm(B_proj, 'fro')
        if nrm > gs_tol:
            projected_basis.append(B_proj / nrm)
    return projected_basis, len(projected_basis)


def isotypic_decomposition(op):
    """Exact Artin-Wedderburn / isotypic decomposition within each spectral layer.

    Uses combinatorial commutant (F1 fix) — full central idempotent basis via
    orbit-based computation in the full 228-dim space.
    """
    full_basis, full_comm_dim = op.full_commutant_combinatorial()

    layers = op.layer_keys
    result = {}
    all_components = []

    for lam in layers:
        d = op.layer_dimension(lam)

        projected_basis, comm_dim = project_commutant_to_layer(op, full_basis, lam)
        center_dim, idempotents, iso_projectors, isotypic_info = op._center_idempotents(
            projected_basis, d)

        isotypic = [(d_irr, mult) for d_irr, mult in isotypic_info]

        result[lam] = {
            'dim': d,
            'commutant_dim': comm_dim,
            'center_dim': center_dim,
            'isotypic': isotypic,
            'isotypic_projectors': iso_projectors,
            'idempotents': idempotents,
            'center_info': isotypic_info,
        }
        for d_irr, mult in isotypic:
            all_components.append((d_irr, mult, float(lam)))

    irrep_summary = {}
    for d_irrep, m, lam_src in all_components:
        key = d_irrep
        if key not in irrep_summary:
            irrep_summary[key] = {'d_irrep': d_irrep, 'total_mult': 0, 'sources': []}
        irrep_summary[key]['total_mult'] += m
        irrep_summary[key]['sources'].append((float(lam_src), m))

    return {
        'blocks': result,
        'total_isotypic_types': len(all_components),
        'irrep_sizes': sorted(irrep_summary.values(), key=lambda x: x['d_irrep'], reverse=True),
        'dim_total': sum(b['commutant_dim'] for b in result.values()),
        'full_comm_dim': full_comm_dim,
    }


def isotypic_transport_tensor(op):
    """Compute isotypic-level transport tensor (F2).

    For each isotypic component α (with central idempotent P_α) and generator γ:
        T[α, β, γ] = ‖P_α ρ(g_γ) P_β‖_F
    """
    iso_result = isotypic_decomposition(op)

    full_projectors = []
    meta = []
    for lam in sorted(iso_result['blocks'], reverse=True):
        blk = iso_result['blocks'][lam]
        V = op.eigenspace_basis(lam)
        iso_projectors = blk.get('isotypic_projectors', [])
        iso_info = blk.get('center_info', [])
        for i, P_d in enumerate(iso_projectors):
            if isinstance(P_d, np.ndarray) and P_d.ndim == 2:
                P_full = V @ P_d @ V.T.conj()
                full_projectors.append(P_full)
                d_irrep, mult = (1, 1)
                if i < len(iso_info):
                    d_irrep, mult = iso_info[i]
                meta.append({
                    'lam': float(lam),
                    'dim_proj': int(np.round(np.trace(P_d).real)),
                    'd_irrep': int(d_irrep),
                    'multiplicity': int(mult),
                    'block_dim': blk['dim'],
                })

    n_iso = len(full_projectors)
    rho_mats = [m.toarray() if hasattr(m, 'toarray') else np.array(m)
                for m in op.rho_matrices()]
    n_gens = len(rho_mats)

    # Precompute sector bases V_a from projectors (P_a = V_a @ V_a^T)
    # Then ||P_a rho P_b||_F = ||V_a^T rho V_b||_F — avoids full projector matmuls
    sector_bases = []
    for a in range(n_iso):
        P = full_projectors[a]
        evals, evecs = np.linalg.eigh(P)
        mask = np.abs(evals - 1.0) < 1e-8
        V = evecs[:, mask]; V, _ = np.linalg.qr(V)
        sector_bases.append(V)

    T = np.zeros((n_iso, n_iso, n_gens))
    # Precompute rho_mats[g] @ V_b for all (g,b)
    rho_V = {}
    for g in range(n_gens):
        for b in range(n_iso):
            rho_V[(g, b)] = rho_mats[g] @ sector_bases[b]

    for a in range(n_iso):
        Va = sector_bases[a]
        for b in range(n_iso):
            for g in range(n_gens):
                transport = Va.T.conj() @ rho_V[(g, b)]
                T[a, b, g] = np.linalg.norm(transport, 'fro')

    K = np.max(T, axis=2)

    return {
        'T': T, 'K': K,
        'projectors': full_projectors, 'meta': meta,
        'n_isotypic': n_iso, 'blocks': iso_result['blocks'],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# F3: Multiplicity-fibre tracking — multiplicity transfer operators
#
# Core object: for each isotypic pair (α,β) with matching irrep and each
# generator g, a multiplicity transfer matrix T_g^{α,β} ∈ C^{m_α × m_β}.
# Scalar copy-copy transport is |T_g[i,j]| (basis-invariant up to unitary
# frame choice within multiplicity spaces).  Diagnostics: SVD spectrum,
# entropy, isotropy deviation — these are invariant under intra-isotypic
# basis changes.
# ═══════════════════════════════════════════════════════════════════════════════

def precompute_layer_kernels(op):
    """Precompute M_g^{a,b} = V_a^H @ rho(g) @ V_b for all layer pairs.

    Returns:
        kernels: dict (lam_a, lam_b) -> list of (d_a, d_b) arrays, one per generator
        layer_bases: dict lam -> V (228 x d) eigenbasis
        rho_mats: list of dense (228, 228) rho matrices
        n_gens: number of generators
    """
    layers = op.layer_keys
    layer_bases = {lam: op.eigenspace_basis(lam) for lam in layers}

    rho_mats = [m.toarray() if hasattr(m, 'toarray') else np.array(m)
                for m in op.rho_matrices()]
    n_gens = len(rho_mats)

    kernels = {}
    for lam_a in layers:
        Va = layer_bases[lam_a]
        for lam_b in layers:
            Vb = layer_bases[lam_b]
            M_list = [Va.T.conj() @ rho @ Vb for rho in rho_mats]
            kernels[(lam_a, lam_b)] = M_list

    return kernels, layer_bases, rho_mats, n_gens


def _skinny_projectors(idempotents, tol=1e-10):
    """Convert d×d projectors to skinny d×r factors: P = U @ U^H.

    Each idempotent is a Hermitian projector with eigenvalues 0 or 1.
    Returns list of (d, r) arrays where r = rank(P) = d_irrep.
    """
    skinny = []
    ranks = []
    for P in idempotents:
        if not isinstance(P, np.ndarray) or P.ndim != 2:
            skinny.append(None)
            ranks.append(0)
            continue
        evals, evecs = np.linalg.eigh(P)
        # Relative threshold: eigenvalues of a projector are either ~1 or ~0
        thresh = max(0.3, 0.5 * np.max(np.abs(evals))) if len(evals) > 0 else 0.5
        mask = evals > thresh
        skinny.append(evecs[:, mask])
        ranks.append(int(np.sum(mask)))
    return skinny, ranks


def multiplicity_transport(op, seed=42):
    """Compute multiplicity transfer operators between isotypic components (F3).

    For each pair of isotypic components (α,β) with matching irrep dimension d,
    and each generator g, extracts the multiplicity transfer matrix.

    Entry (i,j) = ‖u_{α,i}^H M_g^{a,b} u_{β,j}‖_F / √d

    By Schur's lemma, u_i^H M_g u_j ∝ I_d when irreps match, so the scalar
    |T_{ij}| is well-defined independent of intra-isotypic basis choice.
    """
    _prev_state = np.random.get_state()
    np.random.seed(seed)
    iso_result = isotypic_decomposition(op)
    np.random.set_state(_prev_state)

    kernels, layer_bases, rho_mats, n_gens = precompute_layer_kernels(op)
    layers = op.layer_keys

    # ── Phase 1: Collect all isotypic components + skinny factors ──
    iso_list = []       # per-isotypic metadata
    skinny_all = []     # per-copy skinny factors (global index)
    copy_to_iso = []    # global copy index -> iso index
    copy_meta = []      # per-copy metadata

    block_slices_local = {
        'cp': slice(0, 64), 'ep': slice(64, 208),
        'co': slice(208, 216), 'eo': slice(216, 228),
    }

    for lam in layers:
        blk = iso_result['blocks'][lam]
        V = layer_bases[lam]
        d = blk['dim']
        idempotents = blk.get('idempotents', [])
        iso_info = blk.get('center_info', [])

        if not idempotents:
            continue

        skinny_list, rank_list = _skinny_projectors(idempotents)

        iso_start = 0
        for iso_idx_local, (d_irr, mult) in enumerate(iso_info):
            copies_here = []
            for copy_in_iso in range(mult):
                i = iso_start + copy_in_iso
                if i >= len(idempotents):
                    break
                if not isinstance(idempotents[i], np.ndarray) or idempotents[i].ndim != 2:
                    continue

                gidx = len(skinny_all)
                skinny_all.append(skinny_list[i])
                copy_to_iso.append(len(iso_list))

                # Block support
                P_full = V @ idempotents[i] @ V.T.conj()
                blocks = [bn for bn, sl in block_slices_local.items()
                          if np.linalg.norm(P_full[sl][:, sl], 'fro') > 1e-8]

                copy_meta.append({
                    'copy_idx': gidx, 'lam': float(lam), 'layer_dim': d,
                    'iso_idx': len(iso_list),
                    'copy_in_iso': copy_in_iso,
                    'd_irrep': int(d_irr), 'mult': int(mult),
                    'd_copy': rank_list[i], 'blocks': blocks,
                })
                copies_here.append(gidx)

            iso_list.append({
                'iso_idx': len(iso_list), 'lam': float(lam), 'layer_dim': d,
                'd_irrep': int(d_irr), 'mult': int(mult),
                'copies': copies_here, 'n_copies': len(copies_here),
                'isotypic_id': f"λ={lam:.4f}_d{d_irr}_m{mult}",
            })
            iso_start += mult

    n_iso = len(iso_list)
    n_copies = len(skinny_all)
    print(f"F3: {n_iso} isotypic components, {n_copies} copies total")

    # ── Phase 2: Multiplicity transfer matrices ──
    mt = {}

    for a in range(n_iso):
        iso_a = iso_list[a]
        d_a = iso_a['d_irrep']
        lam_a = iso_a['lam']
        m_a = iso_a['n_copies']
        copies_a = iso_a['copies']

        for b in range(n_iso):
            iso_b = iso_list[b]
            d_b = iso_b['d_irrep']
            lam_b = iso_b['lam']
            m_b = iso_b['n_copies']
            copies_b = iso_b['copies']

            # Only matching irreps can have nonzero transport (Schur)
            if d_a != d_b:
                continue

            T_pair = np.zeros((m_a, m_b, n_gens))
            # Schur diagnostics: intra-isotypic orthogonality (i≠j ⇒ block≈0 ⊗ I)
            schur_ortho_residuals = []    # intra-isotypic, i≠j: block should vanish
            schur_diag_scale_ratio = []   # intra-isotypic, i=j: ‖diag‖/‖off-diag‖

            M_list = kernels[(lam_a, lam_b)]
            same_iso = (a == b)  # same isotypic component

            for g in range(n_gens):
                M_g = M_list[g]  # d_layer_a × d_layer_b

                for i_loc, i_g in enumerate(copies_a):
                    u_i = skinny_all[i_g]
                    if u_i is None or u_i.shape[1] == 0:
                        continue
                    ui_M = u_i.T.conj() @ M_g  # d_a × d_layer_b

                    for j_loc, j_g in enumerate(copies_b):
                        u_j = skinny_all[j_g]
                        if u_j is None or u_j.shape[1] == 0:
                            continue
                        # u_i^H @ M_g @ u_j  (d_a × d_b) = (d × d)
                        block = ui_M @ u_j
                        nrm = np.linalg.norm(block, 'fro')
                        T_pair[i_loc, j_loc, g] = nrm / np.sqrt(d_a)

                        if same_iso and nrm > 1e-10:
                            if i_loc == j_loc:
                                # Diagonal: ρ_W(g) — non-abelian irreps aren't ∝ I
                                off_diag = nrm - np.linalg.norm(np.diag(np.diag(block)), 'fro')
                                schur_diag_scale_ratio.append(
                                    np.linalg.norm(np.diag(np.diag(block)), 'fro') / nrm)
                            else:
                                # Off-diagonal: Schur orthogonality ⇒ block ≈ 0
                                schur_ortho_residuals.append(nrm)

            K_pair = np.max(T_pair, axis=2) if T_pair.size > 0 else np.zeros((m_a, m_b))

            key = (iso_a['isotypic_id'], iso_b['isotypic_id'])
            mt[key] = {
                'T': T_pair,
                'K': K_pair,
                'd_irrep': d_a,
                'lam_a': lam_a, 'lam_b': lam_b,
                'm_a': m_a, 'm_b': m_b,
                'same_iso': same_iso,
                'schur_ortho_max': float(np.max(schur_ortho_residuals)) if schur_ortho_residuals else 0.0,
                'schur_diag_ratio': float(np.median(schur_diag_scale_ratio)) if schur_diag_scale_ratio else 1.0,
            }

    return {
        'mt': {k: v for k, v in mt.items() if v['K'].size > 0 and np.max(v['K']) >= 0},
        'iso_list': iso_list,
        'copy_meta': copy_meta,
        'n_iso': n_iso,
        'n_copies': n_copies,
        'kernels': kernels,
        'layer_bases': layer_bases,
        'iso_result': iso_result,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# F3 Diagnostics: SVD spectrum, entropy, isotropy of multiplicity transfer
# ═══════════════════════════════════════════════════════════════════════════════

def _entropy(singular_values, tol=1e-12):
    """Entropy of normalized singular value distribution."""
    sv = singular_values[singular_values > tol]
    if len(sv) == 0:
        return 0.0
    p = sv / sv.sum()
    return -float(np.sum(p * np.log(np.maximum(p, 1e-15))))

def _isotropy_deviation(singular_values, tol=1e-12):
    """Coefficient of variation of singular values — 0 = perfectly isotropic."""
    sv = singular_values[singular_values > tol]
    if len(sv) <= 1 or sv[0] < tol:
        return 0.0
    return float(np.std(sv) / np.mean(sv))

def analyze_multiplicity_transport(result):
    """Analyze multiplicity transfer operators.

    Diagnostics per isotypic pair:
      - SVD spectrum (singular values of T_g matrices)
      - Entropy of singular value distribution
      - Isotropy deviation (std/mean of singular values)
      - Effective rank: number of singular values > 1% of max
    """
    mt = result['mt']
    iso_list = result['iso_list']
    print("=" * 72)
    print("F3: Multiplicity Transfer Operators — Invariant Diagnostics")
    print("=" * 72)

    # ── Per-pair diagnostics ──
    rows = []
    for (id_a, id_b), data in sorted(mt.items()):
        T = data['T']     # (m_a, m_b, n_gens)
        K = data['K']     # (m_a, m_b)
        m_a, m_b = data['m_a'], data['m_b']

        # Only analyze pairs with at least one side having mult > 1
        if m_a == 1 and m_b == 1:
            continue

        # Average T over generators (per-entry), then SVD
        T_avg = np.mean(T, axis=2)  # (m_a, m_b)

        # SVD of T_avg
        U, S, Vh = np.linalg.svd(T_avg, full_matrices=False)
        eff_rank = int(np.sum(S > 0.01 * S[0])) if len(S) > 0 and S[0] > 0 else 0
        ent = _entropy(S)
        iso = _isotropy_deviation(S)

        # SVD of K (max over generators)
        _, S_K, _ = np.linalg.svd(K, full_matrices=False)
        eff_rank_K = int(np.sum(S_K > 0.01 * S_K[0])) if len(S_K) > 0 and S_K[0] > 0 else 0

        # Max and mean transfer strength
        max_val = np.max(K)
        mean_val = np.mean(K[K > 1e-8]) if np.any(K > 1e-8) else 0.0

        rows.append({
            'pair': f"{id_a} → {id_b}",
            'shape': f"{m_a}×{m_b}",
            'max_K': max_val,
            'mean_K': mean_val,
            'eff_rank': eff_rank,
            'eff_rank_K': eff_rank_K,
            'entropy': ent,
            'isotropy': iso,
            'svals': S,
            'same_iso': data['same_iso'],
            'ortho_max': data['schur_ortho_max'],
            'diag_ratio': data['schur_diag_ratio'],
        })

    rows.sort(key=lambda r: r['max_K'], reverse=True)

    print(f"\n{'Pair':<48} {'shape':>7} {'max_K':>8} {'mean_K':>8} {'r_eff':>5}"
          f" {'entropy':>8} {'isotropy':>9} {'ortho':>8} {'diag':>7}")
    print("-" * 110)
    for r in rows[:30]:
        print(f"{r['pair']:<48} {r['shape']:>7} {r['max_K']:>8.4f}"
              f" {r['mean_K']:>8.4f} {r['eff_rank']:>5}"
              f" {r['entropy']:>8.3f} {r['isotropy']:>9.3f}"
              f" {r['ortho_max']:>8.1e} {r['diag_ratio']:>7.3f}")

    # ── Global summary ──
    high_entropy = [r for r in rows if r['entropy'] > 1.5]
    anisotropic = [r for r in rows if r['isotropy'] > 0.5]
    multirank = [r for r in rows if r['eff_rank'] > 1]

    print(f"\n─ Global summary ─")
    print(f"  Total isotypic pairs with matching irrep: {len(mt)}")
    print(f"  Pairs with mult > 1 on at least one side: {len(rows)}")
    print(f"  High-entropy pairs (entropy > 1.5): {len(high_entropy)}"
          f" — suggests distributed copy coupling")
    print(f"  Anisotropic pairs (isotropy > 0.5): {len(anisotropic)}"
          f" — suggests selective copy coupling")
    print(f"  Multi-rank pairs (eff_rank > 1): {len(multirank)}"
          f" — suggests independent copy channels")
    if multirank:
        print(f"  Multi-rank details:")
        for r in multirank:
            sv = r['svals'][:r['eff_rank']]
            print(f"    {r['pair']}: SVs = {[f'{s:.3f}' for s in sv]}"
                  f"  entropy={r['entropy']:.3f}  isotropy={r['isotropy']:.3f}")

    # ── Schur diagnostics ──
    same_iso_pairs = [r for r in rows if r['same_iso'] and r['shape'] != '1×1']
    cross_iso_pairs = [r for r in rows if not r['same_iso']]
    print(f"\n─ Schur diagnostics ─")
    print(f"  Same-isotypic pairs with m_a,m_b>1: {len(same_iso_pairs)}")
    if same_iso_pairs:
        bad_ortho = [r for r in same_iso_pairs if r['ortho_max'] > 1e-6]
        if bad_ortho:
            worst = max(r['ortho_max'] for r in bad_ortho)
            print(f"  Schur orthogonality (i≠j ⇒ block≈0): WARNING {len(bad_ortho)} pairs, max={worst:.1e}")
        else:
            print(f"  Schur orthogonality (i≠j ⇒ block≈0): PASS")
        for r in same_iso_pairs:
            irtype = '(non-abelian irrep)' if r['diag_ratio'] < 0.95 else '(abelian/1D irrep)'
            print(f"    {r['pair']:<48} ortho_max={r['ortho_max']:.1e}  diag_ratio={r['diag_ratio']:.3f} {irtype}")

    return rows


def plot_multiplicity_histogram(result, output_dir='figures'):
    """Multiplicity histogram: x = multiplicity, y = count.

    The stark distribution (m=1: 50, m=11: 1) visually conveys
    "the representation is almost multiplicity-free, with one reservoir."
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os

    os.makedirs(output_dir, exist_ok=True)
    iso_list = result['iso_list']

    mults = [iso['mult'] for iso in iso_list]
    unique_mults, counts = np.unique(mults, return_counts=True)

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))

    # Bar chart — log y to make the 1-vs-50 contrast visible
    colors = ['#2E86AB' if m == 1 else '#D62828' for m in unique_mults]
    bars = ax.bar(unique_mults.astype(float), counts, color=colors,
                  edgecolor='#333333', linewidth=1.2, width=0.8)

    ax.set_xlabel('Multiplicity $m$', fontsize=13)
    ax.set_ylabel('Number of Isotypic Components', fontsize=13)
    ax.set_title('Multiplicity Distribution: Almost Multiplicity-Free,\n'
                 'with One Multiplicity Reservoir ($m=11$)',
                 fontsize=14, fontweight='bold')

    # Annotate bars
    for m, c in zip(unique_mults, counts):
        label = f'{c}' if c > 1 else f'{c}'
        ax.text(m, c + max(counts)*0.03, label, ha='center', va='bottom',
                fontsize=12, fontweight='bold',
                color='#D62828' if m == 11 else '#2E86AB')

    ax.set_xticks(unique_mults.astype(float))
    ax.set_xticklabels([str(int(m)) for m in unique_mults], fontsize=11)
    ax.set_yscale('log')
    ax.set_ylim(0.5, max(counts) * 3)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', edgecolor='#333333', label='Multiplicity-free ($m=1$)'),
        Patch(facecolor='#D62828', edgecolor='#333333', label='Multiplicity Reservoir ($m=11$)'),
    ]
    ax.legend(handles=legend_elements, fontsize=10, loc='upper right')

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'f3_multiplicity_histogram.png'), dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved f3_multiplicity_histogram.png")


def plot_reservoir_svd_spectrum(result, output_dir='figures'):
    """Singular value spectrum of the V₅/₉ d=3×11 multiplicity reservoir.

    Shows the internal channel hierarchy — the 11 singular values form a
    smooth decay from dominant to subdominant channels, revealing the
    mode structure within the reservoir.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os

    os.makedirs(output_dir, exist_ok=True)

    mt = result['mt']
    reservoir_key = None
    for (id_a, id_b), data in mt.items():
        if data['m_a'] > 1 and data['m_b'] > 1 and id_a == id_b:
            reservoir_key = (id_a, id_b)
            break

    if reservoir_key is None:
        print("  No multiplicity reservoir found — skipping SVD plot.")
        return

    data = mt[reservoir_key]
    T = data['T']          # (m, m, n_gens)
    T_avg = np.mean(T, axis=2)  # (m, m)
    U, S, Vh = np.linalg.svd(T_avg, full_matrices=False)
    m = data['m_a']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # ── Left: singular value spectrum ──
    sv_norm = S / S[0]
    colors_sv = plt.cm.inferno(np.linspace(0.15, 0.95, m))

    ax1.bar(range(1, m + 1), sv_norm, color=colors_sv, edgecolor='#222222',
            linewidth=1.2, width=0.7)
    ax1.plot(range(1, m + 1), sv_norm, 'o-', color='#D62828', markersize=8,
             markeredgecolor='white', markeredgewidth=1, zorder=5)

    for i, sv in enumerate(S):
        ax1.text(i + 1, sv/S[0] + 0.03, f'{sv:.2f}', ha='center', va='bottom',
                 fontsize=8, rotation=90, color='#333333')

    ax1.set_xlabel('Channel Index $k$', fontsize=12)
    ax1.set_ylabel('Normalized Singular Value $\\sigma_k / \\sigma_1$', fontsize=12)
    ax1.set_title('Multiplicity Reservoir: Internal Channel Hierarchy\n'
                  r'$V_{5/9}^{(3,11)}$ 11×11 Multiplicity Transfer',
                  fontsize=12, fontweight='bold')
    ax1.set_xticks(range(1, m + 1))
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, 1.15)

    # ── Right: K matrix heatmap ──
    K = data['K']
    im = ax2.imshow(K, cmap='inferno', aspect='equal')
    ax2.set_title(f'Multiplicity Transfer K Matrix\n11×11 Internal Channels',
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('Copy $j$ (target)', fontsize=11)
    ax2.set_ylabel('Copy $i$ (source)', fontsize=11)
    ax2.set_xticks(range(m))
    ax2.set_yticks(range(m))
    plt.colorbar(im, ax=ax2, fraction=0.046, label='$\\bar{K}_{ij}$')

    # ── Annotations ──
    fig.suptitle('The Unique Multiplicity Reservoir', fontsize=14,
                 fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'f3_reservoir_svd.png'), dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved f3_reservoir_svd.png")


def plot_multiplicity_transport(result, diag_rows, output_dir='figures'):
    """Visualize multiplicity transfer matrices (F3).

    Focus on pairs with multiplicity > 1 on both sides.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os

    os.makedirs(output_dir, exist_ok=True)
    mt = result['mt']

    # ── Find interesting pairs (mult > 1 on both sides) ──
    interesting = []
    for (id_a, id_b), data in mt.items():
        if data['m_a'] > 1 and data['m_b'] > 1:
            interesting.append((id_a, id_b, data))
        elif data['m_a'] > 1 or data['m_b'] > 1:
            interesting.append((id_a, id_b, data))

    interesting.sort(key=lambda x: x[2]['K'].max(), reverse=True)

    # ── Figure 1: Gallery of multiplicity transfer K matrices ──
    n_pairs = min(len(interesting), 16)
    if n_pairs == 0:
        print("  No interesting multiplicity transfer pairs to plot.")
        return

    n_cols = min(4, n_pairs)
    n_rows = (n_pairs + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3.5*n_rows))
    if n_rows * n_cols == 1:
        axes = np.array([[axes]])
    axes = np.atleast_2d(axes)

    for idx in range(n_pairs):
        ax = axes[idx // n_cols, idx % n_cols]
        id_a, id_b, data = interesting[idx]
        K = data['K']
        m_a, m_b = data['m_a'], data['m_b']

        im = ax.imshow(K, cmap='inferno', aspect='auto')
        ax.set_title(f"{id_a} → {id_b}\n{m_a}×{m_b}", fontsize=8)
        ax.set_xlabel(f'm_b={m_b}', fontsize=7)
        ax.set_ylabel(f'm_a={m_a}', fontsize=7)
        plt.colorbar(im, ax=ax, fraction=0.046)

    # Hide unused axes
    for idx in range(n_pairs, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].axis('off')

    fig.suptitle('Multiplicity Transfer K Matrices (F3)', fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'f3_multiplicity_transfer.png'), dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved f3_multiplicity_transfer.png")

    # ── Figure 2: SVD spectrum of top pairs ──
    top_pairs = sorted(diag_rows, key=lambda r: r['max_K'], reverse=True)[:10]
    top_pairs = [r for r in top_pairs if len(r['svals']) > 1]

    if top_pairs:
        fig, ax = plt.subplots(1, 1, figsize=(12, 5))
        for i, r in enumerate(top_pairs):
            sv = r['svals']
            sv_norm = sv / sv[0] if sv[0] > 0 else sv
            ax.plot(range(1, len(sv_norm) + 1), sv_norm, 'o-',
                    label=f"{r['pair'][:45]}", markersize=4, alpha=0.8)
        ax.set_xlabel('Singular Value Index', fontsize=12)
        ax.set_ylabel('Normalized Singular Value', fontsize=12)
        ax.set_title('Multiplicity Transfer SVD Spectrum (F3)', fontsize=14)
        ax.legend(fontsize=6, ncol=2, loc='upper right')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, 'f3_svd_spectrum.png'), dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  Saved f3_svd_spectrum.png")

    # ── Figure 3: Entropy vs Isotropy scatter ──
    if diag_rows:
        ents = [r['entropy'] for r in diag_rows]
        isos = [r['isotropy'] for r in diag_rows]
        sizes = [max(r['eff_rank'] * 20, 10) for r in diag_rows]

        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        sc = ax.scatter(ents, isos, s=sizes, c=[r['max_K'] for r in diag_rows],
                        cmap='inferno', alpha=0.7, edgecolors='gray', linewidth=0.5)
        ax.set_xlabel('Entropy', fontsize=12)
        ax.set_ylabel('Isotropy Deviation (std/mean)', fontsize=12)
        ax.set_title('Multiplicity Transfer: Entropy vs Isotropy (F3)', fontsize=14)
        plt.colorbar(sc, ax=ax, label='max K')
        ax.grid(True, alpha=0.3)

        # Annotate high-entropy or high-isotropy points
        for i, r in enumerate(diag_rows):
            if r['entropy'] > 1.5 or r['isotropy'] > 0.5:
                short = r['pair'][:30]
                ax.annotate(short, (ents[i], isos[i]), fontsize=6, alpha=0.8)

        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, 'f3_entropy_isotropy.png'), dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  Saved f3_entropy_isotropy.png")


def run_f3():
    """Run full F3 pipeline: compute multiplicity transfer + analyze + plot."""
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)

    print("=" * 72)
    print("F3: Multiplicity-Fibre Tracking — Multiplicity Transfer Operators")
    print("=" * 72)

    result = multiplicity_transport(op, seed=42)
    diag_rows = analyze_multiplicity_transport(result)
    plot_multiplicity_histogram(result)
    plot_reservoir_svd_spectrum(result)
    plot_multiplicity_transport(result, diag_rows)
    print("\nF3 done.")
    return result, diag_rows


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_isotypic():
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    iso_result = isotypic_decomposition(op)

    print("=" * 72)
    print("Isotypic Decomposition (F1)")
    print("=" * 72)
    print(f"Full commutant dimension: {iso_result['full_comm_dim']}")
    print(f"Sum of per-layer comm_dim: {iso_result['dim_total']}")
    print(f"Overcompleteness ratio: {iso_result['dim_total']}/{iso_result['full_comm_dim']} = "
          f"{iso_result['dim_total']/iso_result['full_comm_dim']:.2f}")
    print()
    print(f"{'Layer':>8} {'dim':>5} {'comm':>5} {'center':>6}  Isotypic (d×mult)")
    print("-" * 72)

    total_isotypic = 0
    for lam in sorted(iso_result['blocks'], reverse=True):
        blk = iso_result['blocks'][lam]
        label = f"{lam:.4f}"
        components = "  ".join(f"{d_irr}D×{m}" for d_irr, m in blk['isotypic'])
        print(f"{label:>8} {blk['dim']:>5} {blk['commutant_dim']:>5} "
              f"{blk['center_dim']:>6}  {components}")
        total_isotypic += blk['center_dim']

    print("-" * 72)
    print(f"Total isotypic components: {total_isotypic}")
    print()

    # F2: Transport tensor
    transport = isotypic_transport_tensor(op)
    K = transport['K']
    n_iso = transport['n_isotypic']

    nz = int(np.sum(K > 1e-8))
    print("=" * 72)
    print(f"Isotypic Transport (F2): {n_iso}×{n_iso}, {nz} nonzero connections")
    print("=" * 72)

    # Print meta of each component
    print(f"\n{'idx':>3} {'lam':>8} {'dim':>5} {'d_irrep':>7} {'mult':>5}")
    print("-" * 36)
    for i, m in enumerate(transport['meta']):
        mult = m.get('mult', m.get('multiplicity', '?'))
        print(f"{i:>3} {m['lam']:>8.4f} {m['dim_proj']:>5} {m['d_irrep']:>7} {mult:>5}")

    # Find connected components
    print(f"\nTransport edges (K > 0.1):")
    for a in range(n_iso):
        for b in range(n_iso):
            if a < b and K[a, b] > 0.1:
                ma = transport['meta'][a]
                mb = transport['meta'][b]
                print(f"  {a:>2}↔{b:<2}  K={K[a,b]:.3f}  "
                      f"(λ={ma['lam']:.3f},{ma['d_irrep']}D) ↔ (λ={mb['lam']:.3f},{mb['d_irrep']}D)")

    # F4: Overcompleteness check
    print(f"\nCommutant dimension check:")
    print(f"  Full-space: {iso_result['full_comm_dim']}")
    print(f"  Sum of per-layer: {iso_result['dim_total']}")
    print(f"  Ratio: {iso_result['dim_total']/iso_result['full_comm_dim']:.2f} (> 1 = overcomplete)")

    return op, iso_result, transport



if __name__ == "__main__":
    op, iso_result, transport = analyze_isotypic()
    print("\n" + "=" * 72)
    result, diag_rows = run_f3()
    print("\nDone.")
