"""Paper XIII Appendix: Network Routing SOF Report Alignment -- Regime A control.

4 prefix sectors (P0=local, P1=dmz, P2=internal, P3=external), 2 routing
observable families:
  X_internal -- routes within the trusted zone (P0, P1, P2)
  X_external -- routes via the external gateway (involving P3)

The ACL (access control list) acts as a constraint that removes edges from
X_external.  A blocked prefix induces frozen prefix-pair structure.

Distinction from Compiler IR (dual observable-family):
  Compiler: X_cfg + X_defuse, both additive (edges add connectivity)
  Network:  X_internal + X_external, ACL selectively REMOVES edges from
            X_external (constraint observable, not connectivity observable)

Failure modes:
  F1 route aliasing      X_external = X_internal (zones indistinguishable)
  F2 blocked prefix      ACL blocks P3->P2 (external can't reach internal)
  F3 forbidden route     hallucinated P0->P3 direct (no gateway)
  F4 metric distortion   external routes weakened (higher cost/latency)
  F5 ACL policy wall      ACL rules added: none -> block P1->P2 -> block P3->P2

Claim status: controlled protocol validation (Regime A).  Appendix domain.
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
N_PREFIXES = 4
P0, P1, P2, P3 = 0, 1, 2, 3
LABELS = ["P0(local)", "P1(dmz)", "P2(internal)", "P3(external)"]
WEIGHT = 1.0
TOL = 1e-8
FROZEN = 999
MAX_DEPTH = 4

# Internal routes: directed mesh within trusted zone (reverse via skew transpose)
INTERNAL_EDGES = [(P0, P1), (P1, P2), (P2, P0)]
# External routes: directed via P3 gateway (reverse via skew transpose)
EXTERNAL_EDGES = [(P0, P3), (P1, P3), (P3, P2)]


# ── Network Routing Model ────────────────────────────────────────────────────
class RoutingModel:
    """4-prefix network with internal and external routing zones.

    X_internal: trusted-zone mesh (P0<->P1<->P2<->P0)
    X_external: gateway routes involving P3

    ACL constraints remove edges from X_external (selective blocking).
    """

    def __init__(self, internal_edges: list[tuple[int, int]] | None = None,
                 external_edges: list[tuple[int, int]] | None = None,
                 weight: float = WEIGHT):
        self.internal = list(internal_edges) if internal_edges is not None else list(INTERNAL_EDGES)
        self.external = list(external_edges) if external_edges is not None else list(EXTERNAL_EDGES)
        self.weight = float(weight)

    def _edge_matrix(self, edges: list[tuple[int, int]], w: float) -> np.ndarray:
        T = np.eye(N_PREFIXES, dtype=float)
        for src, dst in edges:
            T[dst, src] = w
            T[src, src] = max(0.0, T[src, src] - w)
        return T

    def action_matrices(self) -> dict[str, np.ndarray]:
        return {
            "X_internal": self._edge_matrix(self.internal, self.weight),
            "X_external": self._edge_matrix(self.external, self.weight),
        }

    def label(self) -> str:
        return f"Route(in={len(self.internal)}e, ex={len(self.external)}e)"


# ── SOF construction ─────────────────────────────────────────────────────────
def skew(M: np.ndarray) -> np.ndarray:
    return ((M - M.T) / 2.0).astype(complex)


def prefix_sectors() -> list[np.ndarray]:
    eye = np.eye(N_PREFIXES, dtype=complex)
    return [eye[:, [j]] for j in range(N_PREFIXES)]


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
        "frozen_D_word": frozen_D_word,
        "frozen_D_lie": frozen["frozen_D"],
        **lie, **frozen,
    }


# ── failure-mode constructors ────────────────────────────────────────────────
def build_reference() -> RoutingModel:
    """Full connectivity: all internal + external edges active, no ACL blocks."""
    return RoutingModel()


def build_f1_route_aliasing() -> dict[str, np.ndarray]:
    """X_external = X_internal -- zones indistinguishable."""
    ref = build_reference()
    mats = ref.action_matrices()
    mats["X_external"] = mats["X_internal"].copy()
    return mats


def build_f2_blocked_prefix() -> dict[str, np.ndarray]:
    """ACL blocks P3->P2: external cannot reach internal.
    Removes edge (P3, P2) from external routes."""
    return RoutingModel(
        external_edges=[(P0, P3), (P1, P3)],
    ).action_matrices()


def build_f3_forbidden_route() -> dict[str, np.ndarray]:
    """Hallucinated P0->P3 direct in internal routes (no gateway needed)."""
    ref = build_reference()
    mats = ref.action_matrices()
    T = mats["X_internal"].copy()
    w = 1.0 / 7.0
    T[P3, P0] = w
    T[P0, P0] = max(0.0, T[P0, P0] - w)
    mats["X_internal"] = T
    return mats


def build_f4_metric_distortion() -> dict[str, np.ndarray]:
    """Asymmetric distortion: external routes weakened, internal routes normal."""
    model = RoutingModel()
    mats = model.action_matrices()
    T = np.eye(N_PREFIXES, dtype=float)
    for src, dst in EXTERNAL_EDGES:
        T[dst, src] = 0.1
        T[src, src] = max(0.0, T[src, src] - 0.1)
    mats["X_external"] = T
    return mats


def build_f5_acl_policy_path() -> list[RoutingModel]:
    """ACL policy changes: open -> block P1->P3 -> block P3->P2."""
    return [
        RoutingModel(external_edges=[(P0, P3), (P1, P3), (P3, P2)]),  # open
        RoutingModel(external_edges=[(P0, P3), (P1, P3), (P3, P2)]),  # open
        RoutingModel(external_edges=[(P0, P3), (P3, P2)]),             # block P1->P3
        RoutingModel(external_edges=[(P0, P3)]),                       # block P3->P2 too
    ]


def build_f5_learned() -> RoutingModel:
    """Stale ACL: rule blocking P1->P3 not yet applied."""
    return RoutingModel(
        external_edges=[(P0, P3), (P1, P3), (P3, P2)],
    )


# ── wall record ──────────────────────────────────────────────────────────────
def compute_wall_record(models: list[RoutingModel]) -> list[dict]:
    sectors = prefix_sectors()
    records = []
    for i, m in enumerate(models):
        mats = m.action_matrices()
        obs, _ = build_observables(mats)
        audit = full_audit(sectors, obs)
        records.append({
            "step": i, "ext_edges": len(m.external),
            "label": m.label(),
            "frozen_R1": audit["frozen_R1"],
            "frozen_D_word": audit["frozen_D_word"],
            "frozen_D_lie": audit["frozen_D_lie"],
        })
    return records


# ── diff protocol (shared pattern) ───────────────────────────────────────────
def _mismatch_pairs(A_ref, A_lrn):
    n = A_ref.shape[0]; extra, missing = [], []
    for i in range(n):
        for j in range(n):
            if i == j: continue
            if A_ref[i, j] and not A_lrn[i, j]: missing.append([i, j])
            elif not A_ref[i, j] and A_lrn[i, j]: extra.append([i, j])
    return {"extra": extra, "extra_count": len(extra), "missing": missing,
            "missing_count": len(missing), "total_mismatch": len(extra) + len(missing),
            "ref_offdiag": offdiag_count(A_ref), "learned_offdiag": offdiag_count(A_lrn)}

def diff_depth(D_ref, D_lrn):
    n = D_ref.shape[0]; distortions, ref_frz, lrn_frz = [], [], []
    for i in range(n):
        for j in range(n):
            if i == j: continue
            dr, dl = D_ref[i, j], D_lrn[i, j]; rf, lf = dr == FROZEN, dl == FROZEN
            if rf and not lf: ref_frz.append([i, j, int(dl)])
            elif not rf and lf: lrn_frz.append([i, j, int(dr)])
            elif not rf and not lf and dr != dl: distortions.append([i, j, int(dr), int(dl)])
    return {"total_mismatch": len(distortions) + len(ref_frz) + len(lrn_frz),
            "depth_distortions": distortions, "distortion_count": len(distortions),
            "ref_frozen_learned_not": ref_frz, "ref_frozen_learned_not_count": len(ref_frz),
            "learned_frozen_ref_not": lrn_frz, "learned_frozen_ref_not_count": len(lrn_frz)}

def diff_constraint_violations(raw_ref, raw_lrn, tol=TOL):
    violations = []
    for a in ["X_internal", "X_external"]:
        Tr = raw_ref.get(a, np.zeros((N_PREFIXES, N_PREFIXES)))
        Tl = raw_lrn.get(a, np.zeros((N_PREFIXES, N_PREFIXES)))
        for i in range(N_PREFIXES):
            for j in range(N_PREFIXES):
                if i == j: continue
                if abs(Tr[i, j]) < tol and abs(Tl[i, j]) >= tol:
                    violations.append({"action": a, "from": LABELS[j], "to": LABELS[i], "learned_value": float(Tl[i, j])})
    return {"violations": violations, "count": len(violations)}

def diff_action_response(resp_ref, resp_lrn, threshold=0.001):
    deltas = {}
    for a in ["X_internal", "X_external"]:
        Rr, Rl = resp_ref[a], resp_lrn[a]; large = []
        for i in range(N_PREFIXES):
            for j in range(N_PREFIXES):
                if i == j: continue
                d = abs(Rr[i, j] - Rl[i, j])
                if d > threshold: large.append({"pair": [LABELS[i], LABELS[j]], "ref": round(Rr[i, j], 6), "learned": round(Rl[i, j], 6), "delta": round(d, 6)})
        deltas[a] = large
    sep_ref = np.linalg.norm(resp_ref["X_internal"] - resp_ref["X_external"])
    sep_lrn = np.linalg.norm(resp_lrn["X_internal"] - resp_lrn["X_external"])
    aliasing = [{"sep_ref": round(sep_ref, 6), "sep_learned": round(sep_lrn, 6), "diagnosis": "aliased"}] if sep_ref > threshold and sep_lrn < threshold else []
    return {"per_action_deltas": deltas, "total_large_deltas": sum(len(v) for v in deltas.values()), "action_aliasing": aliasing, "response_sep": {"ref": round(sep_ref, 6), "learned": round(sep_lrn, 6)}}

def _diff_wall(wall_ref, wall_lrn):
    steps = []
    for k in range(len(wall_ref)):
        fr, fl = wall_ref[k], wall_lrn[k]
        steps.append({"step": k, "ext_edges": fr["ext_edges"],
            "frozen_R1_ref": fr["frozen_R1"], "frozen_R1_lrn": fl["frozen_R1"], "frozen_R1_delta": fl["frozen_R1"] - fr["frozen_R1"],
            "frozen_D_word_ref": fr["frozen_D_word"], "frozen_D_word_lrn": fl["frozen_D_word"], "frozen_D_word_delta": fl["frozen_D_word"] - fr["frozen_D_word"],
            "frozen_D_lie_ref": fr["frozen_D_lie"], "frozen_D_lie_lrn": fl["frozen_D_lie"], "frozen_D_lie_delta": fl["frozen_D_lie"] - fr["frozen_D_lie"]})
    return {"steps": steps, "n_steps": len(steps)}

def full_diff(ref_audit, lrn_audit, raw_ref=None, raw_lrn=None, resp_ref=None, resp_lrn=None, wall_ref=None, wall_lrn=None):
    result = {
        "support_mismatch": _mismatch_pairs(ref_audit["R1_word"], lrn_audit["R1_word"]),
        "bridge_word_mismatch": _mismatch_pairs(ref_audit["R2_word"], lrn_audit["R2_word"]),
        "bridge_lie_mismatch": _mismatch_pairs(ref_audit["R2_lie"], lrn_audit["R2_lie"]),
        "depth_distortion": diff_depth(ref_audit["D_word"], lrn_audit["D_word"]),
        "frozen_pair_disagreement": {
            "frozen_R1": {"ref": ref_audit["frozen_R1"], "learned": lrn_audit["frozen_R1"], "delta": lrn_audit["frozen_R1"] - ref_audit["frozen_R1"]},
            "frozen_D_word": {"ref": ref_audit["frozen_D_word"], "learned": lrn_audit["frozen_D_word"], "delta": lrn_audit["frozen_D_word"] - ref_audit["frozen_D_word"]},
            "frozen_D_lie": {"ref": ref_audit["frozen_D_lie"], "learned": lrn_audit["frozen_D_lie"], "delta": lrn_audit["frozen_D_lie"] - ref_audit["frozen_D_lie"]},
        },
    }
    if raw_ref is not None: result["constraint_violations"] = diff_constraint_violations(raw_ref, raw_lrn)
    if resp_ref is not None: result["action_response_failure"] = diff_action_response(resp_ref, resp_lrn)
    if wall_ref is not None: result["wall_record_mismatch"] = _diff_wall(wall_ref, wall_lrn)
    return result

def run_failure_mode(name, lrn_mats, lrn_label="", wall_ref=None, wall_lrn=None):
    sectors = prefix_sectors()
    ref_model = build_reference(); ref_mats = ref_model.action_matrices()
    ref_obs, ref_raw = build_observables(ref_mats); ref_audit = full_audit(sectors, ref_obs)
    ref_resp = {a: action_response_matrix(sectors, skew(ref_mats[a])) for a in ["X_internal", "X_external"]}
    lrn_obs, lrn_raw = build_observables(lrn_mats); lrn_audit = full_audit(sectors, lrn_obs)
    lrn_resp = {a: action_response_matrix(sectors, skew(lrn_mats[a])) for a in ["X_internal", "X_external"]}
    diff = full_diff(ref_audit, lrn_audit, raw_ref=ref_raw, raw_lrn=lrn_raw, resp_ref=ref_resp, resp_lrn=lrn_resp, wall_ref=wall_ref, wall_lrn=wall_lrn)
    return {"name": name, "ref_audit": ref_audit, "learned_audit": lrn_audit, "diff": diff, "ref_label": ref_model.label(), "learned_label": lrn_label or name}

# ── print ────────────────────────────────────────────────────────────────────
def print_diff_summary(diff):
    sm = diff["support_mismatch"]; bw = diff["bridge_word_mismatch"]; bl = diff["bridge_lie_mismatch"]; dd = diff["depth_distortion"]; fp = diff["frozen_pair_disagreement"]
    print(f"    Support mismatch:          {sm['total_mismatch']:>3d}  (extra={sm['extra_count']}, missing={sm['missing_count']})")
    print(f"    Bridge mismatch (word):    {bw['total_mismatch']:>3d}  (extra={bw['extra_count']}, missing={bw['missing_count']})")
    print(f"    Bridge mismatch (Lie):     {bl['total_mismatch']:>3d}  (extra={bl['extra_count']}, missing={bl['missing_count']})")
    print(f"    Depth distortion:          {dd['total_mismatch']:>3d}  (pure={dd['distortion_count']}, frz={dd['ref_frozen_learned_not_count']}+{dd['learned_frozen_ref_not_count']})")
    print(f"    Frozen R1/D_word/D_lie:    {fp['frozen_R1']['delta']:>+3d} / {fp['frozen_D_word']['delta']:>+3d} / {fp['frozen_D_lie']['delta']:>+3d}")
    if "constraint_violations" in diff:
        cv = diff["constraint_violations"]
        print(f"    Constraint violations:     {cv['count']:>3d}")
        for v in cv["violations"]: print(f"      {v['action']}: {v['from']} -> {v['to']}  ({v['learned_value']:.4f})")
    if "action_response_failure" in diff:
        ar = diff["action_response_failure"]; rs = ar.get("response_sep", {})
        print(f"    Control-response delta>eps: {ar['total_large_deltas']:>3d}  (int/ext sep ref={rs.get('ref', 0):.4f}, lrn={rs.get('learned', 0):.4f})")
        for aa in ar["action_aliasing"]: print(f"      aliasing: sep_ref={aa['sep_ref']:.4f} sep_lrn={aa['sep_learned']:.4f}")
    if "wall_record_mismatch" in diff: print(f"    Wall-record steps:         {diff['wall_record_mismatch']['n_steps']:>3d}")

def section(title): print(f"\n{'─' * 72}\n  {title}\n{'─' * 72}")

# ── main ─────────────────────────────────────────────────────────────────────
def run():
    print("=" * 72)
    print("  Paper XIII Appendix: Network Routing SOF Report Alignment")
    print("=" * 72)
    print(f"  Regime A: 4 prefixes [{', '.join(LABELS)}]")
    print("  2 routing zones: X_internal (trusted mesh), X_external (gateway)")
    print(f"  ACL constraints selectively remove edges from X_external")
    print()

    ref_model = build_reference()
    ref_obs, _ = build_observables(ref_model.action_matrices())
    ref_audit = full_audit(prefix_sectors(), ref_obs)
    print(f"  Reference (full connectivity, no ACL blocks):")
    print(f"    internal edges: {len(INTERNAL_EDGES)} (P0<->P1<->P2 mesh)")
    print(f"    external edges: {len(EXTERNAL_EDGES)} (P3 gateway to all)")
    print(f"    frozen_R1={ref_audit['frozen_R1']}, frozen_D_word={ref_audit['frozen_D_word']}")

    all_results = {}
    RESULTS = Path(__file__).resolve().parent / "results"
    ref_id = "network_ref"

    write_artifact(build_sofreport(
        report_id=ref_id, system="4-prefix network routing",
        sectorization={"origin": "one-hot prefix sectors", "prefixes": LABELS, "sector_count": N_PREFIXES, "strict_sof_realization": True},
        observable_family={"observables": ["X_internal (trusted-zone mesh)", "X_external (gateway routes)"], "constraint": "ACL selectively removes X_external edges", "generator_type": "skew-symmetrised routing matrices"},
        audit=ref_audit, claim_note="controlled reference (Regime A, appendix)",
        failure_modes=["controlled reference"],
    ), RESULTS / f"{ref_id}.sofreport")

    # F1
    section("F1: Route Aliasing -- X_external = X_internal")
    mats = build_f1_route_aliasing()
    res = run_failure_mode("f1_route_aliasing", mats, "ext=int (aliased)")
    print(f"  Reference: {res['ref_label']}\n  Learned:   X_external = X_internal (zones indistinguishable)")
    print_diff_summary(res["diff"]); all_results["f1"] = res
    write_artifact(build_sofreport(report_id="network_f1_learned", system="4-prefix (route aliasing)",
        sectorization={"origin": "one-hot prefix sectors", "prefixes": LABELS, "sector_count": N_PREFIXES, "strict_sof_realization": True},
        observable_family={"observables": ["X_internal", "X_external = X_internal (aliased)"]},
        audit=res["learned_audit"], claim_note="constructed failure: route aliasing",
        failure_modes=["X_external aliased to X_internal"]), RESULTS / "network_f1_learned.sofreport")
    write_artifact(build_sofaudit(audit_id="network_f1", system="4-prefix route aliasing audit", failure_mode="f1_route_aliasing",
        reference_report_id=ref_id, reference_label=res["ref_label"], candidate_report_id="network_f1_learned", candidate_label="ext=int",
        diff=res["diff"], normalization={"ordered_pairs": 12, "action_opportunities": 16, "constraint_opportunities": 8}),
    RESULTS / "network_f1.sofaudit")

    # F2
    section("F2: Blocked Prefix -- ACL blocks P3<->P2")
    mats = build_f2_blocked_prefix()
    res = run_failure_mode("f2_blocked_prefix", mats, "P3->P2 blocked")
    print(f"  Reference: {res['ref_label']}\n  Learned:   ACL removes P3<->P2 from external routes")
    print(f"    Blocked prefix induces frozen prefix-pair structure")
    print_diff_summary(res["diff"]); all_results["f2"] = res
    write_artifact(build_sofreport(report_id="network_f2_learned", system="4-prefix (blocked prefix)",
        sectorization={"origin": "one-hot prefix sectors", "prefixes": LABELS, "sector_count": N_PREFIXES, "strict_sof_realization": True},
        observable_family={"observables": ["X_internal", "X_external (P3<->P2 blocked)"]},
        audit=res["learned_audit"], claim_note="constructed failure: ACL block",
        failure_modes=["ACL blocks P3<->P2"]), RESULTS / "network_f2_learned.sofreport")
    write_artifact(build_sofaudit(audit_id="network_f2", system="4-prefix blocked prefix audit", failure_mode="f2_blocked_prefix",
        reference_report_id=ref_id, reference_label=res["ref_label"], candidate_report_id="network_f2_learned", candidate_label="P3->P2 blocked",
        diff=res["diff"], normalization={"ordered_pairs": 12, "action_opportunities": 16, "constraint_opportunities": 8}),
    RESULTS / "network_f2.sofaudit")

    # F3
    section("F3: Forbidden Route -- hallucinated P0->P3 in internal zone")
    mats = build_f3_forbidden_route()
    res = run_failure_mode("f3_forbidden_route", mats, "+P0->P3 internal")
    print(f"  Reference: {res['ref_label']}\n  Learned:   X_internal gains spurious P0->P3 (bypasses gateway)")
    print_diff_summary(res["diff"]); all_results["f3"] = res
    write_artifact(build_sofreport(report_id="network_f3_learned", system="4-prefix (forbidden route)",
        sectorization={"origin": "one-hot prefix sectors", "prefixes": LABELS, "sector_count": N_PREFIXES, "strict_sof_realization": True},
        observable_family={"observables": ["X_internal (with spurious P0->P3)", "X_external"]},
        audit=res["learned_audit"], claim_note="constructed failure: forbidden route",
        failure_modes=["hallucinated P0->P3 in internal zone"]), RESULTS / "network_f3_learned.sofreport")
    write_artifact(build_sofaudit(audit_id="network_f3", system="4-prefix forbidden route audit", failure_mode="f3_forbidden_route",
        reference_report_id=ref_id, reference_label=res["ref_label"], candidate_report_id="network_f3_learned", candidate_label="+P0->P3",
        diff=res["diff"], normalization={"ordered_pairs": 12, "action_opportunities": 16, "constraint_opportunities": 8}),
    RESULTS / "network_f3.sofaudit")

    # F4
    section("F4: Metric Distortion -- all routes weakened")
    mats = build_f4_metric_distortion()
    res = run_failure_mode("f4_metric_distortion", mats, "weight=0.1")
    print(f"  Reference: {res['ref_label']}\n  Learned:   all weights = 0.1 (high latency / poor links)")
    print_diff_summary(res["diff"]); all_results["f4"] = res
    write_artifact(build_sofreport(report_id="network_f4_learned", system="4-prefix (metric distortion)",
        sectorization={"origin": "one-hot prefix sectors", "prefixes": LABELS, "sector_count": N_PREFIXES, "strict_sof_realization": True},
        observable_family={"observables": ["X_internal (w=0.1)", "X_external (w=0.1)"]},
        audit=res["learned_audit"], claim_note="constructed failure: metric distortion",
        failure_modes=["all route weights reduced to 0.1"]), RESULTS / "network_f4_learned.sofreport")
    write_artifact(build_sofaudit(audit_id="network_f4", system="4-prefix metric distortion audit", failure_mode="f4_metric_distortion",
        reference_report_id=ref_id, reference_label=res["ref_label"], candidate_report_id="network_f4_learned", candidate_label="weight=0.1",
        diff=res["diff"], normalization={"ordered_pairs": 12, "action_opportunities": 16, "constraint_opportunities": 8}),
    RESULTS / "network_f4.sofaudit")

    # F5
    section("F5: ACL Policy Wall -- open -> block P1->P3 -> block P3->P2")
    wall_path = build_f5_acl_policy_path()
    wall_ref = compute_wall_record(wall_path)
    lrn_model = build_f5_learned()
    lrn_mats = lrn_model.action_matrices()
    lrn_base = compute_wall_record([lrn_model])[0]
    wall_lrn = [{**lrn_base, "ext_edges": m.external} for m in wall_path]
    res = run_failure_mode("f5_acl_policy", lrn_mats, lrn_model.label(), wall_ref=wall_ref, wall_lrn=wall_lrn)
    acl_states = ["open", "open", "block P1<->P3", "block P3<->P2"]
    print(f"  Reference ACL policy: open -> block P1<->P3 -> block P3<->P2")
    print(f"  Learned (stale):      open (ACL update not applied)")
    print(f"  {'ACL':<16s} {'ext':>4s} {'fR1_ref':>8s} {'fR1_lrn':>8s} {'fR1_d':>7s} {'fDW_ref':>8s} {'fDW_lrn':>8s} {'fDW_d':>7s}")
    for step in res["diff"].get("wall_record_mismatch", {}).get("steps", []):
        s = step; acl = acl_states[s["step"]] if s["step"] < 4 else "?"
        mark = " <-- wall" if s["frozen_R1_delta"] != 0 else ""
        ext = s.get('ext_edges', 0)
        print(f"  {acl:<16s} {ext:>4d} {s['frozen_R1_ref']:>8d} {s['frozen_R1_lrn']:>8d} {s['frozen_R1_delta']:>+7d} {s['frozen_D_word_ref']:>8d} {s['frozen_D_word_lrn']:>8d} {s['frozen_D_word_delta']:>+7d}{mark}")
    all_results["f5"] = res
    write_artifact(build_sofreport(report_id="network_f5_learned", system="4-prefix (ACL policy)",
        sectorization={"origin": "one-hot prefix sectors", "prefixes": LABELS, "sector_count": N_PREFIXES, "strict_sof_realization": True},
        observable_family={"observables": ["X_internal", "X_external"], "deformation": "ACL policy changes"},
        audit=res["learned_audit"], claim_note="constructed failure: stale ACL policy",
        failure_modes=["ACL policy not updated, reference blocks prefixes"]), RESULTS / "network_f5_learned.sofreport")
    write_artifact(build_sofaudit(audit_id="network_f5", system="4-prefix ACL policy audit", failure_mode="f5_acl_policy",
        reference_report_id=ref_id, reference_label=res["ref_label"], candidate_report_id="network_f5_learned", candidate_label=lrn_model.label(),
        diff=res["diff"], normalization={"ordered_pairs": 12, "action_opportunities": 16, "constraint_opportunities": 8, "path_samples": 4}),
    RESULTS / "network_f5.sofaudit")

    # summary
    section("Diff Protocol Summary -- Network Routing (Appendix)")
    print(f"  {'Failure':<26s} {'Supp':>5s} {'BrdW':>5s} {'BrdL':>5s} {'Dep':>5s} {'FR1':>5s} {'FDW':>5s} {'FDL':>5s} {'CnsV':>5s} {'CtrlR':>5s} {'Wall':>5s}")
    print(f"  {'-'*26} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5}")
    for key, r in all_results.items():
        d = r["diff"]; fp = d["frozen_pair_disagreement"]; dd = d["depth_distortion"]
        print(f"  {r['name']:<26s} {d['support_mismatch']['total_mismatch']:>5d} {d['bridge_word_mismatch']['total_mismatch']:>5d} {d['bridge_lie_mismatch']['total_mismatch']:>5d} {dd['total_mismatch']:>5d} {fp['frozen_R1']['delta']:>+5d} {fp['frozen_D_word']['delta']:>+5d} {fp['frozen_D_lie']['delta']:>+5d} {d.get('constraint_violations',{}).get('count',0):>5d} {d.get('action_response_failure',{}).get('total_large_deltas',0):>5d} {d.get('wall_record_mismatch',{}).get('n_steps',0):>5d}")

    print(f"\n  Network routing is the 5th Regime A domain (appendix).")
    print(f"  Distinction from Compiler: ACL REMOVES edges (constraint observable),")
    print(f"  not additive.  Blocked prefix is a structural analogue of freezing.")
    print("\nDone.")
    return all_results

def main(): run()

if __name__ == "__main__": run()
