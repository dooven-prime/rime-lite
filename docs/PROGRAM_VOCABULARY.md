# RIME Program Vocabulary

This companion defines the public cross-paper vocabulary used by the RIME
program. Owning manuscripts remain authoritative for formal definitions. The
purpose here is to prevent neighboring constructions from being collapsed by
informal shorthand.

## 1. Naming Rules

- Use **RIME program**, not trilogy, except in an immutable historical title.
- Use **Sectorized Observable Framework (SOF)** on first occurrence and **SOF**
  thereafter.
- Treat cross-paper citations as interface references, not hypothesis imports.
- Use **invariant** only after declaring an equivalence relation and proving
  invariance under it.
- Qualify every count, rate, depth, wall coordinate, and diagnostic by the
  choices on which it depends.

## 2. Spectral and Sector Vocabulary

| Term | Controlled meaning |
|------|--------------------|
| represented averaging operator | a declared operator obtained from a finite-dimensional representation and weighting policy |
| spectral layer | a blockwise or jointly registered spectral component under declared conventions |
| compatible sectorization | a complete marked orthogonal projector family compatible with the stated source data |
| collision arrangement | a fixed declared family of branches together with their equality loci |
| collision quotient | the quotient structure induced by collisions inside that fixed arrangement |
| `Sigma_comm` | commutativity gate for a declared operator family |
| `Sigma_normal` | normality gate; it is not implied by commutativity alone |
| `Sigma_spec` | spectral admissibility domain after the preceding gates |
| pointwise registration | a certified sample at one parameter value, not a coherent moving projector field |

Do not use *spectral wall* for every repeated eigenvalue without identifying the
field, chart, multiplicity convention, and wall policy.

## 3. Static SOF Vocabulary

The static operator core is

```text
F_op = (V, {Q_i}, Y),
```

where `V` is a finite-dimensional complex Hilbert space, `{Q_i}` is a complete
marked orthogonal sectorization, and `Y = {Y_a}` is a labelled observable
alphabet. The labels are data and are not recoverable from an aggregate span.

Keep the linear layers distinct:

```text
D_Q       = span{Q_i}
E_Y       = span{I, Y_a, Y_a^*}
S_{Q,Y}   = D_Q + E_Y
```

Keep the closure layers distinct:

```text
A_Y^+     positive-word algebra
A_Y^*     observable star-closure
A_{Q,Y}^* sector-enriched star-closure
```

Closure describes eventual generated structure. It does not recover generator
labels, route data, word length, or first-hit depth.

## 4. Accessibility Vocabulary

### Operator and word branch

| Term | Controlled meaning |
|------|--------------------|
| labelled block | `Q_i Y_a Q_j` for a declared observable label `a` |
| `R_1[Y]` | aggregate direct operator support of the labelled family `Y` |
| `Route_d[Y]` | routed projected products with declared intermediate sectors |
| `W_d[Y]` | full associative word support at word length `d` |
| `D_route[Y]` | first-hit depth in the routed-product filtration |
| `D_word[Y]` | first-hit depth in the full-word filtration |

### Lie/Hall branch

| Term | Controlled meaning |
|------|--------------------|
| registered Lie family `X` | independently declared Lie generators |
| `R_1^Lie` | direct support of the registered Lie generators |
| `R_2^Lie` | simple-commutator support under the declared convention |
| Hall filtration `H` | declared formal-expression filtration |
| `D_Lie` | first-hit depth in that Lie/Hall filtration |

The two branches are independent unless an explicit induction or bridge rule
is part of the realization. Do not use unqualified `R_1`, `R_2`, or `D` in
cross-paper prose.

### Depth states

- **exact first hit at `d`:** witness at `d` plus verified non-hits below `d`;
- **hit observed by `d`:** a witness exists by `d`, but minimality is unaudited;
- **`UNREACHED_AT_CUTOFF`:** no hit through the declared finite cutoff;
- **infinity:** requires an appropriate closure or saturation certificate.

The retired numeric sentinel `999` never denotes infinity and must not enter
statistics.

## 5. Deformation and Wall Vocabulary

| Term | Controlled meaning |
|------|--------------------|
| typed deformation chart | a local parameter domain with fixed labels, carrier conventions, comparison maps, and declared continuity |
| fibre comparison map | a typed map placing selected fibrewise data into a fixed comparison space |
| trajectory | a declared one-parameter path in a chart |
| typed wall | a policy-relative local change of a selected typed field under Paper IX admissibility |
| wall pullback | restriction of a chart-level discriminant or wall package to a declared trajectory |
| response time | a trajectory-relative measurement with declared normalization, norm, threshold, and censoring policy |

Paper XI records admitted wall data using a sum type:

```text
WallAtom = TrajectoryEvent | LocusSample
```

A `TrajectoryEvent` has an orientation, event parameter or interval, sampling
rule, and sparse before/after field changes. A `LocusSample` records incident
stratum germs and has no intrinsic before/after order unless a probe path is
declared.

Keep these fields independent:

- `realization_kind`: `strict_sof` or `diagnostic_analogue`;
- `record_role`: wall event, locus sample, reference, boundary witness, or
  another declared role;
- `field_family`: spectral, operator, route, word, Lie/Hall, closure, state,
  proxy, or another typed family.

Wall coordinates are profile-relative diagnostics unless an invariance theorem
is separately proved. Multi-label curation tags are not mutually exclusive
classification classes.

## 6. Compilation and Reporting Vocabulary

| Term | Controlled meaning |
|------|--------------------|
| Capability Manifest | declares which typed capabilities and conventions a source provides |
| Typed SOF IR | records validated typed objects, findings, dependencies, and evidence status |
| Report Profile | declares which supported claims a compiler requests and how they are gated |
| capability-sound compilation | every affirmative emitted claim is supported by the typed IR within its declared scope |
| Registry | capability-aware evidence architecture, not the compiler theorem and not an automatic compiler input |
| `.sofreport` | one realization-relative report under Paper XII protocol semantics |
| Audit Profile | requested aligned comparison coordinates and their policies |
| `.sofaudit` | sparse typed comparison of two explicitly aligned reports |

Strict SOF and diagnostic analogue are mutually exclusive realization kinds.
A diagnostic analogue does not instantiate strict-SOF theorems.

## 7. SOFAUDIT Comparison States

| State | Meaning |
|-------|---------|
| `ALIGNED` | aligned and equal, or within the declared comparison tolerance |
| `MISMATCH` | aligned but unequal, or outside the declared comparison tolerance |
| `NOT_DECLARED` | the source report did not declare a required field |
| `NOT_APPLICABLE` | the coordinate does not apply under the declared profile |
| `INCOMPARABLE` | no valid alignment or compatible convention is available |
| `UNRESOLVED` | the requested comparison has not reached a supported conclusion |

`ALIGNED` names the successful aligned-equality outcome in the current
contract; it does not merely mean that an alignment map exists.

## 8. Action Semantics Vocabulary

| Term | Controlled meaning |
|------|--------------------|
| `ActionContext` | independently admitted actor, scope, objective, constraints, time, authority, and uncertainty input; it is not derived from an audit |
| `PolicyProfile` | the sole normative rule input of the current Paper XIV contract, with closed predicate, uncertainty, exception, and precedence semantics |
| `InterpretationRecord` | context- and policy-relative interpretation of retained Paper XIII coordinates; it does not rewrite the audit |
| `CandidateActionSet` | bounded set of policy-supported candidate records; it is not a selected or executed plan |
| `.sofaction` | Paper XIV artifact binding the immutable audit projection, admitted context and policy, interpretations, and disposition result |
| `NoDisposition` | no legal disposition was formed, including failed context or policy admission |
| `UnresolvedDisposition` | admitted inputs remain insufficient for a supported disposition |
| `NoActionDisposition` | an explicit applicable-policy result; it is not an empty candidate set by default |

The current `.sofaction` contract stops at bounded candidates. Selected plans,
authorization receipts, post-action observations, and independently validated
effects require separate downstream contracts. A missing context, policy, or
capability is never promoted into `NoAction`.

## 9. Claim and Evidence Vocabulary

Use exactly four reader-facing levels:

| Level | Meaning |
|-------|---------|
| Theorem | exact statement proved from declared hypotheses |
| Computational Certificate | reproducible finite computation tied to declared inputs |
| Computational Observation | bounded numerical pattern without theorem promotion |
| Research Program | open problem, conjectural bridge, or proposed extension |

Use **conditional** when a conclusion depends on an unverified registration or
bridge. Use **proxy** when the measured field is not the claimed strict field.
Use **sampled** or **truncated** when the conclusion is bounded by a grid,
interval, or cutoff.

## 10. Deprecated or Restricted Shorthand

Avoid the following as active cross-paper vocabulary:

| Avoid | Use instead |
|-------|-------------|
| `observable invariant` without a theorem | profile-relative observable coordinate or diagnostic |
| `accessibility determines behavior` | the declared carrier records or constrains the selected behavior |
| universal `Sigma_access` | a named typed discriminant or declared wall package |
| unqualified `R_1`, `R_2`, `D` | carrier-qualified support or depth notation |
| graph path as route witness | graph diagnostic unless a projected-product certificate exists |
| word support as commutator support | `W_d[Y]` or `R_2^Lie`, whichever was computed |
| capability becomes present along a chart | typed field witness or reachability state becomes present |
| `NOT_RECORDED` as a result state | record-field presence marker only |
| `999` | `UNREACHED_AT_CUTOFF` with an explicit cutoff |
| Type I--IV as universal wall/accessibility classes | named mechanism such as commutator cancellation or image--kernel incidence |
| ADE as universal wall taxonomy | ADE candidate local model after a declared eligibility gate |

## 11. Numerical and Release Discipline

Public numerical values belong to versioned result records and passing
validators. Public release identity belongs to Zenodo records, accepted release
manifests, and the root [Public Release table](../README.md#public-release).
Vocabulary documents must not become parallel numerical or release ledgers.
