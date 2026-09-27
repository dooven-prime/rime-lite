# P28.6v: Canonical Return-Certificate Alignment

## Status

Complete on the tagged fixed-`n=7`, rank-four inherited domain.  This is not
an all-`n` projectability theorem.

The audit separates two statements that were previously compressed into the
word *projectability*:

\[
\begin{aligned}
\textbf{Origin Coverage:}\quad
 &(C,\kappa_4^{\rm ret})\in\operatorname{Sec}_4^{\rm inh,fs}(7)\\
 &\Longrightarrow \exists\tau_{5\to4}:\
   \operatorname{TransferRecord}_5(\tau),\
   \operatorname{tgt}(\tau)=C,\
   \operatorname{ret}(\tau)=\kappa_4^{\rm ret},\\[1mm]
\textbf{Projection Existence:}\quad
 &\tau\in\mathcal T_{5\to4}^{\rm inh,fs}(7)\\
 &\Longrightarrow \exists\kappa_4^{\rm ISE}:\
   \operatorname{Proj}_{\rm ISE}(\tau,\kappa_4^{\rm ISE}).
\end{aligned}
\]

Here `Sec_4^{inh,fs}(7)` is exactly the tagged union of the five admitted
carriers whose rank-five transfer origins were frozen before `Good_5`:

\[
 35+48+36+36+10=165.
\]

The theorem does **not** assert

\[
 \operatorname{Sec}_4\Longrightarrow\operatorname{Sec}_4^{\rm inh}
\]

outside this declared finite domain.

## Canonical construction

For each typed source context `C`, the audit reconstructs

\[
 \Lambda_4^{\rm complete}(C)
\]

directly from the P28.6c equations through `CompleteExitOracle.exits`:
rank-four plateau, first strict exit, endpoint normalization, endpoint-shortest
distance, and every tied shortest exact realization.  No low-rank membership
or component evaluator is loaded during this phase.

Independently, `CompleteExitOracle.macro_edges` reconstructs the composable
Type-I/II macro paths used to check the adapter replay. This second relation is
not used as the definition of `Lambda_4^complete(C)`.

An adapter receipt is normalized only by removing artifact identity:
`schema`, `receipt_id`, `seed_surface`, `relation_role`, `origin`, and derived
outcome fields.  Its theorem-facing row retains the complete `skeleton`,
`accounting`, and `exact` objects.  In particular, words, corridor boundaries,
packet identities, fusion sources, target contexts, ancestry updates, and debt
data remain present.

## Alignment relation

The frozen relation

\[
 \operatorname{Align}_4
 (C;\kappa_4^{\rm fs},\kappa_4^{\rm can})
\]

has three audited strengths:

| level | statement | fixed-scope result |
|---|---|---:|
| A0 | every adapter macro lift has a canonical first-exit path image | `26,995/26,995` |
| A1 | boundary, ancestry, normalization, exact observables, and ISE provenance transport | `165/165` sources |
| A2 | adapter relation equals `Lambda_4^complete(C)` | **not claimed: different relation types** |

The distinction is structural. `Lambda_4^complete(C)` contains one strict
first exit. A Type-I adapter receipt maps to one such row; a Type-II receipt
maps to a composable `Lambda_4` row followed by a `Lambda_3` row. Therefore
the adapter is a debt-compatible one/two-step macro relation derived from the
canonical first-exit relations, not another serialization of `Lambda_4`.

Raw JSON equality is also neither required nor claimed. Historical receipt
IDs, schemas, origins, and surface tags intentionally differ. Thus the result
is

\[
 \boxed{
  \Lambda_4^{\rm fs}(C)
  \longrightarrow
  \operatorname{Path}_{1,2}
  (\Lambda_4^{\rm complete},\Lambda_3^{\rm complete})
 }
\]

with an explicit macro-lift-to-path injection and complete replay of the
adapter macro relation. No equality with the single first-exit relation is
inferred.

Per carrier:

| carrier | sources | transfers | `Lambda_4` rows | macro paths |
|---|---:|---:|---:|---:|
| `ext` | 35 | 35 | 1,537 | 4,182 |
| `cand2` | 48 | 48 | 4,178 | 9,600 |
| `cand3` | 36 | 36 | 3,511 | 5,239 |
| `cand4` | 36 | 36 | 3,284 | 6,498 |
| `cand5` | 10 | 10 | 939 | 1,476 |
| **total** | **165** | **165** | **13,449** | **26,995** |

The macro paths split into 1,528 Type-I one-segment paths and 25,467 Type-II
two-segment paths.

The frozen success-free alignment-core digest is

```text
969c59b14051c347fdf8da33a2c23e6d839abde9f2d521722c736c1e5b5901b6
```

## Post-freeze mechanism transport

Only after the alignment digest is frozen does the audit open the existing
GFPC and PEC component artifacts.  It does not rerun either evaluator.

Support transports by identical ISE provenance records.  `LocalReturn`
transports by the A0 exact-row image.  Therefore the reduced fixed-scope cover
also closes on canonical certificates:

| carrier | schema | canonical completed sources | canonical return paths |
|---|---|---:|---:|
| `ext` | GFPC | 35/35 | 2,329 |
| `cand2` | GFPC | 48/48 | 9,498 |
| `cand3` | PEC | 36/36 | 4,208 |
| `cand4` | PEC | 36/36 | 5,937 |
| `cand5` | PEC | 10/10 | 1,205 |
| **total** | | **165/165** | **23,177** |

This establishes semantic transport of the finite mechanism theorem through
canonical first-exit paths without assuming representation identity or
adapter/`Lambda_4` equality.

## Claim boundary

The artifact proves:

1. origin coverage on `Sec_4^{inh,fs}(7)`;
2. projection existence on the 165-record frozen inherited transfer domain;
3. A0/A1 path alignment for all five adapters;
4. complete replay of every adapter macro lift as one or two canonical
   first-exit segments; and
5. transport of the already frozen GFPC/PEC support and completion witnesses
   to canonical fixed-scope certificates.

It does not prove:

- `Sec_4 -> Sec_4^inh` for arbitrary admitted sections;
- all-`n` Projectable-Origin Cover on a non-singleton transfer fiber;
- all-`n` Uniform Projection of every transfer record;
- equality of a Type-I/II macro adapter with the single first-exit relation;
- raw receipt or JSON equality;
- all-`n` GFPC/PEC completion; or
- all-rank F5.

P28.6w further separates the next theorem boundary. Define the transfer fiber
`T_5->4(C,kappa_4^ret)` and its projectable subfiber. The minimal inherited
route requires only

\[
\boxed{
 (C,\kappa_4^{\rm ret})\in\operatorname{Sec}_4^{\rm inh}
 \Longrightarrow
 \mathcal T_{5\to4}^{\rm proj}(C,\kappa_4^{\rm ret})\neq\varnothing
}
\]

The stronger claims `Sec_4 -> Sec_4^inh` and projection of every transfer
record are optional sufficient strengthenings, not minimal F5 blockers. This
quantifier boundary is frozen in
[`P28_6W_TRANSFER_FIBER_PROJECTABILITY_AND_ORIGIN_QUANTIFIERS.md`](P28_6W_TRANSFER_FIBER_PROJECTABILITY_AND_ORIGIN_QUANTIFIERS.md).
None of these theorems is hidden inside `Align_4`.

## Artifacts

- `paper28_canonical_return_certificate_alignment_v1.json.gz`
- `paper28_canonical_return_certificate_alignment_v1.receipt.json`
- producer: `paper28_audit_canonical_return_certificate_alignment.py`
- validator: `validation/validate_paper28_canonical_return_certificate_alignment.py`

Artifact SHA-256:

```text
69564521589c51f99dd3e29d96c554be19253ac73741c418ea1fa723c201e6f9
```
