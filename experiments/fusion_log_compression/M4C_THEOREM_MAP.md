# M4-C theorem-to-source map

## Actual-word Interface

Owner: `lean_m4c/FusionLogInterpretation/ArbitraryInitialReplay.lean`.
The paper-facing corollary has this signature, under `{n : Nat} [NeZero n]`
and `{alpha : Type*} [DecidableEq alpha]`:

```lean
theorem arbitrary_initial_log_endpoint_representative
    (F : Finset α) (actual : LoggedExecution n α) (word : List Letter) (hn : 3 ≤ n)
    (nonempty : (occupiedSites actual.state.placed).Nonempty) :
    ∃ representative : List Letter,
      (runLogged F actual representative).fullLog = (runLogged F actual word).fullLog ∧
      (runLogged F actual representative).state.placed = (runLogged F actual word).state.placed ∧
      representative.length ≤ normalFormBudget n (occupiedSites actual.state.placed).card
        (occupiedSites (run F actual.state word).placed).card
```

`arbitrary_initial_log_endpoint_budget` is stronger: it returns an
`InterpretedJointPlan` with actual M2 stage admission and an actual M3
batch plan over the original atom type, together with B, K and M inequalities.
The budget functions are imported unchanged from M4-B. `n >= 3`, nonempty
occupied support, and the actual chronological reference word are explicit.

For eligible packet partitions, occupied-site rank is the ordinary packet
rank. `named_occupied_rank` and `named_initial_log_endpoint_representative`
make the existing finite `LegalNamedPlacement n r alpha` specialization
explicit. No assumption that its supplied naming is positively oriented is
needed: the canonical source order is induced by physical sites.

## Ownership and Proof Chain

| Declaration | Owner under `lean_m4c/FusionLogInterpretation/` | Role |
| --- | --- | --- |
| `expandBlock_union` | `PacketInterpretation.lean` | Union interpretation of finite index sets |
| `expandPlacement_fusion`, `step_placement_interprets` | same | Exact real-action commutation |
| `event_interprets`, `eventTrace_interprets` | same | Complete ordered parents/result, every actual prefix |
| `fusionFree_iff`, `run_support_interprets` | same | Guard reflection and support equality |
| `occupiedRounding_image`, `occupiedRounding_fixed` | `InitialEncoding.lean` | Degree-one monotone rounding onto occupied sites |
| `canonicalPlacement_ordered`, `initial_placement_interprets` | same | SourceOrdered representation and literal decoding |
| `batchPlan_interprets` | `PhysicalRoutes.lean` | Actual generic-atom M3 plan with unchanged word/K/M |
| `admitted_fusion_stage`, `fusionPlan_interprets` | same | M2 routes enabled at actual successive representatives |
| `InterpretedJointPlan.word_eq`, `batches_eq`, `transfers_eq` | same | Costs belong to the transported physical program |
| `jointPlan_interprets` | same | Assembles the two actual route components |
| `interpreted_sourceOrdered_budget` | `ArbitraryInitialReplay.lean` | Transport of the frozen theorem under an initial interpretation |
| `arbitrary_initial_log_endpoint_budget` | same | Supplies the interpretation for every nonempty initial placement |
| `arbitrary_initial_log_endpoint_representative` | same | Actual raw-word compression corollary |
| `named_initial_log_endpoint_representative` | same | Initial packet-cycle specialization with rank r |

```text
initial occupied support S + original site labels
  -> monotone periodic occupied-site rounding
  -> canonical ZMod n source fibres
  -> SourceOrdered representation decoding exactly to the initial placement
union/action/event/support commutation + frozen M4-B theorem
  -> same literal fusion program admitted on actual predecessors
  -> generic-atom M3 batch plan, same word and K/M
  -> actual complete log + literal endpoint + unchanged B/K/M
```

The rounding construction is a static encoding, not an entry word. No
runtime cost is silently omitted. Hole indices have empty labels but are
part of canonical source fibres; Option-level decoding preserves physical
support exactly throughout execution. The theorem only transports the
raw observation contract. It does not identify the two selected `origin`
or `chain` policies when their targets differ.

Any pre-existing actual complete-log prefix remains unchanged on both
sides of the final comparison. Reinterpreting that old prefix in the new
initial packet alphabet is not an assumption of the theorem.

## Fixed Ancestor and Evidence

The ancestor is M4-B v1.0, archived at
<https://doi.org/10.5281/zenodo.23976349>, ZIP SHA-256
`66ce493a68199b965d17ef275c1d4e0e39619a652c543cde6d6429d28d8b60dc`.
Its development manifest SHA-256 remains
`69456464ff271024c8ab9e97694d5c8fdf125db3c309aadf98fded7fb07612ed`;
the M1-M3 manifest SHA-256 remains
`65bf9a915294891a0b5558a16445f64588cda4db8cd893c579ccd4d294cd4169`.

`m4c-development-manifest.v1.json` binds only this new layer and pins the
ancestor. `validation/replay_m4c.py` checks the ancestor gates before and
after the build and audits 29 declarations through `#print axioms`; only
`propext`, `Classical.choice` and `Quot.sound` are permitted. Its receipt
includes the full Lean signatures, not merely theorem names.

This is a local M4-C development result, not an expansion of the deposited
M4-B identity or HAL v1 proof status. The actual-word compression part of
manuscript Corollary 4.3 is covered on arbitrary nonempty set-valued initial
placements. Theorem 4.1's independent admissible-schedule/compatible-target
iff, Section 5 counts and Section 6 optimality are not added here.
