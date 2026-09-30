# Paper XXXII: Five-Token Permutation Evidence Package

This directory is the paper-owned evidence package for
[Paper XXXII](../../papers/paper32/Paper%20XXXII.md). It is self-contained and
does not read the broader exploratory source tree.

**Status:** version 1.0 release candidate with a nested paper-owned development
closure. Its receipt records local closure verification, not independent
mathematical validation of the manuscript.

## Evidence Layers

| Layer | Owned files | Scope |
|---|---|---|
| All-$n$ mathematics | the manuscript | Lane-wise dihedral closure, guarded gap transfer, single-lane order-fiber transitivity, and the complete single-lane branch-permutation dichotomy |
| Source and reference audit | validation/validate_source.py | Bibliography identities, citation closure, equation tags, theorem numbering, cross-references, claim boundaries, and source hygiene |
| Bounded consistency controls | affine_five_token_audit.py, results/, and validation/validate_affine_five_token_audit.py | Exact replay of the retained finite domains |

The finite result has status FINITE_SANITY_CHECK_NOT_ALL_N_PROOF. It is a
development control, not an all-$n$ proof and not an independent
Computational Certificate.

## Source Audit

The source validator checks:

- an LF-only UTF-8 manuscript and bibliography;
- absence of control-character and common TeX-escape corruption;
- unique equation tags and resolved equation references;
- the exact theorem/lemma/proposition/corollary declaration surface;
- resolved numbered theorem references and local proof blocks;
- an exact paper-owned bibliography slice with no missing or unused keys;
- stable DOI/title metadata for the cited external and released RIME papers;
- the published Paper XXIX--XXXI citation identities, including their Zenodo
  DOIs;
- the raw/typed and finite/all-$n$ claim firewalls.

Run:

~~~powershell
python experiments/paper32/validation/validate_source.py
~~~

## Bounded Affine Audit

The standard-library-only producer constructs the normalized five-token
partial system directly.

### Single-lane domain

For every $6\le n\le12$, every $\Delta$ coprime to $n$, and every unit
multiplier modulo $n-1$, it checks:

- identity Safe-Hit equals lane adjacency;
- every enabled identity edge preserves the hole-deleted token order;
- each of the two token-order fibers is strongly connected;
- every applicable local gap transfer has the manuscript's exact effect; and
- the finite Safe-Hit set is adjacency for $u=\pm1$ and the full state space
  otherwise.

This retained scan is an affine normalizer subfamily of the manuscript's
stronger arbitrary-permutation theorem. It checks the original arithmetic
controls and the guarded mobility mechanism; it is not presented as an
exhaustion of $\operatorname{Sym}(E)$.

### Single-lane arbitrary-permutation control

For $n=6,7$, every coprime kernel separation and every branch permutation of
$E$ is checked exactly. The audit verifies that cycle automorphisms have the
adjacency Safe-Hit set, every nonautomorphism has the full Safe-Hit set, and
each nonautomorphism carries at least one physical nonedge to an edge. This
is still a bounded consistency control, not the all-$n$ proof.

### Multi-lane hostile domain

For $6\le n\le9$, every non-coprime kernel separation, and every affine
normalizer parameter $(u,\sigma,\boldsymbol\beta)$, it records:

- the exact Safe-Hit set and whether it is ADJ, SAME, or intermediate;
- mixed-sign lane-wise dihedral controls;
- variation across equal multipliers with different phases or lane
  permutations; and
- the first witness for each distinct Safe-Hit set.

The retained totals are:

| Domain | Retained total |
|---|---:|
| Single-lane $(n,\Delta)$ cells | 36 |
| Single-lane state cases | 53,300 |
| Single-lane unit cells | 172 |
| Identity labelled edges | 481,680 |
| Local gap-transfer checks | 147,000 |
| Exhaustive single-lane permutation branches ($n=6,7$) | 4,560 |
| Cycle-automorphism branches in that control | 92 |
| Nonautomorphism branches in that control | 4,468 |
| Multi-lane affine branches | 320 |
| Multi-lane multiplier cells | 18 |
| Mixed-sign multiplier cells | 4 |

The bounded hostile scan currently contains no intermediate Safe-Hit set and
no same-multiplier variation. This is a retained finite observation only. It
does not prove multiplier descent or the open multi-lane dichotomy.

Check the retained result:

~~~powershell
python experiments/paper32/validation/validate_affine_five_token_audit.py
~~~

Replay it:

~~~powershell
python experiments/paper32/validation/validate_affine_five_token_audit.py --replay
~~~

Regenerate it explicitly:

~~~powershell
python experiments/paper32/affine_five_token_audit.py --single-min-n 6 --single-max-n 12 --permutation-max-n 7 --hostile-max-n 9 --output experiments/paper32/results/affine_five_token_audit_v1.json
~~~

## Lean Boundary

This initial package does not claim a Paper XXXII Lean formalization.
Paper XXXI already formalizes the inherited generic reachability, quotient,
skew-transport, and same-witness implication spine. Repeating those
declarations under a new namespace would add no Paper XXXII theorem coverage.

A useful later formalization should target the genuinely new combinatorial
content: directed unit transfers on five-part weak compositions, the
resulting order-fiber transitivity, and the nonedge-to-edge conversion for a
non-automorphism of $C_L$. Until those proofs are mechanized, the all-$n$
permutation theorem remains manuscript mathematics.

## Development Closure

development-manifest.json binds the manuscript, bibliography, source audit,
finite producer and result, documentation, and validators by SHA-256. It
intentionally claims no release identity. The public release manifest binds
that immutable development closure together with the reader PDF, release
environment, and public-package validator.

papers/paper32/DIRECTION_DRAFT.md is a research ledger and is intentionally
excluded from this closure and from any future reader release.

~~~powershell
python experiments/paper32/validation/validate_package.py
python experiments/paper32/validation/validate_package.py --replay
~~~

## Release Validation

The release receipt is excluded from its own closure. Regenerate the canonical
release manifest and receipt only after the manuscript, bibliography, reader
PDF, development closure, release environment, and validator are frozen:

~~~powershell
python experiments/paper32/validation/validate_public_package.py --write-manifest
python experiments/paper32/validation/validate_public_package.py --replay --write-receipt
python experiments/paper32/validation/validate_public_package.py --replay
~~~

## Claim Boundary

The package proves no additional all-$n$ mathematics. In particular, it does
not establish the open multi-lane promotion dichotomy, multiplier-only
descent, survivor placement, typed transfer membership, projectability,
recursive return, credit settlement, or a reset bound.
