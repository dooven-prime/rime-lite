import fibres.PlacementEquivalence
import AxiomAudit

open Lean Elab Command

set_option Elab.async false

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#placement_fibre_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.Chains.outsideCount_eq, `ProperArc.Chains.actual_code_carrier,
      `ProperArc.Chains.actual_fiber_normal_form, `ProperArc.Chains.fiber_target_reachable,
      `ProperArc.Chains.positiveFiberTarget_injective, `ProperArc.Chains.actual_fiber_params,
      `ProperArc.Chains.positivePlacementFibreEquiv, `ProperArc.Chains.full_carrier_target_reachable,
      `ProperArc.Chains.fullPlacementFibreEquiv, `ProperArc.Chains.codePlacementFibreEquiv,
      `ProperArc.Chains.card_actualCodePlacements,
      `ProperArc.Chains.actualSelectedChainsEquivCode, `ProperArc.Chains.actual_chain_decode_encode,
      `ProperArc.Chains.realize_clean_code, `ProperArc.run_originWord]
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
        ("axioms",ProperArcAudit.names axioms),("dependencies",ProperArcAudit.names dependencies)])
    let mut nodes : Array Json := #[]
    for name in all.toArray.qsort Name.lt do
      let info ← getConstInfo name
      nodes := nodes.push (Json.mkObj [
        ("name",toJson name.toString),("kind",toJson (ProperArcAudit.kind info)),
        ("direct_dependencies",ProperArcAudit.names (info.getUsedConstantsAsSet.toArray.qsort Name.lt))])
    let mut definitions : Array (String × Json) := #[]
    for name in #[`ProperArc.Chains.ActualCodePlacements, `ProperArc.Chains.CodeFiberParams,
        `ProperArc.Chains.positiveFiberData] do
      let info ← getConstInfo name
      let some value := info.value? | throwError "Missing fibre definition {name}"
      let text ← Meta.ppExpr value
      definitions := definitions.push (name.toString,toJson text.pretty)
    return Json.mkObj [("schema",toJson "proper_arc_placement_fibre_audit.v1"),
      ("scope_status",toJson "ACTUAL_FIXED_ORIGIN_CHAIN_PLACEMENT_FIBRE"),
      ("targets",toJson targets),("nodes",toJson nodes),("definitions",Json.mkObj definitions.toList)]
  logInfo m!"PLACEMENT_FIBRE_JSON\n{report.compress}"

#placement_fibre_audit

#print axioms ProperArc.Chains.outsideCount_eq
#print axioms ProperArc.Chains.renamePlacement_injective
#print axioms ProperArc.Chains.canonical_code_carrier
#print axioms ProperArc.Chains.normalized_run
#print axioms ProperArc.Chains.normalized_code_carrier
#print axioms ProperArc.Chains.actual_code_carrier
#print axioms ProperArc.Chains.carrier_full_of_outside_zero
#print axioms ProperArc.Chains.ordered_fiber_naming
#print axioms ProperArc.Chains.ordered_fiber_normal_form
#print axioms ProperArc.Chains.actual_fiber_normal_form
#print axioms ProperArc.Chains.rank_params_outside_bound
#print axioms ProperArc.Chains.canonical_fiber_target_reachable
#print axioms ProperArc.Chains.fiber_target_reachable
#print axioms ProperArc.Chains.positiveFiberTarget_reachable
#print axioms ProperArc.Chains.decodedCarrier_full
#print axioms ProperArc.Chains.full_carrier_target_reachable
#print axioms ProperArc.Chains.positiveFiberTarget_injective
#print axioms ProperArc.Chains.actual_fiber_params
#print axioms ProperArc.Chains.positivePlacementFibreEquiv_val
#print axioms ProperArc.Chains.fullPlacementFibreEquiv_val
#print axioms ProperArc.Chains.card_actualCodePlacements
#print axioms ProperArc.Chains.ActualCodePlacements
#print axioms ProperArc.Chains.CodeFiberParams
#print axioms ProperArc.Chains.positiveFiberData
#print axioms ProperArc.Chains.positiveFiberTarget
#print axioms ProperArc.Chains.positivePlacementFibreEquiv
#print axioms ProperArc.Chains.fullPlacementFibreEquiv
#print axioms ProperArc.Chains.codePlacementFibreEquiv
#print axioms ProperArc.Chains.actualSelectedChainsEquivCode
#print axioms ProperArc.Chains.actual_chain_decode_encode
#print axioms ProperArc.Chains.realize_clean_code
#print axioms ProperArc.run_originWord
