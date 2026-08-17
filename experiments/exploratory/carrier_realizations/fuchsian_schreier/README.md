# Finite Fuchsian-Schreier Carriers v2

**Research status:** typed carrier candidate with exact finite census controls.

**Execution status:** the modular and bounded triangle censuses, replay
validator, and hostile controls are runnable with the repository Python
environment.

**Paper evidence:** none by package placement. Paper VIII v2.1 separately
registers only `results/modular_p1_census_v2.json` and
`results/triangle_low_index_census_v2.json` through its paper-owned promotion
record and replay receipt. The remaining package files are public support or
exploratory controls, not paper evidence.

Paper VIII v2.1 consumes the two bundles only as source-addressed provenance
through its paper-owned promotion record and replay receipt under
`experiments/paper8/`. That downstream promotion does not change the status of
this exploratory package.

This package retains only finite permutation actions associated with modular
and hyperbolic triangle-group presentations. It does not include the legacy
report builders, Hecke comparison, Teichmuller protocol, Fuchsian numerical
slice, or Selberg heat-trace proxy.

## Typed Carrier

For each finite action on a state set `Omega`, the declared static carrier is

```text
V = C^Omega
Q = coordinate projectors from one declared state partition
Y = a labelled symmetric permutation alphabet.
```

Generator labels remain part of the data. Equal represented permutations with
different source labels are not merged. An inverse label is omitted only when
it repeats the same generator label's self-inverse operator.

The modular family uses

```text
PSL(2,Z) = <S,R | S^2=R^3=1>
Omega = P^1(F_p)
Y = {S,R,R_inv}
Q = coordinate projectors for T-orbits.
```

The triangle census uses transitive permutation homomorphisms of

```text
Delta(l,m,n) = <x,y,z | x^l=y^m=z^n=xyz=1>
```

through a declared index bound. Cycle partitions of `x`, `y`, and `z` are
three separate sectorizations. Their intersection tables are retained as
alignment controls; no equivalence or refinement is inferred.

## Accessibility Objects

The package computes three separate layers:

```text
Path_d(R1[Y])   Boolean powers of aggregate direct support
Route_2[Y]      actual Q_target P_second Q_middle P_first Q_source products
W_d[Y]          actual ordered permutation words of exact length d
```

For a displayed left-to-right word `a1...ad`, states are acted on in that
order and the represented matrix product is `P_ad...P_a1`. Exact first-hit
word depth is computed over `d >= 1` only after finite image saturation; the
empty word is excluded. The shortest nonempty identity word is retained in
the saturation certificate. A bounded word layer is not used to declare
infinity.

The hostile suite contains a four-state permutation example for which
`Path_2` is full while `W_2` is diagonal. Thus graph powers cannot replace
actual ordered products even on a finite group carrier with nonsingleton
sectors.

## Exact Arithmetic

Certificate arithmetic uses Python integers and `fractions.Fraction`:

- permutation relations and finite image closure;
- coordinate block ranks and support;
- routed products and actual word layers;
- rational graph-Laplacian rank;
- fraction-free Matrix-Tree cofactor;
- characteristic polynomial through exact Newton identities.

No NumPy eigensolver or float64 field enters either v2 bundle. The graph
Laplacian is a finite labelled Schreier/group Laplacian and is not a surface
Laplace-Beltrami operator.

## Run

From the repository root:

```bash
python experiments/exploratory/carrier_realizations/fuchsian_schreier/modular_census.py --primes 3 5 7 11 13 17 --max-word-depth 4 --out experiments/exploratory/carrier_realizations/fuchsian_schreier/results/modular_p1_census_v2.json --markdown experiments/exploratory/carrier_realizations/fuchsian_schreier/results/modular_p1_census_v2.md
python experiments/exploratory/carrier_realizations/fuchsian_schreier/triangle_census.py --max-index 7 --max-word-depth 3 --out experiments/exploratory/carrier_realizations/fuchsian_schreier/results/triangle_low_index_census_v2.json --markdown experiments/exploratory/carrier_realizations/fuchsian_schreier/results/triangle_low_index_census_v2.md
python experiments/exploratory/carrier_realizations/fuchsian_schreier/validate.py experiments/exploratory/carrier_realizations/fuchsian_schreier/results/modular_p1_census_v2.json
python experiments/exploratory/carrier_realizations/fuchsian_schreier/validate.py experiments/exploratory/carrier_realizations/fuchsian_schreier/results/triangle_low_index_census_v2.json
python experiments/exploratory/carrier_realizations/fuchsian_schreier/hostile_cases.py
```

The committed bundles are rebuilt from their declared scope and compared by
canonical JSON equality. Updating a result and its top-level digest does not
bypass replay against the frozen producer implementation.

## Public Package Boundary

The public package contains the finite carrier core, two deterministic census
producers, their exact JSON bundles and Markdown projections, the replay
validator, and the four-state hostile control. These files are sufficient to
rebuild and validate the declared public finite scope.

Detailed source-repository migration notes and historical excluded bytes are
author-side provenance. They are not required to execute this package and are
not part of its public closure. Public exclusions are stated directly in the
Known Nonclaims below.

## Known Nonclaims

- The bounded triangle census is not a classification beyond its signatures,
  index bound, and simultaneous-conjugacy convention.
- A relation-preserving quotient may have proper-divisor generator orders;
  those records are labelled and are not full-signature-order realizations.
- Permutation words have full operator rank, so this carrier supplies no rank
  collapse, synchronization, or mortality result.
- No Lie/Hall carrier or Lie depth is declared.
- No expansion, Ramanujan, arithmetic spectral, quantum-chaos, or asymptotic
  cross-prime theorem is claimed.
- No surface geometry, Hecke, moduli, Selberg, SOFRS, SOFAUDIT, or action
  semantics is included.
