import FusionLogReplay

namespace FusionLogInterpretation

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay

variable {n : ℕ} [NeZero n]
variable {ι α : Type*} [DecidableEq ι] [DecidableEq α]

/-- Interpret an index set as the union of its initial packet labels. -/
def expandBlock (labels : ι → Finset α) (I : Finset ι) : Finset α :=
  I.biUnion labels

@[simp] theorem expandBlock_empty (labels : ι → Finset α) :
    expandBlock labels ∅ = ∅ := by simp [expandBlock]

@[simp] theorem expandBlock_union (labels : ι → Finset α) (I J : Finset ι) :
    expandBlock labels (I ∪ J) = expandBlock labels I ∪ expandBlock labels J := by
  ext a
  simp [expandBlock]
  aesop

def expandPlacement (labels : ι → Finset α) (P : Placement n (Finset ι)) :
    Placement n (Finset α) := fun q => (P q).map (expandBlock labels)

def expandRecord (labels : ι → Finset α) (event : FusionRecord ι) : FusionRecord α :=
  ⟨expandBlock labels event.left, expandBlock labels event.right,
    expandBlock labels event.result⟩

@[simp] theorem expandPlacement_none (labels : ι → Finset α)
    (P : Placement n (Finset ι)) (q : ZMod n) :
    expandPlacement labels P q = none ↔ P q = none := by
  simp [expandPlacement]

theorem expandPlacement_rotate (labels : ι → Finset α)
    (P : Placement n (Finset ι)) (phase : ZMod n) :
    expandPlacement labels (rotate phase P) = rotate phase (expandPlacement labels P) := rfl

theorem expandPlacement_fusion (labels : ι → Finset α) (P : Placement n (Finset ι)) :
    expandPlacement labels (fusionPlacement P) = fusionPlacement (expandPlacement labels P) := by
  funext q
  by_cases h0 : q = 0
  · subst q
    cases hp0 : P 0 <;> cases hp1 : P 1 <;>
      simp [expandPlacement, fusionPlacement, hp0, hp1]
  · simp only [expandPlacement, fusionPlacement, if_neg h0]
    split_ifs <;> rfl

/-- The selected-registration policy may differ on the two sides. Its
fields do not participate in the raw placement action or complete event. -/
theorem step_placement_interprets (labels : ι → Finset α)
    (G : Finset ι) (F : Finset α) (source : Execution n ι) (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) (a : Letter) :
    (step F actual a).placed = expandPlacement labels (step G source a).placed := by
  cases a with
  | p => rw [show (step F actual .p).placed = rotate 1 actual.placed from rfl,
      show (step G source .p).placed = rotate 1 source.placed from rfl,
      same, expandPlacement_rotate]
  | d =>
      change (stepDefect F actual).placed = expandPlacement labels (stepDefect G source).placed
      rw [stepDefect_placed_eq, stepDefect_placed_eq, same, expandPlacement_fusion]

theorem event_interprets (labels : ι → Finset α)
    (source : Execution n ι) (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) (a : Letter) :
    effectiveEvent actual a = (effectiveEvent source a).map (expandRecord labels) := by
  cases a with
  | p => rfl
  | d =>
      cases h0 : source.placed 0 <;> cases h1 : source.placed 1 <;>
        simp [effectiveEvent, same, expandPlacement, h0, h1, expandRecord]

theorem run_placement_interprets (labels : ι → Finset α)
    (G : Finset ι) (F : Finset α) (source : Execution n ι) (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) (word : List Letter) :
    (run F actual word).placed = expandPlacement labels (run G source word).placed := by
  induction word generalizing source actual with
  | nil => exact same
  | cons a rest ih =>
      exact ih (step G source a) (step F actual a)
        (step_placement_interprets labels G F source actual same a)

theorem eventTrace_interprets (labels : ι → Finset α)
    (G : Finset ι) (F : Finset α) (source : Execution n ι) (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) (word : List Letter) :
    eventTrace F actual word = (eventTrace G source word).map (expandRecord labels) := by
  induction word generalizing source actual with
  | nil => rfl
  | cons a rest ih =>
      have head := event_interprets labels source actual same a
      have tail := ih (step G source a) (step F actual a)
        (step_placement_interprets labels G F source actual same a)
      simp only [eventTrace, List.map_append]
      rw [tail, head]
      cases effectiveEvent source a <;> rfl

theorem fusionFree_iff (labels : ι → Finset α)
    (G : Finset ι) (F : Finset α) (source : Execution n ι) (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) (word : List Letter) :
    FusionFree F actual word ↔ FusionFree G source word := by
  rw [← eventTrace_eq_nil_iff, ← eventTrace_eq_nil_iff,
    eventTrace_interprets labels G F source actual same word, List.map_eq_nil_iff]

theorem occupiedSites_expand (labels : ι → Finset α) (P : Placement n (Finset ι)) :
    occupiedSites (expandPlacement labels P) = occupiedSites P := by
  ext q
  simp [occupiedSites]

theorem run_support_interprets (labels : ι → Finset α)
    (G : Finset ι) (F : Finset α) (source : Execution n ι) (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) (word : List Letter) :
    occupiedSites (run F actual word).placed = occupiedSites (run G source word).placed := by
  rw [run_placement_interprets labels G F source actual same word, occupiedSites_expand]

theorem complete_log_interprets (labels : ι → Finset α)
    (G : Finset ι) (F : Finset α) (source : LoggedExecution n ι) (actual : LoggedExecution n α)
    (same : actual.state.placed = expandPlacement labels source.state.placed)
    (logs : actual.fullLog = source.fullLog.map (expandRecord labels)) (word : List Letter) :
    (runLogged F actual word).fullLog =
      (runLogged G source word).fullLog.map (expandRecord labels) := by
  rw [runLogged_fullLog, runLogged_fullLog, logs,
    eventTrace_interprets labels G F source.state actual.state same word, List.map_append]

end FusionLogInterpretation
