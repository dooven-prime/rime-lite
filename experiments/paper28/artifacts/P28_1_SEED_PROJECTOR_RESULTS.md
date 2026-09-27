# P28.1 `4+35` Seed Projector Results

## Status

This note records the first deterministic output of the Paper XXVIII
mechanism projector. It is fixed-scope evidence for quotient design, not an
all-`n` mechanism theorem.

The source relation is constructed without reading low-rank success. Exact
`P_1/P_2/P_3` membership is evaluated only after each receipt exists.

## 1. Scope

The input consists of:

- four fixed-`n=6` Type-II-only section contexts;
- thirty-five fixed-`n=7` extremal carrier contexts.

Every tied endpoint-shortest admissible Type-I/II receipt is retained. The
projector then closes the targets strictly downward through ranks three and
two so that exact successor composition is a nonempty binary relation.

| quantity | count |
| --- | ---: |
| seed contexts | 39 |
| seed receipts | 4,250 |
| low-rank closure receipts | 7,002 |
| all exact receipts | 11,252 |
| exact compatibility edges | 13,054 |
| Type-I receipts | 1,634 |
| Type-II receipts | 9,618 |

The seed receipts split as follows.

| surface | Type I | Type II | total |
| --- | ---: | ---: | ---: |
| `n=6` four-context section | 3 | 65 | 68 |
| `n=7` thirty-five-context carrier | 132 | 4,050 | 4,182 |

The three `n=6` Type-I receipts do not contradict the Type-II-only theorem:
none lands in the exact low-rank base. The projector retains admissible
receipts before applying that evaluator.

## 2. Unary Observable Audit

The first quotient matrix gives three levels.

### Skeleton level

The following observables descend to the proposed mechanism skeleton:

- source/target rank and packet partition;
- corridor count and rank-drop vector;
- fusion mass pattern;
- residual tail budget.

The tail budget descends here because it is determined by the retained target
partition on this scope.

### Accounting-only level

The following descend to the accounting refinement but not to the skeleton:

- corridor lengths;
- corridor surpluses;
- debt profile;
- total surplus.

This is the first direct evidence for separating the interaction-skeleton
layer from its credit refinement.

### Exact-relation level

The following do not descend through the accounting quotient:

- exact source packet identity;
- exact fusion packet identity;
- exact ancestry update;
- exact target transport channel;
- the hostile evaluator `target_in_exact_P_le3`.

The last item is not proposed as quotient data. Its failure is a control
showing that neither future success nor a selected witness has leaked into the
future-free keys.

## 3. Composition Congruence

Exact composition is defined by equality of the typed target context of one
receipt with the typed source context of the next, including the outgoing
distinguished ancestry packet.

| quotient | source fibers | noncongruent fibers | nonempty mismatches |
| --- | ---: | ---: | ---: |
| accounting | 250 | 103 | 69 |
| skeleton | 30 | 9 | 8 |

Thus neither proposed quotient is a semantic composition congruence on this
seed closure. Even successor nonemptiness fails to descend. Accounting
addition can therefore coexist with exact-relation-valued semantic
composition:

\[
 \boxed{
  \text{interaction skeleton layer}
  +\text{ accounting refinement}
  +\text{ exact typed realization fiber}.}
\]

This is a positive layer-separation result, not a failure of P28.1. Any later
coarser composition interface must add a proved liftability relation; it may
not infer one from equal accounting tuples.

The follow-up boundary audit does not add fields to either mechanism key. It
tests the target boundary separately and is recorded in
[`P28_1B_BOUNDARY_LIFTABILITY_RESULTS.md`](P28_1B_BOUNDARY_LIFTABILITY_RESULTS.md).

## 4. Reproducibility

The canonical artifact is
`results/paper28_seed_mechanism_catalog_v1.json.gz`. It contains 11,252 exact
receipt records and uses deterministic gzip bytes. Its validator reconstructs
the complete relation from the two bound Paper XXVII inputs, verifies every
receipt digest, rebuilds every compatibility edge, and recomputes both audit
matrices.

The sidecar `paper28_seed_mechanism_catalog_v1.receipt.json` binds the artifact,
the two released inputs, and the local transitive source closure. Its mode is
`LOCAL_REPLAY_WITH_BOUND_RELEASE_INPUTS`; no independent implementation is
claimed.

The current input SHA-256 bindings are:

- `n=6`: `e52a2dbad23ee8c86c18779de97e9bd129f45fe2f984a3772f89a2cb963deaa9`;
- `n=7`: `129cbcbbe97e9af95673ce9e5716bfeea9e1a29f1a6c56e716ba135561142f65`.

No `n=8` state, historical common-witness cache, or outcome-derived menu is
read by the projector.
