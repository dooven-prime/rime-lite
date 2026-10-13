# Promotion Audit: No Silent Strengthening

**Status:** public RIME method note. This is a working audit language for
cross-type claims, not a paper, theorem source, protocol contract, validator,
or admission authority. The owning manuscripts and their versioned evidence
remain authoritative. The longer unnumbered research draft is not part of this
public source chain.

## The Question

For a proposed move from an available object or result $A$ to a stronger
claim $B$, ask: **what licenses this particular move on its declared scope?**
Constructing $A$ honestly is not itself a promotion. Promotion occurs when
$A$, perhaps with extra data $\Gamma$, is used to assert a target not already
supplied by the construction of $A$.

A promotion is *silent* when the target is asserted while its source and
target types, information or warrant gap, bridge, scope, or evidence identity
are absent or hidden. An omitted hostile test alone does not make an otherwise
proved, fully scoped implication silent. Nor does the audit assume that every
gap is caused by a lossy map: quantifier coverage, witness compatibility,
provenance, and operational authority can fail separately.

The terms *bridge* and *certificate* here mean a declared, scope-bound reason
for one inference. They do not automatically mean a machine certificate or
grant authority to an artifact, actor, or action.

## Fibre Test

For a surjection $q:X\to Y$ and a target $h:X\to Z$, a unique map
$\bar h:Y\to Z$ with $h=\bar h\circ q$ exists exactly when

$$
q(x)=q(x')\quad\Longrightarrow\quad h(x)=h(x')
\qquad(x,x'\in X).
$$

Indeed, factorization implies fibre constancy; conversely, constancy makes
$\bar h(y)=h(x)$ independent of the choice of $x\in q^{-1}(y)$.
For a non-surjective $q$, the same test determines $\bar h$ only on $q(X)$;
values outside the image require another declaration. This elementary
criterion is a diagnostic for deterministic *representational* promotion,
not a universal test for every claim boundary.

One pair with equal $q$-values and unequal $h$-values refutes factorization
on the declared domain. Separating that pair by refining $q$ does not prove
factorization: every fibre of the refined representation must still pass.
Other legitimate repairs are to restrict the domain, weaken the target to a
relation or uncertainty state, or retain auxiliary data. Each repair changes
the claim and must be stated.

In particular, fibre constancy on $D\subseteq X$ for an observation $O$ and
update $F$ yields a one-step map
$\bar F_D:O(D)\to O(F(D))$. It does not by itself yield an autonomous endomap
of $O(D)$ or an iterable coarse dynamics. That stronger claim needs successor
image closure and a compatible microscopic domain, or separately declared
time-indexed domains. [Paper XVI](../papers/paper16/Paper%20XVI.md) and
[Paper XVII](../papers/paper17/Paper%20XVII.md) own their respective case
results; this note does not restate them as a general mechanism theorem.

## Nine-Field Record

Use one record per proposed arrow. The fields are audit questions, not a new
JSON contract or a universal admission algorithm.

| Field | Record |
|---|---|
| `A` source | Exact available object or evidence state, including its semantic owner. |
| `B` target | Exact stronger object, predicate, permission, or transition, and its owner. |
| `L` gap | Information lost, quantifier not covered, witness not shared, provenance not bound, or authority not supplied. |
| `Gamma` bridge | Additional hypothesis, datum, proof, alignment, witness, policy, or authority basis that licenses this arrow. |
| `S` scope | Carriers, domains, parameters, depths, fields, policies, actors, and targets covered. |
| `E` evidence | Actual proof or validation kind, and the meaning of failure or absence; do not collapse `ZERO`, `UNREACHED_AT_CUTOFF`, `INCOMPARABLE`, and `UNRESOLVED`. |
| `I` identity | Exact source, producer, result, validator, receipt, contract, version, and release anchor, where applicable. |
| `N` negative boundary | Nearby stronger interpretations that this record does not support. |
| `F` falsifier | A concrete hostile pair, failed lift, separating regime, or authority gap that would reject the proposed arrow. |

After filling the record, state an outcome for the *declared arrow*: supported
in scope, refuted, unresolved, or not declared. These are prose audit outcomes,
not substitutes for a paper's claim taxonomy, a schema's state machine, or a
validator's result. Record a failed condition without converting it to a
numerical zero or a universal impossibility result.

The shortest useful review path is:

1. Name `A` and `B` with their owners and exact scope.
2. Exhibit the missing datum or warrant and a candidate bridge.
3. Try the strongest cheap falsifier while keeping the asserted upstream
   warrant fixed.
4. Check the bridge against the owning theorem or contract and bound evidence.
5. Record the outcome and the strongest nearby claim that remains unlicensed.

## Exact Control

Boolean support of two nonzero matrices does not determine whether their
product is nonzero. Let

$$
A=\begin{pmatrix}1&0\\0&0\end{pmatrix},\qquad
B_0=\begin{pmatrix}0&0\\0&1\end{pmatrix},\qquad
B_1=\begin{pmatrix}1&0\\0&0\end{pmatrix}.
$$

The pairs $(A,B_0)$ and $(A,B_1)$ have the same two-step Boolean support,
but $AB_0=0$ and $AB_1=A\ne0$. The missing datum is the intermediate
image--kernel relation:

$$
AB\ne0\quad\Longleftrightarrow\quad
\operatorname{im}B\not\subseteq\ker A.
$$

This is a hostile pair for support-to-composition promotion, not a claim that
support is useless. Support identifies candidate routes; survival needs an
additional test. [Paper III](../papers/paper3/Paper%20III.md) owns its
composition results and hypotheses.

An audit of the overstrong arrow can therefore be written without guessing
its missing premise:

```text
A:       two nonzero factors, reduced to Boolean support
B:       nonzero composed product
L:       intermediate image and kernel are forgotten
Gamma:   image(B) is not contained in kernel(A)
S:       the declared two-factor matrix product
E:       exact integer calculation; zero is evaluated, not missing
I:       the three explicit matrices above; no external receipt is claimed
N:       supported does not mean active at every depth
F:       (A,B_0) and (A,B_1) have equal support, unequal product activity
Outcome: the unqualified arrow is refuted; the Gamma-qualified arrow holds
```

## Other Boundaries

The same audit vocabulary can expose different missing warrants without
asserting that they are all fibre collisions:

| Available result | Stronger reading to audit | Missing bridge |
|---|---|---|
| Bounded finite census | All-depth or generic theorem | Symbolic argument covering the new quantifier and exceptional regimes. |
| Two separately witnessed steps | One composable path | A common witness and a typed handoff. |
| Aligned report difference | Causal attribution | A separately declared causal or intervention model. |
| Passing validation receipt | Current-use or execution authority | The relevant activation or authorization basis and external execution path. |

For these cases, the owning paper or contract defines the object and required
bridge. This note neither transfers a theorem between papers nor promotes a
local receipt into independent validation. A repository link, Git tag, or DOI
identifies only the objects it actually anchors; it does not establish
scientific adequacy or semantic correctness.
