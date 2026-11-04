# Reproducing Version 1.0

Run commands from this directory, whether obtained from the source tag or
the narrow standalone ZIP. Python 3.12+, Git and Lean 4.33.0 are required.
The recorded full replay is Windows x86-64; the owning validators bind its
exact Lean executable version string. Other platforms are not covered by
that frozen replay identity.

## Check the Shipped Closure

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python -B theorem_map.py
python -B cold_replay/verify_result.py --evidence cold_replay/results/isolated-windows-v1
```

These checks read the sources, reports and acceptance evidence. They do not
execute the Lean kernel. The original cold record is final acceptance for
this snapshot, not a claim that the person running these commands has
performed a new replay.

## Obtain the Locked Dependencies

Install the toolchain named by `lean-toolchain`. Confirm `lean --version`
and `lake --version`; the recorded Lean commit is
`d8b18978322de05a8f3dba51ef03cf5461676c17`.
Keep `lake-manifest.json` unchanged. Lake obtains packages at those locked
revisions; do not replace the lock with `lake update`.

The following uses the same official cache scope and module selection as
the accepted cold run:

```powershell
$env:MATHLIB_NO_CACHE_ON_UPDATE = '1'
$env:MATHLIB_CACHE_DIR = Join-Path $PWD '.lake/fresh-mathlib-cache'
$modules = @(
  'Mathlib.Algebra.BigOperators.Intervals', 'Mathlib.Algebra.BigOperators.Option',
  'Mathlib.Data.Finset.Basic', 'Mathlib.Data.Finset.Powerset',
  'Mathlib.Data.Fintype.Basic', 'Mathlib.Data.Fintype.BigOperators',
  'Mathlib.Data.Fintype.Card', 'Mathlib.Data.Fintype.Powerset',
  'Mathlib.Data.Nat.Choose.Basic', 'Mathlib.Data.Nat.Choose.Vandermonde',
  'Mathlib.Data.ZMod.Basic', 'Mathlib.Tactic'
)
lake --no-cache exe cache get --cache-from=master,legacy --repo=leanprover-community/mathlib4 @modules
if ($LASTEXITCODE -ne 0) { throw 'Dependency acquisition failed' }
```

For a new isolated cold run, begin with empty cache directories and a newly
acquired toolchain. [cold_replay/README.md](cold_replay/README.md) records the
accepted run's environment and source-acquisition recovery. Its historical
`prepare.py` procedure used a local source overlay; a new public-archive
replay instead starts from the extracted source snapshot here.

## Replay the Nine Owners

```powershell
$validators = @(
  'validate_companion.py',
  'interfaces/validate_interfaces.py',
  'classification/validate_classification.py',
  'chains/validate_chains.py',
  'converse/validate_converse.py',
  'fibres/validate_fibres.py',
  'summary/validate_summary.py',
  'counting/validate_counting.py',
  'refinements/validate_refinements.py'
)
foreach ($validator in $validators) {
  python -B $validator
  if ($LASTEXITCODE -ne 0) { throw "Replay failed: $validator" }
}
```

Each owner rebuilds its declared proof modules and compares the new report
with the frozen signature, axiom and graph data. Do not use `--freeze`.
`lake build` alone builds the original origin target, not all nine layers.
`RIME_LAKE_EXE` may select an absolute Lake executable.

## Tests and Final Check

```powershell
$suites = @(
  'tests', 'interfaces/tests', 'classification/tests', 'chains/tests',
  'converse/tests', 'fibres/tests', 'summary/tests', 'counting/tests',
  'refinements/tests', 'map_tests'
)
foreach ($suite in $suites) {
  python -B -m unittest discover -s $suite -p 'test_*.py' -v
  if ($LASTEXITCODE -ne 0) { throw "Tests failed: $suite" }
}
python -B theorem_map.py
```

The accepted run passed 94 tests. Historical Git byte checks are optional
in a full checkout with the referenced commits: `theorem_map.py
--check-upstream-git`. The default checks also work without `.git`.
The frozen files remain immutable during a new replay; retain new output
logs separately instead of editing the accepted record.
