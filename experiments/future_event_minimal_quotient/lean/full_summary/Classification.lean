import full_summary.Observation

namespace FullSummary

open RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

/-- Only permanently unregistered states form the full-summary null class.
Registered rank-one states are deliberately excluded. -/
def PermanentlyUnregistered (s : Execution n (ZMod n)) : Prop :=
  s.origin = none ∧ ¬ PairRegisterable s

theorem permanently_unregistered_run (s : Execution n (ZMod n))
    (h : PermanentlyUnregistered s) (word : List Letter) :
    (run {0, 1} s word).origin = none := by
  cases ho : (run {0, 1} s word).origin with
  | none => rfl
  | some r => exact False.elim (h.2 ⟨h.1, word, by simp [ho]⟩)

theorem permanently_unregistered_equivalent (s t : Execution n (ZMod n))
    (hs : PermanentlyUnregistered s) (ht : PermanentlyUnregistered t) :
    Equivalent {0, 1} s t := by
  intro word
  exact ((output_eq_none _).mpr (permanently_unregistered_run s hs word)).trans
    ((output_eq_none _).mpr (permanently_unregistered_run t ht word)).symm

theorem registerable_iff_of_equivalent (s t : Execution n (ZMod n))
    (hs : s.origin = none) (ht : t.origin = none) (h : Equivalent {0, 1} s t) :
    PairRegisterable s ↔ PairRegisterable t := by
  have transfer (x y : Execution n (ZMod n)) (hy : y.origin = none)
      (he : Equivalent {0, 1} x y) (hx : PairRegisterable x) : PairRegisterable y := by
    obtain ⟨_, word, hw⟩ := hx
    have ho := congrArg (fun o : Option (Execution n (ZMod n)) => o.bind Execution.origin) (he word)
    rw [output_origin, output_origin] at ho
    exact ⟨hy, word, by rw [← ho]; exact hw⟩
  exact ⟨transfer s t ht h, transfer t s hs (fun word => (h word).symm)⟩

/-- Full-summary equivalence is classified from the Moore contract, not
defined by the proposed classes. Registered identity includes every field. -/
theorem equivalent_iff_normalForm (s t : Execution n (ZMod n))
    (hn : 3 ≤ n) (hs : PairGenerated s) (ht : PairGenerated t) :
    Equivalent {0, 1} s t ↔
      (PermanentlyUnregistered s ∧ PermanentlyUnregistered t) ∨ s = t := by
  constructor
  · intro h
    have hnow : output s = output t := h []
    rcases output_equal_cases s t hnow with ⟨ho, hp⟩ | he
    · have hreg := registerable_iff_of_equivalent s t ho hp h
      by_cases hr : PairRegisterable s
      · right
        by_contra hne
        obtain ⟨word, hdiff, _⟩ := registerable_pair_separation s t hn hs ht hr (hreg.mp hr) hne
        exact hdiff (equivalent_implies_future {0, 1} s t h word)
      · exact Or.inl ⟨⟨ho, hr⟩, ⟨hp, fun htr => hr (hreg.mpr htr)⟩⟩
    · exact Or.inr he
  · rintro (⟨hzs, hzt⟩ | rfl)
    · exact permanently_unregistered_equivalent s t hzs hzt
    · exact equivalent_refl {0, 1} s

theorem registered_equivalent_iff_eq (s t : Execution n (ZMod n))
    (hs : s.origin.isSome = true) : Equivalent {0, 1} s t ↔ s = t := by
  constructor
  · intro h
    have hnow : output s = output t := h []
    have hout : output s = some s := (output_eq_some s s).mpr ⟨rfl, hs⟩
    exact ((output_eq_some t s).mp (hnow.symm.trans hout)).1.symm
  · rintro rfl
    exact equivalent_refl {0, 1} s

end FullSummary
