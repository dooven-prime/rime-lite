import FutureEvent
import Lean.Util.CollectAxioms
import Lean.Util.FoldConsts

open Lean Elab Command

set_option Elab.async false

namespace FutureEventMilestoneAudit

def countingTargets : Array Name := #[
  `FutureEvent.registerablePlacementParamsEquiv,
  `FutureEvent.registeredPlacementParamsEquiv,
  `FutureEvent.card_actual_registerable_placements,
  `FutureEvent.card_actual_registered_placements_closed,
  `FutureEvent.card_futureQuotient_closed]

def parameterTargets : Array Name := #[
  `FutureEvent.RegisterableParam, `FutureEvent.RegisterableParams,
  `FutureEvent.RegisteredPlacementParam, `FutureEvent.RegisteredPlacementParams]

def declarationKind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient_primitive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"
  | .inductInfo _ => "inductive"

/-- Walk checked declaration types and values, including opaque proof bodies,
inductive constructors and recursor families. This is not an import-only graph. -/
def dependencyClosure (env : Environment) (root : Name) : CoreM (Array Name) := do
  let mut pending := #[root]
  let mut seen : NameSet := {}
  while !pending.isEmpty do
    let name := pending.back!
    pending := pending.pop
    if seen.contains name then continue
    seen := seen.insert name
    let some info := env.find? name | throwError "Missing imported declaration: {name}"
    pending := pending ++ info.getUsedConstantsAsSet.toArray
  return seen.toArray.qsort Name.lt

def nameArray (names : Array Name) : Json := toJson (names.map Name.toString)

end FutureEventMilestoneAudit

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#finite_milestone_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let mut all : NameSet := {}
    let mut targets : Array Json := #[]
    for target in FutureEventMilestoneAudit.countingTargets do
      let names ← FutureEventMilestoneAudit.dependencyClosure env target
      for name in names do all := all.insert name
      let info ← getConstInfo target
      let axioms ← collectAxioms target
      let signature ← Meta.ppExpr info.type
      targets := targets.push (Json.mkObj [
        ("name", toJson target.toString),
        ("kind", toJson (FutureEventMilestoneAudit.declarationKind info)),
        ("signature", toJson signature.pretty),
        ("axioms", FutureEventMilestoneAudit.nameArray axioms),
        ("dependencies", FutureEventMilestoneAudit.nameArray names)])
    let mut parameters : Array Json := #[]
    for target in FutureEventMilestoneAudit.parameterTargets do
      let names ← FutureEventMilestoneAudit.dependencyClosure env target
      let info ← getConstInfo target
      let some value := info.value? | throwError "No parameter definition: {target}"
      let display ← Meta.ppExpr value
      parameters := parameters.push (Json.mkObj [
        ("name", toJson target.toString), ("definition", toJson display.pretty),
        ("dependencies", FutureEventMilestoneAudit.nameArray names)])
    let mut nodes : Array Json := #[]
    for name in all.toArray.qsort Name.lt do
      let info ← getConstInfo name
      nodes := nodes.push (Json.mkObj [
        ("name", toJson name.toString),
        ("kind", toJson (FutureEventMilestoneAudit.declarationKind info)),
        ("direct_dependencies", FutureEventMilestoneAudit.nameArray
          (info.getUsedConstantsAsSet.toArray.qsort Name.lt))])
    return Json.mkObj [("schema", toJson "future_event_finite_dependency_audit.v1"),
      ("targets", toJson targets), ("parameters", toJson parameters), ("nodes", toJson nodes)]
  logInfo m!"FINITE_MILESTONE_JSON\n{report.compress}"

#finite_milestone_audit

#print axioms FutureEvent.registerablePlacementParamsEquiv
#print axioms FutureEvent.registeredPlacementParamsEquiv
#print axioms FutureEvent.card_actual_registerable_placements
#print axioms FutureEvent.card_actual_registered_placements_closed
#print axioms FutureEvent.card_futureQuotient_closed
