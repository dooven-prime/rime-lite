import Mathlib.Data.List.Rotate
import Mathlib.Tactic

/-!
Self-contained routing of holes among a cyclic list of named packets.
The route has only positive hole slides and cyclic changes of frame.
Its inverse slides are derived, not assumed.
-/

namespace RSR2History

variable {α : Type*} [DecidableEq α]

def stripEmpty (empty : α) (xs : List α) : List α :=
  xs.filter (fun a => a != empty)

inductive SlotRoute (empty : α) : List α → List α → Prop
  | refl (xs) : SlotRoute empty xs xs
  | rotate (xs ys) : SlotRoute empty (xs ++ ys) (ys ++ xs)
  | slide (pre post) (a) :
      SlotRoute empty (pre ++ empty :: a :: post) (pre ++ a :: empty :: post)
  | trans {xs ys zs} :
      SlotRoute empty xs ys → SlotRoute empty ys zs → SlotRoute empty xs zs

omit [DecidableEq α] in
theorem SlotRoute.length_eq {empty : α} {xs ys : List α}
    (h : SlotRoute empty xs ys) : xs.length = ys.length := by
  induction h with
  | refl => rfl
  | rotate xs ys => simp; omega
  | slide pre post a => simp
  | trans _ _ ih₁ ih₂ => exact ih₁.trans ih₂

omit [DecidableEq α] in
/-- Move one hole through a linear sequence, one enabled slide at a time. -/
theorem SlotRoute.holeWalk (empty : α) (pre xs post : List α) :
    SlotRoute empty (pre ++ empty :: (xs ++ post)) (pre ++ xs ++ empty :: post) := by
  induction xs generalizing pre with
  | nil => simpa using (SlotRoute.refl (empty := empty) (pre ++ empty :: post))
  | cons a xs ih =>
      have h₁ := SlotRoute.slide (empty := empty) pre (xs ++ post) a
      have h₂ := ih (pre ++ [a])
      exact h₁.trans (by simpa [List.append_assoc] using h₂)

omit [DecidableEq α] in
/-- A reverse local slide is implemented by carrying its hole around the
complementary arc; no inverse generator is added. -/
theorem SlotRoute.backslide (empty : α) (pre post : List α) (a : α) :
    SlotRoute empty (pre ++ a :: empty :: post) (pre ++ empty :: a :: post) := by
  have h₁ := SlotRoute.rotate (empty := empty) (pre ++ [a]) (empty :: post)
  have h₂ := SlotRoute.holeWalk empty [] (post ++ pre) [a]
  have h₃ := SlotRoute.rotate (empty := empty) post (pre ++ [empty, a])
  have h₁' : SlotRoute empty (pre ++ a :: empty :: post)
      (empty :: (post ++ pre ++ [a])) := by
    simpa [List.append_assoc] using h₁
  have h₂' : SlotRoute empty (empty :: (post ++ pre ++ [a]))
      (post ++ pre ++ [empty, a]) := by
    simpa [List.append_assoc] using h₂
  exact h₁'.trans (h₂'.trans (by simpa [List.append_assoc] using h₃))

omit [DecidableEq α] in
theorem SlotRoute.symm {empty : α} {xs ys : List α}
    (h : SlotRoute empty xs ys) : SlotRoute empty ys xs := by
  induction h with
  | refl xs => exact .refl xs
  | rotate xs ys => exact .rotate ys xs
  | slide pre post a => exact .backslide empty pre post a
  | trans _ _ ih₁ ih₂ => exact ih₂.trans ih₁

/-- Linear bubble sorting of holes, retaining the literal nonempty word. -/
theorem SlotRoute.pack (empty : α) (xs pre post : List α) :
    SlotRoute empty (pre ++ xs ++ post)
      (pre ++ stripEmpty empty xs ++
        List.replicate (xs.count empty) empty ++ post) := by
  induction xs generalizing pre with
  | nil => simpa [stripEmpty] using (.refl (pre ++ post) : SlotRoute empty _ _)
  | cons a xs ih =>
      have h₁ := ih (pre ++ [a])
      by_cases ha : a = empty
      · subst a
        have h₂ := SlotRoute.holeWalk empty pre (stripEmpty empty xs)
          (List.replicate (xs.count empty) empty ++ post)
        have h₁' : SlotRoute empty (pre ++ empty :: xs ++ post)
            (pre ++ empty :: (stripEmpty empty xs ++
              List.replicate (xs.count empty) empty ++ post)) := by
          simpa [List.append_assoc] using h₁
        exact h₁'.trans
          (by simpa [stripEmpty, List.append_assoc, List.replicate_succ] using h₂)
      · simpa [stripEmpty, ha, List.append_assoc] using h₁

theorem SlotRoute.strip_rotated {empty : α} {xs ys : List α}
    (h : SlotRoute empty xs ys) :
    (stripEmpty empty xs).IsRotated (stripEmpty empty ys) := by
  induction h with
  | refl xs => exact .refl _
  | rotate xs ys =>
      simpa [stripEmpty] using
        (List.isRotated_append (l := stripEmpty empty xs) (l' := stripEmpty empty ys))
  | slide pre post a =>
      by_cases ha : a = empty <;>
        simp [stripEmpty, ha, List.IsRotated.refl]
  | trans _ _ ih₁ ih₂ => exact ih₁.trans ih₂

theorem SlotRoute.same_strip {empty : α} {xs ys : List α}
    (hlen : xs.length = ys.length)
    (hstrip : stripEmpty empty xs = stripEmpty empty ys) :
    SlotRoute empty xs ys := by
  have hmass (as : List α) : (stripEmpty empty as).length + as.count empty = as.length := by
    induction as with
    | nil => simp [stripEmpty]
    | cons a as ih =>
        by_cases ha : a = empty <;> simp [stripEmpty, ha] at * <;> omega
  have hc : xs.count empty = ys.count empty := by
    have hx := hmass xs
    have hy := hmass ys
    rw [hstrip] at hx
    omega
  have hx : SlotRoute empty xs
      (stripEmpty empty xs ++ List.replicate (xs.count empty) empty) := by
    simpa using SlotRoute.pack empty xs [] []
  exact hx.trans
    (by simpa [hstrip, hc] using (SlotRoute.pack empty ys [] []).symm)

/-- Complete invariant of the abstract directed hole-routing system. -/
theorem slotRoute_iff (empty : α) (xs ys : List α) :
    SlotRoute empty xs ys ↔ xs.length = ys.length ∧
      (stripEmpty empty xs).IsRotated (stripEmpty empty ys) := by
  refine ⟨fun h => ⟨h.length_eq, h.strip_rotated⟩, ?_⟩
  rintro ⟨hlen, hrot⟩
  obtain ⟨k, hk⟩ := hrot
  rw [List.rotate_eq_drop_append_take_mod] at hk
  have hparts : stripEmpty empty xs =
      (stripEmpty empty xs).take (k % (stripEmpty empty xs).length) ++
      (stripEmpty empty xs).drop (k % (stripEmpty empty xs).length) :=
    (List.take_append_drop _ _).symm
  obtain ⟨a, b, hab, ha, hb⟩ :=
    (List.filter_eq_append_iff (p := fun a : α => a != empty)).mp hparts
  have hsplit : xs = a ++ b := hab
  have hcut : stripEmpty empty (b ++ a) = stripEmpty empty ys := by
    simp only [stripEmpty, List.filter_append]
    rw [hb, ha]
    exact hk
  have hr : SlotRoute empty xs (b ++ a) := by
    simpa [hsplit] using (SlotRoute.rotate (empty := empty) a b)
  exact hr.trans
    (SlotRoute.same_strip (by simpa [hsplit, Nat.add_comm] using hlen) hcut)

end RSR2History
