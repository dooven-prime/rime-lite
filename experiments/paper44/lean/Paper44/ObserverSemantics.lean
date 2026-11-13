import PaperXL.PrefixObserver

/-!
# Paper 44: prefix-observer semantics

This module is the first Lean companion layer for the prefix-memory paper.
It reuses the abstract `PaperXL.LabelledMachine` and `PrefixLabel` API from
the Paper XL companion.  It proves only the semantic statements needed before
the circular counting model is introduced:

* observer equivalence is future-trace equivalence plus the current label;
* equal current labels and equal future traces give equal labels after every
  common continuation;
* the concrete prefix label update is compositional over event lists.

The circular chain/fibre counts, exact quotient formulas, entropy estimates,
critical-window limits, and finite replay controls are intentionally not
claimed here.  They require a separate model-specific layer.
-/

namespace Paper44

open PaperXL

universe u v w z o r

variable {State : Type u} {Letter : Type v} {Event : Type w} {Label : Type z}

abbrev FutureTraceEq (M : LabelledMachine State Letter Event Label)
    (x y : State) : Prop := LabelledMachine.FutureEq M x y

abbrev PrefixObserverEq (M : LabelledMachine State Letter Event Label)
    (x y : State) : Prop := LabelledMachine.ObserverEq M x y

theorem prefixObserverEq_iff
    (M : LabelledMachine State Letter Event Label) (x y : State) :
    PrefixObserverEq M x y ↔
      (∀ w, M.trace x w = M.trace y w) ∧ M.label x = M.label y := by
  rfl

theorem label_run_eq_of_same_trace_and_label
    (M : LabelledMachine State Letter Event Label)
    {x y : State}
    (htrace : ∀ w, M.trace x w = M.trace y w)
    (hlabel : M.label x = M.label y)
    (w : List Letter) :
    M.label (M.run x w) = M.label (M.run y w) := by
  exact LabelledMachine.label_run_eq_of_observerEq M ⟨htrace, hlabel⟩ w

theorem prefixLabel_update_registration_positive
    {Origin : Type o} {Record : Type r}
    (depth : Nat) (origin : Origin) (hdepth : 0 < depth) :
    PrefixLabel.update (Origin := Origin) (Record := Record) depth
        (.unregistered : PrefixLabel Origin Record)
        (.registration origin) =
      (.registered origin ([] : List Record) .short : PrefixLabel Origin Record) := by
  simp [PrefixLabel.update, hdepth]

theorem prefixLabel_update_saturated_is_identity
    {Origin : Type o} {Record : Type r}
    (depth : Nat) (origin : Origin) (records : List Record)
    (event : PrefixEvent Origin Record) :
    PrefixLabel.update depth
        (.registered origin records .saturated) event =
      .registered origin records .saturated := by
  exact PrefixLabel.saturated_update_eq depth origin records event

theorem prefixLabel_scan_append
    {Origin : Type o} {Record : Type r}
    (depth : Nat) (initial : PrefixLabel Origin Record)
    (left right : List (PrefixEvent Origin Record)) :
    PrefixLabel.scanFrom depth initial (left ++ right) =
      PrefixLabel.scanFrom depth
        (PrefixLabel.scanFrom depth initial left) right := by
  exact PrefixLabel.scanFrom_append depth initial left right

theorem prefixLabel_scan_wellFormed
    {Origin : Type o} {Record : Type r}
    (depth : Nat) (events : List (PrefixEvent Origin Record)) :
    PrefixLabel.WellFormed depth (PrefixLabel.scan depth events) := by
  exact PrefixLabel.scan_wellFormed depth events

end Paper44
