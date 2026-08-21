# Paper XV Artifact and Claim Map

This directory supports the initial Paper XV manuscript, *Corrigible Structural
Interfaces*. The paper is a theorem-and-interface position paper. It introduces
no computational census, numerical observation, released wire contract, or
runtime implementation.

The manuscript closes the numbered SOF protocol line. Later contextual and
descent mathematics is independently scoped; it is not a successor protocol
package and does not extend the Paper XV tuple with execution-stage objects.

## Reader Entry Points

- Manuscript: [`papers/paper15/Paper XV.md`](../../papers/paper15/Paper%20XV.md)
- Reader PDF: [`papers/paper15/paper15_arxiv.pdf`](../../papers/paper15/paper15_arxiv.pdf)

The manuscript owns the definitions and propositions. This README records their
artifact and evidence posture; it is not an additional source of semantic
authority.

## Owned Interface

```text
EpistemicState
  + EvidenceUpdate admitted under active AdmissionPolicy
  + active RevisionPolicy
    -> proposed EpistemicState'
    + proposed RevisionRecord
    + SupersessionMap
    + RevalidationObligation
    -> conformance validation
    -> explicit activation basis
    -> current EpistemicState'
```

The interface is informational. It does not select, authorize, or execute an
object-level action. `EpistemicState.K` contains typed current-use commitment
entries, not artifact identities. A commitment entry binds an immutable
`subject_ref` to a role, scope, and validation basis.

## Claim Ledger

| Claim ID | Statement | Manuscript label | Evidence level | Basis | Manuscript location |
|---|---|---|---|---|---|
| `P15-T01` | provenance history is append-only while current commitments may be withdrawn or replaced | Proposition | Theorem | proof under the declared revision construction | Provenance-Monotone, Commitment-Nonmonotone Principle |
| `P15-T02` | supersession preserves prior bytes and declared historical semantic binding while successor entries may reuse the same immutable subject | Proposition | Theorem | proof under the declared revision construction | Non-Retroactive Semantic-Binding Principle |
| `P15-T03` | dependents of a superseded current-use binding do not inherit current validity without a successor validation binding | Proposition | Theorem | proof under declared normative dependencies | Revalidation Obligation |
| `P15-T04` | feedback, challenge, and revision artifacts have no authorization or object-transition codomain | Proposition | Theorem | type-level proof under the declared interface | Feedback Non-Authority |
| `P15-T05` | current epistemic commitments need not stabilize without additional structure | Proposition | Theorem | explicit alternating construction | No Convergence Without Additional Structure |

Definitions, the six position principles, shadow revision, contestability, and
the finite boundary examples are not additional evidence claims. The Outlook
records open questions about convergence hypotheses, epistemic-state
equivalence, dependency-scoped revalidation, and independently scoped
contextual/descent mathematics; it does not announce another protocol stage.

## Evidence Posture

No paper experiment is required. The alternating revision sequence and the
shadow-revision example are mathematical constructions, not numerical
observations. The boundary figure is explanatory and carries no independent
evidence status.

Paper XV therefore publishes no Computational Certificate or Computational
Observation. A runtime replay, JSON Schema, Registry row, or machine receipt
would not strengthen the current theorem claims merely by existing. Any later
machine representation must be separately scoped and must preserve the
five-object interface and its authority boundary.

## Maintainer Notes

- Edit the canonical Markdown manuscript; do not edit generated TeX or PDF by
  hand.
- Dated manuscript snapshots are archival drafts and should not enter the
  release artifact closure.
- Do not add an experiment, schema, validator, receipt, or Registry row solely
  to make this directory resemble Papers XII--XIV.
- Internal construction checks may test the declared invariants, but they are
  not independent validation or scientific evidence.
- Later serialization or runtime support is maintenance of this interface, not
  a successor numbered protocol. This paper allocates no selected-plan,
  authorization, execution, outcome, or effect contract.

## Negative Boundary

- `ObjectState` and `EpistemicState` are different types.
- Artifact identity and a current-use commitment binding are different types.
- `SupersessionMap` is a finite typed relation and may record split or merge
  succession without rewriting subject artifacts.
- New evidence must be admitted under the active admission policy before it can
  trigger normative revision.
- Admission and revision policies require active current-use bindings; a
  revision cannot select a convenient policy ad hoc.
- Recency does not establish truth or priority.
- A revision reason does not identify a cause of object change.
- Audit mismatch does not imply object defect, repair, or intervention.
- Feedback and challenge do not imply selection or authorization.
- Prior artifacts retain their bytes and declared historical semantic binding
  after supersession.
- `SUPERSEDED` does not mean false or invalid at creation.
- A proposal remains non-current until both its conformance receipt and an
  explicit activation basis are present; conformance alone grants no
  currentness authority.
- Typed replay does not imply convergence to truth or a global optimum.
