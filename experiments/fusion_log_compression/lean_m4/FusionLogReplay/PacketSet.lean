import FusionLogReplay.EventTrace

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

/-- Literal occupied packet values; no source order or selected carrier is used. -/
def packetSet (P : Placement n (Finset α)) : Finset (Finset α) :=
  Finset.univ.biUnion (fun q => (P q).toFinset)

theorem mem_packetSet (P : Placement n (Finset α)) (B : Finset α) :
    B ∈ packetSet P ↔ ∃ q, P q = some B := by
  simp [packetSet]

theorem packetSet_rotate (P : Placement n (Finset α)) (phase : ZMod n) :
    packetSet (rotate phase P) = packetSet P := by
  ext B
  simp only [mem_packetSet]
  constructor
  · rintro ⟨q, hq⟩
    exact ⟨q - phase, hq⟩
  · rintro ⟨q, hq⟩
    exact ⟨q + phase, by simpa [rotate] using hq⟩

theorem packetSet_moveBack (P : Placement n (Finset α)) (j : ZMod n)
    (hole : P j = none) :
    packetSet (moveBack j P) = packetSet P := by
  ext B
  simp only [mem_packetSet]
  constructor
  · rintro ⟨q, hq⟩
    by_cases h0 : q = j
    · subst q
      exact ⟨j + 1, by simpa [moveBack] using hq⟩
    · by_cases h1 : q = j + 1
      · rw [moveBack, if_neg h0, if_pos h1] at hq
        cases hq
      · exact ⟨q, by simpa [moveBack, h0, h1] using hq⟩
  · rintro ⟨q, hq⟩
    by_cases h0 : q = j
    · subst q
      simp [hole] at hq
    · by_cases h1 : q = j + 1
      · exact ⟨j, by simpa [moveBack, h1] using hq⟩
      · exact ⟨q, by simpa [moveBack, h0, h1] using hq⟩

theorem stepDefect_placed_eq (F : Finset α) (s : Execution n α) :
    (stepDefect F s).placed = fusionPlacement s.placed := by
  unfold stepDefect
  cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;> simp

theorem packetSet_step_of_noEvent (F : Finset α) (s : Execution n α)
    (a : Letter) (empty : effectiveEvent s a = none) :
    packetSet (step F s a).placed = packetSet s.placed := by
  cases a with
  | p => exact packetSet_rotate s.placed 1
  | d =>
      change packetSet (stepDefect F s).placed = _
      rw [stepDefect_placed_eq]
      cases h0 : s.placed 0 with
      | none =>
          have hm : fusionPlacement s.placed = moveBack 0 s.placed := by
            funext q
            simp [fusionPlacement, moveBack, h0]
          rw [hm]
          exact packetSet_moveBack s.placed 0 h0
      | some A =>
          cases h1 : s.placed 1 with
          | some B => simp [effectiveEvent, h0, h1] at empty
          | none =>
              have hm : fusionPlacement s.placed = s.placed := by
                funext q
                by_cases hq0 : q = 0
                · subst q; simp [fusionPlacement, h0, h1]
                · by_cases hq1 : q = 1
                  · subst q; simp [fusionPlacement, hq0, h1]
                  · simp [fusionPlacement, hq0, hq1]
              rw [hm]

/-- A real fusion-free prefix changes placement but not the packet partition. -/
theorem packetSet_run_of_fusionFree (F : Finset α) (s : Execution n α)
    (word : List Letter) (free : FusionFree F s word) :
    packetSet (run F s word).placed = packetSet s.placed := by
  induction word generalizing s with
  | nil => rfl
  | cons a rest ih =>
      obtain ⟨head, tail⟩ := (fusionFree_cons_iff F s a rest).mp free
      exact (ih (step F s a) tail).trans (packetSet_step_of_noEvent F s a head)

/-- No literal packet value occupies two sites. -/
def UniquePackets (P : Placement n (Finset α)) : Prop :=
  ∀ q q' B, P q = some B → P q' = some B → q = q'

theorem packetSet_fusion (P : Placement n (Finset α))
    (A B : Finset α) (unique : UniquePackets P)
    (left : P 0 = some A) (right : P 1 = some B) :
    packetSet (fusionPlacement P) = insert (A ∪ B) ((packetSet P).erase A |>.erase B) := by
  ext C
  simp only [mem_packetSet, Finset.mem_insert, Finset.mem_erase]
  constructor
  · rintro ⟨q, hq⟩
    by_cases h0 : q = 0
    · subst q
      left
      exact Option.some.inj (hq.symm.trans (by simp [fusionPlacement, left, right]))
    · by_cases h1 : q = 1
      · rw [fusionPlacement, if_neg h0, if_pos h1] at hq
        cases hq
      · have old : P q = some C := by simpa [fusionPlacement, h0, h1] using hq
        right
        refine ⟨?_, ?_, q, old⟩
        · intro eq
          subst C
          exact h1 (unique q 1 B old right)
        · intro eq
          subst C
          exact h0 (unique q 0 A old left)
  · rintro (rfl | ⟨neB, neA, q, hq⟩)
    · exact ⟨0, by simp [fusionPlacement, left, right]⟩
    · have h0 : q ≠ 0 := by
        intro eq
        subst q
        exact neA (Option.some.inj (hq.symm.trans left))
      have h1 : q ≠ 1 := by
        intro eq
        subst q
        exact neB (Option.some.inj (hq.symm.trans right))
      exact ⟨q, by simpa [fusionPlacement, h0, h1] using hq⟩

theorem sourceOrdered_uniquePackets
    (P : Placement n (Finset (ZMod n))) (ordered : SourceOrdered P) :
    UniquePackets P := by
  intro q q' B hq hq'
  obtain ⟨lift, hp⟩ := ordered
  obtain ⟨hf, ⟨a, ha⟩⟩ :=
    (placementOfMap_some_iff lift.position q B).mp (hp ▸ hq)
  have hf' := (placementOfMap_some_iff lift.position q' B).mp (hp ▸ hq')
  have hqa := (mem_sourceFiber lift.position a q).mp (hf.symm ▸ ha)
  have hqa' := (mem_sourceFiber lift.position a q').mp (hf'.1.symm ▸ ha)
  exact hqa.symm.trans hqa'

end FusionLogReplay
