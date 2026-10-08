# Paper XXXVII Guarded-Group Lean Spine

**Status:** paper-owned partial formalization. Compilation and source
bindings are recorded in the formalization manifest after replay.
The manuscript remains the theorem authority.

## Checked Surface

| Lean declaration | Manuscript role |
|---|---|
| runWord_append, guardedReach_trans | Actual paths concatenate at the successor produced by the preceding word |
| loopControl_inv | A finite-order positive loop supplies inverse control without a new generator |
| generated_loop_control | Supplied actual generator loops realize the generated subgroup |
| guardedReach_iff_mem_generated | Conditional logical spine of Theorem 4.1 |
| rightPhaseClass_eq_iff | Right-phase class equality means y*x-inverse belongs to H |
| lanePhaseEquiv | Corollary 4.2's abstract lane-by-right-coset state-set equivalence |
| phaseDeterministic_iff_mem_normalizer | Proposition 4.3's necessary and sufficient finite-phase normalizer condition |
| phase_non_descent_witness | Nonnormalization supplies equal input phase classes with unequal output classes |
| survivorRestriction_eq_iff | Equal survivor reads have at most the two kernel-order extensions |
| restrictionFiber_card | The exact restriction fiber has size one or two according to kernel-swap membership |
| terminal_card_eq_frontier_card_mul | Corollary 5.3's exact terminal/frontier cardinality relation |
| survivorFrontier_card_eq_div | The corresponding exact quotient count |
| alternating_survivorFrontier_eq_full | Theorem 6.3's algebraic A5/S5 survivor-projection equality |

## Assumption and Type Boundary

The actual-word module uses a partial step returning an Option successor.
Reachability contains an actual list of labels. Its concatenation theorem
uses the same intermediate state, not separate existential edge witnesses.
The finite-group closure argument proves that uniform positive generator
loops give positive inverse loops and all subgroup elements.

Theorem 4.1's logical reduction explicitly consumes geometric edge soundness,
actual lane relocation, and uniform generator-loop realization. It does not
prove those hypotheses for the concrete normalized circular action.
The guards, physical ordinary-lane confinement, explicit relocation words,
and physical terminal-placement converse remain manuscript proofs.

Phase acts by left multiplication. The classes are the right cosets H*kappa.
No normal-subgroup hypothesis or quotient-group structure is introduced.
The state-set equivalence and deterministic-update iff are separate results.
The normalizer theorem assumes only that the phase subgroup is finite.

Fin 5 in the restriction module denotes within-lane indices, not the
normalized physical carrier E. Its index zero is legitimate. The physical
map sending an index to index*Delta is outside this formalized subset.
Terminal membership and the three survivor reads come from one permutation.
The algebraic A5/S5 equality uses opposite-parity kernel extensions;
it does not formalize the concrete branch-generation or raw reachability
claims of the matched family.

## Noncoverage

This is not a complete Lean proof of the all-g normalized full-lane
classification. It does not formalize the finite JSON catalogue, the
concrete F20/S5 generation/non-descent family, exhaustive subgroup strata,
shortest or budgeted paths, partial occupancy, typed source or authorization,
handoff, projectability, recursive return, settlement, or reset bounds.
The paused B0 audit and independent forest consumer are not inputs.

## Pinned Build

The project pins Lean 4.33.0 and Mathlib revision
db584cd6d46c92f209a44c0f1c829460d327499d. All package revisions are in
lake-manifest.json. No other paper's Lean project is imported.

~~~text
lake build
lake env lean AxiomAudit.lean
~~~

The Python validator supports static source/lock/manifest checks and
explicit compiler replay. It also checks the printed axiom footprint.
Only the standard Lean dependencies propext, Classical.choice, and
Quot.sound are permitted; no project axiom, proof placeholder, or
native-decision trust shortcut is admitted.

~~~powershell
python -B experiments/paper37/validation/validate_lean_formalization.py
python -B experiments/paper37/validation/validate_lean_formalization.py --replay
~~~

The optional replay requires the pinned toolchain and Mathlib dependencies.
An ignored local dependency cache is not a paper dependency or release
artifact. Default package verification checks the bound formal sources
statically without requiring a compiler installation.
