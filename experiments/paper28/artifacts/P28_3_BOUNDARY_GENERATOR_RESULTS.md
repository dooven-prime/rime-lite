# P28.3 Boundary-Relational Generator Factorization

## Status

This note records a fixed-scope factorization of the canonical Paper XXVIII
`4+35` exact-receipt relation. It does not enumerate new automata, contexts,
or exits. It consumes
`results/paper28_seed_mechanism_catalog_v1.json.gz` and exactly replays every
stored source-addressed word.

The result is a generator **cover on the declared seed closure**, not an
all-rank taxonomy, a unique factorization theorem for mechanism classes, or a
composition law on bare generator names.

## Boundary-relational object

Let `x` be one exactly replayed local operation. Its abstract row is

\[
 b^-x \xrightarrow{\ g(x),\ a(x)\ } b^+x,
\]

where:

- `b^-x,b^+x` retain the action and normalized mass placement;
- `g(x)` is an interaction generator;
- `a(x)` records length, maturity gain, surplus, incoming/outgoing debt, and
  source/target budget;
- the realization fiber retains the exact packet placement, distinguished
  packet, word segment, receipt, corridor, and operation indices.

The local boundary space is certified by exact replay with carried accounting.
Stored section/completion source and target contexts form a distinguished
subset of it. Internal operation boundaries are not silently identified with
section-certified checkpoints.

Composition is therefore typed:

\[
 b_0\xrightarrow{g_1,a_1}b_1
 \xrightarrow{g_2,a_2}b_2,
\]

and requires equality of the intermediate exact typed state. No unconditional
product `g_2g_1` is defined.

## Canonical word factorization

Every corridor word is split at maximal rotation blocks and defect letters:

| generator | exact word segment | rank behavior |
| --- | --- | --- |
| `TRANSPORT` | one nonempty maximal `p^a` block | rank preserving |
| `RETURN` | one `d` | rank preserving |
| `FUSION` | one corridor-terminal `d` | one binary strict drop |

For a fixed stored exact word this split is canonical. It says nothing about
uniqueness among different tied endpoint-shortest words.

The full replay gives:

\[
11252\text{ receipts}
\longrightarrow
123240\text{ exact operation occurrences},
\]

with

\[
\boxed{
49656\ \mathrm{TRANSPORT}
+52714\ \mathrm{RETURN}
+20870\ \mathrm{FUSION}.}
\]

All `11,252` stored endpoints, lengths, corridor surpluses, and receipt credit
allocations are recovered. Every corridor has exactly one terminal fusion.
The uncovered receipt set is empty.

## Generator Soundness

Grouping operation occurrences by

\[
(b^-,g,a,b^+)
\]

produces `24,355` boundary-relational rows:

| kind | relation rows | largest exact realization fiber |
| --- | ---: | ---: |
| `TRANSPORT` | 12,053 | 200 |
| `RETURN` | 8,113 | 336 |
| `FUSION` | 4,189 | 192 |

Every displayed row has a nonempty exact source-addressed realization fiber.
This proves fixed-scope generator soundness. It does not assert that every
formally writable row outside this observed relation is realizable.

The rows have `8,763` source boundary classes. A source boundary has at most
`32` decorated relation rows and at most two of the three interaction kinds in
this local relation. These figures are checksums for the seed closure, not B1
or B2 bounds for the recursive mechanism menu.

## Historical mechanism names after factorization

The operation cover separates interaction primitives from path/accounting
predicates.

| derived predicate | receipts |
| --- | ---: |
| one-corridor completion | 1,634 |
| two-corridor repayment | 9,618 |
| repeated-fusion heavy chain | 9,608 |
| rank-two `(5,2)` target choice | 106 |
| rank-two `(6,1)` target choice | 3,936 |
| zero-surplus `(5,2)` fallback | 87 |
| zero-surplus `(6,1)` heavy target | 1,020 |

In particular, repayment is not synonymous with heavy comb: ten repayment
receipts do not feed the first fresh fusion packet into the second fusion.
Likewise, fallback is a target/accounting allocation predicate rather than a
new interaction primitive. The fixed-scope identity

\[
20+7=12+15=27
\]

belongs to the zero-surplus `(6,1)`/`(5,2)` subfamilies already audited in
P28.2.

`B2` steering, bridge, and orbit closure are retained as exact
transport-return realization refinements. This audit does not yet prove a
normal-form theorem that identifies them with one another, so it does not
promote or eliminate them by name.

## Mathematical interpretation

On this seed surface, a smaller interaction basis is enough:

\[
\boxed{
\text{typed local boundary}
+\{\mathrm{TRANSPORT},\mathrm{RETURN},\mathrm{FUSION}\}
+\text{accounting decoration}
+\text{exact realization fiber}.}
\]

The named descent mechanisms are paths, constraints, or credit allocations in
this graph. Thus the current object is an exact typed compatibility graph with
an additive accounting cocycle, not a skeleton algebra.

## Replay

Produce the deterministic artifact and receipt:

```powershell
python experiments/synchronizing_automata/paper28_factor_boundary_generators.py
```

Recompute it from the canonical seed catalog:

```powershell
python experiments/synchronizing_automata/validation/validate_paper28_boundary_generator_factorization.py
```

The validator checks the fixed counts, exact endpoint and accounting replay,
nonempty realization fiber for every abstract row, zero residual receipts,
and byte-equivalence of the stored mathematical payload with a fresh full
recomputation.

## Claim boundary

This result establishes generator soundness and exact cover only for the
canonical `4+35` closure. It does not establish:

- all-rank completeness of the three operation kinds;
- unique factorization across tied exact words;
- a quotient category or algebra on bare generator labels;
- a rank-controlled or uniform bound on recursive mechanism menus;
- future-free section-to-section return.

