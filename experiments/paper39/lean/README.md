# Paper XXXIX: Partial Implementation Spine

**Scope:** fifteen kernel-checked declarations about port-indexed lookup,
binary-tree counts, and conditional continuation. This is not a complete
formalization of the forest model, Theorem 4.1, or Proposition 5.1. The
manuscript remains the mathematical theorem owner.

Lean is pinned to 4.33.0. Only its bundled `Std` and core library are used;
there is no Mathlib dependency, finite JSON import, or earlier paper's Lean
source dependency. `.lake` is ignored runtime output, not evidence.

## Coverage

| Source | Checked result | Required boundary |
|---|---|---|
| PortLookup.lean | A functional position-to-tree list has permutation-invariant lookup; selecting children by the fixed two ports is storage-order invariant; reversed two-root example | Key functionality is explicit. This is a port-selection model, not a proof that the Python sorting implementation refines Lean or that every grouped update is well formed. |
| ForestCounts.lean | Binary tree and forest identities: leaves = fusions + roots; nodes + roots = 2 leaves; nonempty forests have at most 2 leaves minus one nodes | Counts are leaf occurrences. The manuscript's well-formedness conditions identify them with distinct source atoms. Distinctness, the finite labelled state enumeration, marker validity, and update preservation are not formalized. |
| Continuation.lean | Single-step domain reflection, chronological path commutation, path domain reflection, and a successor witness starting from the same concrete representative | Single-step Option-map commutation is an explicit hypothesis. The concrete forest/log adequacy theorem must supply it on registered generated invocations. No concrete adequacy proof is assumed to have been formalized. |

The continuation lemmas are standard simulation/path-induction machinery,
not a new result or evidence that the forest and UFE adapters already satisfy
their premises in Lean. `X` is the chosen implementation invocation type;
the caller must supply the declared domain and the fixed selected event.
No inverse decoder, representative switching, admission predicate, or new
consumer field is introduced.

The root-storage repair in Python is separately covered by regression tests:
the unordered roots accepted by `check_wellformed` are grouped, and collision
children are explicitly put in kernel-port order before node construction.
Packet projection is canonical by position. Lean proves the abstract
storage-order independence of port lookup, not correctness of Python code.

## Verification

Static formal source/digest/coverage check, with no compiler requirement:

~~~powershell
python -B experiments/paper39/validation/validate_lean_formalization.py
~~~

Fresh compiler and all fifteen declaration axiom audits:

~~~powershell
python -B experiments/paper39/validation/validate_lean_formalization.py --replay
~~~

After intentional formal edits, compile and audit before sealing:

~~~powershell
python -B experiments/paper39/validation/validate_lean_formalization.py --seal
python -B experiments/paper39/seal_manifest.py
~~~

The validator pins the runtime and admits only `propext`, `Classical.choice`,
and `Quot.sound` in axiom footprints. Project axioms, admitted proofs, unsafe
proof shortcuts, and native-decision proof shortcuts are prohibited. The
small reversed-root control uses ordinary kernel-checked `decide`.

## Excluded Scope

The general event/node and ancestor/log correspondence, concrete Carry/Absorb
definedness and full successor equations, seed-generated-domain closure,
atom-renaming adequacy, placed forward-UFE correspondence, external UFE code,
and the Python replay catalogue are not proved in this partial formalization.
No old B0, authorization, transfer, POS, settlement, or reset-bound bridge is
asserted. Static verification does not perform a new compiler replay.
