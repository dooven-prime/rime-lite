import Paper44.TerminalLabelEquiv

/-! # The actual terminal observer quotient

This quotient uses the machine's all-word observer equivalence, not a relation
defined by counting parameters. The terminal classification proves that its
classes are exactly the actually attained retained labels.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

def ActualTerminalState (n : ℕ) [NeZero n] :=
  {s : CircularState n // s.val.origin.isSome = true ∧ RankOnePlacement s.val}

def terminalObserverSetoid (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Setoid (ActualTerminalState n) where
  r x y := (circularPrefixMachine hn j hj).ObserverEq x.val y.val
  iseqv := ⟨fun x => LabelledMachine.observerEq_refl _ x.val,
    fun h => LabelledMachine.observerEq_symm _ h,
    fun hxy hyz => LabelledMachine.observerEq_trans _ hxy hyz⟩

abbrev TerminalObserverQuotient (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :=
  Quotient (terminalObserverSetoid hn j hj)

def terminalStateLabel (j : ℕ) (x : ActualTerminalState n) :
    ActualTerminalLabel n j :=
  ⟨circularLabel j x.val.val, x.val, x.property.1, x.property.2, rfl⟩

theorem terminalStateLabel_eq_iff (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x y : ActualTerminalState n) :
    terminalStateLabel j x = terminalStateLabel j y ↔
      (terminalObserverSetoid hn j hj).r x y := by
  constructor
  · intro h
    exact (circular_terminal_observerEq_iff_label hn j hj x.val y.val
      x.property.2 y.property.2).mpr (congrArg Subtype.val h)
  · intro h
    exact Subtype.ext ((circular_terminal_observerEq_iff_label hn j hj x.val y.val
      x.property.2 y.property.2).mp h)

def terminalQuotientLabel (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    TerminalObserverQuotient hn j hj → ActualTerminalLabel n j :=
  Quotient.lift (terminalStateLabel j) (fun x y h =>
    (terminalStateLabel_eq_iff hn j hj x y).mpr h)

theorem terminalQuotientLabel_bijective (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Function.Bijective (terminalQuotientLabel hn j hj) := by
  constructor
  · intro x y
    induction x using Quotient.inductionOn with
    | _ x =>
      induction y using Quotient.inductionOn with
      | _ y =>
        intro h
        exact Quotient.sound ((terminalStateLabel_eq_iff hn j hj x y).mp h)
  · intro label
    obtain ⟨s, hr, ht, hl⟩ := label.property
    exact ⟨Quotient.mk _ ⟨s, hr, ht⟩, Subtype.ext hl⟩

/-- An explicit forward map from actual terminal observer classes to labels.
The inverse is noncomputable; both identities concern classes, not raw words. -/
noncomputable def terminalObserverLabelEquiv (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    TerminalObserverQuotient hn j hj ≃ ActualTerminalLabel n j :=
  Equiv.ofBijective (terminalQuotientLabel hn j hj)
    (terminalQuotientLabel_bijective hn j hj)

@[simp] theorem terminalObserverLabelEquiv_mk (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x : ActualTerminalState n) :
    terminalObserverLabelEquiv hn j hj (Quotient.mk _ x) = terminalStateLabel j x := rfl

theorem terminalObserver_encode_decode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x : TerminalObserverQuotient hn j hj) :
    (terminalObserverLabelEquiv hn j hj).symm
      (terminalObserverLabelEquiv hn j hj x) = x :=
  (terminalObserverLabelEquiv hn j hj).symm_apply_apply x

theorem terminalObserver_decode_encode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (label : ActualTerminalLabel n j) :
    terminalObserverLabelEquiv hn j hj
      ((terminalObserverLabelEquiv hn j hj).symm label) = label :=
  (terminalObserverLabelEquiv hn j hj).apply_symm_apply label

/-- Lemma 3.2 is also the exact minimal terminal-sector quotient count. -/
theorem card_terminalObserverQuotient_paper (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (TerminalObserverQuotient hn j hj) =
      2 ^ j * (n - 2).choose j +
        ∑ ell ∈ Finset.Icc 1 (j - 1), 2 ^ ell * (n - 3).choose (ell - 1) := by
  rw [Nat.card_congr (terminalObserverLabelEquiv hn j hj)]
  exact card_actualTerminalLabel_paper hn j hj

end Paper44
