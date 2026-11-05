# Bounded controls for fusion-log compression

These standard-library Python controls accompany the unnumbered preprint
*History-Preserving Quadratic Normal Forms for Circular Coalescence*.
Run from this directory:

```text
python -B fusion_log_arbitrary_start_control.py --max-n 6
python -B audit_math.py
```

Optional `--output path.json` writes a new report and refuses to overwrite an
existing report. The saved runs are under `results/`.

- The arbitrary-start control saturates 36 prescribed layouts across every
  rank for n=3,...,6, with two-atom packet labels. It reconstructs all 65,992
  reachable log/endpoint pairs and checks literal words and K, M, B budgets.
- The mathematical control checks both forgetful fibres on all singleton
  log/endpoint objects for n=3,...,6; bounded BFS verifies the all-R shortest
  word and uniqueness, and a separate endpoint-only BFS changes only the
  observation contract. Detour words exercise rotation excess, unchanged
  defects and carrier backslides, including the rank-one tail.
- The cost-identity loop checks every valid (n,t,s) triple through n=80.
  The all-parameter algebra and bijections are proved in the manuscript;
  these finite checks do not replace those proofs.

`fusion_log_arbitrary_start_control.py` is an exact copy of the exploratory
script of that name. `core.py` retains only its four required raw primitives
from the same exploratory source; no selected-consumer semantics is imported.
The controls share those raw transition primitives and are bounded consistency
checks, not independent validation of the all-parameter proofs. The saved
`c2` filenames identify the retained finite runs, not the HAL manuscript's
publication version.
