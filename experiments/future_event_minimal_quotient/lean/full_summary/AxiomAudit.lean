import full_summary.CountBridge
import FutureEvent.MilestoneAudit

open Lean Elab Command

set_option Elab.async false

namespace FullSummaryAudit

def targets : Array Name := #[
  `FullSummary.event_to_summary_prefix_detection,
  `FullSummary.equivalent_iff_normalForm,
  `FullSummary.fullQuotientEquivSummaries,
  `FullSummary.card_fullQuotient_closed,
  `FullSummary.forgetToFuture_surjective]

end FullSummaryAudit

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#full_summary_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let mut all : NameSet := {}
    let mut targets : Array Json := #[]
    for target in FullSummaryAudit.targets do
      let names ← FutureEventMilestoneAudit.dependencyClosure env target
      for name in names do all := all.insert name
      let info ← getConstInfo target
      let axioms ← collectAxioms target
      let signature ← Meta.ppExpr info.type
      targets := targets.push (Json.mkObj [
        ("name", toJson target.toString), ("signature", toJson signature.pretty),
        ("axioms", FutureEventMilestoneAudit.nameArray axioms),
        ("dependencies", FutureEventMilestoneAudit.nameArray names)])
    let mut nodes : Array Json := #[]
    for name in all.toArray.qsort Name.lt do
      let info ← getConstInfo name
      nodes := nodes.push (Json.mkObj [
        ("name", toJson name.toString),
        ("kind", toJson (FutureEventMilestoneAudit.declarationKind info)),
        ("direct_dependencies", FutureEventMilestoneAudit.nameArray
          (info.getUsedConstantsAsSet.toArray.qsort Name.lt))])
    return Json.mkObj [("schema", toJson "full_summary_dependency_audit.v1"),
      ("targets", toJson targets), ("nodes", toJson nodes)]
  logInfo m!"FULL_SUMMARY_JSON\n{report.compress}"

#full_summary_audit

#print axioms FullSummary.permanently_unregistered_run
#print axioms FullSummary.permanently_unregistered_equivalent
#print axioms FullSummary.registerable_iff_of_equivalent
#print axioms FullSummary.equivalent_iff_normalForm
#print axioms FullSummary.registered_equivalent_iff_eq
#print axioms FullSummary.finite_fullQuotient
#print axioms FullSummary.card_fullQuotient_actual_counts
#print axioms FullSummary.card_fullQuotient_closed
#print axioms FullSummary.card_future_le_full
#print axioms FullSummary.spoiledSeed_generated
#print axioms FullSummary.spoiledSeed_null
#print axioms FullSummary.output_eq_none
#print axioms FullSummary.output_eq_some
#print axioms FullSummary.output_equal_cases
#print axioms FullSummary.output_origin
#print axioms FullSummary.unregistered_event_from_origin
#print axioms FullSummary.event_eq_of_adjacent_outputs
#print axioms FullSummary.events_eq_of_prefix_outputs
#print axioms FullSummary.event_to_summary_prefix_detection
#print axioms FullSummary.equivalent_refl
#print axioms FullSummary.equivalent_right_congruent
#print axioms FullSummary.equivalent_implies_future
#print axioms FullSummary.full_region_cases
#print axioms FullSummary.normalKey_of_permanent
#print axioms FullSummary.normalKey_of_registerable
#print axioms FullSummary.normalKey_of_registered
#print axioms FullSummary.normalKey_eq_iff
#print axioms FullSummary.normalKey_surjective
#print axioms FullSummary.quotientKey_mk
#print axioms FullSummary.quotientKey_injective
#print axioms FullSummary.quotientKey_surjective
#print axioms FullSummary.fullQuotientRun_mk
#print axioms FullSummary.fullQuotientRun_append
#print axioms FullSummary.forgetToFuture_surjective
#print axioms FullSummary.forgetToFuture_run
#print axioms FullSummary.fullQuotientEquivNormalForms
#print axioms FullSummary.registeredStatesEquivActualSummaries
#print axioms FullSummary.fullQuotientEquivSummaries
#print axioms FullSummary.forgetToFuture
