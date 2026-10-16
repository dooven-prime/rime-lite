# Paper XXXIX Consumer Realization Controls

**Status:** paper-owned evidence package. Its development manifest is not a
release identity; the separate release manifest binds the reader PDF and
the selected public closure.
The [manuscript](../../papers/paper39/Paper%20XXXIX.md) owns the all-N proofs.

**Execution status:** runnable with Python 3.11+ and the standard library only.
Default validation requires no Lean, network, external data, Git history,
exploratory tree, or external UFE implementation. It is read-only. An
optional [partial Lean spine](lean/README.md) uses pinned Lean 4.33.0 and its
bundled standard library, without Mathlib.

**Paper evidence:** bounded consistency controls under
`LOCAL_CLOSURE_VERIFICATION`, not independent validation, a Computational
Certificate, or a machine proof of the general theorems.

## Fixed Inputs

| Domain | Actions and seeds | History coverage |
|---|---|---|
| n = 2, 3, 4 | Every rank-(n-1) coordinate self-map, identity singleton seed on all n atoms | Every p/d word of length 0 through 5 |
| n = 4 | The same 144 defects, additionally seed (0,2) on two atoms and (0,1,3) on three atoms | Every word of length 0 through 5 |
| n = 5, 6, 7 | Canonical and one fixed output-transported defect, seeds on n-1 and n atoms, reversed atom enumeration | Every word of length 0 through 6 |

There are 464 fixed action/seed cases. This is not an exhaustive catalogue of
all seeds or larger actions. Exact inputs and ranges belong to
[audit_scope.py](audit_scope.py); a result cannot shrink its own audit domain.
At every retained history all nonempty atom subsets are tested for event
registration, including those that were never created as fusion events.
Both commands for both letters are tested at every such query. Successor
checks also examine the one-letter extension at the history-depth boundary;
those extensions are not counted as additional retained histories.

The retained catalogue has 30,000 histories, 318,936 nonempty-block registration
queries, and 1,275,744 command-domain queries. It includes 934 legal Carry
commands with an unrelated fusion and 3,715 legal Absorb commands. These
numbers are generated counters bound by the development manifest, not new
mathematical claims or population estimates.

The three-state dd/pdd origin counterexample and the seven-state invocation
`dppd; ppd; p^5d` are separately retained with full trees, port addresses,
marker, ordered UFE inputs, and consumer summaries. These examples are not
included in the catalogue counters. Atom-renaming continuation is checked
structurally, not merely by packet masses. A long-plateau test is an additional
finite test, not a bound on the mathematical execution domain.

## Three Implementations and the Comparison

1. [log_consumer.py](log_consumer.py) independently runs raw packet unions
   and an occurrence-ordered event log. It specifies registration, origin,
   selected absorptions, full partition, and command successors without
   importing either representation.
2. [forest.py](forest.py) stores only placed trees and a latest-event marker.
   Its decoder follows the selected node's ancestor path; no word, timestamp,
   chronological event list, or consumer summary is stored in the forest.
3. [placed_ufe.py](placed_ufe.py) stores an abstract effective-union input list
   and class placement. Prefix classes decode event ports and absorptions.
   A separate fold reconstructs the entire forest and marker for comparison.

The implementations share immutable record declarations and environment
data, not transition or consumer-decoding algorithms. The UFE forest fold
uses the forest's record constructors, not its transition function. Its
ordered union inputs bind the fixed kernel ports; they are not sorted or
deduced from parent-pointer directions.

The runner checks complete registration/read equality, both directions of
command definedness, full successor commutation, actual next representatives,
the finite node bound, disjoint absorption partners, and atom renaming with
the transported seed and enumeration. In particular, `Carry(d)` can append
an unrelated UFE union and create a new forest marker. It must still update
the full partition while retaining the original selected event.

The retained JSON fingerprints complete concrete traces and summaries; counts
alone are not treated as equality of state sets. The default validator reruns
the same audit runner, comparing the exact resulting record. This is local
replay, not a separately implemented or externally independent validator.
The separate algorithms being compared are the log, forest, and abstract UFE
implementations; shared software can still contain errors.

Root storage order is not a semantic coordinate order. Well-formed roots
may be stored in any permutation. Packet projection sorts by current
position, and every collision explicitly orders incoming trees by the fixed
kernel ports before constructing a node. The Python regression tests cover
the reversed two-point seed and all root permutations in three selected
states, including a nontrivial latest marker and selected invocation.

## Hostile Controls

The contract tests reject or distinguish containment-only registration,
latest-marker substitution, loss of an unrelated Carry fusion, swapped
event ports, reversed ordered UFE inputs, an omitted absorption, incomplete
atom renaming, narrowed result ranges, changed seeds, and missing suffixes.

A generated four-state matched control compares histories `dp` and `dppd`:
the origin, selected absorption list, and carrier coincide, but the complete
partitions and next `Absorb(d)` domains differ. This exercises the full-state
requirement without admitting arbitrary ambient consumer tuples.

## Commands

Read-only release verification, including the bounded replay, hostile tests,
and isolated Lean compilation:

~~~powershell
python -B experiments/paper39/validation/validate_release.py
~~~

The release receipt records `LOCAL_CLOSURE_VERIFICATION`. It does not certify
the manuscript's general proofs or constitute independent validation.

Read-only closure, contract tests, and full bounded replay:

~~~powershell
python -B experiments/paper39/validation/validate_package.py
~~~

Closure, source lint, and fixed record coverage only; explicitly no replay:

~~~powershell
python -B experiments/paper39/validation/validate_package.py --static
~~~

Default validation plus an isolated Lean build and fifteen declaration
axiom audits:

~~~powershell
python -B experiments/paper39/validation/validate_package.py --lean
~~~

Default and static modes check the formal source/digest/coverage closure
but do not invoke the compiler. The explicit Lean replay copies only the
declared formal sources to a temporary project and builds without a prior
project cache. See the formal README for the conditional continuation
hypotheses and the concrete adequacy results that remain outside Lean.

Intentional authoring-time regeneration and digest refresh:

~~~powershell
python -B experiments/paper39/consumer_audit.py
python -B experiments/paper39/seal_manifest.py
python -B experiments/paper39/validation/validate_package.py
~~~

After intentional Lean changes, first run its validator with `--seal`,
then refresh the outer development manifest. Neither validator seals by
default. A formal seal is written only after compilation and axiom checking.

Validation never regenerates results or repairs digests. Child processes
remove `PYTHONOPTIMIZE` and disable bytecode writes. Mathematical checks use
explicit exceptions. Directory scans prune caches before descending. The
manifest excludes itself; verification compares bound bytes before and after
running. The development seal excludes the release manifest and receipt;
their validation is owned by the separate release gate above.

## Inventory and Provenance

| Path | Role |
|---|---|
| audit_scope.py, contract.py | Fixed domain and immutable record formats |
| log_consumer.py | Independent occurrence-log task implementation |
| forest.py | Finite placed-fusion realization |
| placed_ufe.py | Abstract placed forward-UFE adapter and decoders |
| consumer_audit.py | Three-model bounded producer |
| results/consumer_audit_v1.json | Complete trace fingerprints and worked examples |
| validation/validate_consumer.py | Fixed-coverage check and local replay |
| validation/test_contract.py | Consumer and package negative controls |
| validation/validate_source.py | Source and implementation-separation lint |
| validation/validate_package.py | Read-only closure entry point |
| seal_manifest.py | Explicit development digest writer |
| development-manifest.json | Exact-byte selected development closure |
| lean/ | Partial formal source, pinned toolchain, coverage, and axiom manifest |
| validation/validate_lean_formalization.py | Static formal closure or explicit isolated compiler replay |

The mathematical source inputs are the canonical manuscript, its independent
consumer specification, supplementary adequacy/correspondence notes, and
maintained bibliography. No dated snapshot, editorial audit, old B0 artifact,
or excluded historical draft is needed for replay.

The broader exploratory source tree contains old packet/B0 controls, not a
retained complete implementation of this named consumer and adapter. This
package is newly implemented from the paper's declared equations; it does
not copy scratch outputs or relabel earlier checks as paper evidence.
Historical exploratory files are left untouched and are not imported.

## Known Nonclaims

All comparisons concern histories generated from declared singleton seeds.
Well-formed ambient forests or arbitrary UFE histories are not thereby
certified as generated. The finite word catalogue is not an execution-length
restriction in the theorem. No external UFE algorithm, imperative refinement,
rollback wrapper, total-correctness result, efficiency claim, expressivity
separation, or minimal representation theorem is verified here.

This is not old B0, target-blind Auth_5, selector identity, transfer membership,
F3, projectability, POS, recursive settlement, or a reset-bound certificate.
No semantics or consumer field is added to make any historical bridge work.
The reader PDF and release environment remain separate publication tasks.
