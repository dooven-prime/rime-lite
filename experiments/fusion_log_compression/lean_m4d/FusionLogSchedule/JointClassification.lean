import FusionLogSchedule.CanonicalRealization

namespace FusionLogSchedule

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

/-- A finite abstract certificate, not an actual execution witness.
Its initial source fibres are exactly the initial physical packets.
Each step contracts whole ordered neighbouring packets and records their union. -/
structure AdmissibleSchedule (initial : Placement n (Finset α))
    (nonempty : (occupiedSites initial).Nonempty) (events : List (FusionRecord α)) where
  indexEvents : List (FusionRecord (ZMod n))
  last : IndexPackets n
  abstractTrace : AbstractTrace (packetSet (canonicalPlacement initial nonempty)) indexEvents last
  records : indexEvents.map (expandRecord (siteLabels initial)) = events

/-- The endpoint reads the terminal partition of this very schedule. The
orientation witness is a static degree-one source lift, never a word. -/
def CompatibleEndpoint {initial : Placement n (Finset α)}
    {nonempty : (occupiedSites initial).Nonempty} {events : List (FusionRecord α)}
    (schedule : AdmissibleSchedule initial nonempty events)
    (target : Placement n (Finset α)) : Prop :=
  ∃ indexTarget : Placement n (Finset (ZMod n)),
    IndexCompatible schedule.last indexTarget ∧
      expandPlacement (siteLabels initial) indexTarget = target

def AdmissibleAndCompatible (initial : Placement n (Finset α))
    (nonempty : (occupiedSites initial).Nonempty) (events : List (FusionRecord α))
    (target : Placement n (Finset α)) : Prop :=
  ∃ schedule : AdmissibleSchedule initial nonempty events, CompatibleEndpoint schedule target

def JointlyAttainable (F : Finset α) (source : Execution n α)
    (events : List (FusionRecord α)) (target : Placement n (Finset α)) : Prop :=
  ∃ word : List Letter, eventTrace F source word = events ∧ (run F source word).placed = target

theorem actual_joint_certificate (F : Finset α) (source : Execution n α)
    (word : List Letter) (hn : 3 ≤ n) (nonempty : (occupiedSites source.placed).Nonempty) :
    AdmissibleAndCompatible source.placed nonempty (eventTrace F source word)
      (run F source word).placed := by
  let indexSource := initialIndexExecution source.placed nonempty
  have ordered : SourceOrdered indexSource.placed := canonicalPlacement_ordered _ nonempty
  have same : source.placed = expandPlacement (siteLabels source.placed) indexSource.placed :=
    initial_placement_interprets _ nonempty
  let schedule : AdmissibleSchedule source.placed nonempty (eventTrace F source word) :=
    { indexEvents := eventTrace ∅ indexSource word
      last := packetSet (run ∅ indexSource word).placed
      abstractTrace := actual_trace_admissible ∅ indexSource word hn ordered
      records := (eventTrace_interprets (siteLabels source.placed) ∅ F
        indexSource source same word).symm }
  refine ⟨schedule, (run ∅ indexSource word).placed, ?_, ?_⟩
  · exact ⟨run_ordered ∅ indexSource word (by omega) ordered, rfl⟩
  · exact (run_placement_interprets (siteLabels source.placed) ∅ F
      indexSource source same word).symm

theorem realize_admissible_schedule (F : Finset α) (source : Execution n α)
    (events : List (FusionRecord α)) (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (nonempty : (occupiedSites source.placed).Nonempty)
    (schedule : AdmissibleSchedule source.placed nonempty events)
    (compatible : CompatibleEndpoint schedule target) :
    ∃ word : List Letter,
      eventTrace F source word = events ∧ (run F source word).placed = target ∧
      word.length ≤ normalFormBudget n (occupiedSites source.placed).card (occupiedSites target).card := by
  let indexSource := initialIndexExecution source.placed nonempty
  have ordered : SourceOrdered indexSource.placed := canonicalPlacement_ordered _ nonempty
  have same : source.placed = expandPlacement (siteLabels source.placed) indexSource.placed :=
    initial_placement_interprets _ nonempty
  obtain ⟨indexTarget, indexCompatible, decoded⟩ := compatible
  obtain ⟨reference, indexLogs, indexEnd⟩ := realize_index_joint ∅ indexSource
    schedule.indexEvents schedule.last indexTarget hn ordered schedule.abstractTrace indexCompatible
  have logs : eventTrace F source reference = events := by
    rw [eventTrace_interprets (siteLabels source.placed) ∅ F indexSource source same reference,
      indexLogs, schedule.records]
  have endpoint : (run F source reference).placed = target := by
    rw [run_placement_interprets (siteLabels source.placed) ∅ F indexSource source same reference,
      indexEnd, decoded]
  obtain ⟨short, shortLogs, shortEnd, cost⟩ :=
    arbitrary_initial_log_endpoint_representative F ⟨source, []⟩ reference hn nonempty
  refine ⟨short, ?_, ?_, ?_⟩
  · have traceEq : eventTrace F source short = eventTrace F source reference := by
      simpa only [runLogged_fullLog, List.nil_append] using shortLogs
    exact traceEq.trans logs
  · have endEq : (run F source short).placed = (run F source reference).placed := by
      simpa only [runLogged_state] using shortEnd
    exact endEq.trans endpoint
  · simpa only [endpoint] using cost

/-- Theorem 4.1's joint object: the same abstract schedule must supply
both the complete records and the endpoint's final cyclic partition. -/
theorem joint_realization_iff (F : Finset α) (source : Execution n α)
    (events : List (FusionRecord α)) (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (nonempty : (occupiedSites source.placed).Nonempty) :
    JointlyAttainable F source events target ↔
      AdmissibleAndCompatible source.placed nonempty events target := by
  constructor
  · rintro ⟨word, logs, endpoint⟩
    have certificate := actual_joint_certificate F source word hn nonempty
    rwa [logs, endpoint] at certificate
  · rintro ⟨schedule, compatible⟩
    obtain ⟨word, logs, endpoint, _⟩ :=
      realize_admissible_schedule F source events target hn nonempty schedule compatible
    exact ⟨word, logs, endpoint⟩

theorem admissible_compatible_iff_bounded_joint (F : Finset α) (source : Execution n α)
    (events : List (FusionRecord α)) (target : Placement n (Finset α)) (hn : 3 ≤ n)
    (nonempty : (occupiedSites source.placed).Nonempty) :
    AdmissibleAndCompatible source.placed nonempty events target ↔
      ∃ word : List Letter,
        eventTrace F source word = events ∧ (run F source word).placed = target ∧
        word.length ≤ normalFormBudget n (occupiedSites source.placed).card
          (occupiedSites target).card := by
  constructor
  · rintro ⟨schedule, compatible⟩
    exact realize_admissible_schedule F source events target hn nonempty schedule compatible
  · rintro ⟨word, logs, endpoint, _⟩
    exact (joint_realization_iff F source events target hn nonempty).mp ⟨word, logs, endpoint⟩

end FusionLogSchedule
