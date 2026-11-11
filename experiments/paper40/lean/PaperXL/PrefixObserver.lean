import PaperXL.Core

/-!
# Prefix observers

This module contains the semantic layer used by the prefix-memory follow-up.
It is deliberately independent of the circular placement implementation:
the concrete model only has to provide a deterministic step, an event output,
and a deterministic label update.
-/

namespace PaperXL

universe u v w z

inductive PrefixPhase
  | short
  | saturated
  deriving DecidableEq, Repr

inductive PrefixEvent (Origin : Type u) (Record : Type v)
  | null
  | registration (origin : Origin)
  | absorption (record : Record)
  deriving DecidableEq, Repr

inductive PrefixLabel (Origin : Type u) (Record : Type v)
  | unregistered
  | registered (origin : Origin) (records : List Record) (phase : PrefixPhase)
  deriving DecidableEq, Repr

namespace PrefixLabel

variable {Origin : Type u} {Record : Type v}

def update (depth : Nat) :
    PrefixLabel Origin Record → PrefixEvent Origin Record →
      PrefixLabel Origin Record
  | .unregistered, .null => .unregistered
  | .unregistered, .registration origin =>
      .registered origin [] (if 0 < depth then .short else .saturated)
  | .unregistered, .absorption _ => .unregistered
  | .registered origin records phase, event =>
      match event with
      | .null => .registered origin records phase
      | .registration _ => .registered origin records phase
      | .absorption record =>
          match phase with
          | .saturated => .registered origin records .saturated
          | .short =>
              let nextRecords :=
                if records.length < depth then records ++ [record] else records
              let nextPhase := if nextRecords.length < depth then .short else .saturated
              .registered origin nextRecords nextPhase

def WellFormed (depth : Nat) : PrefixLabel Origin Record → Prop
  | .unregistered => True
  | .registered _ records .short => records.length < depth
  | .registered _ records .saturated => records.length = depth

def scanFrom (depth : Nat) (initial : PrefixLabel Origin Record)
    (events : List (PrefixEvent Origin Record)) : PrefixLabel Origin Record :=
  events.foldl (update depth) initial

def scan (depth : Nat) (events : List (PrefixEvent Origin Record)) :
    PrefixLabel Origin Record :=
  scanFrom depth .unregistered events

theorem update_wellFormed (depth : Nat) (label : PrefixLabel Origin Record)
    (event : PrefixEvent Origin Record) (h : WellFormed depth label) :
    WellFormed depth (update depth label event) := by
  cases label with
  | unregistered =>
      cases event with
      | null => simp [update, WellFormed]
      | registration origin =>
          by_cases hdepth : 0 < depth
          · simp [update, WellFormed, hdepth]
          · have hzero : depth = 0 := by omega
            simp [update, WellFormed, hzero]
      | absorption record => simp [update, WellFormed]
  | registered origin records phase =>
      cases event with
      | null => simpa [update, WellFormed] using h
      | registration _ => simpa [update, WellFormed] using h
      | absorption record =>
          cases phase with
          | saturated => simpa [update, WellFormed] using h
          | short =>
              change WellFormed depth
                (let nextRecords :=
                  if records.length < depth then records ++ [record] else records
                 let nextPhase :=
                  if nextRecords.length < depth then .short else .saturated
                 .registered origin nextRecords nextPhase)
              have hlen : records.length < depth := by
                simpa [WellFormed] using h
              by_cases hnext : records.length + 1 < depth
              · simp [WellFormed, hlen, hnext]
              · have hboundary : depth = records.length + 1 := by omega
                simp [WellFormed, hboundary]

theorem scanFrom_wellFormed (depth : Nat) (initial : PrefixLabel Origin Record)
    (events : List (PrefixEvent Origin Record))
    (h : WellFormed depth initial) :
    WellFormed depth (scanFrom depth initial events) := by
  induction events generalizing initial with
  | nil => simpa [scanFrom] using h
  | cons event events ih =>
      simp only [scanFrom, List.foldl_cons]
      exact ih (update depth initial event) (update_wellFormed depth initial event h)

theorem scan_wellFormed (depth : Nat)
    (events : List (PrefixEvent Origin Record)) :
    WellFormed depth (scan depth events) := by
  exact scanFrom_wellFormed depth .unregistered events trivial

theorem scanFrom_append (depth : Nat) (initial : PrefixLabel Origin Record)
    (left right : List (PrefixEvent Origin Record)) :
    scanFrom depth initial (left ++ right) =
      scanFrom depth (scanFrom depth initial left) right := by
  simp [scanFrom, List.foldl_append]

theorem scan_append (depth : Nat)
    (left right : List (PrefixEvent Origin Record)) :
    scan depth (left ++ right) =
      scanFrom depth (scan depth left) right := by
  exact scanFrom_append depth .unregistered left right

theorem saturated_update_eq (depth : Nat) (origin : Origin)
    (records : List Record) (event : PrefixEvent Origin Record) :
    update depth (.registered origin records .saturated) event =
      .registered origin records .saturated := by
  cases event <;> rfl

theorem saturated_scanFrom_eq (depth : Nat) (origin : Origin)
    (records : List Record) (events : List (PrefixEvent Origin Record)) :
    scanFrom depth (.registered origin records .saturated) events =
      .registered origin records .saturated := by
  induction events with
  | nil => rfl
  | cons event events ih =>
      change scanFrom depth
        (update depth (.registered origin records .saturated) event) events = _
      rw [saturated_update_eq, ih]

end PrefixLabel

/- A deterministic machine with a per-letter event and a current label. -/
structure LabelledMachine (State : Type u) (Letter : Type v)
    (Event : Type w) (Label : Type z) where
  step : State → Letter → State
  emit : State → Letter → Event
  label : State → Label
  update : Label → Event → Label
  label_step : ∀ s a,
    label (step s a) = update (label s) (emit s a)

namespace LabelledMachine

variable {State : Type u} {Letter : Type v} {Event : Type w} {Label : Type z}

def run (M : LabelledMachine State Letter Event Label) :
    State → List Letter → State :=
  List.foldl M.step

def trace (M : LabelledMachine State Letter Event Label) :
    State → List Letter → List Event
  | _, [] => []
  | s, a :: w => M.emit s a :: trace M (M.step s a) w

@[simp] theorem trace_nil (M : LabelledMachine State Letter Event Label) (s : State) :
    trace M s [] = [] := rfl

@[simp] theorem trace_cons (M : LabelledMachine State Letter Event Label)
    (s : State) (a : Letter) (w : List Letter) :
    trace M s (a :: w) = M.emit s a :: trace M (M.step s a) w := rfl

def FutureEq (M : LabelledMachine State Letter Event Label) (x y : State) : Prop :=
  ∀ w, trace M x w = trace M y w

def ObserverEq (M : LabelledMachine State Letter Event Label) (x y : State) : Prop :=
  FutureEq M x y ∧ M.label x = M.label y

def OutputStable (M : LabelledMachine State Letter Event Label)
    (R : State → State → Prop) : Prop :=
  ∀ x y, R x y → ∀ a,
    M.emit x a = M.emit y a ∧ R (M.step x a) (M.step y a)

theorem futureEq_refl (M : LabelledMachine State Letter Event Label) (x : State) :
    FutureEq M x x := by
  intro w
  rfl

theorem futureEq_symm (M : LabelledMachine State Letter Event Label)
    {x y : State} (h : FutureEq M x y) : FutureEq M y x := by
  intro w
  exact (h w).symm

theorem futureEq_trans (M : LabelledMachine State Letter Event Label)
    {x y z : State} (hxy : FutureEq M x y) (hyz : FutureEq M y z) :
    FutureEq M x z := by
  intro w
  exact (hxy w).trans (hyz w)

theorem observerEq_refl (M : LabelledMachine State Letter Event Label) (x : State) :
    ObserverEq M x x := by
  exact ⟨futureEq_refl M x, rfl⟩

theorem observerEq_symm (M : LabelledMachine State Letter Event Label)
    {x y : State} (h : ObserverEq M x y) : ObserverEq M y x := by
  exact ⟨futureEq_symm M h.1, h.2.symm⟩

theorem observerEq_trans (M : LabelledMachine State Letter Event Label)
    {x y z : State} (hxy : ObserverEq M x y) (hyz : ObserverEq M y z) :
    ObserverEq M x z := by
  exact ⟨futureEq_trans M hxy.1 hyz.1, hxy.2.trans hyz.2⟩

theorem futureEq_step (M : LabelledMachine State Letter Event Label)
    {x y : State} (h : FutureEq M x y) (a : Letter) :
    M.emit x a = M.emit y a ∧
      FutureEq M (M.step x a) (M.step y a) := by
  have hone := h [a]
  have hemit : M.emit x a = M.emit y a := by
    simpa [trace] using hone
  constructor
  · exact hemit
  · intro w
    have hfull := h (a :: w)
    have htail := congrArg List.tail hfull
    simpa using htail

theorem observerEq_step (M : LabelledMachine State Letter Event Label)
    {x y : State} (h : ObserverEq M x y) (a : Letter) :
    M.emit x a = M.emit y a ∧
      ObserverEq M (M.step x a) (M.step y a) := by
  rcases futureEq_step M h.1 a with ⟨hemit, hfuture⟩
  refine ⟨hemit, hfuture, ?_⟩
  calc
    M.label (M.step x a) = M.update (M.label x) (M.emit x a) :=
      M.label_step x a
    _ = M.update (M.label y) (M.emit y a) := by rw [h.2, hemit]
    _ = M.label (M.step y a) := (M.label_step y a).symm

theorem observerEq_outputStable (M : LabelledMachine State Letter Event Label) :
    OutputStable M (ObserverEq M) := by
  intro x y h a
  exact observerEq_step M h a

theorem outputStable_le_observerEq
    (M : LabelledMachine State Letter Event Label)
    (R : State → State → Prop) (hstable : OutputStable M R)
    (hlabel : ∀ x y, R x y → M.label x = M.label y)
    {x y : State} (hxy : R x y) : ObserverEq M x y := by
  refine ⟨?_, hlabel x y hxy⟩
  intro word
  induction word generalizing x y with
  | nil => rfl
  | cons a word ih =>
      rcases hstable x y hxy a with ⟨hemit, hnext⟩
      simp [trace, hemit, ih hnext]

theorem observerEq_isLargestOutputStable
    (M : LabelledMachine State Letter Event Label)
    (R : State → State → Prop)
    (hstable : OutputStable M R)
    (hlabel : ∀ x y, R x y → M.label x = M.label y) :
    (∀ x y, R x y → ObserverEq M x y) ∧ OutputStable M (ObserverEq M) := by
  constructor
  · intro x y hxy
    exact outputStable_le_observerEq M R hstable hlabel hxy
  · exact observerEq_outputStable M

theorem label_run (M : LabelledMachine State Letter Event Label)
    (x : State) (w : List Letter) :
    M.label (run M x w) =
      List.foldl M.update (M.label x) (trace M x w) := by
  induction w generalizing x with
  | nil => rfl
  | cons a w ih =>
      change M.label (run M (M.step x a) w) =
        List.foldl M.update (M.update (M.label x) (M.emit x a))
          (trace M (M.step x a) w)
      rw [ih (M.step x a), M.label_step x a]

theorem label_run_eq_of_observerEq
    (M : LabelledMachine State Letter Event Label)
    {x y : State} (h : ObserverEq M x y) (w : List Letter) :
    M.label (run M x w) = M.label (run M y w) := by
  induction w generalizing x y with
  | nil => exact h.2
  | cons a w ih =>
      rcases observerEq_step M h a with ⟨hemit, hnext⟩
      have hlabel : M.label (M.step x a) = M.label (M.step y a) := by
        calc
          M.label (M.step x a) = M.update (M.label x) (M.emit x a) :=
            M.label_step x a
          _ = M.update (M.label y) (M.emit y a) := by rw [h.2, hemit]
          _ = M.label (M.step y a) := (M.label_step y a).symm
      simpa [run] using ih hnext

theorem observerEq_iff_futureEq_and_label
    (M : LabelledMachine State Letter Event Label) (x y : State) :
    ObserverEq M x y ↔ FutureEq M x y ∧ M.label x = M.label y := by
  rfl

theorem observerEq_implies_same_future_trace
    (M : LabelledMachine State Letter Event Label) {x y : State}
    (h : ObserverEq M x y) (word : List Letter) :
    trace M x word = trace M y word := h.1 word

end LabelledMachine

abbrev PrefixObserver (State : Type u) (Letter : Type v)
    (Origin : Type w) (Record : Type z) :=
  LabelledMachine State Letter (PrefixEvent Origin Record)
    (PrefixLabel Origin Record)

end PaperXL
