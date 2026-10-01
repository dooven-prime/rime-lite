# Versioned Inheritance Gate

A consuming paper must not inherit a historical receipt's `replay: true`
field as if the current verification run had reproduced that result. The
inheritance gate compares each declared tag object and target commit with the
paper's post-release anchor, materializes the verified commit SHA in an
isolated temporary directory, checks the exact tagged receipt, runs the tagged
validator with its replay option, and requires explicit truth markers from the
nested checks. A moved tag or a tag recreated as a lightweight ref is rejected.

The gate clears `PYTHONOPTIMIZE`, keeps current-HEAD bytes out of the historical
checkout, and rejects any replay that changes files present in the tag. New
build caches in the temporary directory are disposable and do not enter an
owner or consumer closure.

For the Paper XXXIV research package, run:

```bash
python tools/release/verify_inheritance_gate.py \
  tools/release/paper34-inheritance-gate.v1.json
```

This verifies the bounded computational and formalization controls of Papers
XXIX, XXXI, and XXXII. It does not import their theorem scope automatically.
The consumer must still bind the exact owner releases and state a paper-local
mathematical dependency.

The Paper XXXIV semantic gate is also fail closed: every theorem-facing domain
object must reference the declared concrete state space and its incidence or
transition relation. An abstract statement over an unconstrained witness type
is a useful logical firewall, but it cannot by itself discharge a domain
admission or same-witness theorem.
