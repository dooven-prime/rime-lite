# C1/RGT Formal Cases v1

This is a fixed finite runtime-comparison candidate for the Paper XL C1/RGT
Lean companion. The general theorem is about its declared complete Lean
state. This package validates four concrete consumers against the exact
Python snapshot released with `paper40-v1.0`; it does not replace that snapshot.

| ID | Fixed consumer | Expected result | Actual displayed histories |
| --- | --- | --- | --- |
| R | Packet/selected candidate, origin-port-0 report, empty command menu; n=3 | read failure | `dpd`, `pdpd` |
| G | Selected/origin/absorption/carrier candidate with Track commands; n=4 | guard failure | `d`, `dpppdp` |
| T | Absorption parity and always-enabled raw d; n=4 | successor failure | `d`, `dp` |
| P | Packet/selected candidate, partition report and Track commands; n=3 | exact on this finite domain | none |

Every environment uses identity singleton seed and the literal C1 defect
`[0,0,2,...,n-1]`. Selected F is the full three-atom set for R/P and `{0,1}`
for G/T. Full typed requests are inputs in `cases.json`; they are not runtime
callbacks. The fixed menus and folds are evaluated by the unchanged frozen
`ECC_SYN_V1` interpreter. Build provenance is in `build_cases.py`.

## Replay

After the companion's `lake build`, from the repository root:

```text
python -B contracts/formal-cases/rgt-bounded-history/v1/replay.py --report output/my-rgt-cases.json
```

The script verifies and extracts the released runtime ZIP into a temporary
directory. Its source owner is `dooven-prime/sof-runtime` content
`a4b3e48bd119908494c6d4de8619bffc01c1ecb9`; the byte authority is the ZIP at
`paper40-v1.0`, SHA-256
`2f473984c02c7d085d4bbec37fe06823c4399d201a08ed35251be57f3ffe3244`.

For each request it saturates the complete generated log domain, recovers
actual histories, and compares Lean evaluation on every state and both raw
successor edges. This includes complete per-atom sites, ordered full events,
registration/origin, selected absorptions, current partition/carrier,
candidate, report and every declared command guard. JSON comparisons retain
Bool/Nat distinctions. The Lean concrete consumers encode candidate/report
values as a decidable structural datatype and exports them to JSON; the
receipt checks the complete structured values and their compact encodings.

The frozen Q2 engine supplies a verdict and its separately implemented
rejection replay checks the negative witnesses. This replayer shares its
types and expression evaluator with the producer; no external-independent
validation is claimed. Displayed histories include every prefix state and
are checked against B(n); T additionally uses one common enabled raw d.
Resource failure, a malformed response or a mismatch raises an error, never
PASS. Existing reports are not overwritten.

In this finite domain, R has clause values `(false,true,true)`, G has
`(true,false,false)`, T has `(true,true,false)` and P has `(true,true,true)`
in R/G/T order. Thus G also fails successor sufficiency; these cases are not
a three-way independence theorem. The replay emits 1,986 observations across
662 complete states and their 1,324 raw successor edges (case-relative counts).

`ConcreteChecks.lean` proves the three specific failures from actual Lean
histories. Finite cross-language agreement does not prove the Python parser,
all environments, or all typed consumers correct. A green CI job records the
all-parameter Lean proof and this finite runtime validation as separate axes.
