"""Paper XIII legitimate-transformation controls.

These controls compare valid before/after configurations. The raw alignment
signature records what changed; a declared transformation contract determines
whether any observed change is unexpected. A nonzero signature is therefore
not interpreted as a failure by itself.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import compiler_ir_sof as compiler
import gridworld_reference_sof as gridworld
import traffic_intersection_sof as traffic
from report_contract import build_sofaudit, build_sofreport, write_artifact


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "archive" / "results"
TOL = 1e-8


def _edge_set(matrices: dict[str, np.ndarray]) -> set[tuple[str, int, int]]:
    edges: set[tuple[str, int, int]] = set()
    for observable, matrix in matrices.items():
        for target, source in np.argwhere(np.abs(matrix) > TOL):
            if source != target:
                edges.add((observable, int(source), int(target)))
    return edges


def _edge_records(edges: set[tuple[str, int, int]], labels: list[str]) -> list[dict]:
    return [
        {"observable": observable, "source": labels[source], "target": labels[target]}
        for observable, source, target in sorted(edges)
    ]


def _response_matrices(module, sectors, matrices: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {
        name: module.action_response_matrix(sectors, module.skew(matrix))
        for name, matrix in matrices.items()
    }


def _zero_constraint_residual(violations: list[dict]) -> dict:
    return {"violations": violations, "count": len(violations)}


def _raw_summary(diff: dict) -> dict:
    response = diff.get("action_response_failure") or {"total_large_deltas": 0}
    return {
        "support_mismatch": int(diff["support_mismatch"]["total_mismatch"]),
        "bridge_word_mismatch": int(diff["bridge_word_mismatch"]["total_mismatch"]),
        "bridge_lie_mismatch": int(diff["bridge_lie_mismatch"]["total_mismatch"]),
        "depth_distortion": int(diff["depth_distortion"]["total_mismatch"]),
        "action_response_changes": int(response["total_large_deltas"]),
    }


def _write_report(
    *,
    report_id: str,
    system: str,
    sectorization: dict,
    observable_family: dict,
    audit: dict,
    configuration: dict,
) -> None:
    write_artifact(
        build_sofreport(
            report_id=report_id,
            system=system,
            sectorization=sectorization,
            observable_family=observable_family,
            audit=audit,
            claim_note="controlled legitimate-transformation configuration",
            failure_modes=[
                "controlled finite configuration",
                "legitimacy is relative to the declared transformation contract",
            ],
            extra={"configuration": configuration},
        ),
        RESULTS / f"{report_id}.sofreport",
    )


def compiler_o0_to_o2() -> dict:
    sectors = compiler.block_sectors()
    before_model = compiler.CompilerIR(
        cfg_edges=list(compiler.CFG_EDGES),
        defuse_edges=list(compiler.DEFUSE_EDGES),
    )
    after_model = compiler.CompilerIR(
        cfg_edges=[
            (compiler.B0, compiler.B1),
            (compiler.B1, compiler.B2),
            (compiler.B2, compiler.B4),
        ],
        defuse_edges=[
            (compiler.B0, compiler.B1),
            (compiler.B1, compiler.B2),
            (compiler.B1, compiler.B4),
            (compiler.B2, compiler.B4),
        ],
    )
    before_matrices = before_model.action_matrices()
    after_matrices = after_model.action_matrices()
    before_observables, _ = compiler.build_observables(before_matrices)
    after_observables, _ = compiler.build_observables(after_matrices)
    before_audit = compiler.full_audit(sectors, before_observables)
    after_audit = compiler.full_audit(sectors, after_observables)
    diff = compiler.full_diff(
        before_audit,
        after_audit,
        resp_ref=_response_matrices(compiler, sectors, before_matrices),
        resp_lrn=_response_matrices(compiler, sectors, after_matrices),
    )

    before_edges = _edge_set(before_matrices)
    after_edges = _edge_set(after_matrices)
    added = after_edges - before_edges
    removed = before_edges - after_edges
    allowed_added = {("X_defuse", compiler.B2, compiler.B4)}
    allowed_removed = {
        ("X_cfg", compiler.B1, compiler.B3),
        ("X_cfg", compiler.B3, compiler.B4),
        ("X_defuse", compiler.B3, compiler.B4),
    }
    residuals = []
    for edge in sorted(added - allowed_added):
        residuals.append({"kind": "unexpected_added_edge", "edge": edge})
    for edge in sorted(removed - allowed_removed):
        residuals.append({"kind": "unexpected_removed_edge", "edge": edge})
    for observable, source, target in after_edges:
        if source == compiler.B3 or target == compiler.B3:
            residuals.append({
                "kind": "retired_sector_still_active",
                "edge": (observable, source, target),
            })
    diff["constraint_violations"] = _zero_constraint_residual(residuals)

    contract = {
        "contract_id": "compiler-dead-branch-elimination-v1",
        "intent": "remove the declared dead side block while preserving the main path",
        "allowed_changes": {
            "added_edges": _edge_records(allowed_added, compiler.LABELS),
            "removed_edges": _edge_records(allowed_removed, compiler.LABELS),
        },
        "preserved_invariants": [
            "observable labels X_cfg and X_defuse",
            "entry and exit block identity",
            "main CFG path B0->B1->B2->B4",
        ],
        "required_postconditions": [
            "B3 has no off-diagonal CFG or def-use incidence",
            "B2->B4 carries the replacement def-use path",
        ],
        "boundary": "controlled structural contract, not a compiler semantic-equivalence proof",
    }
    evaluation = {
        "status": "conforming" if not residuals else "nonconforming",
        "residual_violation_count": len(residuals),
        "residual_violations": residuals,
        "observed_added_edges": _edge_records(added, compiler.LABELS),
        "observed_removed_edges": _edge_records(removed, compiler.LABELS),
        "raw_change_summary": _raw_summary(diff),
    }

    sectorization = {
        "origin": "one-hot basic-block sectors in a shared five-block ambient space",
        "blocks": compiler.LABELS,
        "sector_count": compiler.N_BLOCKS,
        "strict_sof_realization": True,
    }
    observable_family = {
        "observables": ["X_cfg", "X_defuse"],
        "generator_type": "skew-symmetrised directed edge matrices",
    }
    _write_report(
        report_id="compiler_o0_before",
        system="Compiler IR before legitimate optimization",
        sectorization=sectorization,
        observable_family=observable_family,
        audit=before_audit,
        configuration={"stage": "O0-like", "active_blocks": compiler.LABELS},
    )
    _write_report(
        report_id="compiler_o2_after",
        system="Compiler IR after legitimate optimization",
        sectorization=sectorization,
        observable_family=observable_family,
        audit=after_audit,
        configuration={
            "stage": "O2-like",
            "active_blocks": [label for index, label in enumerate(compiler.LABELS) if index != compiler.B3],
            "retired_ambient_sector": compiler.LABELS[compiler.B3],
        },
    )
    artifact = build_sofaudit(
        audit_id="before_after_compiler_o0_o2",
        system="Compiler IR legitimate transformation alignment",
        failure_mode="legitimate_transformation_control",
        reference_report_id="compiler_o0_before",
        reference_label="O0-like before transformation",
        candidate_report_id="compiler_o2_after",
        candidate_label="O2-like transformed target",
        diff=diff,
        normalization={
            "ordered_pairs": 20,
            "action_opportunities": 40,
            "constraint_opportunities": len(allowed_added) + len(allowed_removed),
            "path_samples": 0,
        },
        alignment={
            "sector_alignment": {
                "kind": "common_ambient_with_retired_target_sector",
                "mapping": {label: label for label in compiler.LABELS},
                "retired_target_sectors": [compiler.LABELS[compiler.B3]],
            },
            "observable_alignment": {
                "kind": "identity_by_semantic_label",
                "mapping": {"X_cfg": "X_cfg", "X_defuse": "X_defuse"},
            },
        },
        claim_note="controlled legitimate-transformation alignment; nonzero change is not a failure",
        failure_modes=[
            "legitimacy is relative to the declared transformation contract",
            "the controlled IR does not establish semantic compiler correctness",
        ],
        extra={
            "comparison_role": "legitimate_transformation_control",
            "transformation_contract": contract,
            "contract_evaluation": evaluation,
        },
    )
    write_artifact(artifact, RESULTS / "before_after_compiler.sofaudit")
    return artifact


def traffic_retiming() -> dict:
    sectors = traffic.sector_list()
    before_model = traffic.TrafficGrid(rho=0.5)
    after_model = traffic.TrafficGrid(rho=2.0)
    before_matrices = before_model.action_matrices()
    after_matrices = after_model.action_matrices()
    before_observables, _ = traffic.build_observables(before_matrices)
    after_observables, _ = traffic.build_observables(after_matrices)
    before_audit = traffic.full_audit(sectors, before_observables)
    after_audit = traffic.full_audit(sectors, after_observables)
    diff = traffic.full_diff(
        before_audit,
        after_audit,
        resp_ref=_response_matrices(traffic, sectors, before_matrices),
        resp_lrn=_response_matrices(traffic, sectors, after_matrices),
    )

    residuals = []
    for key in ("support_mismatch", "bridge_word_mismatch", "bridge_lie_mismatch"):
        if diff[key]["total_mismatch"]:
            residuals.append({"kind": "topology_changed", "channel": key})
    if diff["depth_distortion"]["total_mismatch"]:
        residuals.append({"kind": "depth_changed"})
    response_count = diff["action_response_failure"]["total_large_deltas"]
    if response_count == 0:
        residuals.append({"kind": "declared_retiming_not_observable"})
    diff["constraint_violations"] = _zero_constraint_residual(residuals)

    contract = {
        "contract_id": "traffic-phase-retiming-v1",
        "intent": "change the phase-weight ratio from rho=0.5 to rho=2.0",
        "allowed_changes": ["phase_A and phase_B response magnitudes"],
        "preserved_invariants": [
            "intersection sectors",
            "phase labels",
            "direct support, bridges, and finite-depth accessibility",
        ],
        "required_postconditions": ["phase_A response exceeds phase_B response after retiming"],
        "boundary": "controlled signal model, not a traffic-engineering recommendation",
    }
    evaluation = {
        "status": "conforming" if not residuals else "nonconforming",
        "residual_violation_count": len(residuals),
        "residual_violations": residuals,
        "raw_change_summary": _raw_summary(diff),
        "parameter_change": {"rho_before": 0.5, "rho_after": 2.0},
    }

    sectorization = {
        "origin": "one-hot intersection-node sectors",
        "labels": traffic.LABELS,
        "sector_count": traffic.N_SECTORS,
        "strict_sof_realization": True,
    }
    observable_family = {
        "observables": ["phase_A", "phase_B"],
        "generator_type": "skew-symmetrised directed phase matrices",
    }
    _write_report(
        report_id="traffic_rho05_before",
        system="Traffic signal before legitimate retiming",
        sectorization=sectorization,
        observable_family=observable_family,
        audit=before_audit,
        configuration={"rho": 0.5, "response_order": "phase_A < phase_B"},
    )
    _write_report(
        report_id="traffic_rho20_after",
        system="Traffic signal after legitimate retiming",
        sectorization=sectorization,
        observable_family=observable_family,
        audit=after_audit,
        configuration={"rho": 2.0, "response_order": "phase_A > phase_B"},
    )
    artifact = build_sofaudit(
        audit_id="before_after_traffic_retiming",
        system="Traffic legitimate retiming alignment",
        failure_mode="legitimate_transformation_control",
        reference_report_id="traffic_rho05_before",
        reference_label="rho=0.5 before retiming",
        candidate_report_id="traffic_rho20_after",
        candidate_label="rho=2.0 transformed target",
        diff=diff,
        normalization={
            "ordered_pairs": 12,
            "action_opportunities": 24,
            "constraint_opportunities": 4,
            "path_samples": 0,
        },
        alignment={
            "sector_alignment": {"kind": "identity", "labels": traffic.LABELS},
            "observable_alignment": {
                "kind": "identity_by_semantic_label",
                "mapping": {"phase_A": "phase_A", "phase_B": "phase_B"},
            },
        },
        claim_note="controlled legitimate retiming; response change with invariant topology",
        failure_modes=[
            "legitimacy is relative to the declared transformation contract",
            "finite rho values do not sample the rho->0 or rho->infinity limit walls",
        ],
        extra={
            "comparison_role": "legitimate_transformation_control",
            "transformation_contract": contract,
            "contract_evaluation": evaluation,
        },
    )
    write_artifact(artifact, RESULTS / "before_after_traffic.sofaudit")
    return artifact


def gridworld_obstacle_relocation() -> dict:
    sectors = gridworld.cell_sectors()
    before_obstacle = (2, 2)
    after_obstacle = (0, 0)
    before_model = gridworld.GridWorld(obstacles=[before_obstacle])
    after_model = gridworld.GridWorld(obstacles=[after_obstacle])
    before_matrices = before_model.action_matrices()
    after_matrices = after_model.action_matrices()
    before_observables, _ = gridworld.build_observables(before_matrices)
    after_observables, _ = gridworld.build_observables(after_matrices)
    before_audit = gridworld.full_audit(sectors, before_observables)
    after_audit = gridworld.full_audit(sectors, after_observables)
    before_response = gridworld.action_response_matrices(
        sectors, {name: gridworld.skew(matrix) for name, matrix in before_matrices.items()}
    )
    after_response = gridworld.action_response_matrices(
        sectors, {name: gridworld.skew(matrix) for name, matrix in after_matrices.items()}
    )
    diff = gridworld.full_diff(
        before_audit,
        after_audit,
        resp_ref=before_response,
        resp_learned=after_response,
    )

    before_edges = _edge_set(before_matrices)
    after_edges = _edge_set(after_matrices)
    changed_edges = before_edges ^ after_edges
    affected = {
        before_model.cell_index(*before_obstacle),
        after_model.cell_index(*after_obstacle),
    }
    unexpected = [
        edge for edge in sorted(changed_edges)
        if edge[1] not in affected and edge[2] not in affected
    ]
    residuals = [
        {"kind": "nonlocal_transition_change", "edge": edge}
        for edge in unexpected
    ]
    diff["constraint_violations"] = _zero_constraint_residual(residuals)

    labels = [f"cell({row},{col})" for row in range(5) for col in range(5)]
    contract = {
        "contract_id": "gridworld-obstacle-relocation-v1",
        "intent": "relocate the single absorbing obstacle from (2,2) to (0,0)",
        "allowed_changes": [
            "transitions incident to the old obstacle sector",
            "transitions incident to the new obstacle sector",
        ],
        "preserved_invariants": [
            "5x5 cell sectorization",
            "action labels N, S, E, W",
            "all transitions outside the old/new obstacle incidence neighborhoods",
        ],
        "required_postconditions": ["exactly one absorbing obstacle at (0,0)"],
        "boundary": "controlled reconfiguration, not a path-planning optimality claim",
    }
    evaluation = {
        "status": "conforming" if not residuals else "nonconforming",
        "residual_violation_count": len(residuals),
        "residual_violations": residuals,
        "observed_changed_transitions": _edge_records(changed_edges, labels),
        "raw_change_summary": _raw_summary(diff),
    }

    sectorization = {
        "origin": "one-hot 5x5 grid-cell sectors",
        "sector_count": gridworld.N_CELLS,
        "strict_sof_realization": True,
    }
    observable_family = {
        "observables": gridworld.ACTION_NAMES,
        "generator_type": "skew-symmetrised deterministic transition matrices",
    }
    _write_report(
        report_id="gridworld_obs22_before",
        system="GridWorld before legitimate obstacle relocation",
        sectorization=sectorization,
        observable_family=observable_family,
        audit=before_audit,
        configuration={"obstacles": [before_obstacle]},
    )
    _write_report(
        report_id="gridworld_obs00_after",
        system="GridWorld after legitimate obstacle relocation",
        sectorization=sectorization,
        observable_family=observable_family,
        audit=after_audit,
        configuration={"obstacles": [after_obstacle]},
    )
    artifact = build_sofaudit(
        audit_id="before_after_gridworld_obstacle",
        system="GridWorld legitimate obstacle-relocation alignment",
        failure_mode="legitimate_transformation_control",
        reference_report_id="gridworld_obs22_before",
        reference_label="obstacle=(2,2) before relocation",
        candidate_report_id="gridworld_obs00_after",
        candidate_label="obstacle=(0,0) transformed target",
        diff=diff,
        normalization={
            "ordered_pairs": 600,
            "action_opportunities": 2400,
            "constraint_opportunities": len(changed_edges),
            "path_samples": 1,
        },
        alignment={
            "sector_alignment": {"kind": "identity", "basis": "fixed 5x5 cell coordinates"},
            "observable_alignment": {
                "kind": "identity_by_semantic_label",
                "mapping": {name: name for name in gridworld.ACTION_NAMES},
            },
        },
        claim_note="controlled legitimate reconfiguration; structural change with zero contract residual",
        failure_modes=[
            "legitimacy is relative to the declared transformation contract",
            "single before/after comparison is not a sampled wall-evolution law",
        ],
        extra={
            "comparison_role": "legitimate_transformation_control",
            "transformation_contract": contract,
            "contract_evaluation": evaluation,
        },
    )
    write_artifact(artifact, RESULTS / "before_after_gridworld.sofaudit")
    return artifact


def run() -> dict[str, dict]:
    print("=" * 76)
    print("  Paper XIII: Legitimate Transformation Alignments")
    print("=" * 76)
    print("  Raw signature = what changed; contract residual = what changed unexpectedly.")

    artifacts = {
        "compiler": compiler_o0_to_o2(),
        "traffic": traffic_retiming(),
        "gridworld": gridworld_obstacle_relocation(),
    }

    assert artifacts["compiler"]["signature"]["support_mismatch"]["total_mismatch"] > 0
    assert artifacts["traffic"]["signature"]["support_mismatch"]["total_mismatch"] == 0
    assert artifacts["traffic"]["signature"]["action_response_failure"]["total_large_deltas"] > 0
    assert artifacts["gridworld"]["signature"]["support_mismatch"]["total_mismatch"] > 0
    assert all(
        artifact["contract_evaluation"]["residual_violation_count"] == 0
        for artifact in artifacts.values()
    )

    print()
    print(f"  {'Case':<12} {'Supp':>6} {'BrW':>6} {'BrL':>6} {'Depth':>6} {'Resp':>6} {'Residual':>9}")
    for name, artifact in artifacts.items():
        summary = artifact["contract_evaluation"]["raw_change_summary"]
        print(
            f"  {name:<12} {summary['support_mismatch']:>6d} "
            f"{summary['bridge_word_mismatch']:>6d} "
            f"{summary['bridge_lie_mismatch']:>6d} "
            f"{summary['depth_distortion']:>6d} "
            f"{summary['action_response_changes']:>6d} "
            f"{artifact['contract_evaluation']['residual_violation_count']:>9d}"
        )
    print(f"\n  Wrote 6 .sofreport and 3 .sofaudit artifacts to {RESULTS}")
    return artifacts


if __name__ == "__main__":
    run()
