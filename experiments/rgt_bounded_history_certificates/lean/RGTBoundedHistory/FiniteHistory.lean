import Std

/-!
# Finite-state history replacement

The cover counts complete auxiliary states. No bound on a lossy summary or
behavior quotient is substituted for it. Words are chronological.
-/

namespace RGTBoundedHistory

universe u v

variable {S : Type u} {A : Type v}

def run (step : S → A → S) (x : S) : List A → S
  | [] => x
  | a :: w => run step (step x a) w

def visits (step : S → A → S) (x : S) : List A → List S
  | [] => [x]
  | a :: w => x :: visits step (step x a) w

@[simp] theorem run_append (step : S → A → S) (x : S) (h k : List A) :
    run step x (h ++ k) = run step (run step x h) k := by
  induction h generalizing x with
  | nil => rfl
  | cons a h ih => exact ih (step x a)

@[simp] theorem visits_length (step : S → A → S) (x : S) (w : List A) :
    (visits step x w).length = w.length + 1 := by
  induction w generalizing x with
  | nil => rfl
  | cons a w ih => simp [visits, ih, Nat.add_assoc]

theorem suffix_from_visit (step : S → A → S) {x y : S} {w : List A}
    (h : x ∈ visits step y w) :
    ∃ v : List A, run step x v = run step y w ∧
      (visits step x v).Sublist (visits step y w) := by
  induction w generalizing y with
  | nil =>
      have heq : x = y := by simpa [visits] using h
      subst y
      exact ⟨[], rfl, List.Sublist.refl _⟩
  | cons a w ih =>
      simp only [visits, List.mem_cons] at h
      rcases h with heq | htail
      · subst y
        exact ⟨a :: w, rfl, List.Sublist.refl _⟩
      · obtain ⟨v, hrun, hsub⟩ := ih htail
        exact ⟨v, hrun, hsub.cons _⟩

/-- Loop erasure preserves the endpoint and uses only original visited states. -/
theorem loop_erasure (step : S → A → S) (x : S) (w : List A) :
    ∃ v : List A, run step x v = run step x w ∧
      (visits step x v).Nodup ∧
      (visits step x v).Sublist (visits step x w) := by
  classical
  induction w generalizing x with
  | nil => exact ⟨[], rfl, by simp [visits], List.Sublist.refl _⟩
  | cons a w ih =>
      obtain ⟨v, hrun, hnodup, hsub⟩ := ih (step x a)
      by_cases hmem : x ∈ visits step (step x a) v
      · obtain ⟨z, hzrun, hzsub⟩ := suffix_from_visit step hmem
        exact ⟨z, hzrun.trans hrun, hnodup.sublist hzsub,
          (hzsub.trans hsub).cons _⟩
      · refine ⟨a :: v, hrun, ?_, hsub.cons_cons _⟩
        simpa only [visits, List.nodup_cons] using And.intro hmem hnodup

theorem visit_is_reachable (step : S → A → S) {x y : S} {w : List A}
    (h : y ∈ visits step x w) : ∃ u : List A, run step x u = y := by
  induction w generalizing x with
  | nil =>
      have heq : y = x := by simpa [visits] using h
      exact ⟨[], heq.symm⟩
  | cons a w ih =>
      simp only [visits, List.mem_cons] at h
      rcases h with heq | htail
      · exact ⟨[], heq.symm⟩
      · obtain ⟨u, hu⟩ := ih htail
        exact ⟨a :: u, hu⟩

/-- A finite list covering every reachable complete state; duplicates are allowed. -/
structure FiniteSystem (S : Type u) (A : Type v) where
  step : S → A → S
  seed : S
  cover : List S
  complete : ∀ w : List A, run step seed w ∈ cover

namespace FiniteSystem

def eval (M : FiniteSystem S A) (w : List A) : S := run M.step M.seed w

/-- Strict length form avoids natural subtraction at the empty-cover boundary. -/
theorem bounded_replacement (M : FiniteSystem S A) (w : List A) :
    ∃ v : List A, M.eval v = M.eval w ∧ v.length < M.cover.length := by
  obtain ⟨v, hv, hnodup, _⟩ := loop_erasure M.step M.seed w
  have hsubset : visits M.step M.seed v ⊆ M.cover := by
    intro y hy
    obtain ⟨u, hu⟩ := visit_is_reachable M.step hy
    rw [← hu]
    exact M.complete u
  have hlen := hnodup.length_le_of_subset hsubset
  rw [visits_length] at hlen
  exact ⟨v, hv, by omega⟩

theorem cover_positive (M : FiniteSystem S A) : 0 < M.cover.length := by
  exact List.length_pos_iff_exists_mem.mpr ⟨M.seed, M.complete []⟩

theorem bounded_replacement_le (M : FiniteSystem S A) (w : List A) :
    ∃ v : List A, M.eval v = M.eval w ∧ v.length ≤ M.cover.length - 1 := by
  obtain ⟨v, hv, hlen⟩ := M.bounded_replacement w
  exact ⟨v, hv, by omega⟩

/-- Every predicate of two endpoints is preserved by separate replacements. -/
theorem bounded_pair (M : FiniteSystem S A) (P : S → S → Prop)
    (h : ∃ u v : List A, P (M.eval u) (M.eval v)) :
    ∃ u v : List A, u.length < M.cover.length ∧ v.length < M.cover.length ∧
      P (M.eval u) (M.eval v) := by
  obtain ⟨u, v, huv⟩ := h
  obtain ⟨u', hu', hlu⟩ := M.bounded_replacement u
  obtain ⟨v', hv', hlv⟩ := M.bounded_replacement v
  exact ⟨u', v', hlu, hlv, by simpa only [hu', hv'] using huv⟩

end FiniteSystem
end RGTBoundedHistory
