import FusionLogSchedule.PacketAddresses
import FusionLogSchedule.OrderInterface

namespace FusionLogSchedule

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

/-- The final source partition is computed from the literal complete log.
No actual execution or choice of an admissibility witness is used. -/
def finalPackets (initial : Placement n (Finset α))
    (nonempty : (occupiedSites initial).Nonempty) (events : List (FusionRecord α)) :
    IndexPackets n :=
  (events.map (restoreRecord initial nonempty)).foldl advance
    (packetSet (canonicalPlacement initial nonempty))

def IsAdmissibleSchedule (initial : Placement n (Finset α))
    (nonempty : (occupiedSites initial).Nonempty) (events : List (FusionRecord α)) : Prop :=
  Nonempty (AdmissibleSchedule initial nonempty events)

/-- Compatibility is relative to the same literal log, not an independently
chosen terminal partition. It is a static oriented-placement condition. -/
def CompatibleForLog (initial : Placement n (Finset α))
    (nonempty : (occupiedSites initial).Nonempty) (events : List (FusionRecord α))
    (target : Placement n (Finset α)) : Prop :=
  ∃ indexTarget : Placement n (Finset (ZMod n)),
    IndexCompatible (finalPackets initial nonempty events) indexTarget ∧
      expandPlacement (siteLabels initial) indexTarget = target

theorem AdmissibleSchedule.last_eq_finalPackets {P : Placement n (Finset α)}
    {nonempty : (occupiedSites P).Nonempty} {events : List (FusionRecord α)}
    (schedule : AdmissibleSchedule P nonempty events) (valid : PacketPartition P) :
    schedule.last = finalPackets P nonempty events := by
  rw [schedule.abstractTrace.last_eq_fold, schedule.indexEvents_recover valid]
  rfl

theorem compatibleEndpoint_iff_forLog {P : Placement n (Finset α)}
    {nonempty : (occupiedSites P).Nonempty} {events : List (FusionRecord α)}
    (schedule : AdmissibleSchedule P nonempty events) (valid : PacketPartition P)
    (target : Placement n (Finset α)) :
    CompatibleEndpoint schedule target ↔ CompatibleForLog P nonempty events target := by
  unfold CompatibleEndpoint CompatibleForLog
  rw [schedule.last_eq_finalPackets valid]

theorem admissibleAndCompatible_iff {P : Placement n (Finset α)}
    {nonempty : (occupiedSites P).Nonempty} {events : List (FusionRecord α)}
    (valid : PacketPartition P) (target : Placement n (Finset α)) :
    AdmissibleAndCompatible P nonempty events target ↔
      IsAdmissibleSchedule P nonempty events ∧ CompatibleForLog P nonempty events target := by
  constructor
  · rintro ⟨schedule, compatible⟩
    exact ⟨⟨schedule⟩, (compatibleEndpoint_iff_forLog schedule valid target).mp compatible⟩
  · rintro ⟨⟨schedule⟩, compatible⟩
    exact ⟨schedule, (compatibleEndpoint_iff_forLog schedule valid target).mpr compatible⟩

/-- Theorem 4.1: admissibility and endpoint compatibility are necessary and
sufficient for the joint complete-log/literal-placement object. -/
theorem abstract_schedule_endpoint_iff (F : Finset α) (source : Execution n α)
    (events : List (FusionRecord α)) (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (nonempty : (occupiedSites source.placed).Nonempty) (valid : PacketPartition source.placed) :
    JointlyAttainable F source events target ↔
      IsAdmissibleSchedule source.placed nonempty events ∧
        CompatibleForLog source.placed nonempty events target :=
  (joint_realization_iff F source events target hn nonempty).trans
    (admissibleAndCompatible_iff valid target)

/-- The converse uses the already frozen arbitrary-initial sharp-budget
theorem only after the abstract joint object has been actually realized. -/
theorem abstract_schedule_bounded_realization (F : Finset α) (source : Execution n α)
    (events : List (FusionRecord α)) (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (nonempty : (occupiedSites source.placed).Nonempty) (valid : PacketPartition source.placed)
    (admissible : IsAdmissibleSchedule source.placed nonempty events)
    (compatible : CompatibleForLog source.placed nonempty events target) :
    ∃ word : List Letter,
      eventTrace F source word = events ∧ (run F source word).placed = target ∧
      word.length ≤ normalFormBudget n (occupiedSites source.placed).card
        (occupiedSites target).card := by
  exact (admissible_compatible_iff_bounded_joint F source events target hn nonempty).mp
    ((admissibleAndCompatible_iff valid target).mpr ⟨admissible, compatible⟩)

theorem abstract_schedule_endpoint_iff_bounded (F : Finset α) (source : Execution n α)
    (events : List (FusionRecord α)) (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (nonempty : (occupiedSites source.placed).Nonempty) (valid : PacketPartition source.placed) :
    (IsAdmissibleSchedule source.placed nonempty events ∧
      CompatibleForLog source.placed nonempty events target) ↔
      ∃ word : List Letter,
        eventTrace F source word = events ∧ (run F source word).placed = target ∧
        word.length ≤ normalFormBudget n (occupiedSites source.placed).card
          (occupiedSites target).card :=
  (admissibleAndCompatible_iff valid target).symm.trans
    (admissible_compatible_iff_bounded_joint F source events target hn nonempty)

theorem packetPartition_of_named {r : ℕ} [NeZero r]
    (named : LegalNamedPlacement n r α) : PacketPartition named.placed := by
  have recover : ∀ q A, named.placed q = some A →
      ∃ i, named.position i = q ∧ named.block i = A := by
    intro q A atSite
    obtain ⟨i, hi⟩ := named.only_named q (by simp [atSite])
    refine ⟨i, hi, ?_⟩
    have eq := named.placed_at i
    rw [hi, atSite] at eq
    exact Option.some.inj eq.symm
  constructor
  · intro q A atSite
    obtain ⟨i, _, rfl⟩ := recover q A atSite
    exact named.block_nonempty i
  · intro q r A B different atQ atR
    obtain ⟨i, hi, rfl⟩ := recover q A atQ
    obtain ⟨j, hj, rfl⟩ := recover r B atR
    exact named.block_disjoint i j (by intro eq; apply different; rw [← hi, ← hj, eq])

end FusionLogSchedule
