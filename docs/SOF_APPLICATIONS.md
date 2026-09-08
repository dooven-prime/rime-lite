# SOF Application Admission and Routing

**Status:** public explanatory companion to Papers X and XII. This document
summarizes how domain sources enter the typed SOF interfaces. It is not a
schema, a Registry snapshot, a theorem source, or an application catalogue.

An application is admitted claim by claim. A domain name alone does not make
a source a strict SOF realization, and one admitted diagnostic does not grant
the source every SOF carrier or conclusion.

## Application Route

The stable route is:

```text
domain source + source snapshot
  -> application adapter
  -> realization declaration + capability manifest
  -> strict SOF or diagnostic analogue admission
  -> Typed SOF IR
  -> profile-gated CompilerOutput
  -> realization-relative SOF Report
```

The adapter translates domain data into declared typed objects. It does not
gain authority to manufacture a missing carrier, infer an undeclared
trajectory, or promote an observation into a theorem.

## Admission Record

An application admission should identify, as applicable:

1. a stable application and source-snapshot identity;
2. adapter identity, version, and source provenance;
3. `strict_sof` or `diagnostic_analogue` realization kind;
4. marked sectorization and its construction or selection basis;
5. labelled operative alphabet and operator convention;
6. declared route, word, closure, Lie/Hall, deformation, or comparison
   capabilities;
7. cutoff, saturation, threshold, norm, alignment, and policy conventions;
8. evidence references and reader-facing claim status;
9. unavailable capabilities and negative interpretation boundaries.

Claim status belongs to each declared result. It is not a property of the
application species as a whole.

## Strict and Analogue Branches

A strict realization supplies validated finite data of the form

```text
(V, {Q_i}, Y)
```

with marked sectors, a labelled operative alphabet, and the conventions
required by each enabled carrier. It may instantiate only the theorems whose
hypotheses and promotion conditions it satisfies.

A diagnostic analogue supplies source provenance, declared descriptors, an
analogue mapping, and an explicit negative strict boundary. It may support
observable comparison without claiming a projector-based SOF realization or
instantiating strict-SOF theorems.

The two branches are mutually exclusive for one admitted report:

```text
strict_sof != diagnostic_analogue
```

## Capability-Local Claims

Applications declare sparse capabilities. Missing capability is not zero,
infinity, failure, or nonexistence:

```text
NOT_DECLARED
  != zero
  != UNREACHED_AT_CUTOFF
  != NOT_APPLICABLE
  != mathematical nonexistence
```

In particular:

- graph reachability does not supply routed operator composition;
- routed composition does not supply full-word support without cancellation
  control;
- positive-word, star-word, and sector-enriched closures are distinct;
- an operator family does not silently supply a Lie/Hall carrier;
- a sampled trajectory does not establish exact depth or saturation;
- an external first-hitting time is not automatically SOF route or word depth.

Dynamic claims additionally require a declared deformation parameter,
coherent identity or comparison maps across the parameter domain, and the
policy under which a response, wall, or threshold event is evaluated.
Recomputing sectors independently at each sample does not by itself provide a
tracked sector trajectory.

## Evidence and Promotion

An application result can enter public Registry or paper evidence only through
an owned, source-addressed promotion:

```text
source snapshot + adapter + declared contracts
  -> typed result artifact
  -> validation receipt
  -> Registry finding or paper-owned evidence record
```

The promotion must bind the claim's actual semantic and execution subclosure.
A passing schema validator establishes contract conformance only. It does not
establish adapter adequacy, causal attribution, scientific truth, or universal
applicability.

The machine-readable Registry remains authoritative for admitted row
membership, capabilities, values, and evidence references. Concrete scripts,
fixtures, censuses, and quantitative results belong to their owning
`experiments/` packages and are not duplicated here.

## Ownership Boundary

| Concern | Owner |
|---|---|
| static SOF object and carrier semantics | Paper VIII and `SOF_OBJECTS.md` |
| deformation, trajectory, wall, and response semantics | Paper IX and `SOF_DEFORMATIONS.md` |
| capability-aware compilation and Registry evidence | Paper X and `SOF_REGISTRY.md` |
| single-report assembly and strict/analogue deployment | Paper XII |
| alignment and pairwise comparison | Paper XIII |
| context/policy interpretation and bounded candidates | Paper XIV |
| reference adapters, execution, validation, and services | `sof-runtime` |

The normative manuscripts, contracts, and accepted evidence remain in
[`rime-lite`](../README.md). Reference adapters and operational demonstrations
belong in [`sof-runtime`](https://github.com/dooven-prime/sof-runtime). A
runtime implementation becomes normative only after explicit source-addressed
promotion into this repository.

## Related Public Guides

- [SOF Objects](SOF_OBJECTS.md)
- [SOF Deformations](SOF_DEFORMATIONS.md)
- [SOF Registry](SOF_REGISTRY.md)
- [SOF Protocol Stack](SOF_PROTOCOL_STACK.md)
- [Paper-owned experiments](../experiments/README.md)
