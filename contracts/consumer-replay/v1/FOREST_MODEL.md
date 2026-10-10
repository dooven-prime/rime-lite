# Placed-Fusion-Forest Representation

This is one representation of the consumer specification, with the same
`Q,p,d,Omega,iota` and ordered kernel ports. The finite Case admits only
states generated from the declared singleton seed, not arbitrary well-formed
forests bearing unverified event labels.

## State and Update

A leaf names one atom. A binary internal node stores its two children at
their **event-time** positions `k_0,k_1`, the letter `d`, and target `c`.
Each node's leaf set is the union of its disjoint child leaf sets. A state
`z = (forest,m)` places one root at each occupied position and designates
either no marker or one retained internal node as the latest marked event.
The roots' leaf sets partition `Omega`; internal nodes are persistent.

For either letter `a`, group all occupied roots by destination `f_a(q)`.
If a destination receives one root, move that tree unchanged. If `d`
merges the two occupied kernel roots, create one new root with children
indexed by their pre-step positions, retaining `d,c`. No other collision
is possible. Update every root, including roots unrelated to a selected
consumer event. The marker is the new node on fusion and otherwise stays
unchanged. A previously selected node persists even if the latest marker
changes.

Packet projection takes each placed root's leaf set. It agrees with raw
push-forward after every letter. The state has no timestamp, plateau
counter, or stored raw word. Its marker is not the selected consumer `F`:
`F` is supplied as a fixed invocation argument.

## Decoder and Domain

For a generated state `z` and nonempty `F`, registration holds exactly when
one internal node `v_F` has leaf set `F`. Node leaf sets are unique: nested
nodes have strictly increasing sets, and incomparable nodes are disjoint.
At creation `v_F` is a root. Each later absorption of its containing root
adds exactly one outer ancestor; fusion elsewhere does not alter that path.

Decode the origin from `v_F`'s local children, their positions, `d`, and
`c`. Decode the complete selected absorption list from the strict ancestors
of `v_F`, from inner to outer: the child containing `v_F` is the carrier
parent and the other child is the partner. Their indices are event-time
addresses. Decode the current carrier from the **position and leaf set** of
the placed root containing `v_F`. Decode the full partition from **all**
placed roots. This recovers the independent log summary, not merely its
latest event.

For `Carry(a)` or `Absorb(a)`, calculate the guard from the full projected
partition and that carrier. When enabled, apply the existing forest action
and keep the same `F`; do not choose a new node. In particular, `Carry(d)`
with fusion elsewhere creates a new node and changes the latest marker and
partition, but it adds nothing to `F`'s ancestor path.

The event-to-node and absorption-to-ancestor correspondences are paper
arguments about the declared generated domain. A finite Case can check
instances of these equations; agreement on its finite witness is not a
machine-checked proof of the general correspondence.
