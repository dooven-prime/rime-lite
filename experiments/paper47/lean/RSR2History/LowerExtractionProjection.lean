import RSR2History.LowerExtractionModel
import RSR2History.ActualEventTrace

/-!
Projection of the *same actual* singleton-transfer prefix to the independent
lower extraction problem. Upper letters disappear. A silent lower defect
either supplies a legal slide or is erased as idle; it is never interpreted
as a fusion. Each successful singleton transfer supplies exactly one
prescribed, zero-cost deletion.
-/

namespace RSR2History
open RSR2.Parametric

def lowerPreparationCount (word : List Letter) : Nat :=
  word.count (.p false) + word.count (.d false)

@[simp] theorem lowerPreparationCount_append (u v : List Letter) :
    lowerPreparationCount (u ++ v) = lowerPreparationCount u + lowerPreparationCount v := by
  simp [lowerPreparationCount, List.count_append]
  omega

@[simp] theorem lowerConfiguration_eq_some (P : Placement n) (a q : Fin n) :
    lowerConfiguration P a = some q ↔ P a = (false, q) := by
  rcases h : P a with ⟨layer, site⟩
  cases layer <;> simp [lowerConfiguration, h]

theorem lowerConfiguration_rotate_lower (n : Nat) (hn : 1 < n) (P : Placement n) :
    lowerConfiguration (rotate n (by omega) P false) =
      lowerRotate n hn (lowerConfiguration P) := by
  funext a
  rcases h : P a with ⟨layer, site⟩
  cases layer <;> simp [lowerConfiguration, lowerRotate, rotate, h]

theorem lowerConfiguration_rotate_upper (n : Nat) (hn : 1 < n) (P : Placement n) :
    lowerConfiguration (rotate n (by omega) P true) = lowerConfiguration P := by
  funext a
  rcases h : P a with ⟨layer, site⟩
  cases layer <;> simp [lowerConfiguration, rotate, h]

theorem lowerConfiguration_collapse_lower (n : Nat) (hn : 1 < n) (P : Placement n) :
    lowerConfiguration (collapse n hn P false) = lowerSlide n hn (lowerConfiguration P) := by
  funext a
  rcases h : P a with ⟨layer, site⟩
  cases layer <;> by_cases hs : site = site1 n hn <;>
    simp [lowerConfiguration, lowerSlide, collapse, h, hs]

theorem lowerConfiguration_collapse_upper (n : Nat) (hn : 1 < n) (P : Placement n) :
    lowerConfiguration (collapse n hn P true) = lowerConfiguration P := by
  funext a
  rcases h : P a with ⟨layer, site⟩
  cases layer <;> by_cases hs : site = site1 n hn <;>
    simp [lowerConfiguration, collapse, h, hs]

/-- Literal singleton identity, rather than only transfer count, determines
the deleted atom and every remaining lower coordinate. -/
theorem lowerConfiguration_transfer_singleton (n : Nat) (hn : 1 < n)
    {P Q : Placement n} {a : Fin n}
    (event : EventStep n hn P Q .v (.transfer {a})) :
    lowerConfiguration Q = lowerDelete (lowerConfiguration P) a := by
  have hpacket := event.transfer_source
  have ha : P a = (false, site0 n (by omega)) := by
    apply (mem_packetAt _ _ _ _).mp
    simp [hpacket]
  obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp event.1
  funext b
  by_cases hba : b = a
  · subst b
    simp [lowerConfiguration, lowerDelete, liftPacket, ha]
  · have hb : P b ≠ (false, site0 n (by omega)) := by
      intro he
      have hm := (mem_packetAt P false (site0 n (by omega)) b).mpr he
      simp [hpacket, hba] at hm
    simp only [lowerConfiguration, liftPacket, if_neg hb, lowerDelete, if_neg hba]

theorem EventStep.lowerExtraction_singleton {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {a : Fin n}
    (event : EventStep n hn P Q .v (.transfer {a})) :
    LowerExtractionPath n hn (lowerConfiguration P) [a] (lowerConfiguration Q) 0 := by
  rw [lowerConfiguration_transfer_singleton n hn event]
  apply LowerExtractionPath.delete
  · apply (lowerConfiguration_eq_some _ _ _).mpr
    apply (mem_packetAt _ _ _ _).mp
    simp [event.transfer_source]
  · intro b hb
    have hm := (mem_packetAt P false (site0 n (by omega)) b).mpr
      ((lowerConfiguration_eq_some _ _ _).mp hb)
    simpa [event.transfer_source] using hm

/-- A silent physical step contributes at most its own lower preparation
letter. Idle `d0` contributes no auxiliary edge and no auxiliary cost. -/
theorem SilentStep.lowerExtraction {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {letter : Letter} (h : SilentStep n hn P Q letter) :
    ∃ k, LowerExtractionPath n hn (lowerConfiguration P) [] (lowerConfiguration Q) k ∧
      k ≤ lowerPreparationCount [letter] := by
  cases letter with
  | p layer =>
      have he : Q = rotate n (by omega) P layer := by simpa [step_p] using h.1.symm
      subst Q
      cases layer with
      | false =>
          rw [lowerConfiguration_rotate_lower n hn]
          exact ⟨1, .rotate _, by simp [lowerPreparationCount]⟩
      | true =>
          rw [lowerConfiguration_rotate_upper n hn]
          exact ⟨0, .refl _, by simp [lowerPreparationCount]⟩
  | d layer =>
      have he : Q = collapse n hn P layer := by simpa [step_d] using h.1.symm
      subst Q
      cases layer with
      | false =>
          have hsilent := (silentStep_d_iff n hn P false).mp h
          by_cases hr : occupiedAt P false (site1 n hn)
          · rw [lowerConfiguration_collapse_lower n hn]
            refine ⟨1, .slide _ ?_ ?_, by simp [lowerPreparationCount]⟩
            · intro a ha
              exact hsilent ⟨⟨a, (lowerConfiguration_eq_some _ _ _).mp ha⟩, hr⟩
            · obtain ⟨a, ha⟩ := hr
              exact ⟨a, (lowerConfiguration_eq_some _ _ _).mpr ha⟩
          · rw [collapse_eq_of_empty_right n hn P false hr]
            exact ⟨0, .refl _, by simp [lowerPreparationCount]⟩
      | true =>
          rw [lowerConfiguration_collapse_upper n hn]
          exact ⟨0, .refl _, by simp [lowerPreparationCount]⟩
  | v => exact False.elim (not_silentStep_v n hn P Q h)

theorem runLogged_empty_lowerExtraction (n : Nat) (hn : 1 < n)
    (word : List Letter) {P Q : Placement n}
    (run : runLogged n hn P word = some (Q, [])) :
    ∃ k, LowerExtractionPath n hn (lowerConfiguration P) [] (lowerConfiguration Q) k ∧
      k ≤ lowerPreparationCount word := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa [runLogged] using run
      subst Q
      exact ⟨0, .refl _, by simp [lowerPreparationCount]⟩
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at run
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at run
          | some result =>
              obtain ⟨S, events⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ events = [] := by
                simpa [runLogged, hs, hr] using run
              obtain ⟨hempty, htail⟩ := List.append_eq_nil_iff.mp he.2
              have hfirst : SilentStep n hn P R letter := ⟨hs, hempty⟩
              have hrest : runLogged n hn R rest = some (Q, []) := by
                simpa [he.1, htail] using hr
              obtain ⟨k, hk, hkb⟩ := hfirst.lowerExtraction
              obtain ⟨l, hl, hlb⟩ := ih hrest
              refine ⟨k + l, by simpa using hk.trans hl, ?_⟩
              have hc := lowerPreparationCount_append [letter] rest
              simp only [List.singleton_append] at hc
              omega

/-- All deletions come from the trace's specified transfer records, in order;
all preparation edges come from its actual silent words. -/
theorem ActualEventTrace.lowerExtraction {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {z : List (Fin n)}
    (trace : ActualEventTrace n hn P (singletonTransferLog z) Q) :
    ∃ k, LowerExtractionPath n hn (lowerConfiguration P) z (lowerConfiguration Q) k ∧
      k ≤ lowerPreparationCount trace.word := by
  induction z generalizing P with
  | nil =>
      cases trace with
      | done tail htail => exact runLogged_empty_lowerExtraction n hn tail htail
  | cons a rest ih =>
      change ActualEventTrace n hn P (.transfer {a} :: singletonTransferLog rest) Q at trace
      cases trace with
      | cons before silent letter event tail =>
          have hletter := event.transfer_letter
          subst letter
          obtain ⟨k, hk, hkb⟩ := runLogged_empty_lowerExtraction n hn before silent
          obtain ⟨l, hl, hlb⟩ := ih tail
          have hp := (hk.trans event.lowerExtraction_singleton).trans hl
          refine ⟨k + l, by simpa using hp, ?_⟩
          simp only [ActualEventTrace.word, lowerPreparationCount_append]
          have hc : lowerPreparationCount (.v :: tail.word) =
              lowerPreparationCount tail.word := by simp [lowerPreparationCount]
          rw [hc]
          omega

/-- The full permutation hypothesis is used only to certify the empty
terminal auxiliary configuration, not to manufacture a projection path. -/
theorem singletonTransferTrace_lowerExtraction_complete {n : Nat} {hn : 1 < n}
    {Q : Placement n} {z : List (Fin n)}
    (trace : ActualEventTrace n hn (seed n) (singletonTransferLog z) Q)
    (hcover : ∀ a, a ∈ z) :
    ∃ k, LowerExtractionPath n hn (lowerExtractionSeed n) z (lowerExtractionEmpty n) k ∧
      k ≤ lowerPreparationCount trace.word := by
  obtain ⟨k, hk, hkb⟩ := trace.lowerExtraction
  have he := hk.terminal_empty hcover
  exact ⟨k, by simpa [he] using hk, hkb⟩

/-- Any actual delayed-chain realizer supplies a feasible auxiliary path.
The lower preparation bound is on the original raw word, not on a chosen
canonical execution. -/
theorem delayedChain_lowerExtraction_projection (n : Nat) (hn : 1 < n)
    (z : List (Fin n)) (hlen : z.length = n) (hnodup : z.Nodup)
    {word : List Letter} {Q : Placement n}
    (run : runLogged n hn (seed n) word = some (Q, delayedUpperChainLog z)) :
    ∃ k, LowerExtractionPath n hn (lowerExtractionSeed n) z (lowerExtractionEmpty n) k ∧
      k ≤ word.count (.p false) + word.count (.d false) := by
  obtain ⟨cut⟩ := delayedChainActualCut_of_runLogged n hn z run
  have hset : z.toFinset = Finset.univ := by
    apply (Finset.card_eq_iff_eq_univ _).mp
    rw [List.toFinset_card_of_nodup hnodup, hlen]
    simp
  have hcover : ∀ a, a ∈ z := by
    intro a
    have ha : a ∈ z.toFinset := by simp [hset]
    simpa using ha
  obtain ⟨k, hk, hkb⟩ := singletonTransferTrace_lowerExtraction_complete cut.loading hcover
  refine ⟨k, hk, ?_⟩
  have hc := congrArg lowerPreparationCount cut.segments_word
  rw [lowerPreparationCount_append] at hc
  change k ≤ lowerPreparationCount word
  omega

theorem delayedChain_lowerExtractionCost_lower_bound (n : Nat) (hn : 1 < n)
    (z : List (Fin n)) (hlen : z.length = n) (hnodup : z.Nodup)
    {word : List Letter} {Q : Placement n}
    (run : runLogged n hn (seed n) word = some (Q, delayedUpperChainLog z)) :
    lowerExtractionCost n hn z ≤ word.count (.p false) + word.count (.d false) := by
  obtain ⟨k, path, hcost⟩ := delayedChain_lowerExtraction_projection n hn z hlen hnodup run
  exact (lowerExtractionCost_le path).trans hcost

theorem delayedChain_lowerExtractionCost_attained (n : Nat) (hn : 1 < n)
    (z : List (Fin n)) (hlen : z.length = n) (hnodup : z.Nodup)
    {word : List Letter} {Q : Placement n}
    (run : runLogged n hn (seed n) word = some (Q, delayedUpperChainLog z)) :
    LowerExtractionPath n hn (lowerExtractionSeed n) z (lowerExtractionEmpty n)
      (lowerExtractionCost n hn z) := by
  obtain ⟨k, path, _⟩ := delayedChain_lowerExtraction_projection n hn z hlen hnodup run
  exact lowerExtractionCost_attained ⟨k, path⟩

end RSR2History
