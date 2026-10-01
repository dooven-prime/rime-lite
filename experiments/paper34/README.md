# Paper XXXIV Survivor-Incidence Evidence Package

**Paper status:** Version 1.0 release candidate.

**Execution status:** runnable with the Python standard library.

**Evidence role:** bounded consistency control for the canonical Paper XXXIV
manuscript. The all-$n$ claims are proved in the manuscript; the retained
finite result is not their proof or an independent Computational Certificate.

## Inheritance Admission Gate

Before Paper XXXIV inherits a result from Papers XXIX, XXXI, or XXXII, run the
versioned owner replay gate from the exact release tags:

~~~powershell
python tools/release/verify_inheritance_gate.py tools/release/paper34-inheritance-gate.v1.json
~~~

The mathematical admission rule is stricter than a generic same-witness
firewall. Every theorem-facing domain object must reference the declared
concrete state space and its incidence or transition relation. An abstract
statement over an unconstrained witness type, including
`separate_witnesses_do_not_combine`, is not domain evidence and cannot
discharge this gate.

## Object

The producer follows five distinct source lineages in the normalized partial
return system. It retains the complete terminal witness $(\lambda,u)$ and
records

$$
\beta_{\lambda,u}=\varepsilon_\Delta p^ua\lambda.
$$

The fused pair is the two-element fiber over $\Delta$; the restriction to the
other three source labels is the survivor placement.

## Bounded Controls

The default run uses $(n,\Delta)=(6,1)$, the source injection
$(1,2,3,4,5)$, and all $5!=120$ branch permutations. It checks the canonical
identity branch against Paper XXIX and searches for two branches with the
same fused-pair reachability set but different survivor spectra.

The retained result also checks every rotation and reflection of the one-lane
cycle for $6\le n\le9$. Those rows control the orientation-character formula
recorded in `ONE_LANE_DIHEDRAL_SURVIVOR_CLASSIFICATION.md`; they are not its
proof.

## Owned Files

| File | Role |
|---|---|
| `survivor_incidence_audit.py` | exact labelled-lineage producer |
| `results/survivor_incidence_n6_v2.json` | complete six-point branch control plus bounded dihedral-family rows |
| `ONE_LANE_DIHEDRAL_SURVIVOR_CLASSIFICATION.md` | symbolic all-$n$ theorem note |
| `lean/` | paper-owned partial formalization of the incidence/counting/non-descent spine |
| `validation/validate_lean_formalization.py` | Lean scope validator and optional build replay |
| `validation/validate_survivor_incidence_audit.py` | static validator and optional exact replay |
| `validation/validate_source.py` | manuscript, citation, and theorem-surface lint |
| `development-manifest.json` and `validation/validate_package.py` | digest-bound paper-owned source closure and aggregate validator |

Run:

~~~powershell
python experiments/paper34/survivor_incidence_audit.py
~~~

Write a result explicitly:

~~~powershell
python experiments/paper34/survivor_incidence_audit.py --output experiments/paper34/results/survivor_incidence_n6_v2.json
~~~

Validate the retained bytes and claims, or replay the producer:

~~~powershell
python experiments/paper34/validation/validate_survivor_incidence_audit.py
python experiments/paper34/validation/validate_survivor_incidence_audit.py --replay
python experiments/paper34/validation/validate_lean_formalization.py
python experiments/paper34/validation/validate_lean_formalization.py --replay
python experiments/paper34/validation/validate_source.py
python experiments/paper34/validation/validate_package.py
python experiments/paper34/validation/validate_package.py --replay-finite --replay-lean
~~~

The direction ledger under `papers/paper34/` is research provenance and is
not a dependency of these validators or of the public release identity.

## Public Release Validation

Freeze the outer release manifest and its self-excluding receipt only after
the manuscript, paper-local bibliography, reader PDF, development closure,
release environment, and public validator are final:

~~~powershell
python experiments/paper34/validation/validate_public_package.py --write-manifest
python experiments/paper34/validation/validate_public_package.py --replay --write-receipt
python experiments/paper34/validation/validate_public_package.py --replay
~~~

The public receipt records local closure verification and explicit replay
status. It does not independently validate the mathematical argument.

## Known Nonclaims

The finite audit is not:

- the proof of the all-$n$ dihedral survivor classification;
- a proof that any coarser summary descends outside its exhausted domain;
- a typed transfer, authorization, or projectability theorem;
- a recursive-return or credit-settlement result.

An absent hostile pair remains OPEN. Separate terminal witnesses may not be
combined into one incidence claim.
