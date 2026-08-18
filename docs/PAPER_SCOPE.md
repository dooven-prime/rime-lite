# Paper Scope

This file is the public ownership and scope ledger for the RIME paper series.
It identifies the object and reader question owned by each paper without
repeating manuscript definitions, numerical tables, or release metadata.

The current public release contains Papers I--XIV. CCS v2.1 is an optional
non-paper archive. Publication identities and DOIs are maintained only in the
root [Public Release table](../README.md#public-release).

The current typed stack includes the frozen Registry v2.0 snapshot and the
published SOFRS v2.0, SOFAUDIT v2.0, and SOFAction v2.0 contracts. Retained v1
artifacts remain immutable. Semantic changes to published contracts require a
versioned reopening rather than a silent documentation edit.

For the narrative architecture, see [PROGRAM_MAP.md](PROGRAM_MAP.md). Detailed
Papers I--VII interfaces and promotion limits are indexed in
[PRE_SOF_INTERFACE_MAP.md](PRE_SOF_INTERFACE_MAP.md). Canonical Rubik numerical
invariants are maintained in [CORE_INVARIANTS.md](CORE_INVARIANTS.md).

## Public Scope Matrix

| Paper | Owned object or interface | Reader question |
|-------|---------------------------|-----------------|
| I | `A_18` and its block spectral layers | What is the blockwise canonical spectrum, and which conditional arithmetic criteria apply? |
| II | QT/HT sectors and registered direct transport | Why does the resolved sector graph have its observed structure? |
| III | direct support graph and projected matrix composition | Why can graph reachability fail to compose at operator level? |
| IV | fixed finite collision arrangements and conditional operator registration | How do affine-branch collisions form quotient layers, and when does an operator realization inherit that quotient? |
| V | direct support, projected products, commutator support, and cutoff Lie depth | Why does Boolean support fail to determine commutator accessibility? |
| VI | linearized commutativity/normality constraints and pointwise typed registrations | Which tangent directions preserve the declared constraints, and which samples pass the spectral gates? |
| VII | incidence geometry, rank protection, and promotion limits | When do nonzero projected factors compose? |
| VIII | marked static SOF objects, typed filtrations, and strict morphisms | What is the sectorized observable object, and what is preserved under strict morphisms? |
| IX | typed dynamic fields, deformation charts, and observable trajectories | Which typed SOF fields can be compared continuously, and where can their walls occur? |
| X | capability-aware compilation theory and Registry evidence | Which claims may be compiled without manufacturing evidence or crossing carrier boundaries? |
| XI | typed wall records, profile-relative coordinates, multi-label taxonomy, and local-model eligibility | How can admitted wall data be organized without redefining walls or assigning an intrinsic type to the source system? |
| XII | versioned single-report protocol and epistemic boundary (`SOFRS`) | What does a compiled report represent, and what remains the adapter's responsibility? |
| XIII | Audit Profiles, explicit alignment, sparse comparison maps, and fixed-frame pseudometrics (`SOFAUDIT`) | How can two reports be compared without manufacturing unavailable coordinates or treating difference as defect? |
| XIV | admitted context/policy interpretation and bounded candidate dispositions (`SOFAction`) | Which interpretations and candidates follow under one explicit `ActionContext` and `PolicyProfile`? |

The matrix is thematic, not a theorem dependency order. A neighboring result
can be reused only after the receiving paper redeclares its object, hypotheses,
realization, and claim status.

## Protocol Ownership

```text
typed SOF objects and findings
  -> CompilerOutput
  -> .sofreport
  -> .sofaudit
  -> .sofaction
  -> STOP
```

Paper X owns capability/evidence guards and claim compilation. Paper XII owns
one realization-relative report. Paper XIII owns pairwise alignment and sparse
comparison. Paper XIV owns policy-relative interpretation and bounded
candidates. The detailed machine handoff is summarized in
[SOF_PROTOCOL_STACK.md](SOF_PROTOCOL_STACK.md).

A `.sofaction` does not own selection, recommendation, authorization,
execution, outcome observation, or causal effect. Those concepts require
separate downstream contracts and cannot be imported backward into SOFAction,
SOFAUDIT, or SOFRS.

## Promotion Boundaries

- Spectral layers, registered sectors, direct support, routed composition,
  full words, commutators, and Lie depth are distinct typed objects.
- A graph path is not a projected composition witness.
- A numerical agreement is not exact equality without the required proof or
  certificate.
- A proxy trajectory is not a binary support or depth result without a
  proxy-to-shadow theorem.
- A schema-valid report does not establish adapter or domain adequacy.
- An aligned mismatch does not establish reference truth, defect, or severity.
- A bounded candidate is not a selected, authorized, or executed action.
- A validation receipt is evidence of declared artifact closure, not a
  scientific result state.

## CCS v2.1 Boundary

CCS v2.1 is optional reproducibility, observation, open-problem, and historical
archive material. It is not a paper, theorem source, semantic authority,
executable certificate, or prerequisite for Papers I--XIV. Its canonical
public source is [ccs/canonical_specification.md](../ccs/canonical_specification.md).

## Out of Scope

This repository does not study cube-solving algorithms, Kociemba search,
pruning tables, BFS or IDA*, sticker rendering, or neural cube solvers. It does
not claim results for all finite groups or all noncommutative representations
unless a manuscript explicitly states the required hypotheses and evidence
level.

## Authority Boundaries

Authority is typed rather than represented by one universal precedence list:

- **Semantic authority:** the owning versioned manuscript determines
  definitions, hypotheses, theorem statements, ownership, and claim
  boundaries. Public companions summarize but do not replace it.
- **Evidence authority:** declared source inputs, the owning versioned result
  record, and its passing validator determine public numerical values,
  censuses, digests, and computational certificates.
- **Release-identity authority:** a published Zenodo record fixes the title,
  authorship, version, deposited files, DOI, and date of that release. The root
  release table indexes those identities.

A disagreement between manuscript prose and owning evidence blocks a new
release. Internal notes, archive placement, runtime execution, and passing
transport tests cannot promote a claim or mutate a published contract.

## Companion Routing

| Scope | Public companion |
|-------|------------------|
| Papers I--VII interfaces and promotion limits | [PRE_SOF_INTERFACE_MAP.md](PRE_SOF_INTERFACE_MAP.md) |
| Paper VIII static object layer | [SOF_OBJECTS.md](SOF_OBJECTS.md) |
| Paper IX deformation layer | [SOF_DEFORMATIONS.md](SOF_DEFORMATIONS.md) |
| Paper X Registry evidence architecture | [SOF_REGISTRY.md](SOF_REGISTRY.md) |
| Papers X--XIV machine-contract handoff | [SOF_PROTOCOL_STACK.md](SOF_PROTOCOL_STACK.md) |

These companions are navigation and explanation layers. They do not replace
the owning manuscripts, schemas, source-addressed evidence, or release records.
