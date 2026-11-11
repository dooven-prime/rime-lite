# R/G/T bounded history certificates

Status: independent, unpublished follow-up to Paper XL. The abstract finite
history theorem, R/G/T consequences, and counted encoding interface below are
Lean-checked. A separate Paper XL Lean companion instantiates the encoding for
its declared circular placement-plus-complete-log model. Correspondence with
the frozen Python runtime/archive remains a separate obligation; the model
instantiation is not a byte-level or runtime-equivalence claim.

This is a quantitative use of elementary finite-state path shortening. It is
not a novelty claim about general quotient or automaton theory.

## 1. Complete-state interface

Fix a deterministic raw system with state type `S`, alphabet `A`, total update
`step : S -> A -> S`, and seed `s0`. A word is chronological and every raw
letter costs one. Write `eval(h)` for execution from `s0`.

Let `cover` be a finite list containing every reachable **complete** state,
and let

\[
N=|\mathsf{cover}|.
\]

Duplicates and unreachable entries are allowed, so `N` need not be the exact
reachable-state cardinality. It is positive because `eval(epsilon)` belongs
to the cover. Neither the alphabet nor the entire ambient type `S` needs to
be finite for the existential results below.

The state must retain everything required to determine future raw updates,
registration, candidate values, reports, and enabledness. In the declared
circular Lean model the complete state is the current atom placement together
with the chronological list of **all** effective fusion records. The list of
selected absorptions alone is not substituted for that log. Whether this
formal state matches every field in the frozen Paper XL Python runtime is a
separate correspondence question.

Let a check specification consist of:

- a domain predicate `U` on complete states, selecting the registered domain;
- a candidate `q`, a tuple `r` of all declared reports, and Boolean command
  guards `g_alpha`, all functions of the complete state;
- a fixed raw letter `a_alpha` for each command label.

For the abstract interface these functions are total. Values outside `U` are
irrelevant to the fiber tests; an application may use option-valued extensions.
The interface does not interpret Paper XL's typed syntax. That interpretation
and query factorization belong to Paper XL, Section 2.3. Commands need not be
finite for the present existence theorem; effective exhaustive checking needs
the additional finiteness and decidability hypotheses of Paper XL.

For reachable states, define

\[
x\mathrel{\mathsf{Fiber}_q}y
\iff U(x)\land U(y)\land q(x)=q(y).
\]

Use precisely the three clauses of Paper XL, Theorem 3.1:

\[
\begin{aligned}
\mathrm R &: x\mathrel{\mathsf{Fiber}_q}y\Rightarrow r(x)=r(y),\\
\mathrm G &: x\mathrel{\mathsf{Fiber}_q}y\Rightarrow
  g_\alpha(x)=g_\alpha(y)\quad\text{for every }\alpha,\\
\mathrm T &: x\mathrel{\mathsf{Fiber}_q}y\ \land
  g_\alpha(x)=g_\alpha(y)=\mathsf{true}\\
&\hspace{2cm}\Rightarrow
 q(\mathsf{step}(x,a_\alpha))=q(\mathsf{step}(y,a_\alpha)).
\end{aligned}
\]

The abstract rejection theorems need no closure assumption on `U`. To identify
these clauses with state sufficiency on the Paper XL registered domain, its
separate inherited causal-closure lemma still applies.

## 2. Short-history replacement theorem

**Theorem 2.1.** Every actual raw history `h` has another actual history `k`
such that

\[
\mathsf{eval}(k)=\mathsf{eval}(h),\qquad |k|\le N-1.
\]

**Proof.** List the states visited by `h`, including seed and endpoint. If a
state occurs twice, remove the intervening loop. Determinism ensures that the
remaining suffix reaches the same complete endpoint. Iterating gives a path
with no repeated visited state. All its visited states lie in `cover`, hence
its `|k|+1` distinct visits number at most `N`. Therefore `|k| <= N-1`.

The Lean proof constructs an endpoint-preserving loop-erased word and proves
that its visits are duplicate-free and a sublist of the original visits. It
then bounds their length using the cover. The theorem is existential, not an
executable BFS implementation and not a claim that the chosen word is shortest.

**Corollary 2.2.** Any predicate of two actual complete endpoints is preserved
by replacing the two histories separately with words of length at most `N-1`.
In particular, registration, equality of `q`, and an R/G/T discrepancy survive.

The replacement may change intermediate positions and event times. It must
not change the complete endpoint log. This is why a lossy observation-state
count is not a sufficient substitute for `N` in this proof.

## 3. Bounded two-history rejection theorem

**Theorem 3.1.** For each of R, G, and T, failure is equivalent to the existence
of two actual histories `h1,h2`, each of length at most `N-1`, whose endpoints
belong to `U`, have equal `q`-values, and witness the corresponding discrepancy:

| Failed clause | Additional certificate data |
|---------------|-----------------------------|
| R | unequal declared report tuples |
| G | a command label with unequal enabledness |
| T | one label enabled at both endpoints, with unequal successor `q`-values |

For T the actual appended histories additionally satisfy

\[
|h_1a_\alpha|,|h_2a_\alpha|\le N.
\]

**Proof.** Negate the relevant universally quantified fiber clause to obtain
two actual histories and, where appropriate, a command label. Apply Corollary
2.2 to retain the two complete endpoints. Since updates, reports, guards, and
`q` are state functions, the discrepancy is unchanged. For T append the same
raw letter to both replacement words. The converse uses the displayed actual
histories directly as a failed instance of the clause.

This does not require assuming the other two clauses hold. The two histories
are not asserted to form a shortest pair. The generic `N-1` bound cannot in
general be reduced to `N-2`: a directed four-state chain has an endpoint first
reachable at length three; `Checks.lean` verifies that example.

**Empty-domain boundary.** If no reachable state satisfies `U`, all three
clauses are vacuously true. This supplies no registration event or POS witness.

### History length is not future distinguishing depth

Theorem 3.1 bounds past executions that expose a failed candidate-state test.
It does not bound a suffix separating two future event languages. A T failure
can occur even when all reports and guards are constant under every suffix:
the candidate may distinguish two successor states that the consumer never
observes. A concrete instance is checked in `Checks.lean`.

Consequently the standard circular-collapse future-observer bound `6n-10`
and this theorem answer different questions. Neither implies the other's
generality. There is no claimed all-defect linear-depth theorem here.

## 4. Explicit complete-log code bound

For the intended finite binary-fusion application, let there be `n` physical
sites and `m` source atoms, with `1 <= m <= n`. Fix the environment, the raw
maps, the single defect letter, its two ordered kernel ports and collision
image. Each effective fusion merges two disjoint nonempty packets, so there
are at most `m-1` such events. Nonfusion steps do not append to the log.

Every atom has one current site. Thus `n^m` assignments overcount all current
placements. For each effective event, label each atom by membership in the
ordered left parent, ordered right parent, or neither. There are at most
`3^m` such labels. With all other event fields fixed or reconstructed from
the ordered parents, a complete log of length `j` has at most `3^(m*j)` codes.
It follows that the code-list length is

\[
\boxed{B_{n,m}=n^m\sum_{j=0}^{m-1}3^{mj}.}
\]

Invalid assignments and invalid event sequences are intentionally retained.
They enlarge a cover rather than invalidate an upper bound. For example,
`B(1,1)=1`, `B(3,2)=90`, and `B(4,3)=48448`.

**Theorem 4.1 (recoverable-encoding interface).** Suppose the complete raw
state admits an encoding by exactly `m` site digits and fewer than `m` event
words of exactly `m` ternary digits, with a decoder satisfying

\[
\mathsf{decode}(\mathsf{encode}(\mathsf{eval}(h)))=\mathsf{eval}(h)
\quad\text{for every actual }h.
\]

Then Theorems 2.1 and 3.1 hold with `N = B(n,m)`. In particular,

\[
\boxed{|h_i|\le B_{n,m}-1,\qquad |h_ia_\alpha|\le B_{n,m}
\text{ for the T successors}.}
\]

**Proof.** Enumerate all codes of the specified widths and decode each. Every
actual complete state is in this list by the width and recovery hypotheses.
The list length is `B(n,m)` by the finite Cartesian-word counts, without any
injectivity requirement on its decoder. Apply the finite-cover theorems.

Both the exact code-list length and this conditional interface theorem are
proved in `LogEncoding.lean`. The decoder may be arbitrary on invalid codes;
its recovery obligation applies to all reachable complete states.

For the declared Paper XL circular Lean model, the support-card potential
proves the event-count premise: every effective `d` event merges the unique
colliding pair of occupied sites and decreases support cardinality by one;
`p` preserves it, and non-event `d` steps cannot increase it. Starting from
the injective `m`-atom seed gives `event_count < m`. The companion's
`PaperXL.BoundedHistory` then instantiates the placement/event encoder and the
resulting history and R/G/T bounds under the stated environment hypotheses.

### Remaining runtime and archive correspondence

The model-level Lean instantiation does **not** prove that its state or event
types coincide with the frozen Paper XL Python `LogState`, `Event`, or
`Summary` types, and it does not replay archived bytes. A separate source-level
correspondence audit is still needed before making such a claim.

Free timestamps, run IDs, independent metadata, an unrecorded invocation
argument, or multiple varying defect labels would invalidate this particular
count unless separately encoded. Fixed invocation arguments such as `F` may
be parameters of the decoder. A general complete-state cover theorem remains
available even when the specific ternary encoding is inapplicable.

## 5. Relation to other research branches

The proof uses no cyclic source-order, canonical defect, proper-arc origin
classification, or Fusion-log quadratic routing theorem. It does not reopen
Paper XL's frozen release files, Proper-arc Lean, B0, or POS.

If a separately established compression theorem replaces every history by
one of length at most `C(n)` while preserving the same complete log and final
placement, the same endpoint-predicate argument gives failure prehistories of
length at most `C(n)` and T successors at most `C(n)+1`. That is an independent
strengthening, not a theorem instantiated by this Lean package.

### Observation-preserving compression interface

The Lean module `ObservationCompression` now formalizes the cross-layer step.
`CompleteLogEndpointCompression` packages a replacement theorem preserving
the ordered complete fusion log and literal terminal placement. It induces
the observation `(completeLog, endpoint)`. A
`CheckSpecObservationFactorization` certificate states that registered-domain
membership, candidate, report, enabledness, and the observed next state all
depend only on this pair. Under exactly these hypotheses, every failed R or G
clause has a pair of actual histories of length at most `B`; every failed T
clause has such a pair and one common enabled command, whose appended
successor histories have length at most `B + 1`.

For the declared circular Paper XL Lean state, `CircularObservation.lean` now
proves that every consumer on `CircularLogState` factors through the exact
pair `(ordered event-code list, terminal atom-site map)`. It also instantiates
the existing finite-code loop-erasure compressor on those fields, so the
model-level finite bound is available directly. For the C1-compatible
fragment, `C1QuadraticCompression.lean` supplies the same-state quadratic
compressor and `C1QuadraticRGT.lean` transports it to the R/G/T certificates;
candidate maps may be lossy while remaining functions on the complete state.
This does not establish that the frozen Python parser, registration decoder,
reports, guards, candidate, and successor fields correspond to this Lean
model or to the C1 compressor. Without that separate correspondence, the
Lean complete-state result is not a runtime or archived-byte claim.

The common-boundary/different-origin construction in frozen Proper-arc v1,
Proposition 3.1, can likewise supply a specific R-origin rejection family. It
is not needed for the generic bound, and its constructive Lean implementation
is not imported here. The XXIX canonical rank-five raw first-exit bound is a
different finite graph problem; typed POS additionally requires authorization,
incidence, handoff, and same-witness projection data.

## 6. Proof status and remaining boundary

| Component | Current status |
|-----------|----------------|
| Loop erasure and finite complete-cover replacement | Lean-checked, arbitrary state/alphabet types under a finite reachable cover |
| R/G/T failure iff bounded actual history pair | Lean-checked, including common-letter T extension and empty-domain case |
| Complete code-list count `B(n,m)` | Lean-checked |
| Recoverable complete-log codec implies the `B(n,m)` certificate bound | Lean-checked conditional theorem |
| Declared circular Lean model codec and event-count premise | Instantiated in the separate Paper XL Lean companion; not an archived-byte/runtime correspondence |
| Consumer factorization through the circular Lean complete log and endpoint | Lean-checked for any `Consumer` on the declared `CircularLogState` |
| C1 quadratic compressor instantiated on the Paper XL circular state type | Lean-checked in the Paper XL companion for `n ≥ 3`, `2 ≤ m ≤ n`, with exact complete-state preservation |
| C1 quadratic R/G/T certificate transfer | Lean-checked conditionally for complete-state consumers with registered-domain reachability; lossy/Python transfer remains open |
| Frozen Python runtime correspondence, registration decoder and typed-expression interpretation | Not established |
| Specialized linear future probes, quadratic routing, POS | Not proved or imported here |

The C1-compatible quadratic acceptance target is now met by the Paper XL
companion: `C1QuadraticCompression` provides the same complete state and
`C1QuadraticRGT` transports it through the generic observation-factorization
interface. A separate source-level correspondence audit between this declared
Lean model and the frozen Python source/records remains necessary for any
runtime or archived-byte claim. Kernel-checked interface examples and public
theorem axiom queries are documented in [lean/README.md](lean/README.md); the
model-level factorization and C1 transfer are documented in [the Paper XL Lean
companion](../paper40/lean/README.md).

## Source references

- [Paper XL, Sections 2--4](../../papers/paper40/Paper%20XL.md): complete-log enumeration, typed query factorization, R/G/T, and actual two-history rejections.
- [Paper XL artifact README](../paper40/README.md): authority and validation boundary of the frozen application package.
- [Proper-arc v1 manuscript](../../papers/unnumbered/proper_arc_registered_summaries/MANUSCRIPT.md), Proposition 3.1: separate source for common-boundary origin constructions, not a dependency of the finite-cover proofs.
