# C1/RGT Theorem-to-Source Map

## Mathematical Contract

Fix `E : CircularEnvironment n m`, `[NeZero n]`, `C1Compatible E` and
`3 <= n`. The environment already carries `2 <= m` and `m <= n`, an
injective singleton seed, ordered kernel ports and the single-pair kernel
law. C1 compatibility fixes ports 0/1 and the literal defect `d(1)=0`,
fixing every other site. It is not inferred from rank defect alone.

For any `Consumer` on the complete `CircularLogState n m`, assume every
state in its declared domain is actually reachable from the seed
(`Consumer.DomainReachable`). Let `B = 7*n*(n-1)/2`, with natural division.
Then any R or G failure has two actual prehistories of length at most B.
Any T failure has two such prehistories, a common enabled command, distinct
successor candidates, and successor histories of length at most B+1.
This bounds past witnesses; it is not a future distinguishing-suffix bound.

## Proof Owners

| Declaration | Owning source | Role |
| --- | --- | --- |
| `Consumer.RGT_iff_quotient` | `PaperXL/Consumer.lean` | Paper XL Theorem 3.1's abstract exact partial-system criterion |
| `ConsumerLogBridge.RGT_iff` | `PaperXL/ConsumerBridge.lean` | Explicit state projection, step commutation and domain-realization interface |
| `CircularLogState.decodeComplete_encodeComplete` | `PaperXL/BoundedHistory.lean` | Complete-state finite-code recovery |
| `BoundedDecision.circular_decision_correct` | `PaperXL/EffectiveCheck.lean` | Executable finite formal checker; not the frozen typed Python parser |
| `codeFusionRecord_list_injective` | `PaperXL/C1EventBridge.lean` | Every ordered parent code is retained |
| `c1RunCorrespondence_initial` | `PaperXL/C1RunCorrespondence.lean` | Whole chronological word: complete log and literal placement |
| `arbitrary_initial_log_endpoint_representative` | C1 `FusionLogInterpretation/ArbitraryInitialReplay.lean` | Inherited M4-C representative-word owner |
| `c1QuadraticCompression` | `PaperXL/C1QuadraticCompression.lean` | Same complete Lean state and specific `normalFormBudget` |
| `c1QuadraticCompression_global` | same | `2 * word.length <= 7*n*(n-1)` |
| `c1_registered_read_failure_quadratic` | `PaperXL/C1QuadraticRGT.lean` | Bounded actual read-failure prehistories |
| `c1_registered_guard_failure_quadratic` | same | Bounded actual guard-failure prehistories |
| `c1_registered_successor_failure_quadratic` | same | Bounded prehistories plus one common enabled step |
| `ConcreteConsumer.domainReachable` | `PaperXL/ConcreteConsumer.lean` | Generated, registered concrete consumers supply the domain hypothesis |
| `ConcreteConsumer.origin_read_failure`, `partition_guard_failure`, `parity_successor_failure` | `PaperXL/ConcreteChecks.lean` | Kernel-checked actual-history controls for the three fixed failures |

Public Paper XL v1.0 owns the manuscript definitions and scope. This new
Lean source package does not modify that release. The complete typed grammar
interpreter and the original Python saturation implementation are not proved
correct by the abstract checker theorem.

## Dependency and Version Identity

```text
Paper XL declared circular action + complete event/site state
  -> exact ordered-record and whole-word correspondence
  -> unchanged C1 M4-C actual representative-word theorem
  -> same complete Lean state with quadratic length
  -> RGTBoundedHistory observation replacement/collision transfer
  -> arbitrary consumer R/G/T certificates under domain reachability
```

`companion-manifest.v1.json` binds this Paper XL Lean source, the R/G/T
support library and the finite-case adapter by exact hashes. It pins Paper XL
at `paper40-v1.0` (content `6df0b4aa9357aa67522aa2e47436674aab1bad5f`),
including its actual released runtime ZIP. C1 M4-C is resolved through the
unchanged `fusion-log-m4d-source-v1.0` content
`0c6bbebf19bca9d1bedc0fe63b23821b8b913d0f`, with M4-C manifest
`606e08c94497e48098d8f7c78ad9572ebc6b4614d5c7552f9254743b35d9660d`.
The R/G/T library has no separate paper identity: it is source-bound here.

Lean is `leanprover/lean4:v4.33.0`, runtime commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`. Mathlib is
`db584cd6d46c92f209a44c0f1c829460d327499d`. The workflow uses official
Mathlib cache, not a committed compiled proof cache. CI receipts record the
actual PR head and checkout separately. No source tag or archive is claimed
before review. Candidate manifests and receipts are not rewritten afterwards.

## Audit and Runtime Layers

The owning audits query 68 Paper XL, 25 R/G/T and 29 M4-C declarations.
Every queried axiom set is transitive and must be a subset of `propext`,
`Classical.choice`, `Quot.sound`. `Signatures.lean` prints exact final types,
including the generated-domain hypothesis and model fields. A successful
build without those signatures and audit inventories is not the acceptance.

The separate finite-case receipt compares the released Python model,
complete events, all concrete reports/guards/candidates and every raw
successor with Lean evaluation. It includes actual double histories and
letter-by-letter prefix states. It validates only the four declared finite
consumers, not an all-parameter Python/Lean bridge or grammar compilation.
