# Paper XIV Experiment Layout

This directory supports the current unpublished Paper XIV draft. The
manuscript, v2 schema, implementation, generated artifacts, and hostile focused
tests use the same SOFActionObject interface. Paper XIV has no published or
frozen release identity.

The current implementation is:

- `action_engine.py`: ActionContext/PolicyProfile admission, interpretation records, and candidate generation;
- `action_workbench.py`: controlled Paper XIII-to-XIV artifact generation;
- `validate_sofaction.py`: independent predicate replay, receipt/digest closure, projection preservation, and cross-field validation;
- `schemas/sofaction/validation-receipt-v2.0.schema.json`: source-addressed validation-receipt contract implemented by downstream runtimes;
- `policy_selector.py`: illustrative downstream control outside the canonical contract;
- `results/`: generated v2 `.sofaction` artifacts.

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
basis operations. The producer and validator execute separate implementations;
unknown operations, dynamic field paths, free-text inference, bare evidence
strings, and implicit coercion of unavailable states are rejected.

Canonical `.sofaction` artifacts stop at `candidate_action_set` and an explicit
`disposition_result`. `NoDisposition`, `UnresolvedDisposition`, and
`NoActionDisposition` are distinct. Optional selection belongs to a separate
downstream plan artifact and is not embedded in `.sofaction`.
The current schema owns only policy-conformance and decision-trace records.
Selected plans, authorization receipts, post-action observations, and causal
effect certificates are reserved for future `.sofplan`, `.sofauth`,
`.sofoutcome`, and `.sofeffect` contracts.

Figures and PDF builds remain draft artifacts until a release is declared.

## Run

From the repository root:

```bash
python experiments/paper14/action_workbench.py
python experiments/paper14/validate_sofaction.py --write-receipts
python -m pytest tests/test_sof_action.py -q
```

`archive/sofdecision/` preserves the superseded decision-engine prototype and
its records. It is provenance only and is not part of the Paper XIV claim or
reproducibility path.
