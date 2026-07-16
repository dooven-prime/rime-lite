"""Paper XII diagnostic: SOF failure and degeneracy cases.

Claim status:
    - Multi-system validator fixture for the SOF diagnostic methodology.
    - Shows when a SOF Report is uninformative, degenerate, or inapplicable.
    - Not a theorem that these five cases exhaust all possible failures.

The point is methodological credibility: Paper XII should show successful
diagnostics and also report when SOF should not be used or should return a
claim-status warning.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine  # noqa: E402


def skew(M: np.ndarray) -> np.ndarray:
    return ((M - M.T) / 2.0).astype(complex)


def section(title: str) -> None:
    print("=" * 76)
    print(f"  {title}")
    print("=" * 76)


def warning(label: str, reason: str) -> None:
    print(f"  Case interpretation: {label}")
    print(f"  Reason:        {reason}")
    print()


def audit(Vs: list[np.ndarray], Xs: list[np.ndarray], max_depth: int = 3) -> dict:
    engine = AccessibilityEngine(Vs, [X.astype(complex) for X in Xs], max_depth=max_depth)
    result = engine.audit()
    result.update(engine.frozen_pairs())
    return result


def failure_single_sector() -> dict:
    section("F1: Single Sector - No Cross-Sector Transport")
    rng = np.random.RandomState(42)
    Vs = [np.eye(8, dtype=complex)]
    Xs = [skew(rng.randn(8, 8)) for _ in range(3)]
    result = audit(Vs, Xs)
    print(f"  sectors={result['n_sec']}, dims={result['sector_dims']}")
    print(f"  off-diagonal sector pairs=0, R1_count={result['R1_count']}")
    print(f"  D_max={result['D_max']}, D_repaired={result['D_repaired']}")
    warning("not applicable", "single-sector SOF has no cross-sector pair to audit")
    return {"case": "single_sector", "status": "not_applicable", **result}


def failure_random_all_to_all() -> dict:
    section("F2: Dense Random All-to-All - No Structure")
    rng = np.random.RandomState(42)
    dim, n_sec = 20, 4
    Vs = [np.eye(dim, dtype=complex)[:, i * 5 : (i + 1) * 5] for i in range(n_sec)]
    Xs = [skew(rng.randn(dim, dim)) for _ in range(3)]
    result = audit(Vs, Xs)
    print(
        f"  R1={result['R1_pct']:.1f}%, R2={result['R2_pct']:.1f}%, "
        f"D_max={result['D_max']}, D_repaired={result['D_repaired']}"
    )
    warning("uninformative", "all pairs connect immediately; no bridge or repair pattern remains")
    return {"case": "random_all_to_all", "status": "uninformative", **result}


def failure_dim_one_sectors() -> dict:
    section("F3: Over-Refined Dim-1 Sectors - Trivial Report")
    rng = np.random.RandomState(43)
    dim = 6
    Vs = [np.eye(dim, dtype=complex)[:, [idx]] for idx in range(dim)]
    Xs = [skew(rng.randn(dim, dim)) for _ in range(2)]
    result = audit(Vs, Xs)
    print(f"  sectors={result['n_sec']}, dims={result['sector_dims']}")
    print(
        f"  R1={result['R1_pct']:.1f}%, R2={result['R2_pct']:.1f}%, "
        f"D_max={result['D_max']}, frozen_R1={result['frozen_R1']}"
    )
    warning("degenerate", "one-dimensional sectors erase internal subspace structure")
    return {"case": "dim_one_sectors", "status": "degenerate", **result}


def failure_commuting_observables() -> dict:
    section("F4: Commuting Observables - No R2 Layer")
    rng = np.random.RandomState(44)
    dim = 8
    Vs = [np.eye(dim, dtype=complex)[:, :4], np.eye(dim, dtype=complex)[:, 4:]]

    X_commuting = [np.diag(rng.randn(dim)).astype(complex) for _ in range(2)]
    X_reference = [skew(rng.randn(dim, dim)) for _ in range(2)]

    commuting = audit(Vs, X_commuting)
    reference = audit(Vs, X_reference)
    print(
        f"  commuting:    R1={commuting['R1_pct']:.1f}%, "
        f"R2={commuting['R2_pct']:.1f}%, D_repaired={commuting['D_repaired']}"
    )
    print(
        f"  noncommuting: R1={reference['R1_pct']:.1f}%, "
        f"R2={reference['R2_pct']:.1f}%, D_repaired={reference['D_repaired']}"
    )
    warning("degenerate", "commuting observables do not create a commutator-driven R2 layer")
    return {
        "case": "commuting_observables",
        "status": "degenerate",
        "commuting": commuting,
        "reference": reference,
    }


def failure_sector_observable_mismatch() -> dict:
    section("F5: Sector-Observable Mismatch - Frozen or Invisible")
    rng = np.random.RandomState(45)
    dim = 12
    Vs = [np.eye(dim, dtype=complex)[:, :6], np.eye(dim, dtype=complex)[:, 6:]]

    mismatched = np.zeros((dim, dim), dtype=float)
    mismatched[8:, 8:] = rng.randn(4, 4)
    X_mismatched = [skew(mismatched)]
    X_aligned = [skew(rng.randn(dim, dim)) for _ in range(2)]

    bad = audit(Vs, X_mismatched)
    good = audit(Vs, X_aligned)
    print(f"  mismatched: R1={bad['R1_pct']:.1f}%, frozen_R1={bad['frozen_R1']}")
    print(f"  aligned:    R1={good['R1_pct']:.1f}%, frozen_R1={good['frozen_R1']}")
    warning("not useful", "observables have no meaningful cross-sector support")
    return {
        "case": "sector_observable_mismatch",
        "status": "not_useful",
        "mismatched": bad,
        "aligned_reference": good,
    }


def print_applicability_table() -> None:
    section("SOF Diagnostic Applicability Table")
    rows = [
        ("multiple sectors", "needed", "cross-sector transport requires sector pairs"),
        ("single sector", "not applicable", "no pair to audit"),
        ("structured noncommuting observables", "useful", "R2 and repair can be meaningful"),
        ("commuting observables", "degenerate", "commutator layer is absent"),
        ("sector-observable overlap", "needed", "R1 needs nonzero cross-sector blocks"),
        ("sector-observable mismatch", "not useful", "all relevant pairs are invisible or frozen"),
        ("moderate sector granularity", "useful", "subspace structure remains visible"),
        ("dim-1 or full-space sectors", "degenerate", "sectorization is too fine or too coarse"),
        ("dense random observables", "uninformative", "all-to-all support destroys pattern"),
    ]
    print(f"  {'Condition':<36s} {'Interpretation':<16s} Why")
    print(f"  {'-' * 36} {'-' * 16} {'-' * 35}")
    for condition, status, why in rows:
        print(f"  {condition:<36s} {status:<16s} {why}")
    print()
    print("  SOF is deployable only when sectors and observables are compatible,")
    print("  non-degenerate, and structured enough to produce an informative report.")


def run() -> list[dict]:
    return [
        failure_single_sector(),
        failure_random_all_to_all(),
        failure_dim_one_sectors(),
        failure_commuting_observables(),
        failure_sector_observable_mismatch(),
    ]


def audit_variants(case: dict) -> dict[str, dict]:
    if "R1_pct" in case:
        return {"primary": case}
    return {
        name: value
        for name, value in case.items()
        if isinstance(value, dict) and "R1_pct" in value
    }


def sofreport(cases: list[dict]) -> dict:
    reasons = {
        "single_sector": "no cross-sector pair exists",
        "random_all_to_all": "all pairs connect immediately, so no structure remains",
        "dim_one_sectors": "one-dimensional sectors erase internal subspace structure",
        "commuting_observables": "the commutator-driven R2 layer is absent",
        "sector_observable_mismatch": "the observables do not see the proposed sector interface",
    }
    support_cases = []
    bridge_cases = []
    repair_cases = []
    for case in cases:
        variants = audit_variants(case)
        support_cases.append(
            {
                "case": case["case"],
                "case_interpretation": case["status"],
                "variants": {
                    name: {
                        "R1_pct": result["R1_pct"],
                        "R1_count": result["R1_count"],
                        "frozen_R1": result["frozen_R1"],
                    }
                    for name, result in variants.items()
                },
            }
        )
        bridge_cases.append(
            {
                "case": case["case"],
                "case_interpretation": case["status"],
                "variants": {
                    name: {"R2_pct": result["R2_pct"], "R2_count": result["R2_count"]}
                    for name, result in variants.items()
                },
            }
        )
        repair_cases.append(
            {
                "case": case["case"],
                "case_interpretation": case["status"],
                "variants": {
                    name: {
                        "D_max": result["D_max"],
                        "D_repaired": result["D_repaired"],
                        "frozen_D": result["frozen_D"],
                    }
                    for name, result in variants.items()
                },
            }
        )

    return {
        "sofrs_version": "1.0",
        "artifact_role": "validator_fixture",
        "protocol_admissible": False,
        "fixture_scope": "five distinct constructed boundary systems",
        "report_id": "failure_cases",
        "system": "SOF diagnostic applicability boundary suite",
        "claim_status": "boundary",
        "claim_note": "five non-exhaustive failure and degeneracy controls",
        "sectorization": {
            "origin": "case-specific constructed finite sectors",
            "cases": [case["case"] for case in cases],
            "realization_status": "constructed boundary controls",
        },
        "observable_family": {
            "case_specific": "random, commuting, aligned, or deliberately mismatched finite observables"
        },
        "support_matrix": {"kind": "case-level R1 summaries", "cases": support_cases},
        "bridge_matrix": {"kind": "case-level R2 summaries", "cases": bridge_cases},
        "repair_matrix": {"kind": "case-level depth summaries", "cases": repair_cases},
        "wall_record": {
            "status": "not_applicable",
            "reason": "the suite audits static applicability boundaries rather than deformation paths",
        },
        "failure_modes": [
            {
                "case": case["case"],
                "case_interpretation": case["status"],
                "reason": reasons[case["case"]],
            }
            for case in cases
        ],
    }


def write_sofreport(report: dict) -> Path:
    path = Path(__file__).resolve().parent / "results" / "failure_cases.fixture.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def main() -> None:
    print("=" * 76)
    print("  Paper XII: SOF Diagnostic Failure Cases")
    print("=" * 76)
    print("  Envelope-valid multi-system fixture; excluded from protocol admission.")
    print()
    cases = run()
    print_applicability_table()
    print(f"SOFRS fixture: {write_sofreport(sofreport(cases))}")
    print("Done.")


if __name__ == "__main__":
    main()
