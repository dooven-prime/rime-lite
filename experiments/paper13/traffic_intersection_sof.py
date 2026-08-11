"""Paper XIII: Traffic Intersection SOF Report Alignment -- Regime A control.

2x2 intersection grid, 4 sectors (NW, NE, SW, SE), 2 signal-phase observables.
Phase A = N-S green (southbound directed edges NW->SW, NE->SE).
Phase B = E-W green (westbound directed edges NE->NW, SE->SW).
Reverse directions are captured by the skew-symmetric transpose.

Deformation parameter rho = t_A / t_B (green-time ratio).
Reference: rho = 1.0 (equal green time).

Failure modes:
    F1 phase aliasing       phase_B replaced by phase_A (horizontal response lost)
    F2 missing phase        rho = 0 (Phase A removed, vertical edges frozen)
    F3 forbidden diagonal   hallucinated NW->SE diagonal edge in Phase A
    F4 timing distortion    rho = 0.01 vs ref rho = 1.0 (vertical nearly extinct)
    F5 wall record          rho sweep 0.01->100; learned fixed at rho=2.0

Claim status: controlled protocol validation (Regime A).  Not a traffic
engineering recommendation.

Note on F5: the sampled interval rho in [0.01, 100] does not contain the
limit points rho -> 0 or rho -> infinity, so frozen-count deltas are zero
across all sampled steps under tol = 1e-8.  The wall record is a rate-order
and trajectory-mismatch placeholder, not strong wall-crossing evidence.
The three walls (rho -> 0, rho = 1, rho -> infinity) are identified as
candidate walls on conceptual grounds; only the rate-crossing at rho = 1
is observable as a response-order swap in the control-response channel.
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
N_SECTORS = 4
NW, NE, SW, SE = 0, 1, 2, 3
LABELS = ["NW", "NE", "SW", "SE"]
RHO_REF = 1.0
TOL = 1e-8
FROZEN = 999
MAX_DEPTH = 4

# Directed edges: each phase activates one direction.
# Reverse directions are captured by the skew-symmetric transpose.
# Phase A (N-S green): southbound only  NW->SW, NE->SE
PHASE_A_EDGES = [(NW, SW), (NE, SE)]
# Phase B (E-W green): westbound only  NE->NW, SE->SW
PHASE_B_EDGES = [(NE, NW), (SE, SW)]


# ── Traffic Model ────────────────────────────────────────────────────────────
class TrafficGrid:
    """2x2 intersection grid with two directed signal phases.

    Phase A (N-S green):  southbound  NW->SW, NE->SE
    Phase B (E-W green):  westbound   NE->NW, SE->SW

    rho = t_A / t_B: green-time ratio.  At rho = 1.0, both phases have equal weight.
    """

    def __init__(self, rho: float = RHO_REF):
        self.rho = float(rho)

    def _phase_matrix(self, edges: list[tuple[int, int]], weight: float) -> np.ndarray:
        T = np.eye(N_SECTORS, dtype=float)
        for src, dst in edges:
            T[dst, src] = weight
            T[src, src] = max(0.0, T[src, src] - weight)
        return T

    def action_matrices(self) -> dict[str, np.ndarray]:
        w_a = self.rho / (1.0 + self.rho)
        w_b = 1.0 / (1.0 + self.rho)
        return {
            "phase_A": self._phase_matrix(PHASE_A_EDGES, w_a),
            "phase_B": self._phase_matrix(PHASE_B_EDGES, w_b),
        }

    def label(self) -> str:
        return f"Traffic2x2(rho={self.rho:.3f})"


# ── SOF construction ─────────────────────────────────────────────────────────
def skew(M: np.ndarray) -> np.ndarray:
    return ((M - M.T) / 2.0).astype(complex)


def sector_list() -> list[np.ndarray]:
    eye = np.eye(N_SECTORS, dtype=complex)
    return [eye[:, [j]] for j in range(N_SECTORS)]


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
def build_reference() -> TrafficGrid:
    return TrafficGrid(rho=RHO_REF)


def build_f1_phase_aliasing() -> dict[str, np.ndarray]:
    """Phase B replaced by Phase A -- horizontal response lost, aliasing detected."""
    gw = build_reference()
    mats = gw.action_matrices()
    mats["phase_B"] = mats["phase_A"].copy()
    return mats


def build_f2_missing_phase() -> dict[str, np.ndarray]:
    """rho = 0: Phase A removed, vertical edges frozen."""
    return TrafficGrid(rho=0.0).action_matrices()


def build_f3_forbidden_diagonal() -> dict[str, np.ndarray]:
    """Hallucinated NW->SE diagonal edge in Phase A."""
    gw = build_reference()
    mats = gw.action_matrices()
    T = mats["phase_A"].copy()
    w_a = 1.0 / 3.0
    T[SE, NW] = w_a
    T[NW, NW] = max(0.0, T[NW, NW] - w_a)
    mats["phase_A"] = T
    return mats


def build_f4_timing_distortion() -> dict[str, np.ndarray]:
    """rho = 0.01 vs ref rho = 1.0: Phase A nearly extinct."""
    return TrafficGrid(rho=0.01).action_matrices()


def build_f5_wall_path() -> list[TrafficGrid]:
    """rho sweep: 0.01 -> 100 in log-spaced steps."""
    rhos = np.logspace(-2, 2, 21)
    return [TrafficGrid(rho=float(r)) for r in rhos]


def build_f5_learned() -> TrafficGrid:
    """Learned model at rho = 2.0 (Phase A doubled)."""
    return TrafficGrid(rho=2.0)


# ── wall record ──────────────────────────────────────────────────────────────
def compute_wall_record(models: list[TrafficGrid]) -> list[dict]:
    sectors = sector_list()
    records = []
    for m in models:
        mats = m.action_matrices()
        obs, _ = build_observables(mats)
        audit = full_audit(sectors, obs)
        records.append({
            "rho": m.rho,
            "label": m.label(),
            "frozen_R1": audit["frozen_R1"],
            "frozen_D_word": audit["frozen_D_word"],
            "frozen_D_lie": audit["frozen_D_lie"],
            "R1_offdiag": audit["R1_offdiag"],
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
    for a in ["phase_A", "phase_B"]:
        Tr = raw_ref.get(a, np.zeros((N_SECTORS, N_SECTORS)))
        Tl = raw_lrn.get(a, np.zeros((N_SECTORS, N_SECTORS)))
        for i in range(N_SECTORS):
            for j in range(N_SECTORS):
                if i == j: continue
                if abs(Tr[i, j]) < tol and abs(Tl[i, j]) >= tol:
                    violations.append({"action": a, "from": LABELS[j], "to": LABELS[i],
                                       "learned_value": float(Tl[i, j])})
    return {"violations": violations, "count": len(violations)}


def diff_action_response(resp_ref, resp_lrn, threshold=0.001) -> dict:
    deltas = {}
    for a in ["phase_A", "phase_B"]:
        Rr, Rl = resp_ref[a], resp_lrn[a]
        large = []
        for i in range(N_SECTORS):
            for j in range(N_SECTORS):
                if i == j: continue
                d = abs(Rr[i, j] - Rl[i, j])
                if d > threshold:
                    large.append({"pair": [LABELS[i], LABELS[j]],
                                  "ref": round(Rr[i, j], 6), "learned": round(Rl[i, j], 6),
                                  "delta": round(d, 6)})
        deltas[a] = large
    sep_ref = np.linalg.norm(resp_ref["phase_A"] - resp_ref["phase_B"])
    sep_lrn = np.linalg.norm(resp_lrn["phase_A"] - resp_lrn["phase_B"])
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
            "step": k, "rho": fr["rho"],
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


# ── run single failure mode ──────────────────────────────────────────────────
def run_failure_mode(name: str, lrn_mats: dict[str, np.ndarray],
                     lrn_label: str = "", wall_ref=None, wall_lrn=None) -> dict:
    sectors = sector_list()
    ref_model = build_reference()
    ref_mats = ref_model.action_matrices()
    ref_obs, ref_raw = build_observables(ref_mats)
    ref_audit = full_audit(sectors, ref_obs)
    ref_resp = {a: action_response_matrix(sectors, skew(ref_mats[a])) for a in ["phase_A", "phase_B"]}

    lrn_obs, lrn_raw = build_observables(lrn_mats)
    lrn_audit = full_audit(sectors, lrn_obs)
    lrn_resp = {a: action_response_matrix(sectors, skew(lrn_mats[a])) for a in ["phase_A", "phase_B"]}

    diff = full_diff(ref_audit, lrn_audit, raw_ref=ref_raw, raw_lrn=lrn_raw,
                     resp_ref=ref_resp, resp_lrn=lrn_resp,
                     wall_ref=wall_ref, wall_lrn=wall_lrn)
    return {"name": name, "ref_audit": ref_audit, "learned_audit": lrn_audit,
            "diff": diff, "ref_label": ref_model.label(),
            "learned_label": lrn_label or name}


# ── print helpers ────────────────────────────────────────────────────────────
def print_matrix(label: str, mat: np.ndarray) -> None:
    print(f"    {label}:")
    header = "        " + "  ".join(f"{l:>6s}" for l in LABELS)
    print(header)
    for i, rl in enumerate(LABELS):
        vals = "  ".join(f"{mat[i, j]:>6.3f}" if isinstance(mat[i, j], (np.floating, float))
                         else f"{str(mat[i, j]):>6s}" for j in range(len(LABELS)))
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
            print(f"      {v['action']}: {v['from']}->{v['to']}  (learned={v['learned_value']:.4f})")
    if "action_response_failure" in diff:
        ar = diff["action_response_failure"]
        rs = ar.get("response_sep", {})
        print(f"    Control-response delta > eps: {ar['total_large_deltas']:>3d}  (sep ref={rs.get('ref', 0):.4f}, lrn={rs.get('learned', 0):.4f})")
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
    print("  Paper XIII: Traffic Intersection SOF Report Alignment")
    print("=" * 72)
    print(f"  Regime A: 2x2 intersection grid, 4 sectors [{', '.join(LABELS)}]")
    print("  2 signal phases: Phase A (N-S green, southbound), Phase B (E-W green, westbound)")
    print(f"  Reference: rho = t_A/t_B = {RHO_REF} (equal green time)")
    print()

    ref_model = build_reference()
    ref_mats = ref_model.action_matrices()
    ref_obs, _ = build_observables(ref_mats)
    ref_audit = full_audit(sector_list(), ref_obs)
    print(f"  Reference SOF structure (rho={RHO_REF}):")
    print_matrix("R1_word", ref_audit["R1_word"].astype(int))
    print_matrix("D_word ", ref_audit["D_word"].astype(float))
    print(f"    frozen_R1={ref_audit['frozen_R1']}, frozen_D_word={ref_audit['frozen_D_word']}, "
          f"frozen_D_lie={ref_audit['frozen_D_lie']}")
    print(f"    R2_word_offdiag={ref_audit['R2_word_offdiag']}, R2_lie_offdiag={ref_audit['R2_lie_offdiag']}")
    print(f"    Diagonal pairs (NW<->SE, NE<->SW): no direct edge -> 2-step word bridges")

    all_results = {}
    RESULTS = Path(__file__).resolve().parent / "archive" / "results"
    ref_sofreport_id = "traffic_ref"

    write_artifact(build_sofreport(
        report_id=ref_sofreport_id,
        system="2x2 traffic intersection grid",
        sectorization={"origin": "one-hot intersection sectors", "intersections": LABELS,
                       "sector_count": N_SECTORS, "strict_sof_realization": True},
        observable_family={"phases": ["phase_A (N-S green, southbound)", "phase_B (E-W green, westbound)"],
                           "generator_type": "skew-symmetrised green-time-weighted transition matrices",
                           "deformation_parameter": "rho = t_A / t_B",
                           "note": "reverse directions are captured by the skew-symmetric transpose"},
        audit=ref_audit,
        claim_note="controlled reference (Regime A)",
        failure_modes=["controlled reference -- no failure mode applied"],
    ), RESULTS / f"{ref_sofreport_id}.sofreport")

    # ── F1: Phase Aliasing ──
    section("F1: Phase Aliasing -- Phase B replaced by Phase A")
    mats = build_f1_phase_aliasing()
    res = run_failure_mode("f1_phase_aliasing", mats, lrn_label="B=A (aliased)")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   phase_B = phase_A (horizontal response lost, aliasing detected)")
    print_diff_summary(res["diff"])
    all_results["f1"] = res
    write_artifact(build_sofreport(
        report_id="traffic_f1_learned", system="2x2 traffic (phase aliasing)",
        sectorization={"origin": "one-hot intersection sectors", "intersections": LABELS,
                       "sector_count": N_SECTORS, "strict_sof_realization": True},
        observable_family={"phases": ["phase_A (N-S green)", "phase_B = phase_A (aliased)"]},
        audit=res["learned_audit"],
        claim_note="constructed failure: phase aliasing",
        failure_modes=["phase_B aliased to phase_A -- horizontal response lost"],
    ), RESULTS / "traffic_f1_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="traffic_f1", system="2x2 traffic phase aliasing audit",
        failure_mode="f1_phase_aliasing",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="traffic_f1_learned", candidate_label="B=A aliased",
        diff=res["diff"],
        normalization={"ordered_pairs": 12, "action_opportunities": 24, "constraint_opportunities": 8},
    ), RESULTS / "traffic_f1.sofaudit")

    # ── F2: Missing Phase ──
    section("F2: Missing Phase -- rho = 0 (Phase A removed)")
    mats = build_f2_missing_phase()
    res = run_failure_mode("f2_missing_phase", mats, lrn_label="rho=0 (no N-S)")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   rho = 0 -- vertical edges frozen, grid splits into two isolated columns")
    print_diff_summary(res["diff"])
    all_results["f2"] = res
    write_artifact(build_sofreport(
        report_id="traffic_f2_learned", system="2x2 traffic (missing phase)",
        sectorization={"origin": "one-hot intersection sectors", "intersections": LABELS,
                       "sector_count": N_SECTORS, "strict_sof_realization": True},
        observable_family={"phases": ["phase_A (removed, rho=0)", "phase_B (E-W green)"]},
        audit=res["learned_audit"],
        claim_note="constructed failure: missing phase",
        failure_modes=["Phase A removed -- vertical connectivity lost"],
    ), RESULTS / "traffic_f2_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="traffic_f2", system="2x2 traffic missing phase audit",
        failure_mode="f2_missing_phase",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="traffic_f2_learned", candidate_label="rho=0",
        diff=res["diff"],
        normalization={"ordered_pairs": 12, "action_opportunities": 24, "constraint_opportunities": 8},
    ), RESULTS / "traffic_f2.sofaudit")

    # ── F3: Forbidden Diagonal ──
    section("F3: Forbidden Diagonal -- hallucinated NW->SE edge")
    mats = build_f3_forbidden_diagonal()
    res = run_failure_mode("f3_forbidden_diagonal", mats, lrn_label="+NW->SE diagonal")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   Phase A gains spurious NW->SE diagonal")
    print_diff_summary(res["diff"])
    all_results["f3"] = res
    write_artifact(build_sofreport(
        report_id="traffic_f3_learned", system="2x2 traffic (forbidden diagonal)",
        sectorization={"origin": "one-hot intersection sectors", "intersections": LABELS,
                       "sector_count": N_SECTORS, "strict_sof_realization": True},
        observable_family={"phases": ["phase_A (with spurious NW->SE)", "phase_B (E-W green)"]},
        audit=res["learned_audit"],
        claim_note="constructed failure: forbidden diagonal",
        failure_modes=["hallucinated NW->SE diagonal edge in Phase A"],
    ), RESULTS / "traffic_f3_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="traffic_f3", system="2x2 traffic forbidden diagonal audit",
        failure_mode="f3_forbidden_diagonal",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="traffic_f3_learned", candidate_label="+NW->SE",
        diff=res["diff"],
        normalization={"ordered_pairs": 12, "action_opportunities": 24, "constraint_opportunities": 8},
    ), RESULTS / "traffic_f3.sofaudit")

    # ── F4: Timing Distortion ──
    section("F4: Timing Distortion -- rho = 0.01 vs ref rho = 1.0")
    mats = build_f4_timing_distortion()
    res = run_failure_mode("f4_timing_distortion", mats, lrn_label="rho=0.01")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   rho = 0.01 -- Phase A nearly extinct (1% green time)")
    print(f"    Vertical edges weakened ~100x; binary structure preserved, control-response dominates")
    print_diff_summary(res["diff"])
    all_results["f4"] = res
    write_artifact(build_sofreport(
        report_id="traffic_f4_learned", system="2x2 traffic (timing distortion)",
        sectorization={"origin": "one-hot intersection sectors", "intersections": LABELS,
                       "sector_count": N_SECTORS, "strict_sof_realization": True},
        observable_family={"phases": ["phase_A (rho=0.01, nearly extinct)", "phase_B (E-W green)"]},
        audit=res["learned_audit"],
        claim_note="constructed failure: timing distortion",
        failure_modes=["rho=0.01 -- Phase A green time reduced 100x"],
    ), RESULTS / "traffic_f4_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="traffic_f4", system="2x2 traffic timing distortion audit",
        failure_mode="f4_timing_distortion",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="traffic_f4_learned", candidate_label="rho=0.01",
        diff=res["diff"],
        normalization={"ordered_pairs": 12, "action_opportunities": 24, "constraint_opportunities": 8},
    ), RESULTS / "traffic_f4.sofaudit")

    # ── F5: Wall Record ──
    section("F5: Wall Record -- rho sweep 0.01->100, learned fixed at rho=2.0")
    wall_path = build_f5_wall_path()
    wall_ref = compute_wall_record(wall_path)
    lrn_model = build_f5_learned()
    lrn_mats = lrn_model.action_matrices()
    lrn_base = compute_wall_record([lrn_model])[0]
    wall_lrn = [{**lrn_base, "rho": m.rho} for m in wall_path]
    res = run_failure_mode("f5_wall_record", lrn_mats, lrn_label=lrn_model.label(),
                           wall_ref=wall_ref, wall_lrn=wall_lrn)
    print(f"  Reference: rho swept 0.01 -> 100 (log-spaced, 21 steps)")
    print(f"  Learned:   {lrn_model.label()} (fixed)")
    print(f"  Wall note: sampled interval [0.01, 100] does not include limit points")
    print(f"    rho -> 0 or rho -> infinity, so frozen-count deltas are zero across")
    print(f"    all sampled steps under tol = {TOL}.  The wall record is a rate-order")
    print(f"    and trajectory-mismatch placeholder, not strong wall-crossing evidence.")
    print(f"  Candidate walls (conceptual, not sampled):")
    print(f"    rho -> 0:       topological wall (vertical edges freeze)")
    print(f"    rho = 1.0:      rate-crossing wall (A/B response order swaps)")
    print(f"    rho -> infinity: topological wall (horizontal edges freeze)")
    print(f"  {'rho':>10s} {'fR1_ref':>8s} {'fR1_lrn':>8s} {'fR1_d':>7s} "
          f"{'fDW_ref':>8s} {'fDW_lrn':>8s} {'fDW_d':>7s} "
          f"{'fDL_ref':>8s} {'fDL_lrn':>8s} {'fDL_d':>7s}")
    for step in res["diff"].get("wall_record_mismatch", {}).get("steps", []):
        s = step
        print(f"  {s['rho']:>10.4f} {s['frozen_R1_ref']:>8d} {s['frozen_R1_lrn']:>8d} "
              f"{s['frozen_R1_delta']:>+7d} {s['frozen_D_word_ref']:>8d} "
              f"{s['frozen_D_word_lrn']:>8d} {s['frozen_D_word_delta']:>+7d} "
              f"{s['frozen_D_lie_ref']:>8d} {s['frozen_D_lie_lrn']:>8d} "
              f"{s['frozen_D_lie_delta']:>+7d}")
    all_results["f5"] = res
    write_artifact(build_sofreport(
        report_id="traffic_f5_learned", system="2x2 traffic (wall record)",
        sectorization={"origin": "one-hot intersection sectors", "intersections": LABELS,
                       "sector_count": N_SECTORS, "strict_sof_realization": True},
        observable_family={"phases": ["phase_A (N-S green)", "phase_B (E-W green)"],
                           "deformation_parameter": "rho = t_A / t_B"},
        audit=res["learned_audit"],
        claim_note="constructed failure: wall record (fixed rho=2.0 vs sweep)",
        failure_modes=["learned model fixed at rho=2.0 while reference sweeps rho",
                       "sampled interval [0.01,100] excludes limit points; frozen deltas are all zero",
                       "wall record is a rate-order / trajectory-mismatch placeholder"],
    ), RESULTS / "traffic_f5_learned.sofreport")
    write_artifact(build_sofaudit(
        audit_id="traffic_f5", system="2x2 traffic wall record audit",
        failure_mode="f5_wall_record",
        reference_report_id=ref_sofreport_id, reference_label=res["ref_label"],
        candidate_report_id="traffic_f5_learned", candidate_label=lrn_model.label(),
        diff=res["diff"],
        normalization={"ordered_pairs": 12, "action_opportunities": 24,
                       "constraint_opportunities": 8, "path_samples": 21},
    ), RESULTS / "traffic_f5.sofaudit")

    # ── summary ──
    section("Diff Protocol Summary -- Traffic Intersection")
    print(f"  {'Failure':<26s} {'Supp':>5s} {'BrdW':>5s} {'BrdL':>5s} "
          f"{'Dep':>5s} {'FR1':>5s} {'FDW':>5s} {'FDL':>5s} {'CnsV':>5s} {'CtrlR':>5s} {'Wall':>5s}")
    print(f"  {'-' * 26} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 5}")
    for key, r in all_results.items():
        d = r["diff"]
        cv = d.get("constraint_violations", {}).get("count", 0)
        ar = d.get("action_response_failure", {}).get("total_large_deltas", 0)
        wr = d.get("wall_record_mismatch", {}).get("n_steps", 0)
        fp = d["frozen_pair_disagreement"]
        dd = d["depth_distortion"]
        print(f"  {r['name']:<26s} "
              f"{d['support_mismatch']['total_mismatch']:>5d} "
              f"{d['bridge_word_mismatch']['total_mismatch']:>5d} "
              f"{d['bridge_lie_mismatch']['total_mismatch']:>5d} "
              f"{dd['total_mismatch']:>5d} "
              f"{fp['frozen_R1']['delta']:>+5d} {fp['frozen_D_word']['delta']:>+5d} "
              f"{fp['frozen_D_lie']['delta']:>+5d} "
              f"{cv:>5d} {ar:>5d} {wr:>5d}")

    print(f"\n  Wall record note:")
    print(f"    The sampled interval rho in [0.01, 100] does not contain the limit")
    print(f"    points rho -> 0 or rho -> infinity.  Frozen-count deltas are zero across")
    print(f"    all sampled steps.  The wall record is a rate-order / trajectory-mismatch")
    print(f"    placeholder, not strong wall-crossing evidence.")
    print(f"    Candidate walls: rho -> 0 (topological), rho = 1 (rate-crossing),")
    print(f"    rho -> infinity (topological).  Only the rho = 1 crossing is observable")
    print(f"    in the sampled interval as a response-order swap in the control-response channel.")
    print(f"\n  Traffic is the 3rd Regime A domain (after GridWorld, SIR).")
    print("  Same .sofaudit alignment protocol, 4-sector directed signal-phase observables.")
    print("\nDone.")
    return all_results


def main() -> None:
    run()


if __name__ == "__main__":
    main()
