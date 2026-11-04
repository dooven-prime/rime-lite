import chains.ActualChains
import AxiomAudit

open Lean Elab Command

set_option Elab.async false

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#chain_construction_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.Chains.decodePrefix_absorbed,
      `ProperArc.Chains.decodeChain_keys, `ProperArc.Chains.decodeChain_injective,
      `ProperArc.Chains.realize_clean_prefix, `ProperArc.Chains.realize_clean_code,
      `ProperArc.Chains.codeEmbeddingActualSelectedChains,
      `ProperArc.Chains.codeEmbeddingActualSelectedChains_clean,
      `ProperArc.run_local_unregistered, `ProperArc.run_originWord,
      `ProperArc.boundary_clean, `ProperArc.actualRegistrationOriginsEquivCuts]
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
    let info ← getConstInfo `ProperArc.Chains.ActualSelectedChains
    let some value := info.value? | throwError "Missing actual-chain definition"
    let definition ← Meta.ppExpr value
    return Json.mkObj [("schema", toJson "proper_arc_chain_construction_audit.v1"),
      ("scope_status", toJson "CONSTRUCTIVE_CHAIN_EMBEDDING"),
      ("targets", toJson targets), ("nodes", toJson nodes),
      ("actual_chains_definition", toJson definition.pretty)]
  logInfo m!"CHAIN_CONSTRUCTION_JSON\n{report.compress}"

#chain_construction_audit

#print axioms ProperArc.Chains.Prefix.initial_carrier
#print axioms ProperArc.Chains.Prefix.inside
#print axioms ProperArc.Chains.decodePrefix_absorbed
#print axioms ProperArc.Chains.rename_fusionPlacement
#print axioms ProperArc.Chains.rename_step
#print axioms ProperArc.Chains.rename_run
#print axioms ProperArc.Chains.sourceShift_apply
#print axioms ProperArc.Chains.shift_interval
#print axioms ProperArc.Chains.shift_arc
#print axioms ProperArc.Chains.shift_origin
#print axioms ProperArc.Chains.shift_seed
#print axioms ProperArc.Chains.shift_boundary
#print axioms ProperArc.Chains.rename_clean
#print axioms ProperArc.Chains.recordKey_R
#print axioms ProperArc.Chains.recordKey_L
#print axioms ProperArc.Chains.keys_zero
#print axioms ProperArc.Chains.keys_succ
#print axioms ProperArc.Chains.keys_injective
#print axioms ProperArc.Chains.decodePrefix_keys
#print axioms ProperArc.Chains.decodeCanonicalChain_injective
#print axioms ProperArc.Chains.realize_clean_prefix
#print axioms ProperArc.Chains.realize_clean_code
#print axioms ProperArc.Chains.renameRecord_symm
#print axioms ProperArc.Chains.rename_chain_injective
#print axioms ProperArc.Chains.decodeChain_injective
#print axioms ProperArc.Chains.shifted_recordKey
#print axioms ProperArc.Chains.decodeChain_keys
#print axioms ProperArc.Chains.codeEmbeddingActualSelectedChains_val
#print axioms ProperArc.Chains.codeEmbeddingActualSelectedChains_clean
#print axioms ProperArc.Chains.codeEmbeddingActualSelectedChains
#print axioms ProperArc.run_local_unregistered
#print axioms ProperArc.run_originWord
#print axioms ProperArc.boundary_clean
#print axioms ProperArc.actualRegistrationOriginsEquivCuts
