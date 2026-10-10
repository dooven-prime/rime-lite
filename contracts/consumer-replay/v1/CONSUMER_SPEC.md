# Consumer Specification

This is the independent log oracle for the finite Case. Its definitions do
not depend on either representation or on the current behavior of a checker.

## Source and Event Log

Fix `Q = Z/nZ`, `n >= 2`, `p(q) = q + 1`, and a labelled map `d:Q -> Q` of
rank `n-1`. The sole nonsingleton kernel is the ordered pair of distinct
positions `(k_0,k_1)`, and `d(k_0) = d(k_1) = c`. Fix a finite atom set
`Omega` with `2 <= N = |Omega| <= n` and an injective singleton seed
`iota:Omega -> Q`. A packet partition `P` places a nonempty atom block at
each occupied position; these blocks are disjoint and cover `Omega`.

For a chronological word `h` over `p,d`, replay each letter by push-forward:

```text
(f_{a#} P)(y) = union of P(q) over occupied q with f_a(q) = y.
```

Only a `d` step with both kernel positions occupied creates a fusion event.
Immediately before that step, record

```text
snap(e) = (d, b_e, c),  b_e(k_i) = P(k_i),
F_e = b_e(k_0) union b_e(k_1).
```

The log orders fusion occurrences chronologically. It need not retain the
number of intervening `p` or nonfusing `d` steps. An event's parent positions
are its event-time addresses and never become its later carrier position.

## Registration and Complete State

For a supplied nonempty `F subseteq Omega`, define

```text
Reg(h,F) iff some logged fusion e has F_e = F.
```

The event is unique: atoms never split, and any later fusion of its carrier
adds a disjoint nonempty partner. Current containment of `F` alone is not
registration. The same `F` remains the selected invocation argument for
every subsequent command, even if another event becomes the latest one.

For a registered `(h,F)`, exactly one current packet `(q_h,C_h)` contains
`F`. The selected absorption sequence `A_F(h)` consists of all later log
events whose one pre-event parent contains `F`, in chronological order. For
such an event, with containing parent `(q_e,C_e)` and other parent
`(s_e,B_e)`, retain the entire record

```text
(d, q_e, C_e, s_e, B_e, c, C_e union B_e).
```

The complete consumer state is

```text
U(h,F) = (P_h, F, snap(e_F), A_F(h)).
```

Only states produced by registered histories are admitted. The **report**
contains the origin snapshot, the whole ordered absorption list, and the
current carrier **including both position `q_h` and block `C_h`**. The full
current partition `P_h` is retained in the state and in a complete Case
comparison: it determines future guards even when it is not displayed as a
carrier-local report field. A checker must also compare actual placements,
not just unordered blocks.

## Commands

For a registered state with carrier `(q,C)` and letter `a`, let

```text
G_a(P,q) = {s in support(P) : f_a(s) = f_a(q)}.
```

`Carry(a)` is enabled exactly when `G_a(P,q) = {q}`. `Absorb(a)` is enabled
exactly when this group is `{q,s}` for some `s != q`. Both are undefined
without registration. Under the declared action, `Absorb` necessarily uses
`d`; `Absorb(p)` is never enabled. On registered states the two commands
partition the labelled next steps.

Both commands apply the requested raw letter to **every** packet and keep
`F` and its origin fixed. `Carry(a)` moves the carrier to `(f_a(q),C)` and
does not append a selected absorption. It may still fuse two other packets:
`Carry(d)` must update the full partition and event log in that case.
`Absorb(d)` appends

```text
(d, q, C, s, P(s), c, C union P(s))
```

and moves the carrier to `(c,C union P(s))`. Registration persists. These
updates define deterministic partial actions on the generated consumer
states; no fresh event may be chosen between commands to make a guard pass.

This specification does not ask for absolute timestamps, plateau counts,
ordering between unrelated events, shortest words, checkpoint status,
authorization, credit settlement, or an all-size proof from finite replay.
