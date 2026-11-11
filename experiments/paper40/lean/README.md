# Paper XL C1/RGT Lean Companion

This is a separately versioned, paper-owned companion candidate for Paper XL. It is
not part of the frozen Paper XL v1.0 release closure and does not rewrite the
manuscript or its evidence archive.

## Current coverage

- `PaperXL.Core` defines chronological raw execution for an abstract
  deterministic system.
- `PaperXL.CircularModel` defines the finite circular single-defect source
  model using per-atom sites and a chronological complete fusion log. Each
  event records the ordered kernel-port parent membership of every atom.
  Under the declared single-pair defect-fiber hypothesis, the support-card
  potential proves that every reachable log has fewer than `m` events.
- `PaperXL.BoundedHistory` encodes every atom site and every ordered event in
  the complete state, proves decode-after-encode recovery, and instantiates
  the reusable finite-history bound and R/G/T rejection certificates.
- `PaperXL.Consumer` defines the registered-domain R/G/T conditions and proves
  the exact quotient interface: under successor closure, R/G/T hold iff a
  deterministic partial quotient witness exists.
- `PaperXL.ConsumerBridge` maps a complete-state consumer to the reusable
  `RGTBoundedHistory.CheckSpec`. It proves the forward implication without
  extra assumptions and the reverse equivalence under explicit endpoint
  reachability of the registered domain. `ConsumerLogBridge` additionally
  handles the realistic case where a registered/causal state is a projection
  of a lower-level complete-log state, with explicit domain, step-commutation,
  and realization hypotheses. Its circular-model wrappers connect that bridge
  to `completeLogEncoding`; they do not identify the Lean state with the
  frozen Python contract bytes.
- `PaperXL.CircularObservation` makes the complete-log/literal-endpoint
  observation explicit as the ordered event-code list plus every atom's
  terminal site. Consumers defined on that view lift to the circular model,
  and their domain, candidate, report, enabledness, and one-step observation
  satisfy the R/G/T compression factorization interface. Fixed environment
  and invocation values are captured as parameters. The observation is
  lossless for the declared `CircularLogState`; therefore every consumer
  defined on that Lean complete state factors through it. It packages the
  existing finite-code replacement as an exact log/endpoint compressor and
  gives explicit finite-bound R/G/T certificate corollaries. Conditional
  quadratic corollaries require a compressor on this same state type whose
  log and endpoint fields are exactly the declared event list and site map.
  This does not prove correspondence with frozen Python parser/JSON bytes or
  instantiate the separate Fusion-log quadratic compressor here.
- `PaperXL.C1StandardSemantics` isolates the standard circular defect required
  for a C1 comparison. Lean checks the literal site update, ordered event-code
  parent recovery, and packet-level two-port fusion. These are local semantic
  bridge lemmas; the general `CircularEnvironment` does not imply C1
  compatibility. The cross-package event, placement, and whole-word run
  correspondences are established for C1-compatible environments. The M4-C
  quadratic representative-word theorem is instantiated separately in
  `PaperXL.C1QuadraticCompression`; complete-state transfer to bounded R/G/T
  certificates is provided by `PaperXL.C1QuadraticRGT` under explicit
  registered-domain reachability.
- `PaperXL.C1EventBridge` is a separately compiled cross-package interface
  importing the C1 M4-C development. It converts a Paper XL ternary event
  code to the ordered C1 fusion record and proves this conversion injective,
  including for complete chronological event lists. It does not identify
  executions, seed placements, or the M4-C representative-word theorem with
  Paper XL's raw system by itself.
- `PaperXL.C1RunCorrespondence` proves the cross-package whole-word
  correspondence for complete event logs and literal endpoint placements.
  Registration and selected-chain metadata remain outside this interface.
- `PaperXL.C1QuadraticCompression` composes that correspondence with the M4-C
  arbitrary-initial representative theorem. For C1-compatible environments
  with `n ≥ 3` and `2 ≤ m ≤ n`, it produces a Paper XL raw-letter word with
  the same complete `CircularLogState` and the M4-C `normalFormBudget`. Its
  global corollary records the quadratic bound as
  `2 * word.length ≤ 7 * n * (n - 1)`.
- `PaperXL.C1QuadraticRGT` supplies the complete-state R/G/T transfer for
  C1-compatible environments. Under explicit registered-domain reachability,
  failed reports and guards have two quadratic-bounded prehistories, while a
  failed successor clause has the same bounded prehistories plus one common
  raw-letter step. Lossy candidate maps on this declared complete Lean state
  are covered; independently defined lossy runtime state models, frozen
  Python contract bytes, and arbitrary non-C1 environments remain outside the
  bridge.
- `PaperXL.FiniteDomain` records the finite generated-domain completeness
  interface needed by the effective-checking theorem.
- `PaperXL.EffectiveCheck` turns the complete-log replacement bound into an
  executable bounded-history R/G/T decision procedure. It enumerates
  explicit raw-letter and command lists, and takes a Boolean registered-domain
  evaluator together with its correctness proof. The theorem reduces that
  finite check to full-history R/G/T and a negative result yields bounded
  actual prehistories for a failed clause.
- `PaperXL.PrefixObserver` defines the reusable semantic layer for finite
  history-prefix observers. It gives the unregistered/registered/saturated
  label transition, well-formedness and append laws, and the generic result
  that future-output equivalence plus current-label equality is the largest
  label-preserving output-stable relation.
- `PaperXL.FixedPrefixGrowth` defines a small cardinality interface for an
  observer that retains a finite history-prefix tag. It proves the lower and
  upper finite-cardinality bounds, including the polynomial-factor form
  `|Observer| ≤ |Future| * (n + 1)^k` when the tag family has that bound. It
  also proves that a nonempty tag family with a fixed polynomial bound has
  `(n+1)`-root growth tending to `1`, so adjoining it preserves any existing
  exponential growth limit. This remains an abstract interface; it does not
  assert the circular-model prefix counts or the critical-window limit.
- `Checks.lean` provides small kernel-checked controls for a two-state system,
  including independent G and T failures.
- `DecisionChecks.lean` kernel-checks positive and negative executions of the
  Boolean finite checker.
- `ConsumerBridgeChecks.lean` kernel-checks the complete-state consumer to
  `CheckSpec` adapter on a two-state generated system.
- `CircularObservationChecks.lean` kernel-checks the lossless observation,
  consumer factorization, and finite/conditional bounded-certificate APIs.
- `PrefixObserverChecks.lean` kernel-checks the prefix-label transition and
  its event-trace fold law. These are semantic controls, not the Paper XL
  archive counts or a circular-model instantiation.
- `FixedPrefixGrowthChecks.lean` kernel-checks the finite cardinality bounds
  and the abstract polynomial-tag growth interface.

The Lean codec is a mathematical complete-state encoding for this declared
circular model, not a byte-level replay of the frozen Python archive. The
actual Paper XL Python encoder/parser and exact finite saturation algorithm
are not instantiated. Registration uniqueness, the 6/39/292 domain counts,
and the frozen JSON results remain outside this companion. No machine
verification of those counts or archived results is claimed.

The versioned `contracts/consumer-replay/v1` package is a separate JSON
consumer-replay contract. Its `U(h,F)` state is a derived registered view of a
complete log, retaining the full placed partition, origin, selected absorption
records, and carrier. The new Lean bridge supplies the abstract projection
interface needed to connect such a view to `CheckSpec`; it does not yet prove
that the frozen contract parser or Python records are byte-for-byte equivalent
to the Lean `CircularLogState` model.

## Reproduce

From this directory, with the pinned Lean toolchain and Lake dependencies:

```text
lake build
lake env lean Checks.lean
lake env lean DecisionChecks.lean
lake env lean ConsumerBridgeChecks.lean
lake env lean CircularObservationChecks.lean
lake env lean PrefixObserverChecks.lean
lake env lean FixedPrefixGrowthChecks.lean
lake env lean AxiomAudit.lean
lake env lean Signatures.lean
```

The Lake manifest explicitly includes the local R/G/T library and the pinned
C1 M4-C source closure. `PaperXL.lean` imports all four cross-package modules,
so `lake build` checks the entire bridge and produces its `.olean` files.
There is no manually concatenated `LEAN_PATH` or pre-existing bridge cache.
The standard all-in-one entry, from the repository root, is:

```text
python -B experiments/paper40/lean/validation/replay.py --verify-inputs-only
python -B experiments/paper40/lean/validation/replay.py --report output/my-c1-rgt-proof.json
python -B contracts/formal-cases/rgt-bounded-history/v1/replay.py --report output/my-c1-rgt-cases.json
```

`C1RunCorrespondence` proves the per-letter and whole-word correspondence for
the complete event log and literal endpoint placement. It intentionally does
not claim a correspondence for Paper XL registration or selected-chain
metadata. `C1QuadraticCompression` additionally instantiates the M4-C
representative-word theorem on the Paper XL complete state; it does not yet
instantiate a transfer to an independently defined lossy/Python state model.
`C1QuadraticRGT` composes that complete-state representative theorem with the generic `CheckSpec` compression
lemmas, yielding the conditional quadratic R/G/T certificate bounds.

The project pins Lean 4.33.0 and the Mathlib revision in `lakefile.toml`; it
uses the sibling `rgt_bounded_history_certificates` package as a local
dependency. `.lake/` is ignored build output. The axiom audit prints the
dependencies of the quotient theorem, executable decision, bounded rejection,
circular-history theorems, and fixed-prefix cardinality/growth results. There
are no custom axioms or `sorry` placeholders in this companion.

## Bounded-history statement and boundary

For every declared environment with `2 ≤ m ≤ n`, the encoding has placement
width `m`, event width `m`, and reachable event count `< m`. It therefore
inherits the generic complete-code cover size

`logBound n m = n^m * sum (j = 0 .. m-1), 3^(m*j)`.

Every endpoint has an equal-endpoint history of length at most
`logBound n m - 1`. Each failed R, G, or T clause has two actual prehistories
of at most that length; the common enabled T letter gives successor histories
of length at most `logBound n m`.

The executable checker requires explicit finite lists for raw letters and
commands, plus a Boolean domain evaluator proved equivalent to the consumer's
domain predicate. It checks all histories through `logBound n m - 1`; complete
log replacement proves equivalence with the unbounded-history R/G/T clauses.
This is a generic checker for the formal complete-state model, not an
implementation claim about the archived Python checker or its runtime.

These bounds concern complete placement-plus-event-log histories. They are
not bounds on a lossy summary quotient, a future distinguishing suffix, or
the frozen Paper XL release counts.

## Fixed Identity and Cases

[THEOREM_MAP.md](THEOREM_MAP.md) separates the all-parameter Lean theorem,
its C1/environment and generated-domain hypotheses, and the finite runtime
comparison. `companion-manifest.v1.json` binds both local libraries, the
four cross-package modules, the workflow and the fixed cases. Its ancestor
identities are `paper40-v1.0` and `fusion-log-m4d-source-v1.0`, which contains
the unchanged M4-C theorem. `Signatures.lean` records complete types in every
proof receipt; the owning audits cover Paper XL, R/G/T and M4-C separately.

The [formal cases](../../../contracts/formal-cases/rgt-bounded-history/v1/README.md)
use the exact Paper XL v1.0 Python ZIP and compare all generated complete
states and every raw edge for four declared C1 consumers. Lean supplies the
complete-state execution and concrete reads; the frozen Python supplies
its own model, typed interpreter, Q2 verdict and rejection replay. This is
finite correspondence validation, not an all-parameter parser/implementation
theorem. The R/G/T support library is included in this companion, not a new
paper. Source tag and external archive identity remain pending review.
