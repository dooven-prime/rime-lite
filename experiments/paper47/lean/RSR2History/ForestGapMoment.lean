import RSR2History.ForestDominatingCut

/-! Cyclic first moments of released holes. The minimum is over cyclic cuts
of the same named root cycle; this definition does not move any packet. -/
namespace RSR2History
variable {r : Nat} [NeZero r]

/-- Hole mass weighted by root distance from one cyclic cut. -/
def forestGapWeight (h : Fin r → Nat) (q : Fin r) : Nat :=
  ∑ j : Fin r, j.val * h (q+j)

private theorem gapWeights_nonempty (h : Fin r → Nat) :
    (Finset.univ.image (forestGapWeight h)).Nonempty := by
  classical
  exact ⟨_, Finset.mem_image.mpr ⟨0, Finset.mem_univ _, rfl⟩⟩

/-- Least cyclic first moment. The source profile and its names are fixed. -/
noncomputable def forestGapMoment (h : Fin r → Nat) : Nat := by
  classical
  exact (Finset.univ.image (forestGapWeight h)).min' (gapWeights_nonempty h)

theorem forestGapMoment_le_weight (h : Fin r → Nat) (q : Fin r) :
    forestGapMoment h ≤ forestGapWeight h q := by
  classical
  exact Finset.min'_le _ _ (Finset.mem_image.mpr ⟨q, Finset.mem_univ _, rfl⟩)

theorem forestGapMoment_attained (h : Fin r → Nat) :
    ∃ q : Fin r, forestGapWeight h q = forestGapMoment h := by
  classical
  obtain ⟨q, _, hq⟩ := Finset.mem_image.mp
    (Finset.min'_mem (Finset.univ.image (forestGapWeight h)) (gapWeights_nonempty h))
  exact ⟨q, hq⟩

/-- A displayed cyclic shift adds the same offset to the chosen cut. -/
theorem forestGapWeight_rotate (h : Fin r → Nat) (c q : Fin r) :
    forestGapWeight (fun i => h (c+i)) q = forestGapWeight h (c+q) := by
  simp only [forestGapWeight, add_assoc]

/-- Rotating the displayed root list changes no cyclic moment. -/
theorem forestGapMoment_rotate (h : Fin r → Nat) (c : Fin r) :
    forestGapMoment (fun i => h (c+i)) = forestGapMoment h := by
  apply le_antisymm
  · obtain ⟨q, hq⟩ := forestGapMoment_attained h
    have he := forestGapMoment_le_weight (fun i => h (c+i)) (q-c)
    have hcancel : c+(q-c)=q := by abel
    simpa only [forestGapWeight_rotate, hcancel, hq] using he
  · obtain ⟨q, hq⟩ := forestGapMoment_attained (fun i => h (c+i))
    have he := forestGapMoment_le_weight h (c+q)
    rw [← forestGapWeight_rotate, hq] at he
    exact he

/-- Reindexing the same weighted sum by the named root itself. -/
theorem forestGapWeight_eq_named_sum (h : Fin r → Nat) (q : Fin r) :
    forestGapWeight h q = ∑ i : Fin r, (i-q).val * h i := by
  apply Fintype.sum_equiv (Equiv.addLeft q)
  intro j
  simp

/-- Zero moment means all positive holes are concentrated at one root. -/
theorem forestGapMoment_eq_zero_iff (h : Fin r → Nat) :
    forestGapMoment h = 0 ↔ ∃ q : Fin r, ∀ i, i ≠ q → h i = 0 := by
  classical
  constructor
  · intro hm
    obtain ⟨q, hq⟩ := forestGapMoment_attained h
    refine ⟨q, ?_⟩
    intro i hi
    have ht : (i-q).val * h i ≤ forestGapWeight h q := by
      rw [forestGapWeight_eq_named_sum]
      exact Finset.single_le_sum (f := fun j : Fin r => (j-q).val * h j)
        (fun j _ => Nat.zero_le _) (Finset.mem_univ i)
    have hz : (i-q).val ≠ 0 := by
      intro he
      have he' : i-q = 0 := Fin.ext he
      exact hi (sub_eq_zero.mp he')
    rw [hq, hm] at ht
    exact (Nat.mul_eq_zero.mp (Nat.eq_zero_of_le_zero ht)).resolve_left hz
  · rintro ⟨q, hq⟩
    have hw : forestGapWeight h q = 0 := by
      rw [forestGapWeight_eq_named_sum]
      apply Finset.sum_eq_zero
      intro i _
      by_cases he : i = q
      · simp [he]
      · simp [hq i he]
    have := forestGapMoment_le_weight h q
    omega

/-- At most the mass at the cut can have zero weight. -/
theorem forestGapWeight_mass_le (h : Fin r → Nat) (q : Fin r) :
    (∑ i : Fin r, h i) ≤ forestGapWeight h q + h q := by
  classical
  rw [forestGapWeight_eq_named_sum]
  calc
    _ ≤ ∑ i : Fin r, ((i-q).val * h i + if i=q then h q else 0) := by
      apply Finset.sum_le_sum
      intro i _
      by_cases he : i = q
      · simp [he]
      · have hz : (i-q).val ≠0 := by
          intro hh
          apply he
          exact sub_eq_zero.mp (Fin.ext hh)
        simp only [if_neg he, Nat.add_zero]
        simpa only [Nat.one_mul] using Nat.mul_le_mul_right (h i) (by omega : 1 ≤ (i-q).val)
    _ = (∑ i : Fin r, (i-q).val*h i)+h q := by
      rw [Finset.sum_add_distrib]
      simp

/-- The cyclic moment pays all hole mass except, at most, the largest
single gap. This includes the zero-hole and one-positive-gap cases. -/
theorem forestGapMoment_mass_le (h : Fin r → Nat) :
    (∑ i : Fin r, h i) ≤ forestGapMoment h + Finset.univ.sup h := by
  classical
  obtain ⟨q, hq⟩ := forestGapMoment_attained h
  have hm := forestGapWeight_mass_le h q
  have hmax : h q ≤ Finset.univ.sup h := Finset.le_sup (Finset.mem_univ q)
  omega

theorem forestGapMoment_lower_bound (h : Fin r → Nat) :
    (∑ i : Fin r, h i) - Finset.univ.sup h ≤ forestGapMoment h := by
  have := forestGapMoment_mass_le h
  omega

/-- A profile with two named positive clusters; other roots release no holes. -/
def twoClusterGapProfile (p : Fin r) (a b : Nat) (i : Fin r) : Nat :=
  (if i=0 then a else 0) + (if i=p then b else 0)

theorem forestGapWeight_twoCluster (p q : Fin r) (a b : Nat) :
    forestGapWeight (twoClusterGapProfile p a b) q =
      (-q).val*a + (p-q).val*b := by
  classical
  rw [forestGapWeight_eq_named_sum]
  simp only [twoClusterGapProfile, Nat.mul_add, Finset.sum_add_distrib]
  congr 1
  · simp [mul_ite]
  · simp [mul_ite]

/-- Two disjoint gap clusters pay the smaller of the two directed
root-distance moments, using one common cursor rather than two routes. -/
theorem forestGapMoment_twoCluster (p : Fin r) (hp : p ≠ 0) (a b : Nat) :
    forestGapMoment (twoClusterGapProfile p a b) =
      min (p.val*b) ((r-p.val)*a) := by
  classical
  have hneg : (-p).val = r-p.val := by simp [Fin.val_neg, hp]
  apply le_antisymm
  · apply le_min
    · simpa [forestGapWeight_twoCluster] using
        forestGapMoment_le_weight (twoClusterGapProfile p a b) 0
    · simpa [forestGapWeight_twoCluster, hneg] using
        forestGapMoment_le_weight (twoClusterGapProfile p a b) p
  · obtain ⟨q, hq⟩ := forestGapMoment_attained (twoClusterGapProfile p a b)
    rw [← hq, forestGapWeight_twoCluster]
    by_cases hq0 : q=0
    · simp [hq0]
    · rw [Fin.val_neg, if_neg hq0]
      by_cases hqp : q ≤ p
      · have hdiff := Nat.mul_le_mul_right a
          (by have : q.val ≤ p.val := hqp; omega : r-p.val ≤ r-q.val)
        exact (min_le_right _ _).trans (by omega)
      · have hval : (p-q).val = r+p.val-q.val :=
          Fin.coe_sub_iff_lt.mpr (lt_of_not_ge hqp)
        rw [hval]
        have hb := Nat.mul_le_mul_right b
          (by have := q.isLt; omega : p.val ≤ r+p.val-q.val)
        exact (min_le_left _ _).trans (by omega)

/-- The smallest two-root separated-hole example has one unit of gain. -/
theorem forestGapMoment_two_unit :
    forestGapMoment (fun _ : Fin 2 => 1) = 1 := by
  have he : (fun _ : Fin 2 => 1) = twoClusterGapProfile (1 : Fin 2) 1 1 := by
    funext i
    fin_cases i <;> decide
  rw [he, forestGapMoment_twoCluster (1 : Fin 2) (by decide)]
  norm_num

end RSR2History
