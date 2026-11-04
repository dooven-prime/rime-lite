import classification.OriginExhaustive
import AxiomAudit

open Lean Elab Command

set_option Elab.async false

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#origin_classification_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.extract_first_registration,
      `ProperArc.sourceOrdered_registration_cut,
      `ProperArc.actual_registered_origin_unique,
      `ProperArc.actual_registered_origin_unique_nat,
      `ProperArc.actualRegistrationOriginsEquivCuts,
      `ProperArc.card_actualRegistrationOrigins,
      `ProperArc.run_local_unregistered, `ProperArc.run_originWord, `ProperArc.boundary_clean]
    let mut all : NameSet := {}
    let mut targets : Array Json := #[]
    for root in roots do
      let dependencies ← ProperArcAudit.closure env root
      for name in dependencies do all := all.insert name
      let info ← getConstInfo root
      let axioms ← collectAxioms root
      let signature ← Meta.ppExpr info.type
      targets := targets.push (Json.mkObj [
        ("name", toJson root.toString), ("signature", toJson signature.pretty),
        ("axioms", ProperArcAudit.names axioms), ("dependencies", ProperArcAudit.names dependencies)])
    let mut nodes : Array Json := #[]
    for name in all.toArray.qsort Name.lt do
      let info ← getConstInfo name
      nodes := nodes.push (Json.mkObj [
        ("name", toJson name.toString), ("kind", toJson (ProperArcAudit.kind info)),
        ("direct_dependencies", ProperArcAudit.names (info.getUsedConstantsAsSet.toArray.qsort Name.lt))])
    let info ← getConstInfo `ProperArc.ActualRegistrationOrigins
    let some value := info.value? | throwError "Missing actual-origin definition body"
    let definition ← Meta.ppExpr value
    return Json.mkObj [("schema", toJson "proper_arc_origin_classification_audit.v1"),
      ("targets", toJson targets), ("nodes", toJson nodes),
      ("actual_origins_definition", toJson definition.pretty)]
  logInfo m!"ORIGIN_CLASSIFICATION_JSON\n{report.compress}"

#origin_classification_audit

#print axioms ProperArc.lift_position_int
#print axioms ProperArc.shiftSourceLift_position
#print axioms ProperArc.ordered_port_addresses
#print axioms ProperArc.sourceOrdered_parent_addresses
#print axioms ProperArc.sourceOrdered_registration_cut
#print axioms ProperArc.new_origin_step
#print axioms ProperArc.extract_first_registration
#print axioms ProperArc.sourceOrdered_ports_disjoint
#print axioms ProperArc.actual_first_registration
#print axioms ProperArc.actual_origin_in_cut_range
#print axioms ProperArc.actual_origin_cut_unique
#print axioms ProperArc.actual_registered_origin_unique
#print axioms ProperArc.actual_registered_origin_unique_nat
#print axioms ProperArc.originCutActual_injective
#print axioms ProperArc.originCutActual_surjective
#print axioms ProperArc.actualRegistrationOriginsEquivCuts_symm_val
#print axioms ProperArc.actualRegistrationOriginsEquivCuts_left_card
#print axioms ProperArc.finite_actualRegistrationOrigins
#print axioms ProperArc.card_actualRegistrationOrigins
#print axioms ProperArc.actualRegistrationOriginsEquivCuts
#print axioms ProperArc.run_local_unregistered
#print axioms ProperArc.run_originWord
#print axioms ProperArc.boundary_clean
