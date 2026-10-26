# Technical Notes and Reproduction Details

## A Path Is Not a State: Exact Predictive Refinement of Fixed Connectome Partitions

WuJun Chen | RIME Paper XVIII, version 1.0

These notes retain finite-domain definitions, historical counts, and replay
instructions supporting the research report. They do not enlarge the theorem
domain or replace the published evidence packages of Papers XVI and XVII.

## T1. Finite Domains

**Table T1. Distinct operations and their checking data.**

| Operation | Finite domain | Obstruction and checking data |
|---|---|---|
| Nonnegative depth-two route | Full-release edge table; three annotation policies | Disjoint incoming and outgoing relay sets; complete relay scan |
| Signed routed words | Signed normalized carrier; somaSide and superclass | Exact routed-product zero on a supported word |
| Unit-source one-step prediction | 163,439 eligible sources; sector means | Unequal positive outgoing sector profiles in one observation fiber |
| Reached-set factorization | 711 selected sources; exact rational orbits through horizon four | Unequal successors in a fiber, or successor outside the verified image |

The nonnegative coverage carrier includes bodies outside the signed dynamic
carrier. The earlier first-reference successor scan is numerical; the
two-source certificate establishes one exact inequality, while the
full-domain census groups rational profiles by canonical integer keys.
Reached-set replay starts from retained exact-orbit records rather than a
fresh reconstruction of the microscopic producer.

## T2. Nonnegative Coverage

Typed core excludes bodies absent from the curated annotation table. Relay
strict admits them at endpoints; coverage inclusive also admits them as
relays. A retained missing value within the table differs from an absent
body.

**Table T2. Supported and lifted depth-two triples by annotation policy.**

| Policy | Supported | Lifted | Incremental supported / lifted |
|---|---:|---:|---:|
| Typed core | 6,237 | 4,970 | -- |
| Relay strict | 7,019 | 5,751 | 782 / 781 |
| Coverage inclusive | 7,831 | 6,125 | 812 / 374 |

Of the last increment's 812 candidates, 438 have no common microscopic
relay. These counts do not belong to the signed dynamic test.

\newpage

## T3. Earlier Numerical Successor Scan

Within each source sector, the registered scan compared eligible unit
sources with its first eligible node. Witness counts are neither all-pairs
counts nor prevalence estimates.

**Table T3. Paper XVI first-reference one-step observation defects.**

| Partition | Sectors | Witnesses | Largest L1 defect |
|---|---:|---:|---:|
| superclass | 28 | 141,296 | 0.005651574473947287 |
| somaSide | 4 | 163,435 | 0.0004874856094383272 |

## T4. Coordinate-Resolved Census

For source sector $E_i$ and target coordinate $j$, let $n_{ijq}$ count
sources with profile coordinate $q$. The exact number of unordered
same-observation source pairs separated by $j$ is

\[
D_{ij}=\binom{N_i}{2}-\sum_q\binom{n_{ijq}}{2}.
\]

**Table T4. Absolute somaSide pair separations by target coordinate.**

| Target coordinate | Separated within-sector source pairs |
|---|---:|
| L | 5,008,763,423 |
| R | 4,993,360,210 |
| missing-label | 3,413,153,081 |
| M | 1,307,422,058 |

The denominator is 5,432,178,301 unordered within-sector pairs. Pairs
separated by multiple coordinates appear in multiple rows, so these counts
are not additive. Figure 2 gives the corresponding percentages.

## T5. Common Reached-Set Support

Paper XVII selected 711 eligible sources across 25 nonempty source strata.
The common comparison domain of the three history orders is
$D_0\times\{2,3\}$.

**Table T5. Exact history fibers on the common 1,422-window domain.**

| History order | Windows | Distinct values | Largest fiber | Failure fibers |
|---|---:|---:|---:|---:|
| 0 | 1,422 | 1,228 | 51 | 0 |
| 1 | 1,422 | 1,228 | 51 | 0 |
| 2 | 1,422 | 1,228 | 51 | 0 |

The three partitions, not just their counts, agree. Five persistent
cohorts have sizes 51, 25, 19, 4, and 3. Each of the $t=2,3,4$ slices
has 614 observation values. The $t=2,3$ slices are disjoint, while every
$t=4$ value escapes their combined verified image. Appendix A gives the
distinct-state and drive-off argument.

## Reproduction

The [Paper XVIII artifact index](https://github.com/dooven-prime/rime-lite/blob/paper18-v1.0/experiments/paper18/README.md)
binds the report's local release closure and its earlier source records.

The source packages are independently identified as
[Paper XVI](https://github.com/dooven-prime/rime-lite/tree/paper16-v1.0/experiments/paper16)
and [Paper XVII](https://github.com/dooven-prime/rime-lite/blob/paper17-v1.0/experiments/paper17/00_START_HERE.md).
The [predictive-profile Dataset](https://doi.org/10.5281/zenodo.23555888)
contains the exact full-domain census, source and focused controls, pinned
derived carrier, and figure sources. Its verifier checks inventory and
digests; optional replay recomputes the census.

The [separate compact witness package](https://github.com/dooven-prime/rime-lite/blob/4d7595936e9fb2271a870ec560e77c021a64fdb9/papers/unnumbered/from_support_to_state/witness/malecns_two_source_witness_v1.0.zip)
contains the two-source certificate, checker, controls, and three Paper XVI
metadata records. Its default check verifies compact arithmetic. Source-row
re-extraction additionally needs the byte-pinned carrier from the Dataset.
The Dataset DOI does not identify this ZIP. Neither replay independently
reconstructs the original connectome pipeline.
