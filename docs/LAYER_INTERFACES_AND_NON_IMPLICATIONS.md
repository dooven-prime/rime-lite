# Observation, History, and Cost Interfaces for Circular Coalescence

Papers XLI--XLV use a fixed circular adjacent-collapse action; Papers XXXIX
and XL supply consumer interfaces that require a compatible instantiation.
These results do not form one chain of theorem implications. For the fixed
action let $n\ge3$, the chronological alphabet be $A=\{p,d\}$, and the
initial placement be declared. Papers XLI, XLIII and XLIV use the singleton
seed and a selected registration rule; Paper XLV also allows arbitrary
disjoint initial packets. Initial state, event fields, consumer and
raw-letter cost are part of each theorem's input.

The common question is which history--endpoint objects can occur, which
history can be forgotten while preserving future observations, how costly
it is to realize a specified observation, and whether a proposed compressed
state supports a declared consumer.

## Quantities and Theorem Interfaces

An observation contract $\mathcal O$ declares a current read
$r_{\mathcal O}(u)$ and outputs on raw-letter continuations. Let
$T_{\mathcal O}(u;z)$ be the residual trace emitted by running suffix $z$
*after* history $u$, together with the declared read after $z$; it excludes
outputs emitted during $u$. For reachable histories $u,v\in A^*$, define

$$
u\equiv_{\mathcal O}v
\iff r_{\mathcal O}(u)=r_{\mathcal O}(v)
\quad\land\quad
\forall z\in A^*,\ T_{\mathcal O}(u;z)=T_{\mathcal O}(v;z).
$$

The observed transition/output system is deterministic and suffix-consistent:
after one common letter, the remaining observation is the corresponding
tail of the longer residual trace. Thus $\equiv_{\mathcal O}$ is a right
congruence. Its minimal behavioral quotient has size

$$
Q_n(\mathcal O)=|A^*/{\equiv_{\mathcal O}}|.
$$

If the contract also supplies a terminal target map
$o_{\mathcal O}:A^*\to Y_{\mathcal O}$, define, only for an attained target
$y\in o_{\mathcal O}(A^*)$,

$$
L_n(\mathcal O,y)=\min\{|w|:o_{\mathcal O}(w)=y\}.
$$

The shorthand $\mathcal O(w)=y$ refers to this terminal map, not to the
entire future-output contract. $L_n$ uses the fixed raw alphabet and start;
for arbitrary starts write $L_{n,P_0}$. A count of realized outputs, a
minimal right-congruence count and a shortest-word cost are different
quantities.

| Layer | Theorem input | Output | Needed dependency; non-implication |
| --- | --- | --- | --- |
| [Papers XLI](../papers/paper41/Paper%20XLI.md) and [XLII](../papers/paper42/Paper%20XLII.md) | Fixed circular action, singleton seed, selected source set and registration rule | Actual selected chains and dependent placement fibres | Uses constructive reachability; a summary count is not a predictive-state count. XLII extends the proper-arc domain, rather than supplying an input to XLIV. |
| [Paper XLV](../papers/paper45/Paper%20XLV.md), Sections 4--6 and Appendix A | Initial placement, complete ordered fusion schedule, compatible literal endpoint, unit-cost $p,d$ | Joint realization, dependent log--endpoint bijection, quadratic bound, specified all-right optimum | Uses cyclic order and actual routing; it does not use selected-chain counts to construct its word, and its length bound does not determine $Q_n(\mathcal O)$. Numbered release candidate. |
| [Papers XLIII](../papers/paper43/Paper%20XLIII.md) and [XLIV](../papers/paper44/Paper%20XLIV.md) | Singleton-seed registered action; future-event, full-summary or prefix-memory observer | Minimal right congruence, exact class counts and prefix growth spectrum | XLIV uses actual chain/fibre counts from XLI and future-event separation from XLIII; counts alone do not prove minimality or shortest realization cost. |
| [Papers XXXIX](../papers/paper39/Paper%20XXXIX.md) and [XL](../papers/paper40/Paper%20XL.md) | Generated event-anchored domain, declared consumer $D$, candidate representation $q$ | Consumer-relative read/guard/successor decision and failure histories | Requires the declared domain and command semantics; success need not mean that $q$ is a minimal quotient. |

## Internal Dependencies and Crossings

The common base for XLI--XLV is the literal $p,d$ action, cyclic packet
order and actual effective-event semantics. A consumer branch joins it only
after its environment has been instantiated on that action:

- **History structure:** actual registered chains and placement fibres
  (XLI); proper-arc extension (XLII); prefix-label counting (XLIV).
- **Observer quotient:** future-event separation (XLIII); prefix-memory
  minimality and growth spectrum (XLIV). The chain/fibre count supplies
  realizability data, while the separation theorem supplies the missing
  minimality argument.
- **Execution cost:** admissible complete log and compatible endpoint,
  actual replay and gap routing (XLV); quadratic normal form; all-right
  surplus identity and unique raw optimum.
- **Consumer verification:** event-anchored consumer (XXXIX); candidate
  $q$ and R/G/T clauses (XL); bounded failure histories under additional
  complete-state and factorization hypotheses.

The following table distinguishes proved maps from proposed shortcuts.

| Cross-layer step | Status | Exact bridge or missing information |
| --- | --- | --- |
| Complete log and endpoint $\to$ registered selected summary | Valid projection on the registered domain | Fix $F$ and read its first exact-creation event, later carrier absorptions and terminal placement from the actual complete log; outside that domain the read is optional rather than a registered summary. |
| XLI chain/fibre classification $\to$ XLIV prefix counts | Valid input, not a complete proof | Prefix counts use actual chain lengths and placements; XLIII's future-event distinguishing theorem is additionally needed to identify minimal classes. |
| XLV quadratic compression $\to$ XLIV prefix growth spectrum | Not implied by the stated theorem alone | A short word for each realized log--endpoint pair does not count residual future-output classes. |
| XLIV quotient growth $\to$ XLV shortest-word length | Not implied by the stated theorem alone | State-cardinality growth does not determine distance to a specified historical target in the raw alphabet. |
| Minimal observer quotient $\to$ an XL candidate $q$ passing R/G/T | Conditional | The supplied $q$ must be expressible in the declared interface, its fibres must preserve reports and guards, and its enabled successors must descend. Even a refinement of behavioral equivalence need not have a successor-stable kernel. |
| XLV compression $\to$ short R/G/T rejection histories | Conditional model-level theorem | Domain membership, $q$, reports, guards and observed successors must factor through the preserved complete-log/endpoint pair. A separate source correspondence is needed for the frozen Python runtime. |

The last row is developed in the independent
[R/G/T bounded-history certificates](../experiments/rgt_bounded_history_certificates/RGT_BOUNDED_HISTORY_CERTIFICATES.md).
For its declared circular Lean state and C1-compatible fragment, the
companion proves a same-complete-state quadratic replacement and transports
R/G/T failures: each prehistory has length at most
$C(n)=\tfrac72n(n-1)$, and a T successor appends one letter. This is a
model-level result, not an archived-byte or Python-runtime equivalence
claim. The quadratic instance applies to the declared C1-compatible
circular model with $n\ge3$ sites and $2\le m\le n$ source atoms; it is not
a bound for arbitrary consumers on arbitrary state spaces. For a different consumer
or state representation, the factorization premise must be proved anew.

## Three Different Fibres

| Name | Map whose fibre is taken | Held fixed; question answered |
| --- | --- | --- |
| Placement fibre | $(o,A,P)\mapsto(o,A)$ for a registered summary | Origin and selected chain; which actual terminal placements occur? |
| Forgetful log fibre | $(\mathcal H,P^\star)\mapsto P^\star$ | Literal endpoint; how many complete ordered logs collapse to it? Paper XLV gives $(t-s)!$ at rank $s\ge2$ and $t!$ at rank one. |
| Candidate-state fibre | $q:S_F\to C$ on the declared generated domain | Candidate value; do all its complete states agree on R/G/T? |

A behavioral equivalence class for $\equiv_{\mathcal O}$ is a fourth object:
it collects histories with equal declared behavior under every suffix. None
of the three fibres above is automatically such a class.

## External Connections

**Transformation-semigroup word length.** For the singleton seed, the
literal terminal placement determines the pointwise transformation $f_w$
of source atoms. In the fixed alphabet $A=\{p,d\}$, compare

$$
\ell_A(f)=\min_{f_w=f}|w|,
\qquad
\ell_A(H,f)=\min_{\substack{f_w=f\\\mathcal H(w)=H}}|w|.
$$

For an attainable pair, $\ell_A(f)\le\ell_A(H,f)$. Paper XLV's all-right
example has $\ell_A(H_R,f_R)=\tfrac32n(n-1)-1$, whereas
$\ell_A(f_R)\le3n-4$. This is adjacent to the endpoint word-length
problem studied by [Cameron, Castillo-Ramirez, Gadouleau and Mitchell](https://doi.org/10.1007/s10801-016-0703-9),
but their $\ell(D,f)$ charges available defect-one digraph-edge
generators. Paper XLV charges only the original $p,d$ letters, so the
two length functions cannot be numerically identified.

**Complete reachability.** [Bondar and Volkov's definition](https://arxiv.org/abs/1607.00554)
requires every nonempty $S\subseteq Q$ to be the image of $Q$ under some
word. Paper XLV, Theorem 4.1 implies this property for its specified
singleton-seed circular action: choose an admissible schedule ending with
$|S|$ packets, place those packets on $S$ in cyclic order, and apply joint
realization. This is a projection from a stronger, labelled-history
statement. Complete reachability alone supplies neither a prescribed
ordered fusion log nor literal labelled packets or the $B/K/M$ budgets;
no reverse theorem is asserted.

**Observer minimization.** The future-event and prefix observers use the
classical residual-behavior viewpoint of deterministic
[Mealy](https://doi.org/10.1002/j.1538-7305.1955.tb03788.x) and
[Moore](https://doi.org/10.1515/9781400882618-006) machines.
Paper XL's R/G/T checks are a consumer-relative instance of asking whether
a proposed kernel carries outputs, enabledness and transitions; they are
not a new general quotient theorem. The model-specific results are the
exact future-event and full-summary counts in XLIII and the prefix growth
spectrum in XLIV. In XLIV's critical window,

$$
\frac{Q_n^{[\lfloor n/3+u\sqrt n\rfloor]}}
     {Q_n^{\mathrm{full}}}\longrightarrow\Phi(3u/2).
$$

This does not show that Paper XL's typed candidate language expresses
that minimal quotient, or that other consumers share its spectrum.

The two central axes are therefore distinct: forgetting history can change
the minimal predictive-state quotient, whereas requiring a prescribed
history can increase the shortest realization cost. A cross-axis conclusion
requires an explicit observation map, semantic factorization or
cost-preserving theorem.

This page indexes theorem interfaces; it is not a new paper or release
identity. Published DOIs are in the root
[Public Release table](../README.md#public-release). Paper XLV is a
numbered candidate until its own release is recorded there.
