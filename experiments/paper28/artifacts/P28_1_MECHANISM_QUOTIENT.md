# P28.1 Mechanism Quotient and Observable Descent

## Status

This note freezes the first mathematical target of Paper XXVIII. It defines a
quotient-audit problem; it does not claim that either quotient below is already
sound on the seed relations.

Paper XXVII determines a sufficient proof state. Paper XXVIII now asks which
parts of an exact local realization may be forgotten while preserving the
observables needed for mechanism composition.

## 1. The Two Quotients

Let `R_exact` be a source-addressed exact receipt relation. A member records the
typed source context, every corridor representative, the packets participating
in each fusion, accounting data, the exact endpoint, and the ancestry produced
for the next context.

The proposed quotient chain is

\[
 \mathcal R_{\rm exact}
 \xrightarrow{q_{\rm acct}}
 \mathcal M_{\rm acct}
 \xrightarrow{q_{\rm skel}}
 \mathcal M_{\rm skel}.
 \tag{1.1}
\]

### Accounting mechanism

`M_acct` retains the proposed interaction skeleton together with:

- corridor count and rank-drop vector;
- maturity gains `Delta M_i`;
- exact corridor lengths `ell_i` and surpluses `S_i`;
- carried debt between corridors;
- target partition and residual tail budget.

It may forget the concrete word and exact packet coordinates only after the
corresponding observables are proved to descend.

### Mechanism skeleton

`M_skel` retains only candidate structural data:

- source rank and source packet partition;
- source-addressed packet-role pattern;
- ordered fusion chain;
- ancestry participation and a proposed ancestry-update type;
- return type.

It forgets exact length and credit allocation. Whether the proposed ancestry
update is sufficiently precise is itself part of the audit.

Neither quotient is defined by visual similarity of finite rows. It is defined
by the fields above and accepted only after observable descent is proved.

### Canonical receipt shape

The first implementation uses one explicit three-layer record:

- `skeleton`: the proposed `M_skel` key;
- `accounting`: corridor, debt, and tail-budget data added to obtain
  `M_acct`;
- `exact`: source context, source packet identities, concrete words, exact
  endpoint channel, and the full ancestry update;
- `observables`: independently computed theorem observables to audit on each
  quotient fiber.

The generic schema and hostile-pair audit live in
[`paper28_mechanism_schema.py`](paper28_mechanism_schema.py). Its synthetic
validator is
[`validation/validate_paper28_mechanism_schema.py`](validation/validate_paper28_mechanism_schema.py).
These files define audit infrastructure only. They do not establish descent
for any seed mechanism or replace the source-addressed seed projector.

An exact receipt identity over-retains provenance. It includes the source
context, concrete word, corridor boundaries, fusion packet identities, exact
endpoint, and ancestry update. Equality of source, endpoint, and length is not
an exact-receipt identity. Any later merger of exact receipts must be justified
by an observable-descent or composition-congruence audit.

### Abstract menu and exact realization fiber

For a proposed mechanism quotient `q`, distinguish the abstract menu from its
exact realizations:

\[
 \mathfrak M_r(C)=\{m:\mathcal R_r(C;m)\ne\varnothing\},
 \qquad
 \mathcal R_r(C;m)
 =\{B\in\mathcal R_{\rm exact}:\partial^-B=C,\ q(B)=m\}.
 \tag{1.2}
\]

The menu is the finite family of interaction labels offered at `C`. A menu
member may have many tied, source-addressed exact realizations. Boundedness
below applies to `|\mathfrak M_r(C)|`, not to the summed cardinality of these
exact fibers.

## 2. Observable Descent

For a quotient `q` and a theorem observable `O`, write

\[
 \operatorname{Desc}_q(O)
 \quad\Longleftrightarrow\quad
 q(x)=q(y)\Longrightarrow O(x)=O(y)
 \quad(x,y\in\mathcal R_{\rm exact}).
 \tag{2.1}
\]

For relation-valued observables, equality in (2.1) means equality of the full
set-valued image, not equality of one producer-selected witness.

The first P28.1 output is an audit matrix, not merely a mechanism catalog.

| theorem observable `O` | `q_acct` | `q_skel o q_acct` | initial status |
| --- | --- | --- | --- |
| source/target rank and packet partitions | retained | retained | definitional candidate |
| ordered fusion mass pattern | retained | retained | definitional candidate |
| rank-drop vector and corridor count | retained | retained | definitional candidate |
| exact corridor lengths | retained | forgotten | skeleton descent generally not expected |
| corridor surplus and debt profile | retained | forgotten | accounting descent expected; skeleton descent must be tested |
| total surplus | derived from retained data | potentially forgotten | test whether skeleton determines it |
| residual tail budget | retained | forgotten | accounting descent expected; skeleton descent must be tested |
| exact ancestry update | proposed typed quotient | proposed typed quotient | must be audited, not assumed |
| source packet identity | may be quotiented | may be quotiented | failure expected in some cells |
| exact target transport channel | may be quotiented | may be quotiented | failure expected in some cells |
| legal composition with a successor mechanism | separate binary congruence audit | separate binary congruence audit | not a unary observable |

The words `expected` and `failure expected` are research hypotheses. The
catalog must display explicit quotient fibers and either prove equality of the
observable or retain a hostile pair witnessing failure.

Downstream winning labels, Bellman values, reset coaccessibility, and
membership in a future success set are not permitted as quotient keys. They
may be used only as hostile evaluators after the future-free quotient is
constructed.

### Composition descent

Typed composability is not a unary observable. Let `Comp(x,y)` be the exact
source-addressed compatibility relation between two receipts and define

\[
 \operatorname{Succ}_q(x)
 =\{q(y):\operatorname{Comp}(x,y)\}.
 \tag{2.2}
\]

`Comp` is constructed from typed output/input boundary compatibility, packet
roles, ancestry transport, endpoint normalization, and accounting. It does
not use eventual recursive success as an edge predicate.

The full composition-congruence requirement is

\[
 q(x)=q(x')
 \quad\Longrightarrow\quad
 \operatorname{Succ}_q(x)=\operatorname{Succ}_q(x').
 \tag{2.3}
\]

Equivalently, every abstract successor class available from one exact source
representative must lift from every representative in the same source fiber:

\[
 \begin{aligned}
 q(x)=q(x'),\quad m\in\operatorname{Succ}_q(x)
 \quad\Longrightarrow\quad
 \exists y':\ &\operatorname{Comp}(x',y')\\
 &\land\ q(y')=m.
 \end{aligned}
 \tag{2.4}
\]

The weaker condition preserving only whether a successor exists is reported
separately:

\[
 q(x)=q(x')
 \Longrightarrow
 \bigl[\operatorname{Succ}_q(x)\ne\varnothing
 \iff\operatorname{Succ}_q(x')\ne\varnothing\bigr].
 \tag{2.5}
\]

Condition (2.5) is not called composition congruence. It may suffice for a
particular existential argument only after the required successor class and
ancestry semantics are shown not to matter.

## 3. Quotient-Audit Theorem Target

The unary target is a maximal proved subset of observables `O_P28` such that

\[
 \forall O\in\mathcal O_{\rm P28},
 \qquad \operatorname{Desc}_{q_{\rm acct}}(O),
 \tag{3.1}
\]

followed by an explicit partition

\[
 \mathcal O_{\rm P28}
 =\mathcal O_{\rm skel}
 \sqcup
 \mathcal O_{\rm acct-only}
 \sqcup
 \mathcal O_{\rm exact-only},
 \tag{3.2}
\]

according to the coarsest level through which each observable descends.

In particular, a skeleton family is composable only if exact compatibility
descends to that skeleton in the stronger sense of (2.3), or if the
accounting/exact refinement required for composition is carried explicitly
alongside it.

Thus P28.1 has two outputs: the unary observable matrix (3.1)--(3.2), and a
composition-congruence audit at both the accounting and skeleton levels. It is
allowed, and mathematically informative, for accounting addition to descend
while semantic composition remains exact-relation-valued.

The theorem is allowed to conclude that no single skeleton quotient preserves
all observables. A typed hierarchy of interaction skeleton, accounting
refinement, and exact realization is an acceptable and likely outcome.

In particular, a positive result may have the layered form

\[
 \boxed{
 \text{interaction skeleton layer}
 +\text{ accounting refinement}
 +\text{ exact typed realization fiber}.}
 \tag{3.3}
\]

The skeleton classifies interaction type and labels exact arrows; it is not
called an algebra until a composition operation has been proved. The
accounting layer may support credit addition, while semantic composition may
still require a typed boundary and an exact source-addressed lift. This is not
a failed quotient theorem; it identifies the level at which each operation is
mathematically defined.

The first boundary-factorization audit is recorded in
[`P28_1B_BOUNDARY_LIFTABILITY_RESULTS.md`](P28_1B_BOUNDARY_LIFTABILITY_RESULTS.md).
On its fixed `4+35` closure, normalized target mass placement explains every
composition-hostile mechanism fiber and supports fiber-uniform successor
classes. This is fixed-scope evidence, not an all-rank congruence theorem.

## 4. Credit Calculus

For each exact corridor,

\[
 S_i=\tau(\mu_{i+1})-\tau(\mu_i)-\ell_i.
 \tag{4.1}
\]

For a composable exact mechanism block `M`, define

\[
 L(M)=\sum_i\ell_i,
 \qquad
 S(M)=\sum_i S_i.
\]

Telescoping gives

\[
 S(M)=\tau(\mu_{\rm out})-\tau(\mu_{\rm in})-L(M).
 \tag{4.2}
\]

If `M_2` is legally source-addressedly composable after `M_1`, then at the
exact level

\[
 S(M_2\circ M_1)=S(M_1)+S(M_2).
 \tag{4.3}
\]

The algebra in (4.3) is immediate once the boundary state is shared. The
Paper XXVIII theorem obligation is different: prove that the quotient retains
enough typed data to decide legal composition and to make `S` well-defined at
the claimed level.

The fixed identity

\[
 20+B_2(6,1)=12+B_2(5,2)=27
\]

is a motivating credit-reallocation instance, not a derivation of (4.3) and
not evidence that the skeleton quotient preserves every budget observable.
The fixed-scope realization of (4.2)--(4.3), including the conditional
accounting-label composition relation, is recorded in
[`P28_2_CREDIT_COMPOSITION_RESULTS.md`](P28_2_CREDIT_COMPOSITION_RESULTS.md).

## 5. Boundedness Levels

Menu boundedness is separated into three strengths:

\[
\begin{aligned}
 \mathrm{B0}:&\quad |\mathfrak M_r(C)|<\infty
   &&\text{for each constructed context menu},\\
 \mathrm{B1}:&\quad |\mathfrak M_r(C)|\le f(r)
   &&\text{for a rank-controlled function},\\
 \mathrm{B2}:&\quad |\mathfrak M_r(C)|\le K
   &&\text{for a uniform constant}.
\end{aligned}
 \tag{5.1}
\]

Paper XXVIII first needs a future-free constructible B0 menu. B1 is a stronger
structural target. B2 is not a prerequisite for Forced FFS and is not inferred
from any fixed-`n=7` menu observation. Exact realization fibers need only be
relation-defined, locally enumerable, and liftable; their cardinality is not
the bounded-menu quantity.

## 6. Forced and General FFS

On the single-defect slice, the open selector statement is

\[
 A\text{ synchronizing},\quad |D_A|=1
 \quad\Longrightarrow\quad
 \mu_d=d_*\mathbf1\in W_A^{2C}.
 \tag{6.1}
\]

A future-free all-rank section return that starts at the certified
single-kernel source and terminates in the exact low-rank base would imply
Forced FFS. No rank-independent constant menu bound is required for that
implication.

General FFS asks for

\[
 A\text{ synchronizing}
 \quad\Longrightarrow\quad
 \exists d\in D_A:\ d_*\mathbf1\in W_A^{2C}.
 \tag{6.2}
\]

Its additional object is a selector among multiple defect kernels and their
steering geometries. That is not part of P28.1 and is provisionally assigned
to a later multi-kernel program.

Thus the intended paper split is:

```text
Paper XXVIII: mechanism quotient + credit calculus
               + single-kernel recursive return -> Forced FFS target

later program: multi-kernel selector geometry -> General FFS target
```

## 7. Primitive-Generator Audit

The current names `direct`, `repayment`, `B2 steering`, `heavy comb`, `bridge`,
`orbit closure`, and `fallback` are candidates, not primitive classes. P28.1
and P28.3 must test whether they factor through a smaller operation set such as

\[
 \boxed{\text{transport}+\text{fusion}+\text{repayment}+\text{return}.}
 \tag{7.1}
\]

For example, a heavy comb may be iterated fusion, a bridge may be a transport
refinement, orbit closure may be a transport normal form, and fallback may be
an accounting reallocation. These are hypotheses to test through the quotient
matrix, not renamings to impose in advance.

## 8. Finite Seed Audit

The first computation uses only existing fixed-scope exact relations. It does
not enumerate new automata. Existing summary artifacts are not automatically
exact relations: the source-readiness boundary is audited in
[`P28_1_SEED_SOURCE_AUDIT.md`](P28_1_SEED_SOURCE_AUDIT.md).

For every quotient fiber it must report:

1. the exact receipt digests in the fiber;
2. the accounting and skeleton keys;
3. every audited observable image;
4. whether that image is singleton;
5. a hostile pair whenever descent fails;
6. the coarsest accepted quotient level for each observable.

The JSON catalog is a certificate for this matrix. The mathematical result is
the proved descent/failure statement for each observable.

Only after the quotient and composition observables stabilize does an
inherited `n=8` pilot become meaningful.

The first run must answer four questions:

1. Which observables descend to `M_skel`?
2. Which descend only to `M_acct`?
3. Which remain exact-relation-valued?
4. At what level, if any, does successor composability become a congruence?

## 9. The `4+35` Seed Projector

The canonical projector is
[`paper28_project_seed_mechanisms.py`](paper28_project_seed_mechanisms.py).
It reconstructs the complete tied endpoint-shortest Type-I/II relation from
the 39 released rank-four roots. It also constructs the strictly descending
rank-three/rank-two closure needed to audit exact successor composition.
Membership in the exact low-rank base is recorded only as an observable; it is
not read by the relation constructor, either quotient, or `Comp`.

With `RIME_PAPER27_RELEASE_ROOT` set to the Paper XXVII v1 release root, run:

```powershell
python experiments/synchronizing_automata/paper28_project_seed_mechanisms.py
python experiments/synchronizing_automata/validation/validate_paper28_seed_mechanism_catalog.py
```

The deterministic output is
`results/paper28_seed_mechanism_catalog_v1.json.gz`. The gzip header uses a
zero timestamp, so compressed bytes are reproducible. Its exact receipt key retains
the source context, concrete corridor words, every packet fusion, the typed
target context, and the ancestry update. Compatibility edges are induced only
by equality of an exact target context with an exact successor source context.
