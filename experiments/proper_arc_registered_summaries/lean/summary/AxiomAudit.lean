import summary.SummaryEquivalence
import AxiomAudit

open Lean Elab Command

set_option Elab.async false

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#dependent_summary_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.Chains.summaryOriginIndex_spec, `ProperArc.Chains.summaryCode_spec,
      `ProperArc.Chains.decodeSummary_origin, `ProperArc.Chains.decodeSummary_chain,
      `ProperArc.Chains.decodeSummary_placed, `ProperArc.Chains.decodeSummary_encodeSummary,
      `ProperArc.Chains.encodeSummary_decodeSummary, `ProperArc.Chains.actualRegisteredSummariesEquivParams,
      `ProperArc.Chains.actualSummary_unique_params, `ProperArc.Chains.decodeSummary_same_word,
      `ProperArc.Chains.decodeSummary_injective, `ProperArc.Chains.codePlacementFibreEquiv,
      `ProperArc.Chains.actual_chain_decode_encode, `ProperArc.actual_registered_origin_unique,
      `ProperArc.run_originWord]
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
    for name in #[`ProperArc.Chains.ActualRegisteredSummaries, `ProperArc.Chains.SummaryParams,
        `ProperArc.Chains.decodeSummary, `ProperArc.Chains.encodeSummary,
        `ProperArc.Chains.summaryPlacementInFibre] do
      let info ← getConstInfo name
      let some value := info.value? | throwError "Missing summary definition {name}"
      let text ← Meta.ppExpr value
      definitions := definitions.push (name.toString,toJson text.pretty)
    return Json.mkObj [("schema",toJson "proper_arc_dependent_summary_audit.v1"),
      ("scope_status",toJson "ACTUAL_DEPENDENT_SUMMARY_EQUIVALENCE"),
      ("targets",toJson targets),("nodes",toJson nodes),("definitions",Json.mkObj definitions.toList)]
  logInfo m!"DEPENDENT_SUMMARY_JSON\n{report.compress}"

#dependent_summary_audit

#print axioms ProperArc.Chains.execution_ext_fields
#print axioms ProperArc.Chains.actualSummary_reachable
#print axioms ProperArc.Chains.actualSummary_registered
#print axioms ProperArc.Chains.summary_origin_unique
#print axioms ProperArc.Chains.summaryOriginIndex_spec
#print axioms ProperArc.Chains.summaryCode_spec
#print axioms ProperArc.Chains.decodeSummary_origin
#print axioms ProperArc.Chains.decodeSummary_chain
#print axioms ProperArc.Chains.decodeSummary_placed
#print axioms ProperArc.Chains.encodeSummary_origin
#print axioms ProperArc.Chains.encodeSummary_code
#print axioms ProperArc.Chains.encodeSummary_placement_readback
#print axioms ProperArc.Chains.decodeSummary_encodeSummary
#print axioms ProperArc.Chains.decodeSummary_injective
#print axioms ProperArc.Chains.encodeSummary_decodeSummary
#print axioms ProperArc.Chains.actualRegisteredSummariesEquivParams_apply
#print axioms ProperArc.Chains.actualRegisteredSummariesEquivParams_symm
#print axioms ProperArc.Chains.actualSummary_unique_params
#print axioms ProperArc.Chains.decodeSummary_same_word
#print axioms ProperArc.Chains.ActualRegisteredSummaries
#print axioms ProperArc.Chains.SummaryParams
#print axioms ProperArc.Chains.summaryOriginIndex
#print axioms ProperArc.Chains.summaryPlacementInFibre
#print axioms ProperArc.Chains.decodeSummary
#print axioms ProperArc.Chains.encodeSummary
#print axioms ProperArc.Chains.actualRegisteredSummariesEquivParams
#print axioms ProperArc.Chains.codePlacementFibreEquiv
#print axioms ProperArc.Chains.actual_chain_decode_encode
#print axioms ProperArc.actual_registered_origin_unique
#print axioms ProperArc.run_originWord
