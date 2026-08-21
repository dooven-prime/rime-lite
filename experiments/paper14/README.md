# Paper XIV Experiment Layout

This directory supports the published Paper XIV v2.0 contract, its retained
release evidence, and the v2.1 Candidate Non-Execution revision candidate. The
immutable publication identity is listed in the repository's root release
table.

The current implementation is:

- `action_engine.py`: ActionContext/PolicyProfile admission, interpretation records, and candidate generation;
- `action_workbench.py`: controlled Paper XIII-to-XIV artifact generation;
- `validate_sofaction.py`: predicate recomputation, receipt/digest closure, projection preservation, and cross-field validation;
- `schemas/sofaction/validation-receipt-v2.0.schema.json`: source-addressed validation-receipt contract implemented by downstream runtimes;
- `migrate_sofaction_v2_to_v2_1.py`: explicit v2.0-to-v2.1 boundary migration;
- `validate_sofaction_v2_1.py`: v2.1 semantic, closure, and receipt-role validator;
- `policy_selector.py`: illustrative downstream control outside the canonical contract;
- `results/`: published v2.0 `.sofaction` artifacts;
- `results/v2.1/`: 29 migrated candidate-only artifacts and conformance-only receipts.

The current workbench reads 28 migrated Paper XIII audits and one native
GridWorld F4 audit. Migrated coordinates remain `UNRESOLVED` or
`NOT_DECLARED`; they produce no affirmative candidates. The native audit can
produce only policy-relative review candidates under the declared profile.

Candidate records use `intended_diagnostic_consequence`; this is a target for a
later audit, not an identified causal effect or outcome prediction. Every
candidate records `declared_risk_considerations`, reversibility, evidence
references, carrier, and a non-authorizing state. Current v2 candidates cannot
self-declare `authorized`.

Policy Predicate Language v1.0 is a closed AST. It permits only declared
Boolean, coordinate, context, constraint, transformation-contract, and policy-
basis operations. Validation recomputes predicate outcomes and candidate closure
from the stored inputs; unknown operations, dynamic field paths, free-text
inference, bare evidence strings, and implicit coercion of unavailable states
are rejected.

Canonical `.sofaction` artifacts stop at `candidate_action_set` and an explicit
`disposition_result`. `NoDisposition`, `UnresolvedDisposition`, and
`NoActionDisposition` are distinct. Optional selection belongs to a separate
downstream plan artifact and is not embedded in `.sofaction`.
The current schema owns only policy-conformance and decision-trace records.
Selected plans, authorization receipts, executor records, post-action
observations, and causal effect certificates remain external artifacts. Paper
XIV does not define their wire names or contracts.

SOFAction v2.1 fixes `execution_boundary` as a required constant object.
Selection, authorization, execution, outcome, and effect semantics are out of
scope for `.sofaction`. A candidate's non-authorizing process state is not
authorization evidence, and `authority.status = verified` does not grant a
candidate-specific authorization. The v2.1 validation receipt has
`receipt_kind = SOFACTION_VALIDATION_RECEIPT` and certifies protocol
conformance only; even a `PASS` receipt cannot substitute for authorization or
execution evidence.

The v2.1 contract is not migration-only: a native candidate artifact must bind
its generation implementation and nonempty input closure and receives a
native-specific validation receipt. The retained 29-artifact candidate corpus
uses explicit v2.0 migration.

The source-addressed results and receipts are release evidence; figures remain
derived summaries rather than independent evidence.

Historical v2.0 action inputs resolve by their declared digest. If the current
Paper XIII path contains a successor v2.1 artifact, the validator uses the
registered `release-snapshots/rime-lite-v2.0/` byte snapshot instead. A missing
or mismatched current and snapshot byte is rejected; historical v2.0 artifacts
are never rewritten or re-signed.

## Run

From the repository root:

```bash
python experiments/paper14/action_workbench.py --output-dir tmp/paper14-v2-replay
python experiments/paper14/validate_sofaction.py
python experiments/paper14/migrate_sofaction_v2_to_v2_1.py
python experiments/paper14/validate_sofaction_v2_1.py --write-receipts
python -m pytest tests/test_sof_action.py -q
```

`archive/sofdecision/` preserves the superseded decision-engine prototype and
its records. It is provenance only and is not part of the Paper XIV claim or
reproducibility path.
