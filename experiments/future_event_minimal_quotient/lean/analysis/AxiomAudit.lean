import analysis.FutureCountAsymptotics
import FutureEvent.MilestoneAudit

open Lean Elab Command

set_option Elab.async false

namespace FutureEventAnalysisAudit

def targets : Array Name := #[
  `FutureEventAnalysis.tendsto_scaled_central_binomial,
  `FutureEventAnalysis.tendsto_normalized_remainder,
  `FutureEventAnalysis.tendsto_futureQuotient_normalized]

def declarations : Array Name := #[
  `FutureEventAnalysis.wallis_central_binomial,
  `FutureEventAnalysis.scaled_central_binomial_sqrt,
  `FutureEventAnalysis.tendsto_wallis_rational,
  `FutureEventAnalysis.tendsto_scaled_central_binomial,
  `FutureEventAnalysis.tendsto_remainder_polynomial,
  `FutureEventAnalysis.tendsto_normalized_remainder,
  `FutureEventAnalysis.futureCardReal_formula,
  `FutureEventAnalysis.tendsto_leading_coefficient,
  `FutureEventAnalysis.tendsto_sqrt_shift_ratio,
  `FutureEventAnalysis.tendsto_normalized_leading,
  `FutureEventAnalysis.normalized_count_decomposition,
  `FutureEventAnalysis.tendsto_futureQuotient_normalized]

end FutureEventAnalysisAudit

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#analytic_milestone_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let mut all : NameSet := {}
    let mut targets : Array Json := #[]
    for target in FutureEventAnalysisAudit.targets do
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
    return Json.mkObj [("schema", toJson "future_event_analytic_dependency_audit.v1"),
      ("targets", toJson targets), ("nodes", toJson nodes)]
  logInfo m!"ANALYTIC_MILESTONE_JSON\n{report.compress}"

#analytic_milestone_audit

#print axioms FutureEventAnalysis.wallis_central_binomial
#print axioms FutureEventAnalysis.scaled_central_binomial_sqrt
#print axioms FutureEventAnalysis.tendsto_wallis_rational
#print axioms FutureEventAnalysis.tendsto_scaled_central_binomial
#print axioms FutureEventAnalysis.tendsto_remainder_polynomial
#print axioms FutureEventAnalysis.tendsto_normalized_remainder
#print axioms FutureEventAnalysis.futureCardReal_formula
#print axioms FutureEventAnalysis.tendsto_leading_coefficient
#print axioms FutureEventAnalysis.tendsto_sqrt_shift_ratio
#print axioms FutureEventAnalysis.tendsto_normalized_leading
#print axioms FutureEventAnalysis.normalized_count_decomposition
#print axioms FutureEventAnalysis.tendsto_futureQuotient_normalized
