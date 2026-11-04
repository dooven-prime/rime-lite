import counting.SummaryCardinality
import AxiomAudit

open Lean Elab Command

set_option Elab.async false

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#summary_count_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.Chains.card_summary_sigma,
      `ProperArc.Chains.card_codes_by_last_checkpoint, `ProperArc.Chains.card_code_fibre,
      `ProperArc.Chains.card_code_fibre_full, `ProperArc.Chains.card_code_fibre_sum,
      `ProperArc.Chains.card_actual_registered_summaries,
      `ProperArc.Chains.card_actual_registered_summaries_short_complement,
      `ProperArc.Chains.sum_codes_by_last_checkpoint,
      `ProperArc.Chains.actualRegisteredSummariesEquivParams,
      `ProperArc.Chains.card_actualCodePlacements,
      `ProperArc.Chains.codePlacementFibreEquiv, `ProperArc.Chains.outsideCount_eq]
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
        `ProperArc.Chains.CodeFiberParams, `ProperArc.Chains.lastCheckpoint] do
      let info ← getConstInfo name
      let some value := info.value? | throwError "Missing counting input definition {name}"
      let text ← Meta.ppExpr value
      definitions := definitions.push (name.toString,toJson text.pretty)
    return Json.mkObj [("schema",toJson "proper_arc_summary_count_audit.v1"),
      ("scope_status",toJson "ACTUAL_REGISTERED_SUMMARY_COUNT"),
      ("targets",toJson targets),("nodes",toJson nodes),("definitions",Json.mkObj definitions.toList)]
  logInfo m!"SUMMARY_COUNT_JSON\n{report.compress}"

#summary_count_audit

#print axioms ProperArc.Chains.lastCheckpoint_le
#print axioms ProperArc.Chains.lastCheckpoint_snoc_prefix
#print axioms ProperArc.Chains.lastCheckpoint_snoc
#print axioms ProperArc.Chains.sum_codes_by_last_checkpoint
#print axioms ProperArc.Chains.card_codes_by_last_checkpoint
#print axioms ProperArc.Chains.card_summary_sigma
#print axioms ProperArc.Chains.card_code_fibre
#print axioms ProperArc.Chains.card_code_fibre_full
#print axioms ProperArc.Chains.sum_range_shift_Icc
#print axioms ProperArc.Chains.card_code_fibre_sum
#print axioms ProperArc.Chains.card_actual_registered_summaries
#print axioms ProperArc.Chains.card_actual_registered_summaries_short_complement
#print axioms ProperArc.Chains.codeSnocEquiv
#print axioms ProperArc.Chains.actualRegisteredSummariesEquivParams
#print axioms ProperArc.Chains.card_actualCodePlacements
#print axioms ProperArc.Chains.codePlacementFibreEquiv
#print axioms ProperArc.Chains.outsideCount_eq
