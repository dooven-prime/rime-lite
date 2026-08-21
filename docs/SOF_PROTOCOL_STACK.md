# SOF Protocol Stack

**Status:** public companion to the published machine-contract interfaces of
Papers X and XII--XIV. The owning manuscripts and versioned schemas remain the
authorities for definitions, admissibility, and claim boundaries.

This document summarizes the handoff between compilation, reporting,
comparison, and interpretation. It is not another contract and does not add a
workflow stage.

## Contract Chain

```text
Paper X
  Capability Manifest
  + Typed SOF IR
  + Compiler Report Profile
  + derivation-rule registry
    -> CompilerOutput

Paper XII
  CompilerOutput
  + Assembly Profile
    -> SOFRS

Paper XIII
  receipt-validated SOFRS reference
  + receipt-validated SOFRS target
  + explicit alignment Phi
  + comparison specification Theta
  + Audit Profile
    -> SOFAUDIT

Paper XIV
  receipt-bound SOFAUDIT projection
  + ActionContext
  + PolicyProfile
    -> InterpretationRecord set
    -> explicit disposition
    -> bounded CandidateActionSet
    -> STOP
```

Paper XI wall morphology may enter compiler and report records through its
owned typed fields and evidence. It does not redefine compiler admission,
single-report assembly, pairwise alignment, or downstream interpretation.

## Ownership

| Layer | Owns | Does not own |
|-------|------|--------------|
| Compiler | capability declarations, Typed SOF IR, profile-gated claim emission, and `CompilerOutput` | adapter scientific adequacy or report serialization |
| SOFRS | one realization-relative report, faithful assembly, provenance, and report validation receipt | pairwise alignment, difference, defect, or action semantics |
| SOFAUDIT | explicit report alignment, profile-selected sparse coordinates, and comparison states | reference truth, defect attribution, severity, or candidate generation |
| SOFAction | admitted context/policy interpretation, deterministic rule replay, dispositions, and bounded candidates | selection, recommendation, authorization, execution, outcome, or effect |

Each layer consumes immutable upstream artifacts or typed objects. A downstream
artifact cannot rewrite the upstream report or audit from which it was formed.

## Authority Boundary

```text
valid report       does not imply adequate realization
recorded difference does not imply defect
bounded candidate  does not imply selection
selection          does not imply authorization
authorization      does not imply execution or effect
```

Protocol validation establishes only the declared contract and artifact
closure. Object-level or scientific claims require their own admitted evidence
and certificate class.

The current public machine protocol stops at bounded candidates. `.sofplan`,
`.sofauth`, `.sofexec`, `.sofoutcome`, and `.sofeffect` are not published
contracts, and their names do not announce successor stages in this
repository. Paper XV closes the numbered protocol line through an epistemic
revision position interface; it is not another wire-contract stage.

## Runtime and Transport Boundary

[`rime-lite`](../README.md) owns the normative manuscripts, versioned
contracts, accepted evidence, and publication identities. The separate
[`sof-runtime`](https://github.com/dooven-prime/sof-runtime) repository provides
reference execution, validation, adapters, and service orchestration. Stable
runtime semantics become normative only after explicit source-addressed
promotion into this repository.

Python, CLI, HTTP, and MCP are transport or API projections over runtime
operations. They do not add SOF semantics, change artifact identity, infer
alignment or policy inputs, or extend SOFAction beyond bounded candidates.

## Canonical Sources

- Compiler contracts: [`schemas/sofcompiler/`](../schemas/sofcompiler/)
- SOFRS: [`schemas/sofrs/`](../schemas/sofrs/)
- SOFAUDIT: [`schemas/sofaudit/`](../schemas/sofaudit/)
- SOFAction: [`schemas/sofaction/`](../schemas/sofaction/)
- Contract index and validation entry points: [`schemas/README.md`](../schemas/README.md)
- Paper-owned evidence routing: [`experiments/README.md`](../experiments/README.md)
