import Paper44

namespace Paper44.Checks

open PaperXL RegisteredAbsorptionChains

inductive DemoEvent
  | null
  | tick
  deriving DecidableEq, Repr

inductive DemoLabel
  | cold
  | hot
  deriving DecidableEq, Repr

private def demo : LabelledMachine Bool Unit DemoEvent DemoLabel where
  step := fun state _ => state
  emit := fun state _ => if state then .tick else .null
  label := fun state => if state then .hot else .cold
  update := fun label event => match label, event with
    | .cold, .tick => .hot
    | label, _ => label
  label_step := by
    intro state _u
    cases state <;> rfl

example (x : Bool) :
    PrefixObserverEq demo x x := by
  exact LabelledMachine.observerEq_refl demo x

example (x y : Bool) (h : x = y) :
    PrefixObserverEq demo x y := by
  subst y
  exact LabelledMachine.observerEq_refl demo x

example (depth : Nat) (origin : Unit) (hdepth : 0 < depth) :
    PrefixLabel.update (Origin := Unit) (Record := Nat) depth
        (.unregistered : PrefixLabel Unit Nat) (.registration origin) =
      (.registered origin ([] : List Nat) .short : PrefixLabel Unit Nat) := by
  exact prefixLabel_update_registration_positive depth origin hdepth

example (depth : Nat) (events : List (PrefixEvent Unit Nat)) :
    PrefixLabel.WellFormed depth (PrefixLabel.scan depth events) := by
  exact prefixLabel_scan_wellFormed depth events

private def seed4 : CircularState 4 :=
  ⟨singletonExecution 4, ⟨[], rfl⟩⟩

example : circularEmit {0, 1} seed4.val .p = .null := rfl

/-- Registration is visible, but does not count as an absorption. -/
example :
    circularLabel 1 (step {0, 1} seed4.val .d) =
      .registered ⟨{0}, {1}, {0} ∪ {1}⟩ [] .short := by
  norm_num [seed4, singletonExecution, step, stepDefect, circularLabel, retainedLabel]

example : (step {0, 1} seed4.val .d).chain = [] := by
  simp [seed4, singletonExecution, step, stepDefect]

example (w : List Letter) :
    ((circularPrefixMachine (n := 4) (by omega) 1 (by omega)).trace seed4 w).length =
      w.length := circular_trace_length _ _ _ _ _

/-- Boundary `N=1`: both bindings survive, even above the maximum depth. -/
example : terminalPrefixCount 1 1 = 2 ∧ terminalPrefixCount 1 2 = 2 := by
  decide

example : terminalPrefixCount 3 1 = 6 ∧ terminalPrefixCount 3 2 = 14 ∧
    terminalPrefixCount 3 3 = 18 ∧ terminalPrefixCount 3 4 = 18 := by
  decide

example : Fintype.card (TerminalPrefixCode 3 2) = 14 := by
  rw [card_terminalPrefixCode]
  decide

/-- Actual label-image counts, including the above-maximum-depth boundary. -/
example : Nat.card (ActualTerminalLabel 3 1) = 2 ∧
    Nat.card (ActualTerminalLabel 3 2) = 2 := by
  constructor <;> rw [card_actualTerminalLabel (by omega) _ (by omega)] <;> decide

example : Nat.card (ActualTerminalLabel 5 2) = 14 ∧
    Nat.card (ActualTerminalLabel 5 4) = 18 := by
  constructor <;> rw [card_actualTerminalLabel (by omega) _ (by omega)] <;> decide

/-- A saturated prefix ending before the final checkpoint is actually completable. -/
private def early4 : Code 2 := fun i => if i.val = 0 then some true else none

example : ∃ s : CircularState 4, s.val.origin.isSome = true ∧
    FutureEvent.RankOnePlacement s.val ∧
      circularLabel 1 s.val = terminalSparseLabel (n := 4) (by omega) 1
        (.inl ⟨early4, by decide⟩) := by
  exact terminalSparseLabel_reachable (by omega) 1 (by omega) _

/-- Even the last full-carrier absorption retains its two ordered port bindings. -/
private def last3 (side : Bool) : Code 1 := fun _ => some side

private def last3Param (side : Bool) : CircularTerminalSparseCode 3 1 (by omega) :=
  .inl ⟨last3 side, by simp [support, last3]⟩

example : terminalSparseLabel (n := 3) (by omega) 1 (last3Param false) ≠
    terminalSparseLabel (n := 3) (by omega) 1 (last3Param true) := by
  intro h
  have hp := terminalSparseLabel_injective (by omega) 1 h
  have hc : last3 false = last3 true := congrArg Subtype.val (Sum.inl.inj hp)
  have he := congrFun hc 0
  simp [last3] at he

example (c : TerminalPrefixCode 3 2) :
    (terminalPrefixActualEquiv (n := 5) (by omega) 2 (by omega)).symm
      (terminalPrefixActualEquiv (n := 5) (by omega) 2 (by omega) c) = c :=
  terminalPrefix_encode_decode _ _ _ _

example (label : ActualTerminalLabel 5 2) :
    terminalPrefixActualEquiv (n := 5) (by omega) 2 (by omega)
      ((terminalPrefixActualEquiv (n := 5) (by omega) 2 (by omega)).symm label) = label :=
  terminalPrefix_decode_encode _ _ _ _

example (f : ProperCarrier 5) (j : ℕ)
    (c : ProperCarrierPrefixCode (n := 5) (by omega) j f) :
    (properCarrierPrefixActualEquiv (n := 5) (by omega) j f).symm
      (properCarrierPrefixActualEquiv (n := 5) (by omega) j f c) = c :=
  properCarrierPrefix_encode_decode _ _ _ _

example (f : ProperCarrier 5) (j : ℕ)
    (label : ActualProperPrefixLabel j f) :
    properCarrierPrefixActualEquiv (n := 5) (by omega) j f
      ((properCarrierPrefixActualEquiv (n := 5) (by omega) j f).symm label) = label :=
  properCarrierPrefix_decode_encode _ _ _ _

example (f : ProperCarrier 5) (j : ℕ) (_label : ActualProperPrefixLabel j f) :
    Nat.card (ActualProperPrefixLabel j f) = Nat.card (ProperCarrierPrefixCode (n := 5) (by omega) j f) :=
  card_actualProperPrefixLabel _ _ _

example (f : ProperCarrier 5) (j : ℕ)
    (label : ActualProperPrefixLabel j f) (r : ℕ)
    (hr : f.val.absorbed = r) :
    Nat.card (ActualProperPlacements j f label) =
      5 * (2 * (5 - 2) - r).choose (5 - 2 - r) := by
  exact card_actualProperPlacements_paper (by omega) j f label r hr

example : Nat.card (SaturatedCarrierParams 2 1) = 6 := by
  rw [card_saturatedCarrierParams]
  decide

example : Nat.card (ActualProperLabelsAt (n := 5) 1 1) = 2 := by
  rw [card_actualProperLabelsAt (by omega) (by omega) (by omega)]
  decide

example : Nat.card (ActualProperLabelsAt (n := 5) 2 2) = 6 := by
  rw [card_actualProperLabelsAt (by omega) (by omega) (by omega)]
  decide

example : Nat.card (ActualProperLabelsAt (n := 5) 0 1) = 1 := by
  exact card_actualProperLabelsAt_zero (by omega) (by omega)

example : Nat.card (ActualProperLabelsAt (n := 5) 2 4) = 6 := by
  rw [card_actualProperLabelsAt (by omega) (by omega) (by omega)]
  decide

example : Nat.card (ActualProperLabelsAt (n := 6) 3 2) = 18 := by
  rw [card_actualProperLabelsAt (by omega) (by omega) (by omega)]
  decide

example (p : SaturatedCarrierParams 2 1 ⊕ TerminalShort 2 1) :
    properCarrierCountEquiv (n := 5) (by omega) (by omega) (by omega)
      ((properCarrierCountEquiv (n := 5) (by omega) (by omega) (by omega)).symm p) = p :=
  properCarrierCount_encode_decode _ _ _ _

example (x : ActualProperLabelsAt (n := 5) 2 1) :
    (properCarrierCountEquiv (n := 5) (by omega) (by omega) (by omega)).symm
      (properCarrierCountEquiv (n := 5) (by omega) (by omega) (by omega) x) = x :=
  properCarrierCount_decode_encode _ _ _ _

example : Nat.card (ActualProperFibreAt (n := 5) 2 2) = 120 := by
  rw [card_actualProperFibreAt (by omega) (by omega) (by omega)]
  decide

example : Nat.card (ActualProperFibreAt (n := 3) 0 1) = 6 := by
  rw [card_actualProperFibreAt_zero (by omega) (by omega)]
  decide

example : Nat.card (TerminalObserverQuotient (n := 3) (by omega) 2 (by omega)) = 2 := by
  rw [card_terminalObserverQuotient_paper]
  decide

example : Nat.card (PrefixObserverQuotient (n := 3) (by omega) 1 (by omega)) = 12 := by
  rw [card_prefixObserverQuotient_paper]
  decide

example : Nat.card (PrefixObserverQuotient (n := 5) (by omega) 2 (by omega)) =
    paperTheorem33Count 5 2 := by
  exact card_prefixObserverQuotient_paper (by omega) 2 (by omega)

example : Nat.card (PrefixObserverQuotient (n := 5) (by omega) 2 (by omega)) = 410 := by
  rw [card_prefixObserverQuotient_paper]
  decide

example : Nat.card (RegisteredPrefixObserverQuotient (n := 5) (by omega) 2 (by omega)) =
    334 := by
  rw [card_registeredPrefixObserverQuotient_paper]
  decide

/-- Above the maximum chain depth, the quotient still forgets terminal phase. -/
example : Nat.card (PrefixObserverQuotient (n := 5) (by omega) 4 (by omega)) = 414 := by
  rw [card_prefixObserverQuotient_paper]
  decide

example : Nat.card (RegisteredPrefixObserverQuotient (n := 3) (by omega) 1 (by omega)) =
    8 := by
  rw [card_registeredPrefixObserverQuotient_paper]
  decide

example (x : PrefixObserverQuotient (n := 5) (by omega) 2 (by omega)) :
    (prefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega)).symm
      (prefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega) x) = x :=
  prefixObserver_encode_decode _ _ _ _

example (x : PrefixNormalForms 5 2) :
    prefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega)
      ((prefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega)).symm x) = x :=
  prefixObserver_decode_encode _ _ _ _

example (x : RegisteredPrefixObserverQuotient (n := 5) (by omega) 2 (by omega)) :
    (registeredPrefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega)).symm
      (registeredPrefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega) x) = x :=
  registeredPrefixObserver_encode_decode _ _ _ _

example (x : RegisteredPrefixNormalForms 5 2) :
    registeredPrefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega)
      ((registeredPrefixObserverNormalEquiv (n := 5) (by omega) 2 (by omega)).symm x) = x :=
  registeredPrefixObserver_decode_encode _ _ _ _

end Paper44.Checks
