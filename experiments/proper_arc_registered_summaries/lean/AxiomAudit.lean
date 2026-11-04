import ProperArc
import Lean.Util.CollectAxioms
import Lean.Util.FoldConsts

open Lean Elab Command

set_option Elab.async false

namespace ProperArcAudit

def targets : Array Name := #[
  `ProperArc.originRecord_injective,
  `ProperArc.assemble_strict_parent,
  `ProperArc.run_originWord,
  `ProperArc.originPrefix_no_early_registration]

def kind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient_primitive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"
  | .inductInfo _ => "inductive"

-- Adapted from the published future-event companion's declaration audit.
def closure (env : Environment) (root : Name) : CoreM (Array Name) := do
  let mut pending := #[root]
  let mut seen : NameSet := {}
  while !pending.isEmpty do
    let name := pending.back!
    pending := pending.pop
    if seen.contains name then continue
    seen := seen.insert name
    let some info := env.find? name | throwError "Missing checked declaration: {name}"
    pending := pending ++ info.getUsedConstantsAsSet.toArray
  return seen.toArray.qsort Name.lt

def names (values : Array Name) : Json := toJson (values.map Name.toString)

end ProperArcAudit

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#proper_arc_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let mut all : NameSet := {}
    let mut targets : Array Json := #[]
    for target in ProperArcAudit.targets do
      let dependencies ← ProperArcAudit.closure env target
      for name in dependencies do all := all.insert name
      let info ← getConstInfo target
      let axioms ← collectAxioms target
      let signature ← Meta.ppExpr info.type
      targets := targets.push (Json.mkObj [
        ("name", toJson target.toString), ("signature", toJson signature.pretty),
        ("axioms", ProperArcAudit.names axioms), ("dependencies", ProperArcAudit.names dependencies)])
    let mut nodes : Array Json := #[]
    for name in all.toArray.qsort Name.lt do
      let info ← getConstInfo name
      nodes := nodes.push (Json.mkObj [
        ("name", toJson name.toString), ("kind", toJson (ProperArcAudit.kind info)),
        ("direct_dependencies", ProperArcAudit.names (info.getUsedConstantsAsSet.toArray.qsort Name.lt))])
    return Json.mkObj [("schema", toJson "proper_arc_origin_dependency_audit.v1"),
      ("targets", toJson targets), ("nodes", toJson nodes)]
  logInfo m!"PROPER_ARC_JSON\n{report.compress}"

#proper_arc_audit

#print axioms ProperArc.mem_interval_iff
#print axioms ProperArc.card_interval
#print axioms ProperArc.card_arc
#print axioms ProperArc.interval_union
#print axioms ProperArc.interval_disjoint
#print axioms ProperArc.originRecord_union
#print axioms ProperArc.originRecord_injective
#print axioms ProperArc.localFusion_eq_rotated
#print axioms ProperArc.run_local_unregistered
#print axioms ProperArc.segmentPlacement_at
#print axioms ProperArc.interval_singleton
#print axioms ProperArc.segmentPlacement_one
#print axioms ProperArc.segmentPlacement_step
#print axioms ProperArc.assemble_strict_parent
#print axioms ProperArc.run_alignment
#print axioms ProperArc.assembled_parents_placement
#print axioms ProperArc.run_parentAssembly
#print axioms ProperArc.moveBack_parents
#print axioms ProperArc.run_slideParents
#print axioms ProperArc.run_originPrefix
#print axioms ProperArc.fusionParents_boundary
#print axioms ProperArc.run_originWord
#print axioms ProperArc.distinct_cut_origins
#print axioms ProperArc.run_origin_of_some
#print axioms ProperArc.originPrefix_no_early_registration
#print axioms ProperArc.boundary_clean
