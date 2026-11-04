import interfaces.OriginInterfaces
import AxiomAudit

open Lean Elab Command

set_option Elab.async false

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#origin_interfaces_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.localLetters_fuse_adjacent,
      `ProperArc.originCut_reaches_common_boundary,
      `ProperArc.originWords_same_boundary, `ProperArc.originWord_clean]
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
    return Json.mkObj [("schema", toJson "proper_arc_origin_interfaces_audit.v1"),
      ("targets", toJson targets), ("nodes", toJson nodes)]
  logInfo m!"ORIGIN_INTERFACES_JSON\n{report.compress}"

#origin_interfaces_audit

#print axioms ProperArc.localLetters_fuse_adjacent
#print axioms ProperArc.originCut_reaches_common_boundary
#print axioms ProperArc.originWords_same_boundary
#print axioms ProperArc.originWord_clean
#print axioms ProperArc.originWord_reachable
