# Adequacy for Event-Anchored Absorption Chains

**Status:** supplementary data-independent proof details for
[Paper XXXIX Theorem 4.1 and Corollaries 4.2--4.4](Paper%20XXXIX.md), using
the separately declared [consumer specification](ABSORPTION_CONSUMER_SPEC.md).
The Paper XXXIX manuscript owns the central theorem; this note expands its
proof and coverage inventory rather than creating a second claim authority.
The result concerns the declared forest semantics on its seed-generated domain. The numbered draft remains subject to mathematical review.

## 1. Declared implementation domain

Use the source, labelled action, and singleton seed of the consumer
specification. Generate the placed forest by the equations in
[Paper XXXIX Section 3](Paper%20XXXIX.md). Write

$$
 z_h=\delta_h^{\mathfrak F}z_{\iota},\qquad
 Z_{\iota}^{\rm reach}=\{z_h:h\in\{p,d\}^*\}.
$$

This domain is closed under both generators. No claim identifies every
ambient well-formed forest with a generated history.

A consumer invocation supplies $F\subseteq\Omega$, $F\ne\varnothing$.
It is not the forest's latest marker. No field is added to $(\mathcal F,m)$,
and the existing marker update rule is not changed. A decoder may inspect
the already retained tree structure to supply derived consumer reads.

## 2. Event-to-node correspondence

**Lemma A1.** For every history $h$, its fusion occurrences are in bijection
with the internal nodes of $z_h$. The corresponding node has fresh leaf set
$F_e$, child leaf set $b_e(k_i)$ at child index $k_i$, event label $d$, and
event target $c$. This correspondence persists under later steps.

**Proof.** The singleton seed has no fusion occurrence and no internal node.
A noncollision step moves each root unchanged and appends no event. At a
collision, the raw log appends precisely the snapshot of the two kernel
packets, and the forest creates precisely one node from those same roots,
indexed by their actual pre-step positions. Packet projection compatibility
identifies the child leaf sets with the two logged parents. Existing nodes
remain present as subtrees. Induction proves the claimed correspondence.

Distinct nodes have distinct leaf sets: nested nodes have strictly nested
nonempty supports, and incomparable nodes have disjoint supports. Thus the
fresh-block identity matches the log's unique-event identity. $\square$

It follows that, on this domain,

$$
 \operatorname{Reg}(h,F)
 \iff \exists v\text{ internal in }z_h:
       \operatorname{leaves}(v)=F.
 \tag{Reg-F}
$$

In particular, merely lying inside a current packet is insufficient for
registration. An unlogged subblock cannot be silently supplied as an event.

## 3. The temporal absorption sequence is an ancestor path

For a valid $F$, let $v_F$ be its unique internal node. It belongs to a unique
placed root at $q$. List its strict ancestors, from its immediate parent
outwards to that root, as $v_1,\ldots,v_t$. For each ancestor $v_i$, take the
child on the path to $v_F$ as its containing parent; its other child is the
partner. Their child indices are the recorded event-time positions.

**Lemma A2.** These ancestors, in that order, correspond exactly to the
chronological absorption subsequence $\mathcal A_F(h)$, with all fields of
each record (Abs) equal. The placed root has leaf set $C_h$ and position $q_h$.

**Proof.** At the creation of $v_F$ it is a root. Its current carrier is $F$,
and both the strict-ancestor list and the later-absorption list are empty.
Suppose the statement holds at a later prefix.

If the next step does not merge the root containing $v_F$, the path from
$v_F$ to that root is unchanged. That root moves to $f_a(q)$, and the log
appends no absorption involving $F$. This includes a collision between two
other roots: it creates an independent node and may replace the latest marker,
but neither changes the selected root's ancestor path nor its absorption list.

If the next step merges the selected root with another root, its new parent
is the newly created fusion node. The old path gains exactly this one outer
ancestor. The log gains exactly one new absorption. Its containing parent,
partner, child positions, union, label, and target are those of this same
new node, by Lemma A1. No other event intervenes in this update. Induction
proves the statement for the entire suffix. $\square$

This recovers a temporal order **along one selected causal lineage**. It does
not recover a total order between incomparable events. The two conclusions
have different scopes.

## 4. Decoder and coverage

Define $J_C(z,F)$ when the right side of (Reg-F) holds. Its values are:

- $P=\pi(z)$ and the supplied $F$;
- the snapshot read from $v_F$;
- the list of (Abs) records read from its strict-ancestor path, using the
  containing child and the other child at each node.

The current carrier is derived from the unique placed root containing $v_F$.
This defines the complete consumer summary (U), not just its report.

The implementation command for `Carry(a)` or `Absorb(a)` applies the existing
forest action $\delta_a^{\mathfrak F}$ and keeps the same invocation argument
$F$. Its guard uses $\pi(z)$ and this current carrier in the formula (Dom).
It is undefined when registration or the requested guard is undefined/false.

| Independent consumer requirement | Supplied interpretation | Proof |
|---|---|---|
| Registration domain | An internal node with fresh set $F$ exists | A1, (Reg-F) |
| Origin parents at their actual positions, label, and target | The node's coordinate-indexed children and local event data | A1 |
| Whole chronological absorption list, including each partner and event addresses | The selected node's strict-ancestor path | A2 |
| Current containing packet and position | Its unique placed root and leaf set | A2 and projection compatibility |
| Complete current partition required for guards | Packet projection of all placed roots | Projection compatibility |
| `Carry` / `Absorb` domains | The actual next-step collision group of the containing root | Theorem A3 below |
| Next summary and subsequent definedness | Existing forest update with the same $F$ | Theorem A3 below |

This table discharges the specification's whole requested interface. It does
not claim coverage of other consumers or of unspecified old characteristic
reads.

## 5. Consumer-adequacy theorem

**Theorem A3 (event-anchored absorption adequacy).** For every declared
singleton seed, every finite history $h$, and every nonempty block
$F\subseteq\Omega$:

1. $J_C(z_h,F)$ is defined if and only if $\operatorname{Reg}(h,F)$.
2. When defined, $J_C(z_h,F)=U(h,F)$, including every report field.
3. For each labelled generator and each of `Carry`, `Absorb`, the forest
   implementation is enabled if and only if the consumer command is enabled.
4. Whenever that command is enabled, its updated forest invocation decodes
   to the consumer's updated summary $U(ha,F)$. Registration persists.

These statements hold for arbitrarily long histories without a length budget.

Equivalently, for a registered generated invocation $x=(z,F)$ and a command
$\alpha$ of type `Carry(a)` or `Absorb(a)`, let
$\widehat\delta_\alpha$ be its forest implementation and $\Delta_\alpha$ its
independent consumer action. Then

$$
 \widehat\delta_\alpha(x)\text{ is defined}
 \iff \Delta_\alpha(J_Cx)\text{ is defined},
 \tag{A-Domain}
$$

and, when defined,

$$
 J_C\bigl(\widehat\delta_\alpha(x)\bigr)=\Delta_\alpha(J_Cx).
 \tag{A-Step}
$$

The first equation reflects the legal domain; the second matches the actual
successor. Agreement of the present report alone would give neither result.

**Proof.** Lemma A1 proves clause 1 and the origin part of clause 2. Projection
compatibility and Lemma A2 prove every other component of clause 2.

For clause 3, both sides have the same placed partition, labelled action, and
current carrier. Their collision groups $G_a(P,q)$ are therefore literally
equal. Because the action has only one binary kernel, a singleton group moves
that root unchanged, whereas a two-point group joins it with exactly the
other kernel root. These are exactly the two command domains. In particular,
a fusion elsewhere cannot be mistaken for an absorption of the selected
carrier. No independently chosen event supplies this guard.

In the singleton case, the selected root's tree and ancestor path stay
unchanged; its position becomes $f_a(q)$. Other roots still obey the full
raw packet update, including any independent collision. In the two-point
case, a new outer node appends exactly the record required by `Absorb`, and
its position is $c$. These are the consumer's complete update rules, proving
clause 4. The selected node is not removed in either case, so registration
persists. This also establishes the premise for the next command on the
same actual successor. $\square$

The resulting realization is a **surjective, domain-reflecting command
simulation** from registered seed-generated forest invocations to generated
consumer summaries. Surjectivity follows by taking $z_h$ for the history
generating each $U(h,F)$. Injectivity and minimality are not claimed: the
forest can retain independent-event structure or marker data that this
consumer does not observe.

## 6. Continuations and handoffs

**Corollary A4 (same-invocation path lifting).** A finite sequence of consumer
commands starting at $J_C(z,F)$ is legal if and only if its implementation is
legal starting at that **same** $(z,F)$. All intermediate summaries and
reports agree. This holds for every generated representative with that
decoded consumer state, without changing representatives between edges.

**Proof.** Apply (A-Domain) and (A-Step) successively. Each actual forest successor
retains the same selected $F$ and realizes the next consumer summary. Domain
reflection gives both directions. $\square$

**Corollary A5 (atom-renaming adequacy).** Under an atom bijection $\eta$, use
the renamed singleton seed $\iota'=\iota\eta^{-1}$ and the selected argument
$\eta(F)$. Registration, command domains, and all reports are transported;
every atom block is renamed and all event-time positions and labels stay fixed.

**Proof.** The forest handoff of Paper XXXIX Proposition 3.2 preserves the
selected node and its ancestor path up to leaf renaming. It preserves current
positions and collision groups. Thus it transports all decoder components,
both guards, and their update equations. Alternatively, the raw log snapshots
rename in exactly the same way. Corollary A4 then transports continuations.
$\square$

**Corollary A6 (bounded absorption sequence).** If the partners in
$\mathcal A_F(h)$ are $B_1,\ldots,B_t$, then

$$
 C_h=F\sqcup B_1\sqcup\cdots\sqcup B_t,
 \qquad t\le N-|F|.
$$

**Proof.** At creation the selected carrier is $F$. A `Carry` command does
not change its atom set. An `Absorb` command joins it with a disjoint nonempty
partner. All previously added atoms remain in the carrier, so every new
partner is disjoint from $F$ and from all earlier partners. Induction gives
the disjoint union and

$$
 |F|+\sum_{i=1}^t|B_i|=|C_h|\le N,
 \qquad t\le\sum_{i=1}^t|B_i|\le N-|F|.
$$

This is derived from the update equations, not a counter added to the state
or a conclusion of finite replay. $\square$

At fixed $N$, all fusions, including unrelated ones, number at most $N-1$
because each reduces the total root count by one. Arbitrarily long histories
are possible through plateau steps, not through arbitrarily many fusions at
that fixed atom count. The bounded causal sequence and finite field types
give a finite consumer state space, consistently with the forest's node bound.

## 7. What has, and has not, been accepted

The Paper XXXIX Section 6 example exercises selection distinct from the
latest marker. Register $F=\{3,5\}$ at the second fusion of `dppd`.
Its parents are $\{3\}$ at port 0 and $\{5\}$ at port 6, and its absorption
list is empty. After the following `ppd`, the latest marker is $\{1,4\}$,
but the invocation retains $F$ and its original snapshot; the absorption
list is still empty. The final `p^5d` appends precisely

$$
 (d,0,\{3,5\},6,\{0,6\},0,\{0,3,5,6\}).
$$

The current carrier is then at 0. This is a worked illustration of A2--A3,
not a substitute for their general proofs or a historical-interface certificate.

The full named consumer is specified independently from execution logs. Its
adequacy uses more than the latest-event read table: a previously selected
event remains registered throughout an arbitrarily long continuation,
including unrelated fusions permitted by the finite atom supply. Its whole
later absorption sequence is recovered by a proven causal-path decoder and
has the bound in Corollary A6.
The theorem covers both legal domains and subsequent updates on a declared
closed source domain.

No timestamp, counter, event-order field, or new marker is added to the forest.
The consumer observes neither plateau chronology nor the relative chronology
of independent fusions. Requiring those would be a different adequacy question.

This is **not** a map into the old Paper XXVII/XXVIII typed system. Old source,
selector, authorization, handoff, and transfer-membership conformance remain
unproved. No checkpoint, credit, settlement, or projectability conclusion follows from
this consumer theorem. Neither historical-interface identification nor a
second consumer is a premise of the named consumer's adequacy.
