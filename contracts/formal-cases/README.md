# Versioned Formal Cases

These are fixed inputs and replay procedures, not new semantic contracts or
protocol-admission rules. Each bundle declares its mathematical model, runtime
source identity, concrete consumers, checked domain and evidence boundary.
The owning companion supplies the proof and source manifest; CI receipts
record the computation actually performed.

| Bundle | Owner | Scope |
| --- | --- | --- |
| [R/G/T bounded histories v1](rgt-bounded-history/v1/README.md) | [Paper XL C1/RGT Lean companion](../../experiments/paper40/lean/README.md) | Four fixed C1 consumers; exact finite generated-domain and successor comparison |

`contracts/consumer-replay/v1/` remains the separately frozen event-anchored
consumer specification. Putting cases under `contracts/` does not modify it,
extend the Paper VIII-XV protocol stack, or turn finite runtime agreement into
an all-parameter implementation theorem.
