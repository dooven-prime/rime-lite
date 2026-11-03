# Mathlib Attribution

The short reciprocal-limit argument in
`FutureEventAnalysis.tendsto_wallis_rational` is adapted from
`Stirling.tendsto_self_div_two_mul_self_add_one` in Mathlib's
`Analysis/SpecialFunctions/Stirling.lean`, at the pinned commit
`db584cd6d46c92f209a44c0f1c829460d327499d`.

The source file records:

```text
Copyright (c) 2022 Moritz Firsching. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Moritz Firsching, Fabian Kruse, Nikolas Kuhn
```

The license text is included in `Apache-2.0.txt`. The adaptation concerns
only the elementary reciprocal normalization. No Stirling module or
Stirling asymptotic estimate is imported by these proofs; the analytic
input for the central-binomial limit is the pinned Wallis theorem.

The Wallis theorem itself is imported from Mathlib, not reproved or claimed
as a new result of this companion.
