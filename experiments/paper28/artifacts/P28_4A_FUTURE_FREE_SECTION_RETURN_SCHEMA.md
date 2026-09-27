# P28.4a Future-Free Section Return Schema

## Status

This note freezes the theorem schema extracted from the completed
fixed-`n=7` extremal section-to-base audit. It introduces no new census and
does not promote the finite menu bound, the success counts, or the extremal
carrier geometry to all-rank hypotheses.

The schema separates three typed objects:

1. a section-certified recursive context;
2. a future-free abstract mechanism menu;
3. a relation-valued exact lift fiber for each menu channel.

The result to be proved is existential over menu channels and exact lifts.
Success is not a field of the menu.

## Typed data

Fix a terminal base rank `r_0`. For every `r>r_0`, let

\[
 \operatorname{Sec}_r
\]

be the typed contexts that have already been granted recursive checkpoint
authority. Define the lower certified destination class

\[
 \mathfrak D_{<r}
 :=P_{\le r_0}\cup
   \bigcup_{r_0<s<r}\operatorname{Sec}_s.
\]

For `C\in\operatorname{Sec}_r`, a menu constructor returns a finite set

\[
 \mathfrak M_r(C)=\{m_1,\ldots,m_k\}.
\]

Each channel `m\in\mathfrak M_r(C)` has an exact realization fiber

\[
 \operatorname{Lift}_r(C,m).
\]

An element `x\in\operatorname{Lift}_r(C,m)` is a finite exact
source-addressed generator path. It has typed boundaries

\[
\partial^-x,\qquad \partial^+x,
\]

and may contain internal replay boundaries that are not recursive proof
states.

The exact-lift certificate also exposes a theorem-facing target view

\[
 \widehat{\partial^+x}=\eta_x(\partial^+x).
\]

Here `\eta_x` may be literal identity or a verified typed relabelling. It is
part of exact-lift soundness F3, not a sixth schema quantifier. It must preserve
every observable read by the lower theorem.

Define success only after the menu and lift fibers have been constructed:

\[
 \boxed{
 \operatorname{Good}_r(C,m)
 \iff
 \exists x\in\operatorname{Lift}_r(C,m):
 \widehat{\partial^+x}\in\mathfrak D_{<r}.}
 \tag{SR-Good}
\]

`Good_r` is a derived predicate. It is not an input to the menu constructor,
the channel key, or exact-lift enumeration.

## The five contracts

### F1. Future-free construction

The construction of `\mathfrak M_r(C)` and `\operatorname{Lift}_r(C,m)` may
read the current certified context, action, normalized mass boundary, typed
ancestry, local generator relations, endpoint normalization, and accounting
constraints. It must not read `\operatorname{Good}_r`, lower-section
membership, low-rank success, winning labels, reset coaccessibility, or a
producer-selected successful witness.

### F2. Source typing

Every exact lift is rooted at the declared section source:

\[
 x\in\operatorname{Lift}_r(C,m)
 \Longrightarrow
 \partial^-x=C.
 \tag{SR-Source}
\]

### F3. Exact-lift soundness

Every exact lift is a legal source-addressed generator path. Its component
operations replay correctly, its fusion roles and packet identities agree at
every boundary, and its normalization, ancestry update, and accounting data
are valid. Abstract labels classify the path; they do not replace this exact
soundness obligation.

If `\partial^+x` and the certified lower context use different exact packet
serializations, F3 includes a certified map `\eta_x` between them. The map must
preserve the rooted action, occupied coordinates, packet masses and roles,
distinguished ancestry, endpoint normalization, and accounting semantics. An
identity handoff is the special case `\eta_x=\operatorname{id}`. The two
completed fixed-`n=7` realizations exhibit both possibilities: atom bijection
in the first chain and identity in the second.

### F4. Checkpoint typing

Internal boundaries remain local states of an exact lift. They acquire
recursive checkpoint authority only through an independent section or base
certificate. In particular,

\[
 \{\text{internal-only boundaries of }x\}
 \cap
 \{\text{exported recursive checkpoints}\}
 =\varnothing.
 \tag{SR-Checkpoint}
\]

### F5. Existential return

For every certified source, at least one future-free menu channel has an exact
lift to a lower certified destination:

\[
 \boxed{
 \forall C\in\operatorname{Sec}_r,
 \quad
 \exists m\in\mathfrak M_r(C):
 \operatorname{Good}_r(C,m).}
 \tag{SR-Return}
\]

Equivalently, there exist `m` and `x\in\operatorname{Lift}_r(C,m)` with
`\widehat{\partial^+x}\in\mathfrak D_{<r}`.

F1--F4 are construction and typing contracts. F5 is the mathematical return
obligation. The schema does not require every channel to succeed and does not
require a unique successful channel.

Accordingly, later all-rank hypothesis extraction must not use “F1--F5” as a
single assumed package. F1--F4 may be proposed as construction/typing
contracts; F5 must be derived, for example from separate Cover and Admission
lemmas.

## Fixed-`n=7` instantiation

The completed P28.4 finite theorem instantiates the schema as follows:

| schema object | fixed-scope realization |
| --- | --- |
| source rank | `r=4` |
| terminal base rank | `r_0=3` |
| section domain | `\operatorname{Sec}^{(7)}_{4,\mathrm{ext}}`, the 35 released extremal contexts |
| destination class | `P_{\le3}^{(7)}` |
| abstract menu | future-free interaction-skeleton channels with relation-valued accounting refinements |
| exact lift | tied endpoint-shortest source-addressed receipts factored through the P28.3 generator relation |
| success predicate | exact target membership in `P_{\le3}^{(7)}`, evaluated after menu freezing |

The instantiation has 173 channels, 864 accounting refinements, and 4,182
exact lifts. There are 169 successful channels and four complete failed
channels, while all 35 sources have a successful channel. The four failed
channels are therefore quantifier-boundary certificates:

\[
 \forall C\ \exists m
 \quad\text{is proved, whereas}\quad
 \forall C\ \forall m
 \quad\text{is false on this scope.}
\]

None of the counts, the observed menu bound of eight, or the `(6,1)` form of
the four failed channels is part of the abstract schema.

## Conditional iteration

Suppose F1--F4 are realized on every certified rank above `r_0`, and suppose
an independently proved return theorem establishes F5 with strict rank
decrease at every such rank. Repeated existential choice then produces a
finite chain ending in `P_{\le r_0}`. This is a theorem schema, not an all-rank
result: the construction contracts and the return theorem above the declared
fixed scopes remain open.

The boundedness hierarchy applies to the abstract menu,
`|\mathfrak M_r(C)|`, not to the cardinality of the exact realization fibers.
Per-context finiteness (B0), a rank-controlled bound (B1), and a uniform bound
(B2) remain distinct.

## Quantifier discipline

The canonical order is:

1. certify `C\in\operatorname{Sec}_r`;
2. construct and freeze `\mathfrak M_r(C)` and all declared exact lift fibers;
3. evaluate `\operatorname{Good}_r(C,m)`;
4. prove that at least one menu member is good.

Reversing steps 2 and 3 turns the menu into an outcome-selected witness list
and violates F1.
