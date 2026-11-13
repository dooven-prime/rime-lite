# Paper XLIV Bounded Controls

The source files here are a narrow extraction of the local exploratory
`paper40-sf-bounds` prefix-observer control. The saved
[`prefix_observer_spectrum.v1.json`](results/prefix_observer_spectrum.v1.json)
is the original bounded report; it was not regenerated to create this
candidate. The code enumerates actual singleton-seed states, minimizes each
finite output machine, and compares the complete partition with Paper XLIV's
normal-form key for all 20 positive-depth cases at `n=3..7`.

Run from this directory:

```text
python -B prefix_observer_spectrum_control.py --max-n 7
python -B -m unittest test_prefix_label_update test_prefix_observer_supercritical -v
```

The six tests include per-transition event/label correspondence, the
chain-length convolution and exact reweighting, the finite deficit bound,
and the exact decomposition (6.17). The minimizer is independent of the
closed counting formula but shares the same raw transition/event code;
this is not an independently implemented dynamics oracle. Finite tests
do not establish the asymptotic growth or Gaussian limit.
