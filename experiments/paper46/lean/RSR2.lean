import RSR2.Model
import RSR2.Crossing
import RSR2.Bell
import RSR2.Parameterized
import RSR2.Construction
import RSR2.Executable
import RSR2.CanonicalEndpoint
import RSR2.BellProjection
import RSR2.LowerRestrictedOrder
import RSR2.RetentionNecessity
import RSR2.RetentionSufficiency
import RSR2.TransferMass
import RSR2.MinimumTransferMass
import RSR2.LowerPacketLedger
import RSR2.LowerPortGeometry
import RSR2.UpperPortVacancy
import RSR2.PortCostSharpness
import RSR2.SingletonWordSymmetry
import RSR2.SingletonElevatorSkeleton
import RSR2.SingletonOptimalClassification
import RSR2.SingletonOptimalCounting
import RSR2.SequentialPreparationDebts
import RSR2.ForcedPreparationDebts
import RSR2.SingleVacancyDebt
import RSR2.SingleVacancyWitness
import RSR2.SingleVacancyOptimality
import RSR2.SingleVacancySlideCount
import RSR2.AntipodalFusionGate
import RSR2.PacketRankLedger
import RSR2.AntipodalLinearWitness
import RSR2.AntipodalLinearBounds

/-!
# RSR-2-A/B Bell realization and RSR-2-C geometry and cost ledgers

This is an independent, small Lean companion for the exploratory restricted
stacked-ring model.  The checked scope includes the four-site crossing
certificate and the all-parameter ordered-partition loading/fusion ledger.
The executable layer now also proves the guarded execution of one instruction,
the plan-level append bridge, and successful execution of the generated
`interleavedPlan` for every `OrderedPartition`.  The coordinate layer identifies
that actual endpoint with the canonical stacked placement, characterizes each
block at its prefix-sum site, and reuses the existing raw-letter cost bound.
The projection layer proves that every unordered partition has an ordered
presentation and that the actual endpoint realizes its same-block relation.
The lower-order layer independently proves preservation by every successful
raw letter and word, then derives cyclic packet intervals and the physical
circular order of distinct lower packets. It imposes no source order above.
The retention layer converts the lift into finite filtered source cycles,
proves necessity and constructive sufficiency for ordered and unordered
endpoint allocations over the actual guarded executor. The independent
transfer-mass observer charges each successful elevator by its pre-step source
packet's atom count. It projects to the existing guarded run and proves the
arbitrary-history mass balance. From the singleton seed, transferred mass is
exactly the endpoint's upper atom count, or `n` minus its lower atom count.
The minimum transferred mass for each endpoint partition is also formalized
from the exact allocation criterion. The independent lower-packet observer
counts effective lower fusions and every nonfusing lower defect along the same
guarded run. It proves exact packet-reduction and lower port-cost balances,
and that lower control-letter cost (port-facing cost) is bounded by raw length.
The geometric layer proves that atom 2 must incur at least `n - 2` lower
rotations before it can appear upstairs or share a packet with another atom.
This applies to all successful histories and all terminal phases. A separate
sync-port credit bounds elevator count by rotations plus nonfusing lower
defects plus initial credit. Their joint lower bound uses a maximum. Two raw
witnesses attain the exact minimum lower-control cost at fixed literal upper
endpoints: `2*n-2` for a full packet at site 0, also the exact minimum raw
length for `n >= 3`, and `2*n-1` for the specified singleton placement.
An independent upper receiver-vacancy budget forces at least `n-1` upper
rotations at every all-upper singleton endpoint. The singleton witness thus
also attains the exact minimum raw length `3*n-2` for `n > 1`.
Partition-diameter optimality remains open. The independent
`SingletonWordSymmetry` module proves that these shortest singleton witnesses
are non-unique: the two layer rotations commute, and every round may choose
either order. It proves an injective equal-length Boolean family and an
explicit pair of distinct optimal words. `SingletonElevatorSkeleton` derives
the inter-elevator skeleton from equality in the actual port-credit budgets,
retaining lower defects as possibilities. `SingletonOptimalClassification`
uses the literal endpoint and lower holes to exclude every lower defect for
`n >= 3`, proving that only independent rotation swaps remain.
`SingletonOptimalCounting` supplies a duplicate-free exhaustive enumeration
of all optimal raw words: exactly `2^(n-1)` for `n >= 3` and exactly four for
`n = 2`, including its two lower-defect exceptions. All statements use the
unchanged guarded executor and the specified literal singleton endpoint.
`SequentialPreparationDebts` now bounds the sum of potential drops on a
state-chained decomposition of one actual raw word. `ForcedPreparationDebts`
extracts two such intervals from every realization with atom 0 lower and
atom 1 upper at the endpoint: the first lower rotation pays one unit and
creates atom 1's fresh `n-2` debt. Its sharp `n-1` rotation lower bound is
linear and does not determine partition diameter.
`SingleVacancyDebt` then proves a quadratic lower-rotation obstruction for
a literal endpoint: only atom 1 is upper, atom 0 is at lower site 1, and
lower site 0 is empty. All atoms must remain in distinct packets. The
actual vacancy is re-exposed to an `n-1` return debt by each productive
lower defect. `SingleVacancyWitness` proves that
`p0^(n-1) v (d0 p0^(n-1))^(n-2)` reaches the specified endpoint and attains
the universal rotation minimum `(n-1)^2`. No raw-word minimum or unlayered
partition-diameter bound is inferred from this rotation optimum alone.
`SingleVacancyOptimality` separately proves the exact raw minimum and
uniqueness. `AntipodalFusionGate` treats an unordered partition target instead:
every successful antipodal realization has at most one effective lower
fusion and at most one terminal lower packet. The same-history ledger then
forces at least `2*m-2` elevators, and the existing geometry and receiver
budgets give lower rotations `2*m-2`, upper rotations `2*m-3`, and lower
control cost `4*m-3` for `m >= 2`. `PacketRankLedger` counts effective
fusions on both layers along that same guarded execution and proves exact
total rank conservation. `AntipodalLinearBounds` uses the terminal rank `m`
and the lower fusion gate to force at least `m-1` upper defects, completing
the raw lower bound `7*m-7`. `AntipodalLinearWitness` proves both passes of
the explicit word against the actual guarded run, including every receiver
guard and the exact endpoint: pair `i` is at upper site `2*((i-1) mod m)`.
Its raw length is `9*m-2` and lower control cost is `4*m-1`.
The combined bounds minimize over all words, layers and coordinates with
the antipodal partition; they do not determine its exact minimum or the
growth order of the general unordered partition diameter.
-/
