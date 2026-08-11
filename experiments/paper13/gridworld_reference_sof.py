"""Paper XIII: GridWorld SOF Report Alignment control.

Regime A: ground-truth 5x5 GridWorld reference plus five constructed transition
model variants. Demonstrates the paired SOF alignment protocol:

    Reference SOF Report R*  <->  Candidate SOF Report R
                    ->
              Delta_audit (8 dimensions)

Failure modes:
    F1 action aliasing       N and S produce identical transitions
    F2 persistence loss      position smearing after certain moves
    F3 forbidden edge        model hallucinates an obstacle-crossing transition
    F4 rare bridge deletion  long-tail 2-step path removed
    F5 obstacle deformation  obstacle shift → wall-record comparison

Claim status:
    - Constructive protocol validation (Regime A).
    - Demonstrates SOF diff protocol on controlled failure modes.
    - Not a theorem about all world models.

Grid: 5×5 = 25 cells, obstacle at (2,2), walls at boundaries.
Sectors: 25 one-hot position sectors.
Observables: skew-symmetrised transition matrices for {N,S,E,W}.
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
SIZE = 5
N_CELLS = SIZE * SIZE
OBSTACLE = (2, 2)
FROZEN = 999
TOL = 1e-8
MAX_DEPTH = 6

ACTION_NAMES = ["N", "S", "E", "W"]
ACTION_DELTA = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}


# ── GridWorld ────────────────────────────────────────────────────────────────
class GridWorld:
    """5×5 grid with obstacles and walls.  Actions are deterministic single-step
    moves; blocked moves stay in place."""

    def __init__(self, size: int = SIZE, obstacles: list[tuple[int, int]] | None = None):
        self.size = size
        self.n_cells = size * size
        self.obstacles: set[tuple[int, int]] = set(obstacles or [])

    def cell_index(self, r: int, c: int) -> int:
        return r * self.size + c

    def index_cell(self, idx: int) -> tuple[int, int]:
        return divmod(idx, self.size)

    def is_valid(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size and (r, c) not in self.obstacles

    def transition_matrix(self, action: str) -> np.ndarray:
        """T[s', s] = 1 if action takes s → s', 0 otherwise.

        Obstacle cells act as **absorbing sectors**: all actions from an obstacle
        cell self-loop (the agent cannot enter or leave).  Boundary walls similarly
        block moves past the grid edge."""
        dr, dc = ACTION_DELTA[action]
        T = np.zeros((self.n_cells, self.n_cells), dtype=float)
        for r in range(self.size):
            for c in range(self.size):
                src = self.cell_index(r, c)
                if (r, c) in self.obstacles:
                    T[src, src] = 1.0  # absorbing sector
                    continue
                nr, nc = r + dr, c + dc
                if self.is_valid(nr, nc):
                    T[self.cell_index(nr, nc), src] = 1.0
                else:
                    T[src, src] = 1.0
        return T

    def action_matrices(self) -> dict[str, np.ndarray]:
        return {a: self.transition_matrix(a) for a in ACTION_NAMES}

    def label(self) -> str:
        obs = sorted(self.obstacles)
        return f"GridWorld({self.size}x{self.size}, obstacles={obs})"


# ── SOF construction ─────────────────────────────────────────────────────────
def cell_sectors() -> list[np.ndarray]:
    """25 one-hot cell sectors in ambient dim=25."""
    eye = np.eye(N_CELLS, dtype=complex)
    return [eye[:, [i]] for i in range(N_CELLS)]


def skew(M: np.ndarray) -> np.ndarray:
    return ((M - M.T) / 2.0).astype(complex)


def build_observables(action_matrices: dict[str, np.ndarray]) -> tuple[list[np.ndarray], dict[str, np.ndarray]]:
    """Return skew-symmetrised observables and per-control raw matrices."""
    raw = {a: T.copy() for a, T in action_matrices.items()}
    obs = [skew(T) for T in action_matrices.values()]
    return obs, raw


def action_response_matrix(sectors: list[np.ndarray], X: np.ndarray) -> np.ndarray:
    """Per-action R1: R[i,j] = ‖P_i X P_j‖_F for i≠j, 0 on diagonal."""
    n = len(sectors)
    R = np.zeros((n, n), dtype=float)
    for i in range(n):
        PiX = sectors[i].conj().T @ X
        for j in range(n):
            if i != j:
                R[i, j] = float(np.linalg.norm(PiX @ sectors[j]))
    return R


def action_response_matrices(sectors: list[np.ndarray], observables: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Per-action response matrices R_a[i,j]."""
    return {a: action_response_matrix(sectors, X) for a, X in observables.items()}


def full_audit(sectors: list[np.ndarray], observables: list[np.ndarray]) -> dict:
    """Run both AccessibilityEngine (Lie) and word-based diagnostics."""
    engine = AccessibilityEngine(sectors, observables, tol=TOL, max_depth=MAX_DEPTH)
    lie = engine.audit()
    frozen = engine.frozen_pairs()
    _R1, _R2_lie, _ = engine.support()
    D_lie, _ = engine.depth()

    R1_word = compute_direct_support(sectors, observables, tol=TOL)
    R2_word = compute_length_two_support(sectors, observables, tol=TOL)
    D_word = compute_word_depth_matrix(sectors, observables, max_depth=MAX_DEPTH, tol=TOL, frozen=FROZEN)
    # _R1 is (n_gens, n_sec, n_sec), _R2_lie is (n_pairs, n_sec, n_sec) — aggregate
    R2_lie_agg = np.any(_R2_lie, axis=0)
    D_lie_mat = D_lie
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
        "D_lie": D_lie_mat,
        "D_lie_max": int(D_lie_mat[D_lie_mat != FROZEN].max()) if np.any(D_lie_mat != FROZEN) else 0,
        "frozen_D_word": frozen_D_word,
        "frozen_D_lie": frozen["frozen_D"],
        **lie,
        **frozen,
    }


# ── failure-mode constructors ────────────────────────────────────────────────
def build_reference() -> GridWorld:
    return GridWorld(obstacles=[OBSTACLE])


def build_f1_action_aliasing() -> dict[str, np.ndarray]:
    """N and S are identical — both use the N transition matrix."""
    gw = build_reference()
    mats = gw.action_matrices()
    mats["S"] = mats["N"].copy()  # alias: S → N
    return mats


def build_f2_persistence_loss() -> dict[str, np.ndarray]:
    """Position smearing: E from (1,1) is blurred across three targets."""
    gw = build_reference()
    mats = gw.action_matrices()
    src = gw.cell_index(1, 1)  # cell 6
    # reference: E from (1,1) → (1,2) = cell 7
    # learned: smeared → 0.5×(1,2) + 0.3×(0,1) + 0.2×(1,0)
    T = mats["E"].copy()
    T[:, src] = 0.0
    T[gw.cell_index(1, 2), src] = 0.5
    T[gw.cell_index(0, 1), src] = 0.3
    T[gw.cell_index(1, 0), src] = 0.2
    mats["E"] = T
    return mats


def build_f3_forbidden_edge() -> dict[str, np.ndarray]:
    """Hallucinated wall-crossing: S from (1,2) goes through obstacle to (2,2)."""
    gw = build_reference()
    mats = gw.action_matrices()
    src = gw.cell_index(1, 2)  # cell 7
    dst = gw.cell_index(2, 2)  # cell 12 — the obstacle
    T = mats["S"].copy()
    T[:, src] = 0.0
    T[dst, src] = 1.0  # forbidden: goes through obstacle
    mats["S"] = T
    return mats


def build_f4_rare_bridge_deletion() -> dict[str, np.ndarray]:
    """Delete ALL E transitions from column-0 cells (0,5,10,15,20).
    This deletes 2-step bridges that rely on those E edges, e.g.:
      (4,0)→E→(4,1)→N→(3,1)  and  (4,0)→N→(3,0)→E→(3,1)
    With E from col-0 removed, these bridges vanish.
    This is a localised deletion — E works normally everywhere else."""
    gw = build_reference()
    mats = gw.action_matrices()
    T = mats["E"].copy()
    column_0_cells = [gw.cell_index(r, 0) for r in range(SIZE)]  # 0,5,10,15,20
    for src in column_0_cells:
        T[:, src] = 0.0
        T[src, src] = 1.0  # E from col-0 cells stays in place
    mats["E"] = T
    return mats


def build_f5_obstacle_deformation_path() -> list[GridWorld]:
    """Obstacle moves (2,2)→(2,1)→(2,0)→(1,0)→(0,0)."""
    path = [(2, 2), (2, 1), (2, 0), (1, 0), (0, 0)]
    return [GridWorld(obstacles=[pos]) for pos in path]


def build_f5_learned() -> GridWorld:
    """Learned model has obstacle at (2,1) instead of (2,2)."""
    return GridWorld(obstacles=[(2, 1)])


# ── diff protocol ────────────────────────────────────────────────────────────
def diff_support(R1_ref: np.ndarray, R1_learned: np.ndarray) -> dict:
    n = R1_ref.shape[0]
    extra = []   # in learned but not in ref
    missing = []  # in ref but not in learned
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if R1_ref[i, j] and not R1_learned[i, j]:
                missing.append([i, j])
            elif not R1_ref[i, j] and R1_learned[i, j]:
                extra.append([i, j])
    return {
        "extra_support": extra,
        "extra_count": len(extra),
        "missing_support": missing,
        "missing_count": len(missing),
        "total_mismatch": len(extra) + len(missing),
        "ref_offdiag": offdiag_count(R1_ref),
        "learned_offdiag": offdiag_count(R1_learned),
    }


def diff_bridge(R2_word_ref: np.ndarray, R2_word_learned: np.ndarray) -> dict:
    n = R2_word_ref.shape[0]
    extra = []
    missing = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if R2_word_ref[i, j] and not R2_word_learned[i, j]:
                missing.append([i, j])
            elif not R2_word_ref[i, j] and R2_word_learned[i, j]:
                extra.append([i, j])
    return {
        "extra_bridge": extra,
        "extra_count": len(extra),
        "missing_bridge": missing,
        "missing_count": len(missing),
        "total_mismatch": len(extra) + len(missing),
        "ref_offdiag": offdiag_count(R2_word_ref),
        "learned_offdiag": offdiag_count(R2_word_learned),
    }


def diff_depth(D_ref: np.ndarray, D_learned: np.ndarray) -> dict:
    n = D_ref.shape[0]
    distortions = []
    ref_frozen_not_learned = []
    learned_frozen_not_ref = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dr = D_ref[i, j]
            dl = D_learned[i, j]
            ref_frz = dr == FROZEN
            lrn_frz = dl == FROZEN
            if ref_frz and not lrn_frz:
                ref_frozen_not_learned.append([i, j, int(dl)])
            elif not ref_frz and lrn_frz:
                learned_frozen_not_ref.append([i, j, int(dr)])
            elif not ref_frz and not lrn_frz and dr != dl:
                distortions.append([i, j, int(dr), int(dl)])
    return {
        "depth_distortions": distortions,
        "distortion_count": len(distortions),
        "ref_frozen_learned_not": ref_frozen_not_learned,
        "ref_frozen_learned_not_count": len(ref_frozen_not_learned),
        "learned_frozen_ref_not": learned_frozen_not_ref,
        "learned_frozen_ref_not_count": len(learned_frozen_not_ref),
        "total_mismatch": (
            len(distortions)
            + len(ref_frozen_not_learned)
            + len(learned_frozen_not_ref)
        ),
    }


def diff_frozen_pairs(frozen_R1_ref: int, frozen_R1_learned: int,
                      frozen_D_word_ref: int, frozen_D_word_learned: int,
                      frozen_D_lie_ref: int, frozen_D_lie_learned: int) -> dict:
    return {
        "frozen_R1": {"ref": frozen_R1_ref, "learned": frozen_R1_learned,
                       "delta": frozen_R1_learned - frozen_R1_ref},
        "frozen_D_word": {
            "ref": frozen_D_word_ref,
            "learned": frozen_D_word_learned,
            "delta": frozen_D_word_learned - frozen_D_word_ref,
        },
        "frozen_D_lie": {
            "ref": frozen_D_lie_ref,
            "learned": frozen_D_lie_learned,
            "delta": frozen_D_lie_learned - frozen_D_lie_ref,
        },
    }


def diff_constraint_violations(raw_ref: dict[str, np.ndarray],
                                raw_learned: dict[str, np.ndarray],
                                tol: float = TOL) -> dict:
    """Transitions present in learned but absent in reference (by raw T_a)."""
    violations = []
    for a in ACTION_NAMES:
        T_ref = raw_ref.get(a, np.zeros((N_CELLS, N_CELLS)))
        T_learned = raw_learned.get(a, np.zeros((N_CELLS, N_CELLS)))
        for i in range(N_CELLS):
            for j in range(N_CELLS):
                if i == j:
                    continue
                if abs(T_ref[i, j]) < tol and abs(T_learned[i, j]) >= tol:
                    violations.append({"action": a, "from": j, "to": i,
                                       "learned_value": float(T_learned[i, j])})
    return {"violations": violations, "count": len(violations)}


def diff_action_response(response_ref: dict[str, np.ndarray],
                          response_learned: dict[str, np.ndarray],
                          threshold: float = 0.01) -> dict:
    """Compare native-control response matrices."""
    n = response_ref[ACTION_NAMES[0]].shape[0]

    # per-pair response deltas
    deltas: dict[str, list] = {}
    for a in ACTION_NAMES:
        Rr = response_ref[a]
        Rl = response_learned[a]
        large = []
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d = abs(Rr[i, j] - Rl[i, j])
                if d > threshold:
                    large.append({"pair": [i, j], "ref": round(Rr[i, j], 4),
                                  "learned": round(Rl[i, j], 4), "delta": round(d, 4)})
        deltas[a] = large

    # action aliasing: pairwise separation collapse
    aliasing = []
    for ai in range(len(ACTION_NAMES)):
        for aj in range(ai + 1, len(ACTION_NAMES)):
            a, b = ACTION_NAMES[ai], ACTION_NAMES[aj]
            sep_ref = np.linalg.norm(response_ref[a] - response_ref[b])
            sep_learned = np.linalg.norm(response_learned[a] - response_learned[b])
            if sep_ref > threshold and sep_learned < threshold:
                aliasing.append({"actions": [a, b], "sep_ref": round(sep_ref, 4),
                                 "sep_learned": round(sep_learned, 4),
                                 "diagnosis": "aliased"})
            elif sep_ref > threshold and sep_learned > threshold:
                ratio = sep_learned / sep_ref if sep_ref > 0 else float("inf")
                if ratio < 0.5:
                    aliasing.append({"actions": [a, b], "sep_ref": round(sep_ref, 4),
                                     "sep_learned": round(sep_learned, 4),
                                     "diagnosis": "partial_collapse",
                                     "ratio": round(ratio, 4)})

    return {"per_action_deltas": deltas,
            "total_large_deltas": sum(len(v) for v in deltas.values()),
            "action_aliasing": aliasing}


def diff_wall_record(wall_ref: list[dict], wall_learned: list[dict]) -> dict:
    """Compare parameterized wall records (frozen set along deformation path)."""
    n_steps = len(wall_ref)
    steps = []
    for k in range(n_steps):
        fr = wall_ref[k]
        fl = wall_learned[k]
        steps.append({
            "step": k,
            "parameter": fr.get("parameter"),
            "frozen_R1_ref": fr["frozen_R1"],
            "frozen_R1_learned": fl["frozen_R1"],
            "frozen_R1_delta": fl["frozen_R1"] - fr["frozen_R1"],
            "frozen_D_word_ref": fr["frozen_D_word"],
            "frozen_D_word_learned": fl["frozen_D_word"],
            "frozen_D_word_delta": fl["frozen_D_word"] - fr["frozen_D_word"],
            "frozen_D_lie_ref": fr["frozen_D_lie"],
            "frozen_D_lie_learned": fl["frozen_D_lie"],
            "frozen_D_lie_delta": fl["frozen_D_lie"] - fr["frozen_D_lie"],
        })
    return {"steps": steps, "n_steps": n_steps}


def full_diff(ref_audit: dict, learned_audit: dict,
              raw_ref: dict[str, np.ndarray] | None = None,
              raw_learned: dict[str, np.ndarray] | None = None,
              resp_ref: dict[str, np.ndarray] | None = None,
              resp_learned: dict[str, np.ndarray] | None = None,
              wall_ref: list[dict] | None = None,
              wall_learned: list[dict] | None = None) -> dict:
    """Run the eight audit dimensions, with null optional channels."""
    result: dict = {
        "support_mismatch": diff_support(ref_audit["R1_word"], learned_audit["R1_word"]),
        "bridge_word_mismatch": diff_bridge(ref_audit["R2_word"], learned_audit["R2_word"]),
        "bridge_lie_mismatch": diff_bridge(ref_audit["R2_lie"], learned_audit["R2_lie"]),
        "depth_distortion": diff_depth(ref_audit["D_word"], learned_audit["D_word"]),
        "frozen_pair_disagreement": diff_frozen_pairs(
            ref_audit["frozen_R1"], learned_audit["frozen_R1"],
            ref_audit["frozen_D_word"], learned_audit["frozen_D_word"],
            ref_audit["frozen_D_lie"], learned_audit["frozen_D_lie"],
        ),
    }
    if raw_ref is not None and raw_learned is not None:
        result["constraint_violations"] = diff_constraint_violations(raw_ref, raw_learned)
    if resp_ref is not None and resp_learned is not None:
        result["action_response_failure"] = diff_action_response(resp_ref, resp_learned)
    if wall_ref is not None and wall_learned is not None:
        result["wall_record_mismatch"] = diff_wall_record(wall_ref, wall_learned)
    return result


# ── wall record ──────────────────────────────────────────────────────────────
def compute_wall_record(gw_list: list[GridWorld]) -> list[dict]:
    """Compute SOF audit at each point along a deformation path."""
    sectors = cell_sectors()
    records = []
    for gw in gw_list:
        mats = gw.action_matrices()
        obs, raw = build_observables(mats)
        audit = full_audit(sectors, obs)
        records.append({
            "parameter": gw.label(),
            "obstacles": sorted(gw.obstacles),
            "frozen_R1": audit["frozen_R1"],
            "frozen_D_word": audit["frozen_D_word"],
            "frozen_D_lie": audit["frozen_D_lie"],
            "R1_offdiag": audit["R1_offdiag"],
            "D_word_max": audit["D_word_max"],
        })
    return records


# ── SOF report + audit output ────────────────────────────────────────────────
def make_sofreport(report_id: str, system: str, label: str, audit: dict) -> dict:
    """Single-system .sofreport (Paper XII format)."""
    return build_sofreport(
        report_id=report_id,
        system=system,
        sectorization={
            "origin": "one-hot grid-cell position sectors",
            "sector_count": N_CELLS,
            "grid_size": f"{SIZE}x{SIZE}",
            "obstacle_treatment": "absorbing sector",
            "strict_sof_realization": True,
        },
        observable_family={
            "actions": ACTION_NAMES,
            "generator_type": "skew-symmetrised deterministic transition matrices",
        },
        audit=audit,
        claim_note="controlled finite GridWorld evidence (Regime A)",
        failure_modes=[
            "constructed finite transition system, not a learned production world model",
            "support is computed from skew-symmetrised action generators",
            "norm-based response constants do not retain action orientation or sign",
        ],
        extra={"model_label": label, "domain": "gridworld"},
    )


def make_sofaudit(audit_id: str, system: str, failure_mode: str,
                  ref_label: str, lrn_label: str,
                  ref_sofreport_id: str, lrn_sofreport_id: str,
                  diff: dict,
                  regime: str = "A") -> dict:
    """Paired .sofaudit (Paper XIII format)."""
    return build_sofaudit(
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
            "controlled constructed variant, not a learned production world model",
            "identity sector and observable alignment only",
            "norm-based action responses are insensitive to sign and orientation aliasing",
        ],
        extra={"domain": "gridworld"},
    )


def write_sofreport(report: dict, stem: str) -> Path:
    path = Path(__file__).resolve().parent / "archive" / "results" / f"{stem}.sofreport"
    return write_artifact(report, path)


def write_sofaudit(audit: dict, stem: str) -> Path:
    path = Path(__file__).resolve().parent / "archive" / "results" / f"{stem}.sofaudit"
    return write_artifact(audit, path)


# ── run single failure mode ──────────────────────────────────────────────────
def run_failure_mode(name: str, learned_mats: dict[str, np.ndarray],
                     learned_gw: GridWorld | None = None,
                     wall_ref: list[dict] | None = None,
                     wall_learned: list[dict] | None = None) -> dict:
    sectors = cell_sectors()

    # reference
    gw_ref = build_reference()
    ref_mats = gw_ref.action_matrices()
    ref_obs, ref_raw = build_observables(ref_mats)
    ref_audit = full_audit(sectors, ref_obs)

    # learned
    learned_obs, learned_raw = build_observables(learned_mats)
    learned_audit = full_audit(sectors, learned_obs)

    # Native-control response matrices; serialized under the v1.0 alias.
    ref_resp = action_response_matrices(sectors,
                                        {a: skew(learned_mats[a]) for a in ACTION_NAMES})  # placeholder
    # rebuild correctly
    ref_resp = action_response_matrices(sectors,
                                        {a: skew(ref_mats[a]) for a in ACTION_NAMES})
    lrn_resp = action_response_matrices(sectors,
                                        {a: skew(learned_mats[a]) for a in ACTION_NAMES})

    diff = full_diff(ref_audit, learned_audit,
                     raw_ref=ref_raw, raw_learned=learned_raw,
                     resp_ref=ref_resp, resp_learned=lrn_resp,
                     wall_ref=wall_ref, wall_learned=wall_learned)

    ll = learned_gw.label() if learned_gw else name
    return {
        "name": name,
        "ref_audit": ref_audit,
        "learned_audit": learned_audit,
        "diff": diff,
        "ref_label": gw_ref.label(),
        "learned_label": ll,
    }


# ── print helpers ────────────────────────────────────────────────────────────
def print_diff_summary(diff: dict) -> None:
    sm = diff["support_mismatch"]
    print(f"    Support mismatch:       {sm['total_mismatch']:>4d}  "
          f"(extra={sm['extra_count']}, missing={sm['missing_count']})")
    bw = diff["bridge_word_mismatch"]
    print(f"    Bridge mismatch (word): {bw['total_mismatch']:>4d}  "
          f"(extra={bw['extra_count']}, missing={bw['missing_count']})")
    bl = diff["bridge_lie_mismatch"]
    print(f"    Bridge mismatch (Lie):  {bl['total_mismatch']:>4d}  "
          f"(extra={bl['extra_count']}, missing={bl['missing_count']})")
    dd = diff["depth_distortion"]
    print(f"    Depth mismatch:         {dd['total_mismatch']:>4d}  "
          f"(ref-frz-not-learned={dd['ref_frozen_learned_not_count']}, "
          f"lrn-frz-not-ref={dd['learned_frozen_ref_not_count']})")
    fp = diff["frozen_pair_disagreement"]
    print(f"    Frozen R1 δ:            {fp['frozen_R1']['delta']:>+4d}")
    print(f"    Frozen word-D δ:        {fp['frozen_D_word']['delta']:>+4d}")
    print(f"    Frozen Lie-D  δ:        {fp['frozen_D_lie']['delta']:>+4d}")

    if "constraint_violations" in diff:
        cv = diff["constraint_violations"]
        print(f"    Constraint violations: {cv['count']:>4d}")
        if cv["count"] <= 8:
            for v in cv["violations"]:
                print(f"      {v['action']}: {v['from']}→{v['to']}  "
                      f"(learned={v['learned_value']:.3f})")

    if "action_response_failure" in diff:
        ar = diff["action_response_failure"]
        print(f"    Control-response δ > ε: {ar['total_large_deltas']:>4d}")
        if ar["action_aliasing"]:
            for aa in ar["action_aliasing"]:
                print(f"      aliasing {aa['actions']}: sep_ref={aa['sep_ref']:.3f} "
                      f"sep_learned={aa['sep_learned']:.3f} [{aa['diagnosis']}]")

    if "wall_record_mismatch" in diff:
        wr = diff["wall_record_mismatch"]
        print(f"    Wall-record steps:  {wr['n_steps']:>4d}")
        for step in wr["steps"]:
            print(f"      step {step['step']} {step['parameter']}: "
                  f"R1 δ={step['frozen_R1_delta']:+d}, "
                  f"word-D δ={step['frozen_D_word_delta']:+d}, "
                  f"Lie-D δ={step['frozen_D_lie_delta']:+d}")


def section(title: str) -> None:
    print(f"\n{'─' * 76}")
    print(f"  {title}")
    print(f"{'─' * 76}")


# ── main ─────────────────────────────────────────────────────────────────────
def run() -> dict:
    print("=" * 76)
    print("  Paper XIII: GridWorld SOF Report Alignment")
    print("=" * 76)
    print(f"  Regime A: 5×5 grid, {N_CELLS} cell sectors, obstacle at {OBSTACLE}")
    print(f"  Observables: skew-symmetrised transition matrices for {ACTION_NAMES}")
    print()

    all_results = {}

    # ── F1: Action Aliasing ──
    section("F1: Action Aliasing — N and S are identical")
    mats = build_f1_action_aliasing()
    gw_ref = build_reference()
    res = run_failure_mode("f1_action_aliasing", mats)
    print(f"  Reference: {gw_ref.label()}")
    print(f"  Learned:   N=S (aliased to N transition matrix)")
    print("  Norm-based response constants cannot distinguish opposite action orientation;")
    print("  the raw transition-constraint channel carries this diagnosis.")
    print_diff_summary(res["diff"])
    all_results["f1"] = res
    write_sofreport(make_sofreport("gridworld_ref", "5×5 GridWorld reference",
                                   res["ref_label"], res["ref_audit"]), "gridworld_ref")
    write_sofreport(make_sofreport("gridworld_f1_learned", "5×5 GridWorld (N=S aliased)",
                                   "N=S aliased", res["learned_audit"]), "gridworld_f1_learned")
    write_sofaudit(make_sofaudit("gridworld_f1", "5×5 GridWorld action aliasing audit",
                                 "f1_action_aliasing",
                                 res["ref_label"], "N=S aliased",
                                 "gridworld_ref", "gridworld_f1_learned",
                                 res["diff"]), "gridworld_f1")

    # ── F2: Persistence Loss ──
    section("F2: Persistence Loss — E from (1,1) smeared")
    mats = build_f2_persistence_loss()
    res = run_failure_mode("f2_persistence_loss", mats)
    print(f"  Reference: {gw_ref.label()}")
    print(f"  Learned:   E from (1,1) → 0.5×(1,2)+0.3×(0,1)+0.2×(1,0)")
    print_diff_summary(res["diff"])
    all_results["f2"] = res
    write_sofreport(make_sofreport("gridworld_f2_learned", "5×5 GridWorld (persistence loss)",
                                   "E(1,1) smeared", res["learned_audit"]), "gridworld_f2_learned")
    write_sofaudit(make_sofaudit("gridworld_f2", "5×5 GridWorld persistence loss audit",
                                 "f2_persistence_loss",
                                 res["ref_label"], "E(1,1) smeared",
                                 "gridworld_ref", "gridworld_f2_learned",
                                 res["diff"]), "gridworld_f2")

    # ── F3: Forbidden Edge ──
    section("F3: Forbidden Edge — S from (1,2) crosses obstacle")
    mats = build_f3_forbidden_edge()
    res = run_failure_mode("f3_forbidden_edge", mats)
    print(f"  Reference: {gw_ref.label()}")
    print(f"  Learned:   S: (1,2)→(2,2) [hallucinated wall-crossing]")
    print_diff_summary(res["diff"])
    all_results["f3"] = res
    write_sofreport(make_sofreport("gridworld_f3_learned", "5×5 GridWorld (forbidden edge)",
                                   "wall-crossing hallucination", res["learned_audit"]), "gridworld_f3_learned")
    write_sofaudit(make_sofaudit("gridworld_f3", "5×5 GridWorld forbidden edge audit",
                                 "f3_forbidden_edge",
                                 res["ref_label"], "wall-crossing hallucination",
                                 "gridworld_ref", "gridworld_f3_learned",
                                 res["diff"]), "gridworld_f3")

    # ── F4: Rare Bridge Deletion ──
    section("F4: Rare Bridge Deletion — E removed from all column-0 cells")
    mats = build_f4_rare_bridge_deletion()
    res = run_failure_mode("f4_rare_bridge_deletion", mats)

    gw = build_reference()
    # (4,0)=20 → (3,1)=16: word bridge preserved (skew-reverse path),
    #                      Lie bridge may be deleted
    pair_a, pair_b = gw.cell_index(4, 0), gw.cell_index(3, 1)  # 20, 16
    # (4,0)=20 → (4,1)=21: direct E edge deleted (col-0),
    #                      word R1 preserved (skew reverse from 21→20 via N-path connect)
    pair_c, pair_d = gw.cell_index(4, 0), gw.cell_index(4, 1)  # 20, 21
    for (si, sj), label in [((pair_a, pair_b), "(4,0)→(3,1)"),
                             ((pair_c, pair_d), "(4,0)→(4,1)")]:
        print(f"    {label} [{si}→{sj}]:")
        print(f"      R1:     ref={res['ref_audit']['R1_word'][si, sj]}  "
              f"learned={res['learned_audit']['R1_word'][si, sj]}")
        print(f"      R2_w:   ref={res['ref_audit']['R2_word'][si, sj]}  "
              f"learned={res['learned_audit']['R2_word'][si, sj]}")
        print(f"      R2_lie: ref={res['ref_audit']['R2_lie'][si, sj]}  "
              f"learned={res['learned_audit']['R2_lie'][si, sj]}")
    print(f"  Learned: E from col-0 cells (0,5,10,15,20) self-loops")
    print(f"  Word bridges preserved: reverse-oriented block components in skew generators")
    print(f"    create alternative word paths for the deleted forward transitions")
    print_diff_summary(res["diff"])
    all_results["f4"] = res
    write_sofreport(make_sofreport("gridworld_f4_learned", "5×5 GridWorld (bridge deletion)",
                                   "E col-0 removed", res["learned_audit"]), "gridworld_f4_learned")
    write_sofaudit(make_sofaudit("gridworld_f4", "5×5 GridWorld bridge deletion audit",
                                 "f4_rare_bridge_deletion",
                                 res["ref_label"], "E col-0 removed",
                                 "gridworld_ref", "gridworld_f4_learned",
                                 res["diff"]), "gridworld_f4")

    # ── F5: Obstacle Deformation ──
    section("F5: Obstacle Deformation — wall-record comparison")
    path = build_f5_obstacle_deformation_path()
    wall_ref = compute_wall_record(path)
    gw_learned = build_f5_learned()
    # learned model uses fixed obstacle at (2,1); for wall comparison,
    # we keep the learned model fixed while reference deforms
    learned_mats = gw_learned.action_matrices()
    res = run_failure_mode("f5_obstacle_deformation", learned_mats,
                           learned_gw=gw_learned,
                           wall_ref=wall_ref,
                           wall_learned=compute_wall_record([gw_learned] * len(path)))

    print(f"  Reference deformation: obstacle (2,2)→(2,1)→(2,0)→(1,0)→(0,0)")
    print(f"  Learned model:         obstacle fixed at {sorted(gw_learned.obstacles)}")
    print(f"  Wall record steps: {len(path)}")
    print(f"  {'Step':<6s} {'Obstacle':<12s} {'R1_δ':>6s} "
          f"{'WD_δ':>6s} {'LD_δ':>6s}")
    for step in res["diff"].get("wall_record_mismatch", {}).get("steps", []):
        s = step
        print(f"  {s['step']:<6d} {str(s['parameter']):<12s} "
              f"{s['frozen_R1_delta']:>+6d} "
              f"{s['frozen_D_word_delta']:>+6d} "
              f"{s['frozen_D_lie_delta']:>+6d}")

    all_results["f5"] = res
    lrn_lbl = f"obstacle at {sorted(gw_learned.obstacles)}"
    write_sofreport(make_sofreport("gridworld_f5_learned", "5×5 GridWorld (deformed obstacle)",
                                   lrn_lbl, res["learned_audit"]), "gridworld_f5_learned")
    write_sofaudit(make_sofaudit("gridworld_f5", "5×5 GridWorld obstacle deformation audit",
                                 "f5_obstacle_deformation",
                                 res["ref_label"], lrn_lbl,
                                 "gridworld_ref", "gridworld_f5_learned",
                                 res["diff"]), "gridworld_f5")

    # ── summary table ──
    section("Diff Protocol Summary")
    print(f"  {'Failure':<28s} {'Suppδ':>6s} {'BrdWδ':>6s} {'BrdLδ':>6s} "
          f"{'Depδ':>6s} {'FR1δ':>6s} {'FWDδ':>6s} {'FLDδ':>6s} "
          f"{'CnsV':>5s} {'CtrlR':>5s} {'Wall':>5s}")
    print(f"  {'-' * 28} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} "
          f"{'-' * 6} {'-' * 6} {'-' * 5} {'-' * 5} {'-' * 5}")
    for key, res in all_results.items():
        d = res["diff"]
        cv = d.get("constraint_violations", {}).get("count", 0)
        ar = d.get("action_response_failure", {}).get("total_large_deltas", 0)
        wr = d.get("wall_record_mismatch", {}).get("n_steps", 0)
        print(f"  {res['name']:<28s} "
              f"{d['support_mismatch']['total_mismatch']:>6d} "
              f"{d['bridge_word_mismatch']['total_mismatch']:>6d} "
              f"{d['bridge_lie_mismatch']['total_mismatch']:>6d} "
              f"{d['depth_distortion']['total_mismatch']:>6d} "
              f"{d['frozen_pair_disagreement']['frozen_R1']['delta']:>+6d} "
              f"{d['frozen_pair_disagreement']['frozen_D_word']['delta']:>+6d} "
              f"{d['frozen_pair_disagreement']['frozen_D_lie']['delta']:>+6d} "
              f"{cv:>5d} {ar:>5d} {wr:>5d}")

    print(f"\n  {'─' * 76}")
    print(f"  Column key:")
    print(f"    Suppδ = R1 support mismatch count")
    print(f"    BrdWδ = word bridge (R2_word) mismatch count")
    print(f"    BrdLδ = Lie bridge (R2_commutator) mismatch count")
    print(f"    Depδ  = word-depth mismatch count, including frozen/reachable changes")
    print(f"    FR1δ  = frozen-R1 delta (learned − ref)")
    print(f"    FWDδ  = frozen word-depth delta (learned − ref)")
    print(f"    FLDδ  = frozen Lie-depth delta (learned − ref)")
    print(f"    CnsV  = constraint violations")
    print(f"    CtrlR = native-control response mismatches (per-control δ > ε)")
    print(f"    Wall  = wall-record steps")
    print(f"\n  Key insight:")
    print(f"    Word bridges on skew generators are robust — reverse-direction")
    print(f"    components in skew parts preserve connectivity under local edge deletion.")
    print(f"    In the F4 control, the Lie bridge channel is more sensitive than the word channel.")
    print(f"    Each failure mode activates a distinct combination of diff dimensions.")

    print("\nDone.")
    return all_results


def main() -> None:
    run()


if __name__ == "__main__":
    main()
