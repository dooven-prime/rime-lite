"""Paper VII archive: Type IV incidence search in real group representations.

Type IV incidence condition: im(B) ⊆ ker(A) where A = Q_i X_g Q_k, B = Q_k X_h Q_j.
Both A and B are nonzero, but AB = 0. Requires d_k >= 2 for nontrivial incidence.

This script searches across multiple groups and generator sets.
"""

from __future__ import annotations

import numpy as np
from itertools import combinations
from rime.accessibility import accessibility_signature
from rime.rep_utils import build_system_from_perms, symmetric_group

TOL = 1e-8


def find_all_type_iv(Vs, Xs, tol=TOL):
    """Find all Type IV (AB=0) incidence candidates in a system.

    For each gap pair (i,j) where D>=2, analyze per-commutator
    intermediate channels. A Type IV occurs when:
      - A = Q_i X_g Q_k is nonzero
      - B = Q_k X_h Q_j is nonzero
      - AB = 0 (im(B) ⊆ ker(A))

    Returns dict mapping (i,j) -> list of Type IV entries.
    """
    result = accessibility_signature(Vs, Xs, max_depth=3, tol=tol)
    D, R1 = result['D'], result['R1']
    n_sec, n_gens = len(Vs), len(Xs)

    type_iv_entries = {}
    type_iii_entries = {}

    for i in range(n_sec):
        for j in range(n_sec):
            if i == j:
                continue
            d_val = int(D[i, j])
            if d_val < 2:
                continue

            iv_list = []
            iii_list = []

            for g in range(n_gens):
                for h in range(g + 1, n_gens):
                    comm = Xs[g] @ Xs[h] - Xs[h] @ Xs[g]
                    comm_block = Vs[i].conj().T @ comm @ Vs[j]
                    comm_nrm = float(np.linalg.norm(comm_block, 'fro'))

                    if comm_nrm > tol:
                        continue  # R2 survives, no wall

                    # Commutator cancels — classify as Type III or Type IV
                    channel_info = []
                    for k in range(n_sec):
                        A_gh = Vs[i].conj().T @ Xs[g] @ Vs[k]
                        B_gh = Vs[k].conj().T @ Xs[h] @ Vs[j]
                        nrm_gh = float(np.linalg.norm(A_gh @ B_gh, 'fro'))

                        A_hg = Vs[i].conj().T @ Xs[h] @ Vs[k]
                        B_hg = Vs[k].conj().T @ Xs[g] @ Vs[j]
                        nrm_hg = float(np.linalg.norm(A_hg @ B_hg, 'fro'))

                        if nrm_gh > tol or nrm_hg > tol:
                            channel_info.append({
                                'g': g, 'h': h, 'k': k,
                                'nrm_gh': nrm_gh, 'nrm_hg': nrm_hg,
                                'a_gh_nrm': float(np.linalg.norm(A_gh, 'fro')),
                                'b_gh_nrm': float(np.linalg.norm(B_gh, 'fro')),
                                'a_hg_nrm': float(np.linalg.norm(A_hg, 'fro')),
                                'b_hg_nrm': float(np.linalg.norm(B_hg, 'fro')),
                            })

                    # Check each alive channel for AB=0
                    for ch in channel_info:
                        # Check gh ordering
                        if ch['a_gh_nrm'] > tol and ch['b_gh_nrm'] > tol and ch['nrm_gh'] <= tol:
                            iv_list.append({
                                'g': g, 'h': h, 'k': ch['k'],
                                'orientation': 'gh',
                                'd_i': Vs[i].shape[1],
                                'd_k': Vs[ch['k']].shape[1],
                                'd_j': Vs[j].shape[1],
                            })
                        # Check hg ordering
                        if ch['a_hg_nrm'] > tol and ch['b_hg_nrm'] > tol and ch['nrm_hg'] <= tol:
                            iv_list.append({
                                'g': g, 'h': h, 'k': ch['k'],
                                'orientation': 'hg',
                                'd_i': Vs[i].shape[1],
                                'd_k': Vs[ch['k']].shape[1],
                                'd_j': Vs[j].shape[1],
                            })

                    # If channels exist but none are Type IV, it's Type III
                    if channel_info and not iv_list:
                        # Check if this specific commutator is Type III
                        has_type_iii = False
                        for ch in channel_info:
                            if ch['nrm_gh'] > tol and ch['nrm_hg'] > tol:
                                has_type_iii = True
                                break
                        if has_type_iii or any(
                            (ch['a_gh_nrm'] > tol and ch['b_gh_nrm'] > tol and ch['nrm_gh'] > tol) or
                            (ch['a_hg_nrm'] > tol and ch['b_hg_nrm'] > tol and ch['nrm_hg'] > tol)
                            for ch in channel_info
                        ):
                            # Products exist but cancel in commutator sum
                            if all(ch['nrm_gh'] <= tol or ch['nrm_hg'] <= tol for ch in channel_info):
                                # Actually Type III: products nonzero, difference zero
                                iii_list.append({
                                    'g': g, 'h': h,
                                    'n_channels': len(channel_info),
                                    'comm_nrm': comm_nrm,
                                })

            if iv_list:
                type_iv_entries[(i, j)] = iv_list
            if iii_list:
                type_iii_entries[(i, j)] = iii_list

    return {
        'D': D,
        'R1': R1,
        'sig': result['sig'],
        'n_sec': n_sec,
        'n_gens': n_gens,
        'type_iv': type_iv_entries,
        'type_iii': type_iii_entries,
        'dims': [V.shape[1] for V in Vs],
    }


def print_findings(findings, label):
    """Print Type IV and Type III findings for a system."""
    print(f"  Sectors: {findings['n_sec']}, dims={findings['dims']}")
    print(f"  Generators: {findings['n_gens']}")
    print(f"  Signature: {findings['sig']}")

    if findings['type_iv']:
        print(f"  *** TYPE IV FOUND: {len(findings['type_iv'])} gap pairs ***")
        for (i, j), entries in findings['type_iv'].items():
            print(f"    S{i}->S{j} (D={int(findings['D'][i,j])}):")
            for e in entries[:5]:  # Show first 5
                print(f"      [{e['g']},{e['h']}] via S{e['k']} "
                      f"orient={e['orientation']} "
                      f"dims=({e['d_i']},{e['d_k']},{e['d_j']})")
            if len(entries) > 5:
                print(f"      ... and {len(entries) - 5} more")
    else:
        print(f"  No Type IV found.")

    if findings['type_iii']:
        print(f"  Type III gap pairs: {len(findings['type_iii'])}")
        for (i, j), entries in findings['type_iii'].items():
            print(f"    S{i}->S{j} (D={int(findings['D'][i,j])}): "
                  f"{len(entries)} cancelling commutators")
    print()


# ============================================================
# Search across S4 generator sets
# ============================================================

def search_s4():
    """Search all 2-generator and selected 3-generator sets of S4."""
    print("=" * 72)
    print("SEARCH: S4 — All 2-generator subsets")
    print("=" * 72)

    S4 = symmetric_group(4)

    # All 2-element subsets
    n_found = 0
    for idx, (p1, p2) in enumerate(combinations(S4, 2)):
        if p1 == tuple(range(4)) or p2 == tuple(range(4)):
            continue  # Skip identity
        try:
            system = build_system_from_perms(S4, [p1, p2])
            findings = find_all_type_iv(system['Vs'], system['Xs'])
            n_iv = len(findings['type_iv'])
            if n_iv > 0:
                n_found += 1
                print(f"\n  [{idx}] GEN_PERMS={[p1, p2]}")
                print_findings(findings, f"S4-2gen-{idx}")
        except Exception as e:
            pass

    print(f"\n  Total 2-gen sets with Type IV: {n_found}")

    # Selected 3-generator sets (known interesting ones)
    print()
    print("=" * 72)
    print("SEARCH: S4 — Selected 3-generator subsets")
    print("=" * 72)

    candidate_3gen_sets = [
        [(1, 0, 2, 3), (0, 2, 1, 3), (1, 2, 3, 0)],  # (12), (23), (1234)
        [(1, 0, 2, 3), (0, 1, 3, 2), (1, 2, 3, 0)],  # (12), (34), (1234)
        [(0, 1, 3, 2), (1, 0, 2, 3), (0, 2, 1, 3)],  # (34), (12), (23)
        [(1, 2, 3, 0), (1, 3, 0, 2), (0, 1, 2, 3)],  # 4-cycle, 4-cycle, identity-like
    ]

    for gen_perms in candidate_3gen_sets:
        gen_perms = [p for p in gen_perms if p != tuple(range(4))]
        if len(gen_perms) < 2:
            continue
        try:
            system = build_system_from_perms(S4, gen_perms)
            findings = find_all_type_iv(system['Vs'], system['Xs'])
            print(f"\n  GEN_PERMS={gen_perms}")
            print_findings(findings, f"S4-{len(gen_perms)}gen")
            if findings['type_iv']:
                n_found += 1
        except Exception as e:
            print(f"  Error: {e}")

    return n_found


# ============================================================
# Search across A5 generator sets
# ============================================================

def search_a5():
    """Search selected generator sets of A5."""
    print("=" * 72)
    print("SEARCH: A5 — 3-cycle generator sets")
    print("=" * 72)

    S5 = symmetric_group(5)

    def is_even(p):
        visited = [False] * len(p)
        swaps = 0
        for start in range(len(p)):
            if not visited[start]:
                cur, clen = start, 0
                while not visited[cur]:
                    visited[cur] = True
                    cur = p[cur]
                    clen += 1
                swaps += clen - 1
        return swaps % 2 == 0

    A5 = [p for p in S5 if is_even(p)]

    # Find all 3-cycles
    three_cycles = [p for p in A5 if len(set(
        tuple(sorted([len([q for q in range(5) if q != x and p[q] != q]) for x in range(5)]))
    )) == 1 and sum(1 for i in range(5) if p[i] != i) == 3]

    # Simpler: classify by cycle type
    def cycle_key(p):
        visited = [False] * len(p)
        cycles = []
        for start in range(len(p)):
            if not visited[start]:
                cur, clen = start, 0
                while not visited[cur]:
                    visited[cur] = True
                    cur = p[cur]
                    clen += 1
                if clen > 1:
                    cycles.append(clen)
        return tuple(sorted(cycles))

    three_cycles = [p for p in A5 if cycle_key(p) == (3,)]

    print(f"  Found {len(three_cycles)} 3-cycles in A5")

    # Try random 3-generator sets of 3-cycles
    rng = np.random.RandomState(42)
    n_tried = 0
    n_found = 0

    for trial in range(50):
        idxs = rng.choice(len(three_cycles), 3, replace=False)
        gen_perms = [three_cycles[i] for i in idxs]

        try:
            system = build_system_from_perms(A5, gen_perms)
            findings = find_all_type_iv(system['Vs'], system['Xs'])
            n_tried += 1

            if findings['type_iv']:
                n_found += 1
                print(f"\n  [TRIAL {trial}] GEN_PERMS={gen_perms}")
                print_findings(findings, f"A5-3gen-{trial}")
            elif findings['type_iii']:
                # Print first few Type III systems
                if n_tried <= 5:
                    print(f"\n  [TRIAL {trial}] Type III only: sig={findings['sig']}")
        except Exception as e:
            pass

    print(f"\n  Tried {n_tried} A5 3-gen sets, {n_found} with Type IV")
    return n_found


# ============================================================
# Search D8 and Q8
# ============================================================

def build_d8():
    """Build D8 group (dihedral group of order 8) as permutations.

    D8 = <r, s | r^4 = s^2 = 1, srs = r^{-1}>
    Represented as permutations of 4 vertices of a square.
    """
    # r = rotation by 90 deg = (0 1 2 3)
    r = (1, 2, 3, 0)
    # s = reflection = (0 2)(1 3) — but let's use (1,0,3,2) = flip across diagonal
    # Actually let's use the standard D8 action on 4 elements
    s = (1, 0, 3, 2)

    # Generate all elements
    from rime.rep_utils import compose_perm
    elements = []
    seen = set()
    queue = [(0, 1, 2, 3)]  # identity
    while queue:
        e = queue.pop(0)
        if e in seen:
            continue
        seen.add(e)
        elements.append(e)
        queue.append(compose_perm(r, e))
        queue.append(compose_perm(s, e))
    return elements, r, s


def search_d8():
    """Search D8 with various generator subsets."""
    print("=" * 72)
    print("SEARCH: D8 — Various generator subsets")
    print("=" * 72)

    elements, r, s = build_d8()
    print(f"  D8 order: {len(elements)}")

    # Generators: r, s, rs, r^2, etc.
    gen_candidates = {
        'r': r,
        's': s,
        'r2': (2, 3, 0, 1),  # r^2
        'r3': (3, 0, 1, 2),  # r^3
        'rs': tuple(r[s[i]] for i in range(4)),
        'sr': tuple(s[r[i]] for i in range(4)),
    }

    n_found = 0
    gen_names = list(gen_candidates.keys())

    # Try all 2-generator and 3-generator sets
    for r in range(2, 4):
        for combo in combinations(range(len(gen_names)), r):
            gen_perms = [gen_candidates[gen_names[i]] for i in combo]
            try:
                system = build_system_from_perms(elements, gen_perms)
                findings = find_all_type_iv(system['Vs'], system['Xs'])
                names = [gen_names[i] for i in combo]
                print(f"\n  GEN={names}")
                print_findings(findings, f"D8-{len(names)}gen")
                if findings['type_iv']:
                    n_found += 1
            except Exception as e:
                print(f"  Error with {names}: {e}")

    print(f"\n  D8: {n_found} sets with Type IV")
    return n_found


# ============================================================
# Search Q8 (quaternion group)
# ============================================================

def build_q8_perm():
    """Build Q8 as a permutation group.

    Q8 = {±1, ±i, ±j, ±k} where i^2 = j^2 = k^2 = ijk = -1.
    Represented via left multiplication action on Q8 itself (regular rep, 8-dim).
    """
    # Use the standard Q8 elements as 8 abstract labels
    # Left multiplication gives an 8-dim permutation representation
    labels = ['1', '-1', 'i', '-i', 'j', '-j', 'k', '-k']

    def multiply(a, b):
        """Q8 multiplication table."""
        table = {
            ('1', '1'): '1', ('1', '-1'): '-1', ('1', 'i'): 'i', ('1', '-i'): '-i',
            ('1', 'j'): 'j', ('1', '-j'): '-j', ('1', 'k'): 'k', ('1', '-k'): '-k',
            ('-1', '1'): '-1', ('-1', '-1'): '1', ('-1', 'i'): '-i', ('-1', '-i'): 'i',
            ('-1', 'j'): '-j', ('-1', '-j'): 'j', ('-1', 'k'): '-k', ('-1', '-k'): 'k',
            ('i', '1'): 'i', ('i', '-1'): '-i', ('i', 'i'): '-1', ('i', '-i'): '1',
            ('i', 'j'): 'k', ('i', '-j'): '-k', ('i', 'k'): '-j', ('i', '-k'): 'j',
            ('-i', '1'): '-i', ('-i', '-1'): 'i', ('-i', 'i'): '1', ('-i', '-i'): '-1',
            ('-i', 'j'): '-k', ('-i', '-j'): 'k', ('-i', 'k'): 'j', ('-i', '-k'): '-j',
            ('j', '1'): 'j', ('j', '-1'): '-j', ('j', 'i'): '-k', ('j', '-i'): 'k',
            ('j', 'j'): '-1', ('j', '-j'): '1', ('j', 'k'): 'i', ('j', '-k'): '-i',
            ('-j', '1'): '-j', ('-j', '-1'): 'j', ('-j', 'i'): 'k', ('-j', '-i'): '-k',
            ('-j', 'j'): '1', ('-j', '-j'): '-1', ('-j', 'k'): '-i', ('-j', '-k'): 'i',
            ('k', '1'): 'k', ('k', '-1'): '-k', ('k', 'i'): 'j', ('k', '-i'): '-j',
            ('k', 'j'): '-i', ('k', '-j'): 'i', ('k', 'k'): '-1', ('k', '-k'): '1',
            ('-k', '1'): '-k', ('-k', '-1'): 'k', ('-k', 'i'): '-j', ('-k', '-i'): 'j',
            ('-k', 'j'): 'i', ('-k', '-j'): '-i', ('-k', 'k'): '1', ('-k', '-k'): '-1',
        }
        return table[(a, b)]

    idx = {label: i for i, label in enumerate(labels)}

    def to_perm(g):
        """Left multiplication by g as a permutation of the 8 labels."""
        result = [0] * 8
        for i, h in enumerate(labels):
            result[i] = idx[multiply(g, h)]
        return tuple(result)

    elements = [to_perm(g) for g in labels]
    i_perm = to_perm('i')
    j_perm = to_perm('j')
    k_perm = to_perm('k')

    return elements, i_perm, j_perm, k_perm


def search_q8():
    """Search Q8 with various generator subsets."""
    print("=" * 72)
    print("SEARCH: Q8 — Various generator subsets")
    print("=" * 72)

    elements, i_perm, j_perm, k_perm = build_q8_perm()
    print(f"  Q8 order: {len(elements)}")

    gen_map = {'i': i_perm, 'j': j_perm, 'k': k_perm}
    gen_names = list(gen_map.keys())

    n_found = 0

    # Try 2-generator sets (any pair generates Q8)
    for combo in combinations(range(len(gen_names)), 2):
        names = [gen_names[i] for i in combo]
        gen_perms = [gen_map[n] for n in names]
        try:
            system = build_system_from_perms(elements, gen_perms)
            findings = find_all_type_iv(system['Vs'], system['Xs'])
            print(f"\n  GEN={names}")
            print_findings(findings, f"Q8-2gen")
            if findings['type_iv']:
                n_found += 1
        except Exception as e:
            print(f"  Error with {names}: {e}")

    # Try all 3 generators
    try:
        system = build_system_from_perms(elements, [i_perm, j_perm, k_perm])
        findings = find_all_type_iv(system['Vs'], system['Xs'])
        print(f"\n  GEN=['i','j','k']")
        print_findings(findings, f"Q8-3gen")
        if findings['type_iv']:
            n_found += 1
    except Exception as e:
        print(f"  Error with i,j,k: {e}")

    print(f"\n  Q8: {n_found} sets with Type IV")
    return n_found


# ============================================================
# Search S5 with 2 generators
# ============================================================

def search_s5():
    """Search S5 with (12) and (12345) generators."""
    print("=" * 72)
    print("SEARCH: S5 — Standard 2-generator set")
    print("=" * 72)

    S5 = symmetric_group(5)
    print(f"  S5 order: {len(S5)}")

    # S5 is generated by a transposition and a 5-cycle
    gen_sets = [
        [(1, 0, 2, 3, 4), (1, 2, 3, 4, 0)],  # (12), (12345)
        [(1, 0, 2, 3, 4), (0, 2, 3, 4, 1)],  # different 5-cycle
    ]

    n_found = 0
    for gen_perms in gen_sets:
        try:
            system = build_system_from_perms(S5, gen_perms)
            findings = find_all_type_iv(system['Vs'], system['Xs'])
            print(f"\n  GEN_PERMS={gen_perms}")
            print_findings(findings, "S5-2gen")
            if findings['type_iv']:
                n_found += 1
        except Exception as e:
            print(f"  Error: {e}")

    return n_found


# ============================================================
# Detailed Type IV analysis for a confirmed candidate
# ============================================================

def analyze_type4_detail(Vs, Xs, gap_pair, tol=TOL):
    """Detailed Type IV analysis for a specific gap pair."""
    i, j = gap_pair
    n_gens = len(Xs)
    n_sec = len(Vs)

    print(f"  Detailed Type IV analysis for S{i}->S{j}:")
    print(f"  dims: d_i={Vs[i].shape[1]}, d_j={Vs[j].shape[1]}")

    iv_entries = []

    for g in range(n_gens):
        for h in range(n_gens):
            if g == h:
                continue
            for k in range(n_sec):
                A = Vs[i].conj().T @ Xs[g] @ Vs[k]
                B = Vs[k].conj().T @ Xs[h] @ Vs[j]
                a_nrm = float(np.linalg.norm(A, 'fro'))
                b_nrm = float(np.linalg.norm(B, 'fro'))

                if a_nrm > tol and b_nrm > tol:
                    AB = A @ B
                    ab_nrm = float(np.linalg.norm(AB, 'fro'))
                    if ab_nrm <= tol:
                        rank_A = int(np.linalg.matrix_rank(A, tol=tol))
                        rank_B = int(np.linalg.matrix_rank(B, tol=tol))
                        d_k = Vs[k].shape[1]

                        # Verify: im(B) ⊆ ker(A)
                        # ker(A) nullspace
                        _, s, Vh = np.linalg.svd(A, full_matrices=True)
                        null_dim = int(np.sum(s <= tol))
                        ker_A_basis = Vh[rank_A:, :].conj().T if null_dim > 0 else None

                        # im(B) basis
                        U_b, s_b, Vh_b = np.linalg.svd(B, full_matrices=True)
                        im_B_basis = U_b[:, :rank_B] if rank_B > 0 else None

                        iv_entries.append({
                            'g': g, 'h': h, 'k': k,
                            'orientation': 'gh',
                            'd_i': Vs[i].shape[1], 'd_k': d_k, 'd_j': Vs[j].shape[1],
                            'rank_A': rank_A, 'rank_B': rank_B,
                            'a_nrm': a_nrm, 'b_nrm': b_nrm, 'ab_nrm': ab_nrm,
                            'null_dim': null_dim,
                        })

                        print(f"    X{g}->S{k}->X{h}: A={A.shape} rank={rank_A}, "
                              f"B={B.shape} rank={rank_B}, |A|={a_nrm:.3f}, "
                              f"|B|={b_nrm:.3f}, |AB|={ab_nrm:.2e}")
                        print(f"      d_k={d_k}, nullity(A)={null_dim}, "
                              f"im(B)<=ker(A): {'YES' if null_dim >= rank_B else 'check'}")

    return iv_entries


# ============================================================
# Main
# ============================================================

def main():
    np.random.seed(42)
    total_iv = 0

    # Search S4
    n = search_s4()
    total_iv += n

    # Search A5
    n = search_a5()
    total_iv += n

    # Search D8
    n = search_d8()
    total_iv += n

    # Search Q8
    n = search_q8()
    total_iv += n

    # Search S5
    n = search_s5()
    total_iv += n

    print()
    print("=" * 72)
    print(f"TOTAL: {total_iv} generator sets with Type IV found across all groups")
    print("=" * 72)


if __name__ == "__main__":
    main()
