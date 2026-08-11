"""Paper XIII: Compiler IR SOF Report Alignment -- Regime A control.

5 basic blocks, 2 observable families:
  X_cfg    -- control-flow edges (branch/jump targets)
  X_defuse -- data-flow edges (def-use chains across blocks)

Reference = O2-like optimized CFG with intact data dependences.
Candidate = buggy pass or mis-optimized variant.

Natural alignment (compiler-native):
  basic-block names, SSA value provenance, CFG node correspondence,
  dominance tree, debug metadata.

Failure modes:
  F1 cfg/defuse aliasing   X_defuse replaced by X_cfg (data-flow structure lost)
  F2 dead branch loss      B3 isolated -- both CFG and def-use edges removed
  F3 spurious cfg edge     hallucinated B0->B4 direct jump
  F4 lost def-use dep      data edge B3->B4 removed, CFG edge B3->B4 kept
  F5 pass-pipeline wall    O0(6 edges) -> mem2reg -> simplifycfg(remove B3)

Claim status: controlled protocol validation (Regime A).  Not a compiler
correctness proof.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import (  # noqa: E402
    AccessibilityEngine,
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
    offdiag_count,
)
from report_contract import (  # noqa: E402
    build_sofaudit,
    build_sofreport,
    write_artifact,
)

# ── constants ────────────────────────────────────────────────────────────────
N_BLOCKS = 5
B0, B1, B2, B3, B4 = 0, 1, 2, 3, 4
LABELS = ["B0(entry)", "B1", "B2", "B3(side)", "B4(exit)"]
WEIGHT = 1.0
TOL = 1e-8
FROZEN = 999
MAX_DEPTH = 4

# Directed CFG edges (control flow)
#   B0 -> B1 -> B2 -> B4 (main path)
#   B1 -> B3 -> B4       (side path via B3, may be removed by simplifycfg)
CFG_EDGES = [(B0, B1), (B1, B2), (B1, B3), (B2, B4), (B3, B4)]

# Directed def-use edges (data flow)
#   B0:x used in B1; B1:y used in B2,B4; B3:z used in B4
DEFUSE_EDGES = [(B0, B1), (B1, B2), (B1, B4), (B3, B4)]


# ── Compiler IR Model ────────────────────────────────────────────────────────
class CompilerIR:
    """5-block CFG with control-flow and data-flow observable families.

    Reference (O2-like): all CFG and def-use edges active.
    Candidate: may have removed edges (dead branch), spurious edges, or
    broken data dependences.
    """

    def __init__(self, cfg_edges: list[tuple[int, int]] | None = None,
                 defuse_edges: list[tuple[int, int]] | None = None,
                 cfg_weight: float = WEIGHT, defuse_weight: float = WEIGHT):
        self.cfg = list(cfg_edges) if cfg_edges is not None else list(CFG_EDGES)
        self.defuse = list(defuse_edges) if defuse_edges is not None else list(DEFUSE_EDGES)
        self.w_cfg = float(cfg_weight)
        self.w_def = float(defuse_weight)

    def _edge_matrix(self, edges: list[tuple[int, int]], weight: float) -> np.ndarray:
        T = np.eye(N_BLOCKS, dtype=float)
        for src, dst in edges:
            T[dst, src] = weight
            T[src, src] = max(0.0, T[src, src] - weight)
        return T

    def action_matrices(self) -> dict[str, np.ndarray]:
        return {
            "X_cfg": self._edge_matrix(self.cfg, self.w_cfg),
            "X_defuse": self._edge_matrix(self.defuse, self.w_def),
        }

    def label(self) -> str:
        return f"IR(cfg={len(self.cfg)}e, defuse={len(self.defuse)}e)"


# ── SOF construction ─────────────────────────────────────────────────────────
def skew(M: np.ndarray) -> np.ndarray:
    return ((M - M.T) / 2.0).astype(complex)


def block_sectors() -> list[np.ndarray]:
    eye = np.eye(N_BLOCKS, dtype=complex)
    return [eye[:, [j]] for j in range(N_BLOCKS)]


def build_observables(mats: dict[str, np.ndarray]) -> tuple[list[np.ndarray], dict[str, np.ndarray]]:
    raw = {a: T.copy() for a, T in mats.items()}
    obs = [skew(T) for T in mats.values()]
    return obs, raw


def action_response_matrix(sectors: list[np.ndarray], X: np.ndarray) -> np.ndarray:
    n = len(sectors)
    R = np.zeros((n, n), dtype=float)
    for i in range(n):
        PiX = sectors[i].conj().T @ X
        for j in range(n):
            if i != j:
                R[i, j] = float(np.linalg.norm(PiX @ sectors[j]))
    return R


def full_audit(sectors: list[np.ndarray], observables: list[np.ndarray]) -> dict:
    engine = AccessibilityEngine(sectors, observables, tol=TOL, max_depth=MAX_DEPTH)
    lie = engine.audit()
    frozen = engine.frozen_pairs()
    _R1, _R2_lie, _ = engine.support()
    D_lie, _ = engine.depth()

    R1_word = compute_direct_support(sectors, observables, tol=TOL)
    R2_word = compute_length_two_support(sectors, observables, tol=TOL)
    D_word = compute_word_depth_matrix(sectors, observables, max_depth=MAX_DEPTH, tol=TOL, frozen=FROZEN)
    R2_lie_agg = np.any(_R2_lie, axis=0)
    frozen_D_word = sum(
        1 for i in range(len(sectors)) for j in range(len(sectors))
        if i != j and D_word[i, j] == FROZEN
    )

    return {
        "n_sec": len(sectors), "n_obs": len(observables),
        "R1_word": R1_word, "R1_offdiag": offdiag_count(R1_word),
        "R2_word": R2_word, "R2_word_offdiag": offdiag_count(R2_word),
        "R2_lie": R2_lie_agg, "R2_lie_offdiag": offdiag_count(R2_lie_agg),
        "D_word": D_word,
        "D_word_max": int(D_word[D_word != FROZEN].max()) if np.any(D_word != FROZEN) else 0,
        "D_lie": D_lie,
        "D_lie_max": int(D_lie[D_lie != FROZEN].max()) if np.any(D_lie != FROZEN) else 0,
        "frozen_D_word": frozen_D_word,
        "frozen_D_lie": frozen["frozen_D"],
        **lie, **frozen,
    }


# ── failure-mode constructors ────────────────────────────────────────────────
def build_reference() -> CompilerIR:
    """O2-like: all CFG and def-use edges present, B3 reachable."""
    return CompilerIR()


def build_f1_cfg_defuse_aliasing() -> dict[str, np.ndarray]:
    """X_defuse replaced by X_cfg -- data-flow structure indistinguishable from CFG."""
    ref = build_reference()
    mats = ref.action_matrices()
    mats["X_defuse"] = mats["X_cfg"].copy()
    return mats


def build_f2_dead_branch() -> dict[str, np.ndarray]:
    """B3 isolated: CFG edges B1->B3 and B3->B4 removed, def-use B3->B4 removed.
    simplifycfg deleted the side branch -- B3 becomes dead code."""
    return CompilerIR(
        cfg_edges=[(B0, B1), (B1, B2), (B2, B4)],
        defuse_edges=[(B0, B1), (B1, B2), (B1, B4)],
    ).action_matrices()


def build_f3_spurious_cfg_edge() -> dict[str, np.ndarray]:
    """Hallucinated B0->B4 direct jump in X_cfg."""
    ref = build_reference()
    mats = ref.action_matrices()
    T = mats["X_cfg"].copy()
    w = 1.0 / 6.0
    T[B4, B0] = w
    T[B0, B0] = max(0.0, T[B0, B0] - w)
    mats["X_cfg"] = T
    return mats


def build_f4_lost_defuse() -> dict[str, np.ndarray]:
    """Data edge B3->B4 removed, but CFG edge B3->B4 kept.
    Data dependence broken while control flow intact -- bridge mismatch
    without support mismatch."""
    return CompilerIR(
        defuse_edges=[(B0, B1), (B1, B2), (B1, B4)],  # B3->B4 removed
    ).action_matrices()


def build_f5_pass_pipeline() -> list[CompilerIR]:
    """Reference pass sequence: O0 -> mem2reg -> simplifycfg.
    3 passes; simplifycfg removes B3, creating a topological wall."""
    o0 = CompilerIR(
        cfg_edges=[(B0, B1), (B1, B2), (B1, B3), (B2, B4), (B3, B4)],
        defuse_edges=[(B0, B1), (B1, B2), (B1, B4), (B3, B4)],
    )
    mem2reg = CompilerIR(
        cfg_edges=[(B0, B1), (B1, B2), (B1, B3), (B2, B4), (B3, B4)],
        defuse_edges=[(B0, B1), (B1, B2), (B1, B4), (B3, B4), (B2, B4)],
    )
    simplifycfg = CompilerIR(
        cfg_edges=[(B0, B1), (B1, B2), (B2, B4)],
        defuse_edges=[(B0, B1), (B1, B2), (B1, B4), (B2, B4)],
    )
    return [o0, mem2reg, simplifycfg]


def build_f5_learned() -> CompilerIR:
    """Buggy pipeline fixed at the pre-simplifycfg reference snapshot.

    The single-snapshot diff is zero against the base reference. Only the
    pass-path wall record captures that simplifycfg was not followed.
    """
    return build_reference()  # same O2-like state as reference


# ── wall record ──────────────────────────────────────────────────────────────
def compute_wall_record(models: list[CompilerIR]) -> list[dict]:
    sectors = block_sectors()
    records = []
    for m in models:
        mats = m.action_matrices()
        obs, _ = build_observables(mats)
        audit = full_audit(sectors, obs)
        records.append({
            "cfg_edges": len(m.cfg), "defuse_edges": len(m.defuse),
            "label": m.label(),
            "frozen_R1": audit["frozen_R1"],
            "frozen_D_word": audit["frozen_D_word"],
            "frozen_D_lie": audit["frozen_D_lie"],
        })
    return records


# ── diff protocol ────────────────────────────────────────────────────────────
def _mismatch_pairs(A_ref: np.ndarray, A_lrn: np.ndarray) -> dict:
    n = A_ref.shape[0]
    extra, missing = [], []
    for i in range(n):
        for j in range(n):
            if i == j: continue
            if A_ref[i, j] and not A_lrn[i, j]: missing.append([i, j])
            elif not A_ref[i, j] and A_lrn[i, j]: extra.append([i, j])
    return {"extra": extra, "extra_count": len(extra), "missing": missing,
            "missing_count": len(missing), "total_mismatch": len(extra) + len(missing),
            "ref_offdiag": offdiag_count(A_ref), "learned_offdiag": offdiag_count(A_lrn)}


def diff_depth(D_ref: np.ndarray, D_lrn: np.ndarray) -> dict:
    n = D_ref.shape[0]
    distortions, ref_frz, lrn_frz = [], [], []
    for i in range(n):
        for j in range(n):
            if i == j: continue
            dr, dl = D_ref[i, j], D_lrn[i, j]
            rf, lf = dr == FROZEN, dl == FROZEN
            if rf and not lf: ref_frz.append([i, j, int(dl)])
            elif not rf and lf: lrn_frz.append([i, j, int(dr)])
            elif not rf and not lf and dr != dl: distortions.append([i, j, int(dr), int(dl)])
    return {"total_mismatch": len(distortions) + len(ref_frz) + len(lrn_frz),
            "depth_distortions": distortions, "distortion_count": len(distortions),
            "ref_frozen_learned_not": ref_frz, "ref_frozen_learned_not_count": len(ref_frz),
            "learned_frozen_ref_not": lrn_frz, "learned_frozen_ref_not_count": len(lrn_frz)}


def diff_constraint_violations(raw_ref, raw_lrn, tol=TOL) -> dict:
    violations = []
    for a in ["X_cfg", "X_defuse"]:
        Tr = raw_ref.get(a, np.zeros((N_BLOCKS, N_BLOCKS)))
        Tl = raw_lrn.get(a, np.zeros((N_BLOCKS, N_BLOCKS)))
        for i in range(N_BLOCKS):
            for j in range(N_BLOCKS):
                if i == j: continue
                if abs(Tr[i, j]) < tol and abs(Tl[i, j]) >= tol:
                    violations.append({"action": a, "from": LABELS[j], "to": LABELS[i],
                                       "learned_value": float(Tl[i, j])})
    return {"violations": violations, "count": len(violations)}


def diff_action_response(resp_ref, resp_lrn, threshold=0.001) -> dict:
    deltas = {}
    for a in ["X_cfg", "X_defuse"]:
        Rr, Rl = resp_ref[a], resp_lrn[a]
        large = []
        for i in range(N_BLOCKS):
            for j in range(N_BLOCKS):
                if i == j: continue
                d = abs(Rr[i, j] - Rl[i, j])
                if d > threshold:
                    large.append({"pair": [LABELS[i], LABELS[j]],
                                  "ref": round(Rr[i, j], 6), "learned": round(Rl[i, j], 6),
                                  "delta": round(d, 6)})
        deltas[a] = large
    sep_ref = np.linalg.norm(resp_ref["X_cfg"] - resp_ref["X_defuse"])
    sep_lrn = np.linalg.norm(resp_lrn["X_cfg"] - resp_lrn["X_defuse"])
    aliasing = []
    if sep_ref > threshold and sep_lrn < threshold:
        aliasing.append({"sep_ref": round(sep_ref, 6), "sep_learned": round(sep_lrn, 6),
                         "diagnosis": "aliased"})
    return {"per_action_deltas": deltas,
            "total_large_deltas": sum(len(v) for v in deltas.values()),
            "action_aliasing": aliasing,
            "response_sep": {"ref": round(sep_ref, 6), "learned": round(sep_lrn, 6)}}


def _diff_wall(wall_ref, wall_lrn) -> dict:
    steps = []
    for k in range(len(wall_ref)):
        fr, fl = wall_ref[k], wall_lrn[k]
        steps.append({
            "step": k, "label": fr["label"],
            "cfg_edges_ref": fr["cfg_edges"], "cfg_edges_lrn": fl["cfg_edges"],
            "defuse_edges_ref": fr["defuse_edges"], "defuse_edges_lrn": fl["defuse_edges"],
            "frozen_R1_ref": fr["frozen_R1"], "frozen_R1_lrn": fl["frozen_R1"],
            "frozen_R1_delta": fl["frozen_R1"] - fr["frozen_R1"],
            "frozen_D_word_ref": fr["frozen_D_word"], "frozen_D_word_lrn": fl["frozen_D_word"],
            "frozen_D_word_delta": fl["frozen_D_word"] - fr["frozen_D_word"],
            "frozen_D_lie_ref": fr["frozen_D_lie"], "frozen_D_lie_lrn": fl["frozen_D_lie"],
            "frozen_D_lie_delta": fl["frozen_D_lie"] - fr["frozen_D_lie"],
        })
    return {"steps": steps, "n_steps": len(steps)}


def full_diff(ref_audit, lrn_audit, raw_ref=None, raw_lrn=None,
              resp_ref=None, resp_lrn=None, wall_ref=None, wall_lrn=None) -> dict:
    result = {
        "support_mismatch": _mismatch_pairs(ref_audit["R1_word"], lrn_audit["R1_word"]),
        "bridge_word_mismatch": _mismatch_pairs(ref_audit["R2_word"], lrn_audit["R2_word"]),
        "bridge_lie_mismatch": _mismatch_pairs(ref_audit["R2_lie"], lrn_audit["R2_lie"]),
        "depth_distortion": diff_depth(ref_audit["D_word"], lrn_audit["D_word"]),
        "frozen_pair_disagreement": {
            "frozen_R1": {"ref": ref_audit["frozen_R1"], "learned": lrn_audit["frozen_R1"],
                          "delta": lrn_audit["frozen_R1"] - ref_audit["frozen_R1"]},
            "frozen_D_word": {"ref": ref_audit["frozen_D_word"], "learned": lrn_audit["frozen_D_word"],
                              "delta": lrn_audit["frozen_D_word"] - ref_audit["frozen_D_word"]},
            "frozen_D_lie": {"ref": ref_audit["frozen_D_lie"], "learned": lrn_audit["frozen_D_lie"],
                             "delta": lrn_audit["frozen_D_lie"] - ref_audit["frozen_D_lie"]},
        },
    }
    if raw_ref is not None and raw_lrn is not None:
        result["constraint_violations"] = diff_constraint_violations(raw_ref, raw_lrn)
    if resp_ref is not None and resp_lrn is not None:
        result["action_response_failure"] = diff_action_response(resp_ref, resp_lrn)
    if wall_ref is not None and wall_lrn is not None:
        result["wall_record_mismatch"] = _diff_wall(wall_ref, wall_lrn)
    return result


def run_failure_mode(name: str, lrn_mats: dict[str, np.ndarray],
                     lrn_label: str = "", wall_ref=None, wall_lrn=None) -> dict:
    sectors = block_sectors()
    ref_model = build_reference()
    ref_mats = ref_model.action_matrices()
    ref_obs, ref_raw = build_observables(ref_mats)
    ref_audit = full_audit(sectors, ref_obs)
    ref_resp = {a: action_response_matrix(sectors, skew(ref_mats[a])) for a in ["X_cfg", "X_defuse"]}

    lrn_obs, lrn_raw = build_observables(lrn_mats)
    lrn_audit = full_audit(sectors, lrn_obs)
    lrn_resp = {a: action_response_matrix(sectors, skew(lrn_mats[a])) for a in ["X_cfg", "X_defuse"]}

    diff = full_diff(ref_audit, lrn_audit, raw_ref=ref_raw, raw_lrn=lrn_raw,
                     resp_ref=ref_resp, resp_lrn=lrn_resp,
                     wall_ref=wall_ref, wall_lrn=wall_lrn)
    return {"name": name, "ref_audit": ref_audit, "learned_audit": lrn_audit,
            "diff": diff, "ref_label": ref_model.label(),
            "learned_label": lrn_label or name}


# ── print helpers ────────────────────────────────────────────────────────────
def print_matrix(label: str, mat: np.ndarray) -> None:
    short = [l.split("(")[0] for l in LABELS]
    print(f"    {label}:")
    header = "        " + "  ".join(f"{l:>6s}" for l in short)
    print(header)
    for i, rl in enumerate(short):
        vals = "  ".join(f"{mat[i, j]:>6.3f}" if isinstance(mat[i, j], (np.floating, float))
                         else f"{str(mat[i, j]):>6s}" for j in range(len(short)))
        print(f"      {rl}: [{vals}]")


def print_diff_summary(diff: dict) -> None:
    sm = diff["support_mismatch"]
    print(f"    Support mismatch:          {sm['total_mismatch']:>3d}  (extra={sm['extra_count']}, missing={sm['missing_count']})")
    bw = diff["bridge_word_mismatch"]
    print(f"    Bridge mismatch (word):    {bw['total_mismatch']:>3d}  (extra={bw['extra_count']}, missing={bw['missing_count']})")
    bl = diff["bridge_lie_mismatch"]
    print(f"    Bridge mismatch (Lie):     {bl['total_mismatch']:>3d}  (extra={bl['extra_count']}, missing={bl['missing_count']})")
    dd = diff["depth_distortion"]
    print(f"    Depth distortion:          {dd['total_mismatch']:>3d}  (pure={dd['distortion_count']}, frz-changes={dd['ref_frozen_learned_not_count']}+{dd['learned_frozen_ref_not_count']})")
    fp = diff["frozen_pair_disagreement"]
    print(f"    Frozen R1 delta:           {fp['frozen_R1']['delta']:>+3d}")
    print(f"    Frozen D_word delta:       {fp['frozen_D_word']['delta']:>+3d}")
    print(f"    Frozen D_lie delta:        {fp['frozen_D_lie']['delta']:>+3d}")
    if "constraint_violations" in diff:
        cv = diff["constraint_violations"]
        print(f"    Constraint violations:     {cv['count']:>3d}")
        for v in cv["violations"]:
            print(f"      {v['action']}: {v['from']} -> {v['to']}  (learned={v['learned_value']:.4f})")
    if "action_response_failure" in diff:
        ar = diff["action_response_failure"]
        rs = ar.get("response_sep", {})
        print(f"    Control-response delta>eps: {ar['total_large_deltas']:>3d}  (cfg/defuse sep ref={rs.get('ref', 0):.4f}, lrn={rs.get('learned', 0):.4f})")
        if ar["action_aliasing"]:
            for aa in ar["action_aliasing"]:
                print(f"      aliasing: sep_ref={aa['sep_ref']:.4f} sep_lrn={aa['sep_learned']:.4f}")
    if "wall_record_mismatch" in diff:
        wr = diff["wall_record_mismatch"]
        print(f"    Wall-record steps:         {wr['n_steps']:>3d}")


def section(title: str) -> None:
    print(f"\n{'─' * 72}")
    print(f"  {title}")
    print(f"{'─' * 72}")


# ── main ─────────────────────────────────────────────────────────────────────
def run() -> dict:
    print("=" * 72)
    print("  Paper XIII: Compiler IR SOF Report Alignment")
    print("=" * 72)
    print(f"  Regime A: 5 basic blocks [{', '.join(LABELS)}]")
    print("  2 observable families: X_cfg (control flow), X_defuse (data flow)")
    print(f"  Reference (O2-like): {len(CFG_EDGES)} CFG edges, {len(DEFUSE_EDGES)} def-use edges")
    print()

    ref_model = build_reference()
    ref_mats = ref_model.action_matrices()
    ref_obs, _ = build_observables(ref_mats)
    ref_audit = full_audit(block_sectors(), ref_obs)
    print(f"  Reference IR (all blocks reachable, all deps intact):")
    print_matrix("R1_word", ref_audit["R1_word"].astype(int))
    print_matrix("D_word ", ref_audit["D_word"].astype(float))
    print(f"    frozen_R1={ref_audit['frozen_R1']}, frozen_D_word={ref_audit['frozen_D_word']}, "
          f"frozen_D_lie={ref_audit['frozen_D_lie']}")
    print(f"    B3 reachable via B1->B3->B4; data dep B3->B4 present")

    all_results = {}
    RESULTS = Path(__file__).resolve().parent / "archive" / "results"
    ref_sofreport_id = "compiler_ref"

    write_artifact(build_sofreport(
        report_id=ref_sofreport_id,
        system="5-block compiler IR (O2-like)",
        sectorization={"origin": "one-hot basic-block sectors", "blocks": LABELS,
                       "sector_count": N_BLOCKS, "strict_sof_realization": True,
                       "alignment": "BB names, SSA provenance, CFG node correspondence"},
        observable_family={"observables": ["X_cfg (control-flow edges)",
                                           "X_defuse (data-flow def-use chains)"],
                           "generator_type": "skew-symmetrised directed edge matrices"},
        audit=ref_audit,
        claim_note="controlled reference (Regime A)",
        failure_modes=["controlled reference -- no failure mode applied"],
    ), RESULTS / f"{ref_sofreport_id}.sofreport")

    # ── F1: CFG/DefUse Aliasing ──
    section("F1: CFG/DefUse Aliasing -- X_defuse replaced by X_cfg")
    mats = build_f1_cfg_defuse_aliasing()
    res = run_failure_mode("f1_cfg_defuse_aliasing", mats, lrn_label="defuse=cfg (aliased)")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   X_defuse = X_cfg (data-flow structure indistinguishable from CFG)")
    print_diff_summary(res["diff"])
    all_results["f1"] = res
    write_artifact(build_sofreport(
        report_id="compiler_f1_learned", system="5-block IR (cfg/defuse aliasing)",
        sectorization={"origin": "one-hot basic-block sectors", "blocks": LABELS, "sector_count": N_BLOCKS, "strict_sof_realization": True},
        observable_family={"observables": ["X_cfg", "X_defuse = X_cfg (aliased)"]},
        audit=res["learned_audit"], claim_note="constructed failure: cfg/defuse aliasing",
        failure_modes=["X_defuse aliased to X_cfg -- data-flow structure lost"],
    ), RESULTS / "compiler_f1_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="compiler_f1", system="5-block IR cfg/defuse aliasing audit",
        failure_mode="f1_cfg_defuse_aliasing",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="compiler_f1_learned", candidate_label="defuse=cfg",
        diff=res["diff"], normalization={"ordered_pairs": 20, "action_opportunities": 20, "constraint_opportunities": 10},
    ), RESULTS / "compiler_f1.sofaudit")

    # ── F2: Dead Branch Loss ──
    section("F2: Dead Branch Loss -- B3 isolated (simplifycfg over-deletion)")
    mats = build_f2_dead_branch()
    res = run_failure_mode("f2_dead_branch", mats, lrn_label="B3 dead")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   B3 isolated -- CFG edges B1->B3, B3->B4 removed")
    print(f"    Dead branch induces frozen block-pair structure under this SOF audit")
    print_diff_summary(res["diff"])
    all_results["f2"] = res
    write_artifact(build_sofreport(
        report_id="compiler_f2_learned", system="5-block IR (dead branch)",
        sectorization={"origin": "one-hot basic-block sectors", "blocks": LABELS, "sector_count": N_BLOCKS, "strict_sof_realization": True},
        observable_family={"observables": ["X_cfg (B1->B3, B3->B4 removed)", "X_defuse (B3->B4 removed)"]},
        audit=res["learned_audit"], claim_note="constructed failure: dead branch loss",
        failure_modes=["B3 isolated -- dead branch induces frozen block-pair structure"],
    ), RESULTS / "compiler_f2_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="compiler_f2", system="5-block IR dead branch audit",
        failure_mode="f2_dead_branch",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="compiler_f2_learned", candidate_label="B3 dead",
        diff=res["diff"], normalization={"ordered_pairs": 20, "action_opportunities": 20, "constraint_opportunities": 10},
    ), RESULTS / "compiler_f2.sofaudit")

    # ── F3: Spurious CFG Edge ──
    section("F3: Spurious CFG Edge -- hallucinated B0->B4 direct jump")
    mats = build_f3_spurious_cfg_edge()
    res = run_failure_mode("f3_spurious_cfg_edge", mats, lrn_label="+B0->B4 jump")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   X_cfg gains spurious B0->B4 edge (bypasses B1,B2,B3)")
    print_diff_summary(res["diff"])
    all_results["f3"] = res
    write_artifact(build_sofreport(
        report_id="compiler_f3_learned", system="5-block IR (spurious edge)",
        sectorization={"origin": "one-hot basic-block sectors", "blocks": LABELS, "sector_count": N_BLOCKS, "strict_sof_realization": True},
        observable_family={"observables": ["X_cfg (with spurious B0->B4)", "X_defuse"]},
        audit=res["learned_audit"], claim_note="constructed failure: spurious cfg edge",
        failure_modes=["hallucinated B0->B4 direct jump in X_cfg"],
    ), RESULTS / "compiler_f3_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="compiler_f3", system="5-block IR spurious edge audit",
        failure_mode="f3_spurious_cfg_edge",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="compiler_f3_learned", candidate_label="+B0->B4",
        diff=res["diff"], normalization={"ordered_pairs": 20, "action_opportunities": 20, "constraint_opportunities": 10},
    ), RESULTS / "compiler_f3.sofaudit")

    # ── F4: Lost Def-Use ──
    section("F4: Lost Def-Use -- data edge B3->B4 removed, CFG intact")
    mats = build_f4_lost_defuse()
    res = run_failure_mode("f4_lost_defuse", mats, lrn_label="-B3->B4 defuse")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   B3->B4 def-use removed, but CFG edge B3->B4 kept")
    print(f"    Data dependence broken while control flow intact -- control-response")
    print(f"    captures the per-channel loss even when aggregate support is unchanged")
    print_diff_summary(res["diff"])
    all_results["f4"] = res
    write_artifact(build_sofreport(
        report_id="compiler_f4_learned", system="5-block IR (lost def-use)",
        sectorization={"origin": "one-hot basic-block sectors", "blocks": LABELS, "sector_count": N_BLOCKS, "strict_sof_realization": True},
        observable_family={"observables": ["X_cfg (intact)", "X_defuse (B3->B4 removed)"]},
        audit=res["learned_audit"], claim_note="constructed failure: lost def-use dependency",
        failure_modes=["B3->B4 def-use removed, CFG intact -- per-channel diagnostic"],
    ), RESULTS / "compiler_f4_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="compiler_f4", system="5-block IR lost def-use audit",
        failure_mode="f4_lost_defuse",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="compiler_f4_learned", candidate_label="-B3->B4 defuse",
        diff=res["diff"], normalization={"ordered_pairs": 20, "action_opportunities": 20, "constraint_opportunities": 10},
    ), RESULTS / "compiler_f4.sofaudit")

    # ── F5: Pass Pipeline ──
    section("F5: Pass Pipeline Wall -- O0 -> mem2reg -> simplifycfg")
    wall_path = build_f5_pass_pipeline()
    wall_ref = compute_wall_record(wall_path)
    lrn_model = build_f5_learned()
    lrn_mats = lrn_model.action_matrices()
    lrn_base = compute_wall_record([lrn_model])[0]
    wall_lrn = [dict(lrn_base) for _ in wall_path]
    res = run_failure_mode("f5_pass_pipeline", lrn_mats, lrn_label=lrn_model.label(),
                           wall_ref=wall_ref, wall_lrn=wall_lrn)
    pass_names = ["O0", "mem2reg", "simplifycfg"]
    print(f"  Reference pipeline: O0 -> mem2reg -> simplifycfg (3 passes)")
    print(f"  Learned (buggy):    fixed at pre-simplifycfg reference snapshot")
    print(f"  Wall: simplifycfg removes B3 -> frozen counts jump at step 1->2")
    print(f"  {'Pass':<12s} {'cfg_r':>5s} {'cfg_c':>5s} {'def_r':>5s} {'def_c':>5s} "
          f"{'fR1_ref':>8s} {'fR1_lrn':>8s} {'fR1_d':>7s} "
          f"{'fDW_ref':>8s} {'fDW_lrn':>8s} {'fDW_d':>7s}")
    for step in res["diff"].get("wall_record_mismatch", {}).get("steps", []):
        s = step
        pn = pass_names[s["step"]] if s["step"] < 3 else "?"
        mark = " <-- wall" if s["frozen_R1_delta"] != 0 else ""
        print(f"  {pn:<12s} {s['cfg_edges_ref']:>5d} {s['cfg_edges_lrn']:>5d} "
              f"{s['defuse_edges_ref']:>5d} {s['defuse_edges_lrn']:>5d} "
              f"{s['frozen_R1_ref']:>8d} {s['frozen_R1_lrn']:>8d} "
              f"{s['frozen_R1_delta']:>+7d} {s['frozen_D_word_ref']:>8d} "
              f"{s['frozen_D_word_lrn']:>8d} {s['frozen_D_word_delta']:>+7d}{mark}")
    all_results["f5"] = res
    write_artifact(build_sofreport(
        report_id="compiler_f5_learned", system="5-block IR (pass pipeline)",
        sectorization={"origin": "one-hot basic-block sectors", "blocks": LABELS, "sector_count": N_BLOCKS, "strict_sof_realization": True},
        observable_family={"observables": ["X_cfg", "X_defuse"], "deformation": "pass pipeline"},
        audit=res["learned_audit"], claim_note="constructed failure: pass pipeline",
        failure_modes=["buggy pipeline fixed at pre-simplifycfg snapshot; simplifycfg wall not followed"],
    ), RESULTS / "compiler_f5_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="compiler_f5", system="5-block IR pass pipeline audit",
        failure_mode="f5_pass_pipeline",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="compiler_f5_learned", candidate_label=lrn_model.label(),
        diff=res["diff"], normalization={"ordered_pairs": 20, "action_opportunities": 20, "constraint_opportunities": 10, "path_samples": 3},
    ), RESULTS / "compiler_f5.sofaudit")

    # ── summary ──
    section("Diff Protocol Summary -- Compiler IR")
    print(f"  {'Failure':<28s} {'Supp':>5s} {'BrdW':>5s} {'BrdL':>5s} "
          f"{'Dep':>5s} {'FR1':>5s} {'FDW':>5s} {'FDL':>5s} {'CnsV':>5s} {'CtrlR':>5s} {'Wall':>5s}")
    print(f"  {'-' * 28} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5}")
    for key, r in all_results.items():
        d = r["diff"]
        cv = d.get("constraint_violations", {}).get("count", 0)
        ar = d.get("action_response_failure", {}).get("total_large_deltas", 0)
        wr = d.get("wall_record_mismatch", {}).get("n_steps", 0)
        fp = d["frozen_pair_disagreement"]
        dd = d["depth_distortion"]
        print(f"  {r['name']:<28s} "
              f"{d['support_mismatch']['total_mismatch']:>5d} "
              f"{d['bridge_word_mismatch']['total_mismatch']:>5d} "
              f"{d['bridge_lie_mismatch']['total_mismatch']:>5d} "
              f"{dd['total_mismatch']:>5d} "
              f"{fp['frozen_R1']['delta']:>+5d} {fp['frozen_D_word']['delta']:>+5d} "
              f"{fp['frozen_D_lie']['delta']:>+5d} "
              f"{cv:>5d} {ar:>5d} {wr:>5d}")

    print(f"\n  Compiler-native SOF mapping:")
    print(f"    basic blocks / regions  ->  sectors")
    print(f"    CFG edges               ->  support matrix (X_cfg)")
    print(f"    def-use chains           ->  observable family (X_defuse)")
    print(f"    phi nodes               ->  bridge / repair mechanism (def-use + CFG merge)")
    print(f"    optimization passes      ->  deformation path")
    print(f"    dead branch              ->  frozen block-pair structure")
    print(f"    lost def-use dep         ->  per-channel control-response mismatch")
    print(f"    pass pipeline            ->  wall record")
    print(f"\n  Compiler IR is the 4th Regime A domain (after GridWorld, SIR, Traffic).")
    print(f"  First domain with dual observable families (control + data).")
    print("\nDone.")
    return all_results


def main() -> None:
    run()


if __name__ == "__main__":
    main()
