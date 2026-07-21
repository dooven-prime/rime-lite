"""Paper XIII: SIR compartmental SOF Report Alignment control.

Regime A epidemiology probe: three compartments, two rate observables, five
constructed model variants, and one beta-parameter wall record.

Failure modes:
    F1 rate equalization     beta=gamma, equal magnitudes on distinct supports
    F2 missing edge          β=0, no infection — S isolated
    F3 forbidden direct      hallucinated S→R edge
    F4 rate distortion       β severely misestimated (0.001 vs 0.3)
    F5 wall record           β swept 0→0.5; learned fixed at β=0.2

Claim status:
    - Constructive protocol validation (Regime A).
    - The 3-sector chain is the smallest chain example with a 2-step bridge.
    - Wall at β=0 (topological) and ρ=1 at R₀=1 (rate crossing, smooth).
    - Not an epidemiological theorem.
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
N_COMPARTMENTS = 3
S, I, R = 0, 1, 2  # compartment indices
LABELS = ["S", "I", "R"]
BETA_REF = 0.3
GAMMA_REF = 0.1
TOL = 1e-8
FROZEN = 999
MAX_DEPTH = 4


# ── SIR Model ────────────────────────────────────────────────────────────────
class SIRModel:
    """3-compartment SIR: S → I (rate β), I → R (rate γ)."""

    def __init__(self, beta: float = BETA_REF, gamma: float = GAMMA_REF):
        self.beta = float(beta)
        self.gamma = float(gamma)

    def transition_matrix_beta(self) -> np.ndarray:
        """T_β: S→I with weight β, self-loops elsewhere."""
        T = np.eye(N_COMPARTMENTS, dtype=float)
        T[I, S] = self.beta
        T[S, S] = 1.0 - self.beta
        return T

    def transition_matrix_gamma(self) -> np.ndarray:
        """T_γ: I→R with weight γ, self-loops elsewhere."""
        T = np.eye(N_COMPARTMENTS, dtype=float)
        T[R, I] = self.gamma
        T[I, I] = 1.0 - self.gamma
        return T

    def action_matrices(self) -> dict[str, np.ndarray]:
        return {"beta": self.transition_matrix_beta(),
                "gamma": self.transition_matrix_gamma()}

    def label(self) -> str:
        return f"SIR(β={self.beta:.3f}, γ={self.gamma:.3f}, R₀={self.beta / self.gamma:.2f})"


# ── SOF construction ─────────────────────────────────────────────────────────
def compartment_sectors() -> list[np.ndarray]:
    """3 one-hot compartment sectors in ambient dim=3."""
    eye = np.eye(N_COMPARTMENTS, dtype=complex)
    return [eye[:, [j]] for j in range(N_COMPARTMENTS)]


def skew(M: np.ndarray) -> np.ndarray:
    return ((M - M.T) / 2.0).astype(complex)


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
        1
        for i in range(len(sectors))
        for j in range(len(sectors))
        if i != j and D_word[i, j] == FROZEN
    )

    return {
        "n_sec": len(sectors),
        "n_obs": len(observables),
        "R1_word": R1_word,
        "R1_offdiag": offdiag_count(R1_word),
        "R2_word": R2_word,
        "R2_word_offdiag": offdiag_count(R2_word),
        "R2_lie": R2_lie_agg,
        "R2_lie_offdiag": offdiag_count(R2_lie_agg),
        "D_word": D_word,
        "D_word_max": int(D_word[D_word != FROZEN].max()) if np.any(D_word != FROZEN) else 0,
        "D_lie": D_lie,
        "frozen_D_word": frozen_D_word,
        "frozen_D_lie": frozen["frozen_D"],
        **lie,
        **frozen,
    }


# ── diff protocol (same as GridWorld, imported pattern) ──────────────────────
def _mismatch_pairs(A_ref: np.ndarray, A_lrn: np.ndarray) -> dict:
    n = A_ref.shape[0]
    extra, missing = [], []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if A_ref[i, j] and not A_lrn[i, j]:
                missing.append([i, j])
            elif not A_ref[i, j] and A_lrn[i, j]:
                extra.append([i, j])
    return {"extra": extra, "extra_count": len(extra),
            "missing": missing, "missing_count": len(missing),
            "total_mismatch": len(extra) + len(missing),
            "ref_offdiag": offdiag_count(A_ref),
            "learned_offdiag": offdiag_count(A_lrn)}


def diff_depth(D_ref: np.ndarray, D_lrn: np.ndarray) -> dict:
    n = D_ref.shape[0]
    distortions, ref_frz, lrn_frz = [], [], []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dr, dl = D_ref[i, j], D_lrn[i, j]
            rf, lf = dr == FROZEN, dl == FROZEN
            if rf and not lf:
                ref_frz.append([i, j, int(dl)])
            elif not rf and lf:
                lrn_frz.append([i, j, int(dr)])
            elif not rf and not lf and dr != dl:
                distortions.append([i, j, int(dr), int(dl)])
    return {"depth_distortions": distortions, "distortion_count": len(distortions),
            "ref_frozen_learned_not": ref_frz, "ref_frozen_learned_not_count": len(ref_frz),
            "learned_frozen_ref_not": lrn_frz, "learned_frozen_ref_not_count": len(lrn_frz),
            "total_mismatch": len(distortions) + len(ref_frz) + len(lrn_frz)}


def diff_constraint_violations(raw_ref: dict, raw_lrn: dict, tol: float = TOL) -> dict:
    violations = []
    for a in ["beta", "gamma"]:
        Tr = raw_ref.get(a, np.zeros((N_COMPARTMENTS, N_COMPARTMENTS)))
        Tl = raw_lrn.get(a, np.zeros((N_COMPARTMENTS, N_COMPARTMENTS)))
        for i in range(N_COMPARTMENTS):
            for j in range(N_COMPARTMENTS):
                if i == j:
                    continue
                if abs(Tr[i, j]) < tol and abs(Tl[i, j]) >= tol:
                    violations.append({"action": a, "from": LABELS[j], "to": LABELS[i],
                                       "learned_value": float(Tl[i, j])})
    return {"violations": violations, "count": len(violations)}


def diff_action_response(resp_ref: dict, resp_lrn: dict, threshold: float = 0.001) -> dict:
    deltas = {}
    for a in ["beta", "gamma"]:
        Rr, Rl = resp_ref[a], resp_lrn[a]
        large = []
        for i in range(N_COMPARTMENTS):
            for j in range(N_COMPARTMENTS):
                if i == j:
                    continue
                d = abs(Rr[i, j] - Rl[i, j])
                if d > threshold:
                    large.append({"pair": [LABELS[i], LABELS[j]],
                                  "ref": round(Rr[i, j], 6),
                                  "learned": round(Rl[i, j], 6), "delta": round(d, 6)})
        deltas[a] = large

    # aliasing: check if beta and gamma response matrices are distinguishable
    sep_ref = np.linalg.norm(resp_ref["beta"] - resp_ref["gamma"])
    sep_lrn = np.linalg.norm(resp_lrn["beta"] - resp_lrn["gamma"])
    aliasing = []
    if sep_ref > threshold and sep_lrn < threshold:
        aliasing.append({"sep_ref": round(sep_ref, 6), "sep_learned": round(sep_lrn, 6),
                         "diagnosis": "aliased"})

    return {"per_action_deltas": deltas,
            "total_large_deltas": sum(len(v) for v in deltas.values()),
            "action_aliasing": aliasing,
            "response_sep": {"ref": round(sep_ref, 6), "learned": round(sep_lrn, 6)}}


def full_diff(ref_audit: dict, lrn_audit: dict,
              raw_ref=None, raw_lrn=None, resp_ref=None, resp_lrn=None,
              wall_ref=None, wall_lrn=None) -> dict:
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


def _diff_wall(wall_ref: list[dict], wall_lrn: list[dict]) -> dict:
    steps = []
    for k in range(len(wall_ref)):
        fr, fl = wall_ref[k], wall_lrn[k]
        steps.append({
            "step": k, "beta": fr["beta"],
            "frozen_R1_ref": fr["frozen_R1"], "frozen_R1_lrn": fl["frozen_R1"],
            "frozen_R1_delta": fl["frozen_R1"] - fr["frozen_R1"],
            "frozen_D_word_ref": fr["frozen_D_word"], "frozen_D_word_lrn": fl["frozen_D_word"],
            "frozen_D_word_delta": fl["frozen_D_word"] - fr["frozen_D_word"],
            "frozen_D_lie_ref": fr["frozen_D_lie"], "frozen_D_lie_lrn": fl["frozen_D_lie"],
            "frozen_D_lie_delta": fl["frozen_D_lie"] - fr["frozen_D_lie"],
            "response_sep_ref": fr.get("response_sep", 0),
            "response_sep_lrn": fl.get("response_sep", 0),
            "R0": fr.get("R0", 0),
        })
    return {"steps": steps, "n_steps": len(steps)}


# ── failure-mode constructors ────────────────────────────────────────────────
def build_reference() -> SIRModel:
    return SIRModel(beta=BETA_REF, gamma=GAMMA_REF)


def build_f1_rate_equalization() -> dict[str, np.ndarray]:
    """Set beta=gamma=0.2 while retaining their distinct support channels."""
    return SIRModel(beta=0.2, gamma=0.2).action_matrices()


def build_f2_missing_edge() -> dict[str, np.ndarray]:
    """β=0 — no infection transition. S is isolated (frozen source)."""
    return SIRModel(beta=0.0, gamma=GAMMA_REF).action_matrices()


def build_f3_forbidden_direct() -> dict[str, np.ndarray]:
    """Learned model hallucinates direct S→R edge in the β matrix."""
    model = SIRModel(beta=BETA_REF, gamma=GAMMA_REF)
    mats = model.action_matrices()
    T = mats["beta"].copy()
    T[R, S] = 0.15    # spurious S→R direct
    T[S, S] -= 0.15   # re-normalise
    mats["beta"] = T
    return mats


def build_f4_rate_distortion() -> dict[str, np.ndarray]:
    """β=0.001 (vs ref 0.3) — structure preserved, rate severely wrong."""
    return SIRModel(beta=0.001, gamma=GAMMA_REF).action_matrices()


def build_f5_wall_path() -> list[SIRModel]:
    """β sweep: 0 → 0.5 in 11 steps."""
    return [SIRModel(beta=b, gamma=GAMMA_REF) for b in np.linspace(0, 0.5, 11)]


def build_f5_learned() -> SIRModel:
    """Learned model fixed at β=0.2."""
    return SIRModel(beta=0.2, gamma=GAMMA_REF)


# ── wall record ──────────────────────────────────────────────────────────────
def compute_wall_record(models: list[SIRModel]) -> list[dict]:
    sectors = compartment_sectors()
    records = []
    for m in models:
        mats = m.action_matrices()
        obs, _ = build_observables(mats)
        audit = full_audit(sectors, obs)
        resp = {a: action_response_matrix(sectors, skew(mats[a])) for a in ["beta", "gamma"]}
        records.append({
            "beta": m.beta, "gamma": m.gamma, "R0": m.beta / m.gamma if m.gamma > 0 else float("inf"),
            "frozen_R1": audit["frozen_R1"],
            "frozen_D_word": audit["frozen_D_word"],
            "frozen_D_lie": audit["frozen_D_lie"],
            "R1_offdiag": audit["R1_offdiag"],
            "response_sep": np.linalg.norm(resp["beta"] - resp["gamma"]),
            "bridge_magnitude": float(np.linalg.norm(
                skew(mats["beta"]) @ skew(mats["gamma"]) - skew(mats["gamma"]) @ skew(mats["beta"])
            )),
        })
    return records


# ── SOFRS paired report ─────────────────────────────────────────────────────
def make_sofreport(report_id: str, system: str, label: str, audit: dict) -> dict:
    """Single-system .sofreport (Paper XII format)."""
    return build_sofreport(
        report_id=report_id,
        system=system,
        sectorization={
            "origin": "one-hot compartment sectors",
            "compartments": LABELS,
            "sector_count": N_COMPARTMENTS,
            "strict_sof_realization": True,
        },
        observable_family={
            "rates": ["beta (S->I)", "gamma (I->R)"],
            "generator_type": "skew-symmetrised rate transition matrices",
            "skew_note": "ordered antisymmetric support is a proxy for directed epidemiological transitions",
        },
        audit=audit,
        claim_note="controlled finite SIR-chain evidence (Regime A)",
        failure_modes=[
            "finite three-compartment control, not an epidemiological theorem",
            "skew support does not preserve the original transition direction",
            "rate-wall conclusions are relative to the chosen response constants",
        ],
        extra={"model_label": label, "domain": "epidemiology"},
    )


def make_sofaudit(audit_id: str, system: str, failure_mode: str,
                  ref_label: str, lrn_label: str,
                  ref_sofreport_id: str, lrn_sofreport_id: str,
                  diff: dict, regime: str = "A",
                  wall_note: str = "") -> dict:
    """Paired .sofaudit (Paper XIII format)."""
    result = build_sofaudit(
        audit_id=audit_id,
        system=system,
        failure_mode=failure_mode,
        reference_report_id=ref_sofreport_id,
        reference_label=ref_label,
        candidate_report_id=lrn_sofreport_id,
        candidate_label=lrn_label,
        diff=diff,
        regime=regime,
        normalization={
            "tol": TOL,
            "max_depth": MAX_DEPTH,
            "frozen_sentinel": FROZEN,
            "depth_semantics": "word depth",
            "bridge_semantics": ["word", "Lie commutator"],
            "generator_normalization": "skew(T)=(T-T^T)/2",
        },
        failure_modes=[
            "controlled finite compartmental variant, not an epidemiological theorem",
            "identity sector and observable alignment only",
            "skew support is a proxy for directed transition semantics",
        ],
        extra={"domain": "epidemiology"},
    )
    if wall_note:
        result["wall_note"] = wall_note
    return result


def _audit_summary(audit: dict) -> dict:
    return {"R1_offdiag": audit["R1_offdiag"], "R2_word_offdiag": audit["R2_word_offdiag"],
            "R2_lie_offdiag": audit["R2_lie_offdiag"], "D_word_max": audit["D_word_max"],
            "frozen_R1": audit["frozen_R1"],
            "frozen_D_word": audit["frozen_D_word"],
            "frozen_D_lie": audit["frozen_D_lie"],
            "n_sec": audit["n_sec"]}


def write_sofreport(report: dict, stem: str) -> Path:
    path = Path(__file__).resolve().parent / "results" / f"{stem}.sofreport"
    return write_artifact(report, path)


def write_sofaudit(audit: dict, stem: str) -> Path:
    path = Path(__file__).resolve().parent / "results" / f"{stem}.sofaudit"
    return write_artifact(audit, path)


# ── run single failure mode ──────────────────────────────────────────────────
def run_failure_mode(name: str, lrn_mats: dict[str, np.ndarray],
                     lrn_label: str = "",
                     wall_ref=None, wall_lrn=None) -> dict:
    sectors = compartment_sectors()

    # reference
    ref_model = build_reference()
    ref_mats = ref_model.action_matrices()
    ref_obs, ref_raw = build_observables(ref_mats)
    ref_audit = full_audit(sectors, ref_obs)
    ref_resp = {a: action_response_matrix(sectors, skew(ref_mats[a])) for a in ["beta", "gamma"]}

    # learned
    lrn_obs, lrn_raw = build_observables(lrn_mats)
    lrn_audit = full_audit(sectors, lrn_obs)
    lrn_resp = {a: action_response_matrix(sectors, skew(lrn_mats[a])) for a in ["beta", "gamma"]}

    diff = full_diff(ref_audit, lrn_audit,
                     raw_ref=ref_raw, raw_lrn=lrn_raw,
                     resp_ref=ref_resp, resp_lrn=lrn_resp,
                     wall_ref=wall_ref, wall_lrn=wall_lrn)

    return {"name": name, "ref_audit": ref_audit, "learned_audit": lrn_audit,
            "diff": diff, "ref_label": ref_model.label(),
            "learned_label": lrn_label or name}


# ── print helpers ────────────────────────────────────────────────────────────
def print_diff_summary(diff: dict) -> None:
    sm = diff["support_mismatch"]
    print(f"    Support mismatch:          {sm['total_mismatch']:>3d}  "
          f"(extra={sm['extra_count']}, missing={sm['missing_count']})")
    bw = diff["bridge_word_mismatch"]
    print(f"    Bridge mismatch (word):    {bw['total_mismatch']:>3d}  "
          f"(extra={bw['extra_count']}, missing={bw['missing_count']})")
    bl = diff["bridge_lie_mismatch"]
    print(f"    Bridge mismatch (Lie):     {bl['total_mismatch']:>3d}  "
          f"(extra={bl['extra_count']}, missing={bl['missing_count']})")
    dd = diff["depth_distortion"]
    print(f"    Depth mismatch:            {dd['total_mismatch']:>3d}  "
          f"(ref-frz-not-lrn={dd['ref_frozen_learned_not_count']}, "
          f"lrn-frz-not-ref={dd['learned_frozen_ref_not_count']})")
    fp = diff["frozen_pair_disagreement"]
    print(f"    Frozen R1 δ:               {fp['frozen_R1']['delta']:>+3d}")
    print(f"    Frozen word-D δ:           {fp['frozen_D_word']['delta']:>+3d}")
    print(f"    Frozen Lie-D  δ:           {fp['frozen_D_lie']['delta']:>+3d}")

    if "constraint_violations" in diff:
        cv = diff["constraint_violations"]
        print(f"    Constraint violations:     {cv['count']:>3d}")
        for v in cv["violations"]:
            print(f"      {v['action']}: {v['from']}→{v['to']}  (learned={v['learned_value']:.4f})")

    if "action_response_failure" in diff:
        ar = diff["action_response_failure"]
        rs = ar.get("response_sep", {})
        print(f"    Control-response δ > ε:    {ar['total_large_deltas']:>3d}  "
              f"(sep ref={rs.get('ref', 0):.4f}, lrn={rs.get('learned', 0):.4f})")
        if ar["action_aliasing"]:
            for aa in ar["action_aliasing"]:
                print(f"      aliasing: sep_ref={aa['sep_ref']:.4f} sep_lrn={aa['sep_learned']:.4f}")

    if "wall_record_mismatch" in diff:
        wr = diff["wall_record_mismatch"]
        print(f"    Wall-record steps:         {wr['n_steps']:>3d}")


def print_matrix(label: str, mat: np.ndarray, row_labels: list[str] = LABELS,
                 col_labels: list[str] = LABELS) -> None:
    print(f"    {label}:")
    header = "        " + "  ".join(f"{c:>6s}" for c in col_labels)
    print(header)
    for i, rl in enumerate(row_labels):
        vals = "  ".join(f"{mat[i, j]:>6.3f}" if isinstance(mat[i, j], (np.floating, float))
                         else f"{str(mat[i, j]):>6s}" for j in range(len(col_labels)))
        print(f"      {rl}: [{vals}]")


def section(title: str) -> None:
    print(f"\n{'─' * 72}")
    print(f"  {title}")
    print(f"{'─' * 72}")


# ── main ─────────────────────────────────────────────────────────────────────
def run() -> dict:
    print("=" * 72)
    print("  Paper XIII: SIR Compartmental SOF Report Alignment")
    print("=" * 72)
    print(f"  Regime A: 3 compartments [{', '.join(LABELS)}], 2 rate observables [β, γ]")
    print(f"  Reference: β={BETA_REF}, γ={GAMMA_REF}, R₀={BETA_REF/GAMMA_REF:.1f}")
    print(f"  Bridge: S─β→I─γ→R  (S→R is 2-step word bridge)")
    print()

    # reference baseline
    ref_model = build_reference()
    ref_mats = ref_model.action_matrices()
    ref_obs, _ = build_observables(ref_mats)
    ref_audit = full_audit(compartment_sectors(), ref_obs)
    print(f"  Reference SOF structure:")
    print_matrix("R1_word", ref_audit["R1_word"].astype(int))
    print_matrix("R2_word", ref_audit["R2_word"].astype(int))
    print_matrix("D_word ", ref_audit["D_word"].astype(int))
    print(f"    frozen_R1={ref_audit['frozen_R1']}, "
          f"frozen_D_word={ref_audit['frozen_D_word']}, "
          f"frozen_D_lie={ref_audit['frozen_D_lie']}")
    print(f"    R2_lie_offdiag={ref_audit['R2_lie_offdiag']}")

    all_results = {}

    # ── F1: Rate Equalization ──
    section("F1: Rate Equalization — β=γ on distinct support channels")
    mats = build_f1_rate_equalization()
    res = run_failure_mode("f1_rate_equalization", mats,
                           lrn_label="SIR(β=0.2, γ=0.2, R₀=1.0)")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   {res['learned_label']}")
    sep = res["diff"]["action_response_failure"]["response_sep"]
    print(f"    response-matrix separation: ref={sep['ref']:.4f} -> "
          f"learned={sep['learned']:.4f} (not aliased because supports differ)")
    print_diff_summary(res["diff"])
    all_results["f1"] = res
    write_sofreport(make_sofreport("sir_ref", "SIR reference", res["ref_label"], res["ref_audit"]), "sir_ref")
    write_sofreport(make_sofreport("sir_f1_learned", "SIR (rate equalization)", res["learned_label"], res["learned_audit"]), "sir_f1_learned")
    write_sofaudit(make_sofaudit("sir_f1", "SIR rate equalization audit", "f1_rate_equalization",
                                 res["ref_label"], res["learned_label"],
                                 "sir_ref", "sir_f1_learned", res["diff"]), "sir_f1")

    # ── F2: Missing Edge ──
    section("F2: Missing Edge — β=0, no infection")
    mats = build_f2_missing_edge()
    res = run_failure_mode("f2_missing_edge", mats,
                           lrn_label="SIR(β=0.0, γ=0.1, R₀=0.0)")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   {res['learned_label']}")
    print(f"    S is isolated — no outgoing transitions ({LABELS[S]} is a frozen source)")
    print_diff_summary(res["diff"])
    all_results["f2"] = res
    write_sofreport(make_sofreport("sir_f2_learned", "SIR (missing edge)", res["learned_label"], res["learned_audit"]), "sir_f2_learned")
    write_sofaudit(make_sofaudit("sir_f2", "SIR missing edge audit", "f2_missing_edge",
                                 res["ref_label"], res["learned_label"],
                                 "sir_ref", "sir_f2_learned", res["diff"]), "sir_f2")

    # ── F3: Forbidden Direct ──
    section("F3: Forbidden Direct — hallucinated S→R edge")
    mats = build_f3_forbidden_direct()
    res = run_failure_mode("f3_forbidden_direct", mats,
                           lrn_label="SIR + spurious S→R")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   S→R direct hallucinated in β matrix")
    print_diff_summary(res["diff"])
    all_results["f3"] = res
    write_sofreport(make_sofreport("sir_f3_learned", "SIR (forbidden direct)", res["learned_label"], res["learned_audit"]), "sir_f3_learned")
    write_sofaudit(make_sofaudit("sir_f3", "SIR forbidden direct audit", "f3_forbidden_direct",
                                 res["ref_label"], res["learned_label"],
                                 "sir_ref", "sir_f3_learned", res["diff"]), "sir_f3")

    # ── F4: Rate Distortion ──
    section("F4: Rate Distortion — β=0.001 vs ref β=0.3")
    mats = build_f4_rate_distortion()
    res = run_failure_mode("f4_rate_distortion", mats,
                           lrn_label="SIR(β=0.001, γ=0.1, R₀=0.01)")
    print(f"  Reference: {res['ref_label']}")
    print(f"  Learned:   {res['learned_label']}")
    print(f"    Structure preserved, but S→I response is 300× weaker")
    print(f"    Demonstrates: binary support unchanged, control-response dominates")
    print_diff_summary(res["diff"])
    all_results["f4"] = res
    write_sofreport(make_sofreport("sir_f4_learned", "SIR (rate distortion)", res["learned_label"], res["learned_audit"]), "sir_f4_learned")
    write_sofaudit(make_sofaudit("sir_f4", "SIR rate distortion audit", "f4_rate_distortion",
                                 res["ref_label"], res["learned_label"],
                                 "sir_ref", "sir_f4_learned", res["diff"]), "sir_f4")

    # ── F5: Wall Record ──
    section("F5: Wall Record — β sweep 0→0.5, learned fixed at β=0.2")
    wall_path = build_f5_wall_path()
    wall_ref = compute_wall_record(wall_path)
    lrn_model = build_f5_learned()
    lrn_mats = lrn_model.action_matrices()

    # compute wall record for learned (fixed, but repeated for comparison)
    wall_lrn_base = compute_wall_record([lrn_model])[0]
    wall_lrn = [{**wall_lrn_base, "beta": m.beta, "R0": m.beta / m.gamma}
                for m in wall_path]

    res = run_failure_mode("f5_wall_record", lrn_mats,
                           lrn_label=lrn_model.label(),
                           wall_ref=wall_ref, wall_lrn=wall_lrn)

    print(f"  Reference: β swept 0 → 0.5, γ={GAMMA_REF} fixed")
    print(f"  Learned:   {lrn_model.label()} (fixed)")
    print(f"  Wall at β=0: topological (S isolation, frozen_R1 jumps 2→4)")
    print(f"  Crossing at R₀=1: smooth rate crossing (no structural change)")
    print(f"  {'β':>8s} {'R₀':>6s} {'fR1_δ':>7s} {'fWD_δ':>7s} {'fLD_δ':>7s} "
          f"{'sep_ref':>8s} {'sep_lrn':>8s}")
    for step in res["diff"].get("wall_record_mismatch", {}).get("steps", []):
        s = step
        print(f"  {s['beta']:>8.3f} {s['R0']:>6.2f} {s['frozen_R1_delta']:>+7d} "
              f"{s['frozen_D_word_delta']:>+7d} {s['frozen_D_lie_delta']:>+7d} "
              f"{s['response_sep_ref']:>8.4f} {s['response_sep_lrn']:>8.4f}")

    all_results["f5"] = res
    write_sofreport(make_sofreport("sir_f5_learned", "SIR (wall record)", res["learned_label"], res["learned_audit"]), "sir_f5_learned")
    write_sofaudit(make_sofaudit("sir_f5", "SIR wall record audit", "f5_wall_record",
                                 res["ref_label"], res["learned_label"],
                                 "sir_ref", "sir_f5_learned", res["diff"],
                                  wall_note="beta=0: topological wall. R0=1: response-order crossing (smooth)."), "sir_f5")

    # ── summary ──
    section("Diff Protocol Summary — SIR Compartmental Model")
    print(f"  {'Failure':<26s} {'Suppδ':>6s} {'BrdWδ':>6s} {'BrdLδ':>6s} "
          f"{'Depδ':>6s} {'FR1δ':>6s} {'FWDδ':>6s} {'FLDδ':>6s} "
          f"{'CnsV':>5s} {'CtrlR':>5s} {'Wall':>5s}")
    print(f"  {'-' * 26} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} "
          f"{'-' * 6} {'-' * 6} {'-' * 5} {'-' * 5} {'-' * 5}")
    for key, r in all_results.items():
        d = r["diff"]
        cv = d.get("constraint_violations", {}).get("count", 0)
        ar = d.get("action_response_failure", {}).get("total_large_deltas", 0)
        wr = d.get("wall_record_mismatch", {}).get("n_steps", 0)
        print(f"  {r['name']:<26s} "
              f"{d['support_mismatch']['total_mismatch']:>6d} "
              f"{d['bridge_word_mismatch']['total_mismatch']:>6d} "
              f"{d['bridge_lie_mismatch']['total_mismatch']:>6d} "
              f"{d['depth_distortion']['total_mismatch']:>6d} "
              f"{d['frozen_pair_disagreement']['frozen_R1']['delta']:>+6d} "
              f"{d['frozen_pair_disagreement']['frozen_D_word']['delta']:>+6d} "
              f"{d['frozen_pair_disagreement']['frozen_D_lie']['delta']:>+6d} "
              f"{cv:>5d} {ar:>5d} {wr:>5d}")

    print(f"\n  Two walls identified in the SIR parameter space:")
    print(f"    β=0:     topological wall — S loses all outgoing edges (frozen_R1 jumps 2→4)")
    print(f"    R₀=1:    rate crossing wall — ρ=‖X_β‖/‖X_γ‖ crosses 1 (smooth, no topology change)")
    print(f"    SOF re-expresses the classical threshold as a response-order crossing.")
    print(f"\n  The 3-sector SIR chain is the smallest chain example with a 2-step bridge.")
    print(f"  Same diff protocol as GridWorld, adapted to rate-parameterized observables.")
    print("\nDone.")
    return all_results


def main() -> None:
    run()


if __name__ == "__main__":
    main()
