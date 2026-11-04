import refinements.ChainLength
import refinements.RankFibre
import AxiomAudit

open Lean Elab Command

set_option Elab.async false
set_option pp.funBinderTypes true
set_option pp.piBinderTypes true

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#combinatorial_refinement_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.Chains.coloredCheckpointsEquivCodes,
      `ProperArc.Chains.card_codes_by_support, `ProperArc.Chains.decodeChain_length,
      `ProperArc.Chains.actualChainsLengthEquivCodes, `ProperArc.Chains.card_actualSelectedChains_length,
      `ProperArc.Chains.positiveFiberTarget_rank, `ProperArc.Chains.rankParamsEquivSlice,
      `ProperArc.Chains.actualRankCodePlacementsEquiv, `ProperArc.Chains.card_actualRankCodePlacements,
      `ProperArc.Chains.actual_full_carrier_rank, `ProperArc.Chains.actualFullRankCodePlacementsEquiv,
      `ProperArc.Chains.card_actualFullRankCodePlacements,
      `ProperArc.Chains.actualSelectedChainsEquivCode, `ProperArc.Chains.positivePlacementFibreEquiv,
      `ProperArc.Chains.fullPlacementFibreEquiv, `ProperArc.Chains.codeSnocEquiv]
    let mut all : NameSet := {}
    let mut targets : Array Json := #[]
    for root in roots do
      let dependencies ← ProperArcAudit.closure env root
      for name in dependencies do all := all.insert name
      let info ← getConstInfo root
      let axioms ← collectAxioms root
      let signature ← Meta.ppExpr info.type
      targets := targets.push (Json.mkObj [
        ("name",toJson root.toString),("signature",toJson signature.pretty),
        ("type_constants",ProperArcAudit.names (info.type.getUsedConstantsAsSet.toArray.qsort Name.lt)),
        ("axioms",ProperArcAudit.names axioms),("dependencies",ProperArcAudit.names dependencies)])
    let mut nodes : Array Json := #[]
    for name in all.toArray.qsort Name.lt do
      let info ← getConstInfo name
      nodes := nodes.push (Json.mkObj [
        ("name",toJson name.toString),("kind",toJson (ProperArcAudit.kind info)),
        ("direct_dependencies",ProperArcAudit.names (info.getUsedConstantsAsSet.toArray.qsort Name.lt))])
    let mut definitions : Array (String × Json) := #[]
    for name in #[`ProperArc.Chains.ActualSelectedChains, `ProperArc.Chains.ActualCodePlacements,
        `ProperArc.Chains.ActualRankCodePlacements, `ProperArc.Chains.ColoredCheckpoints] do
      let info ← getConstInfo name
      let some value := info.value? | throwError "Missing refinement domain {name}"
      let text ← Meta.ppExpr value
      definitions := definitions.push (name.toString,toJson text.pretty)
    return Json.mkObj [("schema",toJson "proper_arc_combinatorial_refinements_audit.v1"),
      ("scope_status",toJson "ACTUAL_CHAIN_LENGTH_AND_PLACEMENT_RANK_COUNTS"),
      ("targets",toJson targets),("nodes",toJson nodes),("definitions",Json.mkObj definitions.toList)]
  logInfo m!"COMBINATORIAL_REFINEMENTS_JSON\n{report.compress}"

#combinatorial_refinement_audit

#print axioms ProperArc.Chains.support_codeOfColors
#print axioms ProperArc.Chains.codeOfColors_readback
#print axioms ProperArc.Chains.card_codes_by_support
#print axioms ProperArc.Chains.support_card_snoc
#print axioms ProperArc.Chains.keys_snoc_prefix
#print axioms ProperArc.Chains.keys_length_support
#print axioms ProperArc.Chains.decodeChain_length
#print axioms ProperArc.Chains.card_actualSelectedChains_length
#print axioms ProperArc.Chains.placedBlocks_renamePlacement
#print axioms ProperArc.Chains.renamePlacement_rank
#print axioms ProperArc.Chains.positiveFiberTarget_rank
#print axioms ProperArc.Chains.card_actualRankCodePlacements
#print axioms ProperArc.Chains.placedBlocks_fullCarrier
#print axioms ProperArc.Chains.actual_full_carrier_rank
#print axioms ProperArc.Chains.card_actualFullRankCodePlacements
#print axioms ProperArc.Chains.ColoredCheckpoints
#print axioms ProperArc.Chains.codeOfColors
#print axioms ProperArc.Chains.coloredCheckpointsEquivCodes
#print axioms ProperArc.Chains.actualChainsLengthEquivCodes
#print axioms ProperArc.Chains.ActualRankCodePlacements
#print axioms ProperArc.Chains.rankIndexSliceEquiv
#print axioms ProperArc.Chains.rankParamsEquivSlice
#print axioms ProperArc.Chains.actualRankCodePlacementsEquiv
#print axioms ProperArc.Chains.actualFullRankCodePlacementsEquiv
#print axioms ProperArc.Chains.actualSelectedChainsEquivCode
#print axioms ProperArc.Chains.positivePlacementFibreEquiv
#print axioms ProperArc.Chains.fullPlacementFibreEquiv
#print axioms ProperArc.Chains.codeSnocEquiv
