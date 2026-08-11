# Program Philosophy

**Status:** public philosophy note for the RIME program. This file explains the
Rubik-as-laboratory stance and the sectorization bridge from the early papers to
Papers VIII--XIII, with Paper XIV as a development horizon. It is not a proof source; paper manuscripts and
[PROGRAM_MAP.md](PROGRAM_MAP.md) control theorem boundaries.

Program invariant:

```text
Source geometry proposes a realization.
Marked sectorization declares the interface.
Typed carriers determine the observable questions.
Filtrations and closures record different generation data.
Deformation, compilation, reporting, comparison, and action remain separate.
```

The objective of this program is not to study the Rubik's Cube itself.

Rather, Rubik serves as a mathematically tractable laboratory in which
increasingly general structures can be isolated, validated, and eventually
detached from the specific combinatorial system.

Rubik is useful here precisely because it is not being used as a puzzle.  It is
a finite, explicit, highly noncommutative representation laboratory: large
enough to force nontrivial spectral, transport, and accessibility phenomena,
but small enough that every layer of the transport hierarchy can be audited
explicitly.

Accordingly:

```text
Rubik
  ->
finite represented systems
  ->
joint spectral geometry
  ->
accessibility geometry
  ->
generator-set deformation
  ->
sectorized observable frameworks
  ->
observable dynamics
  ->
capability-aware compilation
  ->
typed wall records
  ->
single-system SOF reports
  ->
aligned sparse audits
  ->
policy-relative decisions
```

Each paper isolates or abstracts one layer of problem-specific structure.
Later papers may refine the object types rather than assume a theorem
dependency on every earlier formulation.

The long-term goal is therefore not a theory of Rubik, but a theory of
sectorized observable geometry and accessibility.

---

## Two-Layer Unity and the Typed Middle

The program now has two formal layers of unity, joined by sectorization and
extended by the observable pipeline.

```text
        Structural Unity (Wedderburn-Artin)
========================================================
Semisimple representation theory decomposes a represented
space into canonical matrix-block data:

  V = direct sum over irreducible types and multiplicity spaces.

The simple modules, multiplicities, central idempotents, and
matrix-block coordinates are fixed by the representation, up to
the usual equivalences. This layer is classical.

                        |
                   sectorization
                        |
                        v

        Observable Transport Architecture (RIME)
========================================================
Once sectors and typed observable families are registered, the
common middle layer is branched:

  admissibility gates
       |
  typed sector fields
       |
       +-- operator / routed composition / full words
       |
       +-- Lie generators / brackets / Hall depth
       |
  branch-specific jets, walls, and promotion certificates
```

Compatible sectorization is the interface between the two layers. It is not
itself a new system. It is the operation that turns source data into a
Sectorized Observable Framework (SOF):

```text
source system
  -> admissibility or realization gate
  -> compatible sectorization
  -> registered operator and/or Lie/Hall families
  -> typed shadows, jets, and walls
```

The central mathematical question is not whether every system has the same
unqualified ladder. It is:

```text
After projection, matrix composition, route summation, and Lie
antisymmetrization, which information survives, which cancels, and which can
be promoted only under an additional certificate?
```

Boolean paths, routed products, full words, and Lie brackets are therefore
different objects. Graph-to-product nondegeneracy, no-cancellation conditions,
operator-to-Lie registration, closure saturation, and proxy-to-shadow control
are different promotion problems.

This interface is necessary for the RIME shadows.  Without sector projectors
there is no sector-to-sector support, no bridge product, no frozen pair, no
repair, and no accessibility wall as a change of sector-indexed data.  Global
observables may still exist, but the SOF shadows do not.  This is the
No-Sector No-Shadow principle. At the current stage this is a programmatic
principle, not a universal theorem.

This is the current clean separation:

| Layer | Status | Role |
|-------|--------|------|
| Structural Unity | classical | Wedderburn-Artin / character-theoretic block decomposition |
| Sectorization | interface | converts representation data into SOF data |
| Observable Transport Architecture | RIME contribution | studies typed operator/word and Lie/Hall branches, their information loss, jets, walls, and promotion certificates |
| Capability-Aware Compiler | Paper X contribution | emits only claims supported by declared carriers, policies, evidence, and checked derivations |
| Wall Records | Paper XI contribution | stores carrier-qualified wall deltas and derives record-level taxonomy profiles |
| Reporting Protocol | Paper XII contribution | serializes one declared realization as a versioned, alignment-ready SOF Report |
| Audit Comparison | Paper XIII contribution | aligns two reports and emits a sparse typed comparison object |
| Action Semantics | Paper XIV horizon | interprets immutable audit coordinates under an admitted `ActionContext` and `PolicyProfile` and stops at bounded candidates |

The novelty of RIME is not the existence of a semisimple block decomposition.
That is the classical input for representation-derived examples. The novelty
is the observable geometry above compatible sectorization: different
represented systems, quantum gate systems, graph systems, Markov systems,
control/PDE systems, and finite spectral-triple systems can be compared once
their sectors and observable families have been fixed.

The statement must remain claim-status gated. RIME does not identify operator
support, word accessibility, and Lie/Hall accessibility, and it does not prove
that one low-order signature determines every higher transport object. The
stable statement is:

```text
Sectorization and adapters are source-dependent.
The typed object and compiler interfaces are shared.
```

This is the philosophical version of the Paper X boundary: capability-sound
compilation is the theorem-level organizational object; the SOF Registry is
evidence architecture, not a universal dynamics theorem. Compiler soundness
also does not establish that an adapter is scientifically adequate.

The corresponding artifact chain is:

```text
typed SOF objects and findings
  -> .sofreport
  -> .sofaudit
  -> .sofaction
```

A report is realization- and profile-relative. An audit additionally requires
explicit alignment and comparison policies. An action artifact additionally
requires an admitted `ActionContext` and applicable `PolicyProfile` and stops
at bounded candidates. Selection, authorization, observation, and effect use
separate downstream contracts. No downstream artifact changes the mathematical
meaning of an upstream carrier.

Stronger completion statements belong to branch-qualified promotion programs.
For example, graph paths require image--kernel nondegeneracy to promote to
routed products, routed terms require cancellation control to promote to full
words, and low-order Lie supports require declared richness and closure
hypotheses to constrain `D_Lie`. Paper VII supplies a local incidence and
rank-protection interface only; it does not establish any stronger common SOF
promotion principle.

This also fixes the relation to adjacent representation-rigidity projects.  A
project such as W33 may be viewed as a parallel world in which a concrete finite
combinatorial object is resolved into representation-theoretic rigidity.  RIME
adopts the same philosophy of finite represented laboratories, but asks a
different mathematical question: not how representations decompose, but how
observable transport emerges, deforms, and admits stable promotion under
explicit hypotheses above that decomposition.
