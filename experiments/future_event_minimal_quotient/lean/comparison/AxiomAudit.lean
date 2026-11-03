import comparison.ObserverGrowth
import FutureEvent.MilestoneAudit

open Lean Elab Command

set_option Elab.async false

namespace ObserverComparisonAudit

def targets : Array Name := #[
  `ObserverComparison.summaryBracket_error,
  `ObserverComparison.tendsto_fullQuotient_normalized,
  `ObserverComparison.tendsto_full_div_future_normalized,
  `ObserverComparison.tendsto_full_div_future_atTop]

end ObserverComparisonAudit

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#observer_comparison_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let mut all : NameSet := {}
    let mut targets : Array Json := #[]
    for target in ObserverComparisonAudit.targets do
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
    return Json.mkObj [("schema", toJson "observer_comparison_dependency_audit.v1"),
      ("targets", toJson targets), ("nodes", toJson nodes)]
  logInfo m!"OBSERVER_COMPARISON_JSON\n{report.compress}"

#observer_comparison_audit

#print axioms ObserverComparison.weighted_choose_sum
#print axioms ObserverComparison.summaryBracket_truncated
#print axioms ObserverComparison.negative_binomial_hasSum
#print axioms ObserverComparison.summaryTail_identity
#print axioms ObserverComparison.summaryTail_nonneg
#print axioms ObserverComparison.summaryTail_le
#print axioms ObserverComparison.summaryBracket_error
#print axioms ObserverComparison.tendsto_summaryBracket_normalized
#print axioms ObserverComparison.fullCardReal_formula
#print axioms ObserverComparison.normalized_extra_bound
#print axioms ObserverComparison.tendsto_normalized_extra
#print axioms ObserverComparison.full_normalized_decomposition
#print axioms ObserverComparison.tendsto_fullQuotient_normalized
#print axioms ObserverComparison.observer_ratio_identity
#print axioms ObserverComparison.tendsto_full_div_future_normalized
#print axioms ObserverComparison.tendsto_full_div_future_atTop
