# Carrier Accessibility Census Results

These files are bounded computational companions for Paper XX,
*All-Depth Carrier Accessibility for Routed Composition*.

| Model | Dimension | Sectors | Enumerated depth | Support-path pairs at final depth | Composition-active pairs | Strictly obstructed pairs |
|---|---:|---:|---:|---:|---:|---:|
| Z2 regular + regular | 4 | 3 | 3 | 9 | 7 | 2 |
| S3 natural + regular | 9 | 6 | 2 | 36 | 28 | 8 |
| Rubik canonical representation | 228 | 9 | 2 | 53 | 43 | 10 |

The separate `within_carrier_obstruction_v1.json` artifact is an exact integer
census for a one-carrier four-dimensional control. Among 108 complete
depth-two labelled routes it finds 24 supported candidates, 16 active
products, and eight strict shared-carrier image--kernel obstructions. It is not
part of the thresholded table above.

The counts are for ordered endpoint pairs and include diagonal pairs when
present. In all three models, the strict difference consists of routes whose
endpoints have disjoint declared carrier support.

Each result also stores `carrier_path_pair_counts`,
`cross_carrier_stitch_pair_counts`, and
`within_carrier_obstructed_pair_counts`. At the final depths the carrier-path
counts equal the composition counts in all three registered models; the
support/composition gaps are therefore cross-carrier stitched paths in these
bounded observations.

For Rubik depth 2, the ten ordered obstruction pairs are the two orientations
of five previously recorded graph-only pairs:

```text
S2--S4, S3--S9, S4--S5, S4--S8, S6--S9.
```

The JSON key `minimum_active_depth_within_bound` is deliberately bounded.
A null value does not assert infinite-depth inaccessibility. The exact
all-depth conclusion comes from the carrier theorem only when endpoint
carrier supports are disjoint.

For the Rubik census, 38 ordered pairs are null through depth 2: 26 are exact
all-depth carrier obstructions, while 12 have overlapping carrier support.
The artifact in `image_kernel/` gives an exact enumeration certificate for all
34,992 depth-two route indices over those 12 registered pairs. Its matrix
classifications are a separate bounded numerical observation: every route has
a prefix or suffix factor below tolerance, and none is observed as a
nontrivial image--kernel annihilation between two active factors. This does not
establish exact projected-factor zero or exact all-depth inaccessibility.
