"""Validate the exact partial Lean source package and replay its declarations."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "formalization-manifest.v1.json"
AUDIT = "RegisteredAbsorptionChains/AxiomAudit.lean"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def replay(lake: str, *args: str) -> str:
    env = dict(os.environ)
    env.pop("LEAN_PATH", None)
    result = subprocess.run(
        [lake, *args], cwd=ROOT, env=env, text=True, encoding="utf-8",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    require(result.returncode == 0, f"{' '.join(args)} failed:\n{result.stdout}")
    return result.stdout


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(
        manifest.get("status") == "COMPILED_LATER_PARTIAL_FORMALIZATION",
        "partial formalization status changed",
    )
    declared = manifest.get("source_sha256")
    require(isinstance(declared, dict) and bool(declared), "missing source digests")
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and ".lake" not in path.relative_to(ROOT).parts
        and "__pycache__" not in path.relative_to(ROOT).parts
        and path.name != MANIFEST.name
    }
    require(actual == set(declared), f"source inventory drift: {sorted(actual ^ set(declared))}")
    for relative, expected in declared.items():
        require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
                f"invalid digest for {relative}")
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        require(digest == expected, f"source byte drift: {relative}")

    lake = os.environ.get("RIME_LAKE_EXE", "lake")
    replay(lake, "build")
    audit = replay(lake, "env", "lean", AUDIT)
    names = {
        "card_chainSkeleton", "card_rankedCode", "card_lastAt",
        "card_rankFiberParams_paper", "card_fiberParams", "card_totalParams",
        "localWord_moves_into_hole", "transferHole_potential_drop",
        "balanceTransfers_correct", "run_localLetters_safe", "run_holeWalk_safe",
        "run_rotation", "crossNextBlock_correct", "crossNextBlock_preserves_records",
        "GapFrame.faithful", "GapFrame.cross_faithful", "crossNextBlock_from_gap",
        "realizeNetTransferZ", "finGaps_transfer", "realizeNetTransfer",
        "NamedCyclicPlacement.toGapFrame_decode",
        "exists_frame_of_named_cyclic_placement", "realizeBalancedGaps",
        "GapFrame.decode_phase", "realizeFrameTarget", "realizeNamedPlacementTarget",
        "fusionFree_localLetters", "crossNextBlock_fusionFree",
        "LegalNamedPlacement.forward_distances",
        "admit_same_oriented_block_cycle", "realize_same_oriented_block_cycle",
        "realize_same_single_block_cycle",
        "sourceDefectLift_monotone", "sourceDefectLift_periodic",
        "placementOfMap_defect", "SourceOrderLift.fiber_convex",
        "SourceOrderLift.adjacent_port_fibers", "reachable_source_ordered",
        "fusion_step_ordered_and_adjacent",
        "SourceOrderLift.same_residue_in_window",
        "SourceOrderLift.source_fiber_cyclic_arc",
        "sourceOrdered_blocks_are_cyclic_arcs",
        "sourceOrdered_block_key_offsets",
        "sourceOrdered_same_blocks_key_order",
        "occupiedBlockKey_injective",
        "canonicalLegalNamed_positive",
        "sourceOrdered_same_blocks_admit",
        "realize_source_ordered_same_blocks",
        "ValidFiberPlacement.cut_cover",
        "ValidFiberPlacement.blockFin_cover",
        "ValidFiberPlacement.toLegal_positive",
        "ValidFiberPlacement.same_cycle_with_source",
        "ValidFiberPlacement.realize_from_named_source",
        "rankCuts_strict",
        "ValidFiberPlacement.ofRankParams",
        "rankFiberParams_target_admit",
        "rankFiberParams_realize_from_named_source",
        "stepDefect_outside_records",
        "run_fusionFree_records",
        "run_prepared_outside_merge",
        "outside_parents_not_selected",
        "fusionPlacement_other_site",
        "realize_one_outside_merge",
        "realize_one_carrier_safe_outside_merge",
        "realize_one_outside_merge_retains_carrier",
        "OutsideAssemblySchedule.realize",
        "realize_rank_target_after_outside_schedule",
        "fullCarrierPlacement_injective", "card_fullCarrierPlacements",
        "placementOfMap_fullCarrier", "sourceOrdered_fullCarrier",
        "rotate_fullCarrierPlacement", "realize_full_carrier_rotation",
        "realize_reachable_fullCarrier_phases",
        "fullCarrierFixedRecords_eq_phases", "fullCarrierFixedRecords_card",
        "step_placementOfMap", "run_placementOfMap",
        "forwardMapRun_preserves_equal", "no_split_after_actual_word",
        "no_split_from_sourceOrdered", "no_split_from_reachable",
        "actual_word_refines", "no_word_to_nonrefining_target",
        "source_packet_subset_future", "source_packet_subset_target_block",
        "outside_packet_within_target_interval", "registration_clean",
        "clean_reachable_outside_singletons",
        "clean_same_named_blocks", "unique_named_block_site",
        "realize_prepared_clean_absorption", "clean_after_prepared_absorption",
        "realize_clean_absorption_step",
        "clean_partner_assembly_invariant",
        "partner_invariant_same_named_blocks",
        "partner_invariant_after_outside_merge",
        "realize_one_partner_assembly_stage",
        "partner_finished_shape",
        "checkpoint_step_records", "partner_shape_same_named_blocks",
        "checkpoint_special_sites", "checkpoint_step_clean",
        "realize_clean_checkpoint_from_schedule",
        "realize_clean_checkpoint_from_finished_partner",
        "realize_clean_singleton_checkpoint",
        "checkpoint_cost_ledger",
        "packedPosition_injective", "packedLegalNamed_positive",
        "packed_adjacent_ports", "packed_outside_ports_with_carrier",
        "gapPosition_injective", "gapLegalNamed_positive", "gap_ports",
        "packed_adjacent_partner_schedule", "packed_adjacent_partner_stage_exact",
        "realize_packed_adjacent_partner_stage",
        "packed_R_ports", "gap_L_ports",
        "realize_packed_R_checkpoint", "realize_gap_L_checkpoint",
        "merged_named_placed_at", "merged_named_only_sites",
        "merge_named_outside_positive", "merge_named_outside_actual",
        "merge_named_R_blocks", "merge_named_L_blocks",
        "OutsideAssemblySchedule.trans", "RPartnerPrefix.step",
        "RPartnerPrefix.assemble_named", "RPartnerPrefix.assemble",
        "LPartnerSuffix.step", "LPartnerSuffix.assemble_named",
        "LPartnerSuffix.assemble",
        "CheckpointSourceFrontier.remaining_plus_absorbed",
        "CheckpointSourceFrontier.mem_carrier_iff",
        "CheckpointSourceFrontier.not_mem_carrier_iff_remaining",
        "CheckpointSourceFrontier.partnerR_card",
        "CheckpointSourceFrontier.partnerL_card",
        "CheckpointSourceFrontier.partnerR_disjoint_carrier",
        "CheckpointSourceFrontier.partnerL_disjoint_carrier",
        "CheckpointSourceFrontier.carrier_nextR",
        "CheckpointSourceFrontier.carrier_nextL",
        "CheckpointSourceFrontier.remaining_splitR",
        "CheckpointSourceFrontier.remaining_splitL",
        "CheckpointSourceFrontier.checkpoint_gap",
        "CheckpointSourceFrontier.nextR_checkpoint",
        "CheckpointSourceFrontier.nextL_checkpoint",
        "CheckpointSourceFrontier.clean_placedBlocks",
        "CheckpointSourceFrontier.clean_block_count",
        "CheckpointSourceFrontier.clean_occupiedKeys",
        "CheckpointSourceFrontier.canonical_outside_key",
        "CheckpointSourceFrontier.canonical_outside_block",
        "canonical_named_carrier", "CheckpointNamedAlignment.admitR",
        "CheckpointSourceFrontier.exists_named_alignment",
        "CheckpointNamedAlignment.admitL", "CheckpointNamedAlignment.assembleR",
        "CheckpointNamedAlignment.assembleL",
        "CheckpointNamedAlignment.realizeR_checkpoint",
        "CheckpointNamedAlignment.realizeL_checkpoint",
        "CheckpointSourceFrontier.realizeR_checkpoint",
        "CheckpointSourceFrontier.realizeL_checkpoint",
        "decodeCodePrefix_absorbed", "realize_clean_code_prefix",
        "realize_clean_code",
        "realize_clean_code_actual_carrier",
        "CheckpointSourceFrontier.carrier_card",
        "CheckpointSourceFrontier.checkpointKey_R",
        "CheckpointSourceFrontier.checkpointKey_L",
        "decodeCodePrefix_keys", "codeKeysPrefix_mem_iff",
        "decodeChain_injective",
        "sourceOrdered_selected_packet_unique",
        "sourceOrdered_distinct_packets_disjoint",
        "sourceOrdered_selected_packet_step",
        "sourceOrdered_selected_packet_run",
        "actual_selected_partner_strict",
        "actual_selected_checkpoint_increases",
        "actual_selected_step_uses_carrier",
        "actual_unselected_carrier_defect",
        "actual_unselected_carrier_step",
        "recordedCarrierResult_append",
        "actual_registered_carrier_step",
        "actual_carrier_trace_step",
        "actual_carrier_trace_run",
        "actual_registered_carrier_from_seed",
        "selected_arc_complement_convex",
        "actual_selected_complement_convex",
        "nonempty_linear_set_eq_sourceInterval",
        "actual_selected_has_frontier",
        "actual_outside_packet_linear",
        "actual_right_partner_contains_lo",
        "actual_left_partner_contains_hi_pred",
        "linear_partner_from_left_endpoint",
        "linear_partner_from_right_endpoint",
        "frontier_partner_checkpoint_size",
        "actual_selected_fusion_frontier",
        "reachable_selected_fusion_frontier",
        "frontier_eq_of_carrier_eq_of_remaining",
        "decodeCodePrefix_congr", "decodeCodePrefix_skip",
        "decodeCodePrefix_insertCheckpoint",
        "actual_selected_step_extends_code",
        "actual_decoded_trace_preserved", "actual_decoded_trace_run",
        "actual_chain_in_decode_range", "actual_chain_unique_code",
        "codeEquivReachableSelectedChain",
        "CountedOutsideSchedule.toSchedule",
        "CountedOutsideSchedule.realize",
        "CountedOutsideSchedule.trans",
        "packed_adjacent_partner_schedule_count",
        "oneCut_assemble_named", "oneCut_realize_target",
        "targetCutBoundaryPlan", "CutNamed.boundaries_merge",
        "CutNamed.merge_actual", "CutNamed.blocks_eq_target",
        "CutBoundaryPlan.realize_named", "allCut_assemble_named",
        "allCut_realize_target", "code_fiber_target_reachable",
        "code_rank_params_reachable",
        "actual_fiber_normal_form",
        "full_carrier_code_fiber_phases",
        "ValidFiberPlacement.of_toRankParams",
        "ValidFiberPlacement.to_ofRankParams",
        "ValidFiberPlacement.target_injective_fixed",
        "rank_params_target_unique",
        "actual_fiber_rank_normal_form",
        "actualFixedChainPlacementEquiv",
        "SourceOrderLift.no_reverse_registration",
        "sourceOrdered_registration_parents",
        "step_origin_standard_or_none", "run_origin_standard_or_none",
        "actual_registered_origin_unique",
        "fullCarrierFixedChainPlacementEquiv",
        "codeFiberPlacementEquiv", "codePlacementEquivActualSummaries",
        "actualSummaryCodeFiberEquiv",
        "positiveRankFiberParams_rank_le", "positiveRankFiberParamsEquiv",
        "finiteCodeFiberEquiv",
        "card_actualFixedChainPlacements_positive",
        "card_actualFixedChainPlacements_full",
        "actualSummaryFiniteParamsEquiv",
        "card_actualRegisteredSummaries_code_sum",
        "codeLastCheckpoint_weighted_sum",
        "lastCodeCheckpoint_eq_codeLastCheckpoint",
        "decodeCode_absorbed_eq_codeLastCheckpoint",
        "decodeCode_remaining_eq_lastCheckpoint",
        "card_actualFixedChainPlacements_lastCheckpoint",
        "card_actualRegisteredSummaries_closed",
        "two_registration_origins_distinct",
        "actualRegisteredSummaries_two_complete",
        "actualRegisteredSummariesTwoEquiv",
        "actualRegisteredSummariesTwoProductEquiv",
        "actualRegisteredSummariesTwoProduct_origin",
        "actualRegisteredSummariesTwoProduct_phase",
        "card_actualRegisteredSummaries_two",
        "card_actualRegisteredSummaries_piecewise",
    }
    rows = re.findall(
        r"'RegisteredAbsorptionChains\.([A-Za-z0-9_.]+)' depends on axioms: \[([^]]*)\]",
        audit,
    )
    require({name for name, _ in rows} == names and len(rows) == len(names),
            "axiom audit declaration set drift")
    for name, payload in rows:
        axioms = {item.strip() for item in payload.split(",") if item.strip()}
        require(axioms <= ALLOWED_AXIOMS, f"unexpected axioms in {name}: {axioms}")
    print(f"PASS partial Lean package: {len(declared)} bound files; {len(rows)} axiom audits")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL partial Lean package: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
