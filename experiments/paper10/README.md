# Paper X Experiments

This directory supports the capability-aware admission examples, frozen
Registry v2.0 evidence, and the separate Registry v2.1 candidate used by Paper
X. It does not establish one common dynamics across species, and no script may
populate a carrier that its realization does not declare.

## Current Evidence

| Artifact | Typed role | Claim status |
|----------|------------|--------------|
| `../paper9/calibrated_response.py` | Paper IX-owned calibrated response fixture imported into one Registry row | inherited Theorem/Computational Certificate; Paper X registers the finding but does not compile or re-own the dynamic result |
| `rubik_wild_type34_audit.py` | counts commutator cancellations and routed image--kernel incidences for the declared Rubik Lie family | Computational Certificate; the historical filename is retained for Registry v1 path compatibility |
| `ncg_spectral_triple_sof.py` | checks the central Connes-distance obstruction and two ordered routed bridges | finite certificate/observation package; no distance-repair theorem |
| `control_pde_combinatorial_sof.py` | records direct and positive-word findings for three sector origins | typed portability diagnostics; no Lie/Hall carrier |
| `barrier_option_sof.py` | records labelled cross-barrier blocks and a separate CTMC first-hit proxy | Computational Observations; first-hit time is not SOF depth |
| `markov_graph_sof.py` | registers a three-state Markov operator and six-vertex path graph with positive-word support and exact word depth | Computational Certificates; no Lie/Hall carrier |
| `tau_quantum_graph_yang.py` | audits declared quantum, graph, and Yang-like proxy trajectories | boundary Computational Observations; no proxy-to-shadow promotion |
| `validation/build_results.py` | compiles six source fixtures into `results/registry_evidence_v2.json` | versioned source-data producer |
| `validation/build_results_v2_1.py` | compiles the current source closure into `results/registry_evidence_v2_1.json` without rewriting v2.0 evidence | Registry v2.1 candidate producer |
| `validation/build_legacy_certificate_imports.py` | imports two source-addressed certificate values from the immutable v1 snapshot and freezes the quantum carrier registration | migration certificate producer, not a fresh scientific recomputation |
| `validation/validate_results.py` | checks current finite invariants and the Registry v2.0 artifact binding | release validator |

The Paper X result builders consume six paper-local Registry probes plus the
Paper IX calibrated-response fixture. The authoritative machine-readable
cross-species records are the frozen
`registry/paper10-typed-v2.0.registry.json` and the separate v2.1 candidate.
The paper-local result JSON files are source-data records injected into those
snapshots, not second Registry catalogues. The v2.1 builder writes a separate
candidate result so current source digests never rewrite v2.0 evidence.

## Verification

Read-only validation checks the immutable v1 and v2.0 snapshots and the current
v2.1 candidate:

```bash
python registry/validate_snapshot.py
python tests/test_registry_migration.py
```

The migration regression binds the frozen predecessor bytes, rebuilds the
v2.1 object in memory, and requires canonical equality with the committed
candidate. It does not rewrite a Registry snapshot.

The older Paper X scientific audit remains scoped to the frozen v2.0 evidence
record:

```bash
python experiments/paper10/validation/validate_results.py
```

Recompute its finite scientific fixtures explicitly with:

```bash
python experiments/paper10/validation/validate_results.py --recompute
```

The proxy-boundary recomputation is a further opt-in:

```bash
python experiments/paper10/validation/validate_results.py --include-slow
```

## Candidate Rebuild

Rebuilding is a separate mutating operation. It writes only the v2.1 candidate
paths and never rewrites the frozen v1, v2.0, or legacy-import artifacts:

```bash
python experiments/paper10/validation/build_results_v2_1.py
python registry/migrate_v1_to_v2.py
```

Individual scripts remain executable for claim-facing output. All response
times are relative to their declared trajectory, normalization, norm, and
threshold policy. `unreached` is cutoff-relative and is never exact infinity.
The migrated quantum repair certificate is bound to registration
`quantum.gates.principal-log-skew.hall-v1`; its generator extraction, Hall
indexing, tolerance, and pair scope are recorded in
`results/legacy_certificate_imports_v2.json`.

## Archive

`archive/registry_evidence.py` is the retired v1 monolithic summary. It mixes
historical terminology and stale aggregate comparisons, so it is provenance
only and must not support Registry v2.0 findings.
