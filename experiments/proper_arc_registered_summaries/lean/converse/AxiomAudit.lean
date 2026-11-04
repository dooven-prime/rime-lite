import converse.ActualChainConverse
import AxiomAudit

open Lean Elab Command

set_option Elab.async false

set_option maxRecDepth 10000 in
set_option maxHeartbeats 0 in
elab "#chain_converse_audit" : command => do
  let report ← liftTermElabM do
    let env ← getEnv
    let roots := #[`ProperArc.Chains.actual_checkpoint_increases,
      `ProperArc.Chains.actual_partner_is_end_interval,
      `ProperArc.Chains.actual_chain_checkpoint_strict,
      `ProperArc.Chains.actual_chain_in_decode_range,
      `ProperArc.Chains.encodeChain_decodeChain,
      `ProperArc.Chains.actual_chain_decode_encode,
      `ProperArc.Chains.actual_chain_unique_code,
      `ProperArc.Chains.actualSelectedChainsEquivCode,
      `ProperArc.Chains.card_actualSelectedChains,
      `ProperArc.Chains.checkpoint_port_bindings_distinct,
      `ProperArc.Chains.codeEmbeddingActualSelectedChains,
      `ProperArc.Chains.realize_clean_code, `ProperArc.Chains.decodeChain_injective,
      `ProperArc.run_originWord, `ProperArc.actualRegistrationOriginsEquivCuts]
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
    let mut definitions : Array (String × Json) := #[]
    for name in #[`ProperArc.Chains.ActualSelectedChains,
        `ProperArc.Chains.ActualChainTrace, `ProperArc.Chains.encodeChain] do
      let info ← getConstInfo name
      let some value := info.value? | throwError "Missing definition {name}"
      let text ← Meta.ppExpr value
      definitions := definitions.push (name.toString, toJson text.pretty)
    return Json.mkObj [("schema", toJson "proper_arc_chain_converse_audit.v1"),
      ("scope_status", toJson "ACTUAL_FIXED_ORIGIN_CHAIN_EQUIVALENCE"),
      ("targets", toJson targets), ("nodes", toJson nodes),
      ("definitions", Json.mkObj definitions.toList)]
  logInfo m!"CHAIN_CONVERSE_JSON\n{report.compress}"

#chain_converse_audit

#print axioms ProperArc.Chains.advance_congr
#print axioms ProperArc.Chains.advance_none
#print axioms ProperArc.Chains.decodePrefix_congr
#print axioms ProperArc.Chains.decodePrefix_skip
#print axioms ProperArc.Chains.decodePrefix_insert
#print axioms ProperArc.Chains.canonical_pair_inside
#print axioms ProperArc.Chains.canonical_arc_nonempty
#print axioms ProperArc.Chains.checkpoint_port_bindings_distinct
#print axioms ProperArc.Chains.actual_checkpoint_increases
#print axioms ProperArc.Chains.actual_partner_is_end_interval
#print axioms ProperArc.Chains.actual_step_extends_code
#print axioms ProperArc.Chains.actual_chain_trace_step
#print axioms ProperArc.Chains.actual_chain_trace_run
#print axioms ProperArc.Chains.canonical_actual_chain_range
#print axioms ProperArc.Chains.shift_aligned_seed
#print axioms ProperArc.Chains.actual_chain_in_decode_range
#print axioms ProperArc.Chains.keys_mem_iff
#print axioms ProperArc.Chains.keys_bounds
#print axioms ProperArc.Chains.keys_strict
#print axioms ProperArc.Chains.encodeChain_decodeChain
#print axioms ProperArc.Chains.actual_chain_decode_encode
#print axioms ProperArc.Chains.actual_chain_checkpoint_strict
#print axioms ProperArc.Chains.actual_chain_unique_code
#print axioms ProperArc.Chains.actualSelectedChainsEquivCode_apply
#print axioms ProperArc.Chains.actualSelectedChainsEquivCode_symm_val
#print axioms ProperArc.Chains.card_actualSelectedChains
#print axioms ProperArc.Chains.encodeChain
#print axioms ProperArc.Chains.ActualChainTrace
#print axioms ProperArc.Chains.actualSelectedChainsEquivCode
#print axioms ProperArc.Chains.codeEmbeddingActualSelectedChains
#print axioms ProperArc.Chains.realize_clean_code
#print axioms ProperArc.Chains.decodeChain_injective
#print axioms ProperArc.run_originWord
#print axioms ProperArc.actualRegistrationOriginsEquivCuts
