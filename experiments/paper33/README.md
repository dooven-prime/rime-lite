# Paper XXXIII: Stabilizer-Incidence Evidence Package

This directory is the paper-owned theorem-discovery package for Paper XXXIII.
It is self-contained and does not read the broader exploratory source tree.

**Status:** version 1.0 release candidate with a nested paper-owned development
closure. Its receipt records local closure verification, not independent
mathematical validation of the manuscript or Lean development.

## Mathematical Boundary

The paper studies the full lane-partition stabilizer after the deterministic
normalizer twist has ceased to exist. Its exact descent object is the
source-addressed orbit incidence

\[
\mathcal I_a(O,O')=a_\#(O)\cap O'.
\]

The retained finite producer checks the corresponding same-witness
factorization. It also searches for hostile behavior of coarser summaries.

The manuscript proof, not this package, establishes the all-\(g\) family

\[
n=5g,\qquad \Delta=g,\qquad g\ge2,
\]

in which a branch breaks only the punctured four-cycle while a complete
five-token context on an ordinary lane cannot enter that breaking lane.
Consequently,

\[
\operatorname{Break}_{\Delta}(a)\ne\varnothing
\not\Longrightarrow
\operatorname{SafeHit}_a=\operatorname{SameLane}_{\Delta}.
\]

This does not prove that the break set itself is a non-descending quotient.
That stronger claim requires matched branches with the same retained break
data and different Safe-Hit predicates.

## Owned Files

| File | Role |
|---|---|
| `../../figures/paper33/render.py` | paper-owned renderer for the source-addressed incidence figure |
| `../../figures/paper33/fig1_source_addressed_incidence.png` | reader-facing theorem-interface figure |
| stabilizer_hostile_audit.py | standard-library exact producer and hostile search |
| results/stabilizer_hostile_audit_v1.json | complete full-stabilizer scan for every multi-lane domain with \(6\le n\le9\) |
| results/stabilizer_n10_delta2_full_v1.json | complete first hostile domain \((n,\Delta)=(10,2)\) |
| validation/validate_source.py | manuscript, bibliography, theorem-surface, and source-hygiene audit |
| validation/validate_stabilizer_hostile_audit.py | static result validator and optional replay wrapper |
| validation/validate_lean_formalization.py | static Lean closure validator and optional compiler replay |
| validation/validate_package.py | exact-byte working-closure validator |
| lean/ | partial Lean formalization of the X4 capacity-obstruction implication spine |

The research ledger papers/paper33/DIRECTION_DRAFT.md is not an evidence
artifact.

## Source Audit

The source validator checks:

- LF-only UTF-8 manuscript and bibliography bytes;
- absence of control-character and common TeX-escape corruption;
- the exact citation and paper-local bibliography slice;
- unique equation tags and the declared theorem surface;
- the expected top-level section order;
- the finite/all-\(g\), quotient, and raw/typed claim firewalls.

Run:

~~~powershell
python experiments/paper33/validation/validate_source.py
~~~

## Exact Incidence Control

For a branch \(a\), the producer compares:

1. the direct quotient edge relation obtained from the concrete partial
   branch dynamics; and
2. the relation reconstructed through the concrete intermediate incidence
   sets \(a_\#(O)\cap O_1\).

Equality checks the exact same-witness factorization. It does not promote
nonempty incidence and a separate base edge into a composable witness.

## Retained Finite Results

### Small full-stabilizer scan

The first result covers all eight multi-lane domains with
\(6\le n\le9\):

- 656 full stabilizer branches;
- 656 source-addressed incidence-factorization checks;
- no retained X3 failure;
- no retained break-set or stronger coarse-signature variation.

This is a bounded positive control, not an all-\(n\) theorem.

### First complete hostile domain

For \((n,\Delta)=(10,2)\), the complete 2,880-branch scan records:

| Outcome | Branches |
|---|---:|
| ADJ | 80 |
| INTERMEDIATE | 160 |
| SAME | 2,640 |

The first intermediate branch breaks only the punctured four-cycle and is the
\(g=2\) member of the paper's symbolic capacity-isolation family. Its exact
state counts are

\[
|\operatorname{Adj}|=505,\qquad
|\operatorname{SafeHit}|=555,\qquad
|\operatorname{SameLane}|=560.
\]

The result checks the incidence factorization on eight representative
branches and exhausts the Safe-Hit classification on all 2,880 branches.

### Bounded family control

Both retained JSON files include a direct bounded check of the symbolic
family for \(2\le g\le12\). The check verifies the forward-invariant ordinary
lane obstruction used by the paper proof. Its status is
BOUNDED_CONTROL_OF_SYMBOLIC_OBSTRUCTION_NOT_PROOF.

## Commands

Validate retained results:

~~~powershell
python experiments/paper33/validation/validate_stabilizer_hostile_audit.py
~~~

Replay the \(n\le9\) scan:

~~~powershell
python experiments/paper33/validation/validate_stabilizer_hostile_audit.py --replay-small
~~~

Replay the complete \((10,2)\) scan:

~~~powershell
python experiments/paper33/validation/validate_stabilizer_hostile_audit.py --replay-hostile
~~~

The hostile replay is substantially slower than the small scan.

Regenerate explicitly:

~~~powershell
python experiments/paper33/stabilizer_hostile_audit.py --max-n 9 --output experiments/paper33/results/stabilizer_hostile_audit_v1.json
python experiments/paper33/stabilizer_hostile_audit.py --domain 10:2 --factorization-limit 8 --output experiments/paper33/results/stabilizer_n10_delta2_full_v1.json
~~~

## Lean Formalization

The paper-owned project in `lean/` compiles a partial formalization of the
data-independent implication spine behind Theorem 5.1. It proves that:

- a rank-five output cannot equal a capacity-four punctured lane;
- one enabled return preserves the declared ordinary-lane nonedge family;
- the family remains invariant along every finite path;
- the family is disjoint from the edge target and therefore cannot Safe-Hit;
- together with the inherited Safe-Hit-to-SameLane implication, one hostile
  state witnesses strict containment.

The abstract `CapacitySystem` deliberately consumes the concrete hypotheses
proved in the manuscript. The Lean development does not construct the branch
family \(a_g\), prove the cyclic lane arithmetic, derive lane shape or
nonedge preservation from the normalized return formula, or read the finite
JSON controls. It also does not formalize source-addressed orbit incidence,
typed transfer membership, projectability, recursive return, settlement, or
reset bounds.

Validate the bound sources or replay the compiler:

~~~powershell
python experiments/paper33/validation/validate_lean_formalization.py
python experiments/paper33/validation/validate_lean_formalization.py --replay
~~~

## Development Closure

development-manifest.json binds the manuscript, bibliography, producer,
retained results, documentation, and validators by SHA-256. It intentionally
claims no release identity. The outer release manifest binds this immutable
development closure together with the reader PDF, figure bytes, release
environment, and public-package validator.

The direction ledger is excluded from this closure and from any future reader
release.

~~~powershell
python experiments/paper33/validation/validate_package.py
python experiments/paper33/validation/validate_package.py --replay-small
python experiments/paper33/validation/validate_package.py --replay-lean
~~~

## Release Validation

The public receipt is excluded from its own closure. Its replay block is
canonical and records whether the small finite control, the complete hostile
domain, and the Lean compiler were actually replayed. Generate the manifest
and receipt only after the manuscript, bibliography, reader PDF, figure,
development closure, release environment, and validator are frozen:

~~~powershell
python experiments/paper33/validation/validate_public_package.py --write-manifest
python experiments/paper33/validation/validate_public_package.py --replay --write-receipt
python experiments/paper33/validation/validate_public_package.py --replay
~~~

## Claim Boundary

The package does not establish:

- a complete full-stabilizer classification;
- break-set or cycle-type quotient descent;
- a general positive mobility-to-break theorem;
- survivor placement;
- typed transfer membership;
- projectability or recursive return;
- credit settlement or a reset bound.

Finite absence of a matched hostile pair is OPEN, not false.
