# Paper XLIV: Structure and Counting Milestone v1

## Scope and identity

This is a local exact-byte proof milestone for the finite structure and
enumeration of **Prefix Memory and the Growth Spectrum of Event Observers**.
It covers all `n >= 3`, positive depths `j >= 1`, singleton-seed chronological
`p,d` histories, the selected source pair `{0,1}`, complete ordered event
records, and null-preserving per-letter traces.

The manifest is
[`milestones/structure-count-v1/manifest.json`](milestones/structure-count-v1/manifest.json).
Its SHA-256 inventory, rather than the repository HEAD, identifies the exact
proof inputs, including currently uncommitted files. It records 102 source
and configuration inputs and 86 explicit Lean axiom-audit outputs. This is
not a Git tag, public archive, independent cold-start reproduction, or
publication receipt.

## Closed finite interfaces

| Mathematical interface | Lean declaration |
| --- | --- |
| Concrete raw-word observer and future-plus-label equivalence | `circularPrefixMachine`, `circular_prefix_classification` |
| Terminal checkpoint code equivalent to the actual terminal-label image | `terminalPrefixActualEquiv` |
| Lemma 3.2 on actual terminal labels | `card_actualTerminalLabel_paper` |
| Terminal minimal observer quotient | `terminalObserverLabelEquiv` |
| Carrier-indexed actual prefix parameters, including retained records | `properCarrierCountEquiv` |
| Lemma 3.1 including the zero-absorption boundary | `card_actualProperLabelsAt_all` |
| Compatible actual placement fibre and its count | `properPrefixPlacementEquiv`, `card_actualProperPlacements_paper` |
| Full and registered actual observer quotient normal forms | `prefixObserverNormalEquiv`, `registeredPrefixObserverNormalEquiv` |
| Both formulas in Theorem 3.3 | `paperTheorem33` |

The forward maps have actual raw-history provenance. The reverse maps
recover the carrier, retained complete records and literal placement, with
the named two-sided inverse identities. The quotient relation is the
concrete machine's all-word `ObserverEq`; the proposed normal-form keys do
not define it by fiat.

The full quotient has four disjoint sectors:

1. one permanently unregistrable unregistered class;
2. actual registerable unregistered placements;
3. actual registered terminal prefix labels, forgetting terminal phase;
4. proper carrier, compatible actual label, and literal placement.

The registered restriction retains the last two sectors. For `N=n-2`,

```text
A = n * sum (r = 0 .. N-1), c(r,j) * choose (2*N-r) (N-r)
card PrefixObserverQuotient           = 1 + R_n + T_(N,j) + A
card RegisteredPrefixObserverQuotient = T_(N,j) + A
```

Noncomputable equivalences use classical choice. No canonical executable
minimizer, unique raw realizing word, or shortest-word result is asserted.

## Source and proof dependency boundary

The milestone includes every local Paper44 module, `Checks.lean`,
`AxiomAudit.lean`, toolchain and Lake locks, the freeze/replay script, and
the transitive imported sibling source modules. The sibling sources remain
in their owning directories; their repository-relative paths and hashes
are recorded in the manifest.

The abstract label/update and observer API comes from Paper XL. The actual
execution, fixed-pair origin/chain/fibre constructions, and future-event
classification come from the existing fixed-pair and future-event source
closures. The upstream and full-summary owner manifests are also bound.
The current companion does not modify those frozen owners.

The audit is an import/source closure plus explicit `#print axioms`
outputs. It is not a declaration-body dependency graph or a new independent
implementation of packet dynamics. All 86 audited declarations use only a
subset of Lean's standard `propext`, `Classical.choice`, `Quot.sound`;
no custom axiom or `sorryAx` occurs in those closures.

## Validation and read-only replay

Pins: Lean 4.33.0, commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`; Mathlib
`db584cd6d46c92f209a44c0f1c829460d327499d`. All nine package revisions
are recorded by the Lake lock and milestone.

The local validation completed on 2026-11-12:

```text
rime-lean-cache .
lake --no-cache build
lake env lean Checks.lean
lake env lean AxiomAudit.lean
```

The build passed with 3100 jobs and upstream linter warnings. Checks passed;
the explicit axiom inventory passed. Existing compatible dependency/build
artifacts were reused. `--no-cache` does not establish a clean-room or
independent cold-start build.

From this Lean directory, with Python 3.11+, the pinned Lean toolchain and
the local `rime-lean-cache` helper available:

```text
python3 -B freeze_structure_count.py --check-only
python3 -B freeze_structure_count.py
```

The first command checks exact bytes only. The second also repeats the four
validation commands and compares the Lean identity and all axiom outputs.
Neither rewrites the milestone. `--freeze` creates an absent milestone and
refuses to overwrite this one. Changed proof inputs require a separately
named later milestone, not new hashes written over v1.

## Separate manuscript and analytic work

The evolving local manuscript and bibliography are not byte-frozen here.
Corollaries 3.4--3.5, the fixed-depth asymptotic constants, the linear-memory
growth spectrum, the sublinear-memory limit, and the Gaussian critical
window remain outside this milestone's formalized statements.

A later analytic package can import the finite count theorem without
changing these inputs. No analysis-layer theorem is inferred solely from
compiling Theorem 3.3. The bounded Python state-minimization controls remain
separate computational evidence; they are not rerun or promoted by this
proof-source snapshot.
